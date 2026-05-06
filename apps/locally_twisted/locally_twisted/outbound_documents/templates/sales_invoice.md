---
id: sales_invoice
title: Sales Invoice
audience: Accounts payable and customer bookkeepers
owner: Accounting / operations
stage: issued_invoice
status: source_template_ready
automation_ready: generator_ready_review_required
trigger: Sales Invoice submitted or printed
delivery_channel: ERPNext Print Format | PDF | reviewed email
record_source: Sales Invoice | Customer | Contact | Address | Payment Terms Template
policy_lanes: corporate_invoicing | refund_policy | privacy
required_fields: invoice_number | invoice_date | due_date | bill_to | po_reference | expense_category | itemized_lines | taxes | total | balance_due | payment_contact
do_not_send_without: submitted_invoice | verified_customer | itemized_total | approved_payment_terms
verification: invoice_branding_contract | outbound_documents_contract
template_type: outbound_markdown_v1
---

## Audience

Accounts payable needs to log `{{ invoice.name }}` without asking Locally Twisted for basics.

## Answer First

Put invoice number, due date, PO/reference, balance due, and payment/contact path at the top so the bookkeeper can identify what this is before reading terms or support copy.

## Required Data

- Invoice number: `{{ invoice.name }}`
- Customer / bill-to: `{{ customer.name }}`
- PO / reference: `{{ invoice.po_no or invoice.name }}`
- Invoice date, due date, status, balance due
- Expense category: event decor / balloon services
- Itemized lines, tax, total, paid amount, and open balance
- Customer service, continued event support, and repeat-order routing through invoice reply

## Recipient Outcome

The bookkeeper can enter the invoice, route it for approval, pay it, and reply to the invoice for customer service, continued event support, or repeat orders.

## Automation Notes

The current production source is the ERPNext `Locally Twisted Sales Invoice` Print Format owned by `locally_twisted.seed.sync_invoice_branding`.

Do not auto-send from this registry. A future sender must confirm the Sales Invoice is real, terms are approved, the recipient is correct, and the generated PDF passes the invoice branding contract.

## Boundaries

Keep this black, white, and neutral gray with the text logo, clean rules, one-line invoice number, gray vertical callouts for secondary information, and accounting-first layout. The bottom support bar stays solid black with white customer-service copy. Do not move gold, dog-logo, patriotic proposal, or event-packet decoration into ordinary Sales Invoices.
