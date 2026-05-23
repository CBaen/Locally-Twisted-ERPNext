# Locally Twisted Launch Runbook

Last updated: 2026-05-23 by Codex.

This is the plain launch doc at the project root.

Detailed technical gate:
`workstreams/frappe-cloud-cloudflare-stripe-launch-2026-05-11.md`

Project capability:
`capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`

Current release-freeze action list:
`workstreams/frappe-cloud-release-prevention-action-items-2026-05-23.md`

Current release-freeze lock and local guard command:
`release_locks/locally-twisted-staging-forensic-freeze.json`

```powershell
npm run test:release-prevention
```

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

The 2026-05-22/23 owner-review staging push failed as a release process and is
frozen. Do not resume deploy/bootstrap mutation from that session. The first
local/offline release-prevention guards now exist, but staging owner review is
still not ready. Reopening provider mutation requires a fresh read-only
provider snapshot, an artifact-backed release packet, explicit release-plan
approval, and `scripts/verify/staging_owner_review_gate.py` passing on the
actual staging site.

2026-05-23 update: the first executable local/offline guard layer now exists:
`scripts/release/frappe_cloud_release_controller.py`,
`scripts/verify/release_lock_contract.py`,
`scripts/verify/release_controller_contract.py`,
`scripts/verify/frappe_cloud_payload_contract.py`, and
`scripts/verify/release_claim_language_contract.py`. This is not permission to
deploy. It is the local prevention gate future release work must pass before
asking to reopen provider mutation.

2026-05-23 template parity update: the previous documentation archive is
`5e11003 Document release artifact template parity`; the underlying template
fix is `f5e2e91 Update staging release artifact template`. It corrected the
staging-freeze packet template so future packets include the current required
shapes for reopen approval, app mirror sync plan, deploy completion, and
hosted preflight checks. It does not create real release artifacts or reopen
provider/staging execution. Handoff:
`workstreams/frappe-cloud-release-artifact-template-parity-2026-05-23.md`.

2026-05-23 chain-binding update: verify current source with `git log`; this
runbook intentionally names durable commit roles instead of trying to be the
latest-HEAD oracle. The artifact-chain implementation archive is
`3054396 Bind staging release artifacts`, with follow-up docs clarification at
`a838d8d Clarify current release archive`. The local release controller now
rejects mutation-capable release packets whose approval, app mirror
plan/freshness, provider snapshot, deploy payload, deploy completion, or
hosted preflight artifacts do not agree on source commit, app hash, rollback
hash, and site. Handoff:
`workstreams/frappe-cloud-release-artifact-chain-binding-2026-05-23.md`.

## Current Confirmed State

1. Frappe Cloud
   - Staging recovery save state:
     `savepoint/lt-staging-recovery-20260522-173929`.
   - Current owner-review staging state as of 2026-05-22: deployed to staging
     with ecommerce paused and public indexing disabled; owner-review
     account/route/gallery/security proof is still required before approval.
   - Current staging provider evidence puts
     `locallytwisted-staging.frappe.cloud` on Frappe Cloud bench group
     `bench-40102` / bench `bench-40102-000003-f4v`.
   - Current live/vanity state is separate from staging on bench group
     `bench-39776` / bench `bench-39776-000015-f94v`.
   - Final staging source commit:
     `2ca1b85 Ensure LT access roles before permission sync`.
   - Final staging Frappe app mirror commit:
     `3e86bc1 Ensure LT access roles before permission sync`.
   - Final installed staging `locally_twisted` hash:
     `3e86bc149d6dcc04daa194b740c1733f5c796261`.
   - Final staging site update/migrate job: `crn5pskff4`, status `Success`.
   - Final staging configuration job: `3u20303jfl`, status `Success`.
   - Final staging cache clear job: `eu27r8q4to`, status `Success`.
   - Final staging site state after deploy/config/cache: Active with `0`
     running jobs.
   - Staging safety settings: `lt_ecommerce_paused=true` and
     `lt_public_indexing_enabled=false`.
   - First staging recovery failure: the Frappe Cloud API was called with
     stringified nested `apps` / `sites` values instead of typed JSON. Release
     Pipeline `6podv9kvbn` failed with `'str' object has no attribute 'get'`.
   - Second staging recovery failure: site update/migrate jobs `8vspcanje0`
     and `63lqkkrppt` failed because the public-access guard blocked Frappe's
     temporary Portal Settings migration value. Source fix:
     `0f6fcad Fix staging portal migration guard`; app mirror fix:
     `9ddcb45 Allow portal guard repair during migrate`.
   - Third staging recovery failure: site update/migrate job `6itfpob0ra`
     failed because `LT Owner Access` and `LT Manager Access` roles did not
     exist before contact-intake permission sync. Source/app mirror fix:
     `2ca1b85` / `3e86bc1 Ensure LT access roles before permission sync`.
   - Live/DNS/Stripe/Search Console were not mutated during this staging
     recovery pass.
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

Staging-safe gate list for a future approved release reopen. Steps after the
active-lock check are not current permission to mutate provider state.

1. Run `npm run test:release-prevention` and confirm the active lock state.
   While `release_locks/locally-twisted-staging-forensic-freeze.json` is
   active, release mutation remains blocked.
2. Confirm the exact source commit and app-mirror commit intended for staging.
   The old 2026-05-22 recovery target was source `2ca1b85`, app mirror
   `3e86bc1`, installed hash `3e86bc149d6dcc04daa194b740c1733f5c796261`.
   Current 2026-05-23 read-only evidence supersedes that lane: source is
   archived through `5e11003`, while the app-root mirror/deployed staging hash
   was still `181076c239b2d1d3d508a41ac471c71f9d2b5158` in the latest no-go
   packets. Do not use the old `3e86bc1` path as current guidance.
3. Confirm current Frappe Cloud provider mapping. Current API inventory beats
   stale runbook bench IDs. As of 2026-05-22, staging is group `bench-40102` /
   bench `bench-40102-000003-f4v`, and live/vanity is group `bench-39776` /
   bench `bench-39776-000015-f94v`.
4. For Frappe Cloud API mutations, send `Content-Type: application/json` typed
   JSON payloads only. Do not send nested `apps` or `sites` values as strings;
   that can fail with `'str' object has no attribute 'get'`. Validate the
   sanitized payload first with `scripts/verify/frappe_cloud_payload_contract.py`.
5. Confirm the staging host, site update/migration job, cache clear, installed
   app order, `lt_ecommerce_paused=1`, and
   `lt_public_indexing_enabled=0`.
6. Run local hard gates first, including the relevant product/owner/access
   gates for the changed slice.
7. Run staging HTTP/browser gates against the staging URL, including logged-in
   owner/backend product review and guest paused-shop behavior.
8. Run staging account gates for `locallytwisted@gmail.com` and
   `marketing@exploringnotboring.com`.
9. Run any database-side proof in the staging environment, or mark that proof
   unverified. Do not claim staging from a local Docker database read.
10. Record remaining live-only blockers before any live/provider/Search Console
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
5. Owner-review staging is deployed but still needs staging-specific account,
   logged-in route, Product Setup/gallery, browser, and security-suite proof
   before it is treated as ready for Jeff's review.

## Do Not Do

1. Do not tell Jeff checkout is live-ready until the real payment test passes.
2. Do not expose live checkout because pages/forms are live.
3. Do not paste Stripe, Cloudflare, or Frappe Cloud secrets into chat or docs.
4. Do not call a Frappe Cloud deploy complete until both bench deploy and site
   update/migration have succeeded. For staging, also prove staging route/API,
   cache, pause, indexing, account, and product/gallery behavior before owner
   review.
5. Do not treat an app mirror commit, a Frappe Cloud release hash, or a deploy
   candidate as staging proof by itself. Hash existence is not site readiness;
   the site update/migration/cache and route/account gates must pass too.
6. Do not call a future release narrow from the final commit alone. Compare the
   previous live app hash to the target app mirror commit before promotion.
7. Do not treat a staging root login screen as live breakage without naming the
   environment and checking Website Settings parity.
8. Do not submit a sitemap or ask Google to reindex while the live sitemap or
   canonical tags point at `locallytwisted.v.frappe.cloud`.
