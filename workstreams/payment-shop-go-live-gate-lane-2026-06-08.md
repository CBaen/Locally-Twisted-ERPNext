# Payment Shop Go-Live Gate Lane - 2026-06-08

Status: documentation gate only. Live shop/payment remains NO-GO until the
approval and verification gates below pass.

## Scope

This lane documents the go-live gate for LT ecommerce, cart, checkout, Stripe
payment, paid-order receipts, and live customer exposure.

This file does not approve staging mutation, live mutation, provider changes,
DNS, Stripe, Search Console, ad accounts, customer data access, or secret
handling. It is a one-file documentation lane.

## Current Resting State

- Public pages and inquiry forms are live at `https://locallytwisted.com`.
- Live checkout is not approved.
- Ecommerce should rest behind the customer-exposure lock:
  `lt_ecommerce_paused=1`.
- `/shop`, `/cart`, and `/checkout` must not be treated as open live commerce
  until the live gate passes.
- A passing local or staging verifier is not live readiness.
- A Frappe Cloud app deploy hash is not release proof until site update/migrate,
  cache behavior, and the affected route/API/payment verifiers pass.

Safe plain-language status:

> The public site can stay live while shop checkout remains paused. Local and
> staging payment paths have evidence, but live checkout still needs account,
> config, policy, webhook, email, approval, and real low-risk payment proof.

## Local Proof Already Present

Repo docs currently record these local/backend facts in
`workstreams/payment-backend-launch-readiness.md`:

- `payment_backend_config_contract.py` passes against the local ERPNext site.
- `payment_webhook_contract.py` passes against mocked Stripe webhook events.
- `payment_cascade_contract.py` passes and rolls back generated ERPNext
  records.
- `cart_checkout_contract.py` passes for purchasable variants, single-SKU
  items, and shop card behavior.
- `payment_launch_readiness.py` passes in local mode.
- `payment_launch_readiness.py --mode live` fails as expected when the site is
  still configured for local Stripe test mode and localhost.

Repo docs also record staging evidence:

- On 2026-05-24, hosted staging checkout route proof passed.
- One staging Stripe test-mode checkout completed into paid ERPNext records:
  Sales Order `SAL-ORD-2026-00024`, Payment Request
  `ACC-PRQ-2026-00021` `Paid`, Sales Invoice `ACC-SINV-2026-00004` `Paid`,
  tax `$2.61`, grand total `$37.61`.
- Staging receipt/operator Email Queue rows `cchsjbegpi` and `cchtiiieuk`
  reached `Sent` after provider secret repair. `Sent` means SMTP acceptance,
  not inbox-visible delivery.
- On 2026-05-25, delivery-only staging proof passed `npm run
  test:checkout-experience` `4/4` against
  `https://locallytwisted-staging.frappe.cloud`.

These proofs do not approve live checkout or live Stripe.

## Live Blockers From Repo Docs And Scripts

Live shop/payment remains blocked by the following documented items:

- `lt_ecommerce_paused=1` is a live/customer-exposure safety lock, not an
  implementation blocker. Opening it requires a separate approved live gate.
- Live Stripe checkout is blocked until live Stripe config, correct merchant
  account ownership, product scope, policy URLs, webhook, and one real
  low-risk payment test pass.
- `payment_launch_readiness.py --mode live --base-url
  https://locallytwisted.com` must pass in the intended live site context. The
  host script currently executes `bench` against local Docker, so do not call a
  host-run result live proof unless the bench target is explicitly the live
  site or the check is run through an approved Frappe Cloud live execution
  path.
- Production site config must explicitly own `host_name`,
  `lt_stripe_settings_name`, `lt_payment_gateway_account`,
  `lt_stripe_payment_method_configuration`, `lt_operator_email`, and
  `stripe_webhook_signing_secret`.
- Stripe webhook endpoint must be configured as:
  `https://locallytwisted.com/api/method/locally_twisted.payments.stripe_webhook.stripe_webhook`.
- Policy routes `/privacy`, `/terms-of-service`, `/refund-policy`, and
  `/accessibility` must return HTTP 200 before live payment.
- Paid checkout receipt/operator email proof must distinguish Email Queue row
  creation, scheduler processing, SMTP `Sent`, and inbox-visible delivery.
- Staging failure recipes remain active guards:
  `frappe-cloud-staging-stripe-secret-drift`,
  `frappe-cloud-staging-email-secret-drift`, and
  `frappe-cloud-staging-email-scheduler-stale`.
- Any future live release must compare the previous live app hash to the target
  app mirror commit. Dirty-worktree status or `git show HEAD` is not release
  scope proof.
- Search Console/reindex work is separate and remains blocked until live
  sitemap/canonical output uses `https://locallytwisted.com`. It must not be
  bundled with live payment go-live unless explicitly approved.

## Verification Commands

Run from repo root:

```bash
Set-Location -LiteralPath '/home/guidingl/projects/Built_by_Cameron/_CLIENTS/locally-twisted'
```

### Local Readiness

Use local commands for local proof only:

```bash
git diff --check
python scripts/verify/ecommerce_expected_mode.py --expect paused
python scripts/verify/ecommerce_pause_contract.py
python scripts/verify/commerce_rules_contract.py
python scripts/verify/cart_checkout_contract.py
python scripts/verify/checkout_fulfillment_contract.py
python scripts/verify/checkout_lead_conversion_contract.py
python scripts/verify/payment_backend_config_contract.py
python scripts/verify/payment_webhook_contract.py
python scripts/verify/payment_cascade_contract.py
python scripts/verify/stripe_amount_parity_contract.py
python scripts/verify/payment_launch_readiness.py
npm run test:checkout-experience
npm run test:ecommerce-full
python scripts/verify/business_automation_index.py
python scripts/verify/synthetic_business_pipeline.py
```

If a local test intentionally opens ecommerce mode, restore the resting state
and prove it before closeout:

```bash
python scripts/verify/ecommerce_expected_mode.py --expect paused
python scripts/verify/ecommerce_pause_contract.py
```

### Staging Readiness

These commands prove hosted staging route/UI/assets only unless the staging
backend/provider evidence is also captured.

```bash
$env:LT_BASE_URL='https://locallytwisted-staging.frappe.cloud'
npm run test:checkout-experience
npm run test:product-gallery-experience
npm run test:search-contract
python scripts/verify/public_asset_integrity.py --base-url https://locallytwisted-staging.frappe.cloud
```

Staging payment readiness additionally needs approved provider/session work and
Desk/backend evidence:

- Confirm intended Stripe test mode settings without printing secrets.
- Confirm Payment Gateway Account and Stripe Payment Method Configuration.
- Prove the staging test secret can be read by Frappe without printing it.
- Complete one authorized Stripe test-mode checkout.
- Verify Sales Order, Payment Request, Sales Invoice, tax, grand total, and
  payment status.
- Verify receipt and operator Email Queue rows exist and reach `Sent`.
- Confirm whether inbox-visible delivery is required for owner approval.

After any staging provider/settings repair, rerun:

```bash
$env:LT_BASE_URL='https://locallytwisted-staging.frappe.cloud'
npm run test:checkout-experience
python scripts/verify/payment_backend_config_contract.py
python scripts/verify/payment_webhook_contract.py
python scripts/verify/stripe_amount_parity_contract.py
```

The three Python payment commands above are local-Docker wrappers in this repo
unless run inside an approved staging execution path. Do not label them staging
config proof from a host run alone.

### Live Readiness

Do not run live/provider/payment checks without explicit approval for this
stage.

```bash
python scripts/verify/frappe_cloud_preflight.py
python scripts/verify/cloudflare_launch_readiness_contract.py
python scripts/verify/cloudflare_launch_readiness.py --base-url https://locallytwisted.com
$env:LT_BASE_URL='https://locallytwisted.com'; npm run test:seo-contract
python scripts/verify/ecommerce_pause_contract.py
python scripts/verify/payment_launch_readiness.py --mode live --base-url https://locallytwisted.com
python scripts/verify/business_automation_index.py
python scripts/verify/synthetic_business_pipeline.py
python scripts/verify/payment_backend_config_contract.py
python scripts/verify/payment_webhook_contract.py
python scripts/verify/stripe_amount_parity_contract.py
```

Live form proof, if bundled into the same release review after approval:

```bash
$env:LT_BACKEND_BASE_URL='https://locallytwisted.v.frappe.cloud'
$env:LT_BACKEND_CDP_URL='http://127.0.0.1:9222'
python scripts/verify/smoke_forms.py --base-url https://locallytwisted.com --form-path /contact --skip-newsletter
python scripts/verify/smoke_forms.py --base-url https://locallytwisted.com --form-path /balloon-twisting-and-face-painting --skip-newsletter
python scripts/verify/book_form_repeat_email_photos.py --base-url https://locallytwisted.com --admin-base-url https://locallytwisted.v.frappe.cloud --cdp-url http://127.0.0.1:9222
```

Again: host-run payment backend scripts are local-Docker proof unless the bench
target is changed or the check is run in the intended Frappe Cloud site
context.

## Approval Gates

Required before live checkout opens:

1. GL approval to enter live payment/provider work.
2. Jeff/business approval of product scope and first live payment amount.
3. Confirmation of the intended merchant account. Stripe CLI access to a Built
   by Cameron account does not prove LT merchant approval.
4. GL/legal/accounting approval for payment, refund, privacy, terms, and
   accessibility URLs used by Stripe.
5. Approval to configure live Stripe keys, webhook secret, Payment Gateway
   Account, and Payment Method Configuration.
6. Approval to change `lt_ecommerce_paused` or otherwise expose live checkout.
7. Approval for a first real payment, including whether to refund or leave the
   payment as a real sale/accounting record.
8. Approval for any live Frappe Cloud site update/migrate/cache clear.
9. Approval for any Cloudflare DNS/cache/security change or Search Console
   action if those are in the same release window.

## First Low-Risk Real Payment Test Plan

Use only after all approval gates above are satisfied.

1. Select one approved low-risk, low-dollar sellable product or service deposit
   with clear tax/fulfillment expectations. If no approved product exists, stop.
2. Keep the cart to one item and one fulfillment path.
3. Confirm live ecommerce opens only for the intended narrow scope.
4. Complete checkout with an approved real card and approved customer/operator
   test identity.
5. Capture the Stripe payment id without printing card data or secrets.
6. Verify ERPNext Sales Order, Payment Request, Sales Invoice, Payment Entry,
   tax, grand total, outstanding amount, fulfillment details, and customer note.
7. Verify thank-you page state and customer-safe copy.
8. Verify receipt and operator Email Queue rows, scheduler processing, and
   `Sent` status. If inbox-visible proof is required, verify through an
   approved inbox path.
9. Reconcile Stripe amount to ERPNext amount to the cent.
10. If the approved plan is to refund, refund through the approved Stripe path
    and verify the ERPNext/accounting follow-up state. If the approved plan is
    to keep the payment, record it as a real sale/test purchase according to the
    business/accounting decision.
11. Restore the resting state unless GL explicitly approves wider live
    ecommerce exposure:

```bash
python scripts/verify/ecommerce_expected_mode.py --expect paused
python scripts/verify/ecommerce_pause_contract.py
```

## Rollback And Resting State

Default rollback/resting posture:

- Set or keep `lt_ecommerce_paused=1`.
- Confirm `/shop`, `/cart`, and `/checkout` route to the branded pause
  experience.
- Keep public pages and inquiry forms live if they are unaffected.
- Do not delete paid records. Mark, refund, cancel, or reverse only through an
  approved accounting/payment path.
- Do not manually patch production data to hide a broken checkout. Record the
  blocker and restore the customer-safe pause.
- If a Frappe Cloud release caused the break, compare previous live app hash to
  target app mirror commit before rollback or forward fix.
- After rollback, rerun:

```bash
python scripts/verify/ecommerce_expected_mode.py --expect paused
python scripts/verify/ecommerce_pause_contract.py
python scripts/verify/cloudflare_launch_readiness.py --base-url https://locallytwisted.com
```

## Must Not Be Touched Without Approval

- Staging or live Frappe Cloud app releases, site update/migrate jobs, cache
  clear, or provider settings.
- Live Stripe keys, webhook secret, Payment Method Configuration, Link/payment
  method settings, payment links, refunds, disputes, or Dashboard URLs.
- Cloudflare DNS, cache rules, security settings, redirects, email routing, or
  worker/pages settings.
- Search Console verification, sitemap submission, recrawl requests, or ad
  account conversion settings.
- `lt_ecommerce_paused`, live checkout exposure, live product publication
  scope, live prices, catalog source, product media, or Item/Website Item
  records.
- Customer records, real orders, real payments, real invoices, customer email,
  owner inboxes, customer data exports, or secrets.
- Email Account passwords, scheduler/worker state, and live receipt behavior
  except inside an approved payment/email gate.

## Closeout Rule

Call the gate `GO` only when live config, live route, product scope, payment,
email, owner/business approval, and first real low-risk payment proof are all
captured in a dated workstream. Until then, the correct status is NO-GO with
ecommerce paused.
