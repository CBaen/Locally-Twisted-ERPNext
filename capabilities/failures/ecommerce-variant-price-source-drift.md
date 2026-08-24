---
name: Ecommerce Variant Price Source Drift
type: failure
failure_kind: recurring_pattern
schema_version: 0.1
date_discovered: 2026-05-19
last_updated: 2026-06-30
status: guarded
scope: project
owner_context: Locally Twisted ERPNext/Frappe ecommerce catalog
related_capabilities:
  - erpnext-catalog-variant-price-parity
  - erpnext-checkout-commerce-rules
related_failures:
  - variant-media-overgating-regression
  - product-setup-projection-authority-drift
tags:
  - ERPNext
  - ecommerce
  - pricing
  - variants
  - import
  - verifier-gap
---

# Failure Recipe: Ecommerce Variant Price Source Drift

## Symptom

A product page, cart, checkout, Stripe session, Sales Order, or invoice appears
internally consistent, but the amount is wrong because the backend sellable Item
has the wrong `Item Price`.

The user-facing sign can be simple: a size, height, length, LED, topper, design,
or add-on option does not change price when the source shop charged a different
amount.

## Trigger conditions

- A catalog import copies page base price, JSON-LD price, card price, or current
  local ERPNext snapshot price into every variant.
- A verifier checks only that variants exist and have prices.
- A downstream verifier checks only that ERPNext and Stripe agree with each
  other.
- Dynamic option pricing exists, but the import treats the exported product row
  as the full pricing source.
- A one-family fix, such as bouquet sizes, gets treated as whole-catalog proof.

## Known instances

| Date | Project | Surface | Action being taken | Bad outcome | Evidence | Guard state | Status |
|---|---|---|---|---|---|---|---|
| 2026-04-30 to 2026-05-19 | Locally Twisted | catalog_data-to-ERPNext catalog import and Webshop product pages | Importing catalog_data catalog into ERPNext Items, variants, and Item Prices | Non-bouquet variant families flattened many active variant `Item Price` rows to base price; Easter Bunny Ear Arch `25ft` showed `$375` instead of `$440` | `workstreams/ecommerce-price-identity-incident-review-2026-05-19.md`; `workstreams/catalog-variant-price-recovery.md`; `9aa117f`; local `product_price_modifier_contract.py` repair evidence | added | guarded-local |
| 2026-06-30 | Locally Twisted | live Product Setup to public runtime authority | Owner changed `large-head-missionary` Product Setup prices from `175` to `125` and saved successfully | Product Setup base/exact prices were `125.0`, but live sellable `Item Price` rows and public price stayed `175.0` | `workstreams/ecommerce-operator-hardening-2026-06-30/live-readonly-api-audit-large-head-missionary-2026-06-30.md`; `capabilities/failures/product-setup-projection-authority-drift.md` | needs new projection guard | active |

## Root pattern

The system proved identity shape and downstream consistency before proving
source price truth. Once ERPNext `Item Price` was wrong, every properly designed
downstream layer preserved that wrong value.

The 2026-06-30 live Product Setup incident is adjacent but distinct: source or
owner intent reached Product Setup, but Product Setup did not project to the
sellable `Item Price` rows that the public page, cart, checkout, and documents
trust.

## Why it seemed reasonable at the time

ERPNext's own architecture makes `Item Price` the right runtime authority.
Therefore cart, checkout, accounting, and Stripe code that ignored browser
prices looked correct. The hidden mistake was earlier: treating an imported
base price as if it were the complete per-variant price matrix.

## Detection signals

- Docs or comments say "base price applies to all combos."
- Verifier names mention variant shape, checkout, Stripe parity, or price
  readiness but do not call the source dynamic-price resolver.
- Product families have many variants but only one active price point.
- A source catalog has priced option axes such as size, height, length, LED,
  topper, design, or add-on choices.
- A known non-first option is not selected in browser proof.
- Launch proof says Stripe matches ERPNext without proving ERPNext matches
  source price truth first.

## Required guard

For LT's catalog_data-derived catalog:

- `python scripts/verify/product_price_modifier_contract.py`
- `npm run test:product-prices`
- `npm run test:product-price-display`

Before release or import closeout, pair those with:

- `python scripts/verify/catalog_variant_contract.py`
- `python scripts/verify/cart_checkout_contract.py`
- `node scripts/verify/post_import_checkout_proof.js`
- `python scripts/verify/stripe_amount_parity_contract.py`

The order matters: source-to-ERPNext price truth must pass before downstream
ERPNext/Stripe parity can mean anything.

## Recovery recipe

1. Stabilize the reported product by comparing source dynamic price and local
   ERPNext `Item Price`.
2. Record the exact wrong variant and source-correct amount before repairing.
3. Identify whether the guard was missing, weak, bypassed, or only family-scoped.
4. Repair the smallest safe visible path first.
5. Expand to the full active variant set through a dry-run-first source-price
   modifier repair.
6. Add launch/import guards so the class cannot be reintroduced by another
   catalog import.
7. Revalidate with source-price, browser visible-price, cart, checkout, and
   payment/accounting proof.
8. Update queue, workstream, capability, decision, and lesson docs.

## What not to do

- Do not call a price table "correct" because every variant has an Item Price.
- Do not call a purchase flow "correct" because Stripe matches ERPNext.
- Do not treat a source page base price as the variant matrix.
- Do not fix only the product GL noticed and leave the import path unguarded.
- Do not downgrade this to a cosmetic product-page bug.
- Do not treat Product Setup price save success as Item Price/public runtime
  proof. Load `product-setup-projection-authority-drift` for owner-save
  incidents.

## Cross-links

- Related capability: `capabilities/recipes/erpnext-catalog-variant-price-parity.md`
- Related workstream: `workstreams/erpnext-ecommerce-receiving-architecture.md`
- Related workstream: `workstreams/ecommerce-price-identity-incident-review-2026-05-19.md`
- Related workstream: `workstreams/catalog-variant-price-recovery.md`
- Related verifier: `scripts/verify/product_price_modifier_contract.py`
- Related verifier: `scripts/verify/product_price_display.spec.js`

## Evidence quality

Verified locally on 2026-05-19: the reported Easter Bunny Ear Arch price now
matches catalog_data source pricing on the product page and cart API, and the broad
modifier dry-run reports 0 remaining active variant price changes across 49
variant products / 10,186 active variants. Staging/live are not verified by this
recipe.
