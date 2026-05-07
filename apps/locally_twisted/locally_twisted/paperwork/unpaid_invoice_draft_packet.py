"""Draft-only packet renderer for unpaid invoice review candidates.

This module is intentionally read-only. It turns the existing unpaid invoice
review surface into human-review packets, but it does not create Email Queue,
Communication, Payment Request, Payment Entry, Journal Entry, or invoice records.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any

import frappe
from frappe.utils import now_datetime

from locally_twisted.paperwork import unpaid_invoice_review


PACKET_TYPE = "unpaid_invoice_draft_packet"
SOURCE_REVIEW_SURFACE = "unpaid_invoice_review"
EXPECTED_DOCUMENT_IDS = {"payment_reminder_draft", "statement_of_account"}


def run() -> dict[str, object]:
    """Render unpaid invoice reminder/statement draft packets without mutations."""
    before = _guard_counts()
    review = unpaid_invoice_review.run()
    return render_from_review(review, guard_counts_before=before)


def render_from_review(
    review: dict[str, Any],
    *,
    guard_counts_before: dict[str, int] | None = None,
    guard_counts_after: dict[str, int] | None = None,
    generated_at: str | None = None,
) -> dict[str, object]:
    """Render packets from an unpaid invoice review payload.

    Kept separate from ``run`` so fake-data contracts can exercise normal and
    outlier packet behavior without creating ERPNext accounting records.
    """
    before = guard_counts_before if guard_counts_before is not None else {}
    failures: list[str] = []

    if not review.get("ok"):
        failures.extend(review.get("failures") or ["unpaid_invoice_review.run returned not ok"])
    if review.get("read_only") is not True:
        failures.append("source unpaid invoice review is not marked read_only")
    if review.get("send_allowed") is not False:
        failures.append("source unpaid invoice review allows sending")
    if review.get("mutation_allowed") is not False:
        failures.append("source unpaid invoice review allows mutations")

    packets = [_packet(candidate) for candidate in review.get("review_candidates") or []]

    if guard_counts_after is not None:
        after = guard_counts_after
    elif guard_counts_before is not None:
        after = _guard_counts()
    else:
        after = before

    if before != after:
        failures.append("mutation guard changed while rendering unpaid invoice draft packets")

    if not _all_packets_are_draft_only(packets):
        failures.append("one or more unpaid invoice packets are not marked draft-only")
    failures.extend(_packet_shape_failures(packets))

    return {
        "ok": not failures,
        "generated_at": generated_at or now_datetime().isoformat(),
        "read_only": True,
        "send_allowed": False,
        "mutation_allowed": False,
        "packet_type": PACKET_TYPE,
        "source_review_surface": SOURCE_REVIEW_SURFACE,
        "source_review_generated_at": review.get("generated_at"),
        "source_candidate_count": review.get("candidate_count", 0),
        "packet_count": len(packets),
        "packets": packets,
        "mutation_guard": {
            "guarded_doctypes": list(unpaid_invoice_review.MUTATION_GUARD_DOCTYPES),
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
            "draft_render_only": True,
        },
        "next_safe_action": (
            "Review packet copy and recipient/cadence rules, then decide whether Jeff/accounting wants an in-Desk "
            "review queue or a scheduled draft report."
        ),
        "failures": failures,
    }


def _packet(candidate: dict[str, Any]) -> dict[str, Any]:
    sections = [_section(candidate, document) for document in candidate.get("draft_documents") or []]
    return {
        "invoice": candidate.get("invoice"),
        "customer": candidate.get("customer"),
        "customer_name": candidate.get("customer_name") or candidate.get("customer"),
        "priority": candidate.get("priority"),
        "days_overdue": candidate.get("days_overdue", 0),
        "balance_due": candidate.get("balance_due"),
        "send_status": "draft_only_not_sent",
        "human_approval_required": True,
        "review_gate": "Human approval of invoice status, recipient, cadence, balance, and copy",
        "sections": sections,
        "internal_review_checklist": [
            "Confirm the invoice is still unpaid before anything is sent.",
            "Confirm the recipient is the right accounts-payable or customer accounting contact.",
            "Confirm the cadence is appropriate and there is no recent payment or reconciliation dispute.",
            "Confirm the payment link or reply path is correct before anything is sent.",
        ],
    }


def _section(candidate: dict[str, Any], document: dict[str, Any]) -> dict[str, Any]:
    document_id = document.get("document_id")
    key_fields = dict(document.get("key_fields_to_review") or {})
    if document_id == "payment_reminder_draft":
        subject = f"Locally Twisted invoice {key_fields.get('invoice_number')} - balance {key_fields.get('balance_due')}"
        answer_first = _payment_reminder_answer_first(key_fields)
        body_preview = _payment_reminder_body(key_fields)
    elif document_id == "statement_of_account":
        subject = f"Locally Twisted account statement - {key_fields.get('customer_name')}"
        answer_first = _statement_answer_first(key_fields)
        body_preview = _statement_body(key_fields)
    else:
        subject = f"Locally Twisted review draft - {document.get('title') or document_id}"
        answer_first = "Review the generated packet before any delivery."
        body_preview = "This document type is registered but does not have specialized packet copy yet."

    return {
        "document_id": document_id,
        "title": document.get("title"),
        "audience": document.get("audience"),
        "delivery_channels": document.get("delivery_channels") or [],
        "review_gate": document.get("review_gate"),
        "do_not_send_without": document.get("do_not_send_without"),
        "automation_ready": document.get("automation_ready"),
        "send_status": "draft_only_not_sent",
        "subject": subject,
        "answer_first": answer_first,
        "body_preview": body_preview,
        "key_fields_to_review": key_fields,
        "source_invoice": candidate.get("invoice"),
    }


def _payment_reminder_answer_first(key_fields: dict[str, Any]) -> str:
    return (
        f"Invoice {key_fields.get('invoice_number')} shows a balance of "
        f"{_money_label(key_fields.get('balance_due'), key_fields.get('currency'))}, "
        f"due {key_fields.get('due_date')}. Payment reference: {key_fields.get('payment_request') or 'not connected yet'}."
    )


def _payment_reminder_body(key_fields: dict[str, Any]) -> str:
    return (
        f"Hello {key_fields.get('customer_name')},\n\n"
        f"Our records show invoice {key_fields.get('invoice_number')} is still open with a balance of "
        f"{_money_label(key_fields.get('balance_due'), key_fields.get('currency'))}. "
        f"If payment has already been sent, reply with the payment reference and we will reconcile it. "
        f"If you need a copy of the invoice or vendor details, reply to this message and we will send the right paperwork.\n\n"
        "Thank you,\nLocally Twisted"
    )


def _statement_answer_first(key_fields: dict[str, Any]) -> str:
    return (
        f"{key_fields.get('customer_name')} has {key_fields.get('open_invoice_count_for_customer')} open invoice(s) "
        f"with a total open balance of {_money_label(key_fields.get('total_open_balance_for_customer'), key_fields.get('currency'))}."
    )


def _statement_body(key_fields: dict[str, Any]) -> str:
    return (
        f"Statement date: {now_datetime().date().isoformat()}\n"
        f"Customer: {key_fields.get('customer_name')}\n"
        f"Open invoice count: {key_fields.get('open_invoice_count_for_customer')}\n"
        f"Total open balance: {_money_label(key_fields.get('total_open_balance_for_customer'), key_fields.get('currency'))}\n\n"
        f"Primary invoice in this review packet: {key_fields.get('invoice_number')}\n"
        f"Invoice date: {key_fields.get('invoice_date')}\n"
        f"Due date: {key_fields.get('due_date')}\n"
        f"Balance due: {_money_label(key_fields.get('balance_due'), key_fields.get('currency'))}\n\n"
        "This draft is for reconciliation review. It should not be treated as a collections demand."
    )


def _money_label(value: Any, currency: Any) -> str:
    amount = Decimal(str(value or "0"))
    return f"{currency or 'USD'} {amount:.2f}"


def _guard_counts() -> dict[str, int]:
    return {
        doctype: int(frappe.db.count(doctype))
        for doctype in unpaid_invoice_review.MUTATION_GUARD_DOCTYPES
        if frappe.db.exists("DocType", doctype)
    }


def _all_packets_are_draft_only(packets: list[dict[str, Any]]) -> bool:
    for packet in packets:
        if packet.get("send_status") != "draft_only_not_sent":
            return False
        if packet.get("human_approval_required") is not True:
            return False
        for section in packet.get("sections") or []:
            if section.get("send_status") != "draft_only_not_sent":
                return False
            if "human_approval" not in str(section.get("do_not_send_without") or ""):
                return False
    return True


def _packet_shape_failures(packets: list[dict[str, Any]]) -> list[str]:
    failures = []
    for packet in packets:
        invoice = packet.get("invoice") or "<missing invoice>"
        section_ids = {section.get("document_id") for section in packet.get("sections") or []}
        if section_ids != EXPECTED_DOCUMENT_IDS:
            failures.append(f"{invoice} packet sections are wrong: {sorted(section_ids)}")
        for section in packet.get("sections") or []:
            document_id = section.get("document_id") or "<missing document>"
            for key in ("subject", "answer_first", "body_preview", "key_fields_to_review"):
                if not section.get(key):
                    failures.append(f"{invoice} {document_id} missing {key}")
    return failures
