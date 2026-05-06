"""Checkout fulfillment contracts for delivery fees, pickup requests, and quote gate."""
from __future__ import annotations

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


def _run_contract():
    results = {
        "standard_delivery": _submit_paid_delivery("84088", "West Jordan", 15.0),
        "park_city_delivery": _submit_paid_delivery("84060", "Park City", 50.0),
        "pickup": _submit_paid_pickup(),
        "out_of_area_quote": _submit_out_of_area_quote(),
    }
    return {"ok": True, "results": results}


def _submit_paid_delivery(postal_code: str, city: str, expected_fee: float):
    result = _submit_checkout(
        email=f"lt-delivery-{postal_code}-{int(time.time())}@example.invalid",
        fulfillment_method="delivery",
        address_line1="123 Delivery Lane",
        city=city,
        state="UT",
        postal_code=postal_code,
        requested_fulfillment_date="2026-06-01",
        requested_window_start="13:00",
        requested_window_end="13:30",
    )
    so = frappe.get_doc("Sales Order", result["sales_order"])
    delivery_lines = [row for row in so.items if row.item_code in {"DELIVERY-STANDARD", "DELIVERY-PARK-CITY"}]
    if len(delivery_lines) != 1:
        raise ContractFail(f"{postal_code} expected one delivery line, found {len(delivery_lines)}")
    if float(delivery_lines[0].rate) != expected_fee:
        raise ContractFail(f"{postal_code} expected fee {expected_fee}, found {delivery_lines[0].rate}")
    if so.get("custom_lt_fulfillment_method") != "Delivery":
        raise ContractFail(f"{postal_code} Sales Order did not record Delivery fulfillment")
    if not so.taxes:
        raise ContractFail(f"{postal_code} Sales Order should include a tax row")
    return {"sales_order": so.name, "grand_total": float(so.grand_total)}


def _submit_paid_pickup():
    result = _submit_checkout(
        email=f"lt-pickup-{int(time.time())}@example.invalid",
        fulfillment_method="pickup",
        pickup_location="Riverdale",
        requested_fulfillment_date="2026-06-01",
        requested_window_start="18:00",
        requested_window_end="18:30",
        address_line1="",
        city="Riverdale",
        state="UT",
        postal_code="84405",
    )
    so = frappe.get_doc("Sales Order", result["sales_order"])
    delivery_lines = [row for row in so.items if row.item_code.startswith("DELIVERY-")]
    if delivery_lines:
        raise ContractFail("pickup order should not include a delivery fee line")
    if so.get("custom_lt_pickup_location") != "Riverdale":
        raise ContractFail("pickup order should record the requested pickup location")
    if so.get("custom_lt_requested_window_start") != "18:00":
        raise ContractFail("pickup order should record requested pickup window")
    return {"sales_order": so.name, "grand_total": float(so.grand_total)}


def _submit_out_of_area_quote():
    result = _submit_checkout(
        email=f"lt-outarea-{int(time.time())}@example.invalid",
        fulfillment_method="delivery",
        address_line1="123 Red Rock Road",
        city="St. George",
        state="UT",
        postal_code="84770",
        requested_fulfillment_date="2026-06-01",
        requested_window_start="13:00",
        requested_window_end="13:30",
    )
    if result.get("ok"):
        raise ContractFail("out-of-area delivery should not create a paid checkout")
    if result.get("status") != "quote_required":
        raise ContractFail(f"out-of-area expected quote_required status, found {result!r}")
    lead_name = result.get("lead")
    if not lead_name or not frappe.db.exists("Lead", lead_name):
        raise ContractFail("out-of-area quote path should create a Lead")
    counts = _money_counts_for_email(result["email"])
    if any(counts.values()):
        raise ContractFail(f"out-of-area quote path should not create money records: {counts}")
    return {"lead": lead_name}


def _submit_checkout(**kwargs):
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

    defaults = {
        "item_code": ITEM_CODE,
        "qty": 1,
        "name": "LT Fulfillment Contract",
        "phone": "801-555-0199",
        "country": "United States",
        "order_notes": "Checkout fulfillment contract.",
        "marketing_opt_in": 0,
    }
    defaults.update(kwargs)

    try:
        stripe_session.create_session_for_sales_order = fake_create_session_for_sales_order
        return submit_guest_order(**defaults)
    finally:
        stripe_session.create_session_for_sales_order = original_create_session


def _money_counts_for_email(email: str) -> dict[str, int]:
    customers = frappe.get_all("Customer", filters={"email_id": email}, pluck="name")
    if not customers:
        return {"customer": 0, "sales_order": 0, "payment_request": 0}
    sales_orders = frappe.get_all("Sales Order", filters={"customer": ["in", customers]}, pluck="name")
    payment_requests = (
        frappe.get_all(
            "Payment Request",
            filters={"reference_doctype": "Sales Order", "reference_name": ["in", sales_orders]},
            pluck="name",
        )
        if sales_orders
        else []
    )
    return {
        "customer": len(customers),
        "sales_order": len(sales_orders),
        "payment_request": len(payment_requests),
    }
