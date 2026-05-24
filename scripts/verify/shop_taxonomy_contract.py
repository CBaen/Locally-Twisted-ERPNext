#!/usr/bin/env python3
"""Verify the approved LT shop taxonomy against the running ERPNext site."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.verify.shop_taxonomy_contract.run"


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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print full JSON report")
    args = parser.parse_args()

    try:
        result = bench_execute()
    except ContractFail as exc:
        print("[SHOP TAXONOMY CONTRACT] FAIL")
        print(f"  - {exc}")
        return 1

    if args.json:
        print(json.dumps(result, indent=2, default=str))
        return 0 if result.get("ok") else 1

    failures = result.get("failures") or []
    evidence = result.get("evidence") or {}
    print("[SHOP TAXONOMY CONTRACT] " + ("PASS" if not failures else "FAIL"))
    print(f"  expected_products: {evidence.get('expected_products')}")
    print(f"  published_products_checked: {evidence.get('published_products_checked')}")
    print(f"  primary_categories: {', '.join(evidence.get('primary_categories') or [])}")
    print(f"  secondary_categories: {', '.join(evidence.get('secondary_categories') or [])}")
    if failures:
        print("  failures:")
        for failure in failures:
            print(f"    - {failure}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
