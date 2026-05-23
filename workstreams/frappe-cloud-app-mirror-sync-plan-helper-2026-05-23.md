# Frappe Cloud App Mirror Sync Plan Helper - 2026-05-23

Status: **implemented local/offline artifact helper; no provider or app mirror
mutation**.

Archive commit: `849d8c2d88cc868990cab124af02648e493b49d1`.
Documentation parity closeout:
`frappe-cloud-doc-parity-849d8c2-2026-05-23.md`.

## Scope

This work adds a local producer/validator for the required pre-sync
`app-mirror-sync-plan.json` artifact. It removes another hand-copy step from a
future approved staging reopen packet.

The helper is:

`scripts/release/app_mirror_sync_plan_artifact.py`

The verifier is:

`scripts/verify/app_mirror_sync_plan_artifact_contract.py`

Package gate:

```powershell
npm run test:app-mirror-sync-plan
```

It is also included in:

```powershell
npm run test:release-prevention
```

## Contract

The helper can write a controller-consumable `app-mirror-sync-plan.json` only
with:

- `--write`
- `--output ...\app-mirror-sync-plan.json`
- `--rollback-hash <current deployed/staging rollback hash>`
- `--reviewed-source`

It binds the plan to the current repo `HEAD`, the staging target
`locallytwisted-staging.frappe.cloud`, the LT app-root mirror URL, the required
hosted-preflight source files, and post-sync `app-mirror-freshness.json`.
The mirror URL is pinned exactly to
`https://github.com/CBaen/Locally-Twisted-Frappe-App.git`, mirror ref is pinned
to `main`, final writes must stay under `workstreams/release-artifacts/`, and
writes refuse dirty release guard/source files so an artifact cannot claim a
committed source while relying on uncommitted release behavior.

The helper proves:

- `provider_mutation_executed: false`
- `app_mirror_sync_executed: false`
- `reviewed_source: true`
- `no_provider_deploy_until_post_sync_freshness: true`

## Boundaries

- No app-root mirror push.
- No Frappe Cloud call.
- No provider deploy/update, provider poll, migrate, cache clear, bootstrap,
  import, user creation, indexing, checkout unpause, live release, DNS, Stripe,
  or Search Console mutation.
- No secrets, tokens, session IDs, credential reads, raw provider logs, or
  customer records.
- No owner-review readiness claim.
- No forensic-freeze reopen by itself.

A valid sync plan is still not enough for `app_mirror_sync`. The release
controller still requires a current valid `freeze-reopen-approval.json`, read
receipt, provider snapshot, failure ledger, artifact-owned triad files, and
cross-artifact chain consistency.

## Fresh Read-Only State

Fresh checks during this pass, with no mutation, confirmed staging remains
**NO-GO** for owner review:

- app mirror freshness still fails for source `0efad50`; mirror hash remains
  `181076c239b2d1d3d508a41ac471c71f9d2b5158`;
- hosted preflight still fails HTTP `417` because staging lacks
  `preflight_staging_owner_review_bootstrap`;
- provider snapshot is read-only pass: staging is Active, app order is correct,
  no running jobs, ecommerce paused, public indexing disabled;
- owner-review gate still fails: product/catalog/Product Setup/gallery counts
  are zero, required owner/marketing users are missing, and representative
  product/category routes return `404`;
- controller still blocks `app_mirror_sync` before provider mutation because
  `freeze-reopen-approval.json` is missing.

The fresh artifacts from this pass were written only under `.tmp/` and are not
release-packet authority.

## Witness Review

Intent/Safety Witness `019e53f6-d03f-76c3-af87-f6734e4f4923` confirmed no
staging mutation can proceed without a fresh, current-HEAD
`freeze-reopen-approval.json`.

Technical/Reality Witness `019e53f6-ea9f-71b0-9365-79e9dfc5dce1` confirmed
staging is not owner-review ready and identified app mirror freshness as the
hard current blocker.

## Cross-References

- LT handoff: `../CODING-HANDOFF.md`
- Ecommerce handoff: `../ECOMMERCE-SHOP-HANDOFF.md`
- Release artifacts README: `release-artifacts/README.md`
- Release prevention action list:
  `frappe-cloud-release-prevention-action-items-2026-05-23.md`
- LT capability recipe:
  `../capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`
- Agency decision: `../../../built-by-cameron-decisions.md`
- Agency lesson: `../../../lessons-learned.md`

## Verification

- `python -m py_compile scripts\release\app_mirror_sync_plan_artifact.py scripts\verify\app_mirror_sync_plan_artifact_contract.py`
- `python scripts\verify\app_mirror_sync_plan_artifact_contract.py`
- `npm run test:app-mirror-sync-plan`
- `npm run test:release-prevention`
- `python scripts\verify\verifier_cli_contract.py`
- `git diff --check`
