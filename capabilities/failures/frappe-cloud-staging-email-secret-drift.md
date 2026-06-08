---
name: Frappe Cloud staging Email Account secret drift
type: failure
failure_kind: release_gate_gap
schema_version: 0.1
date_discovered: 2026-05-24
last_updated: 2026-05-24
status: guarded
scope: project
owner_context: Locally Twisted Frappe Cloud staging receipt/operator email proof
related_capabilities:
  - ../recipes/frappe-cloud-cloudflare-stripe-launch-gate.md
  - ../recipes/customer-email-delivery-branding-contract.md
related_failures:
  - frappe-cloud-staging-email-scheduler-stale.md
  - frappe-cloud-staging-stripe-secret-drift.md
  - public-form-stale-email-queue-idempotency.md
tags:
  - locally-twisted
  - frappe-cloud
  - staging
  - email
  - smtp
  - encryption-key
  - receipt
  - fail-loud
---

# Failure Recipe: Frappe Cloud Staging Email Account Secret Drift

## Symptom

Checkout payment succeeds on hosted staging and ERPNext creates Email Queue
records, but sending fails because the staging site cannot decrypt the
`Email Account.Locally Twisted.password` password field.

## Trigger Conditions

- A staging site is restored, copied, or rebuilt from another site context.
- Password fields were encrypted with a different site encryption key.
- Checkout payment proof reaches the paid-order cascade.
- Email Queue rows are treated as receipt proof before their send status is
  checked.

## Known Instances

| Date | Project | Surface | Bad outcome | Evidence | Guard state | Status |
|---|---|---|---|---|---|---|
| 2026-05-24 | Locally Twisted | Staging paid-order emails | Receipt/operator Email Queue rows were created, but send attempts failed until the staging Email Account app password was re-entered | `workstreams/ecommerce-audit/staging-checkout-product-flow-2026-05-24.md`; Email Queue `cchsjbegpi`, `cchtiiieuk` | failure recipe added; staged password repaired; both records reached `Sent` | guarded |

## Root Pattern

Payment success, Email Queue creation, SMTP acceptance, and inbox-visible
delivery are separate proof surfaces. A restored Frappe Cloud staging site can
have valid source code and valid checkout records while encrypted provider
passwords fail at send time.

## Detection Signals

- Email Queue records stay `Not Sent` or flip to `Error`.
- If rows stay `Not Sent` with no row-level error and scheduled job timestamps
  are stale, check `frappe-cloud-staging-email-scheduler-stale.md` before
  changing SMTP credentials.
- Desk dev logs mention `Email Account.<name>.password`, decryption failure, or
  site encryption key mismatch.
- Re-entering the password changes the failure from decrypt error to a normal
  send attempt.

## Required Guard

Before saying staging checkout receipts are ready for owner review:

1. complete a hosted staging test-mode checkout;
2. verify Sales Order, Payment Request, and Sales Invoice state;
3. verify the receipt and operator Email Queue records exist;
4. verify their queue status reaches `Sent`;
5. say plainly that `Sent` means SMTP acceptance, not guaranteed inbox
   visibility.

## Recovery Recipe

1. Do not rename this as a checkout, Stripe, or product setup bug after payment
   succeeds.
2. Re-enter the staging Email Account app password, or restore the correct site
   encryption key if staging should keep copied encrypted fields.
3. Retry the affected Email Queue rows only after preserving evidence of
   whether the automatic scheduler path was running.
4. Confirm status changes to `Sent`.
5. If status becomes `Error` again, inspect the current error before changing
   code. Do not print SMTP passwords.

## What Not To Do

- Do not print email passwords or app passwords.
- Do not touch the live Email Account during staging repair.
- Do not treat queued emails as sent emails.
- Do not treat `Sent` as proof that Gmail put the message in the visible inbox.
- Do not send owner-review links while the receipt path is still blocked.

## Cross-Links

- `../../workstreams/ecommerce-audit/staging-checkout-product-flow-2026-05-24.md`
- `../../workstreams/frappe-cloud-staging-owner-review-2026-05-24.md`
- `../../workstreams/payment-backend-launch-readiness.md`
- `../recipes/customer-email-delivery-branding-contract.md`

## Evidence Quality

Sufficient for staging ERPNext/Frappe email-send acceptance on 2026-05-24:
the two test paid-order Email Queue records for `SAL-ORD-2026-00024` reached
`Sent` after the Email Account password was re-entered. Not sufficient for
inbox-visible receipt proof because the connected Gmail MCP account was
`cameronbpaul@gmail.com`, not the recipient `locallytwisted@gmail.com`.
