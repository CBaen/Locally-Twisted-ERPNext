# Synthetic Business Pipeline

Last updated: 2026-05-06 by Codex after adding no-live customer reminder dry-run coverage.

## Outcome

Flush out broken cascading information, fake-data cleanup leaks, and backend piping gaps without live Stripe keys, real operator details, or real customer information.

This lane is deliberately separate from live cutover. Live Stripe keys, webhook secrets, production host checks, and real contact data are deferred until cutover work begins.

## Current Verified State

Latest command:

```powershell
python scripts/verify/synthetic_business_pipeline.py --report output/synthetic-business-pipeline.json
```

Current result on 2026-05-06:

- `ok: true`
- `synthetic_only: true`
- `live_inputs_required: false`
- `uses_real_customer_data: false`
- 9 synthetic contracts run
- 9 synthetic contracts passing
- 0 broken piping items
- 9 inefficiencies / partial connections surfaced
- 3 cutover-deferred items surfaced

The report writes ignored JSON to `output/synthetic-business-pipeline.json`.

## What It Exercises

- Stripe Checkout amount parity with in-memory fake Sales Orders.
- Checkout-to-Lead conversion with a stubbed Stripe URL and rollback-only records.
- Checkout fulfillment branches with stubbed Stripe session creation and rollback-only records.
- Paid-order cascade through Payment Request, Payment Entry, Sales Invoice, receipt/operator/welcome emails, and rollback cleanup.
- Stripe webhook behavior with mocked Stripe events and intercepted expected `frappe.log_error` calls.
- Customer policy document anchors and inquiry acknowledgment policy blocks.
- Outbound document registry/template contract.
- Unpaid invoice packet normal/outlier fake-data scenarios.
- Customer reminder dry-run normal/outlier fake-data scenarios, including missing payment path and malformed send-enabled packets.

## Current Inefficiencies / Partial Connections

The synthetic audit currently surfaces, but does not fail on, these non-live gaps:

- no Bank Account record
- no Company default bank account
- no Supplier/vendor records
- no Employee records
- missing payroll DocTypes / HRMS
- quote/proposal templates exist but no Quotation-to-PDF approval generator is wired
- vendor setup/W-9 template exists but no approved W-9/Supplier/secure-send flow is wired
- bank reconciliation exists as ERPNext capability but no LT bank setup is connected
- payroll is future feasibility, not operational

## Boundaries

Do not add live keys, real operator email, real customer records, live Stripe checkout, bank credentials, or provider credentials to this lane.

Do not turn this verifier into customer sending or accounting mutation. Rollback/fake contracts may create temporary records inside their own cleanup guards, but the synthetic audit must fail if guarded business record counts change.

## Related Files

- `apps/locally_twisted/locally_twisted/verify/synthetic_business_pipeline.py`
- `scripts/verify/synthetic_business_pipeline.py`
- `apps/locally_twisted/locally_twisted/verify/paperwork_status.py`
- `apps/locally_twisted/locally_twisted/paperwork/paperwork_review_digest.py`
- `apps/locally_twisted/locally_twisted/paperwork/customer_reminder_dry_run.py`
- `apps/locally_twisted/locally_twisted/verify/business_automation_index.py`

## Next Safe Slice

Use the synthetic audit as the regression gate while building the reviewed reminder Desk page or scheduled internal-only digest. Add new fake-data scenarios when a new backend pipe is connected, then keep live cutover checks separate.
