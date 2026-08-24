---
name: Product Fulfillment Copy Lane Drift
type: failure
failure_kind: recurring_pattern
schema_version: 0.1
date_discovered: 2026-05-20
last_updated: 2026-05-20
status: guarded-local
scope: project
owner_context: Locally Twisted ERPNext/Frappe product pages
related_capabilities:
  - frappe-product-page-company-first
  - frappe-product-clear-control-contract
related_failures:
  - ecommerce-variant-price-source-drift
  - variant-media-overgating-regression
tags:
  - ERPNext
  - Frappe
  - ecommerce
  - product-page
  - fulfillment
  - quote-first
  - verifier-gap
---

# Failure Recipe: Product Fulfillment Copy Lane Drift

## Symptom

A product page correctly blocks direct checkout or renders quote-first controls,
but another visible panel still promises checkout pickup/delivery behavior.

The user-facing risk is false success: the customer sees copy that implies a
normal checkout path even though the product is quote/install reviewed.

## Trigger Conditions

- Product page behavior reads the Website Item runtime contract.
- A secondary panel, helper, or copy block still reads Item Group/category
  fallback.
- A verifier checks controls, price, media, or cart behavior but not the visible
  customer promise text.
- A complex or needs-review product remains visible and priced while direct
  checkout is intentionally blocked.

## Known Instances

| Date | Project | Surface | Action being taken | Bad outcome | Evidence | Guard state | Status |
|---|---|---|---|---|---|---|---|
| 2026-05-20 | Locally Twisted | Classic Arch product page | Local product-page design/logic review before staging | Runtime contract was `complex_custom_product|quote_first`, but fulfillment copy still said "Pickup is requested at checkout" | `workstreams/ecommerce-audit/product-page-local-review-2026-05-20.md`; `scripts/verify/smoke_shop.py` | quote-first copy guard added | guarded-local |

## Root Pattern

The product page had more than one authority source. The main product contract
used the record-level Website Item runtime lane, while the fulfillment copy
used category fallback. That made the page internally contradictory.

## Detection Signals

- A quote-first or needs-review page contains "checkout" in pickup/delivery
  copy.
- A page has no add-to-cart controls but still talks about checkout pickup.
- `public_fulfillment_panel` or similar helper accepts only Item Group/category.
- Verifier proof says "quote-first controls passed" but does not assert visible
  customer promise text.

## Required Guard

For LT product pages:

- `python scripts/verify/smoke_shop.py`
- `python scripts/verify/product_page_runtime_contract.py`
- `python scripts/verify/proof_product_contract.py`

`smoke_shop.py` must assert that quote-first product pages do not show checkout
pickup copy and do show quote/install language.

## Recovery Recipe

1. Confirm the resolved Website Item runtime product type and commerce lane.
2. Identify every visible customer promise panel on the product page.
3. Make those panels read the runtime lane before any category fallback.
4. Keep category fallback only as a fallback for records without explicit
   product contract data.
5. Add a browser or smoke assertion for the visible copy, not only the behavior.
6. Re-run product runtime, proof product, shop smoke, and layout gates.
7. Update the active handoff, queue, decision, lesson, and this Failure Recipe.

## What Not To Do

- Do not treat checkout copy as harmless because add-to-cart is hidden.
- Do not trust Item Group/category as the first authority when Website Item
  contract fields exist.
- Do not apply broad classification changes to make a verifier pass before
  checking the current product/business model.
- Do not promote a page to staging while visible copy contradicts runtime
  behavior.

## Cross-Links

- Related handoff: `workstreams/ecommerce-audit/product-page-local-review-2026-05-20.md`
- Related recipe: `capabilities/recipes/frappe-product-page-company-first.md`
- Related recipe: `capabilities/recipes/frappe-product-clear-control-contract.md`
- Related decision: `locally-twisted-decisions.md`
- Related lesson: `lessons-learned.md`

## Evidence Quality

Verified locally on 2026-05-20 against the Classic Arch product page, runtime
contract, proof product report, shop smoke gate, and focused product layout
gate. Staging/live are not verified by this recipe.
