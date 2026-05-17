#!/usr/bin/env python3
"""Run the LT Phase 3 checkout product-family contract inside ERPNext."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.verify.checkout_product_family_contract.run"
ROOT = Path(__file__).resolve().parents[2]
EXPECTED_DIRECT_CHECKOUT_WEBSITE_ITEMS = {
    "6-graduation-stands",
    "7-butterfly-column",
    "easter-balloon-cups",
    "elsa-bouquet",
    "encanto-bouquet",
    "flamingo-bouquet",
    "football-bouquet",
    "graduation-grab-n-go",
    "holy-cow-bouquet",
    "mickey-mouse-bouquet",
    "minion-bouquet",
    "mothers-day-bouquet",
    "over-the-hill-bouquet",
    "paw-patrol-bouquet",
    "soccer-bouquet",
    "space-bouquet",
    "stitch-bouquet",
    "unicorn-bouquet",
}


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
        raise ContractFail("checkout product-family contract returned no output")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ContractFail(f"checkout product-family contract returned non-JSON output: {text}") from exc
    if not isinstance(parsed, dict):
        raise ContractFail(f"checkout product-family contract returned {type(parsed).__name__}, expected object")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print full JSON report")
    parser.add_argument("--report", help="Write full JSON report to a file")
    args = parser.parse_args()

    try:
        result = bench_execute()
    except ContractFail as exc:
        print(f"[CHECKOUT PRODUCT-FAMILY CONTRACT] FAIL\n  - {exc}")
        return 1
    contract_failures = _contract_failures(result)

    rendered = json.dumps(result, indent=2, sort_keys=True, default=str)
    if args.report:
        report_path = _rooted(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(rendered + "\n", encoding="utf-8")
        print(f"[CHECKOUT PRODUCT-FAMILY CONTRACT] wrote {report_path.relative_to(ROOT)}")

    if args.json:
        print(rendered)
    else:
        print("[CHECKOUT PRODUCT-FAMILY CONTRACT] " + ("PASS" if result.get("ok") and not contract_failures else "FAIL"))
        print(f"  bouquet_family_count: {result.get('bouquet_family_count')}")
        print(f"  direct_checkout_family_count: {result.get('direct_checkout_family_count')}")
        print(f"  enabled_sale_sku_count: {result.get('enabled_sale_sku_count')}")
        print(f"  add_on_line_count: {result.get('add_on_line_count')}")
        print(f"  sales_order_line_count: {result.get('sales_order_line_count')}")
        print(f"  sales_invoice: {result.get('sales_invoice')}")
        easter = result.get('easter_balloon_cups') or {}
        print(f"  easter_balloon_cups: {easter.get('seasonal_status') or easter.get('status')}")
        print(f"  survivor_counts: {result.get('survivor_counts')}")
        if result.get("rolled_back"):
            print("  rollback: verifier rolled back all generated records")
        failures = result.get("failures") or []
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
    covered = _covered_website_items(result)
    missing = sorted(EXPECTED_DIRECT_CHECKOUT_WEBSITE_ITEMS - covered)
    extra = sorted(covered - EXPECTED_DIRECT_CHECKOUT_WEBSITE_ITEMS)
    failures: list[str] = []
    if missing:
        failures.append(f"direct checkout family contract is missing product families: {missing}")
    if extra:
        failures.append(f"direct checkout family contract covered unexpected product families: {extra}")
    if result.get("direct_checkout_family_count") != len(EXPECTED_DIRECT_CHECKOUT_WEBSITE_ITEMS):
        failures.append(
            "direct_checkout_family_count should be "
            f"{len(EXPECTED_DIRECT_CHECKOUT_WEBSITE_ITEMS)}, found {result.get('direct_checkout_family_count')}"
        )
    return failures


def _covered_website_items(result: dict[str, Any]) -> set[str]:
    covered = {
        str(row.get("website_item_code"))
        for row in result.get("bouquet_family") or []
        if row.get("website_item_code")
    }
    for key in (
        "mothers_day",
        "easter_balloon_cups",
        "graduation_stands",
        "butterfly_column",
        "graduation_grab_n_go",
    ):
        row = result.get(key) or {}
        if row.get("website_item_code"):
            covered.add(str(row.get("website_item_code")))
    return covered


if __name__ == "__main__":
    sys.exit(main())
