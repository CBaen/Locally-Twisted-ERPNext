# Customer Reminder Review Report

Last updated: 2026-05-08 by Codex after adding the internal Desk Script Report.

## Outcome

Give Jeff/accounting a Desk-accessible report view of the customer reminder dry-run queue without going live.

This layer turns no-live queue items into:

- table columns for invoice, customer, days overdue, balance, cadence, drafts, send status, and blockers
- report rows that stay `internal_review_only` and `draft_only_not_sent`
- groups for `review_now`, `hold`, and `blocked_send`
- optional ignored JSON, Markdown, and CSV artifacts for review
- the `LT Customer Reminder Review` Desk Script Report and Accountant Home shortcut

It does not send reminders, queue email, create Communications, mutate invoices, create payment records, or enable automatic cadence.

## Current Verified State

Fresh local verification on 2026-05-08:

```powershell
python scripts/setup/sync_finance_workspace.py
python scripts/verify/finance_workspace_parity.py
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
- `sync_finance_workspace.py` ensured the `LT Customer Reminder Review` Report record and Accountant Home shortcut.
- `finance_workspace_parity.py` passed and exercises Frappe's `frappe.desk.query_report.run` path for the report.
- The synthetic pipeline now runs 15 no-live contracts, all passing, with 0 broken piping.
- The business automation index now maps 24 surfaces, 21 connected, 3 exists-but-not-connected, and 0 loud-failure gaps.

## Source Files

- App surface: `apps/locally_twisted/locally_twisted/paperwork/customer_reminder_review_report.py`
- Desk report adapter: `apps/locally_twisted/locally_twisted/locally_twisted/report/lt_customer_reminder_review/lt_customer_reminder_review.py`
- Desk report record: `apps/locally_twisted/locally_twisted/locally_twisted/report/lt_customer_reminder_review/lt_customer_reminder_review.json`
- Workspace/report sync: `apps/locally_twisted/locally_twisted/seed/sync_finance_workspace.py`
- Fake-data contract: `apps/locally_twisted/locally_twisted/verify/customer_reminder_review_report_contract.py`
- Host verifier: `scripts/verify/customer_reminder_review_report.py`
- Host fake-data verifier: `scripts/verify/customer_reminder_review_report_contract.py`
- Workspace/report verifier: `scripts/verify/finance_workspace_parity.py`
- Source queue: `apps/locally_twisted/locally_twisted/paperwork/customer_reminder_dry_run.py`

## Boundaries

Allowed now:

- internal report rows
- the internal Desk Script Report and Accountant Home shortcut
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

Audit receipt/operator/welcome/inquiry acknowledgment email bodies so policy lanes and attachment boundaries stay correct. Keep it verifier-only: no new sends, no PDF attachments, and no customer-delivery actions.
