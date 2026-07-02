# Locally Twisted Outbound Documents

This folder is the standard source for files Locally Twisted sends outside the company.

It is intentionally app-owned so ERPNext/Frappe automation can import the same registry later instead of guessing from ad hoc PDFs, screenshots, or one-off notes.

2026-06-28 brand-lane guard: the current registry is LT-lane source, not proof
that the same templates can be used for Commercial Balloon Decor or Memorial
Balloons. Future generators must carry an explicit `operating_brand` and block
send/render readiness when the brand lane, logo, remit-to copy, support inbox,
legal/policy wording, or customer-facing promise is missing.

## Folder Contract

- `registry.py` lists every supported outbound document family and the data it needs.
- `templates/` holds the source templates, answer-first guidance, and automation notes.
- `locally_twisted.verify.outbound_documents_contract` verifies the registry and templates.

## Answer-First Contract

Every outbound document should answer the recipient's practical question before it talks about internal automation, policy mechanics, or brand story.

The high-visibility review area should identify the fields the audience cares about: amount, due date, PO/reference, event date, location, next step, approval path, payment status, or reconciliation contact. Internal automation metadata can remain in source notes and review gates, but it should not occupy the first customer-facing slot.

## Current Document Families

- Sales invoice
- Payment receipt
- Quote / estimate
- Event proposal packet
- Vendor setup / W-9 packet
- Statement of account
- Payment reminder draft
- Event install work order
- Contract acceptance summary
- Post-event reorder follow-up

## Automation Boundary

These templates are ready for generators, review queues, and print/email workflows. They do not approve automatic sending by themselves.

Accounting, legal, payment, reminder, and contract documents still need the review gates named in each template before any live send or posting automation uses them.
