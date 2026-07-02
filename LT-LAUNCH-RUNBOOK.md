# Locally Twisted Launch Runbook

Last updated: 2026-05-24 by Codex.

This is the plain launch doc at the project root.

Detailed technical gate:
`workstreams/frappe-cloud-cloudflare-stripe-launch-2026-05-11.md`

Project capability:
`capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`

## The Simple Version

The public website and inquiry forms are now live on Frappe Cloud at
`https://locallytwisted.com`.

Ecommerce/live checkout is still a separate gate. The site can stay live while
checkout remains paused and unproven products remain internally held.

The 2026-05-14 connection audit proves public route health, not direct Frappe
Cloud dashboard/API control from Codex.

The 2026-05-15 inquiry-photo hotfix is now live and proved on 2026-05-16 by a
real company-email smoke with five photos. That smoke proved CRM photo rows and
owner-only queued attachment refs. Ecommerce/live checkout is still blocked.

The 2026-05-19 domain/provider audit confirms the public web path is GoDaddy
registrar -> Cloudflare DNS/email routing -> Frappe Cloud -> ERPNext/Frappe.
Reindexing is blocked until the live sitemap/canonical fix is released because
current live discovery URLs still advertise the Frappe Cloud vanity host.

The 2026-05-24 staging owner-review recovery put the current product/cart
experience back on hosted staging far enough for route proof:
`npm run test:checkout-experience` passed `3/3` and
`npm run test:product-gallery-experience` passed `4/4` against
`https://locallytwisted-staging.frappe.cloud`. Owner card-path testing is still
blocked because staging cannot decrypt `Stripe Settings.Test.secret_key`.
Staging payment settings must be repaired before test-card review.

## Current Confirmed State

1. Frappe Cloud
   - Current full repo source commit:
     `631f9a8 Run contact intake schema sync on install`.
   - Current Frappe app mirror commit:
     `b4b3bf8 Run contact intake schema sync on install`.
   - Previous live app hash:
     `04de8212aa7dbf4895716717865fc6e1029c757b`.
   - Current site update/migrate job: `b48j584nua`, status `Success`.
   - Current update job: `b48oge6unq`, status `Success`.
   - Source bench: `bench-39776-000013-f94-virginia`.
   - Destination bench: `bench-39776-000015-f94v`.
   - Cache clear job: `26es8svcaq`, status `Success`.
   - Site state after update: Active, no update available.
   - 2026-05-14 public route probe: `https://locallytwisted.com` returned HTTP
     200 with `Server: Frappe Cloud`.
   - 2026-05-14 API probe: `/api/method/frappe.ping` returned HTTP 200 with
     `{"message":"pong"}`.
   - Direct Frappe Cloud management from this host is not proven by that route
     probe. No direct `fcloud`/Frappe Cloud CLI, host `bench`, or Frappe Cloud
     env vars were found during the connection audit.

2. Cloudflare / domain
   - `locallytwisted.com` now reaches the Frappe Cloud site for the public
     website and inquiry forms.
   - Cloudflare is authoritative DNS with `edward.ns.cloudflare.com` and
     `laura.ns.cloudflare.com`.
   - Cloudflare API reports original registrar as GoDaddy and original
     nameservers as Bluehost.
   - 2026-05-14 Cloudflare dynamic-route gate passed 10 checks with 0 blockers
     and 0 warnings.
   - 2026-05-14 Frappe Cloud preflight recognized the `www` Frappe Cloud
     vanity host target and passed with 0 blockers and 0 warnings after stale
     DNS-target wording was corrected.
   - Future DNS/security/cache changes still need the Cloudflare dynamic-route
     gate before claiming route health.

3. Search / reindex
   - Google Search Console TXT verification exists in Cloudflare DNS.
   - Live sitemap currently uses `locallytwisted.v.frappe.cloud` for all 29
     locs. Live `/about` canonical and `og:url` also use the vanity host.
   - Source fix started in `seo.py` and `www/sitemap.py`; no Frappe Cloud
     release has been run for that fix yet.
   - Do not submit the sitemap or request recrawl until live SEO verification
     passes against `https://locallytwisted.com`.

4. Public forms
   - `/contact` live smoke passed.
   - `/balloon-twisting-and-face-painting` live smoke passed.
   - Strict live repeat-email/five-photo proof passed with customer and business
     Email Queue body/recipient verification and cleanup.
   - 2026-05-16 real company-email smoke passed with contact name
     `smoke test from cameron`, Lead `CRM-LEAD-2026-00013`, five private Lead
     Files, five CRM photo rows, owner Email Queue `683s86r04b` with five
     attachment refs, and customer Email Queue `683suhfaa9` with no photo
     attachments.

5. Stripe / ecommerce
   - Stripe CLI access on `wardenclyffe` works for the Built by Cameron account,
     but that does not approve LT live checkout or merchant-account ownership.
   - Live checkout remains blocked until the live Stripe config, product scope,
     policy URLs, webhook, and one real low-risk payment test pass.
   - Do not treat the public website being live as checkout approval.
   - There are no business quote-first products. Product rows that still carry
     legacy internal hold values are blocked because source, pricing, media,
     browser, payment, or owner-approval proof is incomplete.
   - Current local repair proof: four simple products passed backend, browser,
     and payment/customer-message cascade; six multi-color products passed
     backend checkout/SO/SI rehearsal plus desktop/mobile browser product,
     cart, and checkout preview. Neither tranche is live-approved.
   - 2026-05-24 staging route proof now passes for checkout and product
     gallery, but staging final payment handoff is blocked by encrypted
     payment-secret configuration. See
     `workstreams/frappe-cloud-staging-owner-review-2026-05-24.md` and
     `capabilities/failures/frappe-cloud-staging-stripe-secret-drift.md`.

## Codex Owns

1. Keep source, Frappe Cloud app mirror, and live site migration state aligned.
2. Verify live public routes and form submission paths after any release.
3. Keep ecommerce hidden or paused, and keep unproven products internally held,
   unless the ecommerce gates pass.
4. Prove any checkout/product/deposit scope before opening it.
5. Configure/check live Stripe without printing secrets.
6. Check Cloudflare dynamic routes after DNS/security/cache changes.
7. Check sitemap/canonical public-domain output before Search Console reindex
   work.
8. Block fake success, half-live checkout, stale migration claims, or unsafe
   payment behavior.

## Required Gates

Use these from the repo root unless a staging/production URL is required.

Public site/forms release:

```bash
python scripts/verify/frappe_cloud_preflight.py
python scripts/verify/cloudflare_launch_readiness_contract.py
python scripts/verify/cloudflare_launch_readiness.py --base-url https://locallytwisted.com
LT_BASE_URL='https://locallytwisted.com' npm run test:seo-contract
```

Live form proof with authenticated backend verification:

```bash
export LT_BACKEND_BASE_URL='https://locallytwisted.v.frappe.cloud'
export LT_BACKEND_CDP_URL='http://127.0.0.1:9222'
python scripts/verify/smoke_forms.py --base-url https://locallytwisted.com --form-path /contact --skip-newsletter
python scripts/verify/smoke_forms.py --base-url https://locallytwisted.com --form-path /balloon-twisting-and-face-painting --skip-newsletter
python scripts/verify/book_form_repeat_email_photos.py --base-url https://locallytwisted.com --admin-base-url https://locallytwisted.v.frappe.cloud --cdp-url http://127.0.0.1:9222
```

Before live checkout opens:

```bash
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
2. Staging owner card-path testing is blocked until staging test payment
   settings decrypt and one authorized test-mode checkout proves ERPNext
   records, receipt, operator email, tax, and payment state.
3. The correct LT merchant account/payment ownership still needs explicit
   business approval before live payments.
4. Public ecommerce/product checkout remains separate from the pages/forms
   launch and must pass its own product/payment/customer-email proof.
5. Reindexing/Search Console submission is blocked until live sitemap and
   canonical URLs use `https://locallytwisted.com`.

## Do Not Do

1. Do not tell Jeff checkout is live-ready until the real payment test passes.
2. Do not expose live checkout because pages/forms are live.
3. Do not paste Stripe, Cloudflare, or Frappe Cloud secrets into chat or docs.
4. Do not call a Frappe Cloud deploy complete until both bench deploy and site
   update/migration have succeeded and live route/API verifiers pass.
5. Do not call a future release narrow from the final commit alone. Compare the
   previous live app hash to the target app mirror commit before promotion.
6. Do not treat a staging root login screen as live breakage without naming the
   environment and checking Website Settings parity.
7. Do not submit a sitemap or ask Google to reindex while the live sitemap or
   canonical tags point at `locallytwisted.v.frappe.cloud`.
