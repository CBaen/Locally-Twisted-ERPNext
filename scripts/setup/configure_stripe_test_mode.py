#!/usr/bin/env python3
"""Configure ERPNext Stripe Settings for the LT site, test mode.

Reads STRIPE_TEST_PUBLISHABLE_KEY and STRIPE_TEST_SECRET_KEY from
the project's .env, then creates (or updates) a Stripe Settings record
named "Test" via bench execute. Idempotent — re-run is safe.

What it does:
1. Reads keys from .env (host side).
2. Creates Stripe Settings doc named "Test" with the keys.
3. Frappe's payments app auto-creates a Payment Gateway record
   "Stripe-Test" via the on_update hook on Stripe Settings.
4. Caller can then create a Payment Gateway Account record to wire
   the gateway to a chart-of-accounts entry for USD.

Usage:
    python scripts/setup/configure_stripe_test_mode.py

Re-runs are idempotent — if Stripe Settings "Test" already exists, the
keys are updated rather than re-inserted.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"
BACKEND_CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
GATEWAY_NAME = "Test"


def read_env_keys():
    """Pull STRIPE_TEST_PUBLISHABLE_KEY and STRIPE_TEST_SECRET_KEY from .env.

    Skips commented lines (starting with #). Returns (pub_key, sec_key).
    Raises SystemExit with a clear message if either is missing or empty.
    """
    if not ENV_FILE.exists():
        sys.exit(f"FATAL: {ENV_FILE} not found.")

    pub = sec = None
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        m = re.match(r"^([A-Z0-9_]+)\s*=\s*(.*)$", stripped)
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip().strip('"').strip("'")
        if key == "STRIPE_TEST_PUBLISHABLE_KEY":
            pub = value
        elif key == "STRIPE_TEST_SECRET_KEY":
            sec = value

    if not pub or not pub.startswith("pk_test_"):
        sys.exit("FATAL: STRIPE_TEST_PUBLISHABLE_KEY missing or doesn't start with pk_test_.")
    if not sec or not sec.startswith("sk_test_"):
        sys.exit("FATAL: STRIPE_TEST_SECRET_KEY missing or doesn't start with sk_test_.")
    return pub, sec


def bench_execute(method, kwargs):
    """Run `bench --site SITE execute METHOD --kwargs JSON` inside the backend container.

    Returns stdout. Raises SystemExit on non-zero exit.
    """
    cmd = [
        "docker", "exec", BACKEND_CONTAINER,
        "bench", "--site", SITE, "execute", method,
        "--kwargs", json.dumps(kwargs),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"FATAL: bench execute failed for {method}:\n  stderr: {result.stderr}\n  stdout: {result.stdout}")
    return result.stdout


def main():
    print("=== Configure Stripe Settings (Test mode) ===")

    pub_key, sec_key = read_env_keys()
    print(f"  Keys found in .env. Publishable len={len(pub_key)}, Secret len={len(sec_key)}.")

    # Idempotent insert/update via frappe.client.set_value won't work for new docs;
    # need a small bit of imperative logic. Use frappe.client.get_value to detect
    # existing doc, then either insert or update.
    existing = bench_execute(
        "frappe.client.get_list",
        {
            "doctype": "Stripe Settings",
            "filters": [["name", "=", GATEWAY_NAME]],
            "fields": ["name"],
            "limit_page_length": 1,
        },
    )
    has_existing = '"name"' in existing and GATEWAY_NAME in existing

    if has_existing:
        print(f"  Stripe Settings '{GATEWAY_NAME}' exists. Updating keys...")
        bench_execute(
            "frappe.client.set_value",
            {
                "doctype": "Stripe Settings",
                "name": GATEWAY_NAME,
                "fieldname": {
                    "publishable_key": pub_key,
                    "secret_key": sec_key,
                },
            },
        )
    else:
        print(f"  Stripe Settings '{GATEWAY_NAME}' does not exist. Creating...")
        bench_execute(
            "frappe.client.insert",
            {
                "doc": {
                    "doctype": "Stripe Settings",
                    "gateway_name": GATEWAY_NAME,
                    "publishable_key": pub_key,
                    "secret_key": sec_key,
                },
            },
        )

    # Verify the auto-created Payment Gateway record landed.
    gw_check = bench_execute(
        "frappe.client.get_list",
        {
            "doctype": "Payment Gateway",
            "filters": [["name", "=", f"Stripe-{GATEWAY_NAME}"]],
            "fields": ["name", "gateway_settings", "gateway_controller"],
        },
    )
    print(f"  Payment Gateway lookup: {gw_check.strip()}")

    print()
    print(f"Done. Stripe Settings '{GATEWAY_NAME}' configured.")
    print(f"Next step: create a Payment Gateway Account linking 'Stripe-{GATEWAY_NAME}' to a USD chart-of-accounts entry.")
    print("(Done in the desk UI under Accounting > Payment Gateway Account, or via a follow-up script.)")


if __name__ == "__main__":
    main()
