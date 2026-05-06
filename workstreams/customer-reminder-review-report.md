# Customer Reminder Review Report

Last updated: 2026-05-06 by Codex after adding the no-live report data source.

## Outcome

Give Jeff/accounting a report-ready view of the customer reminder dry-run queue without going live.

This layer turns no-live queue items into:

- table columns for invoice, customer, days overdue, balance, cadence, drafts, send status, and blockers
- report rows that stay `internal_review_only` and `draft_only_not_sent`
- groups for `review_now`, `hold`, and `blocked_send`
- optional ignored JSON, Markdown, and CSV artifacts for review

It does not send reminders, queue email, create Communications, mutate invoices, create payment records, or enable automatic cadence.

## Current Verified State

Fresh local verification on 2026-05-06:

```powershell
python scripts/verify/customer_reminder_review_report_contract.py
python scripts/verify/customer_reminder_review_report.py --report output/customer-reminder-review-report.json --markdown output/customer-reminder-review-report.md --csv output/customer-reminder-review-report.csv
python scripts/verify/synthetic_business_pipeline.py --report output/synthetic-business-pipeline.json
python scripts/verify/business_automation_index.py --report output/business-automation-index.json
```

Current result:

- `customer_reminder_review_report_contract.py` passed 3 fake scenarios: mixed queue grouping, empty queue, and malformed send-enabled source rejection.
- `customer_reminder_review_report.py` passed against local ERPNext with 1 row for `ACC-SINV-2026-00001`.
- The report row is `internal_review_only`, `draft_only_not_sent`, and `customer_delivery_enabled: false`.
- The row is grouped under `review_now` with cadence `review_now_payment_reminder`.
- The synthetic pipeline now runs 10 no-live contracts, all passing, with 0 broken piping.
- The business automation index now maps 22 surfaces, 18 connected, 4 exists-but-not-connected, and 0 loud-failure gaps.

## Source Files

- App surface: `apps/locally_twisted/locally_twisted/paperwork/customer_reminder_review_report.py`
- Fake-data contract: `apps/locally_twisted/locally_twisted/verify/customer_reminder_review_report_contract.py`
- Host verifier: `scripts/verify/customer_reminder_review_report.py`
- Host fake-data verifier: `scripts/verify/customer_reminder_review_report_contract.py`
- Source queue: `apps/locally_twisted/locally_twisted/paperwork/customer_reminder_dry_run.py`

## Boundaries

Allowed now:

- internal report rows
- JSON/Markdown/CSV review artifacts under ignored `output/`
- fake-data report-shape testing
- grouping reminders into review/hold/blocked buckets

Not allowed in this lane:

- customer email/SMS delivery
- automatic reminder schedules
- Email Queue or Communication creation
- Payment Request, Payment Entry, Journal Entry, Error Log, or Sales Invoice mutation
- treating the report as approval to send reminders

## Recursion Guard

The report consumes `customer_reminder_dry_run.run()`, and the dry run consumes `paperwork_review_digest.run()`. The digest and synthetic pipeline call `business_automation_index.run(...)` with both `include_customer_reminders=False` and `include_customer_reminder_report=False` so the index can classify these surfaces without recursively invoking itself through the digest chain.

## Next Safe Slice

Build the Desk page that displays these rows for Jeff/accounting review. Keep the first Desk version read-only with review checkboxes or notes only; do not add a send action until recipient, cadence, copy, payment path, approval logging, and opt-out handling are explicitly approved.
