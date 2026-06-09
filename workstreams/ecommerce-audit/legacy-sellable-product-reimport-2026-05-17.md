# legacy_source Sellable Product Reimport - 2026-05-17

## Purpose

Closeout handoff for the local-only correction that treats every
legacy_source-imported Locally Twisted product as a sellable product target.

This is not a live-release approval. Local ecommerce was temporarily opened
only for proof and then restored to `lt_ecommerce_paused=1`.

## Owner Correction

GL corrected the model: every product imported from legacy_source is a product. There
are no business "quote-first products." If product detail or pricing is unclear,
repair or repull the legacy_source source/import path instead of preserving a
non-purchasable product category.

Legacy `quote_first` wording may still exist where it names a stored field or
older verifier branch, but peer agents should read it as an internal safety
hold only. It is not a business lane.

## Local Data Actions

- Cleaned two local-only proof products before reimport:
  `owner-blueprint-smoke-20260517-101250` and
  `release-proof-complex-product-1779036020`.
- Created clean local snapshot:
  `audits/catalog-import-audit-2026-05-08/current-state-snapshot-2026-05-17-2132-clean-legacy_source-products/`.
- Took fresh local Frappe backups before destructive local reimport:
  `20260517_153250-frontend-database.sql.gz` and
  `20260517_160858-frontend-database.sql.gz`.
- Reimported the local `frontend` site with 53 included products, 0 excluded
  products, and 290 priced sale units.
- Repaired flattened bouquet-size prices by staging
  `21-product-page-price-enrichment-candidates.json` into the seed data path
  and making `seed_catalog.py` prefer approved sale-unit enrichment before
  scraped page-level fallback prices.
- Follow-up 2026-05-19: GL caught that this was still too narrow. Easter Bunny
  Ear Arch `20ft` and `25ft` still shared the same local price even though legacy_source
  charged `$375` and `$440`. Treat the reimport proof's price claims as
  superseded by the price-identity incident lane:
  `workstreams/ecommerce-price-identity-incident-review-2026-05-19.md`.
- Follow-up 2026-05-18: disabled the 390 stale `Add Foil Number` optional
  add-on variants that were still enabled from older imports, then wired the
  same idempotent cleanup into `seed_catalog.py` so future destructive import
  runs do not leave optional add-ons as required SKU axes.
- Follow-up 2026-05-18: added a school/seasonal color-preset guard. The
  imported products remain real products, but direct checkout now requires a
  bounded sale unit. Graduation Grab n Go and 6' Graduation stands use college
  preset checkout variants; hyperspecialized 50+ raw-color products route to
  quote request until GL approves their UI/UX, pricing, color logic, and
  operator flow.

## Code Changes

- `catalog_contract/source_builder.py`: `simple_product` and
  `complex_custom_product` resolve to checkout; only `needs_review` stays out.
- `product_page_runtime.py`: explicit `complex_custom_product|checkout` is
  valid runtime state.
- `product_page_labels.py`: operator labels now frame complex pages as
  configurable product pages and `quote_first` as an internal hold.
- `catalog_import_subset.py`: no owner-excluded legacy_source product slugs.
- `seed/seed_catalog.py` and `scripts/setup/stage_seed_data.py`: stage and use
  price enrichment for sale-unit prices during import; `seed_catalog.py` now
  also runs the optional-add-on variant repair and school/seasonal color-preset
  repair after destructive import.
- `catalog_contract/*` and `scripts/verify/*`: all import/readiness/product
  gates now expect 53 checkout products and 0 exclusions.
- `scripts/verify/post_import_checkout_proof.js`: default browser proof now
  loads included products from the V1 manifest, uses the clean Website Item
  snapshot as route authority, batches 53 products as 27/26 to respect the cart
  line cap, and fails loudly if run while the local ecommerce pause is on.
- Product page/shop/cart routing:
  `templates/generators/item/item_configure.html`,
  `templates/generators/item/item_add_to_cart.html`, `www/shop.py`, and
  `api/cart.py` use the Website Item product contract before legacy
  item-group/category lane fallback.
- Follow-up variant media repair:
  `product_variant_media.py`, `api/variant_media.py`, `api/cart.py`,
  `product_page_runtime.py`, and `scripts/verify/variant_media_contract.py`
  restore simple checkout variant `Item.image` rendering/cascade while keeping
  complex raw media held without Product Setup approval.

## Verification

Backend/source gates passed locally:

- `python scripts/verify/product_import_readiness_gate.py --report output/product-import-readiness-gate.json`
- `python scripts/verify/v1_legacy_source_erpnext_import_manifest.py`
- `python scripts/verify/catalog_purge_scope_dry_run.py`
- `python scripts/verify/product_source_repair_map.py`
- `python scripts/verify/complex_checkout_scaffold.py`
- `python scripts/verify/product_pattern_contract_report.py`
- `python scripts/verify/product_page_architecture_contract.py`
- `python scripts/verify/product_page_runtime_contract.py`
- `python scripts/verify/cart_checkout_contract.py`
- `python scripts/verify/product_variant_price_contract.py`
- `python scripts/verify/product_price_modifier_contract.py`
- `npm run test:product-price-display`
- `python scripts/verify/catalog_variant_contract.py`

Browser proof:

- `node scripts/verify/post_import_checkout_proof.js` passed for all 53 live
  Website Item routes at desktop and mobile widths in two batches per viewport:
  27 products and 26 products. The split is required because the cart API
  intentionally caps submitted cart lines at 50. The report recorded 106
  product proofs total.

Safety proof:

- `lt_ecommerce_paused` was restored to `1`.
- `python scripts/verify/ecommerce_pause_contract.py` passed after restore.

## Current State

- Published local Website Items: 53.
- legacy_source-imported product exclusions: 0.
- Import manifest sale units: 290.
- Import readiness blockers: 0.
- Product-page architecture: all 53 imported rows remain products, but checkout
  is now gated by product safety. Graduation preset products are checkout;
  hyperspecialized raw-color products are quote request until reviewed.
- Product pattern report from the all-sellable reimport is superseded for the
  school/seasonal color slice by
  `school-seasonal-color-preset-product-logic-2026-05-18.md`.
- Extra images remain held until classified: 95.
- Simple checkout variant Item images are approved selected media and are not
  part of the extra-image hold.
- `Add Foil Number` variants and old graduation raw-color variants are disabled
  legacy history, not active sale units. Active catalog variants are now
  10,186; all variant records are 10,629 including disabled legacy variants.
- Review-only add-on controls remain hidden until mapped: 9.
- 2026-05-19 price identity correction: local active variant prices are now
  guarded by `npm run test:product-prices` plus
  `npm run test:product-price-display`, but no staging/live approval follows
  from this local evidence.

## Boundaries

- No staging or live Frappe Cloud update was run.
- No Cloudflare/DNS/Stripe live change was run.
- This commit may be pushed to GitHub as source/archive, but it must not be
  promoted to live until GL tests locally and explicitly approves the live
  release path.
- Any future live promotion must compare old live app hash to target app mirror
  commit and run the Frappe Cloud site update plus live route/form/ecommerce
  proof chain.

## Next Safe Step

GL tests the local storefront/product/cart/checkout behavior. After approval,
prepare a separate staging/live release packet from the accepted commit with the
normal Frappe Cloud, Stripe, DNS, ecommerce exposure gates, and 2026-05-19
source-price identity guards.

Related follow-up handoff:
`workstreams/ecommerce-audit/variant-item-media-restore-2026-05-17.md`.

Related follow-up guard:
`workstreams/ecommerce-audit/catalog-optional-addon-variant-guard-2026-05-18.md`.

Related school/seasonal follow-up:
`workstreams/ecommerce-audit/school-seasonal-color-preset-product-logic-2026-05-18.md`.
