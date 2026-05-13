#!/usr/bin/env python3
"""Pure checks for the generic product-page architecture contract.

Run:
  python scripts/verify/product_page_architecture_contract_contract.py
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any

from _cli import parse_noop_args


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps" / "locally_twisted"))

from locally_twisted.catalog_contract.product_page_architecture_contract import (  # noqa: E402
    build_product_page_architecture_contract,
    build_product_page_architecture_report,
    validate_product_page_architecture_contract,
)


class ProductPageArchitectureContractTest(unittest.TestCase):
    def test_maps_axes_to_payload_targets_without_product_specific_rules(self) -> None:
        contract = build_product_page_architecture_contract(
            _row(
                axes=[
                    _axis("Size", "sale_unit", values=["Small", "Large"]),
                    _axis("latex colors", "customization", values=["White", "Gold"], multi=True),
                    _axis("Foil number", "add_on", add_on_ready=True),
                ],
                status="checkout_ready",
                lane="checkout",
            )
        ).to_dict()

        self.assertTrue(contract["checkout_allowed"])
        self.assertFalse(contract["product_specific_rules_allowed"])
        controls = {control["axis_name"]: control for control in contract["controls"]}
        self.assertEqual(controls["Size"]["payload_target"], "selected_options")
        self.assertEqual(controls["latex colors"]["payload_target"], "color_recipes")
        self.assertEqual(controls["Foil number"]["payload_target"], "add_ons")
        self.assertIn("canonical_cart_line_key", contract["payload_contract"]["server_derived_keys"])
        self.assertEqual(validate_product_page_architecture_contract(contract), [])

    def test_review_only_add_on_blocks_checkout_instead_of_becoming_free_option(self) -> None:
        contract = build_product_page_architecture_contract(
            _row(
                axes=[
                    _axis("Package", "sale_unit", values=["Standard"]),
                    _axis("Plush add ons", "review_only", values=["Bear"]),
                ],
                status="needs_add_on_pricing",
                lane="checkout",
                fail_loud=["review_only_add_on"],
            )
        ).to_dict()

        self.assertFalse(contract["checkout_allowed"])
        controls = {control["axis_name"]: control for control in contract["controls"]}
        self.assertEqual(controls["Plush add ons"]["payload_target"], "quote_context")
        self.assertIn("review_only_add_on", contract["fail_loud_states"])

    def test_color_customization_never_targets_selected_options(self) -> None:
        contract = build_product_page_architecture_contract(
            _row(axes=[_axis("Color Palette", "customization", values=["Bright"], multi=True)])
        ).to_dict()
        controls = {control["axis_name"]: control for control in contract["controls"]}
        self.assertEqual(controls["Color Palette"]["selector_type"], "multi_color_recipe_builder")
        self.assertEqual(controls["Color Palette"]["payload_target"], "color_recipes")

        broken = dict(contract)
        broken["controls"] = [dict(control) for control in contract["controls"]]
        broken["controls"][0]["payload_target"] = "selected_options"
        failures = validate_product_page_architecture_contract(broken)
        self.assertTrue(any("color customization must target color_recipes" in failure for failure in failures))

    def test_report_fails_structural_contract_errors_only(self) -> None:
        report = build_product_page_architecture_report(
            [
                _row(slug="checkout-proof", axes=[_axis("Size", "sale_unit")], status="checkout_ready", lane="checkout"),
                _row(
                    slug="quote-proof",
                    axes=[_axis("Add ons", "review_only")],
                    status="needs_add_on_pricing",
                    lane="quote_first",
                    fail_loud=["review_only_add_on"],
                ),
            ]
        )
        self.assertTrue(report["ok"])
        self.assertEqual(report["summary"]["product_count"], 2)
        self.assertEqual(report["summary"]["product_specific_rules_allowed"], False)


def _row(
    slug: str = "architecture-proof-product",
    *,
    axes: list[dict[str, Any]] | None = None,
    status: str = "checkout_ready",
    lane: str = "checkout",
    fail_loud: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": "lt-product-pattern-contract-v1",
        "slug": slug,
        "item_code": slug,
        "source_name": slug.replace("-", " ").title(),
        "route": f"shop-items/proof/{slug}",
        "current_page_type": "simple_product" if lane == "checkout" else "complex_custom_product",
        "current_commerce_lane": lane,
        "axis_contracts": axes or [],
        "checkout_eligibility": {
            "status": status,
            "current_commerce_lane": lane,
            "fail_loud_states": fail_loud or [],
            "required_work": ["quote/review before checkout"] if fail_loud else [],
        },
        "order_preservation_contract": {
            "line_fields": {
                "Quotation Item": _line_fields(),
                "Sales Order Item": _line_fields(),
                "Sales Invoice Item": _line_fields(),
            },
            "summary_required": True,
            "json_required": True,
            "add_on_line_detail_required": True,
            "color_recipe_detail_required": True,
        },
    }


def _axis(
    name: str,
    role: str,
    *,
    values: list[str] | None = None,
    multi: bool = False,
    add_on_ready: bool = False,
) -> dict[str, Any]:
    return {
        "name": name,
        "role": role,
        "values": values or ["One"],
        "selector_type": "multi_color_recipe_builder" if multi else "single_select",
        "allows_multiple_values": multi,
        "source": "odoo_source",
        "status": "ready",
        "add_on_contract": {
            "ready_for_checkout": add_on_ready,
            "item_code": "ADDON-PROOF" if add_on_ready else "",
            "price_status": "ready" if add_on_ready else "",
            "live_unit_price": "12.00" if add_on_ready else "",
            "quantity_min": 1 if add_on_ready else "",
            "quantity_max": 4 if add_on_ready else "",
            "receipt_label": "Proof add-on" if add_on_ready else "",
        },
    }


def _line_fields() -> tuple[str, ...]:
    return (
        "custom_lt_product_template_item",
        "custom_lt_product_page_type",
        "custom_lt_configuration_version",
        "custom_lt_configuration_summary",
        "custom_lt_configuration_json",
    )


def main() -> int:
    parse_noop_args(__doc__)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ProductPageArchitectureContractTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
