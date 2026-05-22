# Owner Product Setup Guard Closeout - 2026-05-22

Status: local-only implementation recovered, triad-reviewed, and partially
reverified after the route/visibility guard fixes. This is not staging/live
approval.

## Scope

This lane protects the owner product-management workflow for Jeff/Locally
Twisted. The owner can work through `LT Product Blueprint` / Product Setup, but
owner-like users are blocked from directly mutating raw ERPNext catalog
infrastructure that can break the public shop.

No Frappe Cloud deploy, staging update, live update, DNS change, Stripe live
payment, Search Console action, provider dashboard mutation, or destructive
catalog import was performed.

## Triad Roles Used

Guiding Light corrected the workflow: this class of work needs a triad.

- Witness: read-only risk review of owner/catalog/public shop failure modes.
- Recorder: mapped handoffs, queue, commit boundaries, and documentation
  obligations.
- Fixer: found implementation gaps in guards, sync/backfill behavior, and
  verifier coverage.

The parent agent integrated the findings, made the source edits, and reran
focused live-local ERPNext verifiers.

## What Changed

Owner guard surface:

- `owner_catalog_guard.py` now includes Website Slideshow and Website
  Slideshow Item so gallery edits are not a raw-owner escape hatch.
- `hooks.py` wires owner catalog guard events for raw catalog DocTypes and a
  wildcard fallback so protected DocTypes fail closed if hook coverage drifts.
- `owner_catalog_guard_contract.py` now probes 19 owner-like actions, including
  create/save/delete/rename for existing Items and Website Items, Item
  Attribute, Item Attribute Value, Item Variant Attribute, Item Group,
  Website Slideshow, Website Slideshow Item, Webshop Settings, and the allowed
  guarded Product Blueprint context.

Product Setup apply safety:

- Existing public Website Items keep their current `published` value during
  local Product Setup apply.
- Existing hidden Website Items cannot be published through local apply.
- Existing public Website Items cannot be hidden through local apply.
- Existing public Website Items cannot be rerouted through local apply. URL
  changes require the reviewed redirect/SEO release path.
- Exact checkout price rows are scoped to the current Product Setup Item or
  its variants; cross-product price rows fail loudly.

Product Setup coverage/backfill:

- `sync_product_blueprints_from_catalog.py` creates/fills Product Setup records
  from current Website Items without mutating Items, Website Items, Item
  Prices, routes, checkout records, or live catalog state.
- Published checkout backfills can be `Local Preview Ready` when active Product
  Setup runtime price/media rules are needed for local or staging preview.
  Non-checkout backfills remain `Draft` until reviewed, so they do not silently
  take over runtime checkout behavior.
- Dry runs now truthfully report `would_update` for existing Product Setup
  records with missing fields/child rows.
- Filling missing price rows no longer clears existing option rows.

Owner-facing content/media setup:

- Product Setup includes exact checkout price rows, fallback/main product
  photo, gallery images, option-specific image rules, and option-specific copy
  rules.
- Selected Product Setup copy and media resolve on product pages and are
  preserved into cart/checkout/Sales Order line payloads where applicable.
- Desk preview now includes `target_item_code` and `target_website_item`, so
  preview and server validation share target-link context.

Public write/network hardening recovered in the same lane:

- Public write/action allow-guest methods are POST-only where mutation is
  intended.
- The LT base template preserves Frappe's `<!-- csrf_token -->` marker so
  logged-in website sessions can make Webshop startup POSTs without CSRF 400s.
- Public network verification now checks stale asset/wrong MIME classes and
  logged-in Desk-session Webshop CSRF regressions.

## Files To Treat As Source For This Lane

Primary source:

- `apps/locally_twisted/locally_twisted/owner_catalog_guard.py`
- `apps/locally_twisted/locally_twisted/hooks.py`
- `apps/locally_twisted/locally_twisted/product_blueprint_validation.py`
- `apps/locally_twisted/locally_twisted/product_blueprint_apply_plan.py`
- `apps/locally_twisted/locally_twisted/product_blueprint_local_apply.py`
- `apps/locally_twisted/locally_twisted/product_setup_runtime.py`
- `apps/locally_twisted/locally_twisted/api/product_setup.py`
- `apps/locally_twisted/locally_twisted/public/js/lt-product-setup-runtime.js`
- `apps/locally_twisted/locally_twisted/templates/generators/item/item_configure.html`
- `apps/locally_twisted/locally_twisted/templates/generators/item/item_details.html`

New/changed child DocTypes:

- `LT Product Blueprint Price`
- `LT Product Blueprint Gallery Image`
- `LT Product Blueprint Content Rule`

Verifiers and setup helpers:

- `scripts/verify/owner_catalog_guard_contract.py`
- `scripts/verify/product_blueprint_live_contract.py`
- `scripts/verify/product_setup_catalog_coverage.py`
- `scripts/verify/catalog_public_sellability_contract.py`
- `scripts/setup/sync_product_blueprints_from_catalog.py`
- `scripts/verify/product_setup_content_runtime.spec.js`
- `scripts/verify/product_options_experience.spec.js`
- `scripts/verify/public_network_integrity.spec.js`

Related evidence:

- `research/owner-product-operations-break-lab/lanes/04-owner-catalog-guard-implementation.md`
- `research/owner-product-operations-break-lab/lanes/05-sidecar-lens-c-access-operational-guardrails.md`
- `workstreams/ecommerce-break-lab-2026-05-21.md`
- `workstreams/ecommerce-audit/generic-product-setup-runtime-2026-05-15.md`

## Verified Locally

Latest proof after the 2026-05-22 triad fixes:

```powershell
python -m py_compile apps\locally_twisted\locally_twisted\product_blueprint_local_apply.py apps\locally_twisted\locally_twisted\verify\product_blueprint_contract.py apps\locally_twisted\locally_twisted\seed\sync_product_blueprints_from_catalog.py apps\locally_twisted\locally_twisted\locally_twisted\doctype\lt_product_blueprint\lt_product_blueprint.py apps\locally_twisted\locally_twisted\verify\owner_catalog_guard_contract.py
python scripts\verify\owner_catalog_guard_contract.py
python scripts\verify\product_blueprint_live_contract.py
python scripts\setup\sync_product_blueprints_from_catalog.py
npm run test:owner-product-safety
npm run test:product-options-experience
npm run test:public-network
python scripts\verify\allow_guest_surface_inventory.py
python scripts\verify\smoke_forms.py --base-url http://localhost:8081 --shape-only --skip-newsletter
python scripts\verify\newsletter_concurrency_contract.py --base-url http://localhost:8081
npm run test:form-experience
npm run test:public-assets
git diff --check
```

Results:

- owner catalog guard passed `19/19` probes;
- Product Blueprint live contract passed, including existing public Website
  Item visibility preservation and hide/route-change blocks;
- Product Setup sync dry run passed with `51` Website Items, `0` creates, and
  `21` truthful would-update rows.
- owner product umbrella passed, including Product Setup coverage, sellability,
  catalog variant identity, price parity, visible price display, selected
  media, Product Setup copy swap, and cart/checkout contract;
- product-option UX passed `4/4`;
- public-network passed `40/40`;
- allow-guest inventory, form smoke, newsletter concurrency, form experience,
  public assets, Python compile, JSON parse checks, and diff whitespace checks
  passed.

Previously green in the recovered lane before the final triad fixes:

- `python scripts/verify/product_setup_catalog_coverage.py`
- `python scripts/verify/catalog_public_sellability_contract.py`
- `python scripts/verify/backend_workspace_parity.py`
- `python scripts/verify/catalog_variant_contract.py`
- `npm run test:public-assets`
- `npm run test:ecommerce-open-mode`
- `npm run test:product-options-experience`
- `npm run test:public-network`
- `python scripts/verify/allow_guest_surface_inventory.py`
- `npm run test:form-experience`
- `python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --shape-only --skip-newsletter`
- `python scripts/verify/newsletter_concurrency_contract.py --base-url http://localhost:8081`
- `npm run test:webshop-guest-party`
- `npm run test:checkout-experience`

Before staging/live, rerun the full owner-product umbrella if source changes
again:

```powershell
npm run test:owner-product-safety
```

## Remaining Gates

- Guiding Light and Jeff need local owner-workflow testing before staging.
- Staging preview for the owner can be prepared only after the local owner
  product gate is green in the final commit state.
- A triad must review release scope, gate evidence, and doc truth before any
  commit/push/staging claim from this lane.
- Staging proof needs the actual staging host/app mirror/site update/cache
  state plus staging HTTP/browser checks. Local Docker database verifiers are
  prerequisites only unless rerun against the staging environment itself.
- Public checkout/Stripe remains gated separately by Frappe Cloud, Stripe,
  webhook, policy, product scope, and low-risk payment proof.
- Direct SQL/import/restore paths remain outside document hooks. Keep same-day
  backup, dry-run, snapshot, and drift-monitor receipts around any destructive
  catalog work.
- The live-readiness research brief at
  `research/expedition-lt-ecommerce-live-readiness/research-brief.md` is a
  question packet only. It is not release approval.

## Cleanup

Removed generated Python `__pycache__` directories from the new Product
Blueprint child DocType folders. No source, fixtures, migrations, or verifier
files were deleted.
