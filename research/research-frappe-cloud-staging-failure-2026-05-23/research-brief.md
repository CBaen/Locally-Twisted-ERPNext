# Frappe Cloud Staging Failure Research Brief

## 2026-05-23 Supersession

This brief is historical research context, not a current release plan. Release
execution was stopped after the owner-review staging process failed as a
process. Do not use the recovery language below to resume provider mutation.
Current controlling docs:

- `../../workstreams/frappe-cloud-staging-release-failure-forensics-2026-05-23.md`
- `../../workstreams/frappe-cloud-release-prevention-action-items-2026-05-23.md`
- `../../capabilities/failures/release-controller-churn-after-stop.md`

Next safe work is implementing executable prevention gates, then taking a fresh
read-only provider snapshot under a new release controller.

### 1. Want

Locally Twisted needs Frappe Cloud staging repaired and documented so peer agents can safely continue owner-review staging without touching live, DNS, Stripe, or Search Console. Success means `https://locallytwisted-staging.frappe.cloud` is proven to run the target `locally_twisted` app mirror commit `f236d6d`, the staging site update/migration and cache clear are proven, and staging-side owner/product/gallery/access/ecommerce checks pass with a sanitized evidence chain another agent can audit.

### 2. Have

As of the requested date boundary, 2026-05-22 America/Denver / 2026-05-23 UTC, LT is an ERPNext/Frappe v15 custom app in `C:\Users\baenb\projects\Built_by_Cameron\_CLIENTS\locally-twisted`; source `main` is archived at `2ee28da Harden product galleries and release gates`, and the private app-root mirror `CBaen/Locally-Twisted-Frappe-App` is archived at `f236d6d Sync app from LT source 2ee28da`. Current repo docs say staging is `https://locallytwisted-staging.frappe.cloud`, mapped to Frappe Cloud bench group `bench-40102` / bench `bench-40102-000003-f4v`; live remains separate on bench group `bench-39776` / bench `bench-39776-000015-f94v`. Local hard gates passed before staging work: `frappe_cloud_preflight.py`, `human_access_silo_matrix.py`, `marketing_review_access_boundary.py`, `npm run test:owner-product-safety`, and `npm run test:ecommerce-full`. Staging is blocked, not owner-review ready: the corrected staging bench deploy was attempted; site update/migrate jobs `8vspcanje0` and `63lqkkrppt` failed; recovery jobs succeeded; latest provider check in repo docs says staging is `Active`, has `0` running jobs, `update_available=true`, and installed `locally_twisted` hash still old `b4b3bf8` instead of target `f236d6d`. Current provider behavior must be researched live because model training stops at 2024-06 and Frappe Cloud docs are actively changing: official docs checked for this brief say Frappe Cloud API uses `Authorization` plus `X-Press-Team` headers, its API docs warn that some site endpoints may need dashboard-request interpretation after UI refactors, private bench apps require bench-group update plus site update, bench updates support `press-deploy` and bench-specific markers, and SSH needs a generated Frappe Cloud SSH certificate, not only a local private key. Relevant known surfaces: public Frappe ping `/api/method/frappe.ping`; Frappe Cloud API examples `press.api.account.me`, `press.api.site.all`, `press.api.site.get`, `press.api.site.login`; repo-documented mutation surface `press.api.bench.deploy_and_update`; discovered dashboard URL `https://cloud.frappe.io/dashboard/groups/bench-39776/deploys/6g85b2nqj7`; and the failed first API assumption that nested `apps` / `sites` JSON could be stringified, which produced a payload-shape failure rather than deploy proof.

### 3. Won't Accept

- No live, DNS, Stripe, Cloudflare cache/security, Search Console, sitemap submit, or production checkout mutation from this research lane.
- No generic `press-deploy` marker; it can target every applicable auto-deploy bench and is not scoped enough for this recovery.
- No use of stale `bench-39776-000013-f94-virginia` as the staging target; current evidence says staging is `bench-40102` / `bench-40102-000003-f4v`.
- No owner-review-ready claim from app mirror commit, deploy candidate, HTTP 200, local Docker verifier, or `LT_BASE_URL` retarget alone.
- No reuse of `press.api.bench.deploy_and_update` without first proving the current typed payload shape from official docs, dashboard requests, or a sanitized successful request.
- No secrets in docs: do not print API keys, API secrets, cookies, session IDs, SSH private keys, generated SSH certificates, or provider tokens.
- No handoff back to GL as a dashboard checklist if an authenticated provider session/API/SSH route is technically available to the agent.
- No weakening staging proof because recovery jobs made the site Active; the installed app hash, site update/migration, cache, app order, pause/index settings, Product Setup records, and browser evidence still need proof.

### 4. Open To

Research may use the authenticated Frappe Cloud dashboard, current Frappe Cloud API docs, dashboard network requests, and Frappe Cloud SSH only if access is already available and no secrets are printed. The safe recovery path is to confirm staging has no running jobs, target only the current staging bench/site, run the smallest staging-only update path that moves installed `locally_twisted` from `b4b3bf8` to `f236d6d`, run or trigger the staging site update/migrate, clear staging cache, and then prove staging records/browser behavior: `locally_twisted` installed last, `lt_ecommerce_paused=1`, `lt_public_indexing_enabled=0`, `locallytwisted@gmail.com` owner/admin access, `marketing@exploringnotboring.com` website-only `LT Marketing Review Access`, Product Setup/gallery projection records, product page gallery/variant rendering, and no live/DNS/Stripe/Search Console changes. If current provider behavior differs from the stored docs, the research output should update the recovery plan with the exact current dashboard/API evidence and mark older repo claims as superseded.

### 5. Questions

1. What is the current Frappe Cloud dashboard/API flow to update `bench-40102` / `bench-40102-000003-f4v` and then update only `locallytwisted-staging.frappe.cloud` to app mirror `f236d6d`?
2. What sanitized request/response proves the correct typed payload shape for the mutation endpoint, especially if using `press.api.bench.deploy_and_update`?
3. What exact logs or status details explain failed jobs `8vspcanje0` and `63lqkkrppt`, and do they indicate a source/migration problem, payload problem, provider transient, or site-state conflict?
4. Why does staging still show `update_available=true` after recovery: app release not deployed to bench, site update not run, update failed, cache/state lag, or another Frappe Cloud state?
5. What is the least risky staging-only recovery option: dashboard deploy/update, API deploy/update, bench-specific commit marker for current bench, redeploy, or SSH-assisted bench/site commands?
6. How will the agent prove installed app hash and app order on staging without exposing secrets: Frappe Cloud app version dialog/API, authenticated site session, SSH `bench`, or a source-owned verifier?
7. What staging-side verifiers must run after target-hash proof, and which existing local verifiers are invalid as staging proof because they read the local Docker `frontend` database?
8. What provider-auth blocker, if any, truly requires GL: MFA, missing API token, missing dashboard session, missing SSH certificate generation, business approval, or destructive go/no-go?

Sources to verify again before mutation: `workstreams/frappe-cloud-staging-owner-review-2026-05-22.md`, `LT-LAUNCH-RUNBOOK.md`, `ECOMMERCE-SHOP-HANDOFF.md`, `capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`, official Frappe Cloud API docs `https://docs.frappe.io/cloud/api`, updating-a-bench docs `https://docs.frappe.io/cloud/benches/updating_a_bench`, installing-an-app docs `https://docs.frappe.io/cloud/installing-an-app`, and SSH docs `https://docs.frappe.io/cloud/benches/ssh`.

## Worker A Proof Addendum - 2026-05-23T00:23Z

This brief's original installed-hash blocker is now superseded by fresh staging proof. Staging runs `locally_twisted` hash `3e86bc149d6dcc04daa194b740c1733f5c796261`, with app order `frappe, erpnext, payments, webshop, locally_twisted`. Frappe Cloud reports staging `Active`, running jobs `0`, successful migrate job `crn5pskff4`, successful config update `3u20303jfl`, and successful cache clear `eu27r8q4to`. Site config has `lt_ecommerce_paused=1` and `lt_public_indexing_enabled=0`.

The current blocker is no longer code deployment. It is staging data/provisioning:

- `locallytwisted@gmail.com` is missing as a staging `User`.
- `marketing@exploringnotboring.com` is missing as a staging `User`.
- `Item`, `Website Item`, `Website Slideshow`, and `Website Slideshow Item` all return count `0` on staging.
- Authenticated `/shop-items` renders the shop shell, but representative product/category routes return `404`.

Owner ecommerce review remains blocked until a staging-safe provisioning path creates the required human users and product/catalog/gallery records, followed by a rerun of the staging account/product proof.
