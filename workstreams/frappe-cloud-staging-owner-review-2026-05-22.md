# Frappe Cloud Staging Owner Review - 2026-05-22

Status: staging source is deployed to the owner-review Frappe Cloud site with
checkout paused and public indexing disabled. This is **not** live approval and
does not touch DNS, Stripe, Search Console, or the live vanity site.

## Scope

Prepare the ecommerce/Product Setup/gallery release for owner review on
Frappe Cloud staging without touching live checkout, Stripe, DNS, Cloudflare,
Search Console, or live promotion.

This workstream cross-links:

- `LT-LAUNCH-RUNBOOK.md`
- `ECOMMERCE-SHOP-HANDOFF.md`
- `workstreams/ecommerce-audit/product-gallery-restoration-2026-05-22.md`
- `workstreams/ecommerce-audit/owner-product-setup-guard-closeout-2026-05-22.md`
- `capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`
- `capabilities/failures/frappe-cloud-app-mirror-release-scope-drift.md`
- `capabilities/failures/frappe-cloud-api-payload-shape-drift.md`
- `capabilities/failures/frappe-cloud-release-site-migration-drift.md`
- `capabilities/failures/frappe-cloud-staging-website-settings-drift.md`

## Current Evidence

| Surface | Evidence |
|---|---|
| Save state | `savepoint/lt-staging-recovery-20260522-173929` was created before the recovery push/retry chain |
| Final full source repo | `2ca1b85 Ensure LT access roles before permission sync`, pushed to `origin/main` |
| Final app-root mirror | `3e86bc1 Ensure LT access roles before permission sync`, pushed to `CBaen/Locally-Twisted-Frappe-App` |
| Final installed staging app hash | `3e86bc149d6dcc04daa194b740c1733f5c796261` |
| Staging provider mapping | `locallytwisted-staging.frappe.cloud` is on Frappe Cloud bench group `bench-40102` / bench `bench-40102-000003-f4v` |
| Live provider mapping | Live/vanity remains separate on bench group `bench-39776` / bench `bench-39776-000015-f94v` |
| Final staging migration | Update Site Migrate job `crn5pskff4` succeeded |
| Final staging config/cache | Update Site Configuration job `3u20303jfl` succeeded; Clear Cache job `eu27r8q4to` succeeded |
| Final staging site state | Site is `Active` with `0` running jobs after the successful deploy/config/cache chain |
| Ecommerce pause | Staging has `lt_ecommerce_paused=true`; guest shop/product routes should remain paused unless owner/backend session bypass is intentionally used for review |
| Public indexing | Staging has `lt_public_indexing_enabled=false`; do not submit or index staging |
| Live boundary | No live/DNS/Stripe/Search Console mutation is part of this staging recovery pass |

## Failure Chain

The first API release failure was caused by a bad Frappe Cloud API payload:
nested `apps` and `sites` were sent as stringified JSON values instead of typed
JSON objects. Frappe Cloud accepted the request shape far enough to create a
release pipeline, then failed with:

```text
'str' object has no attribute 'get'
```

Release Pipeline: `6podv9kvbn`.

The corrected typed JSON deploy reached staging site update/migrate, then
failed because the LT public-access migration guard treated Frappe's temporary
Portal Settings migration value as hostile drift:

```text
frappe.exceptions.PermissionError:
Portal Settings.default_portal_home must stay 'me' for the LT account home.
```

Failed site update/migrate jobs: `8vspcanje0`, `63lqkkrppt`.
Recovery jobs succeeded. Source fix: `0f6fcad Fix staging portal migration
guard`. App mirror fix: `9ddcb45 Allow portal guard repair during migrate`.

The next deploy reached migration again and failed because the contact-intake
permission sync referenced LT roles before ensuring they existed on the staging
site:

```text
frappe.exceptions.LinkValidationError:
Could not find Row #2: Role: LT Owner Access,
Row #3: Role: LT Manager Access
```

Failed site update/migrate job: `6itfpob0ra`. Recovery job `cjifa26m76`
succeeded. Source/app mirror fix: `2ca1b85` / `3e86bc1 Ensure LT access roles
before permission sync`.

## Triad Decision

The original `press-deploy` marker idea was blocked because the provider mapping
was stale. API inventory later proved current staging is `bench-40102` /
`bench-40102-000003-f4v`, while live remains on `bench-39776` /
`bench-39776-000015-f94v`.

Current decision: staging release recovery has crossed the provider deploy and
site migration gate for app hash
`3e86bc149d6dcc04daa194b740c1733f5c796261`. Owner review is still gated by
staging-specific account, route, gallery, Product Setup, browser, and security
proof. Do not collapse "staging deployed" into "live ready."

Official Frappe Cloud docs checked on 2026-05-22:

- Updating a bench supports `press-deploy` markers and specific bench markers.
- Private bench app updates require bench deploy plus site update.
- SSH needs a generated Frappe Cloud SSH certificate; the local private key
  alone is not enough.

## Owner-Review Next Gates

Run these as staging-specific proof before handing the URL to Jeff as review
ready:

1. Prove the installed staging app hash is still
   `3e86bc149d6dcc04daa194b740c1733f5c796261` and `locally_twisted` remains
   installed last.
2. Prove `lt_ecommerce_paused=true` and `lt_public_indexing_enabled=false`
   after cache clear.
3. Prove `locallytwisted@gmail.com` exists with intended backend/owner access.
4. Prove `marketing@exploringnotboring.com` exists with review-only access and
   no unintended Desk/product-edit access.
5. Prove logged-in owner/backend review can see shop/products while guest shop
   remains safely paused.
6. Prove Product Setup/gallery projection exists in staging records and product
   pages render the restored gallery behavior.
7. Run staging HTTP/browser smoke for `/`, `/contact`, `/login`,
   `/shop-items`, representative category pages, and representative product
   pages.
8. Run the full release/security suite needed before any live promotion
   discussion; keep Stripe/live checkout as a separate blocked gate.

## Commands Already Run

Local hard gates were run before the source/app mirror recovery chain:

```powershell
python scripts/verify/frappe_cloud_preflight.py
python scripts/verify/human_access_silo_matrix.py
python scripts/verify/marketing_review_access_boundary.py
npm run test:owner-product-safety
npm run test:ecommerce-full
python scripts/verify/public_access_guard_contract.py
```

The second migration fix was locally smoke-tested with:

```powershell
python -m py_compile apps\locally_twisted\locally_twisted\seed\sync_contact_intake_backend.py
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.seed.sync_contact_intake_backend.execute
```

App mirror sync used a temporary clone at:

```text
C:\Users\baenb\agent-worktrees\builtbycameron-lt\app-mirror-sync-20260522-portalfix
```

That mirror was pushed through `3e86bc1`.

## Boundaries

Do not touch live, DNS, Stripe, Search Console, or production indexing from this
workstream. Do not run a generic `press-deploy` marker. Do not call owner review
complete until the staging-specific gates above pass. Do not call live ready
until staging approval plus live release/security/payment gates pass.
