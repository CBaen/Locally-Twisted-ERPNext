"""Customer-note checkout preservation contract.

Creates guest checkout orders through submit_guest_order, verifies optional
customer notes land on the Sales Order Communication, verifies the linked
Payment Request, runs the same paid-order/operator cascade in rollback-safe
mode, and proves no generated verifier records survive rollback.
"""
from __future__ import annotations

from datetime import date, timedelta
from html import unescape
from quopri import decodestring
import time

import frappe


ITEM_CODE = "unicorn-bouquet-SMA"
UNIQUE_NOTE = "Please leave the bouquet with the blue front-desk sign."
NO_NOTE_MARKER = "NO_CUSTOMER_NOTE_MARKER_SHOULD_NOT_EXIST"


class ContractFail(Exception):
    pass


def run():
    """Run the customer-note checkout contract and return JSON-safe evidence."""
    original_commit = frappe.db.commit
    original_operator_email = frappe.conf.get("lt_operator_email")
    original_in_test = frappe.flags.get("in_test")
    original_testing_email = frappe.flags.get("testing_email")

    from locally_twisted import ecommerce_pause
    import locally_twisted.payments.stripe_session as stripe_session

    original_is_ecommerce_paused = ecommerce_pause.is_ecommerce_paused
    original_create_session = stripe_session.create_session_for_sales_order
    intercepted_commits = []
    token = str(int(time.time()))

    def no_commit(*args, **kwargs):
        intercepted_commits.append(True)

    def fake_create_session_for_sales_order(
        sales_order: str,
        payment_request: str,
        cancel_route: str,
        customer_email: str,
    ) -> str:
        return f"https://checkout.stripe.example.invalid/{sales_order}/{payment_request}"

    try:
        frappe.db.commit = no_commit
        frappe.flags.in_test = True
        frappe.flags.testing_email = False
        frappe.conf.lt_operator_email = "lt-note-operator@example.invalid"
        ecommerce_pause.is_ecommerce_paused = lambda: False
        stripe_session.create_session_for_sales_order = fake_create_session_for_sales_order

        result = _run_contract(token)
        result["commit_calls_intercepted"] = len(intercepted_commits)
        frappe.db.rollback()
        result["rolled_back"] = True
        result["survivor_counts"] = _survivor_counts(token)
        survivors = {key: value for key, value in result["survivor_counts"].items() if value}
        if survivors:
            raise ContractFail(f"generated verifier records survived rollback: {survivors}")
        return {"ok": True, **result}
    except ContractFail as exc:
        frappe.db.rollback()
        return {"ok": False, "failures": [str(exc)], "survivor_counts": _survivor_counts(token)}
    except Exception:
        frappe.db.rollback()
        return {"ok": False, "failures": [frappe.get_traceback()], "survivor_counts": _survivor_counts(token)}
    finally:
        frappe.db.commit = original_commit
        ecommerce_pause.is_ecommerce_paused = original_is_ecommerce_paused
        stripe_session.create_session_for_sales_order = original_create_session
        if original_operator_email is None:
            frappe.conf.pop("lt_operator_email", None)
        else:
            frappe.conf.lt_operator_email = original_operator_email
        _restore_flag("in_test", original_in_test)
        _restore_flag("testing_email", original_testing_email)
        frappe.db.rollback()


def _run_contract(token: str) -> dict:
    note_email = f"lt-note-{token}@example.invalid"
    no_note_email = f"lt-no-note-{token}@example.invalid"

    note_result = _submit_checkout(note_email, token, UNIQUE_NOTE)
    note_evidence = _verify_note_case(note_result, UNIQUE_NOTE)
    no_note_result = _submit_checkout(no_note_email, token, "")
    no_note_evidence = _verify_no_note_case(no_note_result)

    return {
        "note_case": note_evidence,
        "no_note_case": no_note_evidence,
    }


def _submit_checkout(email: str, token: str, order_notes: str) -> dict:
    from locally_twisted.www.checkout import submit_guest_order

    future_date = (date.today() + timedelta(days=30)).isoformat()
    result = submit_guest_order(
        item_code=ITEM_CODE,
        qty=1,
        name=f"LT Note Contract {token}",
        email=email,
        phone="801-555-0199",
        preferred_contact_method="email",
        fulfillment_method="delivery",
        address_line1=f"{token} Note Contract Lane",
        address_line2="",
        city="West Jordan",
        state="UT",
        postal_code="84088",
        country="United States",
        requested_fulfillment_date=future_date,
        requested_window_start="13:00",
        requested_window_end="13:30",
        order_notes=order_notes,
        marketing_opt_in=0,
    )
    if not result.get("ok"):
        status = result.get("status")
        if status == "ecommerce_paused":
            raise ContractFail(
                "checkout API returned ecommerce_paused inside the customer-note verifier; "
                "the verifier pause bypass is not active"
            )
        raise ContractFail(f"checkout submit failed before Sales Order creation: {result!r}")
    if not result.get("sales_order"):
        raise ContractFail(f"checkout submit did not return a Sales Order: {result!r}")
    return result


def _verify_note_case(result: dict, unique_note: str) -> dict:
    sales_order = result["sales_order"]
    payment_request = _payment_request_for_sales_order(sales_order)
    if payment_request != result.get("payment_request"):
        raise ContractFail(
            f"Payment Request should link to Sales Order {sales_order}; "
            f"submit returned {result.get('payment_request')!r}, lookup found {payment_request!r}"
        )

    communication = _checkout_notes_for_sales_order(sales_order)
    if not communication:
        raise ContractFail("note checkout did not create a Sales Order Communication")
    if communication.get("subject") != f"Customer checkout notes - {sales_order}":
        raise ContractFail(f"checkout note subject mismatch: {communication.get('subject')!r}")
    if unique_note not in (communication.get("content") or ""):
        raise ContractFail("Sales Order Communication does not contain the unique submitted note")

    from locally_twisted.www.payment_success import _get_customer_order_notes_html, _send_operator_notification

    operator_lookup_note = _get_customer_order_notes_html(sales_order)
    if unique_note not in (operator_lookup_note or ""):
        raise ContractFail("operator note lookup did not return the unique submitted note")

    # Exercise the same operator-notification path used by the paid-order
    # cascade, without marking payment paid or sending external mail. Frappe
    # queues the message inside this rollback-only verifier transaction.
    _send_operator_notification(sales_order)
    operator_queue = _email_queue_for("Sales Order", sales_order, "New paid order")
    if not operator_queue:
        raise ContractFail("operator notification path did not queue operator evidence")
    readable_operator_message = _readable_message(operator_queue.get("message") or "")
    if unique_note not in readable_operator_message:
        raise ContractFail("operator notification does not contain the unique submitted note")

    return {
        "sales_order": sales_order,
        "payment_request": payment_request,
        "communication": communication["name"],
        "operator_email_queue": operator_queue["name"],
        "operator_lookup_consumed_note": True,
    }


def _verify_no_note_case(result: dict) -> dict:
    sales_order = result["sales_order"]
    payment_request = _payment_request_for_sales_order(sales_order)
    if payment_request != result.get("payment_request"):
        raise ContractFail(f"no-note Payment Request does not link to Sales Order {sales_order}")

    communication = _checkout_notes_for_sales_order(sales_order)
    content = communication.get("content") if communication else ""
    if UNIQUE_NOTE in (content or "") or NO_NOTE_MARKER in (content or ""):
        raise ContractFail("no-note checkout invented or leaked customer note content")

    from locally_twisted.www.payment_success import _get_customer_order_notes_html

    operator_lookup_note = _get_customer_order_notes_html(sales_order) or ""
    if UNIQUE_NOTE in operator_lookup_note or NO_NOTE_MARKER in operator_lookup_note:
        raise ContractFail("operator note lookup invented or leaked customer note content for no-note order")

    return {
        "sales_order": sales_order,
        "payment_request": payment_request,
        "communication": communication["name"] if communication else None,
        "no_fake_customer_note": True,
    }


def _payment_request_for_sales_order(sales_order_name: str) -> str | None:
    rows = frappe.get_all(
        "Payment Request",
        filters={"reference_doctype": "Sales Order", "reference_name": sales_order_name},
        fields=["name"],
        limit=1,
    )
    return rows[0]["name"] if rows else None


def _checkout_notes_for_sales_order(sales_order_name: str):
    rows = frappe.get_all(
        "Communication",
        filters={
            "reference_doctype": "Sales Order",
            "reference_name": sales_order_name,
            "subject": f"Customer checkout notes - {sales_order_name}",
        },
        fields=["name", "subject", "content"],
        limit=1,
    )
    return rows[0] if rows else None


def _email_queue_for(reference_doctype: str, reference_name: str, subject_snippet: str):
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


def _readable_message(message: str) -> str:
    decoded = decodestring(message.encode("utf-8", errors="ignore")).decode("utf-8", errors="ignore")
    return unescape(f"{message}\n{decoded}")


def _sales_invoice_for_sales_order(sales_order_name: str) -> str | None:
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


def _payment_entry_for_payment_request(payment_request_name: str) -> str | None:
    rows = frappe.get_all(
        "Payment Entry",
        filters={"reference_no": payment_request_name, "docstatus": 1},
        fields=["name"],
        limit=1,
    )
    return rows[0]["name"] if rows else None


def _survivor_counts(token: str) -> dict[str, int]:
    customer_names = frappe.get_all(
        "Customer",
        filters={"customer_name": ("like", f"%LT Note Contract {token}%")},
        pluck="name",
    )
    address_names = frappe.get_all(
        "Address",
        filters={"address_line1": ("like", f"%{token} Note Contract Lane%")},
        pluck="name",
    )
    contact_names = frappe.get_all(
        "Contact",
        filters={"first_name": ("like", f"%LT Note Contract {token}%")},
        pluck="name",
    )
    emails = [f"lt-note-{token}@example.invalid", f"lt-no-note-{token}@example.invalid"]
    contact_email_names = frappe.get_all(
        "Contact Email",
        filters={"email_id": ("in", emails)},
        pluck="name",
    )

    sales_orders = []
    if customer_names:
        sales_orders = frappe.get_all(
            "Sales Order",
            filters={"customer": ("in", customer_names)},
            pluck="name",
        )
    payment_requests = []
    sales_invoices = []
    payment_entries = []
    communications = []
    email_queues = []
    if sales_orders:
        payment_requests = frappe.get_all(
            "Payment Request",
            filters={"reference_doctype": "Sales Order", "reference_name": ("in", sales_orders)},
            pluck="name",
        )
        sales_invoices = frappe.get_all(
            "Sales Invoice Item",
            filters={"sales_order": ("in", sales_orders)},
            pluck="parent",
        )
        communications = frappe.get_all(
            "Communication",
            filters={"reference_doctype": "Sales Order", "reference_name": ("in", sales_orders)},
            pluck="name",
        )
        email_queues = frappe.get_all(
            "Email Queue",
            filters={"reference_doctype": "Sales Order", "reference_name": ("in", sales_orders)},
            pluck="name",
        )
    if payment_requests:
        payment_entries = frappe.get_all(
            "Payment Entry",
            filters={"reference_no": ("in", payment_requests)},
            pluck="name",
        )

    return {
        "customer": len(customer_names),
        "contact": len(contact_names),
        "contact_email": len(contact_email_names),
        "address": len(address_names),
        "sales_order": len(set(sales_orders)),
        "payment_request": len(set(payment_requests)),
        "payment_entry": len(set(payment_entries)),
        "sales_invoice": len(set(sales_invoices)),
        "communication": len(set(communications)),
        "email_queue": len(set(email_queues)),
    }


def _restore_flag(flag_name: str, original_value) -> None:
    if original_value is None:
        frappe.flags.pop(flag_name, None)
    else:
        frappe.flags[flag_name] = original_value
