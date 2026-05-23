---
name: Frappe Cloud Cloudflare Stripe launch gate
level: recipe
last_verified: 2026-05-22
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
- As of 2026-05-14, public Frappe Cloud route health and Cloudflare
  dynamic-route health are verified, but direct Frappe Cloud dashboard/API/CLI
  management from Codex is not proven by those checks.
- As of 2026-05-16, the inquiry-photo storage/owner attachment hotfix and
  inquiry form hardening are live at full repo `631f9a8` and app mirror
  `b4b3bf8`; site update `b48j584nua` / update job `b48oge6unq` succeeded, and
  the accepted live smoke proved CRM photo rows plus owner-only Email Queue
  attachment refs.
- Future release scope must be compared from previous live app hash to target
  app mirror commit. Dirty-worktree checks do not prove full deployed scope.
- Staging root/login behavior depends on Website Settings parity. Check
  staging `/`, `/#login`, `/home`, `/contact`, `home_page`, branding, favicon,
  and theme before calling source broken or live broken.
- Public route health is not Search Console readiness. After custom-domain
  cutover, sitemap, canonical, Open Graph URL, and structured-data URLs must
  advertise the public domain, not the Frappe Cloud vanity host. As of
  2026-05-19, source guard work exists but live reindex work remains blocked
  until the fix is released and verified.
- As of 2026-05-22, owner-review staging is blocked, not ready. Current
  provider evidence puts `locallytwisted-staging.frappe.cloud` on Frappe Cloud
  bench group `bench-40102` / bench `bench-40102-000003-f4v`, while live and
  vanity traffic are separate on group `bench-39776` / bench
  `bench-39776-000015-f94v`. The target app mirror commit `f236d6d` exists, but
  staging still reports installed app hash
  `b4b3bf80108234c12051b572ac9b9cd4728f0efc` after a failed
  site update/migrate. Hash is not site readiness: app mirror hash, deploy
  candidate, or bench deploy evidence is not owner-review proof until the
  staging installed app hash matches the target, site update/migration/cache
  succeeds, and staging route/browser/account/Product Setup/gallery checks pass
  on staging.
- As of 2026-05-23, the owner-review staging attempt documented in
  `workstreams/frappe-cloud-staging-release-failure-forensics-2026-05-23.md`
  failed as a release process and is frozen. That session's commits, app mirror
  hashes, deploy IDs, and interrupted bootstrap attempts are not launch
  authority. A new release controller must start from current read-only
  provider state and an artifact-backed plan before any mutation. The concrete
  action list is
  `workstreams/frappe-cloud-release-prevention-action-items-2026-05-23.md`.

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

Triad rule:

- Release processes, major builds, and patch spirals require triad review
  before commit, push, staging, live, provider, or Search Console claims.
- The triad must separately check source scope, staging/live gate evidence, and
  doc truth. Local green checks are prerequisites, not release approval.
- Release triads must include artifact-owning helpers, not advisory-only
  commentary. Each helper must own a check or artifact and return concrete
  evidence such as a provider mapping report, payload validation note, verifier
  output, patch plan, or blocker log that the controller can inspect before
  mutation or closeout.
- Do not treat `LT_BASE_URL=<staging-url>` as a universal retarget. A verifier
  that shells into the local Docker `frontend` site still proves local ERPNext
  records even if it fetches rendered HTML from another host.
- After one provider/bootstrap failure, stop for forensic classification and
  write the guard before retry. After two related failures, all provider
  mutation stops until a new artifact-owning triad approves a fresh release
  plan. If GL says stop, execution stops immediately.

Concise staging-safe list:

1. Identify the source commit, app-mirror commit, staging host, rollback path,
   and whether the push is archive-only or deploy-triggering.
2. Prove current Frappe Cloud site mapping before mutation. Current API
   inventory beats stale runbook bench IDs; do not reuse old bench IDs from
   docs without API/dashboard proof. For 2026-05-22 staging, the current target
   is group `bench-40102` / bench `bench-40102-000003-f4v`, not the old
   `bench-39776-000013-f94-virginia` source-bench reference.
3. For Frappe Cloud API mutations, send `Content-Type: application/json`
   typed JSON payloads only. For `press.api.bench.deploy_and_update`, `apps`
   and `sites` must be real JSON arrays/objects accepted by the endpoint, not
   nested JSON strings. A payload that stringifies nested `apps` or `sites` can
   fail with `'str' object has no attribute 'get'`.
4. Prove Frappe Cloud deploy, site update/migration, cache clear, app order, and
   `lt_ecommerce_paused=1` on staging.
5. Run local hard gates for the changed slice before staging.
6. Run staging HTTP/browser gates against the staging URL.
7. Run database-side contracts in the staging environment, or leave them
   explicitly unverified for staging.
8. Keep live checkout, Stripe, DNS, Search Console, and provider mutations
   blocked until their separate gates pass.

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
$env:LT_BASE_URL='https://locallytwisted.com'; npm run test:seo-contract
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
- Treating app mirror commit `f236d6d`, app release hash, or deploy candidate
  creation as staging proof while the target site still reports the old
  installed app hash. Hash existence is not site readiness.
- Continuing provider/bootstrap mutation after repeated failure classes instead
  of stopping for forensic review and prevention architecture.
- Treating prose warnings as release controls when no release lock, payload
  validator, circuit breaker, or required-doc receipt exists.
- Letting advisory-only subagents satisfy a release triad without concrete
  artifacts owned by Provider Witness, Gate/Fixer, and Recorder.
- Treating the final source commit as the full Frappe Cloud release scope
  instead of comparing previous live app hash to target app mirror commit.
- Sending Frappe Cloud API payloads without `Content-Type: application/json`,
  or with nested `apps` or `sites` encoded as strings instead of typed JSON
  arrays/objects, then treating the API exception as a provider mystery instead
  of a payload-contract failure.
- Treating staging `/#login` rendering Sign In as live breakage before checking
  environment and Website Settings parity.
- Treating `Server: Frappe Cloud` or a passing dynamic-route gate as proof that
  sitemap/canonical URLs are ready for Search Console.
- Letting custom fields or custom DocTypes exist only in the local database
  instead of source-controlled install/migration code.
- Querying optional legacy fields during migration without checking current
  DocType metadata.
- Opening checkout because local fake-data contracts pass, without live
  HTTPS host, explicit live Stripe config, webhook secret, policy URLs, and one
  low-risk real payment test.
- Treating a source/app mirror push for form-photo delivery as live proof
  before bench deploy, site update/migration, and live verifier proof of CRM
  photo rows plus owner Email Queue attachment refs.
- Treating a local Docker/database verifier as staging proof just because
  `LT_BASE_URL` points at a staging URL.

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

On 2026-05-14:

- `https://locallytwisted.com` returned HTTP 200 with `Server: Frappe Cloud`.
- `/api/method/frappe.ping` returned HTTP 200 with `{"message":"pong"}`.
- `cloudflare_launch_readiness.py --base-url https://locallytwisted.com`
  passed 10 checks with 0 blockers and 0 warnings.
- `frappe_cloud_preflight.py` passed after its `dns_current_target` wording was
  corrected to recognize `www.locallytwisted.com` targeting
  `locallytwisted.v.frappe.cloud`.
- Host inspection found no direct Frappe Cloud CLI, host `bench`, or Frappe
  Cloud environment variables. Treat dashboard/API control as a separate
  authenticated management surface.

On 2026-05-15:

- Full repo commit `4422793 Fix inquiry photo storage and owner attachments`
  and app mirror commit `6a06062 Fix inquiry photo storage and owner
  attachments` were pushed.
- `frappe_cloud_preflight.py` and `cloudflare_launch_readiness.py --base-url
  https://locallytwisted.com` passed after the source push, proving preflight
  and route health only.
- Direct Frappe Cloud management was still unavailable from Codex in that
  session, so live deploy/site update and live repeat-email/five-photo verifier
  proof remained pending until the 2026-05-16 release below.

On 2026-05-16:

- Full repo commit `631f9a8 Run contact intake schema sync on install` and app
  mirror commit `b4b3bf8 Run contact intake schema sync on install` were live.
- Frappe Cloud site update `b48j584nua` and update job `b48oge6unq` succeeded;
  cache clear job `26es8svcaq` succeeded.
- Live routes `/`, `/#login`, `/contact`, and `/login` returned expected
  surfaces.
- Real company-email smoke `smoke test from cameron` created Lead
  `CRM-LEAD-2026-00013` with five private Files and five CRM photo rows. Owner
  Email Queue `683s86r04b` sent to `locallytwisted@gmail.com` with five
  attachment refs; customer Email Queue `683suhfaa9` sent with zero photo
  attachments.
- Staging `/#login` rendered Sign In because staging Website Settings drifted,
  not because live was broken. Staging was repaired and cache clear job
  `fb85o6ncdh` succeeded.

On 2026-05-22:

- Source `2ee28da Harden product galleries and release gates` and app mirror
  `f236d6d Sync app from LT source 2ee28da` exist and were prepared for
  owner-review staging.
- Current provider API inventory superseded the older staging/source-bench
  assumption and any stale runbook bench IDs: staging is group `bench-40102` / bench
  `bench-40102-000003-f4v`; live and vanity are group `bench-39776` / bench
  `bench-39776-000015-f94v`.
- Staging installed app hash remained
  `b4b3bf80108234c12051b572ac9b9cd4728f0efc` after a failed
  site update/migrate, so the owner-review staging gate remained blocked until
  the installed hash is the target and staging site update/migrate/cache plus
  route, browser, account, Product Setup, and gallery proof pass.
- Frappe Cloud API payloads must use `Content-Type: application/json` and
  preserve nested `apps` and `sites` as typed JSON. A failed attempt that sent
  nested values as strings produced `'str' object has no attribute 'get'`; the
  recovery path is payload validation, not guessing at new hashes.
