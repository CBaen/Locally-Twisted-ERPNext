---
name: Frappe Cloud staging Email Queue scheduler stale
type: failure
failure_kind: recurring_pattern
schema_version: 0.1
date_discovered: 2026-05-29
last_updated: 2026-05-29
status: open
scope: project
owner_context: Locally Twisted Frappe Cloud staging paid-order receipt/operator email proof
related_capabilities:
  - ../recipes/codex-browser-verification-surface.md
  - ../recipes/customer-email-delivery-branding-contract.md
  - ../recipes/frappe-cloud-cloudflare-stripe-launch-gate.md
related_failures:
  - frappe-cloud-staging-email-secret-drift.md
  - frappe-cloud-staging-stripe-secret-drift.md
tags:
  - locally-twisted
  - frappe-cloud
  - staging
  - scheduler
  - email-queue
  - receipt
  - fail-loud
---

# Failure Recipe: Frappe Cloud Staging Email Queue Scheduler Stale

## Symptom

Hosted staging checkout payment succeeds and ERPNext creates paid-order receipt
and operator Email Queue rows, but the rows remain `Not Sent` with no row-level
error because the automatic scheduler/background queue path is stale.

## Trigger Conditions

- Paid-order emails are queued with `frappe.sendmail(..., now=False)`.
- Frappe's `frappe.email.queue.flush` and `retry_sending_emails` scheduled jobs
  have not run after the checkout.
- Email Queue rows are treated as receipt proof before their status reaches
  `Sent` or an explicit `Error`.
- A connector failure, such as Gmail `token_revoked`, distracts from the
  ERPNext queue evidence.

## Known Instances

| Date | Project | Surface | Bad outcome | Evidence | Guard state | Status |
|---|---|---|---|---|---|---|
| 2026-05-29 | Locally Twisted | Hosted staging paid-order emails | Four paid staging orders created eight receipt/operator Email Queue rows, all `Not Sent`, while scheduler/job timestamps were stale | `.tmp/staging-record-audit-20260529034307.json`; witness packet `C:\Users\baenb\.codex\tmp\witness-state\lt-staging-email-queue-20260529.md`; triad review | failure recipe added; repair still needs staging scheduler recovery and fresh checkout proof | open |

## Root Pattern

Payment success, queue-row creation, scheduler/background processing, SMTP
acceptance, and inbox visibility are separate proof surfaces. When receipt
emails are queued asynchronously, a stale scheduler can leave the customer path
half-complete while the thank-you page still looks successful.

## Detection Signals

- Paid Sales Orders and Payment Requests are complete.
- Receipt/operator Email Queue rows exist for the Sales Order.
- Email Queue status stays `Not Sent` with blank or empty error fields.
- `Scheduled Job Type` or `Scheduled Job Log` timestamps for
  `frappe.email.queue.flush` and `retry_sending_emails` are older than the
  checkout.
- Frappe Cloud documentation says scheduler status can be checked from the RQ
  Job doctype, and Frappe framework schedules `frappe.email.queue.flush` under
  scheduler `all`.

## Required Guard

Before saying hosted staging checkout receipt delivery is ready:

1. Preserve a read-only snapshot of the paid order, Payment Request, Email
   Queue rows, scheduled job timestamps, and current row errors.
2. Verify the automatic scheduler/worker path is current after the affected
   Email Queue rows exist.
3. Confirm affected paid-order Email Queue rows move to `Sent` or to explicit,
   actionable `Error`.
4. Run one fresh staging Stripe test checkout and confirm its receipt/operator
   rows reach `Sent` without a manual flush.
5. Say plainly that `Sent` proves SMTP acceptance only, not inbox-visible Gmail
   delivery.

## Recovery Recipe

1. Do not rename this as a checkout, Stripe, product, or Gmail connector bug
   after payment and queue-row creation are proven.
2. Do not manually flush first. Manual flush can prove SMTP after evidence is
   captured, but it bypasses the customer-path scheduler proof.
3. Repair staging scheduler/workers through the provider/site operations path.
4. Retry or allow normal queue processing for the affected rows.
5. If rows change to `Error`, inspect the current error before changing code or
   secrets. Do not print provider passwords, app passwords, OAuth tokens, or
   SMTP secrets.

## What Not To Do

- Do not switch paid receipts to `now=True` as the first fix; that hides the
  operational scheduler problem and changes checkout behavior.
- Do not treat a Gmail connector `token_revoked` error as proof of receipt
  delivery failure. It blocks connector-based inbox proof only.
- Do not touch live Email Account, live Stripe, DNS, Search Console, or
  production data for a staging scheduler failure.
- Do not tell the owner staging checkout is ready while receipt/operator rows
  are still `Not Sent`.

## Cross-Links

- `../recipes/codex-browser-verification-surface.md`
- `../recipes/customer-email-delivery-branding-contract.md`
- `frappe-cloud-staging-email-secret-drift.md`
- `../../workstreams/ecommerce-audit/staging-checkout-product-flow-2026-05-24.md`

## Evidence Quality

Good enough to classify the 2026-05-29 item-1 blocker as staging scheduler/email
queue processing until contradicted by fresh staging evidence. Not yet proof of
repair. Gmail inbox-visible proof remains blocked when the Gmail connector is
revoked unless an authenticated browser or other approved inbox lane is used.
