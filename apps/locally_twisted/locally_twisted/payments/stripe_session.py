"""Stripe Checkout Session helper for guest checkouts.

We use Stripe's hosted Checkout (https://checkout.stripe.com/<session>) instead
of Frappe's built-in card form. Two reasons:

1. Trust signal — customers recognize the Stripe-hosted page; the URL bar
   literally reads "checkout.stripe.com". Frappe's form is a custom card UI
   that looks unbranded and erodes confidence at the point of payment.
2. Modern Stripe API — Checkout Sessions support 3DS / SCA, dynamic payment
   methods (Apple Pay, Google Pay, Link), address autocomplete, and the
   real-time validation Stripe is famous for. Frappe's bundled flow uses the
   legacy Charges API and supports none of that.

Skill guidance applied (stripe-best-practices, 2026-04-29):
- Never recommend Charges API → we don't use it
- Don't pass payment_method_types — let dynamic payment methods choose
- Default to latest API/SDK — using whatever Stripe SDK ships in the bench

We keep ERPNext's existing Sales Order + Payment Request creation as the
auditable record. The Payment Request's payment_url is replaced with the
Stripe Checkout Session URL. When Stripe fires the checkout.session.completed
webhook, we reconcile by marking the PR Paid (creates Payment Entry).
"""
from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import flt, get_url

from locally_twisted.payments.settings import (
    get_stripe_payment_method_configuration,
    get_stripe_settings,
)
from locally_twisted.product_page_runtime import (
    customer_facing_line_image,
    customer_facing_line_label,
)


def stripe_line_items_for_sales_order(so) -> list[dict]:
    """Build Stripe line items that exactly match ERPNext grand_total."""
    currency = (so.currency or "USD").lower()
    line_items = []

    for item in so.items:
        item_name = customer_facing_line_label(item)
        product_data = {"name": item_name}
        image = customer_facing_line_image(item)
        if image:
            product_data["images"] = [_absolute_image_url(image)]
        qty = int(item.qty)
        unit_amount_cents = _money_to_cents(item.rate)
        line_items.append({
            "price_data": {
                "currency": currency,
                "product_data": product_data,
                "unit_amount": unit_amount_cents,
            },
            "quantity": qty,
        })

    expected_cents = _money_to_cents(so.grand_total)
    line_item_cents = _stripe_line_items_total_cents(line_items)
    adjustment_cents = expected_cents - line_item_cents

    if adjustment_cents < 0:
        frappe.throw(
            _(
                "Stripe checkout amount would exceed the order total. "
                "Please review the order before taking payment."
            ),
            frappe.ValidationError,
        )

    if adjustment_cents > 0:
        line_items.append({
            "price_data": {
                "currency": currency,
                "product_data": {"name": "Sales tax and charges"},
                "unit_amount": adjustment_cents,
            },
            "quantity": 1,
        })

    return line_items


def _stripe_line_items_total_cents(line_items: list[dict]) -> int:
    return sum(
        int(row["price_data"]["unit_amount"]) * int(row.get("quantity") or 1)
        for row in line_items
    )


def _money_to_cents(value) -> int:
    return int(round(flt(value) * 100))


def _absolute_image_url(image: str) -> str:
    image = str(image or "").strip()
    if image.startswith(("http://", "https://")):
        return image
    if not image.startswith("/"):
        image = f"/{image}"
    return get_url(image)


def create_session_for_sales_order(
    sales_order: str,
    payment_request: str,
    cancel_route: str,
    customer_email: str,
) -> str:
    """Create a Stripe Checkout Session for a guest's Sales Order.

    Returns the hosted Stripe URL. Caller redirects the customer's browser
    there. After payment, Stripe redirects to /payment-success?session_id=...
    which our www/payment_success.py override handles.

    Raises if the Stripe API call fails — the @whitelist caller in
    submit_guest_order will surface the error as a form-level message.
    """
    import stripe

    stripe_settings = get_stripe_settings()
    api_key = stripe_settings.get_password("secret_key", raise_exception=True)

    so = frappe.get_doc("Sales Order", sales_order)
    line_items = stripe_line_items_for_sales_order(so)

    site_url = get_url().rstrip("/")
    success_url = f"{site_url}/payment-success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{site_url}{cancel_route}"

    metadata = {
        "sales_order": so.name,
        "payment_request": payment_request,
        "lt_origin": "guest_checkout",
        "amount_expected_cents": str(_money_to_cents(so.grand_total)),
    }

    # Link is disabled at the ACCOUNT LEVEL via a custom Payment Method
    # Configuration (GL directive 2026-04-29). Stripe's default PMC has
    # link.display_preference="on", which makes the Stripe-hosted page
    # render Link "Save info" + Bank-via-Link UI even when the Session
    # restricts payment_method_types to ["card"]. Per Stripe support:
    # *"Link is controlled through the Dashboard. Create a custom payment
    # method configuration with Link off."* — see the knowledge gem in
    # the stripe:stripe-best-practices skill.
    #
    # We created `pmc_1TRZH2DfnlZQv66ncb001soG` ("LT No Link") on LT's
    # account with link=off, card=on. Passing payment_method_configuration
    # on every Session forces that configuration. payment_method_types is
    # NOT passed alongside because Stripe rejects the combination — when
    # a configuration is set, the configuration owns the method list.
    #
    # Live mode can override this through lt_stripe_payment_method_configuration
    # in site_config.json without changing this checkout code.
    #
    # GL's product reason: *"I hate Link, it's not going to gatekeep our
    # checkout."* Apple Pay + Google Pay still work — they're card wallets
    # that surface automatically on device-supported browsers, independent
    # of whether Link is on the configuration.
    session_kwargs = {
        "mode": "payment",
        "line_items": line_items,
        "success_url": success_url,
        "cancel_url": cancel_url,
        "allow_promotion_codes": True,
        "customer_email": customer_email,
        "client_reference_id": so.name,
        "metadata": metadata,
        "payment_intent_data": {"metadata": metadata},
    }
    payment_method_configuration = get_stripe_payment_method_configuration()
    if payment_method_configuration:
        session_kwargs["payment_method_configuration"] = payment_method_configuration

    session = stripe.checkout.Session.create(api_key=api_key, **session_kwargs)

    return session.url


def retrieve_session(session_id: str):
    """Retrieve a Checkout Session for verification on /payment-success."""
    import stripe

    stripe_settings = get_stripe_settings()
    api_key = stripe_settings.get_password("secret_key", raise_exception=True)
    return stripe.checkout.Session.retrieve(session_id, api_key=api_key)
