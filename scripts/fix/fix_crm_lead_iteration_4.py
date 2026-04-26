#!/usr/bin/env python3
"""
Iteration 4 of the Lead form refinement, addressing GL feedback after
iteration 3:

  1. Delivery Only is a non-event service. Hide event-specific fields
     (Event Start Time, Event End Time, Estimated Guests) when Delivery
     Only is the ONLY service selected. Add Delivery Window Start + End
     Time fields inside the Delivery Details section.
  2. Switch all time-of-day Custom Fields from `Data` to `Time` fieldtype.
     Frappe's Time picker uses the browser's <input type="time"> which on
     US-locale Chrome/Edge typically renders as AM/PM. Remove the
     "Format: 12-hour..." description hints (GL: customers/employees know
     what AM/PM is).
  3. Remove `custom_next_anniversary_date` from Internal section.
  4. Property Setters to relabel standard Lead fields with plain language:
     - qualified_by:        "Qualified By"        -> "Reviewed and First Contact By"
     - qualified_on:        "Qualified on"        -> "Reviewed On"
     - qualification_status:"Qualification Status"-> "Status of Inquiry"
     (Standing directive 2026-04-26: take business jargon out of LT's UI.)
  5. Add Inspiration Photos as a child table on Lead (up to 5 photos).
     Bump System Settings.max_file_size to 25 MB. Hard limit-of-5 needs
     a Server Script (queued for Phase 3).
  6. Add `custom_internal_notes` Long Text inside Internal section.
  7. Hide standard Lead's "Additional Information" tab (other_info_tab)
     — none of its 8 fields fit a balloon business.

Frappe blocks in-place fieldtype change for some pairs (Data->Time);
script handles via delete + recreate. No data loss because no Lead
records exist yet.

Idempotent. Stdlib only. Safe to re-run.
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

MAX_UPLOAD_BYTES = 25 * 1024 * 1024  # 25 MB

# ──────────────────────────────────────────────────────────────────────
# Time fields to migrate from Data to Time
# ──────────────────────────────────────────────────────────────────────
TIME_FIELDS_DATA_TO_TIME = [
    "custom_event_time",
    "custom_event_end_time",
    "custom_setup_time_arrival",
    "custom_artist_start",
    "custom_artist_end",
    "custom_painter_start",
    "custom_painter_end",
]

# ──────────────────────────────────────────────────────────────────────
# depends_on expressions
# ──────────────────────────────────────────────────────────────────────
def _selected(svcs):
    quoted = ",".join(f"'{s}'" for s in svcs)
    return ("eval:doc.custom_event_type "
            "&& doc.custom_event_type.some(function(r){"
            f"return [{quoted}].indexOf(r.service_type) !== -1;"
            "})")

# Hide event-specific fields when ONLY 'Delivery Only' is selected.
# Show when: nothing selected, OR at least one selected service is NOT Delivery Only.
EVENT_VISIBLE_DEPENDS_ON = (
    "eval:!doc.custom_event_type "
    "|| doc.custom_event_type.length === 0 "
    "|| doc.custom_event_type.some(function(r){"
    "return r.service_type !== 'Delivery Only';"
    "})"
)


# ──────────────────────────────────────────────────────────────────────
# Photo child DocType
# ──────────────────────────────────────────────────────────────────────
LEAD_PHOTO_DOCTYPE = {
    "doctype": "DocType",
    "name": "LT Lead Photo",
    "module": "Custom",
    "custom": 1,
    "istable": 1,
    "fields": [
        {
            "fieldname": "photo",
            "label": "Photo",
            "fieldtype": "Attach Image",
            "reqd": 1,
        },
        {
            "fieldname": "caption",
            "label": "Caption",
            "fieldtype": "Data",
            "in_list_view": 1,
        },
    ],
    "permissions": [],
}


# ──────────────────────────────────────────────────────────────────────
# Property Setters for label renames on standard Lead fields
# ──────────────────────────────────────────────────────────────────────
PROPERTY_SETTERS = [
    {
        "doctype_or_field": "DocField",
        "doc_type": "Lead",
        "field_name": "qualified_by",
        "property": "label",
        "value": "Reviewed and First Contact By",
        "property_type": "Data",
    },
    {
        "doctype_or_field": "DocField",
        "doc_type": "Lead",
        "field_name": "qualified_on",
        "property": "label",
        "value": "Reviewed On",
        "property_type": "Data",
    },
    {
        "doctype_or_field": "DocField",
        "doc_type": "Lead",
        "field_name": "qualification_status",
        "property": "label",
        "value": "Status of Inquiry",
        "property_type": "Data",
    },
    # Hide the "Additional Information" tab entirely
    {
        "doctype_or_field": "DocField",
        "doc_type": "Lead",
        "field_name": "other_info_tab",
        "property": "hidden",
        "value": "1",
        "property_type": "Check",
    },
]


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
           f"&fields=%5B%22name%22%2C%22fieldtype%22%2C%22insert_after%22%2C%22label%22%5D")
    req = urllib.request.Request(url)
    with opener.open(req, timeout=10) as r:
        data = json.loads(r.read().decode())
    matches = data.get("message", [])
    return matches[0] if matches else None


def doctype_exists(opener, name):
    url = f"{BASE}/api/resource/DocType/{urllib.parse.quote(name)}"
    try:
        with opener.open(urllib.request.Request(url), timeout=10) as r:
            return r.status == 200
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False
        raise


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


def find_property_setter(opener, doc_type, field_name, prop):
    """Find existing Property Setter for this (doctype, field, property)."""
    flt = json.dumps([
        ["doc_type", "=", doc_type],
        ["field_name", "=", field_name],
        ["property", "=", prop],
    ])
    url = (f"{BASE}/api/method/frappe.client.get_list?doctype=Property+Setter"
           f"&filters={urllib.parse.quote(flt)}&fields=%5B%22name%22%5D")
    req = urllib.request.Request(url)
    with opener.open(req, timeout=10) as r:
        data = json.loads(r.read().decode())
    matches = data.get("message", [])
    return matches[0]["name"] if matches else None


# ──────────────────────────────────────────────────────────────────────
# Main flow
# ──────────────────────────────────────────────────────────────────────
def main():
    opener = make_opener()
    login(opener)

    # ── Step A: Switch time Data fields to Time fieldtype ──
    print("[step A] Migrate time fields Data -> Time (delete + recreate)")
    for fn in TIME_FIELDS_DATA_TO_TIME:
        cf = find_custom_field(opener, TARGET_DOCTYPE, fn)
        if not cf:
            print(f"  [skip] {fn} not found")
            continue
        if cf["fieldtype"] == "Time":
            print(f"  [skip] {fn} already Time")
            continue
        # Save its position + label before deletion
        position_after = cf["insert_after"]
        label = cf["label"]
        if delete_doc(opener, "Custom Field", cf["name"]):
            insert_doc(opener, {
                "doctype": "Custom Field",
                "dt": TARGET_DOCTYPE,
                "fieldname": fn,
                "fieldtype": "Time",
                "label": label,
                "insert_after": position_after,
                "description": "",
            }, f"Custom Field/{fn} (Time)")

    # ── Step B: Add Delivery Window Start + End Time fields ──
    print("[step B] Add Delivery Window Time fields")
    if not find_custom_field(opener, TARGET_DOCTYPE, "custom_delivery_window_start"):
        insert_doc(opener, {
            "doctype": "Custom Field",
            "dt": TARGET_DOCTYPE,
            "fieldname": "custom_delivery_window_start",
            "fieldtype": "Time",
            "label": "Delivery Window Start",
            "insert_after": "lt_section_delivery",
        }, "Custom Field/custom_delivery_window_start")
    if not find_custom_field(opener, TARGET_DOCTYPE, "custom_delivery_window_end"):
        insert_doc(opener, {
            "doctype": "Custom Field",
            "dt": TARGET_DOCTYPE,
            "fieldname": "custom_delivery_window_end",
            "fieldtype": "Time",
            "label": "Delivery Window End",
            "insert_after": "custom_delivery_window_start",
        }, "Custom Field/custom_delivery_window_end")
    # Reposition delivery_notes to come after the window fields
    cf = find_custom_field(opener, TARGET_DOCTYPE, "custom_delivery_notes")
    if cf:
        set_field(opener, "Custom Field", cf["name"], "insert_after",
                  "custom_delivery_window_end")

    # ── Step C: Hide event-specific fields when only Delivery Only selected ──
    print("[step C] depends_on event fields: hide if Delivery Only is sole service")
    for fn in ["custom_event_time", "custom_event_end_time", "custom_guest_count"]:
        cf = find_custom_field(opener, TARGET_DOCTYPE, fn)
        if cf:
            set_field(opener, "Custom Field", cf["name"], "depends_on",
                      EVENT_VISIBLE_DEPENDS_ON)

    # ── Step D: Remove custom_next_anniversary_date ──
    print("[step D] Remove custom_next_anniversary_date")
    cf = find_custom_field(opener, TARGET_DOCTYPE, "custom_next_anniversary_date")
    if cf:
        if delete_doc(opener, "Custom Field", cf["name"]):
            print(f"  [del]  custom_next_anniversary_date")
    else:
        print("  [skip] already absent")

    # ── Step E: Add custom_internal_notes Long Text in Internal section ──
    print("[step E] Add custom_internal_notes")
    if not find_custom_field(opener, TARGET_DOCTYPE, "custom_internal_notes"):
        # Position right after the section break (top of Internal section)
        insert_doc(opener, {
            "doctype": "Custom Field",
            "dt": TARGET_DOCTYPE,
            "fieldname": "custom_internal_notes",
            "fieldtype": "Long Text",
            "label": "Internal Only Notes",
            "description": "Visible to staff only — never shown to the customer.",
            "insert_after": "lt_section_internal",
        }, "Custom Field/custom_internal_notes")
    else:
        print("  [skip] custom_internal_notes already exists")

    # ── Step F: Inspiration Photos child table + Lead field ──
    print("[step F] Inspiration Photos (child DocType + Table on Lead)")
    if not doctype_exists(opener, "LT Lead Photo"):
        insert_doc(opener, LEAD_PHOTO_DOCTYPE, "DocType/LT Lead Photo")
    else:
        print("  [skip] LT Lead Photo DocType already exists")
    # Add a Section Break + Table field for the photos
    if not find_custom_field(opener, TARGET_DOCTYPE, "lt_section_photos"):
        insert_doc(opener, {
            "doctype": "Custom Field",
            "dt": TARGET_DOCTYPE,
            "fieldname": "lt_section_photos",
            "fieldtype": "Section Break",
            "label": "Inspiration Photos",
            "description": "Up to 5 photos, 25 MB each.",
            "insert_after": "lt_section_environment",
        }, "Custom Field/lt_section_photos")
    if not find_custom_field(opener, TARGET_DOCTYPE, "custom_inspiration_photos"):
        insert_doc(opener, {
            "doctype": "Custom Field",
            "dt": TARGET_DOCTYPE,
            "fieldname": "custom_inspiration_photos",
            "fieldtype": "Table",
            "label": "Inspiration Photos",
            "options": "LT Lead Photo",
            "insert_after": "lt_section_photos",
        }, "Custom Field/custom_inspiration_photos")

    # ── Step G: Property Setters (label renames + tab hide) ──
    print("[step G] Property Setters: relabel standard fields, hide other_info_tab")
    for ps in PROPERTY_SETTERS:
        existing = find_property_setter(opener, ps["doc_type"], ps["field_name"], ps["property"])
        if existing:
            set_field(opener, "Property Setter", existing, "value", ps["value"])
        else:
            insert_doc(opener, {"doctype": "Property Setter", **ps},
                       f"Property Setter/{ps['doc_type']}-{ps['field_name']}-{ps['property']}")

    # ── Step H: System Settings.max_file_size = 25 MB ──
    print(f"[step H] System Settings.max_file_size -> {MAX_UPLOAD_BYTES} bytes (25 MB)")
    set_field(opener, "System Settings", "System Settings",
              "max_file_size", MAX_UPLOAD_BYTES)

    print()
    print("OK -> http://localhost:8081/app/lead/new")
    print()
    print("Verify:")
    print("  - Time fields show a real time picker (browser-native; AM/PM on US Chrome/Edge)")
    print("  - Pick ONLY 'Delivery Only': Event Start/End Time + Guest Count hidden;")
    print("    Delivery Details shows Delivery Window Start/End + Notes")
    print("  - Pick 'Delivery Only' + 'Balloon Decor': all event fields visible")
    print("  - 'Additional Information' tab is gone from the top of the form")
    print("  - Internal section has 'Internal Only Notes' Long Text + photo gallery")
    print("  - 'Reviewed and First Contact By' / 'Reviewed On' / 'Status of Inquiry'")
    print("    are the new labels in the Qualification section")
    return 0


if __name__ == "__main__":
    sys.exit(main())
