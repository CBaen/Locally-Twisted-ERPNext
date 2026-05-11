# Phase 3 edge-case review — checkout product-family proof — 2026-05-10

## Verdict: PASS

The current repo state passes the Phase 3 edge-case lens for the approved bouquet family + Mother's Day simple path, with Easter explicitly deferred. I did not mutate production code. I did run the rollback verifier and wrote/confirmed `output/phase-3-checkout-product-family-contract-20260510.json`.

## Evidence inspected

- `apps/locally_twisted/locally_twisted/verify/checkout_product_family_contract.py`
- `apps/locally_twisted/locally_twisted/product_page_runtime.py`
- `apps/locally_twisted/locally_twisted/api/cart.py`
- `apps/locally_twisted/locally_twisted/www/checkout.py`
- `apps/locally_twisted/locally_twisted/product_options.py`
- `apps/locally_twisted/locally_twisted/verify/product_add_on_dependency_contract.py`
- `scripts/verify/checkout_product_family_contract.py`
- `scripts/verify/product_add_on_dependency_contract.py`
- `workstreams/ecommerce-audit/phase-3-product-family-proof-build-brief-2026-05-10.md`
- `workstreams/ecommerce-audit/ready-to-order-product-candidate-list-2026-05-10.md`
- `workstreams/ecommerce-audit/ecommerce-product-proof-matrix-2026-05-10.md`
- `output/phase-3-checkout-product-family-contract-20260510.json`

## Gates run

- `python scripts/verify/checkout_product_family_contract.py --report output/phase-3-checkout-product-family-contract-20260510.json --json` — PASS
  - `ok: true`
  - `bouquet_family_count: 13`
  - `sales_order_line_count: 27`
  - `expected_sales_order_line_count: 27`
  - `rolled_back: true`
  - `survivor_counts: {customer: 0, sales_order: 0, sales_invoice: 0}`
- `python scripts/verify/product_add_on_dependency_contract.py --json` — PASS
  - confirmed add-on remains only `Add Foil Number`
  - review-only source add-ons remain quote-blocked: `Add Bouquet`, `Add ons`, `Orbz toppers`, `Plush add ons`

## Edge-case findings

### Missing family members

PASS. The verifier's `EXPECTED_FOIL_BOUQUET_WEBSITE_ITEMS` matches the approved bouquet rows in the candidate/proof docs:

- Unicorn, Mickey Mouse, Minion, Encanto, Stitch, Flamingo, Football, Soccer, Space, Over the Hill, Paw Patrol, Elsa, Holy COW!!

The rollback verifier resolved all 13 as published `simple_product|checkout` Website Items and found one enabled Small variant for each.

### Variant option matching

PASS. Runtime Sales Order payloads use server-resolved variant attributes, not client-trusted labels. The verifier confirms the stored base-line `selected_options` match the resolved variant's `Bouquet Size` for every family member.

Stale/mismatched known attributes are rejected by `_assert_client_options_match_variant`; old schema payloads are rejected by `normalize_client_configuration`.

### Foil-number pricing and quantity

PASS. Phase 3 verifier confirms the approved add-on scope and server-side `$12` Item Price, then creates one priced add-on line per bouquet. The add-on dependency contract separately proves multi-digit value handling (`"12"` => quantity `2`) and rate preservation.

No client price/rate is accepted into the base payload; add-on lines price from ERPNext Item Price.

### Mother's Day no-add-on path

PASS. Mother's Day resolves as a simple single-SKU checkout line, exposes zero checkout add-ons, stores one backend line, and preserves LT configuration fields without add-on payload.

### Easter seasonal deferral

PASS. The verifier reports Easter Balloon Cups as `deferred_pending_seasonal_approval` and does not claim launch/orderability approval. Current inspected output shows it exists and is published as `simple_product|checkout`, but the proof correctly keeps seasonal visibility/orderability outside this Phase 3 claim.

### Stale cart / direct checkout risks

PASS for Phase 3 scope.

- Cart JSON entries are schema-normalized and line-keyed by item + configuration.
- Old/invalid configuration formats fail loudly.
- Submitted checkout lines are re-resolved server-side before Sales Order creation.
- Quote-first products are rejected in cart/checkout resolution before paid order creation.
- Direct buy-now URLs without configuration can only buy the resolved base SKU; they cannot smuggle add-ons or client prices.

### `needs_review` / `quote_first` boundaries

PASS. The product-family verifier checks foil add-on scope does not leak to Mother's Day or Birthday Deliveries. The dependency verifier confirms review-only add-on axes remain quote-blocked and are not priced checkout add-ons.

## Risks / follow-ups

No blocking fixes found for Phase 3.

Non-blocking hardening idea: add one negative test to the Phase 3 or adjacent cart contract for a deliberately stale configuration with an extra unknown `selected_options` key, documenting that server-resolved variant attributes are authoritative and unknown client option labels are ignored/rejected by policy. Current behavior is safe for this family because checkout stores the resolved variant options, not the extra client data.
