#!/usr/bin/env python3
"""Pure contract checks for product source-repair mapping.

Run:
  python scripts/verify/product_source_repair_map_contract.py
"""
from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path
from typing import Any

from _cli import parse_noop_args


ROOT = Path(__file__).resolve().parents[2]
APP_PATH = ROOT / "apps" / "locally_twisted"
MODULE_PATH = APP_PATH / "locally_twisted" / "catalog_contract" / "product_source_repair_map.py"
sys.path.insert(0, str(APP_PATH))


class ProductSourceRepairMapContract(unittest.TestCase):
    def test_legacy_quote_first_field_becomes_blocked_purchasable_repair_state(self) -> None:
        module = _module()
        report = module.build_product_source_repair_map(
            source_products=[
                _source_product("ready-product", variant_count=3),
                _source_product("held-product", variant_count=2),
            ],
            price_enrichment_artifact=_price_artifact(
                [
                    _price_product("ready-product", commerce_lane="checkout", expected_units=3),
                    _price_product("held-product", commerce_lane="quote_first", expected_units=2),
                ]
            ),
            scaffold_artifact=_scaffold_artifact(
                [
                    _scaffold_product("ready-product", stage="direct_checkout_regression_guard"),
                    _scaffold_product("held-product", stage="simple_axis_lane_flip_candidate"),
                ]
            ),
            expected_source_products=2,
            expected_direct_checkout_products=1,
        )

        self.assertEqual(report.contract_failures, ())
        rows = {row.slug: row for row in report.rows}
        self.assertEqual(rows["ready-product"].current_customer_state, "certified_checkout")
        self.assertEqual(rows["held-product"].business_target, "purchasable_product")
        self.assertEqual(rows["held-product"].current_customer_state, "blocked_until_certified")
        self.assertEqual(rows["held-product"].repair_lane, "simple_purchasable_rehearsal")
        serialized = report.to_artifact()
        business_text = " ".join(
            str(value)
            for row in serialized["products"]
            for key, value in row.items()
            if key in {"business_target", "current_customer_state", "repair_lane"}
        )
        self.assertNotIn("quote", business_text.lower())

    def test_missing_odoo_source_row_fails_loudly(self) -> None:
        module = _module()
        report = module.build_product_source_repair_map(
            source_products=[_source_product("source-backed")],
            price_enrichment_artifact=_price_artifact([_price_product("source-backed")]),
            scaffold_artifact=_scaffold_artifact(
                [
                    _scaffold_product("source-backed", stage="direct_checkout_regression_guard"),
                    _scaffold_product("missing-source", stage="needs_review_or_missing"),
                ]
            ),
            expected_source_products=2,
            expected_direct_checkout_products=1,
        )

        self.assertFalse(report.summary()["ok"])
        self.assertIn("missing Odoo source rows: ['missing-source']", report.contract_failures)


def _module():
    if not MODULE_PATH.exists():
        raise AssertionError(f"missing product source-repair module: {MODULE_PATH.relative_to(ROOT)}")
    return importlib.import_module("locally_twisted.catalog_contract.product_source_repair_map")


def _source_product(slug: str, *, variant_count: int = 1) -> dict[str, Any]:
    return {
        "slug": slug,
        "odoo_id": 100,
        "url": f"http://odoo.example/shop/{slug}",
        "name": slug.replace("-", " ").title(),
        "base_price": 25.0,
        "image_url": f"http://odoo.example/web/image/{slug}",
        "additional_image_urls": [],
        "attributes": {"Size": {"values": [{"name": "Small"}]}},
        "variant_count": variant_count,
        "variants": [{"combo": {"Size": "Small"}, "price": 25.0}],
    }


def _price_artifact(products: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "lt-product-page-price-enrichment-v1",
        "products": products,
        "summary": {"source_products": len(products)},
    }


def _price_product(
    slug: str,
    *,
    commerce_lane: str = "checkout",
    expected_units: int = 1,
) -> dict[str, Any]:
    return {
        "slug": slug,
        "name": slug.replace("-", " ").title(),
        "commerce_lane": commerce_lane,
        "expected_units": expected_units,
        "candidate_units": expected_units,
        "price_status": "PASS_PRICE_ENRICHMENT",
        "source_base_units": expected_units,
        "live_snapshot_units": 0,
        "source_resolver_units": 0,
        "blockers": [],
        "sale_units": [{"sale_unit_key": "single SKU", "chosen_price": "25.00"}],
    }


def _scaffold_artifact(products: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "lt-complex-checkout-scaffold-v1",
        "products": products,
        "summary": {"source_products": len(products)},
    }


def _scaffold_product(slug: str, *, stage: str) -> dict[str, Any]:
    return {
        "slug": slug,
        "source_name": slug.replace("-", " ").title(),
        "current_website_lane": "checkout" if stage == "direct_checkout_regression_guard" else "quote_first",
        "scaffold_stage": stage,
        "required_ui_components": ["product_page_checkout_contract"],
        "required_server_contracts": ["Sales Order/Sales Invoice line summary and JSON fields"],
        "gate_verifiers": ["python scripts/verify/checkout_product_family_contract.py"],
        "preconditions_before_checkout": ["focused local proof required"],
    }


def main() -> int:
    parse_noop_args(__doc__)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ProductSourceRepairMapContract)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
