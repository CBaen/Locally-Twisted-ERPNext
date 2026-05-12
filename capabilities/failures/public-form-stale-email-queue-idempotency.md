---
name: Public form stale Email Queue idempotency
type: failure
failure_kind: regression_pattern
schema_version: 0.1
date_discovered: 2026-05-12
last_updated: 2026-05-12
status: guarded
scope: project
owner_context: Locally Twisted ERPNext public inquiry forms
related_capabilities:
  - ../recipes/customer-email-delivery-branding-contract.md
  - ../recipes/shared-inquiry-form-experience.md
tags:
  - locally-twisted
  - public-form
  - email-queue
  - idempotency
  - fail-loud
---

# Failure Recipe: Public Form Stale Email Queue Idempotency

## Symptom

A customer sees a successful public-form submission, but the current Lead does
not queue a new customer confirmation email because an older Email Queue or
Communication row with the same Lead reference name exists.

## Trigger conditions

- A verifier, cleanup helper, import, or local DB operation deletes and
  recreates Leads while Frappe autoname can reuse a prior Lead name.
- Idempotency checks look only at `reference_doctype = Lead` and
  `reference_name = <lead name>`.
- Customer-visible success is allowed before the current submission's email
  queue row is proven.

## Known instances

| Date | Project | Surface | Bad outcome | Evidence | Guard state | Status |
|---|---|---|---|---|---|---|
| 2026-05-12 | Locally Twisted | `/contact` public inquiry | `CRM-LEAD-2026-00073` saw success while an old 2026-05-10 Email Queue row suppressed the 2026-05-11 confirmation | Live DB showed stale `2eghkl7krg` and new requeued `gbf0g958qj`; both final customer/company recipients sent | idempotency scoped to current Lead creation | guarded |

## Root pattern

Record names are not always incarnation identifiers in a mutable local ERPNext
site. A historical row can share the same reference name as a newly created
record. Idempotency checks need a current-record boundary, not only a reference
name boundary.

## Detection signals

- A public form says `Request received` but there is no current Email Queue row
  with `creation >= Lead.creation`.
- Email Queue history contains multiple rows for the same Lead reference across
  different dates.
- A cleanup/verifier path deletes Leads but does not or cannot delete older
  Email Queue or Communication rows.
- The UI success copy promises email while backend code only catches and logs
  confirmation failures.

## Required guard

Public-form confirmation idempotency must scope existing `Email Queue` and
`Communication` rows to the current Lead incarnation. The backend must fail
loudly if `frappe.sendmail` returns without creating a current queue row.

## Recovery recipe

1. Query the Lead's `creation` timestamp.
2. Query `Email Queue` and `Communication` rows for the Lead reference and
   compare their `creation` timestamps against the Lead.
3. If the current Lead has no confirmation queue row, call the public
   confirmation sender for that Lead and verify the resulting queue recipients.
4. Patch the idempotency check rather than deleting historical rows.
5. Run `npm run test:form-experience`,
   `python scripts/verify/customer_email_policy_contract.py`,
   `python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --skip-newsletter`,
   and `python scripts/verify/book_form_repeat_email_photos.py --base-url http://localhost:8081`.

## What not to do

- Do not delete old Email Queue rows as the primary fix.
- Do not claim success because an older same-reference row is `Sent`.
- Do not catch email-queue failures and still return `message.ok`.
- Do not remove direct `#received` fake-success protection while repairing copy.

## Cross-links

- `../../workstreams/form-email-confirmation-regression-2026-05-12.md`
- `../../workstreams/form-submission-experience.md`
- `../../workstreams/customer-email-policy-boundary.md`
- `../recipes/customer-email-delivery-branding-contract.md`
- `../recipes/shared-inquiry-form-experience.md`

## Evidence quality

Verified against live local ERPNext DB rows on 2026-05-12 and guarded by focused
form/email verifiers.
