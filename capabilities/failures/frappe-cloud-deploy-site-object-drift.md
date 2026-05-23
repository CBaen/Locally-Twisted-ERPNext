---
name: Frappe Cloud deploy site object drift
type: failure
failure_kind: release_gate_gap
schema_version: 0.1
date_discovered: 2026-05-23
last_updated: 2026-05-23
status: guarded
scope: project
owner_context: Locally Twisted Frappe Cloud staging deploy/update
related_capabilities:
  - ../recipes/frappe-cloud-cloudflare-stripe-launch-gate.md
related_failures:
  - frappe-cloud-api-payload-shape-drift.md
  - frappe-cloud-release-site-migration-drift.md
  - staging-proof-surface-conflation.md
tags:
  - locally-twisted
  - frappe-cloud
  - provider-api
  - staging
  - payload-shape
  - site-object
  - fail-loud
---

# Failure Recipe: Frappe Cloud Deploy Site Object Drift

## Symptom

A Frappe Cloud deploy/update request uses real `application/json` with typed
`apps` and `sites` arrays, but the staging site does not update because the
`sites[]` row only contains the site `name`.

## Trigger Conditions

- The release agent builds a sanitized deploy/update payload by hand.
- The agent copies a minimal site object from an older packet or chat.
- The payload contract checks JSON type shape but not provider-required site
  fields.
- The release controller treats request validation or a transient pipeline as
  enough to retry without classifying the provider state.

## Known Instances

| Date | Project | Surface | Action being taken | Bad outcome | Evidence | Guard state | Status |
|---|---|---|---|---|---|---|---|
| 2026-05-23 | Locally Twisted | Frappe Cloud staging deploy/update | Deploy app mirror hash `5dd674c5ae9d6b3cb125ecf7ba2dd2e4e65e3831` to `locallytwisted-staging.frappe.cloud` | Attempt 1 used typed JSON but `sites` contained only `{name}`; staging installed app hash remained `181076c239b2d1d3d508a41ac471c71f9d2b5158` | `workstreams/release-artifacts/2026-05-23-staging-reopen-5edb641-use-now/deploy-attempt-1-result.json`; corrected `sanitized-payload.json`; deploy completion `eu92fvbhpp` / site job `41ftn09ocp` | payload contract hardened to require complete site object | guarded |

## Root Pattern

"Typed JSON" is necessary but not sufficient. For the Frappe Cloud Press
deploy/update path, the site row must carry the complete provider site object
used by the current site update code.

## Why It Seemed Reasonable At The Time

The previous failure was caused by stringified nested JSON. Once the payload
used real arrays and objects, `{name}` looked like enough site identity. The
provider source showed that the update row also reads `server`, `bench`,
`skip_backups`, and `skip_failing_patches`.

## Detection Signals

- A deploy/update payload has `sites: [{"name": "..."}]`.
- A corrected payload is created after a provider attempt instead of before.
- The provider briefly creates work but the installed app hash remains old.
- The local payload contract passes a name-only `sites[]` row.

## Required Guard

Before any `frappe_cloud_deploy` / deploy-update action, validate the sanitized
payload through `scripts/verify/frappe_cloud_payload_contract.py`. Each
`sites[]` row must include:

- `name`
- `server`
- `bench`
- `skip_backups`
- `skip_failing_patches`

Use the current provider `deploy_information.sites` row for the target site.
Do not invent these fields from stale docs.

## Recovery Recipe

1. Stop and archive the failed attempt as a provider payload failure class.
2. Read the current provider site row from Frappe Cloud/Press
   `deploy_information.sites`.
3. Rebuild the sanitized payload with the full site row.
4. Re-run `scripts/verify/frappe_cloud_payload_contract.py --payload-file ...`.
5. Re-run the release controller for the exact approved action.
6. After deploy/update, require `deploy-completion.json` before hosted
   preflight, bootstrap/import, cache, or owner-review claims.

## What Not To Do

- Do not treat `Content-Type: application/json` as full payload correctness.
- Do not send a name-only `sites[]` row for deploy/update.
- Do not patch the payload after a failed attempt without recording the failure
  class and guard.
- Do not move from app hash success to owner-review readiness.

## Cross-links

- `../../workstreams/frappe-cloud-staging-app-deploy-closeout-2026-05-23.md`
- `../../workstreams/release-artifacts/2026-05-23-staging-reopen-5edb641-use-now/`
- `../recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`
- `frappe-cloud-api-payload-shape-drift.md`
- `frappe-cloud-release-site-migration-drift.md`
- `staging-proof-surface-conflation.md`

## Evidence Quality

Verified from the approved 2026-05-23 staging-only deploy/update packet,
provider snapshot, and post-deploy completion artifact. The guard is local
payload validation; it does not prove future Frappe Cloud provider behavior by
itself.
