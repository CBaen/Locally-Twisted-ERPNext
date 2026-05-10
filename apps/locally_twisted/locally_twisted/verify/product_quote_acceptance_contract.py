"""Rollback-safe contract for accepted product-page quotes.

The accepted quote bridge is intentionally narrow: it may create a draft Sales
Order from a human-accepted, submitted Quotation, but it must not create
invoices, payment requests, or outbound email.
"""
from __future__ import annotations

import json
import time

import frappe
from frappe.utils import add_days, nowdate

from locally_twisted.product_page_runtime import CONFIG_VERSION, LINE_FIELDNAMES
from locally_twisted.product_quote_runtime import PRODUCT_QUOTE_REVIEW_ITEM, QUOTATION_FIELDNAMES


PRICE_LIST = "Standard Selling"
PROOF_PRODUCT_PAGE = "classic-arch"
PROOF_ORDER_ITEM = "unicorn-bouquet-SMA"
ACCEPTANCE_FIELDNAMES = {
    "source_quotation": "custom_lt_source_quotation",
    "accepted_by": "custom_lt_quote_acceptance_by",
    "accepted_email": "custom_lt_quote_acceptance_email",
    "accepted_on": "custom_lt_quote_acceptance_on",
    "acceptance_reference": "custom_lt_quote_acceptance_reference",
    "acceptance_payload": "custom_lt_quote_acceptance_payload",
}


class ContractFail(Exception):
    pass


def run() -> dict[str, object]:
    original_commit = frappe.db.commit
    intercepted_commits = []

    def no_commit(*args, **kwargs):
        intercepted_commits.append(True)

    try:
        frappe.db.commit = no_commit
        result = _run_contract()
        result["commit_calls_intercepted"] = len(intercepted_commits)
        result["rolled_back"] = True
        return result
    except ContractFail as exc:
        return {"ok": False, "failures": [str(exc)]}
    except Exception:
        return {"ok": False, "failures": [frappe.get_traceback()]}
    finally:
        frappe.db.commit = original_commit
        frappe.db.rollback()


def _run_contract() -> dict[str, object]:
    from locally_twisted.product_quote_acceptance import (
        create_draft_sales_order_from_accepted_product_quote,
        create_draft_sales_order_from_product_quote_token,
        issue_product_quote_acceptance_token,
    )

    _assert_acceptance_schema()
    quotation_name = _submitted_reviewed_product_quote()
    before = _guard_counts()
    sales_order = create_draft_sales_order_from_accepted_product_quote(
        quotation_name,
        acceptance={
            "accepted_by": "Cameron Test Customer",
            "accepted_email": "cameron-test@example.invalid",
            "accepted_on": nowdate(),
            "acceptance_reference": "rollback-contract-written-approval",
        },
    )
    after = _guard_counts()

    if sales_order.doctype != "Sales Order":
        raise ContractFail(f"acceptance helper returned wrong doctype: {sales_order.doctype}")
    if sales_order.docstatus != 0:
        raise ContractFail("accepted product quote must create a draft Sales Order only")
    if not sales_order.name:
        raise ContractFail("accepted product quote did not insert a draft Sales Order")
    if not sales_order.items:
        raise ContractFail("accepted product quote Sales Order has no line items")
    _assert_acceptance_context_preserved(sales_order, quotation_name)
    _assert_line_payload_preserved(sales_order.items[0])
    _assert_no_finance_or_email_mutations(before, after)
    _assert_placeholder_quote_blocks_acceptance()
    _assert_draft_quote_blocks_acceptance()
    _assert_missing_acceptance_blocks_loudly(quotation_name)
    _assert_missing_sales_order_acceptance_storage_blocks_loudly()
    _assert_non_ready_quote_status_blocks_token_and_acceptance()
    _assert_reused_token_does_not_create_duplicate_order()
    _assert_reused_token_with_cancelled_order_fails_without_duplicate()
    _assert_quote_accept_context_sanitizes_unexpected_preview_error()
    token_quote = _submitted_reviewed_product_quote()
    token_info = issue_product_quote_acceptance_token(
        token_quote,
        base_url="http://localhost:8081",
    )
    token_order = create_draft_sales_order_from_product_quote_token(
        token_info["token"],
        acceptance=_acceptance_payload(),
    )
    _assert_acceptance_context_preserved(token_order, token_quote)
    _assert_line_payload_preserved(token_order.items[0])
    _assert_expired_token_blocks_loudly()

    return {
        "ok": True,
        "quotation": quotation_name,
        "sales_order": sales_order.name,
        "token_sales_order": token_order.name,
        "acceptance_url": token_info.get("acceptance_url"),
        "draft_only": True,
        "invoice_creation_allowed": False,
        "payment_request_allowed": False,
        "email_send_allowed": False,
        "guard_counts_before": before,
        "guard_counts_after": after,
        "acceptance_fields": sorted(ACCEPTANCE_FIELDNAMES.values()),
    }


def _assert_acceptance_schema() -> None:
    meta = frappe.get_meta("Sales Order")
    missing = sorted(fieldname for fieldname in ACCEPTANCE_FIELDNAMES.values() if not meta.has_field(fieldname))
    if missing:
        raise ContractFail(f"Sales Order missing product quote acceptance fields: {missing}")


def _assert_acceptance_context_preserved(sales_order, quotation_name: str) -> None:
    expected = {
        ACCEPTANCE_FIELDNAMES["source_quotation"]: quotation_name,
        ACCEPTANCE_FIELDNAMES["accepted_by"]: "Cameron Test Customer",
        ACCEPTANCE_FIELDNAMES["accepted_email"]: "cameron-test@example.invalid",
        ACCEPTANCE_FIELDNAMES["accepted_on"]: nowdate(),
        ACCEPTANCE_FIELDNAMES["acceptance_reference"]: "rollback-contract-written-approval",
    }
    for fieldname, value in expected.items():
        if sales_order.get(fieldname) != value:
            raise ContractFail(f"Sales Order did not preserve {fieldname}: {sales_order.get(fieldname)!r}")
    payload = json.loads(sales_order.get(ACCEPTANCE_FIELDNAMES["acceptance_payload"]) or "{}")
    if payload.get("acceptance_reference") != "rollback-contract-written-approval":
        raise ContractFail(f"Sales Order acceptance payload is wrong: {payload}")


def _submitted_reviewed_product_quote(*, status: str = "Ready For Customer Review") -> str:
    quotation = _base_quotation("REVIEWED")
    quotation.set(QUOTATION_FIELDNAMES["status"], status)
    payload = _product_quote_payload()
    quotation.append(
        "items",
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
        },
    )
    quotation.insert(ignore_permissions=True)
    quotation.submit()
    return quotation.name


def _assert_placeholder_quote_blocks_acceptance() -> None:
    from locally_twisted.product_quote_acceptance import create_draft_sales_order_from_accepted_product_quote

    quotation = _base_quotation("PLACEHOLDER")
    payload = _product_quote_payload()
    quotation.append(
        "items",
        {
            "item_code": PRODUCT_QUOTE_REVIEW_ITEM,
            "qty": 1,
            "rate": 0,
            "price_list_rate": 0,
            "description": payload["summary"],
            LINE_FIELDNAMES["template_item"]: PROOF_PRODUCT_PAGE,
            LINE_FIELDNAMES["page_type"]: "complex_custom_product",
            LINE_FIELDNAMES["version"]: CONFIG_VERSION,
            LINE_FIELDNAMES["summary"]: payload["summary"],
            LINE_FIELDNAMES["json"]: json.dumps(payload, sort_keys=True),
        },
    )
    quotation.insert(ignore_permissions=True)
    quotation.submit()
    try:
        create_draft_sales_order_from_accepted_product_quote(
            quotation.name,
            acceptance=_acceptance_payload(),
        )
    except frappe.ValidationError as exc:
        if "pricing" not in str(exc).lower() and "placeholder" not in str(exc).lower():
            raise ContractFail(f"placeholder quote failed with unclear message: {exc}")
        return
    raise ContractFail("placeholder product quote should not become a Sales Order")


def _assert_draft_quote_blocks_acceptance() -> None:
    from locally_twisted.product_quote_acceptance import create_draft_sales_order_from_accepted_product_quote

    quotation = _base_quotation("DRAFT")
    payload = _product_quote_payload()
    quotation.append(
        "items",
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
        },
    )
    quotation.insert(ignore_permissions=True)
    try:
        create_draft_sales_order_from_accepted_product_quote(
            quotation.name,
            acceptance=_acceptance_payload(),
        )
    except frappe.ValidationError as exc:
        if "submit" not in str(exc).lower():
            raise ContractFail(f"draft quote failed with unclear message: {exc}")
        return
    raise ContractFail("draft product quote should not become a Sales Order")


def _assert_missing_acceptance_blocks_loudly(quotation_name: str) -> None:
    from locally_twisted.product_quote_acceptance import create_draft_sales_order_from_accepted_product_quote

    try:
        create_draft_sales_order_from_accepted_product_quote(quotation_name, acceptance={})
    except frappe.ValidationError as exc:
        if "accept" not in str(exc).lower():
            raise ContractFail(f"missing acceptance failed with unclear message: {exc}")
        return
    raise ContractFail("missing acceptance details should block Sales Order creation")


def _assert_missing_sales_order_acceptance_storage_blocks_loudly() -> None:
    from locally_twisted import product_quote_acceptance

    class MetaWithoutSourceQuote:
        def has_field(self, fieldname: str) -> bool:
            return fieldname != ACCEPTANCE_FIELDNAMES["source_quotation"]

    class FakeSalesOrder:
        def set(self, fieldname: str, value: object) -> None:
            raise ContractFail(f"missing acceptance storage was silently bypassed and set {fieldname}")

    class FakeQuotation:
        name = "ROLLBACK-QUOTATION"

    original_get_meta = product_quote_acceptance.frappe.get_meta

    def patched_get_meta(doctype: str):
        if doctype == "Sales Order":
            return MetaWithoutSourceQuote()
        return original_get_meta(doctype)

    try:
        product_quote_acceptance.frappe.get_meta = patched_get_meta
        product_quote_acceptance._copy_acceptance_context(
            FakeSalesOrder(),
            FakeQuotation(),
            _acceptance_payload(),
        )
    except frappe.ValidationError as exc:
        message = str(exc).lower()
        if "acceptance" not in message or "source" not in message:
            raise ContractFail(f"missing Sales Order acceptance storage failed unclearly: {exc}")
        return
    finally:
        product_quote_acceptance.frappe.get_meta = original_get_meta
    raise ContractFail("missing Sales Order acceptance storage should fail loudly")


def _assert_non_ready_quote_status_blocks_token_and_acceptance() -> None:
    from locally_twisted.product_quote_acceptance import (
        create_draft_sales_order_from_accepted_product_quote,
        issue_product_quote_acceptance_token,
        product_quote_acceptance_blockers,
    )

    quotation_name = _submitted_reviewed_product_quote(status="Needs Operator Review")
    quotation = frappe.get_doc("Quotation", quotation_name)
    blockers = product_quote_acceptance_blockers(quotation)
    if "product_quote_not_ready_for_customer_review" not in blockers:
        raise ContractFail(f"non-ready quote status did not return readiness blocker: {blockers}")

    for label, action in (
        ("token issuance", lambda: issue_product_quote_acceptance_token(quotation_name, base_url="http://localhost:8081")),
        (
            "Sales Order creation",
            lambda: create_draft_sales_order_from_accepted_product_quote(
                quotation_name,
                acceptance=_acceptance_payload(),
            ),
        ),
    ):
        try:
            action()
        except frappe.ValidationError as exc:
            if "review" not in str(exc).lower() and "ready" not in str(exc).lower():
                raise ContractFail(f"non-ready quote blocked {label} with unclear message: {exc}")
            continue
        raise ContractFail(f"non-ready quote status should block {label}")


def _assert_expired_token_blocks_loudly() -> None:
    from locally_twisted.product_quote_acceptance import (
        create_draft_sales_order_from_product_quote_token,
        issue_product_quote_acceptance_token,
    )

    quotation_name = _submitted_reviewed_product_quote()
    token_info = issue_product_quote_acceptance_token(
        quotation_name,
        base_url="http://localhost:8081",
        expires_on="2026-01-01",
    )
    try:
        create_draft_sales_order_from_product_quote_token(
            token_info["token"],
            acceptance=_acceptance_payload(),
        )
    except frappe.ValidationError as exc:
        if "expired" not in str(exc).lower():
            raise ContractFail(f"expired token failed with unclear message: {exc}")
        return
    raise ContractFail("expired quote acceptance token should not create a Sales Order")


def _assert_reused_token_does_not_create_duplicate_order() -> None:
    from locally_twisted.product_quote_acceptance import (
        create_draft_sales_order_from_product_quote_token,
        issue_product_quote_acceptance_token,
    )

    quotation_name = _submitted_reviewed_product_quote()
    token_info = issue_product_quote_acceptance_token(
        quotation_name,
        base_url="http://localhost:8081",
    )
    first_order = create_draft_sales_order_from_product_quote_token(
        token_info["token"],
        acceptance=_acceptance_payload(),
    )
    frappe.db.set_value("Sales Order", first_order.name, "docstatus", 1, update_modified=False)
    before_count = frappe.db.count(
        "Sales Order",
        {ACCEPTANCE_FIELDNAMES["source_quotation"]: quotation_name},
    )
    second_order = create_draft_sales_order_from_product_quote_token(
        token_info["token"],
        acceptance=_acceptance_payload(),
    )
    after_count = frappe.db.count(
        "Sales Order",
        {ACCEPTANCE_FIELDNAMES["source_quotation"]: quotation_name},
    )
    if second_order.name != first_order.name:
        raise ContractFail(
            f"reused quote token returned a different Sales Order: {first_order.name} vs {second_order.name}"
        )
    if after_count != before_count:
        raise ContractFail("reused quote token created a duplicate Sales Order")


def _assert_reused_token_with_cancelled_order_fails_without_duplicate() -> None:
    from locally_twisted.product_quote_acceptance import (
        create_draft_sales_order_from_product_quote_token,
        issue_product_quote_acceptance_token,
    )

    quotation_name = _submitted_reviewed_product_quote()
    token_info = issue_product_quote_acceptance_token(
        quotation_name,
        base_url="http://localhost:8081",
    )
    first_order = create_draft_sales_order_from_product_quote_token(
        token_info["token"],
        acceptance=_acceptance_payload(),
    )
    frappe.db.set_value("Sales Order", first_order.name, "docstatus", 2, update_modified=False)
    before_count = frappe.db.count(
        "Sales Order",
        {ACCEPTANCE_FIELDNAMES["source_quotation"]: quotation_name},
    )
    try:
        create_draft_sales_order_from_product_quote_token(
            token_info["token"],
            acceptance=_acceptance_payload(),
        )
    except frappe.ValidationError as exc:
        message = str(exc).lower()
        if "cancelled" not in message or "fresh approval link" not in message:
            raise ContractFail(f"cancelled order reuse failed with unclear message: {exc}")
    else:
        raise ContractFail("reused quote token with cancelled order should fail loudly")
    after_count = frappe.db.count(
        "Sales Order",
        {ACCEPTANCE_FIELDNAMES["source_quotation"]: quotation_name},
    )
    if after_count != before_count:
        raise ContractFail("reused quote token with cancelled order created a duplicate Sales Order")


def _assert_quote_accept_context_sanitizes_unexpected_preview_error() -> None:
    from frappe import _dict
    from locally_twisted.www import quote_accept

    original_preview = quote_accept.product_quote_acceptance_preview
    original_form_dict = frappe.form_dict
    original_log_error = frappe.log_error
    log_calls = []

    def broken_preview(token: str):
        raise RuntimeError("custom_lt_secret_field DocType setup exploded")

    def capture_log_error(*args, **kwargs):
        log_calls.append({"args": args, "kwargs": kwargs})
        return "ROLLBACK-QUOTE-ACCEPT-ERROR"

    try:
        quote_accept.product_quote_acceptance_preview = broken_preview
        frappe.form_dict = _dict({"token": "bad-token"})
        frappe.log_error = capture_log_error
        context = quote_accept.get_context(_dict())
    finally:
        quote_accept.product_quote_acceptance_preview = original_preview
        frappe.form_dict = original_form_dict
        frappe.log_error = original_log_error

    message = str(context.get("acceptance_error") or "")
    for unsafe in ("custom_lt_", "DocType", "setup exploded", "RuntimeError"):
        if unsafe in message:
            raise ContractFail(f"quote accept page leaked raw exception text: {message}")
    if "Tiny snag" not in message or "fresh link" not in message:
        raise ContractFail(f"quote accept page did not show safe approval-link failure copy: {message}")
    if not log_calls:
        raise ContractFail("quote accept page did not log unexpected preview failure")


def _assert_line_payload_preserved(order_row) -> None:
    for fieldname in LINE_FIELDNAMES.values():
        if not order_row.get(fieldname):
            raise ContractFail(f"Sales Order Item did not receive product quote field {fieldname}")
    payload = json.loads(order_row.get(LINE_FIELDNAMES["json"]))
    if payload.get("source") != "lt_product_page_quote_runtime":
        raise ContractFail(f"Sales Order Item copied wrong product quote payload: {payload}")
    if payload.get("website_item_code") != PROOF_PRODUCT_PAGE:
        raise ContractFail(f"Sales Order Item lost requested product page: {payload}")
    if payload.get("selected_options", {}).get("Arch Size") != "20ft":
        raise ContractFail(f"Sales Order Item lost selected product quote options: {payload}")


def _assert_no_finance_or_email_mutations(before: dict[str, int], after: dict[str, int]) -> None:
    for doctype in ("Sales Invoice", "Payment Request", "Email Queue", "Communication"):
        if after.get(doctype) != before.get(doctype):
            raise ContractFail(f"{doctype} changed during accepted product quote Sales Order draft")


def _base_quotation(label: str):
    token = str(int(time.time() * 1000))
    lead_name = _lead_name(label, token)
    return frappe.get_doc(
        {
            "doctype": "Quotation",
            "quotation_to": "Lead",
            "party_name": lead_name,
            "transaction_date": nowdate(),
            "valid_till": add_days(nowdate(), 14),
            "order_type": "Sales",
            "company": _company_name(),
            "currency": "USD",
            "selling_price_list": PRICE_LIST,
            "ignore_pricing_rule": 1,
            "contact_email": f"{label.lower()}-{token}@example.invalid",
            "customer_name": f"LT Accepted Product Quote {label} {token}",
            "terms": "Customer accepted reviewed quote by written confirmation. Payment path remains separate.",
            "custom_event_date": add_days(nowdate(), 21),
            "custom_event_location": "Ogden, Utah",
            QUOTATION_FIELDNAMES["source_lead"]: lead_name,
            QUOTATION_FIELDNAMES["template_item"]: PROOF_PRODUCT_PAGE,
            QUOTATION_FIELDNAMES["page_type"]: "complex_custom_product",
            QUOTATION_FIELDNAMES["commerce_lane"]: "quote_first",
            QUOTATION_FIELDNAMES["version"]: CONFIG_VERSION,
            QUOTATION_FIELDNAMES["summary"]: _product_quote_payload()["summary"],
            QUOTATION_FIELDNAMES["json"]: json.dumps(_product_quote_payload(), sort_keys=True),
            QUOTATION_FIELDNAMES["status"]: "Ready For Customer Review",
        }
    )


def _lead_name(label: str, token: str) -> str:
    lead = frappe.get_doc(
        {
            "doctype": "Lead",
            "first_name": f"LT Accepted Quote {label} {token}",
            "email_id": f"lt-accepted-{label.lower()}-{token}@example.invalid",
            "source": "Website",
            "status": "Open",
        }
    )
    lead.insert(ignore_permissions=True)
    return lead.name


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


def _acceptance_payload() -> dict[str, str]:
    return {
        "accepted_by": "Cameron Test Customer",
        "accepted_email": "cameron-test@example.invalid",
        "accepted_on": nowdate(),
        "acceptance_reference": "rollback-contract-written-approval",
    }


def _guard_counts() -> dict[str, int]:
    return {
        doctype: int(frappe.db.count(doctype))
        for doctype in ("Sales Invoice", "Payment Request", "Email Queue", "Communication")
        if frappe.db.exists("DocType", doctype)
    }


def _company_name() -> str:
    company = frappe.defaults.get_user_default("Company") or frappe.db.get_value("Company", {}, "name")
    if not company:
        raise ContractFail("ERPNext needs a company before product quote acceptance can be tested")
    return company
