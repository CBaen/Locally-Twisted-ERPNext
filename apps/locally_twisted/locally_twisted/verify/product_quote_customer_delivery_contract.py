"""Rollback-safe contract for product quote customer delivery."""
from __future__ import annotations

import json
import time

import frappe
from frappe.utils import add_days, nowdate

from locally_twisted.product_page_runtime import CONFIG_VERSION, LINE_FIELDNAMES
from locally_twisted.product_quote_runtime import QUOTATION_FIELDNAMES
from locally_twisted.communication_copy_policy import BUSINESS_DOCUMENT_COPY, routed_alias_copy_risks


PRICE_LIST = "Standard Selling"
PROOF_PRODUCT_PAGE = "classic-arch"
PROOF_ORDER_ITEM = "unicorn-bouquet-SMA"
BUSINESS_BCC = BUSINESS_DOCUMENT_COPY


class ContractFail(Exception):
    pass


def run() -> dict[str, object]:
    original_commit = frappe.db.commit
    original_sendmail = frappe.sendmail
    intercepted_commits = []
    sent_messages = []

    def no_commit(*args, **kwargs):
        intercepted_commits.append(True)

    def capture_sendmail(**kwargs):
        sent_messages.append(kwargs)
        return None

    try:
        frappe.db.commit = no_commit
        frappe.sendmail = capture_sendmail
        result = _run_contract(sent_messages)
        result["commit_calls_intercepted"] = len(intercepted_commits)
        result["rolled_back"] = True
        return result
    except ContractFail as exc:
        return {"ok": False, "failures": [str(exc)]}
    except Exception:
        return {"ok": False, "failures": [frappe.get_traceback()]}
    finally:
        frappe.db.commit = original_commit
        frappe.sendmail = original_sendmail
        frappe.db.rollback()


def _run_contract(sent_messages: list[dict]) -> dict[str, object]:
    from locally_twisted.product_quote_customer_delivery import send_product_quote_customer_review

    quotation_name = _submitted_reviewed_product_quote()
    sent_messages.clear()
    before = _guard_counts()
    result = send_product_quote_customer_review(
        quotation_name,
        recipient_email="cameronbpaul@example.invalid",
        business_bcc=BUSINESS_BCC,
        base_url="http://localhost:8081",
    )
    after = _guard_counts()
    if len(sent_messages) != 1:
        raise ContractFail(f"customer quote sender should call sendmail once, found {len(sent_messages)}")
    message = sent_messages[0]
    if message.get("recipients") != ["cameronbpaul@example.invalid"]:
        raise ContractFail(f"customer quote sender used wrong recipient: {message.get('recipients')}")
    if message.get("bcc") != [BUSINESS_BCC]:
        raise ContractFail(f"customer quote sender did not BCC the business: {message.get('bcc')}")
    risks = routed_alias_copy_risks(message.get("bcc"))
    if risks:
        raise ContractFail(f"customer quote sender used routed alias copy recipients: {risks}")
    if "quote-accept?token=" not in str(message.get("message") or ""):
        raise ContractFail("customer quote sender did not include the approval link")
    for unsafe in ("custom_lt_", "LT-PRODUCT-QUOTE-REVIEW", "DocType"):
        if unsafe in str(message.get("message") or ""):
            raise ContractFail(f"customer quote email leaked internal marker {unsafe}")
    _assert_no_order_finance_or_email_mutations(before, after)
    _assert_missing_bcc_blocks_loudly(quotation_name)
    _assert_routed_alias_bcc_blocks_loudly(quotation_name)
    customer_quote_name = _submitted_reviewed_customer_product_quote_with_linked_contact()
    _assert_customer_quote_uses_linked_contact_email(customer_quote_name, sent_messages)

    return {
        "ok": True,
        "quotation": quotation_name,
        "recipient": result.get("recipient"),
        "business_bcc": result.get("business_bcc"),
        "acceptance_url": result.get("acceptance_url"),
        "sendmail_calls": len(sent_messages),
        "guard_counts_before": before,
        "guard_counts_after": after,
    }


def _assert_missing_bcc_blocks_loudly(quotation_name: str) -> None:
    from locally_twisted.product_quote_customer_delivery import send_product_quote_customer_review

    try:
        send_product_quote_customer_review(
            quotation_name,
            recipient_email="cameronbpaul@example.invalid",
            business_bcc="",
            base_url="http://localhost:8081",
        )
    except frappe.ValidationError as exc:
        if "copy" not in str(exc).lower() and "bcc" not in str(exc).lower():
            raise ContractFail(f"missing BCC failed with unclear message: {exc}")
        return
    raise ContractFail("customer quote sender should not send without business BCC")


def _assert_routed_alias_bcc_blocks_loudly(quotation_name: str) -> None:
    from locally_twisted.product_quote_customer_delivery import send_product_quote_customer_review

    try:
        send_product_quote_customer_review(
            quotation_name,
            recipient_email="cameronbpaul@example.invalid",
            business_bcc="hi@locallytwisted.com",
            base_url="http://localhost:8081",
        )
    except frappe.ValidationError as exc:
        message = str(exc).lower()
        if "loop" not in message and "delivery-safe" not in message:
            raise ContractFail(f"routed alias BCC failed with unclear message: {exc}")
        return
    raise ContractFail("customer quote sender should block routed-alias business BCC")


def _assert_customer_quote_uses_linked_contact_email(quotation_name: str, sent_messages: list[dict]) -> None:
    from locally_twisted.product_quote_customer_delivery import send_product_quote_customer_review

    sent_messages.clear()
    result = send_product_quote_customer_review(
        quotation_name,
        business_bcc=BUSINESS_BCC,
        base_url="http://localhost:8081",
    )
    if len(sent_messages) != 1:
        raise ContractFail(f"customer linked-contact quote should call sendmail once, found {len(sent_messages)}")
    message = sent_messages[0]
    if message.get("recipients") != ["linked-product-quote-contact@example.invalid"]:
        raise ContractFail(f"customer linked-contact quote used wrong recipient: {message.get('recipients')}")
    if result.get("recipient") != "linked-product-quote-contact@example.invalid":
        raise ContractFail(f"customer linked-contact quote returned wrong recipient: {result.get('recipient')}")
    if message.get("bcc") != [BUSINESS_BCC]:
        raise ContractFail(f"customer linked-contact quote did not BCC the business: {message.get('bcc')}")


def _assert_no_order_finance_or_email_mutations(before: dict[str, int], after: dict[str, int]) -> None:
    for doctype in ("Sales Order", "Sales Invoice", "Payment Request", "Email Queue", "Communication"):
        if after.get(doctype) != before.get(doctype):
            raise ContractFail(f"{doctype} changed during customer quote delivery")


def _submitted_reviewed_product_quote() -> str:
    token = str(int(time.time() * 1000))
    lead = frappe.get_doc(
        {
            "doctype": "Lead",
            "first_name": f"LT Quote Delivery {token}",
            "email_id": f"lt-delivery-{token}@example.invalid",
            "source": "Website",
            "status": "Open",
        }
    )
    lead.insert(ignore_permissions=True)
    payload = _product_quote_payload()
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
            "customer_name": "Quote Delivery Buyer",
            "terms": "Customer may approve the reviewed quote with the approval link. Payment path is separate.",
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
    return quotation.name


def _submitted_reviewed_customer_product_quote_with_linked_contact() -> str:
    token = str(int(time.time() * 1000))
    lead = frappe.get_doc(
        {
            "doctype": "Lead",
            "first_name": f"LT Quote Delivery Customer Source {token}",
            "email_id": f"lt-delivery-customer-source-{token}@example.invalid",
            "source": "Website",
            "status": "Open",
        }
    )
    lead.insert(ignore_permissions=True)
    customer = frappe.get_doc(
        {
            "doctype": "Customer",
            "customer_name": f"LT Quote Delivery Customer {token}",
            "customer_type": "Individual",
            "customer_group": _first_leaf("Customer Group"),
            "territory": _first_leaf("Territory"),
        }
    )
    customer.insert(ignore_permissions=True)
    contact = frappe.get_doc(
        {
            "doctype": "Contact",
            "first_name": "Linked",
            "last_name": f"Delivery Contact {token}",
            "email_ids": [{"email_id": "linked-product-quote-contact@example.invalid", "is_primary": 1}],
            "links": [{"link_doctype": "Customer", "link_name": customer.name}],
        }
    )
    contact.insert(ignore_permissions=True)
    frappe.db.set_value("Contact", contact.name, "email_id", "")
    payload = _product_quote_payload()
    quotation = frappe.get_doc(
        {
            "doctype": "Quotation",
            "quotation_to": "Customer",
            "party_name": customer.name,
            "transaction_date": nowdate(),
            "valid_till": add_days(nowdate(), 14),
            "order_type": "Sales",
            "company": _company_name(),
            "currency": "USD",
            "selling_price_list": PRICE_LIST,
            "ignore_pricing_rule": 1,
            "customer_name": customer.customer_name,
            "contact_email": "",
            "terms": "Customer may approve the reviewed quote with the approval link. Payment path is separate.",
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
    return quotation.name


def _product_quote_payload() -> dict[str, object]:
    return {
        "schema_version": CONFIG_VERSION,
        "source": "lt_product_page_quote_runtime",
        "website_item_code": PROOF_PRODUCT_PAGE,
        "product_page_type": "complex_custom_product",
        "commerce_lane": "quote_first",
        "summary": "Requested product page quote: Classic Arch; Arch Size: 20ft; pricing reviewed",
        "selected_options": {"Arch Size": "20ft"},
        "customizations": [{"label": "Color notes", "value": "White, gold, navy"}],
        "add_ons": [],
    }


def _guard_counts() -> dict[str, int]:
    return {
        doctype: int(frappe.db.count(doctype))
        for doctype in ("Sales Order", "Sales Invoice", "Payment Request", "Email Queue", "Communication")
        if frappe.db.exists("DocType", doctype)
    }


def _company_name() -> str:
    company = frappe.defaults.get_user_default("Company") or frappe.db.get_value("Company", {}, "name")
    if not company:
        raise ContractFail("ERPNext needs a company before quote delivery can be tested")
    return company


def _first_leaf(doctype: str) -> str:
    value = frappe.db.get_value(doctype, {"is_group": 0}, "name") or frappe.db.get_value(doctype, {}, "name")
    if not value:
        raise ContractFail(f"Missing {doctype} record for product quote delivery contract")
    return value
