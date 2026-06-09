D:2026-05-10 | Review:Phase 4 quote/event checkout boundary security/ops rereview | Confidence:high
# Phase 4 security/ops rereview — quote/event checkout boundary

## Verdict

PASS

## Evidence reviewed

- Prior security/ops review: `workstreams/ecommerce-audit/phase-4-security-ops-review-2026-05-10.md`
- Verifier implementation: `apps/locally_twisted/locally_twisted/verify/quote_event_checkout_boundary_contract.py`
- Verifier runner: `scripts/verify/quote_event_checkout_boundary_contract.py`
- Verifier artifact: `workstreams/ecommerce-audit/phase-4-quote-event-checkout-boundary-contract-20260510.json`
- Runtime product contract/precedence: `apps/locally_twisted/locally_twisted/product_page_runtime.py`
- Runtime cart boundary: `apps/locally_twisted/locally_twisted/api/cart.py`

## Findings

### Added contract precedence tests fail closed

PASS.

- `resolved_product_page_contract_values()` allows paid checkout only when both stored fields explicitly resolve to `simple_product|checkout`.
- Blank fields, partial checkout fields, inferred checkout, and explicit needs-review values resolve to `needs_review|needs_review` rather than checkout.
- The verifier includes explicit precedence cases for blank lane/page fields, inferred checkout, partial checkout, preserved explicit checkout, and preserved quote-first.
- Artifact evidence: `contract_precedence` contains all six expected cases with no failures.

### No live payment/customer message/PII/token/session exposure

PASS.

- The verifier and runner do not call `submit_guest_order`, `get_payment_gateway_account`, Stripe session creation, Payment Request creation/submission, Sales Order insertion/submission, or checkout note/Communication creation.
- Static search of the reviewed verifier/runner found no database insert/save/submit/set-value calls, sendmail calls, Stripe/payment-session calls, legacy_source calls, or network-client imports.
- Artifact content is limited to item codes, lane/template status, block outcomes, precedence outcomes, rollback status, and count deltas. I found no customer email, phone, address, name, token, secret, checkout URL, payment session, or customer message body.

### No legacy_source mutation risk

PASS.

- The runner executes a local Frappe method inside the ERPNext container via `docker exec ... bench --site frontend execute locally_twisted.verify.quote_event_checkout_boundary_contract.run`.
- The reviewed verifier path uses Frappe reads plus local runtime/cart/checkout boundary functions. I found no legacy_source imports, API clients, export calls, XML-RPC/JSON-RPC calls, or other network write paths.

### Rollback-safe / no persistent business-record deltas

PASS.

- `run()` captures counts before execution for `Customer`, `Contact`, `Address`, `Sales Order`, `Payment Request`, `Payment Entry`, `Sales Invoice`, `Communication`, and `Email Queue`.
- It monkeypatches `frappe.db.commit` to a no-op during the contract, restores it in `finally`, and always calls `frappe.db.rollback()`.
- It fails if any counted business-record deltas survive.
- Artifact evidence: `record_count_deltas: {}`, `rolled_back: true`, `commit_calls_intercepted: 0`.

### Cart/checkout boundary remains fail-closed

PASS.

- `api/cart.py` re-resolves the Website Item contract server-side and returns `quote_required` whenever `commerce_lane != "checkout"`.
- Direct buy-now checkout uses `resolve_cart_item_for_sale(..., raise_on_missing=False)` and fails to page-not-found when the item is not server-approved for checkout.
- Stale/localStorage checkout payloads are re-resolved through `_resolve_sale_lines()` and fail with quote-required/unavailable before Sales Order line construction.
- Artifact evidence: `quote_first_count: 33`, `needs_review_count: 5`, `cart_api_blocked_count: 38`, `direct_checkout_url_blocked_count: 38`, `stale_localstorage_blocked_count: 38`, `no_sellable_candidate_count: 0`, `ok: true`.

### Artifact present/readable

PASS.

- Artifact path is present and readable: `workstreams/ecommerce-audit/phase-4-quote-event-checkout-boundary-contract-20260510.json`.
- Parsed JSON successfully.
- Observed size: 30,553 bytes.
- Artifact reports `ok: true` with no failures.

## Residual notes

- The rollback strategy covers Frappe database mutations in the verifier path. If future verifier expansion exercises external side effects outside the DB transaction, those paths should be explicitly stubbed/guarded before execution.
- Runtime helper functions may log setup errors on actual checkout-lane add-on misconfiguration, but this rereviewed contract path blocks quote/review items before those checkout-lane add-on write paths are reached.

## Required fixes

None.
