---
id: frappe-product-clear-control-contract
name: Frappe Product Clear Control Contract
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted ERPNext/Frappe product detail option controls and product-page containers
currently_true: yes
verification_level: 2
last_verified: 2026-05-07
evidence_quality: direct
successful_uses: 1
failed_uses: 0
regressions: 0
depends_on:
  - frappe-public-container-contract
  - responsive-container-audit
tags:
  - Locally Twisted
  - Frappe
  - ERPNext
  - Webshop
  - product detail
  - option controls
  - containers
  - visual contract
---

# Frappe Product Clear Control Contract

Use this recipe before changing product detail CSS, product option selectors,
variant chips, dropdown/select styling, product price/add-to-cart grouping, or
the product detail layout shell.

## Rule

Product detail pages must not be ruled by nested containers. Product options
such as size, latex color, add-on numbers, and variant selectors are controls,
not cards.

The only framed product-detail notice currently approved is the pickup/delivery
fulfillment panel.

## Current LT Contract

- The major product stage/wrapper may provide page structure.
- The product photo area may have a deliberate visual frame.
- The pickup/delivery panel may keep its warm background, border, and contained
  notice treatment.
- Product option groups must be clear: no panel background, border, radius, or
  box shadow.
- Variant chips must not look like pill cards. Use clear text controls with
  selected text emphasis, not boxed buttons.
- Select/dropdown controls must not render as white bordered selection boxes.
  Keep them transparent and inline with the product copy.
- The price/add-to-cart group must not sit inside a boxed panel. Buttons may
  remain real buttons because they are commands, not containers.
- `What's Included` may use a section divider, but it must not become a box.
- Do not reintroduce these boxed product-control selectors through
  `lt-theme.css`, `lt-product-polish.css`, or future route CSS:
  `.lt-product__configure`, `.lt-product__cart`, `.lt-product__attr`,
  `.lt-product__chip-label`, `.lt-product__select`.

## Implementation Pattern

1. Keep Frappe/Webshop product behavior intact: variant data, selected variant
   resolution, price updates, media swap, cart handoff, and checkout still own
   the functional path.
2. Remove visual box styling from the option layer. For product options and the
   price group, set background transparent, border 0, radius 0, and shadow none.
3. Use typography, spacing, selected text emphasis, and focus outlines for
   clarity instead of nested panels.
4. Leave `.lt-product__fulfillment` framed unless GL changes that specific
   exception.
5. Bump CSS cache keys in `hooks.py` after product CSS edits, then clear website
   cache and restart the backend.

## Verification

Run:

```powershell
python scripts/dev/clear_website_cache.py --restart
python scripts/verify/smoke_shop.py
npm run test:layout-fit -- --grep "variant-product|single-product|seasonal-category"
```

`smoke_shop.py` includes the product clear-control guard. It fails if the
product configure form, option controls, variant chips, select controls, or
price/add-to-cart group render with boxed background, borders, or shadows. It
also confirms the pickup/delivery panel remains the allowed framed exception.

Capture desktop and mobile screenshots for the exact product path GL flagged,
not a proxy product.

## Receipt

On 2026-05-07, GL rejected the remaining product-page option boxes after the
recommendation-panel cleanup. The red smoke run failed on the live Unicorn
Bouquet route because `.lt-product__configure` still had a 1px border, 4px
radius, and box shadow from the theme layer. The repair cleared product option,
chip, select, and price/add-to-cart boxes in both `lt-theme.css` and
`lt-product-polish.css`, while leaving pickup/delivery framed.

Verification passed with `python scripts/dev/clear_website_cache.py --restart`
and `python scripts/verify/smoke_shop.py`. Fresh screenshots were captured at
`output/playwright/product-page-clear-options-unicorn-1366.png` and
`output/playwright/product-page-clear-options-unicorn-390.png`; computed styles
showed 0 borders, transparent backgrounds, and no shadows for product controls,
with pickup/delivery still framed.
