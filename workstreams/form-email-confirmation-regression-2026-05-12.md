# Form Email Confirmation Regression - 2026-05-12

## Scope

This handoff owns the May 12 regression closeout for the shared public inquiry
forms on `/contact` and `/balloon-twisting-and-face-painting`.

It covers customer-visible success copy, customer/company confirmation email
queueing, stale idempotency rows, and the verifiers that keep the submit path
honest. It does not own product-page quote emails, paid receipts, invoice
emails, or finance/legal outbound documents.

## Regression

GL submitted both public forms and saw the modal copy:

- `Request received`
- `Thanks, we got it and will follow up soon.`

The expected copy is:

- `Request received`
- `A confirmation of your request will be sent to your email address shortly. We will be in contact within 24 hours!`

The contact-form submission also did not initially queue a current customer
confirmation email even though the customer saw success.

## Root Cause

`lead_cascade.py` used Lead reference name alone as the idempotency boundary for
public-form acknowledgments. The Contact submission created
`CRM-LEAD-2026-00073` on 2026-05-11, but an older sent Email Queue row from
2026-05-10 already referenced the same Lead name. The old row made the new Lead
look already acknowledged.

The same stale-record class can affect `Communication` rows, so both checks
must be scoped to the current Lead incarnation by `creation >= doc.creation`.

## Current State

- Public form success copy now promises the confirmation email and 24-hour contact window.
- Direct `#received` visits still do not open fake success.
- The backend throws a customer-safe loud failure if the confirmation email does not queue.
- Confirmation idempotency checks ignore stale `Email Queue` and `Communication` rows from an older Lead with the same name.
- The missing Contact confirmation was requeued after the fix.

Live DB evidence from the screenshot submissions:

| Route | Lead | Email Queue | Status | Recipients |
|---|---|---|---|---|
| `/contact` | `CRM-LEAD-2026-00073` | `gbf0g958qj` | Sent | `locallytwisted@gmail.com`, `cameronbpaul@gmail.com` |
| `/balloon-twisting-and-face-painting` | `CRM-LEAD-2026-00074` | `95fi9c31jm` | Sent | `locallytwisted@gmail.com`, `cameronbpaul@gmail.com` |

The older stale Contact queue row `2eghkl7krg` from 2026-05-10 remains history
but no longer suppresses the current Lead's confirmation.

## Owner Files

- `apps/locally_twisted/locally_twisted/lead_cascade.py`
- `apps/locally_twisted/locally_twisted/www/book.py`
- `apps/locally_twisted/locally_twisted/public/js/lt-inquiry-form-experience.js`
- `apps/locally_twisted/locally_twisted/templates/includes/book_form.html`
- `apps/locally_twisted/locally_twisted/hooks.py`
- `scripts/verify/form_experience.spec.js`
- `scripts/verify/book_form_repeat_email_photos.py`
- `scripts/verify/smoke_forms.py`
- `apps/locally_twisted/locally_twisted/verify/customer_email_policy_contract.py`

## Verification Receipt

Passed on 2026-05-12:

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

## Guardrails

- Do not use Lead name alone as proof a public-form confirmation already sent.
- Do not show `message.ok` or the success modal unless the backend has queued
  the customer confirmation or confirmed a current same-Lead queue row exists.
- Do not use `#received`, cookies, localStorage, or static page state to imply
  success.
- Do not let public-form confirmation email failures become console-only logs.
- Do not remove stale historical Email Queue rows as a routine cleanup; scope
  the idempotency query instead.

## Cross-links

- `workstreams/form-submission-experience.md`
- `workstreams/customer-email-policy-boundary.md`
- `capabilities/recipes/shared-inquiry-form-experience.md`
- `capabilities/recipes/customer-email-delivery-branding-contract.md`
- `capabilities/failures/public-form-stale-email-queue-idempotency.md`
