#!/usr/bin/env python3
"""Verify offline Product Setup authority packet source-boundary semantics.

This verifier uses synthetic saved-artifact payloads only. It does not read
env files, contact ERPNext, use Docker, clear cache, deploy, or mutate data.
"""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[2]
REPORTER_PATH = ROOT / "scripts" / "dev" / "lt_product_setup_authority_packet_report.py"
CATALOG_COLLECTOR_PATH = ROOT / "scripts" / "dev" / "lt_live_readonly_catalog_authority_audit.py"
PRODUCT_COLLECTOR_PATH = ROOT / "scripts" / "dev" / "lt_live_readonly_product_api_audit.py"
PARITY_VERIFIER_PATH = ROOT / "scripts" / "verify" / "product_setup_authority_parity_contract.py"


def load_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


REPORTER = load_module(REPORTER_PATH, "lt_product_setup_authority_packet_report")
PARITY_VERIFIER = load_module(PARITY_VERIFIER_PATH, "product_setup_authority_parity_contract")


class ProductSetupAuthorityPacketContractTest(unittest.TestCase):
    def test_source_declared_brand_does_not_become_live_proof(self) -> None:
        packet = REPORTER.build_packet(Path("synthetic-valid-source.json"), artifact())
        blockers = {blocker["code"] for blocker in packet["blockers"]}

        self.assertEqual(packet["source_authority"]["operating_brand"]["value"], "locally_twisted")
        self.assertEqual(packet["source_authority"]["operating_brand"]["authority_state"], "source_declared")
        self.assertEqual(packet["source_authority"]["operating_brand"]["proof_scope"], "source_only")
        self.assertFalse(packet["source_authority"]["operating_brand"]["live_brand_lane_proved"])
        self.assertTrue(packet["source_authority"]["same_brand_source_uniqueness"]["proved"])
        self.assertEqual(packet["source_authority"]["same_brand_source_uniqueness"]["status"], "source_declared_unique")
        self.assertNotIn("active_uniqueness_unproved", blockers)
        self.assertIn("brand_lane_unproved", blockers)
        self.assertIn("public_route_proof_missing", blockers)
        self.assertIn("pre_mutation_rollback_packet_missing", blockers)
        self.assertFalse(packet["release_readiness"]["mutation_approved"])
        self.assertFalse(packet["release_readiness"]["deploy_approved"])
        self.assertFalse(packet["product_setup"]["active_authority"])

    def test_same_brand_duplicate_keeps_source_uniqueness_blocked(self) -> None:
        duplicate = artifact(
            candidates=[
                candidate("large-head-missionary"),
                candidate("large-head-missionary-copy"),
            ]
        )
        packet = REPORTER.build_packet(Path("synthetic-duplicate-source.json"), duplicate)
        blockers = {blocker["code"] for blocker in packet["blockers"]}

        self.assertFalse(packet["source_authority"]["same_brand_source_uniqueness"]["proved"])
        self.assertEqual(
            packet["source_authority"]["same_brand_source_uniqueness"]["status"],
            "unproved_duplicate_same_brand",
        )
        self.assertIn("active_uniqueness_unproved", blockers)
        self.assertEqual(
            packet["source_authority"]["same_brand_source_uniqueness"]["conflicts"],
            ["large-head-missionary", "large-head-missionary-copy"],
        )

    def test_collectors_preserve_operating_brand_for_future_artifacts(self) -> None:
        catalog_collector = CATALOG_COLLECTOR_PATH.read_text(encoding="utf-8")
        product_collector = PRODUCT_COLLECTOR_PATH.read_text(encoding="utf-8")

        self.assertIn('"operating_brand"', catalog_collector)
        self.assertIn('"brand_lane_status": "source_declared"', catalog_collector)
        self.assertIn('"operating_brand"', product_collector)

    def test_parity_verifier_accepts_packet_boundary_shape(self) -> None:
        packet = REPORTER.build_packet(Path("synthetic-valid-source.json"), artifact())
        packet["blockers"] = []
        report = PARITY_VERIFIER.report_from_packet({"packets": [packet]}, parity_args())

        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["input_summary"]["detected_type"], "packet")

    def test_parity_verifier_rejects_source_declared_as_live_proof(self) -> None:
        packet = REPORTER.build_packet(Path("synthetic-valid-source.json"), artifact())
        packet["blockers"] = []
        packet["source_authority"]["operating_brand"]["live_brand_lane_proved"] = True
        report = PARITY_VERIFIER.report_from_packet({"packets": [packet]}, parity_args())

        self.assertEqual(report["status"], "fail")
        self.assertIn("source_declared operating brand is incorrectly marked as live proved", "\n".join(report["blockers"]))


def artifact(*, candidates: list[dict[str, object]] | None = None) -> dict[str, object]:
    candidates = candidates or [candidate("large-head-missionary")]
    return {
        "product_identifier": {
            "website_item": "WEB-ITM-0039",
            "item_code": "large-head-missionary",
            "route": "/shop-items/bouquets/large-head-missionary",
            "brand_lane": "locally_twisted",
            "brand_lane_status": "source_declared",
            "product_setup": "large-head-missionary",
            "product_name": "Large head Missionary",
        },
        "match_summary": {
            "blueprint_match_status": "matched",
            "blueprint_match_basis": "target_item_code=large-head-missionary",
            "candidate_blueprints": candidates,
        },
        "blueprint_summary": {
            "name": "large-head-missionary",
            "product_name": "Large head Missionary",
            "product_slug": "large-head-missionary",
            "operating_brand": "locally_twisted",
            "base_price": 125.0,
            "publish_status": "Local Preview Ready",
            "target_item_code": "large-head-missionary",
            "target_website_item": "WEB-ITM-0039",
        },
        "website_item_summary": {
            "name": "WEB-ITM-0039",
            "item_code": "large-head-missionary",
            "route": "/shop-items/bouquets/large-head-missionary",
        },
        "counts": {
            "variants": 1,
            "item_prices": 1,
            "blueprint_price_rows": 1,
        },
        "price_summary": {
            "blueprint_base_price": 125.0,
            "blueprint_price_row_values": [125.0],
            "item_price_values": [125.0],
        },
        "content_summary": {
            "blueprint_content_fields": {"product_story": "Bright, friendly balloon bouquet."},
            "website_item_content_fields": {"lt_brand_description": "Bright, friendly balloon bouquet."},
        },
        "public_summary": {"skipped": True, "reason": "synthetic verifier"},
        "rows": {
            "blueprint_price_rows": [{"item_code": "large-head-missionary", "price": 125.0}],
            "item_prices": [{"item_code": "large-head-missionary", "price_list_rate": 125.0}],
        },
        "failures": [],
    }


def candidate(name: str) -> dict[str, object]:
    return {
        "name": name,
        "product_slug": "large-head-missionary",
        "operating_brand": "locally_twisted",
        "target_item_code": "large-head-missionary",
        "target_website_item": "WEB-ITM-0039",
        "publish_status": "Local Preview Ready",
    }


def parity_args() -> SimpleNamespace:
    return SimpleNamespace(
        input="synthetic-packet-report.json",
        input_type="packet",
        allow_price_drift=False,
        allow_copy_drift=False,
    )


if __name__ == "__main__":
    unittest.main(verbosity=2)
