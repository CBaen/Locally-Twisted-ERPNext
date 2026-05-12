---
name: Frappe Cloud Cloudflare Stripe launch gate
level: recipe
last_verified: 2026-05-12
currently_true: true
---

# Frappe Cloud Cloudflare Stripe Launch Gate

## What It Does

Keeps Locally Twisted launch work from collapsing four different jobs into one:

- Frappe Cloud staging/production host setup.
- Cloudflare DNS/security routing.
- Stripe live payment readiness.
- Public ecommerce exposure.

The project-root human/operator runbook is `LT-LAUNCH-RUNBOOK.md`.
The detailed technical handoff is
`workstreams/frappe-cloud-cloudflare-stripe-launch-2026-05-11.md`.

## Current Contract

Default public launch posture:

- Public site and `/contact` can launch first. As of 2026-05-12,
  `locallytwisted.com` is serving the Frappe Cloud site for pages/forms.
- Ecommerce remains paused with `lt_ecommerce_paused=1` unless a deliberate
  product/payment gate opens a narrow shelf.
- Some ecommerce may launch only after hardening, security, payment, product
  scope, and live payment proof pass.
- Face painting and balloon twisting deposits count as ecommerce/payment
  surfaces; they need the same proof as product checkout.
- If ecommerce fails a real gate, the site launches with the branded ecommerce
  pause fallback instead of waiting for full checkout.
- A Frappe Cloud bench deploy hash is not enough. The site update/migration job
  must succeed, the source app must own the live schema, and public live
  route/API/form verifiers must pass.

## Human Access Boundary

Do not confuse technical preflight with account control.

- Frappe Cloud: local preflight can confirm GitHub mirror/SSH/app packaging,
  but dashboard login/ownership still requires Cameron.
- Cloudflare: nameserver delegation can be verified, but account control is
  not confirmed unless Wrangler/API/session access works or Cameron is logged
  in.
- Stripe: CLI access on Wardenclyffe currently shows `Built by Cameron`; agents
  must confirm whether LT live payments should use that account or a
  Locally Twisted/Jeff-owned Stripe account.

Once GL says the needed provider account is logged in or otherwise available,
dashboard execution becomes agent-owned work. Use the documented Frappe Cloud
flow, provider API/CLI/SSH, or Playwright/browser automation before escalating.
Escalate only MFA, unavailable credentials, payment/business approval, or a
destructive final go/no-go.

## Required Gates

Run from repo root unless a staging/production URL is explicitly required.

```powershell
python scripts/verify/frappe_cloud_preflight.py
python scripts/verify/website_launch_verify.py --base-url <staging-url> --with-a11y --with-contact-smoke
python scripts/verify/ecommerce_pause_contract.py
python scripts/verify/cloudflare_launch_readiness_contract.py
python scripts/verify/cloudflare_launch_readiness.py --base-url https://locallytwisted.com
python scripts/verify/payment_launch_readiness.py --mode live --base-url https://locallytwisted.com
python scripts/verify/business_automation_index.py
python scripts/verify/synthetic_business_pipeline.py
python scripts/verify/payment_backend_config_contract.py
python scripts/verify/payment_webhook_contract.py
python scripts/verify/stripe_amount_parity_contract.py
```

For live inquiry form release proof, include authenticated backend verification
against the Frappe Cloud admin host:

```powershell
$env:LT_BACKEND_BASE_URL='https://locallytwisted.v.frappe.cloud'
$env:LT_BACKEND_CDP_URL='http://127.0.0.1:9222'
python scripts/verify/smoke_forms.py --base-url https://locallytwisted.com --form-path /contact --skip-newsletter
python scripts/verify/smoke_forms.py --base-url https://locallytwisted.com --form-path /balloon-twisting-and-face-painting --skip-newsletter
python scripts/verify/book_form_repeat_email_photos.py --base-url https://locallytwisted.com --admin-base-url https://locallytwisted.v.frappe.cloud --cdp-url http://127.0.0.1:9222
```

## Failure Modes

- Treating `frappe_cloud_preflight.py` as proof of Frappe Cloud dashboard
  ownership.
- Treating Cloudflare nameserver delegation as proof that Codex can edit DNS.
- Treating any logged-in Stripe account as the correct LT merchant account.
- Handing GL Frappe Cloud/Cloudflare dashboard steps after GL has already made
  the account session available.
- Treating `locallytwisted.com` as the Frappe host before the dynamic Frappe
  routes and webhook path pass.
- Treating a successful Frappe Cloud bench deploy as proof the site is running
  the new code before site update/migration succeeds.
- Letting custom fields or custom DocTypes exist only in the local database
  instead of source-controlled install/migration code.
- Querying optional legacy fields during migration without checking current
  DocType metadata.
- Opening checkout because local fake-data contracts pass, without live
  HTTPS host, explicit live Stripe config, webhook secret, policy URLs, and one
  low-risk real payment test.

## Verification Notes

On 2026-05-11:

- `frappe_cloud_preflight.py` had no hard blockers but did warn when the
  worktree was dirty/ahead.
- `cloudflare_launch_readiness.py --base-url http://localhost:8081 --allow-http`
  proved the local route logic.
- `cloudflare_launch_readiness.py --base-url https://locallytwisted.com`
  blocked because the public domain still hit the existing non-Frappe site.
- `payment_launch_readiness.py` passed local test-mode checks.
- `payment_launch_readiness.py --mode live` correctly failed on test Stripe
  config and local/non-HTTPS host configuration.

On 2026-05-12:

- Final Frappe Cloud custom app release was `72a4se4v64`.
- Final app hash was `04de8212aa7dbf4895716717865fc6e1029c757b`.
- Final bench deploy `62q1r0otg1` succeeded.
- Final site update/migrate job `15s16992i2` succeeded.
- `deploy_in_progress=false` and `has_running_release_pipeline=false`.
- Live `/contact` and live BTFP smoke passed with backend proof and cleanup.
- Strict live repeat-email/five-photo proof passed with customer and owner
  Email Queue body/recipient verification and cleanup.
