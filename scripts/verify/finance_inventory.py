#!/usr/bin/env python3
"""Read-only finance, payroll, and migration inventory for LT ERPNext.

This does not mutate ERPNext. It reports the accounting surfaces that matter
before QuickBooks migration, collections automation, banking sync, or payroll
setup are enabled.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"

CORE_FINANCE_DOCTYPES = [
    "Customer",
    "Supplier",
    "Sales Order",
    "Sales Invoice",
    "Payment Request",
    "Payment Entry",
    "Journal Entry",
    "Account",
    "Bank Account",
    "Bank Transaction",
    "Bank Reconciliation Tool",
    "Plaid Settings",
    "Process Statement Of Accounts",
    "Payment Terms Template",
    "Payment Term",
    "Purchase Invoice",
    "Company",
    "Fiscal Year",
    "Sales Taxes and Charges Template",
    "Payment Gateway Account",
    "Mode of Payment",
    "Stripe Settings",
]
PAYROLL_DOCTYPES = [
    "Employee",
    "Payroll Entry",
    "Salary Slip",
    "Salary Structure",
]
COUNT_DOCTYPES = [
    "Customer",
    "Supplier",
    "Sales Order",
    "Sales Invoice",
    "Payment Request",
    "Payment Entry",
    "Journal Entry",
    "Account",
    "Bank Account",
    "Bank Transaction",
    "Payment Terms Template",
    "Payment Term",
    "Purchase Invoice",
    "Employee",
    "Payroll Entry",
    "Salary Slip",
]


def bench_execute(
    method: str,
    *,
    args: list[Any] | None = None,
    kwargs: dict[str, Any] | None = None,
    timeout: int = 90,
) -> Any:
    cmd = [
        "docker",
        "exec",
        CONTAINER,
        "bench",
        "--site",
        SITE,
        "execute",
        method,
    ]
    if args is not None:
        cmd.extend(["--args", json.dumps(args)])
    if kwargs is not None:
        cmd.extend(["--kwargs", json.dumps(kwargs)])

    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
    if proc.returncode != 0:
        raise RuntimeError(
            f"bench execute failed for {method}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    text = proc.stdout.strip()
    return json.loads(text) if text else None


def get_all(doctype: str, **kwargs: Any) -> list[dict[str, Any]]:
    payload = {"doctype": doctype, **kwargs}
    return bench_execute("frappe.client.get_list", kwargs=payload) or []


def get_count(doctype: str, filters: dict[str, Any] | None = None) -> int:
    kwargs: dict[str, Any] = {"doctype": doctype}
    if filters:
        kwargs["filters"] = filters
    return int(bench_execute("frappe.client.get_count", kwargs=kwargs) or 0)


def existing_doctypes(rows: list[dict[str, Any]]) -> set[str]:
    return {str(row["name"]) for row in rows}


def missing_doctypes(required: list[str], existing: set[str]) -> list[str]:
    return [name for name in required if name not in existing]


def classify_payroll_state(existing: set[str], installed_apps: list[str]) -> dict[str, Any]:
    missing = missing_doctypes(PAYROLL_DOCTYPES, existing)
    hrms_installed = "hrms" in installed_apps
    if not missing and hrms_installed:
        status = "HRMS payroll app appears installed and payroll DocTypes are present."
    elif not missing:
        status = "Payroll DocTypes are present, but HRMS is not listed in installed apps."
    elif "Employee" in existing:
        status = "Employee exists, but payroll DocTypes are missing. Treat payroll as feasibility work."
    else:
        status = "Employee and payroll DocTypes are missing. Payroll is not ready."
    return {
        "hrms_installed": hrms_installed,
        "missing_payroll_doctypes": missing,
        "status": status,
    }


def finance_setting_gaps(inventory: dict[str, Any]) -> list[str]:
    gaps: list[str] = []
    counts = inventory["record_counts"]
    companies = inventory["settings"]["companies"]
    if companies and not any(company.get("default_bank_account") for company in companies):
        gaps.append("Company default bank account is not set.")
    if counts.get("Bank Account", 0) == 0:
        gaps.append("No Bank Account records found.")
    if counts.get("Payment Terms Template", 0) == 0:
        gaps.append("No Payment Terms Template records found.")
    if counts.get("Supplier", 0) == 0:
        gaps.append("No Supplier/vendor records found.")
    if inventory["payroll"]["missing_payroll_doctypes"]:
        gaps.append("Payroll DocTypes are missing; HRMS/payroll setup is not ready.")
    return gaps


def count_if_present(doctype: str, existing: set[str], filters: dict[str, Any] | None = None) -> int | None:
    if doctype not in existing:
        return None
    return get_count(doctype, filters=filters)


def collect_inventory() -> dict[str, Any]:
    installed_apps = bench_execute("frappe.get_installed_apps") or []
    all_surface_names = sorted(set(CORE_FINANCE_DOCTYPES + PAYROLL_DOCTYPES))
    doctype_rows = get_all(
        "DocType",
        filters={"name": ["in", all_surface_names]},
        fields=["name", "module", "custom", "istable", "issingle"],
        order_by="name asc",
        limit_page_length=200,
    )
    existing = existing_doctypes(doctype_rows)

    record_counts = {
        doctype: count_if_present(doctype, existing)
        for doctype in COUNT_DOCTYPES
        if doctype in existing
    }
    record_counts.update(
        {
            "Unpaid Sales Invoices": count_if_present(
                "Sales Invoice",
                existing,
                {"docstatus": 1, "outstanding_amount": [">", 0]},
            ),
            "Overdue Sales Invoices": count_if_present(
                "Sales Invoice",
                existing,
                {"docstatus": 1, "status": "Overdue"},
            ),
            "Expected Payment Requests": count_if_present(
                "Payment Request",
                existing,
                {
                    "payment_request_type": "Inward",
                    "status": ["in", ["Initiated", "Requested"]],
                    "outstanding_amount": [">", 0],
                },
            ),
            "Paid Payment Requests": count_if_present(
                "Payment Request",
                existing,
                {"payment_request_type": "Inward", "status": "Paid"},
            ),
            "Open Purchase Invoices": count_if_present(
                "Purchase Invoice",
                existing,
                {"docstatus": 1, "outstanding_amount": [">", 0]},
            ),
        }
    )

    settings = {
        "companies": get_all(
            "Company",
            fields=["name", "default_currency", "country", "default_bank_account"],
            limit_page_length=20,
        )
        if "Company" in existing
        else [],
        "fiscal_years": get_all(
            "Fiscal Year",
            fields=["name", "year_start_date", "year_end_date", "disabled"],
            order_by="year_start_date desc",
            limit_page_length=20,
        )
        if "Fiscal Year" in existing
        else [],
        "tax_templates": get_all(
            "Sales Taxes and Charges Template",
            fields=["name", "company", "disabled", "is_default"],
            limit_page_length=50,
        )
        if "Sales Taxes and Charges Template" in existing
        else [],
        "payment_gateway_accounts": get_all(
            "Payment Gateway Account",
            fields=["name", "payment_gateway", "payment_account", "currency", "is_default"],
            limit_page_length=50,
        )
        if "Payment Gateway Account" in existing
        else [],
        "modes_of_payment": get_all(
            "Mode of Payment",
            fields=["name", "type", "enabled"],
            limit_page_length=50,
        )
        if "Mode of Payment" in existing
        else [],
    }

    inventory = {
        "installed_apps": installed_apps,
        "doctype_rows": doctype_rows,
        "missing_core_finance_doctypes": missing_doctypes(CORE_FINANCE_DOCTYPES, existing),
        "payroll": classify_payroll_state(existing, installed_apps),
        "record_counts": record_counts,
        "settings": settings,
    }
    inventory["setting_gaps"] = finance_setting_gaps(inventory)
    return inventory


def emit_markdown(inventory: dict[str, Any]) -> str:
    rows = {row["name"]: row for row in inventory["doctype_rows"]}
    lines = [
        "# Finance Inventory",
        "",
        "## Installed Apps",
        "",
        f"- {', '.join(inventory['installed_apps'])}",
        "",
        "## Required Finance Surfaces",
        "",
    ]
    for name in CORE_FINANCE_DOCTYPES:
        row = rows.get(name)
        if row:
            lines.append(f"- {name}: present ({row.get('module')})")
        else:
            lines.append(f"- {name}: MISSING")

    lines.extend(["", "## Payroll Feasibility", ""])
    lines.append(f"- HRMS installed: {inventory['payroll']['hrms_installed']}")
    lines.append(f"- Status: {inventory['payroll']['status']}")
    missing_payroll = inventory["payroll"]["missing_payroll_doctypes"]
    lines.append(f"- Missing payroll DocTypes: {', '.join(missing_payroll) if missing_payroll else 'none'}")

    lines.extend(["", "## Record Counts", ""])
    for key, value in inventory["record_counts"].items():
        lines.append(f"- {key}: {value}")

    lines.extend(["", "## Settings Snapshot", ""])
    for company in inventory["settings"]["companies"]:
        lines.append(
            "- Company: "
            f"{company.get('name')} / currency {company.get('default_currency')} / "
            f"country {company.get('country')} / default bank {company.get('default_bank_account') or 'not set'}"
        )
    for fiscal_year in inventory["settings"]["fiscal_years"]:
        disabled = "disabled" if fiscal_year.get("disabled") else "active"
        lines.append(
            "- Fiscal Year: "
            f"{fiscal_year.get('name')} ({fiscal_year.get('year_start_date')} to "
            f"{fiscal_year.get('year_end_date')}, {disabled})"
        )
    for template in inventory["settings"]["tax_templates"]:
        default = "default" if template.get("is_default") else "not default"
        disabled = "disabled" if template.get("disabled") else "active"
        lines.append(f"- Sales Tax Template: {template.get('name')} ({default}, {disabled})")
    for account in inventory["settings"]["payment_gateway_accounts"]:
        default = "default" if account.get("is_default") else "not default"
        lines.append(
            "- Payment Gateway Account: "
            f"{account.get('name')} / {account.get('payment_gateway')} / "
            f"{account.get('payment_account')} / {account.get('currency')} ({default})"
        )
    for mode in inventory["settings"]["modes_of_payment"]:
        enabled = "enabled" if mode.get("enabled") else "disabled"
        lines.append(f"- Mode of Payment: {mode.get('name')} ({mode.get('type')}, {enabled})")

    lines.extend(["", "## Setup Gaps To Review", ""])
    if inventory["setting_gaps"]:
        for gap in inventory["setting_gaps"]:
            lines.append(f"- {gap}")
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Guardrail",
            "",
            "- This inventory is read-only. It does not submit invoices, send reminders, sync banks, import QuickBooks data, or run payroll.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown.")
    args = parser.parse_args()

    try:
        inventory = collect_inventory()
    except Exception as exc:
        print("[FINANCE INVENTORY] FAIL")
        print(f"  - {exc}")
        return 1

    if args.json:
        print(json.dumps(inventory, indent=2, sort_keys=True, default=str))
    else:
        print(emit_markdown(inventory))
        if inventory["missing_core_finance_doctypes"]:
            print("[FINANCE INVENTORY] FAIL")
            for name in inventory["missing_core_finance_doctypes"]:
                print(f"  - Missing required finance DocType: {name}")
            return 1
        print("[FINANCE INVENTORY] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
