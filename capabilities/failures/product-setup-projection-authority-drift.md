---
name: Product Setup Projection Authority Drift
type: failure
failure_kind: recurring_pattern
schema_version: 0.1
date_discovered: 2026-06-30
last_updated: 2026-06-30
status: active_guard_needed
scope: project
owner_context: Locally Twisted ERPNext/Frappe ecommerce Product Setup and public shop projection
related_capabilities:
  - erpnext-product-blueprint-authoring
  - erpnext-ecommerce-receiving-architecture
  - erpnext-catalog-variant-price-parity
related_failures:
  - ecommerce-variant-price-source-drift
  - product-primary-media-attachment-drift
  - product-gallery-projection-regression
tags:
  - ERPNext
  - ecommerce
  - Product Setup
  - owner workflow
  - pricing
  - public projection
  - fail-loud
---

# Failure Recipe: Product Setup Projection Authority Drift

## Symptom

An authorized backend user edits and saves a product in `LT Product Blueprint`
or Product Setup, receives a normal saved confirmation, but the customer-facing
shop still shows old price, copy, media, availability, option, or add-on truth.

The important sign is not only "the public page is stale." The backend save can
be real while the website, cart, checkout, and documents read different
authority records.

## Confirmed Instance

On 2026-06-30, GL changed `large-head-missionary` on live
`locallytwisted.com`:

- Product Setup base price and all visible price rows were changed from `175`
  to `125`.
- Base Checkout Price was toggled `125 -> 120 -> 125`.
- Each save produced a saved confirmation.
- The most recent save was around 1:43 AM America/Denver by
  `locallytwisted@gmail.com`.

Live authenticated read-only API proof confirmed:

- `LT Product Blueprint` `large-head-missionary` modified
  `2026-06-30 01:43:01.382176` by `locallytwisted@gmail.com`.
- Product Setup `base_price` is `125.0`.
- 30 Product Setup price rows are all `125.0`.
- 30 live `Standard Selling` `Item Price` rows are all still `175.0`.
- Public page still renders `from $ 175.00`.
- Public copy renders from Website Item fields, not top-level Product Setup
  story/details fields.

Receipt:

- `workstreams/ecommerce-operator-hardening-2026-06-30/live-readonly-api-audit-large-head-missionary-2026-06-30.md`

## Root Pattern

Product Setup is currently an owner-editable authoring surface, but it is not
the complete write-through authority for every public/runtime commerce field.

For the confirmed product:

- owner save wrote Product Setup rows;
- public/customer price resolved through `Item Price`;
- public/customer copy resolved through Website Item custom fields;
- cart and checkout pricing are designed to trust sellable ERPNext price rows,
  not browser or Product Setup-only values.

## Why It Seemed Reasonable

The old safety design intentionally protected raw ERPNext catalog records and
made Product Setup the safer owner surface. That was correct as a direction,
but incomplete as a live operating workflow. A protected raw catalog plus an
incomplete Product Setup projection path creates false success: the owner can
save business meaning without changing the customer-facing authority.

## Detection Signals

- A Desk save succeeds, but public route HTML or public API still shows old
  data.
- Product Setup `modified`/`modified_by` is newer than Website Item, Item,
  Item Price, slideshow, or File attachment rows.
- Product Setup price rows disagree with `Standard Selling` Item Prices for
  active sellable Items.
- Product Setup story/details disagree with `Website Item.lt_brand_description`
  or `Website Item.lt_product_details`.
- Product Setup status says preview/review while public runtime embeds Product
  Setup data that does not drive the visible page.
- A verifier checks Product Setup only, or checks public page only, but not the
  projection chain between them.

## Required Guard

Do not treat Product Setup save success as public product change success.

Every owner-facing product edit path must choose one of two explicit models:

1. Product Setup is the direct runtime authority for that field; or
2. Product Setup is a draft/review/publish authority that must project to named
   runtime records through an explicit apply step.

Either model must fail loudly when Product Setup and public/runtime authority
disagree.

Minimum guard for price/copy:

- Product Setup row and relevant child rows.
- Website Item public copy fields.
- Item template and active variant Items.
- `Standard Selling` Item Price rows.
- Public product page visible price and copy.
- Cart/checkout resolver proof where the product is checkout-enabled.
- Modified timestamps and modified_by values for every authority row.

## Recovery Recipe

1. Capture read-only live evidence before any cache clear or write.
2. Confirm whether the owner save reached Product Setup.
3. Compare Product Setup fields/child rows to the public runtime authorities:
   Website Item, Item, Item Price, Website Slideshow, File attachment, cart
   resolver, and checkout resolver.
4. Classify the mismatch as save failure, projection failure, authority split,
   cache, or release drift. Do not call it cache unless row evidence supports
   that.
5. Build a no-write preview that names the exact rows and fields that would
   change.
6. Capture rollback targets for every affected live row.
7. Apply only through an approved Product Setup publish/apply contract or an
   explicitly approved repair packet.
8. Prove the public route/API/cart/checkout path after mutation.
9. Update Product Setup status so the owner sees whether the change is draft,
   blocked, approved, or live.

## What Not To Do

- Do not hand-patch one product and call the architecture fixed.
- Do not weaken the owner catalog guard to make raw Desk edits easier.
- Do not tell the owner a saved Product Setup is live unless public/runtime
  proof exists.
- Do not clear cache before read-only row evidence unless the task is explicitly
  cache-only and rollback risk is understood.
- Do not rely on downstream Stripe/payment parity before proving Product Setup
  or source price authority reached `Item Price`.

## Current Required Next Work

- Build a catalog authority resolver/packet layer on top of the full-catalog
  saved-artifact set.
- Run the parity verifier across saved audit/projection artifacts; it must fail
  when Product Setup active price/copy differs from public/sellable authority
  or when brand lane / active authority proof is missing.
- Decide and implement the owner workflow: explicit publish/apply contract or
  direct Product Setup runtime authority per field.
- Extend the catalog-wide report to list every published product with Product
  Setup-vs-runtime price, copy, media, option, add-on, and cart eligibility
  status.

## 2026-06-30 No-Write Tooling

Initial offline tools exist:

- `scripts/dev/lt_live_readonly_catalog_authority_audit.py`
- `scripts/dev/lt_product_setup_authority_packet_report.py`
- `scripts/dev/lt_product_setup_projection_preview.py`
- `scripts/verify/product_setup_authority_parity_contract.py`
- `scripts/dev/lt_product_setup_catalog_blast_radius_report.py`

Against the saved live audit artifact for `large-head-missionary`, the
projection preview reports 30 Item Price changes from `175.0` to `125.0`, two
Website Item copy suggestions, rollback targets for the current Item Price
rows, and limitations for brand lane, active Product Setup uniqueness, rollback
snapshot completeness, and business copy approval. The parity verifier fails
on both the audit and projection artifacts. The blast-radius helper marks the
product risky from saved artifacts only.

These tools are proof and planning surfaces. They are not repair approval,
cache approval, deploy approval, or live mutation approval.

The first full live read-only published-catalog collection on 2026-06-30 wrote
47 saved product artifacts and intentionally failed loudly: all 47 published
Website Items matched Product Setup records, but all 47 products had blockers.
Brand lane was unproved for 47 products, and 19 matched Product Setups were in
Draft/inactive authority status. One product had 2,430 variants and 2,430 Item
Price rows, proving that the variant-explosion issue is catalog-scale. See
`workstreams/ecommerce-operator-hardening-2026-06-30/phase-3-catalog-authority-audit-2026-06-30.md`.

The follow-up offline authority packet report intentionally blocks all 47
published products with 284 blockers. The dominant blockers are unproved brand
lane, unproved active uniqueness, missing public-route proof, missing
pre-mutation rollback packet, media-role proof gaps, inactive Product Setup
authority, ambiguous base-price-to-many-variant mapping, and variant explosion.
See
`workstreams/ecommerce-operator-hardening-2026-06-30/phase-4-authority-packet-resolver-2026-06-30.md`.
