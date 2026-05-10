---
id: payment_receipt
title: Payment Receipt
audience: Customer accounting and accounts receivable reconciliation
owner: Accounting / operations
stage: payment_recorded
status: source_template_ready
automation_ready: generator_ready_review_required
trigger: Payment Entry created or Sales Invoice marked paid
delivery_channel: email body | PDF when needed
record_source: Payment Entry | Sales Invoice | Sales Order | Customer
policy_lanes: ready_to_order_pickup_delivery | corporate_invoicing | privacy
required_fields: receipt_reference | payment_date | amount_paid | payment_method | related_invoice | related_order | remaining_balance | customer_contact
do_not_send_without: recorded_payment | related_invoice_or_order | customer_contact | payment_amount
verification: payment_cascade_contract | customer_documents_contract | outbound_documents_contract
template_type: outbound_markdown_v1
---

## Audience

Customer accounting needs proof that `{{ payment.reference_no or payment.name }}` was recorded against the right order or invoice.

## Answer First

Put amount paid, payment date, receipt/reference, related invoice or order, remaining balance, and reconciliation contact at the top so the recipient can close their books quickly.

## Required Data

- Receipt/payment reference: `{{ payment.name }}`
- Amount paid and payment date
- Related invoice: `{{ invoice.name }}`
- Related order: `{{ sales_order.name }}`
- Remaining balance, if any
- Locally Twisted payment contact

## Recipient Outcome

The recipient can close the payment loop, attach the receipt to their expense record, and reconcile any remaining balance without extra emails.

## Automation Notes

Receipt automation may use the paid-order cascade after it confirms the payment and related invoice status.

Do not auto-send from this registry. The live sender must be idempotent, avoid duplicate receipt emails, and use the code-owned policy blocks.

## Boundaries

This is a receipt, not a corporate invoice. It should clearly say what was paid and what remains, while keeping terms and refund links scoped to the related order.
