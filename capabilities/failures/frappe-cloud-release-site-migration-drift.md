---
name: Frappe Cloud release site migration drift
type: failure
failure_kind: release_gate_gap
schema_version: 0.1
date_discovered: 2026-05-12
last_updated: 2026-05-22
status: guarded
scope: project
owner_context: Locally Twisted Frappe Cloud release and live cutover
related_capabilities:
  - ../recipes/frappe-cloud-cloudflare-stripe-launch-gate.md
  - ../recipes/erpnext-intake-form-parity.md
related_failures:
  - frappe-cloud-api-payload-shape-drift.md
  - frappe-cloud-permission-role-fixture-order-drift.md
  - staging-proof-surface-conflation.md
  - frappe-cloud-app-mirror-release-scope-drift.md
  - frappe-cloud-staging-website-settings-drift.md
tags:
  - locally-twisted
  - frappe-cloud
  - staging
  - migration
  - schema
  - release
  - fail-loud
---

# Failure Recipe: Frappe Cloud Release Site Migration Drift

## Symptom

Frappe Cloud shows a new deployed app hash or a successful bench deploy, but the
live site still fails routes, forms, or migrations because the site update job
did not complete with the expected schema and settings.

## Trigger Conditions

- The custom app deploy succeeds before the site update/migrate succeeds.
- A patch assumes mandatory Singles fields are already populated on a fresh
  Frappe Cloud site.
- Custom fields or DocTypes exist locally but are not created by source-owned
  install/migration code.
- A migration queries optional legacy fields without checking the current
  DocType metadata.
- A guard patch enforces the desired current state but does not safely repair
  stale staging values before asserting.
- Permission sync creates `Custom DocPerm` rows before ensuring every custom
  Role referenced by those rows exists on the target site.

## Known Instances

| Date | Project | Surface | Bad outcome | Evidence | Guard state | Status |
|---|---|---|---|---|---|---|
| 2026-05-12 | Locally Twisted | Frappe Cloud live site update | Bench deploy/app hash advanced while site update failed on `System Settings.language` / `time_zone`, missing Lead custom schema, then absent optional `custom_services` | Final repaired release `72a4se4v64`, app hash `04de8212aa7dbf4895716717865fc6e1029c757b`, bench deploy `62q1r0otg1` success, site update `15s16992i2` success | site update and live route/form proof required | guarded |
| 2026-05-22 | Locally Twisted | Frappe Cloud staging owner-review recovery | Correct JSON deploy reached the site update layer, then migration failed because staging had `Portal Settings.default_portal_home` drifted away from the required LT account home value | Staging group `bench-40102`, bench `bench-40102-000003-f4v`; live group `bench-39776`, bench `bench-39776-000015-f94v`; target app hash `f236d6d86deca0066c98e3776189b32c8818cb6d`; site update/migrate jobs `8vspcanje0` and `63lqkkrppt` failed with `Portal Settings.default_portal_home must stay 'me' for the LT account home`; source commit `0f6fcad` added a migration-safe portal repair path | migration guard must repair safe staged drift before asserting | guarded |
| 2026-05-22 | Locally Twisted | Frappe Cloud staging owner-review recovery | The next site update failed because permission sync wrote `Custom DocPerm` rows for roles that did not exist yet on staging | Site update job `6itfpob0ra` failed with `Could not find Row #2: Role: LT Owner Access, Row #3: Role: LT Manager Access`; source commit `2ca1b85` ensured required LT roles before permission sync; final app mirror hash `3e86bc149d6dcc04daa194b740c1733f5c796261`, site migrate job `crn5pskff4`, config job `3u20303jfl`, and clear-cache job `eu27r8q4to` were successful per Controller evidence | role-first permission sync guard added; release still requires route/account proof before owner-ready claims | guarded |

## Root Pattern

Frappe Cloud release has at least three separate proof surfaces: provider
deploy candidate, site update/migration, and route/browser behavior after
cache clear. Local Docker can hide source-schema gaps because fields and
DocTypes already exist in the local database. A fresh cloud site exposes those
gaps during migration or first live form write.

Staging drift is not automatically a reason to stop forever, but it is never a
reason to bypass the guard. If the desired state is deterministic and safe,
the migration should repair the staged value and then assert it. If the repair
would be destructive or business-sensitive, the migration must fail loudly and
name the exact field.

## Required Guard

Treat release as incomplete until the deploy candidate reaches terminal
success, the site update/migrate job reaches terminal success, cache is cleared,
the installed hash and installed app order match the target, the site is
`Active`, no deploy/update jobs are running, and route/browser verifiers pass.
Source code must create the schema and roles it writes. Permission sync must
ensure every referenced custom Role exists before any `Custom DocPerm` save.
Migration guards that enforce staging settings must either repair known-safe
drift first or fail with an explicit field-level blocker.

## Recovery Recipe

1. Check Frappe Cloud deploy status and the active app hash.
2. Confirm nested provider payloads were sent as typed JSON, not form-encoded
   strings.
3. Check the deploy candidate job status separately from the HTTP response.
4. Check the site update/migrate job status separately.
5. Read the failing migration traceback and identify whether it is settings,
   schema, role-fixture, permission-order, or optional legacy-field drift.
6. Patch the source app so fresh sites get the needed defaults/schema/roles.
7. Guard optional legacy-field rewrites with DocType metadata checks, and guard
   setting patches with safe repair-or-loud-fail behavior.
8. Deploy the mirror/source app again and run site update/migrate.
9. Clear cache and verify installed hash/app order, site status, and no running
   jobs.
10. Verify staging/live public routes and writing form/API paths after the final
   successful site update.

## What Not To Do

- Do not call a Frappe Cloud release complete from app hash alone.
- Do not call a `200`/`null` provider response complete; it is enqueue-only.
- Do not assume local Custom Fields exist on Frappe Cloud.
- Do not assume local custom Roles exist on Frappe Cloud before permission
  sync.
- Do not patch the live database manually instead of source-owning schema.
- Do not ignore a failed site update because the public homepage looks newer.
- Do not run optional legacy migrations against fields that are absent on the
  current site.
- Do not use this guard as a substitute for release-scope review. Site
  migration success proves the target migrated; it does not prove the target
  app diff was narrow.

## Cross-links

- `../../workstreams/frappe-cloud-cloudflare-stripe-launch-2026-05-11.md`
- `../../workstreams/inquiry-form-live-release-2026-05-16.md`
- `../../LT-LAUNCH-RUNBOOK.md`
- `../recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`
- `../recipes/erpnext-intake-form-parity.md`
- `frappe-cloud-api-payload-shape-drift.md`
- `frappe-cloud-permission-role-fixture-order-drift.md`
- `staging-proof-surface-conflation.md`
- `frappe-cloud-app-mirror-release-scope-drift.md`
- `frappe-cloud-staging-website-settings-drift.md`

## Evidence Quality

Verified during the 2026-05-12 live Frappe Cloud cutover, with 2026-05-22
staging-recovery instances added from parent Controller evidence. This Worker C
docs-only pass did not mutate provider state or independently re-run staging
checks. The final staging deploy/migrate/cache success is not live proof and
does not authorize DNS, Stripe, Search Console, or production promotion.
