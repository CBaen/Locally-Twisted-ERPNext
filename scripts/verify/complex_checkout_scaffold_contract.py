#!/usr/bin/env python3
"""Pure contract checks for the complex checkout scaffold classifier.

Run:
  python scripts/verify/complex_checkout_scaffold_contract.py
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any

from _cli import parse_noop_args


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps" / "locally_twisted"))

from locally_twisted.catalog_contract.complex_checkout_scaffold import (  # noqa: E402
    build_complex_checkout_scaffold_report,
)


class ComplexCheckoutScaffoldContract(unittest.TestCase):
    def test_classifies_direct_simple_multi_color_addon_and_classic_arch_rows(self) -> None:
        report = build_complex_checkout_scaffold_report(
            _artifact(
                [
                    _row("direct-product", lane="checkout", capability="direct_checkout_ready"),
                    _row(
                        "simple-quote-product",
                        lane="quote_first",
                        capability="quote_first_supported",
                        required_axes=["Size"],
                    ),
                    _row(
                        "color-product",
                        lane="quote_first",
                        capability="quote_first_supported",
                        patterns=["multi_color_recipes"],
                        customization_axes=["Latex Colors"],
                    ),
                    _row(
                        "addon-product",
                        lane="quote_first",
                        capability="quote_first_supported",
                        patterns=["add_ons", "conditional_pricing"],
                        add_on_axes=["Add ons"],
                        conditional_pricing_axes=["Balloon Count"],
                    ),
                    _row(
                        "classic-arch",
                        lane="quote_first",
                        capability="quote_first_supported",
                        patterns=["multi_color_recipes"],
                        customization_axes=["Latex Colors", "Color Palette"],
                    ),
                ]
            ),
            expected_source_products=5,
            expected_direct_checkout_products=1,
        )

        self.assertEqual(report.contract_failures, ())
        rows = {row.slug: row for row in report.rows}
        self.assertEqual(rows["direct-product"].scaffold_stage, "direct_checkout_regression_guard")
        self.assertEqual(rows["simple-quote-product"].scaffold_stage, "simple_axis_lane_flip_candidate")
        self.assertTrue(rows["simple-quote-product"].lane_flip_policy["may_enter_focused_local_lane_flip_rehearsal"])
        self.assertEqual(rows["color-product"].scaffold_stage, "multi_color_recipe_ui_required")
        self.assertIn("multi_slot_color_recipe_builder", rows["color-product"].required_ui_components)
        self.assertIn("color_recipe_summary_parity", rows["color-product"].required_ui_components)
        self.assertTrue(any("post_import_checkout_proof" in gate for gate in rows["color-product"].gate_verifiers))
        self.assertEqual(rows["addon-product"].scaffold_stage, "add_on_or_conditional_pricing_blocked")
        self.assertIn("add_on_contract_ui", rows["addon-product"].required_ui_components)
        self.assertIn("conditional_pricing_panel", rows["addon-product"].required_ui_components)
        self.assertEqual(rows["classic-arch"].proof_ladder_stage, "06_classic_arch_last")
        self.assertEqual(
            rows["classic-arch"].special_rules["design_dependent_color_limits"][0]["max_color_count"],
            4,
        )

    def test_checkout_lane_with_blockers_fails_the_scaffold_gate(self) -> None:
        report = build_complex_checkout_scaffold_report(
            _artifact(
                [
                    _row(
                        "broken-checkout-product",
                        lane="checkout",
                        capability="checkout_architecture_gap",
                        blockers=["multi_color_recipe_configuration_contract_needed"],
                        customization_axes=["Latex Colors"],
                    )
                ]
            ),
            expected_source_products=1,
            expected_direct_checkout_products=1,
        )

        self.assertFalse(report.summary()["ok"])
        self.assertIn(
            "explicit checkout products have architecture gaps: ['broken-checkout-product']",
            report.contract_failures,
        )

    def test_add_on_rows_never_become_simple_lane_flip_candidates(self) -> None:
        report = build_complex_checkout_scaffold_report(
            _artifact(
                [
                    _row(
                        "review-only-addon-product",
                        lane="quote_first",
                        capability="quote_first_supported",
                        add_on_axes=["Add ons"],
                        review_only_axes=["Plush add ons"],
                    )
                ]
            ),
            expected_source_products=1,
            expected_direct_checkout_products=0,
        )

        row = report.rows[0]
        self.assertEqual(row.scaffold_stage, "add_on_or_conditional_pricing_blocked")
        self.assertFalse(row.lane_flip_policy["customer_checkout_enablement_allowed_by_this_report"])
        self.assertTrue(row.lane_flip_policy["do_not_flip_until"])
        self.assertNotEqual(row.scaffold_stage, "simple_axis_lane_flip_candidate")


def _artifact(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "lt-erpnext-product-pattern-contract-v1",
        "read_only": True,
        "destructive_allowed": False,
        "summary": {
            "source_products": len(rows),
            "explicit_checkout_products": sum(
                1 for row in rows if (row.get("checkout_eligibility") or {}).get("website_lane") == "checkout"
            ),
        },
        "products": rows,
    }


def _row(
    slug: str,
    *,
    lane: str,
    capability: str,
    patterns: list[str] | None = None,
    required_axes: list[str] | None = None,
    customization_axes: list[str] | None = None,
    add_on_axes: list[str] | None = None,
    review_only_axes: list[str] | None = None,
    conditional_pricing_axes: list[str] | None = None,
    blockers: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "slug": slug,
        "source_name": slug.replace("-", " ").title(),
        "patterns": patterns or [],
        "capability": capability,
        "website_item": {"route": f"/shop/{slug}", "lt_commerce_lane": lane},
        "source_axes": {
            "required_sale_unit_axes": required_axes or [],
            "customization_axes": customization_axes or [],
            "add_on_axes": add_on_axes or [],
            "review_only_axes": review_only_axes or [],
            "conditional_pricing_axes": conditional_pricing_axes or [],
            "freeform_customer_text_axes": [],
        },
        "checkout_eligibility": {
            "website_lane": lane,
            "blocking_reasons": blockers or [],
            "representative_priced_item_ready": True,
            "line_configuration_fields_ready": True,
        },
        "server_boundary": {
            "selected_config_schema": {
                "website_item_code": slug,
                "selected_options": {},
                "color_recipes": [],
                "add_ons": [],
                "customizations": [],
            }
        },
        "live_counts": {},
    }


def main() -> int:
    parse_noop_args(__doc__)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ComplexCheckoutScaffoldContract)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
