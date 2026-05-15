# Form Email Confirmation Regression - 2026-05-12

## Scope

This handoff owns the May 12 regression and live-cutover closeout for the
shared public inquiry forms on `/contact` and
`/balloon-twisting-and-face-painting`.

It covers customer-visible success copy, customer/company confirmation email
queueing, stale idempotency rows, and the verifiers that keep the submit path
honest. It does not own product-page quote emails, paid receipts, invoice
emails, or finance/legal outbound documents.

2026-05-15 follow-up: the May 12 proof was sufficient for repeat same-email
submit, customer/owner queue existence, body content, recipients, and cleanup.
It was not sufficient for inquiry-photo delivery because it did not inspect CRM
photo rows or owner Email Queue attachment refs. The dedicated follow-up is
`workstreams/inquiry-photo-storage-owner-attachments-2026-05-15.md`.

## Regression

GL submitted both public forms and saw the modal copy:

- `Request received`
- `Thanks, we got it and will follow up soon.`

The expected copy is:

- `Request received`
- `A confirmation of your request will be sent to your email address shortly. We will be in contact within 24 hours!`

The contact-form submission also did not initially queue a current customer
confirmation email even though the customer saw success.

After the public DNS cutover, both live form routes returned the customer-safe
snag copy and the browser console showed:

- `api/method/locally_twisted.www.book.submit_book_inquiry` returned `409`.
- The business did not receive the expected owner notification.
- Existing smoke coverage was insufficient because it checked broad success
  rather than the submitted-detail content and recipient-specific owner email.

## Root Cause

`lead_cascade.py` used Lead reference name alone as the idempotency boundary for
public-form acknowledgments. The Contact submission created
`CRM-LEAD-2026-00073` on 2026-05-11, but an older sent Email Queue row from
2026-05-10 already referenced the same Lead name. The old row made the new Lead
look already acknowledged.

The same stale-record class can affect `Communication` rows, so both checks
must be scoped to the current Lead incarnation by `creation >= doc.creation`.

The live `409` was a second, separate failure: ERPNext's linked Email Address
record is unique, so a second inquiry with the same email could fail while
creating a new Lead. The public form needs repeat same-email inquiries because
one customer can request multiple events. The repair retries the Lead insert
without `email_id` when the unique Email Address link blocks the insert, stores
the customer email in the internal `custom_anything_else` fallback marker for
the current Lead, and strips that marker from customer/owner email bodies.

The Frappe Cloud deployment surfaced a third boundary: a bench deploy hash is
not proof that the live site has migrated to the source schema. The site update
first failed on missing `System Settings.language` / `time_zone`, then on
missing source-owned Lead fields/custom DocTypes, then on an optional legacy
`custom_services` field query. Those are launch blockers until the source app
owns the schema and the site update job succeeds.

## Current State

- `locallytwisted.com` is serving the Frappe Cloud custom app release
  `72a4se4v64` / app hash `04de8212aa7dbf4895716717865fc6e1029c757b`.
- Final Frappe Cloud bench deploy `62q1r0otg1` succeeded.
- Final Frappe Cloud site update/migrate job `15s16992i2` succeeded.
- Public form success copy now promises the confirmation email and 24-hour contact window.
- Direct `#received` visits still do not open fake success.
- The backend throws a customer-safe loud failure if either the customer
  confirmation or the owner/business notification does not queue.
- Confirmation idempotency checks ignore stale `Email Queue` and `Communication` rows from an older Lead with the same name.
- Repeat same-email inquiries are allowed. If ERPNext's unique Email Address
  link blocks a fresh Lead insert, the retry preserves the customer email in the
  Lead notes and email rendering while avoiding the duplicate Email Address
  link.
- The owner/business notification uses `render_operator_email`, is addressed to
  the business, and includes the same customer-submitted details that the
  customer receives.
- The owner/customer email detail blocks strip the internal `Customer email:`
  fallback marker before display.
- The missing Contact confirmation was requeued after the fix.
- 2026-05-15 source now adds a stricter photo-delivery contract: uploaded
  photos must appear as private Lead Files, `custom_inspiration_photos` rows,
  and owner-only Email Queue attachment refs; customer confirmations remain
  attachment-free and count-only. This source fix is pushed but not yet
  live-verified on Frappe Cloud.

Live DB evidence from the screenshot submissions:

| Route | Lead | Email Queue | Status | Recipients |
|---|---|---|---|---|
| `/contact` | `CRM-LEAD-2026-00073` | `gbf0g958qj` | Sent | `locallytwisted@gmail.com`, `cameronbpaul@gmail.com` |
| `/balloon-twisting-and-face-painting` | `CRM-LEAD-2026-00074` | `95fi9c31jm` | Sent | `locallytwisted@gmail.com`, `cameronbpaul@gmail.com` |

The older stale Contact queue row `2eghkl7krg` from 2026-05-10 remains history
but no longer suppresses the current Lead's confirmation.

Final live verifier proof used generated repeat-email Leads
`CRM-LEAD-2026-00006` and `CRM-LEAD-2026-00007`. The verifier proved both
customer queues (`272rcukhrj`, `4734gdkr3d`) and business queues
(`272ri0hilj`, `473363hkdp`), including body content/recipients, then cleaned
the verifier namespace. A cleanup preview after the run returned zero remaining
verifier-owned Leads, Files, Email Queue rows, Communications, Contacts, Tasks,
ToDos, Events, or Comments.

## Owner Files

- `apps/locally_twisted/locally_twisted/lead_cascade.py`
- `apps/locally_twisted/locally_twisted/www/book.py`
- `apps/locally_twisted/locally_twisted/seed/sync_contact_intake_backend.py`
- `apps/locally_twisted/locally_twisted/patches/sync_site_branding.py`
- `apps/locally_twisted/locally_twisted/patches/resync_contact_intake_backend_20260512.py`
- `apps/locally_twisted/patches.txt`
- `apps/locally_twisted/locally_twisted/public/js/lt-inquiry-form-experience.js`
- `apps/locally_twisted/locally_twisted/templates/includes/book_form.html`
- `apps/locally_twisted/locally_twisted/hooks.py`
- `scripts/verify/form_experience.spec.js`
- `scripts/verify/book_form_repeat_email_photos.py`
- `apps/locally_twisted/locally_twisted/verify/book_form_repeat_email_photos_email_contract.py`
- `scripts/verify/frappe_whitelisted_client.py`
- `scripts/verify/smoke_forms.py`
- `apps/locally_twisted/locally_twisted/verify/customer_email_policy_contract.py`

## Verification Receipt

Local proof passed on 2026-05-12:

```powershell
python -m py_compile apps\locally_twisted\locally_twisted\lead_cascade.py apps\locally_twisted\locally_twisted\www\book.py
node --check apps\locally_twisted\locally_twisted\public\js\lt-inquiry-form-experience.js
node --check scripts\verify\form_experience.spec.js
python scripts/dev/clear_website_cache.py
npm run test:form-experience
python scripts/verify/customer_email_policy_contract.py
python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --skip-newsletter
python scripts/verify/book_form_repeat_email_photos.py --base-url http://localhost:8081
```

`docker restart locally-twisted-erpnext-v15-backend-1 locally-twisted-erpnext-v15-frontend-1`
was run before clearing website cache so the local site served the corrected
backend and cache-busted JS.

Live proof passed after the final Frappe Cloud deploy and site update:

```powershell
$env:LT_BACKEND_BASE_URL='https://locallytwisted.v.frappe.cloud'
$env:LT_BACKEND_CDP_URL='http://127.0.0.1:9222'
python scripts\verify\book_form_repeat_email_photos.py --base-url https://locallytwisted.com --admin-base-url https://locallytwisted.v.frappe.cloud --cdp-url http://127.0.0.1:9222
python scripts\verify\smoke_forms.py --base-url https://locallytwisted.com --form-path /contact --skip-newsletter
python scripts\verify\smoke_forms.py --base-url https://locallytwisted.com --form-path /balloon-twisting-and-face-painting --skip-newsletter
```

Strict live verifier output included:

```text
BOOK FORM REPEAT EMAIL + 5 PHOTO CHECK PASSED
email_delivery_verified: True
records_kept: False
```

Live route smokes both reported `FORM SHAPE OK`, `SUCCESS UI VISIBLE`,
`BACKEND VERIFIED`, and `CLEANUP OK`.

## Guardrails

- Do not use Lead name alone as proof a public-form confirmation already sent.
- Do not show `message.ok` or the success modal unless the backend has queued
  the customer confirmation or confirmed a current same-Lead queue row exists.
- Do not return `message.ok` unless the business/owner notification also
  queued or a current same-Lead owner queue row exists.
- Do not accept smoke proof that only says an email queued. Customer and owner
  Email Queue bodies must contain the customer-submitted details; owner copy
  must be directed at the owner, not the customer.
- Do not reject a repeat same-email public inquiry as a duplicate when the
  business treats each inquiry as a separate event/opportunity.
- Do not use `#received`, cookies, localStorage, or static page state to imply
  success.
- Do not let public-form confirmation email failures become console-only logs.
- Do not remove stale historical Email Queue rows as a routine cleanup; scope
  the idempotency query instead.
- Do not treat a Frappe Cloud bench deploy hash as live release proof. The site
  update/migration job and live route/API verifiers must pass.
- Do not treat uploaded-file count, customer/owner queue existence, or message
  body text as photo delivery proof. Photo delivery requires CRM photo rows and
  owner `Email Queue.attachments` `fid` refs.

## Cross-links

- `workstreams/form-submission-experience.md`
- `workstreams/customer-email-policy-boundary.md`
- `workstreams/inquiry-photo-storage-owner-attachments-2026-05-15.md`
- `workstreams/frappe-cloud-cloudflare-stripe-launch-2026-05-11.md`
- `capabilities/recipes/shared-inquiry-form-experience.md`
- `capabilities/recipes/customer-email-delivery-branding-contract.md`
- `capabilities/recipes/erpnext-inquiry-photo-delivery-contract.md`
- `capabilities/recipes/erpnext-intake-form-parity.md`
- `capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`
- `capabilities/failures/public-form-photo-storage-owner-attachment-gap.md`
- `capabilities/failures/public-form-stale-email-queue-idempotency.md`
- `capabilities/failures/public-form-repeat-email-lead-conflict.md`
- `capabilities/failures/frappe-cloud-release-site-migration-drift.md`
