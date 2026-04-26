#!/usr/bin/env python3
"""
Translate Locally Twisted's Odoo `crm.lead` model extension into ERPNext
Lead Custom Fields on the local LT install at http://localhost:8081.

Source: locally-twisted-odoo/addons/locally_twisted/models/crm_lead.py
Target: http://localhost:8081/app/lead

Maps 35 Odoo `x_*` fields to Frappe Custom Field records on the Lead
DocType. Adds a dedicated "LT Booking Details" tab with sectioned layout
mirroring the source's commented groupings.

Field naming convention:
  Odoo:   x_event_type      (Odoo's customization-prefix convention)
  Frappe: custom_event_type (Frappe's customization-prefix convention)

The 36th field on the Odoo model — `x_task_count` — is a *computed* field
(`_compute_x_task_count`). That logic is a Server Script port (Phase 3
work, automation layer), not a field translation. Skipped here.

Author: 2026-04-26 evening session.
Pattern follows scripts/translate/translate_dashboard_review.py (Trellis).
Stdlib only — no `pip install` required.

Idempotent: API "already exists" responses are caught and the loop continues.
Safe to re-run if the script aborts partway.
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
# Field translation table.
# Each entry becomes one `Custom Field` record on the Lead DocType.
# `insert_after` chains via `_chain_inserts()` so source order is preserved.
# ──────────────────────────────────────────────────────────────────────

# (fieldtype, fieldname, label, extras_dict)
# extras_dict keys: options, default, reqd, description, in_list_view
LT_FIELDS = [
    # ── Tab break: dedicated tab for LT booking detail ──
    ("Tab Break", "lt_booking_tab", "LT Booking Details", {}),

    # ── Section: Service Type & Event ──
    ("Section Break", "lt_section_service", "Service & Event", {}),
    ("Select", "custom_event_type", "Service Type", {
        "options": "\nBalloon Arch\nBalloon Drop\nBalloon Wall\nFace Painting\n"
                   "Balloon Twisting\nCustom Installation\nEvent Package\nOther",
    }),
    ("Datetime", "custom_event_date", "Event Date", {}),
    ("Data", "custom_event_location", "Event Location", {}),
    ("Data", "custom_venue_name", "Venue Name", {}),
    ("Int", "custom_crew_size", "Crew Size Needed", {"default": "1"}),
    ("Float", "custom_setup_duration", "Setup Duration (hrs)", {"default": "2.0"}),

    # ── Section: Service Choice & Occasion (twisting/face painting form) ──
    ("Section Break", "lt_section_choice", "Service Choice & Occasion", {}),
    ("Select", "custom_service_choice", "Service Choice", {
        "options": "\nBoth — Balloon Twisting & Face Painting\n"
                   "Balloon Twisting Only\nFace Painting Only",
    }),
    ("Select", "custom_occasion_type", "Occasion Type", {
        "options": "\nBirthday Party\nSchool Event\nCorporate Event\n"
                   "Festival / Fair\nChurch Event\nFamily Reunion\n"
                   "Holiday Party\nOther",
    }),
    ("Data", "custom_event_time", "Preferred Start Time", {}),
    ("Int", "custom_guest_count", "Estimated Guests", {}),
    ("Data", "custom_hours_needed", "Hours Needed", {}),

    # ── Section: Indoor/Outdoor & Crew Counts (dynamic booking form, 2026-03-19) ──
    ("Section Break", "lt_section_dynamic", "Venue & Crew", {}),
    ("Select", "custom_indoor_outdoor", "Indoor / Outdoor", {
        "options": "\nIndoor\nOutdoor\nBoth",
    }),
    ("Check", "custom_shade_required", "Shade Required", {
        "description": "Automatically required for outdoor events",
    }),
    ("Int", "custom_num_twisters", "Number of Twisters", {}),
    ("Int", "custom_num_painters", "Number of Face Painters", {}),
    ("Data", "custom_artist_start", "Artist Start Time", {}),
    ("Data", "custom_artist_end", "Artist End Time", {}),
    ("Data", "custom_setup_time_arrival", "Setup Arrival Time", {
        "description": "What time can we arrive to set up?",
    }),
    ("Data", "custom_colors", "Color Preferences", {}),
    ("Data", "custom_decor_types", "Decor Types", {
        "description": "Entrance decor, table decor, helium balloons, etc.",
    }),
    ("Data", "custom_painter_start", "Painter Start Time", {}),
    ("Data", "custom_painter_end", "Painter End Time", {}),

    # ── Section: Multi-select Services + per-section Notes (/book form, 2026-04-23) ──
    ("Section Break", "lt_section_services", "Services Requested & Notes", {}),
    ("Data", "custom_services", "Services Requested", {
        "description": "Multi-select from /book: Balloon Decor, Balloon Twisting, "
                       "Face Painting, Delivery, Event Package, Something Else",
    }),
    ("Long Text", "custom_decor_notes", "Balloon Decor Notes", {}),
    ("Long Text", "custom_twisting_notes", "Balloon Twisting Notes", {}),
    ("Long Text", "custom_painting_notes", "Face Painting Notes", {}),
    ("Long Text", "custom_delivery_notes", "Delivery Notes", {}),
    ("Long Text", "custom_package_notes", "Event Package Notes", {}),
    ("Long Text", "custom_other_notes", "Other / Something Else Notes", {}),

    # ── Section: Relationship & Source ──
    ("Section Break", "lt_section_relationship", "Relationship & Source", {}),
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

    # ── Section: Workflow (payment terms routing + dedupe guard) ──
    ("Section Break", "lt_section_workflow", "Workflow", {}),
    ("Select", "custom_client_type", "Client Type", {
        "options": "\nPersonal / Private Party\nCorporate / Business",
        "description": "Determines payment terms: personal = 72hr prepay, corporate = Net 30",
    }),
    ("Check", "custom_booking_confirmed", "Booking Confirmed", {
        "description": "Set True after booking confirmation email is sent. "
                       "Prevents resending when a lead transitions to Won more than once.",
    }),
]


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


def insert_custom_field(opener, doc, label):
    payload = json.dumps({"doc": doc}).encode()
    req = urllib.request.Request(
        f"{BASE}/api/method/frappe.client.insert",
        data=payload,
        headers={"Content-Type": "application/json", "X-Requested-With": "XMLHttpRequest"},
    )
    try:
        with opener.open(req, timeout=30) as r:
            body = r.read().decode()
        parsed = json.loads(body)
        return parsed.get('message', {}).get('name', '?'), False
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        if 'already exists' in body or 'DuplicateEntryError' in body:
            return None, True
        raise SystemExit(f"[{label}] failed: HTTP {e.code} body={body[:300]}")


def main():
    opener = make_opener()
    login(opener)

    print(f"[translate] Inserting {len(LT_FIELDS)} Custom Fields on {TARGET_DOCTYPE}...")

    # Chain insert_after — each field positions after the previous fieldname.
    # First entry positions after Lead's standard `qualification_tab` so the
    # LT block lands right after Qualification, before Additional Information.
    previous_fieldname = "qualification_tab"

    created = 0
    skipped = 0
    for fieldtype, fieldname, label, extras in LT_FIELDS:
        doc = {
            "doctype": "Custom Field",
            "dt": TARGET_DOCTYPE,
            "fieldname": fieldname,
            "fieldtype": fieldtype,
            "label": label,
            "insert_after": previous_fieldname,
        }
        doc.update(extras)

        name, was_dup = insert_custom_field(opener, doc, fieldname)
        if was_dup:
            skipped += 1
            print(f"  [skip] {fieldtype:14} {fieldname:32} (already exists)")
        else:
            created += 1
            print(f"  [ok]   {fieldtype:14} {fieldname:32} -> {name}")

        # Chain: next field inserts after this one
        previous_fieldname = fieldname

    print()
    print(f"[summary] {created} created, {skipped} skipped (already existed)")
    print(f"OK -> http://localhost:8081/app/lead/new")
    print(f"OK -> http://localhost:8081/app/customize-form/Lead")
    return 0


if __name__ == "__main__":
    sys.exit(main())
