# Lane 04 - Owner Catalog Guard Implementation

Date: 2026-05-21
Status: locally implemented and verified

Scope: local-only owner product/catalog safety guard for the ERPNext/Frappe
storefront. No staging, live, provider, DNS, Stripe, or public indexing state was
touched.

## Decision

The business owner should not directly add, delete, publish, unpublish, reprice,
reroute, disable, or restructure storefront products through raw ERPNext catalog
records.

The safe owner path is:

1. Create or update an `LT Product Blueprint`.
2. Save as draft/review.
3. Preview the apply plan.
4. Apply only through a named guarded server context after the local gate and
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
- `scripts/verify/owner_catalog_guard_contract.py`

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
- create and edit `LT Product Blueprint` records;
- save product intent, options, add-ons, media rules, base price, and notes in
  Product Setup;
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

This is intentional. These actions can create public pages with wrong prices,
dead routes, missing checkout records, duplicate variant matches, or global shop
behavior drift.

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
python .\scripts\verify\product_blueprint_contract.py
python .\scripts\verify\webshop_guest_party_contract.py
python .\scripts\verify\website_item_classification_contract.py --json
python .\scripts\verify\owner_business_access_contract.py
python .\scripts\verify\ecommerce_expected_mode.py --expect open
npm run test:product-prices
```

Results:

- compile: pass;
- owner guard contract: pass, `5/5` probes passed;
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

The local ecommerce site is currently open, not paused. That matches this
checkout-focused local testing session. Do not assume this is acceptable for
staging/live.

## Next Required Automation

Before owner product work is considered production-safe:

- add a daily or pre-release drift verifier for public catalog sellability;
- add a route-change/redirect guard before allowing any URL edits;
- add a variant uniqueness verifier to block exact-match duplicates globally;
- remove or replace the direct `Product Prices` owner workspace shortcut with a
  guarded Product Setup or Price Review action;
- run this verifier set after any Product Setup change and before staging/live
  release.
