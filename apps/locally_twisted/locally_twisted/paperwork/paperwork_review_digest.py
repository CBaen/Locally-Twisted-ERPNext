"""Read-only internal paperwork review digest.

This digest is an internal review surface. It gathers existing verified reports
into one action-oriented payload, but it does not send email, create records, or
mutate accounting state.
"""
from __future__ import annotations

from typing import Any

import frappe
from frappe.utils import now_datetime

from locally_twisted.paperwork import unpaid_invoice_draft_packet, unpaid_invoice_review
from locally_twisted.verify import business_automation_index, paperwork_status


DIGEST_TYPE = "paperwork_review_digest"
SOURCE_SURFACES = (
    "paperwork_status",
    "business_automation_index",
    "unpaid_invoice_review",
    "unpaid_invoice_draft_packet",
)
MUTATION_GUARD_DOCTYPES = tuple(
    dict.fromkeys((*unpaid_invoice_review.MUTATION_GUARD_DOCTYPES, "Error Log"))
)


def run() -> dict[str, object]:
    """Return the internal paperwork review digest without mutating ERPNext."""
    before = _guard_counts()
    failures: list[str] = []

    status = paperwork_status.run()
    automation = business_automation_index.run(
        include_digest=False,
        include_synthetic=False,
        include_customer_reminders=False,
    )
    invoice_review = unpaid_invoice_review.run()
    draft_packets = unpaid_invoice_draft_packet.run()

    after = _guard_counts()
    if before != after:
        failures.append("mutation guard changed while rendering paperwork review digest")

    failures.extend(_source_failures("paperwork_status", status))
    failures.extend(_source_failures("business_automation_index", automation))
    failures.extend(_source_failures("unpaid_invoice_review", invoice_review))
    failures.extend(_source_failures("unpaid_invoice_draft_packet", draft_packets))

    sections = {
        "unpaid_invoice_packets": _section(
            "unpaid_invoice_packets",
            "Unpaid invoice packets",
            _unpaid_packet_items(draft_packets),
        ),
        "cutover_deferred_not_blocking": _section(
            "cutover_deferred_not_blocking",
            "Cutover deferred, not blocking synthetic readiness",
            _cutover_deferred_items(status),
        ),
        "setup_gaps": _section(
            "setup_gaps",
            "Setup gaps",
            status.get("attention_items") or [],
        ),
        "partial_connections": _section(
            "partial_connections",
            "Exists but not connected",
            _partial_connection_items(automation),
        ),
        "next_safe_actions": _section(
            "next_safe_actions",
            "Next safe actions",
            _next_safe_actions(status, automation, draft_packets),
        ),
    }

    failures.extend(_section_failures(sections))

    return {
        "ok": not failures,
        "generated_at": now_datetime().isoformat(),
        "read_only": True,
        "send_allowed": False,
        "mutation_allowed": False,
        "digest_type": DIGEST_TYPE,
        "source_surfaces": list(SOURCE_SURFACES),
        "sections": sections,
        "source_summaries": {
            "paperwork_status": {
                "ok": status.get("ok"),
                "counts": status.get("counts"),
            },
            "business_automation_index": {
                "ok": automation.get("ok"),
                "summary": automation.get("summary"),
            },
            "unpaid_invoice_review": {
                "ok": invoice_review.get("ok"),
                "candidate_count": invoice_review.get("candidate_count"),
                "priority_counts": invoice_review.get("priority_counts"),
            },
            "unpaid_invoice_draft_packet": {
                "ok": draft_packets.get("ok"),
                "packet_count": draft_packets.get("packet_count"),
            },
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
        },
        "failures": failures,
    }


def _source_failures(source_name: str, payload: dict[str, Any]) -> list[str]:
    failures = []
    if payload.get("ok") is not True:
        source_failures = payload.get("failures") or [f"{source_name} returned not ok"]
        failures.extend(f"{source_name}: {failure}" for failure in source_failures)
    if payload.get("read_only") is not True:
        failures.append(f"{source_name} is not marked read_only")
    if payload.get("send_allowed") is True:
        failures.append(f"{source_name} allows customer sending")
    if payload.get("mutation_allowed") is True:
        failures.append(f"{source_name} allows accounting mutations")
    if payload.get("mutation_guard", {}).get("changed"):
        failures.append(f"{source_name} mutation guard changed")
    return failures


def _section(
    section_id: str,
    label: str,
    items: list[Any],
) -> dict[str, Any]:
    return {
        "id": section_id,
        "label": label,
        "count": len(items),
        "items": items,
    }


def _unpaid_packet_items(draft_packets: dict[str, Any]) -> list[dict[str, Any]]:
    items = []
    for packet in draft_packets.get("packets") or []:
        items.append(
            {
                "invoice": packet.get("invoice"),
                "customer": packet.get("customer"),
                "customer_name": packet.get("customer_name"),
                "priority": packet.get("priority"),
                "days_overdue": packet.get("days_overdue"),
                "balance_due": packet.get("balance_due"),
                "send_status": packet.get("send_status"),
                "human_approval_required": packet.get("human_approval_required"),
                "review_gate": packet.get("review_gate"),
                "section_ids": [section.get("document_id") for section in packet.get("sections") or []],
                "internal_review_checklist": packet.get("internal_review_checklist") or [],
            }
        )
    return items


def _cutover_deferred_items(status: dict[str, Any]) -> list[dict[str, str]]:
    return [
        dict(item)
        for item in status.get("cutover_deferred_not_blocking") or []
    ]


def _partial_connection_items(automation: dict[str, Any]) -> list[dict[str, Any]]:
    items = []
    for row in automation.get("exists_but_not_connected") or []:
        items.append(
            {
                "id": row.get("id"),
                "lane": row.get("lane"),
                "summary": row.get("summary"),
                "future_connection": row.get("future_connection"),
                "verifiers": row.get("verifiers") or [],
            }
        )
    return items


def _next_safe_actions(
    status: dict[str, Any],
    automation: dict[str, Any],
    draft_packets: dict[str, Any],
) -> list[str]:
    actions = []
    if draft_packets.get("packet_count"):
        actions.append("Review unpaid invoice draft packets internally before any customer reminder or statement.")
    if status.get("attention_items"):
        actions.append("Resolve non-live setup gaps that affect operational readiness: bank account, supplier/vendor, and payroll.")
    if status.get("cutover_deferred_not_blocking"):
        actions.append("Keep live Stripe keys, webhook secrets, production host checks, and real operator/customer data out of synthetic pipeline work until cutover.")
    if automation.get("exists_but_not_connected"):
        actions.append("Keep partially connected surfaces visible; do not describe quote/proposal, vendor packet, bank reconciliation, or payroll paths as operational.")
    actions.append("Do not send reminders, submit accounting records, or wire CRM stages to finance without an explicit approval path.")
    return actions


def _section_failures(sections: dict[str, dict[str, Any]]) -> list[str]:
    failures = []
    for packet in sections["unpaid_invoice_packets"]["items"]:
        invoice = packet.get("invoice") or "<missing invoice>"
        if packet.get("send_status") != "draft_only_not_sent":
            failures.append(f"{invoice} packet is not draft-only")
        if packet.get("human_approval_required") is not True:
            failures.append(f"{invoice} packet does not require human approval")
        if set(packet.get("section_ids") or []) != {"payment_reminder_draft", "statement_of_account"}:
            failures.append(f"{invoice} packet section ids are wrong")
    return failures


def _guard_counts() -> dict[str, int]:
    return {
        doctype: int(frappe.db.count(doctype))
        for doctype in MUTATION_GUARD_DOCTYPES
        if frappe.db.exists("DocType", doctype)
    }
