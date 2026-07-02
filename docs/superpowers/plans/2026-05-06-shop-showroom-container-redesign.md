# Shop Showroom Container Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn `/shop`, `/shop-items`, `/shop-items/<group>`, and product detail pages into wide, mobile-responsive product-showcase surfaces with large contained images and no smashed Webshop cards.

**Architecture:** Keep Frappe and Webshop route lifecycle, product data, variant selection, and guest cart behavior intact. Change the visible presentation by widening LT-owned wrappers, replacing category sidebars with top controls, overriding Webshop card layout safely, and adding verifier coverage for card width, image containment, and route behavior.

**Tech Stack:** ERPNext v15.105.0, Frappe v15, Webshop, Jinja route/templates, LT app CSS/JS, Playwright Test, Python smoke verifiers.

---

## File Map

- `apps/locally_twisted/locally_twisted/templates/generators/item_group.html`: category listing markup. Remove the desktop sidebar visual pattern and move categories/filters/sort into top controls while preserving `item-group-content`, `#product-listing`, Webshop filter macros, and `/all-products/index.js`.
- `apps/locally_twisted/locally_twisted/www/shop.html`: broad `/shop` showroom markup. Keep LT-owned cards and cart hooks; update structure only if needed for large-card layout.
- `apps/locally_twisted/locally_twisted/www/shop.py`: `/shop` data and route context. Add any category route data needed by top controls; do not change catalog/query semantics unless route evidence requires it.
- `apps/locally_twisted/locally_twisted/templates/generators/item/item.html`: product detail shell. Keep Webshop generator lifecycle and selectors; allow larger showroom image/detail layout.
- `apps/locally_twisted/locally_twisted/templates/generators/item/item_details.html`: product detail text, price, action, and option include area. Preserve variant and add-to-cart hooks.
- `apps/locally_twisted/locally_twisted/templates/generators/item/item_configure.html`: variant selector. Only change layout wrappers if needed; do not rewrite variant lookup behavior.
- `apps/locally_twisted/locally_twisted/public/css/lt-product-polish.css`: primary showroom CSS for `/shop`, category pages, and product detail.
- `apps/locally_twisted/locally_twisted/hooks.py`: CSS cache-bust only if CSS changes.
- `scripts/verify/layout_helpers.js`: shared route/viewport helper. Add shop-specific selectors only if needed.
- `scripts/verify/layout_fit.spec.js`: passive layout gate. Add/adjust shop showroom assertions if helper-only checks are insufficient.
- `scripts/verify/interactive_layout.spec.js`: stateful shop/product checks if filter controls or product options need explicit state verification.
- `scripts/verify/smoke_shop.py`: behavioral/visual contract for shop routes, category pages, product cards, variant selection, and single-SKU cart behavior.
- `workstreams/shop.md` and `workstreams/website-launch.md`: update only after implementation and verification, recording the new showroom route contract.

## Task 1: Add Failing Showroom Contract Checks

**Files:**
- Modify: `scripts/verify/smoke_shop.py`
- Optionally modify: `scripts/verify/layout_helpers.js`

- [ ] Add checks that fail on the current state:
  - `/shop` desktop first product cards must be at least `340px` wide.
  - `/shop` desktop product-card images must be at least `300px` wide.
  - `/shop` mobile cards must not use the current 96px thumbnail/list treatment.
  - `/shop-items/arches` must not expose a desktop sidebar layout.
  - `/shop-items/arches` desktop rendered cards must be at least `340px` wide.
  - `/shop-items/arches` product images must be contained, not cropped.
  - `/shop-items` must not expose a cramped default listing surface.

- [ ] Run the focused smoke verifier and confirm it fails for the expected layout reason:

```bash
python scripts/verify/smoke_shop.py
```

Expected: fail on shop/category showroom width or category sidebar/card collapse assertions, while existing route/cart assertions still run.

## Task 2: Redesign Category Listing Layout

**Files:**
- Modify: `apps/locally_twisted/locally_twisted/templates/generators/item_group.html`
- Modify: `apps/locally_twisted/locally_twisted/public/css/lt-product-polish.css`

- [ ] Replace the visible desktop sidebar with top controls:
  - category intro remains at the top.
  - category navigation appears above the grid as horizontal chips/links.
  - field/attribute filters remain available above the grid or in the existing mobile panel pattern.
  - keep `item-group-content`, `#product-listing`, `field_filter_section`, `attribute_filter_section`, `lt-sort-select`, mobile filter IDs, and `/all-products/index.js`.

- [ ] Override Webshop native card layout without deleting required classes:
  - neutralize `.col-sm-4.item-card` width/flex assumptions inside `.lt-shop--category`.
  - make `#product-listing.lt-shop__grid` a wide CSS grid with `repeat(auto-fit, minmax(min(100%, 360px), 1fr))` or equivalent.
  - keep maximum density to 3 columns on wide desktop.
  - use `min-width: 0` on wrappers/cards.
  - make images use a large fixed frame and contained imagery.

- [ ] Bump the `lt-product-polish.css` query string in `hooks.py` after CSS changes.

## Task 3: Redesign `/shop` Broad Showroom Cards

**Files:**
- Modify: `apps/locally_twisted/locally_twisted/www/shop.html`
- Modify: `apps/locally_twisted/locally_twisted/www/shop.py`
- Modify: `apps/locally_twisted/locally_twisted/public/css/lt-product-polish.css`

- [ ] Keep `/shop` as the broad ready-to-order showroom hub.
- [ ] Increase desktop wrapper scale to the approved wide showroom range.
- [ ] Make cards photo-first:
  - mobile: one full-width card, no 96px image thumbnail layout.
  - tablet: two columns.
  - desktop: two to three columns.
  - wide desktop: three columns.
  - images are large fixed frames using contained imagery.
- [ ] Preserve current `LT_CART` add-to-cart hooks and variant-template `Choose options` links.

## Task 4: Normalize `/shop-items` Route Behavior

**Files:**
- Inspect/modify route rules or `www` route files as needed.
- Likely modify: `apps/locally_twisted/locally_twisted/hooks.py`
- Likely inspect: any existing `apps/locally_twisted/locally_twisted/www/shop_items*` route source.
- Modify tests in `scripts/verify/smoke_shop.py` if the contract is made more explicit.

- [ ] Verify how `/shop-items` currently resolves.
- [ ] Implement the approved behavior:
  - redirect/alias `/shop-items` to `/shop`, or
  - render the same broad showroom system as `/shop`.
- [ ] Prefer redirect/alias to `/shop` unless a live route constraint makes render-reuse safer.
- [ ] Preserve `/shop-items/<group>` and `/shop-items/<group>/<product>` route behavior.

## Task 5: Redesign Product Detail Showroom Layout

**Files:**
- Modify: `apps/locally_twisted/locally_twisted/templates/generators/item/item.html`
- Modify: `apps/locally_twisted/locally_twisted/templates/generators/item/item_details.html`
- Modify only if necessary: `apps/locally_twisted/locally_twisted/templates/generators/item/item_configure.html`
- Modify: `apps/locally_twisted/locally_twisted/public/css/lt-product-polish.css`

- [ ] Make product detail feel like a product showcase:
  - larger image frame on desktop.
  - clear image/details balance.
  - mobile stacks image, details, options, and actions in a clean order.
  - option selectors remain visible and usable.
  - price and cart/quote path remain clear.
- [ ] Preserve selectors used by variant media and add-to-cart code:
  - `.product-image img.website-image`
  - `.lt-product__configure`
  - `#lt-add-to-cart-variant`
  - `.lt-view-in-cart`
  - `.lt-product__cart`

## Task 6: Verify, Integrate, And Document

**Files:**
- Modify: `workstreams/shop.md`
- Modify: `workstreams/website-launch.md`
- Optionally modify: `CODING-HANDOFF.md` if the implementation changes the next-handoff startup state materially.

- [ ] Clear website cache:

```bash
python scripts/dev/clear_website_cache.py --restart
```

- [ ] Run focused verification:

```bash
python scripts/verify/smoke_shop.py
npm run test:layout-fit
npm run test:interactive-layout
```

- [ ] Run broad public verification:

```bash
npm run test:public-verify
```

- [ ] Capture desktop/mobile screenshots for `/shop`, `/shop-items/arches`, and a representative product detail:

```bash
npx playwright screenshot --viewport-size=375,812 --full-page http://localhost:8081/shop output/playwright/shop-showroom-20260506/shop-mobile.png
npx playwright screenshot --viewport-size=1366,900 --full-page http://localhost:8081/shop output/playwright/shop-showroom-20260506/shop-desktop.png
npx playwright screenshot --viewport-size=375,812 --full-page http://localhost:8081/shop-items/arches output/playwright/shop-showroom-20260506/category-mobile.png
npx playwright screenshot --viewport-size=1366,900 --full-page http://localhost:8081/shop-items/arches output/playwright/shop-showroom-20260506/category-desktop.png
npx playwright screenshot --viewport-size=375,812 --full-page http://localhost:8081/shop-items/garlands/baby-shower-garland output/playwright/shop-showroom-20260506/product-mobile.png
npx playwright screenshot --viewport-size=1366,900 --full-page http://localhost:8081/shop-items/garlands/baby-shower-garland output/playwright/shop-showroom-20260506/product-desktop.png
```

- [ ] Update workstream docs with:
  - changed files.
  - verification commands and results.
  - remaining visual review notes.
  - confirmation that portfolio, checkout behavior, Lead schema, Event Playground, finance, and catalog seed logic were not part of the slice.

## Parallel Ownership Plan

Use parallel agents only with disjoint write scopes:

- Worker A: category listing template/CSS and route behavior for `/shop-items/<group>`.
- Worker B: `/shop` broad showroom markup/data/CSS.
- Worker C: product detail template/CSS.
- Controller: failing verifier, smoke/layout integration, hooks cache-bust, docs, final verification.

If two workers need `lt-product-polish.css`, they must edit different clearly marked sections or return proposed patches for controller integration. The controller owns final CSS merge and all verification.
