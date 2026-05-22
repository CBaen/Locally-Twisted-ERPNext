#!/usr/bin/env python3
"""Verify public catalog pages still map to sellable or quote-safe records.

Run:
  python scripts/verify/catalog_public_sellability_contract.py
  python scripts/verify/catalog_public_sellability_contract.py --json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.verify.catalog_public_sellability_contract.run"


class ContractFail(Exception):
    pass


def bench_execute() -> dict[str, Any]:
    proc = subprocess.run(
        ["docker", "exec", CONTAINER, "bench", "--site", SITE, "execute", METHOD],
        text=True,
        capture_output=True,
        timeout=180,
    )
    if proc.returncode != 0:
        raise ContractFail(
            f"bench execute failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )

    text = proc.stdout.strip()
    if not text:
        raise ContractFail("verifier returned no output")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ContractFail(f"verifier returned non-JSON output: {text}") from exc
    if not isinstance(parsed, dict):
        raise ContractFail(f"verifier returned {type(parsed).__name__}, expected object")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true", help="Print full JSON report")
    args = parser.parse_args()

    try:
        result = bench_execute()
    except ContractFail as exc:
        print("[CATALOG PUBLIC SELLABILITY CONTRACT] FAIL")
        print(f"  - {exc}")
        return 1

    if args.json:
        print(json.dumps(result, indent=2, default=str))
        return 0 if result.get("ok") else 1

    failures = result.get("failures") or []
    warnings = result.get("warnings") or []
    evidence = result.get("evidence") or {}
    print("[CATALOG PUBLIC SELLABILITY CONTRACT] " + ("PASS" if not failures else "FAIL"))
    print(f"  published_website_items: {evidence.get('published_website_items')}")
    print(f"  checkout_website_items: {evidence.get('checkout_website_items')}")
    print(f"  quote_first_website_items: {evidence.get('quote_first_website_items')}")
    print(f"  checked_variant_templates: {evidence.get('checked_variant_templates')}")
    print(f"  checked_active_variants: {evidence.get('checked_active_variants')}")
    print(f"  checked_sellable_item_codes: {evidence.get('checked_sellable_item_codes')}")
    print(f"  warnings: {len(warnings)}")
    if failures:
        print("  failures:")
        for failure in failures:
            print(f"    - {failure}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
