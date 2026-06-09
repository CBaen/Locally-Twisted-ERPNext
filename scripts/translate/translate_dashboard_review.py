#!/usr/bin/env python3
"""
Translate Locally Twisted's legacy_source `lt.dashboard.review` model into a Frappe
Custom DocType in the local LT ERPNext install at http://localhost:8081.

Source: locally-twisted-legacy_source/addons/locally_twisted/models/dashboard_review.py
Target: http://localhost:8081/app/doctype/dashboard-reviewed-item

This is the first model translation in the LT legacy_source->ERPNext migration.
Stdlib only (urllib + json) — no `pip install` required.

Pattern proven here is the on-ramp for the remaining model translations:
  - 7 standard-extension models (just need Custom Fields, not new DocTypes)
  - 1 more custom domain model (twilio_service.py)

Author: Trellis (Opus 4.7), 2026-04-25 evening.
"""

import json
import sys
import urllib.parse
import urllib.request
from http.cookiejar import CookieJar


BASE = "http://localhost:8081"
USER = "Administrator"
PWD = "admin"

DOCTYPE_NAME = "Dashboard Reviewed Item"

# Field schema mirroring legacy_source's lt.dashboard.review with Frappe-native types.
# Notes inline explain divergences from the legacy_source source.
FIELDS = [
    {
        "fieldname": "user",
        "label": "User",
        "fieldtype": "Link",
        "options": "User",                  # Frappe's User DocType ~ legacy_source res.users
        "reqd": 1,
        "default": "__user",                # Frappe convention: current session user
        "in_list_view": 1,
    },
    {
        "fieldname": "source_doctype",
        "label": "Source DocType",
        "fieldtype": "Link",
        "options": "DocType",               # Elegant: every Frappe model IS a DocType record
        "reqd": 1,
        "in_list_view": 1,
        "description": "The DocType of the reviewed item (e.g. 'Lead', 'Sales Order').",
    },
    {
        "fieldname": "source_name",
        "label": "Source Record Name",
        "fieldtype": "Data",
        "reqd": 1,
        "in_list_view": 1,
        "description": "Frappe records are name-keyed strings, not integer IDs like legacy_source's source_res_id.",
    },
    {
        "fieldname": "review_date",
        "label": "Review Date",
        "fieldtype": "Datetime",
        "default": "now",
        "in_list_view": 1,
    },
]


def make_opener():
    """Returns a urllib opener that maintains session cookies across requests."""
    cj = CookieJar()
    handler = urllib.request.HTTPCookieProcessor(cj)
    return urllib.request.build_opener(handler)


def login(opener):
    """POST /api/method/login → sets sid cookie in the opener."""
    data = urllib.parse.urlencode({"usr": USER, "pwd": PWD}).encode()
    req = urllib.request.Request(f"{BASE}/api/method/login", data=data)
    with opener.open(req, timeout=10) as r:
        body = r.read().decode()
    if r.status != 200:
        raise SystemExit(f"login failed: HTTP {r.status} body={body}")
    print(f"[login] OK as {USER}")


def existing(opener, doctype_name):
    """Return True if a DocType with this name already exists."""
    url = f"{BASE}/api/resource/DocType/{urllib.parse.quote(doctype_name)}"
    req = urllib.request.Request(url)
    try:
        with opener.open(req, timeout=10) as r:
            return r.status == 200
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False
        raise


def create_doctype(opener):
    """POST /api/method/frappe.client.insert → creates the DocType."""
    payload = {
        "doc": {
            "doctype": "DocType",
            "name": DOCTYPE_NAME,
            "module": "Custom",
            "custom": 1,
            "naming_rule": "Random",
            "autoname": "hash",
            "track_changes": 1,
            "sort_field": "review_date",
            "sort_order": "DESC",
            "description": (
                "Tracks which dashboard notification items have been reviewed by a user. "
                "Lightweight pivot: one record per reviewed item per user. "
                "Translated from legacy_source lt.dashboard.review on 2026-04-25 by Trellis. "
                "TODO: add a Server Script to force user = session.user on insert "
                "(legacy_source's create() override prevents client-side user_id spoofing)."
            ),
            "fields": FIELDS,
            "permissions": [
                {
                    "role": "System Manager",
                    "read": 1, "write": 1, "create": 1, "delete": 1,
                    "report": 1, "export": 1, "share": 1,
                },
            ],
        }
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{BASE}/api/method/frappe.client.insert",
        data=data,
        headers={"Content-Type": "application/json", "X-Requested-With": "XMLHttpRequest"},
    )
    with opener.open(req, timeout=30) as r:
        body = r.read().decode()
    if r.status != 200:
        raise SystemExit(f"create failed: HTTP {r.status} body={body}")
    parsed = json.loads(body)
    print(f"[create] OK: {parsed.get('message', {}).get('name', '?')}")
    return parsed


def verify(opener):
    """Read it back to confirm it exists in the DB."""
    url = f"{BASE}/api/resource/DocType/{urllib.parse.quote(DOCTYPE_NAME)}"
    with opener.open(url, timeout=10) as r:
        body = json.loads(r.read().decode())
    fields_listed = [f["fieldname"] for f in body["data"]["fields"]]
    print(f"[verify] DocType present, {len(fields_listed)} fields: {fields_listed}")
    return body


def main():
    opener = make_opener()
    login(opener)

    if existing(opener, DOCTYPE_NAME):
        print(f"[skip] DocType '{DOCTYPE_NAME}' already exists — verifying only.")
        verify(opener)
        print()
        print(f"OK -> http://localhost:8081/app/doctype/{DOCTYPE_NAME.lower().replace(' ', '-')}")
        return 0

    create_doctype(opener)
    verify(opener)
    print()
    print(f"OK -> http://localhost:8081/app/doctype/{DOCTYPE_NAME.lower().replace(' ', '-')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
