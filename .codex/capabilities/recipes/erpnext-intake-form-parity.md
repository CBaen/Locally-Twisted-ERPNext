---
name: ERPNext intake form parity
level: recipe
last_verified: 2026-05-08
---

## What it does

Keeps a public inquiry form, ERPNext Lead metadata, submit mapping, and the operator-facing Desk form in agreement.

This recipe owns data and schema parity. If the change is about the customer
submit/status/modal experience, pair it with
`shared-inquiry-form-experience`.

## When to reach for it

Use this when changing a public `/contact` or `/book` style form, Lead Custom Fields, service taxonomy, conditional Desk sections, uploaded photo fields, or any field label that differs between customer copy and employee copy.

Current LT public form contract is `inquiry-v1`. Service routes can scope and
preselect service choices through controller context, but they must not fork a
second customer intake form unless GL explicitly approves a separate form
contract.

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

4. Avoid Frappe `Time` fields for estimated event times.

   Desk renders `Time` fields as low-level time controls that are awkward for quick human entry. For estimates such as event start/end, setup arrival, artist start/end, and delivery windows, prefer `Data` fields with examples like `3 PM`, `3:30 PM`, `afternoon`, or `TBD`.

5. Treat fieldtype changes as migrations.

   Frappe blocks many Custom Field fieldtype changes through normal validation. If changing an existing `Time` field to `Data`, use a guarded idempotent sync that only allows the known safe widening, lets Frappe rebuild the DocType schema, and normalizes old machine-style values.

6. Verify with both backend and browser evidence.

   Backend metadata passing is not enough when the complaint is visual. Open the actual Desk route and confirm the field renders as the intended input type with the intended label.

7. Keep service-page pricing helpers separate from form submission.

   A calculator on a service page can help the customer estimate scope, but it
   is not a Lead schema field or checkout shortcut unless that is deliberately
   approved. For BTFP, the calculator is row-based pricing transparency while
   the shared inquiry form still owns the customer request.

## LT verification commands

```powershell
python scripts/setup/sync_contact_intake_backend.py
python scripts/verify/lead_backend_intake_parity.py
python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --shape-only --skip-newsletter
python scripts/verify/contact_service_logic.py --base-url http://localhost:8081
python scripts/verify/contact_prefill.py --base-url http://localhost:8081
npm run test:form-experience
```

If running the full writing smoke test, delete the generated test Lead/newsletter records afterward.

## Failure modes

- A public form can look right while Desk conditionals still depend on a different Lead field.
- A browser success modal can hide a backend mapping drift.
- A polished form experience can hide a broken submit path unless success is
  gated on the backend's `message.ok` response.
- Employee-facing labels can accidentally inherit customer helper copy and make Desk feel noisy.
- `Time` fields can create slider/time-picker friction for simple estimates.
- Existing `Time` values can turn into machine-style strings with seconds or microseconds after conversion; clean those up so staff do not treat junk timestamps as real event times.
- A service page forks a new customer form because it needs scoped choices,
  when controller context on the shared form would preserve one intake path.
