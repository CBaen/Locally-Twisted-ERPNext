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

    return {
        "ok": not failures,
        "failures": failures,
        "evidence": evidence,
    }


def _fake_sales_order(*, grand_total: float, items: list[dict[str, object]]):
    return SimpleNamespace(
        currency="USD",
        grand_total=grand_total,
        items=[frappe._dict(item) for item in items],
    )
