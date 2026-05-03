#!/usr/bin/env python3
"""Contract checks for finance inventory helper logic."""
from __future__ import annotations

import pathlib
import sys
import unittest


SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import finance_inventory as inventory  # noqa: E402


class FinanceInventoryContract(unittest.TestCase):
    def test_missing_doctypes_preserves_required_order(self) -> None:
        missing = inventory.missing_doctypes(
            ["Customer", "Supplier", "Payroll Entry"],
            {"Supplier"},
        )

        self.assertEqual(missing, ["Customer", "Payroll Entry"])

    def test_payroll_state_marks_employee_only_as_feasibility(self) -> None:
        state = inventory.classify_payroll_state({"Employee"}, ["frappe", "erpnext"])

        self.assertFalse(state["hrms_installed"])
        self.assertIn("Payroll Entry", state["missing_payroll_doctypes"])
        self.assertIn("feasibility", state["status"])

    def test_setting_gaps_find_bank_payment_terms_supplier_and_payroll(self) -> None:
        gaps = inventory.finance_setting_gaps(
            {
                "record_counts": {
                    "Bank Account": 0,
                    "Payment Terms Template": 0,
                    "Supplier": 0,
                },
                "settings": {
                    "companies": [{"name": "Locally Twisted", "default_bank_account": None}],
                },
                "payroll": {
                    "missing_payroll_doctypes": ["Payroll Entry"],
                },
            }
        )

        self.assertIn("Company default bank account is not set.", gaps)
        self.assertIn("No Bank Account records found.", gaps)
        self.assertIn("No Payment Terms Template records found.", gaps)
        self.assertIn("No Supplier/vendor records found.", gaps)
        self.assertIn("Payroll DocTypes are missing; HRMS/payroll setup is not ready.", gaps)

    def test_no_setting_gaps_when_minimums_exist(self) -> None:
        gaps = inventory.finance_setting_gaps(
            {
                "record_counts": {
                    "Bank Account": 1,
                    "Payment Terms Template": 1,
                    "Supplier": 1,
                },
                "settings": {
                    "companies": [{"name": "Locally Twisted", "default_bank_account": "Main Bank"}],
                },
                "payroll": {
                    "missing_payroll_doctypes": [],
                },
            }
        )

        self.assertEqual(gaps, [])


if __name__ == "__main__":
    unittest.main()
