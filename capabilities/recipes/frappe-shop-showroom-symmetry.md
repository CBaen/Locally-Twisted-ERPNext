---
id: frappe-shop-showroom-symmetry
name: Frappe Shop Showroom Symmetry
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted ERPNext/Frappe shop, category, and product showcase layouts
currently_true: yes
verification_level: 2
last_verified: 2026-05-06
evidence_quality: direct
successful_uses: 2
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
  - shop
  - product cards
  - symmetry
  - responsive layout
---

# Frappe Shop Showroom Symmetry

Use this recipe when changing `/shop`, `/shop-items`, `/shop-items/<group>`,
product listing cards, category controls, or product showcase grids.

## Rule

Shop pages are product-showcase pages, not cramped admin grids. They need large
photos, room to breathe, and symmetrical rows at each breakpoint.

If a row cannot be symmetrical across, split it into balanced rows instead of
leaving a lone orphan card or a ragged chip row.

## Current LT Contract

- `/shop` is the all-decor showroom hub.
- `/shop-items` aliases to the `/shop` showroom contract.
- `/shop` uses a shared category-navigation component, not a chip/filter wall.
- `/shop-items/<group>` uses the same shared category navigation plus a
  photo-first product grid. It must not fall back to a Frappe/Webshop
  sidebar-card feeling.
- Category navigation is a slim desktop left rail and a native mobile select.
  It includes `All Ready-to-Order` plus the 8 active customer-facing
  `Shop Items` primary children.
- Do not restore text-width chips, a top 12-button tile wall, or in-place
  category filtering on `/shop` unless GL explicitly reverses this decision.
- `/shop` product grids and category product grids must not leave one desktop
  orphan card where the rendered count makes a balanced row possible. If a
  3-up grid would end with one card and the count is even, switch that visible
  grid to 2-up rows.
- Homepage product merchandising rows must follow the same showroom symmetry
  principle. Four curated products should be 4-across on desktop and 2x2 on
  mobile unless GL explicitly accepts cramped phone cards.
- Product-card price labels must stay in parity with the product page/source.
  Do not show a `From` price for a quote-first product unless that price is
  also source-backed and product-page clear.

## Implementation Pattern

1. Preserve Frappe/Webshop route ownership, template hooks, product selectors,
   filters, cart selectors, and event hooks.
2. Load shared shop showroom CSS through `web_include_css` and bump the cache
   query string after edits.
3. Use the shared `shop_category_nav.html` include for the shop category
   rail/select. Avoid text-width flex chips and top button walls for category
   navigation.
4. Give product cards stable image aspect ratios and enough width for the photo
   to sell the product.
5. Use a small route-local script only where rendered item counts are needed for
   balancing. Keep it scoped to the listing container and re-run after Webshop
   product-list updates.
6. Clear the Frappe website cache after Jinja, CSS, hook, or route edits.
7. Verify the exact affected routes at mobile and desktop widths before calling
   the visual repair ready for GL review.

## Verification

Run the focused showroom checks first:

```powershell
python scripts/verify/smoke_shop.py
npm run test:layout-fit -- --grep shop
npm run test:layout-fit -- --grep "variant-product|single-product|seasonal-category"
npm run test:interactive-layout -- --grep "/shop category navigation"
```

When the change touches shared public CSS or route containment, also run the
broader gate from `responsive-container-audit.md`.

## Receipt

On 2026-05-06, GL rejected the first shop showroom pass because the category
controls and product rows were technically functional but visually cheap and
asymmetric. The repair added the neutral `All Ready-to-Order` category tile to
make a 12-tile control grid, converted category controls to equal-width and
equal-height grid tracks, and added product-grid balancing so both `/shop`
filtered Arches and `/shop-items/arches` render five paired 2-card desktop rows
instead of ending with one orphan card.

Later on 2026-05-06, GL rejected the category button/tile treatment itself and
approved Option B: desktop category list plus mobile dropdown. The current
contract replaces both the `/shop` chip wall and the `/shop-items/<group>` top
tile wall with `shop_category_nav.html`, a slim desktop rail and native mobile
select. `/shop` category choices now navigate to category pages instead of
filtering in place.

Verified on the running local Frappe site with `python scripts/verify/smoke_shop.py`,
`npm run test:layout-fit -- --grep shop`, `npm run test:layout-fit -- --grep
"variant-product|single-product|seasonal-category"`, and `npm run
test:interactive-layout -- --grep "/shop category navigation"`. Browser checks
also verified no `.lt-shop__chip` controls on `/shop`, no old
`.lt-shop__toolbar--categories` button wall on category pages, one 12-link
desktop category rail, one 12-option mobile category select, and paired Arches
product rows; transient screenshot folders were not kept as source.

On 2026-06-24, the planned homepage Customer Favorites row added a related
symmetry rule: 4 curated product cards across on desktop and 2x2 on mobile,
with `From` prices only when the product-page/source truth supports them.
GL replaced Classic Arch with Minion Bouquet so the current planned row uses
four products with visible live starting prices. Planning handoff:
`workstreams/homepage-july-favorites-nav-plan-2026-06-24.md`.
