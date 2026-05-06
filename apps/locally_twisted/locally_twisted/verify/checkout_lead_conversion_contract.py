"""Checkout-to-Lead conversion contract for local launch checks.

This creates a Lead and its linked Contact, submits the real guest checkout
path with Stripe session creation stubbed, verifies the CRM/accounting story,
then rolls the transaction back.
"""
from __future__ import annotations

from datetime import date, timedelta
import time

import frappe


ITEM_CODE = "mothers-day-bouquet"


class ContractFail(Exception):
    pass


def run():
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


def _future_date() -> str:
    return (date.today() + timedelta(days=30)).isoformat()


def _run_contract():
    token = str(int(time.time()))
    marker = f"LT Checkout Lead {token}"
    email = f"lt-checkout-lead-{token}@example.invalid"

    lead = _create_lead(marker, email)
    contact_name = _contact_for_lead(lead.name)
    if not contact_name:
        raise ContractFail("Lead insert did not create/link a Contact")

    counts_before = _counts()
    initial_tasks = _tasks_for_lead(lead.name)
    if not _task_for_stage(initial_tasks, "New Inquiry", open_only=True):
        raise ContractFail("Lead insert did not create an open New Inquiry task")

    result = _submit_checkout(email=email, name=marker)

    lead_after = frappe.get_doc("Lead", lead.name)
    contact_after = frappe.get_doc("Contact", contact_name)
    counts_after = _counts()
    tasks_after = _tasks_for_lead(lead.name)

    failures = []
    failures.extend(_check_counts(counts_before, counts_after))
    failures.extend(_check_checkout_result(result, lead_after, contact_after, contact_name))
    failures.extend(_check_lead_state(lead_after, result))
    failures.extend(_check_task_state(tasks_after))

    if failures:
        raise ContractFail("; ".join(failures))

    return {
        "ok": True,
        "lead": lead.name,
        "contact": contact_name,
        "customer": result.get("customer"),
        "sales_order": result.get("sales_order"),
        "payment_request": result.get("payment_request"),
        "lead_status": lead_after.status,
        "pipeline_stage": lead_after.get("custom_pipeline_stage"),
        "active_task_stage": _active_task_stage(tasks_after),
    }


def _create_lead(marker: str, email: str):
    lead = frappe.get_doc(
        {
            "doctype": "Lead",
            "first_name": marker,
            "lead_name": marker,
            "email_id": email,
            "mobile_no": "801-555-0199",
            "status": "Open",
            "custom_pipeline_stage": "New Inquiry",
        }
    )
    lead.insert(ignore_permissions=True)
    return lead


def _contact_for_lead(lead_name: str) -> str | None:
    return frappe.db.get_value(
        "Dynamic Link",
        {"link_doctype": "Lead", "link_name": lead_name, "parenttype": "Contact"},
        "parent",
    )


def _submit_checkout(email: str, name: str):
    import locally_twisted.payments.stripe_session as stripe_session
    from locally_twisted.www.checkout import submit_guest_order

    original_create_session = stripe_session.create_session_for_sales_order

    def fake_create_session_for_sales_order(
        sales_order: str,
        payment_request: str,
        cancel_route: str,
        customer_email: str,
    ) -> str:
        return f"https://checkout.stripe.example.invalid/{sales_order}/{payment_request}"

    try:
        stripe_session.create_session_for_sales_order = fake_create_session_for_sales_order
        return submit_guest_order(
            item_code=ITEM_CODE,
            qty=1,
            name=name,
            email=email,
            phone="801-555-0199",
            address_line1="123 Checkout Lead Lane",
            city="West Jordan",
            state="UT",
            postal_code="84088",
            country="United States",
            fulfillment_method="delivery",
            requested_fulfillment_date=_future_date(),
            requested_window_start="13:00",
            requested_window_end="13:30",
            order_notes="Checkout Lead conversion contract.",
            marketing_opt_in=0,
        )
    finally:
        stripe_session.create_session_for_sales_order = original_create_session


def _counts() -> dict[str, int]:
    return {
        doctype: frappe.db.count(doctype)
        for doctype in (
            "Customer",
            "Contact",
            "Sales Order",
            "Payment Request",
            "Sales Invoice",
            "Payment Entry",
        )
    }


def _check_counts(before: dict[str, int], after: dict[str, int]) -> list[str]:
    expected_delta = {
        "Customer": 1,
        "Contact": 0,
        "Sales Order": 1,
        "Payment Request": 1,
        "Sales Invoice": 0,
        "Payment Entry": 0,
    }
    failures = []
    for doctype, delta in expected_delta.items():
        actual = after[doctype] - before[doctype]
        if actual != delta:
            failures.append(f"{doctype} delta expected {delta}, found {actual}")
    return failures


def _check_checkout_result(result: dict, lead, contact, original_contact_name: str) -> list[str]:
    failures = []
    if not result.get("ok"):
        failures.append(f"checkout result did not return ok: {result!r}")
    if not result.get("sales_order"):
        failures.append("checkout did not return Sales Order")
    if not result.get("payment_request"):
        failures.append("checkout did not return Payment Request")
    if not result.get("customer"):
        failures.append("checkout did not return Customer")
    if result.get("stripe_redirect_url", "").find("checkout.stripe.example.invalid") == -1:
        failures.append("checkout did not use the stubbed Stripe URL")
    if contact.name != original_contact_name:
        failures.append("checkout created or switched to a different Contact")

    customer_links = [
        row.link_name
        for row in contact.links
        if row.link_doctype == "Customer" and row.link_name
    ]
    if result.get("customer") not in customer_links:
        failures.append("existing Contact was not linked to the checkout Customer")

    lead_links = [
        row.link_name
        for row in contact.links
        if row.link_doctype == "Lead" and row.link_name
    ]
    if lead.name not in lead_links:
        failures.append("existing Contact lost its Lead link")
    return failures


def _check_lead_state(lead, result: dict) -> list[str]:
    failures = []
    if lead.status != "Converted":
        failures.append(f"Lead.status expected 'Converted', found {lead.status!r}")
    if lead.get("customer") != result.get("customer"):
        failures.append(
            f"Lead.customer expected {result.get('customer')!r}, found {lead.get('customer')!r}"
        )
    if lead.get("custom_pipeline_stage") != "Approved":
        failures.append(
            "Lead.custom_pipeline_stage expected 'Approved' after checkout conversion, "
            f"found {lead.get('custom_pipeline_stage')!r}"
        )
    return failures


def _check_task_state(tasks: list[dict]) -> list[str]:
    failures = []
    if _task_for_stage(tasks, "New Inquiry", open_only=True):
        failures.append("New Inquiry task should be closed after checkout conversion")
    if not _task_for_stage(tasks, "Approved", open_only=True):
        failures.append("Approved task should be open after checkout conversion")
    return failures


def _tasks_for_lead(lead_name: str) -> list[dict]:
    return frappe.get_all(
        "Task",
        filters={"custom_lt_lead": lead_name},
        fields=["name", "subject", "status", "custom_pipeline_stage"],
        order_by="creation asc",
        limit_page_length=100,
    )


def _task_for_stage(tasks: list[dict], stage: str, *, open_only: bool) -> dict | None:
    for task in tasks:
        if task.get("custom_pipeline_stage") != stage:
            continue
        if open_only and task.get("status") in {"Completed", "Cancelled"}:
            continue
        return task
    return None


def _active_task_stage(tasks: list[dict]) -> str | None:
    for task in tasks:
        if task.get("status") not in {"Completed", "Cancelled"}:
            return task.get("custom_pipeline_stage")
    return None
