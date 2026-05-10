---
id: customer-email-delivery-branding-contract
name: Customer Email Delivery And Branding Contract
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted ERPNext/Frappe customer/operator email branding, company-copy routing, and Email Queue proof
currently_true: true
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
- Public form confirmation subjects use `Locally Twisted U+1F388 Thanks {first_name}! We'll be in touch within a day`.
- Public form confirmation titles use `Here is what we received`; do not repeat the subject as the message header.
- Public form confirmations must echo only non-empty customer-submitted fields, including free-text notes.
- Public form confirmations must mention reference files only when files were actually attached. The `/contact` and BTFP form path defers the customer confirmation until after upload handling so the count is accurate.
- Public form confirmations use compact policy links, not the full long policy block, to keep print output short.
- The repeat-email/five-photo verifier owns its fake record namespace and must
  clean it. `scripts/verify/book_form_repeat_email_photos.py` deletes old and
  current verifier-owned Leads, uploaded Files, Communications, Email Queue
  rows, Contacts, Tasks, and Comments on localhost; cleanup failure is a
  verifier failure unless `--keep-records` is explicit.
- Review/export previews rendered outside an email client must not leave `cid:`
  image sources in standalone HTML. Rewrite queued inline images to embedded
  data URLs before browser screenshots or PDFs, then verify image dimensions.
- Only public intake confirmations use the playful branded shell with the balloon-dog footer mark.
- Paid receipts, first-order welcome emails, reviewed quote emails, and other customer proof responses use `render_formal_customer_email` with logo-only inline images.
- Internal paid-order notifications use `render_operator_email`: plain, formal, action oriented, and specific to the operator recipient.
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
- `apps/locally_twisted/locally_twisted/verify/book_form_repeat_email_photos_cleanup.py`

## Verification

Run the static policy guard and rollback-safe Email Queue contracts after any
email theme, copy routing, subject, or sendmail change:

```powershell
python scripts/verify/customer_email_policy_contract.py
python scripts/verify/customer_documents_contract.py
python scripts/verify/book_form_repeat_email_photos.py --base-url http://localhost:8081
python scripts/verify/payment_cascade_contract.py
python scripts/verify/product_quote_customer_delivery_contract.py
python scripts/verify/customer_contact_points_contract.py
```

When print fit changes, create a PDF from the actual queued Email Queue HTML
and inspect it through large-document intake. Current proof for the customer
form confirmation is ignored at `output/email-print-fit/customer-form-confirmation.pdf`
and intake reported 1 PDF page. This is not yet global proof for every email
family.

When generating review previews under `output/email-previews/`, run a browser
image check that fails on unresolved images:

```powershell
# This should print no matches; any cid: match means the standalone preview is
# not self-contained. Then use Playwright to fail any image whose
# naturalWidth/naturalHeight is 0.
rg -n "cid:" output/email-previews output/email-print-fit
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
- Letting the playful intake shell leak into receipts, quote approvals,
  operator notifications, invoices, reminders, vendor packets, or legal/billing
  messages.
- Sending the public form confirmation before uploads finish, which makes the
  customer receipt lie about attached files.
- Letting public-form proof scripts leave fake Leads, private Files,
  Communications, Email Queue rows, Contacts, Tasks, or Comments behind. Test
  proof is not clean unless its generated business records are gone.
- Treating a standalone browser/PDF email preview as valid while it still
  contains `src="cid:..."`; that renders as a broken logo even when the queued
  email MIME parts are present for real email clients.
- Re-expanding inquiry emails with long policy blocks until the printed email
  spills onto a second page.
- Adding a new sendmail surface without `document_copy_kwargs(...)`, explicit
  primary recipients, and a verifier marker.
