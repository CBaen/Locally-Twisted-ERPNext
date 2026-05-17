#!/usr/bin/env python3
"""Verify no-snapshot readiness gate command-packet path handling.

Run:
  python scripts/verify/product_import_readiness_gate_contract.py
"""
from __future__ import annotations

import sys

from _cli import parse_noop_args
import product_import_readiness_gate as gate

EXPECTED_PLACEHOLDER = "<fresh current-state-snapshot-* required>"


def _add_on_row_for_manifest(manifest: dict) -> gate.GateRow:
    original_optional_json = gate._optional_json
    try:
        gate._optional_json = lambda _path: manifest
        return gate._v1_add_on_row()
    finally:
        gate._optional_json = original_optional_json


def main() -> int:
    parse_noop_args(__doc__)

    failures: list[str] = []
    try:
        display_path = gate._snapshot_display_path([])
    except ValueError as exc:
        failures.append(f"empty snapshot list raised ValueError: {exc}")
    else:
        if display_path != EXPECTED_PLACEHOLDER:
            failures.append(f"empty snapshot list returned {display_path!r}, expected {EXPECTED_PLACEHOLDER!r}")

    protected_row = _add_on_row_for_manifest(
        {
            "products": [
                {
                    "source_name": "Protected Checkout Product",
                    "slug": "protected-checkout-product",
                    "product_contract": {"commerce_lane": "checkout"},
                    "add_on_manifest": {"review_only_axes_from_global_packet": ["Add ons"]},
                }
            ]
        }
    )
    if protected_row.status != "pass":
        failures.append(
            "review-only add-ons should be hidden without blocking the product import, "
            f"found {protected_row.status}: {protected_row.summary}"
        )

    no_add_on_row = _add_on_row_for_manifest(
        {
            "products": [
                {
                    "source_name": "Plain Checkout Product",
                    "slug": "plain-checkout-product",
                    "product_contract": {"commerce_lane": "checkout"},
                    "add_on_manifest": {"review_only_axes_from_global_packet": []},
                }
            ]
        }
    )
    if no_add_on_row.status != "pass":
        failures.append(
            "products with no review-only add-ons should pass, "
            f"found {no_add_on_row.status}: {no_add_on_row.summary}"
        )

    if failures:
        print("[PRODUCT IMPORT READINESS GATE CONTRACT] FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("[PRODUCT IMPORT READINESS GATE CONTRACT] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
