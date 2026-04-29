#!/usr/bin/env python3
"""Backend prep for the /book form.

Adds three new options to the Lead Custom Field `custom_occasion_type`:
  - Wedding
  - Baby Shower
  - Grand Opening

These came from the Odoo /contact form's event_type and were folded into
the consolidated /book form per GL's directive 2026-04-29. The Custom
Field is a Select type, so unknown values would fail validation on
Lead.insert().

Idempotent: re-running adds only what's missing, leaves existing options
alone.

CRM stages (6 LT-specific values) are tracked separately in the queue —
not blocking the form rebuild itself.

Usage:
    python scripts/setup/setup_book_form_backend.py
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

NEW_OCCASION_OPTIONS = [
    "Wedding",
    "Baby Shower",
    "Grand Opening",
]


def make_opener():
    cj = CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))


def login(opener):
    data = urllib.parse.urlencode({"usr": USER, "pwd": PWD}).encode()
    req = urllib.request.Request(f"{BASE}/api/method/login", data=data)
    with opener.open(req, timeout=10) as r:
        if r.status != 200:
            raise SystemExit(f"login failed: HTTP {r.status}")
    print(f"[login] OK as {USER}")


def get_custom_field(opener, dt, fieldname):
    """Return the Custom Field doc as a dict, or None if not found."""
    qs = urllib.parse.urlencode({
        "filters": json.dumps([
            ["dt", "=", dt],
            ["fieldname", "=", fieldname],
        ]),
        "fields": json.dumps(["name", "fieldtype", "options"]),
        "limit_page_length": 1,
    })
    req = urllib.request.Request(
        f"{BASE}/api/method/frappe.client.get_list?doctype=Custom Field&{qs}"
    )
    with opener.open(req, timeout=15) as r:
        body = json.loads(r.read().decode())
    rows = body.get("message", [])
    return rows[0] if rows else None


def update_custom_field_options(opener, name, options_str):
    payload = json.dumps({
        "doctype": "Custom Field",
        "name": name,
        "fieldname": "options",
        "value": options_str,
    }).encode()
    req = urllib.request.Request(
        f"{BASE}/api/method/frappe.client.set_value",
        data=payload,
        headers={"Content-Type": "application/json", "X-Requested-With": "XMLHttpRequest"},
    )
    with opener.open(req, timeout=30) as r:
        body = r.read().decode()
    print(f"[update] {name} options updated")


def ensure_occasion_options(opener):
    cf = get_custom_field(opener, "Lead", "custom_occasion_type")
    if not cf:
        raise SystemExit("FAIL: Custom Field Lead.custom_occasion_type not found")
    if cf.get("fieldtype") != "Select":
        raise SystemExit(f"FAIL: custom_occasion_type is {cf.get('fieldtype')!r}, expected Select")

    current_raw = cf.get("options") or ""
    # Frappe stores Select options as newline-separated; first row may be
    # blank for the "no selection" placeholder.
    existing = [line.strip() for line in current_raw.split("\n")]
    existing_set = {l for l in existing if l}

    to_add = [opt for opt in NEW_OCCASION_OPTIONS if opt not in existing_set]
    if not to_add:
        print(f"[skip] All target options already present on custom_occasion_type")
        return

    # Insert the new options at the right alphabetic-ish positions, but
    # keep this simple: append them. GL can reorder via the desk if they
    # care about order.
    new_options = list(existing) + to_add
    new_raw = "\n".join(new_options)
    print(f"[add] custom_occasion_type += {to_add}")
    update_custom_field_options(opener, cf["name"], new_raw)


def main():
    opener = make_opener()
    login(opener)

    print(f"\n[task] Ensure 3 new options on Lead.custom_occasion_type")
    ensure_occasion_options(opener)

    print(f"\nDONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
