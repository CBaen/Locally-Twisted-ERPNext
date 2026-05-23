# Frappe Cloud Release Artifact Template Parity - 2026-05-23

Status: **complete as documentation/template parity only**.

Source commit: `f5e2e91 Update staging release artifact template`.
Documentation parity archive: `5e11003 Document release artifact template
parity`.

This work did not perform provider, staging, live, DNS, Stripe, Search
Console, app mirror, bootstrap, migrate, cache, checkout, or secret-reading
mutation.

2026-05-23 follow-up: the template's `sanitized-payload.json` example now uses
the complete provider site object after the later deploy/update attempt proved
that typed JSON with a name-only `sites[]` row is still incomplete. See
`workstreams/frappe-cloud-staging-app-deploy-closeout-2026-05-23.md` and
`capabilities/failures/frappe-cloud-deploy-site-object-drift.md`.

## Why This Exists

After the post-`ebb7151` release-guard pass, the controller required artifacts
that the packet template did not yet describe. That created a real next-agent
risk: the source guards could be correct while the release packet starter still
encouraged an incomplete or invalid artifact set.

The gap was found by the Gate/Fixer review lane and verified against the
release controller/guard contracts.

## What Changed

Updated:

- `workstreams/release-artifacts/2026-05-23-staging-freeze/TEMPLATE.md`

The template now includes:

- `freeze-reopen-approval.json`
- `app-mirror-sync-plan.json`
- `deploy-completion.json`
- hosted preflight shape with the required `checks` object
- the validation command for `frappe_cloud_deploy_completion_contract.py`
- explicit language that chat approval, commit messages, and hand-shaped
  `ok=true` files are not release proof

## Triad Receipts

- Provider Witness: confirmed the active forensic-freeze lock remains no-go
  for `app_mirror_sync`; current real artifacts are missing for mutation.
- Gate/Fixer: patched the release packet template and pushed `f5e2e91`.
- Recorder: this document and the linked handoff/queue/capability parity pass.

## Verification

Gate/Fixer verification after the template patch:

- `npm run test:release-prevention` passed.
- `git diff --check` passed.
- `main` matched `origin/main` at
  `f5e2e91e576f5aec11beb2c11f8b71df83a603e6`.

Follow-up documentation parity was archived at
`5e11003d5cf8cd0d81e3d8e5acd4087a7d104c24`.

## Current No-Go State

`f5e2e91` is GitHub source/template archive proof only.

It is not:

- a current `freeze-reopen-approval.json`
- a current `app-mirror-sync-plan.json`
- app mirror freshness
- Frappe Cloud deploy/update completion
- hosted bootstrap preflight proof
- staging data/account/product/gallery proof
- owner-review readiness
- live release approval

The active lock remains:

- `release_locks/locally-twisted-staging-forensic-freeze.json`

Current required read-first docs remain:

- `workstreams/frappe-cloud-release-prevention-action-items-2026-05-23.md`
- `workstreams/frappe-cloud-staging-release-failure-forensics-2026-05-23.md`
- `workstreams/release-artifacts/README.md`
- `capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`
- `locally-twisted-queue.md`

## Next Safe Step

If release execution is explicitly reopened, copy the template into a fresh
dated packet and produce real artifacts for that attempt. Do not reuse the
template file itself as release evidence.

The first mutating action remains blocked until the release controller accepts
the current packet's real:

- read receipt
- freeze reopen approval
- app mirror sync plan, for `app_mirror_sync`
- provider snapshot
- triad artifacts
- failure ledger

Downstream actions still require post-sync app mirror freshness, deploy
completion, hosted preflight, and the staging owner-review gate.

## Backlinks

- `workstreams/release-artifacts/2026-05-23-staging-freeze/TEMPLATE.md`
- `workstreams/release-artifacts/README.md`
- `workstreams/frappe-cloud-release-prevention-action-items-2026-05-23.md`
- `workstreams/frappe-cloud-post-ebb7151-staging-readonly-2026-05-23.md`
- `workstreams/frappe-cloud-staging-release-failure-forensics-2026-05-23.md`
- `capabilities/failures/release-controller-churn-after-stop.md`
- `capabilities/failures/artifactless-subagent-release-triad.md`
