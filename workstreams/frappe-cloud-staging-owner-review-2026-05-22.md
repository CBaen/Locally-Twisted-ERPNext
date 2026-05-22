# Frappe Cloud Staging Owner Review - 2026-05-22

Status: source and app mirror prepared; staging deploy/update is blocked on
current Frappe Cloud bench/site mapping proof.

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
- `capabilities/failures/frappe-cloud-staging-website-settings-drift.md`

## Current Evidence

| Surface | Evidence |
|---|---|
| Full source repo | `2ee28da Harden product galleries and release gates`, pushed to `origin/main` |
| App-root mirror | `f236d6d Sync app from LT source 2ee28da`, pushed to `CBaen/Locally-Twisted-Frappe-App` |
| Previous app mirror | `b4b3bf8 Run contact intake schema sync on install` |
| Mirror scope | Broad app-root sync from `apps/locally_twisted`; not just the final source commit |
| Local hard gates | `frappe_cloud_preflight.py`, `human_access_silo_matrix.py`, `marketing_review_access_boundary.py`, `npm run test:owner-product-safety`, and `npm run test:ecommerce-full` passed after the source push |
| Staging host probe | `https://locallytwisted-staging.frappe.cloud/` returns HTTP 200 from Frappe Cloud |
| Staging stale signals | `/robots.txt` is blank; product routes still redirect to `ready-to-order-paused`; product-gallery staging proof is absent |
| Provider access | No Frappe Cloud CLI/env vars found; no SSH certificate present; raw SSH with the local key returned `Permission denied`; known local dev/admin credentials did not log into staging |

## Triad Decision

The triad reviewed whether to trigger Frappe Cloud with an app-mirror empty
commit containing `press-deploy-bench-39776-000013-f94-virginia`.

- Sartre: conditional pass if `bench-39776-000013-f94-virginia` is proven to
  be staging-only; reject plain `press-deploy`.
- Peirce: block until current provider evidence proves that bench/site mapping.
- Controller decision: no marker deploy yet. The stricter release gate wins.

Reason: repo history strongly suggests `bench-39776-000013-f94-virginia` was
the source/staging bench and `bench-39776-000015-f94v` was the live/destination
bench, but provider state can drift. A targeted marker is still a provider
mutation and must not run until the current Frappe Cloud dashboard/API/SSH view
proves no live/custom-domain site sits on the target bench.

Official Frappe Cloud docs checked on 2026-05-22:

- Updating a bench supports `press-deploy` markers and specific bench markers.
- Private bench app updates require bench deploy plus site update.
- SSH needs a generated Frappe Cloud SSH certificate; the local private key
  alone is not enough.

## Next Safe Step

Prove provider mapping before any deploy trigger:

1. Confirm `https://locallytwisted-staging.frappe.cloud` is on
   `bench-39776-000013-f94-virginia`.
2. Confirm `https://locallytwisted.com` and
   `https://locallytwisted.v.frappe.cloud` are on
   `bench-39776-000015-f94v`.
3. Confirm no live/custom-domain/customer-facing site is attached to
   `bench-39776-000013-f94-virginia`.
4. Confirm Frappe Cloud accepts the full bench identifier for targeted
   `press-deploy-bench-39776-000013-f94-virginia`, or use dashboard deploy and
   update with the staging site explicitly selected.

After that proof, deploy/update staging only, then prove:

- staging bench deploy succeeded;
- staging site update/migrate succeeded;
- staging cache clear succeeded;
- `locally_twisted` remains installed last;
- `lt_ecommerce_paused=1`;
- `lt_public_indexing_enabled=0`;
- `locallytwisted@gmail.com` owner/admin access exists;
- `marketing@exploringnotboring.com` is website-only with exactly
  `LT Marketing Review Access`;
- Product Setup/gallery projection exists in staging records;
- staging product pages render galleries and variant media correctly;
- live/DNS/Stripe/Search Console remain untouched.

## Commands Already Run

```powershell
python scripts/verify/frappe_cloud_preflight.py
python scripts/verify/human_access_silo_matrix.py
python scripts/verify/marketing_review_access_boundary.py
npm run test:owner-product-safety
npm run test:ecommerce-full
```

App mirror sync used a temporary clone at:

```text
C:\Users\baenb\agent-worktrees\builtbycameron-lt\app-mirror-sync-20260522
```

That clone was pushed clean at `f236d6d` and should be deleted after this
workstream/source docs commit is safely archived.

## Boundaries

Do not call this staging-ready yet. Do not run a generic `press-deploy` marker.
Do not run a targeted marker until the current provider mapping is proven. Do
not submit Search Console or index staging. Do not open live checkout or live
Stripe.
