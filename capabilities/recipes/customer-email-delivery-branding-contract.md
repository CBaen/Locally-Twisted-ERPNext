---
id: customer-email-delivery-branding-contract
name: Customer Email Delivery And Branding Contract
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted ERPNext/Frappe customer/operator email branding, company-copy routing, and Email Queue proof
currently_true: true
verification_level: 2
last_verified: 2026-06-13
evidence_quality: direct
successful_uses: 6
failed_uses: 4
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
Email Queue assertions, public/company email addresses, or checkout/order-email
privacy copy.

## Current Contract

- 2026-06-28 brand-lane guard: this recipe currently describes the
  `locally_twisted` email lane. Do not reuse its subjects, logos, playful
  shell, inboxes, policy links, or operator-copy assumptions for Commercial
  Balloon Decor or Memorial Balloons without an explicit `operating_brand`
  source and brand-specific rendering proof.
- Public inquiry acknowledgments use `customer_email_theme.py`.
- Public form confirmation subjects use `Locally Twisted U+1F388 Thanks {first_name}! We'll be in touch within a day`.
- Public form confirmation titles use `Here is what we received`; do not repeat the subject as the message header.
- Public form confirmations must echo only non-empty customer-submitted fields, including free-text notes.
- Public form confirmations must mention reference files only when files were actually attached. The `/contact` and BTFP form path defers the customer confirmation until after upload handling so the count is accurate.
- Public form confirmations must not attach customer-submitted inspiration
  photos back to the customer. They are count-only for files.
- Public form confirmation idempotency must be scoped to the current Lead
  incarnation. A historical `Email Queue` or `Communication` row with the same
  `reference_name` is not proof that the current Lead was acknowledged.
- Public form endpoints must fail loudly if the customer confirmation email
  does not queue; they must not return `message.ok` and show public success.
- Public form endpoints must also fail loudly if the owner/business notification
  does not queue; the business has to receive the inquiry details.
- Public form owner/business notifications use `render_operator_email`, go to
  `locallytwisted@gmail.com`, and speak to the business owner, not to the
  customer.
- Public form owner/business notifications may attach submitted photos, but
  only as queued private Lead File refs in `Email Queue.attachments`, such as
  `{"fid": file_doc.name}`. The refs must resolve to Files attached to the
  current Lead.
- Owner/business notification detail tables must contain the same
  customer-submitted fields as the customer confirmation, while stripping
  internal fallback markers such as `Customer email:`.
- Repeat same-email inquiries are legitimate. If ERPNext's linked Email Address
  uniqueness blocks a fresh Lead insert, preserve the customer email in a
  controlled internal fallback and keep email rendering correct.
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
- Paid receipts must include the server-selected Product Setup thumbnail when
  a checkout line has `selected_media`; the image must come from trusted line
  JSON, not from a browser-supplied display URL.
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
- Checkout email copy must stay transactional: invoices, receipts, support, and
  order-related information. Marketing email requires newsletter or marketing
  opt-in and must not be implied by ordinary checkout email collection.
- Known-account password reset emails for external vendors must use the Locally
  Twisted branded reset template/helper, identify the Locally Twisted website
  account, show the account email, link only to `https://locallytwisted.com`,
  explain what other accounts are not reset, and avoid generic Frappe/Built by
  Cameron/Administrator copy.

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
- `apps/locally_twisted/locally_twisted/verify/book_form_repeat_email_photos_email_contract.py`
- `apps/locally_twisted/locally_twisted/verify/customer_contact_points_contract.py`
- `apps/locally_twisted/locally_twisted/password_reset_email.py`
- `apps/locally_twisted/locally_twisted/marketing_access_reset.py`
- `scripts/verify/book_form_repeat_email_photos.py`
- `scripts/verify/frappe_whitelisted_client.py`
- `scripts/verify/customer_contact_points_contract.py`
- `workstreams/form-email-confirmation-regression-2026-05-12.md`
- `workstreams/inquiry-photo-storage-owner-attachments-2026-05-15.md`
- `workstreams/inquiry-form-live-release-2026-05-16.md`
- `capabilities/recipes/erpnext-inquiry-photo-delivery-contract.md`

## Verification

Run the static policy guard and rollback-safe Email Queue contracts after any
email theme, copy routing, subject, or sendmail change:

```powershell
python scripts/verify/customer_email_policy_contract.py
python scripts/verify/customer_documents_contract.py
python scripts/verify/book_form_repeat_email_photos.py --base-url http://localhost:8081
python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --skip-newsletter
python scripts/verify/payment_cascade_contract.py
python scripts/verify/product_quote_customer_delivery_contract.py
python scripts/verify/customer_contact_points_contract.py
npm run test:password-reset-template
npm run test:marketing-access-reset
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

For live public form release proof, use authenticated backend checks and verify
actual Email Queue content:

```powershell
$env:LT_BACKEND_BASE_URL='https://locallytwisted.v.frappe.cloud'
$env:LT_BACKEND_CDP_URL='http://127.0.0.1:9222'
python scripts/verify/book_form_repeat_email_photos.py --base-url https://locallytwisted.com --admin-base-url https://locallytwisted.v.frappe.cloud --cdp-url http://127.0.0.1:9222
python scripts/verify/smoke_forms.py --base-url https://locallytwisted.com --form-path /contact --skip-newsletter
python scripts/verify/smoke_forms.py --base-url https://locallytwisted.com --form-path /balloon-twisting-and-face-painting --skip-newsletter
```

For inquiry-photo changes, the repeat-email/five-photo verifier must prove
customer queues have no attachments and owner/business queues contain private
Lead File `fid` refs in `Email Queue.attachments`. Body text and counts are not
enough.

2026-05-16 live business-email smoke receipt: Lead `CRM-LEAD-2026-00013`,
owner Email Queue `683s86r04b` sent to `locallytwisted@gmail.com` with five
attachment refs, and customer Email Queue `683suhfaa9` sent with zero photo
attachments.

2026-05-17 local ecommerce receipt proof: fake-card Sales Order
`SAL-ORD-2026-00023` sent customer receipt Email Queue `q710cltm2i`; SQL
position check confirmed `/files/lt-proof-large-chrome.png` was present in the
receipt message and recipients were the customer plus `locallytwisted@gmail.com`.

2026-06-13 live external-account reset receipt: branded Locally Twisted reset
Email Queue `e4aqh31606` sent to `marketing@exploringnotboring.com` from
`Locally Twisted <accounting@locallytwisted.com>` after source/app deploy
`456c9a3` / `8b10a92`; safe reset-page check returned HTTP 200 and did not
consume the key.

## Failure Modes

- Treating `Email Queue.status = Sent` as inbox delivery proof. It only proves
  SMTP acceptance.
- Treating any same-reference `Email Queue` or `Communication` row as
  idempotency proof. Public-form confirmations need a current Lead creation
  boundary so old rows cannot suppress newly recreated Leads.
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
- Attaching submitted inspiration photos to the customer confirmation.
- Treating uploaded-file count, `Email Queue.message` body text, or generic
  Lead File rows as proof the owner received photos. Owner delivery requires
  queued `Email Queue.attachments` refs.
- Returning public success when the confirmation email did not queue for the
  current Lead.
- Returning public success when the owner/business notification did not queue
  for the current Lead.
- Treating a smoke test as sufficient when it does not inspect the submitted
  details in the actual customer and owner Email Queue messages.
- Rendering owner notifications with customer-directed copy.
- Leaking the internal `Customer email:` fallback marker into either customer
  or owner email.
- Rejecting a repeat same-email public inquiry as a duplicate event.
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
- Treating checkout email collection as silent marketing-list consent.
- Treating a known-account password reset as complete because public forgot-password UI returned success.
- Letting Frappe generic reset copy, Administrator signature, or Built by Cameron wording reach an external vendor account reset.
- Checking only pre-send HTML and missing MIME/quoted-printable encoded Email Queue content drift.
- Printing or committing a real password-reset token/full URL.
