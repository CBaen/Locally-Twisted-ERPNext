---
id: customer-email-delivery-branding-contract
name: Customer Email Delivery And Branding Contract
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted ERPNext/Frappe customer/operator email branding, company-copy routing, and Email Queue proof
currently_true: unknown
verification_level: 2
last_verified: 2026-05-10
evidence_quality: direct
successful_uses: 1
failed_uses: 0
regressions: 0
depends_on:
  - external-document-audience-contract
  - fail-loud-operating-law
used_by: []
tags:
  - Locally Twisted
  - ERPNext
  - Frappe
  - Email Queue
  - customer email
---

# Customer Email Delivery And Branding Contract

Use this recipe when changing customer acknowledgments, receipts, operator
notifications, welcome emails, internal copy routing, email subjects, Frappe
Email Queue assertions, or public/company email addresses.

## Current Contract

- Public inquiry acknowledgments use `customer_email_theme.py`.
- Public inquiry subject/title is `U+1F388 Locally Twisted U+1F388 We Got Your Message! Be in Touch Soon!`.
- The playful public inquiry subject is only for public forms. Do not use it
  for legal, billing, invoices, receipts, payroll, vendor packets, contracts, or
  other finance/legal emails.
- The branded shell embeds the LT logo and mirrored red balloon-dog footer mark.
- Frappe's standard email footer must stay disabled so customer mail does not
  say `Sent via ERPNext`.
- Public reply identities are role-based:
  - `hi@locallytwisted.com` for general inquiry and web copy.
  - `legal@locallytwisted.com` for legal/policy/accessibility copy and legal paperwork.
  - `billing@locallytwisted.com` for invoices, billing, refunds, payment reconciliation, accounts payable, and payroll.
- Current internal company copies must use delivery-safe BCC to
  `locallytwisted@gmail.com` while ERPNext sends through that same Gmail account.
- Do not use Cloudflare-routed `@locallytwisted.com` aliases as internal copy or
  QA-send targets while they route back into the same Gmail sender.

## Implementation Surfaces

- `apps/locally_twisted/locally_twisted/customer_email_theme.py`
- `apps/locally_twisted/locally_twisted/communication_copy_policy.py`
- `apps/locally_twisted/locally_twisted/email_delivery_guard.py`
- `apps/locally_twisted/locally_twisted/lead_cascade.py`
- `apps/locally_twisted/locally_twisted/www/payment_success.py`
- `apps/locally_twisted/locally_twisted/patches/configure_email_branding.py`
- `apps/locally_twisted/locally_twisted/verify/customer_email_policy_contract.py`
- `apps/locally_twisted/locally_twisted/verify/customer_documents_contract.py`

## Verification

Run the static policy guard and rollback-safe Email Queue contracts after any
email theme, copy routing, subject, or sendmail change:

```powershell
python scripts/verify/customer_email_policy_contract.py
python scripts/verify/customer_documents_contract.py
python scripts/verify/payment_cascade_contract.py
python scripts/verify/customer_contact_points_contract.py
```

When payment/operator paths are touched, also run:

```powershell
python scripts/verify/client_event_automation_matrix.py
python scripts/verify/synthetic_business_pipeline.py --report output/synthetic-business-pipeline.json
```

## Failure Modes

- Treating `Email Queue.status = Sent` as inbox delivery proof. It only proves
  SMTP acceptance.
- Looking up emoji subjects with raw `LIKE "%Subject: ...%"`. Find rows by
  reference record and decode the MIME subject instead.
- Sending company copies to `hi@locallytwisted.com` while the sender is
  `locallytwisted@gmail.com`; that routed-alias loop can disappear from the
  expected inbox.
- Reintroducing Frappe's standard footer or any `Sent via ERPNext` marker into
  customer mail.
- Applying the playful public-form subject to finance/legal surfaces that need
  professional role-specific subjects.
- Adding a new sendmail surface without `document_copy_kwargs(...)`, explicit
  primary recipients, and a verifier marker.
