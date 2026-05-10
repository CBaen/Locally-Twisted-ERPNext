# Form Submission Experience

Last updated: 2026-05-10

## Scope

This handoff owns the customer-facing submit experience for the shared
`inquiry-v1` form used by `/contact` and by
`/balloon-twisting-and-face-painting`.

It does not own product-page architecture, checkout pricing, Lead schema
changes, or customer email policy.

## Current Contract

- The form stays guest-friendly; no login is required.
- Submission is AJAX to
  `locally_twisted.www.book.submit_book_inquiry`.
- The UI may only show success after the backend response includes
  `message.ok`.
- Success stays on the page. Do not restore the old forced 4-second redirect.
- A direct `#received` URL must not show fake success; the modal opens only
  from the verified submit path.
- The success modal explains next steps, gives the urgent call path, and lets
  the customer choose whether to stay or keep browsing.
- Failure copy stays customer-safe and plain. Internal exceptions stay out of
  public copy.
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

## Verification Receipt

Passed on 2026-05-10:

```powershell
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

## Known Non-Blocking Failures

Full `npm run test:interactive-layout` was rerun on 2026-05-10 and still has
unrelated failures in parked product/ecommerce-pause surfaces:

- `/shop-items/garlands` missing expected compact hero contract elements.
- paused ecommerce pages have a small-target issue on the help link.

Those failures predate or sit outside this shared-form UX slice. The form-owned
interactive checks listed above pass.
