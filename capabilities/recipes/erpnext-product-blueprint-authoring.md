---
id: erpnext-product-blueprint-authoring
name: ERPNext Product Blueprint Authoring
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted ERPNext staff-authored product setup for highly customizable ecommerce products
currently_true: true
verification_level: 2
last_verified: 2026-05-22
evidence_quality: direct
successful_uses: 4
failed_uses: 0
regressions: 0
used_by:
  - Codex
  - OpenClaw
depends_on:
  - erpnext-ecommerce-receiving-architecture
  - fail-loud-operating-law
tags:
  - Locally Twisted
  - ERPNext
  - Frappe
  - ecommerce
  - product authoring
  - custom products
  - local only
---

# ERPNext Product Blueprint Authoring

Use this when adding or changing Locally Twisted products that need employee
authoring in ERPNext instead of developer-coded product packets.

## Rule

Staff-facing product setup belongs in `LT Product Blueprint`. legacy_source product
records are useful witnesses for behavior, but the architecture must support
highly customizable products beyond the exact legacy_source catalog that happened to
exist. The blueprint is the local bridge from employee-entered product meaning
to ERPNext Items, Website Items, prices, options, add-ons, and future
conditional pricing/media flows.

`lt_ecommerce_paused=1` is a live/customer exposure safety lock. It is not a
reason to stop local product-authoring, cart, checkout, pricing, media, or
verifier work. For local build work, name the actual blocker.

## Current Contract

- Employees create a Desk `LT Product Blueprint` record with product basics,
  options, color recipes, add-ons, and conditional pricing rows.
- Validation maps employee labels to the architecture contract:
  `simple_product`, `complex_custom_product`, `checkout`, `quote_first`,
  `needs_review`, `selected_options`, `color_recipes`, `add_ons`, and
  `quote_context`.
- Drafts may save while blocked so staff can work incrementally. Moving blocked
  records to preview/staging fails loudly.
- `Approved For Live` is blocked in this local slice.
- Dry-run preview writes no product records and names the intended Item,
  Website Item, attribute, variant, price, add-on, and held-media work.
- Local apply is guarded by role, site config, and server-only confirmation:
  `System Manager` or `Item Manager`, `lt_allow_local_blueprint_apply=1`, and
  the server-held `LOCAL_ONLY_BLUEPRINT_APPLY` token.
- Local apply keeps Website Items unpublished and creates no Sales Orders,
  Sales Invoices, Payment Requests, Stripe records, Frappe Cloud updates, DNS
  changes, or live publish actions.
- For existing Website Items, local apply preserves the current public
  `published` state instead of forcing a new value. Hidden->visible,
  public->hidden, and public route-change requests for existing Website Items
  are blocked; those changes require the reviewed release/redirect path.
- Blueprint-authored checkout add-ons currently cascade only when they are
  checkout-approved fixed-item-price rows pointing at an enabled Item with a
  Standard Selling Item Price. Quantity min/max is enforced by checkout
  validation.
- The real owner account `locallytwisted@gmail.com` can create and locally
  apply a Product Blueprint through the guarded Product Setup path. The owner
  profile does not need raw `Website Item` DocPerm access; generated Website
  Items are created unpublished by the server-side helper after the owner passes
  Product Setup role and local-site gates.
- Product-create capability now covers both `Item Manager` and `System Manager`
  local apply paths without raw Website Item profile access. The server helper
  owns generated Website Item creation.
- Approved media can be keyed to one selection group/value or to an explicit
  selection combination. The server-resolved `selected_media` value is the
  authority for the product page API, cart, checkout, Stripe Checkout line
  images, Sales Order/Sales Invoice line JSON, and customer receipt thumbnail.
- Stored option values and customer display labels are separate concerns.
  Product pages may keep stored source values for backend matching while
  rendering short selected labels and intentional included-copy detail.
- Product Setup exact checkout price rows must belong to the Product Setup's
  target Item or variants. Cross-product Item Price targets are save blockers.
- Backfilled Product Setup records stay Draft until reviewed so they do not
  silently take over runtime checkout behavior.

## Workflow

1. Create or edit the `LT Product Blueprint` in Desk.
2. Resolve validation blockers until the record is `Ready For Local Preview`.
3. Use `Preview Local Apply` and read the planned record counts/blockers.
4. Use `Apply Locally` only on the local `frontend` site when the temporary
   product needs ERPNext runtime proof.
5. Run the pure and rollback-safe verifiers below before trusting the generated
   product records.
6. Keep generated Website Items unpublished until browser, cart, checkout,
   pricing, media, and staging gates prove the product family.

## Verification

```powershell
python scripts/verify/product_blueprint_contract.py
python scripts/verify/product_blueprint_live_contract.py
python scripts/verify/product_page_runtime_contract.py
python scripts/verify/product_add_on_dependency_contract.py
python scripts/verify/product_page_architecture_contract_contract.py
python scripts/verify/cart_checkout_contract.py
python scripts/verify/stripe_amount_parity_contract.py
python scripts/verify/payment_cascade_contract.py
python scripts/verify/ecommerce_pause_contract.py
python scripts/verify/product_page_architecture_readiness.py --json
python scripts/verify/verifier_cli_contract.py
python scripts/verify/product_setup_catalog_coverage.py
python scripts/verify/catalog_public_sellability_contract.py
python scripts/verify/owner_catalog_guard_contract.py
npm run test:owner-product-safety
```

Expected current result: product blueprint pure/live contracts pass;
`product_page_architecture_readiness.py --json` reports
`technical_architecture_ok=true` and `import_reopen_ok=false` while the public
exposure lock is on. That false `import_reopen_ok` is expected local safety
posture, not a local product-authoring blocker.

The live contract now includes owner-profile Product Setup proof:
`locallytwisted@gmail.com` creates and applies a rollback-safe local product
with two SKU variants, two Item Prices, and an unpublished Website Item.

The 2026-05-22 owner-guard closeout adds focused proof that owner-like raw
catalog mutation is blocked across `19/19` probes, existing public Website
Items keep their visibility during local apply, public hide/route changes fail
loudly, and Product Setup catalog sync reports `51` Website Items with `0`
creates and `21` would-update rows. Final pre-commit
`npm run test:owner-product-safety` and
`npm run test:product-options-experience` passed. Handoff:
`workstreams/ecommerce-audit/owner-product-setup-guard-closeout-2026-05-22.md`.

The 2026-05-17 release smoke created a local employee-authored 48-variant proof
product and completed one real local Stripe test-card checkout. Verified
selected image chain:
`/files/lt-proof-large-chrome.png` on product page -> cart -> checkout ->
Sales Order line JSON -> Stripe Checkout line image -> customer receipt email.
Local ecommerce was restored to `lt_ecommerce_paused=1` afterward.

## Remaining Work

- Richer self-service UI for multi-slot color recipes, complex add-on families,
  and conditional pricing.
- Conditional pricing runtime and fail-loud checkout/quote behavior.
- Broader media assignment review UI and approval evidence for real catalog
  product families beyond the local proof product.
- Owner/GL local workflow testing before staging.
- Fresh import safety evidence before any staging/live product release.

Backlinks:

- `workstreams/ecommerce-audit/product-blueprint-authoring-2026-05-14.md`
- `workstreams/ecommerce-audit/owner-product-setup-guard-closeout-2026-05-22.md`
- `workstreams/ecommerce-audit/README.md`
- `ECOMMERCE-SHOP-HANDOFF.md`
- `locally-twisted-decisions.md`
