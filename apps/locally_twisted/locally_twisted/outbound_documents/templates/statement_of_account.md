---
id: statement_of_account
title: Statement Of Account
audience: Accounts payable or customer accounting
owner: Accounting / operations
stage: account_reconciliation
status: source_template_ready
automation_ready: generator_ready_review_required
trigger: Customer or accounting requests account balance or open invoice summary
delivery_channel: PDF | reviewed email
record_source: Customer | Sales Invoice | Payment Entry | Payment Request
policy_lanes: corporate_invoicing | privacy
required_fields: customer_name | statement_date | date_range | open_invoices | payments | credits | total_balance | reconciliation_contact
do_not_send_without: verified_customer_ledger | date_range | reviewed_balance | recipient_check
verification: outbound_documents_contract | paperwork_status
template_type: outbound_markdown_v1
---

## Audience

Accounting needs a dated snapshot of `{{ customer.name }}` activity and open balances.

## Answer First

Put statement date, date range, open balance, open invoice count, credits/payments summary, and reconciliation contact at the top so accounting can match records fast.

## Required Data

- Statement date and date range
- Open invoices with invoice numbers, dates, due dates, and balances
- Payments and credits in the same range
- Total open balance
- Reconciliation contact

## Recipient Outcome

The recipient can reconcile their books, identify missing invoices or payments, and resolve balance questions with one clear contact path.

## Automation Notes

Use read-only ledger data first. A future generator should create statement drafts from selected date ranges and customer accounts.

Do not auto-send from this registry. Customer, date range, and balance need human review before release.

## Boundaries

Do not treat a statement as a collections demand. Keep it factual and reconciliation-focused.
