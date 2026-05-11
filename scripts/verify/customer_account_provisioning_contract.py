#!/usr/bin/env python3
"""Verify invite-only customer account provisioning without sending email."""
from __future__ import annotations

import json
import subprocess
import sys

from _cli import parse_noop_args


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.verify.customer_account_provisioning_contract.run"


def main() -> int:
    parse_noop_args(__doc__)
    proc = subprocess.run(
        ["docker", "exec", CONTAINER, "bench", "--site", SITE, "execute", METHOD],
        text=True,
        capture_output=True,
        timeout=120,
    )
    if proc.returncode != 0:
        print("[CUSTOMER ACCOUNT PROVISIONING CONTRACT] FAIL")
        print(proc.stdout)
        print(proc.stderr)
        return 1

    result = json.loads(proc.stdout.strip() or "{}")
    if not result.get("ok"):
        print("[CUSTOMER ACCOUNT PROVISIONING CONTRACT] FAIL")
        for failure in result.get("failures") or ["Verifier returned no result"]:
            print(f"  - {failure}")
        return 1

    print("[CUSTOMER ACCOUNT PROVISIONING CONTRACT] PASS")
    print(f"  created_user: {result.get('user')}")
    print(f"  blocked_cases: {', '.join(result.get('blocked_cases') or [])}")
    print("  rollback: verifier rolled back the temporary customer account records")
    return 0


if __name__ == "__main__":
    sys.exit(main())
