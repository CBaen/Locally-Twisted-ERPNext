---
name: ERPNext no-live customer reminders
level: recipe
last_verified: 2026-05-06
---

## What it does

Sets up customer reminder readiness without going live. The system can identify unpaid/overdue invoices, render draft reminder/statement sections, suggest cadence, show blockers, and shape internal report rows while proving no customer delivery or accounting mutation happens.

## When to use it

Use this before adding payment reminders, statements of account, collections follow-up, or scheduled internal paperwork reports in ERPNext/Frappe.

Use it when the business wants reminder infrastructure but has not approved live customer sending, reminder cadence, recipient rules, or payment-path cutover.

## LT implementation

The current no-live reminder queue is:

```bash
python scripts/verify/customer_reminder_dry_run.py --report output/customer-reminder-dry-run.json --markdown output/customer-reminder-dry-run.md
```

The current no-live reminder review report is:

```bash
python scripts/verify/customer_reminder_review_report.py --report output/customer-reminder-review-report.json --markdown output/customer-reminder-review-report.md --csv output/customer-reminder-review-report.csv
```

Fake scenario coverage is:

```bash
python scripts/verify/customer_reminder_dry_run_contract.py
python scripts/verify/customer_reminder_review_report_contract.py
```

This surface depends on:

- `unpaid_invoice_review.py`
- `unpaid_invoice_draft_packet.py`
- `paperwork_review_digest.py`

## Rules

1. The reminder dry run and review report must return `send_allowed: false`, `customer_delivery_enabled: false`, `automatic_delivery_enabled: false`, and `mutation_allowed: false`.
2. Queue items must use `delivery_mode: internal_review_only` and `send_status: draft_only_not_sent`.
3. Report rows must also carry `delivery_mode: internal_review_only`, `send_status: draft_only_not_sent`, and customer-delivery-disabled flags so a future UI cannot mistake rows for send approval.
4. Every queue item must block customer delivery until human approval, recipient, invoice status, cadence, and copy are reviewed.
5. Missing payment paths must be explicit blockers, not hidden warnings.
6. Fake-data contracts should cover current unpaid, overdue, severely overdue, missing-payment-path, empty, grouped-report, and malformed send-enabled scenarios.
7. Live Stripe keys, production host checks, and real customer sends stay outside this recipe until cutover and approval.

## Failure modes

- A dry-run queue item quietly looks ready to send.
- A missing payment request is treated as a minor note instead of a delivery blocker.
- Automatic cadence gets enabled before reminder timing and audience rules are approved.
- A scheduled internal digest accidentally creates Email Queue or Communication rows.
- The aggregate automation index recursively checks the reminder surface through its own digest source.
- A report row hides delivery flags and becomes easy to wire to a send button later.
