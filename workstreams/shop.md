# Shop Workstream

Last updated: 2026-05-19 by Codex after the ecommerce price-identity incident review.

## Outcome

Make the Locally Twisted shop feel like a polished, trustworthy extension of the public site while preserving ERPNext as the source of truth for catalog, cart, checkout, and order flow. As of 2026-05-10, this is a full local ecommerce testing lane; production launch still requires staging/client approval and live payment/cutover gates.

This is the active feature-lane handoff for shop work. `HANDOFF.md` remains valid as a reference guide, but shop work should coordinate here first, then verify against the queue, current files, git state, and the running ERPNext site.

## Current Stage

Active full-testing handoff lane. Local ecommerce is currently open with `lt_ecommerce_paused=0`; guest traffic to `/shop`, `/shop-items`, `/shop-by-category`, `/all-products`, `/cart`, and `/checkout` should render the actual customer surfaces, not the pause page. The pause layer remains available as a safety switch, but it is not the current proof mode.

The guest cart/checkout item-code contract, broad browse routing, first variant-media reconciliation pass, per-product variant correctness diff, category-media candidate packet, 2026-05-06 shop showroom container redesign, same-day symmetry repair, 2026-05-07 product-detail company-first/clear-control cleanup, 2026-05-08 bouquet-size price repair, 2026-05-08 whole-card product navigation, and 2026-05-19 broad local source-price modifier repair are in place and now have focused local verification. Product detail pages no longer render Webshop's lower Additional Info/Reviews/Recommendations panel, product option controls no longer render as nested boxes, and product listing cards navigate from non-interactive card areas while preserving real buttons and links. `smoke_shop.py` is mode-aware. The 2026-05-06 commerce-rules checkout slice has its own lane at `workstreams/commerce-rules-checkout.md`; catalog price recovery now has its own lane at `workstreams/catalog-variant-price-recovery.md`; the 2026-05-19 price incident lane is `workstreams/ecommerce-price-identity-incident-review-2026-05-19.md`; public microinteractions have their own lane at `workstreams/public-site-microinteractions.md`. Keep shop layout/media work coordinated with checkout, source-price parity, and microinteraction contracts. The next shop work should continue with GL local review of design/logic, target-site source-price proof before any staging/live claim, Jeff/GL media approval before assigning category/product media, then product photo/options polish from real product states.

Security note from 2026-05-08: `/shop?q=` reflected XSS was reproduced through
the real local site and patched by escaping `search_query`. Product-gallery
image rendering was also hardened. The broader public storefront security lane
is `workstreams/public-site-security-hardening.md`; shop agents must keep public
input/output escaping in scope when changing listing/search/product templates.

Priority order from the current queue:

1. Preserve the 2026-05-19 price-identity guard stack from `workstreams/ecommerce-price-identity-incident-review-2026-05-19.md` before changing product import, selectors, cart, checkout, or payment behavior.
2. Review skipped/unmatched catalog media and approve category browse imagery from `output/category-media-candidates.md` after regenerating it.
3. Remaining configure-option UX fixes where they affect customer purchase flow.

## Owner

Unassigned next agent/session.

Work from the main project workspace unless the user explicitly asks for a separate worktree:

`C:\Users\baenb\projects\Built_by_Cameron\_CLIENTS\locally-twisted`

## User-Facing Impact

Customers should be able to browse categories, inspect products, choose only valid options, add configured products to the guest cart, and check out without seeing ERPNext jargon, login traps, broken combinations, missing images, or placeholder category visuals. If the pause switch is deliberately enabled later, customers should instead see a clear branded pause page that points them to `/contact` and `/portfolio`.

## Touched Areas

- `/shop`
- `/shop-by-category` compatibility redirect
- `/shop-items/<group>`
- `/shop-items/<group>/<slug>`
- `/cart`
- `/checkout`
- `/payment-success`
- `/thank-you`
- Product listing cards, category detail pages, product detail pages, configure controls, and guest cart behavior.
- Public pause layer: `apps/locally_twisted/locally_twisted/ecommerce_pause.py`, `www/ready_to_order_paused.py`, `www/ready_to_order_paused.html`, and `scripts/verify/ecommerce_pause_contract.py`.

Primary files:

- `apps/locally_twisted/locally_twisted/www/shop.py`
- `apps/locally_twisted/locally_twisted/www/shop.html`
- `apps/locally_twisted/locally_twisted/www/shop-by-category/index.py`
- `apps/locally_twisted/locally_twisted/www/shop-by-category/index.html`
- `apps/locally_twisted/locally_twisted/templates/generators/item_group.html`
- `apps/locally_twisted/locally_twisted/templates/generators/item/item_details.html`
- `apps/locally_twisted/locally_twisted/templates/generators/item/item_configure.html`
- `apps/locally_twisted/locally_twisted/templates/generators/item/item_add_to_cart.html`
- `apps/locally_twisted/locally_twisted/api/product_listing.py`
- `apps/locally_twisted/locally_twisted/api/cart.py`
- `apps/locally_twisted/locally_twisted/api/variant_media.py`
- `apps/locally_twisted/locally_twisted/seed/sync_variant_media.py`
- `apps/locally_twisted/locally_twisted/seed/repair_variant_prices_from_legacy_source.py`
- `apps/locally_twisted/locally_twisted/templates/generators/item/item.html`
- `apps/locally_twisted/locally_twisted/templates/includes/shop_category_nav.html`
- `apps/locally_twisted/locally_twisted/www/lt_cart.html`
- `apps/locally_twisted/locally_twisted/www/checkout.py`
- `apps/locally_twisted/locally_twisted/www/checkout.html`
- `apps/locally_twisted/locally_twisted/public/js/lt-guest-cart.js`
- `apps/locally_twisted/locally_twisted/public/js/lt-product-card-click.js`
- `apps/locally_twisted/locally_twisted/public/js/lt-webshop-a11y.js`
- `apps/locally_twisted/locally_twisted/public/css/lt-theme.css`
- `apps/locally_twisted/locally_twisted/public/css/lt-shop-showroom.css`
- `apps/locally_twisted/locally_twisted/hooks.py`
- `apps/locally_twisted/locally_twisted/seed/seed_catalog.py`
- `scripts/setup/stage_seed_data.py`

Reference and verification files:

- `locally-twisted-queue.md`
- `PROJECT-STATUS.md`
- `HANDOFF.md`
- `MIRROR-REBUILD-PLAN.md`
- `_resources/STYLE-GUIDE.md`
- `_resources/STYLE-GUIDE.md` version 4.2 or newer for all current visual guidance; the old `_resources/design-guide/` synthesis was deleted on 2026-05-05 and must not be used.
- `_resources/catalog-source/catalog.json`
- `_resources/catalog-source/images/`
- `_resources/catalog-source/value_normalize_map.json`
- `scripts/verify/smoke_shop.py`
- `scripts/verify/cart_checkout_contract.py`
- `scripts/verify/product_variant_price_contract.py`
- `scripts/verify/variant_media_contract.py`
- `scripts/verify/catalog_variant_contract.py`
- `scripts/setup/sync_variant_media.py`
- `scripts/verify/nav_ia.py`
- `scripts/verify/layout_fit.spec.js`
- `capabilities/recipes/frappe-product-page-company-first.md`
- `capabilities/recipes/frappe-product-clear-control-contract.md`
- `capabilities/recipes/public-site-microinteraction-contract.md`

## Known Current Facts

- Phase 1 shop surfaces are currently open for local guest testing: `/shop`, `/shop-by-category`, `/shop-items/<group>`, `/shop-items/<group>/<slug>`, `/cart`, and `/checkout` should render the live customer ecommerce path with `lt_ecommerce_paused=0`. `/payment-success` and `/thank-you` remain payment-return surfaces and still need live/payment-mode care before production cutover.
- Current local taxonomy state verified 2026-05-24 by `shop_taxonomy_contract.py` is 51 published Website Items, 8 visible primary groups under `Shop Items`, 9 secondary groups under hidden `Shop Occasions`, and 51 secondary Website Item Group rows. Current sellability proof is 30 checkout Website Items and 21 quote-first Website Items. Re-check the target DB before changing seed logic or making staging/live claims from these numbers.
- Item Group hierarchy under `Shop Items` has 8 customer-facing children: Arches, Balloon Drops, Bouquets, Columns, Garlands, Photo Ops & Backdrops, Stands & Easels, and Table Decor. Prior fulfillment/menu/occasion groups are hidden and covered by route aliases.
- Webshop settings are documented with variants and attribute filters enabled.
- Bulk catalog import lives in `seed_catalog.py` and honors captured legacy_source `data-attribute-exclusions`.
- Product listing cards use `lt_brand_description` through `locally_twisted.api.product_listing`.
- `/shop` is the all-decor hub. `/shop-items`, `/all-products`, and `/shop-by-category` route or redirect to `/shop`; category detail pages stay at `/shop-items/<group>`.
- `/shop-items/arches` previously required restoring `.item-group-content`; do not remove that structure without retesting group pages.
- Shop showroom container redesign completed 2026-05-06: `/shop` uses large photo-first ready-to-order cards; `/shop-items` aliases to the `/shop` showroom contract; `/shop-items/<group>` keeps Webshop/Frappe product listing behavior while using the LT showroom shell; product detail pages use a wider contained image/detail layout. The shared override is `lt-shop-showroom.css`, loaded after `lt-product-polish.css`.
- Product detail company-first cleanup completed 2026-05-07: the Webshop lower Additional Info/Reviews/Recommended Items panel is removed from product detail pages, the old auxiliary/recommendation CSS selectors are gone, and the primary product shell is less visibly boxed. The same-day clear-control correction removed boxed styling from product options, variant chips, select/dropdowns, and price/add-to-cart groups; pickup/delivery is the approved framed product-detail exception. Do not restore recommendation panels, empty reviews/spec tabs, generic upsell sections, or boxed product controls unless GL explicitly reopens the decision. Capabilities: `capabilities/recipes/frappe-product-page-company-first.md` and `capabilities/recipes/frappe-product-clear-control-contract.md`.
- Shop category navigation UX repair completed 2026-05-06: the old `/shop` chip filter wall and `/shop-items/<group>` 12-button tile wall are retired. Both `/shop` and category pages use the shared `shop_category_nav.html` component: a slim desktop left rail and a native mobile category select. `/shop` category choices now navigate to category pages instead of filtering in place; product grids still avoid a single desktop orphan card where the rendered count makes that possible.
- Verified showroom measurements on 2026-05-06: `/shop` desktop cards remain above the `340px` card and `300px` image minimums with the category rail present, `/shop` mobile cards remain non-thumbnail, `/shop-items/arches` desktop cards remain showroom-sized in paired rows, and the representative product detail image remains above the desktop image-size contract.
- Current ERPNext product records are test fixtures for ecommerce receiving proof, not final catalog truth. Do not make catalog-completeness claims from them. Future product work must prove a controlled purge/reupload/import path populates LT Website Item/custom fields, preserves cascading option/dependency information, and triggers expected automations before any public product shelf is trusted.
- The guest cart is localStorage-based at `/cart`, supports multi-item checkout, and connects to Stripe Checkout Sessions in test mode.
- Current checkout commerce rules: ready-to-order goods can check out and are taxable by fulfillment ZIP/city rate; services, BTFP, service deposits, and delivery charges are non-taxable; standard local delivery is `$15`; Park City delivery is `$50`; out-of-area delivery redirects to a prefilled `/contact` quote path. Product group alone is not a checkout quote gate. See `workstreams/commerce-rules-checkout.md` before changing cart, checkout, delivery, service, or deposit behavior.
- Cart/checkout now sells actual Item codes and uses the parent Website Item for route/name display when the item is a variant. If the variant has its own `Item.image`, cart/checkout use that selected-variant image; otherwise they fall back to the parent Website Item image. Fixed-price products stay cartable unless fulfillment details, especially out-of-area delivery ZIP, require a quote path.
- `/shop` cards for variant templates link to "Choose options" instead of adding an unpriced template code. Single-SKU cards add directly when priced.
- `/shop` and Webshop-rendered category product cards are whole-card clickable from non-interactive card areas. The delegated handler preserves real links/buttons, `Add to cart`, `Choose options`, `Request quote`, selectors, modified clicks, and text selection. Do not wrap entire cards in anchors; use `lt-product-card-click.js` and `.lt-product-card-clickable`.
- `smoke_shop.py` now verifies fixed-price product pages do not invent product-level quote gates, proves a real retail option-selection add-to-cart flow for `unicorn-bouquet`, distinguishes optional add-on checkboxes from variant chips, and checks the showroom contracts for `/shop`, `/shop-items`, `/shop-items/<group>`, product detail image scale/containment, the desktop rail/mobile select category navigation contract, `/shop` product-grid orphan prevention, and category-product-grid orphan prevention. `cart_checkout_contract.py` verifies the shared API/checkout contract.
- Variant media first pass completed 2026-05-02: 1,712 variant `Item.image` values are set from `_resources/catalog-source/images/` where legacy_source image labels clearly matched product options. Product pages call `locally_twisted.api.variant_media.get_variant_media` after exact option selection and swap the main image when a variant image exists.
- Detailed media review is now reproducible with `python scripts/setup/sync_variant_media.py --dry-run --include-details --report output/catalog-media-review.json`. Latest refreshed report on 2026-05-06: 49 products checked, 35 with candidate image labels, 45 needing review, 1,712 unchanged mapped variants, and 6,831 skipped variant image assignments.
- Category browse media review is now reproducible with `python scripts/verify/category_media_candidates.py`. Latest taxonomy smoke on 2026-05-24 checked the 8 active customer-facing Item Groups and wrote ignored local reports to `output/category-media-candidates-taxonomy-smoke.json` and `output/category-media-candidates-taxonomy-smoke.md`. `python scripts/setup/sync_category_media.py --write-template` creates an approval template, and the dry-run helper stages approved selections through Frappe without writing unless `--apply` is used. No ERPNext image fields were changed.
- Product breadcrumbs on detail pages now start at `All Balloon Decor` instead of the retired `Shop by Category` route.
- Per-product variant correctness now compares normalized legacy_source `valid_variants` plus approved preset projections to active, required-choice ERPNext variants. Current pass on 2026-05-19: `scripts/verify/catalog_variant_contract.py` checked 53 products, 10,186 expected active variants, 10,186 live active variants, and 4 single-SKU products. Disabled legacy optional-add-on/raw-color variants are intentionally ignored by this customer-facing contract. This is variant-shape parity only.
- Catalog variant price parity is locally guarded after the 2026-05-19 incident. The bouquet-size contract still covers the historical bouquet failure; `product_price_modifier_contract.py` now checks broad legacy_source option price modifiers across active variant products; `product_price_display.spec.js` proves the reported Easter Bunny Ear Arch page changes visible price and selected item code. Continue in `workstreams/ecommerce-price-identity-incident-review-2026-05-19.md` and `workstreams/catalog-variant-price-recovery.md`.
- Product option UX P0 pass completed 2026-05-02: no per-attribute Jinja DB lookup, progressive invalid-option disabling wired to `valid_options_for_attributes`, and chip inputs verified as radio/single-select. Active uncommitted work may also be refining variant starting-price display; verify before claiming that slice complete.
- `.product-code` CSS hiding is the known intentional `!important` exception.
- The stale Webshop generated asset map was corrected in the running ERPNext stack on 2026-05-02. No package install was needed: Yarn Classic exists at `/home/frappe/.nvm/versions/node/v20.19.2/bin/yarn`, but non-interactive `docker exec` does not include it in `PATH`. Build Webshop assets with `export PATH=/home/frappe/.nvm/versions/node/v20.19.2/bin:$PATH`. The frontend/nginx container must be built last because shared `assets.json` points to files served from that container's app-public symlink. Current rendered `/shop` references `/assets/webshop/dist/css/webshop-web.bundle.C4VO6TJ6.css` and `/assets/webshop/dist/css-rtl/webshop-web.bundle.JDOEFDY5.css`, both returning `200 text/css`; Playwright console sweeps returned 0 errors/warnings.
- A historical 320px category-grid overflow on the old seasonal category route was fixed by overriding Webshop's stock `.item-card { min-width: 300px; }` with `min-width: 0` inside `#products-grid-area .item-card`; current active category routes are governed by the 2026-05-24 taxonomy proof.
- A 2026-05-02 browser smoke check verified `/shop-by-category` redirects to `/shop`, the desktop/mobile `All Balloon Decor` links use `/shop`, and `/shop-items/arches` returns 200.

## Active Risks

- Category browse media is still unassigned in ERPNext. The 2026-05-24 taxonomy pass retained that boundary: route hero art exists in source, but Item Group `image` fields remain unapproved. `scripts/verify/category_media_candidates.py` creates a no-mutation approval packet for the 8 active categories, but Jeff/GL still need to approve selected images before live assignment. Do not restore the retired `/shop-by-category` card index as a shortcut.
- Catalog media remains incomplete where the legacy_source image labels were too generic to map safely. Do not assign skipped images by guess; review them with GL/Jeff or add explicit mapping rules.

## Dependencies And Collision Points

- Shop design work depends on `_resources/STYLE-GUIDE.md`. Do not use the deleted `_resources/design-guide/` synthesis, old pastel screenshots, DM Serif/Raleway rules, or light-blue/blush treatment as current shop guidance.
- Variant shape correctness is locally verified; variant price correctness is locally guarded for the active variant set after the 2026-05-19 incident. Do not treat local repair as staging/live approval, and do not make product-detail/layout polish imply purchase readiness unless source-price, cart, checkout, payment, and receipt proof are current for the target site.
- Cart/checkout changes can collide with payment cascade, sales invoice creation, and email behavior. Treat those as customer purchase-flow boundaries, not just frontend work.
- Backend simplification and shop work may touch shared ERPNext doctypes, fixtures, or seed scripts. Check `PROJECT-STATUS.md` and other `workstreams/*.md` before changing shared catalog or checkout data.

## Do Not Do

- Do not rewrite `HANDOFF.md` just because this file exists.
- Do not treat placeholder images, template-only images, or documented catalog counts as proof of current ERPNext state.
- Do not remove ERPNext structures needed by Website Item, Item Group, cart, checkout, or payment cascade without verifying the whole purchase flow.
- Do not split work by generic frontend/backend ownership. Keep this lane organized around the customer-facing shop outcome.
- Do not make broad visual changes before checking variant validity and media completeness for the products being redesigned.
- Do not restore Webshop recommendation panels, empty auxiliary product detail boxes, or boxed product option controls as a substitute for company proof.

## Verification

Use the exact route or flow being changed. Do not rely on proxy checks.

Before shop edits:

- Review `locally-twisted-queue.md`, this file, `PROJECT-STATUS.md`, and `HANDOFF.md`.
- Re-run or refresh the relevant catalog truth check before seed, variant, or media changes.
- Run the mirror/product diff path from `MIRROR-REBUILD-PLAN.md` before layout overhaul work.

After route, template, CSS, or JS edits:

- `npm run test:ecommerce-full`
- `python scripts/verify/ecommerce_pause_contract.py`
- `python scripts/verify/smoke_shop.py`
- `python scripts/verify/cart_checkout_contract.py`
- `npm run test:product-prices`
- `npm run test:product-price-display`
- `python scripts/verify/commerce_rules_contract.py`
- `python scripts/verify/checkout_fulfillment_contract.py`
- `python scripts/verify/checkout_lead_conversion_contract.py`
- `python scripts/verify/variant_media_contract.py`
- `python scripts/verify/catalog_variant_contract.py`
- `python scripts/setup/sync_variant_media.py --dry-run --include-details --report output/catalog-media-review.json`
- `python scripts/verify/category_media_candidates.py`
- `python scripts/setup/sync_category_media.py --write-template`
- `python scripts/setup/sync_category_media.py --selection output/category-media-selection.template.json`
- `python scripts/verify/nav_ia.py`
- `npm run test:layout-fit`
- `npm run test:interactive-layout`

Whole-card product navigation verification on 2026-05-08:

- Targeted browser check proved all 53 `/shop` cards were clickable from card body areas.
- Targeted browser check proved Webshop category cards became clickable after render.
- Single-SKU add-to-cart still stayed on the page and added the item instead of being hijacked by card navigation.
- `python scripts/dev/clear_website_cache.py` passed.
- `npm run test:shop-smoke` passed.
- `npm run test:layout-fit` passed 247/247.
- `npm run test:interactive-layout` passed 88/88 after decorative cursor overflow was clamped.

Latest showroom-focused verification on 2026-05-06:

- `python scripts/verify/smoke_shop.py` passed.
- `npm run test:layout-fit -- --grep shop` passed 26/26.
- `npm run test:layout-fit -- --grep "variant-product|single-product|seasonal-category"` passed 39/39.
- `npm run test:interactive-layout -- --grep "/shop category navigation"` passed 4/4.
- Browser screenshot and geometry checks were historically refreshed for `/shop`, `/shop-items/arches`, one old get-well route, and `/shop-items/garlands/baby-shower-garland`; transient screenshot folders were not kept as source. Rerun current checks against the 8 active primary category routes before using this as launch evidence.
- The category navigation repair verified no `.lt-shop__chip` controls on `/shop`, no old `.lt-shop__toolbar--categories` button wall on category pages, one 12-link desktop category rail, one 12-option mobile category select, and paired Arches product rows on `/shop-items/arches`.

Product-detail company-first verification on 2026-05-07:

- `python scripts/dev/clear_website_cache.py --restart` passed.
- `python scripts/verify/smoke_shop.py` passed, including the new
  no-auxiliary/recommendation-panel guard.
- `npm run test:layout-fit -- --grep "variant-product|single-product|seasonal-category"`
  passed 39/39.
- Fresh Unicorn Bouquet desktop/mobile screenshots were captured at
  `output/playwright/product-page-company-first-unicorn-1366.png` and
  `output/playwright/product-page-company-first-unicorn-390.png`.
- Same-day clear-control verification added a red/green smoke guard: the first
  `python scripts/verify/smoke_shop.py` run failed on `.lt-product__configure`
  because the live route still had borders/radius/shadow; after clearing the
  product controls in CSS, `python scripts/dev/clear_website_cache.py --restart`
  and `python scripts/verify/smoke_shop.py` passed. Fresh screenshots are in
  `output/playwright/product-page-clear-options-unicorn-1366.png` and
  `output/playwright/product-page-clear-options-unicorn-390.png`.

For cache-sensitive Website Route or template changes:

- Clear ERPNext website cache using the local project script if available.
- Recheck the exact changed route in browser-sized desktop and mobile views.

For purchase-flow changes:

- Verify guest add-to-cart from product listing and configured product detail.
- Verify cart line items use purchasable variant codes where variants are required.
- Verify checkout can proceed without guest login redirect.
- Verify payment success still reaches `/thank-you` and does not break the documented invoice/email cascade.

Full ecommerce testing verification on 2026-05-10:

- `bench --site frontend set-config lt_ecommerce_paused 0` opened local public ecommerce and `python scripts/dev/clear_website_cache.py` cleared website caches.
- `npm run test:ecommerce-full` passed: public ecommerce mode, shop smoke, product prices, variant media, checkout experience, checkout fulfillment, and checkout-to-Lead conversion.
- `npm run test:public-verify` passed 12 website steps with open ecommerce checks included.
- `python scripts/verify/synthetic_business_pipeline.py` passed with 22 synthetic readiness contracts, 0 broken piping, 8 inefficiencies, and 3 cutover-deferred items.
- `python scripts/verify/business_automation_index.py` passed with 27 connected surfaces, 3 future/setup partials, 0 missing required/useful surfaces, and 0 loud-failure gaps.

Shop smoke closeout on 2026-05-11:

- `scripts/verify/smoke_shop.py` was rebaselined for current audience-page H1
  copy from `apps/locally_twisted/locally_twisted/www/event_type_pages.py`.
- The `/civic-community missing focused page title` blocker is cleared. The
  same title map now matches the current `/corporate-events`,
  `/schools-campuses`, and `/private-celebrations` H1 source so peer GPT 5.5
  agents do not rediscover the same stale verifier mismatch route by route.
- Closeout command: `npm run test:shop-smoke` passed with
  `=== All shop smoke checks PASSED ===`.
- This is a real client project. The currently visible/imported product records
  are test products/fixtures for architecture and behavior proof only, not
  launch catalog truth.

Open ecommerce webshop role for future peer agents:

- Do not treat the ecommerce lane as frontend-only. Product-page UX and
  SEO/AEO/GEO decisions must preserve ERPNext v15.105.0 / Frappe v15 Webshop
  backend meaning through Item, Item Variant, Website Item, Item Price, Item
  Attribute, media/gallery, Webshop Settings, cart/checkout APIs, payments, and
  Frappe Cloud persistence.
- If product-page copy, media, price, variants, structured data, or discovery
  claims cannot be verified against backend fields or runtime evidence, mark
  the claim blocked instead of guessing.

## Decisions And References

- Active task source: `locally-twisted-queue.md`.
- Overall project map: `PROJECT-STATUS.md`.
- Reference guide and historical context: `HANDOFF.md`.
- Mirror rebuild sequencing: `MIRROR-REBUILD-PLAN.md`.
- Durable reasoning: `locally-twisted-decisions.md`.
- Project agent routing: `AGENTS.md`.

## Next Handoff Stage

When handing this lane to another agent/session, update this file with:

- What changed.
- Exact routes and product examples touched.
- Verification commands run and their results.
- Any product, variant, image, cart, or checkout behavior that still needs attention.
- Any decision that should be promoted to `locally-twisted-decisions.md`.
