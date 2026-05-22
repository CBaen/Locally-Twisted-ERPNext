# Frappe Cloud Staging Owner Review - 2026-05-22

Status: source and app mirror are archived; Frappe Cloud staging owner review
is still blocked because staging is Active but still running the old
`locally_twisted` app hash.

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
| Current staging provider mapping | Staging is on Frappe Cloud bench group `bench-40102` / bench `bench-40102-000003-f4v` |
| Current live provider mapping | Live remains on bench group `bench-39776` / bench `bench-39776-000015-f94v` |
| First API issue | Initial API payload failed because nested JSON was stringified; this was a payload-shape error, not proof of deploy success |
| Deploy/update attempt | Corrected staging bench deploy was attempted; site update/migrate jobs `8vspcanje0` and `63lqkkrppt` failed, with recovery jobs succeeding |
| Latest provider check | Staging is `Active`, has `0` running jobs, `update_available=true`, and installed `locally_twisted` hash is still old `b4b3bf8`, not target `f236d6d` |
| Owner review status | Blocked: staging is stable after recovery, but it has not picked up the target app mirror commit |

## Triad Decision

The triad first reviewed whether to trigger Frappe Cloud with an app-mirror
empty commit containing `press-deploy-bench-39776-000013-f94-virginia`.

- Sartre: conditional pass if `bench-39776-000013-f94-virginia` is proven to
  be staging-only; reject plain `press-deploy`.
- Peirce: block until current provider evidence proves that bench/site mapping.
- Controller decision: no marker deploy yet. The stricter release gate wins.

Provider API proof later showed the prior staging-bench assumption was stale:
current staging is `bench-40102` / `bench-40102-000003-f4v`, while live remains
`bench-39776` / `bench-39776-000015-f94v`. This confirms the earlier block was
correct: repo history was not enough evidence for a provider mutation.

Current decision: owner review remains blocked. Staging is Active with no
running jobs after recovery, but `update_available=true` and the installed
`locally_twisted` app hash is still old `b4b3bf8`, not target `f236d6d`.

Official Frappe Cloud docs checked on 2026-05-22:

- Updating a bench supports `press-deploy` markers and specific bench markers.
- Private bench app updates require bench deploy plus site update.
- SSH needs a generated Frappe Cloud SSH certificate; the local private key
  alone is not enough.

## Next Safe Step

Recover staging to the target app hash without touching live:

1. Treat `bench-40102` / `bench-40102-000003-f4v` as the current staging
   target, not the older `bench-39776-000013-f94-virginia` value.
2. Confirm no running staging jobs before the next action.
3. Use the Frappe Cloud staging-only update path for
   `locallytwisted-staging.frappe.cloud`; do not use generic `press-deploy`.
4. After any update attempt, prove the installed `locally_twisted` hash changes
   from `b4b3bf8` to target `f236d6d`.

After target hash proof, deploy/update staging only, then prove:

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
