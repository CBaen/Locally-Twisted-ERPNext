#!/usr/bin/env python3
"""Contract checks for the backend schema inventory helper logic."""
from __future__ import annotations

import pathlib
import sys
import unittest


SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import backend_schema_inventory as inventory  # noqa: E402


class BackendSchemaInventoryContract(unittest.TestCase):
    def test_code_owned_custom_fields_are_classified_from_hooks(self) -> None:
        hooks = {
            "fixtures": [
                {
                    "dt": "Custom Field",
                    "filters": [["name", "in", ["Lead-custom_pipeline_stage", "Task-custom_lt_lead"]]],
                }
            ]
        }

        rows = [
            {"name": "Lead-custom_pipeline_stage", "dt": "Lead", "fieldname": "custom_pipeline_stage"},
            {"name": "Lead-custom_event_type", "dt": "Lead", "fieldname": "custom_event_type"},
            {"name": "Task-custom_lt_lead", "dt": "Task", "fieldname": "custom_lt_lead"},
        ]

        classified = inventory.classify_custom_fields(rows, hooks)

        self.assertEqual(
            classified["code_owned"],
            ["Lead-custom_pipeline_stage", "Task-custom_lt_lead"],
        )
        self.assertEqual(classified["db_only"], ["Lead-custom_event_type"])

    def test_stale_label_scan_reports_file_and_term(self) -> None:
        findings = inventory.find_stale_terms(
            {
                "scripts/setup/current.py": "Delivery\nPickup",
                "scripts/fix/old.py": "Event Package",
            },
            ["Event Package", "Delivery Only"],
        )

        self.assertEqual(
            findings,
            [{"path": "scripts/fix/old.py", "term": "Event Package"}],
        )

    def test_stale_label_scan_can_ignore_guardrail_references(self) -> None:
        findings = inventory.find_stale_terms(
            {"scripts/verify/guard.py": "Event Package"},
            ["Event Package"],
            ignored={("scripts/verify/guard.py", "Event Package")},
        )

        self.assertEqual(findings, [])

    def test_code_source_reference_marks_custom_field_as_owned(self) -> None:
        classified = inventory.classify_custom_fields(
            [{"name": "Task-custom_lt_lead", "dt": "Task", "fieldname": "custom_lt_lead"}],
            {"fixtures": []},
            {"stage_cascade.py": 'LEAD_TASK_FIELD = "custom_lt_lead"'},
        )

        self.assertEqual(classified["sync_owned"], ["Task-custom_lt_lead"])
        self.assertEqual(classified["db_only"], [])

    def test_generic_fieldname_reference_does_not_mark_field_as_owned(self) -> None:
        classified = inventory.classify_custom_fields(
            [{"name": "GoCardless Mandate-customer", "dt": "GoCardless Mandate", "fieldname": "customer"}],
            {"fixtures": []},
            {"checkout.py": '"customer"'},
        )

        self.assertEqual(classified["code_owned"], [])
        self.assertEqual(classified["db_only"], ["GoCardless Mandate-customer"])


if __name__ == "__main__":
    unittest.main()
