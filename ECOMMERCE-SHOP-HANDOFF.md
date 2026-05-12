# Ecommerce Shop Handoff

## Current Repository State

- Branch: `main`
- HEAD / `origin/main`: `e4186c1 Hide homepage custom decor block`
- Recent relevant commits:
  - `e4186c1` Hide homepage custom decor block
  - `84ba8be` Archive current launch worktree state
  - `32e9098` Add landing page event photos
  - `c0a77f9` harden ready-to-order nav search gates
  - `5b11041` treat protected add-ons as import-ready
  - `6ff9e50` add ecommerce finished experience roadmap
  - `c67f6fb` prove color recipe checkout path
  - `3bcf67e` expand checkout product family parity proof
  - `5ee4c3c` harden catalog reimport safety gates
  - `019bf27` gate unclassified product media rendering
  - `b02a0c4` guard generic checkout mapper contract
  - `cb05559` enforce generic multi-color checkout contract

## Scope Correction

The immediate work should stay on the ERPNext ecommerce shop architecture and code/data wiring:

- Catalog import safety and source trace
- Website Items, Items, variants, disabled add-on variants, Item Prices
- Product pattern contracts and resolver behavior
- Multi-color configuration payloads
- Add-on validation, pricing, cart lines, Sales Order lines, Sales Invoice lines
- Quote-first fallback for products not approved for checkout
- Ready-to-Order nav/search driven by backend eligibility
- Media role semantics and held source media

Do not spend the main workstream on broad Playwright/browser sweeps. Browser checks should be final confirmation only after code/backend gates are green.

## Verified Backend Status

`erpnext-backend-specialist` completed task `f82b8ef1` on `main` at `e4186c1`. They reported no backend edits needed.

Passed backend/verifier commands:

- `python scripts\verify\product_pattern_contract.py`
  - 53 source products
  - 18 explicit/direct checkout products
  - 35 quote-first supported products
  - `inventory_ok=True`
  - `checkout_gate_ok=True`
  - no checkout blockers
- `python scripts\verify\product_pattern_contract_report.py`
  - 53 published/priced Website Items
  - checkout statuses: `checkout_ready=18`, `lane_mapping_only=25`, `needs_add_on_pricing=9`, `needs_customization_payload=1`
  - fail-loud states: `review_only_add_on=9`, `unsupported_customization_payload=5`
- `python scripts\verify\cart_checkout_contract.py`
- `python scripts\verify\product_page_runtime_contract.py` with rollback
- `python scripts\verify\checkout_product_family_contract.py` with rollback
- `python scripts\verify\product_add_on_dependency_contract.py`
- `python scripts\verify\checkout_fulfillment_contract.py` with rollback
- `python scripts\verify\checkout_lead_conversion_contract.py` with rollback
- `python scripts\verify\product_quote_customization_contract.py` with rollback
- `python scripts\verify\product_quote_acceptance_contract.py` with rollback
- `python scripts\verify\product_quote_operator_review_contract.py`
- `python scripts\verify\product_quote_customer_delivery_contract.py` with rollback
- `python scripts\verify\product_quote_operator_send_control_contract.py` with rollback
- `python scripts\verify\customer_note_checkout_preservation_contract.py` with rollback

Interpretation: the backend checkout/order/quote wiring currently appears green. Next work should not re-run these endlessly unless a dependent file changes.

## Catalog / Import Status

Last successful catalog/import commands from this session:

- `python scripts\verify\catalog_state_snapshot_contract.py` PASS
- `python scripts\verify\catalog_purge_scope_dry_run.py` PASS
  - included products: 48
  - excluded products: 5
  - templates: 48
  - variants: 6894
  - prices: 6928
- `python scripts\verify\product_import_readiness_gate.py` PASS
  - 12 pass, 0 warning, 0 blocker
  - destructive import allowed by that gate
- `python scripts\verify\v1_odoo_erpnext_import_manifest.py` PASS
  - included: 48
  - excluded: 5
  - sale units: 225
  - price review units: 0
  - extra images held: 66
- `python scripts\verify\product_import_source_trace_contract.py` PASS
- `python scripts\verify\post_import_catalog_state_contract.py` PASS
- `python scripts\verify\product_page_architecture_readiness.py` PASS
  - 14 pass, 0 blocked
  - finance/bank/payment remains deferred

## Active Blocker / Conflict To Resolve

`python scripts\verify\product_page_contract_source_audit.py` last returned BLOCKED:

```text
{'color_axis_customization': 25, 'missing_resolver_prices': 49, 'unclassified_gallery_images': 49, 'axis_needs_review': 9}
```

This is the key unresolved contract conflict. Other newer gates treat these lanes as handled by live ERPNext price snapshots, held media roles, quote-first fallback, and add-on approval packets. This older source audit still treats them as destructive import blockers.

Next owner must resolve this directly, not sidestep it:

- If this audit is meant to be a destructive source import gate, then source enrichment must be completed so resolver prices, media roles, color customization semantics, and add-on review states are represented in the source-side artifact.
- If this audit is meant to be a readiness inventory report, update its schema and exit behavior to distinguish:
  - `source_inventory_ok`
  - `checkout_gate_ok`
  - `destructive_import_gate_ok`
  - intentional holds such as `ignored_artifact`, `quote_only_until_approved`, and `live_erpnext_snapshot`
- It should not contradict `product_import_readiness_gate.py`, `product_page_price_enrichment_contract.py`, `product_page_media_visibility_contract.py`, and the ProductPatternContract gates.

This is code/backend verifier architecture work, not browser work.

## Storefront / Navigation Status

Targeted storefront checks reported green before the scope correction:

- `python scripts\verify\smoke_shop.py` PASS
  - Ready-to-Order menu linked backend-approved checkout products
  - mobile drawer included `Shop All`
  - Unicorn Bouquet MED/LAR item code and price resolved
  - product media stayed nonblank
- `python scripts\verify\nav_ia.py` PASS
- `npm run test:search-contract` PASS using the repo wrapper

Do not expand this into broad browser work until code/backend blockers are resolved.

## Media Status

Known current model:

- Source extra images are held as `ignored_artifact` unless classified as `gallery`, `variant_image`, or `reference`.
- Primary images exist for live product pages.
- Variant media stays gated until classification is explicit.

Last reported green media commands:

- `python scripts\verify\product_page_media_visibility_contract.py` PASS
  - 95 held-back ignored artifacts
  - 0 unclassified source images under the newer media role contract
  - 53 Website Items with live images
  - 0 Website Slideshow records, matching 0 approved gallery images
- `python scripts\verify\variant_media_contract.py` PASS
- `python scripts\verify\product_page_media_classification_packet.py` PASS

This ties back to the source audit conflict above: source media is intentionally held, but the older audit still reports `unclassified_gallery_images`.

## Current Dirty Worktree

`git status --short --branch` shows `main...origin/main` aligned, with local dirty files:

- `apps/locally_twisted/locally_twisted/api/variant_media.py`
- `apps/locally_twisted/locally_twisted/catalog_contract/media_classification.py`
- `apps/locally_twisted/locally_twisted/catalog_contract/media_visibility.py`
- `apps/locally_twisted/locally_twisted/catalog_contract/models.py`
- `apps/locally_twisted/locally_twisted/catalog_contract/product_pattern_contract.py`
- `apps/locally_twisted/locally_twisted/catalog_contract/source_builder.py`
- `apps/locally_twisted/locally_twisted/www/home.html`
- `apps/locally_twisted/locally_twisted/www/home.py`
- `audits/odoo-erpnext-migration-audit-2026-05-08/15-product-page-contract-source-audit.md`
- `audits/odoo-erpnext-migration-audit-2026-05-08/16-catalog-purge-scope-dry-run.json`
- `audits/odoo-erpnext-migration-audit-2026-05-08/16-catalog-purge-scope-dry-run.md`
- `audits/odoo-erpnext-migration-audit-2026-05-08/25-v1-odoo-erpnext-import-manifest.json`
- `audits/odoo-erpnext-migration-audit-2026-05-08/25-v1-odoo-erpnext-import-manifest.md`
- `scripts/verify/product_page_media_classification_packet.py`
- `scripts/verify/variant_media_contract.py`

`git diff --stat` reported 13 changed files with 151 insertions and 55 deletions. The audit/report files were regenerated by verifier runs. Do not broad-stage. Use scoped staging only.

## Active Team Work At Handoff

Backend lane:

- `f82b8ef1` completed by `erpnext-backend-specialist`; no backend gap found.

Still active/pending lanes:

- `4da4b135` assigned to `catalog-purge-import-executor`: catalog/pricing/import setup.
- `3132de36` assigned to `ecommerce-webshop-builder`: storefront implementation, nav/search/product UX.
- `d2653ce8` assigned to `media-classification-sprinter`: media readiness and image-role architecture.
- `4ca40e2d` assigned to `overnight-verification-sweeper`: final synthesis after implementation lanes report.

The browser-runner task was explicitly de-prioritized.

## Recommended Next Action

1. Stop broad browser testing.
2. Resolve `product_page_contract_source_audit.py` so it matches the current ERPNext ecommerce architecture.
3. Decide whether the dirty media/source-builder/model changes are intended and publishable.
4. If publishable, stage only the scoped files after reviewing `git diff`.
5. Rerun the non-browser code/backend gates that correspond to changed files:
   - `python -m py_compile ...` for touched Python files
   - `python scripts\verify\product_page_contract_source_audit.py`
   - `python scripts\verify\product_import_readiness_gate.py`
   - `python scripts\verify\product_page_media_visibility_contract.py`
   - `python scripts\verify\product_page_media_classification_packet.py`
   - `python scripts\verify\variant_media_contract.py`
   - `python scripts\verify\product_pattern_contract.py`
   - `python scripts\verify\product_pattern_contract_report.py`
6. Only after the code/backend gates are coherent, run targeted storefront/browser confirmation.

## Do Not Lose

- Multi-color selection is mandatory. Do not allow a single-select color shortcut to make a product checkout-ready.
- ProductPatternContract/backend resolver is the source of checkout eligibility.
- Quote-first is a valid safe lane, not a failure, when paid checkout semantics are not approved.
- Add-ons must preserve item, price, quantity/value limits, and SO/SI line detail before checkout-ready status.
- Source media cannot silently render as gallery/variant media until classified.
- Do not commit broad dirty audit artifacts or unrelated local changes.
