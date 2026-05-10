"""Business automation index surface for product-page quote operator review."""
from __future__ import annotations

from pathlib import Path

import frappe


APP_ROOT = Path(frappe.get_app_path("locally_twisted"))


def product_quote_operator_review_surface(*, run_runtime_contracts: bool) -> dict[str, object]:
    return {
        "id": "product_quote_operator_review",
        "lane": "paperwork",
        "summary": (
            "Product-page quote Quotations can be reviewed internally for blockers and no-send "
            "customer-review readiness without creating orders, invoices, or payment requests."
        ),
        "required_for_launch": False,
        "exists": _exists,
        "connected": lambda: _connected(run_runtime_contracts=run_runtime_contracts),
        "loud_failure": _loud_failure,
        "evidence": [
            "apps/locally_twisted/locally_twisted/product_quote_operator_review.py",
            "apps/locally_twisted/locally_twisted/verify/product_quote_operator_review_contract.py",
        ],
        "verifiers": [
            "python scripts/verify/product_quote_operator_review.py --report output/product-quote-operator-review.json",
            "python scripts/verify/product_quote_operator_review_contract.py",
        ],
    }


def product_quote_acceptance_surface(*, run_runtime_contracts: bool) -> dict[str, object]:
    return {
        "id": "product_quote_acceptance_to_draft_order",
        "lane": "paperwork",
        "summary": (
            "Accepted product-page quote Quotations can create draft Sales Orders while preserving "
            "quote payload and acceptance details without invoices, payment requests, or emails."
        ),
        "required_for_launch": False,
        "exists": lambda: _files_exist(
            "locally_twisted/product_quote_acceptance.py",
            "locally_twisted/verify/product_quote_acceptance_contract.py",
            "locally_twisted/www/quote_accept.py",
            "locally_twisted/www/quote_accept.html",
        ),
        "connected": lambda: _acceptance_connected(run_runtime_contracts=run_runtime_contracts),
        "loud_failure": _acceptance_loud_failure,
        "evidence": [
            "apps/locally_twisted/locally_twisted/product_quote_acceptance.py",
            "apps/locally_twisted/locally_twisted/verify/product_quote_acceptance_contract.py",
            "apps/locally_twisted/locally_twisted/www/quote_accept.py",
            "apps/locally_twisted/locally_twisted/www/quote_accept.html",
        ],
        "verifiers": [
            "python scripts/verify/product_quote_acceptance_contract.py",
            "npm run test:quote-accept-experience",
        ],
        "creates_fake_data": True,
    }


def product_quote_customer_delivery_surface(*, run_runtime_contracts: bool) -> dict[str, object]:
    return {
        "id": "product_quote_customer_delivery",
        "lane": "paperwork",
        "summary": (
            "Reviewed product-page quote approval links can be sent to the customer with required "
            "business BCC and no order, invoice, or payment side effects."
        ),
        "required_for_launch": False,
        "exists": lambda: _files_exist(
            "locally_twisted/product_quote_customer_delivery.py",
            "locally_twisted/verify/product_quote_customer_delivery_contract.py",
        ),
        "connected": lambda: _customer_delivery_connected(run_runtime_contracts=run_runtime_contracts),
        "loud_failure": _customer_delivery_loud_failure,
        "evidence": [
            "apps/locally_twisted/locally_twisted/product_quote_customer_delivery.py",
            "apps/locally_twisted/locally_twisted/verify/product_quote_customer_delivery_contract.py",
        ],
        "verifiers": [
            "python scripts/verify/product_quote_customer_delivery_contract.py",
        ],
        "creates_fake_data": True,
    }


def product_quote_operator_send_control_surface(*, run_runtime_contracts: bool) -> dict[str, object]:
    return {
        "id": "product_quote_operator_send_control",
        "lane": "paperwork",
        "summary": (
            "Submitted reviewed product-page Quotations expose an operator Desk control that sends "
            "the customer approval link with required business BCC and no order, invoice, or payment side effects."
        ),
        "required_for_launch": False,
        "exists": lambda: _files_exist(
            "locally_twisted/product_quote_operator_send.py",
            "locally_twisted/public/js/lt-product-quote-quotation.js",
            "locally_twisted/verify/product_quote_operator_send_control_contract.py",
        ),
        "connected": lambda: _operator_send_control_connected(run_runtime_contracts=run_runtime_contracts),
        "loud_failure": _operator_send_control_loud_failure,
        "evidence": [
            "apps/locally_twisted/locally_twisted/product_quote_operator_send.py",
            "apps/locally_twisted/locally_twisted/public/js/lt-product-quote-quotation.js",
            "apps/locally_twisted/locally_twisted/hooks.py",
            "apps/locally_twisted/locally_twisted/verify/product_quote_operator_send_control_contract.py",
        ],
        "verifiers": [
            "python scripts/verify/product_quote_operator_send_control_contract.py",
        ],
        "creates_fake_data": True,
    }


def _exists() -> list[str]:
    return _files_exist(
        "locally_twisted/product_quote_operator_review.py",
        "locally_twisted/verify/product_quote_operator_review_contract.py",
    )


def _connected(*, run_runtime_contracts: bool = True) -> list[str]:
    failures = []
    failures.extend(
        _callables_exist(
            "locally_twisted.product_quote_operator_review.run",
            "locally_twisted.product_quote_operator_review.evaluate_product_quote_quotation",
            "locally_twisted.verify.product_quote_operator_review_contract.run",
        )
    )
    if failures:
        return failures

    result = frappe.get_attr("locally_twisted.product_quote_operator_review.run")()
    if result.get("ok") is not True:
        failures.extend(result.get("failures") or ["product_quote_operator_review.run returned not ok"])
    for key, expected in {
        "read_only": True,
        "send_allowed": False,
        "customer_delivery_enabled": False,
        "sales_order_creation_allowed": False,
        "invoice_creation_allowed": False,
        "payment_request_allowed": False,
    }.items():
        if result.get(key) is not expected:
            failures.append(f"product_quote_operator_review {key} expected {expected}, found {result.get(key)}")
    if result.get("review_surface") != "product_quote_operator_review":
        failures.append("product_quote_operator_review returned wrong review_surface")
    if result.get("mutation_guard", {}).get("changed"):
        failures.append("product_quote_operator_review mutation guard changed")

    if run_runtime_contracts:
        contract = frappe.get_attr("locally_twisted.verify.product_quote_operator_review_contract.run")()
        if contract.get("ok") is not True:
            failures.extend(contract.get("failures") or ["product_quote_operator_review_contract.run returned not ok"])
        for key, expected in {
            "read_only": True,
            "send_allowed": False,
            "customer_delivery_enabled": False,
            "sales_order_creation_allowed": False,
            "payment_request_allowed": False,
        }.items():
            if contract.get(key) is not expected:
                failures.append(f"product_quote_operator_review_contract {key} expected {expected}, found {contract.get(key)}")
    return failures


def _loud_failure() -> list[str]:
    failures = []
    source = _read("locally_twisted/product_quote_operator_review.py")
    for marker in (
        "replace_placeholder_review_line_with_real_scope_and_pricing",
        "required_field:reviewed_product_quote_pricing",
        "malformed_product_quote_payload",
        "send_allowed",
        "sales_order_creation_allowed",
        "payment_request_allowed",
    ):
        if marker not in source:
            failures.append(f"product_quote_operator_review.py missing marker {marker}")
    return failures


def _acceptance_connected(*, run_runtime_contracts: bool = True) -> list[str]:
    failures = []
    failures.extend(
        _callables_exist(
            "locally_twisted.product_quote_acceptance.create_draft_sales_order_from_accepted_product_quote",
            "locally_twisted.product_quote_acceptance.product_quote_acceptance_blockers",
            "locally_twisted.verify.product_quote_acceptance_contract.run",
        )
    )
    if failures or not run_runtime_contracts:
        return failures

    contract = frappe.get_attr("locally_twisted.verify.product_quote_acceptance_contract.run")()
    if contract.get("ok") is not True:
        failures.extend(contract.get("failures") or ["product_quote_acceptance_contract.run returned not ok"])
    for key, expected in {
        "draft_only": True,
        "invoice_creation_allowed": False,
        "payment_request_allowed": False,
        "email_send_allowed": False,
        "rolled_back": True,
    }.items():
        if contract.get(key) is not expected:
            failures.append(f"product_quote_acceptance_contract {key} expected {expected}, found {contract.get(key)}")
    if contract.get("guard_counts_before") != contract.get("guard_counts_after"):
        failures.append("product_quote_acceptance_contract changed finance/email guard counts")
    return failures


def _acceptance_loud_failure() -> list[str]:
    failures = []
    source = _read("locally_twisted/product_quote_acceptance.py")
    for marker in (
        "ACCEPTANCE_REQUIRED_FIELDS",
        "submit_the_reviewed_quotation_before_order_draft",
        "replace_placeholder_review_line_before_order",
        "pricing_review_required",
        "create an invoice",
        "Payment Request",
            "send email",
            "issue_product_quote_acceptance_token",
            "accept_product_quote_from_token",
            "product_quote_acceptance_preview",
        ):
        if marker not in source:
            failures.append(f"product_quote_acceptance.py missing marker {marker}")
    return failures


def _customer_delivery_connected(*, run_runtime_contracts: bool = True) -> list[str]:
    failures = []
    failures.extend(
        _callables_exist(
            "locally_twisted.product_quote_customer_delivery.send_product_quote_customer_review",
            "locally_twisted.verify.product_quote_customer_delivery_contract.run",
        )
    )
    if failures or not run_runtime_contracts:
        return failures

    contract = frappe.get_attr("locally_twisted.verify.product_quote_customer_delivery_contract.run")()
    if contract.get("ok") is not True:
        failures.extend(contract.get("failures") or ["product_quote_customer_delivery_contract.run returned not ok"])
    if contract.get("business_bcc") != "locallytwisted@gmail.com":
        failures.append("product_quote_customer_delivery_contract did not use delivery-safe business BCC")
    if contract.get("sendmail_calls") != 1:
        failures.append("product_quote_customer_delivery_contract did not capture exactly one sendmail call")
    if contract.get("guard_counts_before") != contract.get("guard_counts_after"):
        failures.append("product_quote_customer_delivery_contract changed order/finance/email guard counts")
    return failures


def _customer_delivery_loud_failure() -> list[str]:
    failures = []
    source = _read("locally_twisted/product_quote_customer_delivery.py")
    for marker in (
        "DEFAULT_BUSINESS_BCC",
        "BUSINESS_DOCUMENT_COPY",
        "routed_alias_copy_risks",
        "business copy",
        "Payment Request",
        "does not charge a card or create an invoice",
        "issue_product_quote_acceptance_token",
    ):
        if marker not in source:
            failures.append(f"product_quote_customer_delivery.py missing marker {marker}")
    return failures


def _operator_send_control_connected(*, run_runtime_contracts: bool = True) -> list[str]:
    failures = []
    failures.extend(
        _callables_exist(
            "locally_twisted.product_quote_operator_send.send_reviewed_product_quote_to_customer",
            "locally_twisted.verify.product_quote_operator_send_control_contract.run",
        )
    )
    if failures or not run_runtime_contracts:
        return failures

    contract = frappe.get_attr("locally_twisted.verify.product_quote_operator_send_control_contract.run")()
    if contract.get("ok") is not True:
        failures.extend(contract.get("failures") or ["product_quote_operator_send_control_contract.run returned not ok"])
    for key, expected in {
        "operator_control": True,
        "customer_delivery_enabled": True,
        "business_bcc": "locallytwisted@gmail.com",
        "sendmail_calls": 1,
    }.items():
        if contract.get(key) != expected:
            failures.append(f"product_quote_operator_send_control_contract {key} expected {expected}, found {contract.get(key)}")
    if contract.get("guard_counts_before") != contract.get("guard_counts_after"):
        failures.append("product_quote_operator_send_control_contract changed order/finance/email guard counts")
    return failures


def _operator_send_control_loud_failure() -> list[str]:
    failures = []
    source = _read("locally_twisted/product_quote_operator_send.py")
    js_source = _read("locally_twisted/public/js/lt-product-quote-quotation.js")
    hooks_source = _read("locally_twisted/hooks.py")
    for marker in (
        "Ready For Customer Review",
        "product_quote_acceptance_blockers",
        "DEFAULT_BUSINESS_BCC",
        "payment_request_allowed",
        "Tiny snag",
    ):
        if marker not in source:
            failures.append(f"product_quote_operator_send.py missing marker {marker}")
    for marker in (
        "Send Approval Link",
        "send_reviewed_product_quote_to_customer",
        "locallytwisted@gmail.com",
    ):
        if marker not in js_source:
            failures.append(f"lt-product-quote-quotation.js missing marker {marker}")
    if "lt-product-quote-quotation.js" not in hooks_source:
        failures.append("hooks.py missing Quotation operator send control registration")
    return failures


def _files_exist(*relative_paths: str) -> list[str]:
    failures = []
    for relative_path in relative_paths:
        if not _app_path(relative_path).exists():
            failures.append(f"Missing file {relative_path}")
    return failures


def _callables_exist(*dotted_paths: str) -> list[str]:
    failures = []
    for dotted_path in dotted_paths:
        try:
            frappe.get_attr(dotted_path)
        except Exception as exc:
            failures.append(f"Missing callable {dotted_path}: {type(exc).__name__}: {exc}")
    return failures


def _read(relative_path: str) -> str:
    path = _app_path(relative_path)
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def _app_path(relative_path: str) -> Path:
    return APP_ROOT.parent / relative_path
