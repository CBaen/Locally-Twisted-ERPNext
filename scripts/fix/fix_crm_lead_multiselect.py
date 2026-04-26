#!/usr/bin/env python3
"""
Revise crm.lead translation: convert `custom_event_type` from Select to
Table MultiSelect (so multiple services can be picked at once) AND add
`depends_on` expressions to the sub-section breaks + per-service note
fields so empty noise sections collapse until they're relevant.

Why this revision:
  GL feedback after the v1 translation (translate_crm_lead.py):
    > "Service type should be multi select, not a dropdown. Customer can
    >  often choose more than 1 service. All of the section options and
    >  additional notes fields for each individual service are already
    >  populating when they shouldn't until a service type is selected."

  The original Odoo `x_event_type` was a single-select Selection. But the
  /book form's `x_services` Char field was multi-value (comma-joined
  checkboxes). The TRUE intent for the admin Lead form is multi-select —
  Jeff often takes a phone call where the customer wants multiple things.

What this script does:
  1. Creates DocType "LT Service Type" (parent, autoname by service_type,
     9 seeded records covering both x_event_type and /book form options).
  2. Creates DocType "LT Lead Service Type" (child / istable=1 for use in
     a Table MultiSelect column on Lead).
  3. Deletes the original `custom_event_type` Custom Field (Select).
  4. Re-creates `custom_event_type` as a Table MultiSelect linking to
     "LT Lead Service Type".
  5. Patches `depends_on` on each section break + each per-service note
     field so they only render when a relevant service is selected.

Idempotent: each step checks-or-skips. Safe to re-run.

Stdlib only.

Run AFTER translate_crm_lead.py has been executed at least once.
"""

import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from http.cookiejar import CookieJar


BASE = "http://localhost:8081"
USER = "Administrator"
PWD = "admin"

# ── DocType: LT Service Type (parent) ──
SERVICE_TYPE_DOCTYPE = {
    "doctype": "DocType",
    "name": "LT Service Type",
    "module": "Custom",
    "custom": 1,
    "naming_rule": "By fieldname",
    "autoname": "field:service_type",
    "title_field": "service_type",
    "track_changes": 0,
    "allow_rename": 1,
    "fields": [
        {
            "fieldname": "service_type",
            "label": "Service Type",
            "fieldtype": "Data",
            "reqd": 1,
            "unique": 1,
            "in_list_view": 1,
        },
    ],
    "permissions": [
        {"role": "System Manager",
         "read": 1, "write": 1, "create": 1, "delete": 1,
         "report": 1, "export": 1, "share": 1},
        {"role": "All", "read": 1},
    ],
}

# ── DocType: LT Lead Service Type (child for Table MultiSelect) ──
LEAD_SERVICE_TYPE_DOCTYPE = {
    "doctype": "DocType",
    "name": "LT Lead Service Type",
    "module": "Custom",
    "custom": 1,
    "istable": 1,
    "fields": [
        {
            "fieldname": "service_type",
            "label": "Service Type",
            "fieldtype": "Link",
            "options": "LT Service Type",
            "reqd": 1,
            "in_list_view": 1,
        },
    ],
    "permissions": [],  # child tables inherit parent permissions
}

# ── Seed records: 9 service types covering both x_event_type and /book ──
SEED_SERVICE_TYPES = [
    "Balloon Arch",
    "Balloon Drop",
    "Balloon Wall",
    "Custom Installation",
    "Balloon Twisting",
    "Face Painting",
    "Delivery",
    "Event Package",
    "Other",
]

# ── Conditional visibility expressions ──
# Frappe `depends_on` accepts JS expressions prefixed with `eval:`.
# For Table MultiSelect, doc.fieldname is a list of child rows.
# A row's value is in row.<child_link_fieldname>.

def _selected(svcs):
    """Return a depends_on JS expression matching when ANY of svcs is selected."""
    quoted = ",".join(f"'{s}'" for s in svcs)
    return ("eval:doc.custom_event_type "
            "&& doc.custom_event_type.some(function(r){"
            f"return [{quoted}].indexOf(r.service_type) !== -1;"
            "})")

# Decor variants — show decor notes whenever any specific decor type is picked
DECOR_VARIANTS = ["Balloon Arch", "Balloon Drop", "Balloon Wall", "Custom Installation"]
ARTIST_VARIANTS = ["Balloon Twisting", "Face Painting"]

DEPENDS_ON_PATCHES = {
    # Sections — collapse the artist-specific blocks unless a relevant service is picked
    "lt_section_choice":       _selected(ARTIST_VARIANTS),
    "lt_section_dynamic":      _selected(ARTIST_VARIANTS),
    "lt_section_services":     "eval:doc.custom_event_type && doc.custom_event_type.length > 0",
    # Per-service notes
    "custom_decor_notes":      _selected(DECOR_VARIANTS),
    "custom_twisting_notes":   _selected(["Balloon Twisting"]),
    "custom_painting_notes":   _selected(["Face Painting"]),
    "custom_delivery_notes":   _selected(["Delivery"]),
    "custom_package_notes":    _selected(["Event Package"]),
    "custom_other_notes":      _selected(["Other"]),
    # custom_services itself is informational; show it when any service is picked
    "custom_services":         "eval:doc.custom_event_type && doc.custom_event_type.length > 0",
}


def make_opener():
    cj = CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))


def login(opener):
    data = urllib.parse.urlencode({"usr": USER, "pwd": PWD}).encode()
    req = urllib.request.Request(f"{BASE}/api/method/login", data=data)
    with opener.open(req, timeout=10) as r:
        body = r.read().decode()
    if r.status != 200:
        raise SystemExit(f"login failed: HTTP {r.status} body={body}")
    print(f"[login] OK as {USER}")


def call(opener, method, payload, timeout=30):
    """POST to /api/method/<method> with JSON payload."""
    req = urllib.request.Request(
        f"{BASE}/api/method/{method}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "X-Requested-With": "XMLHttpRequest"},
    )
    try:
        with opener.open(req, timeout=timeout) as r:
            return json.loads(r.read().decode()), False
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return body, True


def doctype_exists(opener, name):
    url = f"{BASE}/api/resource/DocType/{urllib.parse.quote(name)}"
    try:
        with opener.open(urllib.request.Request(url), timeout=10) as r:
            return r.status == 200
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False
        raise


def insert_doc(opener, doc, label):
    res, err = call(opener, "frappe.client.insert", {"doc": doc})
    if err:
        if 'already exists' in res or 'DuplicateEntryError' in res:
            print(f"  [skip] {label} already exists")
            return None
        raise SystemExit(f"[{label}] failed: {res[:300]}")
    name = res.get('message', {}).get('name', '?')
    print(f"  [ok]   {label} -> {name}")
    return res


def delete_doc(opener, doctype, name, label):
    res, err = call(opener, "frappe.client.delete",
                    {"doctype": doctype, "name": name})
    if err:
        if 'DoesNotExistError' in res or 'not found' in res.lower():
            print(f"  [skip] {label} not present")
            return False
        raise SystemExit(f"[delete {label}] failed: {res[:300]}")
    print(f"  [ok]   deleted {label}")
    return True


def set_field(opener, doctype, name, fieldname, value, label):
    res, err = call(opener, "frappe.client.set_value", {
        "doctype": doctype,
        "name": name,
        "fieldname": fieldname,
        "value": value,
    })
    if err:
        if 'DoesNotExistError' in res:
            print(f"  [skip] {label} not present")
            return
        raise SystemExit(f"[set {label}] failed: {res[:300]}")
    print(f"  [ok]   {label}.{fieldname} updated")


def find_custom_field_name(opener, dt, fieldname):
    """Return the auto-generated Custom Field name (e.g. 'Lead-custom_event_type')."""
    url = (f"{BASE}/api/method/frappe.client.get_list?doctype=Custom+Field"
           f"&filters=%5B%5B%22dt%22%2C%22%3D%22%2C%22{urllib.parse.quote(dt)}%22%5D%2C"
           f"%5B%22fieldname%22%2C%22%3D%22%2C%22{fieldname}%22%5D%5D"
           f"&fields=%5B%22name%22%5D")
    req = urllib.request.Request(url)
    with opener.open(req, timeout=10) as r:
        data = json.loads(r.read().decode())
    matches = data.get("message", [])
    return matches[0]["name"] if matches else None


def main():
    opener = make_opener()
    login(opener)

    # ── Step 1: Create parent DocType ──
    print("[step 1] LT Service Type DocType")
    if doctype_exists(opener, "LT Service Type"):
        print("  [skip] LT Service Type already exists")
    else:
        insert_doc(opener, SERVICE_TYPE_DOCTYPE, "DocType/LT Service Type")

    # ── Step 2: Seed 9 service type records ──
    print("[step 2] Seed service type records")
    for st in SEED_SERVICE_TYPES:
        insert_doc(opener,
                   {"doctype": "LT Service Type", "service_type": st},
                   f"LT Service Type/{st}")

    # ── Step 3: Create child DocType ──
    print("[step 3] LT Lead Service Type child DocType")
    if doctype_exists(opener, "LT Lead Service Type"):
        print("  [skip] LT Lead Service Type already exists")
    else:
        insert_doc(opener, LEAD_SERVICE_TYPE_DOCTYPE,
                   "DocType/LT Lead Service Type")

    # ── Step 4: Delete the original Select-based custom_event_type ──
    print("[step 4] Remove old Select custom_event_type field")
    cf_name = find_custom_field_name(opener, "Lead", "custom_event_type")
    if cf_name:
        old_cf_url = f"{BASE}/api/resource/Custom%20Field/{urllib.parse.quote(cf_name)}"
        with opener.open(urllib.request.Request(old_cf_url), timeout=10) as r:
            old = json.loads(r.read().decode())["data"]
        # Only delete if it's still the old Select type — don't clobber our re-creation
        if old.get("fieldtype") == "Select":
            delete_doc(opener, "Custom Field", cf_name, f"Custom Field/{cf_name}")
        else:
            print(f"  [skip] custom_event_type already {old.get('fieldtype')}")

    # ── Step 5: Re-create custom_event_type as Table MultiSelect ──
    print("[step 5] Insert custom_event_type as Table MultiSelect")
    new_cf = {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_event_type",
        "fieldtype": "Table MultiSelect",
        "label": "Service Type(s)",
        "options": "LT Lead Service Type",
        "insert_after": "lt_section_service",
        "description": ("Pick one or more services. The booking detail "
                        "sub-sections below appear automatically based on "
                        "which services are selected."),
    }
    insert_doc(opener, new_cf, "Custom Field/Lead.custom_event_type (Table MultiSelect)")

    # ── Step 6: Patch depends_on on sections + per-service note fields ──
    print("[step 6] Apply depends_on to sections + note fields")
    for fieldname, expr in DEPENDS_ON_PATCHES.items():
        cf_name = find_custom_field_name(opener, "Lead", fieldname)
        if not cf_name:
            print(f"  [skip] {fieldname} not found")
            continue
        set_field(opener, "Custom Field", cf_name, "depends_on", expr,
                  f"Custom Field/{cf_name}")

    # ── Done ──
    print()
    print("OK -> http://localhost:8081/app/lead/new")
    print("OK -> http://localhost:8081/app/lt-service-type")
    print("Refresh the Lead form. Sub-sections should now stay collapsed")
    print("until you pick a Service Type.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
