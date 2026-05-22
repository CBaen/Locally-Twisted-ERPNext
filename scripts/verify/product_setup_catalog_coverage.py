#!/usr/bin/env python3
"""Verify every storefront product has an owner-editable Product Setup record."""
from __future__ import annotations

import json
import subprocess
import sys

from _cli import parse_noop_args


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.verify.product_setup_catalog_coverage.run"


def main() -> int:
    parse_noop_args(__doc__)
    proc = subprocess.run(
        ["docker", "exec", CONTAINER, "bench", "--site", SITE, "execute", METHOD],
        text=True,
        capture_output=True,
        timeout=180,
    )
    if proc.returncode != 0:
        print("[PRODUCT SETUP CATALOG COVERAGE] FAIL")
        print(proc.stdout)
        print(proc.stderr)
        return proc.returncode
    try:
        result = json.loads(proc.stdout.strip())
    except json.JSONDecodeError:
        print("[PRODUCT SETUP CATALOG COVERAGE] FAIL")
        print(f"Non-JSON output: {proc.stdout}")
        print(proc.stderr)
        return 1
    evidence = result.get("evidence") or {}
    print("[PRODUCT SETUP CATALOG COVERAGE] " + ("PASS" if result.get("ok") else "FAIL"))
    print(f"  website_items: {evidence.get('website_items')}")
    print(f"  blueprints: {evidence.get('blueprints')}")
    print(f"  draft_backfilled_blueprints: {evidence.get('draft_backfilled_blueprints')}")
    print(f"  active_preview_blueprints: {evidence.get('active_preview_blueprints')}")
    print(f"  checkout_products: {evidence.get('checkout_products')}")
    print(f"  checked_price_rows: {evidence.get('checked_price_rows')}")
    print(f"  checked_variant_media_rows: {evidence.get('checked_variant_media_rows')}")
    print(f"  checked_gallery_rows: {evidence.get('checked_gallery_rows')}")
    print(f"  checked_customer_safe_setup_schemas: {evidence.get('checked_customer_safe_setup_schemas')}")
    failures = result.get("failures") or []
    for failure in failures[:40]:
        print(f"  - {failure}")
    if len(failures) > 40:
        print(f"  - ... {len(failures) - 40} more")
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
