# Synthetic Business Pipeline

Last updated: 2026-05-08 by Codex after adding customer/operator email policy boundaries.

## Outcome

Flush out broken cascading information, fake-data cleanup leaks, and backend piping gaps without live Stripe keys, real operator details, or real customer information.

This lane is deliberately separate from live cutover. Live Stripe keys, webhook secrets, production host checks, and real contact data are deferred until cutover work begins.

## Current Verified State

Latest command:

```powershell
python scripts/verify/synthetic_business_pipeline.py --report output/synthetic-business-pipeline.json
```

Current result on 2026-05-08:

- `ok: true`
- `synthetic_only: true`
- `live_inputs_required: false`
- `uses_real_customer_data: false`
- 16 synthetic contracts run
- 16 synthetic contracts passing
- 0 broken piping items
- 8 inefficiencies / partial connections surfaced
- 3 cutover-deferred items surfaced

The report writes ignored JSON to `output/synthetic-business-pipeline.json`.

## What It Exercises

- Record-level backend failure evidence with rollback-safe Lead blockers and Error Log evidence.
- Inquiry upload rejection/failure handling with customer-visible summary and Lead-level evidence.
- Payment-success browser-return reconciliation errors with pending thank-you copy.
- Stripe Checkout amount parity with in-memory fake Sales Orders.
- Checkout-to-Lead conversion with a stubbed Stripe URL and rollback-only records.
- Checkout fulfillment branches with stubbed Stripe session creation and rollback-only records.
- Paid-order cascade through Payment Request, Payment Entry, Sales Invoice, receipt/operator/welcome emails, and rollback cleanup.
- Stripe webhook behavior with mocked Stripe events and intercepted expected `frappe.log_error` calls.
- Customer policy document anchors and inquiry acknowledgment policy blocks.
- Customer/operator email policy and no-PDF/no-attachment boundaries for inquiry acknowledgment, paid receipt, operator notification, first-order welcome, and paid-order cascade coverage.
- Outbound document registry/template contract.
- Outbound document send-readiness blockers for missing required fields, recipient confirmation, payment path, branding, human approval, sensitive attachments, and record-level blocker evidence.
- Quote/proposal draft packets with fake Quotation/Lead-style scenarios, including missing acceptance path and malformed send-ready source rows.
- Unpaid invoice packet normal/outlier fake-data scenarios.
- Customer reminder dry-run normal/outlier fake-data scenarios, including missing payment path and malformed send-enabled packets.
- Customer reminder review-report normal/outlier fake-data scenarios, including grouped rows, empty queues, and malformed send-enabled source rows.

## Current Inefficiencies / Partial Connections

The synthetic audit currently surfaces, but does not fail on, these non-live gaps:

- no Bank Account record
- no Company default bank account
- no Supplier/vendor records
- no Employee records
- missing payroll DocTypes / HRMS
- vendor setup/W-9 template exists but no approved W-9/Supplier/secure-send flow is wired
- bank reconciliation exists as ERPNext capability but no LT bank setup is connected
- payroll is future feasibility, not operational

## Boundaries

Do not add live keys, real operator email, real customer records, live Stripe checkout, bank credentials, or provider credentials to this lane.

Do not turn this verifier into customer sending or accounting mutation. Rollback/fake contracts may create temporary records inside their own cleanup guards, but the synthetic audit must fail if guarded business record counts change.

## Related Files

- `apps/locally_twisted/locally_twisted/verify/synthetic_business_pipeline.py`
- `scripts/verify/synthetic_business_pipeline.py`
- `apps/locally_twisted/locally_twisted/verify/record_level_failure_contract.py`
- `apps/locally_twisted/locally_twisted/verify/inquiry_upload_failure_contract.py`
- `apps/locally_twisted/locally_twisted/verify/payment_success_reconciliation_contract.py`
- `apps/locally_twisted/locally_twisted/verify/customer_email_policy_contract.py`
- `apps/locally_twisted/locally_twisted/failure_recorder.py`
- `apps/locally_twisted/locally_twisted/verify/paperwork_status.py`
- `apps/locally_twisted/locally_twisted/paperwork/paperwork_review_digest.py`
- `apps/locally_twisted/locally_twisted/paperwork/customer_reminder_dry_run.py`
- `apps/locally_twisted/locally_twisted/paperwork/customer_reminder_review_report.py`
- `apps/locally_twisted/locally_twisted/verify/customer_reminder_review_report_contract.py`
- `apps/locally_twisted/locally_twisted/outbound_documents/send_readiness.py`
- `apps/locally_twisted/locally_twisted/verify/outbound_document_send_readiness_contract.py`
- `apps/locally_twisted/locally_twisted/paperwork/quote_proposal_draft_packet.py`
- `apps/locally_twisted/locally_twisted/verify/quote_proposal_draft_packet_contract.py`
- `apps/locally_twisted/locally_twisted/verify/business_automation_index.py`

## Next Safe Slice

Use the synthetic audit as the regression gate while adding any remaining no-send paperwork/reporting slices. Vendor/W-9 packet generation, bank reconciliation, payroll/HRMS, and real reminder delivery are approval-gated and stay out of this lane until their owner/accountant inputs are available.
