#!/usr/bin/env python3
"""Verify the two GL-selected proof products in the source contract.

Read-only. Does not touch ERPNext.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps" / "locally_twisted"))

from locally_twisted.catalog_contract import build_product_page_contract

SOURCE_CATALOG = ROOT / "_resources/odoo-live/catalog.json"
SLUG_TO_GROUP = ROOT / "_resources/odoo-live/slug_to_group.json"
REPORT_PATH = ROOT / Path(
    "audits/odoo-erpnext-migration-audit-2026-05-08/"
    "18-proof-product-contract-report.md"
)


def _products() -> list[dict]:
    data = json.loads(SOURCE_CATALOG.read_text(encoding="utf-8"))
    return list(data.get("products") if isinstance(data, dict) else data)


def _groups() -> dict[str, str]:
    if not SLUG_TO_GROUP.exists():
        return {}
    return json.loads(SLUG_TO_GROUP.read_text(encoding="utf-8"))


def _find(products: list[dict], slug: str) -> dict:
    for product in products:
        if product.get("slug") == slug:
            return product
    raise AssertionError(f"Missing proof product in source catalog: {slug}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.parse_args()

    products = _products()
    groups = _groups()
    contracts = {
        slug: build_product_page_contract(_find(products, slug), category_hint=groups.get(slug, ""))
        for slug in ["unicorn-bouquet", "classic-arch"]
    }

    failures: list[str] = []
    unicorn = contracts["unicorn-bouquet"]
    classic = contracts["classic-arch"]

    if not any(axis.name == "Bouquet Size" for axis in unicorn.required_axes):
        failures.append("Unicorn Bouquet must keep Bouquet Size as a required visible selector.")
    if unicorn.product_page_type != "simple_product" or unicorn.commerce_lane != "checkout":
        failures.append(
            f"Unicorn Bouquet must classify as simple_product/checkout, found {unicorn.product_page_type}/{unicorn.commerce_lane}."
        )
    if not any(addon.key == "foil_number" for addon in unicorn.add_ons):
        failures.append("Unicorn Bouquet must expose foil number as optional add-on contract.")
    if len(unicorn.gallery) < 2:
        failures.append("Unicorn Bouquet should have primary + alternate gallery image evidence.")

    latex_axes = [axis for axis in classic.customization_axes if axis.name == "latex colors"]
    if not latex_axes:
        failures.append("Classic Arch must move latex colors into customization_axes.")
    else:
        latex = latex_axes[0]
        if latex.selector_type != "multi_select_drawer":
            failures.append("Classic Arch latex colors must use multi_select_drawer selector type.")
        group_names = {group.group for group in latex.color_groups}
        for required_group in ["Pastels", "Reflex", "Dusk"]:
            if required_group not in group_names:
                failures.append(f"Classic Arch color groups missing {required_group} drawer.")
        if len(latex.values) < 50:
            failures.append("Classic Arch latex colors should preserve the full high-cardinality color list.")
    if any(axis.name == "latex colors" for axis in classic.required_axes):
        failures.append("Classic Arch latex colors must not remain a normal required ERPNext variant selector/dropdown.")
    if classic.product_page_type != "complex_custom_product" or classic.commerce_lane != "quote_first":
        failures.append(
            f"Classic Arch must classify as complex_custom_product/quote_first, found {classic.product_page_type}/{classic.commerce_lane}."
        )
    if not classic.dependency_matrices:
        failures.append("Classic Arch must preserve source valid-option dependency matrix.")
    else:
        matrix = classic.dependency_matrices[0]
        if matrix.axes != ("Arch Size", "Design", "LED Lights") or matrix.valid_combination_count != 16:
            failures.append(f"Classic Arch dependency matrix wrong: axes={matrix.axes}, combinations={matrix.valid_combination_count}.")

    lines = [
        "# Proof Product Contract Report",
        "",
        "Read-only contract verification for GL-selected proof products.",
        "",
        "## Unicorn Bouquet",
        "",
        f"- Template: {unicorn.product_page_type_label} (`{unicorn.product_page_type}`)",
        f"- Commerce lane: {unicorn.commerce_lane_label} (`{unicorn.commerce_lane}`)",
        f"- Required axes: {', '.join(axis.name for axis in unicorn.required_axes) or '(none)'}",
        f"- Add-ons: {', '.join(addon.key for addon in unicorn.add_ons) or '(none)'}",
        f"- Gallery images in source contract: {len(unicorn.gallery)}",
        f"- Warnings: {len(unicorn.warnings)}",
        "",
        "## Classic Arch",
        "",
        f"- Template: {classic.product_page_type_label} (`{classic.product_page_type}`)",
        f"- Commerce lane: {classic.commerce_lane_label} (`{classic.commerce_lane}`)",
        f"- Required axes: {', '.join(axis.name for axis in classic.required_axes) or '(none)'}",
        f"- Customization axes: {', '.join(axis.name for axis in classic.customization_axes) or '(none)'}",
        f"- Gallery images in source contract: {len(classic.gallery)}",
        f"- Dependency matrices: {len(classic.dependency_matrices)}",
        f"- Warnings: {len(classic.warnings)}",
        "",
    ]

    latex_axes = [axis for axis in classic.customization_axes if axis.name == "latex colors"]
    if latex_axes:
        latex = latex_axes[0]
        lines.extend([
            "### Classic Arch latex color drawers",
            "",
            f"Selector type: `{latex.selector_type}`",
            "",
        ])
        for group in latex.color_groups:
            lines.append(f"- {group.group}: {len(group.options)} colors")

    lines.extend(["", "## Gate result", ""])
    if failures:
        lines.append("**FAIL**")
        lines.append("")
        for failure in failures:
            lines.append(f"- {failure}")
        REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
        print("[PROOF PRODUCT CONTRACT] FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    lines.append("**PASS for proof-product contract shape.** Source import is still blocked by price/media review gates elsewhere.")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print("[PROOF PRODUCT CONTRACT] PASS")
    print(f"report={REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
