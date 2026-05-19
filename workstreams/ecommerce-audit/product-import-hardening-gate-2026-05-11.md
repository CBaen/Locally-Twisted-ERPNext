# Product Import Hardening Gate - 2026-05-11

## Purpose

This is the minimum gate before Locally Twisted runs a real ERPNext product catalog import, purge, or reupload rehearsal.

Current visible/imported product records are fixture product records for architecture proof. They are not real launch catalog truth.

## Peer Agent Operating Context

This handoff is written for peer GPT 5.5 agents working in the LT Frappe stack:

- Stack anchor: Frappe v15.106.0, ERPNext v15.105.0, Webshop, payments, and the custom `locally_twisted` app.
- App order matters: `locally_twisted` must stay last in `installed_apps` so hooks, fixtures, and template overrides win.
- Frappe Cloud target: Git-backed private bench deployment; repo changes must persist through hooks, fixtures, patches, and site config, not local Desk-only edits.
- Technical code/verifier choices route to Leader. Ask the user only for business-owner approvals such as destructive catalog purge/import, real catalog approval, live payment tests, secrets/account access, DNS cutover, or production customer-record mutation.
- Odoo CE 19 remains a read-only source witness for product meaning. If source mapping goes beyond the existing approved packets, route it to the Odoo-to-Frappe specialist instead of guessing.

## Gate Command

```powershell
python scripts/verify/product_import_readiness_gate.py --report output/product-import-readiness-gate.json
```

The verifier is read-only. It does not import, purge, upload, delete, or change ERPNext records.

Current local result is `PASS` with no warnings. That is evidence that the
local corrected V1 import gate is prepared for the guarded local path; it is not
approval for Frappe Cloud/live import, live Stripe, DNS cutover, or final real
catalog merchandising.

## Current Non-Destructive Import Runner Prep

`apps/locally_twisted/locally_twisted/seed/seed_catalog.py` now defaults to dry-run planning. Calling `execute()` without kwargs must not write ERPNext records. Destructive/write mode requires:

- `dry_run=False`
- `destructive=True`
- `backup_path`
- `snapshot_path`
- `purge_scope_report`

The dry-run plan excludes V1 products with color/customization axes, more than 50 source variant rows, cups products, quote-first products, and needs-review products. The owner specifically decided to skip 50+ color/high-variant products and cups; the source packet currently contains `easter-balloon-cups` / `Easter Balloon Cups` as the concrete cups exclusion. The dry-run manifest writes machine-readable `primary_exclusion_reason`, `excluded_reason_codes`, `excluded_reason_details`, `excluded_counts_by_primary_reason`, and `excluded_counts_by_reason`, writes the planned `lt_product_page_type` and `lt_commerce_lane` values from `build_product_page_contract`, and records that Sales Order/Sales Invoice line-level configuration fields are written by `locally_twisted.product_page_runtime`.

Next command sequence for peer GPT 5.5 agents:

```powershell
python scripts/setup/stage_seed_data.py
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.seed.seed_catalog.execute --kwargs "{'dry_run': True}"
python scripts/verify/product_import_readiness_gate.py
python scripts/verify/catalog_state_snapshot_contract.py
python scripts/verify/catalog_purge_scope_dry_run.py
# After source freeze, backup, snapshot, approval, and staging-only destructive approval:
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.seed.seed_catalog.execute --kwargs "{'dry_run': False, 'destructive': True, 'backup_path': '<bench-backup-name-or-path>', 'snapshot_path': '<fresh-snapshot-path>', 'purge_scope_report': '<purge-dry-run-report-path>'}"
```

## Required Backend Fields

A real catalog import runner must populate or preserve these ERPNext authority fields:

- `Website Item.lt_product_page_type`
- `Website Item.lt_commerce_lane`
- `Sales Order Item.custom_lt_product_template_item`
- `Sales Order Item.custom_lt_product_page_type`
- `Sales Order Item.custom_lt_configuration_version`
- `Sales Order Item.custom_lt_configuration_summary`
- `Sales Order Item.custom_lt_configuration_json`
- `Sales Invoice Item.custom_lt_product_template_item`
- `Sales Invoice Item.custom_lt_product_page_type`
- `Sales Invoice Item.custom_lt_configuration_version`
- `Sales Invoice Item.custom_lt_configuration_summary`
- `Sales Invoice Item.custom_lt_configuration_json`

The import must derive Website Item page template and buying path from the source contract, not from product names, visible cards, or frontend labels.

## Required Source/Approval Inputs

Before destructive import is allowed, the gate requires:

- `_resources/odoo-live/catalog.json`
- `_resources/odoo-live/slug_to_group.json`
- `_resources/odoo-live/value_normalize_map.json`
- `_resources/odoo-live/images/`
- `15-product-page-contract-source-audit.json`
- `21-product-page-price-enrichment-candidates.json`
- `22-product-add-on-approval-packet.json`
- `23-product-page-media-classification-packet.json`
- `24-product-page-price-review-packet.json`
- `16-catalog-purge-scope-dry-run.md`
- a fresh current-state catalog snapshot made after source freeze

## V1 Product Re-Export/Re-Import Acceptance Proof

Owner question: will the Odoo CE 19 V1 product re-export/re-import path produce
correct ERPNext/Frappe Webshop product pages?

Acceptance answer is **only yes after a post-import proof passes**. The proof
must be run on the approved V1 subset, not the full current fixture catalog.

V1 subset rules:

- Include only approved ready-to-order/simple products with explicit source
  approval for public sale.
- Exclude 50+ color/high-variant products, unresolved add-on families,
  complex/high-dollar event decor, and products whose source meaning requires a
  quote-first path.
- Treat current visible/imported ERPNext products as fixtures only. They can
  prove architecture, but they do not prove final catalog truth.

Post-import acceptance checks:

1. Backend authority fields are populated from source:
   `Website Item.lt_product_page_type`, `Website Item.lt_commerce_lane`,
   Item/Item Variant identity, Item Price rows, Item Attribute rows, and media
   links must be generated from the import/source contract, not edited into the
   frontend by hand.
2. Product page rendering reads backend truth:
   page title, buying lane, price display, variant controls, gallery/media,
   SEO title/description, canonical data, product schema, and FAQ/discovery
   content must be traceable to ERPNext/Frappe records or approved source
   packets.
3. Variant behavior matches source meaning:
   where Odoo source says a selected variant changes image or price, the
   ERPNext Item Variant / Item Price / media mapping must drive the visible
   change. If source says no public checkout variant exists, the product must
   stay quote-first or blocked from paid checkout.
4. Cart and checkout preserve product meaning:
   adding a selected product must use the resolved ERPNext Item or Item Variant
   code, preserve configuration JSON/summary on Sales Order Item and Sales
   Invoice Item, and keep quote-first products out of paid checkout through
   product controls, cart API, direct checkout URL, and stale localStorage.
5. Search/discovery is backend-truth aligned:
   SEO/AEO/GEO output cannot be manual decoration that contradicts backend
   product type, price, variant, availability, media, or quote/checkout lane.

Minimal post-import verifier set:

- `python scripts/verify/product_import_readiness_gate.py --json`
- `python scripts/verify/product_page_architecture_readiness.py --json`
- `python scripts/verify/catalog_variant_contract.py`
- `python scripts/verify/variant_media_contract.py`
- `npm run test:product-prices`
- `npm run test:product-price-display`
- `npm run test:variant-media`
- `python scripts/verify/cart_checkout_contract.py`
- `node scripts/verify/post_import_checkout_proof.js`
- `python scripts/verify/stripe_amount_parity_contract.py`
- `python scripts/verify/checkout_product_family_contract.py --report <durable-v1-report-path>`
- `python scripts/verify/quote_event_checkout_boundary_contract.py --report <durable-v1-boundary-report-path>`
- `npm run test:shop-smoke`

Do not substitute screenshots or visible product cards for backend field proof.
Screenshots can supplement the post-import review, but they are not acceptance
evidence unless the backend/source mapping checks pass first.

## Required Import Runner Behavior

The import runner must be changed before real use:

- default mode is dry-run
- destructive/import mode requires an explicit flag
- destructive/import mode requires a named fresh backup and snapshot
- import writes `lt_product_page_type` and `lt_commerce_lane`
- import writes only approved public prices, or keeps unresolved units quote-only
- import holds unclassified extra media instead of guessing gallery or variant roles
- import keeps unresolved add-on families quote-only or dropped until approved
- failure is nonzero with a report row naming the product, field, and missing approval

## Snapshot And Rollback Plan

Before staging import rehearsal:

1. Freeze source and identify the exact commit/import code.
2. Run `bench --site frontend backup --with-files` on the target site.
3. Create a fresh catalog state snapshot for `Website Item`, `Item`, `Item Price`, `Item Variant Attribute`, `Item Attribute`, `Item Group`, and product `File` rows.
4. Run `python scripts/verify/catalog_purge_scope_dry_run.py`.
5. Run the import runner in dry-run mode and archive the report.
6. Run this gate again.
7. Only after approval, run destructive/import mode on staging first.
8. After import, rerun catalog shape, price, media, cart/checkout, and product import readiness gates.

Rollback is restore DB/files backup first. Snapshot-based repair is only a secondary forensic path, not the primary rollback plan.

## Current Blockers

Current result: historical `PASS` for local corrected V1 import readiness is
stale after the 2026-05-19 price-identity incident. Re-run the gate and the new
source-price modifier / visible-price checks before using this packet as import
approval evidence.

Fresh read-only gate result on 2026-05-12:

- Command:
  `python scripts/verify/product_import_readiness_gate.py --report output/product-import-readiness-gate.json`
- Result: exit 0 / `PASS`, read-only, 12 pass rows, 0 warnings, 0 blockers.
- Corrected V1 manifest: 48 included products, 5 owner-explicit Classic
  exclusions, 225 deterministic source-priced sale units.
- Purge scope: 48 templates, 6,894 variants, 6,928 prices.
- Snapshot: fresh local snapshot exists at
  `audits/odoo-erpnext-migration-audit-2026-05-08/current-state-snapshot-2026-05-11-1050`.
- Backup guard path recorded:
  `/home/frappe/frappe-bench/sites/frontend/private/backups/20260511_122754-frontend-database.sql.gz`.
- Import runner contains required product-page authority fields and destructive
  guard markers.
- Final explicit local-only destructive approval is recorded for the local
  `frontend` site.
- `v1_add_on_fallbacks`: 8 included products keep review-only add-on axes
  protected behind quote-first fallback. The gate now blocks only if a
  review-only add-on leaks onto a direct-checkout product.

Regression fixes completed on 2026-05-12:

- `AddOnContract` now preserves confirmed add-on metadata such as
  `item_code`, quantity bounds, required value behavior, and receipt label.
- `product_import_readiness_gate_contract.py` proves a clean checkout with no
  snapshot cannot crash the command packet; it returns the fresh-snapshot
  placeholder instead.
- `post_import_catalog_state_contract.py` proves missing/unpublished/disabled
  or unpriced included products return `ok: false`.
- `post_import_checkout_proof.js` now checks visible color-drawer controls,
  verifies `color_recipes`, and calls the non-mutating checkout totals preview
  API before accepting checkout proof.

## Follow-Up Owner

Backend owner: keep the import runner and gate green as source/import code changes. Re-run the readiness gate, post-import catalog state, and checkout proof before any fresh catalog-import claim.

Data/import owner: keep final real catalog approval, live merchandising, Frappe Cloud/live import, payment cutover, and unresolved add-on mapping as separate owner-approved gates.
