D:2026-05-10 | Review:Phase 4 quote/event checkout boundary architecture | Confidence:high
# Phase 4 architecture review — quote/event checkout boundary

## Verdict

CONCERN

The boundary is correctly moving into runtime/cart/sale-line resolution instead of living only in templates, and the current classified Phase 4 rows pass the recorded verifier. However, the implementation still has one architecture gap: a partial explicit `needs_review` contract can be overridden by inferred checkout if only one Website Item field is set. That is close enough to the Phase 4 failure mode that I would fix it before calling this hardened.

## Evidence reviewed

- Build brief: `workstreams/ecommerce-audit/phase-4-quote-event-path-hardening-build-brief-2026-05-10.md`
- Runtime contract: `apps/locally_twisted/locally_twisted/product_page_runtime.py`
- Cart API resolver: `apps/locally_twisted/locally_twisted/api/cart.py`
- Checkout boundary verifier: `apps/locally_twisted/locally_twisted/verify/quote_event_checkout_boundary_contract.py`
- Script wrapper: `scripts/verify/quote_event_checkout_boundary_contract.py`
- Recorded verifier output: `workstreams/ecommerce-audit/phase-4-quote-event-checkout-boundary-contract-20260510.json`
- Phase 3 recorded checkout output spot-check: `workstreams/ecommerce-audit/phase-3-checkout-product-family-contract-20260510.json`

## What is sound

1. Boundary is not template-only.
   - Product page context now comes from `product_page_contract_for_website_item()` through `get_product_page_runtime_context()`.
   - Cart sale resolution calls `product_page_contract_for_website_item(website_item["item_code"])` and blocks anything where `commerce_lane != "checkout"`.
   - Sales Order line configuration and add-on line builders also block `commerce_lane != "checkout"`, so stale cart payloads cannot become sale lines just by carrying `commerce_lane: checkout` client-side.
   - Direct `/checkout?item=...` uses `resolve_cart_item_for_sale(..., raise_on_missing=False)` and fails closed with `PageDoesNotExistError` when resolution blocks.

2. Current Phase 4 classified rows are covered.
   - Recorded Phase 4 verifier output has `ok: true`.
   - It covers 33 `quote_first` rows and 5 `needs_review` rows.
   - It reports 38/38 blocked at cart API, direct checkout URL, and stale localStorage/sale-line resolution.
   - It reports `record_count_deltas: {}` and `rolled_back: true`.

3. Phase 3 checkout path appears preserved for explicitly approved checkout products.
   - Cart resolver changed from blocking only `quote_first` to allowing only explicit `checkout`, which is the right safer default.
   - Recorded Phase 3 output still shows checkout-family rows with `stored_contract: simple_product|checkout`, add-on resolution, and zero survivor business records.

## Architecture concern

`product_page_contract_for_website_item()` currently resolves fields as:

- `page_type = explicit_page_type or inferred["product_page_type"]`
- `commerce_lane = explicit_commerce_lane or inferred["commerce_lane"]`

That honors `lt_commerce_lane = needs_review`, but it does not make `lt_product_page_type = needs_review` authoritative if `lt_commerce_lane` is blank/invalid/missing. For an item group that matches checkout hints, the resolved contract can become:

- `product_page_type = needs_review`
- `commerce_lane = checkout`

That mixed state is dangerous because:

- Product templates may still show quote/review UI via `needs_review`.
- Cart API and sale-line resolution key on `commerce_lane`, so the same item could still enter checkout.
- The verifier does not test partial/mismatched explicit fields; it only tests current classified rows where both stored fields are already `needs_review|needs_review`.

This means explicit needs-review does not fully override inferred checkout in the architecture; only explicit needs-review commerce lane does.

## Required fixes

1. Make `needs_review` fail-closed across the whole resolved contract.
   - Recommended rule: if either explicit Website Item field is `needs_review`, and the paired field is absent/invalid, resolve both sides to review-safe values instead of inferring checkout.
   - At minimum: `explicit_page_type == "needs_review"` must force `commerce_lane = "needs_review"` unless an explicit non-review lane is intentionally present and separately validated.
   - Safer default: any mixed `needs_review|checkout` contract should normalize to `needs_review|needs_review` or fail closed.

2. Add verifier coverage for the partial/mixed-field failure mode.
   - The current verifier proves the live classified rows, but not the precedence rule itself.
   - Add a read-only/pure helper test if possible, or extract contract precedence into a small pure function and assert:
     - explicit page type `needs_review` + inferred checkout => resolved `needs_review|needs_review`
     - explicit commerce lane `needs_review` + inferred checkout => resolved `needs_review|needs_review`
     - explicit `simple_product|checkout` still resolves checkout for Phase 3 products

3. Keep Phase 3 regression gate mandatory after the change.
   - The allow-list posture should remain: paid checkout is allowed only for explicit `commerce_lane == checkout` products, and Phase 3 products should continue to prove that path.

## Risks if shipped as-is

- A future sync/manual edit that sets only `lt_product_page_type = needs_review` on a checkout-hinted group could display review/quote UI while still permitting cart/checkout resolution.
- The current verifier would not catch that mismatch because it checks only fully classified current rows.
- This is not a live-record mutation risk; it is a contract-precedence and future-data-drift risk.
