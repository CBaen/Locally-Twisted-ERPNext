---
name: Frappe Cloud release site migration drift
type: failure
failure_kind: release_gate_gap
schema_version: 0.1
date_discovered: 2026-05-12
last_updated: 2026-05-16
status: guarded
scope: project
owner_context: Locally Twisted Frappe Cloud release and live cutover
related_capabilities:
  - ../recipes/frappe-cloud-cloudflare-stripe-launch-gate.md
  - ../recipes/erpnext-intake-form-parity.md
related_failures:
  - frappe-cloud-app-mirror-release-scope-drift.md
  - frappe-cloud-staging-website-settings-drift.md
tags:
  - locally-twisted
  - frappe-cloud
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

## Known Instances

| Date | Project | Surface | Bad outcome | Evidence | Guard state | Status |
|---|---|---|---|---|---|---|
| 2026-05-12 | Locally Twisted | Frappe Cloud live site update | Bench deploy/app hash advanced while site update failed on `System Settings.language` / `time_zone`, missing Lead custom schema, then absent optional `custom_services` | Final repaired release `72a4se4v64`, app hash `04de8212aa7dbf4895716717865fc6e1029c757b`, bench deploy `62q1r0otg1` success, site update `15s16992i2` success | site update and live route/form proof required | guarded |

## Root Pattern

Frappe Cloud release has at least two separate proof surfaces: app deploy and
site migration. Local Docker can hide source-schema gaps because fields and
DocTypes already exist in the local database. A fresh cloud site exposes those
gaps during migration or first live form write.

## Required Guard

Treat release as incomplete until the bench deploy succeeds, the site
update/migrate job succeeds, deploy pipelines are no longer running, and live
route/API/form verifiers pass. Source code must create the schema it writes.

## Recovery Recipe

1. Check Frappe Cloud deploy status and the active app hash.
2. Check the site update/migrate job status separately.
3. Read the failing migration traceback and identify whether it is settings,
   schema, or optional legacy-field drift.
4. Patch the source app so fresh sites get the needed defaults/schema.
5. Guard optional legacy-field rewrites with DocType metadata checks.
6. Deploy the mirror/source app again and run site update/migrate.
7. Verify live public routes and live writing form/API paths after the final
   successful site update.

## What Not To Do

- Do not call a Frappe Cloud release complete from app hash alone.
- Do not assume local Custom Fields exist on Frappe Cloud.
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
- `frappe-cloud-app-mirror-release-scope-drift.md`
- `frappe-cloud-staging-website-settings-drift.md`

## Evidence Quality

Verified during the 2026-05-12 live Frappe Cloud cutover. Final public form
proof passed only after the bench deploy and site update/migrate job both
succeeded.
