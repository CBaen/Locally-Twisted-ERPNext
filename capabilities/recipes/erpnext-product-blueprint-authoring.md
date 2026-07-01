---
id: erpnext-product-blueprint-authoring
name: ERPNext Product Blueprint Authoring
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted ERPNext staff-authored product setup for highly customizable ecommerce products
currently_true: true
verification_level: 2
last_verified: 2026-06-30
evidence_quality: direct
successful_uses: 4
failed_uses: 1
regressions: 1
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

## 2026-06-30 Live Authority Correction

Product Setup save success is not public product-change proof.

Live `large-head-missionary` proof showed the owner save worked:
`LT Product Blueprint` modified at `2026-06-30 01:43:01.382176` by
`locallytwisted@gmail.com`, Product Setup base price `125.0`, and all 30
Product Setup price rows `125.0`. The customer-facing price still rendered
`from $ 175.00` because the active `Standard Selling` Item Price rows stayed
`175.0`. Public copy rendered from Website Item custom fields, not Product
Setup top-level story/details fields.

Until a publish/apply contract or direct Product Setup runtime authority is
implemented, agents must treat Product Setup as an authoring surface with
incomplete live projection. Do not tell GL or the owner that a Product Setup
save changed the live shop unless Website Item, Item, Item Price, public route,
cart/checkout, and rollback proof support that claim.

Failure recipe:
`capabilities/failures/product-setup-projection-authority-drift.md`.

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
- Product Setup requires `operating_brand` with one of
  `locally_twisted`, `commercial_balloon_decor`, or `memorial_balloons`.
  Validation marks valid values as `source_declared`; this is not live proof
  and does not approve mutation, public projection, payment/document identity,
  or provider/customer action.
- Product Setups in active source authority statuses (`Local Preview Ready`,
  `Staging Ready`, or `Approved For Live`) must be unique per source-declared
  operating brand for the same slug, target Item, or target Website Item. This
  is a source save guard, not live/global uniqueness proof.
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
- For existing live products, Product Setup price/copy/media saves are not
  enough. The workflow must either directly power runtime fields or project
  into the Website Item, Item Price, media, cart, and checkout authorities
  through an explicit publish/apply step with no-write preview and rollback
  proof.
- Offline authority packets expose `source_authority` separately from live
  proof. `source_declared` operating brand and same-brand source uniqueness do
  not set active authority, mutation approval, deploy approval, cache approval,
  public route proof, payment/document identity, or release readiness.
- Runtime Product Setup lookup is brand-aware source/runtime protection:
  schema/API/gallery resolution requires explicit or source-declared
  `operating_brand`, checks target Item, target Website Item, and slug inside
  that brand, and fails closed on missing/invalid brand or active ambiguity
  instead of selecting by modified time.
- Active Product Setup validation includes runtime authority blockers for
  existing linked Website Items. Missing Website Item runtime brand fields,
  wrong `operating_brand`, missing `source_declared` state, or target
  Item/Website Item disagreement blocks active source states before preview,
  staging, live approval, or local apply can imply readiness.

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
- No-write Product Setup projection preview and parity verifier for existing
  live products, starting with `large-head-missionary`.
- Saved-artifact authority packets must report source-declared operating brand
  and same-brand source uniqueness separately from live brand/route proof.
- Variant-axis classification/collapse planning is still required before
  reducing the 10k-plus Item/Item Price shape. Do not delete, disable, rename,
  or repurpose existing variant records until dry-run dependency, rollback,
  historical-reference, and owner-scope approval pass.

2026-06-30 update: the first offline no-write tools are available:
`scripts/dev/lt_live_readonly_catalog_authority_audit.py`,
`scripts/dev/lt_product_setup_authority_packet_report.py`,
`scripts/dev/lt_product_setup_projection_preview.py`,
`scripts/verify/product_setup_authority_parity_contract.py`, and
`scripts/dev/lt_product_setup_catalog_blast_radius_report.py`. They consume
saved audit/projection JSON and intentionally fail on the known live drift
artifact. The catalog collector performs live read-only GETs to create saved
artifacts; the projection/parity/blast-radius tools remain offline. The first
full published-catalog collection processed 47 Website Items and found 47
Product Setup matches, 47 products with blockers, 47 unproved brand lanes, 19
Draft/inactive Product Setup authorities, and one product with 2,430 variants
/ 2,430 Item Prices. The authority packet report turns those artifacts into
47 blocked product packets and 284 explicit blockers. These tools do not
replace the future owner publish/apply workflow.

2026-06-30 Phase 5 update: Product Setup now has a source-level
`operating_brand` contract guarded by `scripts/verify/product_blueprint_contract.py`.
The field is required in the DocType, pure validation fails closed on
missing/invalid values, dry-run apply-plan output and runtime Product Setup
schema carry the source value, and generated catalog-sync Product Setups
default to `locally_twisted` as `source_declared`. This does not prove live
brand lane or repair public projection. See
`workstreams/ecommerce-operator-hardening-2026-06-30/phase-5-operating-brand-source-contract-2026-06-30.md`.

2026-06-30 Phase 5 follow-up: Product Setup source validation now blocks active
same-brand duplicates for the same slug, target Item, or target Website Item,
and runtime active lookup logs ambiguity and returns no setup when more than
one active record matches a runtime key. This keeps ambiguity loud without
claiming live repair, cross-brand route proof, or database-level uniqueness.

2026-06-30 Phase 6 update: offline authority packet reporting now carries
`source_authority.operating_brand` and
`source_authority.same_brand_source_uniqueness`, and the parity verifier can
consume packet reports. Old saved catalog artifacts remain blocked; the packet
contract only makes source evidence visible.

2026-06-30 Phase 7 update: runtime Product Setup lookup now uses explicit or
source-declared operating brand for schema/API/gallery resolution and fails
closed on missing/invalid brand, same-brand duplicates, invalid active Product
Setup brand, or target-item ambiguity. Website Item operating-brand custom
fields are seeded by `sync_commerce_rules` and registered for existing sites
through `sync_product_setup_brand_runtime_fields_20260630`. This does not
repair live public projection or prove live brand lane.

2026-06-30 Phase 8 update: Product Setup validation now surfaces runtime
authority blockers in Desk for active source states. Existing linked Website
Items must have installed operating-brand runtime fields, matching
source-declared brand metadata, and matching target identity before the Product
Setup can imply preview/staging/live/apply readiness. Drafts and new preview
plans with no existing Website Item are not blocked by this guard.

2026-06-30 Phases 9-12 update: Birthday Deliveries now has a source-only
hardening chain for variant collapse planning. Phase 9 classifies the current
2,430-variant shape into a blocked 3-SKU candidate model. Phase 10 captures
saved-artifact rollback rows and blockers. Phase 11 creates a no-write
replacement model. Phase 12 translates the replacement blockers into
owner-visible `Blocked - Proof Needed` readiness. None of these phases approve
live writes, cache clear, deploy, current variant disablement, or publish/apply.

Backlinks:

- `workstreams/ecommerce-audit/product-blueprint-authoring-2026-05-14.md`
- `workstreams/ecommerce-audit/owner-product-setup-guard-closeout-2026-05-22.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/live-readonly-api-audit-large-head-missionary-2026-06-30.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/phase-3-catalog-authority-audit-2026-06-30.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/phase-4-authority-packet-resolver-2026-06-30.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/phase-5-operating-brand-source-contract-2026-06-30.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/phase-7-runtime-brand-aware-lookup-2026-06-30.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/phase-8-owner-visible-runtime-authority-blockers-2026-06-30.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/phase-9-variant-axis-classification-birthday-deliveries-2026-06-30.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/phase-10-dependency-rollback-capture-birthday-deliveries-2026-06-30.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/phase-11-no-write-replacement-model-birthday-deliveries-2026-06-30.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/phase-12-owner-visible-publish-readiness-birthday-deliveries-2026-06-30.md`
- `workstreams/ecommerce-audit/README.md`
- `ECOMMERCE-SHOP-HANDOFF.md`
- `locally-twisted-decisions.md`
