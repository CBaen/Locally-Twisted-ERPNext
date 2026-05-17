#!/usr/bin/env python3
"""Run the simple purchasable product rehearsal inside ERPNext.

This is rollback-only proof for the first blocked product tranche. It does not
publish lanes, open ecommerce, create payment sessions, or send email.
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
METHOD = "locally_twisted.verify.simple_purchasable_rehearsal_contract.run"
ROOT = Path(__file__).resolve().parents[2]
EXPECTED_PRODUCTS = {
    "large-head-missionary",
    "mothers-day-front-yard-7-column",
    "easter-arch",
    "pride-arch",
}
EXPECTED_SALE_SKUS = 33


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
        raise ContractFail(f"bench execute failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")
    text = proc.stdout.strip()
    if not text:
        raise ContractFail("simple purchasable rehearsal returned no output")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ContractFail(f"simple purchasable rehearsal returned non-JSON output: {text}") from exc
    if not isinstance(parsed, dict):
        raise ContractFail(f"simple purchasable rehearsal returned {type(parsed).__name__}, expected object")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print full JSON report")
    parser.add_argument("--report", help="Write full JSON report to a file")
    args = parser.parse_args()

    try:
        result = bench_execute()
    except ContractFail as exc:
        print(f"[SIMPLE PURCHASABLE REHEARSAL] FAIL\n  - {exc}")
        return 1
    contract_failures = _contract_failures(result)
    rendered = json.dumps(result, indent=2, sort_keys=True, default=str)

    if args.report:
        report_path = _rooted(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(rendered + "\n", encoding="utf-8")
        print(f"[SIMPLE PURCHASABLE REHEARSAL] wrote {report_path.relative_to(ROOT)}")

    if args.json:
        print(rendered)
    else:
        ok = bool(result.get("ok")) and not contract_failures
        print("[SIMPLE PURCHASABLE REHEARSAL] " + ("PASS" if ok else "FAIL"))
        print(f"  products: {result.get('simple_rehearsal_product_count')}")
        print(f"  enabled_sale_sku_count: {result.get('enabled_sale_sku_count')}")
        print(f"  sales_order_line_count: {result.get('sales_order_line_count')}")
        print(f"  sales_invoice: {result.get('sales_invoice')}")
        print(f"  survivor_counts: {result.get('survivor_counts')}")
        if result.get("rolled_back"):
            print("  rollback: verifier rolled back all generated records")
        failures = list(result.get("failures") or [])
        failures.extend(contract_failures)
        if failures:
            print("  failures:")
            for failure in failures:
                print(f"    - {failure}")

    return 0 if result.get("ok") and not contract_failures else 1


def _rooted(path: str) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return candidate.resolve()


def _contract_failures(result: dict[str, Any]) -> list[str]:
    products = {
        str(row.get("website_item_code"))
        for row in result.get("simple_rehearsal_products") or []
        if row.get("website_item_code")
    }
    failures: list[str] = []
    missing = sorted(EXPECTED_PRODUCTS - products)
    extra = sorted(products - EXPECTED_PRODUCTS)
    if missing:
        failures.append(f"simple rehearsal is missing products: {missing}")
    if extra:
        failures.append(f"simple rehearsal covered unexpected products: {extra}")
    if result.get("simple_rehearsal_product_count") != len(EXPECTED_PRODUCTS):
        failures.append(
            f"simple_rehearsal_product_count should be {len(EXPECTED_PRODUCTS)}, "
            f"found {result.get('simple_rehearsal_product_count')}"
        )
    if result.get("enabled_sale_sku_count") != EXPECTED_SALE_SKUS:
        failures.append(
            f"enabled_sale_sku_count should be {EXPECTED_SALE_SKUS}, "
            f"found {result.get('enabled_sale_sku_count')}"
        )
    if result.get("sales_order_line_count") != EXPECTED_SALE_SKUS:
        failures.append(
            f"sales_order_line_count should be {EXPECTED_SALE_SKUS}, "
            f"found {result.get('sales_order_line_count')}"
        )
    return failures


if __name__ == "__main__":
    sys.exit(main())
