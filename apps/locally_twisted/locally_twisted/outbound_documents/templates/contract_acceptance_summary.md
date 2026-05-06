---
id: contract_acceptance_summary
title: Contract Acceptance Summary
audience: Corporate buyer, procurement, legal, or event owner
owner: Sales / accounting
stage: booking_acceptance
status: source_template_ready
automation_ready: generator_ready_review_required
trigger: Quote, Sales Order, or Sales Invoice is accepted for a contract-sensitive booking
delivery_channel: PDF | reviewed email
record_source: Quotation | Sales Order | Sales Invoice | Customer
policy_lanes: event_balloon_decor | corporate_invoicing | refund_policy | privacy
required_fields: accepted_scope | accepted_amount | acceptance_date | payment_terms | incorporated_policy_links | signer_or_approver | contract_exception_notes
do_not_send_without: legal_or_accounting_review | accepted_scope | accepted_amount | approved_terms_language
verification: outbound_documents_contract | customer_documents_contract
template_type: outbound_markdown_v1
---

## Audience

Corporate buyers and procurement teams need a concise record of what `{{ customer.name }}` accepted and what terms govern the booking.

## Answer First

Put accepted record, accepted amount, acceptance date, approver/status, governing terms source, and contract/procurement contact at the top so the recipient can file the approval record.

## Required Data

- Accepted quote/order/invoice reference
- Accepted scope and amount
- Acceptance date and approver, when known
- Payment terms, policy links, and exception notes
- Contact for contract or procurement questions

## Recipient Outcome

The recipient can keep one summary with their purchase approval record and know where the full invoice, quote, or contract terms live.

## Automation Notes

This is a summary, not a substitute for attorney-drafted contract language.

Do not auto-send from this registry. Legal/accounting approval is required before this document is used for contract-sensitive work.

## Boundaries

Do not invent contract clauses. Only summarize accepted records and approved policy/contract language.
