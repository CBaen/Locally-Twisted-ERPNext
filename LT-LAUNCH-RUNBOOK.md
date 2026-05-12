# Locally Twisted Launch Runbook

Last updated: 2026-05-12 by Codex.

This is the plain launch doc at the project root.

Detailed technical gate:
`workstreams/frappe-cloud-cloudflare-stripe-launch-2026-05-11.md`

Project capability:
`capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`

## The Simple Version

The public website and inquiry forms are now live on Frappe Cloud at
`https://locallytwisted.com`.

Ecommerce/live checkout is still a separate gate. The site can stay live while
checkout remains paused or quote-first.

## Current Confirmed State

1. Frappe Cloud
   - Live custom app release: `72a4se4v64`.
   - Live app hash: `04de8212aa7dbf4895716717865fc6e1029c757b`.
   - Final bench deploy: `62q1r0otg1`, status `Success`.
   - Final site update/migrate job: `15s16992i2`, status `Success`.
   - `deploy_in_progress=false`.
   - `has_running_release_pipeline=false`.

2. Cloudflare / domain
   - `locallytwisted.com` now reaches the Frappe Cloud site for the public
     website and inquiry forms.
   - Future DNS/security/cache changes still need the Cloudflare dynamic-route
     gate before claiming route health.

3. Public forms
   - `/contact` live smoke passed.
   - `/balloon-twisting-and-face-painting` live smoke passed.
   - Strict live repeat-email/five-photo proof passed with customer and business
     Email Queue body/recipient verification and cleanup.

4. Stripe / ecommerce
   - Live checkout remains blocked until the live Stripe config, product scope,
     policy URLs, webhook, and one real low-risk payment test pass.
   - Do not treat the public website being live as checkout approval.

## Codex Owns

1. Keep source, Frappe Cloud app mirror, and live site migration state aligned.
2. Verify live public routes and form submission paths after any release.
3. Keep ecommerce hidden, paused, or quote-first unless the ecommerce gates pass.
4. Prove any checkout/product/deposit scope before opening it.
5. Configure/check live Stripe without printing secrets.
6. Check Cloudflare dynamic routes after DNS/security/cache changes.
7. Block fake success, half-live checkout, stale migration claims, or unsafe
   payment behavior.

## Required Gates

Use these from the repo root unless a staging/production URL is required.

Public site/forms release:

```powershell
python scripts/verify/frappe_cloud_preflight.py
python scripts/verify/cloudflare_launch_readiness_contract.py
python scripts/verify/cloudflare_launch_readiness.py --base-url https://locallytwisted.com
```

Live form proof with authenticated backend verification:

```powershell
$env:LT_BACKEND_BASE_URL='https://locallytwisted.v.frappe.cloud'
$env:LT_BACKEND_CDP_URL='http://127.0.0.1:9222'
python scripts/verify/smoke_forms.py --base-url https://locallytwisted.com --form-path /contact --skip-newsletter
python scripts/verify/smoke_forms.py --base-url https://locallytwisted.com --form-path /balloon-twisting-and-face-painting --skip-newsletter
python scripts/verify/book_form_repeat_email_photos.py --base-url https://locallytwisted.com --admin-base-url https://locallytwisted.v.frappe.cloud --cdp-url http://127.0.0.1:9222
```

Before live checkout opens:

```powershell
python scripts/verify/ecommerce_pause_contract.py
python scripts/verify/payment_launch_readiness.py --mode live --base-url https://locallytwisted.com
python scripts/verify/business_automation_index.py
python scripts/verify/synthetic_business_pipeline.py
python scripts/verify/payment_backend_config_contract.py
python scripts/verify/payment_webhook_contract.py
python scripts/verify/stripe_amount_parity_contract.py
```

## Current Blockers

1. Live Stripe checkout is not approved.
2. The correct LT merchant account/payment ownership still needs explicit
   business approval before live payments.
3. Public ecommerce/product checkout remains separate from the pages/forms
   launch and must pass its own product/payment/customer-email proof.

## Do Not Do

1. Do not tell Jeff checkout is live-ready until the real payment test passes.
2. Do not expose live checkout because pages/forms are live.
3. Do not paste Stripe, Cloudflare, or Frappe Cloud secrets into chat or docs.
4. Do not call a Frappe Cloud deploy complete until both bench deploy and site
   update/migration have succeeded and live route/API verifiers pass.
