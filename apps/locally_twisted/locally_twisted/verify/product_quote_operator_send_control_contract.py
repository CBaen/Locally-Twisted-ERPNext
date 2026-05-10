"""Rollback-safe contract for the operator product-quote send control."""
from __future__ import annotations

import frappe
from pathlib import Path

from locally_twisted.product_quote_runtime import QUOTATION_FIELDNAMES
from locally_twisted.verify.product_quote_customer_delivery_contract import (
    BUSINESS_BCC,
    _assert_no_order_finance_or_email_mutations,
    _guard_counts,
    _submitted_reviewed_product_quote,
)


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
    method = _operator_method()
    _assert_operator_desk_control_registered()

    quotation_name = _submitted_reviewed_product_quote()
    sent_messages.clear()
    before = _guard_counts()
    result = method(
        quotation_name,
        recipient_email="cameronbpaul@example.invalid",
        base_url="http://localhost:8081",
    )
    after = _guard_counts()

    if result.get("operator_control") is not True:
        raise ContractFail("operator send control did not mark the result as operator-owned")
    if result.get("customer_delivery_enabled") is not True:
        raise ContractFail("operator send control did not mark customer delivery enabled for the reviewed quote")
    if result.get("business_bcc") != BUSINESS_BCC:
        raise ContractFail(f"operator send control used wrong BCC: {result.get('business_bcc')}")
    if len(sent_messages) != 1:
        raise ContractFail(f"operator send control should call sendmail once, found {len(sent_messages)}")
    if sent_messages[0].get("recipients") != ["cameronbpaul@example.invalid"]:
        raise ContractFail(f"operator send control used wrong recipient: {sent_messages[0].get('recipients')}")
    if sent_messages[0].get("bcc") != [BUSINESS_BCC]:
        raise ContractFail(f"operator send control did not BCC the business: {sent_messages[0].get('bcc')}")
    if "quote-accept?token=" not in str(sent_messages[0].get("message") or ""):
        raise ContractFail("operator send control email did not include the approval link")
    _assert_no_order_finance_or_email_mutations(before, after)
    sendmail_calls = len(sent_messages)

    _assert_not_ready_quote_blocks_loudly(method, quotation_name, sent_messages)

    return {
        "ok": True,
        "quotation": quotation_name,
        "operator_control": result.get("operator_control"),
        "customer_delivery_enabled": result.get("customer_delivery_enabled"),
        "business_bcc": result.get("business_bcc"),
        "sendmail_calls": sendmail_calls,
        "guard_counts_before": before,
        "guard_counts_after": after,
    }


def _operator_method():
    method = frappe.get_attr("locally_twisted.product_quote_operator_send.send_reviewed_product_quote_to_customer")
    if method in getattr(frappe, "guest_methods", set()):
        raise ContractFail("operator send control must not allow guest calls")
    if method not in getattr(frappe, "whitelisted", set()):
        raise ContractFail("operator send control must be a whitelisted Desk method")
    return method


def _assert_operator_desk_control_registered() -> None:
    hooks = frappe.get_hooks("doctype_js") or {}
    quotation_hooks = hooks.get("Quotation") or []
    if isinstance(quotation_hooks, str):
        quotation_hooks = [quotation_hooks]
    expected = "public/js/lt-product-quote-quotation.js"
    if expected not in quotation_hooks:
        raise ContractFail(f"Quotation doctype_js hook missing {expected}")

    js_path = Path(frappe.get_app_path("locally_twisted", "public", "js", "lt-product-quote-quotation.js"))
    source = js_path.read_text(encoding="utf-8") if js_path.exists() else ""
    for marker in (
        "Send Approval Link",
        "send_reviewed_product_quote_to_customer",
        "Ready For Customer Review",
        BUSINESS_BCC,
    ):
        if marker not in source:
            raise ContractFail(f"operator Quotation JS missing marker {marker}")


def _assert_not_ready_quote_blocks_loudly(method, quotation_name: str, sent_messages: list[dict]) -> None:
    frappe.db.set_value(
        "Quotation",
        quotation_name,
        QUOTATION_FIELDNAMES["status"],
        "Draft Quotation Created",
        update_modified=False,
    )
    sent_messages.clear()
    try:
        method(
            quotation_name,
            recipient_email="cameronbpaul@example.invalid",
            base_url="http://localhost:8081",
        )
    except frappe.ValidationError as exc:
        message = str(exc)
        if "Ready For Customer Review" not in message and "review" not in message.lower():
            raise ContractFail(f"not-ready quote failed with unclear message: {message}")
        if sent_messages:
            raise ContractFail("not-ready quote should not call sendmail")
        return
    raise ContractFail("operator send control should block quotes not marked Ready For Customer Review")
