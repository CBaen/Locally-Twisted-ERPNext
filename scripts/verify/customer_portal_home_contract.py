#!/usr/bin/env python3
"""Verify the LT customer account home renders for a real Website User role."""
from __future__ import annotations

import json
import subprocess
import sys

from _cli import parse_noop_args


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.verify.customer_portal_home_contract.run"


def main() -> int:
    parse_noop_args(__doc__)
    proc = subprocess.run(
        ["docker", "exec", CONTAINER, "bench", "--site", SITE, "execute", METHOD],
        text=True,
        capture_output=True,
        timeout=90,
    )
    if proc.returncode != 0:
        print("[CUSTOMER PORTAL HOME CONTRACT] FAIL")
        print(proc.stdout)
        print(proc.stderr)
        return 1

    result = json.loads(proc.stdout.strip() or "{}")
    if not result.get("ok"):
        print("[CUSTOMER PORTAL HOME CONTRACT] FAIL")
        for failure in result.get("failures") or ["Verifier returned no result"]:
            print(f"  - {failure}")
        return 1

    print("[CUSTOMER PORTAL HOME CONTRACT] PASS")
    print(f"  rendered_route: {result.get('rendered_route')}")
    print(f"  sidebar_routes: {', '.join(result.get('sidebar_routes') or [])}")
    print("  rollback: verifier rolled back the temporary customer user")
    return 0


if __name__ == "__main__":
    sys.exit(main())
