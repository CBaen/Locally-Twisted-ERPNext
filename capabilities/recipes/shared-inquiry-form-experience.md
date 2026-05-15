---
id: shared-inquiry-form-experience
name: Shared Inquiry Form Experience
schema_version: 2.1
profile: governed
level: recipe
maturity: candidate
scope: Locally Twisted shared inquiry-v1 public form experience on /contact and service-page embeds
currently_true: true
verification_level: 2
last_verified: 2026-05-15
evidence_quality: direct
successful_uses: 6
failed_uses: 5
regressions: 0
depends_on:
  - erpnext-intake-form-parity
  - fail-loud-operating-law
  - responsive-container-audit
used_by:
  - form-submission-experience
  - btfp-live-service-page-contract
tags:
  - Locally Twisted
  - inquiry form
  - contact
  - BTFP
  - spam gate
  - sales filter
  - modal
  - fail loud
  - UX
---

# Shared Inquiry Form Experience

Use this before changing the visible submit flow, modal, validation copy,
cookie notice placement, or JavaScript behavior for the shared `inquiry-v1`
form. The current consumers are `/contact` and the embedded form on
`/balloon-twisting-and-face-painting`.

This recipe does not own Lead schema parity or field taxonomy. Use
`erpnext-intake-form-parity` for public-field-to-ERPNext mapping.

## Contract

- The form remains guest-friendly; login is not required.
- The form must render a signed `lt_form_token` and an invisible `website`
  honeypot.
- Backend submit must reject missing, malformed, too-fast, stale, or
  honeypot-filled posts before Lead creation, customer confirmation, owner
  notification, or file handling.
- Repeat inquiries from the same email are allowed when the business treats each Lead as a separate event/opportunity.
- Repeat same-email inquiries must not return `409` only because ERPNext's
  linked Email Address row is unique.
- The visible success state is caused only by the verified submit path.
- A route hash such as `/contact#received` must not open a success modal by
  itself.
- The submit flow may show progress while sending, but it must not imply final
  success until the backend response includes `message.ok`.
- The backend may return `message.ok` only after the current customer
  confirmation email queues or a current same-Lead queue row exists. A stale
  `Email Queue` or `Communication` row from an older Lead with the same name is
  not proof.
- The backend may return `message.ok` only after the current owner/business
  notification queues or a current same-Lead owner queue row exists.
- Exception: a high-confidence sales solicitation may return the normal
  customer-safe response while suppressing only the owner notification, but only
  when the Lead is still saved and an audit comment records the suppression.
- The success message is `A confirmation of your request will be sent to your
  email address shortly. We will be in contact within 24 hours!`
- Customer-facing failure copy stays calm, plain, and non-technical. Internal
  exception text stays out of public UI.
- Success stays on-page with quiet confirmation. Do not restore the forced
  4-second redirect away from the form, a next-step lecture, or a browse-away
  link.
- The modal must be accessible enough for normal keyboard and screen-reader
  use: labelled dialog, short described message, close action, and no hidden
  fake success route.
- Up to five real inspiration-photo uploads must attach successfully on the backend when selected.
- Backend proof for selected inspiration photos includes private Lead Files,
  matching `custom_inspiration_photos` rows, customer Email Queue rows with no
  attachments, and owner Email Queue rows with private Lead File `fid`
  attachment refs.
- Empty upload slots from the browser are not submitted photos. Do not surface
  an inspiration-photo warning unless a real selected file failed validation or
  attachment.
- Cookie or preference notices on form pages must not overlay required fields,
  submit buttons, or validation copy. On current LT form routes, the notice
  renders inline after the form grid.

## Source Files

- `apps/locally_twisted/locally_twisted/templates/includes/book_form.html`
- `apps/locally_twisted/locally_twisted/public/js/lt-inquiry-form-experience.js`
- `apps/locally_twisted/locally_twisted/inquiry_sales_filter.py`
- `apps/locally_twisted/locally_twisted/public/css/lt-form-experience.css`
- `apps/locally_twisted/locally_twisted/public/js/lt-site-preferences.js`
- `scripts/verify/form_experience.spec.js`
- `scripts/verify/inquiry_spam_gate.py`
- `scripts/verify/inquiry_sales_solicitation_filter.py`
- `workstreams/form-submission-experience.md`
- `workstreams/form-email-confirmation-regression-2026-05-12.md`
- `workstreams/inquiry-photo-storage-owner-attachments-2026-05-15.md`
- `workstreams/inquiry-form-spam-sales-filter-2026-05-15.md`
- `capabilities/recipes/erpnext-inquiry-photo-delivery-contract.md`

## Verification

Focused form experience:

```powershell
npm run test:form-experience
python scripts/verify/inquiry_spam_gate.py --base-url http://localhost:8081
python scripts/verify/inquiry_sales_solicitation_filter.py --base-url http://localhost:8081
```

Backend submit and cleanup:

```powershell
python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --skip-newsletter
python scripts/verify/book_form_repeat_email_photos.py --base-url http://localhost:8081
python scripts/verify/customer_email_policy_contract.py
```

Live public form release proof:

```powershell
$env:LT_BACKEND_BASE_URL='https://locallytwisted.v.frappe.cloud'
$env:LT_BACKEND_CDP_URL='http://127.0.0.1:9222'
python scripts/verify/book_form_repeat_email_photos.py --base-url https://locallytwisted.com --admin-base-url https://locallytwisted.v.frappe.cloud --cdp-url http://127.0.0.1:9222
python scripts/verify/smoke_forms.py --base-url https://locallytwisted.com --form-path /contact --skip-newsletter
python scripts/verify/smoke_forms.py --base-url https://locallytwisted.com --form-path /balloon-twisting-and-face-painting --skip-newsletter
```

Useful adjacent checks after form markup, cache-buster, or page-shell changes:

```powershell
python scripts/verify/contact_prefill.py --base-url http://localhost:8081
python scripts/verify/contact_service_logic.py --base-url http://localhost:8081
python scripts/verify/inquiry_upload_failure_contract.py
npm run test:container-contract
npm run test:a11y-manual
```

## Red Flags

- A success modal appears from a URL hash, cookie, localStorage flag, or any
  path other than a verified backend submit response.
- The form posts successfully without a current signed token.
- A honeypot-filled post creates a Lead, Email Queue row, Communication, or
  File.
- A customer sees "sent" or "received" copy while the AJAX request failed,
  returned a non-OK response, or returned a response without `message.ok`.
- A customer sees "Request received" while the confirmation email did not
  queue for the current Lead.
- A customer sees "Request received" while the owner/business notification did
  not queue for the current Lead.
- The owner notification does not include the same submitted details the
  customer provided, or speaks to the owner as if they were the customer.
- A sales pitch suppresses owner notification without leaving a Lead comment or
  explicit suppression metadata.
- A real event/customer inquiry is classified as a sales solicitation only
  because it mentions corporate, marketing, school, nonprofit, or business
  context.
- Idempotency checks use Lead reference name alone instead of the current
  Lead's creation boundary.
- A customer sees an inspiration-photo warning when no file was selected.
- A repeat customer email is rejected as a duplicate Lead.
- A live verifier checks only that an email queued, not that the customer and
  owner Email Queue bodies contain the submitted details.
- The UI claims "Up to 5 images" but the endpoint only proves one/no uploaded file path.
- Uploaded Lead Files exist, but the CRM photo table or owner Email Queue
  attachment refs are empty.
- The form reintroduces the removed progress-step text (`Details checked`,
  `Saved for follow-up`) or the `No account needed` helper line.
- A cookie notice, banner, drawer, or modal covers form controls on mobile.
- The form partial grows a second inline submit system instead of using the
  dedicated `lt-inquiry-form-experience.js` owner.
- The BTFP page forks a separate intake form to solve a copy or scoped-choice
  problem that can be handled through shared form context.

## Receipt

On 2026-05-10 the focused form verifier first failed because the shared form
had no submit-status region and the cookie banner could overlay form pages.
The repair added the status region, dedicated submit-experience JavaScript,
focused form-experience CSS, inline cookie placement for form routes, and a
guard proving direct `#received` URLs do not show fake success. The focused
form verifier, backend smoke submit with cleanup, contact prefill/service logic,
container contract, manual accessibility, and focused interactive contact
checks passed.

On 2026-05-10 GL flagged two regressions from the first UX pass: an empty file
input on the BTFP form could produce an inspiration-photo warning, and the form
chrome/modal copy was too instructional. The repair filters empty upload slots,
suppresses photo warnings unless a real selected file had an issue, removes the
visible progress-step/note copy, and reduces the modal to a short confirmation
with one close action. `npm run test:form-experience`,
`python scripts/verify/inquiry_upload_failure_contract.py`, and a real BTFP
smoke submit passed.


On 2026-05-10 the BTFP route exposed a repeat-email failure from ERPNext's default Lead duplicate-email validation while GL was testing five inspiration photos. The repair enabled duplicate Lead emails through CRM Settings, added a durable patch, and added `scripts/verify/book_form_repeat_email_photos.py` to submit two separate inquiries with the same email and five PNG files each. The verifier passed locally and should remain part of public form closeout when upload or CRM settings change.

On 2026-05-12 GL caught that both public form success modals still used weak
copy and that the Contact form had not initially queued the current customer
confirmation. Root cause was stale Lead-reference idempotency: an older
`Email Queue` row shared the recreated Lead name. The repair scoped both
`Email Queue` and `Communication` idempotency to the current Lead creation time,
added a loud backend failure if queue proof is missing, updated success copy,
requeued the missing Contact confirmation, and passed the focused form/email
guards. Feature handoff:
`../../workstreams/form-email-confirmation-regression-2026-05-12.md`.

Later on 2026-05-12 after DNS cutover, the live forms returned `409` for repeat
same-email inquiries and the owner email path was not proven deeply enough. The
repair made repeat same-email inquiries safe despite ERPNext Email Address
uniqueness, added owner/business notification proof, verified the actual
customer and owner Email Queue bodies/recipients, deployed through Frappe Cloud
release `72a4se4v64` / app hash
`04de8212aa7dbf4895716717865fc6e1029c757b`, and passed live `/contact`, live
BTFP, and strict repeat-email/five-photo form proof with cleanup.

On 2026-05-15 GL reported that a production inquiry photo was not visible to
the business owner. The photo existed as a private Lead File, but the Lead
photo table and owner Email Queue attachment refs were empty. The local repair
keeps customer success gated on the same form/email path while extending photo
proof to private Files, CRM photo rows, customer no-attachment queues, owner
`fid` attachment refs, and cleanup. Feature handoff:
`../../workstreams/inquiry-photo-storage-owner-attachments-2026-05-15.md`.

Later on 2026-05-15, GL reported immediate form spam from a
Nicole/vettedvas-style sales pitch and requested a blocker that would not lose
real customers. The repair added the signed hidden token, invisible honeypot,
and conservative sales-solicitation suppression path. Local gates
`python scripts/verify/inquiry_spam_gate.py --base-url http://localhost:8081`
and
`python scripts/verify/inquiry_sales_solicitation_filter.py --base-url http://localhost:8081`
passed along with the existing form, Lead parity, smoke, repeat-email/photo,
and email policy gates. Feature handoff:
`../../workstreams/inquiry-form-spam-sales-filter-2026-05-15.md`.
