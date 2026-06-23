"""Verify Stripe Checkout line items stay in parity with ERPNext totals."""
from __future__ import annotations

import frappe
from types import SimpleNamespace


def run() -> dict[str, object]:
    failures: list[str] = []
    evidence: dict[str, object] = {}

    from locally_twisted.payments.stripe_session import (
        _stripe_line_items_total_cents,
        stripe_line_items_for_sales_order,
    )

    taxable_order = _fake_sales_order(
        grand_total=107.45,
        items=[{"item_code": "taxable-decor", "item_name": "Taxable decor", "rate": 100.00, "qty": 1}],
    )
    taxable_items = stripe_line_items_for_sales_order(taxable_order)
    taxable_total = _stripe_line_items_total_cents(taxable_items)
    evidence["taxable_order_cents"] = 10745
    evidence["taxable_stripe_cents"] = taxable_total
    evidence["taxable_adjustment_line_count"] = len(taxable_items) - 1
    if taxable_total != 10745:
        failures.append(f"Taxable order Stripe total {taxable_total} cents, expected 10745")
    if len(taxable_items) != 2:
        failures.append("Taxable order should include a tax/charges adjustment line")

    nontaxable_order = _fake_sales_order(
        grand_total=315.00,
        items=[
            {"item_code": "service-deposit", "item_name": "Service deposit", "rate": 300.00, "qty": 1},
            {"item_code": "local-delivery", "item_name": "Local delivery", "rate": 15.00, "qty": 1},
        ],
    )
    nontaxable_items = stripe_line_items_for_sales_order(nontaxable_order)
    nontaxable_total = _stripe_line_items_total_cents(nontaxable_items)
    evidence["nontaxable_order_cents"] = 31500
    evidence["nontaxable_stripe_cents"] = nontaxable_total
    evidence["nontaxable_adjustment_line_count"] = len(nontaxable_items) - 2
    if nontaxable_total != 31500:
        failures.append(f"Nontaxable order Stripe total {nontaxable_total} cents, expected 31500")
    if len(nontaxable_items) != 2:
        failures.append("Nontaxable order should not need an adjustment line")

    configured_order = _fake_sales_order(
        grand_total=71.00,
        items=[
            {
                "item_code": "unicorn-bouquet-SMA",
                "item_name": "Unicorn Bouquet",
                "rate": 35.00,
                "qty": 1,
                "custom_lt_configuration_json": '{"selected_media":{"image":"/files/selected-unicorn-proof.png"}}',
            },
            {
                "item_code": "ADDON-FOIL-NUMBER",
                "item_name": "Foil Number Add-On",
                "rate": 12.00,
                "qty": 3,
                "custom_lt_configuration_summary": "Add-on - Foil number: 111; Parent item - unicorn-bouquet-SMA; Qty per product - 3",
            },
        ],
    )
    configured_items = stripe_line_items_for_sales_order(configured_order)
    configured_names = [
        row["price_data"]["product_data"]["name"]
        for row in configured_items
    ]
    evidence["configured_line_names"] = configured_names
    configured_images = [
        row["price_data"]["product_data"].get("images") or []
        for row in configured_items
    ]
    evidence["configured_line_images"] = configured_images
    if "Foil number: 111" not in " ".join(configured_names):
        failures.append(f"Configured add-on Stripe line should preserve selected foil number, found {configured_names}")
    if "Parent item" in " ".join(configured_names):
        failures.append(f"Configured add-on Stripe line should not expose internal parent summary, found {configured_names}")
    if not any("/files/selected-unicorn-proof.png" in " ".join(images) for images in configured_images):
        failures.append(f"Configured Stripe line should include selected Product Setup image, found {configured_images}")

    negative_adjustment_rejected = False
    try:
        stripe_line_items_for_sales_order(
            _fake_sales_order(
                grand_total=90.00,
                items=[{"item_code": "over-total", "item_name": "Over total", "rate": 100.00, "qty": 1}],
            )
        )
    except frappe.ValidationError:
        negative_adjustment_rejected = True
    evidence["negative_adjustment_rejected"] = negative_adjustment_rejected
    if not negative_adjustment_rejected:
        failures.append("Stripe helper should reject item totals greater than ERPNext grand_total")

    promo_session_kwargs = _capture_checkout_session_kwargs(
        _fake_sales_order(
            name="SO-PROMO-CODE-CONTRACT",
            grand_total=125.00,
            items=[{"item_code": "promo-test", "item_name": "Promo Test", "rate": 125.00, "qty": 1}],
        )
    )
    evidence["allow_promotion_codes"] = promo_session_kwargs.get("allow_promotion_codes")
    evidence["payment_method_collection"] = promo_session_kwargs.get("payment_method_collection")
    if promo_session_kwargs.get("allow_promotion_codes") is not True:
        failures.append("Stripe Checkout Session must enable allow_promotion_codes for live gift-card codes")
    if "payment_method_collection" in promo_session_kwargs:
        failures.append("Stripe Checkout Session must not set payment_method_collection for one-time payment gift-card orders")

    return {
        "ok": not failures,
        "failures": failures,
        "evidence": evidence,
    }


def _fake_sales_order(*, grand_total: float, items: list[dict[str, object]], name: str = "SO-CONTRACT"):
    return SimpleNamespace(
        name=name,
        currency="USD",
        grand_total=grand_total,
        items=[frappe._dict(item) for item in items],
    )


def _capture_checkout_session_kwargs(sales_order):
    import stripe

    import locally_twisted.payments.stripe_session as stripe_session

    original_get_doc = frappe.get_doc
    original_get_url = stripe_session.get_url
    original_get_stripe_settings = stripe_session.get_stripe_settings
    original_get_payment_method_configuration = stripe_session.get_stripe_payment_method_configuration
    original_create = stripe.checkout.Session.create
    captured = {}

    class FakeStripeSettings:
        def get_password(self, fieldname, raise_exception=False):
            if fieldname != "secret_key":
                raise AssertionError(f"unexpected Stripe settings field: {fieldname}")
            return "sk_test_contract"

    class FakeSession:
        url = "https://checkout.stripe.example.invalid/session"

    def fake_get_doc(doctype, name=None, *args, **kwargs):
        if doctype == "Sales Order" and name == sales_order.name:
            return sales_order
        return original_get_doc(doctype, name, *args, **kwargs)

    def fake_get_url(path=None):
        base = "https://locallytwisted.example"
        if not path:
            return base
        path = str(path)
        if path.startswith(("http://", "https://")):
            return path
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{base}{path}"

    def fake_create(api_key=None, **kwargs):
        captured.update(kwargs)
        captured["api_key"] = api_key
        return FakeSession()

    try:
        frappe.get_doc = fake_get_doc
        stripe_session.get_url = fake_get_url
        stripe_session.get_stripe_settings = lambda: FakeStripeSettings()
        stripe_session.get_stripe_payment_method_configuration = lambda: "pmc_test_contract"
        stripe.checkout.Session.create = fake_create
        stripe_session.create_session_for_sales_order(
            sales_order.name,
            "PR-PROMO-CODE-CONTRACT",
            "/checkout",
            "lt-promo-contract@example.invalid",
        )
        return captured
    finally:
        frappe.get_doc = original_get_doc
        stripe_session.get_url = original_get_url
        stripe_session.get_stripe_settings = original_get_stripe_settings
        stripe_session.get_stripe_payment_method_configuration = original_get_payment_method_configuration
        stripe.checkout.Session.create = original_create
