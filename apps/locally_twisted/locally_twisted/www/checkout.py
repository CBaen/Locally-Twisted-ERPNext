"""LT guest checkout — true guest, no User account.

Single-item buy-now flow for demo:
    /checkout?item=<item_code>&qty=<n>

- Page renders item summary + shipping form (email, name, phone, address)
- Submits to submit_guest_order via AJAX
- Endpoint creates Customer + Contact (NO User) + Sales Order
- Returns sales_order name; next turn wires the Stripe Payment Request

Legal frame: customer data collected only for order fulfillment. No
account-creation surface. No marketing without opt-in. Receipt email
on order completion is transactional only (CAN-SPAM-safe).
"""
import frappe
from frappe import _
from frappe.rate_limiter import rate_limit
from frappe.utils import escape_html, validate_email_address, flt, cint

no_cache = 1
sitemap = 0  # don't index the checkout page


PAGE_CSS = """
.lt-checkout {
    background-color: var(--lt-near-white);
    padding: 3rem 1rem 4rem;
    min-height: 60vh;
}
.lt-checkout__inner {
    max-width: 640px;
    margin: 0 auto;
}
.lt-checkout__title {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 2rem;
    color: var(--lt-near-black);
    margin: 0 0 0.5rem;
    line-height: 1.15;
}
.lt-checkout__subtitle {
    color: var(--lt-soft-gray);
    margin: 0 0 2rem;
    font-size: 1rem;
    line-height: 1.5;
}
.lt-checkout__summary {
    background-color: var(--lt-white);
    border: 1px solid rgba(26, 26, 26, 0.08);
    border-radius: 0.5rem;
    padding: 1.25rem;
    margin: 0 0 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}
.lt-checkout__summary-img {
    width: 80px;
    height: 80px;
    border-radius: 0.375rem;
    background-color: var(--lt-blush-tint);
    background-size: cover;
    background-position: center;
    flex-shrink: 0;
}
.lt-checkout__summary-body {
    flex: 1 1 auto;
}
.lt-checkout__summary-name {
    font-family: 'Raleway', sans-serif;
    font-weight: 600;
    color: var(--lt-near-black);
    margin: 0 0 0.25rem;
    font-size: 1rem;
}
.lt-checkout__summary-meta {
    font-size: 0.875rem;
    color: var(--lt-soft-gray);
    margin: 0;
}
.lt-checkout__summary-price {
    font-family: 'Raleway', sans-serif;
    font-weight: 600;
    color: var(--lt-near-black);
    font-size: 1.125rem;
    flex-shrink: 0;
}
.lt-checkout__form { margin: 0; }
.lt-checkout__field { margin-bottom: 1rem; }
.lt-checkout__field label {
    display: block;
    font-family: 'Raleway', sans-serif;
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--lt-near-black);
    margin-bottom: 0.35rem;
}
.lt-checkout__required { color: #c0392b; margin-left: 0.15rem; }
.lt-checkout__row {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1rem;
    margin-bottom: 1rem;
}
@media (min-width: 640px) {
    .lt-checkout__row { grid-template-columns: 1fr 1fr; }
    .lt-checkout__row--3 { grid-template-columns: 2fr 1fr 1fr; }
}
.lt-checkout__input {
    width: 100%;
    padding: 0.65rem 0.85rem;
    border: 1px solid rgba(26, 26, 26, 0.18);
    border-radius: 0.375rem;
    background-color: var(--lt-white);
    color: var(--lt-near-black);
    font-family: 'Raleway', sans-serif;
    font-size: 1rem;
    min-height: 44px;
    box-sizing: border-box;
}
.lt-checkout__input:focus {
    outline: 2px solid var(--lt-teal);
    outline-offset: 1px;
    border-color: var(--lt-teal);
}
.lt-checkout__notice {
    background-color: var(--lt-blue-tint);
    border-radius: 0.375rem;
    padding: 0.75rem 1rem;
    font-size: 0.875rem;
    color: var(--lt-near-black);
    margin: 1.5rem 0;
    line-height: 1.5;
}
.lt-checkout__notice a {
    color: var(--lt-teal);
    font-weight: 600;
    text-decoration: underline;
}
.lt-checkout__submit {
    background-color: var(--lt-teal);
    color: var(--lt-white);
    border: none;
    border-radius: 0.375rem;
    padding: 0.875rem 2rem;
    font-family: 'Raleway', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    min-height: 48px;
    width: 100%;
    margin-top: 1rem;
}
.lt-checkout__submit:hover,
.lt-checkout__submit:focus-visible {
    background-color: #006666;
    outline: 2px solid var(--lt-near-black);
    outline-offset: 2px;
}
.lt-checkout__submit[disabled] {
    opacity: 0.6;
    cursor: not-allowed;
}
.lt-checkout__feedback {
    margin-top: 1rem;
    padding: 0.85rem 1rem;
    border-radius: 0.375rem;
    font-size: 0.95rem;
    display: none;
    line-height: 1.5;
}
.lt-checkout__feedback.is-success {
    display: block;
    background-color: #e8f6ee;
    border: 1px solid #198754;
    color: #0e5732;
}
.lt-checkout__feedback.is-error {
    display: block;
    background-color: #fdecec;
    border: 1px solid #c0392b;
    color: #842424;
}
"""


def get_context(context):
    """Render the guest checkout page for one Website Item.

    Query params: item (item_code, required), qty (int, default 1).
    Page-not-found if the item is missing or unpublished.
    """
    item_code = (frappe.form_dict.get("item") or "").strip()
    qty = max(1, cint(frappe.form_dict.get("qty") or 1))

    if not item_code:
        frappe.throw(_("Please pick an item before checking out."), frappe.ValidationError)

    website_item = frappe.db.get_value(
        "Website Item",
        {"item_code": item_code, "published": 1},
        ["name", "item_code", "web_item_name", "website_image", "route"],
        as_dict=True,
    )
    if not website_item:
        raise frappe.PageDoesNotExistError(_("Item not found."))

    item_price = frappe.db.get_value(
        "Item Price",
        {"item_code": item_code, "price_list": "Standard Selling"},
        ["price_list_rate"],
    )
    if not item_price:
        frappe.throw(_("This item doesn't have a price set."), frappe.ValidationError)

    context.title = f"Checkout — {website_item.web_item_name} | Locally Twisted"
    context.metatags = {
        "description": "Locally Twisted secure checkout. Pay by card via Stripe.",
        "robots": "noindex, nofollow",
    }
    context.colocated_css = PAGE_CSS
    context.item = website_item
    context.qty = qty
    context.unit_price = flt(item_price)
    context.line_total = flt(item_price) * qty
    return context


@frappe.whitelist(allow_guest=True)
@rate_limit(limit=10, seconds=60 * 60)
def submit_guest_order(item_code="", qty=1, name="", email="", phone="",
                       address_line1="", address_line2="", city="", state="",
                       postal_code="", country="United States",
                       order_notes="", marketing_opt_in=0):
    """Create Customer + Contact + Sales Order for a guest checkout.

    No User account is created. Customer is identified by email_id.
    Returns the Sales Order name; the next stage (Stripe payment) is
    wired in a follow-up phase.

    Loud-failure compliant: validation and persistence errors raise so
    the caller can surface the message to the user.
    """
    item_code = (item_code or "").strip()
    qty = max(1, cint(qty))
    name = (name or "").strip()
    email = (email or "").strip()
    phone = (phone or "").strip()
    address_line1 = (address_line1 or "").strip()
    city = (city or "").strip()
    state = (state or "").strip()
    postal_code = (postal_code or "").strip()
    country = (country or "United States").strip()
    marketing_opt_in = cint(marketing_opt_in)

    # ── Validate ─────────────────────────────────────────────────────
    if not item_code:
        frappe.throw(_("Please pick an item before checking out."), frappe.ValidationError)
    if not name:
        frappe.throw(_("Please tell us your name."), frappe.ValidationError)
    if not email:
        frappe.throw(_("Please give us an email so we can send your receipt."), frappe.ValidationError)
    if not phone:
        frappe.throw(_("Please give us a phone number for delivery coordination."), frappe.ValidationError)
    if not address_line1 or not city or not state or not postal_code:
        frappe.throw(_("Please give us a complete delivery address."), frappe.ValidationError)

    email = validate_email_address(email, throw=True)

    # Verify item still published + priced
    website_item = frappe.db.get_value(
        "Website Item", {"item_code": item_code, "published": 1},
        ["item_code", "web_item_name"], as_dict=True,
    )
    if not website_item:
        frappe.throw(_("That item is not available right now."), frappe.ValidationError)

    item_price = frappe.db.get_value(
        "Item Price",
        {"item_code": item_code, "price_list": "Standard Selling"},
        ["price_list_rate"],
    )
    if not item_price:
        frappe.throw(_("That item doesn't have a price right now."), frappe.ValidationError)

    safe_name = escape_html(name)
    safe_phone = escape_html(phone)

    # ── Customer (idempotent by email) ───────────────────────────────
    # We identify customers by email. No User account is created — guest
    # checkout means just Customer + Contact records.
    # Lookup chain: Contact Email (child) → parent Contact → Dynamic Link → Customer.
    customer_name = None
    contact_name = frappe.db.get_value(
        "Contact Email", {"email_id": email}, "parent"
    )
    if contact_name:
        customer_name = frappe.db.get_value(
            "Dynamic Link",
            {"parent": contact_name, "link_doctype": "Customer", "parenttype": "Contact"},
            "link_name",
        )

    if not customer_name:
        customer_doc = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": safe_name,
            "customer_type": "Individual",
            "customer_group": "Individual",
            "territory": "All Territories",
            "marketing_opt_in": 1 if marketing_opt_in else 0,
        })
        customer_doc.insert(ignore_permissions=True)
        customer_name = customer_doc.name

        contact_doc = frappe.get_doc({
            "doctype": "Contact",
            "first_name": safe_name,
            "email_ids": [{"email_id": email, "is_primary": 1}],
            "phone_nos": [{"phone": safe_phone, "is_primary_mobile_no": 1}] if safe_phone else [],
            "links": [{"link_doctype": "Customer", "link_name": customer_name}],
        })
        contact_doc.insert(ignore_permissions=True)
    elif marketing_opt_in:
        # Existing customer just opted in this checkout — flip the flag.
        frappe.db.set_value("Customer", customer_name, "marketing_opt_in", 1)

    # ── Address (always create a fresh shipping address per order) ───
    address_doc = frappe.get_doc({
        "doctype": "Address",
        "address_title": safe_name,
        "address_type": "Shipping",
        "address_line1": escape_html(address_line1),
        "address_line2": escape_html(address_line2 or ""),
        "city": escape_html(city),
        "state": escape_html(state),
        "pincode": escape_html(postal_code),
        "country": country,
        "email_id": email,
        "phone": safe_phone,
        "links": [{"link_doctype": "Customer", "link_name": customer_name}],
    })
    address_doc.insert(ignore_permissions=True)

    # ── Sales Order ──────────────────────────────────────────────────
    # order_type="Shopping Cart" matters: ERPNext's Payment Request on_submit
    # checks this and skips the auto-email/PDF render if true. Without it,
    # the wkhtmltopdf PDF render runs and fails inside Docker because it
    # can't reach localhost:8081. Setting Shopping Cart is also semantically
    # accurate for guest webshop purchases.
    so = frappe.get_doc({
        "doctype": "Sales Order",
        "customer": customer_name,
        "order_type": "Shopping Cart",
        "transaction_date": frappe.utils.nowdate(),
        "delivery_date": frappe.utils.add_days(frappe.utils.nowdate(), 7),
        "currency": "USD",
        "selling_price_list": "Standard Selling",
        "shipping_address_name": address_doc.name,
        "items": [{
            "item_code": item_code,
            "qty": qty,
            "rate": flt(item_price),
        }],
    })
    so.insert(ignore_permissions=True)
    so.submit()

    # ── Payment Request (auditable record only) ──────────────────────
    # We still create the Payment Request because ERPNext uses it as the
    # auditable record linking SO → Payment Entry. But we DO NOT use its
    # payment_url — that points at Frappe's bundled card form (legacy
    # Charges API, ugly). Instead we hand the customer to a Stripe
    # Checkout Session (Stripe-hosted page, modern Stripe API).
    #
    # mute_email=1 + order_type="Shopping Cart" together suppress the
    # auto-email + wkhtmltopdf render that fails inside Docker. The
    # transactional receipt email fires later on Payment Entry submit.
    pr = frappe.get_doc({
        "doctype": "Payment Request",
        "payment_request_type": "Inward",
        "payment_gateway_account": "Stripe-Test - USD - LT",
        "party_type": "Customer",
        "party": customer_name,
        "reference_doctype": "Sales Order",
        "reference_name": so.name,
        "currency": "USD",
        "grand_total": flt(so.grand_total),
        "email_to": email,
        "subject": f"Payment for order {so.name} — Locally Twisted",
        "message": "Please complete your payment to confirm your order.",
    })
    pr.flags.mute_email = True
    pr.insert(ignore_permissions=True)
    pr.submit()

    # ── Stripe Checkout Session → hand the customer a hosted URL ─────
    from locally_twisted.payments.stripe_session import create_session_for_sales_order

    cancel_route = f"/checkout?item={item_code}&qty={qty}"
    stripe_url = create_session_for_sales_order(
        sales_order=so.name,
        payment_request=pr.name,
        cancel_route=cancel_route,
        customer_email=email,
    )

    frappe.db.commit()

    return {
        "ok": True,
        "sales_order": so.name,
        "customer": customer_name,
        "address": address_doc.name,
        "payment_request": pr.name,
        "stripe_redirect_url": stripe_url,
    }
