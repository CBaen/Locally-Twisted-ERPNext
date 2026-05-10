---
id: shared-inquiry-form-experience
name: Shared Inquiry Form Experience
schema_version: 2.1
profile: governed
level: recipe
maturity: candidate
scope: Locally Twisted shared inquiry-v1 public form experience on /contact and service-page embeds
currently_true: yes
verification_level: 2
last_verified: 2026-05-10
evidence_quality: direct
successful_uses: 3
failed_uses: 2
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
- Repeat inquiries from the same email are allowed when the business treats each Lead as a separate event/opportunity.
- The visible success state is caused only by the verified submit path.
- A route hash such as `/contact#received` must not open a success modal by
  itself.
- The submit flow may show progress while sending, but it must not imply final
  success until the backend response includes `message.ok`.
- Customer-facing failure copy stays calm, plain, and non-technical. Internal
  exception text stays out of public UI.
- Success stays on-page with quiet confirmation. Do not restore the forced
  4-second redirect away from the form, a next-step lecture, or a browse-away
  link.
- The modal must be accessible enough for normal keyboard and screen-reader
  use: labelled dialog, short described message, close action, and no hidden
  fake success route.
- Up to five real inspiration-photo uploads must attach successfully on the backend when selected.
- Empty upload slots from the browser are not submitted photos. Do not surface
  an inspiration-photo warning unless a real selected file failed validation or
  attachment.
- Cookie or preference notices on form pages must not overlay required fields,
  submit buttons, or validation copy. On current LT form routes, the notice
  renders inline after the form grid.

## Source Files

- `apps/locally_twisted/locally_twisted/templates/includes/book_form.html`
- `apps/locally_twisted/locally_twisted/public/js/lt-inquiry-form-experience.js`
- `apps/locally_twisted/locally_twisted/public/css/lt-form-experience.css`
- `apps/locally_twisted/locally_twisted/public/js/lt-site-preferences.js`
- `scripts/verify/form_experience.spec.js`
- `workstreams/form-submission-experience.md`

## Verification

Focused form experience:

```powershell
npm run test:form-experience
```

Backend submit and cleanup:

```powershell
python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --skip-newsletter
python scripts/verify/book_form_repeat_email_photos.py --base-url http://localhost:8081
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
- A customer sees "sent" or "received" copy while the AJAX request failed,
  returned a non-OK response, or returned a response without `message.ok`.
- A customer sees an inspiration-photo warning when no file was selected.
- A repeat customer email is rejected as a duplicate Lead.
- The UI claims "Up to 5 images" but the endpoint only proves one/no uploaded file path.
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
