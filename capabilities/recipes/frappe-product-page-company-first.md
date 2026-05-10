---
id: frappe-product-page-company-first
name: Frappe Product Page Company First
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted ERPNext/Frappe Webshop product detail pages
currently_true: yes
verification_level: 2
last_verified: 2026-05-07
evidence_quality: direct
successful_uses: 1
failed_uses: 0
regressions: 0
depends_on:
  - frappe-public-container-contract
  - frappe-product-clear-control-contract
  - frappe-shop-showroom-symmetry
  - responsive-container-audit
tags:
  - Locally Twisted
  - Frappe
  - ERPNext
  - Webshop
  - product detail
  - recommendations
  - company first
---

# Frappe Product Page Company First

Use this recipe before changing Webshop product detail templates, product-page
CSS, product recommendations, reviews, additional-info panels, product photo
layout, or option selectors.

## Rule

Ready-to-order ecommerce supports Locally Twisted. It is not the main product.
Product detail pages should help a customer understand the item, choose valid
options, and check out or contact LT. They should not behave like a generic
retail recommendation engine.

## Current LT Contract

- Product detail pages use the Webshop item override under
  `templates/generators/item/`.
- Keep the primary product content: breadcrumbs, photo, product name, price,
  option selector, stock/fulfillment notes, useful product copy, and add-to-cart
  or contact path.
- Do not render Webshop's lower Additional Info, Reviews, or Recommended Items
  panel unless GL explicitly reopens that product-page decision.
- Do not restore `.lt-product__more`, `.lt-product__info-panel`,
  `.lt-product__info-content`, `.lt-product__recommendations`,
  `.recommended-item-section`, or `.recommendation-container` as visible product
  detail surfaces.
- Avoid visible boxes that exist only because the ecommerce template had a
  section. A framed/cart-like surface is acceptable only when it carries actual
  customer work, such as selecting options or reviewing checkout facts.
- Same-day correction: product options and the price/add-to-cart group are not
  approved framed surfaces. Use `frappe-product-clear-control-contract`; the
  pickup/delivery panel is the current approved product-detail frame.
- Product recommendations, upsells, cross-sells, generic reviews tabs, and
  empty specification panels are out of scope for launch. The company, proof
  photos, service authority, and contact path carry the brand.

## Implementation Pattern

1. Preserve Frappe/Webshop route ownership and native hooks that are needed for
   item rendering, variants, price, stock, cart, and checkout.
2. Keep useful product content in the main image/detail area. If content is
   empty or generic, remove the surface instead of styling an empty panel.
3. Keep product photos large enough to sell the item. Do not shrink the page
   into a CAD/spec-card feeling.
4. Keep option controls plain, large enough to tap, and tied to Webshop's valid
   variant data.
5. After Jinja, CSS, or hook edits, clear the website cache. If `hooks.py`
   changes, restart the backend through `python scripts/dev/clear_website_cache.py
   --restart`.

## Verification

Run focused product checks first:

```powershell
python scripts/verify/smoke_shop.py
npm run test:layout-fit -- --grep "variant-product|single-product|seasonal-category"
```

If shared public CSS changed, also run the responsive container gate from
`responsive-container-audit.md`.

Before claiming visual readiness, capture desktop and mobile screenshots of at
least one variant product and one single-SKU product.

## Receipt

On 2026-05-07, GL flagged the product detail page as boxed-in and ecommerce-led,
with a random white container under product content. The root cause was the
Webshop Additional Info/Reviews/Recommendations block in
`templates/generators/item/item.html`, plus LT CSS that made its empty wrapper
visible. The fix removed that lower ecommerce block, deleted the matching CSS
selectors from the product/showroom layers, softened the primary product detail
shell, and added `smoke_shop.py` coverage that fails if the auxiliary panel or
recommendation selectors return.

Verification passed with `python scripts/dev/clear_website_cache.py --restart`,
`python scripts/verify/smoke_shop.py`, and `npm run test:layout-fit -- --grep
"variant-product|single-product|seasonal-category"` (39/39). Screenshots for
the flagged Unicorn Bouquet path were saved under `output/playwright/` with
`product-page-company-first-unicorn-*`.
