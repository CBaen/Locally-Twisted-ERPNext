---
name: Public form repeat email Lead conflict
type: failure
failure_kind: regression_pattern
schema_version: 0.1
date_discovered: 2026-05-12
last_updated: 2026-05-12
status: guarded
scope: project
owner_context: Locally Twisted ERPNext public inquiry forms
related_capabilities:
  - ../recipes/shared-inquiry-form-experience.md
  - ../recipes/customer-email-delivery-branding-contract.md
  - ../recipes/erpnext-intake-form-parity.md
related_failures:
  - public-form-stale-email-queue-idempotency.md
tags:
  - locally-twisted
  - public-form
  - lead
  - repeat-email
  - frappe-cloud
  - fail-loud
---

# Failure Recipe: Public Form Repeat Email Lead Conflict

## Symptom

The public form returns the customer-safe snag copy and the browser console
shows a `409` from
`api/method/locally_twisted.www.book.submit_book_inquiry` when a customer uses
the same email for another inquiry.

## Trigger Conditions

- The public inquiry path creates a new Lead for each event/opportunity.
- ERPNext tries to link the same email through the unique Email Address path.
- The business treats repeat same-email inquiries as legitimate separate
  opportunities.

## Known Instances

| Date | Project | Surface | Bad outcome | Evidence | Guard state | Status |
|---|---|---|---|---|---|---|
| 2026-05-12 | Locally Twisted | Live `/contact` and `/balloon-twisting-and-face-painting` after cutover | Public forms showed snag copy; customer and business notifications did not complete | Browser console showed `submit_book_inquiry` `409`; strict verifier reproduced repeat same-email path | retry without duplicate Email Address link, preserve submitted email, verify customer+owner messages | guarded |

## Root Pattern

ERPNext's linked Email Address uniqueness is not the business rule for event
inquiries. A repeat email can be a new event. The Lead insert path has to
preserve the submitted email for operator/customer communication without
forcing a duplicate Email Address link.

## Required Guard

When the unique Email Address link blocks a fresh public Lead, retry the insert
without `email_id`, preserve the submitted customer email in a controlled
internal fallback on the Lead, and strip the fallback marker from rendered
customer/owner emails.

## Recovery Recipe

1. Reproduce with two public submissions using the same email address.
2. Confirm whether the failure is the Email Address uniqueness path rather than
   validation, rate limit, upload, or permissions.
3. Retry Lead insert without `email_id` only for the known repeat-email
   conflict.
4. Preserve the submitted email in a controlled internal marker so operator
   review and outgoing email rendering still have the real address.
5. Strip the internal marker from customer and owner email bodies.
6. Run the repeat-email/five-photo verifier and inspect both customer and
   business Email Queue bodies/recipients.

## What Not To Do

- Do not reject repeat same-email inquiries as duplicates.
- Do not silently drop the customer's submitted email.
- Do not expose internal fallback markers in public or owner emails.
- Do not solve this by merging separate event inquiries into one Lead.
- Do not claim the fix from a one-submission smoke test.

## Cross-links

- `../../workstreams/form-email-confirmation-regression-2026-05-12.md`
- `../recipes/shared-inquiry-form-experience.md`
- `../recipes/customer-email-delivery-branding-contract.md`
- `../recipes/erpnext-intake-form-parity.md`
- `public-form-stale-email-queue-idempotency.md`

## Evidence Quality

Verified against live Frappe Cloud on 2026-05-12 with two repeat same-email
public submissions, five files per submission, customer and business Email Queue
body/recipient checks, and verifier-owned record cleanup.
