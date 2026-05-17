"""Paid-order cascade verifier for local launch checks.

This creates a realistic guest-order accounting chain inside the current
transaction, runs the same reconciliation helper used by Stripe return/webhook
paths, verifies the downstream ERPNext records, then rolls everything back.
"""
from __future__ import annotations

import json
import time
from html import unescape
from quopri import decodestring

import frappe
from frappe.utils import add_days, flt, nowdate


ITEM_CODE = "easter-arch"
PRICE_LIST = "Standard Selling"
NOTES = "Gate code 1234. Please call on arrival."
SELECTED_IMAGE = "/files/payment-cascade-selected-image.png"


class ContractFail(Exception):
    pass


def run():
    """Run the paid-order cascade contract and return JSON-safe evidence."""
    original_commit = frappe.db.commit
    original_operator_email = frappe.conf.get("lt_operator_email")
    original_in_test = frappe.flags.get("in_test")
    original_testing_email = frappe.flags.get("testing_email")
    intercepted_commits = []

    def no_commit(*args, **kwargs):
        intercepted_commits.append(True)

    try:
        frappe.db.commit = no_commit
        frappe.flags.in_test = True
        frappe.flags.testing_email = False
        frappe.conf.lt_operator_email = "lt-cascade-operator@example.invalid"
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
        if original_operator_email is None:
            frappe.conf.pop("lt_operator_email", None)
        else:
            frappe.conf.lt_operator_email = original_operator_email
        _restore_flag("in_test", original_in_test)
        _restore_flag("testing_email", original_testing_email)
        frappe.db.rollback()


def _run_contract():
    token = str(int(time.time()))
    email = f"lt-cascade-{token}@example.invalid"

    customer = _create_customer(token, email)
    contact = _create_contact(customer.name, token, email)
    address = _create_address(customer.name, token, email)
    sales_order = _create_sales_order(customer.name, address.name)

    from locally_twisted.www.checkout import _record_order_notes

    _record_order_notes(sales_order.name, NOTES, sender=email)
    payment_request = _create_payment_request(sales_order.name, customer.name, email)

    from locally_twisted.www.payment_success import reconcile_paid_sales_order

    first = _reconcile_as_guest(
        reconcile_paid_sales_order,
        sales_order.name,
        payment_request=payment_request.name,
        source="payment_cascade_contract",
        raise_on_error=True,
    )
    if not first.get("ok"):
        raise ContractFail(f"first reconciliation returned errors: {first.get('errors')}")

    evidence = _collect_evidence(sales_order.name, customer.name, payment_request.name, contact.name)

    second = _reconcile_as_guest(
        reconcile_paid_sales_order,
        sales_order.name,
        payment_request=payment_request.name,
        source="payment_cascade_contract_second_run",
        raise_on_error=True,
    )
    if not second.get("ok"):
        raise ContractFail(f"second reconciliation returned errors: {second.get('errors')}")

    duplicate_failures = _check_idempotency(sales_order.name, customer.name)
    if duplicate_failures:
        raise ContractFail("; ".join(duplicate_failures))

    billed_retry = _run_billed_sales_order_retry(token)

    return {"ok": True, **evidence, "billed_sales_order_retry": billed_retry}


def _reconcile_as_guest(func, *args, **kwargs):
    previous_user = frappe.session.user
    try:
        frappe.set_user("Guest")
        return func(*args, **kwargs)
    finally:
        frappe.set_user(previous_user or "Administrator")


def _run_billed_sales_order_retry(token):
    email = f"lt-cascade-billed-{token}@example.invalid"
    customer = _create_customer(f"billed {token}", email)
    contact = _create_contact(customer.name, f"billed {token}", email)
    address = _create_address(customer.name, f"billed {token}", email)
    sales_order = _create_sales_order(customer.name, address.name)

    from locally_twisted.www.payment_success import (
        _ensure_sales_invoice,
        reconcile_paid_sales_order,
    )

    invoice = _ensure_sales_invoice(sales_order.name)
    payment_request = _create_payment_request(sales_order.name, customer.name, email)
    result = _reconcile_as_guest(
        reconcile_paid_sales_order,
        sales_order.name,
        payment_request=payment_request.name,
        source="payment_cascade_billed_retry",
        raise_on_error=True,
    )
    if not result.get("ok"):
        raise ContractFail(f"billed retry reconciliation returned errors: {result.get('errors')}")
    if frappe.db.get_value("Payment Request", payment_request.name, "status") != "Paid":
        raise ContractFail("billed retry Payment Request did not become Paid")
    payment_entry = _payment_entry_for_payment_request(payment_request.name)
    if not payment_entry:
        raise ContractFail("billed retry did not create a Payment Entry linked to the Payment Request")
    return {
        "sales_order": sales_order.name,
        "sales_invoice": invoice,
        "payment_request": payment_request.name,
        "payment_entry": payment_entry,
        "contact": contact.name,
    }


def _create_customer(token, email):
    customer = frappe.get_doc(
        {
            "doctype": "Customer",
            "customer_name": f"LT Cascade Test {token}",
            "customer_type": "Individual",
            "customer_group": "Individual",
            "territory": "All Territories",
            "marketing_opt_in": 0,
        }
    )
    customer.insert(ignore_permissions=True)
    return customer


def _create_contact(customer_name, token, email):
    contact = frappe.get_doc(
        {
            "doctype": "Contact",
            "first_name": f"LT Cascade Test {token}",
            "email_ids": [{"email_id": email, "is_primary": 1}],
            "phone_nos": [{"phone": "801-555-0100", "is_primary_mobile_no": 1}],
            "links": [{"link_doctype": "Customer", "link_name": customer_name}],
        }
    )
    contact.insert(ignore_permissions=True)
    return contact


def _create_address(customer_name, token, email):
    address = frappe.get_doc(
        {
            "doctype": "Address",
            "address_title": f"LT Cascade Test {token}",
            "address_type": "Shipping",
            "address_line1": "123 Test Cascade Lane",
            "city": "West Jordan",
            "state": "UT",
            "pincode": "84088",
            "country": "United States",
            "email_id": email,
            "phone": "801-555-0100",
            "links": [{"link_doctype": "Customer", "link_name": customer_name}],
        }
    )
    address.insert(ignore_permissions=True)
    return address


def _create_sales_order(customer_name, address_name):
    from locally_twisted import commerce_rules

    rate = frappe.db.get_value(
        "Item Price",
        {"item_code": ITEM_CODE, "price_list": PRICE_LIST},
        "price_list_rate",
    )
    if rate is None:
        raise ContractFail(f"missing Item Price for {ITEM_CODE} in {PRICE_LIST}")

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
            "items": [
                {
                    "item_code": ITEM_CODE,
                    "qty": 1,
                    "rate": flt(rate),
                    "custom_lt_configuration_json": json.dumps(
                        {
                            "schema_version": "lt-product-config-v1",
                            "selected_media": {
                                "image": SELECTED_IMAGE,
                                "label": "Payment cascade selected image",
                            },
                        },
                        sort_keys=True,
                    ),
                }
            ],
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
    sales_order.insert(ignore_permissions=True)
    sales_order.submit()
    return sales_order


def _create_payment_request(sales_order_name, customer_name, email):
    from locally_twisted.payments.settings import get_payment_gateway_account

    payment_gateway_account = get_payment_gateway_account()
    if not frappe.db.exists("Payment Gateway Account", payment_gateway_account):
        raise ContractFail(f"missing Payment Gateway Account {payment_gateway_account}")

    sales_order = frappe.get_doc("Sales Order", sales_order_name)
    payment_request = frappe.get_doc(
        {
            "doctype": "Payment Request",
            "payment_request_type": "Inward",
            "payment_gateway_account": payment_gateway_account,
            "party_type": "Customer",
            "party": customer_name,
            "reference_doctype": "Sales Order",
            "reference_name": sales_order.name,
            "currency": "USD",
            "grand_total": flt(sales_order.grand_total),
            "email_to": email,
            "subject": f"Payment for order {sales_order.name} - Locally Twisted",
            "message": "Please complete your payment to confirm your order.",
        }
    )
    payment_request.flags.mute_email = True
    payment_request.insert(ignore_permissions=True)
    payment_request.submit()
    return payment_request


def _collect_evidence(sales_order_name, customer_name, payment_request_name, contact_name):
    failures = []
    from locally_twisted.communication_copy_policy import BUSINESS_DOCUMENT_COPY

    pr_status = frappe.db.get_value("Payment Request", payment_request_name, "status")
    if pr_status != "Paid":
        failures.append(f"Payment Request status should be Paid, found {pr_status!r}")

    payment_entry = _payment_entry_for_payment_request(payment_request_name)
    if not payment_entry:
        failures.append("missing submitted Payment Entry linked to Payment Request")

    sales_invoice = _sales_invoice_for_sales_order(sales_order_name)
    if not sales_invoice:
        failures.append("missing submitted Sales Invoice linked to Sales Order")

    receipt_queue = _email_queue_for(
        "Sales Order",
        sales_order_name,
        "Your Locally Twisted order is confirmed",
    )
    if not receipt_queue:
        failures.append("missing customer receipt Email Queue row")
    else:
        failures.extend(
            _check_copy_recipients(
                receipt_queue["name"],
                [BUSINESS_DOCUMENT_COPY],
                "customer receipt",
            )
        )
        receipt_message = _readable_message(receipt_queue.get("message") or "")
        for expected in (
            "/terms-of-service#ready-to-order-pickup-delivery",
            "/refund-policy#ready-to-order-pickup-delivery",
            "/privacy",
            "Pickup and delivery windows are requests until confirmed",
            "not returnable once they are prepared, delivered, or picked up",
            "same day",
            SELECTED_IMAGE,
        ):
            if expected not in receipt_message:
                failures.append(f"customer receipt email missing policy text/link: {expected}")

    operator_queue = _email_queue_for("Sales Order", sales_order_name, "New paid order")
    if not operator_queue:
        failures.append("missing operator paid-order Email Queue row")
    else:
        if NOTES not in (operator_queue.get("message") or ""):
            failures.append("operator paid-order email is missing checkout notes")
        failures.extend(
            _check_copy_recipients(
                operator_queue["name"],
                [BUSINESS_DOCUMENT_COPY],
                "operator paid-order",
            )
        )

    welcome_queue = _email_queue_for("Customer", customer_name, "Welcome to Locally Twisted")
    if not welcome_queue:
        failures.append("missing first-order welcome Email Queue row")
    else:
        failures.extend(
            _check_copy_recipients(
                welcome_queue["name"],
                [BUSINESS_DOCUMENT_COPY],
                "first-order welcome",
            )
        )

    checkout_notes = _checkout_notes_for_sales_order(sales_order_name)
    if not checkout_notes:
        failures.append("missing checkout notes Communication on Sales Order")
    elif NOTES not in (checkout_notes.get("content") or ""):
        failures.append("checkout notes Communication does not contain the submitted notes")

    if not frappe.db.exists("Contact", contact_name):
        failures.append("missing Contact linked to test Customer")

    if failures:
        raise ContractFail("; ".join(failures))

    return {
        "sales_order": sales_order_name,
        "payment_request": payment_request_name,
        "payment_entry": payment_entry,
        "sales_invoice": sales_invoice,
        "receipt_email_queue": receipt_queue["name"],
        "operator_email_queue": operator_queue["name"],
        "welcome_email_queue": welcome_queue["name"],
        "checkout_notes": checkout_notes["name"],
    }


def _payment_entry_for_payment_request(payment_request_name):
    rows = frappe.get_all(
        "Payment Entry",
        filters={"reference_no": payment_request_name, "docstatus": 1},
        fields=["name"],
        limit=1,
    )
    return rows[0]["name"] if rows else None


def _readable_message(message: str) -> str:
    decoded = decodestring(message.encode("utf-8", errors="ignore")).decode("utf-8", errors="ignore")
    return unescape(f"{message}\n{decoded}")


def _sales_invoice_for_sales_order(sales_order_name):
    rows = frappe.get_all(
        "Sales Invoice Item",
        filters={"sales_order": sales_order_name},
        fields=["parent"],
        limit=1,
    )
    if not rows:
        return None
    name = rows[0]["parent"]
    if frappe.db.get_value("Sales Invoice", name, "docstatus") != 1:
        return None
    return name


def _email_queue_for(reference_doctype, reference_name, subject_snippet):
    rows = frappe.get_all(
        "Email Queue",
        filters={
            "reference_doctype": reference_doctype,
            "reference_name": reference_name,
            "message": ("like", f"%Subject: {subject_snippet}%"),
        },
        fields=["name", "message", "status"],
        limit=1,
    )
    return rows[0] if rows else None


def _email_queue_recipients(queue_name):
    rows = frappe.get_all(
        "Email Queue Recipient",
        filters={"parent": queue_name},
        fields=["recipient"],
    )
    return {
        (row.get("recipient") or "").strip().lower()
        for row in rows
        if row.get("recipient")
    }


def _check_copy_recipients(queue_name, expected_recipients, label):
    from locally_twisted.communication_copy_policy import routed_alias_copy_risks

    recipients = _email_queue_recipients(queue_name)
    failures = [
        f"{label} email missing required copy recipient: {expected}"
        for expected in expected_recipients
        if expected not in recipients
    ]
    for alias in routed_alias_copy_risks(recipients):
        failures.append(f"{label} email should not copy routed alias loop: {alias}")
    return failures


def _restore_flag(flag_name: str, original_value) -> None:
    if original_value is None:
        frappe.flags.pop(flag_name, None)
    else:
        frappe.flags[flag_name] = original_value


def _checkout_notes_for_sales_order(sales_order_name):
    rows = frappe.get_all(
        "Communication",
        filters={
            "reference_doctype": "Sales Order",
            "reference_name": sales_order_name,
            "subject": f"Customer checkout notes - {sales_order_name}",
        },
        fields=["name", "content"],
        limit=1,
    )
    return rows[0] if rows else None


def _check_idempotency(sales_order_name, customer_name):
    failures = []
    if _count_sales_invoices(sales_order_name) != 1:
        failures.append("second reconciliation created a duplicate Sales Invoice")
    if _count_email_queues("Sales Order", sales_order_name, "Your Locally Twisted order is confirmed") != 1:
        failures.append("second reconciliation created a duplicate customer receipt email")
    if _count_email_queues("Sales Order", sales_order_name, "New paid order") != 1:
        failures.append("second reconciliation created a duplicate operator email")
    if _count_email_queues("Customer", customer_name, "Welcome to Locally Twisted") != 1:
        failures.append("second reconciliation created a duplicate welcome email")
    return failures


def _count_sales_invoices(sales_order_name):
    return len(
        frappe.get_all(
            "Sales Invoice Item",
            filters={"sales_order": sales_order_name},
            fields=["parent"],
        )
    )


def _count_email_queues(reference_doctype, reference_name, subject_snippet):
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
