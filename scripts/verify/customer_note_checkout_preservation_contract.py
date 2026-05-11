#!/usr/bin/env python3
"""Verify checkout customer-note preservation from submit_guest_order to operator evidence."""
from __future__ import annotations

import json
import subprocess
import sys

from _cli import parse_noop_args


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"


def main() -> int:
    parse_noop_args(__doc__)
    cmd = [
        "docker",
        "exec",
        CONTAINER,
        "bench",
        "--site",
        SITE,
        "execute",
        "locally_twisted.verify.customer_note_checkout_preservation_contract.run",
    ]
    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=120)
    if proc.returncode != 0:
        print("[CUSTOMER NOTE CHECKOUT PRESERVATION CONTRACT] FAIL")
        print(proc.stdout)
        print(proc.stderr)
        return 1
    result = json.loads(proc.stdout.strip() or "{}")
    if not result.get("ok"):
        print("[CUSTOMER NOTE CHECKOUT PRESERVATION CONTRACT] FAIL")
        for failure in result.get("failures") or ["Verifier returned no result"]:
            print(f"  - {failure}")
        if result.get("survivor_counts"):
            print(f"  survivor_counts: {result['survivor_counts']}")
        return 1
    print("[CUSTOMER NOTE CHECKOUT PRESERVATION CONTRACT] PASS")
    note_case = result.get("note_case") or {}
    no_note_case = result.get("no_note_case") or {}
    print(f"  note_sales_order: {note_case.get('sales_order')}")
    print(f"  note_payment_request: {note_case.get('payment_request')}")
    print(f"  note_communication: {note_case.get('communication')}")
    print(f"  operator_email_queue: {note_case.get('operator_email_queue')}")
    print(f"  no_note_sales_order: {no_note_case.get('sales_order')}")
    print(f"  no_note_payment_request: {no_note_case.get('payment_request')}")
    print("  no_fake_customer_note: true")
    print(f"  survivor_counts: {result.get('survivor_counts')}")
    print("  rollback: verifier rolled back all generated records")
    return 0


if __name__ == "__main__":
    sys.exit(main())
