# Locally Twisted Launch Runbook

Last updated: 2026-05-11 by Codex.

This is the plain launch doc at the project root.

Detailed technical gate:
`workstreams/frappe-cloud-cloudflare-stripe-launch-2026-05-11.md`

Project capability:
`capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`

## The Simple Version

We are launching the site first and opening only the ecommerce pieces that pass
hardening, security, payment, and product-scope proof.

If ecommerce does not pass, the site still launches with ecommerce paused.

## Current Confirmed Access

1. Frappe Cloud
   - Partly confirmed.
   - GitHub access, app-source mirror, and SSH key are ready enough for preflight.
   - Frappe Cloud dashboard login/ownership is not confirmed from this machine.
   - Human part: Cameron must be available to log into Frappe Cloud.

2. Cloudflare
   - Domain uses Cloudflare nameservers.
   - This machine is not logged into Cloudflare Wrangler.
   - No Cloudflare API token is set here.
   - Human part: Cameron must be available to log into Cloudflare or approve DNS changes while authenticated.

3. Stripe
   - Stripe CLI is logged in on this machine.
   - Account shown: `Built by Cameron`.
   - Test and live keys are available until 2026-06-08.
   - Human/business part: confirm whether live LT payments should run through Built by Cameron Stripe or a Locally Twisted/Jeff-owned Stripe account.

## Launch Target

1. Public site goes live.
2. Contact/inquiry path goes live.
3. Ecommerce opens only for a small proven product set if the gates pass.
4. Face painting and balloon twisting deposits can be included only if their checkout path passes the same gates.
5. Live Stripe checkout stays blocked until the production config and one real low-risk payment test pass.

## Cameron's Human Checklist

Do these in order.

1. Be ready to log into Frappe Cloud.
2. Be ready to log into Cloudflare for `locallytwisted.com`.
3. Decide the Stripe account:
   - Built by Cameron Stripe, or
   - Locally Twisted / Jeff-owned Stripe.
4. Be available during DNS cutover.
5. Be ready for one tiny real live purchase/refund test when checkout is opened.

Jeff does not need to do the technical work. Cameron is the human operator for
cutover.

## Codex Owns

1. Freeze and check the exact source state.
2. Run Frappe Cloud preflight.
3. Get Frappe Cloud staging ready.
4. Verify staging pages, forms, accessibility, and contact smoke.
5. Keep ecommerce hidden unless the ecommerce gates pass.
6. Prove the small ecommerce product/deposit scope before opening it.
7. Configure/check live Stripe without printing secrets.
8. Check Cloudflare dynamic routes after DNS points at Frappe Cloud.
9. Block fake success, half-live checkout, or unsafe payment behavior.

## Required Gates

Run these from the repo root unless a staging/production URL is required.

```powershell
python scripts/verify/frappe_cloud_preflight.py
python scripts/verify/website_launch_verify.py --base-url <staging-url> --with-a11y --with-contact-smoke
python scripts/verify/ecommerce_pause_contract.py
python scripts/verify/cloudflare_launch_readiness.py --base-url https://locallytwisted.com
python scripts/verify/payment_launch_readiness.py --mode live --base-url https://locallytwisted.com
python scripts/verify/business_automation_index.py
python scripts/verify/synthetic_business_pipeline.py
python scripts/verify/payment_backend_config_contract.py
python scripts/verify/payment_webhook_contract.py
python scripts/verify/stripe_amount_parity_contract.py
```

## Current Blockers

1. Frappe Cloud dashboard login/ownership is not confirmed.
2. Cloudflare account control is not confirmed.
3. Stripe is confirmed on this machine, but it may be the wrong merchant account for LT.
4. `locallytwisted.com` is still the old/non-Frappe site today.

Before cutover, re-check `git status -sb` and the Frappe Cloud preflight. Do
not cut DNS from a dirty, ahead, behind, or unreviewed source state.

## Do Not Do Yet

1. Do not change DNS until staging passes.
2. Do not expose live checkout until live Stripe config passes.
3. Do not paste Stripe, Cloudflare, or Frappe Cloud secrets into chat or docs.
4. Do not tell Jeff checkout is live-ready until the real payment test passes.
5. Do not delay the public website just because full ecommerce is not ready.
