"""Draft Quotation bridge for quote-first LT product pages."""
from __future__ import annotations

import json
from typing import Any

import frappe
from frappe import _
from frappe.utils import add_days, nowdate

from locally_twisted.product_page_runtime import (
    CONFIG_VERSION,
    LINE_FIELDNAMES,
    MAX_CONFIGURATION_BYTES,
    PRICE_LIST,
    product_page_contract_for_website_item,
)


QUOTATION_FIELDNAMES = {
    "source_lead": "custom_lt_source_lead",
    "template_item": "custom_lt_product_template_item",
    "page_type": "custom_lt_product_page_type",
    "commerce_lane": "custom_lt_commerce_lane",
    "version": "custom_lt_configuration_version",
    "summary": "custom_lt_product_quote_summary",
    "json": "custom_lt_product_quote_payload",
    "status": "custom_lt_product_quote_status",
}


QUOTE_STATUS_NEEDS_REVIEW = "Needs Operator Review"
QUOTE_STATUS_DRAFT_CREATED = "Draft Quotation Created"

PRODUCT_QUOTE_REVIEW_ITEM = "LT-PRODUCT-QUOTE-REVIEW"
PRODUCT_QUOTE_REVIEW_ITEM_CONTRACT = {
    "item_code": PRODUCT_QUOTE_REVIEW_ITEM,
    "item_name": "Product Page Quote Review",
    "item_group": "Services",
    "description": "Internal zero-dollar line used to draft product-page quote requests when the public page is a template item.",
    "rate": 0.0,
}


def create_product_page_draft_quotation_from_lead(lead_name: str):
    """Create or return a draft Quotation for a product-page quote Lead.

    This is an internal/operator bridge only. It creates a draft Quotation,
    preserves the product-page payload on the Quotation and Quotation Item,
    and does not submit, email, request payment, or imply customer success.
    """
    _assert_quotation_storage()
    _assert_quotation_item_storage()

    lead_name = str(lead_name or "").strip()
    if not lead_name:
        frappe.throw(_("Tiny snag: the product quote needs a source inquiry before we can draft it."))
    lead = frappe.get_doc("Lead", lead_name)

    existing = _existing_draft_quotation_name(lead.name)
    if existing:
        return frappe.get_doc("Quotation", existing)

    payload = _product_quote_payload_from_lead(lead)
    item_code = _quote_item_code(payload)
    payload = _runtime_payload(payload, lead.name, item_code)
    summary = payload.get("summary") or f"Requested product page quote: {item_code}"
    encoded_payload = _encoded_payload(payload)

    quotation = frappe.get_doc(
        {
            "doctype": "Quotation",
            "quotation_to": "Lead",
            "party_name": lead.name,
            "transaction_date": nowdate(),
            "valid_till": add_days(nowdate(), 14),
            "order_type": "Sales",
            "company": _company_name(),
            "currency": _currency(),
            "selling_price_list": PRICE_LIST,
            "ignore_pricing_rule": 1,
            QUOTATION_FIELDNAMES["source_lead"]: lead.name,
            QUOTATION_FIELDNAMES["template_item"]: payload.get("website_item_code"),
            QUOTATION_FIELDNAMES["page_type"]: payload.get("product_page_type"),
            QUOTATION_FIELDNAMES["commerce_lane"]: payload.get("commerce_lane"),
            QUOTATION_FIELDNAMES["version"]: CONFIG_VERSION,
            QUOTATION_FIELDNAMES["summary"]: summary,
            QUOTATION_FIELDNAMES["json"]: encoded_payload,
            QUOTATION_FIELDNAMES["status"]: QUOTE_STATUS_DRAFT_CREATED,
            "items": [
                {
                    "item_code": item_code,
                    "qty": 1,
                    "rate": 0,
                    "price_list_rate": 0,
                    "description": summary,
                    LINE_FIELDNAMES["template_item"]: payload.get("website_item_code"),
                    LINE_FIELDNAMES["page_type"]: payload.get("product_page_type"),
                    LINE_FIELDNAMES["version"]: CONFIG_VERSION,
                    LINE_FIELDNAMES["summary"]: summary,
                    LINE_FIELDNAMES["json"]: encoded_payload,
                }
            ],
        }
    )
    quotation.flags.ignore_permissions = True
    quotation.insert(ignore_permissions=True)
    _mark_lead_quote_child_as_drafted(lead, payload)
    return quotation


def copy_quotation_line_configuration_to_sales_order(sales_order_doc, quotation_name: str) -> None:
    """Copy quote-first product-page payload from Quotation Item to Sales Order Item.

    This helper does not create, submit, email, invoice, or request payment. It
    exists so a future human-approved quote acceptance path can preserve the
    same product-page meaning when it intentionally creates a Sales Order.
    """
    _assert_sales_order_item_storage()

    quotation_name = str(quotation_name or "").strip()
    if not quotation_name:
        frappe.throw(
            _("Tiny snag: the product quote needs a source quote before it can become an order."),
            frappe.ValidationError,
        )
    quotation = frappe.get_doc("Quotation", quotation_name)
    quote_items = {row.name: row for row in quotation.items}
    fallback_by_code: dict[str, list[Any]] = {}
    for row in quotation.items:
        fallback_by_code.setdefault(row.item_code, []).append(row)

    for order_row in sales_order_doc.items:
        source_row = _matching_quotation_item(order_row, quote_items, fallback_by_code)
        if not source_row:
            continue
        for fieldname in LINE_FIELDNAMES.values():
            value = source_row.get(fieldname)
            if value not in (None, ""):
                order_row.set(fieldname, value)


def _product_quote_payload_from_lead(lead) -> dict[str, Any]:
    raw = lead.get("custom_lt_product_quote_payload")
    if raw:
        payload = _decode_payload(raw)
        if payload:
            return _validate_payload(payload)

    for row in lead.get("custom_lt_product_quote_items") or []:
        payload = _decode_payload(row.get("payload_json"))
        if payload:
            return _validate_payload(payload)

    frappe.throw(
        _(
            "Tiny snag: this inquiry does not have product-page quote details yet. "
            "Please open the original inquiry before drafting a quote."
        ),
        frappe.ValidationError,
    )


def _decode_payload(raw: Any) -> dict[str, Any] | None:
    if not raw:
        return None
    if isinstance(raw, dict):
        return raw
    try:
        payload = json.loads(raw)
    except (TypeError, ValueError):
        frappe.throw(
            _("Tiny snag: this inquiry's product-page quote details are not readable yet."),
            frappe.ValidationError,
        )
    if not isinstance(payload, dict):
        frappe.throw(
            _("Tiny snag: this inquiry's product-page quote details are not readable yet."),
            frappe.ValidationError,
        )
    return payload


def _validate_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("schema_version") != CONFIG_VERSION:
        frappe.throw(
            _(
                "Tiny snag: this inquiry used an older product-page quote format. "
                "Please review the Lead before drafting a quote."
            ),
            frappe.ValidationError,
        )
    if not payload.get("website_item_code"):
        frappe.throw(
            _("Tiny snag: this product quote is missing the requested product page."),
            frappe.ValidationError,
        )
    return dict(payload)


def _quote_item_code(payload: dict[str, Any]) -> str:
    item_code = str(payload.get("website_item_code") or "").strip()
    item = frappe.db.get_value(
        "Item",
        item_code,
        ["item_code", "has_variants"],
        as_dict=True,
    )
    if not item:
        frappe.throw(
            _("Tiny snag: this requested product page is not an ERPNext Item yet.")
            + (f" Missing Item: {item_code}" if item_code else ""),
            frappe.ValidationError,
        )
    if item.get("has_variants"):
        if not frappe.db.exists("Item", PRODUCT_QUOTE_REVIEW_ITEM):
            frappe.throw(
                _(
                    "Tiny snag: the product quote review line is not installed yet. "
                    "Please keep this inquiry in operator review for now."
                )
                + f" Missing Item: {PRODUCT_QUOTE_REVIEW_ITEM}",
                frappe.ValidationError,
            )
        return PRODUCT_QUOTE_REVIEW_ITEM
    return item_code


def _runtime_payload(payload: dict[str, Any], lead_name: str, item_code: str) -> dict[str, Any]:
    contract = product_page_contract_for_website_item(payload.get("website_item_code"))
    normalized = {
        "schema_version": CONFIG_VERSION,
        "source": "lt_product_page_quote_runtime",
        "original_source": payload.get("source"),
        "lead": lead_name,
        "item_code": item_code,
        "website_item_code": payload.get("website_item_code"),
        "web_item_name": payload.get("web_item_name"),
        "item_group": payload.get("item_group"),
        "route": payload.get("route"),
        "product_page_type": payload.get("product_page_type") or contract.get("product_page_type"),
        "commerce_lane": payload.get("commerce_lane") or contract.get("commerce_lane"),
        "summary": payload.get("summary"),
        "selected_options": payload.get("selected_options") or {},
        "add_ons": payload.get("add_ons") or [],
        "customizations": payload.get("customizations") or [],
        "needs_operator_review": True,
    }
    return normalized


def _encoded_payload(payload: dict[str, Any]) -> str:
    try:
        encoded = json.dumps(payload, sort_keys=True, default=str)
    except (TypeError, ValueError):
        frappe.throw(
            _("Tiny snag: this product quote has details we cannot save yet."),
            frappe.ValidationError,
        )
    if len(encoded.encode("utf-8")) > MAX_CONFIGURATION_BYTES:
        frappe.throw(
            _("Tiny snag: this product quote has too many details for one draft. Please split the request."),
            frappe.ValidationError,
        )
    return encoded


def _existing_draft_quotation_name(lead_name: str) -> str | None:
    return frappe.db.get_value(
        "Quotation",
        {
            QUOTATION_FIELDNAMES["source_lead"]: lead_name,
            "docstatus": 0,
        },
        "name",
        order_by="modified desc",
    )


def _mark_lead_quote_child_as_drafted(lead, payload: dict[str, Any]) -> None:
    rows = lead.get("custom_lt_product_quote_items") or []
    if not rows:
        return
    requested = payload.get("website_item_code")
    for row in rows:
        if row.get("product_page") == requested and row.get("status") != QUOTE_STATUS_DRAFT_CREATED:
            frappe.db.set_value(
                row.doctype,
                row.name,
                "status",
                QUOTE_STATUS_DRAFT_CREATED,
                update_modified=False,
            )
            row.status = QUOTE_STATUS_DRAFT_CREATED


def _assert_quotation_storage() -> None:
    meta = frappe.get_meta("Quotation")
    missing = [field for field in QUOTATION_FIELDNAMES.values() if not meta.has_field(field)]
    if missing:
        frappe.throw(
            _(
                "Tiny snag: the product quote draft storage is not installed yet. "
                "Please keep this inquiry in operator review for now."
            )
            + f" Missing Quotation fields: {', '.join(missing)}",
            frappe.ValidationError,
        )


def _assert_quotation_item_storage() -> None:
    meta = frappe.get_meta("Quotation Item")
    missing = [field for field in LINE_FIELDNAMES.values() if not meta.has_field(field)]
    if missing:
        frappe.throw(
            _(
                "Tiny snag: the product quote line storage is not installed yet. "
                "Please keep this inquiry in operator review for now."
            )
            + f" Missing Quotation Item fields: {', '.join(missing)}",
            frappe.ValidationError,
        )


def _assert_sales_order_item_storage() -> None:
    meta = frappe.get_meta("Sales Order Item")
    missing = [field for field in LINE_FIELDNAMES.values() if not meta.has_field(field)]
    if missing:
        frappe.throw(
            _(
                "Tiny snag: the product quote order storage is not installed yet. "
                "Please keep this quote in operator review for now."
            ),
            frappe.ValidationError,
        )


def _matching_quotation_item(order_row, quote_items: dict[str, Any], fallback_by_code: dict[str, list[Any]]):
    for fieldname in ("quotation_item", "prevdoc_detail_docname", "reference_detail"):
        source_name = order_row.get(fieldname)
        if source_name and source_name in quote_items:
            return quote_items[source_name]
    candidates = fallback_by_code.get(order_row.item_code) or []
    if len(candidates) == 1:
        return candidates[0]
    return None


def _company_name() -> str:
    company = frappe.defaults.get_user_default("Company") or frappe.db.get_value("Company", {}, "name")
    if not company:
        frappe.throw(_("Tiny snag: ERPNext needs a company before it can draft product quotes."))
    return company


def _currency() -> str:
    company_currency = frappe.db.get_value("Company", _company_name(), "default_currency")
    return company_currency or frappe.defaults.get_global_default("currency") or "USD"
