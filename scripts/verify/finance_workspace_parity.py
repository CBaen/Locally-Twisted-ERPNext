#!/usr/bin/env python3
"""Verify LT accounting finance workspace and cards."""
from __future__ import annotations

import json
import subprocess
import sys
from typing import Any

from _cli import parse_noop_args


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
ACCOUNTANT_HOME = "LT Accountant Home"
ACCOUNTANT_HOME_TITLE = "Accounting Home"
ACCOUNTANT_ROLE = "LT Accountant Access"
ACCOUNTANT_TEMP_USER = "lt-accountant-temp@example.com"

EXPECTED_NUMBER_CARDS = {
    "Unpaid Invoices": {
        "label": "Unpaid Invoices",
        "document_type": "Sales Invoice",
        "function": "Count",
        "filters_json": [
            ["Sales Invoice", "docstatus", "=", 1, False],
            ["Sales Invoice", "outstanding_amount", ">", 0, False],
        ],
    },
    "Overdue Invoices": {
        "label": "Overdue Invoices",
        "document_type": "Sales Invoice",
        "function": "Count",
        "filters_json": [
            ["Sales Invoice", "docstatus", "=", 1, False],
            ["Sales Invoice", "status", "=", "Overdue", False],
        ],
    },
    "Expected Payments": {
        "label": "Expected Payments",
        "document_type": "Payment Request",
        "function": "Count",
        "filters_json": [
            ["Payment Request", "payment_request_type", "=", "Inward", False],
            ["Payment Request", "status", "in", ["Initiated", "Requested"], False],
            ["Payment Request", "outstanding_amount", ">", 0, False],
        ],
    },
    "Recent Paid Orders": {
        "label": "Recent Paid Orders",
        "document_type": "Payment Request",
        "function": "Count",
        "filters_json": [
            ["Payment Request", "payment_request_type", "=", "Inward", False],
            ["Payment Request", "status", "=", "Paid", False],
            ["Payment Request", "modified", "Timespan", "this year", False],
        ],
    },
}

EXPECTED_SHORTCUTS = {
    "Sales Invoices": ("Sales Invoice", "List"),
    "Payment Requests": ("Payment Request", "List"),
    "Payments": ("Payment Entry", "List"),
    "Customers": ("Customer", "List"),
    "Journal Entries": ("Journal Entry", "List"),
    "Chart of Accounts": ("Account", "Tree"),
}

FORBIDDEN_SHORTCUTS = {
    "Suppliers",
    "Purchase Invoices",
    "Bank Transactions",
    "Bank Accounts",
    "Bank Reconciliation",
    "Payment Terms",
    "Statement Reminders",
    "Employees",
}

EXPECTED_URL_SHORTCUTS = {}

EXPECTED_REPORT_SHORTCUTS = {
    "Reminder Review Report": {
        "report_name": "LT Customer Reminder Review",
        "ref_doctype": "Sales Invoice",
        "report_type": "Script Report",
        "module": "Locally Twisted",
    },
}

EXPECTED_TEXT = {
    "Accounting Home",
    "Money to collect",
    "Review before sending",
    "Accounting reference",
}


def bench_execute(method: str, *, kwargs: dict[str, Any] | None = None) -> Any:
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
    if kwargs is not None:
        cmd.extend(["--kwargs", json.dumps(kwargs)])

    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=60)
    if proc.returncode != 0:
        raise RuntimeError(
            f"bench execute failed for {method}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    text = proc.stdout.strip()
    return json.loads(text) if text else None


def get_doc(doctype: str, name: str) -> dict[str, Any]:
    return bench_execute("frappe.client.get", kwargs={"doctype": doctype, "name": name})


def try_get_doc(doctype: str, name: str) -> dict[str, Any] | None:
    try:
        return get_doc(doctype, name)
    except RuntimeError as exc:
        if "DoesNotExistError" in str(exc):
            return None
        raise


def decode_json(value: str | None) -> Any:
    if not value:
        return []
    return json.loads(value)


def check_workspace() -> list[str]:
    failures = []
    workspace = get_doc("Workspace", ACCOUNTANT_HOME)
    content = json.loads(workspace.get("content") or "[]")
    content_text = json.dumps(content)
    shortcut_blocks = {
        (block.get("data") or {}).get("shortcut_name")
        for block in content
        if block.get("type") == "shortcut"
    }
    card_blocks = {
        (block.get("data") or {}).get("number_card_name")
        for block in content
        if block.get("type") == "number_card"
    }
    shortcuts = {row.get("label"): row for row in workspace.get("shortcuts", [])}
    roles = {row.get("role") for row in workspace.get("roles", [])}
    workspace_cards = {row.get("number_card_name") for row in workspace.get("number_cards", [])}

    if workspace.get("title") != ACCOUNTANT_HOME_TITLE:
        failures.append(
            f"{ACCOUNTANT_HOME} title expected {ACCOUNTANT_HOME_TITLE!r}, found {workspace.get('title')!r}"
        )

    if ACCOUNTANT_ROLE not in roles:
        failures.append(f"{ACCOUNTANT_HOME} missing role {ACCOUNTANT_ROLE!r}")

    forbidden_found = sorted(
        (set(shortcuts) | {label for label in shortcut_blocks if label}) & FORBIDDEN_SHORTCUTS
    )
    if forbidden_found:
        failures.append(
            f"{ACCOUNTANT_HOME} still shows unfinished finance/payroll shortcuts: "
            f"{', '.join(forbidden_found)}"
        )

    for text in EXPECTED_TEXT:
        if text not in content_text:
            failures.append(f"{ACCOUNTANT_HOME} content missing text {text!r}")

    for label, (doctype, view) in EXPECTED_SHORTCUTS.items():
        shortcut = shortcuts.get(label)
        if not shortcut:
            failures.append(f"{ACCOUNTANT_HOME} missing shortcut {label!r}")
            continue
        if label not in shortcut_blocks:
            failures.append(f"{ACCOUNTANT_HOME} content missing shortcut block {label!r}")
        if shortcut.get("link_to") != doctype or shortcut.get("doc_view") != view:
            failures.append(
                f"{ACCOUNTANT_HOME} {label!r} expected {doctype}/{view}, found "
                f"{shortcut.get('link_to')}/{shortcut.get('doc_view')}"
            )

    for label, url in EXPECTED_URL_SHORTCUTS.items():
        shortcut = shortcuts.get(label)
        if not shortcut:
            failures.append(f"{ACCOUNTANT_HOME} missing shortcut {label!r}")
            continue
        if label not in shortcut_blocks:
            failures.append(f"{ACCOUNTANT_HOME} content missing shortcut block {label!r}")
        if shortcut.get("type") != "URL" or shortcut.get("url") != url:
            failures.append(
                f"{ACCOUNTANT_HOME} {label!r} expected URL {url}, found "
                f"{shortcut.get('type')} {shortcut.get('url')}"
            )

    for label, expected in EXPECTED_REPORT_SHORTCUTS.items():
        shortcut = shortcuts.get(label)
        if not shortcut:
            failures.append(f"{ACCOUNTANT_HOME} missing shortcut {label!r}")
            continue
        if label not in shortcut_blocks:
            failures.append(f"{ACCOUNTANT_HOME} content missing shortcut block {label!r}")
        if (
            shortcut.get("type") != "Report"
            or shortcut.get("link_to") != expected["report_name"]
            or shortcut.get("report_ref_doctype") != expected["ref_doctype"]
        ):
            failures.append(
                f"{ACCOUNTANT_HOME} {label!r} expected Report {expected['report_name']} "
                f"for {expected['ref_doctype']}, found {shortcut.get('type')} "
                f"{shortcut.get('link_to')} / {shortcut.get('report_ref_doctype')}"
            )

    for card_name in EXPECTED_NUMBER_CARDS:
        if card_name not in workspace_cards:
            failures.append(f"{ACCOUNTANT_HOME} missing number card child row {card_name!r}")
        if card_name not in card_blocks:
            failures.append(f"{ACCOUNTANT_HOME} content missing number card block {card_name!r}")

    return failures


def check_number_cards() -> list[str]:
    failures = []
    for name, expected in EXPECTED_NUMBER_CARDS.items():
        card = try_get_doc("Number Card", name)
        if not card:
            failures.append(f"Missing Number Card {name!r}")
            continue
        for key in ("label", "document_type", "function"):
            if card.get(key) != expected[key]:
                failures.append(
                    f"Number Card {name!r} {key} expected {expected[key]!r}, found {card.get(key)!r}"
                )
        if decode_json(card.get("filters_json")) != expected["filters_json"]:
            failures.append(
                f"Number Card {name!r} filters expected {expected['filters_json']!r}, "
                f"found {decode_json(card.get('filters_json'))!r}"
            )
    return failures


def check_reports() -> list[str]:
    failures = []
    for label, expected in EXPECTED_REPORT_SHORTCUTS.items():
        report = try_get_doc("Report", expected["report_name"])
        if not report:
            failures.append(f"Missing Report {expected['report_name']!r} for {label!r}")
            continue
        for key in ("report_name", "ref_doctype", "report_type", "module"):
            if report.get(key) != expected[key]:
                failures.append(
                    f"Report {expected['report_name']!r} {key} expected {expected[key]!r}, "
                    f"found {report.get(key)!r}"
                )
        if report.get("disabled"):
            failures.append(f"Report {expected['report_name']!r} is disabled")
    return failures


def check_accountant_default_workspace() -> list[str]:
    user = try_get_doc("User", ACCOUNTANT_TEMP_USER)
    if not user:
        return []
    if user.get("default_workspace") != ACCOUNTANT_HOME:
        return [
            f"{ACCOUNTANT_TEMP_USER} default workspace expected {ACCOUNTANT_HOME!r}, "
            f"found {user.get('default_workspace')!r}"
        ]
    return []


def check_report_execute() -> list[str]:
    failures = []
    try:
        result = bench_execute(
            "frappe.desk.query_report.run",
            kwargs={"report_name": "LT Customer Reminder Review", "filters": {}},
        )
    except Exception as exc:
        return [f"LT Customer Reminder Review execute failed: {exc}"]

    if not isinstance(result, dict):
        return [f"LT Customer Reminder Review execute returned {type(result).__name__}, expected report payload"]

    columns = result.get("columns") or []
    rows = result.get("result") or []
    fieldnames = {column.get("fieldname") for column in columns if isinstance(column, dict)}
    for fieldname in ("invoice", "customer_name", "recommended_cadence", "send_status", "blocked_customer_send_until"):
        if fieldname not in fieldnames:
            failures.append(f"LT Customer Reminder Review execute missing column {fieldname!r}")
    for row in rows or []:
        if row.get("delivery_mode") != "internal_review_only":
            failures.append(f"{row.get('invoice')} report row is not internal-review-only")
        if row.get("send_status") != "draft_only_not_sent":
            failures.append(f"{row.get('invoice')} report row is not draft-only")
        if row.get("customer_delivery_enabled") is not False:
            failures.append(f"{row.get('invoice')} report row enables customer delivery")
    return failures


def main() -> int:
    parse_noop_args(__doc__)
    failures = []
    try:
        failures.extend(check_workspace())
        failures.extend(check_number_cards())
        failures.extend(check_reports())
        failures.extend(check_accountant_default_workspace())
        failures.extend(check_report_execute())
    except Exception as exc:
        failures.append(str(exc))

    if failures:
        print("[FINANCE WORKSPACE PARITY] FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("[FINANCE WORKSPACE PARITY] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
