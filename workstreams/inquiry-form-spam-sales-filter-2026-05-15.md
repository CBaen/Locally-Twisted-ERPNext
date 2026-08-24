# Inquiry Form Spam And Sales Filter - 2026-05-15

## Purpose

This is the handoff for the current `inquiry-v1` public form hardening slice.
It covers the customer-visible form layout, the backend anti-bot gate, and the
soft sales-solicitation filter. It does not cover ecommerce product setup,
marketing-review access, catalog_data catalog edits, or checkout.

Parent form handoff: [contact-form-ux-readiness-2026-05-14.md](contact-form-ux-readiness-2026-05-14.md)

Related capabilities:

- [shared-inquiry-form-experience](../capabilities/recipes/shared-inquiry-form-experience.md)
- [erpnext-intake-form-parity](../capabilities/recipes/erpnext-intake-form-parity.md)
- [frappe-public-storefront-security](../capabilities/recipes/frappe-public-storefront-security.md)
- [customer-email-delivery-branding-contract](../capabilities/recipes/customer-email-delivery-branding-contract.md)

## Current Contract

- `/contact` owns the public inquiry form. `/book` remains the legacy redirect
  path into `/contact?intent=quick`.
- The shared form partial is still `inquiry-v1`; BTFP embeds the same contract
  with scoped service choices instead of forking a second form.
- Contact Details appear first. On desktop, preferred contact method sits beside
  name and email starts the next row; on mobile, preferred contact method sits
  directly under name.
- Preferred-contact helper copy is removed.
- Event Basics follows Contact Details and uses the alternate section
  background `#F6F7F8`.
- `What are you celebrating?` is optional in both frontend validation and
  backend submit handling.
- Timing and Scale uses title case and does not label optional fields as
  optional. Event start and end time fields show `Even Estimates Help`.
- The form renders a signed hidden `lt_form_token` and an invisible `website`
  honeypot.
- Backend submit rejects missing, malformed, too-fast, stale, or honeypot-filled
  posts before Lead creation, customer confirmation, owner notification, or
  file handling.
- The sales-solicitation classifier is conservative. It suppresses the owner
  "New website inquiry" email only for high-confidence vendor/sales pitches,
  records a Lead comment for audit, and still saves the Lead plus normal
  customer-safe confirmation so potential customers are not lost.
- Real customer/event language such as corporate events, marketing events,
  balloons, decor, face painting, dates, guests, locations, and services must
  keep the owner notification path open.

## Source Files

- `apps/locally_twisted/locally_twisted/templates/includes/book_form.html`
- `apps/locally_twisted/locally_twisted/public/js/lt-inquiry-form-experience.js`
- `apps/locally_twisted/locally_twisted/www/book.py`
- `apps/locally_twisted/locally_twisted/www/contact.py`
- `apps/locally_twisted/locally_twisted/www/balloon_twisting_and_face_painting.py`
- `apps/locally_twisted/locally_twisted/inquiry_sales_filter.py`
- `apps/locally_twisted/locally_twisted/verify/inquiry_upload_failure_contract.py`
- `scripts/verify/form_experience.spec.js`
- `scripts/verify/contact_service_logic.py`
- `scripts/verify/lead_backend_intake_parity.py`
- `scripts/verify/smoke_forms.py`
- `scripts/verify/book_form_repeat_email_photos.py`
- `scripts/verify/inquiry_spam_gate.py`
- `scripts/verify/inquiry_sales_solicitation_filter.py`

## Verified Locally

Run against local ERPNext at `http://localhost:8081` on 2026-05-15:

```bash
python scripts/verify/inquiry_sales_solicitation_filter.py --base-url http://localhost:8081
python scripts/verify/inquiry_spam_gate.py --base-url http://localhost:8081
npm run test:form-experience
python scripts/verify/lead_backend_intake_parity.py
python scripts/verify/contact_service_logic.py --base-url http://localhost:8081
python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --form-path /contact --skip-newsletter
python scripts/verify/book_form_repeat_email_photos.py --base-url http://localhost:8081
python scripts/verify/customer_email_policy_contract.py
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.verify.inquiry_upload_failure_contract.run
```

All listed gates passed. The Docker/Frappe command emitted existing cssutils
warnings for unrelated CSS values but returned `ok: true`.

## Live Status

The source for this slice is now live as part of the 2026-05-16 Frappe Cloud
site update:

| Field | Value |
|---|---|
| Full repo source commit | `631f9a8 Run contact intake schema sync on install` |
| Frappe app mirror commit | `b4b3bf8 Run contact intake schema sync on install` |
| Frappe Cloud site update | `b48j584nua`, `Success` |
| Frappe Cloud update job | `b48oge6unq`, `Success` |
| Live route proof | `/`, `/#login`, `/contact`, `/login` returned HTTP 200 on expected public surfaces |
| Live smoke proof | `smoke test from cameron` created Lead `CRM-LEAD-2026-00013` and sent customer/owner queues |

The 2026-05-16 live smoke proved the customer happy path, Lead creation, photo
storage, and owner/customer email paths after deploy. It did not specifically
exercise the sales-suppression branch or bot rejection fixtures on live.

Use these gates after any future form-security, spam-filter, token, honeypot,
submit, email, or file-handling change:

```bash
python scripts/verify/inquiry_spam_gate.py --base-url https://locallytwisted.com
python scripts/verify/inquiry_sales_solicitation_filter.py --base-url https://locallytwisted.com
python scripts/verify/smoke_forms.py --base-url https://locallytwisted.com --form-path /contact --skip-newsletter
python scripts/verify/book_form_repeat_email_photos.py --base-url https://locallytwisted.com --admin-base-url https://locallytwisted.v.frappe.cloud --cdp-url http://127.0.0.1:9222
```

Use `LT_BACKEND_BASE_URL` / `LT_BACKEND_CDP_URL` as needed for authenticated
backend proof. The spam/sales classifier should be considered live code, but
future changes still require the dedicated live fixture gates before claiming a
new production-hardening release.

## Investigation Notes

- The pasted Nicole/vettedvas owner email matches LT ERPNext owner-notification
  copy, but the local DB did not contain a Nicole/vettedvas Lead, Communication,
  or Email Queue row. Local `CRM-LEAD-2026-00011` was an older smoke-test Lead,
  not Nicole.
- Treat pasted owner emails as environment evidence, not local database proof.
  Verify the exact environment that generated the email before blaming local
  form behavior.
- Do not inspect personal email or unrelated mailboxes while investigating LT
  ERPNext form delivery. The source of truth is ERPNext/Frappe records, the
  public form, Email Queue, Communication rows, and live/staging/local route
  proof.

## Not Owned In This Slice

The following dirty worktree areas were intentionally left out of this handoff:

- catalog_data live catalog/resource JSON changes.
- Product blueprint/runtime/product setup code.
- Marketing review access code, role sync, and `/marketing-review`.
- Backend simplification/user-access audit docs.
- Ecommerce checkout/product-page runtime changes.
