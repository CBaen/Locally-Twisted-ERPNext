# LT Staging Reopen Packet - 2026-05-23 - 5edb641

Status: **archive evidence after staging app deploy/update; not authority for
future mutation after commit**.

Source commit:
`5edb641de4a3f09cc6c292904fb70551c87db3df`.

Target:
`locallytwisted-staging.frappe.cloud`.

Purpose:
move the clean source toward staging while preserving the new release gates.

Archive rule:
once this packet is committed, it is proof of the completed
`app_mirror_sync`, `frappe_cloud_deploy`, and read-only hosted preflight
results. It must not be reused to authorize a later bootstrap/import/cache/live
or provider action, because repo `HEAD` will have moved.

## Plain State

The source repo is clean and pushed. The approved app-root mirror sync was
completed from source commit
`5edb641de4a3f09cc6c292904fb70551c87db3df`.

The app-root mirror is now at
`5dd674c5ae9d6b3cb125ecf7ba2dd2e4e65e3831`.

The installed staging app is now also at
`5dd674c5ae9d6b3cb125ecf7ba2dd2e4e65e3831` after Frappe Cloud deploy
`eu92fvbhpp` and site update job `41ftn09ocp` reached `Success`.

The next provider mutation, if approved, is **not deploy/update again by
default**. Current hosted preflight is NO-GO, so the next action must address
the blockers in `hosted-bootstrap-preflight.json` under a fresh approval
artifact. This archive is not owner-review readiness, live release, DNS,
Stripe, Search Console, indexing, checkout unpause, bootstrap, migrate, or
cache clear authority.

## Generated Artifacts

- `read-receipt.json`
- `release-identity-proof.json`
- `failure-ledger.json`
- `app-mirror-sync-plan.json`
- `provider-snapshot.json`
- `app-mirror-freshness-before-sync.json`
- `freeze-reopen-approval.json`
- `app-mirror-sync-result.json`
- `app-mirror-freshness.json`
- `provider-snapshot-post-mirror-sync.json`
- `sanitized-payload.json`
- `deploy-attempt-1-result.json`
- `sanitized-payload-attempt-1.json`
- `deploy-request.json`
- `deploy-request-2.json`
- `deploy-completion.json`
- `hosted-bootstrap-preflight.json`

## Completed Approved Boundary

- GL approved staging-only `app_mirror_sync` from source `5edb641`.
- The release controller passed for `app_mirror_sync`.
- The app-root mirror was synced and pushed from the committed app source.
- Post-sync freshness proof passed.
- Post-sync provider snapshot shows staging is active, paused, not indexing,
  and still needs an update from installed hash
  `181076c239b2d1d3d508a41ac471c71f9d2b5158` to target hash
  `5dd674c5ae9d6b3cb125ecf7ba2dd2e4e65e3831`.
- GL approved staging-only `frappe_cloud_deploy` / deploy-update from app
  mirror hash `5dd674c5ae9d6b3cb125ecf7ba2dd2e4e65e3831`.
- Attempt 1 did not complete because the site object was incomplete; that
  failure class is recorded in `deploy-attempt-1-result.json`.
- Attempt 2 used the full provider site object and completed. Provider deploy
  `eu92fvbhpp` reached `Success`, site job `41ftn09ocp` reached `Success`, and
  staging installed `locally_twisted` app hash now matches
  `5dd674c5ae9d6b3cb125ecf7ba2dd2e4e65e3831`.
- Read-only hosted preflight was run after deploy completion and failed safely.
  It proves the app hash is correct, but blocks bootstrap/import on:
  missing `LT Marketing Review Access`, `Webshop Settings.enable_checkout=0`,
  and missing backup/zero-data proof for destructive catalog seed.

## Needs Before Next Mutation

- fresh bounded approval specifically for hosted preflight and/or any later
  `staging_bootstrap` action;
- controller pass for the next exact action;
- a fix/approved path for the hosted preflight blockers in
  `hosted-bootstrap-preflight.json`;
- GL/provider session availability if Frappe Cloud requires MFA.

## Stop Conditions

- no fresh approval artifact;
- controller blocks;
- deploy/update cannot be completed cleanly;
- Frappe Cloud/GitHub account context is ambiguous beyond the documented
  dual-account model;
- any live/DNS/Stripe/Search Console/checkout action appears in scope.

## After Approved App Mirror Sync

1. Capture post-sync `app-mirror-freshness.json`.
2. Capture a fresh provider snapshot against the post-sync mirror hash.
3. Only then evaluate provider deploy/update.
4. After deploy/update, capture deploy-completion proof.
5. Only then run hosted preflight. **Current result: NO-GO.**
6. Only after hosted preflight passes, evaluate bootstrap/import.
7. Only after bootstrap/import, run the staging owner-review gate.
