"""Send-readiness gates for LT external documents.

This module does not send anything. It answers one question for future
generators and Desk queues: is this outbound document allowed to leave the
system, or which exact fields and approvals still block it?
"""
from __future__ import annotations

from typing import Any

from locally_twisted.communication_copy_policy import (
    BUSINESS_DOCUMENT_COPY,
    document_copy_recipients,
)
from locally_twisted.outbound_documents.registry import (
    OUTBOUND_DOCUMENTS,
    load_template,
    parse_frontmatter,
)


MISSING_VALUE_MARKERS = {
    "",
    "none",
    "null",
    "n/a",
    "na",
    "not connected yet",
    "pending",
    "tbd",
    "todo",
    "unknown",
}

UNIVERSAL_REQUIRED_FIELDS = (
    "recipient",
    "business_copy_recipient",
    "company_branding",
)

UNIVERSAL_APPROVAL_GATES = (
    "correct_recipient_confirmed",
    "copy_routing_confirmed",
    "company_branding_confirmed",
    "human_approval_recorded",
)

DOCUMENT_EXTRA_REQUIRED_FIELDS = {
    "sales_invoice": ("payment_terms", "payment_path", "corporate_bookkeeping_fields"),
    "payment_receipt": ("corporate_bookkeeping_fields",),
    "quote_estimate": ("payment_terms",),
    "event_proposal_packet": ("payment_terms",),
    "vendor_setup_w9_packet": ("secure_delivery_path",),
    "statement_of_account": ("payment_path", "corporate_bookkeeping_fields"),
    "payment_reminder_draft": ("payment_path", "corporate_bookkeeping_fields"),
    "event_install_work_order": ("crew_delivery_path",),
    "contract_acceptance_summary": ("payment_terms", "corporate_bookkeeping_fields"),
    "post_event_reorder_followup": ("contact_path",),
}


def evaluate_send_readiness(
    document_id: str,
    fields: dict[str, Any] | None = None,
    approvals: list[str] | tuple[str, ...] | set[str] | None = None,
    *,
    primary_doctype: str | None = None,
    primary_name: str | None = None,
    record_blocker: bool = False,
) -> dict[str, Any]:
    """Return a fail-loud send-readiness decision for one document family."""
    fields = dict(fields or {})
    approvals_set = set(approvals or [])
    failures: list[str] = []

    spec = OUTBOUND_DOCUMENTS.get(document_id)
    if not spec:
        return {
            "ok": False,
            "document_id": document_id,
            "send_ready": False,
            "send_allowed": False,
            "failures": [f"Unknown outbound document id: {document_id}"],
        }

    frontmatter, _body = parse_frontmatter(load_template(document_id))
    required_fields = _dedupe(
        [
            *_split_pipe(frontmatter.get("required_fields")),
            *UNIVERSAL_REQUIRED_FIELDS,
            *DOCUMENT_EXTRA_REQUIRED_FIELDS.get(document_id, ()),
        ]
    )
    required_approvals = _dedupe(
        [
            *_split_pipe(frontmatter.get("do_not_send_without")),
            *UNIVERSAL_APPROVAL_GATES,
        ]
    )

    missing_fields = [
        fieldname
        for fieldname in required_fields
        if not _has_value(fields.get(fieldname))
    ]
    missing_approvals = [
        gate
        for gate in required_approvals
        if gate not in approvals_set and not _truthy(fields.get(gate))
    ]
    blocked_send_until = [
        *[f"required_field:{fieldname}" for fieldname in missing_fields],
        *[f"approval_gate:{gate}" for gate in missing_approvals],
    ]

    evidence: dict[str, Any] | None = None
    if record_blocker and blocked_send_until:
        evidence = _record_readiness_blocker(
            document_id=document_id,
            primary_doctype=primary_doctype,
            primary_name=primary_name,
            blocked_send_until=blocked_send_until,
        )
        if evidence and evidence.get("ok") is not True:
            failures.extend(evidence.get("errors") or ["record-level send-readiness blocker failed"])

    send_ready = not failures and not blocked_send_until
    return {
        "ok": not failures,
        "document_id": document_id,
        "title": spec.title,
        "read_only": True,
        "send_ready": send_ready,
        "send_allowed": send_ready,
        "required_fields": required_fields,
        "required_approvals": required_approvals,
        "required_copy_recipients": document_copy_recipients(external_audience=True),
        "missing_required_fields": missing_fields,
        "missing_approval_gates": missing_approvals,
        "blocked_send_until": blocked_send_until,
        "record_blocker_requested": record_blocker,
        "record_blocker_evidence": evidence,
        "failures": failures,
    }


def complete_fake_fields(document_id: str) -> dict[str, Any]:
    """Return non-sensitive fake values that satisfy the readiness field list."""
    frontmatter, _body = parse_frontmatter(load_template(document_id))
    required_fields = _dedupe(
        [
            *_split_pipe(frontmatter.get("required_fields")),
            *UNIVERSAL_REQUIRED_FIELDS,
            *DOCUMENT_EXTRA_REQUIRED_FIELDS.get(document_id, ()),
        ]
    )
    return {fieldname: _fake_value(fieldname) for fieldname in required_fields}


def complete_fake_approvals(document_id: str) -> list[str]:
    frontmatter, _body = parse_frontmatter(load_template(document_id))
    return _dedupe(
        [
            *_split_pipe(frontmatter.get("do_not_send_without")),
            *UNIVERSAL_APPROVAL_GATES,
        ]
    )


def _record_readiness_blocker(
    *,
    document_id: str,
    primary_doctype: str | None,
    primary_name: str | None,
    blocked_send_until: list[str],
) -> dict[str, Any]:
    if not primary_doctype or not primary_name:
        return {
            "ok": False,
            "errors": ["record_blocker requested without primary_doctype and primary_name"],
        }

    from locally_twisted.failure_recorder import record_backend_failure

    return record_backend_failure(
        surface="outbound_document_send_readiness",
        step=f"{document_id}_send_readiness_blocked",
        severity="warning",
        primary_doctype=primary_doctype,
        primary_name=primary_name,
        customer_visible_impact="The external document was not sent because required send-readiness details are missing.",
        internal_next_action="Resolve before sending: " + ", ".join(blocked_send_until),
        exception="; ".join(blocked_send_until),
        grouping_key=f"outbound_document_send_readiness:{document_id}:{primary_doctype}:{primary_name}",
    )


def _split_pipe(value: str | None) -> list[str]:
    return [
        part.strip()
        for part in str(value or "").split("|")
        if part.strip()
    ]


def _dedupe(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def _has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    normalized = str(value).strip().lower()
    if normalized in MISSING_VALUE_MARKERS:
        return False
    return True


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "approved", "done", "confirmed"}


def _fake_value(fieldname: str) -> str:
    if fieldname == "business_copy_recipient":
        return BUSINESS_DOCUMENT_COPY
    if "date" in fieldname:
        return "2026-05-08"
    if "amount" in fieldname or "balance" in fieldname or "total" in fieldname or fieldname == "taxes":
        return "100.00"
    if "email" in fieldname or "contact" in fieldname or fieldname == "recipient":
        return "ap@example.invalid"
    if "path" in fieldname or "link" in fieldname:
        return "https://pay.example.invalid/lt-test"
    if "branding" in fieldname:
        return "Locally Twisted approved print/email branding"
    if "bookkeeping" in fieldname:
        return "PO/reference, category, tax, terms, total, balance, contact"
    return f"fake {fieldname}"
