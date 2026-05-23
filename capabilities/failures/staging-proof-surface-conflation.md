---
name: Staging proof surface conflation
type: failure
failure_kind: release_gate_gap
schema_version: 0.1
date_discovered: 2026-05-22
last_updated: 2026-05-23
status: guarded
scope: project
owner_context: Locally Twisted staging, live, GitHub archive, Frappe Cloud, and cache-proof boundaries
related_capabilities:
  - ../recipes/frappe-cloud-cloudflare-stripe-launch-gate.md
  - ../recipes/take-live-coordinated-workflows.md
related_failures:
  - frappe-cloud-api-payload-shape-drift.md
  - frappe-cloud-release-site-migration-drift.md
  - frappe-cloud-permission-role-fixture-order-drift.md
  - release-controller-churn-after-stop.md
tags:
  - locally-twisted
  - staging
  - release
  - github
  - frappe-cloud
  - cache
  - live-boundary
  - fail-loud
---

# Failure Recipe: Staging Proof Surface Conflation

## Symptom

An agent says staging is ready, owner-ready, or release-ready because one layer
passed, while another required layer is still unproved. Typical false bridges:
local tests to staging proof, GitHub push to Frappe Cloud install, app mirror
hash to site migration, site status to cache/runtime proof, or staging proof to
live readiness.

## Trigger Conditions

- The same task includes local fixes, GitHub commits, app mirror sync, Frappe
  Cloud release, cache clear, staging review, and live-prep language.
- The app mirror commit exists, but the Frappe Cloud site has not migrated to
  that hash.
- The Frappe Cloud site is `Active`, but `update_available` remains true or an
  update job failed.
- A verifier hits staging HTTP routes while still reading the local Docker
  `frontend` database.
- A cache clear is skipped or assumed after migration.
- Live/DNS/Stripe/Search Console are mentioned before staging proof is
  separated and recorded.

## Known Instances

| Date | Project | Surface | Bad outcome | Evidence | Guard state | Status |
|---|---|---|---|---|---|---|
| 2026-05-22 | Locally Twisted | Ecommerce staging owner review | Local product/gallery proof, source commits, app mirror push, provider deploy, site update, cache, staging route proof, account proof, and live readiness were discussed as one blended release path | Coordination board and handoff records separated local-main, GitHub archive, app mirror, staging gate, and live-release gate; Frappe Cloud recovery showed why app hash, site update/migrate, cache clear, and route proof must each be terminal before owner-ready language | proof-surface checklist added to failure layer | guarded |
| 2026-05-23 | Locally Twisted | Frappe Cloud staging owner review | Provider/app hash success and bootstrap attempts still did not equal owner-review readiness because staging had zero catalog/shop/gallery rows and missing required users; the release process itself was frozen | `../../workstreams/frappe-cloud-staging-release-failure-forensics-2026-05-23.md`; `../../workstreams/frappe-cloud-release-prevention-action-items-2026-05-23.md` | owner-review gate exists; release lock/action items still required | open |

## Root Pattern

Each layer proves only itself:

- Local tests prove the local checkout and local ERPNext database.
- A GitHub push archives source; it does not deploy Frappe Cloud.
- An app mirror commit gives Frappe Cloud something to install; it does not
  prove the site updated.
- A successful Frappe Cloud deploy candidate proves the app artifact; it does
  not prove site migration.
- A successful site update/migrate proves schema and patches applied; it does
  not prove cache/runtime/routes/accounts.
- A cache clear proves refresh was requested; it does not prove owner workflows.
- Staging proof proves staging; it is not live, DNS, Stripe, or Search Console
  approval.

## Detection Signals

- Status text uses "ready" without naming which layer is ready.
- A route verifier has a staging `LT_BASE_URL` but still shells into local
  Docker for database checks.
- The installed app hash is old while the target app mirror hash is current.
- `Active` site status is quoted without update job, cache, and route evidence.
- A live or Search Console next step appears before staging account proof.

## Required Guard

Every LT release/staging note must name the proven layer explicitly:

1. local source/test proof;
2. GitHub archive proof;
3. app mirror proof;
4. Frappe Cloud deploy-candidate proof;
5. site update/migrate proof;
6. site cache/config proof;
7. staging route/browser proof;
8. staging account/business-workflow proof;
9. live/DNS/Stripe/Search Console proof, only when explicitly approved.

Do not let one layer's success borrow another layer's name.

## Recovery Recipe

1. Stop using generic ready language.
2. Build a one-row proof table with each layer and its current state.
3. For every missing layer, either run the correct verifier in that
   environment or mark it unverified.
4. If the next action is provider mutation, require the artifact-owning triad
   and typed payload/job-polling guard.
5. If live, DNS, Stripe, or Search Console appears in scope, split it into a
   separate live-release gate and require explicit approval.

## What Not To Do

- Do not call a GitHub push staging proof.
- Do not call an app mirror hash site-update proof.
- Do not call Frappe Cloud `Active` status runtime proof.
- Do not call staging proof live proof.
- Do not submit Search Console from staging proof.
- Do not enable Stripe or checkout exposure from staging owner-review proof.

## Cross-links

- `artifactless-subagent-release-triad.md`
- `frappe-cloud-api-payload-shape-drift.md`
- `frappe-cloud-release-site-migration-drift.md`
- `frappe-cloud-permission-role-fixture-order-drift.md`
- `../recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`
- `../recipes/take-live-coordinated-workflows.md`

## Evidence Quality

Documented from the 2026-05-22 LT staging recovery and coordination records.
This Worker C pass is documentation-only and did not re-run local, staging, or
live proof.
