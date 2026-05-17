"""Rollback payment cascade proof for the simple purchasable product tranche.

This verifier temporarily applies the checkout contract in one ERPNext
transaction, builds a Sales Order from the same resolver-backed lines used by
the simple rehearsal, runs the paid-order reconciliation helper, verifies
Payment Request / Payment Entry / Sales Invoice / receipt / operator / welcome
email evidence, then rolls everything back.
"""
from __future__ import annotations

import json
import time
from html import unescape
from quopri import decodestring
from typing import Any

import frappe
from frappe.utils import add_days, flt, nowdate

from locally_twisted.verify import checkout_product_family_contract as checkout_family
from locally_twisted.verify import payment_cascade_contract as payment_contract
from locally_twisted.verify import simple_purchasable_rehearsal_contract as simple_rehearsal


NOTES = "Simple product payment cascade proof. Please stage pickup carefully."
PRICE_LIST = "Standard Selling"
EXPECTED_PRODUCT_COUNT = 4
EXPECTED_SALE_SKUS = 33


class ContractFail(Exception):
    pass


def run() -> dict[str, Any]:
    token = f"simple-pay-{int(time.time() * 1000)}"
    original_commit = frappe.db.commit
    original_operator_email = frappe.conf.get("lt_operator_email")
    original_in_test = frappe.flags.get("in_test")
    original_testing_email = frappe.flags.get("testing_email")
    intercepted_commits: list[bool] = []

    def no_commit(*args, **kwargs):
        intercepted_commits.append(True)

    try:
        frappe.db.commit = no_commit
        frappe.flags.in_test = True
        frappe.flags.testing_email = False
        frappe.conf.lt_operator_email = "lt-simple-cascade-operator@example.invalid"
        result = _run_contract(token)
        result["commit_calls_intercepted"] = len(intercepted_commits)
        frappe.db.rollback()
        result["rolled_back"] = True
        result["survivor_counts"] = _survivor_counts(token)
        survivors = {key: value for key, value in result["survivor_counts"].items() if value}
        if survivors:
            raise ContractFail(f"generated simple payment cascade records survived rollback: {survivors}")
        return {"ok": True, **result}
    except ContractFail as exc:
        frappe.db.rollback()
        return {"ok": False, "failures": [str(exc)], "survivor_counts": _survivor_counts(token)}
    except Exception:
        frappe.db.rollback()
        return {"ok": False, "failures": [frappe.get_traceback()], "survivor_counts": _survivor_counts(token)}
    finally:
        frappe.db.commit = original_commit
        if original_operator_email is None:
            frappe.conf.pop("lt_operator_email", None)
        else:
            frappe.conf.lt_operator_email = original_operator_email
        _restore_flag("in_test", original_in_test)
        _restore_flag("testing_email", original_testing_email)
        frappe.db.rollback()


def _run_contract(token: str) -> dict[str, Any]:
    email = f"lt-{token}@example.invalid"
    simple_rehearsal._apply_transactional_checkout_contracts()
    checkout_family._assert_line_schema()

    product_results, sale_lines = _resolved_simple_tranche_lines()
    if len(product_results) != EXPECTED_PRODUCT_COUNT:
        raise ContractFail(f"expected {EXPECTED_PRODUCT_COUNT} simple products, found {len(product_results)}")
    if len(sale_lines) != EXPECTED_SALE_SKUS:
        raise ContractFail(f"expected {EXPECTED_SALE_SKUS} sale lines, found {len(sale_lines)}")

    customer = payment_contract._create_customer(token, email)
    contact = payment_contract._create_contact(customer.name, token, email)
    address = payment_contract._create_address(customer.name, token, email)
    sales_order = _create_sales_order(customer.name, address.name, sale_lines)

    from locally_twisted.www.checkout import _record_order_notes

    _record_order_notes(sales_order.name, NOTES, sender=email)
    payment_request = payment_contract._create_payment_request(sales_order.name, customer.name, email)

    from locally_twisted.www.payment_success import reconcile_paid_sales_order

    first = payment_contract._reconcile_as_guest(
        reconcile_paid_sales_order,
        sales_order.name,
        payment_request=payment_request.name,
        source="simple_purchasable_payment_cascade_contract",
        raise_on_error=True,
    )
    if not first.get("ok"):
        raise ContractFail(f"first reconciliation returned errors: {first.get('errors')}")

    evidence = _collect_evidence(
        sales_order=sales_order,
        customer_name=customer.name,
        payment_request_name=payment_request.name,
        contact_name=contact.name,
        product_results=product_results,
    )

    second = payment_contract._reconcile_as_guest(
        reconcile_paid_sales_order,
        sales_order.name,
        payment_request=payment_request.name,
        source="simple_purchasable_payment_cascade_contract_second_run",
        raise_on_error=True,
    )
    if not second.get("ok"):
        raise ContractFail(f"second reconciliation returned errors: {second.get('errors')}")
    duplicate_failures = _check_idempotency(sales_order.name, customer.name)
    if duplicate_failures:
        raise ContractFail("; ".join(duplicate_failures))

    return {
        **evidence,
        "simple_payment_product_count": len(product_results),
        "enabled_sale_sku_count": len(sale_lines),
        "products": product_results,
        "schema_version": checkout_family.CONFIG_VERSION,
    }


def _resolved_simple_tranche_lines() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    product_results: list[dict[str, Any]] = []
    sale_lines: list[dict[str, Any]] = []
    for website_item_code, spec in simple_rehearsal.SIMPLE_REHEARSAL_PRODUCTS.items():
        product_result, lines = simple_rehearsal._assert_product_rehearsal(website_item_code, spec)
        product_results.append(product_result)
        sale_lines.extend(lines)
    return product_results, sale_lines


def _create_sales_order(customer_name: str, address_name: str, sale_lines: list[dict[str, Any]]):
    from locally_twisted import commerce_rules

    sales_order = frappe.get_doc(
        {
            "doctype": "Sales Order",
            "customer": customer_name,
            "order_type": "Shopping Cart",
            "transaction_date": nowdate(),
            "delivery_date": add_days(nowdate(), 7),
            "currency": "USD",
            "selling_price_list": PRICE_LIST,
            "shipping_address_name": address_name,
            "items": sale_lines,
            "taxes": [
                {
                    "charge_type": "On Net Total",
                    "account_head": commerce_rules.validate_sales_tax_account_head(),
                    "description": "Utah sales tax (84088)",
                    "rate": 7.45,
                }
            ],
        }
    )
    sales_order.flags.ignore_permissions = True
    sales_order.flags.mute_email = True
    sales_order.insert(ignore_permissions=True)
    sales_order.submit()
    checkout_family._assert_stored_rows_preserve_line_fields(
        "Sales Order",
        sales_order.items,
        expected_base_line_count=EXPECTED_SALE_SKUS,
        expected_add_on_line_count=0,
        expected_color_recipe_line_count=0,
    )
    return sales_order


def _collect_evidence(
    *,
    sales_order,
    customer_name: str,
    payment_request_name: str,
    contact_name: str,
    product_results: list[dict[str, Any]],
) -> dict[str, Any]:
    failures: list[str] = []
    from locally_twisted.communication_copy_policy import BUSINESS_DOCUMENT_COPY

    if frappe.db.get_value("Payment Request", payment_request_name, "status") != "Paid":
        failures.append("Payment Request did not become Paid")
    payment_entry = payment_contract._payment_entry_for_payment_request(payment_request_name)
    if not payment_entry:
        failures.append("missing submitted Payment Entry linked to Payment Request")
    sales_invoice = payment_contract._sales_invoice_for_sales_order(sales_order.name)
    if not sales_invoice:
        failures.append("missing submitted Sales Invoice linked to Sales Order")
    else:
        invoice = frappe.get_doc("Sales Invoice", sales_invoice)
        if len(invoice.items) != EXPECTED_SALE_SKUS:
            failures.append(f"Sales Invoice stored {len(invoice.items)} lines, expected {EXPECTED_SALE_SKUS}")
        else:
            checkout_family._assert_stored_rows_preserve_line_fields(
                "Sales Invoice",
                invoice.items,
                expected_base_line_count=EXPECTED_SALE_SKUS,
                expected_add_on_line_count=0,
                expected_color_recipe_line_count=0,
            )

    receipt_queue = payment_contract._email_queue_for(
        "Sales Order",
        sales_order.name,
        "Your Locally Twisted order is confirmed",
    )
    operator_queue = payment_contract._email_queue_for("Sales Order", sales_order.name, "New paid order")
    welcome_queue = payment_contract._email_queue_for("Customer", customer_name, "Welcome to Locally Twisted")
    checkout_notes = payment_contract._checkout_notes_for_sales_order(sales_order.name)

    if not receipt_queue:
        failures.append("missing customer receipt Email Queue row")
    else:
        failures.extend(payment_contract._check_copy_recipients(receipt_queue["name"], [BUSINESS_DOCUMENT_COPY], "customer receipt"))
        receipt_message = _readable_message(receipt_queue.get("message") or "")
        failures.extend(_assert_email_covers_products("customer receipt", receipt_message, product_results))
        for expected in (
            "/terms-of-service#ready-to-order-pickup-delivery",
            "/refund-policy#ready-to-order-pickup-delivery",
            "/privacy",
            "This email is your receipt.",
        ):
            if expected not in receipt_message:
                failures.append(f"customer receipt email missing policy/receipt text: {expected}")

    if not operator_queue:
        failures.append("missing operator paid-order Email Queue row")
    else:
        failures.extend(payment_contract._check_copy_recipients(operator_queue["name"], [BUSINESS_DOCUMENT_COPY], "operator paid-order"))
        operator_message = _readable_message(operator_queue.get("message") or "")
        failures.extend(_assert_email_covers_products("operator email", operator_message, product_results))
        if NOTES not in operator_message:
            failures.append("operator paid-order email is missing checkout notes")

    if not welcome_queue:
        failures.append("missing first-order welcome Email Queue row")
    else:
        failures.extend(payment_contract._check_copy_recipients(welcome_queue["name"], [BUSINESS_DOCUMENT_COPY], "first-order welcome"))

    if not checkout_notes:
        failures.append("missing checkout notes Communication on Sales Order")
    elif NOTES not in (checkout_notes.get("content") or ""):
        failures.append("checkout notes Communication does not contain the submitted notes")
    if not frappe.db.exists("Contact", contact_name):
        failures.append("missing Contact linked to test Customer")

    if failures:
        raise ContractFail("; ".join(failures))

    return {
        "sales_order": sales_order.name,
        "payment_request": payment_request_name,
        "payment_entry": payment_entry,
        "sales_invoice": sales_invoice,
        "sales_order_line_count": len(sales_order.items),
        "receipt_email_queue": receipt_queue["name"],
        "operator_email_queue": operator_queue["name"],
        "welcome_email_queue": welcome_queue["name"],
        "checkout_notes": checkout_notes["name"],
        "grand_total": flt(sales_order.grand_total),
    }


def _assert_email_covers_products(label: str, message: str, product_results: list[dict[str, Any]]) -> list[str]:
    failures: list[str] = []
    for row in product_results:
        source_name = str(row.get("source_name") or row.get("web_item_name") or row.get("website_item_code") or "")
        website_item_code = str(row.get("website_item_code") or "")
        needles = [needle for needle in {source_name, website_item_code} if needle]
        if not any(needle in message for needle in needles):
            failures.append(f"{label} is missing product evidence for {website_item_code or source_name}")
    return failures


def _check_idempotency(sales_order_name: str, customer_name: str) -> list[str]:
    failures: list[str] = []
    invoice_names = {
        row["parent"]
        for row in frappe.get_all(
            "Sales Invoice Item",
            filters={"sales_order": sales_order_name},
            fields=["parent"],
        )
        if row.get("parent")
    }
    if len(invoice_names) != 1:
        failures.append(f"second reconciliation should leave one Sales Invoice, found {sorted(invoice_names)}")
    if _count_email_queues("Sales Order", sales_order_name, "Your Locally Twisted order is confirmed") != 1:
        failures.append("second reconciliation created a duplicate customer receipt email")
    if _count_email_queues("Sales Order", sales_order_name, "New paid order") != 1:
        failures.append("second reconciliation created a duplicate operator email")
    if _count_email_queues("Customer", customer_name, "Welcome to Locally Twisted") != 1:
        failures.append("second reconciliation created a duplicate welcome email")
    return failures


def _count_email_queues(reference_doctype: str, reference_name: str, subject_snippet: str) -> int:
    return len(
        frappe.get_all(
            "Email Queue",
            filters={
                "reference_doctype": reference_doctype,
                "reference_name": reference_name,
                "message": ("like", f"%Subject: {subject_snippet}%"),
            },
            fields=["name"],
        )
    )


def _survivor_counts(token: str) -> dict[str, int]:
    customer_names = frappe.get_all(
        "Customer",
        filters={"customer_name": ["like", f"%{token}%"]},
        pluck="name",
    )
    sales_orders = frappe.get_all(
        "Sales Order",
        filters={"customer": ["in", customer_names]},
        pluck="name",
    ) if customer_names else []
    payment_requests = frappe.get_all(
        "Payment Request",
        filters={"reference_name": ["in", sales_orders]},
        pluck="name",
    ) if sales_orders else []
    email_references = [*sales_orders, *customer_names]
    return {
        "customer": len(customer_names),
        "contact": _linked_count("Contact", customer_names),
        "address": _linked_count("Address", customer_names),
        "sales_order": len(sales_orders),
        "payment_request": len(payment_requests),
        "payment_entry": frappe.db.count("Payment Entry", {"reference_no": ["in", payment_requests]}) if payment_requests else 0,
        "sales_invoice": frappe.db.count("Sales Invoice", {"customer": ["in", customer_names]}) if customer_names else 0,
        "email_queue": frappe.db.count("Email Queue", {"reference_name": ["in", email_references]}) if email_references else 0,
    }


def _linked_count(parenttype: str, customer_names: list[str]) -> int:
    if not customer_names:
        return 0
    parents = frappe.get_all(
        "Dynamic Link",
        filters={
            "link_doctype": "Customer",
            "link_name": ["in", customer_names],
            "parenttype": parenttype,
        },
        pluck="parent",
    )
    return len(set(parents))


def _readable_message(message: str) -> str:
    decoded = decodestring(message.encode("utf-8", errors="ignore")).decode("utf-8", errors="ignore")
    return unescape(f"{message}\n{decoded}")


def _restore_flag(flag_name: str, original_value) -> None:
    if original_value is None:
        frappe.flags.pop(flag_name, None)
    else:
        frappe.flags[flag_name] = original_value
