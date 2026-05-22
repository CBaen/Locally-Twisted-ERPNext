# Locally Twisted Launch Runbook

Last updated: 2026-05-22 by Codex.

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

## Current Confirmed State

1. Frappe Cloud
   - Staging-prep source commit exists and was prepared on 2026-05-22:
     `2ee28da Harden product galleries and release gates`.
   - Staging-prep Frappe app mirror commit exists and was prepared on
     2026-05-22:
     `f236d6d Sync app from LT source 2ee28da`.
   - These commits are not staging or live proof until Frappe Cloud
     deploy/update/migration/cache evidence exists for the target site.
   - Current owner-review staging state as of 2026-05-22: blocked. Current
     provider evidence puts `locallytwisted-staging.frappe.cloud` on Frappe
     Cloud bench group `bench-40102` / bench `bench-40102-000003-f4v`.
   - Current live/vanity state as of 2026-05-22: separate from staging on bench
     group `bench-39776` / bench `bench-39776-000015-f94v`.
   - Target app mirror commit for staging is `f236d6d`, but staging still
     reports installed app hash `b4b3bf80108234c12051b572ac9b9cd4728f0efc`
     after a failed site update/migrate. Hash is not site readiness. Owner
     review remains blocked until the installed app hash is the target and
     staging site update/migration/cache, app order, pause state, route,
     browser, account, Product Setup, and gallery proof pass on staging.
   - Last proven live full repo source commit:
     `631f9a8 Run contact intake schema sync on install`.
   - Last proven live Frappe app mirror commit:
     `b4b3bf8 Run contact intake schema sync on install`.
   - Previous live app hash:
     `04de8212aa7dbf4895716717865fc6e1029c757b`.
   - Last proven live site update/migrate job: `b48j584nua`, status `Success`.
   - Last proven live update job: `b48oge6unq`, status `Success`.
   - Historical 2026-05-16 source bench: `bench-39776-000013-f94-virginia`.
     This is not the current 2026-05-22 staging target.
   - Live/destination bench: `bench-39776-000015-f94v`.
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

Release/process rule:

- A triad is required before any commit/push/staging claim for release
  processes, major builds, or patch spirals.
- The triad must include artifact-owning helpers, not advisory-only helpers.
  Each helper must own a check or artifact and return inspectable evidence such
  as provider mapping, payload validation, verifier output, a patch plan, or a
  blocker log.
- Keep source scope, staging scope, and live/provider scope separate. A local
  pass is a prerequisite, not staging proof.
- Do not treat `LT_BASE_URL=<staging-url>` as a universal retarget. Verifiers
  that read the local Docker `frontend` database still prove local records even
  if their browser fetch points at staging.

Staging-safe gate list:

1. Confirm the exact source commit and app-mirror commit intended for staging.
2. Confirm current Frappe Cloud provider mapping. Current API inventory beats
   stale runbook bench IDs. As of 2026-05-22, staging is group `bench-40102` /
   bench `bench-40102-000003-f4v`, and live/vanity is group `bench-39776` /
   bench `bench-39776-000015-f94v`.
3. For Frappe Cloud API mutations, send `Content-Type: application/json` typed
   JSON payloads only. Do not send nested `apps` or `sites` values as strings;
   that can fail with `'str' object has no attribute 'get'`.
4. Confirm the staging host, site update/migration job, cache clear, installed
   app order, and `lt_ecommerce_paused=1`.
5. Run local hard gates first, including the relevant product/owner/access
   gates for the changed slice.
6. Run staging HTTP/browser gates against the staging URL.
7. Run any database-side proof in the staging environment, or mark that proof
   unverified. Do not claim staging from a local Docker database read.
8. Record remaining live-only blockers before any live/provider/Search Console
   action.

2026-05-22 provider trigger rule: Frappe Cloud supports commit-message deploy
markers for benches, but LT agents must not use generic `press-deploy`.
The old proposed targeted marker
`press-deploy-bench-39776-000013-f94-virginia` is stale and must not be used
for the current staging site. Current evidence points staging at group
`bench-40102`; any deploy/update must target the current staging group/site
explicitly and must still pass site update/migration before owner review.
Prefer dashboard/API deploy/update with the staging site explicitly selected.

Public site/forms release:

```powershell
python scripts/verify/frappe_cloud_preflight.py
python scripts/verify/cloudflare_launch_readiness_contract.py
python scripts/verify/cloudflare_launch_readiness.py --base-url https://locallytwisted.com
$env:LT_BASE_URL='https://locallytwisted.com'; npm run test:seo-contract
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
4. Reindexing/Search Console submission is blocked until live sitemap and
   canonical URLs use `https://locallytwisted.com`.

## Do Not Do

1. Do not tell Jeff checkout is live-ready until the real payment test passes.
2. Do not expose live checkout because pages/forms are live.
3. Do not paste Stripe, Cloudflare, or Frappe Cloud secrets into chat or docs.
4. Do not call a Frappe Cloud deploy complete until both bench deploy and site
   update/migration have succeeded and live route/API verifiers pass.
5. Do not treat app mirror commit `f236d6d`, a Frappe Cloud app hash, or a
   deploy candidate as staging proof while the target site still reports an old
   installed app hash. Hash existence is not site readiness.
6. Do not call a future release narrow from the final commit alone. Compare the
   previous live app hash to the target app mirror commit before promotion.
7. Do not treat a staging root login screen as live breakage without naming the
   environment and checking Website Settings parity.
8. Do not submit a sitemap or ask Google to reindex while the live sitemap or
   canonical tags point at `locallytwisted.v.frappe.cloud`.
