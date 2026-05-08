"""LT guest checkout — true guest, no User account.

Two entry shapes both land here:

    /checkout?item=<code>&qty=<n>   buy-now path; server renders the summary line
    /checkout                        cart path; client JS hydrates summary from localStorage

Submission accepts EITHER `item_code` + `qty` (buy-now, backwards-compatible)
OR `items_json` (cart, JSON array of {item_code, qty}). The endpoint resolves
both shapes through `_resolve_cart_items` into a single canonical list, then
validates each line against published Website Item + Item Price on the server
side. Pricing is NEVER taken from the client.

Endpoint creates Customer + Contact (NO User) + Sales Order with one or more
lines + Payment Request + Stripe Checkout Session. Returns the hosted Stripe
URL; the caller redirects there.

Legal frame: customer data collected only for order fulfillment. No
account-creation surface. No marketing without opt-in. Receipt email
on order completion is transactional only (CAN-SPAM-safe).
"""
import json

import frappe
from frappe import _
from frappe.rate_limiter import rate_limit
from frappe.utils import escape_html, validate_email_address, flt, cint

from locally_twisted import commerce_rules
from locally_twisted.failure_recorder import record_backend_failure

no_cache = 1
sitemap = 0  # don't index the checkout page

MAX_CART_LINES = 50  # mirrors locally_twisted.api.cart.MAX_CART_LINES
MAX_QTY_PER_LINE = 99  # mirrors lt-guest-cart.js MAX_QTY_PER_LINE
PRICE_LIST = "Standard Selling"


PAGE_CSS = """
.lt-checkout {
    background-color: var(--lt-near-white);
    padding: 3rem 1rem 4rem;
    min-height: 60vh;
}
.lt-checkout__container {
    max-width: 1080px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 1fr;
    grid-template-areas: "aside" "main";
    gap: 1.5rem;
}
@media (min-width: 900px) {
    .lt-checkout__container {
        grid-template-columns: minmax(0, 1fr) 360px;
        grid-template-areas: "main aside";
        gap: 2.5rem;
    }
}
.lt-checkout__main { grid-area: main; min-width: 0; }
.lt-checkout__aside { grid-area: aside; }
@media (min-width: 900px) {
    .lt-checkout__aside { position: sticky; top: 1rem; align-self: start; }
}
.lt-checkout__title {
    font-family: 'Cormorant Garamond', Georgia, serif;
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
.lt-checkout__order-card {
    background-color: var(--lt-white);
    border: 1px solid rgba(26, 26, 26, 0.08);
    border-radius: 0.5rem;
    padding: 1.5rem;
}
.lt-checkout__order-heading {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 1.25rem;
    color: var(--lt-near-black);
    margin: 0 0 1rem;
    line-height: 1.2;
}
.lt-checkout__line {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin: 0 0 1rem;
    padding: 0 0 1rem;
    border-bottom: 1px solid rgba(26, 26, 26, 0.06);
}
.lt-checkout__line-img {
    width: 64px;
    height: 64px;
    border-radius: 0.375rem;
    background-color: var(--lt-warm-tint);
    background-size: cover;
    background-position: center;
    flex-shrink: 0;
}
.lt-checkout__line-body { flex: 1 1 auto; min-width: 0; }
.lt-checkout__line-name {
    font-family: 'Lato', sans-serif;
    font-weight: 600;
    color: var(--lt-near-black);
    margin: 0 0 0.2rem;
    font-size: 0.95rem;
    line-height: 1.3;
    word-break: break-word;
}
.lt-checkout__line-meta { font-size: 0.8rem; color: var(--lt-soft-gray); margin: 0; }
.lt-checkout__line-amount {
    font-family: 'Lato', sans-serif;
    font-weight: 600;
    color: var(--lt-near-black);
    font-size: 1rem;
    margin: 0;
    flex-shrink: 0;
}
.lt-checkout__totals-row {
    display: flex;
    justify-content: space-between;
    font-size: 0.9rem;
    color: var(--lt-near-black);
    padding: 0.35rem 0;
}
.lt-checkout__totals-row--grand {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 1.25rem;
    border-top: 1px solid rgba(26, 26, 26, 0.12);
    margin-top: 0.5rem;
    padding-top: 0.75rem;
}
.lt-checkout__secure {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid rgba(26, 26, 26, 0.06);
    font-size: 0.8rem;
    color: var(--lt-soft-gray);
    line-height: 1.45;
}
.lt-checkout__secure strong { color: var(--lt-near-black); font-weight: 600; }
.lt-checkout__form { margin: 0; }
.lt-checkout__fieldset {
    border: 1px solid rgba(14, 34, 64, 0.16);
    border-radius: 3px;
    padding: 1rem;
    margin: 0 0 1rem;
    background: rgba(255, 255, 255, 0.68);
}
.lt-checkout__fieldset legend {
    font-family: var(--lt-font-body);
    color: var(--lt-ink);
    font-weight: 900;
    font-size: 0.875rem;
    padding: 0 0.25rem;
}
.lt-checkout__choice-row {
    display: grid;
    grid-template-columns: 1fr;
    gap: 0.75rem;
}
@media (min-width: 640px) {
    .lt-checkout__choice-row { grid-template-columns: 1fr 1fr; }
}
.lt-checkout__choice {
    display: flex;
    align-items: center;
    gap: 0.55rem;
    border: 1px solid rgba(14, 34, 64, 0.18);
    border-radius: 3px;
    padding: 0.7rem 0.85rem;
    background: #fff;
    cursor: pointer;
}
.lt-checkout__choice input { margin: 0; }
.lt-checkout__choice span {
    font-family: var(--lt-font-body);
    color: var(--lt-ink);
    font-weight: 800;
}
.lt-checkout__hint {
    margin: 0.75rem 0 0;
    color: var(--lt-soft-gray);
    font-size: 0.85rem;
    line-height: 1.45;
}
.lt-checkout__field { margin-bottom: 1rem; }
.lt-checkout__field label {
    display: block;
    font-family: 'Lato', sans-serif;
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
    font-family: 'Lato', sans-serif;
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
    background-color: var(--lt-stone-tint);
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
    font-family: 'Lato', sans-serif;
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

/* Civic Celebration override */
.lt-checkout {
    background:
        linear-gradient(135deg, rgba(250, 247, 242, 0.98) 0%, rgba(250, 247, 242, 0.94) 58%, rgba(217, 199, 179, 0.34) 100%);
}
.lt-checkout__title,
.lt-checkout__order-heading,
.lt-checkout__totals-row--grand {
    font-family: var(--lt-font-heading);
    font-weight: 700;
    color: var(--lt-ink);
}
.lt-checkout__subtitle {
    color: var(--lt-soft-gray);
}
.lt-checkout__order-card {
    border: 1px solid rgba(14, 34, 64, 0.16);
    border-radius: 4px;
    box-shadow: 0 18px 36px rgba(10, 10, 11, 0.06);
}
.lt-checkout__line-name,
.lt-checkout__line-amount,
.lt-checkout__field label,
.lt-checkout__input,
.lt-checkout__submit {
    font-family: var(--lt-font-body);
}
.lt-checkout__line-name,
.lt-checkout__line-amount,
.lt-checkout__totals-row--grand {
    color: var(--lt-navy);
}
.lt-checkout__field label {
    color: var(--lt-ink);
    font-weight: 900;
}
.lt-checkout__input {
    background: #fff;
    border: 1px solid rgba(14, 34, 64, 0.18);
    border-radius: 3px;
}
.lt-checkout__input:focus {
    outline: 2px solid var(--lt-brass);
    border-color: var(--lt-navy);
}
.lt-checkout__notice {
    background-color: rgba(217, 199, 179, 0.3);
    border-radius: 3px;
}
.lt-checkout__notice a {
    color: var(--lt-navy);
}
.lt-checkout__submit {
    background-color: var(--lt-crimson);
    border-radius: 3px;
}
.lt-checkout__submit:hover,
.lt-checkout__submit:focus-visible {
    background-color: var(--lt-navy);
    outline: 2px solid var(--lt-brass);
}
"""


def get_context(context):
    """Render the guest checkout page in either buy-now or cart mode.

    Buy-now mode (?item=<code>&qty=<n>): server renders the single-item
    summary at request time. Backwards-compatible with existing buy-now
    URLs from product detail pages.

    Cart mode (no params): server renders an empty summary container.
    Client JS in checkout.html reads localStorage, calls
    locally_twisted.api.cart.get_cart_items, and hydrates the summary
    + a hidden items_json field on the form.

    Page-not-found is reserved for buy-now URLs whose item disappears;
    cart mode renders happily even with an empty cart (the JS shows an
    empty-cart message and disables submit).
    """
    item_code = (frappe.form_dict.get("item") or "").strip()
    qty = max(1, cint(frappe.form_dict.get("qty") or 1))

    context.metatags = {
        "description": "Locally Twisted secure checkout. Pay by card via Stripe.",
        "robots": "noindex, nofollow",
    }
    context.colocated_css = PAGE_CSS

    if item_code:
        # Buy-now: server-render the single line.
        from locally_twisted.api.cart import resolve_cart_item_for_sale

        cart_item = resolve_cart_item_for_sale(item_code, raise_on_missing=False)
        if not cart_item:
            raise frappe.PageDoesNotExistError(_("Item not found."))

        context.mode = "buy_now"
        context.title = f"Checkout - {cart_item['web_item_name']} | Locally Twisted"
        context.item = frappe._dict(cart_item)
        context.qty = qty
        context.unit_price = flt(cart_item["price_list_rate"])
        context.line_total = flt(cart_item["price_list_rate"]) * qty
        context.checkout_items_payload_json = _json_for_script([
            {
                "item_code": cart_item["item_code"],
                "website_item_code": cart_item.get("website_item_code"),
                "name": cart_item.get("web_item_name") or cart_item["item_code"],
                "qty": qty,
            }
        ])
    else:
        # Cart mode: empty shell, JS hydrates from localStorage.
        context.mode = "cart"
        context.title = "Checkout | Locally Twisted"
        context.item = None
        context.qty = 0
        context.unit_price = 0.0
        context.line_total = 0.0
        context.checkout_items_payload_json = "[]"
    return context


def _json_for_script(value):
    return json.dumps(value).replace("</", "<\\/")


def _normalize_line_qty(qty):
    qty_value = max(1, cint(qty or 1))
    if qty_value > MAX_QTY_PER_LINE:
        frappe.throw(
            _("Tiny snag: one cart line has more than {0} items. Please lower the quantity and try again.").format(MAX_QTY_PER_LINE),
            frappe.ValidationError,
        )
    return qty_value


def _resolve_cart_items(item_code, qty, items_json):
    """Resolve buy-now params OR items_json payload into one canonical list.

    Returns list of {"item_code": str, "qty": int}. Order is preserved.
    Duplicates are coalesced (later qty wins on collision — matches the
    client cart's add-or-increment semantics).

    Raises ValidationError on malformed input.
    """
    if items_json:
        try:
            parsed = json.loads(items_json)
        except (ValueError, TypeError):
            frappe.throw(
                _("Tiny snag: the cart details did not come through cleanly. Please refresh your cart and try again."),
                frappe.ValidationError,
            )
        if not isinstance(parsed, list):
            frappe.throw(
                _("Tiny snag: the cart details did not come through cleanly. Please refresh your cart and try again."),
                frappe.ValidationError,
            )
        if len(parsed) > MAX_CART_LINES:
            frappe.throw(
                _("Tiny snag: your cart has more than {0} items. Please remove a few items and try again.").format(MAX_CART_LINES),
                frappe.ValidationError,
            )
        seen = {}
        order = []
        for entry in parsed:
            if not isinstance(entry, dict):
                continue
            ic = (entry.get("item_code") or "").strip()
            q = _normalize_line_qty(entry.get("qty") or 1)
            if not ic:
                continue
            if ic not in seen:
                order.append(ic)
            seen[ic] = q
        return [{"item_code": ic, "qty": seen[ic]} for ic in order]

    if item_code:
        return [{"item_code": item_code.strip(), "qty": _normalize_line_qty(qty)}]

    return []


def _resolve_sale_lines(cart_items):
    """Resolve cart items into server-priced Sales Order lines.

    Delivery-zone quote handling is resolved later through fulfillment rules;
    product group alone does not make a priced cart line quote-only.
    """
    from locally_twisted.api.cart import resolve_cart_item_for_sale

    so_line_items = []
    resolved_items = []
    for line in cart_items:
        resolved = resolve_cart_item_for_sale(line["item_code"], raise_on_missing=False)
        if not resolved:
            frappe.throw(
                _("Tiny snag: one cart item is no longer available. Please return to your cart and choose again."),
                frappe.ValidationError,
            )
        qty_value = int(line["qty"])
        rate = flt(resolved["price_list_rate"])
        so_line = {
            "item_code": resolved["item_code"],
            "item_group": resolved.get("item_group"),
            "qty": qty_value,
            "rate": rate,
        }
        so_line.update(_item_tax_override(so_line))
        so_line_items.append(so_line)
        resolved_items.append({**resolved, "qty": qty_value, "line_total": rate * qty_value})
    return so_line_items, resolved_items


def _item_tax_override(line):
    if commerce_rules.is_taxable_item(
        item_code=line.get("item_code"),
        item_group=line.get("item_group"),
    ):
        return {}
    return {
        "item_tax_template": _non_taxable_item_tax_template(),
        "item_tax_rate": json.dumps({commerce_rules.TAX_ACCOUNT_HEAD: 0}),
    }


def _non_taxable_item_tax_template():
    company = frappe.defaults.get_user_default("Company") or frappe.db.get_value("Company", {}, "name")
    return (
        frappe.db.get_value(
            "Item Tax Template",
            {"title": commerce_rules.NON_TAXABLE_ITEM_TAX_TEMPLATE, "company": company},
            "name",
        )
        or commerce_rules.NON_TAXABLE_ITEM_TAX_TEMPLATE
    )


def _validate_requested_date(value):
    value = (value or "").strip()
    if not value:
        frappe.throw(_("Please choose a requested pickup or delivery date."), frappe.ValidationError)
    try:
        requested_date = frappe.utils.getdate(value)
    except Exception:
        frappe.throw(_("Requested date is not valid."), frappe.ValidationError)
    if requested_date < frappe.utils.getdate(frappe.utils.nowdate()):
        frappe.throw(_("Please choose today or a future pickup or delivery date."), frappe.ValidationError)
    return requested_date


def _validate_window(start, end):
    result = commerce_rules.validate_requested_window(start, end)
    if not result.ok:
        frappe.throw(_(result.message), frappe.ValidationError)
    return (start or "").strip(), (end or "").strip()


def _fulfillment_for_request(
    *,
    fulfillment_method,
    pickup_location,
    city,
    postal_code,
):
    method = (fulfillment_method or "delivery").strip().lower()
    if method not in {"pickup", "delivery"}:
        frappe.throw(_("Please choose pickup or delivery."), frappe.ValidationError)
    if method == "pickup" and pickup_location not in commerce_rules.PICKUP_LOCATIONS:
        frappe.throw(_("Please choose a pickup location."), frappe.ValidationError)
    return commerce_rules.resolve_fulfillment(
        method=method,
        postal_code=postal_code,
        city=city,
        pickup_location=pickup_location,
    )


def _tax_for_fulfillment(fulfillment, *, pickup_location, city, postal_code):
    if fulfillment.method == "pickup":
        location = commerce_rules.PICKUP_LOCATIONS[pickup_location]
        return commerce_rules.resolve_tax_rate(
            postal_code=location["postal_code"],
            city=location["city"],
        )
    return commerce_rules.resolve_tax_rate(postal_code=postal_code, city=city)


def _build_totals(so_line_items, fulfillment, tax):
    subtotal = commerce_rules.money(sum(flt(row["rate"]) * int(row["qty"]) for row in so_line_items))
    delivery_fee = commerce_rules.money(fulfillment.delivery_fee)
    taxable_total = commerce_rules.money(
        sum(
            flt(row["rate"]) * int(row["qty"])
            for row in so_line_items
            if commerce_rules.is_taxable_item(
                item_code=row.get("item_code"),
                item_group=row.get("item_group"),
            )
        )
    )
    tax_amount = commerce_rules.money(taxable_total * tax.rate / commerce_rules.Decimal("100"))
    total = commerce_rules.money(subtotal + delivery_fee + tax_amount)
    return {
        "subtotal": float(subtotal),
        "delivery_fee": float(delivery_fee),
        "tax_rate": float(tax.rate),
        "tax_amount": float(tax_amount),
        "total": float(total),
    }


@frappe.whitelist(allow_guest=True)
@rate_limit(limit=60, seconds=60 * 60)
def preview_checkout_totals(item_code="", qty=1, items_json="",
                            fulfillment_method="delivery", pickup_location="",
                            city="", postal_code=""):
    """Return server-trusted checkout totals for the visible order summary."""
    cart_items = _resolve_cart_items(item_code, qty, items_json)
    if not cart_items:
        return {"ok": False, "status": "empty_cart", "message": _("Please pick at least one item.")}
    so_line_items, _resolved_items = _resolve_sale_lines(cart_items)
    fulfillment = _fulfillment_for_request(
        fulfillment_method=fulfillment_method,
        pickup_location=(pickup_location or "").strip(),
        city=(city or "").strip(),
        postal_code=(postal_code or "").strip(),
    )
    if not fulfillment.can_checkout:
        subtotal = sum(flt(row["rate"]) * int(row["qty"]) for row in so_line_items)
        return {
            "ok": False,
            "status": "quote_required",
            "message": fulfillment.message,
            "subtotal": float(commerce_rules.money(subtotal)),
        }
    tax = _tax_for_fulfillment(
        fulfillment,
        pickup_location=(pickup_location or "").strip(),
        city=(city or "").strip(),
        postal_code=(postal_code or "").strip(),
    )
    return {"ok": True, "fulfillment": fulfillment.__dict__, **_build_totals(so_line_items, fulfillment, tax)}


@frappe.whitelist(allow_guest=True)
@rate_limit(limit=10, seconds=60 * 60)
def submit_guest_order(item_code="", qty=1, items_json="",
                       name="", email="", phone="",
                       address_line1="", address_line2="", city="", state="",
                       postal_code="", country="United States",
                       fulfillment_method="delivery", pickup_location="",
                       requested_fulfillment_date="",
                       requested_window_start="", requested_window_end="",
                       order_notes="", marketing_opt_in=0):
    """Create Customer + Contact + Sales Order for a guest checkout.

    Accepts EITHER buy-now params (item_code + qty) OR a cart payload
    (items_json — JSON list of {item_code, qty}). One canonical items
    list comes out of `_resolve_cart_items` and drives the rest.

    No User account is created. Customer is identified by email_id.
    Returns the Stripe-hosted checkout URL; caller redirects there.

    Loud-failure compliant: validation and persistence errors raise so
    the caller can surface the message to the user. Pricing is taken
    from server-side Item Price ONLY — client-supplied prices are never
    trusted at any layer.
    """
    name = (name or "").strip()
    email = (email or "").strip()
    phone = (phone or "").strip()
    address_line1 = (address_line1 or "").strip()
    address_line2 = (address_line2 or "").strip()
    city = (city or "").strip()
    state = (state or "").strip()
    postal_code = (postal_code or "").strip()
    country = (country or "United States").strip()
    pickup_location = (pickup_location or "").strip()
    requested_fulfillment_date = (requested_fulfillment_date or "").strip()
    requested_window_start = (requested_window_start or "").strip()
    requested_window_end = (requested_window_end or "").strip()
    order_notes = (order_notes or "").strip()
    marketing_opt_in = cint(marketing_opt_in)

    # ── Resolve + validate cart ──────────────────────────────────────
    cart_items = _resolve_cart_items(item_code, qty, items_json)
    if not cart_items:
        frappe.throw(_("Please pick at least one item before checking out."), frappe.ValidationError)

    # ── Validate customer fields ─────────────────────────────────────
    if not name:
        frappe.throw(_("Please tell us your name."), frappe.ValidationError)
    if not email:
        frappe.throw(_("Please give us an email so we can send your receipt."), frappe.ValidationError)
    if not phone:
        frappe.throw(_("Please give us a phone number for delivery coordination."), frappe.ValidationError)

    email = validate_email_address(email, throw=True)
    requested_date = _validate_requested_date(requested_fulfillment_date)
    requested_window_start, requested_window_end = _validate_window(
        requested_window_start,
        requested_window_end,
    )
    fulfillment = _fulfillment_for_request(
        fulfillment_method=fulfillment_method,
        pickup_location=pickup_location,
        city=city,
        postal_code=postal_code,
    )
    if fulfillment.method == "delivery" and (not address_line1 or not city or not state or not postal_code):
        frappe.throw(_("Please give us a complete delivery address."), frappe.ValidationError)

    # ── Validate each cart line; build SO line list with server prices.
    # Pricing comes from Item Price here, never from anything the client
    # sent. Unpublished or unpriced items abort the order — the cart UI
    # already prunes those at /cart load, so reaching here means the
    # state changed between cart load and submit (rare, but possible).
    so_line_items, resolved_items = _resolve_sale_lines(cart_items)

    if not fulfillment.can_checkout:
        return {
            "ok": False,
            "status": "quote_required",
            "message": fulfillment.message,
            "email": email,
            "fulfillment": fulfillment.__dict__,
            "items": [
                {
                    "item_code": row["item_code"],
                    "name": row.get("web_item_name") or row["item_code"],
                    "qty": row["qty"],
                }
                for row in resolved_items
            ],
        }

    tax = _tax_for_fulfillment(
        fulfillment,
        pickup_location=pickup_location,
        city=city,
        postal_code=postal_code,
    )
    totals = _build_totals(so_line_items, fulfillment, tax)

    if fulfillment.delivery_item_code and fulfillment.delivery_fee:
        delivery_line = {
            "item_code": fulfillment.delivery_item_code,
            "item_group": "Services",
            "qty": 1,
            "rate": float(fulfillment.delivery_fee),
        }
        delivery_line.update(_item_tax_override(delivery_line))
        so_line_items.append(delivery_line)

    safe_name = escape_html(name)
    safe_phone = escape_html(phone)

    # ── Customer dedup + Lead linking ────────────────────────────────
    # We identify customers by email. No User account is created — guest
    # checkout means just Customer + Contact records.
    #
    # Three cases the lookup chain handles:
    #   A. Email matches an existing Contact already linked to a Customer
    #      → reuse that Customer (return customer)
    #   B. Email matches an existing Contact linked ONLY to a Lead (the
    #      person filled /contact previously) -> create Customer and attach
    #      it to the same Contact. The Lead remains pending until the paid
    #      order cascade verifies payment and performs final CRM conversion.
    #   C. No match → create Customer + new Contact
    #
    # Lookup chain: Contact Email (child) → parent Contact → Dynamic Link.
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

    is_new_customer = False

    if customer_name:
        # Case A — returning customer.
        if marketing_opt_in:
            # Existing customer just opted in this checkout — flip the flag.
            frappe.db.set_value("Customer", customer_name, "marketing_opt_in", 1)
    elif contact_name:
        # Case B — Contact exists (likely from a Lead inquiry) but no
        # Customer linked yet. Promote the Contact: create the Customer,
        # attach Customer to the existing Contact, and leave any linked
        # Lead in inquiry state until Stripe payment succeeds.
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
        is_new_customer = True

        # Append Customer link to the existing Contact (preserves the
        # Lead link if one exists — Dynamic Links is a child table).
        contact_doc = frappe.get_doc("Contact", contact_name)
        contact_doc.append(
            "links",
            {"link_doctype": "Customer", "link_name": customer_name},
        )
        contact_doc.save(ignore_permissions=True)
    else:
        # Case C — fresh customer, no prior Contact.
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
        is_new_customer = True

        contact_doc = frappe.get_doc({
            "doctype": "Contact",
            "first_name": safe_name,
            "email_ids": [{"email_id": email, "is_primary": 1}],
            "phone_nos": [{"phone": safe_phone, "is_primary_mobile_no": 1}] if safe_phone else [],
            "links": [{"link_doctype": "Customer", "link_name": customer_name}],
        })
        contact_doc.insert(ignore_permissions=True)

    # ── Address (always create a fresh shipping address per order) ───
    address_doc = None
    if fulfillment.method == "delivery":
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
    so_doc = {
        "doctype": "Sales Order",
        "customer": customer_name,
        "order_type": "Shopping Cart",
        "transaction_date": frappe.utils.nowdate(),
        "delivery_date": requested_date,
        "currency": "USD",
        "selling_price_list": PRICE_LIST,
        "items": so_line_items,
        "taxes": [{
            "charge_type": "On Net Total",
            "account_head": commerce_rules.TAX_ACCOUNT_HEAD,
            "description": f"Utah sales tax ({tax.label})",
            "rate": float(tax.rate),
        }],
    }
    if address_doc:
        so_doc["shipping_address_name"] = address_doc.name
    so_doc.update(_sales_order_custom_fields(
        fulfillment=fulfillment,
        pickup_location=pickup_location,
        requested_fulfillment_date=requested_fulfillment_date,
        requested_window_start=requested_window_start,
        requested_window_end=requested_window_end,
    ))
    so = frappe.get_doc(so_doc)
    so.insert(ignore_permissions=True)
    so.submit()

    try:
        _record_order_notes(
            so.name,
            _compose_checkout_notes(
                order_notes=order_notes,
                fulfillment=fulfillment,
                pickup_location=pickup_location,
                requested_fulfillment_date=requested_fulfillment_date,
                requested_window_start=requested_window_start,
                requested_window_end=requested_window_end,
                totals=totals,
            ),
            sender=email,
        )
    except Exception as exc:
        record_backend_failure(
            surface="guest_checkout_to_payment_request",
            step="checkout_notes_transfer",
            severity="error",
            primary_doctype="Sales Order",
            primary_name=so.name,
            customer_visible_impact="Checkout can continue, but the customer's order notes did not attach to the Sales Order timeline.",
            internal_next_action="Review the checkout payload and add the missing order notes before fulfillment.",
            exception=exc,
            grouping_key=f"guest_checkout_to_payment_request:checkout_notes_transfer:{so.name}",
        )

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
    from locally_twisted.payments.settings import get_payment_gateway_account

    pr = frappe.get_doc({
        "doctype": "Payment Request",
        "payment_request_type": "Inward",
        "payment_gateway_account": get_payment_gateway_account(),
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
    # Cart mode → cancel returns to /cart so the customer can adjust
    # before retrying. Buy-now mode → cancel returns to the same buy-now
    # checkout URL with the original item + qty preserved.
    from locally_twisted.payments.stripe_session import create_session_for_sales_order

    if items_json:
        cancel_route = "/cart"
    else:
        first = so_line_items[0]
        cancel_route = f"/checkout?item={first['item_code']}&qty={first['qty']}"

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
        "address": address_doc.name if address_doc else None,
        "payment_request": pr.name,
        "stripe_redirect_url": stripe_url,
        "fulfillment": fulfillment.__dict__,
        "totals": totals,
    }


def _sales_order_custom_fields(
    *,
    fulfillment,
    pickup_location,
    requested_fulfillment_date,
    requested_window_start,
    requested_window_end,
):
    meta = frappe.get_meta("Sales Order")
    fields = {
        "custom_lt_fulfillment_method": "Pickup" if fulfillment.method == "pickup" else "Delivery",
        "custom_lt_delivery_zone": fulfillment.zone,
        "custom_lt_pickup_location": pickup_location if fulfillment.method == "pickup" else None,
        "custom_lt_requested_fulfillment_date": requested_fulfillment_date,
        "custom_lt_requested_window_start": requested_window_start,
        "custom_lt_requested_window_end": requested_window_end,
        "custom_lt_fulfillment_status": "Requested - Not Confirmed",
    }
    return {fieldname: value for fieldname, value in fields.items() if meta.has_field(fieldname)}


def _compose_checkout_notes(
    *,
    order_notes,
    fulfillment,
    pickup_location,
    requested_fulfillment_date,
    requested_window_start,
    requested_window_end,
    totals,
):
    parts = [
        f"Fulfillment: {fulfillment.label}",
        f"Requested date: {requested_fulfillment_date}",
        f"Requested window: {requested_window_start}-{requested_window_end} (requested, not confirmed)",
    ]
    if fulfillment.method == "pickup":
        parts.append(f"Pickup location: {pickup_location}")
    if fulfillment.delivery_fee:
        parts.append(f"Delivery fee: ${totals['delivery_fee']:.2f}")
    parts.append(f"Estimated tax: ${totals['tax_amount']:.2f}")
    if order_notes:
        parts.append("")
        parts.append(order_notes)
    return "\n".join(parts)


def _record_order_notes(so_name, notes, sender=None):
    """Attach customer checkout notes to the Sales Order timeline."""
    notes = (notes or "").strip()
    if not notes:
        return

    subject = f"Customer checkout notes - {so_name}"
    already_recorded = frappe.get_all(
        "Communication",
        filters={
            "reference_doctype": "Sales Order",
            "reference_name": so_name,
            "subject": subject,
        },
        limit=1,
    )
    if already_recorded:
        return

    frappe.get_doc({
        "doctype": "Communication",
        "communication_type": "Communication",
        "communication_medium": "Other",
        "sent_or_received": "Received",
        "reference_doctype": "Sales Order",
        "reference_name": so_name,
        "sender": sender,
        "subject": subject,
        "content": escape_html(notes),
        "status": "Open",
    }).insert(ignore_permissions=True)
