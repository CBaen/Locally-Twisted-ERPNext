# Form Submission Experience

Last updated: 2026-05-12 by Codex after the live repeat-email/owner-notification fix.

## Scope

This handoff owns the customer-facing submit experience for the shared
`inquiry-v1` form used by `/contact` and by
`/balloon-twisting-and-face-painting`.

It does not own product-page architecture, checkout pricing, Lead schema
changes, or customer email policy.

Capability router:
`capabilities/recipes/shared-inquiry-form-experience.md`.

## Current Contract

- The form stays guest-friendly; no login is required.
- Submission is AJAX to
  `locally_twisted.www.book.submit_book_inquiry`.
- The UI may only show success after the backend response includes
  `message.ok`.
- Success stays on the page. Do not restore the old forced 4-second redirect.
- A direct `#received` URL must not show fake success; the modal opens only
  from the verified submit path.
- The success modal is intentionally quiet: `Request received`, the
  confirmation-email/24-hour response promise, and one close button.
- Backend success requires customer confirmation and owner/business
  notification email-queue proof. If either queue path fails, the endpoint must
  fail loudly with customer-safe copy instead of returning `message.ok`.
- Repeat same-email inquiries are allowed. A returning customer's second event
  inquiry must not become a duplicate-email `409`.
- Failure copy stays customer-safe and plain. Internal exceptions stay out of
  public copy.
- Empty file inputs must not become photo warnings. Only a real selected file
  can produce an upload issue message.
- The first-visit cookie notice renders inline after form surfaces instead of
  covering fields or submit controls.

## Files

- `apps/locally_twisted/locally_twisted/templates/includes/book_form.html`
  owns the shared markup, status-region hooks, and modal markup.
- `apps/locally_twisted/locally_twisted/public/js/lt-inquiry-form-experience.js`
  owns submit validation, progress states, AJAX submit, success modal behavior,
  and customer-safe failure display.
- `apps/locally_twisted/locally_twisted/public/css/lt-form-experience.css`
  owns the status panel, loading button, modal action layout, and reduced-motion
  handling.
- `apps/locally_twisted/locally_twisted/public/js/lt-site-preferences.js`
  owns cookie notice placement.
- `scripts/verify/form_experience.spec.js` is the focused verifier for this
  contract.
- `capabilities/recipes/shared-inquiry-form-experience.md` is the
  reusable recipe for future agents changing submit/status/modal behavior.

## Verification Receipt

Passed on 2026-05-10:

```bash
node --check apps/locally_twisted/locally_twisted/public/js/lt-inquiry-form-experience.js
node --check apps/locally_twisted/locally_twisted/public/js/lt-site-preferences.js
python -m py_compile apps/locally_twisted/locally_twisted/hooks.py
python scripts/dev/clear_website_cache.py --restart
npm run test:form-experience
python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --skip-newsletter
python scripts/verify/contact_prefill.py --base-url http://localhost:8081
python scripts/verify/contact_service_logic.py --base-url http://localhost:8081
npm run test:container-contract
npm run test:a11y-manual
npx playwright test scripts/verify/interactive_layout.spec.js -g "contact expanded conditionals" --reporter=line --workers=1
npx playwright test scripts/verify/interactive_layout.spec.js -g "homepage serves the current site-preferences cache buster" --reporter=line --workers=1
```

The real smoke test created marker `SMOKE-TEST-1778380640428736700`, verified
the backend record, and cleaned up the fake Lead plus linked smoke Tasks.

Commit receipt: `399932d Improve shared inquiry form experience`.

Follow-up pass on 2026-05-10 removed the over-explaining submit chrome and
quieted the modal. It also fixed the false photo-warning path where an empty
browser upload slot counted as a failed photo. Verification:

```bash
node --check apps/locally_twisted/locally_twisted/public/js/lt-inquiry-form-experience.js
python -m py_compile apps/locally_twisted/locally_twisted/www/book.py apps/locally_twisted/locally_twisted/verify/inquiry_upload_failure_contract.py
python scripts/dev/clear_website_cache.py --restart
npm run test:form-experience
python scripts/verify/inquiry_upload_failure_contract.py
python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --form-path /balloon-twisting-and-face-painting --skip-newsletter
```

Follow-up regression closeout on 2026-05-12 fixed the success-copy and
confirmation-email trust boundary. The Contact form had reused a Lead name, and
an old Email Queue row suppressed the current confirmation. Idempotency now
scopes existing `Email Queue` and `Communication` rows to the current Lead
creation time, and the UI copy promises a confirmation email plus 24-hour
contact window. Verification:

```bash
node --check apps/locally_twisted/locally_twisted/public/js/lt-inquiry-form-experience.js
node --check scripts/verify/form_experience.spec.js
python -m py_compile apps/locally_twisted/locally_twisted/lead_cascade.py apps/locally_twisted/locally_twisted/www/book.py
python scripts/dev/clear_website_cache.py
npm run test:form-experience
python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --skip-newsletter
python scripts/verify/book_form_repeat_email_photos.py --base-url http://localhost:8081
```

Live cutover closeout later on 2026-05-12 fixed the repeat same-email `409`,
added owner/business notification proof, and required actual customer/owner
Email Queue body/recipient verification. Live proof:

```bash
export LT_BACKEND_BASE_URL='https://locallytwisted.v.frappe.cloud'
export LT_BACKEND_CDP_URL='http://127.0.0.1:9222'
python scripts/verify/book_form_repeat_email_photos.py --base-url https://locallytwisted.com --admin-base-url https://locallytwisted.v.frappe.cloud --cdp-url http://127.0.0.1:9222
python scripts/verify/smoke_forms.py --base-url https://locallytwisted.com --form-path /contact --skip-newsletter
python scripts/verify/smoke_forms.py --base-url https://locallytwisted.com --form-path /balloon-twisting-and-face-painting --skip-newsletter
```

Feature handoff:
`workstreams/form-email-confirmation-regression-2026-05-12.md`.
Failure Recipe:
`capabilities/failures/public-form-stale-email-queue-idempotency.md` and
`capabilities/failures/public-form-repeat-email-lead-conflict.md`.

## Known Non-Blocking Failures

None currently carried for this slice. A later 2026-05-10 open-ecommerce
public verification passed through the broad layout/interactive gates and the
form-owned checks listed above still own this shared-form UX contract.
