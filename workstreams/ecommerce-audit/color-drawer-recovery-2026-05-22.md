# Color Drawer Recovery - 2026-05-22

Status: local recovery verified and published as a scoped GitHub commit; broader overlapping local product/catalog edits were intentionally left out.

## What Guiding Light Reported

The product color system appeared to have lost the balloon colors Jeff provided and the legacy_source export preserved: grouped drawers by style/type, real owner-approved swatch images, and matching hex labels for business color matching.

## What Actually Broke

The color system was not deleted. The source-authority hardening added by product page architecture work required the runtime source catalog before treating a balloon-color-looking axis as a color recipe drawer.

Inside the running Frappe container, the old `_resources/catalog-source/catalog.json` lookup paths were absent, but the app-local staged seed artifact existed at:

`apps/locally_twisted/locally_twisted/seed/_data/catalog.json`

Because `product_options.py` did not look at that app-local staged path, quote-first products such as `classic-arch` fell back to a plain sale-unit select instead of the grouped color recipe drawer.

## Recovery Applied

- Added the app-local seed catalog paths to `product_options._source_catalog_paths()`.
- Kept source authority intact: color-looking ERPNext axes still need legacy_source/backend source evidence before becoming recipe drawers.
- Restored visible hex labels even when an owner-approved swatch image exists.
- Added missing approximate hex entries for active classic-arch color values that had owner swatches but no local hex fallback.
- Strengthened the quote-first browser verifier so `classic-arch` must render as a color recipe drawer with grouped swatches and hex labels.

## Verified Locally

- `python -m py_compile apps\locally_twisted\locally_twisted\product_options.py apps\locally_twisted\locally_twisted\catalog_contract\color_rules.py`
- `python scripts\dev\clear_website_cache.py`
- `python scripts\verify\color_swatch_contract.py`
- `node_modules\.bin\playwright.cmd test scripts\verify\product_quote_first_experience.spec.js --reporter=line --workers=1`
- `node_modules\.bin\playwright.cmd test scripts\verify\product_options_experience.spec.js --reporter=line --workers=1`

Current browser proof on `shop-items/arches/classic-arch`:

- `latex colors` target: `color_recipes`
- display type: `color-drawer`
- drawers: 8
- active rendered color swatch images: 51
- active rendered hex labels: 51

The source swatch contract still maps the legacy_source/owner color asset set and reports 53 unique source assets. The rendered page currently shows 51 active normalized values because duplicate-case source values collapse in ERPNext.

## Separate Blocker

`python scripts\verify\product_page_architecture_contract.py` still fails on a stale published Website Item count expectation: expected 53, found 51. Its payload-target evidence confirms the recovered color recipe path is present; the count mismatch needs a separate catalog/count gate update or source reconciliation pass.
