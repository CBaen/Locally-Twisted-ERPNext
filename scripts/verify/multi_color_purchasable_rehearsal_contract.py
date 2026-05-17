#!/usr/bin/env python3
"""Run the multi-color purchasable product rehearsal in ERPNext.

This is rollback-safe proof for the first multi-color repair-lane tranche. It
does not open public ecommerce, create live Stripe sessions, or send email.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.verify.multi_color_purchasable_rehearsal_contract.run"
ROOT = Path(__file__).resolve().parents[2]
EXPECTED_PRODUCTS = 6
EXPECTED_ENABLED_COLOR_SKUS = 563


class ContractFail(Exception):
    pass


def bench_execute() -> dict[str, Any]:
    proc = subprocess.run(
        ["docker", "exec", CONTAINER, "bench", "--site", SITE, "execute", METHOD],
        text=True,
        capture_output=True,
        timeout=360,
    )
    if proc.returncode != 0:
        raise ContractFail(f"bench execute failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")
    text = proc.stdout.strip()
    if not text:
        raise ContractFail("multi-color rehearsal returned no output")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ContractFail(f"multi-color rehearsal returned non-JSON output: {text}") from exc
    if not isinstance(parsed, dict):
        raise ContractFail(f"multi-color rehearsal returned {type(parsed).__name__}, expected object")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print full JSON report")
    parser.add_argument("--report", help="Write full JSON report to a file")
    args = parser.parse_args()

    try:
        result = bench_execute()
    except ContractFail as exc:
        print(f"[MULTI-COLOR PURCHASABLE REHEARSAL] FAIL\n  - {exc}")
        return 1

    failures = _contract_failures(result)
    rendered = json.dumps(result, indent=2, sort_keys=True, default=str)

    if args.report:
        report_path = _rooted(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(rendered + "\n", encoding="utf-8")
        print(f"[MULTI-COLOR PURCHASABLE REHEARSAL] wrote {report_path.relative_to(ROOT)}")

    if args.json:
        print(rendered)
    else:
        ok = bool(result.get("ok")) and not failures
        print("[MULTI-COLOR PURCHASABLE REHEARSAL] " + ("PASS" if ok else "FAIL"))
        print(f"  products: {result.get('multi_color_rehearsal_product_count')}")
        print(f"  enabled_color_sku_count: {result.get('enabled_color_sku_count')}")
        print(f"  sales_order_line_count: {result.get('sales_order_line_count')}")
        print(f"  color_recipe_line_count: {result.get('color_recipe_line_count')}")
        print(f"  sales_invoice: {result.get('sales_invoice')}")
        print(f"  survivor_counts: {result.get('survivor_counts')}")
        if result.get("rolled_back"):
            print("  rollback: verifier rolled back all generated records")
        all_failures = list(result.get("failures") or [])
        all_failures.extend(failures)
        if all_failures:
            print("  failures:")
            for failure in all_failures:
                print(f"    - {failure}")

    return 0 if result.get("ok") and not failures else 1


def _rooted(path: str) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return candidate.resolve()


def _contract_failures(result: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if result.get("multi_color_rehearsal_product_count") != EXPECTED_PRODUCTS:
        failures.append(f"expected {EXPECTED_PRODUCTS} products, found {result.get('multi_color_rehearsal_product_count')}")
    if result.get("enabled_color_sku_count") != EXPECTED_ENABLED_COLOR_SKUS:
        failures.append(f"expected {EXPECTED_ENABLED_COLOR_SKUS} color SKUs, found {result.get('enabled_color_sku_count')}")
    if result.get("sales_order_line_count") != EXPECTED_ENABLED_COLOR_SKUS:
        failures.append(f"expected {EXPECTED_ENABLED_COLOR_SKUS} Sales Order lines, found {result.get('sales_order_line_count')}")
    if result.get("color_recipe_line_count") != EXPECTED_ENABLED_COLOR_SKUS:
        failures.append(f"expected {EXPECTED_ENABLED_COLOR_SKUS} color-recipe lines, found {result.get('color_recipe_line_count')}")
    survivors = result.get("survivor_counts") or {}
    remaining = {key: value for key, value in survivors.items() if value}
    if remaining:
        failures.append(f"generated records survived rollback: {remaining}")
    return failures


if __name__ == "__main__":
    sys.exit(main())
