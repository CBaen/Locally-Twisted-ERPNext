#!/usr/bin/env python3
"""
Complete the LT ERPNext setup wizard via API and seed the Locally Twisted
Company record with real address/phone/email/website pulled from the existing
catalog_data project (external-catalog-data).

After completion:
  - System Settings.setup_complete = 1
  - Company "Locally Twisted" exists with fiscal year 2026, USD, "Standard
    with Numbers" chart of accounts, Services domain
  - User "cameron@builtbycameron.com" exists as System Manager (developer)
  - User "locallytwisted@gmail.com" exists as System Manager (Jeff Kimber,
    pre-created so future Frappe Cloud transfer is clean)
  - Address "Locally Twisted HQ" linked to the Company with the West Jordan
    storefront address, phone, and contact email
  - Company record has phone_no, email, website fields populated

Idempotent: each step checks-or-skips. Safe to re-run.

Stdlib only (urllib + json) — no `pip install` required.
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

# Wizard payload — values pulled from external-catalog-data source:
#   - Company name + tagline: data/res_company.xml + automation_data.xml
#   - Address: automation_data.xml signature blocks
#   - Phone: views/footer.xml + page_accessibility.xml
#   - Email: migrations/19.0.2.11.0/post-migrate.py (current LT email)
#   - Fiscal year + chart of accounts: confirmed with GL 2026-04-26
#   - Industry: Services (confirmed with GL 2026-04-26)
SETUP_ARGS = {
    "language": "English",
    "country": "United States",
    "timezone": "America/Denver",          # Utah is Mountain Time
    "currency": "USD",
    "full_name": "Cameron Paul",
    "email": "cameron@builtbycameron.com",
    "password": "admin",                   # local dev — same as Administrator for memorability
    "company_name": "Locally Twisted",
    "company_abbr": "LT",
    "company_tagline": "Utah's Balloon Specialists",
    "chart_of_accounts": "Standard with Numbers",
    "fy_start_date": "2026-01-01",
    "fy_end_date": "2026-12-31",
    "domains": ["Services"],
    "bank_account": "",
}

# Pre-create Jeff's User account so the future Frappe Cloud transfer is
# clean. Local site has no SMTP configured so no welcome email fires.
JEFF_USER = {
    "doctype": "User",
    "email": "locallytwisted@gmail.com",
    "first_name": "Jeff",
    "last_name": "Kimber",
    "send_welcome_email": 0,
    "enabled": 1,
    "user_type": "System User",
    "roles": [{"role": "System Manager"}],
}

# Real LT business address — surfaced as the Company's primary Address.
LT_ADDRESS = {
    "doctype": "Address",
    "address_title": "Locally Twisted HQ",
    "address_type": "Office",
    "address_line1": "8969 S 2700 W",
    "city": "West Jordan",
    "state": "Utah",
    "country": "United States",
    "pincode": "84088",
    "phone": "(801) 285-0860",
    "email_id": "hi@locallytwisted.com",
    "is_primary_address": 1,
    "is_shipping_address": 1,
    "links": [{"link_doctype": "Company", "link_name": "Locally Twisted"}],
}

# Top-level fields on the Company DocType itself (separate from Address).
COMPANY_FIELDS = {
    "phone_no": "(801) 285-0860",
    "email": "hi@locallytwisted.com",
    "website": "https://locallytwisted.com",
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


def is_setup_complete(opener):
    """Return True iff the setup wizard has already been run on this site."""
    url = (f"{BASE}/api/method/frappe.client.get_value"
           f"?doctype=System+Settings&fieldname=setup_complete")
    req = urllib.request.Request(url)
    try:
        with opener.open(req, timeout=10) as r:
            data = json.loads(r.read().decode())
        val = data.get("message", {}).get("setup_complete")
        return str(val) == "1"
    except Exception as e:
        print(f"[setup-check] error: {e}; assuming NOT complete")
        return False


def run_setup_wizard(opener):
    payload = urllib.parse.urlencode({"args": json.dumps(SETUP_ARGS)}).encode()
    req = urllib.request.Request(
        f"{BASE}/api/method/frappe.desk.page.setup_wizard.setup_wizard.setup_complete",
        data=payload,
        headers={"X-Requested-With": "XMLHttpRequest"},
    )
    # Wizard touches accounts, taxes, fiscal year, domain modules — slow on first run.
    with opener.open(req, timeout=600) as r:
        body = r.read().decode()
    if r.status != 200:
        raise SystemExit(f"setup_complete failed: HTTP {r.status} body={body[:500]}")
    parsed = json.loads(body)
    msg = parsed.get('message', {})
    print(f"[setup] status={msg.get('status', '?')}")
    return parsed


def insert_doc(opener, doc, label):
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
        print(f"[{label}] created: {parsed.get('message', {}).get('name', '?')}")
        return parsed
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        if 'already exists' in body or 'DuplicateEntryError' in body:
            print(f"[{label}] already exists — skipping")
            return None
        raise SystemExit(f"[{label}] failed: HTTP {e.code} body={body[:300]}")


def set_company_field(opener, fieldname, value):
    """Update one field on the Locally Twisted Company record."""
    payload = json.dumps({
        "doctype": "Company",
        "name": "Locally Twisted",
        "fieldname": fieldname,
        "value": value,
    }).encode()
    req = urllib.request.Request(
        f"{BASE}/api/method/frappe.client.set_value",
        data=payload,
        headers={"Content-Type": "application/json", "X-Requested-With": "XMLHttpRequest"},
    )
    try:
        with opener.open(req, timeout=15) as r:
            r.read()
        print(f"[company.{fieldname}] = {value}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"[company.{fieldname}] FAILED HTTP {e.code} body={body[:200]}")


def main():
    opener = make_opener()
    login(opener)

    if is_setup_complete(opener):
        print("[skip] Setup wizard already complete.")
    else:
        run_setup_wizard(opener)

    insert_doc(opener, JEFF_USER, "user/jeff")
    insert_doc(opener, LT_ADDRESS, "address/lt-hq")

    for k, v in COMPANY_FIELDS.items():
        set_company_field(opener, k, v)

    print()
    print("OK -> http://localhost:8081/app/company/Locally%20Twisted")
    print("OK -> http://localhost:8081/app/user/locallytwisted@gmail.com")
    return 0


if __name__ == "__main__":
    sys.exit(main())
