# Customer Reminder Dry Run

Last updated: 2026-05-06 by Codex after adding the no-live internal customer reminder queue.

## Outcome

Set up as much of customer reminders as possible without going live:

- identify unpaid/overdue invoice reminder candidates
- render draft reminder and statement sections
- suggest internal review cadence
- show exactly what blocks customer sending
- verify fake overdue/current/missing-payment-path/malformed-send scenarios
- keep live delivery, automatic cadence, and accounting mutation disabled

This is not a customer-send surface. It is an internal review queue payload that can feed a Desk page or scheduled internal-only report later.

## Current Verified State

Fresh local verification on 2026-05-06:

```powershell
python scripts/verify/customer_reminder_dry_run_contract.py
python scripts/verify/customer_reminder_dry_run.py --report output/customer-reminder-dry-run.json --markdown output/customer-reminder-dry-run.md
python scripts/verify/synthetic_business_pipeline.py --report output/synthetic-business-pipeline.json
python scripts/verify/business_automation_index.py --report output/business-automation-index.json
```

Current result:

- `customer_reminder_dry_run_contract.py` passed 6 fake scenarios: overdue reminder, severe overdue statement, current unpaid hold, missing payment path, empty source, and malformed delivery-enabled packet.
- `customer_reminder_dry_run.py` passed against local ERPNext with 1 queue item for `ACC-SINV-2026-00001`.
- The queue item is `internal_review_only`, `draft_only_not_sent`, and recommends `review_now_payment_reminder`.
- `send_allowed: false`, `customer_delivery_enabled: false`, `automatic_delivery_enabled: false`, and `mutation_allowed: false`.
- The synthetic pipeline now runs 9 no-live contracts, all passing, with 0 broken piping.
- The business automation index now maps 21 surfaces, 17 connected, 4 exists-but-not-connected, and 0 loud-failure gaps.

## Source Files

- App surface: `apps/locally_twisted/locally_twisted/paperwork/customer_reminder_dry_run.py`
- Fake-data contract: `apps/locally_twisted/locally_twisted/verify/customer_reminder_dry_run_contract.py`
- Host verifier: `scripts/verify/customer_reminder_dry_run.py`
- Host fake-data verifier: `scripts/verify/customer_reminder_dry_run_contract.py`
- Upstream sources: `unpaid_invoice_review.py`, `unpaid_invoice_draft_packet.py`, and `paperwork_review_digest.py`

## Boundaries

Allowed now:

- internal queue payloads
- JSON/Markdown review packets
- fake-data outlier testing
- cadence suggestions for Jeff/accounting review
- visible blockers for payment path, recipient, invoice status, cadence, and copy

Not allowed in this lane:

- customer email/SMS delivery
- automatic reminder schedules
- Email Queue or Communication creation
- Payment Request, Payment Entry, Journal Entry, Sales Invoice mutation
- live Stripe key or production host dependency
- hiding bank/supplier/payroll gaps

## Next Safe Slice

Build a reviewed Desk page or scheduled internal-only report that displays this dry-run queue. The UI should show invoice, customer, days overdue, balance, recommended cadence, draft sections, and approval checkboxes. It still must not send reminders or mutate accounting records.
