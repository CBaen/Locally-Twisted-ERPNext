"""Fake-data contract for internal product quote operator review."""
from __future__ import annotations

import json

import frappe
from frappe import _dict

from locally_twisted.product_page_runtime import CONFIG_VERSION, LINE_FIELDNAMES
from locally_twisted.product_quote_operator_review import render_from_quotations
from locally_twisted.product_quote_runtime import PRODUCT_QUOTE_REVIEW_ITEM, QUOTATION_FIELDNAMES


FIXED_GENERATED_AT = "2026-05-10T00:00:00"
GUARD_COUNTS = {
    "Quotation": 2,
    "Lead": 12,
    "Customer": 4,
    "Sales Order": 8,
    "Sales Invoice": 1,
    "Payment Request": 8,
    "Email Queue": 30,
    "Communication": 12,
    "Comment": 0,
    "Error Log": 0,
}


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
    finally:
        frappe.db.commit = original_commit
        frappe.db.rollback()


def _run_contract() -> dict[str, object]:
    scenario_specs = (
        ("placeholder_zero_price_blocks_customer_review", _placeholder_quote(), _expect_placeholder_blocked),
        ("reviewed_quote_is_ready_but_still_no_send_or_order", _reviewed_quote(), _expect_ready_draft_only),
        ("malformed_payload_blocks_customer_review", _malformed_quote(), _expect_malformed_blocked),
        (
            "customer_quote_uses_linked_contact_email",
            _customer_quote_with_linked_contact_email(),
            _expect_ready_draft_only,
        ),
    )
    scenarios = []
    failures = []
    for scenario_id, quotation, expectation in scenario_specs:
        result = _render([quotation])
        scenario_failures = expectation(result)
        scenarios.append(
            {
                "id": scenario_id,
                "passed": not scenario_failures,
                "review_count": result.get("review_count"),
                "ready_count": result.get("ready_count"),
                "blocked_count": result.get("blocked_count"),
                "failures": scenario_failures,
            }
        )
        failures.extend(f"{scenario_id}: {failure}" for failure in scenario_failures)

    empty = _render([])
    if empty.get("ok") is not True or empty.get("review_count") != 0:
        failures.append("empty review should be ok with zero rows")

    return {
        "ok": not failures,
        "generated_at": FIXED_GENERATED_AT,
        "read_only": True,
        "send_allowed": False,
        "customer_delivery_enabled": False,
        "sales_order_creation_allowed": False,
        "payment_request_allowed": False,
        "scenario_count": len(scenarios),
        "scenarios": scenarios,
        "failures": failures,
    }


def _render(quotations: list[_dict]) -> dict[str, object]:
    return render_from_quotations(
        quotations,
        guard_counts_before=dict(GUARD_COUNTS),
        guard_counts_after=dict(GUARD_COUNTS),
        generated_at=FIXED_GENERATED_AT,
    )


def _placeholder_quote() -> _dict:
    payload = _payload(summary="Requested product page quote: Classic Arch; Arch Size: 20ft")
    return _quotation(
        name="SAL-QTN-PLACEHOLDER",
        grand_total=0,
        terms="Human-reviewed quote acceptance path required before send.",
        items=[
            _item(PRODUCT_QUOTE_REVIEW_ITEM, 0, payload),
        ],
        payload=payload,
    )


def _reviewed_quote() -> _dict:
    payload = _payload(summary="Requested product page quote: Classic Arch; Arch Size: 20ft; colors reviewed")
    return _quotation(
        name="SAL-QTN-REVIEWED",
        grand_total=650,
        terms="Customer may approve the reviewed quote by written confirmation. Payment path is separate.",
        items=[
            _item("CUSTOM-ARCH-SCOPE", 650, payload),
        ],
        payload=payload,
    )


def _malformed_quote() -> _dict:
    quote = _reviewed_quote()
    quote.name = "SAL-QTN-MALFORMED"
    quote[QUOTATION_FIELDNAMES["json"]] = "{not-json"
    quote["items"][0][LINE_FIELDNAMES["json"]] = "{not-json"
    return quote


def _customer_quote_with_linked_contact_email() -> _dict:
    token = "operator-review-linked-contact"
    customer = frappe.get_doc(
        {
            "doctype": "Customer",
            "customer_name": f"LT {token}",
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
            "last_name": "Quote Contact",
            "email_ids": [{"email_id": "linked-contact@example.invalid", "is_primary": 1}],
            "links": [{"link_doctype": "Customer", "link_name": customer.name}],
        }
    )
    contact.insert(ignore_permissions=True)

    quote = _reviewed_quote()
    quote.name = "SAL-QTN-CUSTOMER-LINKED-CONTACT"
    quote.quotation_to = "Customer"
    quote.party_name = customer.name
    quote.customer_name = customer.customer_name
    quote.contact_email = ""
    return quote


def _quotation(*, name: str, grand_total: float, terms: str, items: list[_dict], payload: dict[str, object]) -> _dict:
    return _dict(
        {
            "name": name,
            "docstatus": 0,
            "quotation_to": "Lead",
            "party_name": "CRM-LEAD-FAKE",
            "customer_name": "Product Quote Buyer",
            "contact_email": "buyer@example.invalid",
            "transaction_date": "2026-05-10",
            "valid_till": "2026-05-24",
            "grand_total": grand_total,
            "currency": "USD",
            "terms": terms,
            "custom_event_date": "2026-06-01",
            "custom_event_location": "Ogden, Utah",
            QUOTATION_FIELDNAMES["source_lead"]: "CRM-LEAD-FAKE",
            QUOTATION_FIELDNAMES["template_item"]: "classic-arch",
            QUOTATION_FIELDNAMES["page_type"]: "complex_custom_product",
            QUOTATION_FIELDNAMES["commerce_lane"]: "quote_first",
            QUOTATION_FIELDNAMES["version"]: CONFIG_VERSION,
            QUOTATION_FIELDNAMES["summary"]: payload["summary"],
            QUOTATION_FIELDNAMES["json"]: json.dumps(payload, sort_keys=True),
            QUOTATION_FIELDNAMES["status"]: "Draft Quotation Created",
            "items": items,
        }
    )


def _item(item_code: str, rate: float, payload: dict[str, object]) -> _dict:
    return _dict(
        {
            "item_code": item_code,
            "item_name": item_code.replace("-", " ").title(),
            "qty": 1,
            "rate": rate,
            "amount": rate,
            LINE_FIELDNAMES["template_item"]: "classic-arch",
            LINE_FIELDNAMES["page_type"]: "complex_custom_product",
            LINE_FIELDNAMES["version"]: CONFIG_VERSION,
            LINE_FIELDNAMES["summary"]: payload["summary"],
            LINE_FIELDNAMES["json"]: json.dumps(payload, sort_keys=True),
        }
    )


def _payload(*, summary: str) -> dict[str, object]:
    return {
        "schema_version": CONFIG_VERSION,
        "source": "lt_product_page_quote_runtime",
        "website_item_code": "classic-arch",
        "product_page_type": "complex_custom_product",
        "commerce_lane": "quote_first",
        "summary": summary,
        "selected_options": {"Arch Size": "20ft"},
        "customizations": [{"label": "Color notes", "value": "White, gold, navy"}],
        "add_ons": [],
    }


def _first_leaf(doctype: str) -> str:
    value = frappe.db.get_value(doctype, {"is_group": 0}, "name") or frappe.db.get_value(doctype, {}, "name")
    if not value:
        raise RuntimeError(f"Missing {doctype} record for product quote operator-review contract")
    return value


def _first_review(result: dict[str, object]) -> dict[str, object]:
    return (result.get("reviews") or [{}])[0]


def _expect_placeholder_blocked(result: dict[str, object]) -> list[str]:
    failures = _expect_boundaries(result)
    review = _first_review(result)
    blockers = review.get("blockers") or []
    for expected in (
        "replace_placeholder_review_line_with_real_scope_and_pricing",
        "required_field:reviewed_product_quote_pricing",
    ):
        if expected not in blockers:
            failures.append(f"placeholder quote missing blocker {expected}")
    if review.get("ready_for_customer_review") is not False:
        failures.append("placeholder quote should not be ready for customer review")
    return failures


def _expect_ready_draft_only(result: dict[str, object]) -> list[str]:
    failures = _expect_boundaries(result)
    review = _first_review(result)
    if review.get("ready_for_customer_review") is not True:
        failures.append(f"reviewed quote should be internally ready, blockers={review.get('blockers')}")
    if review.get("status") != "Ready For Customer Review":
        failures.append(f"reviewed quote status wrong: {review.get('status')}")
    for forbidden in ("send_allowed", "customer_delivery_enabled", "sales_order_creation_allowed", "payment_request_allowed"):
        if result.get(forbidden) is not False or review.get(forbidden) is not False:
            failures.append(f"reviewed quote must remain no-send/no-order for {forbidden}")
    return failures


def _expect_malformed_blocked(result: dict[str, object]) -> list[str]:
    failures = _expect_boundaries(result)
    review = _first_review(result)
    blockers = review.get("blockers") or []
    if not any(str(blocker).startswith("malformed_product_quote_payload") for blocker in blockers):
        failures.append(f"malformed quote did not block on payload: {blockers}")
    if review.get("ready_for_customer_review") is not False:
        failures.append("malformed quote should not be ready")
    return failures


def _expect_boundaries(result: dict[str, object]) -> list[str]:
    failures = []
    for fieldname in (
        "read_only",
    ):
        if result.get(fieldname) is not True:
            failures.append(f"result is not marked {fieldname}")
    for fieldname in (
        "send_allowed",
        "customer_delivery_enabled",
        "sales_order_creation_allowed",
        "payment_request_allowed",
    ):
        if result.get(fieldname) is not False:
            failures.append(f"result allows forbidden action {fieldname}")
    if result.get("ok") is not True:
        failures.append(f"review render failed: {result.get('failures')}")
    return failures
