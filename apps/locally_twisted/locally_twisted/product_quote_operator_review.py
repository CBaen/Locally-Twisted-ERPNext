"""Internal review evaluator for product-page quote Quotations.

This module is read-only. It does not send quotes, create Sales Orders, create
Invoices, create Payment Requests, or imply customer acceptance.
"""
from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from typing import Any

import frappe
from frappe.utils import now_datetime

from locally_twisted.product_page_runtime import CONFIG_VERSION, LINE_FIELDNAMES
from locally_twisted.product_quote_runtime import PRODUCT_QUOTE_REVIEW_ITEM, QUOTATION_FIELDNAMES


REVIEW_SURFACE = "product_quote_operator_review"
STATUS_BLOCKED = "Needs Operator Review"
STATUS_READY = "Ready For Customer Review"
MUTATION_GUARD_DOCTYPES = (
    "Quotation",
    "Lead",
    "Customer",
    "Sales Order",
    "Sales Invoice",
    "Payment Request",
    "Email Queue",
    "Communication",
    "Comment",
    "Error Log",
)


def run(limit: int = 20) -> dict[str, object]:
    """Return live product-page quote review rows without mutating records."""
    before = _guard_counts()
    quotations = _live_product_quote_quotations(limit=limit)
    return render_from_quotations(quotations, guard_counts_before=before)


def render_from_quotations(
    quotations: list[Any],
    *,
    guard_counts_before: dict[str, int] | None = None,
    guard_counts_after: dict[str, int] | None = None,
    generated_at: str | None = None,
) -> dict[str, object]:
    before = guard_counts_before if guard_counts_before is not None else {}
    reviews = [evaluate_product_quote_quotation(quotation) for quotation in quotations]
    after = (
        guard_counts_after
        if guard_counts_after is not None
        else _guard_counts()
        if guard_counts_before is not None
        else before
    )
    failures = []
    if before != after:
        failures.append("mutation guard changed while rendering product quote operator review")

    return {
        "ok": not failures,
        "generated_at": generated_at or now_datetime().isoformat(),
        "read_only": True,
        "send_allowed": False,
        "customer_delivery_enabled": False,
        "sales_order_creation_allowed": False,
        "invoice_creation_allowed": False,
        "payment_request_allowed": False,
        "review_surface": REVIEW_SURFACE,
        "review_count": len(reviews),
        "ready_count": sum(1 for review in reviews if review["ready_for_customer_review"]),
        "blocked_count": sum(1 for review in reviews if not review["ready_for_customer_review"]),
        "reviews": reviews,
        "mutation_guard": {
            "guarded_doctypes": list(MUTATION_GUARD_DOCTYPES),
            "before": before,
            "after": after,
            "changed": before != after,
        },
        "failures": failures,
    }


def evaluate_product_quote_quotation(quotation: Any) -> dict[str, object]:
    """Return one operator review row for a product-page quote Quotation."""
    payload, payload_failures = _product_quote_payload(quotation)
    items = list(_get(quotation, "items") or [])
    blockers = []
    blockers.extend(payload_failures)

    if int(_get(quotation, "docstatus") or 0) != 0:
        blockers.append("blocked_state:quotation_must_be_draft_for_operator_review")
    if _has_placeholder_review_line(items):
        blockers.append("replace_placeholder_review_line_with_real_scope_and_pricing")
    if _money_is_zero(_get(quotation, "grand_total")) or _has_zero_priced_non_note_line(items):
        blockers.append("required_field:reviewed_product_quote_pricing")
    if not _recipient(quotation):
        blockers.append("required_field:recipient")
    if not _get(quotation, "valid_till"):
        blockers.append("required_field:valid_till")
    if not _terms_or_acceptance_path(quotation):
        blockers.append("required_field:terms_and_acceptance_path")
    if not _event_context(quotation, payload):
        blockers.append("required_field:event_context")

    blockers = _dedupe(blockers)
    ready = not blockers
    return {
        "quotation": _get(quotation, "name"),
        "source_lead": _get(quotation, QUOTATION_FIELDNAMES["source_lead"]),
        "customer_name": _get(quotation, "customer_name") or _get(quotation, "party_name") or "Customer",
        "status": STATUS_READY if ready else STATUS_BLOCKED,
        "ready_for_customer_review": ready,
        "send_allowed": False,
        "customer_delivery_enabled": False,
        "sales_order_creation_allowed": False,
        "payment_request_allowed": False,
        "blockers": blockers,
        "requested_product_page": payload.get("website_item_code") if payload else _get(quotation, QUOTATION_FIELDNAMES["template_item"]),
        "product_page_type": payload.get("product_page_type") if payload else _get(quotation, QUOTATION_FIELDNAMES["page_type"]),
        "quote_summary": payload.get("summary") if payload else _get(quotation, QUOTATION_FIELDNAMES["summary"]),
        "operator_next_action": _next_action(blockers),
    }


def _live_product_quote_quotations(limit: int) -> list[Any]:
    if not frappe.db.exists("DocType", "Quotation"):
        return []
    meta = frappe.get_meta("Quotation")
    source_field = QUOTATION_FIELDNAMES["source_lead"]
    if not meta.has_field(source_field):
        return []
    names = frappe.get_all(
        "Quotation",
        filters={source_field: ("is", "set")},
        fields=["name"],
        order_by="modified desc",
        limit=limit,
    )
    return [frappe.get_doc("Quotation", row["name"]) for row in names]


def _product_quote_payload(quotation: Any) -> tuple[dict[str, Any], list[str]]:
    raw = _get(quotation, QUOTATION_FIELDNAMES["json"])
    if not raw:
        for item in _get(quotation, "items") or []:
            raw = _get(item, LINE_FIELDNAMES["json"])
            if raw:
                break
    if not raw:
        return {}, ["malformed_product_quote_payload:missing"]
    try:
        payload = json.loads(raw) if isinstance(raw, str) else raw
    except (TypeError, ValueError):
        return {}, ["malformed_product_quote_payload:unreadable_json"]
    if not isinstance(payload, dict):
        return {}, ["malformed_product_quote_payload:not_object"]
    if payload.get("schema_version") != CONFIG_VERSION:
        return payload, ["malformed_product_quote_payload:wrong_schema_version"]
    if not payload.get("website_item_code"):
        return payload, ["malformed_product_quote_payload:missing_requested_product"]
    return payload, []


def _has_placeholder_review_line(items: list[Any]) -> bool:
    return any(_get(item, "item_code") == PRODUCT_QUOTE_REVIEW_ITEM for item in items)


def _has_zero_priced_non_note_line(items: list[Any]) -> bool:
    for item in items:
        if _get(item, "item_code") == PRODUCT_QUOTE_REVIEW_ITEM:
            continue
        if _money_is_zero(_get(item, "rate")) and _money_is_zero(_get(item, "amount")):
            return True
    return False


def _money_is_zero(value: Any) -> bool:
    try:
        return Decimal(str(value or "0")) == 0
    except (InvalidOperation, ValueError):
        return True


def _recipient(quotation: Any) -> str:
    for fieldname in ("contact_email", "email_id", "customer_email", "recipient"):
        value = str(_get(quotation, fieldname) or "").strip()
        if value:
            return value
    quotation_to = _get(quotation, "quotation_to")
    party_name = _get(quotation, "party_name")
    if quotation_to == "Lead" and party_name and frappe.db.exists("Lead", party_name):
        return str(frappe.db.get_value("Lead", party_name, "email_id") or "").strip()
    if quotation_to == "Customer" and party_name:
        rows = frappe.get_all(
            "Dynamic Link",
            filters={"link_doctype": "Customer", "link_name": party_name, "parenttype": "Contact"},
            fields=["parent"],
            limit=1,
        )
        if rows:
            return str(frappe.db.get_value("Contact", rows[0]["parent"], "email_id") or "").strip()
    return ""


def _terms_or_acceptance_path(quotation: Any) -> str:
    for fieldname in ("terms", "tc_name", "acceptance_path", "custom_acceptance_path"):
        value = str(_get(quotation, fieldname) or "").strip()
        if value:
            return value
    return ""


def _event_context(quotation: Any, payload: dict[str, Any]) -> str:
    for fieldname in (
        "custom_event_date",
        "event_date",
        "custom_event_location",
        "event_location",
        "custom_venue_address",
    ):
        value = str(_get(quotation, fieldname) or "").strip()
        if value:
            return value
    for fieldname in ("selected_options", "customizations", "summary"):
        value = payload.get(fieldname)
        if value:
            return str(value)
    return ""


def _next_action(blockers: list[str]) -> str:
    if not blockers:
        return "Human can prepare the customer review packet; sending is still a separate gated workflow."
    if "replace_placeholder_review_line_with_real_scope_and_pricing" in blockers:
        return "Replace the product quote review placeholder with real scoped Quotation lines and pricing."
    if "required_field:reviewed_product_quote_pricing" in blockers:
        return "Review and enter real pricing before preparing anything customer-facing."
    return "Clear the listed blockers before preparing a customer quote review."


def _guard_counts() -> dict[str, int]:
    return {
        doctype: int(frappe.db.count(doctype))
        for doctype in MUTATION_GUARD_DOCTYPES
        if frappe.db.exists("DocType", doctype)
    }


def _get(row: Any, fieldname: str) -> Any:
    if hasattr(row, "get"):
        return row.get(fieldname)
    return getattr(row, fieldname, None)


def _dedupe(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result
