#!/usr/bin/env python3
"""Run the simple purchasable product payment cascade verifier in ERPNext.

This is rollback-safe proof for the first simple repair-lane tranche. It does
not open public ecommerce, create live Stripe sessions, or send email outside
the local ERPNext transaction.
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
METHOD = "locally_twisted.verify.simple_purchasable_payment_cascade_contract.run"
ROOT = Path(__file__).resolve().parents[2]
EXPECTED_PRODUCTS = 4
EXPECTED_SALE_SKUS = 33


class ContractFail(Exception):
    pass


def bench_execute() -> dict[str, Any]:
    proc = subprocess.run(
        ["docker", "exec", CONTAINER, "bench", "--site", SITE, "execute", METHOD],
        text=True,
        capture_output=True,
        timeout=240,
    )
    if proc.returncode != 0:
        raise ContractFail(f"bench execute failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")
    text = proc.stdout.strip()
    if not text:
        raise ContractFail("simple payment cascade returned no output")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ContractFail(f"simple payment cascade returned non-JSON output: {text}") from exc
    if not isinstance(parsed, dict):
        raise ContractFail(f"simple payment cascade returned {type(parsed).__name__}, expected object")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print full JSON report")
    parser.add_argument("--report", help="Write full JSON report to a file")
    args = parser.parse_args()

    try:
        result = bench_execute()
    except ContractFail as exc:
        print(f"[SIMPLE PURCHASABLE PAYMENT CASCADE] FAIL\n  - {exc}")
        return 1
    failures = _contract_failures(result)
    rendered = json.dumps(result, indent=2, sort_keys=True, default=str)

    if args.report:
        report_path = _rooted(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(rendered + "\n", encoding="utf-8")
        print(f"[SIMPLE PURCHASABLE PAYMENT CASCADE] wrote {report_path.relative_to(ROOT)}")

    if args.json:
        print(rendered)
    else:
        ok = bool(result.get("ok")) and not failures
        print("[SIMPLE PURCHASABLE PAYMENT CASCADE] " + ("PASS" if ok else "FAIL"))
        print(f"  products: {result.get('simple_payment_product_count')}")
        print(f"  enabled_sale_sku_count: {result.get('enabled_sale_sku_count')}")
        print(f"  sales_order_line_count: {result.get('sales_order_line_count')}")
        print(f"  payment_request: {result.get('payment_request')}")
        print(f"  payment_entry: {result.get('payment_entry')}")
        print(f"  sales_invoice: {result.get('sales_invoice')}")
        print(f"  receipt_email_queue: {result.get('receipt_email_queue')}")
        print(f"  operator_email_queue: {result.get('operator_email_queue')}")
        print(f"  welcome_email_queue: {result.get('welcome_email_queue')}")
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
    if result.get("simple_payment_product_count") != EXPECTED_PRODUCTS:
        failures.append(f"expected {EXPECTED_PRODUCTS} products, found {result.get('simple_payment_product_count')}")
    if result.get("enabled_sale_sku_count") != EXPECTED_SALE_SKUS:
        failures.append(f"expected {EXPECTED_SALE_SKUS} sale SKUs, found {result.get('enabled_sale_sku_count')}")
    if result.get("sales_order_line_count") != EXPECTED_SALE_SKUS:
        failures.append(f"expected {EXPECTED_SALE_SKUS} Sales Order lines, found {result.get('sales_order_line_count')}")
    survivors = result.get("survivor_counts") or {}
    remaining = {key: value for key, value in survivors.items() if value}
    if remaining:
        failures.append(f"generated records survived rollback: {remaining}")
    return failures


if __name__ == "__main__":
    sys.exit(main())
