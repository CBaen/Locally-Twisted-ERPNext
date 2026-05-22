#!/usr/bin/env python3
"""Create owner-editable Product Setup records from current Website Items.

Dry run:
  python scripts/setup/sync_product_blueprints_from_catalog.py

Write local Product Setup records:
  python scripts/setup/sync_product_blueprints_from_catalog.py --write
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.seed.sync_product_blueprints_from_catalog.execute"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--write", action="store_true", help="Create/fill Product Setup records locally")
    args = parser.parse_args()

    proc = subprocess.run(
        [
            "docker",
            "exec",
            CONTAINER,
            "bench",
            "--site",
            SITE,
            "execute",
            METHOD,
            "--kwargs",
            repr({"write": args.write}),
        ],
        text=True,
        capture_output=True,
        timeout=240,
    )
    if proc.returncode != 0:
        print("[PRODUCT SETUP CATALOG SYNC] FAIL", file=sys.stderr)
        print(proc.stdout)
        print(proc.stderr, file=sys.stderr)
        return proc.returncode
    text = proc.stdout.strip()
    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        print("[PRODUCT SETUP CATALOG SYNC] FAIL", file=sys.stderr)
        print(f"Non-JSON output: {text}", file=sys.stderr)
        return 1
    summary = result.get("summary") or {}
    mode = "WRITE" if args.write else "DRY RUN"
    print(f"[PRODUCT SETUP CATALOG SYNC] {mode} PASS")
    print(f"  website_items: {result.get('website_items')}")
    print(f"  would_create: {summary.get('would_create')}")
    print(f"  would_update: {summary.get('would_update')}")
    print(f"  created: {summary.get('created')}")
    print(f"  updated: {summary.get('updated')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
