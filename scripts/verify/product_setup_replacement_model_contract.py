#!/usr/bin/env python3
"""Verify the no-write Product Setup replacement model report contract."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "dev" / "lt_product_setup_replacement_model_report.py"


class ProductSetupReplacementModelContractTest(unittest.TestCase):
    def test_replacement_model_keeps_current_rows_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            classification = Path(tmp) / "classification.json"
            rollback = Path(tmp) / "rollback.json"
            source = Path(tmp) / "source.json"
            output = Path(tmp) / "replacement.json"
            classification.write_text(json.dumps(_classification_report()), encoding="utf-8")
            rollback.write_text(json.dumps(_rollback_report()), encoding="utf-8")
            source.write_text(json.dumps(_source_artifact()), encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--classification",
                    str(classification),
                    "--rollback",
                    str(rollback),
                    "--source-artifact",
                    str(source),
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
            self.assertEqual(report["schema_version"], "lt-product-setup-replacement-model-v1")
            model = report["replacement_model"]
            self.assertFalse(model["mutation_approval"])
            self.assertFalse(model["collapse_approval"])
            self.assertEqual(model["candidate_sku_variant_count"], 3)
            self.assertEqual([row["sku_value"] for row in model["candidate_sku_variants"]], ["Small", "Medium", "Large"])
            self.assertEqual(model["candidate_sku_variants"][0]["price_strategy"]["candidate_base_price"], "90")
            self.assertEqual([axis["axis_name"] for axis in model["configuration_payload_axes"]], ["Delivery themes"])
            self.assertEqual([axis["axis_name"] for axis in model["paid_add_on_candidate_axes"]], ["Add Foil Number", "Add Bouquet"])
            self.assertEqual(model["current_records_to_preserve"]["rollback_rows"]["variants"], 9)
            blocker_codes = {row["code"] for row in report["blockers"]}
            self.assertIn("paid_add_on_runtime_proof_missing", blocker_codes)
            self.assertIn("non_sku_price_axis_requires_add_on_pricing", blocker_codes)
            self.assertIn("owner_scope_approval_missing", blocker_codes)
            self.assertIn("pre_mutation_release_packet_missing", blocker_codes)

    def test_report_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            classification = Path(tmp) / "classification.json"
            rollback = Path(tmp) / "rollback.json"
            source = Path(tmp) / "source.json"
            output_a = Path(tmp) / "a.json"
            output_b = Path(tmp) / "b.json"
            classification.write_text(json.dumps(_classification_report()), encoding="utf-8")
            rollback.write_text(json.dumps(_rollback_report()), encoding="utf-8")
            source.write_text(json.dumps(_source_artifact()), encoding="utf-8")

            for output in (output_a, output_b):
                completed = subprocess.run(
                    [
                        sys.executable,
                        str(SCRIPT),
                        "--classification",
                        str(classification),
                        "--rollback",
                        str(rollback),
                        "--source-artifact",
                        str(source),
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

    def test_saved_birthday_deliveries_reports_when_available(self) -> None:
        classification = Path("/tmp/lt-birthday-deliveries-variant-axis-classification.json")
        rollback = Path("/tmp/lt-birthday-deliveries-dependency-rollback-report.json")
        source = Path("/tmp/lt-catalog-authority-full-20260630/044-birthday-deliveries.json")
        if not (classification.exists() and rollback.exists() and source.exists()):
            self.skipTest("saved Birthday Deliveries Phase 9/10 artifacts are not present")
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "replacement.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--classification",
                    str(classification),
                    "--rollback",
                    str(rollback),
                    "--source-artifact",
                    str(source),
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
            self.assertEqual(report["product"]["item_code"], "birthday-deliveries")
            model = report["replacement_model"]
            self.assertEqual(model["candidate_sku_variant_count"], 3)
            self.assertEqual([row["sku_value"] for row in model["candidate_sku_variants"]], ["Small", "Medium", "Large"])
            self.assertEqual([axis["axis_name"] for axis in model["configuration_payload_axes"]], ["Delivery themes"])
            self.assertEqual([axis["axis_name"] for axis in model["paid_add_on_candidate_axes"]], ["Add Foil Number", "Add Bouquet"])
            self.assertEqual(model["current_records_to_preserve"]["rollback_rows"]["variants"], 2430)
            self.assertEqual(model["current_records_to_preserve"]["rollback_rows"]["item_prices"], 2430)
            blocker_codes = {row["code"] for row in report["blockers"]}
            self.assertIn("rollback_live_public_route_proof_missing", blocker_codes)
            self.assertIn("paid_add_on_runtime_proof_missing", blocker_codes)
            self.assertIn("pre_mutation_release_packet_missing", blocker_codes)


def _classification_report() -> dict:
    axes = [
        _axis("Delivery Size", "sku_defining_variant_candidate", ["Small", "Medium", "Large"], True),
        _axis("Delivery themes", "configuration_only_candidate", ["A", "B", "C"], False),
        _axis("Add Foil Number", "paid_add_on_candidate", ["No", "1", "2"], False),
        _axis("Add Bouquet", "paid_add_on_candidate", ["No", "Standard", "Large"], True),
    ]
    return {
        "schema_version": "lt-product-setup-variant-axis-classification-v1",
        "products": [
            {
                "product": _product(),
                "axes": axes,
                "current": {"variant_count": 9, "item_price_count": 9, "option_axis_count": 4},
                "blockers": [
                    {"code": "current_sku_axes_need_reclassification", "message": "Current SKU axes need review."}
                ],
            }
        ],
    }


def _axis(name: str, classification: str, values: list[str], price_affecting: bool) -> dict:
    return {
        "axis_name": name,
        "candidate_classification": classification,
        "current_selection_behavior": "SKU-defining variant",
        "target_payload_target": "selected_options",
        "value_count": len(values),
        "sample_values": values,
        "price_affecting": price_affecting,
        "mutation_approval": False,
    }


def _rollback_report() -> dict:
    return {
        "schema_version": "lt-product-setup-dependency-rollback-v1",
        "products": [
            {
                "product_identifier": _product(),
                "status": "blocked",
                "target_categories": {
                    "variants": {"rollback_rows": [{"item_code": f"variant-{index}"} for index in range(9)]},
                    "item_prices": {"rollback_rows": [{"item_code": f"variant-{index}"} for index in range(9)]},
                    "option_rows": {"rollback_rows": [{"axis_name": "Delivery Size"}]},
                    "media_gallery_rows": {"rollback_rows": [{"image": "/files/a.webp"}]},
                },
                "blockers": [
                    {"code": "live_public_route_proof_missing", "message": "Public route proof missing."}
                ],
            }
        ],
    }


def _source_artifact() -> dict:
    rows = []
    for size, base in (("Small", 90), ("Medium", 120), ("Large", 150)):
        for bouquet, delta in (("No", 0), ("Standard", 30), ("Large", 60)):
            rows.append(
                {
                    "item_code": f"birthday-deliveries-{size}-{bouquet}",
                    "option_summary": f"Delivery Size: {size}; Delivery themes: A; Add Foil Number: No; Add Bouquet: {bouquet}",
                    "price": base + delta,
                }
            )
    return {"rows": {"blueprint_price_rows": rows}, "blueprint_summary": {"name": "birthday-deliveries"}}


def _product() -> dict:
    return {
        "product_setup": "birthday-deliveries",
        "item_code": "birthday-deliveries",
        "website_item": "WEB-ITM-0047",
        "product_name": "Birthday Deliveries",
        "route": "/shop-items/bouquets/birthday-deliveries",
        "route_slug": "birthday-deliveries",
        "brand_lane": None,
        "brand_lane_status": "not_proved",
    }


if __name__ == "__main__":
    unittest.main(verbosity=2)
