#!/usr/bin/env python3
"""
Realign the Lead DocType's LT Booking Details tab to match the LIVE
production booking form at http://5.78.136.133/book.

Why this revision:
  GL feedback after the multi-select revision:
    > "Not all the fields are correct. Can you look into the Odoo file
    >  for this form and make sure every field is in the correct location
    >  and the logic is correct? When the customer fills out this form
    >  the input should directly map to these exact fields."

  Discovery: the on-disk page_book.xml is STALE (Odoo's noupdate=1 +
  website-editor edits live in production arch_db, not source XML).
  The actual current form has 6 service checkboxes (not 8), per-service
  detail sections, and an Event Environment block. Pulled the truth by
  curling the public /book page and parsing the form HTML.

Target state (per the live form, top-to-bottom):

  Standard Lead fields (no Custom Field needed — already on Lead):
    contact_name → lead_name (form posts to lead_name in ERPNext)
    phone        → phone
    email_from   → email_id
    partner_name → company_name

  LT Booking Details TAB
    Section: Event Basics  (always visible)
      custom_occasion_type   ('birthday', 'school', ... — 8 options)
      custom_event_date
      custom_event_time
      custom_event_location
      custom_guest_count
      custom_event_type      (Table MultiSelect of 6 LT Service Types)

    Section: Balloon Decor Details   (when 'Balloon Decor' selected)
      custom_decor_types
      custom_setup_time_arrival
      custom_decor_notes

    Section: Balloon Twisting Details (when 'Balloon Twisting' selected)
      custom_num_twisters
      custom_artist_start
      custom_artist_end
      custom_twisting_notes

    Section: Face Painting Details   (when 'Face Painting' selected)
      custom_num_painters
      custom_painter_start
      custom_painter_end
      custom_painting_notes

    Section: Delivery Details        (when 'Delivery Only' selected)
      custom_delivery_notes

    Section: Event Package Details   (when 'Event Package' selected)
      custom_package_notes

    Section: Something Else Details  (when 'Something Else' selected)
      custom_other_notes

    Section: Event Environment       (when ANY service selected)
      custom_indoor_outdoor
      custom_shade_required
      custom_colors

    Section: Anything Else           (always visible)
      custom_anything_else  (Long Text — maps to form's `description`)

    Section: Internal — Relationship & Workflow  (always visible, admin-only)
      custom_next_anniversary_date
      custom_referred_by
      custom_source_channel
      custom_taken_by
      custom_client_type
      custom_booking_confirmed

Removed (not on the live form, were artifacts of an earlier "twisting +
face painting page" form that's been superseded):
  custom_venue_name, custom_crew_size, custom_setup_duration,
  custom_service_choice, custom_hours_needed, custom_services

Service Type seed updated from 9 → 6 to match the form's checklist.

Customer/Contact dedup logic (Odoo's `_find_matching_partner` behavior
in crm_lead.py) is NOT implemented here — that's Phase 3 (Server Script
on Lead before_insert). Tracked in queue.

Idempotent: each step checks-or-skips. Safe to re-run.
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
# Service Types — 6 canonical, matching the live /book form's checkboxes
# ──────────────────────────────────────────────────────────────────────
CANONICAL_SERVICES = [
    "Balloon Decor",
    "Balloon Twisting",
    "Face Painting",
    "Delivery Only",
    "Event Package",
    "Something Else",
]

# Old 9-service seed from prior fix — delete any not in the new canonical 6
OLD_SERVICES_TO_REMOVE = [
    "Balloon Arch", "Balloon Drop", "Balloon Wall", "Custom Installation",
    "Delivery", "Other",
]


# ──────────────────────────────────────────────────────────────────────
# Custom Fields to DELETE (obsolete: artifacts of older forms)
# ──────────────────────────────────────────────────────────────────────
OBSOLETE_FIELDS = [
    # Old service-detail fields (not on the live /book form):
    "custom_venue_name",
    "custom_crew_size",
    "custom_setup_duration",
    "custom_service_choice",       # was from twisting+face-painting page
    "custom_hours_needed",
    "custom_services",             # redundant — custom_event_type IS the multi-select
    # Old section breaks (will be re-inserted with new structure):
    "lt_section_service",          # → lt_section_basics
    "lt_section_choice",           # removed
    "lt_section_dynamic",          # → split into per-service sections
    "lt_section_services",         # → split into per-service sections
    "lt_section_relationship",     # → lt_section_internal
    "lt_section_workflow",         # → lt_section_internal
]


# ──────────────────────────────────────────────────────────────────────
# Helper: depends_on JS for a Table MultiSelect with specific service rows
# ──────────────────────────────────────────────────────────────────────
def _selected(svcs):
    """Return depends_on expr matching when ANY of svcs is in custom_event_type."""
    quoted = ",".join(f"'{s}'" for s in svcs)
    return ("eval:doc.custom_event_type "
            "&& doc.custom_event_type.some(function(r){"
            f"return [{quoted}].indexOf(r.service_type) !== -1;"
            "})")

ANY_SERVICE_SELECTED = ("eval:doc.custom_event_type "
                        "&& doc.custom_event_type.length > 0")


# ──────────────────────────────────────────────────────────────────────
# Target field layout — declarative state.
# Each entry: (fieldtype, fieldname, label, extras_dict)
# Order = render order. insert_after gets chained automatically.
# ──────────────────────────────────────────────────────────────────────
TARGET_LAYOUT = [
    # ── Tab break: dedicated tab for LT booking detail ──
    ("Tab Break", "lt_booking_tab", "LT Booking Details", {}),

    # ── Section: Event Basics (always visible) ──
    ("Section Break", "lt_section_basics", "Event Basics", {}),
    ("Select", "custom_occasion_type", "What are they celebrating?", {
        "options": "\nBirthday Party\nSchool Event\nCorporate Event\n"
                   "Festival / Fair\nChurch Event\nFamily Reunion\n"
                   "Holiday Party\nOther",
    }),
    ("Date", "custom_event_date", "Event Date", {}),
    ("Data", "custom_event_time", "Preferred Event Time", {
        "description": "Form posts time-of-day as text (e.g. '14:30').",
    }),
    ("Data", "custom_event_location", "City / Location", {
        "description": "Address, venue name, or city",
    }),
    ("Int", "custom_guest_count", "Estimated Guests", {}),
    ("Table MultiSelect", "custom_event_type", "Service Type(s)", {
        "options": "LT Lead Service Type",
        "description": ("Pick one or more services. The booking detail "
                        "sub-sections appear automatically based on which "
                        "services are selected."),
    }),

    # ── Section: Balloon Decor Details ──
    ("Section Break", "lt_section_decor", "Balloon Decor Details", {
        "depends_on": _selected(["Balloon Decor"]),
    }),
    ("Data", "custom_decor_types", "Decor Types", {
        "description": "Entrance decor, table decor, backdrop, columns...",
    }),
    ("Data", "custom_setup_time_arrival", "Setup Arrival Time", {
        "description": "What time can we arrive to set up?",
    }),
    ("Long Text", "custom_decor_notes", "Decor Notes", {
        "description": "Size, style, any special requirements...",
    }),

    # ── Section: Balloon Twisting Details ──
    ("Section Break", "lt_section_twisting", "Balloon Twisting Details", {
        "depends_on": _selected(["Balloon Twisting"]),
    }),
    ("Int", "custom_num_twisters", "Number of Twisters", {}),
    ("Data", "custom_artist_start", "Twister Start Time", {}),
    ("Data", "custom_artist_end", "Twister End Time", {}),
    ("Long Text", "custom_twisting_notes", "Twisting Notes", {
        "description": "Special requests, character themes...",
    }),

    # ── Section: Face Painting Details ──
    ("Section Break", "lt_section_painting", "Face Painting Details", {
        "depends_on": _selected(["Face Painting"]),
    }),
    ("Int", "custom_num_painters", "Number of Face Painters", {}),
    ("Data", "custom_painter_start", "Painter Start Time", {}),
    ("Data", "custom_painter_end", "Painter End Time", {}),
    ("Long Text", "custom_painting_notes", "Face Painting Notes", {
        "description": "Design preferences, age range of kids...",
    }),

    # ── Section: Delivery Details ──
    ("Section Break", "lt_section_delivery", "Delivery Details", {
        "depends_on": _selected(["Delivery Only"]),
    }),
    ("Long Text", "custom_delivery_notes", "Delivery Notes", {
        "description": "When do you need delivery? Morning, afternoon, specific time...",
    }),

    # ── Section: Event Package Details ──
    ("Section Break", "lt_section_package", "Event Package Details", {
        "depends_on": _selected(["Event Package"]),
    }),
    ("Long Text", "custom_package_notes", "Event Package Notes", {
        "description": "Describe your ideal event package...",
    }),

    # ── Section: Something Else Details ──
    ("Section Break", "lt_section_other", "Something Else Details", {
        "depends_on": _selected(["Something Else"]),
    }),
    ("Long Text", "custom_other_notes", "Something Else Notes", {
        "description": "Tell us about your idea...",
    }),

    # ── Section: Event Environment (any service selected) ──
    ("Section Break", "lt_section_environment", "Event Environment", {
        "depends_on": ANY_SERVICE_SELECTED,
    }),
    ("Select", "custom_indoor_outdoor", "Indoor / Outdoor", {
        "options": "\nIndoor\nOutdoor\nBoth",
    }),
    ("Check", "custom_shade_required", "Shade Required", {
        "description": "Automatically required for outdoor events",
    }),
    ("Data", "custom_colors", "Color Preferences", {
        "description": "Specific colors, brand colors, theme colors...",
    }),

    # ── Section: Anything Else (always visible) ──
    ("Section Break", "lt_section_anything_else", "Anything Else", {}),
    ("Long Text", "custom_anything_else", "Anything else we should know?", {
        "description": "Form posts to `description`. Map at form-handler layer.",
    }),

    # ── Section: Internal — Relationship & Workflow (admin-only) ──
    ("Section Break", "lt_section_internal",
     "Internal — Relationship & Workflow", {
         "collapsible": 1,
     }),
    ("Date", "custom_next_anniversary_date", "Next Anniversary", {}),
    ("Link", "custom_referred_by", "Referred By (Contact)", {
        "options": "Contact",
    }),
    ("Select", "custom_source_channel", "Source Channel", {
        "options": "\nPhone Call\nEmail\nText Message\nIn Person\nWebsite Form",
        "description": "How did this lead come in?",
    }),
    ("Link", "custom_taken_by", "Taken By", {
        "options": "User",
        "description": "Who received this inquiry (Jeff, Julie, etc.)",
    }),
    ("Select", "custom_client_type", "Client Type", {
        "options": "\nPersonal / Private Party\nCorporate / Business",
        "description": "Determines payment terms: personal = 72hr prepay, corporate = Net 30",
    }),
    ("Check", "custom_booking_confirmed", "Booking Confirmed", {
        "description": "Set True after booking confirmation email is sent. "
                       "Prevents resending when a lead transitions to Won more than once.",
    }),
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
    """Return the Custom Field doc (dict) or None."""
    url = (f"{BASE}/api/method/frappe.client.get_list?doctype=Custom+Field"
           f"&filters=%5B%5B%22dt%22%2C%22%3D%22%2C%22{urllib.parse.quote(dt)}%22%5D%2C"
           f"%5B%22fieldname%22%2C%22%3D%22%2C%22{fieldname}%22%5D%5D"
           f"&fields=%5B%22name%22%2C%22fieldtype%22%5D")
    req = urllib.request.Request(url)
    with opener.open(req, timeout=10) as r:
        data = json.loads(r.read().decode())
    matches = data.get("message", [])
    return matches[0] if matches else None


def delete_doc(opener, doctype, name):
    res, err = call(opener, "frappe.client.delete",
                    {"doctype": doctype, "name": name})
    if err:
        if 'DoesNotExistError' in res or 'not found' in res.lower():
            return False
        print(f"  [warn] delete {doctype}/{name}: {res[:200]}")
        return False
    return True


def insert_doc(opener, doc, label):
    res, err = call(opener, "frappe.client.insert", {"doc": doc})
    if err:
        if 'already exists' in res or 'DuplicateEntryError' in res:
            return None, True
        raise SystemExit(f"[{label}] insert failed: {res[:300]}")
    return res.get('message', {}), False


def set_field(opener, doctype, name, fieldname, value):
    res, err = call(opener, "frappe.client.set_value", {
        "doctype": doctype, "name": name, "fieldname": fieldname, "value": value,
    })
    if err:
        print(f"  [warn] set {doctype}/{name}.{fieldname}: {res[:200]}")


def list_service_types(opener):
    url = (f"{BASE}/api/method/frappe.client.get_list?doctype=LT+Service+Type"
           f"&fields=%5B%22name%22%5D&limit_page_length=100")
    req = urllib.request.Request(url)
    with opener.open(req, timeout=10) as r:
        return [r["name"] for r in json.loads(r.read().decode()).get("message", [])]


# ──────────────────────────────────────────────────────────────────────
# Main flow
# ──────────────────────────────────────────────────────────────────────
def main():
    opener = make_opener()
    login(opener)

    # ── Step 1: Reseed LT Service Type to canonical 6 ──
    print("[step 1] Reseed LT Service Type → 6 canonical")
    existing = set(list_service_types(opener))
    desired = set(CANONICAL_SERVICES)
    for st in existing - desired:
        if delete_doc(opener, "LT Service Type", st):
            print(f"  [del]  {st}")
        else:
            print(f"  [skip] {st} (could not delete — may be linked to existing Lead rows)")
    for st in desired - existing:
        doc, dup = insert_doc(opener, {"doctype": "LT Service Type", "service_type": st},
                              f"LT Service Type/{st}")
        print(f"  [ok]   {st}")

    # ── Step 2: Delete obsolete Custom Fields ──
    print("[step 2] Delete obsolete Custom Fields")
    for fn in OBSOLETE_FIELDS:
        cf = find_custom_field(opener, TARGET_DOCTYPE, fn)
        if cf:
            if delete_doc(opener, "Custom Field", cf["name"]):
                print(f"  [del]  {fn}")
            else:
                print(f"  [warn] {fn} could not be deleted")
        else:
            print(f"  [skip] {fn} (already absent)")

    # ── Step 3: Walk TARGET_LAYOUT — insert missing, update existing ──
    print(f"[step 3] Apply target layout ({len(TARGET_LAYOUT)} elements)")
    previous_fieldname = "qualification_tab"  # Lead's standard tab break
    for fieldtype, fieldname, label, extras in TARGET_LAYOUT:
        cf = find_custom_field(opener, TARGET_DOCTYPE, fieldname)
        if cf:
            # EXISTS — update its config to match TARGET_LAYOUT
            updates = {
                "label": label,
                "fieldtype": fieldtype,
                "insert_after": previous_fieldname,
            }
            updates.update(extras)
            for k, v in updates.items():
                set_field(opener, "Custom Field", cf["name"], k, v)
            print(f"  [upd]  {fieldtype:18} {fieldname:32}")
        else:
            # NEW — insert
            doc = {
                "doctype": "Custom Field",
                "dt": TARGET_DOCTYPE,
                "fieldname": fieldname,
                "fieldtype": fieldtype,
                "label": label,
                "insert_after": previous_fieldname,
            }
            doc.update(extras)
            insert_doc(opener, doc, f"Custom Field/{fieldname}")
            print(f"  [new]  {fieldtype:18} {fieldname:32}")
        previous_fieldname = fieldname

    # ── Done ──
    print()
    print("OK -> http://localhost:8081/app/lead/new")
    print("OK -> http://localhost:8081/app/customize-form/Lead")
    print()
    print("Refresh the Lead form. You should see one section per service,")
    print("each appearing only when its service is selected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
