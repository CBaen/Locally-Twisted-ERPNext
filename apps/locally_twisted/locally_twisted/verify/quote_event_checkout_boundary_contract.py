"""Verify Phase 4 quote/event checkout boundaries.

This verifier is read-only/rollback-safe. It proves complex/event and
needs-review product pages remain quote-first examples and cannot slip into
paid checkout through the public product controls, cart API, direct checkout
URL, or stale localStorage payloads.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import frappe

from locally_twisted.product_page_runtime import CONFIG_VERSION
from locally_twisted.verify.website_item_classification_contract import (
    HIDE_OR_NEEDS_REVIEW,
    QUOTE_FIRST,
)


class ContractFail(Exception):
    pass


COUNT_DOCTYPES = (
    "Customer",
    "Contact",
    "Address",
    "Sales Order",
    "Payment Request",
    "Payment Entry",
    "Sales Invoice",
    "Communication",
    "Email Queue",
)


def run() -> dict[str, Any]:
    original_commit = frappe.db.commit
    intercepted_commits: list[bool] = []

    def no_commit(*args, **kwargs):
        intercepted_commits.append(True)

    before_counts = _counts()
    try:
        frappe.db.commit = no_commit
        result = _run_contract(before_counts)
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


def _run_contract(before_counts: dict[str, int]) -> dict[str, Any]:
    precedence_evidence = _assert_contract_precedence_fail_closed()
    _assert_product_page_templates_route_to_quote_cta()
    quote_rows = _assert_boundaries_for_lane(
        item_codes=QUOTE_FIRST,
        expected_page_type="complex_custom_product",
        expected_commerce_lane="quote_first",
    )
    needs_review_rows = _assert_boundaries_for_lane(
        item_codes=HIDE_OR_NEEDS_REVIEW,
        expected_page_type="needs_review",
        expected_commerce_lane="needs_review",
    )
    after_counts = _counts()
    survivor_deltas = {
        doctype: after_counts[doctype] - before_counts[doctype]
        for doctype in COUNT_DOCTYPES
        if after_counts[doctype] != before_counts[doctype]
    }
    if survivor_deltas:
        raise ContractFail(f"Phase 4 boundary verifier created records unexpectedly: {survivor_deltas}")

    malformed_config_evidence = _assert_malformed_and_stale_config_fail_loudly(
        quote_candidate=quote_rows[0]["candidate_item_code"],
        needs_review_candidate=needs_review_rows[0]["candidate_item_code"],
    )
    no_candidate_evidence = _assert_no_sellable_candidate_fail_closed()

    all_rows = quote_rows + needs_review_rows
    return {
        "ok": True,
        "quote_first_count": len(quote_rows),
        "needs_review_count": len(needs_review_rows),
        "cart_api_blocked_count": sum(1 for row in all_rows if row.get("cart_api") == "blocked_quote_required"),
        "direct_checkout_url_blocked_count": sum(1 for row in all_rows if row.get("direct_checkout_url") == "blocked_not_found"),
        "stale_localstorage_blocked_count": sum(1 for row in all_rows if row.get("stale_localstorage") == "blocked_quote_required"),
        "no_sellable_candidate_count": sum(1 for row in all_rows if not row.get("candidate_item_code")),
        "contract_precedence": precedence_evidence,
        "malformed_and_stale_config": malformed_config_evidence,
        "no_sellable_candidate_synthetic": no_candidate_evidence,
        "quote_first_rows": quote_rows,
        "needs_review_rows": needs_review_rows,
        "quote_first_samples": _sample_rows(quote_rows),
        "needs_review_samples": _sample_rows(needs_review_rows),
        "record_count_deltas": survivor_deltas,
    }


def _assert_contract_precedence_fail_closed() -> list[dict[str, Any]]:
    from locally_twisted.product_page_runtime import resolved_product_page_contract_values

    inferred_checkout = {"product_page_type": "simple_product", "commerce_lane": "checkout"}
    inferred_quote = {"product_page_type": "complex_custom_product", "commerce_lane": "quote_first"}
    cases = [
        {
            "case": "explicit_page_needs_review_blank_lane_does_not_infer_checkout",
            "explicit_page_type": "needs_review",
            "explicit_commerce_lane": "",
            "inferred": inferred_checkout,
            "expected": {"product_page_type": "needs_review", "commerce_lane": "needs_review"},
        },
        {
            "case": "blank_page_explicit_lane_needs_review_does_not_infer_checkout",
            "explicit_page_type": "",
            "explicit_commerce_lane": "needs_review",
            "inferred": inferred_checkout,
            "expected": {"product_page_type": "needs_review", "commerce_lane": "needs_review"},
        },
        {
            "case": "blank_fields_never_infer_paid_checkout",
            "explicit_page_type": "",
            "explicit_commerce_lane": "",
            "inferred": inferred_checkout,
            "expected": {"product_page_type": "needs_review", "commerce_lane": "needs_review"},
        },
        {
            "case": "partial_explicit_checkout_without_simple_page_type_fails_closed",
            "explicit_page_type": "",
            "explicit_commerce_lane": "checkout",
            "inferred": inferred_checkout,
            "expected": {"product_page_type": "needs_review", "commerce_lane": "needs_review"},
        },
        {
            "case": "explicit_simple_checkout_still_allowed",
            "explicit_page_type": "simple_product",
            "explicit_commerce_lane": "checkout",
            "inferred": inferred_quote,
            "expected": {"product_page_type": "simple_product", "commerce_lane": "checkout"},
        },
        {
            "case": "explicit_complex_quote_first_still_allowed",
            "explicit_page_type": "complex_custom_product",
            "explicit_commerce_lane": "quote_first",
            "inferred": inferred_checkout,
            "expected": {"product_page_type": "complex_custom_product", "commerce_lane": "quote_first"},
        },
    ]
    evidence = []
    for case in cases:
        resolved = resolved_product_page_contract_values(
            explicit_page_type=case["explicit_page_type"],
            explicit_commerce_lane=case["explicit_commerce_lane"],
            inferred=case["inferred"],
        )
        if resolved != case["expected"]:
            raise ContractFail(f"contract precedence case {case['case']} resolved {resolved}, expected {case['expected']}")
        evidence.append({"case": case["case"], "resolved": resolved})
    return evidence


def _assert_product_page_templates_route_to_quote_cta() -> None:
    app_path = Path(frappe.get_app_path("locally_twisted"))
    item_details = (app_path / "templates/generators/item/item_details.html").read_text(encoding="utf-8")
    item_quote_first = (app_path / "templates/generators/item/item_quote_first.html").read_text(encoding="utf-8")

    required_details_markers = (
        "lt_product_runtime.is_quote_first or lt_product_runtime.needs_review",
        'include "templates/generators/item/item_quote_first.html"',
        "lt_product_runtime.is_ready_to_order",
        'include "templates/generators/item/item_add_to_cart.html"',
    )
    for marker in required_details_markers:
        if marker not in item_details:
            raise ContractFail(f"product detail template missing quote/checkout branch marker: {marker}")

    required_quote_markers = (
        "lt-product__cart--quote-first",
        "Request a Quote",
        "lt_product_quote_handoff_v1",
        "data-commerce-lane",
        "needs_operator_review: true",
    )
    for marker in required_quote_markers:
        if marker not in item_quote_first:
            raise ContractFail(f"quote-first template missing CTA/payload marker: {marker}")

    forbidden_quote_markers = ("btn-add-to-cart", "update_cart({")
    for marker in forbidden_quote_markers:
        if marker in item_quote_first:
            raise ContractFail(f"quote-first template contains checkout/cart marker: {marker}")


def _assert_boundaries_for_lane(
    *,
    item_codes: tuple[str, ...],
    expected_page_type: str,
    expected_commerce_lane: str,
) -> list[dict[str, Any]]:
    rows = []
    for website_item_code in item_codes:
        row = _assert_stored_and_runtime_contract(
            website_item_code,
            expected_page_type=expected_page_type,
            expected_commerce_lane=expected_commerce_lane,
        )
        candidate = _sellable_candidate(website_item_code)
        evidence = {
            "website_item_code": website_item_code,
            "stored_contract": f"{row.get('lt_product_page_type')}|{row.get('lt_commerce_lane')}",
            "runtime_context": row["runtime_context"],
            "candidate_item_code": candidate,
        }
        _assert_no_checkout_add_ons(website_item_code)
        if candidate:
            _assert_cart_api_blocks(candidate)
            _assert_direct_checkout_url_blocks(candidate)
            _assert_stale_localstorage_blocks(candidate, website_item_code)
            evidence.update(
                {
                    "cart_api": "blocked_quote_required",
                    "direct_checkout_url": "blocked_not_found",
                    "stale_localstorage": "blocked_quote_required",
                }
            )
        else:
            evidence.update(
                {
                    "cart_api": "no_enabled_sellable_item",
                    "direct_checkout_url": "no_enabled_sellable_item",
                    "stale_localstorage": "no_enabled_sellable_item",
                }
            )
        rows.append(evidence)
    return rows


def _assert_stored_and_runtime_contract(
    website_item_code: str,
    *,
    expected_page_type: str,
    expected_commerce_lane: str,
) -> dict[str, Any]:
    from locally_twisted.product_options import get_product_page_runtime_context
    from locally_twisted.product_page_runtime import product_page_contract_for_website_item

    row = frappe.db.get_value(
        "Website Item",
        {"item_code": website_item_code},
        ["name", "item_code", "published", "lt_product_page_type", "lt_commerce_lane"],
        as_dict=True,
    )
    if not row:
        raise ContractFail(f"missing Website Item for {website_item_code}")
    if row.get("lt_product_page_type") != expected_page_type or row.get("lt_commerce_lane") != expected_commerce_lane:
        raise ContractFail(
            f"{website_item_code} stored contract should be "
            f"{expected_page_type}|{expected_commerce_lane}, found "
            f"{row.get('lt_product_page_type')}|{row.get('lt_commerce_lane')}"
        )

    contract = product_page_contract_for_website_item(website_item_code)
    actual = (contract.get("product_page_type"), contract.get("commerce_lane"))
    expected = (expected_page_type, expected_commerce_lane)
    if actual != expected:
        raise ContractFail(f"{website_item_code} runtime contract should be {expected}, found {actual}")

    runtime = get_product_page_runtime_context(website_item_code)
    if runtime.get("is_ready_to_order"):
        raise ContractFail(f"{website_item_code} runtime context is ready-to-order despite {expected_commerce_lane}")
    if expected_commerce_lane == "quote_first" and not runtime.get("is_quote_first"):
        raise ContractFail(f"{website_item_code} runtime context did not mark quote-first: {runtime}")
    if expected_commerce_lane == "needs_review" and not runtime.get("needs_review"):
        raise ContractFail(f"{website_item_code} runtime context did not mark needs-review: {runtime}")

    row["runtime_context"] = {
        "product_page_type": runtime.get("product_page_type"),
        "commerce_lane": runtime.get("commerce_lane"),
        "is_quote_first": bool(runtime.get("is_quote_first")),
        "needs_review": bool(runtime.get("needs_review")),
        "is_ready_to_order": bool(runtime.get("is_ready_to_order")),
    }
    return row


def _assert_no_checkout_add_ons(website_item_code: str) -> None:
    from locally_twisted.product_options import get_checkout_add_on_options

    options = get_checkout_add_on_options(website_item_code)
    if options:
        raise ContractFail(f"{website_item_code} exposed checkout add-on options despite quote/review lane: {options}")


def _sellable_candidate(website_item_code: str) -> str | None:
    variant = frappe.db.get_value(
        "Item",
        {"variant_of": website_item_code, "disabled": 0, "has_variants": 0},
        "item_code",
        order_by="item_code asc",
    )
    if variant:
        return str(variant)

    item = frappe.db.get_value(
        "Item",
        {"item_code": website_item_code, "disabled": 0, "has_variants": 0},
        "item_code",
    )
    return str(item) if item else None


def _assert_cart_api_blocks(candidate_item_code: str) -> None:
    from locally_twisted.api.cart import resolve_cart_item_for_sale_with_reason

    resolved, reason = resolve_cart_item_for_sale_with_reason(candidate_item_code)
    if resolved:
        raise ContractFail(f"{candidate_item_code} resolved as purchasable cart item despite quote/review lane: {resolved}")
    if reason != "quote_required":
        raise ContractFail(f"{candidate_item_code} cart API should block as quote_required, found {reason!r}")


def _assert_direct_checkout_url_blocks(candidate_item_code: str) -> None:
    from locally_twisted.www.checkout import get_context

    original_form_dict = getattr(frappe, "form_dict", None)
    try:
        frappe.form_dict = frappe._dict({"item": candidate_item_code, "qty": "1"})
        try:
            context = get_context(frappe._dict())
        except Exception as exc:  # Frappe raises PageDoesNotExistError for blocked buy-now URLs.
            if exc.__class__.__name__ == "PageDoesNotExistError":
                return
            raise
        if getattr(context, "item", None):
            raise ContractFail(f"direct /checkout?item= URL rendered checkout item for {candidate_item_code}: {context.item}")
    finally:
        if original_form_dict is None:
            try:
                delattr(frappe, "form_dict")
            except AttributeError:
                pass
        else:
            frappe.form_dict = original_form_dict

    raise ContractFail(f"direct /checkout?item= URL did not fail closed for {candidate_item_code}")


def _assert_stale_localstorage_blocks(candidate_item_code: str, website_item_code: str) -> None:
    from locally_twisted.www.checkout import _resolve_cart_items, _resolve_sale_lines

    payload = [
        {
            "item_code": candidate_item_code,
            "qty": 1,
            "configuration": _lying_checkout_configuration(candidate_item_code, website_item_code),
        }
    ]
    cart_items = _resolve_cart_items("", 1, json.dumps(payload))
    try:
        _resolve_sale_lines(cart_items)
    except frappe.ValidationError as exc:
        if "needs a quote" not in str(exc):
            raise ContractFail(f"stale localStorage rejection for {candidate_item_code} had unexpected message: {exc}")
        return
    raise ContractFail(f"stale localStorage payload entered checkout sale-line resolution for {candidate_item_code}")


def _assert_malformed_and_stale_config_fail_loudly(
    *,
    quote_candidate: str,
    needs_review_candidate: str,
) -> dict[str, Any]:
    from locally_twisted.www.checkout import _resolve_cart_items

    evidence: dict[str, Any] = {}
    malformed_cases = {
        "malformed_items_json": "not-json",
        "non_list_items_json": json.dumps({"item_code": quote_candidate}),
    }
    for case_name, payload in malformed_cases.items():
        try:
            _resolve_cart_items("", 1, payload)
        except frappe.ValidationError as exc:
            if "cart details did not come through cleanly" not in str(exc):
                raise ContractFail(f"{case_name} failed with unexpected message: {exc}")
            evidence[case_name] = "blocked_validation_error"
        else:
            raise ContractFail(f"{case_name} should fail before sale-line resolution")

    for case_name, candidate in {
        "quote_first_old_schema_configuration": quote_candidate,
        "needs_review_old_schema_configuration": needs_review_candidate,
    }.items():
        stale_payload = json.dumps(
            [
                {
                    "item_code": candidate,
                    "qty": 1,
                    "configuration": {"schema_version": "lt-product-config-old", "selected_options": {}},
                }
            ]
        )
        try:
            _resolve_cart_items("", 1, stale_payload)
        except frappe.ValidationError as exc:
            if "older option format" not in str(exc):
                raise ContractFail(f"{case_name} failed with unexpected message: {exc}")
            evidence[case_name] = "blocked_old_schema"
        else:
            raise ContractFail(f"{case_name} should fail before sale-line resolution")

    return evidence


def _assert_no_sellable_candidate_fail_closed() -> dict[str, Any]:
    from locally_twisted.api.cart import resolve_cart_item_for_sale_with_reason
    from locally_twisted.www.checkout import _resolve_cart_items, _resolve_sale_lines, get_context

    missing_item_code = "__lt_phase4_no_sellable_candidate__"
    candidate = _sellable_candidate(missing_item_code)
    if candidate is not None:
        raise ContractFail(f"synthetic no-candidate fixture unexpectedly resolved candidate {candidate}")

    resolved, reason = resolve_cart_item_for_sale_with_reason(missing_item_code)
    if resolved or reason != "unavailable":
        raise ContractFail(f"missing synthetic item should be unavailable, found resolved={resolved}, reason={reason}")

    original_form_dict = getattr(frappe, "form_dict", None)
    try:
        frappe.form_dict = frappe._dict({"item": missing_item_code, "qty": "1"})
        try:
            get_context(frappe._dict())
        except Exception as exc:
            if exc.__class__.__name__ != "PageDoesNotExistError":
                raise
        else:
            raise ContractFail("direct checkout URL rendered for synthetic no-candidate item")
    finally:
        if original_form_dict is None:
            try:
                delattr(frappe, "form_dict")
            except AttributeError:
                pass
        else:
            frappe.form_dict = original_form_dict

    payload = json.dumps([{"item_code": missing_item_code, "qty": 1}])
    cart_items = _resolve_cart_items("", 1, payload)
    try:
        _resolve_sale_lines(cart_items)
    except frappe.ValidationError as exc:
        if "no longer available" not in str(exc):
            raise ContractFail(f"synthetic no-candidate stale cart failed with unexpected message: {exc}")
    else:
        raise ContractFail("synthetic no-candidate stale cart entered sale-line resolution")

    return {
        "item_code": missing_item_code,
        "sellable_candidate": None,
        "cart_api": "blocked_unavailable",
        "direct_checkout_url": "blocked_not_found",
        "stale_localstorage": "blocked_unavailable",
    }


def _lying_checkout_configuration(candidate_item_code: str, website_item_code: str) -> dict[str, Any]:
    return {
        "schema_version": CONFIG_VERSION,
        "source": "phase-4-stale-localstorage-boundary-verifier",
        "item_code": candidate_item_code,
        "website_item_code": website_item_code,
        "product_page_type": "simple_product",
        "commerce_lane": "checkout",
        "selected_options": {},
        "add_ons": [],
        "customizations": [],
    }


def _counts() -> dict[str, int]:
    return {doctype: frappe.db.count(doctype) for doctype in COUNT_DOCTYPES}


def _sample_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if len(rows) <= 6:
        return rows
    return rows[:3] + rows[-3:]
