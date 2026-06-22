"""Checkout fulfillment contracts for delivery fees, pickup requests, and quote gate."""
from __future__ import annotations

from datetime import date, timedelta
import json
import time

import frappe


ITEM_CODE = "unicorn-bouquet-SMA"
DELIVERY_ONLY_ITEM_CODE = "graduation-grab-n-go-BYU"


class ContractFail(Exception):
    pass


def run():
    original_commit = frappe.db.commit
    from locally_twisted import ecommerce_pause

    original_is_ecommerce_paused = ecommerce_pause.is_ecommerce_paused
    intercepted_commits = []

    def no_commit(*args, **kwargs):
        intercepted_commits.append(True)

    try:
        frappe.db.commit = no_commit
        ecommerce_pause.is_ecommerce_paused = lambda: False
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
        ecommerce_pause.is_ecommerce_paused = original_is_ecommerce_paused
        frappe.db.rollback()


def _run_contract():
    results = {
        "setup_records": _check_setup_records(),
        "standard_delivery": _submit_paid_delivery("84088", "West Jordan", 15.0),
        "standard_delivery_utah_county": _submit_paid_delivery("84003", "American Fork", 15.0),
        "park_city_delivery": _submit_paid_delivery("84060", "Park City", 50.0),
        "pickup": _submit_paid_pickup(),
        "configured_bouquet_pickup": _submit_configured_bouquet_pickup(),
        "mixed_delivery_only_and_pickup": _submit_mixed_delivery_only_and_pickup(),
        "out_of_area_quote": _submit_out_of_area_quote(),
        "past_date_rejected": _submit_past_date_rejected(),
    }
    return {"ok": True, "results": results}


def _check_setup_records():
    from locally_twisted import commerce_rules

    required_so_fields = {
        "custom_lt_fulfillment_method",
        "custom_lt_delivery_zone",
        "custom_lt_pickup_location",
        "custom_lt_requested_fulfillment_date",
        "custom_lt_requested_window_start",
        "custom_lt_requested_window_end",
        "custom_lt_fulfillment_status",
    }
    meta = frappe.get_meta("Sales Order")
    missing_fields = sorted(field for field in required_so_fields if not meta.has_field(field))
    if missing_fields:
        raise ContractFail(f"Sales Order is missing checkout fulfillment fields: {missing_fields}")

    required_line_fields = {
        "custom_lt_fulfillment_policy",
        "custom_lt_line_fulfillment_method",
        "custom_lt_line_fulfillment_zone",
        "custom_lt_line_fulfillment_note",
    }
    line_meta = frappe.get_meta("Sales Order Item")
    missing_line_fields = sorted(field for field in required_line_fields if not line_meta.has_field(field))
    if missing_line_fields:
        raise ContractFail(f"Sales Order Item is missing checkout line fulfillment fields: {missing_line_fields}")

    delivery_items = {
        commerce_rules.DELIVERY_STANDARD_ITEM,
        commerce_rules.DELIVERY_PARK_CITY_ITEM,
    }
    company = frappe.defaults.get_user_default("Company") or frappe.db.get_value("Company", {}, "name")
    if not frappe.db.exists(
        "Item Tax Template",
        {"title": commerce_rules.NON_TAXABLE_ITEM_TAX_TEMPLATE, "company": company},
    ):
        raise ContractFail(
            f"missing non-taxable item tax template: {commerce_rules.NON_TAXABLE_ITEM_TAX_TEMPLATE}"
        )
    try:
        tax_account = commerce_rules.validate_sales_tax_account_head()
    except Exception as exc:
        raise ContractFail(f"checkout sales tax account is not transaction-ready: {exc}") from exc

    missing_items = sorted(item for item in delivery_items if not frappe.db.exists("Item", item))
    if missing_items:
        raise ContractFail(f"missing checkout delivery items: {missing_items}")

    missing_prices = sorted(
        item
        for item in delivery_items
        if not frappe.db.exists(
            "Item Price",
            {"item_code": item, "price_list": commerce_rules.PRICE_LIST, "selling": 1},
        )
    )
    if missing_prices:
        raise ContractFail(f"missing checkout delivery item prices: {missing_prices}")

    return {
        "sales_order_fields": len(required_so_fields),
        "delivery_items": len(delivery_items),
        "sales_tax_account": tax_account,
    }


def _future_date() -> str:
    return (date.today() + timedelta(days=30)).isoformat()


def _next_pickup_date() -> str:
    target = date.today()
    while target.weekday() != 1:
        target += timedelta(days=1)
    return target.isoformat()


def _submit_paid_delivery(postal_code: str, city: str, expected_fee: float):
    result = _submit_checkout(
        email=f"lt-delivery-{postal_code}-{int(time.time())}@example.invalid",
        fulfillment_method="delivery",
        address_line1="123 Delivery Lane",
        city=city,
        state="UT",
        postal_code=postal_code,
        requested_fulfillment_date=_future_date(),
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
    if not delivery_lines[0].item_tax_rate:
        raise ContractFail(f"{postal_code} delivery line should carry a non-taxable item tax override")
    product_subtotal = sum(row.net_amount for row in so.items if not row.item_code.startswith("DELIVERY-"))
    expected_tax = round(float(product_subtotal) * float(so.taxes[0].rate) / 100, 2)
    actual_tax = round(float(so.total_taxes_and_charges), 2)
    if actual_tax != expected_tax:
        raise ContractFail(
            f"{postal_code} tax should apply to goods only; expected {expected_tax}, found {actual_tax}"
        )
    return {"sales_order": so.name, "grand_total": float(so.grand_total)}


def _submit_paid_pickup():
    result = _submit_checkout(
        email=f"lt-pickup-{int(time.time())}@example.invalid",
        fulfillment_method="pickup",
        pickup_location="Riverdale",
        requested_fulfillment_date=_next_pickup_date(),
        requested_window_start="12:00",
        requested_window_end="12:30",
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
    if so.get("custom_lt_requested_window_start") != "12:00":
        raise ContractFail("pickup order should record requested pickup window")
    return {"sales_order": so.name, "grand_total": float(so.grand_total)}


def _submit_configured_bouquet_pickup():
    dash = chr(8212)
    size = f"Small {dash} 1 featured foil balloon, 2 coordinating foil balloons, 7 latex balloons"
    configuration = {
        "schema_version": "lt-product-config-v1",
        "item_code": "encanto-bouquet-SMA",
        "website_item_code": "encanto-bouquet",
        "selected_options": {"Bouquet Size": size},
        "color_recipes": [],
        "configuration_groups": [],
        "add_ons": [],
        "customizations": [],
    }
    result = _submit_checkout(
        email=f"lt-encanto-pickup-{int(time.time())}@example.invalid",
        item_code="",
        items_json=json.dumps(
            [
                {
                    "item_code": "encanto-bouquet-SMA",
                    "qty": 1,
                    "configuration": configuration,
                }
            ]
        ),
        fulfillment_method="pickup",
        pickup_location="West Jordan",
        requested_fulfillment_date=_next_pickup_date(),
        requested_window_start="12:00",
        requested_window_end="12:30",
        address_line1="",
        city="West Jordan",
        state="UT",
        postal_code="84088",
    )
    so = frappe.get_doc("Sales Order", result["sales_order"])
    first_line = so.items[0]
    payload = json.loads(first_line.get("custom_lt_configuration_json") or "{}")
    if payload.get("selected_options", {}).get("Bouquet Size") != size:
        raise ContractFail(f"configured bouquet size was not preserved: {payload}")
    return {"sales_order": so.name, "item_code": first_line.item_code}


def _submit_mixed_delivery_only_and_pickup():
    result = _submit_checkout(
        email=f"lt-mixed-fulfillment-{int(time.time())}@example.invalid",
        item_code="",
        items_json=json.dumps(
            [
                {"item_code": ITEM_CODE, "qty": 1},
                {"item_code": DELIVERY_ONLY_ITEM_CODE, "qty": 1},
            ]
        ),
        fulfillment_method="pickup",
        pickup_location="West Jordan",
        address_line1="123 Mixed Lane",
        city="West Jordan",
        state="UT",
        postal_code="84088",
        requested_fulfillment_date=_next_pickup_date(),
        requested_window_start="12:00",
        requested_window_end="12:30",
    )
    so = frappe.get_doc("Sales Order", result["sales_order"])
    if so.get("custom_lt_fulfillment_method") != "Mixed":
        raise ContractFail(f"mixed cart should record Mixed fulfillment, found {so.get('custom_lt_fulfillment_method')}")
    delivery_lines = [row for row in so.items if row.item_code.startswith("DELIVERY-")]
    if len(delivery_lines) != 1:
        raise ContractFail(f"mixed cart should include one delivery fee line, found {len(delivery_lines)}")
    pickup_lines = [row for row in so.items if row.item_code == ITEM_CODE]
    delivery_only_lines = [row for row in so.items if row.item_code == DELIVERY_ONLY_ITEM_CODE]
    if not pickup_lines or pickup_lines[0].get("custom_lt_line_fulfillment_method") != "Pickup":
        raise ContractFail("mixed cart should keep pickup-eligible product as Pickup")
    if not delivery_only_lines or delivery_only_lines[0].get("custom_lt_line_fulfillment_method") != "Delivery":
        raise ContractFail("mixed cart should keep delivery-only product as Delivery")
    if delivery_only_lines[0].get("custom_lt_fulfillment_policy") != "Delivery Only":
        raise ContractFail("delivery-only line should retain Delivery Only policy")
    return {"sales_order": so.name, "method": so.get("custom_lt_fulfillment_method")}


def _submit_out_of_area_quote():
    email = f"lt-outarea-{int(time.time())}@example.invalid"
    result = _submit_checkout(
        allow_quote_required=True,
        email=email,
        fulfillment_method="delivery",
        address_line1="123 Red Rock Road",
        city="St. George",
        state="UT",
        postal_code="84770",
        requested_fulfillment_date=_future_date(),
        requested_window_start="13:00",
        requested_window_end="13:30",
    )
    if result.get("ok"):
        raise ContractFail("out-of-area delivery should not create a paid checkout")
    if result.get("status") != "quote_required":
        raise ContractFail(f"out-of-area expected quote_required status, found {result!r}")
    if result.get("lead"):
        raise ContractFail("checkout quote fallback should not create a Lead before /contact submit")
    if frappe.db.exists("Lead", {"email_id": email}):
        raise ContractFail("checkout quote fallback should leave Lead creation to /contact")
    counts = _money_counts_for_email(result["email"])
    if any(counts.values()):
        raise ContractFail(f"out-of-area quote path should not create money records: {counts}")
    return {"contact_handoff": True}


def _submit_past_date_rejected():
    try:
        _submit_checkout(
            email=f"lt-past-date-{int(time.time())}@example.invalid",
            fulfillment_method="delivery",
            address_line1="123 Old Date Road",
            city="West Jordan",
            state="UT",
            postal_code="84088",
            requested_fulfillment_date="2000-01-01",
            requested_window_start="13:00",
            requested_window_end="13:30",
        )
    except frappe.ValidationError as exc:
        if "future" not in str(exc).lower() and "today" not in str(exc).lower():
            raise ContractFail(f"past date rejected with unexpected message: {exc}")
        return {"rejected": True}
    raise ContractFail("past requested fulfillment date should be rejected before checkout records are created")


def _submit_checkout(allow_quote_required: bool = False, **kwargs):
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
        "preferred_contact_method": "email",
        "country": "United States",
        "order_notes": "Checkout fulfillment contract.",
        "marketing_opt_in": 0,
    }
    defaults.update(kwargs)

    try:
        stripe_session.create_session_for_sales_order = fake_create_session_for_sales_order
        result = submit_guest_order(**defaults)
        if not result.get("ok"):
            status = result.get("status")
            if status == "ecommerce_paused":
                raise ContractFail(
                    "checkout API returned ecommerce_paused inside the verifier; "
                    "the verifier pause bypass is not active"
                )
            if allow_quote_required and status == "quote_required":
                return result
            raise ContractFail(f"checkout submit failed before Sales Order creation: {result!r}")
        if not result.get("sales_order"):
            raise ContractFail(f"checkout submit did not return a Sales Order: {result!r}")
        return result
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
