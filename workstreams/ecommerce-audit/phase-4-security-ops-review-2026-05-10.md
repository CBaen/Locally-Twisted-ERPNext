D:2026-05-10 | Review:Phase 4 quote/event checkout boundary security/ops | Confidence:high
# Phase 4 security/ops review — quote/event checkout boundary

## Verdict

PASS

## Evidence reviewed

- Build brief: `workstreams/ecommerce-audit/phase-4-quote-event-path-hardening-build-brief-2026-05-10.md`
- Verifier implementation: `apps/locally_twisted/locally_twisted/verify/quote_event_checkout_boundary_contract.py`
- Verifier runner: `scripts/verify/quote_event_checkout_boundary_contract.py`
- Verifier artifact: `workstreams/ecommerce-audit/phase-4-quote-event-checkout-boundary-contract-20260510.json`
- Runtime cart boundary: `apps/locally_twisted/locally_twisted/api/cart.py`
- Checkout boundary: `apps/locally_twisted/locally_twisted/www/checkout.py`

## Findings

### No live payment, token, or customer-message exposure

PASS.

- The Phase 4 verifier does not call `submit_guest_order`, `get_payment_gateway_account`, `create_session_for_sales_order`, Stripe session creation, Payment Request creation, or checkout note/Communication creation.
- Static search of the verifier/runner found no `insert`, `save`, `submit`, `set_value`, sendmail, Stripe, or payment-session calls. The only payment/customer doctypes referenced are count targets for rollback/delta checks.
- The verifier artifact contains item codes, lane status, runtime booleans, block outcomes, rollback status, and record-count deltas only. I found no customer PII, payment token, session secret, checkout URL, email, phone, address, or customer message content.

### No legacy_source mutation

PASS.

- The reviewed verifier runs inside ERPNext via `docker exec ... bench --site frontend execute locally_twisted.verify.quote_event_checkout_boundary_contract.run`.
- The implementation uses Frappe reads and local runtime/checkout/cart resolution functions only. I found no legacy_source API/client imports, network calls, export calls, or legacy_source write paths in the reviewed verifier/runner.

### Rollback/no business-record deltas

PASS.

- `quote_event_checkout_boundary_contract.run()` captures counts for `Customer`, `Contact`, `Address`, `Sales Order`, `Payment Request`, `Payment Entry`, `Sales Invoice`, `Communication`, and `Email Queue` before the contract run.
- It monkeypatches `frappe.db.commit` to a no-op during the contract and always restores the original commit plus calls `frappe.db.rollback()` in `finally`.
- It fails the contract if any counted business-record deltas survive.
- Artifact evidence: `record_count_deltas: {}`, `rolled_back: true`, and `commit_calls_intercepted: 0`.

### Public ecommerce remains paused

PASS.

- `checkout.py` defines paused status/message as `ecommerce_paused` and guards both `preview_checkout_totals()` and `submit_guest_order()` with `_assert_checkout_api_open(...)` before cart resolution, customer validation, Sales Order creation, Payment Request creation, Stripe session creation, or commit.
- When paused, the guard returns HTTP 403 with a contact/quote path instead of mutating business records.
- The paused-checkout log payload records safe metadata and form keys only, excluding `name`, `email`, `phone`, `address_line1`, and `address_line2` values.
- Note: the `/checkout` page shell can still render, but purchase APIs fail closed while paused. That matches the current safety boundary: no public payment/customer/order mutation.

### Quote/event/needs-review products cannot enter checkout

PASS.

- `api/cart.py` blocks anything whose trusted product-page contract has `commerce_lane != "checkout"` and returns `quote_required`.
- Direct buy-now URLs use `resolve_cart_item_for_sale(..., raise_on_missing=False)` and raise `PageDoesNotExistError` when the item is not purchasable.
- Checkout sale-line resolution re-checks the cart API result and throws a quote-required validation error before Sales Order line creation.
- The verifier covers the required surfaces: product-page template routing, cart API blocking, direct `/checkout?item=...` blocking, stale/localStorage-style payload blocking, and business-record delta checks.
- Artifact evidence: `quote_first_count: 33`, `needs_review_count: 5`, `cart_api_blocked_count: 38`, `direct_checkout_url_blocked_count: 38`, `stale_localstorage_blocked_count: 38`, `no_sellable_candidate_count: 0`, `ok: true`.

### Verifier artifact present/readable

PASS.

- Artifact path is present and readable: `workstreams/ecommerce-audit/phase-4-quote-event-checkout-boundary-contract-20260510.json`.
- Artifact size observed: 6,746 bytes.
- Artifact reports `ok: true` with no failures and the expected 38 blocked classified products.

## Risks / residual notes

- The verifier monkeypatches `frappe.db.commit` and performs a final rollback, which is appropriate for this contract. If future verifier coverage calls code that performs side effects outside the database transaction, such as external network calls or non-Frappe file writes, those would need explicit stubs or guards. I found no such side effects in the current reviewed path.
- The paused checkout guard logs an Error Log entry on blocked public API attempts. The payload is intentionally low-sensitivity, but it is still an ERPNext record mutation by real public traffic. This is acceptable operational telemetry for a blocked attempt, not a checkout/customer/order/payment mutation.

## Required fixes

None.
