# Shop Workstream

Last updated: 2026-05-02 by Codex.

## Outcome

Make the Locally Twisted shop feel like a polished, trustworthy extension of the public site while preserving ERPNext as the source of truth for catalog, cart, checkout, and order flow.

This is the active feature-lane handoff for shop work. `HANDOFF.md` remains valid as a reference guide, but shop work should coordinate here first, then verify against the queue, current files, git state, and the running ERPNext site.

## Current Stage

Active handoff lane. The guest cart/checkout item-code contract, broad browse routing, first variant-media reconciliation pass, and per-product variant correctness diff were completed on 2026-05-02. The next shop work should continue with remaining media review before broad layout overhaul.

Priority order from the current queue:

1. Review skipped/unmatched catalog media and category browse imagery.
2. Webshop layout overhaul for `/shop`, product group pages, and product detail pages.
3. Remaining configure-option UX fixes where they affect customer purchase flow.

## Owner

Unassigned next agent/session.

Work from the main project workspace unless the user explicitly asks for a separate worktree:

`C:\Users\baenb\projects\Built_by_Cameron\_CLIENTS\locally-twisted`

## User-Facing Impact

Customers should be able to browse categories, inspect products, choose only valid options, add configured products to the guest cart, and check out without seeing ERPNext jargon, login traps, broken combinations, missing images, or placeholder category visuals.

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
- `apps/locally_twisted/locally_twisted/templates/generators/item/item.html`
- `apps/locally_twisted/locally_twisted/www/lt_cart.html`
- `apps/locally_twisted/locally_twisted/www/checkout.py`
- `apps/locally_twisted/locally_twisted/www/checkout.html`
- `apps/locally_twisted/locally_twisted/public/js/lt-guest-cart.js`
- `apps/locally_twisted/locally_twisted/public/js/lt-webshop-a11y.js`
- `apps/locally_twisted/locally_twisted/public/css/lt-theme.css`
- `apps/locally_twisted/locally_twisted/seed/seed_catalog.py`

Reference and verification files:

- `locally-twisted-queue.md`
- `PROJECT-STATUS.md`
- `HANDOFF.md`
- `MIRROR-REBUILD-PLAN.md`
- `_resources/STYLE-GUIDE.md`
- `_resources/design-guide/`
- `_resources/odoo-live/catalog.json`
- `_resources/odoo-live/images/`
- `_resources/odoo-live/value_normalize_map.json`
- `scripts/verify/smoke_shop.py`
- `scripts/verify/cart_checkout_contract.py`
- `scripts/verify/variant_media_contract.py`
- `scripts/verify/catalog_variant_contract.py`
- `scripts/setup/sync_variant_media.py`
- `scripts/verify/nav_ia.py`
- `scripts/verify/layout_fit.spec.js`

## Known Current Facts

- Phase 1 shop surfaces are live or compatibility-safe: `/shop`, `/shop-by-category` redirecting to `/shop`, `/shop-items/<group>`, `/shop-items/<group>/<slug>`, `/cart`, `/checkout`, `/payment-success`, and `/thank-you`.
- Current documented catalog state is 53 Website Items, 10,631 Items, 49 variant templates, 4 single-SKU templates, 10,578 variants, 10,613 Item Prices, 32,002 Item Variant Attribute rows, and 26 Item Attributes. Re-check live DB counts before changing seed logic or making claims from these numbers.
- Item Group hierarchy under `Shop Items` has 11 customer-facing children: Arches, Columns, Bouquets, Get-Well Bouquets, Garlands, Drops, Grab & Go, Table Decor, Stands & Easels, Deliveries, and Seasonal & Specialty.
- Webshop settings are documented with variants and attribute filters enabled.
- Bulk catalog import lives in `seed_catalog.py` and honors captured Odoo `data-attribute-exclusions`.
- Product listing cards use `lt_brand_description` through `locally_twisted.api.product_listing`.
- `/shop` is the all-decor hub. `/shop-items`, `/all-products`, and `/shop-by-category` route or redirect to `/shop`; category detail pages stay at `/shop-items/<group>`.
- `/shop-items/arches` previously required restoring `.item-group-content`; do not remove that structure without retesting group pages.
- The guest cart is localStorage-based at `/cart`, supports multi-item checkout, and connects to Stripe Checkout Sessions in test mode.
- Cart/checkout now sells actual Item codes and uses the parent Website Item for route/name display when the item is a variant. If the variant has its own `Item.image`, cart/checkout use that selected-variant image; otherwise they fall back to the parent Website Item image. Verified example: configured variant `6-color-rainbow-arch-20F` resolves with parent route, selected variant image, and price 340.0; template `6-color-rainbow-arch` is not directly purchasable.
- `/shop` cards for variant templates link to "Choose options" instead of adding an unpriced template code. Single-SKU cards still add directly.
- `smoke_shop.py` now verifies a real option-selection add-to-cart flow for `6-color-rainbow-arch-20F`. `cart_checkout_contract.py` verifies the shared API/checkout contract.
- Variant media first pass completed 2026-05-02: 1,712 variant `Item.image` values are set from `_resources/odoo-live/images/` where Odoo image labels clearly matched product options. Product pages call `locally_twisted.api.variant_media.get_variant_media` after exact option selection and swap the main image when a variant image exists.
- Detailed media review is now reproducible with `python scripts/setup/sync_variant_media.py --dry-run --include-details --report output/catalog-media-review.json`. Latest report: 49 products checked, 35 with candidate image labels, 45 needing review, 1,712 unchanged mapped variants, and 6,831 skipped variant image assignments.
- Product breadcrumbs on detail pages now start at `All Balloon Decor` instead of the retired `Shop by Category` route.
- Per-product variant correctness passed on 2026-05-02: `scripts/verify/catalog_variant_contract.py` checked all 53 catalog products, comparing normalized Odoo `valid_variants` to live ERPNext `Item Variant Attribute` rows. Result: 10,578 expected variants, 10,578 live variants, 4 single-SKU products, PASS.
- Product option UX P0 pass completed 2026-05-02: no per-attribute Jinja DB lookup, progressive invalid-option disabling wired to `valid_options_for_attributes`, and chip inputs verified as radio/single-select.
- `.product-code` CSS hiding is the known intentional `!important` exception.
- The stale Webshop generated asset map was corrected in the running ERPNext stack on 2026-05-02. No package install was needed: Yarn Classic exists at `/home/frappe/.nvm/versions/node/v20.19.2/bin/yarn`, but non-interactive `docker exec` does not include it in `PATH`. Build Webshop assets with `export PATH=/home/frappe/.nvm/versions/node/v20.19.2/bin:$PATH`. The frontend/nginx container must be built last because shared `assets.json` points to files served from that container's app-public symlink. Current rendered `/shop` references `/assets/webshop/dist/css/webshop-web.bundle.C4VO6TJ6.css` and `/assets/webshop/dist/css-rtl/webshop-web.bundle.JDOEFDY5.css`, both returning `200 text/css`; Playwright console sweeps returned 0 errors/warnings.
- A 320px category-grid overflow on `/shop-items/seasonal-specialty` was fixed by overriding Webshop's stock `.item-card { min-width: 300px; }` with `min-width: 0` inside `#products-grid-area .item-card`; `npm run test:layout-fit` passes 60/60 after the fix.
- A 2026-05-02 browser smoke check verified `/shop-by-category` redirects to `/shop`, the desktop/mobile `All Balloon Decor` links use `/shop`, and `/shop-items/arches` returns 200.

## Active Risks

- Category browse media is still incomplete because all 11 customer-facing child Item Groups under `Shop Items` have `image = null`; do not restore the retired `/shop-by-category` card index as a shortcut.
- Catalog media remains incomplete where the Odoo image labels were too generic to map safely. Do not assign skipped images by guess; review them with GL/Jeff or add explicit mapping rules.

## Dependencies And Collision Points

- Shop design work depends on `_resources/design-guide/` and `_resources/STYLE-GUIDE.md`.
- Variant correctness is verified; remaining media review should happen before final product-detail layout polish so the design work is based on real product states.
- Cart/checkout changes can collide with payment cascade, sales invoice creation, and email behavior. Treat those as customer purchase-flow boundaries, not just frontend work.
- Backend simplification and shop work may touch shared ERPNext doctypes, fixtures, or seed scripts. Check `PROJECT-STATUS.md` and other `workstreams/*.md` before changing shared catalog or checkout data.

## Do Not Do

- Do not rewrite `HANDOFF.md` just because this file exists.
- Do not treat placeholder images, template-only images, or documented catalog counts as proof of current ERPNext state.
- Do not remove ERPNext structures needed by Website Item, Item Group, cart, checkout, or payment cascade without verifying the whole purchase flow.
- Do not split work by generic frontend/backend ownership. Keep this lane organized around the customer-facing shop outcome.
- Do not make broad visual changes before checking variant validity and media completeness for the products being redesigned.

## Verification

Use the exact route or flow being changed. Do not rely on proxy checks.

Before shop edits:

- Review `locally-twisted-queue.md`, this file, `PROJECT-STATUS.md`, and `HANDOFF.md`.
- Re-run or refresh the relevant catalog truth check before seed, variant, or media changes.
- Run the mirror/product diff path from `MIRROR-REBUILD-PLAN.md` before layout overhaul work.

After route, template, CSS, or JS edits:

- `python scripts/verify/smoke_shop.py`
- `python scripts/verify/cart_checkout_contract.py`
- `python scripts/verify/variant_media_contract.py`
- `python scripts/verify/catalog_variant_contract.py`
- `python scripts/setup/sync_variant_media.py --dry-run --include-details --report output/catalog-media-review.json`
- `python scripts/verify/nav_ia.py`
- `npm run test:layout-fit`

For cache-sensitive Website Route or template changes:

- Clear ERPNext website cache using the local project script if available.
- Recheck the exact changed route in browser-sized desktop and mobile views.

For purchase-flow changes:

- Verify guest add-to-cart from product listing and configured product detail.
- Verify cart line items use purchasable variant codes where variants are required.
- Verify checkout can proceed without guest login redirect.
- Verify payment success still reaches `/thank-you` and does not break the documented invoice/email cascade.

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
