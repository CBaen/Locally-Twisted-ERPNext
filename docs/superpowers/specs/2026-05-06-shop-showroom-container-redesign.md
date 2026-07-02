# Shop Showroom Container Redesign

Date: 2026-05-06
Project: Locally Twisted ERPNext/Frappe
Status: Approved for implementation planning

## Purpose

The current `/shop`, `/shop-items`, and `/shop-items/<group>` pages do not show products well enough. The pages are behaving too much like squeezed ERP/Webshop listing screens: cards are small, category cards can collapse badly, and product images are cut off or reduced to thumbnails.

The redesign should make the shop surfaces feel like product-showcase pages. Longer pages are acceptable and expected if that gives products larger photos and room to breathe.

## Current Evidence

Live checks on 2026-05-06 showed:

- Frappe's mandatory `main.container` is already visually neutralized on these routes: full viewport width, `max-width: 100%`, and zero horizontal padding.
- `/shop` desktop product cards measured about 263px wide with images around 229px by 172px.
- `/shop-items/arches` desktop cards measured about 115px wide in one live probe because Webshop's native `col-sm-4 item-card` behavior was fighting the LT grid.
- The checked product detail page image measured about 325px by 243px on desktop, too modest for a product-showcase page.

The main issue is not only Frappe's wrapper. It is the current LT/Webshop card and grid contract inside the already-neutralized shell.

## Approved Approach

Use the **LT Showroom Breakout** approach.

This keeps Frappe/Webshop route lifecycle and commerce behavior, but makes the visible shop pages use LT-owned showroom presentation:

- wide wrappers on desktop
- larger photo-first product cards
- no desktop sidebar stealing category product width
- category pages with a distinct intro/product-showcase role
- fixed large image frames that show the whole product image
- breakpoints designed for product presentation rather than ERP density

## Route Roles

### `/shop`

Broad ready-to-order showroom hub.

Required treatment:

- large intro explaining ready-to-order decor
- category chips or similar top controls
- large product cards
- clear `Choose options`, `Add to cart`, or quote-path calls to action
- wide desktop layout, not a narrow content column

### `/shop-items`

This should not be a separate cramped Webshop/default visual surface.

Recommended treatment:

- redirect or alias cleanly to `/shop`, so there is one broad browse surface.
- If it renders instead of redirecting, it must use the same broad showroom system as `/shop`.

### `/shop-items/<group>`

Distinct category showcase.

Required treatment:

- category intro at the top
- no desktop sidebar
- category navigation, filters, and sort controls above the grid
- large product cards for that category
- presentation should feel like a category landing page, not filtered database output

### `/shop-items/<group>/<product>`

Product detail should receive compatible showroom treatment.

Required treatment:

- larger image area
- clearer image/details balance
- option selectors remain visible and usable
- price and cart/quote path stay clear
- no cramped option or image region

## Product Card Rules

Product cards should be large, calm, and photo-first.

Approved image treatment:

- use a fixed large image frame
- use contained imagery so the whole product/photo is visible
- do not crop the balloon work with `object-fit: cover` as the default card behavior
- warm or neutral padding/letterboxing is acceptable when source image proportions require it

Approved density:

- mobile: 1 card per row
- tablet: 2 cards per row
- normal desktop: 2 to 3 cards per row
- wide desktop: 3 cards per row
- avoid 4 to 5 column grids for these product-showcase pages

Pages may become longer vertically. That is a desired tradeoff.

## Container Contract

The shop redesign must follow the project Frappe container contract:

- Frappe owns the website lifecycle and mandatory wrapper.
- LT owns visual containment inside the wrapper.
- Do not depend on Frappe's stock `main.container` for readable width because LT neutralizes it.
- Use LT-owned inner wrappers with wide max widths, stable gutters, `box-sizing: border-box`, and `min-width: 0`.
- Full-width or wide bands must still contain readable content inside an inner wrapper.

Target desktop wrapper scale:

- broad shop and category surfaces should use a wide wrapper around 1440px to 1500px where appropriate.
- product detail should use a wide but controlled wrapper that gives image and option areas room without making text unreadable.

## Webshop Guardrails

Do not break the commerce system while fixing the visual layout.

Preserve required Webshop/Frappe behavior and hooks:

- route lifecycle under Frappe/Jinja
- item and item group routes
- category route behavior
- product detail route behavior
- variant selector data and cart writes
- single-SKU add-to-cart behavior
- local guest cart behavior
- checkout lane and quote-path behavior

Do not remove or rename native hooks blindly. In particular, be careful with:

- `item-group-content`
- `#product-listing`
- Webshop product card classes consumed by bundled JS
- product detail selectors used by variant media and add-to-cart code

If a native class causes layout failure, override its visual layout deliberately instead of deleting it without checking dependent JS.

## Scope

In scope:

- `/shop`
- `/shop-items`
- `/shop-items/<group>`
- product detail pages under `/shop-items/<group>/<product>`
- shop/category/product CSS
- route-specific verifier updates
- smoke tests needed to prove category/product/cart behavior still works

Out of scope:

- portfolio
- Event Playground
- checkout payment behavior
- cart storage behavior
- Lead/contact schema
- finance automation
- catalog seed logic
- broad site rebrand changes outside shop surfaces

## Implementation Order

Recommended order:

1. Fix the category listing contract first because it has the worst card collapse.
2. Align `/shop` to the same large-card visual system while preserving its broader hub role.
3. Decide and implement `/shop-items` as a redirect/alias to `/shop` or a direct reuse of the `/shop` showroom.
4. Update product detail image/info layout to match the showroom direction.
5. Update verifiers to check the new visual and behavioral contract.

## Verification Requirements

Before calling the work done, verify:

- `/shop` loads and uses large photo-first cards.
- `/shop-items` does not expose a cramped Webshop/default listing.
- `/shop-items/<group>` uses top controls, not a desktop sidebar.
- category product cards no longer collapse or smash.
- product card images are contained and not cut off.
- mobile cards are full-width and readable.
- tablet and desktop breakpoints use the approved density.
- product detail image area is meaningfully larger and not cramped.
- variant product option selection still works.
- variant cart writes still work.
- single-SKU add-to-cart still works.
- category/product routes still return 200.
- no document-level overflow appears at the project breakpoint set.

Run the relevant current commands:

```bash
python scripts/dev/clear_website_cache.py
npm run test:layout-fit
npm run test:interactive-layout
python scripts/verify/smoke_shop.py
npm run test:public-verify
```

Add or adjust focused checks if the current verifier does not prove the new showroom contract.

## Approval

Guiding Light approved:

- LT Showroom Breakout as the approach.
- Distinct category intro/product-showcase treatment for `/shop-items/<group>`.
- Top controls instead of desktop sidebars on category pages.
- Fixed large image frames with contained imagery.
- 1 / 2 / 2-3 / 3 responsive density.
- Longer pages as the correct tradeoff for showing products well.
