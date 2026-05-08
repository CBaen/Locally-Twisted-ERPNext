"""Draft-only quote/proposal packet renderer.

This surface turns existing Quotation/Lead-style data into internal review
packets for the quote and proposal outbound document families. It does not
create PDFs, Email Queue rows, Communications, Sales Orders, Sales Invoices, or
Payment Requests.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

import frappe
from frappe.utils import now_datetime

from locally_twisted.outbound_documents.registry import OUTBOUND_DOCUMENTS
from locally_twisted.outbound_documents.send_readiness import evaluate_send_readiness


PACKET_TYPE = "quote_proposal_draft_packet"
SOURCE_REVIEW_SURFACE = "quotation_review"
EXPECTED_DOCUMENT_IDS = {"quote_estimate", "event_proposal_packet"}
MUTATION_GUARD_DOCTYPES = (
    "Quotation",
    "Lead",
    "Customer",
    "Sales Order",
    "Sales Invoice",
    "Payment Request",
    "Email Queue",
    "Communication",
    "File",
    "Comment",
    "Error Log",
)


def run(limit: int = 20) -> dict[str, object]:
    """Render draft-only quote/proposal packets from current Quotation rows."""
    before = _guard_counts()
    review = _quotation_review(limit=limit)
    return render_from_review(review, guard_counts_before=before)


def render_from_review(
    review: dict[str, Any],
    *,
    guard_counts_before: dict[str, int] | None = None,
    guard_counts_after: dict[str, int] | None = None,
    generated_at: str | None = None,
) -> dict[str, object]:
    before = guard_counts_before if guard_counts_before is not None else {}
    failures: list[str] = []

    failures.extend(_source_failures(review))
    packets = [_packet(candidate) for candidate in review.get("review_candidates") or []]

    if guard_counts_after is not None:
        after = guard_counts_after
    elif guard_counts_before is not None:
        after = _guard_counts()
    else:
        after = before

    if before != after:
        failures.append("mutation guard changed while rendering quote/proposal draft packets")

    failures.extend(_packet_shape_failures(packets))

    return {
        "ok": not failures,
        "generated_at": generated_at or now_datetime().isoformat(),
        "read_only": True,
        "send_allowed": False,
        "mutation_allowed": False,
        "customer_delivery_enabled": False,
        "automatic_delivery_enabled": False,
        "packet_type": PACKET_TYPE,
        "source_review_surface": review.get("review_surface") or SOURCE_REVIEW_SURFACE,
        "source_review_generated_at": review.get("generated_at"),
        "source_candidate_count": review.get("candidate_count", 0),
        "packet_count": len(packets),
        "packets": packets,
        "mutation_guard": {
            "guarded_doctypes": list(MUTATION_GUARD_DOCTYPES),
            "before": before,
            "after": after,
            "changed": before != after,
        },
        "boundaries": {
            "no_pdf_generation": True,
            "no_email_queue": True,
            "no_communication": True,
            "no_sales_order": True,
            "no_sales_invoice": True,
            "no_payment_request": True,
            "no_customer_send": True,
            "human_review_required": True,
            "draft_render_only": True,
        },
        "next_safe_action": (
            "Review scope, pricing, terms, recipient, and proof-photo use before building any PDF or sender."
        ),
        "failures": failures,
    }


def _quotation_review(limit: int) -> dict[str, Any]:
    candidates = []
    if frappe.db.exists("DocType", "Quotation"):
        rows = frappe.get_all(
            "Quotation",
            fields=[
                "name",
                "quotation_to",
                "party_name",
                "customer_name",
                "transaction_date",
                "valid_till",
                "grand_total",
                "currency",
                "status",
                "docstatus",
            ],
            order_by="modified desc",
            limit=limit,
        )
        candidates = [_candidate_from_quotation(row) for row in rows]

    return {
        "ok": True,
        "generated_at": now_datetime().isoformat(),
        "read_only": True,
        "send_allowed": False,
        "mutation_allowed": False,
        "review_surface": SOURCE_REVIEW_SURFACE,
        "candidate_count": len(candidates),
        "review_candidates": candidates,
    }


def _candidate_from_quotation(row: dict[str, Any]) -> dict[str, Any]:
    customer_name = row.get("customer_name") or row.get("party_name") or "Customer"
    event_date = _custom_or_default("Quotation", row.get("name"), ("custom_event_date", "valid_till"), row.get("valid_till"))
    event_location = _custom_or_default("Quotation", row.get("name"), ("custom_event_location", "custom_venue_address"), "")
    scope = _custom_or_default("Quotation", row.get("name"), ("custom_event_type", "custom_decor_scope"), "Review quoted event decor scope")
    proof_photos = _custom_or_default("Quotation", row.get("name"), ("custom_proof_photos",), "")
    approval_steps = "Human scope, pricing, terms, recipient, and photo-use review"
    total = _money(row.get("grand_total"), row.get("currency"))
    key_fields = {
        "quote_number": row.get("name"),
        "customer_name": customer_name,
        "event_date": event_date or "Review event date",
        "event_location": event_location or "Review event location",
        "scope": scope,
        "line_items": "Review Quotation item table",
        "assumptions": "Review delivery, install, teardown, weather, and venue assumptions",
        "subtotal": total,
        "taxes": "Review Quotation tax table",
        "total": total,
        "acceptance_path": "Human-reviewed quote acceptance path",
        "event_goal": scope,
        "client_context": customer_name,
        "proof_photos": proof_photos or "Photo use not approved yet",
        "proposed_scope": scope,
        "venue_assumptions": event_location or "Review venue assumptions",
        "investment": total,
        "approval_steps": approval_steps,
        "next_event_prompt": "Ask about repeat or annual event only after review",
        "recipient": _recipient_for_party(row.get("quotation_to"), row.get("party_name")),
        "company_branding": "Locally Twisted approved quote/proposal branding",
        "payment_terms": "Review payment terms before delivery",
    }
    return _candidate(
        source_doctype="Quotation",
        source_name=row.get("name"),
        customer_name=customer_name,
        status=row.get("status") or "Draft",
        key_fields=key_fields,
    )


def _candidate(
    *,
    source_doctype: str,
    source_name: str,
    customer_name: str,
    status: str,
    key_fields: dict[str, Any],
) -> dict[str, Any]:
    return {
        "source_doctype": source_doctype,
        "source_name": source_name,
        "customer_name": customer_name,
        "status": status,
        "priority": "proposal_review" if _wants_proposal(key_fields) else "quote_review",
        "draft_document_ids": ["quote_estimate", "event_proposal_packet"],
        "draft_documents": [
            _document("quote_estimate", key_fields),
            _document("event_proposal_packet", key_fields),
        ],
        "human_review": {
            "required": True,
            "send_status": "not_sent",
        },
    }


def _document(document_id: str, key_fields: dict[str, Any]) -> dict[str, Any]:
    spec = OUTBOUND_DOCUMENTS[document_id]
    readiness = evaluate_send_readiness(document_id, key_fields, [])
    return {
        "document_id": document_id,
        "title": spec.title,
        "audience": spec.audience,
        "delivery_channels": list(spec.delivery_channels),
        "review_gate": spec.review_gate,
        "do_not_send_without": "human_approval | correct_recipient | reviewed_scope | reviewed_pricing | approved_terms_language",
        "automation_ready": "generator_ready_review_required",
        "send_status": "draft_only_not_sent",
        "send_readiness": readiness,
        "key_fields_to_review": dict(key_fields),
    }


def _packet(candidate: dict[str, Any]) -> dict[str, Any]:
    sections = [_section(candidate, document) for document in candidate.get("draft_documents") or []]
    return {
        "source_doctype": candidate.get("source_doctype"),
        "source_name": candidate.get("source_name"),
        "customer_name": candidate.get("customer_name"),
        "status": candidate.get("status"),
        "priority": candidate.get("priority"),
        "send_status": "draft_only_not_sent",
        "human_approval_required": True,
        "review_gate": "Human approval of scope, pricing, recipient, terms, and proof-photo use",
        "sections": sections,
        "internal_review_checklist": [
            "Confirm event date, location, and onsite contact before sending.",
            "Confirm scope, line items, delivery/install/teardown assumptions, and price.",
            "Confirm payment terms and acceptance path.",
            "Confirm recipient and whether proof photos are approved for this customer.",
        ],
    }


def _section(candidate: dict[str, Any], document: dict[str, Any]) -> dict[str, Any]:
    document_id = document.get("document_id")
    key_fields = dict(document.get("key_fields_to_review") or {})
    if document_id == "quote_estimate":
        subject = f"Draft quote {key_fields.get('quote_number') or candidate.get('source_name')} - {key_fields.get('customer_name')}"
        answer_first = _quote_answer_first(key_fields)
        body_preview = _quote_body(key_fields)
    elif document_id == "event_proposal_packet":
        subject = f"Draft proposal packet - {key_fields.get('customer_name')}"
        answer_first = _proposal_answer_first(key_fields)
        body_preview = _proposal_body(key_fields)
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
        "send_readiness": document.get("send_readiness") or {},
        "subject": subject,
        "answer_first": answer_first,
        "body_preview": body_preview,
        "key_fields_to_review": key_fields,
        "source_doctype": candidate.get("source_doctype"),
        "source_name": candidate.get("source_name"),
    }


def _quote_answer_first(key_fields: dict[str, Any]) -> str:
    return (
        f"Quote {key_fields.get('quote_number')} for {key_fields.get('customer_name')} covers "
        f"{key_fields.get('scope')} on {key_fields.get('event_date')} at {key_fields.get('event_location')}; "
        f"reviewed total: {key_fields.get('total')}."
    )


def _quote_body(key_fields: dict[str, Any]) -> str:
    return (
        f"Event date: {key_fields.get('event_date')}\n"
        f"Location: {key_fields.get('event_location')}\n"
        f"Scope: {key_fields.get('scope')}\n"
        f"Assumptions: {key_fields.get('assumptions')}\n"
        f"Total: {key_fields.get('total')}\n"
        f"Acceptance path: {key_fields.get('acceptance_path')}\n\n"
        "This is a draft review packet. Confirm pricing, terms, and recipient before delivery."
    )


def _proposal_answer_first(key_fields: dict[str, Any]) -> str:
    return (
        f"Proposal packet for {key_fields.get('customer_name')}: goal is {key_fields.get('event_goal')}; "
        f"investment is {key_fields.get('investment')}; approval steps: {key_fields.get('approval_steps')}."
    )


def _proposal_body(key_fields: dict[str, Any]) -> str:
    return (
        f"Client context: {key_fields.get('client_context')}\n"
        f"Event goal: {key_fields.get('event_goal')}\n"
        f"Proposed scope: {key_fields.get('proposed_scope')}\n"
        f"Venue assumptions: {key_fields.get('venue_assumptions')}\n"
        f"Proof photos: {key_fields.get('proof_photos')}\n"
        f"Investment: {key_fields.get('investment')}\n\n"
        "This proposal is internal-only until proof photos, commercial terms, and recipient are approved."
    )


def _source_failures(review: dict[str, Any]) -> list[str]:
    failures = []
    if review.get("ok") is not True:
        failures.extend(review.get("failures") or ["quotation review returned not ok"])
    if review.get("read_only") is not True:
        failures.append("source quotation review is not marked read_only")
    if review.get("send_allowed") is not False:
        failures.append("source quotation review allows sending")
    if review.get("mutation_allowed") is not False:
        failures.append("source quotation review allows mutations")
    return failures


def _packet_shape_failures(packets: list[dict[str, Any]]) -> list[str]:
    failures = []
    for packet in packets:
        label = packet.get("source_name") or "<missing source>"
        if packet.get("send_status") != "draft_only_not_sent":
            failures.append(f"{label} packet is not draft-only")
        if packet.get("human_approval_required") is not True:
            failures.append(f"{label} packet does not require human approval")
        section_ids = {section.get("document_id") for section in packet.get("sections") or []}
        if section_ids != EXPECTED_DOCUMENT_IDS:
            failures.append(f"{label} packet sections are wrong: {sorted(section_ids)}")
        for section in packet.get("sections") or []:
            document_id = section.get("document_id") or "<missing document>"
            if section.get("send_status") != "draft_only_not_sent":
                failures.append(f"{label} {document_id} is not draft-only")
            readiness = section.get("send_readiness") or {}
            if readiness.get("send_ready") is True:
                failures.append(f"{label} {document_id} should not be send-ready before approvals")
            for key in ("subject", "answer_first", "body_preview", "key_fields_to_review"):
                if not section.get(key):
                    failures.append(f"{label} {document_id} missing {key}")
    return failures


def _guard_counts() -> dict[str, int]:
    return {
        doctype: int(frappe.db.count(doctype))
        for doctype in MUTATION_GUARD_DOCTYPES
        if frappe.db.exists("DocType", doctype)
    }


def _custom_or_default(doctype: str, name: str | None, fields: tuple[str, ...], default: Any) -> Any:
    if not name:
        return default
    for fieldname in fields:
        if frappe.db.has_column(doctype, fieldname):
            value = frappe.db.get_value(doctype, name, fieldname)
            if value:
                return value
    return default


def _recipient_for_party(quotation_to: Any, party_name: Any) -> str:
    if quotation_to == "Customer" and party_name:
        return "confirm linked customer contact before delivery"
    return "recipient must be confirmed"


def _wants_proposal(key_fields: dict[str, Any]) -> bool:
    text = " ".join(str(key_fields.get(key) or "") for key in ("scope", "event_goal", "proposed_scope")).lower()
    return any(word in text for word in ("corporate", "school", "sponsor", "proposal", "gala", "venue"))


def _money(value: Any, currency: Any) -> str:
    try:
        amount = Decimal(str(value or "0"))
    except (InvalidOperation, ValueError):
        amount = Decimal("0")
    return f"{currency or 'USD'} {amount:.2f}"
