#!/usr/bin/env python3
"""Verify the offline Product Setup variant-axis classification report."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "dev" / "lt_product_setup_variant_axis_classification_report.py"


class ProductSetupVariantAxisClassificationContractTest(unittest.TestCase):
    def test_report_classifies_price_axes_without_variant_explosion(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            artifact = Path(tmp) / "birthday-like.json"
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
            self.assertEqual(report["product_count"], 1)
            self.assertEqual(report["blocked_product_count"], 1)
            product = report["products"][0]
            self.assertEqual(product["current"]["variant_count"], 24)
            self.assertEqual(product["candidate"]["sku_defining_axes"], ["Size"])
            self.assertEqual(product["candidate"]["candidate_sku_variant_count"], 2)
            self.assertIn("Theme", product["candidate"]["configuration_payload_axes"])
            self.assertIn("Add Foil Number", product["candidate"]["paid_add_on_candidate_axes"])
            blocker_codes = {row["code"] for row in product["blockers"]}
            self.assertIn("current_sku_axes_need_reclassification", blocker_codes)

    def test_report_filters_saved_birthday_deliveries_when_available(self) -> None:
        artifact = Path("/tmp/lt-catalog-authority-full-20260630/044-birthday-deliveries.json")
        if not artifact.exists():
            self.skipTest("saved Birthday Deliveries artifact is not present")
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "birthday-report.json"
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
            self.assertEqual(product["product"]["item_code"], "birthday-deliveries")
            self.assertEqual(product["current"]["variant_count"], 2430)
            self.assertEqual(product["candidate"]["candidate_sku_variant_count"], 3)
            self.assertEqual(product["candidate"]["sku_defining_axes"], ["Delivery Size"])
            self.assertIn("Delivery themes", product["candidate"]["configuration_payload_axes"])
            self.assertIn("Add Foil Number", product["candidate"]["paid_add_on_candidate_axes"])
            self.assertIn("Add Bouquet", product["candidate"]["paid_add_on_candidate_axes"])


def _birthday_like_artifact() -> dict:
    price_rows = []
    for size, price in (("Small", 10), ("Large", 15)):
        for theme in ("A", "B", "C"):
            for number in ("0", "1", "2", "3"):
                price_rows.append(
                    {
                        "item_code": f"birthday-{size}-{theme}-{number}",
                        "option_summary": f"Size: {size}; Theme: {theme}; Add Foil Number: {number}",
                        "price": price,
                    }
                )
    return {
        "product_identifier": {
            "item_code": "birthday-like",
            "product_setup": "birthday-like",
            "route_slug": "birthday-like",
        },
        "counts": {
            "variants": 24,
            "item_prices": 24,
            "blueprint_price_rows": 24,
            "blueprint_option_rows": 3,
        },
        "blueprint_summary": {"name": "birthday-like", "target_item_code": "birthday-like"},
        "website_item_summary": {"item_code": "birthday-like"},
        "rows": {
            "blueprint_option_rows": [
                {
                    "axis_name": "Size",
                    "selection_behavior": "SKU-defining variant",
                    "role": "Sale unit option",
                    "values": "Small\nLarge",
                },
                {
                    "axis_name": "Theme",
                    "selection_behavior": "SKU-defining variant",
                    "role": "Sale unit option",
                    "values": "A\nB\nC",
                },
                {
                    "axis_name": "Add Foil Number",
                    "selection_behavior": "SKU-defining variant",
                    "role": "Sale unit option",
                    "values": "0\n1\n2\n3",
                },
            ],
            "blueprint_price_rows": price_rows,
            "item_prices": [{"item_code": row["item_code"], "price_list_rate": row["price"]} for row in price_rows],
            "variants": [{"item_code": row["item_code"]} for row in price_rows],
        },
    }


if __name__ == "__main__":
    unittest.main(verbosity=2)
