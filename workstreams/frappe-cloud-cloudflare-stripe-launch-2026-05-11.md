# Frappe Cloud, Cloudflare, And Stripe Launch Gate

Last updated: 2026-05-11 by Codex.

## Scope

This workstream turns the public launch plan into an executable gate.

Project-root operator runbook: `LT-LAUNCH-RUNBOOK.md`.
Project capability: `capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`.

Default launch posture:

- Public pages and `/contact` go live first.
- `lt_ecommerce_paused=1` stays set for launch unless GL/Jeff explicitly reopen public checkout.
- `/shop`, `/cart`, and `/checkout` must show the branded quote fallback while paused.
- Live Stripe checkout stays closed until staging, live payment config, product scope, and one real low-risk payment test pass.

This file does not authorize DNS cutover by itself. The controller still owns the final go/no-go evidence.

## Tracks

| Track | Owner lane | Gate |
|---|---|---|
| Source/Frappe Cloud | Push exact reviewed launch commit, sync the app-root Frappe Cloud source, create staging, install apps with `locally_twisted` last | `python scripts/verify/frappe_cloud_preflight.py` before staging mutation |
| Public site/forms | Verify staging pages, layout, accessibility, and `/contact` backend smoke | `python scripts/verify/website_launch_verify.py --base-url <staging-url> --with-a11y --with-contact-smoke` |
| Hidden commerce | Keep ecommerce paused for launch and prove no half-live checkout leaks | `python scripts/verify/ecommerce_pause_contract.py` |
| Cloudflare | After staging passes, point `www` and apex only in the owner-present cutover window; dynamic routes must bypass cache/challenges | `python scripts/verify/cloudflare_launch_readiness.py --base-url https://locallytwisted.com` |
| Stripe | Configure live keys/settings/webhook only after production host exists | `python scripts/verify/payment_launch_readiness.py --mode live --base-url https://locallytwisted.com` |
| Backend proof before opening checkout | Prove checkout/payment cascades with fake-data and mocked Stripe first | `business_automation_index.py`, `synthetic_business_pipeline.py`, `payment_backend_config_contract.py`, `payment_webhook_contract.py`, `stripe_amount_parity_contract.py` |

## Production Config Contract

Set these explicitly in the Frappe Cloud site config before live checkout:

- `host_name`
- `lt_stripe_settings_name`
- `lt_payment_gateway_account`
- `lt_stripe_payment_method_configuration`
- `lt_operator_email`
- `stripe_webhook_signing_secret`

`payment_launch_readiness.py --mode live` now fails if `host_name` is missing, local-only, or not HTTPS.

Stripe webhook endpoint:

```text
/api/method/locally_twisted.payments.stripe_webhook.stripe_webhook
```

Use the full production URL in Stripe Dashboard after the production host exists:

```text
https://locallytwisted.com/api/method/locally_twisted.payments.stripe_webhook.stripe_webhook
```

## Cloudflare Dynamic Route Contract

Cloudflare must not cache or challenge these dynamic paths:

- `/login`
- `/me`
- `/contact`
- `/cart`
- `/checkout`
- `/payment-success`
- `/thank-you`
- `/api/method/frappe.ping`
- `/api/method/locally_twisted.payments.stripe_webhook.stripe_webhook`

`scripts/verify/cloudflare_launch_readiness.py` checks those paths through
public HTTP and fails on missing `404` routes, Cloudflare challenge markers, or
`cf-cache-status` values that show Cloudflare considered a dynamic route
cacheable. Only absent cache headers, `BYPASS`, and `DYNAMIC` pass. `MISS` is a
blocker because it can become `HIT` on the next request after purge or a
Cache-Everything-style rule.

Fast local contract:

```powershell
python scripts/verify/cloudflare_launch_readiness_contract.py
```

## Cutover Order

1. Freeze source: no unrelated dirty or ahead work can be part of cutover.
2. Run `python scripts/verify/frappe_cloud_preflight.py`.
3. Create or refresh Frappe Cloud staging from the reviewed source.
4. Install apps in order with `locally_twisted` last.
5. On staging, run `python scripts/verify/website_launch_verify.py --base-url <staging-url> --with-a11y --with-contact-smoke`.
6. Keep `lt_ecommerce_paused=1` and run `python scripts/verify/ecommerce_pause_contract.py`.
7. Point Cloudflare DNS only after staging passes.
8. Run `python scripts/verify/cloudflare_launch_readiness_contract.py`, then `python scripts/verify/cloudflare_launch_readiness.py --base-url https://locallytwisted.com`.
9. Configure live Stripe settings, payment gateway account, webhook secret, operator email, and policy URLs only after owner/legal approval.
10. Run `python scripts/verify/payment_launch_readiness.py --mode live --base-url https://locallytwisted.com`.
11. Do one low-risk live Stripe Checkout purchase only when checkout is intentionally opened, confirm ERPNext paid chain and customer/operator emails queue once, then refund if appropriate.

## Current Blockers / Deferrals

- Current public-domain probe on 2026-05-11 still hits the existing non-Frappe site: `/login`, `/payment-success`, `/api/method/frappe.ping`, and the Stripe webhook route return `404`. This is expected before DNS cutover and blocks treating `locallytwisted.com` as the Frappe production host today.
- DNS cutover is blocked until staging passes and the source commit is frozen.
- Live Stripe checkout is blocked until live config passes and policy URLs are owner/legal approved.
- Public ecommerce is intentionally deferred for launch unless GL/Jeff explicitly approve reopening it.
- Link remains disabled unless GL/Jeff explicitly approve it in the live Stripe account.
