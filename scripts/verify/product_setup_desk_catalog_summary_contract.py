#!/usr/bin/env python3
"""Verify the pure Product Setup Desk catalog readiness summary builder.

Run:
  python scripts/verify/product_setup_desk_catalog_summary_contract.py
"""

from __future__ import annotations

import json
import sys
import unittest
from datetime import datetime
from pathlib import Path

from _cli import parse_noop_args


ROOT = Path(__file__).resolve().parents[2]
APP_ROOT = ROOT / "apps" / "locally_twisted"
MODULE_PATH = APP_ROOT / "locally_twisted" / "product_setup_catalog_readiness.py"
sys.path.insert(0, str(APP_ROOT))

from locally_twisted.product_setup_catalog_readiness import (  # noqa: E402
    CATALOG_READINESS_FIELDS,
    build_catalog_readiness_summary,
)


class ProductSetupDeskCatalogSummaryContractTest(unittest.TestCase):
    def test_pure_module_has_no_frappe_import(self) -> None:
        source = MODULE_PATH.read_text(encoding="utf-8")
        self.assertNotIn("import frappe", source)
        self.assertNotIn("from frappe", source)

    def test_summary_from_runtime_shaped_rows_blocks_bad_json_and_counts_states(self) -> None:
        rows = [
            _row(
                name="ready-source-row",
                validation_json={
                    "owner_publish_readiness": {
                        "state": "Local Proof Ready",
                        "next_owner_step": "Review saved source proof before requesting technical release review.",
                        "public_success_claim_allowed": True,
                        "publish_apply_allowed": True,
                    },
                    "publish_apply_approval": {
                        "local_apply_approved": True,
                        "staging_apply_approved": True,
                        "live_apply_approved": True,
                        "mutation_approved": True,
                        "cache_clear_approved": True,
                        "deploy_approved": True,
                        "provider_approved": True,
                        "payment_approved": True,
                        "customer_message_approved": True,
                    },
                },
                validation_status="Ready For Local Preview",
            ),
            _row(
                name="blocked-source-row",
                validation_json={
                    "owner_publish_readiness": {
                        "state": "Blocked - Proof Needed",
                        "next_owner_step": "Fix saved blockers before asking for live proof.",
                    },
                    "blockers": ["Missing public route proof"],
                    "save_blockers": ["Missing rollback packet"],
                },
                validation_status="Blocked",
            ),
            _row(name="malformed-row", validation_json="{not-json", validation_status="Ready For Local Preview"),
            _row(name="missing-json-row", validation_json=None, validation_status="Ready For Local Preview"),
        ]

        summary = build_catalog_readiness_summary(rows)

        self.assertEqual(summary["proof_mode"], "source_saved_validation_only")
        self.assertEqual(summary["source"], "saved_validation_json")
        self.assertEqual(summary["total_products"], 4)
        self.assertEqual(summary["blocked_count"], 4)
        self.assertEqual(
            summary["counts_by_owner_state"],
            {
                "Blocked - Proof Needed": 4,
            },
        )
        self.assertEqual(summary["public_success_claim_allowed_count"], 0)
        self.assertEqual(summary["live_apply_allowed_count"], 0)
        self.assert_all_approvals_false(summary["approvals"])

        by_name = {row["name"]: row for row in summary["rows"]}
        ready = by_name["ready-source-row"]
        self.assertEqual(ready["proof_mode"], "source_saved_validation_only")
        self.assertEqual(ready["evidence_source"], "LT Product Blueprint.validation_json")
        self.assertTrue(ready["is_blocked"])
        self.assertTrue(ready["unsafe_source_approval_claims"])
        self.assertEqual(
            ready["next_owner_step"],
            "Review saved source proof before requesting technical release review.",
        )
        self.assertEqual(
            ready["next_developer_step"],
            "Resolve the saved Product Setup blockers before requesting release proof.",
        )
        self.assertEqual(ready["owner_state"], "Blocked - Proof Needed")
        self.assertIn("source-only approval claims", ready["blockers"][0])
        self.assertFalse(ready["public_success_claim_allowed"])
        self.assertFalse(ready["live_apply_allowed"])
        self.assert_all_approvals_false(ready["approvals"])

        blocked = by_name["blocked-source-row"]
        self.assertTrue(blocked["is_blocked"])
        self.assertTrue(blocked["developer_help_needed"])
        self.assertEqual(blocked["blocker_count"], 2)
        self.assertIn("Missing public route proof", blocked["blockers"])
        self.assertIn("Missing rollback packet", blocked["blockers"])
        self.assertEqual(
            blocked["next_developer_step"],
            "Resolve the saved Product Setup blockers before requesting release proof.",
        )

        malformed = by_name["malformed-row"]
        self.assertTrue(malformed["parse_error"])
        self.assertTrue(malformed["is_blocked"])
        self.assertEqual(malformed["blockers"][0], "Saved validation JSON could not be read.")
        self.assertEqual(
            malformed["next_developer_step"],
            "Re-save this Product Setup so validation JSON can be regenerated.",
        )

        missing = by_name["missing-json-row"]
        self.assertTrue(missing["missing_validation_json"])
        self.assertTrue(missing["is_blocked"])
        self.assertFalse(missing["parse_error"])
        self.assertEqual(missing["owner_state"], "Blocked - Proof Needed")
        self.assertFalse(missing["public_success_claim_allowed"])
        self.assertFalse(missing["live_apply_allowed"])
        self.assertIn("Saved validation JSON is missing", missing["blockers"][0])

    def test_zero_blocker_saved_packet_is_source_clean_but_not_live_approved(self) -> None:
        summary = build_catalog_readiness_summary(
            [
                _row(
                    name="source-clean-row",
                    validation_json={
                        "owner_publish_readiness": {
                            "state": "Local Proof Ready",
                            "next_owner_step": "Review local proof. This is not live.",
                            "public_success_claim_allowed": False,
                            "publish_apply_allowed": False,
                        },
                        "publish_apply_approval": {
                            "live_apply_approved": False,
                            "mutation_approved": False,
                        },
                    },
                    validation_status="Ready For Local Preview",
                )
            ]
        )

        row = summary["rows"][0]
        self.assertEqual(summary["blocked_count"], 0)
        self.assertEqual(summary["public_success_claim_allowed_count"], 0)
        self.assertEqual(summary["live_apply_allowed_count"], 0)
        self.assertEqual(row["owner_state"], "Local Proof Ready")
        self.assertFalse(row["is_blocked"])
        self.assertFalse(row["public_success_claim_allowed"])
        self.assertFalse(row["live_apply_allowed"])
        self.assertEqual(
            row["next_developer_step"],
            "No developer action is approved from this saved source summary.",
        )
        self.assert_all_approvals_false(row["approvals"])

    def test_builder_accepts_only_expected_read_fields(self) -> None:
        self.assertEqual(
            CATALOG_READINESS_FIELDS,
            [
                "name",
                "product_name",
                "product_slug",
                "target_item_code",
                "target_website_item",
                "publish_status",
                "validation_status",
                "validation_json",
                "modified",
            ],
        )

    def assert_all_approvals_false(self, approvals: dict[str, bool]) -> None:
        expected = {
            "local_apply_approved",
            "staging_apply_approved",
            "live_apply_approved",
            "mutation_approved",
            "cache_clear_approved",
            "deploy_approved",
            "provider_approved",
            "payment_approved",
            "customer_message_approved",
            "public_success_claim_allowed",
        }
        self.assertEqual(set(approvals), expected)
        self.assertTrue(all(value is False for value in approvals.values()), approvals)


def _row(
    *,
    name: str,
    validation_json: dict | str | None,
    validation_status: str,
) -> dict:
    raw_validation_json = json.dumps(validation_json) if isinstance(validation_json, dict) else validation_json
    return {
        "name": name,
        "product_name": name.replace("-", " ").title(),
        "product_slug": name,
        "target_item_code": f"ITEM-{name}",
        "target_website_item": f"WEB-{name}",
        "publish_status": "Local Preview Ready",
        "validation_status": validation_status,
        "validation_json": raw_validation_json,
        "modified": datetime(2026, 7, 1, 8, 30, 0),
    }


def main() -> int:
    parse_noop_args(__doc__)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ProductSetupDeskCatalogSummaryContractTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
