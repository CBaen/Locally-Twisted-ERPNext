"""LT guest cart page — /cart.

This OVERRIDES webshop's bundled /cart route via the website_route_rule
registered in hooks.py. Webshop's /cart requires login; ours doesn't.

The cart itself lives in localStorage on the client. Server renders the
shell (empty + populated containers, hidden by default), and a vanilla
JS bundle on the page reads localStorage on load, calls
locally_twisted.api.cart.get_cart_items to fetch display details, and
renders. Quantity edits and removals stay client-side until the
customer hits Continue to Checkout.

No server-side cart state is created by visiting this page.
"""
import frappe
from frappe import _

no_cache = 1
sitemap = 0  # don't index the cart


def get_context(context):
    context.title = "Your cart | Locally Twisted"
    context.metatags = {
        "description": "Review your selections and continue to secure checkout.",
        "robots": "noindex, nofollow",
    }
    context.colocated_css = PAGE_CSS
    return context


PAGE_CSS = """
.lt-cart {
    background-color: var(--lt-near-white);
    padding: 3rem 1rem 4rem;
    min-height: 60vh;
}
.lt-cart__container {
    max-width: 980px;
    margin: 0 auto;
}
.lt-cart__title {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 2rem;
    color: var(--lt-near-black);
    margin: 0 0 0.5rem;
    line-height: 1.15;
}
.lt-cart__subtitle {
    color: var(--lt-soft-gray);
    margin: 0 0 2rem;
    font-size: 1rem;
    line-height: 1.5;
}
@media (min-width: 900px) {
    .lt-cart__title { font-size: 2.5rem; }
}

/* States — only one is visible at a time */
.lt-cart__state[hidden] { display: none; }

/* Empty state */
.lt-cart__empty {
    background-color: var(--lt-white);
    border: 1px solid rgba(26, 26, 26, 0.08);
    border-radius: 0.5rem;
    padding: 3rem 2rem;
    text-align: center;
}
.lt-cart__empty-icon {
    margin: 0 auto 1.25rem;
    width: 56px;
    height: 56px;
    color: var(--lt-soft-gray);
}
.lt-cart__empty h2 {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 1.5rem;
    color: var(--lt-near-black);
    margin: 0 0 0.5rem;
}
.lt-cart__empty p {
    color: var(--lt-soft-gray);
    margin: 0 0 1.5rem;
    line-height: 1.5;
}
.lt-cart__empty-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    justify-content: center;
}

/* Loading state */
.lt-cart__loading {
    text-align: center;
    color: var(--lt-soft-gray);
    padding: 3rem 1rem;
    font-size: 1rem;
}

/* Error state */
.lt-cart__error {
    background-color: #fdecec;
    border: 1px solid #c0392b;
    border-radius: 0.5rem;
    padding: 1.5rem;
    color: #842424;
    line-height: 1.5;
}
.lt-cart__error strong { display: block; margin-bottom: 0.25rem; }

/* Populated cart */
.lt-cart__layout {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.5rem;
}
@media (min-width: 900px) {
    .lt-cart__layout { grid-template-columns: minmax(0, 1fr) 320px; gap: 2.5rem; }
}

.lt-cart__lines {
    background-color: var(--lt-white);
    border: 1px solid rgba(26, 26, 26, 0.08);
    border-radius: 0.5rem;
    overflow: hidden;
}
.lt-cart__line {
    display: grid;
    grid-template-columns: 80px 1fr auto;
    gap: 1rem;
    padding: 1.25rem;
    border-bottom: 1px solid rgba(26, 26, 26, 0.06);
    align-items: center;
}
.lt-cart__line:last-child { border-bottom: none; }
@media (min-width: 600px) {
    .lt-cart__line { grid-template-columns: 96px 1fr auto auto; }
}
.lt-cart__line-img {
    width: 80px;
    height: 80px;
    border-radius: 0.375rem;
    background-color: var(--lt-blush-tint);
    background-size: cover;
    background-position: center;
    flex-shrink: 0;
    display: block;
}
@media (min-width: 600px) {
    .lt-cart__line-img { width: 96px; height: 96px; }
}
.lt-cart__line-body { min-width: 0; }
.lt-cart__line-name {
    font-family: 'Raleway', sans-serif;
    font-weight: 600;
    color: var(--lt-near-black);
    margin: 0 0 0.25rem;
    font-size: 1rem;
    line-height: 1.3;
    word-break: break-word;
}
.lt-cart__line-name a { color: inherit; text-decoration: none; }
.lt-cart__line-name a:hover { text-decoration: underline; text-underline-offset: 0.2em; }
.lt-cart__line-meta { font-size: 0.85rem; color: var(--lt-soft-gray); margin: 0; }
.lt-cart__line-remove {
    display: inline-flex;
    align-items: center;
    background: none;
    border: none;
    color: var(--lt-soft-gray);
    font-family: 'Raleway', sans-serif;
    font-size: 0.8rem;
    padding: 0.25rem 0;
    margin-top: 0.5rem;
    cursor: pointer;
    text-decoration: underline;
    text-underline-offset: 0.15em;
}
.lt-cart__line-remove:hover, .lt-cart__line-remove:focus-visible {
    color: #842424;
}
.lt-cart__qty {
    display: inline-flex;
    align-items: center;
    border: 1px solid rgba(26, 26, 26, 0.18);
    border-radius: 0.375rem;
    overflow: hidden;
    height: 40px;
}
.lt-cart__qty-btn {
    background: var(--lt-white);
    border: none;
    color: var(--lt-near-black);
    font-size: 1.1rem;
    width: 36px;
    height: 100%;
    cursor: pointer;
    line-height: 1;
}
.lt-cart__qty-btn:hover, .lt-cart__qty-btn:focus-visible {
    background-color: var(--lt-blush-tint);
}
.lt-cart__qty-btn[disabled] {
    color: rgba(26, 26, 26, 0.3);
    cursor: not-allowed;
}
.lt-cart__qty-input {
    width: 44px;
    height: 100%;
    border: none;
    border-left: 1px solid rgba(26, 26, 26, 0.12);
    border-right: 1px solid rgba(26, 26, 26, 0.12);
    text-align: center;
    font-family: 'Raleway', sans-serif;
    font-size: 0.95rem;
    color: var(--lt-near-black);
    background: var(--lt-white);
    /* hide spin buttons on number input */
    -moz-appearance: textfield;
}
.lt-cart__qty-input::-webkit-inner-spin-button,
.lt-cart__qty-input::-webkit-outer-spin-button {
    -webkit-appearance: none;
    margin: 0;
}
.lt-cart__line-amount {
    font-family: 'Raleway', sans-serif;
    font-weight: 600;
    color: var(--lt-near-black);
    font-size: 1rem;
    margin: 0;
    text-align: right;
    grid-column: 2 / -1;
}
@media (min-width: 600px) {
    .lt-cart__line-amount { grid-column: auto; }
}

/* Summary card */
.lt-cart__summary {
    background-color: var(--lt-white);
    border: 1px solid rgba(26, 26, 26, 0.08);
    border-radius: 0.5rem;
    padding: 1.5rem;
    height: max-content;
}
@media (min-width: 900px) {
    .lt-cart__summary { position: sticky; top: 1rem; }
}
.lt-cart__summary h2 {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 1.25rem;
    color: var(--lt-near-black);
    margin: 0 0 1rem;
    line-height: 1.2;
}
.lt-cart__summary-row {
    display: flex;
    justify-content: space-between;
    font-size: 0.9rem;
    color: var(--lt-near-black);
    padding: 0.4rem 0;
}
.lt-cart__summary-row--grand {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 1.25rem;
    border-top: 1px solid rgba(26, 26, 26, 0.12);
    margin-top: 0.5rem;
    padding-top: 0.75rem;
}
.lt-cart__summary-note {
    margin: 1rem 0 0;
    font-size: 0.8rem;
    color: var(--lt-soft-gray);
    line-height: 1.45;
}
.lt-cart__checkout {
    background-color: var(--lt-teal);
    color: var(--lt-white);
    border: none;
    border-radius: 0.375rem;
    padding: 0.875rem 2rem;
    font-family: 'Raleway', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    width: 100%;
    margin-top: 1.25rem;
    text-decoration: none;
    display: inline-flex;
    justify-content: center;
    align-items: center;
    min-height: 48px;
}
.lt-cart__checkout:hover, .lt-cart__checkout:focus-visible {
    background-color: #006666;
    color: var(--lt-white);
    text-decoration: none;
}

.lt-cart__continue {
    display: inline-flex;
    align-items: center;
    padding: 0.7rem 1.4rem;
    background: var(--lt-white);
    color: var(--lt-near-black);
    border: 1px solid rgba(26, 26, 26, 0.18);
    border-radius: 0.375rem;
    font-family: 'Raleway', sans-serif;
    font-weight: 500;
    font-size: 0.9rem;
    text-decoration: none;
    margin-top: 1rem;
}
.lt-cart__continue:hover, .lt-cart__continue:focus-visible {
    border-color: var(--lt-near-black);
    background-color: var(--lt-blush-tint);
    color: var(--lt-near-black);
    text-decoration: none;
}

/* Removed/missing notice */
.lt-cart__notice {
    background-color: var(--lt-blush-tint);
    border-radius: 0.375rem;
    padding: 0.75rem 1rem;
    margin-bottom: 1rem;
    font-size: 0.875rem;
    color: var(--lt-near-black);
    line-height: 1.5;
}
"""
