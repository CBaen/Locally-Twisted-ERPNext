#!/usr/bin/env python3
"""Verify LT customer document/email policy lane behavior."""
from __future__ import annotations

import json
import subprocess
import sys

from _cli import parse_noop_args


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"


def main() -> int:
    parse_noop_args(__doc__)
    proc = subprocess.run(
        [
            "docker",
            "exec",
            CONTAINER,
            "bench",
            "--site",
            SITE,
            "execute",
            "locally_twisted.verify.customer_documents_contract.run",
        ],
        text=True,
        capture_output=True,
        timeout=90,
    )
    if proc.returncode != 0:
        print("[CUSTOMER DOCUMENTS CONTRACT] FAIL")
        print(proc.stdout)
        print(proc.stderr)
        return 1
    result = json.loads(proc.stdout.strip() or "{}")
    if not result.get("ok"):
        print("[CUSTOMER DOCUMENTS CONTRACT] FAIL")
        for failure in result.get("failures") or ["Verifier returned no result"]:
            print(f"  - {failure}")
        return 1
    print("[CUSTOMER DOCUMENTS CONTRACT] PASS")
    print(f"  anchors: {', '.join(result.get('checked_anchors') or [])}")
    print("  rollback: verifier rolled back generated Lead/email records")
    return 0


if __name__ == "__main__":
    sys.exit(main())
