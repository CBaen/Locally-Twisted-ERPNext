# Frappe Cloud Staging Failure Evidence Summary

Date boundary: 2026-05-22 America/Denver / 2026-05-23 UTC.

Scope: staging repair research only. No live, DNS, Stripe, Cloudflare mutation, Search Console, checkout exposure, secret printing, or production promotion.

2026-05-23 supersession: this evidence summary is historical. It is not current
release authority and does not authorize the "next safe recovery path" below as
an execution plan. Release execution is frozen until the prevention action list
is implemented:
`../../workstreams/frappe-cloud-release-prevention-action-items-2026-05-23.md`.
Forensics source:
`../../workstreams/frappe-cloud-staging-release-failure-forensics-2026-05-23.md`.

## Current Evidence Chain

### Worker A Staging/Account Proof Update - 2026-05-23T00:23Z

The prior installed-hash blocker is superseded. Frappe Cloud staging now runs the latest app mirror hash, and the latest migration/cache/config jobs are successful. The current blocker is staging data/provisioning: the site has no catalog records and lacks the required owner/marketing users.

| Surface | Current Evidence |
|---|---|
| Staging status | `Active` |
| Staging bench group | `bench-40102` |
| Staging server | `f4-virginia.frappe.cloud` |
| Installed app order | `frappe, erpnext, payments, webshop, locally_twisted` |
| Installed `locally_twisted` hash | `3e86bc149d6dcc04daa194b740c1733f5c796261` |
| Running jobs | `0` |
| Latest successful migrate | `crn5pskff4` / `Update Site Migrate` / `Success` |
| Latest config update | `3u20303jfl` / `Update Site Configuration` / `Success` |
| Latest cache clear | `eu27r8q4to` / `Clear Cache` / `Success` |
| `lt_ecommerce_paused` | `1` |
| `lt_public_indexing_enabled` | `0` |
| Staging auth bootstrap | Frappe Cloud `site.login` then `/app?sid=[redacted]`; confirmed `Administrator` |
| Required owner user | `locallytwisted@gmail.com` missing: `404 Not Found` |
| Required marketing user | `marketing@exploringnotboring.com` missing: `404 Not Found` |
| `Item` count | `0` |
| `Website Item` count | `0` |
| `Website Slideshow` count | `0` |
| `Website Slideshow Item` count | `0` |
| Authenticated shop shell | `/shop-items` returns `200` |
| Authenticated product/category routes | Mickey Mouse Bouquet and Columns return `404` because data/routes are missing |
| Public ecommerce pause | Guest `/shop-items` and product route redirect to `/ready-to-order-paused` |
| Indexing note | Pages checked emit `noindex`, but `/robots.txt` allows crawling and `/sitemap.xml` still lists staging URLs |

Current decision: **code deployment recovered; owner ecommerce review still BLOCKED until staging data and required users are provisioned.**

| Surface | Evidence |
|---|---|
| Source repo | `2ee28da Harden product galleries and release gates`, pushed to `origin/main` |
| App-root mirror | `f236d6d Sync app from LT source 2ee28da`, pushed to `CBaen/Locally-Twisted-Frappe-App` |
| Previous proven app mirror | `b4b3bf8 Run contact intake schema sync on install` |
| Staging host | `https://locallytwisted-staging.frappe.cloud/` returns HTTP 200 from Frappe Cloud per current repo docs |
| Current staging mapping | Bench group `bench-40102`; bench `bench-40102-000003-f4v` |
| Current live mapping | Bench group `bench-39776`; bench `bench-39776-000015-f94v` |
| Stale avoided target | `bench-39776-000013-f94-virginia`; do not use as current staging target |
| Local hard gates | `frappe_cloud_preflight.py`, `human_access_silo_matrix.py`, `marketing_review_access_boundary.py`, `npm run test:owner-product-safety`, `npm run test:ecommerce-full` passed before staging mutation |
| Failed provider jobs | Staging site update/migrate jobs `8vspcanje0` and `63lqkkrppt` failed; recovery jobs later succeeded |
| Superseded blocker | Earlier staging was `Active` with old installed `locally_twisted` hash `b4b3bf8`; Worker A proof now shows app hash `3e86bc149d6dcc04daa194b740c1733f5c796261` |
| Current blocker | Staging has latest app code but zero catalog records and missing required owner/marketing users |
| First failed API assumption | Nested `apps` / `sites` JSON was stringified; this caused a payload-shape failure and was not deploy proof |
| Auth/tooling evidence | Repo docs record no local API token, no generated SSH certificate, and unauthenticated dashboard/API state as `Guest` / `403` in the prior search |

## API And Dashboard Surfaces Mentioned

- Public route health probe: `/api/method/frappe.ping`.
- Official Frappe Cloud API auth check example: `press.api.account.me`.
- Official Frappe Cloud site API examples: `press.api.site.all`, `press.api.site.get`, `press.api.site.login`.
- Repo-documented mutation surface: `press.api.bench.deploy_and_update`; exact accepted payload must be re-proven before reuse.
- Dashboard evidence URL found in prior search: `https://cloud.frappe.io/dashboard/groups/bench-39776/deploys/6g85b2nqj7`; treat it as historical evidence, not current staging target proof.

## Failed Assumptions

- Stale bench history is not provider mapping proof.
- App mirror commit `f236d6d` is not staging proof.
- A Frappe Cloud HTTP 200 is not installed-hash proof.
- Active site state after recovery is not site update/migration success.
- Generic `press-deploy` is not staging-safe for this recovery.
- `LT_BASE_URL=https://locallytwisted-staging.frappe.cloud` does not turn local Docker database verifiers into staging database proof.
- Current Frappe Cloud behavior cannot be assumed from model memory; official docs and dashboard/API behavior must be checked live.

## Next Safe Recovery Path

1. Confirm the provider session/API path is authenticated without printing secrets.
2. Confirm staging still maps to `bench-40102` / `bench-40102-000003-f4v` and has no running jobs.
3. Capture sanitized current provider state: installed app hash, update availability, bench/site mapping, failed job summaries, and app order if available.
4. Choose the smallest staging-only update path: dashboard deploy/update, authenticated API, current-bench-specific marker, redeploy, or SSH-assisted commands.
5. Before mutation, capture sanitized payload shape or dashboard action proof.
6. Done: installed `locally_twisted` is now `3e86bc149d6dcc04daa194b740c1733f5c796261`.
7. Done: site update/migration succeeded, cache cleared, app order is correct, `lt_ecommerce_paused=1`, and `lt_public_indexing_enabled=0`.
8. Blocked: staging-specific owner/access/Product Setup/gallery/browser checks fail because users and product data are missing.
9. Still required: provision staging site data/users through the approved staging-safe setup path, then rerun Worker A proof.
10. Record that live, DNS, Stripe, and Search Console remained untouched.
