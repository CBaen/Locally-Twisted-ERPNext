"""No-live customer reminder dry-run queue.

This surface prepares internal reminder review items from existing draft
packets. It does not send email, create Communications, alter invoices, or
enable automatic customer delivery.
"""
from __future__ import annotations

from typing import Any

import frappe
from frappe.utils import now_datetime

from locally_twisted.paperwork import paperwork_review_digest, unpaid_invoice_draft_packet, unpaid_invoice_review


REMINDER_SURFACE = "customer_reminder_dry_run"
OPERATING_MODE = "no_live_internal_review"
MUTATION_GUARD_DOCTYPES = tuple(
    dict.fromkeys((*unpaid_invoice_review.MUTATION_GUARD_DOCTYPES, "Error Log"))
)
BASE_SEND_BLOCKERS = (
    "human_approval_recorded",
    "correct_recipient_confirmed",
    "invoice_status_rechecked",
    "cadence_approved",
    "copy_approved",
)


def run() -> dict[str, object]:
    """Return an internal-only reminder queue without mutating ERPNext."""
    before = _guard_counts()
    digest = paperwork_review_digest.run()
    draft_packets = unpaid_invoice_draft_packet.run()
    return build_from_sources(digest, draft_packets, guard_counts_before=before)


def build_from_sources(
    digest: dict[str, Any],
    draft_packets: dict[str, Any],
    *,
    guard_counts_before: dict[str, int] | None = None,
    guard_counts_after: dict[str, int] | None = None,
    generated_at: str | None = None,
) -> dict[str, object]:
    """Build dry-run queue items from digest and draft packet payloads."""
    before = guard_counts_before if guard_counts_before is not None else {}
    failures: list[str] = []

    failures.extend(_source_failures("paperwork_review_digest", digest, expected_type=("digest_type", "paperwork_review_digest")))
    failures.extend(_source_failures("unpaid_invoice_draft_packet", draft_packets, expected_type=("packet_type", "unpaid_invoice_draft_packet")))

    queue_items = [_queue_item(packet) for packet in draft_packets.get("packets") or []]
    failures.extend(_queue_failures(queue_items, draft_packets.get("packets") or []))

    if guard_counts_after is not None:
        after = guard_counts_after
    elif guard_counts_before is not None:
        after = _guard_counts()
    else:
        after = before

    if before != after:
        failures.append("mutation guard changed while building customer reminder dry run")

    digest_sections = digest.get("sections") or {}
    can_setup_without_live = [
        "Generate internal reminder review queue items.",
        "Render payment reminder and statement draft sections.",
        "Export JSON or Markdown review packets for Jeff/accounting.",
        "Run fake-data outlier contracts without live Stripe keys or real customer sends.",
        "Keep live cutover blockers visible without treating them as synthetic-readiness blockers.",
    ]
    live_or_approval_required = [
        "Customer email/SMS delivery.",
        "Automatic reminder cadence.",
        "Final recipient approval and copy approval.",
        "Live payment link/payment gateway cutover.",
        "Any invoice submit/cancel/write-off or accounting mutation.",
    ]

    return {
        "ok": not failures,
        "generated_at": generated_at or now_datetime().isoformat(),
        "read_only": True,
        "send_allowed": False,
        "mutation_allowed": False,
        "customer_delivery_enabled": False,
        "automatic_delivery_enabled": False,
        "live_inputs_required": False,
        "uses_real_customer_data_for_contract": False,
        "reminder_surface": REMINDER_SURFACE,
        "operating_mode": OPERATING_MODE,
        "source_surfaces": [
            "paperwork_review_digest",
            "unpaid_invoice_draft_packet",
        ],
        "summary": {
            "queue_item_count": len(queue_items),
            "ready_for_internal_review_count": len(queue_items),
            "blocked_customer_send_count": len(queue_items),
            "cutover_deferred_count": (digest_sections.get("cutover_deferred_not_blocking") or {}).get("count", 0),
            "setup_gap_count": (digest_sections.get("setup_gaps") or {}).get("count", 0),
        },
        "queue_items": queue_items,
        "sections": {
            "internal_review_queue": _section("internal_review_queue", "Internal reminder review queue", queue_items),
            "can_setup_without_live": _section("can_setup_without_live", "Can set up without going live", can_setup_without_live),
            "live_or_approval_required": _section("live_or_approval_required", "Still requires approval or live cutover", live_or_approval_required),
        },
        "mutation_guard": {
            "guarded_doctypes": list(MUTATION_GUARD_DOCTYPES),
            "before": before,
            "after": after,
            "changed": before != after,
        },
        "boundaries": {
            "no_email_queue": True,
            "no_communication": True,
            "no_payment_request": True,
            "no_payment_entry": True,
            "no_journal_entry": True,
            "no_invoice_submit_cancel": True,
            "no_error_log": True,
            "no_customer_send": True,
            "internal_review_only": True,
            "live_cutover_is_separate": True,
        },
        "failures": failures,
    }


def _queue_item(packet: dict[str, Any]) -> dict[str, Any]:
    sections = packet.get("sections") or []
    blockers = _send_blockers(packet, sections)
    recommended_document_ids = _recommended_document_ids(packet)
    return {
        "queue_id": f"customer-reminder-dry-run:{packet.get('invoice')}",
        "invoice": packet.get("invoice"),
        "customer": packet.get("customer"),
        "customer_name": packet.get("customer_name") or packet.get("customer"),
        "priority": packet.get("priority"),
        "days_overdue": int(packet.get("days_overdue") or 0),
        "balance_due": packet.get("balance_due"),
        "operating_mode": OPERATING_MODE,
        "delivery_mode": "internal_review_only",
        "send_status": "draft_only_not_sent",
        "customer_delivery_enabled": False,
        "automatic_delivery_enabled": False,
        "human_approval_required": packet.get("human_approval_required") is True,
        "review_gate": packet.get("review_gate"),
        "recommended_cadence": _recommended_cadence(packet),
        "recommended_document_ids": recommended_document_ids,
        "blocked_customer_send_until": blockers,
        "review_checklist": _review_checklist(packet),
        "draft_sections": [_draft_section(section) for section in sections if section.get("document_id") in recommended_document_ids],
    }


def _recommended_cadence(packet: dict[str, Any]) -> str:
    days_overdue = int(packet.get("days_overdue") or 0)
    if days_overdue >= 30:
        return "review_now_statement_and_payment_path"
    if days_overdue > 0:
        return "review_now_payment_reminder"
    return "hold_until_due_or_terms_review"


def _recommended_document_ids(packet: dict[str, Any]) -> list[str]:
    days_overdue = int(packet.get("days_overdue") or 0)
    if days_overdue >= 30:
        return ["statement_of_account", "payment_reminder_draft"]
    return ["payment_reminder_draft"]


def _send_blockers(packet: dict[str, Any], sections: list[dict[str, Any]]) -> list[str]:
    blockers = list(BASE_SEND_BLOCKERS)
    if _payment_path_missing(sections):
        blockers.append("payment_path_confirmed")
    if packet.get("human_approval_required") is not True:
        blockers.append("human_approval_required")
    if packet.get("send_status") != "draft_only_not_sent":
        blockers.append("draft_only_send_status_restored")
    return blockers


def _payment_path_missing(sections: list[dict[str, Any]]) -> bool:
    for section in sections:
        key_fields = section.get("key_fields_to_review") or {}
        payment_request = key_fields.get("payment_request")
        answer_first = str(section.get("answer_first") or "")
        if not payment_request or "not connected yet" in answer_first.lower():
            return True
    return False


def _review_checklist(packet: dict[str, Any]) -> list[str]:
    checklist = list(packet.get("internal_review_checklist") or [])
    for item in (
        "Record who approved the reminder before any future customer delivery.",
        "Keep this item internal-only until reminder cadence and copy are approved.",
    ):
        if item not in checklist:
            checklist.append(item)
    return checklist


def _draft_section(section: dict[str, Any]) -> dict[str, Any]:
    return {
        "document_id": section.get("document_id"),
        "title": section.get("title"),
        "send_status": section.get("send_status"),
        "subject": section.get("subject"),
        "answer_first": section.get("answer_first"),
        "body_preview": section.get("body_preview"),
        "key_fields_to_review": section.get("key_fields_to_review") or {},
    }


def _source_failures(
    source_name: str,
    payload: dict[str, Any],
    *,
    expected_type: tuple[str, str],
) -> list[str]:
    failures = []
    type_key, expected_value = expected_type
    if payload.get("ok") is not True:
        failures.extend(f"{source_name}: {failure}" for failure in payload.get("failures") or ["not ok"])
    if payload.get("read_only") is not True:
        failures.append(f"{source_name} is not marked read_only")
    if payload.get("send_allowed") is not False:
        failures.append(f"{source_name} allows customer sending")
    if payload.get("mutation_allowed") is not False:
        failures.append(f"{source_name} allows mutations")
    if payload.get(type_key) != expected_value:
        failures.append(f"{source_name} returned wrong {type_key}")
    if payload.get("mutation_guard", {}).get("changed"):
        failures.append(f"{source_name} mutation guard changed")
    return failures


def _queue_failures(queue_items: list[dict[str, Any]], packets: list[dict[str, Any]]) -> list[str]:
    failures = []
    for packet in packets:
        invoice = packet.get("invoice") or "<missing invoice>"
        if packet.get("send_status") != "draft_only_not_sent":
            failures.append(f"{invoice} source packet is not draft-only")
        if packet.get("human_approval_required") is not True:
            failures.append(f"{invoice} source packet does not require human approval")
        for section in packet.get("sections") or []:
            if section.get("send_status") != "draft_only_not_sent":
                failures.append(f"{invoice} {section.get('document_id')} section is not draft-only")
            if "human_approval" not in str(section.get("do_not_send_without") or ""):
                failures.append(f"{invoice} {section.get('document_id')} missing human approval gate")

    for item in queue_items:
        invoice = item.get("invoice") or "<missing invoice>"
        if item.get("delivery_mode") != "internal_review_only":
            failures.append(f"{invoice} queue item is not internal-review-only")
        if item.get("send_status") != "draft_only_not_sent":
            failures.append(f"{invoice} queue item is not draft-only")
        if item.get("customer_delivery_enabled") is not False:
            failures.append(f"{invoice} queue item enables customer delivery")
        if item.get("automatic_delivery_enabled") is not False:
            failures.append(f"{invoice} queue item enables automatic delivery")
        for blocker in BASE_SEND_BLOCKERS:
            if blocker not in (item.get("blocked_customer_send_until") or []):
                failures.append(f"{invoice} queue item missing blocker {blocker}")
    return failures


def _section(section_id: str, label: str, items: list[Any]) -> dict[str, Any]:
    return {
        "id": section_id,
        "label": label,
        "count": len(items),
        "items": items,
    }


def _guard_counts() -> dict[str, int]:
    return {
        doctype: int(frappe.db.count(doctype))
        for doctype in MUTATION_GUARD_DOCTYPES
        if frappe.db.exists("DocType", doctype)
    }
