# Frappe Cloud Hosted Preflight Guard Refresh - 2026-05-23

Status: **implemented locally; staging remains no-go under forensic-freeze**.

This handoff covers the guard/documentation refresh after the app-root mirror
freshness no-go packet. It did not perform app mirror sync, provider deploy,
site update, staging bootstrap/import, cache clear, live release, DNS, Stripe,
Search Console, production indexing, or checkout unpause.

## Why This Exists

The read-only staging owner-review gate can report the last durable bootstrap
status, but that is not the same thing as a fresh non-mutating hosted preflight
from the current staging target. The previous failed bootstrap status remains
useful forensic evidence; it must not be used as permission to bootstrap again.

The new hard boundary is:

1. Reviewed source is archived.
2. Forensic-freeze is explicitly reopened.
3. App-root mirror is synced from reviewed source through the release path.
4. `app-mirror-freshness.json` proves the mirror contains the hosted preflight
   files.
5. `hosted-bootstrap-preflight.json` proves the actual staging app exposes and
   passes `preflight_staging_owner_review_bootstrap`.
6. Only then can a future controller consider staging bootstrap/import.

## Source Changes

- Added `scripts/verify/staging_owner_review_hosted_preflight.py`.
- Added `npm run test:staging-owner-review-hosted-preflight`.
- Added the hosted-preflight self-test to `npm run test:release-prevention`.
- Added hosted-preflight artifact validation to
  `scripts/release/release_guard_common.py`.
- Required `--hosted-bootstrap-preflight` before the release controller can
  permit a future `staging_bootstrap` action.
- Expanded `release_locks/locally-twisted-staging-forensic-freeze.json` reopen
  requirements with a fresh hosted bootstrap preflight artifact.

## Evidence Packet

Current read-only packet:

- `workstreams/release-artifacts/2026-05-23-staging-reopen-readiness-refresh/`

Post-guard current-state packet:

- `workstreams/release-artifacts/2026-05-23-staging-reopen-post-ebb7151-readonly/`
  rechecked staging after source commit `ebb7151` and is still no-go. The
  app-root mirror/deployed hash remains `181076c239b2d1d3d508a41ac471c71f9d2b5158`,
  mirror freshness is `ok=false`, hosted preflight returns HTTP `417`,
  owner-review data is still zero/missing, and required owner/marketing users
  are absent.

Important artifacts:

- `app-mirror-freshness.json` is no-go because the app-root mirror is still
  missing `locally_twisted/staging_owner_review_preflight.py`.
- `hosted-bootstrap-preflight.json` is no-go because staging returns HTTP `417`
  for `preflight_staging_owner_review_bootstrap`.
- `provider-snapshot.json` is read-only proof that staging is Active, paused,
  noindex, has no running jobs, and is still on app hash
  `181076c239b2d1d3d508a41ac471c71f9d2b5158`.
- `staging-owner-review-gate-readonly.json` is no-go because catalog/Product
  Setup/gallery rows are zero, owner/marketing users are missing, routes return
  `404`, and the last bootstrap status is a prior failed Standard Report
  developer-mode attempt.

## Verification

Run from repo root:

```powershell
python -m py_compile scripts\verify\staging_owner_review_hosted_preflight.py scripts\release\release_guard_common.py scripts\release\frappe_cloud_release_controller.py scripts\verify\release_lock_contract.py scripts\verify\release_controller_contract.py
npm run test:release-prevention
python scripts\verify\verifier_cli_contract.py
```

## Next Safe Step

Do not mutate staging from this packet. The next agent must first run the local
release-prevention suite, verify the active lock, and get explicit reopen
approval. After that, the controlled order is app mirror sync from reviewed
source, fresh app-mirror freshness proof, fresh provider snapshot, fresh hosted
preflight proof, then staged bootstrap/import only if every gate passes.
