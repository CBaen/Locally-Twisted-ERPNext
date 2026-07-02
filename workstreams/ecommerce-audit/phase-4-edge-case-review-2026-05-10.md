D:2026-05-10 | Review:Phase 4 quote/event checkout boundary edge cases | Confidence:high
# Phase 4 edge-case review — quote/event checkout boundary

## Verdict: CONCERN

The implementation blocks the real 33 quote-first rows and 5 needs-review rows across product-page routing, cart API resolution, direct `/checkout?item=...`, and stale localStorage payloads that lie `commerce_lane: checkout`. I do not see a live checkout escape in the reviewed path.

The concern is verifier completeness: two requested edge lenses are only partially exercised by the Phase 4 boundary verifier/report.

## Evidence reviewed

- Build brief: `workstreams/ecommerce-audit/phase-4-quote-event-path-hardening-build-brief-2026-05-10.md`.
- Phase 4 verifier: `apps/locally_twisted/locally_twisted/verify/quote_event_checkout_boundary_contract.py`.
- Phase 4 result artifacts:
  - `workstreams/ecommerce-audit/phase-4-quote-event-checkout-boundary-contract-20260510.json`
  - `output/phase-4-quote-event-checkout-boundary-contract-20260510.json`
- Classification verifier and artifact:
  - `apps/locally_twisted/locally_twisted/verify/website_item_classification_contract.py`
  - `output/phase-4-website-item-classification-contract-20260510.json`
- Runtime/cart/checkout boundary code:
  - `apps/locally_twisted/locally_twisted/product_page_runtime.py`
  - `apps/locally_twisted/locally_twisted/api/cart.py`
  - `apps/locally_twisted/locally_twisted/www/checkout.py`
- Syntax gate run during review:
  - `python -m py_compile apps/locally_twisted/locally_twisted/product_page_runtime.py apps/locally_twisted/locally_twisted/api\cart.py apps/locally_twisted/locally_twisted/verify\quote_event_checkout_boundary_contract.py scripts/verify/quote_event_checkout_boundary_contract.py` passed.

## Passing evidence

1. **All target rows are represented.**
   - Classification report is `ok: true` with `matched_count: 53`.
   - Stored target counts are exactly:
     - `simple_product|checkout`: 15
     - `complex_custom_product|quote_first`: 33
     - `needs_review|needs_review`: 5
   - Phase 4 boundary report has `quote_first_count: 33` and `needs_review_count: 5`.

2. **Needs-review explicit fields now win over inferred checkout hints.**
   - `product_page_contract_for_website_item()` now uses explicit `lt_product_page_type` / `lt_commerce_lane` whenever valid, including `needs_review`, instead of treating `needs_review` as fallback-empty.
   - This directly protects products such as `birthday-deliveries`, whose group/name hints could otherwise look checkout-like.

3. **Cart API blocks every non-checkout lane.**
   - `api/cart.py` rejects `product_page_contract.commerce_lane != "checkout"` with `quote_required`.
   - Phase 4 result: `cart_api_blocked_count: 38`.

4. **Direct checkout URL fails closed.**
   - `www/checkout.py#get_context()` calls `resolve_cart_item_for_sale(..., raise_on_missing=False)` and raises `PageDoesNotExistError` when the item does not resolve.
   - Phase 4 result: `direct_checkout_url_blocked_count: 38`, with sample rows marked `blocked_not_found`.

5. **Stale localStorage lying about checkout is blocked by server truth.**
   - Phase 4 verifier sends a current-schema configuration that claims `product_page_type: simple_product` and `commerce_lane: checkout` for quote/review items.
   - `_resolve_sale_lines()` re-resolves via `resolve_cart_item_for_sale_with_reason()` and throws the quote-required checkout message before Sales Order lines are built.
   - Phase 4 result: `stale_localstorage_blocked_count: 38`.

6. **No business-record deltas in the boundary verifier.**
   - Phase 4 result: `record_count_deltas: {}`, `rolled_back: true`, `commit_calls_intercepted: 0`.

## Risks / concerns

1. **No-sellable-candidate branch is not exercised by current data.**
   - The verifier has a branch for no enabled sellable candidate, but the result says `no_sellable_candidate_count: 0`.
   - That means the current contract proves all 38 classified quote/review rows have candidates and are blocked, not that a no-candidate quote/review row remains harmless under this verifier.
   - Runtime behavior appears fail-closed (`Item` missing/disabled -> unavailable), but this edge case is not directly covered by a fixture or synthetic assertion in Phase 4.

2. **Malformed/stale-schema cart config is covered elsewhere, not in this Phase 4 boundary artifact.**
   - `normalize_client_configuration()` rejects bad JSON/non-dict/old schema/oversized configs.
   - `product_page_runtime_contract.py` has an old-schema assertion (`older option format`).
   - Phase 4 specifically tests a valid-schema stale/lying payload, which is the most important checkout-lane bypass case, but it does not itself prove malformed or old-schema payloads for these 38 quote/review products.

3. **Boundary report samples, not full row evidence.**
   - The Phase 4 report returns counts plus samples, while the verifier iterates all `QUOTE_FIRST` and `HIDE_OR_NEEDS_REVIEW` constants.
   - This is acceptable for pass/fail, but weaker for audit handoff because the artifact does not list all 38 product-to-candidate mappings.

## Required fixes before marking this edge-case review PASS

1. Add explicit Phase 4 verifier assertions for malformed/stale-schema configurations against at least one quote-first and one needs-review candidate:
   - malformed JSON / non-list `items_json` at `_resolve_cart_items`, and/or
   - old `schema_version` in `configuration`, expecting a loud validation failure before checkout records.

2. Add a synthetic no-sellable-candidate assertion or document it as intentionally out of scope:
   - Preferred: add a rollback-safe temporary disabled/no-variant fixture or monkeypatched resolver scenario proving the verifier/report handles `candidate_item_code: null` without checkout/API leakage.
   - Minimum: make the report state that current production set has `no_sellable_candidate_count: 0` and that unavailable Item resolution is covered by existing cart semantics.

3. Expand the Phase 4 JSON report to include all 38 row evidences, not just samples, or write a companion full evidence artifact. This is not a runtime safety issue, but it makes future audit review much less brittle.

## Bottom line

Runtime boundary looks safe for the real Phase 2 quote-first + needs-review rows. I would not block deployment on a suspected checkout escape, but I would keep the review at **CONCERN** until the Phase 4 verifier explicitly covers malformed/stale-schema config and no-sellable-candidate behavior, or those are clearly delegated to named regression contracts.
