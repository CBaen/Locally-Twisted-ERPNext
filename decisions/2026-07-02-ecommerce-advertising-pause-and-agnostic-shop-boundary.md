# 2026-07-02 - Ecommerce Advertising Pause And Agnostic Shop Boundary

## Decision

Do not treat the current LT ecommerce shop as advertising-ready.

Do not use LT's current ecommerce implementation as the architecture for the
reusable ecommerce shop. The reusable ERPNext ecommerce shop must be built
first as a project-agnostic parent template. LT products should migrate into
that template only after the template is correct.

## Trigger

During emergency live checks for `large-head-missionary` and
`birthday-deliveries`, GL concluded that advertising into the current shop is
too risky. The live fixes proved selected customer-facing paths can be held
together temporarily, but they also exposed the broader failure class:
backend product edits, public pages, variant selectors, add-ons, Item Prices,
and cart behavior are not governed by one trustworthy shop contract.

## Reasoning

The correct target is not "LT ecommerce with better patches." The target is a
clean, reusable ecommerce shop that can fit any ERPNext client and only later
receive LT as one migrated implementation.

LT's current shop contains known emergency bridges, Product Setup projection
drift, variant explosion, and authority splits. Those facts make LT useful as a
failure-test source, not as a template.

## Current Emergency State

`large-head-missionary` was repaired live to `$125` in the public page and
Item Price/cart proof path.

`birthday-deliveries` was temporarily bridged so customers see
`ADD BIRTHDAY AGE` as a number input and the old `Add Foil Number` native
selector is hidden while current ERPNext variants still resolve.

The focused live verifier
`scripts/verify/ad_product_live_stability.spec.js` passed 11 tests against
`https://locallytwisted.com` on 2026-07-02. This verifier is a smoke alarm and
temporary holding guard. It is not proof that the catalog is advertising-safe.

## Required Next Architecture

Build the parent template first:

- parent charter:
  `/home/guidingl/projects/Built_by_Cameron/_TEMPLATES/agnostic-erpnext-ecommerce-shop/README.md`
- parent capability:
  `/home/guidingl/projects/Built_by_Cameron/capabilities/recipes/agnostic-erpnext-ecommerce-shop-template.md`

The template must define product creation, pricing, public copy, image
authority, main-image selection, options, add-ons, SKU-defining variant axes,
configuration-only fields, cart/checkout parity, publish/readiness state, and
advertising-readiness proof without deriving those contracts from LT's current
implementation.

## Guards

- Do not launch LT advertising campaigns that depend on ecommerce product-page
  checkout confidence until the agnostic shop/migration path is accepted or GL
  gives a narrower explicit exception.
- Do not describe LT emergency repairs as the ecommerce architecture.
- Do not call the reusable shop a generalized LT shop.
- Do not migrate LT products into the new shop until the parent template is
  correct.

## Receipts

- `workstreams/ecommerce-operator-hardening-2026-06-30/emergency-live-repair-ad-products-2026-07-01.md`
- `scripts/verify/ad_product_live_stability.spec.js`
- Parent template charter and capability named above.

## Decided By

Guiding Light corrected the framing on 2026-07-02. Codex documented the
project and parent boundaries.
