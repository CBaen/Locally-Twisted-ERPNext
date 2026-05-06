---
id: quote_estimate
title: Quote / Estimate
audience: Event buyer, procurement contact, or department coordinator
owner: Sales / event planning
stage: quote_sent
status: source_template_ready
automation_ready: generator_ready_review_required
trigger: Lead reaches quote-ready stage or Quotation is prepared
delivery_channel: PDF | reviewed email
record_source: Lead | Quotation | Customer | Item | Address
policy_lanes: event_balloon_decor | corporate_invoicing | privacy
required_fields: customer_name | event_date | event_location | scope | line_items | assumptions | subtotal | taxes | total | acceptance_path
do_not_send_without: reviewed_scope | reviewed_pricing | event_date | location | acceptance_terms
verification: outbound_documents_contract | customer_documents_contract
template_type: outbound_markdown_v1
---

## Audience

The event buyer needs to know what `{{ quotation.name }}` includes, what it costs, and exactly how to approve it.

## Answer First

Put event date, location, scope summary, estimated total, deposit/payment expectation, and approval path at the top so the buyer knows the decision in front of them.

## Required Data

- Customer and contact: `{{ customer.name }}`
- Event date, install window, teardown window, and location
- Decor scope and itemized estimate
- Assumptions about access, weather, ceiling/attachment limits, and customer-provided details
- Quote expiration or review date
- Acceptance path and payment/deposit expectation

## Recipient Outcome

The buyer can approve, request a revision, or route the estimate to procurement without asking for missing scope or timing details.

## Automation Notes

Use Lead and Quotation data once the scope is reviewed by a human.

Do not auto-send from this registry. A future quote sender should create a draft/review candidate until stage thresholds and approval rules are explicit.

## Boundaries

Do not invent final install promises. Say final install details are confirmed by Locally Twisted before quote/install.
