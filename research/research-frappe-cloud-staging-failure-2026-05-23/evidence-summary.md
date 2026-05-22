# Frappe Cloud Staging Failure Evidence Summary

Date boundary: 2026-05-22 America/Denver / 2026-05-23 UTC.

Scope: staging repair research only. No live, DNS, Stripe, Cloudflare mutation, Search Console, checkout exposure, secret printing, or production promotion.

## Current Evidence Chain

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
| Latest blocker | Staging is `Active`, has `0` running jobs, `update_available=true`, and installed `locally_twisted` hash is still old `b4b3bf8`, not target `f236d6d` |
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
6. After mutation, prove the installed `locally_twisted` hash is `f236d6d`.
7. Prove site update/migration succeeded, cache cleared, app order is correct, `lt_ecommerce_paused=1`, and `lt_public_indexing_enabled=0`.
8. Run staging-specific owner/access/Product Setup/gallery/browser checks.
9. Record that live, DNS, Stripe, and Search Console remained untouched.
