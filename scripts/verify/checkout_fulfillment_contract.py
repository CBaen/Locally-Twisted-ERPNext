#!/usr/bin/env python3
"""Verify checkout fulfillment behavior for pickup, delivery, and quote gate."""
from __future__ import annotations

import json
import subprocess
import sys


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"


def main() -> int:
    cmd = [
        "docker",
        "exec",
        CONTAINER,
        "bench",
        "--site",
        SITE,
        "execute",
        "locally_twisted.verify.checkout_fulfillment_contract.run",
    ]
    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=120)
    if proc.returncode != 0:
        print("[CHECKOUT FULFILLMENT CONTRACT] FAIL")
        print(proc.stdout)
        print(proc.stderr)
        return 1
    result = json.loads(proc.stdout.strip() or "{}")
    if not result.get("ok"):
        print("[CHECKOUT FULFILLMENT CONTRACT] FAIL")
        for failure in result.get("failures") or ["Verifier returned no result"]:
            print(f"  - {failure}")
        return 1
    print("[CHECKOUT FULFILLMENT CONTRACT] PASS")
    print("  rollback: verifier rolled back generated records")
    return 0


if __name__ == "__main__":
    sys.exit(main())
