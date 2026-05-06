"""Read-only paperwork and backend automation status for launch planning."""
from __future__ import annotations

import frappe
from frappe.utils import now_datetime, nowdate


def run() -> dict[str, object]:
    """Return JSON-safe paperwork status without mutating ERPNext."""
    live_payment = _live_payment_readiness()
    counts = _counts()
    setup_gaps = _setup_gaps(counts, live_payment)

    return {
        "ok": True,
        "generated_at": now_datetime().isoformat(),
        "read_only": True,
        "counts": counts,
        "invoice_review": _invoice_review(),
        "payment_request_review": _payment_request_review(),
        "email_queue_review": _email_queue_review(),
        "customer_document_policy": _customer_document_policy(),
        "automation_boundaries": {
            "crm_stage_finance": "Task-only today; no CRM stage creates Customers, Quotes, Sales Orders, Sales Invoices, Payment Requests, or Payment Entries.",
            "reminders": "Customer reminders are not approved for automatic sending.",
            "banking": "No bank sync or Plaid setup is approved for launch.",
            "payroll": "Payroll is feasibility-only until HRMS/payroll DocTypes and provider/accountant approval exist.",
        },
        "live_payment_readiness": live_payment,
        "attention_items": setup_gaps,
    }


def _counts() -> dict[str, int]:
    doctypes = [
        "Lead",
        "Contact",
        "Customer",
        "Sales Order",
        "Sales Invoice",
        "Payment Request",
        "Payment Entry",
        "Journal Entry",
        "Bank Account",
        "Bank Transaction",
        "Supplier",
        "Employee",
        "Email Queue",
        "Communication",
        "Payment Terms Template",
        "Payment Term",
    ]
    return {doctype: _count_if_present(doctype) for doctype in doctypes}


def _invoice_review() -> dict[str, object]:
    unpaid_filters = {"docstatus": 1, "outstanding_amount": [">", 0]}
    overdue_filters = {
        "docstatus": 1,
        "outstanding_amount": [">", 0],
        "due_date": ["<", nowdate()],
    }
    return {
        "unpaid_count": _count_if_present("Sales Invoice", unpaid_filters),
        "overdue_count": _count_if_present("Sales Invoice", overdue_filters),
        "unpaid": _safe_get_all(
            "Sales Invoice",
            filters=unpaid_filters,
            fields=[
                "name",
                "customer",
                "customer_name",
                "posting_date",
                "due_date",
                "status",
                "grand_total",
                "outstanding_amount",
            ],
            order_by="due_date asc, modified desc",
            limit_page_length=10,
        ),
    }


def _payment_request_review() -> dict[str, object]:
    expected_filters = {
        "payment_request_type": "Inward",
        "status": ["in", ["Initiated", "Requested"]],
    }
    paid_filters = {"payment_request_type": "Inward", "status": "Paid"}
    return {
        "expected_count": _count_if_present("Payment Request", expected_filters),
        "paid_count": _count_if_present("Payment Request", paid_filters),
        "expected": _safe_get_all(
            "Payment Request",
            filters=expected_filters,
            fields=[
                "name",
                "reference_doctype",
                "reference_name",
                "status",
                "grand_total",
                "outstanding_amount",
                "modified",
            ],
            order_by="modified desc",
            limit_page_length=10,
        ),
    }


def _email_queue_review() -> dict[str, object]:
    if not frappe.db.exists("DocType", "Email Queue"):
        return {"exists": False}

    status_counts = {}
    for row in frappe.db.sql(
        """
        select status, count(*) as count
        from `tabEmail Queue`
        group by status
        order by status asc
        """,
        as_dict=True,
    ):
        status_counts[row.status or "(blank)"] = int(row.count)

    return {
        "exists": True,
        "status_counts": status_counts,
        "recent": _safe_get_all(
            "Email Queue",
            fields=["name", "status", "reference_doctype", "reference_name", "creation", "modified"],
            order_by="creation desc",
            limit_page_length=10,
        ),
    }


def _customer_document_policy() -> dict[str, object]:
    from locally_twisted import policy_documents

    return {
        "lanes": {
            key: {
                "label": value["label"],
                "terms": value["terms"],
                "refund": value["refund"],
            }
            for key, value in policy_documents.POLICY_LANES.items()
        },
        "policy_blocks_are_code_owned": True,
        "erpnext_terms_records_required_today": False,
    }


def _live_payment_readiness() -> dict[str, object]:
    from locally_twisted.verify import payment_launch_readiness

    result = payment_launch_readiness.run(mode="live")
    return {
        "ok": bool(result.get("ok")),
        "failures": result.get("failures") or [],
        "warnings": result.get("warnings") or [],
        "stripe_mode": result.get("stripe_mode"),
        "stripe_settings_name": result.get("stripe_settings_name"),
        "payment_gateway_account": result.get("payment_gateway_account"),
        "webshop_checkout_enabled": result.get("webshop_checkout_enabled"),
        "operator_email": result.get("operator_email"),
        "webhook_secret_configured": result.get("webhook_secret_configured"),
        "outgoing_email_account": result.get("outgoing_email_account"),
    }


def _setup_gaps(counts: dict[str, int], live_payment: dict[str, object]) -> list[str]:
    gaps = []
    if counts.get("Bank Account", 0) == 0:
        gaps.append("No Bank Account records found; banking/reconciliation cannot be launch-ready.")
    if counts.get("Supplier", 0) == 0:
        gaps.append("No Supplier/vendor records found; contractor/1099 paperwork is not operational.")
    if counts.get("Employee", 0) == 0:
        gaps.append("No Employee records found; payroll is not operational.")
    missing_payroll = [
        doctype
        for doctype in ["Payroll Entry", "Salary Slip", "Salary Structure"]
        if not frappe.db.exists("DocType", doctype)
    ]
    if missing_payroll:
        gaps.append("Payroll DocTypes are missing: " + ", ".join(missing_payroll))
    company_default_bank = frappe.db.get_value("Company", "Locally Twisted", "default_bank_account")
    if not company_default_bank:
        gaps.append("Company default bank account is not set.")
    if not live_payment.get("ok"):
        gaps.append("Live payment readiness is blocked; see live_payment_readiness.failures.")
    return gaps


def _count_if_present(doctype: str, filters: dict | None = None) -> int:
    if not frappe.db.exists("DocType", doctype):
        return 0
    return int(frappe.db.count(doctype, filters=filters or {}))


def _safe_get_all(
    doctype: str,
    *,
    filters: dict | None = None,
    fields: list[str] | None = None,
    order_by: str | None = None,
    limit_page_length: int = 20,
) -> list[dict[str, object]]:
    if not frappe.db.exists("DocType", doctype):
        return []
    kwargs = {
        "doctype": doctype,
        "filters": filters or {},
        "fields": fields or ["name"],
        "limit_page_length": limit_page_length,
    }
    if order_by:
        kwargs["order_by"] = order_by
    return [dict(row) for row in frappe.get_all(**kwargs)]
