D:2026-05-10 | Review:Phase 4 quote/event checkout boundary edge-case rereview | Confidence:high
# Phase 4 edge-case rereview — quote/event checkout boundary

## Verdict: PASS

The previous verifier-completeness gaps are resolved in the reviewed Phase 4 contract artifact. I did not modify code.

## Evidence reviewed

- Prior review: `workstreams/ecommerce-audit/phase-4-edge-case-review-2026-05-10.md`
- Verifier: `apps/locally_twisted/locally_twisted/verify/quote_event_checkout_boundary_contract.py`
- Result artifact: `workstreams/ecommerce-audit/phase-4-quote-event-checkout-boundary-contract-20260510.json`
- Runtime boundary code:
  - `apps/locally_twisted/locally_twisted/www/checkout.py`
  - `apps/locally_twisted/locally_twisted/api/cart.py`

## Focus-area findings

### 1. Malformed / non-list / stale-schema config: resolved

The verifier now calls `_assert_malformed_and_stale_config_fail_loudly(...)` and the artifact includes:

- `malformed_items_json: blocked_validation_error`
- `non_list_items_json: blocked_validation_error`
- `quote_first_old_schema_configuration: blocked_old_schema`
- `needs_review_old_schema_configuration: blocked_old_schema`

This covers malformed cart JSON, non-list `items_json`, and old-schema `configuration` for both a quote-first candidate and a needs-review candidate. The runtime path matches the assertion: `checkout._resolve_cart_items()` rejects malformed/non-list payloads, and `cart_line_key()` routes configuration through `normalize_client_configuration()`, which rejects stale schema versions with the expected older-option-format validation error.

### 2. No-sellable-candidate behavior: resolved

The artifact still correctly reports the current production target set as `no_sellable_candidate_count: 0`, meaning all 38 real quote/review rows have enabled sellable candidates. The prior uncovered behavior is now represented by `no_sellable_candidate_synthetic`:

```json
{
  "item_code": "__lt_phase4_no_sellable_candidate__",
  "sellable_candidate": null,
  "cart_api": "blocked_unavailable",
  "direct_checkout_url": "blocked_not_found",
  "stale_localstorage": "blocked_unavailable"
}
```

The synthetic uses a missing item code rather than a temporary disabled Website Item fixture, but it proves the relevant unavailable/no-candidate checkout surfaces fail closed through the same cart API, direct checkout URL, and sale-line resolution paths. That satisfies the minimum from the prior review: current production set documented as having zero no-candidate rows, with unavailable item resolution covered by the verifier.

### 3. Full row evidence for all 38 rows: resolved

The artifact now includes full arrays, not only samples:

- `quote_first_rows`: 33 rows
- `needs_review_rows`: 5 rows
- Total full evidence rows: 38

I verified every row has a `candidate_item_code` and all three boundary checks set to the expected blocked states:

- `cart_api: blocked_quote_required`
- `direct_checkout_url: blocked_not_found`
- `stale_localstorage: blocked_quote_required`

Counts also align with the summary fields:

- `quote_first_count: 33`
- `needs_review_count: 5`
- `cart_api_blocked_count: 38`
- `direct_checkout_url_blocked_count: 38`
- `stale_localstorage_blocked_count: 38`

## Notes

- `record_count_deltas: {}` and `rolled_back: true` remain present in the artifact.
- The no-candidate coverage is synthetic unavailable-item coverage, not a synthetic quote/review Website Item with disabled variants. I do not consider that a blocker because the prior review allowed documenting the production zero-candidate count plus existing unavailable-item semantics as the minimum acceptable fix.

## Bottom line

The three previous gaps are now covered well enough for audit handoff. Verdict: **PASS**.
