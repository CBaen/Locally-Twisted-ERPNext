#!/usr/bin/env python3
"""Generate the backend-driven product-page architecture contract report.

Run:
  python scripts/verify/product_page_architecture_contract.py
  python scripts/verify/product_page_architecture_contract.py --output output/product-page-architecture-contract.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.verify.product_page_architecture_contract.run"
DEFAULT_OUTPUT = Path("output/product-page-architecture-contract.json")
DEFAULT_MARKDOWN = Path("output/product-page-architecture-contract.md")
SOURCE_CATALOG = Path("_resources/odoo-live/catalog.json")
CONTAINER_SOURCE_CATALOG = "/tmp/lt-odoo-live-catalog.json"


class ContractFail(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Host-side JSON report path.")
    parser.add_argument("--markdown", default=str(DEFAULT_MARKDOWN), help="Host-side Markdown summary path.")
    parser.add_argument("--json", action="store_true", help="Print the full JSON report.")
    return parser.parse_args()


def bench_execute(*, kwargs: dict[str, Any] | None = None) -> dict[str, Any]:
    cmd = ["docker", "exec", CONTAINER, "bench", "--site", SITE, "execute", METHOD]
    if kwargs is not None:
        cmd.extend(["--kwargs", json.dumps(kwargs)])
    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=180)
    if proc.returncode != 0:
        raise ContractFail(f"bench execute failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")
    text = proc.stdout.strip()
    if not text:
        raise ContractFail("architecture contract returned empty output")
    try:
        result = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ContractFail(f"architecture contract returned non-JSON output: {text}") from exc
    if not isinstance(result, dict):
        raise ContractFail(f"architecture contract returned {type(result).__name__}, expected object")
    return result


def copy_source_catalog_to_container() -> None:
    if not SOURCE_CATALOG.exists():
        raise ContractFail(f"missing host source catalog: {SOURCE_CATALOG}")
    proc = subprocess.run(
        ["docker", "cp", str(SOURCE_CATALOG), f"{CONTAINER}:{CONTAINER_SOURCE_CATALOG}"],
        text=True,
        capture_output=True,
        timeout=60,
    )
    if proc.returncode != 0:
        raise ContractFail(f"docker cp failed for source catalog\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")


def main() -> int:
    args = parse_args()
    try:
        copy_source_catalog_to_container()
        result = bench_execute(kwargs={"source_catalog_path": CONTAINER_SOURCE_CATALOG})
    except ContractFail as exc:
        print(f"[PRODUCT PAGE ARCHITECTURE CONTRACT] FAIL\n  - {exc}")
        return 1

    output = Path(args.output)
    markdown = Path(args.markdown)
    output.parent.mkdir(parents=True, exist_ok=True)
    markdown.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown.write_text(_to_markdown(result), encoding="utf-8")

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        _print_summary(result, output, markdown)
    return 0 if result.get("ok") else 2


def _print_summary(result: dict[str, Any], output: Path, markdown: Path) -> None:
    summary = result.get("summary") or {}
    print("[PRODUCT PAGE ARCHITECTURE CONTRACT] " + ("PASS" if result.get("ok") else "FAIL"))
    print(f"  - report: {output}")
    print(f"  - markdown: {markdown}")
    print(f"  - products: {summary.get('product_count')}")
    print(f"  - checkout_allowed_products: {summary.get('checkout_allowed_products')}")
    print(f"  - quote_first_allowed_products: {summary.get('quote_first_allowed_products')}")
    print(f"  - payload targets: {summary.get('payload_target_counts')}")
    print(f"  - product_specific_rules_allowed: {summary.get('product_specific_rules_allowed')}")
    for failure in result.get("failures") or []:
        print(f"  - {failure}")


def _to_markdown(result: dict[str, Any]) -> str:
    summary = result.get("summary") or {}
    lines = [
        "# Product Page Architecture Contract",
        "",
        "This report proves the generic ERPNext receiving architecture, not product-specific launch approval.",
        "",
        "## Summary",
        "",
        f"- Products checked: {summary.get('product_count')}",
        f"- Checkout-allowed products: {summary.get('checkout_allowed_products')}",
        f"- Quote-first-allowed products: {summary.get('quote_first_allowed_products')}",
        f"- Payload targets: {summary.get('payload_target_counts')}",
        f"- Product-specific rules allowed: {summary.get('product_specific_rules_allowed')}",
        "",
        "## Boundaries",
        "",
    ]
    for boundary in result.get("architecture_boundaries") or []:
        lines.append(f"- {boundary}")
    failures = result.get("failures") or []
    lines.extend(["", "## Failures", ""])
    if failures:
        lines.extend(f"- {failure}" for failure in failures)
    else:
        lines.append("- None")
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    sys.exit(main())
