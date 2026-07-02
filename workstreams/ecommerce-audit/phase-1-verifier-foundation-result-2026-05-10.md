D:2026-05-10 | Check:test/build/lint 2026-05-10 | Confidence:[LOCAL-PROOF]
# Phase 1 verifier foundation result — ready-to-order ecommerce

## Scope

Goal Phase 1 only: repair rollback-safe checkout verifier foundation and add focused customer-note checkout preservation proof before any product/catalog edits.

Non-scope honored: no catalog_data mutation, no public ecommerce opening, no product publish/catalog mutation, no live payment, no customer email send, no secrets/PII/tokens exposed.

## Files changed

- `apps/locally_twisted/locally_twisted/verify/checkout_fulfillment_contract.py`
  - Bypasses `locally_twisted.ecommerce_pause.is_ecommerce_paused()` only inside the rollback-safe verifier run.
  - Restores the pause function in `finally` and rolls back generated records.
  - Checks `ok/status` before reading `sales_order`, converting paused/setup/no-SO responses into clear `ContractFail` messages instead of raw `KeyError`.
  - Allows the intentional out-of-area `quote_required` scenario without expecting a Sales Order.
- `apps/locally_twisted/locally_twisted/verify/customer_note_checkout_preservation_contract.py`
  - New rollback-safe verifier for `submit_guest_order(order_notes=...)` and no-note checkout cases.
  - Stubs Stripe checkout-session creation, intercepts `frappe.db.commit`, sets test email flags, bypasses ecommerce pause only inside the verifier, and restores all patches.
  - Proves Sales Order Communication subject/content, Payment Request link, operator lookup/notification note consumption, no fake no-note content, rollback/no-survivor counts.
- `scripts/verify/customer_note_checkout_preservation_contract.py`
  - New CLI wrapper for the Frappe verifier.
- `workstreams/ecommerce-audit/phase-1-verifier-foundation-result-2026-05-10.md`
  - This result artifact.
- `workstreams/ecommerce-audit/README.md`
  - Indexed this result artifact. Note: the file already contained unrelated modified/untracked ecommerce-audit index work before this slice; this slice only adds the Phase 1 result row.

## Commands run and exact output

### `python scripts/verify/checkout_fulfillment_contract.py`

```text
[CHECKOUT FULFILLMENT CONTRACT] PASS
  rollback: verifier rolled back generated records
```

### `python scripts/verify/payment_cascade_contract.py`

```text
[PAYMENT CASCADE CONTRACT] PASS
  sales_order: SAL-ORD-2026-00021
  payment_request: ACC-PRQ-2026-00020
  payment_entry: ACC-PAY-2026-00002
  sales_invoice: ACC-SINV-2026-00003
  receipt_email_queue: l2ttgmlo75
  operator_email_queue: l2tppp17ua
  welcome_email_queue: l2urcel848
  checkout_notes: l2kfqjh682
  rollback: verifier rolled back all generated records
```

### `python scripts/verify/customer_note_checkout_preservation_contract.py`

```text
[CUSTOMER NOTE CHECKOUT PRESERVATION CONTRACT] PASS
  note_sales_order: SAL-ORD-2026-00021
  note_payment_request: ACC-PRQ-2026-00020
  note_communication: l6tq2j7t6u
  operator_email_queue: l709vvtg8d
  no_note_sales_order: SAL-ORD-2026-00022
  no_note_payment_request: ACC-PRQ-2026-00021
  no_fake_customer_note: true
  survivor_counts: {'customer': 0, 'contact': 0, 'contact_email': 0, 'address': 0, 'sales_order': 0, 'payment_request': 0, 'payment_entry': 0, 'sales_invoice': 0, 'communication': 0, 'email_queue': 0}
  rollback: verifier rolled back all generated records
```

## Result

- PASS: checkout fulfillment verifier no longer crashes with `KeyError: 'sales_order'` under the default ecommerce pause. It deterministically opens checkout only inside the rollback-safe verifier and fails clearly if paused/setup responses leak through.
- PASS: focused customer-note verifier proves a unique `order_notes` value submitted through `submit_guest_order(...)` creates a Sales Order-linked `Communication` with subject `Customer checkout notes - <SO>` and containing the unique note.
- PASS: the generated Payment Request links to the same Sales Order.
- PASS: the paid-order/operator notification lookup path can consume the same note using rollback-safe queued operator evidence; no real payment/customer email was sent.
- PASS: no-note checkout case proves the unique note/no-note marker is not invented or leaked.
- PASS: rollback/no-survivor proof reports zero generated Customer, Contact, Contact Email, Address, Sales Order, Payment Request, Payment Entry, Sales Invoice, Communication, or Email Queue survivors for the verifier token.

## Remaining blockers / unverified claims

- This does not open public ecommerce and does not make any product `checkout_ready_now`.
- This does not prove live Stripe payment success; Stripe session creation is stubbed in the new customer-note verifier.
- The new customer-note verifier exercises the operator notification path used by the paid-order cascade without marking the checkout Payment Request paid, because full paid-order accounting cascade remains covered separately by `payment_cascade_contract.py`.
- Website Item classification saves, product family proof, delivery mapping cleanup, public payment-success proof, media/price approvals, and launch opening remain later-phase blockers.

## Rollback / privacy notes

- `frappe.db.commit` is intercepted during verifier execution.
- Ecommerce pause bypass is an in-process monkeypatch restored in `finally`; public pause behavior remains safe by default.
- Stripe checkout session creation is stubbed to `checkout.stripe.example.invalid`.
- Test emails use `example.invalid`; Frappe email work is queued inside the rollback-only transaction.
- No catalog_data files/systems were mutated.
- No customer PII, tokens, raw sessions, or secrets were exposed in this artifact.
