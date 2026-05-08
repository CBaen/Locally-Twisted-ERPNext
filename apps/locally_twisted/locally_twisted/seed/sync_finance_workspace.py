"""Sync LT accountant finance workspace.

Run in-process:
  bench --site frontend execute locally_twisted.seed.sync_finance_workspace.execute
"""
from __future__ import annotations

import json

import frappe


ACCOUNTANT_HOME = "LT Accountant Home"
ACCOUNTANT_ROLE = "LT Accountant Access"
CUSTOMER_REMINDER_REPORT_NAME = "LT Customer Reminder Review"
CUSTOMER_REMINDER_REPORT_REF_DOCTYPE = "Sales Invoice"
CUSTOMER_REMINDER_REPORT_ROLES = [
    "LT Accountant Access",
    "Accounts Manager",
    "Accounts User",
    "System Manager",
]

ACCOUNTANT_NUMBER_CARDS = {
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

ACCOUNTANT_SHORTCUTS = [
    {"label": "Sales Invoices", "type": "DocType", "link_to": "Sales Invoice", "doc_view": "List", "color": "Blue"},
    {"label": "Payment Requests", "type": "DocType", "link_to": "Payment Request", "doc_view": "List", "color": "Green"},
    {"label": "Payments", "type": "DocType", "link_to": "Payment Entry", "doc_view": "List", "color": "Green"},
    {"label": "Customers", "type": "DocType", "link_to": "Customer", "doc_view": "List", "color": "Blue"},
    {"label": "Suppliers", "type": "DocType", "link_to": "Supplier", "doc_view": "List", "color": "Grey"},
    {"label": "Purchase Invoices", "type": "DocType", "link_to": "Purchase Invoice", "doc_view": "List", "color": "Yellow"},
    {"label": "Bank Transactions", "type": "DocType", "link_to": "Bank Transaction", "doc_view": "List", "color": "Green"},
    {"label": "Bank Accounts", "type": "DocType", "link_to": "Bank Account", "doc_view": "List", "color": "Green"},
    {"label": "Bank Reconciliation", "type": "URL", "url": "/app/bank-reconciliation-tool", "color": "Green"},
    {"label": "Journal Entries", "type": "DocType", "link_to": "Journal Entry", "doc_view": "List", "color": "Grey"},
    {"label": "Chart of Accounts", "type": "DocType", "link_to": "Account", "doc_view": "Tree", "color": "Grey"},
    {"label": "Payment Terms", "type": "DocType", "link_to": "Payment Terms Template", "doc_view": "List", "color": "Grey"},
    {
        "label": "Statement Reminders",
        "type": "DocType",
        "link_to": "Process Statement Of Accounts",
        "doc_view": "List",
        "color": "Orange",
    },
    {
        "label": "Reminder Review Report",
        "type": "Report",
        "link_to": CUSTOMER_REMINDER_REPORT_NAME,
        "report_ref_doctype": CUSTOMER_REMINDER_REPORT_REF_DOCTYPE,
        "color": "Orange",
    },
    {"label": "Employees", "type": "DocType", "link_to": "Employee", "doc_view": "List", "color": "Grey"},
]


def execute() -> str:
    summary = {
        "ensured_number_cards": [],
        "ensured_reports": [],
        "updated_workspace": False,
        "missing_roles": [],
    }
    for name, spec in ACCOUNTANT_NUMBER_CARDS.items():
        _ensure_number_card(name, spec, summary)
    _ensure_customer_reminder_report(summary)
    _ensure_accountant_workspace(summary)
    frappe.clear_cache()
    frappe.db.commit()
    print(json.dumps(summary, indent=2, sort_keys=True))
    return json.dumps(summary, sort_keys=True)


def _ensure_number_card(name: str, spec: dict, summary: dict) -> None:
    fields = {
        "is_standard": 0,
        "module": "Accounts",
        "label": spec["label"],
        "type": "Document Type",
        "function": spec["function"],
        "document_type": spec["document_type"],
        "is_public": 1,
        "show_percentage_stats": 0,
        "filters_json": json.dumps(spec["filters_json"]),
        "dynamic_filters_json": None,
        "aggregate_function_based_on": None,
    }

    if frappe.db.exists("Number Card", name):
        doc = frappe.get_doc("Number Card", name)
        changed = _set_fields(doc, fields)
        if changed:
            doc.save(ignore_permissions=True)
            summary["ensured_number_cards"].append(name)
        return

    doc = frappe.get_doc({"doctype": "Number Card", "name": name, **fields})
    doc.insert(ignore_permissions=True)
    summary["ensured_number_cards"].append(name)


def _ensure_customer_reminder_report(summary: dict) -> None:
    fields = {
        "report_name": CUSTOMER_REMINDER_REPORT_NAME,
        "ref_doctype": CUSTOMER_REMINDER_REPORT_REF_DOCTYPE,
        "is_standard": "Yes",
        "module": "Locally Twisted",
        "report_type": "Script Report",
        "disabled": 0,
        "prepared_report": 0,
        "add_total_row": 0,
    }

    if frappe.db.exists("Report", CUSTOMER_REMINDER_REPORT_NAME):
        doc = frappe.get_doc("Report", CUSTOMER_REMINDER_REPORT_NAME)
        is_new = False
        changed = False
    else:
        doc = frappe.get_doc({"doctype": "Report", "name": CUSTOMER_REMINDER_REPORT_NAME})
        is_new = True
        changed = True

    changed = _set_fields(doc, fields) or changed

    roles = []
    for role in CUSTOMER_REMINDER_REPORT_ROLES:
        if frappe.db.exists("Role", role):
            roles.append({"role": role})
        elif role not in summary["missing_roles"]:
            summary["missing_roles"].append(role)

    if _child_table_rows(doc.roles, ["role"]) != roles:
        doc.set("roles", [])
        for row in roles:
            doc.append("roles", row)
        changed = True

    if is_new:
        doc.insert(ignore_permissions=True)
        summary["ensured_reports"].append(CUSTOMER_REMINDER_REPORT_NAME)
    elif changed:
        doc.save(ignore_permissions=True)
        summary["ensured_reports"].append(CUSTOMER_REMINDER_REPORT_NAME)


def _ensure_accountant_workspace(summary: dict) -> None:
    if frappe.db.exists("Workspace", ACCOUNTANT_HOME):
        doc = frappe.get_doc("Workspace", ACCOUNTANT_HOME)
        changed = False
    else:
        doc = frappe.get_doc(
            {
                "doctype": "Workspace",
                "name": ACCOUNTANT_HOME,
                "label": ACCOUNTANT_HOME,
                "title": "Accountant Home",
                "module": "Accounts",
                "icon": "organization",
                "indicator_color": "green",
                "public": 1,
                "is_hidden": 0,
                "hide_custom": 1,
            }
        )
        doc.insert(ignore_permissions=True)
        changed = True

    fields = {
        "label": ACCOUNTANT_HOME,
        "title": "Accountant Home",
        "module": "Accounts",
        "icon": "organization",
        "indicator_color": "green",
        "public": 1,
        "is_hidden": 0,
        "hide_custom": 1,
    }
    changed = _set_fields(doc, fields) or changed
    changed = _ensure_role(doc, summary) or changed
    changed = _ensure_shortcuts(doc, ACCOUNTANT_SHORTCUTS) or changed

    number_cards = [
        {"number_card_name": name, "label": spec["label"]}
        for name, spec in ACCOUNTANT_NUMBER_CARDS.items()
    ]
    if _child_table_rows(doc.number_cards, ["number_card_name", "label"]) != number_cards:
        doc.set("number_cards", [])
        for row in number_cards:
            doc.append("number_cards", row)
        changed = True

    desired_content = _accountant_home_content()
    if _load_content(doc.content) != desired_content:
        doc.content = json.dumps(desired_content)
        changed = True

    if changed:
        doc.save(ignore_permissions=True)
        summary["updated_workspace"] = True


def _ensure_role(doc, summary: dict) -> bool:
    if not frappe.db.exists("Role", ACCOUNTANT_ROLE):
        summary["missing_roles"].append(ACCOUNTANT_ROLE)
        return False

    existing = {row.role for row in doc.roles}
    if ACCOUNTANT_ROLE in existing:
        return False
    doc.append("roles", {"role": ACCOUNTANT_ROLE})
    return True


def _ensure_shortcuts(doc, desired_shortcuts: list[dict]) -> bool:
    changed = False
    existing_by_label = {row.label: row for row in doc.shortcuts}

    for spec in desired_shortcuts:
        row = existing_by_label.get(spec["label"])
        if row is None:
            row = doc.append("shortcuts", {})
            changed = True
        for key in (
            "label",
            "type",
            "link_to",
            "url",
            "doc_view",
            "kanban_board",
            "color",
            "format",
            "report_ref_doctype",
        ):
            value = spec.get(key)
            if not _same_value(getattr(row, key, None), value):
                setattr(row, key, value)
                changed = True
    return changed


def _accountant_home_content() -> list[dict]:
    blocks = [
        _header(
            "lt-accountant-title",
            '<span class="h4"><b>Accountant Home</b></span>',
            12,
        ),
        _header(
            "lt-accountant-subtitle",
            '<span class="text-muted">Invoices, payments, bank reconciliation, payroll/vendor records, and accountant review exports.</span>',
            12,
        ),
    ]

    for idx, card_name in enumerate(ACCOUNTANT_NUMBER_CARDS, start=1):
        blocks.append(_number_card(f"lt-accountant-card-{idx}", card_name, 3))

    blocks.extend(
        [
            _spacer("lt-accountant-spacer-1"),
            _header(
                "lt-accountant-collect-title",
                '<span class="h4"><b>Money to collect</b></span>',
                12,
            ),
            _shortcut("lt-accountant-sales-invoices", "Sales Invoices", 3),
            _shortcut("lt-accountant-payment-requests", "Payment Requests", 3),
            _shortcut("lt-accountant-payments", "Payments", 3),
            _shortcut("lt-accountant-customers", "Customers", 3),
            _header(
                "lt-accountant-bank-title",
                '<span class="h4"><b>Banking and review</b></span>',
                12,
            ),
            _shortcut("lt-accountant-bank-transactions", "Bank Transactions", 3),
            _shortcut("lt-accountant-bank-accounts", "Bank Accounts", 3),
            _shortcut("lt-accountant-bank-reconciliation", "Bank Reconciliation", 3),
            _shortcut("lt-accountant-journal-entries", "Journal Entries", 3),
            _header(
                "lt-accountant-vendor-title",
                '<span class="h4"><b>Vendors and payroll records</b></span>',
                12,
            ),
            _shortcut("lt-accountant-suppliers", "Suppliers", 3),
            _shortcut("lt-accountant-purchase-invoices", "Purchase Invoices", 3),
            _shortcut("lt-accountant-employees", "Employees", 3),
            _shortcut("lt-accountant-payment-terms", "Payment Terms", 3),
            _header(
                "lt-accountant-reports-title",
                '<span class="h4"><b>Accounting setup and statements</b></span>',
                12,
            ),
            _shortcut("lt-accountant-chart-of-accounts", "Chart of Accounts", 3),
            _shortcut("lt-accountant-statement-reminders", "Statement Reminders", 3),
            _shortcut("lt-accountant-reminder-review-report", "Reminder Review Report", 3),
        ]
    )
    return blocks


def _set_fields(doc, fields: dict) -> bool:
    changed = False
    for key, value in fields.items():
        if not _same_value(getattr(doc, key, None), value):
            setattr(doc, key, value)
            changed = True
    return changed


def _same_value(current, desired) -> bool:
    if current in (None, "") and desired in (None, ""):
        return True
    return current == desired


def _child_table_rows(rows, fields: list[str]) -> list[dict]:
    return [{field: getattr(row, field, None) for field in fields} for row in rows]


def _header(block_id: str, text: str, col: int) -> dict:
    return {"id": block_id, "type": "header", "data": {"text": text, "col": col}}


def _shortcut(block_id: str, shortcut_name: str, col: int) -> dict:
    return {
        "id": block_id,
        "type": "shortcut",
        "data": {"shortcut_name": shortcut_name, "col": col},
    }


def _number_card(block_id: str, number_card_name: str, col: int) -> dict:
    return {
        "id": block_id,
        "type": "number_card",
        "data": {"number_card_name": number_card_name, "col": col},
    }


def _spacer(block_id: str) -> dict:
    return {"id": block_id, "type": "spacer", "data": {"col": 12}}


def _load_content(value: str | None) -> list[dict]:
    if not value:
        return []
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return []
    return parsed if isinstance(parsed, list) else []
