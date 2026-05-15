# Customer Email Policy Boundary

Last updated: 2026-05-15 by Codex after the inquiry-photo storage and owner
attachment hotfix.

## Outcome

Keep customer/operator email behavior aligned with receipts, policy lanes, and bookkeeping expectations without sending live email or mutating accounting records during verification.

## Current State

- `locally_twisted.verify.customer_email_policy_contract.run` statically checks source code for inquiry acknowledgment, paid receipt, operator notification, first-order welcome, and paid-order cascade coverage.
- `scripts/verify/customer_email_policy_contract.py` runs the in-app contract through Docker/Frappe and exits nonzero on missing policy markers, attachment/PDF kwargs, wrong reference DocTypes, or non-queued sendmail calls.
- Public customer-facing inboxes are role-based: `hi@locallytwisted.com` for general inquiry/web copy, `legal@locallytwisted.com` for legal/policy/accessibility copy and legal paperwork, and `billing@locallytwisted.com` for invoices, billing, refunds, payment reconciliation, accounts payable, and payroll.
- Public inquiry acknowledgments use `customer_email_theme.py`: LT logo, mirrored red balloon-dog footer mark, no ERPNext standard footer, and dynamic subject `Locally Twisted U+1F388 Thanks {first_name}! We'll be in touch within a day`.
- The public form endpoint defers the customer confirmation until after inspiration-photo handling, so the confirmation can accurately say how many reference files were received. Direct Website Lead inserts still use the same renderer without a file-count line.
- Customer confirmations remain attachment-free. They may report the count of
  received reference files, but they must not attach customer-submitted photos
  back to the customer.
- Public form success requires current customer confirmation and owner/business
  notification Email Queue proof. Stale `Email Queue` or `Communication` rows
  from an older Lead with the same name must not suppress a newly recreated
  Lead's confirmation. Idempotency checks are scoped by the current Lead
  creation time.
- If `frappe.sendmail` returns without a current customer confirmation or
  owner/business notification `Email Queue` row, the public form endpoint must
  fail loudly with customer-safe copy and must not return `message.ok`.
- Owner/business public-inquiry notifications use `render_operator_email`,
  go to `locallytwisted@gmail.com`, speak to the business owner, and include
  the same customer-submitted details as the customer receipt.
- Owner/business public-inquiry notifications may attach submitted photos, but
  only by resolving private `File` docs attached to the same Lead and queuing
  `Email Queue.attachments` refs such as `{"fid": file_doc.name}`. A body count
  is not proof of owner photo delivery.
- Internal fallback markers such as `Customer email:` must be stripped from
  customer and owner email bodies.
- Repeat same-email public inquiries are allowed. ERPNext Email Address
  uniqueness cannot reject a legitimate second event/opportunity with `409`;
  the retry path preserves the submitted customer email without linking a
  duplicate Email Address row.
- Customer form confirmations use the email title `Here is what we received` instead of repeating the subject line. The body echoes only non-empty fields the customer submitted, includes free-text notes, and only includes `We received X files for reference.` when files were attached.
- Customer form confirmations tell customers to reply if anything looks wrong. Current reply-to stays `hi@locallytwisted.com`; external customer replies should route through Cloudflare, but same-Gmail routed-alias QA sends are blocked/unsafe while ERPNext sends from `locallytwisted@gmail.com`.
- Inquiry confirmation policy copy is compact links, not the full long policy block, so the email is better suited for one-page printing.
- The playful branded intake shell is for public form confirmations only. Paid receipts, first-order welcome, reviewed quote emails, and operator paid-order notifications use restrained formal shells specific to the recipient.
- Formal customer emails use `render_formal_customer_email` and logo-only inline images. Internal operator action emails use `render_operator_email`; they should be plain, scannable, and Desk/action oriented.
- The playful public inquiry subject is limited to public forms. Do not reuse it on legal, billing, receipt, invoice, payroll, vendor, or other finance/legal emails.
- `configure_email_branding.py` disables Frappe's standard email footer through System Settings/defaults so customer mail does not say `Sent via ERPNext`.
- `locally_twisted.communication_copy_policy` owns standing internal copy routing: current internal copy delivery goes to `locallytwisted@gmail.com`.
- `hi@locallytwisted.com` and `cameron@locallytwisted.com` are Cloudflare-routed aliases back into the same Gmail SMTP account; do not use routed aliases as internal copy or QA-send targets while the sender is `locallytwisted@gmail.com`.
- `locally_twisted.email_delivery_guard` is wired to `Email Queue.before_insert` and blocks routed-alias loop sends even when a live probe bypasses `communication_copy_policy`.
- Cameron is not a standing future copy recipient. Use a non-LT mailbox for explicit one-time QA/review sends unless the SMTP sender changes.
- `scripts/verify/customer_documents_contract.py` and `scripts/verify/payment_cascade_contract.py` now prove the required copy recipients exist in ERPNext `Email Queue Recipient` rows during rollback-safe fake-data runs.
- `scripts/verify/book_form_repeat_email_photos.py --base-url http://localhost:8081` proves the real form path can queue customer and business notifications after uploads, include the correct file count, and preserve submitted details. It now cleans verifier-owned fake Leads, uploaded Files, Communications, Email Queue rows, Contacts, Tasks, and Comments before/after the run; cleanup failure is a test failure unless `--keep-records` is explicitly used for debugging.
- 2026-05-15 local source proof extends the repeat-email/five-photo verifier to
  prove CRM photo rows and owner-only Email Queue attachment refs while keeping
  customer queues attachment-free. Production still needs Frappe Cloud deploy,
  site update/migrate, and live verifier proof for this new contract.
- Live release proof on 2026-05-12 ran the same verifier against
  `https://locallytwisted.com` with authenticated Frappe Cloud backend CDP and
  verified customer and owner Email Queue bodies/recipients for two repeat
  same-email, five-photo submissions.
- One-page print proof for the current customer-form confirmation was generated from a real queued five-photo test Email Queue row at ignored path `output/email-print-fit/customer-form-confirmation.pdf`; large-document intake reported 1 PDF page. This proves the customer-form confirmation sample, not every outbound email family.
- Current visual review previews live under ignored `output/email-previews/`: `customer-form-confirmation.html`, `.png`, `.pdf`, and `email-preview-gallery.html` / `.png` for intake, formal customer, and operator examples.
- Email clients resolve queued inline images through `cid:` MIME parts, but standalone browser/PDF review renders do not. Preview exports must rewrite those `cid:` image sources to embedded data URLs before screenshot/PDF capture, then fail if any image has `naturalWidth` or `naturalHeight` of 0.
- Business automation index now treats this contract as part of Lead acknowledgment and paid-order reconciliation.
- Synthetic business pipeline now includes `customer_email_policy_boundaries`.
- Checkout and policy copy now state the order-email boundary plainly: checkout
  email is used for invoices, receipts, support, and order-related information.
  Marketing email is separate and requires newsletter/marketing opt-in.

## Boundaries

The static/rollback policy contract has these boundaries:

- No customer email is sent.
- No Email Queue row is created by this verifier.
- No Sales Invoice, Payment Request, Payment Entry, or Communication is mutated.
- No PDF or print attachment kwargs are allowed in the checked sendmail calls.
- This is source-policy verification, not final copy approval.
- Internal business copies are queued as BCC where possible so outside recipients do not see the copy-routing address.
- Verifier runs must set Frappe test email flags before queue assertions; rollback-safe database tests are not delivery-safe if a background mail worker can send routed aliases first.

The live public-form verifier is different: it intentionally creates and cleans
real verifier-owned Leads, Files, Communications, Email Queue rows, Contacts,
Tasks, and Comments so the production form and email path are actually proven.
For inquiry photos, it must also prove Lead photo child rows and owner
`Email Queue.attachments` `fid` refs; customer queue attachments must remain
absent.

## Owner Files

- `apps/locally_twisted/locally_twisted/verify/customer_email_policy_contract.py`
- `scripts/verify/customer_email_policy_contract.py`
- `apps/locally_twisted/locally_twisted/customer_email_theme.py`
- `apps/locally_twisted/locally_twisted/public/icons/lt-balloon-dog-red-email-mirrored.png`
- `apps/locally_twisted/locally_twisted/patches/configure_email_branding.py`
- `apps/locally_twisted/locally_twisted/verify/customer_documents_contract.py`
- `apps/locally_twisted/locally_twisted/verify/book_form_repeat_email_photos_cleanup.py`
- `apps/locally_twisted/locally_twisted/verify/book_form_repeat_email_photos_email_contract.py`
- `apps/locally_twisted/locally_twisted/lead_cascade.py`
- `apps/locally_twisted/locally_twisted/www/book.py`
- `apps/locally_twisted/locally_twisted/www/payment_success.py`
- `apps/locally_twisted/locally_twisted/communication_copy_policy.py`
- `apps/locally_twisted/locally_twisted/verify/payment_cascade_contract.py`
- `apps/locally_twisted/locally_twisted/verify/customer_contact_points_contract.py`
- `apps/locally_twisted/locally_twisted/verify/business_automation_index.py`
- `apps/locally_twisted/locally_twisted/verify/synthetic_business_pipeline.py`
- `scripts/verify/synthetic_business_pipeline.py`
- `scripts/verify/book_form_repeat_email_photos.py`
- `scripts/verify/frappe_whitelisted_client.py`
- `scripts/verify/customer_contact_points_contract.py`
- `workstreams/form-email-confirmation-regression-2026-05-12.md`
- `workstreams/inquiry-photo-storage-owner-attachments-2026-05-15.md`
- `capabilities/recipes/erpnext-inquiry-photo-delivery-contract.md`

## Verification

```powershell
python scripts/verify/customer_email_policy_contract.py
python scripts/verify/customer_documents_contract.py
python scripts/verify/book_form_repeat_email_photos.py --base-url http://localhost:8081
python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --skip-newsletter
python scripts/verify/payment_cascade_contract.py
python scripts/verify/product_quote_customer_delivery_contract.py
python scripts/verify/customer_contact_points_contract.py
python scripts/verify/synthetic_business_pipeline.py --report output/synthetic-business-pipeline.json
python scripts/verify/business_automation_index.py --report output/business-automation-index.json
```

Live release proof:

```powershell
$env:LT_BACKEND_BASE_URL='https://locallytwisted.v.frappe.cloud'
$env:LT_BACKEND_CDP_URL='http://127.0.0.1:9222'
python scripts/verify/book_form_repeat_email_photos.py --base-url https://locallytwisted.com --admin-base-url https://locallytwisted.v.frappe.cloud --cdp-url http://127.0.0.1:9222
python scripts/verify/smoke_forms.py --base-url https://locallytwisted.com --form-path /contact --skip-newsletter
python scripts/verify/smoke_forms.py --base-url https://locallytwisted.com --form-path /balloon-twisting-and-face-painting --skip-newsletter
```

## Next Safe Slice

Next email work should be either provider/sender architecture review, a formal
print-fit verifier that covers every outbound email family, or expanding
content-body proof to the next outbound email family. Do not treat the
customer-form one-page proof as global proof for receipts, operator notices,
welcome emails, reminders, or finance/legal packets. If LT moves away from
Gmail-as-sender or changes Cloudflare routing, revalidate whether
`hi@locallytwisted.com` can become an internal delivery mailbox. Keep delivery
no-live until recipients, opt-out/response handling, and approval gates are
explicit.
