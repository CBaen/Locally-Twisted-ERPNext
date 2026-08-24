---
name: ERPNext intake form parity
level: recipe
last_verified: 2026-05-16
---

## What it does

Keeps a public inquiry form, ERPNext Lead metadata, submit mapping, and the operator-facing Desk form in agreement.

This recipe owns data and schema parity. If the change is about the customer
submit/status/modal experience, pair it with
`shared-inquiry-form-experience`.

## When to reach for it

Use this when changing a public `/contact` or `/book` style form, Lead Custom
Fields, required/optional field state, service taxonomy, conditional Desk
sections, uploaded photo fields, or any field label that differs between
customer copy and employee copy.

Current LT public form contract is `inquiry-v1`. Service routes can scope and
preselect service choices through controller context, but they must not fork a
second customer intake form unless GL explicitly approves a separate form
contract.

On Frappe Cloud, the source app must own the intake schema. Local database
customizations are not enough: a fresh cloud site needs the Lead Custom Fields,
`LT Service Type`, `LT Lead Service Type`, and `LT Lead Photo` created by
source-controlled sync/patch code before public forms can write safely.

## How to use it

Mantra: if it can fail, it must fail loudly. A public form must not show a
success state unless the backend mapping it promises is actually reachable. If
the public fields, submit handler, Lead fields, Desk conditionals, or
acknowledgment path drift, the verifier should fail instead of leaving a
customer-facing success message over broken intake.

1. Start with the public form contract.

   Record the customer-facing labels, field names, and which fields are conditional. Customer helper copy belongs here, not automatically in ERPNext Desk labels.

2. Check the Lead metadata that drives Desk behavior.

   Verify the actual `Custom Field` records for `dt="Lead"`: `fieldname`, `label`, `fieldtype`, `depends_on`, `options`, and `description`.

3. Check the submit handler mapping.

   Confirm the form handler writes to the same field that Desk conditionals read. For LT, selected services must populate `custom_event_type` child rows, not only a text echo.

4. Keep required fields intentionally small.

   Contact identity and enough follow-up detail matter more than forcing every
   event attribute up front. On the current public form, `What are you
   celebrating?` is optional and must not be re-required in the browser,
   backend submit path, or smoke verifier without a new explicit decision.

5. Avoid Frappe `Time` fields for estimated event times.

   Desk renders `Time` fields as low-level time controls that are awkward for quick human entry. For estimates such as event start/end, setup arrival, artist start/end, and delivery windows, prefer `Data` fields with examples like `3 PM`, `3:30 PM`, `afternoon`, or `TBD`.

6. Treat fieldtype changes as migrations.

   Frappe blocks many Custom Field fieldtype changes through normal validation. If changing an existing `Time` field to `Data`, use a guarded idempotent sync that only allows the known safe widening, lets Frappe rebuild the DocType schema, and normalizes old machine-style values.

7. Verify with both backend and browser evidence.

   Backend metadata passing is not enough when the complaint is visual. Open the actual Desk route and confirm the field renders as the intended input type with the intended label.

8. Treat photo uploads as three connected backend contracts.

   A private `File` attached to the Lead is not the same as CRM photo storage.
   For LT inquiry photos, successful uploads must create private Lead Files and
   matching `custom_inspiration_photos` rows. Owner notification attachment
   refs are covered by
   `capabilities/failures/public-form-photo-storage-owner-attachment-gap.md`
   and `workstreams/inquiry-photo-storage-owner-attachments-2026-05-15.md`.

9. Keep service-page pricing helpers separate from form submission.

   A calculator on a service page can help the customer estimate scope, but it
   is not a Lead schema field or checkout shortcut unless that is deliberately
   approved. For BTFP, the calculator is row-based pricing transparency while
   the shared inquiry form still owns the customer request.

10. Guard optional legacy fields.

   Migration helpers may need to rewrite older data such as `Lead.custom_services`,
   but Frappe Cloud sites that never had that legacy field must skip the query
   entirely. Check `frappe.get_meta("Lead").has_field(...)` before selecting or
   rewriting optional columns.

11. Keep anti-bot fields out of Desk schema.

    `lt_form_token` and `website` are public submit guards, not Lead metadata.
    They must block bad requests before Lead creation and must not become
    operator-facing fields or customer-submitted details in email bodies.

## LT verification commands

```bash
python scripts/setup/sync_contact_intake_backend.py
python scripts/verify/lead_backend_intake_parity.py
python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --shape-only --skip-newsletter
python scripts/verify/contact_service_logic.py --base-url http://localhost:8081
python scripts/verify/contact_prefill.py --base-url http://localhost:8081
python scripts/verify/inquiry_spam_gate.py --base-url http://localhost:8081
python scripts/verify/inquiry_sales_solicitation_filter.py --base-url http://localhost:8081
python scripts/verify/book_form_repeat_email_photos.py --base-url http://localhost:8081
npm run test:form-experience
```

For Frappe Cloud/live schema proof, include the site update/migrate job and a
live writing smoke:

```bash
export LT_BACKEND_BASE_URL='https://locallytwisted.v.frappe.cloud'
export LT_BACKEND_CDP_URL='http://127.0.0.1:9222'
python scripts/verify/smoke_forms.py --base-url https://locallytwisted.com --form-path /contact --skip-newsletter
python scripts/verify/smoke_forms.py --base-url https://locallytwisted.com --form-path /balloon-twisting-and-face-painting --skip-newsletter
python scripts/verify/book_form_repeat_email_photos.py --base-url https://locallytwisted.com --admin-base-url https://locallytwisted.v.frappe.cloud --cdp-url http://127.0.0.1:9222
```

If running the full writing smoke test, delete the generated test Lead/newsletter records afterward.

2026-05-16 live release receipt: site update `b48j584nua` / update job
`b48oge6unq` succeeded for full repo `631f9a8` and app mirror `b4b3bf8`; real
smoke Lead `CRM-LEAD-2026-00013` proved five private Files, five
`custom_inspiration_photos` rows, owner Email Queue `683s86r04b` with five
attachment refs, and customer Email Queue `683suhfaa9` with zero photo
attachments.

## Failure modes

- A public form can look right while Desk conditionals still depend on a different Lead field.
- A browser success modal can hide a backend mapping drift.
- A polished form experience can hide a broken submit path unless success is
  gated on the backend's `message.ok` response.
- Employee-facing labels can accidentally inherit customer helper copy and make Desk feel noisy.
- A field marked optional in the UI can still be required by backend submit or
  smoke fixtures.
- Bot-token/honeypot fields can accidentally leak into Lead fields, customer
  confirmation bodies, or owner customer-submitted detail sections.
- `Time` fields can create slider/time-picker friction for simple estimates.
- Existing `Time` values can turn into machine-style strings with seconds or microseconds after conversion; clean those up so staff do not treat junk timestamps as real event times.
- A service page forks a new customer form because it needs scoped choices,
  when controller context on the shared form would preserve one intake path.
- A Frappe Cloud release succeeds at bench deploy but fails site update because
  schema only existed in the local database.
- A migration queries an optional legacy field before verifying that the field
  exists on the current site's Lead DocType.
- Uploaded private Files exist, but the Lead's `custom_inspiration_photos`
  child table is empty, so the CRM backend does not show the photos where staff
  expect them.
