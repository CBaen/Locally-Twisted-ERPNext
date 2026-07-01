#!/usr/bin/env python3
"""Verify the source-only Product Setup release packet contract."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "dev" / "lt_product_setup_release_packet_report.py"


class ProductSetupReleasePacketContractTest(unittest.TestCase):
    def test_blocked_dashboard_product_builds_release_packet(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dashboard = Path(tmp) / "dashboard.json"
            output = Path(tmp) / "release-packet.json"
            dashboard.write_text(json.dumps(_dashboard()), encoding="utf-8")

            completed = _run_packet(dashboard, output, "large-head-missionary", fail_on_blocker=True)

            self.assertEqual(completed.returncode, 1, completed.stderr)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["schema_version"], "lt-product-setup-release-packet-v1")
            self.assertTrue(report["deterministic"])
            self.assertIn("offline saved Phase 15 catalog readiness dashboard JSON only", report["proof_mode"])
            self.assertEqual(report["product"]["item_code"], "large-head-missionary")
            self.assertEqual(report["product"]["route_slug"], "large-head-missionary")
            self.assertEqual(report["source_dashboard_summary"]["selected_product_blocker_count"], 7)
            self.assertTrue(report["release_packet"]["blocked"])
            self.assertFalse(report["release_packet"]["approved"])
            self.assertIn("fresh_target_site_public_route_proof", _missing_gate_names(report))
            self.assertIn("rollback_packet_complete_and_reviewed", _missing_gate_names(report))
            self.assertTrue(report["rollback_requirements"]["required"])
            self.assertFalse(report["rollback_requirements"]["complete"])
            self.assertFalse(report["no_downtime_customer_impact"]["approved"])
            self.assertFalse(report["no_downtime_customer_impact"]["customer_message_approved"])
            self.assert_all_approvals_false(report["approval_contract"])
            self.assert_all_target_approvals_false(report["target_environment_approvals"])
            self.assertTrue(any(action["allowed"] for action in report["owner_allowed_actions"]))
            self.assertTrue(any(not action["allowed"] for action in report["owner_allowed_actions"]))
            self.assertTrue(report["stop_condition"]["stop"])

    def test_zero_dashboard_blockers_still_block_without_target_proof(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dashboard = Path(tmp) / "dashboard.json"
            output = Path(tmp) / "release-packet.json"
            dashboard.write_text(json.dumps(_dashboard()), encoding="utf-8")

            completed = _run_packet(dashboard, output, "ready-review-product", fail_on_blocker=True)

            self.assertEqual(completed.returncode, 1, completed.stderr)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["source_dashboard_summary"]["selected_product_blocker_count"], 0)
            gates = {gate["gate"]: gate for gate in report["proof_gates"]}
            self.assertTrue(gates["dashboard_blockers_clear"]["passed"])
            self.assertFalse(gates["fresh_target_site_public_route_proof"]["passed"])
            self.assertFalse(gates["owner_product_scope_approval"]["passed"])
            self.assertTrue(report["release_packet"]["blocked"])
            self.assertFalse(report["approval_contract"]["live_apply_approved"])
            self.assertFalse(report["approval_contract"]["mutation_approved"])
            self.assertFalse(report["approval_contract"]["provider_action_approved"])
            self.assertFalse(report["approval_contract"]["payment_action_approved"])
            self.assertFalse(report["approval_contract"]["customer_message_approved"])

    def test_product_filter_matches_product_setup_item_code_route_slug_and_route(self) -> None:
        filters = [
            "large-head-missionary-setup",
            "large-head-missionary",
            "/shop-items/bouquets/large-head-missionary",
            "birthday-deliveries-setup",
            "birthday-deliveries",
            "/shop-items/bouquets/birthday-deliveries",
        ]
        with tempfile.TemporaryDirectory() as tmp:
            dashboard = Path(tmp) / "dashboard.json"
            dashboard.write_text(json.dumps(_dashboard()), encoding="utf-8")
            for product_filter in filters:
                output = Path(tmp) / f"{product_filter.strip('/').replace('/', '-')}.json"
                completed = _run_packet(dashboard, output, product_filter)
                self.assertEqual(completed.returncode, 0, completed.stderr)
                report = json.loads(output.read_text(encoding="utf-8"))
                self.assertIn(report["product"]["item_code"], {"large-head-missionary", "birthday-deliveries"})

    def test_rejects_non_dashboard_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad_input = Path(tmp) / "packet-report.json"
            output = Path(tmp) / "release-packet.json"
            bad_input.write_text(json.dumps({"schema_version": "lt-product-setup-authority-packet-v1"}), encoding="utf-8")

            completed = _run_packet(bad_input, output, "large-head-missionary", fail_on_blocker=True)

            self.assertEqual(completed.returncode, 2, completed.stderr)
            self.assertIn("unexpected dashboard schema_version", completed.stderr)
            self.assertFalse(output.exists())

    def test_output_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dashboard = Path(tmp) / "dashboard.json"
            output_a = Path(tmp) / "a.json"
            output_b = Path(tmp) / "b.json"
            dashboard.write_text(json.dumps(_dashboard()), encoding="utf-8")

            completed_a = _run_packet(dashboard, output_a, "large-head-missionary")
            completed_b = _run_packet(dashboard, output_b, "large-head-missionary")

            self.assertEqual(completed_a.returncode, 0, completed_a.stderr)
            self.assertEqual(completed_b.returncode, 0, completed_b.stderr)
            self.assertEqual(output_a.read_text(encoding="utf-8"), output_b.read_text(encoding="utf-8"))

    def test_saved_catalog_dashboard_when_available(self) -> None:
        dashboard = Path("/tmp/lt-catalog-readiness-dashboard.json")
        if not dashboard.exists():
            self.skipTest("saved Phase 15 catalog readiness dashboard is not present")
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "release-packet.json"
            completed = _run_packet(dashboard, output, "large-head-missionary", fail_on_blocker=True)

            self.assertEqual(completed.returncode, 1, completed.stderr)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["schema_version"], "lt-product-setup-release-packet-v1")
            self.assertTrue(report["release_packet"]["blocked"])
            self.assertFalse(report["approval_contract"]["mutation_approved"])

    def assert_all_approvals_false(self, approvals: dict) -> None:
        self.assertTrue(approvals)
        for key, value in approvals.items():
            self.assertIs(value, False, key)

    def assert_all_target_approvals_false(self, approvals: dict) -> None:
        self.assertTrue(approvals)
        for environment in approvals.values():
            for key, value in environment.items():
                if key.endswith("_approved"):
                    self.assertIs(value, False, key)


def _run_packet(
    dashboard: Path,
    output: Path,
    product_filter: str,
    *,
    fail_on_blocker: bool = False,
) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable,
        str(SCRIPT),
        "--dashboard",
        str(dashboard),
        "--product",
        product_filter,
        "--output",
        str(output),
        "--pretty",
    ]
    if fail_on_blocker:
        command.append("--fail-on-blocker")
    return subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)


def _missing_gate_names(report: dict) -> set[str]:
    return {gate["gate"] for gate in report["missing_gates"]}


def _dashboard() -> dict:
    rows = [
        _row(
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
            public_route_proved=False,
        ),
        _row(
            item_code="birthday-deliveries",
            product_name="Birthday Deliveries",
            route="/shop-items/bouquets/birthday-deliveries",
            blockers=["variant_explosion", "pre_mutation_rollback_packet_missing"],
            variants=2430,
            item_prices=2430,
            public_route_proved=False,
        ),
        _row(
            item_code="ready-review-product",
            product_name="Ready Review Product",
            route="/shop-items/bouquets/ready-review-product",
            blockers=[],
            public_route_proved=True,
        ),
    ]
    return {
        "schema_version": "lt-product-setup-catalog-readiness-dashboard-v1",
        "generated_at": "deterministic-offline-report",
        "deterministic": True,
        "proof_mode": "offline saved authority packet report JSON only",
        "catalog_counts": {
            "product_count": 3,
            "blocked_product_count": 2,
            "ready_product_count": 1,
            "blocker_count": 9,
        },
        "product_rows": rows,
    }


def _row(
    *,
    item_code: str,
    product_name: str,
    route: str,
    blockers: list[str],
    public_route_proved: bool,
    variants: int = 30,
    item_prices: int = 30,
) -> dict:
    return {
        "product": {
            "product_setup": f"{item_code}-setup",
            "item_code": item_code,
            "website_item": f"WEB-{item_code}",
            "route": route,
            "product_name": product_name,
            "operating_brand": "locally_twisted",
            "operating_brand_authority_state": "source_declared",
            "brand_lane_status": "source_declared",
        },
        "readiness": {
            "authority_status": "blocked" if blockers else "ready",
            "owner_state": "Blocked - Proof Needed" if blockers else "Ready For Reviewed Apply",
            "public_success_claim_allowed": False,
            "next_owner_action": "Request technical review.",
            "next_developer_action": "Resolve blockers.",
        },
        "blockers": {
            "count": len(blockers),
            "codes": sorted(blockers),
            "groups": ["public_release_proof"] if blockers else [],
            "primary_code": sorted(blockers)[0] if blockers else None,
        },
        "authority": {
            "product_setup_match_status": "matched",
            "product_setup_publish_status": "Local Preview Ready",
            "product_setup_active_status": True,
            "product_setup_active_authority": False,
            "live_brand_lane_proved": False,
            "same_brand_source_uniqueness_status": "source_declared_unique",
            "same_brand_source_uniqueness_proved": True,
        },
        "price": {
            "drift_status": "mismatch" if "price_mismatch" in blockers else "match",
            "setup_values": ["125.00"],
            "item_price_values": ["175.00" if "price_mismatch" in blockers else "125.00"],
        },
        "copy": {"differs": "copy_authority_drift" in blockers},
        "variant": {
            "variants": variants,
            "item_prices": item_prices,
            "severity_bucket": "critical" if variants > 1000 else "normal",
            "variant_explosion": "variant_explosion" in blockers,
        },
        "release_readiness": {
            "public_route_proved": public_route_proved,
            "rollback_packet_complete": False,
            "approvals": {
                "local_apply_approved": False,
                "staging_apply_approved": False,
                "live_apply_approved": False,
                "cache_clear_approved": False,
                "deploy_approved": False,
                "mutation_approved": False,
                "public_success_claim_allowed": False,
            },
        },
    }


if __name__ == "__main__":
    unittest.main(verbosity=2)
