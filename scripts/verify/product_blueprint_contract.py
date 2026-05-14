#!/usr/bin/env python3
"""Pure contract checks for employee-authored product blueprints.

Run:
  python scripts/verify/product_blueprint_contract.py
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

from _cli import parse_noop_args


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps" / "locally_twisted"))

from locally_twisted.product_blueprint_validation import validate_blueprint  # noqa: E402
from locally_twisted.product_blueprint_apply_plan import build_apply_plan  # noqa: E402
from locally_twisted.product_blueprint_local_apply import (  # noqa: E402
    LOCAL_APPLY_CONFIRMATION,
    build_local_apply_preview,
    validate_local_apply_request,
)


DOCTYPE_ROOT = ROOT / "apps" / "locally_twisted" / "locally_twisted" / "locally_twisted" / "doctype"


class ProductBlueprintContractTest(unittest.TestCase):
    def test_ready_to_order_checkout_maps_to_runtime_contract(self) -> None:
        result = validate_blueprint(
            _blueprint(
                page_template="Ready-to-order page",
                buying_path="Direct checkout",
                base_price=35,
                option_rows=[{"axis_name": "Size", "role": "Sale unit option", "values": "Small\nLarge"}],
                add_on_rows=[
                    {
                        "add_on_name": "Foil number",
                        "add_on_item": "ADDON-FOIL-NUMBER",
                        "price_source": "Fixed Item Price",
                        "checkout_approved": 1,
                    }
                ],
            )
        )

        self.assertTrue(result["ok"], result)
        self.assertEqual(result["validation_status"], "Ready For Local Preview")
        self.assertEqual(result["contract"]["product_page_type"], "simple_product")
        self.assertEqual(result["contract"]["commerce_lane"], "checkout")
        self.assertEqual(result["contract"]["payload_target_counts"]["selected_options"], 1)
        self.assertEqual(result["contract"]["payload_target_counts"]["add_ons"], 1)
        self.assertFalse(result["contract"]["product_generation_enabled"])
        self.assertFalse(result["contract"]["live_publish_enabled"])

    def test_apply_plan_is_dry_run_and_names_records(self) -> None:
        result = build_apply_plan(
            _blueprint(
                page_template="Ready-to-order page",
                buying_path="Direct checkout",
                base_price=35,
                option_rows=[{"axis_name": "Size", "role": "Sale unit option", "values": "Small\nLarge"}],
            )
        )

        self.assertTrue(result["ok"], result)
        self.assertTrue(result["dry_run"])
        self.assertFalse(result["writes_enabled"])
        self.assertFalse(result["live_publish_enabled"])
        self.assertEqual(result["planned_records"]["base_item"]["item_code"], "proof-product")
        self.assertEqual(result["planned_records"]["website_item"]["published"], 0)
        self.assertEqual(len(result["planned_records"]["item_variants"]), 2)
        self.assertEqual(len(result["planned_records"]["item_prices"]), 2)
        self.assertEqual(result["next_required_gate"], "guarded_local_apply")

    def test_local_apply_preview_names_writes_without_enabling_them(self) -> None:
        result = build_local_apply_preview(
            _blueprint(
                page_template="Ready-to-order page",
                buying_path="Direct checkout",
                base_price=35,
                option_rows=[{"axis_name": "Size", "role": "Sale unit option", "values": "Small\nLarge"}],
            )
        )

        self.assertTrue(result["ok"], result)
        self.assertTrue(result["dry_run"])
        self.assertFalse(result["writes_enabled"])
        self.assertFalse(result["live_publish_enabled"])
        self.assertEqual(result["website_item_published"], 0)
        self.assertEqual(result["planned_counts"]["item_variants"], 2)
        self.assertEqual(result["planned_counts"]["item_prices"], 2)

    def test_local_apply_requires_explicit_write_confirmation(self) -> None:
        plan = build_apply_plan(
            _blueprint(
                page_template="Ready-to-order page",
                buying_path="Direct checkout",
                base_price=35,
            )
        )

        blocked = validate_local_apply_request(plan)
        self.assertFalse(blocked["ok"])
        self.assertTrue(any("allow_writes=True" in row for row in blocked["blockers"]))
        self.assertTrue(any(LOCAL_APPLY_CONFIRMATION in row for row in blocked["blockers"]))

        allowed = validate_local_apply_request(
            plan,
            allow_writes=True,
            confirmation=LOCAL_APPLY_CONFIRMATION,
        )
        self.assertTrue(allowed["ok"], allowed)
        self.assertTrue(allowed["writes_enabled"])
        self.assertFalse(allowed["live_publish_enabled"])
        self.assertEqual(allowed["website_item_published"], 0)

    def test_local_apply_blocks_duplicate_variant_item_codes(self) -> None:
        plan = build_apply_plan(
            _blueprint(
                page_template="Ready-to-order page",
                buying_path="Direct checkout",
                base_price=35,
                option_rows=[
                    {
                        "axis_name": "Style",
                        "role": "Sale unit option",
                        "values": "Same Code\nSame-Code",
                    }
                ],
            )
        )

        result = validate_local_apply_request(
            plan,
            allow_writes=True,
            confirmation=LOCAL_APPLY_CONFIRMATION,
        )
        self.assertFalse(result["ok"])
        self.assertTrue(any("Variant item codes must be unique" in row for row in result["blockers"]))

    def test_apply_plan_blocks_high_variant_direct_checkout(self) -> None:
        result = build_apply_plan(
            _blueprint(
                page_template="Ready-to-order page",
                buying_path="Direct checkout",
                base_price=35,
                option_rows=[
                    {"axis_name": "A", "role": "Sale unit option", "values": "\n".join(str(i) for i in range(8))},
                    {"axis_name": "B", "role": "Sale unit option", "values": "\n".join(str(i) for i in range(8))},
                ],
            )
        )

        self.assertFalse(result["ok"])
        self.assertTrue(any("would create 64 variants" in row for row in result["blockers"]))

    def test_direct_checkout_requires_base_price(self) -> None:
        result = validate_blueprint(
            _blueprint(
                page_template="Ready-to-order page",
                buying_path="Direct checkout",
                option_rows=[{"axis_name": "Size", "role": "Sale unit option", "values": "Small"}],
            )
        )

        self.assertFalse(result["ok"])
        self.assertTrue(any("base checkout price" in row for row in result["blockers"]))

    def test_direct_checkout_rejects_review_only_addons(self) -> None:
        result = validate_blueprint(
            _blueprint(
                page_template="Ready-to-order page",
                buying_path="Direct checkout",
                base_price=35,
                add_on_rows=[{"add_on_name": "Plush add ons", "price_source": "Needs review"}],
            )
        )

        self.assertFalse(result["ok"])
        self.assertTrue(any("direct checkout add-ons require checkout approval" in row for row in result["blockers"]))
        self.assertTrue(any("resolved price source" in row for row in result["blockers"]))

    def test_quote_first_allows_review_only_complexity_without_checkout_success(self) -> None:
        result = validate_blueprint(
            _blueprint(
                page_template="Custom quote page",
                buying_path="Quote first",
                option_rows=[{"axis_name": "Design", "role": "Review only", "values": "Swirl\nLayered"}],
                conditional_price_rows=[
                    {
                        "condition_label": "Large install",
                        "applies_when": "Customer needs large venue install",
                        "price_behavior": "Quote only",
                    }
                ],
            )
        )

        self.assertTrue(result["ok"], result)
        self.assertEqual(result["contract"]["commerce_lane"], "quote_first")
        self.assertEqual(result["contract"]["payload_target_counts"]["quote_context"], 1)

    def test_preview_status_with_blockers_fails_loudly(self) -> None:
        result = validate_blueprint(_blueprint(product_slug="Bad Slug", publish_status="Local Preview Ready"))

        self.assertFalse(result["ok"])
        self.assertIn("Product setup cannot move to preview/staging while validation blockers remain.", result["save_blockers"])

    def test_live_approval_is_not_available_from_blueprint(self) -> None:
        result = validate_blueprint(_blueprint(publish_status="Approved For Live"))

        self.assertIn("Live approval is not available from local product blueprints.", result["save_blockers"])
        self.assertFalse(result["ready_for_live"])

    def test_color_recipe_limits_fail_loudly(self) -> None:
        result = validate_blueprint(
            _blueprint(color_recipe_rows=[{"recipe_name": "Arch palette", "min_colors": 4, "max_colors": 2}])
        )

        self.assertFalse(result["ok"])
        self.assertTrue(any("minimum colors cannot exceed maximum colors" in row for row in result["blockers"]))

    def test_doctype_schema_has_no_live_publish_action(self) -> None:
        product = _doctype("lt_product_blueprint", "lt_product_blueprint.json")
        self.assertEqual(product["actions"], [])
        fields = {field["fieldname"]: field for field in product["fields"]}
        self.assertTrue(fields["ready_for_live"].get("read_only"))
        self.assertTrue(fields["target_item_code"].get("read_only"))
        self.assertTrue(fields["target_website_item"].get("read_only"))
        self.assertTrue(fields["apply_plan_json"].get("read_only"))
        self.assertEqual(fields["option_rows"]["options"], "LT Product Blueprint Option")
        self.assertEqual(fields["color_recipe_rows"]["options"], "LT Product Blueprint Color Recipe")
        self.assertEqual(fields["add_on_rows"]["options"], "LT Product Blueprint Add On")
        self.assertEqual(fields["conditional_price_rows"]["options"], "LT Product Blueprint Conditional Price")
        roles = {row["role"] for row in product["permissions"]}
        self.assertIn("System Manager", roles)
        self.assertIn("Item Manager", roles)

    def test_desk_apply_ui_uses_server_guard_without_leaking_confirmation_token(self) -> None:
        controller = _read_doctype_file("lt_product_blueprint", "lt_product_blueprint.py")
        client = _read_doctype_file("lt_product_blueprint", "lt_product_blueprint.js")

        self.assertIn("@frappe.whitelist()", controller)
        self.assertIn("def apply_locally_from_desk", controller)
        self.assertIn("lt_allow_local_blueprint_apply", controller)
        self.assertIn("Only System Manager or Item Manager", controller)
        self.assertIn("apply_locally_from_desk", client)
        self.assertIn("Preview Local Apply", client)
        self.assertNotIn(LOCAL_APPLY_CONFIRMATION, client)

    def test_child_doctypes_are_child_tables(self) -> None:
        for folder, filename in (
            ("lt_product_blueprint_option", "lt_product_blueprint_option.json"),
            ("lt_product_blueprint_color_recipe", "lt_product_blueprint_color_recipe.json"),
            ("lt_product_blueprint_add_on", "lt_product_blueprint_add_on.json"),
            ("lt_product_blueprint_conditional_price", "lt_product_blueprint_conditional_price.json"),
        ):
            data = _doctype(folder, filename)
            self.assertEqual(data.get("istable"), 1, filename)
            self.assertEqual(data.get("permissions"), [], filename)


def _blueprint(**overrides):
    data = {
        "product_name": "Proof Product",
        "product_slug": "proof-product",
        "item_group": "Bouquets",
        "page_template": "Custom quote page",
        "buying_path": "Quote first",
        "publish_status": "Draft",
        "option_rows": [],
        "color_recipe_rows": [],
        "add_on_rows": [],
        "conditional_price_rows": [],
    }
    data.update(overrides)
    return data


def _doctype(folder: str, filename: str) -> dict:
    path = DOCTYPE_ROOT / folder / filename
    return json.loads(path.read_text(encoding="utf-8"))


def _read_doctype_file(folder: str, filename: str) -> str:
    return (DOCTYPE_ROOT / folder / filename).read_text(encoding="utf-8")


def main() -> int:
    parse_noop_args(__doc__)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ProductBlueprintContractTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
