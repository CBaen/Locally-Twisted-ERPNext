# Ecommerce Shop Handoff

Status as of 2026-05-12 for peer GPT-5.5 Codex/OpenClaw agents.

## Current Repository State

- Branch: `main`
- HEAD / `origin/main`: `ab46734 Update ecommerce closeout references`
- This file is the front-door handoff for the finished local ecommerce shop setup slice.
- Do not treat current product names/counts/photos as final public catalog approval unless a later real-catalog approval gate says so. The local ERPNext catalog/import/backend architecture is ready; live Frappe Cloud, Stripe, DNS, webhook, and real payment cutover remain separate gates.

## Completed Lanes

### Backend checkout/order wiring - `f82b8ef1`

Owner: `erpnext-backend-specialist`

Result: complete on `main` at `e4186c1`; no backend edits were needed.

Green gates:

- `python scripts\verify\product_pattern_contract.py`
- `python scripts\verify\product_pattern_contract_report.py`
- `python scripts\verify\cart_checkout_contract.py`
- `python scripts\verify\product_page_runtime_contract.py`
- `python scripts\verify\checkout_product_family_contract.py`
- `python scripts\verify\product_add_on_dependency_contract.py`
- `python scripts\verify\checkout_fulfillment_contract.py`
- `python scripts\verify\checkout_lead_conversion_contract.py`
- `python scripts\verify\product_quote_customization_contract.py`
- `python scripts\verify\product_quote_acceptance_contract.py`
- `python scripts\verify\product_quote_operator_review_contract.py`
- `python scripts\verify\product_quote_customer_delivery_contract.py`
- `python scripts\verify\product_quote_operator_send_control_contract.py`
- `python scripts\verify\customer_note_checkout_preservation_contract.py`

Evidence summary: 53 published/priced Website Items; 18 checkout-ready; 25 lane-mapping-only; 9 add-on-pricing; 1 customization-payload. ProductPatternContract, selected config, cart line keys, fail-loud checkout blocks, add-on Sales Order/Sales Invoice line preservation, checkout lead conversion, quote fallback, and customer note preservation are green.

### Catalog/import and pricing - `4da4b135`

Owner: `catalog-purge-import-executor`

Result: complete. Commit pushed: `9a27b49 treat needs review lane as fail closed catalog state`.

Guarded data repair:

- `python scripts\verify\website_item_classification_contract.py --apply`
- Changed exactly 5 Website Item classification fields to `needs_review|needs_review`.

Current local ERPNext counts:

- 53 published Website Items
- 10,674 Items
- 49 templates
- 10,617 variants
- 10,227 active variants
- 390 disabled variants
- 10,656 Item Prices
- 26 Item Attributes
- 32,028 Item Variant Attribute rows

Result: no ERPNext catalog/pricing/import blocker remains for the local setup.

### Media readiness - `d2653ce8` and `d9543e5f`

Owners: `media-classification-sprinter`

Result: complete. Commit pushed: `8e4a95b38822d67300a3c66b17275acaf548e4ee` (`harden ecommerce media readiness contract`).

Files changed in that lane:

- `apps/locally_twisted/locally_twisted/api/variant_media.py`
- `apps/locally_twisted/locally_twisted/catalog_contract/media_classification.py`
- `apps/locally_twisted/locally_twisted/catalog_contract/media_visibility.py`
- `apps/locally_twisted/locally_twisted/catalog_contract/models.py`
- `apps/locally_twisted/locally_twisted/catalog_contract/product_pattern_contract.py`
- `apps/locally_twisted/locally_twisted/catalog_contract/source_builder.py`
- `scripts/verify/product_page_media_classification_packet.py`
- `scripts/verify/variant_media_contract.py`

Evidence summary: 49 products / 95 source extra images are explicitly held as `ignored_artifact` / `hold_back`; `unsafe_unclassified_images=0`; media visibility and variant media contracts pass. No media readiness blocker remains.

### Storefront/product UX and homepage contract - `3132de36`, `4fd5ae4f`

Owner: `ecommerce-webshop-builder`

Result: complete. Commit pushed: `3179463 Align homepage container contract with hidden decor`.

Change: `scripts/verify/layout_helpers.js` rebaselined the homepage container contract to the current committed design where `show_custom_event_decor=False`. This was verifier alignment, not an app behavior change.

Green gates:

- `python scripts/dev/clear_website_cache.py`
- focused container contract
- focused interactive-layout checks
- `python scripts\verify\nav_ia.py`
- `npm run test:search-contract`
- `python scripts\verify\smoke_shop.py`

Remaining broad layout-fit noise is transient ERPNext HTTP 417/502 during long sweeps; exact reruns passed and it is not a product behavior or runner primitive blocker.

### Storefront runner - `786f962e`

Result: complete in `e4186c1 Hide homepage custom decor block`.

Evidence: `run_playwright.cmd` uses Program Files Node and package scripts call the wrapper. Search contract, checkout experience, ecommerce browser proof, and focused interactive layout passed. Broad layout-fit showed 310/312 then exact rerun 2/2 pass; remaining issue is transient ERPNext HTTP behavior only.

### Odoo option-pattern mapper

Older mapper task `991323ce` was already published in `d0d5c41`. No docs work was done by `source-contract-sprinter` for `60a5e721`; this handoff replaces that missing closeout.

## Current Working Position

- Backend ecommerce architecture is green.
- Catalog/import/pricing local setup is green.
- Media readiness is green.
- Storefront product UX/nav/search/homepage verifier alignment is green.
- Runner wrapper is green.
- The shared worktree may still show regenerated audit artifacts under `audits/odoo-erpnext-migration-audit-2026-05-08/`; do not broad-stage them without reviewing the producing lane.

## Remaining Launch Gates

These are not current local ecommerce architecture blockers:

- Frappe Cloud staging deployment and source-freeze review.
- Cloudflare/DNS cutover approval and verification.
- Live Stripe/site-config/webhook setup.
- Legal/policy copy approval where needed.
- One intentional low-risk live payment test after explicit owner approval.
- Final real catalog approval if the visible local product set is being treated as public launch catalog truth rather than architecture/import proof.

## Do Not Regress

- `quote_first` is a lane/state, not a permanent product blocker.
- Direct checkout must still be backend-truth driven by Website Item fields, ProductPatternContract, resolver behavior, selected config, item code, price, media, add-ons, cart line key, checkout summary, and SO/SI preserved fields.
- `needs_review` and partial/blank Website Item classification must fail closed.
- Add-ons require explicit mapping, price, quantity/value limits, and SO/SI line preservation before checkout.
- Held media must not render as gallery/variant media until classified.
- Use scoped staging only; do not commit regenerated audit artifacts or unrelated dirty files.
