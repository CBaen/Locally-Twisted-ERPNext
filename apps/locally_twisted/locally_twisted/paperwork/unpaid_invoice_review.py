"""Draft-only unpaid invoice review surface.

This module creates visibility for unpaid or overdue invoices. It does not send
email, create reminders, submit accounting records, or mutate live records.
"""
from __future__ import annotations

from collections import Counter
from decimal import Decimal
from typing import Any

import frappe
from frappe.utils import date_diff, getdate, now_datetime, nowdate

from locally_twisted.outbound_documents.registry import (
    OUTBOUND_DOCUMENTS,
    load_template,
    parse_frontmatter,
)


DRAFT_DOCUMENT_IDS = ("payment_reminder_draft", "statement_of_account")
MUTATION_GUARD_DOCTYPES = (
    "Email Queue",
    "Communication",
    "Sales Invoice",
    "Payment Request",
    "Payment Entry",
    "Journal Entry",
)


def run() -> dict[str, object]:
    """Return review candidates for unpaid invoices without mutating live records."""
    before = _guard_counts()
    failures: list[str] = []

    template_meta = _template_meta(failures)
    rows = _open_invoices()
    candidates = [_candidate(row, template_meta) for row in rows]

    after = _guard_counts()
    if before != after:
        failures.append("mutation guard changed while building unpaid invoice review")

    if not _all_candidates_are_draft_only(candidates):
        failures.append("one or more candidates are not marked draft-only")

    priority_counts = dict(Counter(candidate["priority"] for candidate in candidates))

    return {
        "ok": not failures,
        "generated_at": now_datetime().isoformat(),
        "read_only": True,
        "send_allowed": False,
        "mutation_allowed": False,
        "review_surface": "unpaid_invoice_review",
        "source": "Sales Invoice unpaid/overdue rows plus outbound document registry",
        "template_ids": list(DRAFT_DOCUMENT_IDS),
        "review_candidates": candidates,
        "candidate_count": len(candidates),
        "priority_counts": priority_counts,
        "mutation_guard": {
            "guarded_doctypes": list(MUTATION_GUARD_DOCTYPES),
            "before": before,
            "after": after,
            "changed": before != after,
        },
        "boundaries": {
            "no_email_queue": True,
            "no_communication": True,
            "no_payment_entry": True,
            "no_journal_entry": True,
            "no_invoice_submit_cancel": True,
            "no_customer_send": True,
            "human_review_required": True,
        },
        "next_safe_action": "Review candidates, confirm recipient/cadence/copy, then build a draft-only Desk queue if Jeff/accounting wants an in-Desk surface.",
        "failures": failures,
    }


def _open_invoices() -> list[dict[str, Any]]:
    if not frappe.db.exists("DocType", "Sales Invoice"):
        return []
    rows = frappe.get_all(
        "Sales Invoice",
        filters={"docstatus": 1, "outstanding_amount": [">", 0]},
        fields=[
            "name",
            "customer",
            "customer_name",
            "posting_date",
            "due_date",
            "status",
            "grand_total",
            "outstanding_amount",
            "currency",
            "contact_person",
            "po_no",
            "payment_terms_template",
        ],
        order_by="due_date asc, modified desc",
        limit_page_length=100,
    )
    return [dict(row) for row in rows]


def _candidate(invoice: dict[str, Any], template_meta: dict[str, dict[str, Any]]) -> dict[str, Any]:
    today = getdate(nowdate())
    due_date = invoice.get("due_date")
    days_overdue = max(date_diff(today, getdate(due_date)), 0) if due_date else 0
    priority = "overdue_review" if days_overdue > 0 else "unpaid_review"
    customer = invoice.get("customer")
    open_invoices = _open_invoices_for_customer(customer)
    payment_request = _payment_request_for_invoice(invoice.get("name"))

    key_fields = {
        "invoice_number": invoice.get("name"),
        "customer": customer,
        "customer_name": invoice.get("customer_name") or customer,
        "invoice_date": _stringify(invoice.get("posting_date")),
        "due_date": _stringify(due_date) if due_date else "Due on receipt or per approved terms",
        "days_overdue": days_overdue,
        "balance_due": _money(invoice.get("outstanding_amount")),
        "invoice_total": _money(invoice.get("grand_total")),
        "currency": invoice.get("currency") or "USD",
        "po_reference": invoice.get("po_no") or invoice.get("name"),
        "payment_terms": invoice.get("payment_terms_template") or "Review terms on invoice",
        "payment_request": payment_request,
        "open_invoice_count_for_customer": len(open_invoices),
        "total_open_balance_for_customer": _money(sum(_decimal(row.get("outstanding_amount")) for row in open_invoices)),
        "review_reason": "Invoice is overdue" if priority == "overdue_review" else "Invoice is unpaid",
    }

    return {
        "invoice": invoice.get("name"),
        "customer": customer,
        "customer_name": invoice.get("customer_name") or customer,
        "status": invoice.get("status"),
        "priority": priority,
        "days_overdue": days_overdue,
        "balance_due": key_fields["balance_due"],
        "draft_document_ids": list(DRAFT_DOCUMENT_IDS),
        "draft_documents": [
            _draft_document("payment_reminder_draft", key_fields, template_meta),
            _draft_document("statement_of_account", key_fields, template_meta),
        ],
        "human_review": {
            "required": True,
            "check_recipient": True,
            "check_invoice_status": True,
            "check_cadence": True,
            "check_copy": True,
            "send_status": "not_sent",
        },
        "next_action": "Confirm invoice status, recipient, and cadence before creating or sending any reminder.",
    }


def _draft_document(
    document_id: str,
    key_fields: dict[str, Any],
    template_meta: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    spec = OUTBOUND_DOCUMENTS[document_id]
    meta = template_meta.get(document_id, {})
    return {
        "document_id": document_id,
        "title": spec.title,
        "template_name": spec.template_name,
        "audience": spec.audience,
        "delivery_channels": list(spec.delivery_channels),
        "review_gate": spec.review_gate,
        "do_not_send_without": meta.get("do_not_send_without", ""),
        "automation_ready": meta.get("automation_ready", ""),
        "send_status": "draft_only_not_sent",
        "key_fields_to_review": key_fields,
        "draft_subject": _draft_subject(document_id, key_fields),
    }


def _draft_subject(document_id: str, key_fields: dict[str, Any]) -> str:
    if document_id == "payment_reminder_draft":
        return f"Draft only: payment review for invoice {key_fields['invoice_number']}"
    return f"Draft only: statement review for {key_fields['customer_name']}"


def _template_meta(failures: list[str]) -> dict[str, dict[str, Any]]:
    meta = {}
    for document_id in DRAFT_DOCUMENT_IDS:
        spec = OUTBOUND_DOCUMENTS.get(document_id)
        if not spec:
            failures.append(f"missing outbound document spec {document_id}")
            continue
        frontmatter, body = parse_frontmatter(load_template(document_id))
        meta[document_id] = frontmatter
        if "human_approval" not in frontmatter.get("do_not_send_without", ""):
            failures.append(f"{document_id} does not require human approval before send")
        if "## Answer First" not in body:
            failures.append(f"{document_id} template missing Answer First section")
        delivery = frontmatter.get("delivery_channel", "")
        if "draft" not in delivery.lower() and "reviewed" not in delivery.lower():
            failures.append(f"{document_id} delivery channel is not draft/review gated")
    return meta


def _open_invoices_for_customer(customer: str | None) -> list[dict[str, Any]]:
    if not customer or not frappe.db.exists("DocType", "Sales Invoice"):
        return []
    rows = frappe.get_all(
        "Sales Invoice",
        filters={"docstatus": 1, "customer": customer, "outstanding_amount": [">", 0]},
        fields=["name", "posting_date", "due_date", "grand_total", "outstanding_amount", "currency"],
        order_by="due_date asc, modified desc",
        limit_page_length=100,
    )
    return [dict(row) for row in rows]


def _payment_request_for_invoice(invoice_name: str | None) -> str | None:
    if not invoice_name or not frappe.db.exists("DocType", "Payment Request"):
        return None
    return frappe.db.get_value(
        "Payment Request",
        {
            "payment_request_type": "Inward",
            "reference_doctype": "Sales Invoice",
            "reference_name": invoice_name,
            "status": ["!=", "Cancelled"],
        },
        "name",
    )


def _guard_counts() -> dict[str, int]:
    return {
        doctype: int(frappe.db.count(doctype))
        for doctype in MUTATION_GUARD_DOCTYPES
        if frappe.db.exists("DocType", doctype)
    }


def _all_candidates_are_draft_only(candidates: list[dict[str, Any]]) -> bool:
    for candidate in candidates:
        if not candidate.get("human_review", {}).get("required"):
            return False
        for document in candidate.get("draft_documents") or []:
            if document.get("send_status") != "draft_only_not_sent":
                return False
    return True


def _money(value: Any) -> str:
    amount = _decimal(value)
    return f"{amount:.2f}"


def _decimal(value: Any) -> Decimal:
    if value is None:
        return Decimal("0")
    return Decimal(str(value))


def _stringify(value: Any) -> str:
    return value.isoformat() if hasattr(value, "isoformat") else str(value)
