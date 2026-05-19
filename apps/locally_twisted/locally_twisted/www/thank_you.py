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
from frappe.utils import flt

from locally_twisted.product_page_runtime import customer_facing_line_label

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
    font-family: 'Cormorant Garamond', Georgia, serif;
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
.lt-thanks__notice {
    background-color: #fffdf9;
    border: 1px solid rgba(179, 27, 52, 0.22);
    border-left: 4px solid #b31b34;
    border-radius: 0.375rem;
    color: #0a0a0b;
    font-size: 0.95rem;
    line-height: 1.55;
    margin: -0.75rem 0 2rem;
    padding: 1rem;
    text-align: left;
}
.lt-thanks__notice strong {
    color: #0e2240;
    display: block;
    margin-bottom: 0.25rem;
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
    font-family: 'Lato', sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    color: var(--lt-soft-gray);
    text-transform: uppercase;
    margin: 0 0 0.5rem;
}
.lt-thanks__order-id {
    font-family: 'Cormorant Garamond', Georgia, serif;
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
    font-family: 'Lato', sans-serif;
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

/* Civic Celebration redesign for secondary editorial pages. */
.lt-thanks {
    background-color: #faf7f2;
    color: #0a0a0b;
}
.lt-thanks__inner {
    background-color: #fffdf9;
    border: 1px solid rgba(14, 34, 64, 0.16);
    border-top: 8px solid #b31b34;
    border-radius: 0.375rem;
    box-shadow: 0 18px 50px rgba(14, 34, 64, 0.08);
    padding: 2rem;
}
.lt-thanks__eyebrow {
    color: #b31b34;
    font-size: 0.75rem;
    font-weight: 800;
    letter-spacing: 0.14em;
    margin: 0 0 0.75rem;
    text-transform: uppercase;
}
.lt-thanks__title,
.lt-thanks__order-id {
    color: #0e2240;
    letter-spacing: 0;
}
.lt-thanks__lede,
.lt-thanks__contact {
    color: rgba(10, 10, 11, 0.72);
}
.lt-thanks__order {
    background-color: #faf7f2;
    border-color: rgba(14, 34, 64, 0.16);
    border-radius: 0.375rem;
}
.lt-thanks__order-meta {
    color: #b31b34;
    font-weight: 800;
}
.lt-thanks__order-line {
    border-bottom-color: rgba(14, 34, 64, 0.12);
}
.lt-thanks__order-line--total {
    border-top-color: rgba(14, 34, 64, 0.28);
    color: #0a0a0b;
}
.lt-thanks__cta {
    background-color: #b31b34;
    border: 1px solid #b31b34;
    color: #faf7f2;
    border-radius: 0.25rem;
}
.lt-thanks__cta:hover,
.lt-thanks__cta:focus-visible {
    background-color: #0e2240;
    border-color: #0e2240;
    color: #faf7f2;
}
"""


def get_context(context):
    so_name = (frappe.form_dict.get("order") or "").strip()
    status = (frappe.form_dict.get("status") or "").strip().lower()

    context.title = "Thank you! | Locally Twisted"
    context.metatags = {
        "description": "Payment status check for a Locally Twisted order.",
        "robots": "noindex, nofollow",
    }
    context.colocated_css = PAGE_CSS
    reconciliation_pending = (
        (frappe.form_dict.get("reconciliation") or "").strip().lower() == "pending"
    )
    payment_state = _payment_state_for_sales_order(so_name) if so_name else _payment_check_state()
    if status == "payment-check":
        payment_state = _payment_check_state()
    payment_check_needed = status == "payment-check" or not so_name or payment_state["state"] == "payment_check"
    context.thank_you_eyebrow = payment_state["eyebrow"]
    context.thank_you_lede = payment_state["lede"]
    context.reconciliation_notice = payment_state["notice"]
    context.reconciliation_pending = (
        reconciliation_pending
        or payment_check_needed
        or payment_state["state"] == "reconciliation_needed"
    )

    if payment_check_needed:
        if reconciliation_pending and so_name:
            context.reconciliation_notice = (
                "Tiny snag: this page was asked to show a payment follow-up, "
                "but the order is not marked paid in our records yet. If you saw "
                "a card charge, please call (801) 285-0860 or email "
                "billing@locallytwisted.com so we can match it up for you."
            )
    elif reconciliation_pending:
        context.thank_you_lede = (
            "Your payment came through. We have your order, and the final receipt "
            "or invoice check is still finishing in the background."
        )
        context.reconciliation_notice = (
            "Tiny snag: the final receipt or invoice details are still being checked. "
            "The team has an internal record to follow up."
        )
    else:
        context.thank_you_lede = (
            "Your payment came through. We have your order and will send a confirmation "
            "receipt to the email you gave us."
        )
        context.reconciliation_notice = ""

    context.so = None
    context.line_items = []
    if so_name and not payment_check_needed:
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
                    "item_name": customer_facing_line_label(item),
                    "qty": item.qty,
                    "amount": item.amount,
                }
                for item in so.items
            ]
        except (frappe.DoesNotExistError, Exception):
            # Don't leak whether the SO exists or not — show generic landing.
            pass

    return context


def _payment_check_state():
    return {
        "state": "payment_check",
        "eyebrow": "Payment Check",
        "lede": "Tiny snag: we could not confirm this payment return in the browser.",
        "notice": (
            "If you saw a card charge, please call (801) 285-0860 or email "
            "billing@locallytwisted.com so we can match it up for you."
        ),
    }


def _payment_state_for_sales_order(so_name):
    if not frappe.db.exists("Sales Order", so_name):
        return _payment_check_state()

    so = frappe.db.get_value(
        "Sales Order",
        so_name,
        ["name", "grand_total", "currency"],
        as_dict=True,
    )
    paid_payment_request = _paid_payment_request_for_sales_order(so)
    invoice_state = _invoice_state_for_sales_order(so)

    if paid_payment_request and invoice_state.get("state") == "paid":
        return _paid_state()

    if paid_payment_request:
        return {
            "state": "reconciliation_needed",
            "eyebrow": "Payment Received",
            "lede": (
                "Your payment came through. We have your order, and the final receipt "
                "or invoice check is still finishing in the background."
            ),
            "notice": (
                "Tiny snag: the final receipt or invoice details are still being checked. "
                "The team has an internal record to follow up."
            ),
        }

    if invoice_state.get("state") == "paid":
        return _paid_state()

    return {
        "state": "payment_check",
        "eyebrow": "Payment Check",
        "lede": "We need to check this payment before we call the order confirmed.",
        "notice": (
            "If you just paid or saw a card charge, please call (801) 285-0860 or email "
            "billing@locallytwisted.com so we can match it up for you."
        ),
    }


def _paid_state():
    return {
        "state": "paid",
        "eyebrow": "Payment Received",
        "lede": (
            "Your payment came through. We have your order and will send a confirmation "
            "receipt to the email you gave us."
        ),
        "notice": "",
    }


def _paid_payment_request_for_sales_order(so):
    rows = frappe.get_all(
        "Payment Request",
        filters={
            "reference_doctype": "Sales Order",
            "reference_name": so.name,
            "status": "Paid",
        },
        fields=["name", "grand_total", "currency", "outstanding_amount"],
        limit_page_length=20,
    )
    expected_cents = _money_to_cents(so.grand_total)
    expected_currency = (so.currency or "USD").upper()
    for row in rows:
        if (row.get("currency") or "USD").upper() != expected_currency:
            continue
        if _money_to_cents(row.get("grand_total")) != expected_cents:
            continue
        if flt(row.get("outstanding_amount")) > 0.01:
            continue
        return row
    return None


def _invoice_state_for_sales_order(so):
    rows = frappe.get_all(
        "Sales Invoice Item",
        filters={"sales_order": so.name, "docstatus": 1},
        fields=["parent"],
        limit_page_length=20,
    )
    if not rows:
        return {"state": "missing"}

    expected_cents = _money_to_cents(so.grand_total)
    expected_currency = (so.currency or "USD").upper()
    for row in rows:
        invoice = frappe.db.get_value(
            "Sales Invoice",
            row["parent"],
            ["grand_total", "currency", "outstanding_amount", "status"],
            as_dict=True,
        )
        if not invoice:
            continue
        if (invoice.get("currency") or "USD").upper() != expected_currency:
            continue
        if _money_to_cents(invoice.get("grand_total")) != expected_cents:
            continue
        if flt(invoice.get("outstanding_amount")) <= 0.01 or invoice.get("status") == "Paid":
            return {"state": "paid", "invoice": row["parent"]}
    return {"state": "unpaid"}


def _money_to_cents(value):
    return int(round(flt(value) * 100))
