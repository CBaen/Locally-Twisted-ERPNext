"""Accepted product-page quote bridge to draft Sales Orders."""
from __future__ import annotations

import json
import secrets
from hashlib import sha256
from typing import Any
from urllib.parse import urlencode

import frappe
from frappe import _
from frappe.utils import add_days, getdate, now_datetime, nowdate

from locally_twisted.product_page_runtime import CONFIG_VERSION, LINE_FIELDNAMES
from locally_twisted.product_quote_runtime import (
    PRODUCT_QUOTE_REVIEW_ITEM,
    QUOTATION_FIELDNAMES,
    copy_quotation_line_configuration_to_sales_order,
)


ACCEPTANCE_REQUIRED_FIELDS = (
    "accepted_by",
    "accepted_email",
    "accepted_on",
    "acceptance_reference",
)

ACCEPTANCE_FIELDNAMES = {
    "source_quotation": "custom_lt_source_quotation",
    "accepted_by": "custom_lt_quote_acceptance_by",
    "accepted_email": "custom_lt_quote_acceptance_email",
    "accepted_on": "custom_lt_quote_acceptance_on",
    "acceptance_reference": "custom_lt_quote_acceptance_reference",
    "acceptance_payload": "custom_lt_quote_acceptance_payload",
}

TOKEN_FIELDNAMES = {
    "token_hash": "custom_lt_quote_acceptance_token_hash",
    "token_issued_on": "custom_lt_quote_acceptance_token_issued_on",
    "token_expires_on": "custom_lt_quote_acceptance_token_expires_on",
}

QUOTE_STATUS_READY_FOR_CUSTOMER_REVIEW = "Ready For Customer Review"


def create_draft_sales_order_from_accepted_product_quote(
    quotation_name: str,
    *,
    acceptance: dict[str, Any] | None,
):
    """Create a draft Sales Order or return the existing order for an accepted quote.

    This is not a payment or finance step. It does not submit the Sales Order,
    create an invoice, create a Payment Request, send email, or imply payment.
    The Quotation must already be human-reviewed, submitted, priced, and
    accepted through an explicit external confirmation.
    """
    quotation_name = str(quotation_name or "").strip()
    if not quotation_name:
        frappe.throw(
            _("Tiny snag: we need the reviewed quote before we can draft the order."),
            frappe.ValidationError,
        )

    quotation = frappe.get_doc("Quotation", quotation_name)
    _assert_acceptance_details(acceptance)
    _assert_sales_order_acceptance_storage()
    blockers = product_quote_acceptance_blockers(quotation)
    if blockers:
        frappe.throw(
            _(
                "Tiny snag: this product quote is not ready to become an order yet. "
                "Please clear these review items first: "
            )
            + "; ".join(blockers),
            frappe.ValidationError,
        )

    existing = _existing_sales_order_for_quote(quotation.name)
    if existing:
        existing_name, existing_docstatus = existing
        if existing_docstatus == 2:
            frappe.throw(
                _(
                    "Tiny snag: this quote approval was already used, but the related order was cancelled. "
                    "Please ask us for a fresh approval link."
                ),
                frappe.ValidationError,
            )
        sales_order = frappe.get_doc("Sales Order", existing_name)
        sales_order.flags.lt_existing_product_quote_order = True
        return sales_order

    from erpnext.selling.doctype.quotation.quotation import _make_sales_order

    sales_order = _make_sales_order(quotation.name, ignore_permissions=True)
    sales_order.flags.ignore_permissions = True
    _set_delivery_dates(sales_order, quotation)
    _copy_acceptance_context(sales_order, quotation, acceptance or {})
    copy_quotation_line_configuration_to_sales_order(sales_order, quotation.name)
    sales_order.insert(ignore_permissions=True)
    return sales_order


def issue_product_quote_acceptance_token(
    quotation_name: str,
    *,
    base_url: str | None = None,
    expires_on: str | None = None,
) -> dict[str, str]:
    """Create a one-quote acceptance token without sending it to a customer."""
    _assert_token_storage()
    quotation_name = str(quotation_name or "").strip()
    if not quotation_name:
        frappe.throw(
            _("Tiny snag: we need the reviewed quote before making an acceptance link."),
            frappe.ValidationError,
        )
    quotation = frappe.get_doc("Quotation", quotation_name)
    blockers = product_quote_acceptance_blockers(quotation)
    if blockers:
        frappe.throw(
            _(
                "Tiny snag: this product quote is not ready for an acceptance link yet. "
                "Please clear these review items first: "
            )
            + "; ".join(blockers),
            frappe.ValidationError,
        )
    token = secrets.token_urlsafe(32)
    expires_on = str(expires_on or add_days(nowdate(), 14))
    frappe.db.set_value(
        "Quotation",
        quotation.name,
        {
            TOKEN_FIELDNAMES["token_hash"]: _hash_token(token),
            TOKEN_FIELDNAMES["token_issued_on"]: now_datetime(),
            TOKEN_FIELDNAMES["token_expires_on"]: expires_on,
        },
        update_modified=False,
    )
    path = "/quote-accept?" + urlencode({"token": token})
    url = _absolute_url(path, base_url=base_url)
    return {
        "quotation": quotation.name,
        "token": token,
        "acceptance_path": path,
        "acceptance_url": url,
        "expires_on": expires_on,
        "email_send_allowed": False,
    }


def product_quote_acceptance_preview(token: str) -> dict[str, Any]:
    """Return customer-safe quote preview data for an approval token."""
    quotation = _quotation_for_token(token)
    expires_on = quotation.get(TOKEN_FIELDNAMES["token_expires_on"])
    if expires_on and getdate(expires_on) < getdate(nowdate()):
        frappe.throw(
            _("Tiny snag: this quote approval link has expired. Please ask us for a fresh one."),
            frappe.ValidationError,
        )
    blockers = product_quote_acceptance_blockers(quotation)
    if blockers:
        frappe.throw(
            _(
                "Tiny snag: this quote still needs a team review before approval. "
                "Please ask us for a fresh approval link."
            ),
            frappe.ValidationError,
        )
    return {
        "ok": True,
        "quotation": quotation.name,
        "customer_name": quotation.get("customer_name") or quotation.get("party_name") or "your event",
        "summary": quotation.get(QUOTATION_FIELDNAMES["summary"]) or "Reviewed product quote",
        "total": float(quotation.get("grand_total") or 0),
        "currency": quotation.get("currency") or "USD",
        "expires_on": str(expires_on or ""),
    }


def create_draft_sales_order_from_product_quote_token(
    token: str,
    *,
    acceptance: dict[str, Any] | None,
):
    """Accept a tokenized quote and create or return the existing Sales Order."""
    quotation = _quotation_for_token(token)
    expires_on = quotation.get(TOKEN_FIELDNAMES["token_expires_on"])
    if expires_on and getdate(expires_on) < getdate(nowdate()):
        frappe.throw(
            _("Tiny snag: this quote approval link has expired. Please ask us for a fresh one."),
            frappe.ValidationError,
        )
    return create_draft_sales_order_from_accepted_product_quote(
        quotation.name,
        acceptance=acceptance,
    )


@frappe.whitelist(allow_guest=True)
def accept_product_quote_from_token(
    token: str | None = None,
    accepted_by: str | None = None,
    accepted_email: str | None = None,
    acceptance_reference: str | None = None,
    accepted_on: str | None = None,
) -> dict[str, Any]:
    """Guest-safe token action for a customer accepting a reviewed quote."""
    sales_order = create_draft_sales_order_from_product_quote_token(
        token or "",
        acceptance={
            "accepted_by": accepted_by,
            "accepted_email": accepted_email,
            "accepted_on": accepted_on or nowdate(),
            "acceptance_reference": acceptance_reference,
        },
    )
    already_accepted = bool(getattr(sales_order.flags, "lt_existing_product_quote_order", False))
    draft_only = int(sales_order.docstatus or 0) == 0
    return {
        "ok": True,
        "sales_order": sales_order.name,
        "draft_only": draft_only,
        "already_accepted": already_accepted,
        "invoice_creation_allowed": False,
        "payment_request_allowed": False,
        "email_send_allowed": False,
        "customer_message": _acceptance_customer_message(already_accepted=already_accepted),
    }


def product_quote_acceptance_blockers(quotation: Any) -> list[str]:
    """Return loud blocker tokens for quote-to-order acceptance."""
    blockers: list[str] = []
    if int(_get(quotation, "docstatus") or 0) != 1:
        blockers.append("submit_the_reviewed_quotation_before_order_draft")
    if str(_get(quotation, QUOTATION_FIELDNAMES["status"]) or "").strip() != QUOTE_STATUS_READY_FOR_CUSTOMER_REVIEW:
        blockers.append("product_quote_not_ready_for_customer_review")
    if not _get(quotation, QUOTATION_FIELDNAMES["source_lead"]):
        blockers.append("missing_product_quote_source_inquiry")
    if _money_is_zero(_get(quotation, "grand_total")):
        blockers.append("pricing_review_required")
    if _is_expired(quotation):
        blockers.append("quotation_is_expired")

    items = list(_get(quotation, "items") or [])
    if not items:
        blockers.append("missing_reviewed_quote_lines")
    if any(_get(item, "item_code") == PRODUCT_QUOTE_REVIEW_ITEM for item in items):
        blockers.append("replace_placeholder_review_line_before_order")

    payload_failures = _payload_failures(quotation, items)
    blockers.extend(payload_failures)
    for item in items:
        if _get(item, "item_code") == PRODUCT_QUOTE_REVIEW_ITEM:
            continue
        if _money_is_zero(_get(item, "rate")) and _money_is_zero(_get(item, "amount")):
            blockers.append("pricing_review_required")
        for fieldname in LINE_FIELDNAMES.values():
            if not _get(item, fieldname):
                blockers.append("missing_quote_line_product_configuration")
                break

    return _dedupe(blockers)


def _existing_sales_order_for_quote(quotation_name: str) -> tuple[str, int] | None:
    _assert_sales_order_acceptance_storage()
    source_field = ACCEPTANCE_FIELDNAMES["source_quotation"]
    active_rows = frappe.get_all(
        "Sales Order",
        filters={source_field: quotation_name, "docstatus": ["in", [0, 1]]},
        fields=["name", "docstatus"],
        order_by="modified desc",
        limit=1,
    )
    if active_rows:
        return active_rows[0]["name"], int(active_rows[0].get("docstatus") or 0)
    any_rows = frappe.get_all(
        "Sales Order",
        filters={source_field: quotation_name},
        fields=["name", "docstatus"],
        order_by="modified desc",
        limit=1,
    )
    if any_rows:
        return any_rows[0]["name"], int(any_rows[0].get("docstatus") or 0)
    return None


def _acceptance_customer_message(*, already_accepted: bool) -> str:
    if already_accepted:
        return (
            "Thanks, we already have your quote approval. "
            "The team will keep using the existing order record before any invoice or payment step."
        )
    return (
        "Thanks, we have your quote approval. "
        "The team will review the order draft before any invoice or payment step."
    )


def _assert_acceptance_details(acceptance: dict[str, Any] | None) -> None:
    if not isinstance(acceptance, dict):
        acceptance = {}
    missing = [
        fieldname
        for fieldname in ACCEPTANCE_REQUIRED_FIELDS
        if not str(acceptance.get(fieldname) or "").strip()
    ]
    if missing:
        frappe.throw(
            _(
                "Tiny snag: we need the customer's acceptance details before drafting the order. "
                "Please record who accepted it, the email, date, and written approval reference."
            ),
            frappe.ValidationError,
        )


def _copy_acceptance_context(sales_order, quotation, acceptance: dict[str, Any]) -> None:
    field_values = {
        ACCEPTANCE_FIELDNAMES["source_quotation"]: quotation.name,
        ACCEPTANCE_FIELDNAMES["accepted_by"]: acceptance.get("accepted_by"),
        ACCEPTANCE_FIELDNAMES["accepted_email"]: acceptance.get("accepted_email"),
        ACCEPTANCE_FIELDNAMES["accepted_on"]: acceptance.get("accepted_on"),
        ACCEPTANCE_FIELDNAMES["acceptance_reference"]: acceptance.get("acceptance_reference"),
        ACCEPTANCE_FIELDNAMES["acceptance_payload"]: json.dumps(acceptance, sort_keys=True, default=str),
    }
    _assert_sales_order_acceptance_storage()
    for fieldname, value in field_values.items():
        if value not in (None, ""):
            sales_order.set(fieldname, value)


def _quotation_for_token(token: str):
    _assert_token_storage()
    token = str(token or "").strip()
    if not token:
        frappe.throw(
            _("Tiny snag: this quote approval link is missing its approval code."),
            frappe.ValidationError,
        )
    quotation_name = frappe.db.get_value(
        "Quotation",
        {TOKEN_FIELDNAMES["token_hash"]: _hash_token(token)},
        "name",
    )
    if not quotation_name:
        frappe.throw(
            _("Tiny snag: this quote approval link is not valid anymore. Please ask us for a fresh one."),
            frappe.ValidationError,
        )
    return frappe.get_doc("Quotation", quotation_name)


def _assert_token_storage() -> None:
    meta = frappe.get_meta("Quotation")
    missing = [fieldname for fieldname in TOKEN_FIELDNAMES.values() if not meta.has_field(fieldname)]
    if missing:
        frappe.throw(
            _(
                "Tiny snag: quote approval links are not fully set up yet. "
                "Please keep this quote in team review for now."
            ),
            frappe.ValidationError,
        )


def _assert_sales_order_acceptance_storage() -> None:
    meta = frappe.get_meta("Sales Order")
    missing = [fieldname for fieldname in ACCEPTANCE_FIELDNAMES.values() if not meta.has_field(fieldname)]
    if missing:
        frappe.throw(
            _(
                "Tiny snag: quote acceptance order storage is not fully set up yet. "
                "Please keep this quote in team review for now."
            )
            + f" Missing Sales Order acceptance fields: {', '.join(missing)}",
            frappe.ValidationError,
        )


def _hash_token(token: str) -> str:
    return sha256(str(token or "").encode("utf-8")).hexdigest()


def _absolute_url(path: str, *, base_url: str | None = None) -> str:
    base = str(base_url or frappe.utils.get_url() or "").rstrip("/")
    if not base:
        return path
    return base + path


def _set_delivery_dates(sales_order, quotation) -> None:
    delivery_date = (
        _get(quotation, "custom_event_date")
        or _get(quotation, "event_date")
        or _get(quotation, "valid_till")
        or add_days(nowdate(), 14)
    )
    if not _get(sales_order, "delivery_date"):
        sales_order.delivery_date = delivery_date
    for row in sales_order.get("items") or []:
        if not _get(row, "delivery_date"):
            row.delivery_date = delivery_date


def _payload_failures(quotation: Any, items: list[Any]) -> list[str]:
    raw = _get(quotation, QUOTATION_FIELDNAMES["json"])
    if not raw:
        for item in items:
            raw = _get(item, LINE_FIELDNAMES["json"])
            if raw:
                break
    if not raw:
        return ["malformed_product_quote_payload:missing"]
    try:
        payload = json.loads(raw) if isinstance(raw, str) else raw
    except (TypeError, ValueError):
        return ["malformed_product_quote_payload:unreadable_json"]
    if not isinstance(payload, dict):
        return ["malformed_product_quote_payload:not_object"]
    if payload.get("schema_version") != CONFIG_VERSION:
        return ["malformed_product_quote_payload:wrong_schema_version"]
    if not payload.get("website_item_code"):
        return ["malformed_product_quote_payload:missing_requested_product"]
    if payload.get("commerce_lane") != "quote_first":
        return ["wrong_product_quote_commerce_lane"]
    return []


def _is_expired(quotation: Any) -> bool:
    valid_till = _get(quotation, "valid_till")
    if not valid_till:
        return False
    return getdate(valid_till) < getdate(nowdate())


def _money_is_zero(value: Any) -> bool:
    try:
        return float(value or 0) == 0
    except (TypeError, ValueError):
        return True


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
