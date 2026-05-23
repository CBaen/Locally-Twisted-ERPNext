---
name: Frappe Cloud permission role fixture order drift
type: failure
failure_kind: release_gate_gap
schema_version: 0.1
date_discovered: 2026-05-22
last_updated: 2026-05-22
status: guarded
scope: project
owner_context: Locally Twisted Frappe Cloud migration, role fixtures, and Custom DocPerm sync
related_capabilities:
  - ../recipes/frappe-cloud-cloudflare-stripe-launch-gate.md
  - ../recipes/erpnext-simplified-role-verification.md
related_failures:
  - frappe-cloud-release-site-migration-drift.md
  - staging-proof-surface-conflation.md
tags:
  - locally-twisted
  - frappe-cloud
  - roles
  - permissions
  - migration
  - custom-docperm
  - fail-loud
---

# Failure Recipe: Frappe Cloud Permission Role Fixture Order Drift

## Symptom

A local permission sync passes, but Frappe Cloud site update/migrate fails when
the sync creates `Custom DocPerm` rows that reference custom Roles not yet
present on the target site.

## Trigger Conditions

- A source sync function writes `Custom DocPerm`, Role Profile, User, or
  workspace permissions.
- The local database already has the custom Roles, so local tests do not expose
  creation-order drift.
- A fresh or partially repaired staging site runs migrate from source.
- The migration saves permission rows before ensuring their Role links exist.

## Known Instances

| Date | Project | Surface | Bad outcome | Evidence | Guard state | Status |
|---|---|---|---|---|---|---|
| 2026-05-22 | Locally Twisted | Staging owner/backend access migration | Site update failed after the portal repair because `LT Owner Access` and `LT Manager Access` did not exist before permission sync created rows referencing them | Frappe Cloud site update job `6itfpob0ra` failed with `Could not find Row #2: Role: LT Owner Access, Row #3: Role: LT Manager Access`; source commit `2ca1b85` added role creation before permission sync; final Controller evidence showed app mirror hash `3e86bc149d6dcc04daa194b740c1733f5c796261` and site migrate job `crn5pskff4` successful | role-first permission sync guard added | guarded |

## Root Pattern

Local ERPNext hides fixture-order bugs because old roles, custom fields, and
permissions often already exist. Frappe Cloud migration runs against the actual
target state. Any sync that writes linked permission records must own the
records it links to in the same source path, in the right order.

## Detection Signals

- `LinkValidationError` mentions a missing Role while saving a permission row.
- A verifier only checks local `Custom DocPerm` output after roles already
  exist.
- A sync function defines a permission matrix but does not create required
  Roles first.
- Staging migrate fails after source code compiled and local DB sync passed.

## Required Guard

Before permission sync creates or updates any `Custom DocPerm`, Role Profile,
User role assignment, or workspace permission, it must ensure every referenced
custom Role exists on the target site. The sync summary should report ensured
roles so the release Controller can tell the order ran.

## Recovery Recipe

1. Read the failing site-update traceback and identify the missing linked
   records.
2. Patch the source sync so required Roles are created before permission rows.
3. Make the role step idempotent; reruns should repair missing roles without
   duplicating existing roles.
4. Run local compile and the focused sync/verifier.
5. Deploy the app mirror again and require site update/migrate terminal
   success before route or account claims.
6. Record the target app hash, migration job id, cache clear, and account proof
   separately from local/GitHub proof.

## What Not To Do

- Do not manually create the Role on staging and leave source order broken.
- Do not call a local permission verifier enough for Frappe Cloud migration.
- Do not create `Custom DocPerm` rows before ensuring their linked Role names.
- Do not treat app hash success as owner/backend access proof.

## Cross-links

- `frappe-cloud-release-site-migration-drift.md`
- `staging-proof-surface-conflation.md`
- `../recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`
- `../recipes/erpnext-simplified-role-verification.md`

## Evidence Quality

Documented from the 2026-05-22 staging recovery Controller evidence. This
Worker C documentation pass did not mutate provider state, secrets, source
code, live, DNS, Stripe, or Search Console.
