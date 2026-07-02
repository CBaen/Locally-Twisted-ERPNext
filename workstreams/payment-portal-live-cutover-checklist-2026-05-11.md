# Payment Portal Live Cutover Checklist - 2026-05-11

## Purpose

Move from the passing local/test payment contracts to a live Locally Twisted payment portal plan without exposing secrets, making live charges, or pretending local Stripe test mode is production readiness.

## Peer Agent Operating Context

Use this checklist for peer GPT 5.5 agents on the exact LT stack: Frappe v15.106.0, ERPNext v15.105.0, Webshop, payments, and the custom `locally_twisted` app installed last. Frappe Cloud deployment is Git-backed/private-bench work: payment behavior must survive deploy through committed app code, hooks, fixtures/patches where appropriate, and explicit `site_config` keys on the target site.

Technical implementation, verifier, and non-production repo-edit decisions route to Leader. Ask the user only for true owner approvals: live Stripe/real charge/refund, DNS cutover, secrets/account access, legal/policy approval, production customer-record mutation, or changing launch/business behavior.

## Current Local Evidence

Known passing local commands from the ecommerce proof pass:

```bash
python scripts/verify/payment_launch_readiness.py
python scripts/verify/payment_backend_config_contract.py
python scripts/verify/payment_webhook_contract.py
python scripts/verify/payment_cascade_contract.py
python scripts/verify/payment_success_reconciliation_contract.py
python scripts/verify/stripe_amount_parity_contract.py
```

Local/test mode is good enough to proceed with launch execution planning. It is not approval for live charges.

## Required Live Site Config Keys

Set these on the staging/live Frappe site without printing values in chat, logs, commits, screenshots, or reports:

- `host_name`
- `lt_stripe_settings_name`
- `lt_payment_gateway_account`
- `lt_stripe_payment_method_configuration`
- `lt_operator_email`
- `stripe_webhook_signing_secret`

Required non-secret expectations:

- `host_name` is the real HTTPS Frappe host, not `http://localhost:8081`
- Stripe Settings resolve to live mode keys
- Payment Gateway Account currency is `USD`
- Webshop checkout is enabled when live checkout is intentionally opened
- operator email is the approved Locally Twisted operator inbox
- public policy routes return 200:
  - `/privacy`
  - `/terms-of-service`
  - `/refund-policy`
  - `/accessibility`

## Live Readiness Gate

Run on staging first:

```bash
python scripts/verify/payment_launch_readiness.py --mode live --base-url <staging-url>
python scripts/verify/payment_backend_config_contract.py
python scripts/verify/payment_webhook_contract.py
python scripts/verify/stripe_amount_parity_contract.py
```

Then after production host cutover, run:

```bash
python scripts/verify/payment_launch_readiness.py --mode live --base-url https://locallytwisted.com
python scripts/verify/cloudflare_launch_readiness.py --base-url https://locallytwisted.com
```

## Stripe Dashboard Checklist

Before one low-risk live payment test:

- Confirm the correct merchant account for Locally Twisted.
- Add the production webhook endpoint:
  - `/api/method/locally_twisted.payments.stripe_webhook.stripe_webhook`
- Store the webhook signing secret only in site config.
- Confirm Privacy Policy URL points to `/privacy`.
- Confirm Terms of Service URL points to `/terms-of-service`.
- Confirm Refund Policy is linked from the checkout/order policy surface.
- Confirm the payment method configuration disables Link if that remains the approved LT choice.
- Confirm live payment descriptor and support contact are appropriate for Locally Twisted.

## One Low-Risk Live Payment Test

Do this only after staging passes and GL/owner approval is explicit:

1. Use an approved low-risk live product/order amount.
2. Create one checkout order through the public customer path.
3. Complete payment with a real card controlled by the owner/tester.
4. Verify ERPNext records:
   - Sales Order exists and matches selected product/configuration.
   - Payment Request is paid.
   - Payment Entry exists.
   - Sales Invoice exists.
   - receipt/customer/operator emails queue or send as expected.
   - Stripe amount equals ERPNext Sales Order grand total.
5. Refund or reconcile according to the owner-approved live-payment test plan.
6. Record the exact Sales Order and Stripe event IDs in the launch packet, not secret values.

## Current Live Blockers

Current `python scripts/verify/payment_launch_readiness.py --mode live` fails because local config still uses:

- test Stripe Settings
- missing explicit live site config keys
- local-only `host_name`

Those are cutover blockers to fix on staging/live. They are not reasons to preserve an ecommerce pause posture.

## Do Not Do

- Do not print Stripe secret keys or webhook signing secrets.
- Do not make a live charge before the live readiness gate passes.
- Do not treat a local/test-mode pass as live payment approval.
- Do not wire CRM stage movement into finance/payment records as part of payment cutover.
- Do not call fixture product records real catalog truth.
