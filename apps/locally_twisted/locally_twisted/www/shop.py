"""Locally Twisted — /shop page.

Custom-themed listing that runs on top of webshop's existing data:
Website Item records for inventory, Item Price for pricing, and webshop's
own cart endpoint + update_cart RPC for cart actions. We do NOT rebuild
cart logic — webshop owns that. This page is purely the visual shell.

Updated 2026-04-30: filter pills now source from Item Group children of
"Shop Items" (Arches, Columns, Bouquets, etc.) instead of the old keyword
categorizer. Driven by item.item_group field after the catalog port.
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
            ON ip.item_code = wi.item_code
            AND ip.price_list = 'Standard Selling'
            AND ip.selling = 1
        LEFT JOIN `tabItem` it ON it.item_code = wi.item_code
        WHERE wi.published = 1
          AND (it.variant_of IS NULL OR it.variant_of = '')
        ORDER BY wi.item_group, wi.web_item_name
        """,
        as_dict=True,
    )

    # For variant templates we don't have an Item Price on the template (validate_item_template
    # blocks that). Pull a representative variant price (the lowest) so the card shows a
    # "from $X" baseline.
    for item in items:
        if item.get("has_variants") and not item.get("price_list_rate"):
            min_price = frappe.db.sql(
                """SELECT MIN(ip.price_list_rate)
                   FROM `tabItem` it
                   JOIN `tabItem Price` ip ON ip.item_code = it.item_code
                   WHERE it.variant_of = %s
                     AND ip.price_list = 'Standard Selling'
                     AND ip.selling = 1""",
                (item["item_code"],),
            )
            if min_price and min_price[0] and min_price[0][0]:
                item["price_list_rate"] = min_price[0][0]
                item["price_is_from"] = True

        # Slug for filter pill data attribute (Item Group "Get-Well Bouquets" → "get-well-bouquets")
        item["category_slug"] = frappe.scrub(item.get("item_group") or "all").replace("_", "-")
        rate = item.get("price_list_rate")
        if rate:
            item["price_display"] = (
                "from ${:g}".format(float(rate)) if item.get("price_is_from")
                else "${:g}".format(float(rate))
            )
        else:
            item["price_display"] = ""
        if not item.get("route"):
            item["route"] = "shop-items/{}/{}".format(
                frappe.scrub(item.get("item_group") or "shop-items").replace("_", "-"),
                item["item_code"],
            )

    # Sourced live from Item Group children of "Shop Items" — order by weightage.
    children = frappe.db.get_all(
        "Item Group",
        filters={"parent_item_group": "Shop Items", "show_in_website": 1},
        fields=["name", "item_group_name", "weightage"],
        order_by="weightage asc, item_group_name asc",
    )
    categories = [{"id": "all", "label": "All items"}]
    for c in children:
        categories.append({
            "id": frappe.scrub(c["name"]).replace("_", "-"),
            "label": c["item_group_name"] or c["name"],
        })

    context.items = items
    context.categories = categories
    context.total_items = len(items)
    context.title = "Ready-to-Order Balloon Decor"
    context.page_css = PAGE_CSS

    return context


PAGE_CSS = """
/* ============================================================
   /shop — Take Home
   ============================================================ */

.lt-shop__hero {
    background:
        linear-gradient(135deg, rgba(250, 247, 242, 0.98) 0%, rgba(250, 247, 242, 0.92) 48%, rgba(217, 199, 179, 0.42) 100%);
    border-bottom: 1px solid rgba(14, 34, 64, 0.16);
    padding: 3rem 1rem 2.4rem;
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
    font-family: var(--lt-font-body);
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--lt-crimson);
    margin: 0 0 0.75rem;
}
.lt-shop__hero-title {
    font-family: var(--lt-font-heading);
    font-size: 2.45rem;
    font-weight: 700;
    color: var(--lt-ink);
    margin: 0 0 1rem;
    line-height: 1.1;
    max-width: 22ch;
}
.lt-shop__hero-lede {
    font-family: var(--lt-font-body);
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
    font-family: var(--lt-font-body);
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
    background-color: var(--lt-warm-tint);
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
.lt-shop__band--sandstone { background-color: var(--lt-sandstone); height: 18px; }

/* Filter + grid */
.lt-shop__listing {
    background: var(--lt-warm-white);
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
    border-bottom: 1px solid rgba(14, 34, 64, 0.14);
}
.lt-shop__chip {
    appearance: none;
    -webkit-appearance: none;
    border: 1px solid rgba(26, 26, 26, 0.18);
    background: var(--lt-white);
    color: var(--lt-near-black);
    font-family: var(--lt-font-body);
    font-size: 0.875rem;
    font-weight: 500;
    padding: 0.5rem 1rem;
    border-radius: 0;
    cursor: pointer;
    transition: background-color 0.15s ease, border-color 0.15s ease;
    min-height: 36px;
}
.lt-shop__chip:hover,
.lt-shop__chip:focus-visible {
    border-color: var(--lt-near-black);
}
.lt-shop__chip[aria-pressed="true"] {
    border-color: var(--lt-navy);
    background-color: var(--lt-navy);
    color: var(--lt-white);
}
.lt-shop__count {
    font-family: var(--lt-font-body);
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
    background-color: rgba(217, 199, 179, 0.34);
    border-radius: 4px;
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
    background-color: rgba(217, 199, 179, 0.34);
}
.lt-shop__oos-badge {
    position: absolute;
    top: 0.75rem;
    left: 0.75rem;
    background-color: var(--lt-near-black);
    color: var(--lt-white);
    font-family: var(--lt-font-body);
    font-size: 0.6875rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 0.25rem 0.5rem;
    border-radius: 2px;
}
.lt-shop__card-name {
    font-family: var(--lt-font-heading);
    font-weight: 700;
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
    font-family: var(--lt-font-body);
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
    font-family: var(--lt-font-body);
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--lt-near-black);
}
.lt-shop__card-add {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background-color: var(--lt-navy);
    color: var(--lt-white);
    border: none;
    border-radius: 3px;
    padding: 0.55rem 1rem;
    font-family: var(--lt-font-body);
    font-size: 0.8125rem;
    font-weight: 600;
    cursor: pointer;
    min-height: 38px;
    transition: background-color 0.15s ease;
    text-decoration: none;
    text-align: center;
}
.lt-shop__card-add:hover,
.lt-shop__card-add:focus-visible {
    background-color: var(--lt-ink);
    color: var(--lt-white);
    text-decoration: none;
}
.lt-shop__card-add[disabled] {
    background-color: rgba(14, 34, 64, 0.28);
    cursor: not-allowed;
}

/* Cross-sell CTA */
.lt-shop__cta {
    background-color: var(--lt-navy);
    padding: 3rem 1rem;
    border-top: 1px solid rgba(26, 26, 26, 0.06);
}
.lt-shop__cta-inner {
    max-width: 1100px;
    margin: 0 auto;
    max-width: 540px;
}
.lt-shop__cta h2 {
    font-family: var(--lt-font-heading);
    font-weight: 700;
    font-size: 2rem;
    color: var(--lt-white);
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
    font-family: var(--lt-font-body);
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
    background-color: var(--lt-warm-tint);
    color: var(--lt-near-black);
    text-decoration: none;
}
.lt-shop__cta-btn--primary {
    background-color: var(--lt-crimson);
    color: var(--lt-white);
    border: 1px solid var(--lt-crimson);
}
.lt-shop__cta-btn--primary:hover,
.lt-shop__cta-btn--primary:focus-visible {
    background-color: var(--lt-ink);
    border-color: var(--lt-ink);
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

/* v4.2 product polish: keep /shop premium even before the global CSS include
   is wired by the parent integration pass. */
.lt-shop--landing {
    background: var(--lt-warm-white);
    color: var(--lt-soft-gray);
    font-family: var(--lt-font-body);
}
.lt-shop--landing .lt-shop__hero {
    background: var(--lt-navy);
    border-bottom: 4px solid var(--lt-brass);
    color: var(--lt-white);
    padding: 0;
}
.lt-shop--landing .lt-shop__hero-inner {
    padding: clamp(2.25rem, 6vw, 4.5rem) clamp(1rem, 4vw, 2rem);
}
.lt-shop--landing .lt-shop__hero-eyebrow,
.lt-shop--landing .lt-shop__count {
    color: var(--lt-brass);
    font-weight: 900;
    letter-spacing: 0.1em;
}
.lt-shop--landing .lt-shop__hero-title {
    color: var(--lt-white);
    font-size: clamp(2.35rem, 7vw, 4.4rem);
    line-height: 1.04;
    max-width: 12ch;
}
.lt-shop--landing .lt-shop__hero-lede {
    color: rgba(250, 247, 242, 0.86);
    max-width: 56ch;
}
.lt-shop--landing .lt-shop__band--sandstone {
    background: var(--lt-brass);
    height: 4px;
}
.lt-shop--landing .lt-shop__listing {
    background: var(--lt-warm-white);
}
.lt-shop--landing .lt-shop__listing-inner,
.lt-shop--landing .lt-shop__hero-inner,
.lt-shop--landing .lt-shop__cta-inner {
    width: min(100%, 1200px);
    max-width: none;
    margin-inline: auto;
}
.lt-shop--landing .lt-shop__card {
    min-width: 0;
    overflow: hidden;
    background: var(--lt-white);
    border: 1px solid rgba(14, 34, 64, 0.12);
    border-radius: 4px;
    box-shadow: none;
    padding: 1rem;
}
.lt-shop--landing .lt-shop__card-name,
.lt-shop--landing .lt-shop__card-name a {
    color: var(--lt-ink);
    font-family: var(--lt-font-heading);
    overflow-wrap: anywhere;
}
.lt-shop--landing .lt-shop__card-desc {
    color: var(--lt-soft-gray);
    overflow-wrap: anywhere;
}
.lt-shop--landing .lt-shop__card-price {
    color: var(--lt-navy);
    font-weight: 900;
}
.lt-shop--landing .lt-shop__chip,
.lt-shop--landing .lt-shop__card-add,
.lt-shop--landing .lt-shop__cta-btn {
    border-radius: 3px;
    min-height: 44px;
    font-weight: 900;
}
.lt-shop--landing .lt-shop__chip[aria-pressed="true"],
.lt-shop--landing .lt-shop__card-add,
.lt-shop--landing .lt-shop__cta-btn--primary {
    background: var(--lt-navy);
    border-color: var(--lt-navy);
    color: var(--lt-white);
}
.lt-shop--landing .lt-shop__card-add:hover,
.lt-shop--landing .lt-shop__card-add:focus-visible,
.lt-shop--landing .lt-shop__cta-btn--primary:hover,
.lt-shop--landing .lt-shop__cta-btn--primary:focus-visible {
    background: var(--lt-crimson);
    border-color: var(--lt-crimson);
    color: var(--lt-white);
}
.lt-shop--landing .lt-shop__cta {
    background: var(--lt-navy);
    border-top: 4px solid var(--lt-brass);
}
.lt-shop--landing .lt-shop__cta h2 {
    max-width: 16ch;
    color: var(--lt-white);
    font-size: clamp(2rem, 5vw, 3.2rem);
}
.lt-shop--landing .lt-shop__cta-btn--secondary {
    background: transparent;
    border-color: rgba(250, 247, 242, 0.5);
    color: var(--lt-white);
}
"""
