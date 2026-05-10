"""Verifier-only fixture for the `/quote-accept` browser journey.

This module intentionally creates persistent temporary records so Playwright can
exercise the real public route and guest acceptance API. The matching cleanup
method removes the records by marker after the browser test.
"""
from __future__ import annotations

import json
import time
from typing import Any

import frappe
from frappe.utils import add_days, nowdate

from locally_twisted.product_page_runtime import CONFIG_VERSION, LINE_FIELDNAMES
from locally_twisted.product_quote_acceptance import (
    ACCEPTANCE_FIELDNAMES,
    issue_product_quote_acceptance_token,
)
from locally_twisted.product_quote_runtime import QUOTATION_FIELDNAMES
from locally_twisted.stage_cascade import LEAD_TASK_FIELD


PRICE_LIST = "Standard Selling"
PROOF_PRODUCT_PAGE = "classic-arch"
PROOF_ORDER_ITEM = "unicorn-bouquet-SMA"
MARKER_PREFIX = "LT-QA-QUOTE-ACCEPT-BROWSER"


def create(base_url: str | None = None) -> dict[str, Any]:
    """Create a submitted reviewed product quote and token for browser testing."""
    marker = f"{MARKER_PREFIX}-{int(time.time() * 1000)}"
    lead = frappe.get_doc(
        {
            "doctype": "Lead",
            "first_name": marker,
            "email_id": f"{marker.lower()}@example.invalid",
            "status": "Open",
        }
    )
    lead.insert(ignore_permissions=True)

    payload = _product_quote_payload(marker)
    quotation = frappe.get_doc(
        {
            "doctype": "Quotation",
            "quotation_to": "Lead",
            "party_name": lead.name,
            "transaction_date": nowdate(),
            "valid_till": add_days(nowdate(), 14),
            "order_type": "Sales",
            "company": _company_name(),
            "currency": "USD",
            "selling_price_list": PRICE_LIST,
            "ignore_pricing_rule": 1,
            "contact_email": f"{marker.lower()}-quote@example.invalid",
            "customer_name": marker,
            "terms": "Customer may approve the reviewed quote. Payment path is separate.",
            "custom_event_date": add_days(nowdate(), 21),
            "custom_event_location": "Ogden, Utah",
            QUOTATION_FIELDNAMES["source_lead"]: lead.name,
            QUOTATION_FIELDNAMES["template_item"]: PROOF_PRODUCT_PAGE,
            QUOTATION_FIELDNAMES["page_type"]: "complex_custom_product",
            QUOTATION_FIELDNAMES["commerce_lane"]: "quote_first",
            QUOTATION_FIELDNAMES["version"]: CONFIG_VERSION,
            QUOTATION_FIELDNAMES["summary"]: payload["summary"],
            QUOTATION_FIELDNAMES["json"]: json.dumps(payload, sort_keys=True),
            QUOTATION_FIELDNAMES["status"]: "Ready For Customer Review",
            "items": [
                {
                    "item_code": PROOF_ORDER_ITEM,
                    "qty": 1,
                    "rate": 650,
                    "price_list_rate": 650,
                    "description": payload["summary"],
                    LINE_FIELDNAMES["template_item"]: PROOF_PRODUCT_PAGE,
                    LINE_FIELDNAMES["page_type"]: "complex_custom_product",
                    LINE_FIELDNAMES["version"]: CONFIG_VERSION,
                    LINE_FIELDNAMES["summary"]: payload["summary"],
                    LINE_FIELDNAMES["json"]: json.dumps(payload, sort_keys=True),
                }
            ],
        }
    )
    quotation.insert(ignore_permissions=True)
    quotation.submit()
    token_info = issue_product_quote_acceptance_token(quotation.name, base_url=base_url)
    frappe.db.commit()
    return {
        "ok": True,
        "marker": marker,
        "lead": lead.name,
        "quotation": quotation.name,
        "acceptance_path": token_info["acceptance_path"],
        "acceptance_url": token_info["acceptance_url"],
    }


def preview_cleanup_state(marker: str | None = None) -> dict[str, Any]:
    marker = _marker(marker)
    quotation_names = _quotation_names(marker)
    sales_orders = _sales_order_names(quotation_names)
    return {
        "ok": True,
        "marker": marker,
        "quotation_count": len(quotation_names),
        "sales_order_count": len(sales_orders),
        "invoice_count": _count("Sales Invoice", marker),
        "payment_request_count": _count("Payment Request", marker),
        "email_queue_count": _count("Email Queue", marker),
        "communication_count": _count("Communication", marker),
    }


def cleanup(marker: str | None = None) -> dict[str, Any]:
    """Delete the temporary browser-journey records created by `create`."""
    marker = _marker(marker)
    quotation_names = _quotation_names(marker)
    lead_names = _lead_names(marker)
    sales_orders = _sales_order_names(quotation_names)
    deleted = []

    for sales_order_name in sales_orders:
        _delete_doc("Sales Order", sales_order_name, deleted)

    for quotation_name in quotation_names:
        doc = frappe.get_doc("Quotation", quotation_name)
        if int(doc.docstatus or 0) == 1:
            doc.cancel()
        _delete_doc("Quotation", quotation_name, deleted)

    for lead_name in lead_names:
        _delete_tasks_for_lead(lead_name, deleted)
        _delete_contacts_for_lead(lead_name, deleted)
        _delete_doc("Lead", lead_name, deleted)

    frappe.db.commit()
    return {
        "ok": True,
        "marker": marker,
        "deleted": deleted,
        "remaining": preview_cleanup_state(marker),
    }


def marker_counts() -> dict[str, Any]:
    """Return leftover browser-journey marker counts for verification closeout."""
    quotations = frappe.get_all(
        "Quotation",
        filters={"customer_name": ["like", f"{MARKER_PREFIX}%"]},
        pluck="name",
        limit_page_length=500,
    )
    return {
        "ok": True,
        "lead_count": int(frappe.db.count("Lead", {"first_name": ["like", f"{MARKER_PREFIX}%"]})),
        "quotation_count": len(quotations),
        "sales_order_count": len(_sales_order_names(quotations)),
    }


def _product_quote_payload(marker: str) -> dict[str, object]:
    return {
        "schema_version": CONFIG_VERSION,
        "source": "lt_product_page_quote_runtime",
        "website_item_code": PROOF_PRODUCT_PAGE,
        "product_page_type": "complex_custom_product",
        "commerce_lane": "quote_first",
        "summary": f"Requested product page quote: Classic Arch; Arch Size: 20ft; {marker}",
        "selected_options": {"Arch Size": "20ft"},
        "customizations": [{"label": "Color notes", "value": "White, gold, navy"}],
        "add_ons": [],
    }


def _delete_tasks_for_lead(lead_name: str, deleted: list[str]) -> None:
    if not frappe.get_meta("Task").has_field(LEAD_TASK_FIELD):
        return
    for task_name in frappe.get_all("Task", filters={LEAD_TASK_FIELD: lead_name}, pluck="name"):
        _delete_doc("Task", task_name, deleted)


def _delete_contacts_for_lead(lead_name: str, deleted: list[str]) -> None:
    contacts = frappe.get_all(
        "Dynamic Link",
        filters={"link_doctype": "Lead", "link_name": lead_name, "parenttype": "Contact"},
        pluck="parent",
    )
    for contact_name in contacts:
        _delete_doc("Contact", contact_name, deleted)


def _quotation_names(marker: str) -> list[str]:
    return frappe.get_all(
        "Quotation",
        filters={"customer_name": ["like", f"%{marker}%"]},
        pluck="name",
        limit_page_length=100,
    )


def _lead_names(marker: str) -> list[str]:
    return frappe.get_all(
        "Lead",
        filters={"first_name": ["like", f"%{marker}%"]},
        pluck="name",
        limit_page_length=100,
    )


def _sales_order_names(quotation_names: list[str]) -> list[str]:
    if not quotation_names:
        return []
    meta = frappe.get_meta("Sales Order")
    if not meta.has_field(ACCEPTANCE_FIELDNAMES["source_quotation"]):
        return []
    return frappe.get_all(
        "Sales Order",
        filters={ACCEPTANCE_FIELDNAMES["source_quotation"]: ["in", quotation_names]},
        pluck="name",
        limit_page_length=100,
    )


def _delete_doc(doctype: str, name: str, deleted: list[str]) -> None:
    if not frappe.db.exists(doctype, name):
        return
    frappe.delete_doc(doctype, name, ignore_permissions=True, force=True)
    deleted.append(f"{doctype}:{name}")


def _count(doctype: str, marker: str) -> int:
    if not frappe.db.exists("DocType", doctype):
        return 0
    meta = frappe.get_meta(doctype)
    if doctype in {"Sales Invoice", "Payment Request"}:
        if meta.has_field("customer_name"):
            return int(frappe.db.count(doctype, {"customer_name": ["like", f"%{marker}%"]}))
        if meta.has_field("party_name"):
            return int(frappe.db.count(doctype, {"party_name": ["like", f"%{marker}%"]}))
        return 0
    if doctype == "Email Queue" and meta.has_field("message"):
        return int(frappe.db.count(doctype, {"message": ["like", f"%{marker}%"]}))
    if doctype == "Communication" and meta.has_field("content"):
        return int(frappe.db.count(doctype, {"content": ["like", f"%{marker}%"]}))
    return 0


def _marker(marker: str | None) -> str:
    marker = str(marker or "").strip()
    if not marker.startswith(MARKER_PREFIX):
        frappe.throw("Missing or invalid quote acceptance fixture marker", frappe.ValidationError)
    return marker


def _company_name() -> str:
    company = frappe.defaults.get_user_default("Company") or frappe.db.get_value("Company", {}, "name")
    if not company:
        frappe.throw("ERPNext needs a company before quote acceptance browser testing can run", frappe.ValidationError)
    return company
