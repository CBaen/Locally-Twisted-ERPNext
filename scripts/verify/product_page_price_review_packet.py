#!/usr/bin/env python3
"""Build and verify the product-page business price review packet.

Run:
  python scripts/verify/product_page_price_review_packet.py
  python scripts/verify/product_page_price_review_packet.py --json
  python scripts/verify/product_page_price_review_packet.py --report output/product-page-price-review-packet.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps" / "locally_twisted"))

from locally_twisted.catalog_contract.price_review import build_price_review_packet


SOURCE_ARTIFACT = ROOT / "audits/odoo-erpnext-migration-audit-2026-05-08/21-product-page-price-enrichment-candidates.json"
DEFAULT_REPORT = ROOT / "audits/odoo-erpnext-migration-audit-2026-05-08/24-product-page-price-review-packet.json"
DEFAULT_MARKDOWN = ROOT / "audits/odoo-erpnext-migration-audit-2026-05-08/24-product-page-price-review-packet.md"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true", help="Print full packet JSON")
    parser.add_argument("--report", help="Write packet JSON to a file")
    parser.add_argument("--markdown", help="Write packet Markdown to a file")
    args = parser.parse_args()

    packet = build_price_review_packet(_source_artifact())
    failures = _contract_failures(packet)
    rendered = json.dumps(packet, indent=2, sort_keys=True)

    report_path = _rooted(args.report) if args.report else DEFAULT_REPORT
    markdown_path = _rooted(args.markdown) if args.markdown else DEFAULT_MARKDOWN
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(rendered + "\n", encoding="utf-8")
    markdown_path.write_text(_to_markdown(packet), encoding="utf-8")

    print(f"[PRODUCT PAGE PRICE REVIEW PACKET] wrote {report_path.relative_to(ROOT)}")
    print(f"[PRODUCT PAGE PRICE REVIEW PACKET] wrote {markdown_path.relative_to(ROOT)}")
    if args.json:
        print(rendered)
    else:
        _print_summary(packet, failures)

    return 0 if not failures else 1


def _contract_failures(packet: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if packet.get("approved_for_public_price_count") != 0:
        failures.append("packet approved public prices")
    if packet.get("safe_default") != "business_review_required":
        failures.append("safe_default must be business_review_required")
    if int(packet.get("review_unit_count") or 0) <= 0:
        failures.append("packet has no review units")
    products = packet.get("products")
    if not isinstance(products, list):
        return failures + ["products must be a list"]
    unit_count = 0
    for product in products:
        units = product.get("review_units") or []
        unit_count += len(units)
        if int(product.get("review_unit_count") or 0) != len(units):
            failures.append(f"{product.get('slug')} review_unit_count does not match review_units")
        for unit in units:
            if unit.get("price_source_kind") != "live_erpnext_snapshot":
                failures.append(f"{product.get('slug')} review unit is not live_erpnext_snapshot")
            if unit.get("safe_default") != "business_review_required":
                failures.append(f"{product.get('slug')} review unit safe_default is wrong")
            if not unit.get("chosen_price"):
                failures.append(f"{product.get('slug')} review unit missing chosen_price")
    if unit_count != packet.get("review_unit_count"):
        failures.append("review_unit_count does not match product review_units")
    return failures


def _print_summary(packet: dict[str, Any], failures: list[str]) -> None:
    print("[PRODUCT PAGE PRICE REVIEW PACKET] " + ("PASS" if not failures else "FAIL"))
    print(f"  source_products: {packet.get('source_product_count')}")
    print(f"  products_needing_review: {packet.get('products_needing_review')}")
    print(f"  review_units: {packet.get('review_unit_count')}")
    print(f"  approved_for_public_price_count: {packet.get('approved_for_public_price_count')}")
    for product in (packet.get("products") or [])[:8]:
        print(f"  - {product.get('slug')}: {product.get('review_unit_count')} unit(s), lane={product.get('commerce_lane')}")
    extra = len(packet.get("products") or []) - 8
    if extra > 0:
        print(f"  - ... {extra} more product(s)")
    if failures:
        print("  failures:")
        for failure in failures:
            print(f"    - {failure}")


def _to_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# Product Page Price Review Packet",
        "",
        "This packet is source-backed and read-only. It does not approve public prices.",
        "Every live ERPNext snapshot candidate stays business-review-required until approved or replaced.",
        "",
        "## Summary",
        "",
        f"- Source products: {packet.get('source_product_count')}",
        f"- Products needing review: {packet.get('products_needing_review')}",
        f"- Review units: {packet.get('review_unit_count')}",
        f"- Approved public prices: {packet.get('approved_for_public_price_count')}",
        "",
        "## Product Rows",
        "",
        "| Product | Lane | Required axes | Review units |",
        "|---|---|---|---:|",
    ]
    for product in packet.get("products") or []:
        axes = ", ".join(product.get("required_axes") or []) or "single SKU"
        lines.append(
            f"| `{product.get('slug')}` {product.get('name')} | "
            f"{product.get('commerce_lane')} | {axes} | {product.get('review_unit_count')} |"
        )
    lines.extend(["", "## Review Units", ""])
    for product in packet.get("products") or []:
        lines.extend([f"### {product.get('slug')}", ""])
        for unit in product.get("review_units") or []:
            combo = unit.get("projected_required_combo") or {}
            combo_label = ", ".join(f"{key}: {value}" for key, value in combo.items()) or "single SKU"
            lines.append(f"- {combo_label}: `{unit.get('chosen_price')}` -> business_review_required")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _source_artifact() -> dict[str, Any]:
    return json.loads(SOURCE_ARTIFACT.read_text(encoding="utf-8"))


def _rooted(path: str) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return candidate.resolve()


if __name__ == "__main__":
    sys.exit(main())
