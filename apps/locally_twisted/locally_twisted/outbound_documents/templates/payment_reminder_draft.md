---
id: payment_reminder_draft
title: Payment Reminder Draft
audience: Accounts payable or customer payment contact
owner: Accounting / operations
stage: collections_review
status: source_template_ready
automation_ready: generator_ready_review_required
trigger: Sales Invoice appears unpaid or overdue in a review queue
delivery_channel: draft email only
record_source: Sales Invoice | Customer | Contact | Payment Request
policy_lanes: corporate_invoicing | privacy
required_fields: invoice_number | due_date | balance_due | payment_link_if_available | payment_contact | internal_review_reason
do_not_send_without: human_approval | correct_recipient | reviewed_invoice_status | approved_cadence
verification: outbound_documents_contract | paperwork_status
template_type: outbound_markdown_v1
---

## Audience

Accounts payable needs a clean reminder about `{{ invoice.name }}` only after Locally Twisted confirms the status and recipient.

## Answer First

Put invoice number, due date, balance due, payment path, and reply path at the top so the recipient can pay or flag a reconciliation issue without reading a sales-style note.

## Required Data

- Invoice number, due date, and balance due
- Payment link or payment instructions if available
- Customer payment contact
- Internal reason the reminder candidate was created
- Prior reminder history, if any

## Recipient Outcome

The recipient can find and pay the invoice or reply with a reconciliation issue without feeling pressured by a sales email.

## Automation Notes

Generate reminder candidates from unpaid/overdue invoice review, not from CRM stage changes.

Do not auto-send from this registry. Reminder copy, cadence, recipient, and edge cases require explicit human approval before anything leaves the system.

## Boundaries

No automatic collections language, late-fee threat, or repeated follow-up without approved rules.
