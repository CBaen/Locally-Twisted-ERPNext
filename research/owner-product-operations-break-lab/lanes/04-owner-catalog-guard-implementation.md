# Lane 04 - Owner Catalog Guard Implementation

Date: 2026-05-21
Status: locally implemented and verified

Scope: local-only owner product/catalog safety guard for the ERPNext/Frappe
storefront. No staging, live, provider, DNS, Stripe, or public indexing state was
touched.

## Decision

The business owner must be able to add, remove, reprice, update photos, and
update copy for products. That business control belongs in Product Setup.

The business owner should not do those actions by directly editing raw ERPNext
catalog infrastructure records such as `Item`, `Website Item`, `Item Price`,
variant attributes, item groups, or `Webshop Settings`.

The safe owner path is:

1. Create or update an `LT Product Blueprint`.
2. Edit business fields there: exact checkout prices, public copy, primary
   product photo, option rows, and shop visibility.
3. Save as draft/review.
4. Preview the apply plan.
5. Apply only through a named guarded server context after the local gate and
   confirmation checks pass.

The owner keeps business visibility and Product Setup access. Direct edits to
live catalog primitives are blocked because they can desync public product pages,
cart resolution, checkout pricing, variants, or global Webshop behavior.

## Why This Is Required

Triadic break-lab evidence found normal-looking owner actions can break the shop:

- a published `Website Item` can exist without a real linked `Item`;
- a public product route can render `200` while cart later fails as unpriced or
  unavailable;
- a disabled `Item` can still have a published public product page;
- route edits immediately strand old URLs;
- duplicate variant attributes can create two exact matches with different
  prices;
- `Webshop Settings` toggles affect the whole storefront, including guest price
  visibility and checkout.

The verified owner role has broad catalog powers today, including product, price,
website, and system roles. Guarding mutations is safer than pretending the role
is harmless.

## Implemented Guard

Files added or changed:

- `apps/locally_twisted/locally_twisted/owner_catalog_guard.py`
- `apps/locally_twisted/locally_twisted/hooks.py`
- `apps/locally_twisted/locally_twisted/product_blueprint_local_apply.py`
- `apps/locally_twisted/locally_twisted/verify/owner_catalog_guard_contract.py`
- `apps/locally_twisted/locally_twisted/verify/catalog_public_sellability_contract.py`
- `apps/locally_twisted/locally_twisted/verify/product_setup_catalog_coverage.py`
- `apps/locally_twisted/locally_twisted/seed/sync_product_blueprints_from_catalog.py`
- `scripts/verify/owner_catalog_guard_contract.py`
- `scripts/verify/catalog_public_sellability_contract.py`
- `scripts/verify/product_setup_catalog_coverage.py`
- `scripts/setup/sync_product_blueprints_from_catalog.py`
- `scripts/verify/backend_workspace_parity.py`
- `apps/locally_twisted/locally_twisted/seed/sync_backend_workspaces.py`
- `package.json`

Protected DocTypes:

- `Item`
- `Website Item`
- `Item Price`
- `Item Attribute`
- `Item Attribute Value`
- `Item Variant Attribute`
- `Item Group`
- `Webshop Settings`

Owner-like users:

- `locallytwisted@gmail.com`
- users with role `LT Owner Access`

Allowed server contexts:

- `blueprint_local_apply`
- `classification_contract_apply`
- `catalog_import_rehearsal`
- `price_repair_contract`
- `ecommerce_break_lab_restore`

The guard is wired through Frappe `doc_events`. Official Frappe docs define
`doc_events` as lifecycle handlers for document events such as `validate`,
`before_insert`, `before_save`, `on_update`, and `on_trash`. Frappe's Document
API can bypass normal permission checks with flags such as `ignore_permissions`,
so this guard is paired with named server contexts and verifier tests.

## Owner Can Do

Allowed now:

- view catalog, product, customer, order, and owner workspace records;
- create and edit `LT Product Blueprint` records for all current storefront
  products;
- change exact checkout prices, product summary, `About This Design`,
  `What's Included`, primary product photo, option rows, add-ons, media rules,
  and shop visibility in Product Setup;
- run no-write preview flows already covered by the Product Blueprint contract;
- run guarded local Product Blueprint apply only when the local config flag and
  confirmation token are present;
- browse and test the local public shop.

Allowed only through guarded server workflows:

- product record creation;
- product price creation/update;
- website product page creation/update;
- variant option/axis creation/update;
- catalog classification repair;
- import rehearsals;
- price repair;
- local break-lab restore.

## Owner Cannot Do Directly

Blocked now for owner-like users:

- create, edit, delete, disable, or rename `Item` records directly;
- publish, unpublish, relink, reroute, delete, or rename `Website Item` records
  directly;
- create, edit, or delete `Item Price` rows directly;
- change variant axes, variant attribute rows, or attribute values directly;
- rename or move `Item Group` records directly;
- change `Webshop Settings` directly.

This is intentional. Jeff can change prices and product content through Product
Setup; he cannot trip over the raw infrastructure tables that can create public
pages with wrong prices, dead routes, missing checkout records, duplicate
variant matches, or global shop behavior drift.

## What This Does Not Cover

This guard does not claim to block:

- `Administrator` repair work;
- direct SQL;
- raw database restore/import activity;
- scripts that intentionally set an allowed guard context;
- staging/live systems until this code is deployed and verified there.

Those paths require drift verifiers, dry-run reports, backups/snapshots, and an
explicit release gate.

## Verification

Commands run on 2026-05-21:

```powershell
python -m compileall .\apps\locally_twisted\locally_twisted\owner_catalog_guard.py .\apps\locally_twisted\locally_twisted\verify\owner_catalog_guard_contract.py .\scripts\verify\owner_catalog_guard_contract.py
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend clear-cache
python .\scripts\verify\owner_catalog_guard_contract.py
python .\scripts\dev\clear_website_cache.py --restart
python .\scripts\verify\owner_catalog_guard_contract.py
python .\scripts\verify\product_blueprint_contract.py
python .\scripts\verify\webshop_guest_party_contract.py
python .\scripts\verify\website_item_classification_contract.py --json
python .\scripts\verify\owner_business_access_contract.py
python .\scripts\verify\ecommerce_expected_mode.py --expect open
npm run test:product-prices
npm run test:public-assets
npm run test:public-network
```

Results:

- compile: pass;
- owner guard contract: pass before and after local backend/frontend restart,
  `5/5` probes passed;
- owner direct `Item` insert: blocked;
- owner direct orphan `Website Item` insert: blocked;
- owner direct `Item Price` insert: blocked;
- owner direct `Webshop Settings` save: blocked;
- owner guarded Product Blueprint context insert: allowed;
- Product Blueprint contract: pass, `22` tests;
- Webshop Guest party contract: pass, `11/11` runtime guard probes blocked;
- Website Item classification contract: pass, dry run, `51` matched records,
  `0` planned changes;
- Owner Business Access contract: pass, owner user available, provider-neutral,
  customer-send blocked, write surface limited to `log_contact_attempt`;
- local ecommerce mode: pass for `expect=open`.
- Product price contracts: pass, cart prices pass, Odoo modifier parity pass for
  `49` products and `10186` active variants.
- Public asset integrity: pass, `31` routes, `291` unique local asset URLs;
- Public network integrity: pass, `31` Playwright route checks with no broken
  same-origin assets or console errors.

Follow-up break-lab verification on 2026-05-21:

```powershell
python .\scripts\verify\allow_guest_surface_inventory.py
python .\scripts\dev\clear_website_cache.py --restart
python .\scripts\verify\newsletter_concurrency_contract.py --base-url http://localhost:8081
python .\scripts\verify\backend_workspace_parity.py
npm run test:owner-product-safety
npm run test:public-network
npm run test:checkout-experience
python .\scripts\verify\event_playground_gate.py
npm run test:event-playground
npm run test:form-experience
python .\scripts\verify\smoke_forms.py --base-url http://localhost:8081 --shape-only --skip-newsletter
python .\scripts\verify\product_import_readiness_gate.py
```

Results:

- Guest endpoint inventory: pass, `12` guest endpoints, `3` public write
  endpoints.
- Public write/action methods: hardened so newsletter signup, inquiry submit,
  checkout preview, guest order submit, and quote acceptance reject direct `GET`
  calls; live probes returned `403`.
- Newsletter concurrency contract: pass after the POST-only hardening.
- Owner Home no longer exposes direct `Product Prices`; workspace parity now
  fails if that shortcut is reintroduced.
- Catalog public sellability verifier: pass, `51` published Website Items, `30`
  checkout Website Items, `21` quote-first Website Items, `28` checked variant
  templates, `3706` active variants, `0` warnings.
- `npm run test:owner-product-safety`: pass; this bundles owner catalog guard,
  rollback-safe Product Setup apply, Product Setup coverage, public sellability,
  backend price contracts, visible price display, variant media, Product Setup
  copy swapping, and cart checkout contract.
- Event playground guest gate: pass. The broader Playwright event playground
  suite ran with `1` pass and `4` skips, so only the guest gate is claimed here.
- Form experience initially caught a real regression: the invisible anti-spam
  honeypot wrapper computed as `opacity: 1`. The template now keeps the field
  in the DOM but visually hidden with `opacity: 0`; `test:form-experience`
  passed `14/14` after the fix.
- Form smoke shape: pass after the honeypot visibility fix.
- Product import readiness gate: blocked as intended because same-day snapshot,
  backup, and final destructive approval were stale for 2026-05-21.

Owner-control correction on 2026-05-21:

```powershell
docker exec locally-twisted-erpnext-v15-backend-1 bash -lc "cd /home/frappe/frappe-bench && bench --site frontend migrate"
python .\scripts\setup\sync_product_blueprints_from_catalog.py
python .\scripts\setup\sync_product_blueprints_from_catalog.py --write
python .\scripts\verify\product_setup_catalog_coverage.py
python .\scripts\verify\product_blueprint_live_contract.py
python .\scripts\verify\cart_checkout_contract.py
npm run test:owner-product-safety
npm run test:public-network
```

Results:

- Product Setup now has owner-editable records for all `51` current Website
  Items.
- The backfill created `3708` exact checkout price rows in Product Setup for
  `30` checkout products, so variant prices are owner-editable without direct
  `Item Price` table access.
- The backfilled records are `Draft` by default. This prevents Product Setup
  from silently taking over checkout runtime before product review.
- Product Setup now includes guarded business fields for shop visibility,
  primary product photo, product summary, `About This Design`, and `What's
  Included`.
- The 2026-05-21 media/copy expansion renamed the owner-facing image field to
  `Fallback/Main Product Photo` and added separate owner tables for gallery
  photos, option-specific image rules, and option-specific copy rules.
- Witness review found and closed four guard gaps: local Product Setup apply
  cannot publish Website Items, visible-shop requests fail loudly when customer
  media is missing, exact checkout price rows cannot target another product's
  Items, and owner direct edits to Website Slideshow records are blocked.
- Selected Product Setup copy is now preserved into checkout/Sales Order line
  payloads, not just rendered on the product page.
- The first sync attempt exposed a real blast radius: active backfilled Product
  Setup records changed checkout failure behavior. The correction keeps
  backfilled records Draft until reviewed; `cart_checkout_contract.py` passes.
- `npm run test:owner-product-safety` passes with owner direct raw catalog and
  gallery mutation blocked, Product Setup rollback/apply guards passing,
  Product Setup coverage complete, public catalog sellability intact, backend
  and visible product prices intact, variant media intact, Product Setup copy
  swapping intact, and cart/checkout intact.
- `npm run test:public-network` passes `31/31`.

The local ecommerce site is currently open, not paused. That matches this
checkout-focused local testing session. Do not assume this is acceptable for
staging/live.

Triad closeout follow-up on 2026-05-22:

```powershell
python -m py_compile apps\locally_twisted\locally_twisted\product_blueprint_local_apply.py apps\locally_twisted\locally_twisted\verify\product_blueprint_contract.py apps\locally_twisted\locally_twisted\seed\sync_product_blueprints_from_catalog.py apps\locally_twisted\locally_twisted\locally_twisted\doctype\lt_product_blueprint\lt_product_blueprint.py apps\locally_twisted\locally_twisted\verify\owner_catalog_guard_contract.py
python .\scripts\verify\owner_catalog_guard_contract.py
python .\scripts\verify\product_blueprint_live_contract.py
python .\scripts\setup\sync_product_blueprints_from_catalog.py
```

Results:

- Owner catalog guard verifier now passes `19/19` probes instead of the earlier
  narrow probe set. Coverage includes existing Item/Website Item save, delete,
  and rename; option-axis/value records; Item Group insert/save/rename; product
  gallery slideshow records; Webshop Settings; and the allowed guarded Product
  Blueprint context.
- Local Product Setup apply preserves existing public Website Item published
  state and blocks owner Product Setup requests that would hide or reroute an
  existing public Website Item.
- Product Setup sync dry run now reports real update intent: `51` Website
  Items, `0` creates, `21` would-update rows.
- The sync bug where filling missing price rows could clear existing option
  rows was fixed.
- Desk preview now carries target Item and Website Item fields into validation
  payloads.
- Full umbrella `npm run test:owner-product-safety` passed in the final
  pre-commit state after these triad refinements.

## Next Required Automation

Before owner product work is considered production-safe:

- wire the public catalog sellability verifier into the daily/pre-release drift
  monitor;
- keep `product_setup_catalog_coverage.py` in the owner-product gate so every
  public product keeps an editable Product Setup record and exact checkout price
  rows;
- keep the route-change guard green so existing public Website Items cannot be
  rerouted through local apply;
- add a variant uniqueness verifier to block exact-match duplicates globally;
- add a guarded Price Review/Product Setup action if Jeff needs explicit price
  review apart from Product Setup;
- run this verifier set after any Product Setup change and before staging/live
  release.
