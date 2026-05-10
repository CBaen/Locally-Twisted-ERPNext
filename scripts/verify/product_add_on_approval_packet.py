#!/usr/bin/env python3
"""Build and verify the source add-on approval packet.

Run:
  python scripts/verify/product_add_on_approval_packet.py
  python scripts/verify/product_add_on_approval_packet.py --json
  python scripts/verify/product_add_on_approval_packet.py --report output/product-add-on-approval-packet.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps" / "locally_twisted"))

from locally_twisted.catalog_contract.addon_review import build_add_on_approval_packet
from locally_twisted.catalog_contract.addon_rules import REVIEW_ADD_ONS


SOURCE_CATALOG = ROOT / "_resources/odoo-live/catalog.json"
SLUG_TO_GROUP = ROOT / "_resources/odoo-live/slug_to_group.json"
DEFAULT_REPORT = ROOT / "audits/odoo-erpnext-migration-audit-2026-05-08/22-product-add-on-approval-packet.json"
DEFAULT_MARKDOWN = ROOT / "audits/odoo-erpnext-migration-audit-2026-05-08/22-product-add-on-approval-packet.md"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true", help="Print full packet JSON")
    parser.add_argument("--report", help="Write packet JSON to a file")
    parser.add_argument("--markdown", help="Write packet Markdown to a file")
    args = parser.parse_args()

    packet = build_add_on_approval_packet(
        _products(),
        review_add_ons=REVIEW_ADD_ONS,
        slug_to_group=_slug_to_group(),
    )
    failures = _contract_failures(packet)
    rendered = json.dumps(packet, indent=2, sort_keys=True)

    report_path = _rooted(args.report) if args.report else DEFAULT_REPORT
    markdown_path = _rooted(args.markdown) if args.markdown else DEFAULT_MARKDOWN
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(rendered + "\n", encoding="utf-8")
    markdown_path.write_text(_to_markdown(packet), encoding="utf-8")

    print(f"[PRODUCT ADD-ON APPROVAL PACKET] wrote {report_path.relative_to(ROOT)}")
    print(f"[PRODUCT ADD-ON APPROVAL PACKET] wrote {markdown_path.relative_to(ROOT)}")
    if args.json:
        print(rendered)
    else:
        _print_summary(packet, failures)

    return 0 if not failures else 1


def _contract_failures(packet: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    expected_axes = set(REVIEW_ADD_ONS)
    rows = packet.get("review_axes")
    if not isinstance(rows, list):
        return ["review_axes must be a list"]
    axis_names = {row.get("axis") for row in rows if isinstance(row, dict)}
    missing_axes = sorted(expected_axes - axis_names)
    if missing_axes:
        failures.append("missing review add-on axes: " + ", ".join(missing_axes))
    if packet.get("approved_for_checkout_count") != 0:
        failures.append("review packet approved an add-on for checkout")
    if int(packet.get("affected_product_count") or 0) <= 0:
        failures.append("review packet has no affected products")
    for row in rows:
        if not isinstance(row, dict):
            failures.append("review_axes contains a non-object row")
            continue
        axis = row.get("axis")
        for fieldname in ("decision_needed", "recommended_safe_default", "source_values", "products"):
            if not row.get(fieldname):
                failures.append(f"{axis} missing {fieldname}")
        if row.get("recommended_safe_default") != "quote_only_until_approved":
            failures.append(f"{axis} safe default must be quote_only_until_approved")
        if row.get("checkout_allowed") is not False:
            failures.append(f"{axis} must not be checkout_allowed")
        if int(row.get("product_count") or 0) != len(row.get("products") or []):
            failures.append(f"{axis} product_count does not match products list")
    return failures


def _print_summary(packet: dict[str, Any], failures: list[str]) -> None:
    print("[PRODUCT ADD-ON APPROVAL PACKET] " + ("PASS" if not failures else "FAIL"))
    print(f"  source_products: {packet.get('source_product_count')}")
    print(f"  review_axes: {packet.get('review_axis_count')}")
    print(f"  affected_products: {packet.get('affected_product_count')}")
    print(f"  approved_for_checkout_count: {packet.get('approved_for_checkout_count')}")
    for row in packet.get("review_axes") or []:
        print(
            f"  - {row.get('axis')}: {row.get('product_count')} product(s), "
            f"{len(row.get('source_values') or [])} value(s), default={row.get('recommended_safe_default')}"
        )
    if failures:
        print("  failures:")
        for failure in failures:
            print(f"    - {failure}")


def _to_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# Product Add-on Approval Packet",
        "",
        "This packet is source-backed and read-only. It does not approve checkout add-ons.",
        "Every row defaults to quote-only until GL/Locally Twisted approves a product-family mapping.",
        "",
        "## Summary",
        "",
        f"- Source products: {packet.get('source_product_count')}",
        f"- Review axes: {packet.get('review_axis_count')}",
        f"- Affected products: {packet.get('affected_product_count')}",
        f"- Approved for checkout: {packet.get('approved_for_checkout_count')}",
        "",
        "## Review Rows",
        "",
        "| Axis | Product count | Values | Decision needed | Safe default |",
        "|---|---:|---|---|---|",
    ]
    for row in packet.get("review_axes") or []:
        values = ", ".join(row.get("source_values") or [])
        lines.append(
            f"| {row.get('axis')} | {row.get('product_count')} | {values} | "
            f"{row.get('decision_needed')} | {row.get('recommended_safe_default')} |"
        )
    lines.extend(["", "## Affected Products", ""])
    for row in packet.get("review_axes") or []:
        lines.extend([f"### {row.get('axis')}", ""])
        for product in row.get("products") or []:
            values = ", ".join(product.get("source_values") or [])
            lines.append(
                f"- `{product.get('slug')}`: {product.get('title')} "
                f"({product.get('commerce_lane_label')}); values: {values}"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _products() -> list[dict[str, Any]]:
    data = json.loads(SOURCE_CATALOG.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        return list(data.get("products") or [])
    return list(data or [])


def _slug_to_group() -> dict[str, str]:
    if not SLUG_TO_GROUP.exists():
        return {}
    data = json.loads(SLUG_TO_GROUP.read_text(encoding="utf-8"))
    return {str(key): str(value) for key, value in data.items() if not str(key).startswith("_")}


def _rooted(path: str) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return candidate.resolve()


if __name__ == "__main__":
    sys.exit(main())
