#!/usr/bin/env python3
"""Verify the source-only Product Setup publish readiness report contract."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "dev" / "lt_product_setup_publish_readiness_report.py"


class ProductSetupPublishReadinessContractTest(unittest.TestCase):
    def test_blocked_replacement_packet_stays_not_publishable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            replacement = Path(tmp) / "replacement.json"
            output = Path(tmp) / "readiness.json"
            replacement.write_text(json.dumps(_replacement_report()), encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--replacement",
                    str(replacement),
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
            self.assertEqual(report["schema_version"], "lt-product-setup-publish-readiness-v1")
            self.assertEqual(report["owner_status"]["state"], "Blocked - Proof Needed")
            self.assertFalse(report["owner_status"]["public_success_claim_allowed"])
            self.assertFalse(report["publish_apply_approval"]["live_apply_approved"])
            self.assertEqual(report["source_report_summary"]["candidate_sku_variant_count"], 3)
            self.assertIn("brand_and_public_route", report["blocker_groups"])
            self.assertIn("options_addons_payload", report["blocker_groups"])
            self.assertIn("approval_and_release", report["blocker_groups"])
            publish = [row for row in report["owner_allowed_actions"] if row["action"] == "Publish/apply to live"][0]
            self.assertFalse(publish["allowed"])

    def test_readiness_report_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            replacement = Path(tmp) / "replacement.json"
            output_a = Path(tmp) / "a.json"
            output_b = Path(tmp) / "b.json"
            replacement.write_text(json.dumps(_replacement_report()), encoding="utf-8")

            for output in (output_a, output_b):
                completed = subprocess.run(
                    [
                        sys.executable,
                        str(SCRIPT),
                        "--replacement",
                        str(replacement),
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

    def test_saved_birthday_deliveries_replacement_when_available(self) -> None:
        replacement = Path("/tmp/lt-birthday-deliveries-replacement-model-report.json")
        if not replacement.exists():
            self.skipTest("saved Birthday Deliveries replacement report is not present")
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "readiness.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--replacement",
                    str(replacement),
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
            self.assertEqual(report["owner_status"]["state"], "Blocked - Proof Needed")
            self.assertEqual(report["blocker_count"], 27)
            self.assertFalse(report["publish_apply_approval"]["mutation_approved"])
            self.assertIn("history_and_rollback", report["blocker_groups"])


def _replacement_report() -> dict:
    return {
        "schema_version": "lt-product-setup-replacement-model-v1",
        "product": {
            "product_setup": "birthday-deliveries",
            "item_code": "birthday-deliveries",
            "route_slug": "birthday-deliveries",
            "route": "/shop-items/bouquets/birthday-deliveries",
        },
        "blocker_count": 5,
        "replacement_model": {"candidate_sku_variant_count": 3},
        "blockers": [
            {"code": "rollback_live_public_route_proof_missing", "message": "Public route proof missing."},
            {"code": "paid_add_on_runtime_proof_missing", "message": "Add-on runtime proof missing."},
            {"code": "non_sku_price_axis_requires_add_on_pricing", "message": "Add-on price proof missing."},
            {"code": "owner_scope_approval_missing", "message": "Owner approval missing."},
            {"code": "pre_mutation_release_packet_missing", "message": "Release packet missing."},
        ],
    }


if __name__ == "__main__":
    unittest.main(verbosity=2)
