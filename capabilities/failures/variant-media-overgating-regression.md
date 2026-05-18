---
name: Variant media overgating regression
type: failure
failure_kind: recurring_pattern
schema_version: 0.1
date_discovered: 2026-05-17
last_updated: 2026-05-17
status: guarded
scope: project
owner_context: Locally Twisted ERPNext ecommerce
related_capabilities:
  - erpnext-ecommerce-receiving-architecture
related_failures: []
tags:
  - ecommerce
  - media
  - variants
  - safety-gate
  - regression
---

# Failure Recipe: Variant media overgating regression

## Symptom

A product option still exists in ERPNext and has its own image, but the
customer-facing product page keeps showing the parent product image after the
variant is selected.

## Trigger Conditions

- A safety gate is added to stop unclassified images from rendering.
- The implementation treats every variant `Item.image` as unclassified media.
- The verifier is rewritten to enforce the new hold behavior without also
  protecting older known-good product behavior.

## Known Instances

| Date | Project | Surface | Action being taken | Bad outcome | Evidence | Guard state | Status |
|---|---|---|---|---|---|---|---|
| 2026-05-17 | Locally Twisted | Encanto Bouquet product page | Media-readiness hardening held unclassified extra images | Simple checkout size variant images were hidden even though `Item.image` was already mapped and customer-facing | `workstreams/ecommerce-audit/variant-item-media-restore-2026-05-17.md`; commits `019bf27`, `8e4a95b`; `scripts/verify/variant_media_contract.py` | positive/negative guard added | guarded |

## Root Pattern

An agent tried to satisfy a safety requirement by applying the hold at the
widest available level. That protected against one risk but erased a separate
approved behavior: simple checkout variant images are product-selection
evidence, not random gallery media.

## Why It Seemed Reasonable At The Time

The phrase "unclassified media" sounded broad, and the system already needed a
strong default for source extra images. Because complex Product Setup media did
need explicit approval, it was easy to collapse all variant images into that
same approval path.

## Detection Signals

- `get_variant_media` returns `held_back_variant_image: true` for a simple
  `simple_product|checkout` variant with a non-fallback `Item.image`.
- Product page image does not change after selecting a known size/design
  variant.
- A verifier says ready-to-order/simple variants should stay on fallback.
- User language: "this used to work," "the backend has the photos," or "good
  things were taken away."

## Required Guard

Any media safety hardening must include both sides:

- Positive guard: known simple checkout variants with approved `Item.image`
  must render on the product page and cascade to cart/order/receipt helpers.
- Negative guard: complex/custom raw Item images and source extra/gallery media
  must remain held until Product Setup or a classification packet approves
  them.

Current guard: `python scripts/verify/variant_media_contract.py`.

## Recovery Recipe

1. Confirm whether the image exists on the resolved Item variant.
2. Confirm the Website Item page type and commerce lane.
3. Check whether Product Setup media rules are present and approved.
4. For `simple_product|checkout`, restore direct variant `Item.image` as
   approved selected media.
5. For `complex_custom_product`, keep raw variant images held unless Product
   Setup media rules approve them.
6. Prove product page, cart, Sales Order payload, and receipt helper.
7. Update queue, decisions, lessons, handoff, capability evidence, and this
   Failure Recipe.

## What Not To Do

- Do not globally render every extra source image.
- Do not globally hold every variant Item image.
- Do not rewrite verifiers to bless a regression without checking prior docs,
  current backend data, and user-visible behavior.
- Do not treat "safety" as permission to remove customer-facing product
  meaning.

## Cross-Links

- Related capability: `capabilities/recipes/erpnext-ecommerce-receiving-architecture.md`
- Related handoff: `workstreams/ecommerce-audit/variant-item-media-restore-2026-05-17.md`
- Related decision: `locally-twisted-decisions.md`
- Related lesson: `lessons-learned.md`

## Evidence Quality

Verified locally against ERPNext API, the rendered Encanto product page, cart
resolver, Sales Order line payload helper, receipt image helper, and nearby
cart/runtime contracts. Live remains unmodified.
