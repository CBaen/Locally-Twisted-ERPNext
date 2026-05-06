---
id: vendor_setup_w9_packet
title: Vendor Setup / W-9 Packet
audience: Procurement and accounts payable
owner: Accounting / operations
stage: vendor_setup
status: source_template_ready
automation_ready: generator_ready_review_required
trigger: Customer requests vendor setup, W-9, or procurement onboarding
delivery_channel: PDF packet | secure attachment after review
record_source: Company | Customer | Address | approved W-9 file
policy_lanes: corporate_invoicing | privacy
required_fields: legal_business_name | remittance_contact | tax_form_attachment | insurance_contact_if_available | payment_terms | procurement_contact
do_not_send_without: accounting_approved_w9 | verified_business_identity | approved_recipient | secure_attachment_check
verification: outbound_documents_contract
template_type: outbound_markdown_v1
---

## Audience

Procurement and accounts payable need to set up `{{ company.name }}` as a vendor without calling Jeff for basic paperwork.

## Answer First

Put legal business name, remittance contact, W-9 delivery status, PO/reference handling, payment terms, and secure follow-up path at the top so procurement can finish setup.

## Required Data

- Legal business name and public contact details
- Remittance/payment contact
- Current approved W-9 attachment or secure delivery path
- Insurance/contact path if available and approved
- Payment terms and PO/reference handling
- Repeat-event or annual-event contact path

## Recipient Outcome

The customer can complete vendor onboarding and issue a PO or payment request with fewer follow-up emails.

## Automation Notes

The packet can be generated as a draft once a customer requests vendor setup.

Do not auto-send from this registry. W-9 content, legal business facts, tax form freshness, and recipient authorization require accounting review.

## Boundaries

Do not fabricate tax, insurance, or certification claims. This template is a routing shell until the approved files and facts are attached.
