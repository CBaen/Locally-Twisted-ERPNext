#!/usr/bin/env python3
"""
Iteration 3 of the Lead form refinement, addressing GL feedback after
the book-form-alignment pass:

  1. Service Type chooser must sit ABOVE "What are they celebrating?"
     (most important field; should anchor the section visually).
  2. Event Environment block does NOT apply to "Delivery Only" — that
     service has no on-site setup, just a drop-off.
  3. "Shade Required" only applies to Face Painting + Balloon Twisting
     (artists are outdoors with the customers' guests). Move it from
     section-level to its own field-level depends_on.
  4. Event Date should be Date-only, not Datetime. The earlier fix
     script could not change the fieldtype in-place (Frappe blocks
     Datetime → Date conversion to prevent silent data loss). Recreate
     it. No data loss because no Lead records exist yet.
  5. Replace "Preferred Event Time" with "Event Start Time" + add
     "Event End Time" — both phrased "(even an estimate is helpful!)"
     to lower customer friction on partially-known events.
  6. ALL time fields display AM/PM, not 24-hour military. The customer
     base is largely socialite-style clientele who don't read military
     time. Set description hints on every time field; label cue too.

Customer-facing form update (Odoo /book page) is a parallel task GL
will run separately — locally-twisted-odoo is read-only from this
project per the 2026-04-25 directive. Tracked in queue.

Idempotent: safe to re-run.
Stdlib only.
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
TARGET_DOCTYPE = "Lead"


# ──────────────────────────────────────────────────────────────────────
# Time field set — every field that captures a time-of-day
# ──────────────────────────────────────────────────────────────────────
TIME_FIELDS = [
    "custom_event_time",
    "custom_event_end_time",      # new in this iteration
    "custom_setup_time_arrival",
    "custom_artist_start",
    "custom_artist_end",
    "custom_painter_start",
    "custom_painter_end",
]

AMPM_HINT = "Format: 12-hour with AM/PM (e.g. 2:30 PM, 10:00 AM)"


# ──────────────────────────────────────────────────────────────────────
# depends_on expressions
# ──────────────────────────────────────────────────────────────────────
def _selected(svcs):
    quoted = ",".join(f"'{s}'" for s in svcs)
    return ("eval:doc.custom_event_type "
            "&& doc.custom_event_type.some(function(r){"
            f"return [{quoted}].indexOf(r.service_type) !== -1;"
            "})")

# Event Environment shows when ANY service EXCEPT "Delivery Only" is selected.
ENVIRONMENT_DEPENDS_ON = _selected([
    "Balloon Decor", "Balloon Twisting", "Face Painting",
    "Event Package", "Something Else",
])

# Shade Required only when Twisting OR Face Painting is selected.
SHADE_DEPENDS_ON = _selected(["Balloon Twisting", "Face Painting"])


# ──────────────────────────────────────────────────────────────────────
# HTTP plumbing
# ──────────────────────────────────────────────────────────────────────
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
    req = urllib.request.Request(
        f"{BASE}/api/method/{method}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "X-Requested-With": "XMLHttpRequest"},
    )
    try:
        with opener.open(req, timeout=timeout) as r:
            return json.loads(r.read().decode()), False
    except urllib.error.HTTPError as e:
        return e.read().decode(), True


def find_custom_field(opener, dt, fieldname):
    url = (f"{BASE}/api/method/frappe.client.get_list?doctype=Custom+Field"
           f"&filters=%5B%5B%22dt%22%2C%22%3D%22%2C%22{urllib.parse.quote(dt)}%22%5D%2C"
           f"%5B%22fieldname%22%2C%22%3D%22%2C%22{fieldname}%22%5D%5D"
           f"&fields=%5B%22name%22%2C%22fieldtype%22%2C%22insert_after%22%5D")
    req = urllib.request.Request(url)
    with opener.open(req, timeout=10) as r:
        data = json.loads(r.read().decode())
    matches = data.get("message", [])
    return matches[0] if matches else None


def delete_doc(opener, doctype, name):
    res, err = call(opener, "frappe.client.delete",
                    {"doctype": doctype, "name": name})
    if err and 'DoesNotExistError' not in res:
        print(f"  [warn] delete {doctype}/{name}: {res[:200]}")
        return False
    return True


def insert_doc(opener, doc, label):
    res, err = call(opener, "frappe.client.insert", {"doc": doc})
    if err:
        if 'already exists' in res or 'DuplicateEntryError' in res:
            print(f"  [skip] {label} already exists")
            return None
        raise SystemExit(f"[{label}] insert failed: {res[:300]}")
    name = res.get('message', {}).get('name', '?')
    print(f"  [ok]   {label} -> {name}")
    return res


def set_field(opener, doctype, name, fieldname, value, quiet=False):
    res, err = call(opener, "frappe.client.set_value", {
        "doctype": doctype, "name": name, "fieldname": fieldname, "value": value,
    })
    if err:
        print(f"  [warn] set {doctype}/{name}.{fieldname}: {res[:200]}")
        return False
    if not quiet:
        print(f"  [ok]   {doctype}/{name}.{fieldname} updated")
    return True


# ──────────────────────────────────────────────────────────────────────
# Main flow
# ──────────────────────────────────────────────────────────────────────
def main():
    opener = make_opener()
    login(opener)

    # ── (4) Recreate custom_event_date as Date ──
    print("[step 4] Recreate custom_event_date as Date")
    cf = find_custom_field(opener, TARGET_DOCTYPE, "custom_event_date")
    if cf and cf.get("fieldtype") == "Datetime":
        if delete_doc(opener, "Custom Field", cf["name"]):
            print(f"  [del]  custom_event_date (was {cf['fieldtype']})")
    elif cf and cf.get("fieldtype") == "Date":
        print(f"  [skip] custom_event_date already Date")
    # Insert (or reinsert) after custom_occasion_type
    if not find_custom_field(opener, TARGET_DOCTYPE, "custom_event_date"):
        insert_doc(opener, {
            "doctype": "Custom Field",
            "dt": TARGET_DOCTYPE,
            "fieldname": "custom_event_date",
            "fieldtype": "Date",
            "label": "Event Date",
            "insert_after": "custom_occasion_type",
        }, "Custom Field/custom_event_date")

    # ── (5a) Add custom_event_end_time (new field) ──
    print("[step 5a] Add custom_event_end_time")
    if not find_custom_field(opener, TARGET_DOCTYPE, "custom_event_end_time"):
        insert_doc(opener, {
            "doctype": "Custom Field",
            "dt": TARGET_DOCTYPE,
            "fieldname": "custom_event_end_time",
            "fieldtype": "Data",
            "label": "Event End Time (even an estimate is helpful!)",
            "description": AMPM_HINT,
            "insert_after": "custom_event_time",
        }, "Custom Field/custom_event_end_time")
    else:
        print("  [skip] custom_event_end_time already exists")

    # ── (5b) Rename custom_event_time label + description ──
    print("[step 5b] Update custom_event_time label")
    cf = find_custom_field(opener, TARGET_DOCTYPE, "custom_event_time")
    if cf:
        set_field(opener, "Custom Field", cf["name"], "label",
                  "Event Start Time (even an estimate is helpful!)")
        set_field(opener, "Custom Field", cf["name"], "description", AMPM_HINT)

    # ── (6) AM/PM hint on every time field ──
    print("[step 6] AM/PM hint on time fields")
    for fn in TIME_FIELDS:
        cf = find_custom_field(opener, TARGET_DOCTYPE, fn)
        if not cf:
            print(f"  [skip] {fn} not found")
            continue
        set_field(opener, "Custom Field", cf["name"], "description", AMPM_HINT, quiet=True)
        print(f"  [ok]   {fn}.description = AM/PM hint")

    # ── (1) Reorder: Service Type ABOVE Occasion ──
    print("[step 1] Move Service Type above Occasion")
    et = find_custom_field(opener, TARGET_DOCTYPE, "custom_event_type")
    oc = find_custom_field(opener, TARGET_DOCTYPE, "custom_occasion_type")
    ed = find_custom_field(opener, TARGET_DOCTYPE, "custom_event_date")
    if et and oc:
        # custom_event_type goes right under the section break
        set_field(opener, "Custom Field", et["name"], "insert_after", "lt_section_basics")
        # custom_occasion_type comes after custom_event_type
        set_field(opener, "Custom Field", oc["name"], "insert_after", "custom_event_type")
        # custom_event_date comes after custom_occasion_type (preserves chain)
        if ed:
            set_field(opener, "Custom Field", ed["name"], "insert_after", "custom_occasion_type")

    # ── (2) Event Environment depends_on: exclude Delivery Only ──
    print("[step 2] Event Environment: exclude Delivery Only")
    cf = find_custom_field(opener, TARGET_DOCTYPE, "lt_section_environment")
    if cf:
        set_field(opener, "Custom Field", cf["name"], "depends_on", ENVIRONMENT_DEPENDS_ON)

    # ── (3) Shade Required: only Twisting + Face Painting ──
    print("[step 3] Shade Required depends_on: Twisting/Face Painting only")
    cf = find_custom_field(opener, TARGET_DOCTYPE, "custom_shade_required")
    if cf:
        set_field(opener, "Custom Field", cf["name"], "depends_on", SHADE_DEPENDS_ON)

    print()
    print("OK -> http://localhost:8081/app/lead/new")
    print()
    print("Hard refresh and verify:")
    print("  - Service Type pill chooser is ABOVE 'What are they celebrating?'")
    print("  - Event Date is a date-only picker (no time component)")
    print("  - 'Event Start Time' + 'Event End Time' both visible (with AM/PM hint)")
    print("  - Delivery Only selected -> NO Event Environment section")
    print("  - Other services selected -> Event Environment shows, but Shade Required only")
    print("    appears when Twisting OR Face Painting is in the selection")
    return 0


if __name__ == "__main__":
    sys.exit(main())
