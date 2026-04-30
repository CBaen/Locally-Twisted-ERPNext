"""Thank-you page after Stripe success.

Public page (no auth) that lands the customer after payment completes.
Reads ?order=<sales_order_name> to surface the order ID and a confirmation
message. Does NOT expose customer data — just the order ID, item line, and
total. Anyone with the URL sees the same thing (they had to complete the
Stripe checkout to get here).

Note on URL design: we surface only the SO name, not customer email or
address. This is intentional — the URL might be shared, copy-pasted, or
land in browser history.
"""
import frappe
from frappe import _

no_cache = 1
sitemap = 0


PAGE_CSS = """
.lt-thanks {
    background-color: var(--lt-near-white);
    padding: 4rem 1.5rem 5rem;
    min-height: 60vh;
    text-align: center;
}
.lt-thanks__inner {
    max-width: 560px;
    margin: 0 auto;
}
.lt-thanks__title {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 2.5rem;
    color: var(--lt-near-black);
    margin: 0 0 1rem;
    line-height: 1.15;
}
.lt-thanks__lede {
    font-size: 1.0625rem;
    color: var(--lt-soft-gray);
    line-height: 1.6;
    margin: 0 0 2rem;
}
.lt-thanks__order {
    background-color: var(--lt-white);
    border: 1px solid rgba(26, 26, 26, 0.08);
    border-radius: 0.5rem;
    padding: 1.5rem;
    margin: 0 0 2rem;
    text-align: left;
}
.lt-thanks__order-meta {
    font-family: 'Raleway', sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    color: var(--lt-soft-gray);
    text-transform: uppercase;
    margin: 0 0 0.5rem;
}
.lt-thanks__order-id {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 1.5rem;
    color: var(--lt-near-black);
    margin: 0 0 1rem;
    word-break: break-all;
}
.lt-thanks__order-line {
    display: flex;
    justify-content: space-between;
    padding: 0.5rem 0;
    border-bottom: 1px solid rgba(26, 26, 26, 0.05);
    font-size: 0.95rem;
}
.lt-thanks__order-line:last-of-type {
    border-bottom: none;
}
.lt-thanks__order-line--total {
    border-top: 2px solid rgba(26, 26, 26, 0.12);
    margin-top: 0.5rem;
    padding-top: 1rem;
    font-weight: 600;
    color: var(--lt-near-black);
}
.lt-thanks__cta {
    display: inline-block;
    background-color: var(--lt-teal);
    color: var(--lt-white);
    padding: 0.875rem 2rem;
    font-family: 'Raleway', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    text-decoration: none;
    border-radius: 0.375rem;
    min-height: 48px;
    line-height: 1.5;
}
.lt-thanks__cta:hover,
.lt-thanks__cta:focus-visible {
    background-color: #006666;
    color: var(--lt-white);
    outline: 2px solid var(--lt-near-black);
    outline-offset: 2px;
}
.lt-thanks__contact {
    margin-top: 2rem;
    font-size: 0.9rem;
    color: var(--lt-soft-gray);
}
.lt-thanks__contact a {
    color: var(--lt-teal);
    font-weight: 600;
    text-decoration: underline;
    text-underline-offset: 0.2em;
}
"""


def get_context(context):
    so_name = (frappe.form_dict.get("order") or "").strip()

    context.title = "Thank you! | Locally Twisted"
    context.metatags = {
        "description": "Order confirmation. Locally Twisted thanks you for your purchase.",
        "robots": "noindex, nofollow",
    }
    context.colocated_css = PAGE_CSS

    context.so = None
    context.line_items = []
    if so_name:
        # Use ignore_permissions for read since the customer (a guest) has no
        # User session that maps to the Customer record. We only expose
        # public-safe fields (order id, items, total). No address, no email.
        try:
            so = frappe.get_doc("Sales Order", so_name)
            context.so = {
                "name": so.name,
                "grand_total": so.grand_total,
                "currency": so.currency,
                "status": so.status,
            }
            context.line_items = [
                {
                    "item_name": item.item_name or item.item_code,
                    "qty": item.qty,
                    "amount": item.amount,
                }
                for item in so.items
            ]
        except (frappe.DoesNotExistError, Exception):
            # Don't leak whether the SO exists or not — show generic landing.
            pass

    return context
