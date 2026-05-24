---
name: Frappe Cloud staging Stripe secret drift
type: failure
failure_kind: release_gate_gap
schema_version: 0.1
date_discovered: 2026-05-24
last_updated: 2026-05-24
status: open
scope: project
owner_context: Locally Twisted Frappe Cloud staging checkout/payment proof
related_capabilities:
  - ../recipes/frappe-cloud-cloudflare-stripe-launch-gate.md
  - ../recipes/erpnext-checkout-commerce-rules.md
related_failures:
  - frappe-cloud-release-site-migration-drift.md
  - frappe-cloud-app-mirror-release-scope-drift.md
  - frappe-cloud-staging-website-settings-drift.md
tags:
  - locally-twisted
  - frappe-cloud
  - staging
  - stripe
  - encryption-key
  - checkout
  - payment
  - fail-loud
---

# Failure Recipe: Frappe Cloud Staging Stripe Secret Drift

## Symptom

Hosted staging product/cart/checkout route tests pass, but the final payment
handoff fails because the staging site cannot decrypt
`Stripe Settings.Test.secret_key`.

## Trigger Conditions

- A staging site is restored, copied, or rebuilt from another site context.
- Password fields or provider secrets were encrypted with a different site
  encryption key.
- Source/app-mirror checkout fixes are deployed, so the flow reaches the
  provider configuration layer.
- Testing stops at a customer-facing product setup error or generic checkout
  error without checking the exact server-side failure.

## Known Instances

| Date | Project | Surface | Bad outcome | Evidence | Guard state | Status |
|---|---|---|---|---|---|---|
| 2026-05-24 | Locally Twisted | Staging checkout | Configured bouquet checkout reached payment setup, then failed because `Stripe Settings.Test.secret_key` could not be decrypted in staging | `workstreams/ecommerce-audit/staging-checkout-product-flow-2026-05-24.md`; `workstreams/frappe-cloud-staging-owner-review-2026-05-24.md` | failure recipe added; config repair still pending | open |

## Root Pattern

Product setup proof, app deploy proof, and payment-secret proof are separate.
A code fix can correctly repair cart/checkout selection while the final
provider handoff remains blocked by encrypted site configuration.

## Detection Signals

- Checkout preview and order-summary browser tests pass.
- Final submit fails at provider/payment handoff.
- Error logs mention `Stripe Settings.Test.secret_key`, decryption failure, or
  site encryption key mismatch.
- The failure appears after restoring or rebuilding staging.

## Required Guard

Before owner card-path testing on staging:

1. confirm the intended staging Stripe Settings record and mode;
2. confirm the Payment Gateway Account and payment method configuration point
   to the intended staging/test setup;
3. prove the test secret can be read by Frappe without printing it;
4. run the checkout route proof;
5. run backend payment config/webhook/amount parity contracts;
6. perform one authorized Stripe test-mode checkout and verify ERPNext records,
   customer receipt, operator email, tax, and payment status.

## Recovery Recipe

1. Do not rename this as a product setup bug after the product route tests pass.
2. Re-enter the staging test secret key in `Stripe Settings`, or restore the
   correct site encryption key if staging was restored/copied and should keep
   encrypted fields. Frappe Cloud reference:
   `https://docs.frappe.io/cloud/sites/migrate-an-existing-site#encryption-key`.
3. Recheck Payment Gateway Account and payment method configuration.
4. Clear staging website/cache.
5. Rerun staging route proof and payment contracts.
6. Only then run an authorized Stripe test-mode checkout.

## What Not To Do

- Do not expose raw provider/decryption wording to customers.
- Do not touch live payment settings while repairing staging.
- Do not claim staging checkout is owner-ready from product/cart route proof
  alone.
- Do not print secret values in chat, docs, logs, or screenshots.
- Do not skip backend record verification after Stripe returns success.

## Cross-Links

- `../../workstreams/frappe-cloud-staging-owner-review-2026-05-24.md`
- `../../workstreams/ecommerce-audit/staging-checkout-product-flow-2026-05-24.md`
- `../../workstreams/payment-backend-launch-readiness.md`
- `../../LT-LAUNCH-RUNBOOK.md`
- `../recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`

## Evidence Quality

Current evidence is sufficient to classify the blocker as staging payment
configuration drift after source checkout fixes, but not sufficient to say the
payment path is repaired. The failure remains open until a staging payment
configuration repair and one authorized test-mode checkout pass.
