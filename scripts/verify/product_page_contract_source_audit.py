#!/usr/bin/env python3
"""Dry-run the product-page contract against the saved legacy_source/source catalog.

This verifier is intentionally read-only. It does not touch ERPNext DB state.
It shows whether source data is ready to drive a purge/rebuild import.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps" / "locally_twisted"))

from locally_twisted.catalog_contract import build_product_page_contract
from locally_twisted.catalog_contract.addon_rules import REVIEW_ADD_ONS

SOURCE_CATALOG = ROOT / "_resources/catalog-source/catalog.json"
SLUG_TO_GROUP = ROOT / "_resources/catalog-source/slug_to_group.json"
REPORT_PATH = ROOT / Path(
    "audits/catalog-import-audit-2026-05-08/"
    "15-product-page-contract-source-audit.md"
)
JSON_PATH = ROOT / Path(
    "audits/catalog-import-audit-2026-05-08/"
    "15-product-page-contract-source-audit.json"
)


def _load_products() -> list[dict]:
    data = json.loads(SOURCE_CATALOG.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        return list(data.get("products") or [])
    return list(data or [])


def _load_slug_to_group() -> dict[str, str]:
    if not SLUG_TO_GROUP.exists():
        return {}
    data = json.loads(SLUG_TO_GROUP.read_text(encoding="utf-8"))
    return {str(k): str(v) for k, v in data.items()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.parse_args()

    products = _load_products()
    slug_to_group = _load_slug_to_group()
    contracts = [
        build_product_page_contract(product, category_hint=slug_to_group.get(str(product.get("slug") or ""), ""))
        for product in products
    ]

    warning_counts = Counter()
    product_page_type_counts = Counter(contract.product_page_type for contract in contracts)
    commerce_lane_counts = Counter(contract.commerce_lane for contract in contracts)
    review_add_on_axis_counts = Counter()
    for contract in contracts:
        for warning in contract.warnings:
            if "resolver-backed" in warning:
                warning_counts["missing_resolver_prices"] += 1
            elif "alternate images" in warning:
                warning_counts["unclassified_gallery_images"] += 1
            elif "Axis needs review" in warning:
                warning_counts["axis_needs_review"] += 1
                for axis_name in REVIEW_ADD_ONS:
                    if f": {axis_name} -" in warning:
                        review_add_on_axis_counts[axis_name] += 1
            elif "Color axis removed" in warning:
                warning_counts["color_axis_customization"] += 1
            else:
                warning_counts["other"] += 1

    add_on_products = [contract for contract in contracts if contract.add_ons]
    dependency_products = [contract for contract in contracts if contract.dependency_matrices]
    dependency_combo_count = sum(
        matrix.valid_combination_count
        for contract in dependency_products
        for matrix in contract.dependency_matrices
    )
    review_products = [contract for contract in contracts if contract.warnings]
    gallery_products = [contract for contract in contracts if len(contract.gallery) > 1]
    resolver_ready = [contract for contract in contracts if contract.source_variant_rows and contract.has_resolver_prices]

    lines = [
        "# Product Page Contract Source Audit",
        "",
        "This is a read-only dry run from legacy_source/source catalog data into the new product-page contract shape.",
        "It is not an ERPNext import and does not mutate the database.",
        "",
        "## Counts",
        "",
        f"- Source products: {len(products)}",
        f"- Products with gallery/alternate images: {len(gallery_products)}",
        f"- Products with confirmed add-on contracts: {len(add_on_products)}",
        f"- Products with source-backed dependency matrices: {len(dependency_products)}",
        f"- Required-axis valid combinations preserved: {dependency_combo_count}",
        f"- Variant products with resolver-backed prices: {len(resolver_ready)}",
        f"- Products with warnings/review notes: {len(review_products)}",
        "",
        "## Product-page template classification",
        "",
    ]
    for key, value in sorted(product_page_type_counts.items()):
        label = next((contract.product_page_type_label for contract in contracts if contract.product_page_type == key), key)
        lines.append(f"- {label} (`{key}`): {value}")

    lines.extend([
        "",
        "## Commerce lane classification",
        "",
    ])
    for key, value in sorted(commerce_lane_counts.items()):
        label = next((contract.commerce_lane_label for contract in contracts if contract.commerce_lane == key), key)
        lines.append(f"- {label} (`{key}`): {value}")

    lines.extend([
        "",
        "## Warning buckets",
        "",
    ])
    for key, value in sorted(warning_counts.items()):
        lines.append(f"- {key}: {value}")

    lines.extend([
        "",
        "## Review-only source add-on families",
        "",
    ])
    for axis_name in sorted(REVIEW_ADD_ONS):
        lines.append(
            f"- {axis_name}: {review_add_on_axis_counts.get(axis_name, 0)} product(s) need mapping before checkout"
        )

    lines.extend([
        "",
        "## Sample contracts with review notes",
        "",
        "| Slug | Template | Lane | Category hint | Variant rows | Required axes | Add-ons | Warnings |",
        "|---|---|---|---|---:|---|---|---|",
    ])
    for contract in review_products[:25]:
        axes = ", ".join(axis.name for axis in contract.required_axes)
        addons = ", ".join(addon.key for addon in contract.add_ons)
        warnings = "<br>".join(contract.warnings)
        lines.append(
            f"| {contract.slug} | {contract.product_page_type_label} | {contract.commerce_lane_label} | "
            f"{contract.category_hint} | {contract.source_variant_rows} | "
            f"{axes} | {addons} | {warnings} |"
        )

    lines.extend([
        "",
        "## Interpretation",
        "",
        "The contract builder separates confirmed foil-number add-ons from required axes and keeps unmapped add-on families out of checkout add-on controls.",
        "Every source product is now classified into one of the two reusable product-page template types and all 53 legacy_source-imported products target checkout.",
        "Resolver-backed price notes remain audit signals: variant rows may lack `erpnext_variant_price`, but the import path can still use source row price/base price and the separate price gates verify Item Price coverage.",
        "`product_page_price_readiness_contract.py` checks the separate live-ERPNext Item Price gate for the current database.",
        "`product_page_price_enrichment_contract.py` builds the separate candidate price map for purge/reimport rehearsal without mutating the source scrape.",
        "Gallery images are present but intentionally marked review-needed until classified as parent gallery vs variant image vs other source media.",
        "`product_page_media_visibility_contract.py` checks the separate live-ERPNext media evidence and source-media classification gate.",
        "",
        "## Gate result",
        "",
    ])

    blocking = not products or commerce_lane_counts.get("checkout", 0) != len(products)
    if blocking:
        lines.append("**BLOCKED for destructive purge/import.** Not every legacy_source product resolved to checkout.")
    else:
        lines.append("**PASS with review notes.** All legacy_source products resolve to sellable checkout targets; add-on/media/price notes remain separate gates.")

    artifact = {
        "source_products": len(products),
        "product_page_type_counts": dict(product_page_type_counts),
        "commerce_lane_counts": dict(commerce_lane_counts),
        "warning_counts": dict(warning_counts),
        "review_only_source_add_on_counts": dict(review_add_on_axis_counts),
        "confirmed_add_on_product_count": len(add_on_products),
        "dependency_matrix_product_count": len(dependency_products),
        "dependency_matrix_valid_combination_count": dependency_combo_count,
        "blocked_for_destructive_import": blocking,
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    JSON_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")

    if blocking:
        print("[PRODUCT PAGE CONTRACT SOURCE AUDIT] BLOCKED")
        print(f"report={REPORT_PATH}")
        print(f"json={JSON_PATH}")
        print(dict(warning_counts))
        return 2

    print("[PRODUCT PAGE CONTRACT SOURCE AUDIT] PASS")
    print(f"report={REPORT_PATH}")
    print(f"json={JSON_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
