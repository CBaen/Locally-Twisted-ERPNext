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
                    "source_name": "Protected Quote Product",
                    "slug": "protected-quote-product",
                    "product_contract": {"commerce_lane": "quote_first"},
                    "add_on_manifest": {"review_only_axes_from_global_packet": ["Add ons"]},
                }
            ]
        }
    )
    if protected_row.status != "pass":
        failures.append(
            "quote-first review-only add-ons should be treated as protected pass, "
            f"found {protected_row.status}: {protected_row.summary}"
        )

    checkout_row = _add_on_row_for_manifest(
        {
            "products": [
                {
                    "source_name": "Unsafe Checkout Product",
                    "slug": "unsafe-checkout-product",
                    "product_contract": {"commerce_lane": "checkout"},
                    "add_on_manifest": {"review_only_axes_from_global_packet": ["Add ons"]},
                }
            ]
        }
    )
    if checkout_row.status != "blocker":
        failures.append(
            "checkout review-only add-ons should remain a blocker, "
            f"found {checkout_row.status}: {checkout_row.summary}"
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
