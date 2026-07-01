#!/usr/bin/env python3
"""Verify the offline Product Setup dependency/rollback report contract."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "dev" / "lt_product_setup_dependency_rollback_report.py"


class ProductSetupDependencyRollbackContractTest(unittest.TestCase):
    def test_report_lists_required_target_categories_and_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            artifact = Path(tmp) / "birthday-deliveries.json"
            output = Path(tmp) / "report.json"
            artifact.write_text(json.dumps(_birthday_like_artifact()), encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--input",
                    str(artifact),
                    "--output",
                    str(output),
                    "--pretty",
                    "--fail-on-blocker",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 1, completed.stderr)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertTrue(report["deterministic"])
            self.assertEqual(report["product_count"], 1)
            self.assertEqual(report["blocked_product_count"], 1)
            self.assertEqual(
                report["target_category_order"],
                [
                    "variants",
                    "item_prices",
                    "website_item",
                    "template_item",
                    "product_setup",
                    "option_rows",
                    "media_gallery_rows",
                ],
            )
            product = report["products"][0]
            categories = product["target_categories"]
            self.assertEqual(categories["variants"]["row_count"], 6)
            self.assertEqual(len(categories["variants"]["rollback_rows"]), 6)
            self.assertTrue(categories["variants"]["all_rows_included"])
            self.assertEqual(categories["item_prices"]["row_count"], 6)
            self.assertEqual(len(categories["item_prices"]["rollback_rows"]), 6)
            self.assertTrue(categories["item_prices"]["all_rows_included"])
            self.assertEqual(categories["website_item"]["row_count"], 1)
            self.assertEqual(categories["template_item"]["template_attribute_count"], 2)
            self.assertEqual(categories["product_setup"]["row_count"], 1)
            self.assertEqual(categories["option_rows"]["row_count"], 2)
            self.assertEqual(len(categories["option_rows"]["rollback_rows"]), 2)
            self.assertEqual(categories["media_gallery_rows"]["gallery_row_count"], 1)
            self.assertEqual(len(categories["media_gallery_rows"]["rollback_rows"]), 3)
            blocker_codes = {row["code"] for row in product["blockers"]}
            self.assertIn("live_public_route_proof_missing", blocker_codes)
            self.assertIn("variants_historical_reference_proof_missing", blocker_codes)
            self.assertIn("item_prices_live_reference_proof_missing", blocker_codes)
            self.assertIn("file_attachment_reference_proof_missing", blocker_codes)
            self.assertFalse(product["approval_state"]["mutation_approved"])
            self.assertFalse(product["approval_state"]["collapse_approved"])

    def test_report_is_deterministic_for_same_input(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            artifact = Path(tmp) / "birthday-deliveries.json"
            output_a = Path(tmp) / "report-a.json"
            output_b = Path(tmp) / "report-b.json"
            artifact.write_text(json.dumps(_birthday_like_artifact()), encoding="utf-8")

            for output in (output_a, output_b):
                completed = subprocess.run(
                    [
                        sys.executable,
                        str(SCRIPT),
                        "--input",
                        str(artifact),
                        "--output",
                        str(output),
                        "--pretty",
                    ],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(completed.returncode, 0, completed.stderr)

            self.assertEqual(output_a.read_text(encoding="utf-8"), output_b.read_text(encoding="utf-8"))

    def test_saved_birthday_deliveries_artifact_when_available(self) -> None:
        artifact = Path("/tmp/lt-catalog-authority-full-20260630/044-birthday-deliveries.json")
        if not artifact.exists():
            self.skipTest("saved Birthday Deliveries artifact is not present")
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "birthday-dependency-rollback.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--input",
                    str(artifact),
                    "--output",
                    str(output),
                    "--pretty",
                    "--fail-on-blocker",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 1, completed.stderr)
            report = json.loads(output.read_text(encoding="utf-8"))
            product = report["products"][0]
            self.assertEqual(product["product_identifier"]["item_code"], "birthday-deliveries")
            self.assertEqual(product["target_categories"]["variants"]["row_count"], 2430)
            self.assertEqual(len(product["target_categories"]["variants"]["rollback_rows"]), 2430)
            self.assertTrue(product["target_categories"]["variants"]["all_rows_included"])
            self.assertEqual(product["target_categories"]["item_prices"]["row_count"], 2430)
            self.assertEqual(len(product["target_categories"]["item_prices"]["rollback_rows"]), 2430)
            self.assertTrue(product["target_categories"]["item_prices"]["all_rows_included"])
            self.assertEqual(product["target_categories"]["option_rows"]["row_count"], 4)
            self.assertEqual(len(product["target_categories"]["option_rows"]["rollback_rows"]), 4)
            self.assertEqual(product["target_categories"]["media_gallery_rows"]["gallery_row_count"], 7)
            blocker_codes = {row["code"] for row in product["blockers"]}
            self.assertIn("live_brand_lane_proof_missing", blocker_codes)
            self.assertIn("same_brand_source_uniqueness_proof_missing", blocker_codes)
            self.assertIn("website_slideshow_row_snapshots_missing", blocker_codes)
            self.assertIn("media_gallery_rows_historical_reference_proof_missing", blocker_codes)


def _birthday_like_artifact() -> dict:
    variants = []
    prices = []
    price_rows = []
    for size, price in (("Small", 90), ("Large", 120)):
        for theme in ("A", "B", "C"):
            item_code = f"birthday-deliveries-{size}-{theme}"
            variants.append({"name": item_code, "item_code": item_code, "variant_of": "birthday-deliveries", "disabled": 0})
            prices.append({"name": f"PRICE-{item_code}", "item_code": item_code, "price_list": "Standard Selling", "price_list_rate": price, "currency": "USD", "selling": 1})
            price_rows.append({"name": f"SETUP-{item_code}", "item_code": item_code, "option_summary": f"Size: {size}; Theme: {theme}", "price": price})
    return {
        "generated_at": "2026-06-30T00:00:00+00:00",
        "scope": "synthetic dependency rollback contract",
        "product_identifier": {
            "item_code": "birthday-deliveries",
            "product_setup": "birthday-deliveries",
            "route": "/shop-items/bouquets/birthday-deliveries",
            "route_slug": "birthday-deliveries",
            "website_item": "WEB-ITM-0047",
            "brand_lane": "locally_twisted",
            "brand_lane_status": "source_declared",
        },
        "match_summary": {
            "blueprint_match_status": "matched",
            "candidate_blueprints": [
                {
                    "name": "birthday-deliveries",
                    "product_slug": "birthday-deliveries",
                    "target_item_code": "birthday-deliveries",
                    "target_website_item": "WEB-ITM-0047",
                    "operating_brand": "locally_twisted",
                    "publish_status": "Local Preview Ready",
                }
            ],
        },
        "counts": {
            "variants": 6,
            "item_prices": 6,
            "blueprint_price_rows": 6,
            "blueprint_option_rows": 2,
            "blueprint_gallery_rows": 1,
            "blueprint_media_rule_rows": 1,
        },
        "blueprint_summary": {
            "name": "birthday-deliveries",
            "product_name": "Birthday Deliveries",
            "product_slug": "birthday-deliveries",
            "target_item_code": "birthday-deliveries",
            "target_website_item": "WEB-ITM-0047",
            "publish_status": "Local Preview Ready",
            "operating_brand": "locally_twisted",
            "base_price": 90,
        },
        "website_item_summary": {
            "name": "WEB-ITM-0047",
            "item_code": "birthday-deliveries",
            "route": "shop-items/bouquets/birthday-deliveries",
            "published": 1,
            "website_image": "/files/birthday-deliveries--extra-12.webp",
            "slideshow": "LT Product Gallery - birthday-deliveries",
        },
        "template_item_summary": {
            "name": "birthday-deliveries",
            "item_code": "birthday-deliveries",
            "has_variants": 1,
            "image": "/files/birthday-deliveries--extra-12.webp",
        },
        "public_summary": {"skipped": True, "reason": "synthetic verifier"},
        "rows": {
            "blueprint": {
                "name": "birthday-deliveries",
                "product_slug": "birthday-deliveries",
                "publish_status": "Local Preview Ready",
                "target_item_code": "birthday-deliveries",
                "target_website_item": "WEB-ITM-0047",
                "operating_brand": "locally_twisted",
                "base_price": 90,
            },
            "website_item": {
                "name": "WEB-ITM-0047",
                "item_code": "birthday-deliveries",
                "route": "shop-items/bouquets/birthday-deliveries",
                "published": 1,
                "website_image": "/files/birthday-deliveries--extra-12.webp",
                "slideshow": "LT Product Gallery - birthday-deliveries",
            },
            "template_item": {
                "name": "birthday-deliveries",
                "item_code": "birthday-deliveries",
                "has_variants": 1,
                "image": "/files/birthday-deliveries--extra-12.webp",
                "attributes": [
                    {"name": "ATTR-SIZE", "attribute": "Size", "idx": 1},
                    {"name": "ATTR-THEME", "attribute": "Theme", "idx": 2},
                ],
            },
            "variants": variants,
            "item_prices": prices,
            "blueprint_price_rows": price_rows,
            "blueprint_option_rows": [
                {
                    "name": "OPT-SIZE",
                    "axis_name": "Size",
                    "selection_behavior": "SKU-defining variant",
                    "payload_target": "selected_options",
                    "pricing_behavior": "Server priced",
                    "values": "Small\nLarge",
                    "required": 1,
                },
                {
                    "name": "OPT-THEME",
                    "axis_name": "Theme",
                    "selection_behavior": "SKU-defining variant",
                    "payload_target": "selected_options",
                    "pricing_behavior": "Server priced",
                    "values": "A\nB\nC",
                    "required": 1,
                },
            ],
            "blueprint_gallery_rows": [
                {"name": "GAL-1", "image": "/files/birthday-deliveries--extra-12.webp", "approved_for_customer": 1}
            ],
            "blueprint_media_rule_rows": [
                {"name": "RULE-1", "variant_item": "birthday-deliveries-Small-A", "image": "/files/birthday-deliveries--extra-12.webp", "approved_for_customer": 0}
            ],
        },
        "failures": [],
    }


if __name__ == "__main__":
    unittest.main(verbosity=2)
