D:2026-05-14 | Check:local-only build brief | Confidence:[LOCAL-SOURCE]
# Product Blueprint Authoring Handoff

Goal approved by GL: staff must be able to define highly customizable products
through ERPNext, not by asking a developer to code each product.

## Local-Only Boundary

This slice creates an employee-facing product setup surface and validation
contract only. It does not create ERPNext Items, Website Items, prices, files,
routes, Stripe records, payment settings, Frappe Cloud updates, DNS changes, or
live publish actions.

Public ecommerce remains gated separately by `lt_ecommerce_paused`.

Framing correction from GL on 2026-05-14: that gate is a live/public safety
lock, not an implementation blocker. The reason ecommerce is not public is that
the product, cart, checkout, pricing, media, and verification paths are not
trustworthy enough yet. Local build work must continue under the safety lock.
Future status updates must name the actual technical blocker instead of using
the public safety lock as the reason work cannot proceed.

## First Slice

Add `LT Product Blueprint` plus child tables for:

- options / variant axes;
- color recipes;
- add-ons;
- conditional pricing.

The controller validates each save and writes readiness evidence back onto the
record. Drafts may save while blocked so staff can work incrementally. Moving a
blocked record to local preview/staging fails loudly. `Approved For Live` is
not available from this local blueprint slice.

## Acceptance

- Product setup is a Desk record, not a code-only source packet.
- The validation result maps employee labels to the LT architecture contract:
  `simple_product`, `complex_custom_product`, `checkout`, `quote_first`,
  `needs_review`, `selected_options`, `color_recipes`, `add_ons`, and
  `quote_context`.
- Direct checkout blocks unresolved add-ons and conditional pricing.
- Live readiness is always false in this slice.
- No product generation or publish action exists yet.

## Verification Receipt

Local commands run:

```bash
python -m py_compile apps/locally_twisted/locally_twisted/product_blueprint_validation.py apps/locally_twisted/locally_twisted/verify/product_blueprint_contract.py scripts/verify/product_blueprint_contract.py scripts/verify/product_blueprint_live_contract.py
python scripts/verify/product_blueprint_contract.py
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend migrate
python scripts/verify/product_blueprint_live_contract.py
python scripts/verify/product_page_architecture_contract_contract.py
python scripts/verify/ecommerce_pause_contract.py
python scripts/verify/verifier_cli_contract.py
```

Results:

- Pure product blueprint contract: PASS.
- Local ERPNext migration: PASS; all five product blueprint DocTypes installed.
- Live product blueprint contract: PASS, rollback-safe; temporary blueprint
  validation evidence wrote successfully, live approval and blocked preview
  failed loudly, and Item / Website Item / price / order / invoice / payment
  counts stayed unchanged.
- Product-page architecture pure contract: PASS.
- Ecommerce pause contract: PASS.
- Verifier CLI contract: PASS.
- `product_page_architecture_readiness.py --json` still returns
  `technical_architecture_ok: true` and `import_reopen_ok: false` because the
  public reopen switch is locked by site config. That safety lock is not an
  implementation blocker and should not be "fixed" by opening public ecommerce
  during product-authoring work.

## Next Slice

Build a dry-run "Apply Blueprint" verifier that shows exactly which ERPNext
Item, Item Variant, Website Item, Item Price, media, and LT custom-field changes
would be made, without writing them. Only after that passes should an explicit
local apply action be considered.

## Dry-run Apply Plan Slice

Status: implemented locally after the first slice.

Added `base_price` and read-only `apply_plan_json` to `LT Product Blueprint`.
On save, the controller now writes both validation evidence and a no-write
apply plan. The apply plan names the records that would be needed but does not
write them:

- base `Item`;
- unpublished `Website Item` with LT page template and buying path fields;
- required `Item Attribute` rows;
- planned `Item` variants for direct-checkout sale-unit axes;
- planned `Item Price` rows for direct-checkout variants or fixed products;
- add-on references;
- held media work for a later media-assignment slice.

Guardrails:

- Direct checkout requires a base checkout price.
- Direct checkout blocks unresolved add-ons and unresolved conditional pricing.
- Direct checkout variant expansion is capped at 50 variants; larger products
  must stay quote-first or be split.
- Dry-run plans keep `writes_enabled=false`, `live_publish_enabled=false`, and
  Website Item `published=0`.
- Quote-first plans do not create checkout Item Price rows.

Additional verification:

```bash
python -m py_compile apps/locally_twisted/locally_twisted/product_blueprint_apply_plan.py
python scripts/verify/product_blueprint_contract.py
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend migrate
python scripts/verify/product_blueprint_live_contract.py
```

Results:

- Pure product blueprint contract now covers the dry-run apply plan, base price
  requirement, and high-variant direct-checkout blocker.
- Local ERPNext migration updated `LT Product Blueprint` with the dry-run fields.
- Live product blueprint contract passed rollback-safe and proved the plan
  writes no product, price, order, invoice, or payment records.

## Next Slice After Dry-run

Build a local-only "Apply Blueprint to ERPNext" action behind an explicit
approval gate. It must consume the dry-run plan, write only local product
records, keep Website Items unpublished by default, regenerate Webshop caches,
and then run product-page architecture, cart/checkout, quote-first, media, and
pause verifiers before any staging discussion.

## Guarded Local Apply Slice

Status: implemented locally after the dry-run slice.

Added `product_blueprint_local_apply.py`. It converts a validated blueprint plan
into local ERPNext records only when the caller passes both:

- `allow_writes=True`;
- confirmation token `LOCAL_ONLY_BLUEPRINT_APPLY`.

Default behavior remains a no-write preview. The write path creates or updates
only the local product records needed by the blueprint:

- template `Item`;
- required `Item Attribute` rows and values;
- variant `Item` rows for direct-checkout sale-unit axes;
- `Item Price` rows for checkout sellable SKUs only;
- one `Website Item` linked to the template.

Guardrails:

- no public Desk action or guest API exists for apply;
- no commits are issued by the helper;
- Website Items stay `published=0`;
- live publishing stays disabled;
- existing Item / Website Item collisions fail loudly unless the blueprint is
  already linked to those target records;
- duplicate generated variant item codes fail before writing;
- template Item Prices are not created for variant products;
- Sales Orders, Sales Invoices, and Payment Requests are not created.

Additional verification run after migration:

```bash
python -m py_compile apps/locally_twisted/locally_twisted/product_blueprint_local_apply.py apps/locally_twisted/locally_twisted/verify/product_blueprint_contract.py scripts/verify/product_blueprint_contract.py scripts/verify/product_blueprint_live_contract.py
python scripts/verify/product_blueprint_contract.py
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend migrate
python scripts/verify/product_blueprint_live_contract.py
python scripts/verify/product_page_architecture_contract_contract.py
python scripts/verify/ecommerce_pause_contract.py
python scripts/verify/product_page_architecture_readiness.py --json
python scripts/verify/verifier_cli_contract.py
```

Results:

- Pure product blueprint contract: PASS, 14 tests.
- Local ERPNext migrate: PASS.
- Live product blueprint contract: PASS, rollback-safe. It proved the local
  apply guard rejects missing confirmation, then applied a temporary product in
  transaction and observed the expected local-only delta: one template Item, two
  variant Items, one Item Attribute, two Item Prices, one unpublished Website
  Item, and zero order, invoice, or payment records.
- Product-page architecture pure contract: PASS.
- Public exposure safety-lock contract: PASS.
- Product-page architecture readiness: `technical_architecture_ok=true`,
  `import_reopen_ok=false`; the remaining public-reopen row is the site-config
  safety lock and is not a local implementation blocker.
- Verifier CLI contract: PASS, 110 scripts.

## Desk Apply Slice

Status: implemented locally after the guarded local apply slice.

Added an employee-facing Desk control on `LT Product Blueprint`:

- `Preview Local Apply` shows the no-write planned counts and blockers.
- `Apply Locally` appears only after a saved blueprint is `Ready For Local Preview`.
- The apply dialog requires an operator confirmation checkbox.
- Target shortcuts open the generated `Item` and `Website Item` after apply.

Server guardrails:

- `apply_locally_from_desk` is whitelisted for Desk but not guest-callable.
- Guest users are rejected before preview.
- Only `System Manager` and `Item Manager` can preview/apply.
- Apply requires the site config flag `lt_allow_local_blueprint_apply=1`.
- The local `frontend` site has that flag set for local testing.
- The browser/client JS does not contain the deeper confirmation token; the
  server passes it to the apply helper only after role and local-site checks.
- The helper still keeps Website Items unpublished and creates no order,
  invoice, payment, Stripe, DNS, Frappe Cloud, or live-site records.

Additional verification run:

```bash
python -m py_compile apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_product_blueprint/lt_product_blueprint.py apps/locally_twisted/locally_twisted/product_blueprint_local_apply.py apps/locally_twisted/locally_twisted/verify/product_blueprint_contract.py scripts/verify/product_blueprint_contract.py scripts/verify/product_blueprint_live_contract.py
node --check apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_product_blueprint/lt_product_blueprint.js
python scripts/verify/product_blueprint_contract.py
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend migrate
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend set-config lt_allow_local_blueprint_apply 1
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend clear-cache
python scripts/verify/product_blueprint_live_contract.py
```

Results:

- Pure product blueprint contract: PASS, 15 tests.
- JS syntax check: PASS.
- Local ERPNext migrate/cache refresh: PASS.
- Local `frontend` site config now permits local blueprint apply.
- Live product blueprint contract: PASS, rollback-safe. It proved Guest preview
  fails, Desk apply fails without the local-site flag, then Desk apply writes
  only the expected temporary local product records and rollback restores guard
  counts.

## Dynamic Blueprint Add-on Runtime Slice

Status: implemented locally after the Desk apply slice.

Blueprint-authored add-ons now cascade into the reusable product-page runtime
when all of these are true:

- the blueprint is applied and linked to the target Item;
- the product is a checkout-lane Website Item;
- the add-on row is `Checkout Approved`;
- the add-on row uses `Fixed Item Price`;
- the add-on row points at an enabled ERPNext Item with a Standard Selling Item
  Price.

The product option helper now merges those blueprint add-ons with the existing
static foil-number add-on contract. Checkout validation resolves the same
dynamic contract, preserves the add-on line into Sales Order Item payloads, and
honors the employee-entered quantity maximum instead of silently accepting an
oversized add-on quantity.

Additional verification run:

```bash
python -m py_compile apps/locally_twisted/locally_twisted/product_page_runtime.py apps/locally_twisted/locally_twisted/product_options.py apps/locally_twisted/locally_twisted/verify/product_blueprint_contract.py scripts/verify/product_blueprint_live_contract.py
python scripts/verify/product_blueprint_live_contract.py
```

Results:

- Live product blueprint contract: PASS, rollback-safe. The verifier creates a
  temporary support add-on Item/Item Price, applies a temporary blueprint with a
  checkout-approved add-on row, proves `get_checkout_add_on_options` exposes
  that add-on for the generated product, proves checkout line generation uses
  the add-on Item, and proves quantity above the blueprint maximum fails loudly.

## Current Status For Next Agent

This slice is a local product-authoring bridge, not a live catalog release. The
employee can now define a highly customizable product in Desk, see validation
evidence, preview the records that would be created, and apply that blueprint
locally into unpublished ERPNext product records. A fixed-price add-on entered
through the blueprint can cascade into product options and checkout validation
when it points at a valid ERPNext Item and Standard Selling Item Price.

Do not regress the framing: public ecommerce is locked because it is not ready
for customers. The lock is correct live safety posture and not a reason to stop
building the local ecommerce path.

## Remaining Work

- Add browser proof for an applied blueprint product page, cart line, checkout
  summary, and rollback-safe Sales Order / Sales Invoice preservation.
- Expand the self-service Desk UI for multi-slot color recipes, more add-on
  families, and conditional pricing so employees can author complex cases
  without code changes.
- Build the conditional pricing runtime and fail-loud quote/checkout behavior.
- Add media assignment fields and a dry-run/apply path that preserves approval
  evidence instead of guessing at images.
- Refresh import safety evidence before any staging/live product release, so a
  generated product is not confused with final public catalog truth.

## Backlinks

- Capability:
  `capabilities/recipes/erpnext-product-blueprint-authoring.md`.
- Receiving architecture:
  `capabilities/recipes/erpnext-ecommerce-receiving-architecture.md`.
- Ecommerce front door:
  `workstreams/ecommerce-audit/README.md`.
- Root shop handoff:
  `ECOMMERCE-SHOP-HANDOFF.md`.
