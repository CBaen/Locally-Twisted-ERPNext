#!/usr/bin/env python3
"""Verify LT commerce rules for delivery zones, tax, lanes, and payment terms."""
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
        "locally_twisted.verify.commerce_rules_contract.run",
    ]
    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=60)
    if proc.returncode != 0:
        print("[COMMERCE RULES CONTRACT] FAIL")
        print(proc.stdout)
        print(proc.stderr)
        return 1
    result = json.loads(proc.stdout.strip() or "{}")
    if not result.get("ok"):
        print("[COMMERCE RULES CONTRACT] FAIL")
        for failure in result.get("failures") or ["Verifier returned no result"]:
            print(f"  - {failure}")
        return 1
    print("[COMMERCE RULES CONTRACT] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
