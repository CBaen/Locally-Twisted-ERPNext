# Ecommerce Shop Handoff

Status as of 2026-05-18 for peer GPT-5.5 Codex/OpenClaw agents.

## Current Repository State

- Branch: `main`
- Published closeout baseline before complex-scaffold work: `1811cd6 Fix ecommerce closeout doc state`; verify current `HEAD` / `origin/main` with `git status -sb` before editing.
- This file is the front-door handoff for the local ecommerce shop setup and
  staff product-authoring slices.
- Current local product import proof treats all 53 Odoo-imported products as
  sellable checkout targets. Do not promote that proof to public/live without
  GL local approval plus the separate Frappe Cloud, Stripe, DNS, webhook, and
  live payment cutover gates.
- Encanto/simple checkout variant media was repaired after GL caught the
  product page keeping the parent image. Simple `simple_product|checkout`
  variant `Item.image` now renders and cascades; complex/unclassified media
  remains held.
- `Add Foil Number` is confirmed as an add-on, not a required SKU axis. The
  local DB repair disabled 390 stale optional-add-on variants, and
  `seed_catalog.py` now runs that idempotent cleanup after destructive import.
- Current local runtime note: `frontend` has `lt_ecommerce_paused=0` so GL can
  test localhost product/cart behavior. Restore it to `1` after local
  acceptance or before release-packet work.
- `lt_ecommerce_paused=1` is a public/live exposure safety lock, not a reason
  to stop local build/test work. Name the actual blocker when ecommerce work is
  incomplete.

## Completed Lanes

### Catalog optional add-on variant guard - 2026-05-18

Owner: `Codex`

Result: complete locally. No staging/live site update, Frappe Cloud update,
DNS change, Stripe live change, or public exposure change was made.

Feature handoff:

- `workstreams/ecommerce-audit/catalog-optional-addon-variant-guard-2026-05-18.md`

Evidence summary: `catalog_variant_contract.py` caught 13 bouquet templates
with 30 stale enabled `Add Foil Number` variants each. The existing
`repair_optional_addon_variants` routine was run against local `frontend`,
which disabled 390 stale optional-add-on variants and left the 39 required
Bouquet Size variants enabled. `seed_catalog.py` now runs that cleanup after
destructive import so a future import rerun does not rely on a manual memory
step. Product Setup/readiness labels now use `Configurable product page`; the
old `Custom quote page` label remains accepted as a legacy safe alias.

Green gates:

- `bench --site frontend migrate`
- `python scripts\verify\catalog_variant_contract.py`
- `python scripts\verify\product_page_architecture_readiness.py --json`
- `python scripts\verify\product_import_readiness_gate.py --report output\product-import-readiness-gate.json`
- `python scripts\verify\product_blueprint_contract.py`
- `bench --site frontend execute locally_twisted.verify.product_blueprint_contract.run`
- `python scripts\verify\cart_checkout_contract.py`
- `python scripts\verify\variant_media_contract.py`
- `python scripts\verify\checkout_product_family_contract.py`
- `python scripts\verify\product_add_on_dependency_contract.py`
- `python scripts\verify\product_page_runtime_contract.py`

### Variant item media restore - 2026-05-17

Owner: `Codex`

Result: complete locally. No staging/live site update, Frappe Cloud update,
DNS change, Stripe live change, or public exposure change was made.

Feature handoff:

- `workstreams/ecommerce-audit/variant-item-media-restore-2026-05-17.md`

Evidence summary: Encanto Bouquet size variants already had backend
`Item.image` values, but the media API held them because the source extra-image
hold gate had been applied too broadly. Source now routes selected media
through `product_variant_media.py`: Product Setup media wins first, simple
checkout variant `Item.image` is approved selected media, and complex raw Item
media stays held unless Product Setup approves it. Cart, Sales Order payload,
and receipt helpers share the same selected-media path.

Green gates:

- `python -m py_compile apps\locally_twisted\locally_twisted\product_variant_media.py apps\locally_twisted\locally_twisted\api\variant_media.py apps\locally_twisted\locally_twisted\api\cart.py apps\locally_twisted\locally_twisted\product_page_runtime.py scripts\verify\variant_media_contract.py`
- `python scripts\verify\variant_media_contract.py`
- `python scripts\verify\cart_checkout_contract.py`
- `python scripts\verify\product_page_runtime_contract.py`

### All-Odoo sellable product reimport - 2026-05-17

Owner: `Codex`

Result: complete locally. No staging/live site update, Frappe Cloud update,
DNS change, Stripe live change, or public exposure change was made.

Feature handoff:

- `workstreams/ecommerce-audit/odoo-sellable-product-reimport-2026-05-17.md`

Evidence summary: GL corrected the product model: every Odoo-imported product
is a product. The local `frontend` site was backed up, cleaned of two generated
proof products, snapshotted, and reimported with 53 included products, 0
exclusions, and 290 priced sale units. Price enrichment now feeds
`seed_catalog.py`, preventing bouquet-size variants from flattening to the page
base price. Product-level Website Item contracts now outrank stale
item-group/category fallback in product pages, shop cards, and cart display
rows. Browser proof passed all 53 live Website Item routes in two batches under
the 50-line cart cap at desktop and mobile widths, including cart and checkout
preview. `lt_ecommerce_paused=1` was restored and verified.

Green gates:

- `python scripts\verify\product_import_readiness_gate.py --report output\product-import-readiness-gate.json`
- `python scripts\verify\v1_odoo_erpnext_import_manifest.py`
- `python scripts\verify\catalog_purge_scope_dry_run.py`
- `python scripts\verify\product_source_repair_map.py`
- `python scripts\verify\complex_checkout_scaffold.py`
- `python scripts\verify\product_pattern_contract_report.py`
- `python scripts\verify\product_page_architecture_contract.py`
- `python scripts\verify\product_page_runtime_contract.py`
- `python scripts\verify\cart_checkout_contract.py`
- `python scripts\verify\product_variant_price_contract.py`
- `node scripts\verify\post_import_checkout_proof.js` with all-53 manifest/snapshot batch proof
- `python scripts\verify\ecommerce_pause_contract.py`

Remaining local product-data caveats: 95 source extra/gallery images remain
held until classified; 9 review-only add-on controls remain hidden until
mapped. Simple checkout variant `Item.image` is no longer part of that hold.

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

Evidence summary after the 2026-05-17 reimport: 53 published/priced Website
Items are checkout-ready at the product-page architecture layer. ProductPatternContract,
selected config, cart line keys, fail-loud checkout blocks, add-on Sales
Order/Sales Invoice line preservation, checkout lead conversion, quote
fallback, and customer note preservation are green.

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
- 29 Item Attributes
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

Evidence summary: 49 products / 95 source extra images are explicitly held as
`ignored_artifact` / `hold_back`; `unsafe_unclassified_images=0`. The
2026-05-17 regression repair clarified that this hold does not cover already
mapped simple checkout variant `Item.image` values; those are selected product
media and are guarded by `variant_media_contract.py`. No source extra-image
readiness blocker remains.

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

### Complex checkout scaffold - 2026-05-12

Owner: `Codex`

Result: complete as local/source scaffolding only. No live site update, Frappe
Cloud update, DNS change, Stripe change, or Website Item lane flip was made.

Files added:

- `apps/locally_twisted/locally_twisted/catalog_contract/complex_checkout_scaffold.py`
- `scripts/verify/complex_checkout_scaffold.py`
- `scripts/verify/complex_checkout_scaffold_contract.py`
- `workstreams/ecommerce-audit/complex-checkout-scaffold-2026-05-12.md`

Green gates:

- `python -m py_compile apps\locally_twisted\locally_twisted\catalog_contract\complex_checkout_scaffold.py scripts\verify\complex_checkout_scaffold.py scripts\verify\complex_checkout_scaffold_contract.py`
- `python scripts\verify\complex_checkout_scaffold_contract.py`
- `python scripts\verify\complex_checkout_scaffold.py`

Evidence summary after the 2026-05-17 reimport: 53 products checked; 53 direct
checkout regression guards; 0 simple lane-flip candidates; 0 complex UI
blockers; 0 add-on or conditional product blockers; 0 needs-review/missing
products; 0 explicit checkout architecture gaps. Generated evidence lives
under ignored `output/complex-checkout-scaffold.*` and can be regenerated.

### Backend product-page architecture contract - 2026-05-12

Owner: `Codex`

Result: complete as source/local architecture. This is the corrected
architecture layer; the complex scaffold is only downstream planning evidence.
Post-review hardening is pushed in `88a708c Harden product page axis
projection`.

Files added/changed:

- `apps/locally_twisted/locally_twisted/catalog_contract/axis_projection.py`
- `apps/locally_twisted/locally_twisted/catalog_contract/product_page_architecture_contract.py`
- `apps/locally_twisted/locally_twisted/catalog_contract/product_pattern_contract.py`
- `apps/locally_twisted/locally_twisted/verify/product_page_architecture_contract.py`
- `apps/locally_twisted/locally_twisted/product_options.py`
- `apps/locally_twisted/locally_twisted/templates/generators/item/item_configure.html`
- `apps/locally_twisted/locally_twisted/templates/generators/item/item_quote_first.html`
- `apps/locally_twisted/locally_twisted/templates/generators/item/item_details.html`
- `scripts/verify/product_page_architecture_contract.py`
- `scripts/verify/product_page_architecture_contract_contract.py`
- `scripts/verify/product_page_architecture_readiness.py`
- `scripts/verify/product_quote_first_experience.spec.js`
- `workstreams/ecommerce-audit/backend-product-page-architecture-contract-2026-05-12.md`

Green gates:

- `python scripts/verify/product_page_architecture_contract_contract.py`
- `python scripts/verify/product_page_architecture_contract.py`
- `python scripts/verify/product_page_runtime_contract.py`
- `docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.verify.direct_checkout_target_contract.run`
- `npm run test:product-quote-first`
- `npm run test:form-experience`
- `python scripts/verify/ecommerce_pause_contract.py`

Expected gated result:

- `python scripts/verify/product_page_architecture_readiness.py --report output/product-page-architecture-readiness.json`
  reports `technical_architecture_ok: True` and `import_reopen_ok: False`
  because the public/live exposure safety lock is on. That lock does not block
  local ecommerce implementation work.

Evidence summary after the 2026-05-17 reimport: 53 product rows are mapped
through the generic receiving architecture and all 53 are checkout allowed.
There are no business quote-first product categories; legacy `quote_first`
values are internal holds only where field names remain. Payload targets are
`selected_options`, `color_recipes`, `add_ons`, and `quote_context`;
product-specific rules are explicitly not allowed.

Post-review axis rule: live ERPNext variant axes are not classified by
attribute name alone. Source/backend recipe patterns keep color axes in
`color_recipes`; missing recipe authority keeps the axis as sale-unit
`selected_options`; explicit single-color sale-unit source markers override
recipe-looking patterns. The browser regression proves `7-butterfly-column`
emits `latex colors -> color_recipes` and preserves the selected color in the
cart payload without leaking it into `selected_options`.

### Product blueprint authoring - 2026-05-14

Owner: `Codex`

Result: complete as a local-only staff product-authoring and unpublished apply
slice. No live site update, Frappe Cloud update, DNS change, Stripe change,
public publish, order, invoice, or Payment Request was made.

Files added/changed:

- `apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_product_blueprint/`
- `apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_product_blueprint_option/`
- `apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_product_blueprint_color_recipe/`
- `apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_product_blueprint_add_on/`
- `apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_product_blueprint_conditional_price/`
- `apps/locally_twisted/locally_twisted/product_blueprint_validation.py`
- `apps/locally_twisted/locally_twisted/product_blueprint_apply_plan.py`
- `apps/locally_twisted/locally_twisted/product_blueprint_local_apply.py`
- `apps/locally_twisted/locally_twisted/product_page_runtime.py`
- `apps/locally_twisted/locally_twisted/product_options.py`
- `apps/locally_twisted/locally_twisted/verify/product_blueprint_contract.py`
- `scripts/verify/product_blueprint_contract.py`
- `scripts/verify/product_blueprint_live_contract.py`
- `workstreams/ecommerce-audit/product-blueprint-authoring-2026-05-14.md`

Green gates:

- `python scripts/verify/product_blueprint_contract.py`
- `python scripts/verify/product_blueprint_live_contract.py`
- `python scripts/verify/product_page_runtime_contract.py`
- `python scripts/verify/product_add_on_dependency_contract.py`
- `python scripts/verify/product_page_architecture_contract_contract.py`
- `python scripts/verify/ecommerce_pause_contract.py`
- `python scripts/verify/verifier_cli_contract.py`

Evidence summary: `LT Product Blueprint` is installed with child tables for
options, color recipes, add-ons, and conditional pricing. Validation maps
employee labels to `simple_product`, `complex_custom_product`, `checkout`,
`quote_first`, `needs_review`, `selected_options`, `color_recipes`, `add_ons`,
and `quote_context`. The dry-run apply plan writes no product records. Desk
apply is role-gated, local-site-config-gated, server-token-gated, and keeps the
generated Website Item unpublished. The rollback-safe verifier proves a
temporary direct-checkout blueprint creates one template Item, two variants,
one Item Attribute, two Item Prices, one unpublished Website Item, zero
orders/invoices/payments, and one checkout-approved fixed-price blueprint add-on
that appears in product options and fails loudly above its quantity max.

## Current Working Position

- Backend ecommerce architecture is green.
- Catalog/import/pricing local setup is green.
- Media readiness is green.
- Storefront product UX/nav/search/homepage verifier alignment is green.
- Runner wrapper is green.
- Complex checkout scaffold is green for local planning and blocks stale
  heuristic lane-flip lists from being used as checkout approval.
- Backend product-page architecture contract is green and emitted to product
  pages as a backend-owned JSON contract.
- Staff product blueprint authoring is green for validation, dry-run preview,
  guarded unpublished local apply, and fixed-price add-on runtime cascade.
- First simple repair-lane backend proof is green: `large-head-missionary`,
  `mothers-day-front-yard-7-column`, `easter-arch`, and `pride-arch` preserve
  source-backed prices and 33 sale SKU lines through Sales Order and Sales
  Invoice in rollback. Local open-mode browser proof is also green at desktop
  and mobile widths for product pages, cart, and checkout preview. Payment
  cascade proof is green for all 33 sale lines through Payment Request, Payment
  Entry, Sales Invoice, receipt email, operator email, welcome email, and
  rollback cleanup. Final owner/product approval and live exposure are still
  pending for that tranche.
- First multi-color repair-lane backend proof is green:
  `7-epic-column`, `baby-shower-combination-photo-opt`, `baby-table-decor`,
  `classic-organic-for-easel`, `number-balloon-columns`, and
  `sleepy-baby-column` preserve source-backed prices and 563 enabled color SKU
  lines through checkout, `color_recipes`, Sales Order, and Sales Invoice in
  rollback. Local open-mode browser proof is also green at desktop and mobile
  widths for product pages, visible color drawers, cart, and checkout preview.
  Payment/customer-message cascade, media update behavior, final owner/product
  approval, and live exposure are still pending for that tranche.
- The shared worktree may still show regenerated audit artifacts under `audits/odoo-erpnext-migration-audit-2026-05-08/`; do not broad-stage them without reviewing the producing lane.

## Remaining Launch Gates

These are not current local ecommerce architecture blockers:

- Frappe Cloud staging deployment and source-freeze review.
- Cloudflare/DNS cutover approval and verification.
- Live Stripe/site-config/webhook setup.
- Legal/policy copy approval where needed.
- One intentional low-risk live payment test after explicit owner approval.
- Final real catalog approval if the visible local product set is being treated as public launch catalog truth rather than architecture/import proof.
- Browser proof of applied blueprint products, richer self-service complex
  authoring UI, conditional pricing runtime, media assignment, broader add-on
  mapping, and refreshed import safety evidence before any product release.

## Do Not Regress

- `quote_first` is a legacy internal hold state, not a business product
  category or permanent product blocker.
- Direct checkout must still be backend-truth driven by Website Item fields, ProductPatternContract, resolver behavior, selected config, item code, price, media, add-ons, cart line key, checkout summary, and SO/SI preserved fields.
- `needs_review` and partial/blank Website Item classification must fail closed.
- Add-ons require explicit mapping, price, quantity/value limits, and SO/SI line preservation before checkout.
- Use the source repair map and complex-checkout scaffold before moving any
  held product into checkout.
  Current source-backed simple-axis candidates are only `large-head-missionary`,
  `mothers-day-front-yard-7-column`, `easter-arch`, and `pride-arch`; their
  backend SO/SI rehearsal and local browser cart/checkout preview are proven,
  and payment/customer-message proof is complete. Do not expose them to
  customers until final owner/product approval is explicit.
- Current source-backed multi-color candidates are only `7-epic-column`,
  `baby-shower-combination-photo-opt`, `baby-table-decor`,
  `classic-organic-for-easel`, `number-balloon-columns`, and
  `sleepy-baby-column`; their backend checkout/SO/SI rehearsal is proven. Do
  not expose them to customers until payment/customer-message, media behavior,
  and final owner/product approval gates pass.
- Product-page controls must be driven by the generic architecture contract,
  not by product-name branches or frontend-only checkout eligibility.
- Color-axis payload targets must come from source/backend semantics, not from
  attribute-name heuristics.
- Staff product creation must stay in `LT Product Blueprint` and its verifiers,
  not developer-only source packets, when the requirement is employee
  self-service authoring.
- Held media must not render as gallery/variant media until classified.
- Use scoped staging only; do not commit regenerated audit artifacts or unrelated changed files.
