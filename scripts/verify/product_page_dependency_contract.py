#!/usr/bin/env python3
"""Verify source option-dependency matrices for product-page contracts.

Read-only. Does not touch ERPNext.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps" / "locally_twisted"))

from locally_twisted.catalog_contract import (
    OptionDependencyMatrixContract,
    available_options_for_selection,
    build_product_page_contract,
)


SOURCE_CATALOG = ROOT / "_resources/odoo-live/catalog.json"
SLUG_TO_GROUP = ROOT / "_resources/odoo-live/slug_to_group.json"


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
    failures: list[str] = []
    contracts = {
        slug: build_product_page_contract(_find(products, slug), category_hint=groups.get(slug, ""))
        for slug in ("classic-arch", "unicorn-bouquet")
    }

    classic = contracts["classic-arch"]
    unicorn = contracts["unicorn-bouquet"]

    if not classic.dependency_matrices:
        failures.append("Classic Arch missing dependency_matrices")
    else:
        matrix = classic.dependency_matrices[0]
        if matrix.source_variant_rows != 848:
            failures.append(f"Classic Arch dependency matrix should preserve 848 source rows, found {matrix.source_variant_rows}")
        if matrix.valid_combination_count != 16:
            failures.append(
                f"Classic Arch dependency matrix should dedupe to 16 required-axis combinations, found {matrix.valid_combination_count}"
            )
        if "latex colors" in matrix.axes:
            failures.append("Classic Arch dependency matrix must not treat latex colors as a required SKU axis")
        if set(matrix.axes) != {"Arch Size", "Design", "LED Lights"}:
            failures.append(f"Classic Arch dependency axes wrong: {matrix.axes}")

    if not unicorn.dependency_matrices:
        failures.append("Unicorn Bouquet missing dependency_matrices")
    else:
        matrix = unicorn.dependency_matrices[0]
        if matrix.valid_combination_count != 3:
            failures.append(f"Unicorn Bouquet dependency matrix should dedupe to 3 bouquet-size combinations, found {matrix.valid_combination_count}")
        if matrix.axes != ("Bouquet Size",):
            failures.append(f"Unicorn Bouquet dependency axes should only be Bouquet Size, found {matrix.axes}")

    helper_failures = _dependency_helper_failures()
    failures.extend(helper_failures)

    if failures:
        print("[PRODUCT PAGE DEPENDENCY CONTRACT] FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("[PRODUCT PAGE DEPENDENCY CONTRACT] PASS")
    print(
        json.dumps(
            {
                "classic_arch": {
                    "axes": classic.dependency_matrices[0].axes,
                    "source_variant_rows": classic.dependency_matrices[0].source_variant_rows,
                    "valid_combination_count": classic.dependency_matrices[0].valid_combination_count,
                },
                "unicorn_bouquet": {
                    "axes": unicorn.dependency_matrices[0].axes,
                    "source_variant_rows": unicorn.dependency_matrices[0].source_variant_rows,
                    "valid_combination_count": unicorn.dependency_matrices[0].valid_combination_count,
                },
                "helper_contract": {
                    "available_options_for_selection": "narrows partial selections and fails loudly on impossible or unknown axes",
                },
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def _dependency_helper_failures() -> list[str]:
    failures: list[str] = []
    matrix = OptionDependencyMatrixContract(
        axes=("Size", "Design"),
        valid_combinations=(
            {"Size": "Small", "Design": "Classic"},
            {"Size": "Large", "Design": "Deluxe"},
        ),
        source_variant_rows=2,
        valid_combination_count=2,
    )
    narrowed = available_options_for_selection(matrix, {"Size": "Small"})
    if narrowed.get("Design") != ("Classic",):
        failures.append(f"dependency helper did not narrow Design for Small: {narrowed}")
    if narrowed.get("Size") != ("Small",):
        failures.append(f"dependency helper did not preserve selected Size: {narrowed}")
    all_options = available_options_for_selection(matrix, {})
    if all_options.get("Design") != ("Classic", "Deluxe"):
        failures.append(f"dependency helper did not expose all initial Design values: {all_options}")
    try:
        available_options_for_selection(matrix, {"Size": "Small", "Design": "Deluxe"})
    except ValueError as exc:
        if "No valid option combination" not in str(exc):
            failures.append(f"invalid dependency selection failed unclearly: {exc}")
    else:
        failures.append("dependency helper should fail loudly for impossible combinations")
    try:
        available_options_for_selection(matrix, {"latex colors": "Red"})
    except ValueError as exc:
        if "Unknown dependency axis" not in str(exc):
            failures.append(f"unknown dependency axis failed unclearly: {exc}")
    else:
        failures.append("dependency helper should fail loudly for unknown axes")
    return failures


if __name__ == "__main__":
    raise SystemExit(main())
