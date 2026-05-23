# Frappe Cloud Release Artifact Chain Binding - 2026-05-23

Status: **implemented locally; no provider mutation**.

This handoff records the Gate/Fixer guard hardening added after `5e11003`.
It does not approve or perform app mirror sync, Frappe Cloud deploy/update,
staging bootstrap, site migrate, cache clear, live release, DNS, Stripe,
Search Console, production indexing, checkout unpause, or secret reading.

## Why This Exists

The release packet contract already required separate artifacts for approval,
payload, app mirror freshness, provider snapshot, deploy completion, and hosted
preflight. The remaining risk was artifact mixing: a future packet could use a
fresh approval with a stale sync plan, a payload pointing at a different app
hash than the app mirror/provider snapshot, or a deploy/preflight artifact from
another release attempt.

## What Changed

Updated:

- `scripts/release/release_guard_common.py`
- `scripts/release/frappe_cloud_release_controller.py`
- `scripts/verify/release_controller_contract.py`
- `scripts/README.md`

Added release-chain validation in the local controller path:

- freeze-reopen approval `source_commit` must match current repo `HEAD`
- app mirror sync plan `source_commit` must match current repo `HEAD`
- app mirror freshness `source_commit` must match current repo `HEAD`
- approval, sync plan, and mirror freshness source commits must agree when
  supplied together
- app mirror sync plan rollback hash must match provider snapshot rollback
  hash when both are supplied
- deploy/update payload `locally_twisted` app hash must match app mirror
  freshness and provider snapshot target hash when supplied
- payload sites must include the provider snapshot site
- deploy completion hash must match provider/mirror artifacts
- hosted preflight hash must match deploy completion hash

For `app_mirror_sync`, the controller still does not require post-sync mirror
freshness before sync. It validates the pre-sync packet chain it can know
before the mutation.

## Verification

Passed:

```powershell
python -m py_compile scripts\release\release_guard_common.py scripts\release\frappe_cloud_release_controller.py scripts\verify\release_controller_contract.py
python scripts\verify\release_controller_contract.py
npm run test:release-prevention
```

## Current Boundary

This is local prevention architecture only. Provider Witness rechecked current
state after `5e11003` and found the app-root mirror still at
`181076c239b2d1d3d508a41ac471c71f9d2b5158`, mirror freshness still no-go, and
`app_mirror_sync` still blocked by missing `freeze-reopen-approval.json`.

Do not create `freeze-reopen-approval.json` from general goal context or chat
momentum. It must be a fresh artifact-bound approval that passes the release
controller.

## Backlinks

- `workstreams/frappe-cloud-doc-head-correction-2026-05-23.md`
- `workstreams/frappe-cloud-release-artifact-template-parity-2026-05-23.md`
- `workstreams/frappe-cloud-release-prevention-action-items-2026-05-23.md`
- `workstreams/frappe-cloud-staging-release-failure-forensics-2026-05-23.md`
- `capabilities/failures/release-controller-churn-after-stop.md`
