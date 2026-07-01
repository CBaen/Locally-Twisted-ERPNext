#!/usr/bin/env python3
"""Verify the source-only Product Setup catalog readiness dashboard contract."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "dev" / "lt_product_setup_catalog_readiness_dashboard.py"


class ProductSetupCatalogReadinessContractTest(unittest.TestCase):
    def test_blocked_packet_report_builds_catalog_dashboard(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            packet_report = Path(tmp) / "authority-packet-report.json"
            output = Path(tmp) / "dashboard.json"
            packet_report.write_text(json.dumps(_packet_report()), encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--packet-report",
                    str(packet_report),
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
            self.assertEqual(report["schema_version"], "lt-product-setup-catalog-readiness-dashboard-v1")
            self.assertTrue(report["deterministic"])
            self.assertIn("offline saved authority packet report JSON only", report["proof_mode"])
            self.assertEqual(report["catalog_counts"]["product_count"], 3)
            self.assertEqual(report["catalog_counts"]["blocked_product_count"], 2)
            self.assertEqual(report["catalog_counts"]["ready_product_count"], 1)
            self.assertEqual(report["catalog_counts"]["blocker_count"], 9)
            self.assertEqual(report["catalog_counts"]["products_with_price_mismatch"], 1)
            self.assertEqual(report["catalog_counts"]["products_with_copy_drift"], 1)
            self.assertEqual(report["catalog_counts"]["products_with_variant_explosion"], 1)
            self.assertEqual(report["catalog_counts"]["products_with_public_route_proof"], 1)
            self.assertEqual(report["catalog_counts"]["source_declared_operating_brands"], 3)
            self.assertEqual(report["catalog_counts"]["mutation_approved_products"], 0)
            self.assertIn("authority_identity", report["blocker_group_counts"])
            self.assertIn("price_runtime", report["blocker_group_counts"])
            self.assertIn("copy_content", report["blocker_group_counts"])
            self.assertIn("variant_model", report["blocker_group_counts"])
            self.assertIn("public_release_proof", report["blocker_group_counts"])
            self.assertEqual(report["variant_explosion_summary"]["variant_explosion_count"], 1)
            self.assertEqual(report["variant_explosion_summary"]["products"][0]["item_code"], "birthday-deliveries")
            self.assertFalse(report["publish_apply_approval"]["live_apply_approved"])
            self.assertFalse(report["publish_apply_approval"]["mutation_approved"])
            for action in report["owner_safe_actions"]:
                if action["action"] == "Publish/apply/cache/deploy/live mutation":
                    self.assertFalse(action["allowed"])
            for row in report["product_rows"]:
                approvals = row["release_readiness"]["approvals"]
                self.assertTrue(all(value is False for value in approvals.values()))

    def test_collector_index_without_packets_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            collector_index = Path(tmp) / "index.json"
            output = Path(tmp) / "dashboard.json"
            collector_index.write_text(
                json.dumps({"product_count": 47, "artifacts": ["001-product.json"]}),
                encoding="utf-8",
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--packet-report",
                    str(collector_index),
                    "--output",
                    str(output),
                    "--fail-on-blocker",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 2, completed.stderr)
            self.assertIn("packets list", completed.stderr)
            self.assertFalse(output.exists())

    def test_dashboard_output_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            packet_report = Path(tmp) / "authority-packet-report.json"
            output_a = Path(tmp) / "a.json"
            output_b = Path(tmp) / "b.json"
            packet_report.write_text(json.dumps(_packet_report()), encoding="utf-8")

            for output in (output_a, output_b):
                completed = subprocess.run(
                    [
                        sys.executable,
                        str(SCRIPT),
                        "--packet-report",
                        str(packet_report),
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

    def test_saved_authority_packet_when_available(self) -> None:
        packet_report = Path("/tmp/lt-catalog-authority-full-20260630/authority-packet-report.json")
        if not packet_report.exists():
            self.skipTest("saved full catalog authority packet report is not present")
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "dashboard.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--packet-report",
                    str(packet_report),
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
            self.assertEqual(report["catalog_counts"]["product_count"], 47)
            self.assertEqual(report["catalog_counts"]["blocked_product_count"], 47)
            self.assertEqual(report["catalog_counts"]["blocker_count"], 284)
            self.assertEqual(report["variant_explosion_summary"]["variant_explosion_count"], 6)
            self.assertFalse(report["publish_apply_approval"]["mutation_approved"])


def _packet_report() -> dict:
    packets = [
        _packet(
            item_code="large-head-missionary",
            product_name="Large head Missionary",
            route="/shop-items/bouquets/large-head-missionary",
            blockers=[
                "brand_lane_unproved",
                "active_uniqueness_unproved",
                "price_mismatch",
                "copy_authority_drift",
                "media_role_proof_missing",
                "public_route_proof_missing",
                "pre_mutation_rollback_packet_missing",
            ],
            price_status="mismatch",
            copy_differs=True,
            variants=30,
            item_prices=30,
            public_route_proved=False,
        ),
        _packet(
            item_code="birthday-deliveries",
            product_name="Birthday Deliveries",
            route="/shop-items/bouquets/birthday-deliveries",
            blockers=["variant_explosion", "pre_mutation_rollback_packet_missing"],
            price_status="match",
            variants=2430,
            item_prices=2430,
            severity_bucket="critical",
            public_route_proved=False,
        ),
        _packet(
            item_code="ready-review-product",
            product_name="Ready Review Product",
            route="/shop-items/bouquets/ready-review-product",
            blockers=[],
            price_status="match",
            variants=1,
            item_prices=1,
            public_route_proved=True,
        ),
    ]
    return {
        "artifact_count": len(packets),
        "blocked_product_count": 2,
        "blocker_count": 9,
        "catalog_authority_status": "blocked",
        "generated_at": "2026-06-30T00:00:00+00:00",
        "product_count": len(packets),
        "proof_mode": "offline saved catalog authority JSON artifacts only",
        "packets": packets,
    }


def _packet(
    *,
    item_code: str,
    product_name: str,
    route: str,
    blockers: list[str],
    price_status: str,
    variants: int,
    item_prices: int,
    public_route_proved: bool,
    copy_differs: bool = False,
    severity_bucket: str = "normal",
) -> dict:
    return {
        "artifact": f"/tmp/{item_code}.json",
        "authority_status": "blocked" if blockers else "ready",
        "blockers": [_blocker(code) for code in blockers],
        "copy": {
            "differs": copy_differs,
            "product_setup_fields_present": True,
            "website_item_public_fields_present": True,
            "evidence": {"difference_count": 1 if copy_differs else 0},
        },
        "next_action": "Resolve saved packet blockers before mutation." if blockers else "Prepare reviewed apply packet.",
        "option": {
            "add_on_row_count": 0,
            "conditional_price_row_count": 0,
            "media_rule_row_count": 1 if "media_role_proof_missing" in blockers else 0,
            "missing_classification_count": 0,
            "option_row_count": 2,
        },
        "price": {
            "drift_status": price_status,
            "item_price_values": ["175.00" if price_status == "mismatch" else "125.00"],
            "mismatched_item_price_count": 30 if price_status == "mismatch" else 0,
            "missing_runtime_item_price_count": 0,
            "row_counts": {
                "item_price_rows": item_prices,
                "product_setup_price_rows": item_prices,
            },
            "setup_base_price": "125.00",
            "setup_values": ["125.00"],
        },
        "product_identifier": {
            "brand_lane": "locally_twisted",
            "brand_lane_status": "source_declared",
            "item_code": item_code,
            "product_name": product_name,
            "product_setup": item_code,
            "route": route,
            "website_item": f"WEB-{item_code}",
        },
        "product_setup": {
            "active_authority": False,
            "active_status": True,
            "brand_lane_proved": False,
            "match_status": "matched",
            "operating_brand": "locally_twisted",
            "operating_brand_authority_state": "source_declared",
            "publish_status": "Local Preview Ready",
            "source_active_uniqueness_proved": True,
            "source_active_uniqueness_status": "source_declared_unique",
        },
        "source_authority": {
            "operating_brand": {
                "value": "locally_twisted",
                "authority_state": "source_declared",
                "live_brand_lane_proved": False,
                "proof_scope": "source_only",
            },
            "same_brand_source_uniqueness": {
                "proved": True,
                "status": "source_declared_unique",
            },
        },
        "release_readiness": {
            "cache_clear_approved": False,
            "deploy_approved": False,
            "mutation_approved": False,
            "public_route_proved": public_route_proved,
            "rollback_packet_complete": False,
        },
        "variant": {
            "item_prices": item_prices,
            "severity_bucket": severity_bucket,
            "variant_explosion": "variant_explosion" in blockers,
            "variants": variants,
        },
    }


def _blocker(code: str) -> dict:
    return {
        "code": code,
        "message": code.replace("_", " "),
        "evidence": {},
    }


if __name__ == "__main__":
    unittest.main(verbosity=2)
