"""Locally Twisted — Take Home shop page.

Custom-themed listing that runs on top of webshop's existing data:
Website Item records for inventory, Item Price for pricing, and webshop's
own /cart endpoint + update_cart RPC for cart actions. We do NOT rebuild
cart logic — webshop owns that. This page is purely the visual shell.

Categorization: webshop ships items in a single "Shop Items" Item Group
right now. Until they're re-tagged into proper groups, the filter chips
bucket items by web_item_name keyword (Bouquet / Cup / Centerpiece / etc.).
That's a v1 shortcut — replace with real Item Groups when re-tagging happens.
"""
import frappe

no_cache = 0
sitemap = 1


def get_context(context):
    items = frappe.db.sql(
        """
        SELECT
            wi.item_code,
            wi.web_item_name,
            wi.route,
            wi.website_image,
            wi.short_description,
            wi.has_variants,
            wi.item_group,
            ip.price_list_rate
        FROM `tabWebsite Item` wi
        LEFT JOIN `tabItem Price` ip
            ON ip.item_code = wi.item_code AND ip.price_list = 'Standard Selling'
        WHERE wi.published = 1
        ORDER BY wi.web_item_name
        """,
        as_dict=True,
    )

    for item in items:
        item["category"] = _categorize(item.get("web_item_name"))
        rate = item.get("price_list_rate")
        item["price_display"] = "${:g}".format(float(rate)) if rate else ""
        # Webshop's product detail route already starts with /shop/<slug>;
        # use as-is when present, otherwise build from item_code.
        if not item.get("route"):
            item["route"] = "shop/{}".format(item["item_code"])

    categories = [
        {"id": "all", "label": "All items"},
        {"id": "bouquets", "label": "Bouquets"},
        {"id": "cups", "label": "Cups & Centerpieces"},
        {"id": "ready-made", "label": "Ready-Made"},
    ]

    context.items = items
    context.categories = categories
    context.total_items = len(items)
    context.title = "Shop"
    context.page_css = PAGE_CSS

    return context


def _categorize(name):
    """Bucket a Website Item into one of the design's 3 customer-facing
    categories by keyword. v1 shortcut — replace when items get re-tagged
    into proper Item Groups."""
    n = (name or "").lower()
    if "bouquet" in n:
        return "bouquets"
    if "cup" in n or "centerpiece" in n:
        return "cups"
    return "ready-made"


PAGE_CSS = """
/* ============================================================
   /shop — Take Home
   ============================================================ */

.lt-shop__hero {
    background-color: var(--lt-near-white);
    padding: 3rem 1rem 2rem;
}
.lt-shop__hero-inner {
    max-width: 1100px;
    margin: 0 auto;
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 1.5rem;
}
.lt-shop__hero-eyebrow {
    font-family: 'Raleway', sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--lt-soft-gray);
    margin: 0 0 0.75rem;
}
.lt-shop__hero-title {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 2.25rem;
    color: var(--lt-near-black);
    margin: 0 0 1rem;
    line-height: 1.1;
    max-width: 22ch;
}
.lt-shop__hero-lede {
    font-family: 'Raleway', sans-serif;
    font-size: 1rem;
    color: var(--lt-soft-gray);
    margin: 0;
    max-width: 50ch;
    line-height: 1.55;
}
.lt-shop__hero-lede a {
    color: var(--lt-near-black);
    font-weight: 600;
    text-decoration: underline;
    text-underline-offset: 0.2em;
}
.lt-shop__cart-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.65rem 1.25rem;
    background: var(--lt-white);
    border: 1px solid rgba(26, 26, 26, 0.18);
    border-radius: 0.375rem;
    color: var(--lt-near-black);
    font-family: 'Raleway', sans-serif;
    font-size: 0.875rem;
    font-weight: 500;
    text-decoration: none;
    flex-shrink: 0;
    transition: border-color 0.15s ease, background-color 0.15s ease;
}
.lt-shop__cart-btn:hover,
.lt-shop__cart-btn:focus-visible {
    color: var(--lt-near-black);
    border-color: var(--lt-near-black);
    text-decoration: none;
    background-color: var(--lt-blush-tint);
}
.lt-shop__cart-btn svg { flex-shrink: 0; }
@media (min-width: 992px) {
    .lt-shop__hero { padding: 4rem 2rem 3rem; }
    .lt-shop__hero-title { font-size: 3rem; }
}

/* Thin accent bands */
.lt-shop__band {
    height: 32px;
    width: 100%;
}
.lt-shop__band--blush { background-color: var(--lt-blush); }

/* Filter + grid */
.lt-shop__listing {
    background: var(--lt-white);
    padding: 2rem 1rem 4rem;
}
.lt-shop__listing-inner {
    max-width: 1100px;
    margin: 0 auto;
}
.lt-shop__filters {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    padding-bottom: 1.25rem;
    margin-bottom: 1.25rem;
    border-bottom: 1px solid rgba(26, 26, 26, 0.08);
}
.lt-shop__chip {
    appearance: none;
    -webkit-appearance: none;
    border: 1px solid rgba(26, 26, 26, 0.18);
    background: var(--lt-white);
    color: var(--lt-near-black);
    font-family: 'Raleway', sans-serif;
    font-size: 0.875rem;
    font-weight: 500;
    padding: 0.5rem 1rem;
    border-radius: 999px;
    cursor: pointer;
    transition: background-color 0.15s ease, border-color 0.15s ease;
    min-height: 36px;
}
.lt-shop__chip:hover,
.lt-shop__chip:focus-visible {
    border-color: var(--lt-near-black);
}
.lt-shop__chip[aria-pressed="true"] {
    border-color: var(--lt-near-black);
    background-color: var(--lt-blush-tint);
}
.lt-shop__count {
    font-family: 'Raleway', sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--lt-soft-gray);
    margin: 0 0 1.5rem;
}

.lt-shop__grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 2rem 1.5rem;
}
@media (min-width: 600px) {
    .lt-shop__grid { grid-template-columns: 1fr 1fr; }
}
@media (min-width: 992px) {
    .lt-shop__grid { grid-template-columns: 1fr 1fr 1fr; }
}

.lt-shop__card {
    display: flex;
    flex-direction: column;
}
.lt-shop__card[hidden] { display: none; }
.lt-shop__card-image {
    position: relative;
    width: 100%;
    aspect-ratio: 3 / 4;
    background-color: var(--lt-blush-tint);
    border-radius: 0.375rem;
    overflow: hidden;
    margin-bottom: 1rem;
    display: block;
}
.lt-shop__card-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}
.lt-shop__card-image--placeholder {
    background-color: var(--lt-blush-tint);
}
.lt-shop__oos-badge {
    position: absolute;
    top: 0.75rem;
    left: 0.75rem;
    background-color: var(--lt-near-black);
    color: var(--lt-white);
    font-family: 'Raleway', sans-serif;
    font-size: 0.6875rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 0.25rem 0.5rem;
    border-radius: 2px;
}
.lt-shop__card-name {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 1.125rem;
    color: var(--lt-near-black);
    margin: 0 0 0.5rem;
    line-height: 1.25;
}
.lt-shop__card-name a {
    color: inherit;
    text-decoration: none;
}
.lt-shop__card-name a:hover,
.lt-shop__card-name a:focus-visible {
    color: var(--lt-near-black);
    text-decoration: underline;
    text-underline-offset: 0.2em;
}
.lt-shop__card-desc {
    font-family: 'Raleway', sans-serif;
    font-size: 0.875rem;
    color: var(--lt-soft-gray);
    line-height: 1.5;
    margin: 0 0 1rem;
}
.lt-shop__card-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
    margin-top: auto;
}
.lt-shop__card-price {
    font-family: 'Raleway', sans-serif;
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--lt-near-black);
}
.lt-shop__card-add {
    background-color: var(--lt-teal);
    color: var(--lt-white);
    border: none;
    border-radius: 0.375rem;
    padding: 0.55rem 1rem;
    font-family: 'Raleway', sans-serif;
    font-size: 0.8125rem;
    font-weight: 600;
    cursor: pointer;
    min-height: 38px;
    transition: background-color 0.15s ease;
}
.lt-shop__card-add:hover,
.lt-shop__card-add:focus-visible {
    background-color: #006666;
}
.lt-shop__card-add[disabled] {
    background-color: rgba(0, 128, 128, 0.3);
    cursor: not-allowed;
}

/* Cross-sell CTA */
.lt-shop__cta {
    background-color: var(--lt-near-white);
    padding: 3rem 1rem;
    border-top: 1px solid rgba(26, 26, 26, 0.06);
}
.lt-shop__cta-inner {
    max-width: 1100px;
    margin: 0 auto;
    max-width: 540px;
}
.lt-shop__cta h2 {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 2rem;
    color: var(--lt-near-black);
    margin: 0 0 1rem;
    line-height: 1.15;
}
.lt-shop__cta-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
}
.lt-shop__cta-btn {
    display: inline-flex;
    align-items: center;
    padding: 0.75rem 1.5rem;
    border-radius: 0.375rem;
    font-family: 'Raleway', sans-serif;
    font-weight: 600;
    font-size: 0.95rem;
    text-decoration: none;
    min-height: 44px;
}
.lt-shop__cta-btn--secondary {
    background-color: var(--lt-white);
    color: var(--lt-near-black);
    border: 1px solid rgba(26, 26, 26, 0.18);
}
.lt-shop__cta-btn--secondary:hover,
.lt-shop__cta-btn--secondary:focus-visible {
    border-color: var(--lt-near-black);
    background-color: var(--lt-blush-tint);
    color: var(--lt-near-black);
    text-decoration: none;
}
.lt-shop__cta-btn--primary {
    background-color: var(--lt-teal);
    color: var(--lt-white);
    border: 1px solid var(--lt-teal);
}
.lt-shop__cta-btn--primary:hover,
.lt-shop__cta-btn--primary:focus-visible {
    background-color: #006666;
    border-color: #006666;
    color: var(--lt-white);
    text-decoration: none;
}

/* Inline feedback for add-to-cart */
.lt-shop__feedback {
    margin-top: 1rem;
    font-size: 0.875rem;
    color: var(--lt-teal);
    min-height: 1.5em;
}
.lt-shop__feedback.is-error { color: #c0392b; }
"""
