---
name: ERPNext business automation index
level: recipe
last_verified: 2026-05-06
---

## What it does

Keeps an ERPNext/Frappe business-management build honest by indexing every important automation surface before it is trusted in production.

Use it to classify:

- what exists and is connected
- what exists but is not connected
- what is missing and required
- what is missing but useful
- which paths create fake data for verification
- which paths fail loudly when a launch-required connection breaks

## When to use it

Use this when a client repo starts connecting forms, Leads, CRM stages, checkout, payment requests, invoices, receipts, emails, reminders, bank setup, supplier setup, payroll, scheduled checkups, or Frappe Cloud cutover readiness.

Use it before adding new automation to avoid creating a second hidden path for money, customer communication, or operations.

## LT implementation

Locally Twisted's implementation lives at:

```powershell
python scripts/verify/business_automation_index.py --report output/business-automation-index.json
```

The Frappe-side source is:

```text
apps/locally_twisted/locally_twisted/verify/business_automation_index.py
```

Current connected launch spine:

- public contact form to Lead
- Lead to Contact/acknowledgment/Task cascade
- CRM stage to Task cascade only
- guest checkout to Customer/Contact/Address/Sales Order/Payment Request/Stripe
- paid checkout to Payment Request/Payment Entry/Sales Invoice/receipt/operator/welcome emails
- Stripe amount parity against ERPNext Sales Order totals
- Stripe webhook reconciliation
- branded Sales Invoice print output
- outbound document registry
- paperwork status checkup
- scheduled daily business automation checkup
- Accountant Home parity

## Rules

1. Required surfaces fail the verifier if files, hooks, setup records, methods, or connections are missing.
2. Scheduled checkups should create visible backend attention, such as Frappe Error Log entries, when required links break.
3. Existing-but-not-connected surfaces must stay visible in the report. Do not imply proposals, vendor packets, bank reconciliation, payroll, reminders, or statements are operational just because templates or native DocTypes exist.
4. Fake-data verifiers must clean up generated business records or explicitly mark rollback behavior.
5. Amount parity and customer communication paths must fail loudly. A silent skipped email, undercharged checkout, or disconnected document generator is a business relationship risk.

## Common failure modes

- Treating a template as an operational document generator.
- Treating an ERPNext DocType as ready just because it exists.
- Adding CRM-stage finance automation while checkout already owns the money path.
- Letting hosted checkout line items differ from the ERPNext grand total.
- Running status/inventory checks while rollback-based verifiers are still creating temporary records.
- Leaving missing future surfaces in prose docs instead of a machine-readable verifier report.
