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
from locally_twisted.product_blueprint_runtime_authority import runtime_authority_save_blockers  # noqa: E402
from locally_twisted.product_setup_runtime import (  # noqa: E402
    OPERATING_BRAND_OPTIONS,
    active_product_setup_name_for_website_item,
    build_product_setup_schema,
    resolve_product_setup_configuration,
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
        self.assertEqual(result["contract"]["operating_brand"], "locally_twisted")
        self.assertEqual(result["contract"]["operating_brand_authority_state"], "source_declared")
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
        self.assertEqual(result["planned_records"]["base_item"]["operating_brand"], "locally_twisted")
        self.assertEqual(result["planned_records"]["website_item"]["operating_brand"], "locally_twisted")
        self.assertEqual(result["planned_records"]["website_item"]["operating_brand_authority_state"], "source_declared")
        self.assertEqual(len(result["planned_records"]["item_variants"]), 2)
        self.assertEqual(len(result["planned_records"]["item_prices"]), 2)
        self.assertEqual(result["next_required_gate"], "guarded_local_apply")

    def test_operating_brand_is_required_source_authority_not_live_proof(self) -> None:
        missing = validate_blueprint(_blueprint(operating_brand=""))
        self.assertFalse(missing["ok"])
        self.assertTrue(any("Operating Brand is required" in row for row in missing["blockers"]))
        self.assertEqual(missing["contract"]["operating_brand_authority_state"], "missing")

        unknown = validate_blueprint(_blueprint(operating_brand="unknown_brand"))
        self.assertFalse(unknown["ok"])
        self.assertTrue(any("Operating Brand must be one of" in row for row in unknown["blockers"]))
        self.assertEqual(unknown["contract"]["operating_brand_authority_state"], "invalid")

        valid = validate_blueprint(_blueprint(operating_brand="commercial_balloon_decor"))
        self.assertTrue(valid["ok"], valid)
        self.assertEqual(valid["contract"]["operating_brand"], "commercial_balloon_decor")
        self.assertEqual(valid["contract"]["operating_brand_authority_state"], "source_declared")
        self.assertFalse(valid["ready_for_live"])

        schema = build_product_setup_schema(_blueprint(operating_brand="memorial_balloons"))
        self.assertEqual(schema["product"]["operating_brand"], "memorial_balloons")
        self.assertEqual(schema["product"]["operating_brand_authority_state"], "source_declared")

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
                page_template="Configurable product page",
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

    def test_legacy_custom_quote_page_label_still_maps_to_safe_internal_hold(self) -> None:
        result = validate_blueprint(
            _blueprint(
                page_template="Custom quote page",
                buying_path="Quote first",
                option_rows=[{"axis_name": "Design", "role": "Review only", "values": "Swirl"}],
            )
        )

        self.assertTrue(result["ok"], result)
        self.assertEqual(result["contract"]["product_page_type"], "complex_custom_product")
        self.assertEqual(result["contract"]["commerce_lane"], "quote_first")

    def test_preview_status_with_blockers_fails_loudly(self) -> None:
        result = validate_blueprint(_blueprint(product_slug="Bad Slug", publish_status="Local Preview Ready"))

        self.assertFalse(result["ok"])
        self.assertIn("Product setup cannot move to preview/staging while validation blockers remain.", result["save_blockers"])

    def test_live_approval_is_not_available_from_blueprint(self) -> None:
        result = validate_blueprint(_blueprint(publish_status="Approved For Live"))

        self.assertIn("Live approval is not available from local product blueprints.", result["save_blockers"])
        self.assertFalse(result["ready_for_live"])
        self.assertEqual(result["owner_publish_readiness"]["state"], "Blocked - Proof Needed")
        self.assertFalse(result["owner_publish_readiness"]["public_success_claim_allowed"])
        self.assertFalse(result["publish_apply_approval"]["live_apply_approved"])
        self.assertFalse(result["publish_apply_approval"]["mutation_approved"])

    def test_owner_publish_readiness_states_do_not_claim_live_success(self) -> None:
        draft = validate_blueprint(_blueprint(publish_status="Draft"))
        self.assertEqual(draft["owner_publish_readiness"]["state"], "Draft")
        self.assertFalse(draft["owner_publish_readiness"]["publish_apply_allowed"])

        review = validate_blueprint(_blueprint(publish_status="Needs Price Review"))
        self.assertEqual(review["owner_publish_readiness"]["state"], "Needs Review")
        self.assertFalse(review["owner_publish_readiness"]["public_success_claim_allowed"])

        local = validate_blueprint(_blueprint(publish_status="Local Preview Ready"))
        self.assertEqual(local["owner_publish_readiness"]["state"], "Local Proof Ready")
        self.assertFalse(local["publish_apply_approval"]["cache_clear_approved"])

        blocked = validate_blueprint(_blueprint(product_slug="Bad Slug", publish_status="Local Preview Ready"))
        self.assertEqual(blocked["owner_publish_readiness"]["state"], "Blocked - Proof Needed")
        self.assertFalse(blocked["owner_publish_readiness"]["publish_apply_allowed"])

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
        self.assertEqual(fields["operating_brand"]["fieldtype"], "Select")
        self.assertTrue(fields["operating_brand"].get("reqd"))
        self.assertEqual(fields["operating_brand"].get("default"), "locally_twisted")
        self.assertEqual(set(fields["operating_brand"].get("options", "").splitlines()), OPERATING_BRAND_OPTIONS)
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

    def test_active_product_setup_uniqueness_fails_closed_in_source(self) -> None:
        controller = _read_doctype_file("lt_product_blueprint", "lt_product_blueprint.py")
        runtime = (ROOT / "apps" / "locally_twisted" / "locally_twisted" / "product_setup_runtime.py").read_text(
            encoding="utf-8"
        )

        self.assertIn("ACTIVE_SETUP_STATUSES", controller)
        self.assertIn("_active_uniqueness_save_blockers", controller)
        self.assertIn("operating_brand", controller)
        self.assertIn("product_slug", controller)
        self.assertIn("target_item_code", controller)
        self.assertIn("target_website_item", controller)
        self.assertIn("or_filters", controller)
        self.assertIn("Only one active Product Setup may target the same slug, Item, or Website Item per operating brand.", controller)
        self.assertIn("limit_page_length=2", runtime)
        self.assertIn("Ambiguous active Product Setup authority", runtime)
        commerce_seed = (
            ROOT / "apps" / "locally_twisted" / "locally_twisted" / "seed" / "sync_commerce_rules.py"
        ).read_text(encoding="utf-8")
        patches = (ROOT / "apps" / "locally_twisted" / "locally_twisted" / "patches.txt").read_text(encoding="utf-8")
        self.assertIn('"fieldname": "operating_brand"', commerce_seed)
        self.assertIn('"fieldname": "operating_brand_authority_state"', commerce_seed)
        self.assertIn("sync_product_setup_brand_runtime_fields_20260630", patches)

    def test_runtime_product_setup_lookup_is_brand_scoped_and_fail_closed(self) -> None:
        rows = [
            {
                "name": "setup-local",
                "target_item_code": "same-slug",
                "target_website_item": "WEB-LOCAL",
                "product_slug": "same-slug",
                "operating_brand": "locally_twisted",
                "publish_status": "Local Preview Ready",
                "modified": 3,
            },
            {
                "name": "setup-commercial",
                "target_item_code": "same-slug",
                "target_website_item": "WEB-CBD",
                "product_slug": "same-slug",
                "operating_brand": "commercial_balloon_decor",
                "publish_status": "Local Preview Ready",
                "modified": 4,
            },
        ]
        fake = _FakeFrappe(
            rows,
            website_item={
                "name": "WEB-LOCAL",
                "operating_brand": "locally_twisted",
                "operating_brand_authority_state": "source_declared",
            },
        )

        with _patched_frappe(fake):
            self.assertEqual(
                active_product_setup_name_for_website_item("same-slug", operating_brand="commercial_balloon_decor"),
                "setup-commercial",
            )
            self.assertEqual(active_product_setup_name_for_website_item("same-slug"), "setup-local")

        missing_brand_fake = _FakeFrappe(rows, website_item={"name": "WEB-LOCAL"})
        with _patched_frappe(missing_brand_fake):
            self.assertEqual(active_product_setup_name_for_website_item("same-slug"), "")
        self.assertTrue(any("Missing Product Setup operating_brand" in row for row in missing_brand_fake.errors))

        duplicate_same_brand = _FakeFrappe(
            rows
            + [
                {
                    "name": "setup-local-newer",
                    "target_item_code": "same-slug",
                    "target_website_item": "WEB-LOCAL-2",
                    "product_slug": "same-slug",
                    "operating_brand": "locally_twisted",
                    "publish_status": "Staging Ready",
                    "modified": 5,
                }
            ],
            website_item={
                "name": "WEB-LOCAL",
                "operating_brand": "locally_twisted",
                "operating_brand_authority_state": "source_declared",
            },
        )
        with _patched_frappe(duplicate_same_brand):
            self.assertEqual(active_product_setup_name_for_website_item("same-slug"), "")
        self.assertTrue(any("Ambiguous active Product Setup authority" in row for row in duplicate_same_brand.errors))

        target_item_conflict = _FakeFrappe(
            [
                {
                    "name": "target-conflict-old",
                    "target_item_code": "target-conflict",
                    "target_website_item": "WEB-OLD",
                    "product_slug": "old-slug",
                    "operating_brand": "locally_twisted",
                    "publish_status": "Local Preview Ready",
                    "modified": 1,
                },
                {
                    "name": "target-conflict-new",
                    "target_item_code": "target-conflict",
                    "target_website_item": "WEB-NEW",
                    "product_slug": "target-conflict",
                    "operating_brand": "locally_twisted",
                    "publish_status": "Local Preview Ready",
                    "modified": 2,
                },
            ],
            website_item={
                "name": "WEB-NEW",
                "operating_brand": "locally_twisted",
                "operating_brand_authority_state": "source_declared",
            },
        )
        with _patched_frappe(target_item_conflict):
            self.assertEqual(active_product_setup_name_for_website_item("target-conflict"), "")
        self.assertTrue(any("target_item_code=target-conflict" in row for row in target_item_conflict.errors))

    def test_runtime_authority_blockers_are_owner_visible_before_active_status(self) -> None:
        active_doc = _doc(
            publish_status="Local Preview Ready",
            operating_brand="locally_twisted",
            product_slug="same-slug",
            target_item_code="same-slug",
            target_website_item="WEB-LOCAL",
        )
        valid_frappe = _FakeFrappe(
            [],
            website_item={
                "name": "WEB-LOCAL",
                "item_code": "same-slug",
                "operating_brand": "locally_twisted",
                "operating_brand_authority_state": "source_declared",
            },
        )
        self.assertEqual(runtime_authority_save_blockers(active_doc, valid_frappe), [])

        draft_data = dict(active_doc.__dict__)
        draft_data["publish_status"] = "Draft"
        draft_doc = _doc(**draft_data)
        missing_fields = _FakeFrappe(
            [],
            website_item={
                "name": "WEB-LOCAL",
                "item_code": "same-slug",
            },
        )
        self.assertEqual(runtime_authority_save_blockers(draft_doc, missing_fields), [])
        draft_blockers = runtime_authority_save_blockers(active_doc, missing_fields)
        self.assertTrue(any("runtime fields are not installed" in row for row in draft_blockers))

        mismatched_brand = _FakeFrappe(
            [],
            website_item={
                "name": "WEB-LOCAL",
                "item_code": "same-slug",
                "operating_brand": "commercial_balloon_decor",
                "operating_brand_authority_state": "source_declared",
            },
        )
        brand_blockers = runtime_authority_save_blockers(active_doc, mismatched_brand)
        self.assertTrue(any("Operating Brand must be source-declared as locally_twisted" in row for row in brand_blockers))

        missing_authority_state = _FakeFrappe(
            [],
            website_item={
                "name": "WEB-LOCAL",
                "item_code": "same-slug",
                "operating_brand": "locally_twisted",
                "operating_brand_authority_state": "missing",
            },
        )
        state_blockers = runtime_authority_save_blockers(active_doc, missing_authority_state)
        self.assertTrue(any("source-declared as locally_twisted" in row for row in state_blockers))

        no_existing_website_item = _FakeFrappe([], website_item=None)
        self.assertEqual(runtime_authority_save_blockers(active_doc, no_existing_website_item), [])

        mismatched_target = _FakeFrappe(
            [],
            website_item={
                "name": "WEB-LOCAL",
                "item_code": "other-item",
                "operating_brand": "locally_twisted",
                "operating_brand_authority_state": "source_declared",
            },
        )
        target_blockers = runtime_authority_save_blockers(active_doc, mismatched_target)
        self.assertTrue(any("targets same-slug" in row for row in target_blockers))

        meta_failure = _FakeFrappeMetaFailure([])
        meta_blockers = runtime_authority_save_blockers(active_doc, meta_failure)
        self.assertTrue(any("runtime fields are not installed" in row for row in meta_blockers))
        self.assertTrue(any("Metadata lookup failed" in row for row in meta_blockers))

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

    def test_generic_selection_groups_do_not_infer_product_specific_defaults(self) -> None:
        values = "\n".join(f"Choice {idx:02d}" for idx in range(1, 61))
        schema = build_product_setup_schema(
            _blueprint(
                page_template="Ready-to-order page",
                buying_path="Direct checkout",
                base_price=35,
                option_rows=[
                    {
                        "axis_name": "Size",
                        "selection_behavior": "SKU-defining variant",
                        "control_type": "Single select",
                        "required": 1,
                        "values": "Small\nLarge",
                    },
                    {
                        "axis_name": "Design Choices",
                        "selection_behavior": "Configuration only",
                        "control_type": "Multi select",
                        "required": 0,
                        "min_selections": 0,
                        "max_selections": 9,
                        "values": values,
                    },
                ],
            )
        )

        groups = {row["key"]: row for row in schema["selection_groups"]}
        self.assertTrue(groups["size"]["sku_defining"])
        self.assertEqual(groups["size"]["payload_target"], "selected_options")
        self.assertFalse(groups["design-choices"]["sku_defining"])
        self.assertEqual(groups["design-choices"]["payload_target"], "configuration_groups")
        self.assertEqual(groups["design-choices"]["max_selections"], 9)
        self.assertEqual(len(groups["design-choices"]["values"]), 60)
        self.assertEqual(groups["design-choices"]["default_values"], [])
        self.assertEqual(schema["generation"]["variant_combination_count"], 2)

    def test_generic_resolver_enforces_min_max_and_allowed_values(self) -> None:
        schema = build_product_setup_schema(
            _blueprint(
                page_template="Ready-to-order page",
                buying_path="Direct checkout",
                base_price=35,
                option_rows=[
                    {
                        "axis_name": "Size",
                        "selection_behavior": "SKU-defining variant",
                        "required": 1,
                        "values": "Small\nLarge",
                    },
                    {
                        "axis_name": "Design Choices",
                        "selection_behavior": "Configuration only",
                        "control_type": "Multi select",
                        "required": 1,
                        "min_selections": 1,
                        "max_selections": 2,
                        "values": "One\nTwo\nThree",
                    },
                ],
            )
        )

        too_many = resolve_product_setup_configuration(
            schema,
            {"selections": {"size": "Small", "design-choices": ["One", "Two", "Three"]}},
        )
        self.assertFalse(too_many["ok"])
        self.assertTrue(any("at most 2" in row for row in too_many["blockers"]))

        unknown = resolve_product_setup_configuration(
            schema,
            {"selections": {"size": "Small", "design-choices": ["Four"]}},
        )
        self.assertFalse(unknown["ok"])
        self.assertTrue(any("is not an allowed choice" in row for row in unknown["blockers"]))

    def test_checkout_resolver_trusts_priced_variant_labels_with_commas(self) -> None:
        small = "Small - 1 featured foil balloon, 2 coordinating foil balloons, 7 latex balloons"
        medium = "Medium - 2 featured foil balloons, 4 coordinating foil balloons, 14 latex balloons"
        schema = build_product_setup_schema(
            _blueprint(
                page_template="Ready-to-order page",
                buying_path="Direct checkout",
                base_price=35,
                option_rows=[
                    {
                        "axis_name": "Bouquet Size",
                        "selection_behavior": "SKU-defining variant",
                        "required": 1,
                        "values": f"{small}\n{medium}",
                    }
                ],
            )
        )

        resolved = resolve_product_setup_configuration(
            schema,
            {"selected_options": {"Bouquet Size": small}},
            trusted_variant_attributes={"Bouquet Size": small},
        )
        self.assertTrue(resolved["ok"], resolved)
        self.assertEqual(resolved["resolved_variant_attributes"], {"Bouquet Size": small})

        mismatch = resolve_product_setup_configuration(
            schema,
            {"selected_options": {"Bouquet Size": medium}},
            trusted_variant_attributes={"Bouquet Size": small},
        )
        self.assertFalse(mismatch["ok"])
        self.assertTrue(any("does not match the priced item" in row for row in mismatch["blockers"]))

    def test_generic_resolver_preserves_checkout_payload_without_variant_explosion(self) -> None:
        schema = build_product_setup_schema(
            _blueprint(
                page_template="Ready-to-order page",
                buying_path="Direct checkout",
                base_price=35,
                option_rows=[
                    {
                        "axis_name": "Size",
                        "selection_behavior": "SKU-defining variant",
                        "required": 1,
                        "values": "Small\nLarge",
                    },
                    {
                        "axis_name": "Design Choices",
                        "selection_behavior": "Configuration only",
                        "control_type": "Multi select",
                        "required": 1,
                        "min_selections": 1,
                        "max_selections": 9,
                        "values": "\n".join(f"Choice {idx:02d}" for idx in range(1, 61)),
                    },
                ],
            )
        )

        resolved = resolve_product_setup_configuration(
            schema,
            {"selections": {"size": "Large", "design-choices": ["Choice 01", "Choice 42"]}},
        )

        self.assertTrue(resolved["ok"], resolved)
        self.assertEqual(resolved["commerce_outcome"], "checkout")
        self.assertEqual(resolved["resolved_variant_attributes"], {"Size": "Large"})
        self.assertEqual(
            resolved["configuration_payload"]["configuration_groups"],
            [
                {
                    "key": "design-choices",
                    "label": "Design Choices",
                    "values": ["Choice 01", "Choice 42"],
                    "document_output": "Customer and operator",
                }
            ],
        )

    def test_apply_plan_uses_only_sku_defining_groups_for_variants(self) -> None:
        result = build_apply_plan(
            _blueprint(
                page_template="Ready-to-order page",
                buying_path="Direct checkout",
                base_price=35,
                option_rows=[
                    {
                        "axis_name": "Size",
                        "selection_behavior": "SKU-defining variant",
                        "required": 1,
                        "values": "Small\nLarge",
                    },
                    {
                        "axis_name": "Design Choices",
                        "selection_behavior": "Configuration only",
                        "control_type": "Multi select",
                        "max_selections": 9,
                        "values": "\n".join(f"Choice {idx:02d}" for idx in range(1, 61)),
                    },
                ],
            )
        )

        self.assertTrue(result["ok"], result)
        self.assertEqual(len(result["planned_records"]["item_variants"]), 2)
        self.assertEqual(result["planned_records"]["product_setup_schema"]["generation"]["variant_combination_count"], 2)

    def test_product_setup_doctypes_have_generic_system_fields(self) -> None:
        option = _doctype("lt_product_blueprint_option", "lt_product_blueprint_option.json")
        fields = {field["fieldname"]: field for field in option["fields"]}
        for fieldname in (
            "selection_behavior",
            "control_type",
            "min_selections",
            "max_selections",
            "default_values",
            "pricing_behavior",
            "media_behavior",
            "document_output",
        ):
            self.assertIn(fieldname, fields)

        product = _doctype("lt_product_blueprint", "lt_product_blueprint.json")
        product_fields = {field["fieldname"]: field for field in product["fields"]}
        self.assertEqual(product_fields["media_rule_rows"]["options"], "LT Product Blueprint Media Rule")

    def test_owner_add_product_opens_guided_product_setup(self) -> None:
        workspace_seed = (ROOT / "apps" / "locally_twisted" / "locally_twisted" / "seed" / "sync_backend_workspaces.py").read_text(
            encoding="utf-8"
        )
        workspace_contract = (ROOT / "scripts" / "verify" / "backend_workspace_parity.py").read_text(encoding="utf-8")
        self.assertIn('"link_to": "LT Product Blueprint"', workspace_seed)
        self.assertIn('"Add Product": ("LT Product Blueprint", "New")', workspace_contract)


def _blueprint(**overrides):
    data = {
        "product_name": "Proof Product",
        "product_slug": "proof-product",
        "operating_brand": "locally_twisted",
        "item_group": "Bouquets",
        "page_template": "Configurable product page",
        "buying_path": "Quote first",
        "publish_status": "Draft",
        "option_rows": [],
        "color_recipe_rows": [],
        "add_on_rows": [],
        "conditional_price_rows": [],
    }
    data.update(overrides)
    return data


class _Doc:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def _doc(**overrides):
    data = {
        "name": "proof-product",
        "product_slug": "proof-product",
        "operating_brand": "locally_twisted",
        "publish_status": "Draft",
        "target_item_code": "",
        "target_website_item": "",
    }
    data.update(overrides)
    return _Doc(**data)


def _doctype(folder: str, filename: str) -> dict:
    path = DOCTYPE_ROOT / folder / filename
    return json.loads(path.read_text(encoding="utf-8"))


def _read_doctype_file(folder: str, filename: str) -> str:
    return (DOCTYPE_ROOT / folder / filename).read_text(encoding="utf-8")


class _PatchedFrappe:
    def __init__(self, fake):
        self.fake = fake
        self.previous = None

    def __enter__(self):
        self.previous = sys.modules.get("frappe")
        sys.modules["frappe"] = self.fake
        return self.fake

    def __exit__(self, exc_type, exc, tb):
        if self.previous is None:
            sys.modules.pop("frappe", None)
        else:
            sys.modules["frappe"] = self.previous


def _patched_frappe(fake):
    return _PatchedFrappe(fake)


class _FakeMeta:
    def __init__(self, fields: set[str]):
        self.fields = fields

    def has_field(self, fieldname: str) -> bool:
        return fieldname in self.fields


class _FakeDb:
    def __init__(self, parent):
        self.parent = parent

    def exists(self, doctype: str, name: str) -> bool:
        return doctype == "DocType" and name == "LT Product Blueprint"

    def get_value(self, doctype: str, filters: dict, fields, as_dict: bool = False):
        if doctype != "Website Item":
            return None
        if not filters.get("item_code") or not self.parent.website_item:
            return None
        if as_dict:
            return dict(self.parent.website_item)
        if isinstance(fields, list):
            return [self.parent.website_item.get(field) for field in fields]
        return self.parent.website_item.get(fields)


class _FakeFrappe:
    def __init__(self, rows: list[dict], *, website_item: dict | None = None):
        self.rows = rows
        self.website_item = website_item or {}
        self.db = _FakeDb(self)
        self.errors: list[str] = []

    def get_meta(self, doctype: str):
        if doctype != "Website Item":
            return _FakeMeta(set())
        return _FakeMeta(set(self.website_item.keys()))

    def get_all(self, doctype: str, filters: dict, fields: list[str], order_by: str, limit_page_length: int):
        if doctype != "LT Product Blueprint":
            return []
        matches = []
        for row in self.rows:
            if not _row_matches_filters(row, filters):
                continue
            matches.append(row)
        matches.sort(key=lambda row: row.get("modified") or 0, reverse=True)
        return [{field: row.get(field) for field in fields} for row in matches[:limit_page_length]]

    def log_error(self, message: str, title: str | None = None):
        self.errors.append(message)


class _FakeFrappeMetaFailure(_FakeFrappe):
    def get_meta(self, doctype: str):
        raise RuntimeError("meta unavailable")


def _row_matches_filters(row: dict, filters: dict) -> bool:
    for fieldname, expected in filters.items():
        actual = row.get(fieldname)
        if isinstance(expected, list) and len(expected) == 2 and expected[0] == "in":
            if actual not in expected[1]:
                return False
            continue
        if actual != expected:
            return False
    return True


def main() -> int:
    parse_noop_args(__doc__)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ProductBlueprintContractTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
