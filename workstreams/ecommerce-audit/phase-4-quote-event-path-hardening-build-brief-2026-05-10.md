D:2026-05-10 | Check:Phase 3 closure + Phase 2 classifications 2026-05-10 | Confidence:high
# Phase 4 quote/event path hardening build brief

## Objective

Prove complex/event and needs-review products remain quote-first examples and cannot enter paid checkout through:

- product-page controls,
- cart API resolution,
- direct `/checkout?item=...` URLs,
- stale/localStorage-style cart payloads that lie about `commerce_lane: checkout`.

## Scope

Use the Phase 2 classified product sets:

- `QUOTE_FIRST`: 33 complex/custom/event products, expected `complex_custom_product|quote_first`.
- `HIDE_OR_NEEDS_REVIEW`: 5 products, expected `needs_review|needs_review`.

Phase 4 does not open public ecommerce, process live payment, mutate catalog_data, approve hidden/seasonal products, or convert quote-first decor into direct checkout.

## Build actions

1. Harden runtime contract precedence so explicit `needs_review` Website Item fields are honored instead of falling back to inferred checkout from item group hints.
2. Harden cart API sale resolution so anything not explicitly `commerce_lane == checkout` fails as quote-required.
3. Add a rollback-safe verifier:
   - `apps/locally_twisted/locally_twisted/verify/quote_event_checkout_boundary_contract.py`
   - `scripts/verify/quote_event_checkout_boundary_contract.py`
4. The verifier must prove product-page template routing, cart API blocking, direct checkout URL blocking, stale localStorage blocking, and zero business-record deltas.

## Required gates

- `python -m py_compile apps/locally_twisted/locally_twisted/product_page_runtime.py apps/locally_twisted/locally_twisted/api\cart.py apps/locally_twisted/locally_twisted/verify\quote_event_checkout_boundary_contract.py scripts/verify/quote_event_checkout_boundary_contract.py`
- `python scripts/verify/quote_event_checkout_boundary_contract.py --report output/phase-4-quote-event-checkout-boundary-contract-20260510.json`
- Regression gates:
  - `python scripts/verify/product_page_runtime_contract.py`
  - `python scripts/verify/checkout_product_family_contract.py --report output/phase-3-checkout-product-family-contract-20260510.json`
  - `python scripts/verify/website_item_classification_contract.py --report output/phase-4-website-item-classification-contract-20260510.json`
  - `python scripts/verify/checkout_fulfillment_contract.py`
  - `python scripts/verify/customer_note_checkout_preservation_contract.py`

## Review lenses

After parent-run gates pass, request separated reviews:

- Architecture: Does the boundary belong in runtime/cart resolution and not just templates?
- Edge cases: Does the verifier cover direct URL, stale localStorage, needs-review fallback, and all classified rows?
- Security/ops: Does the verifier remain read-only/rollback-safe, avoid PII/live payment/customer messages/catalog_data mutation, and keep public ecommerce paused?
