---
name: Frappe Cloud app mirror release scope drift
type: failure
failure_kind: process_failure
schema_version: 0.1
date_discovered: 2026-05-16
last_updated: 2026-05-16
status: guarded
scope: project
owner_context: Locally Twisted Frappe Cloud custom app releases
related_capabilities:
  - ../recipes/frappe-cloud-cloudflare-stripe-launch-gate.md
related_failures:
  - frappe-cloud-release-site-migration-drift.md
  - public-form-photo-storage-owner-attachment-gap.md
tags:
  - locally-twisted
  - frappe-cloud
  - app-mirror
  - release-scope
  - dirty-worktree
  - fail-loud
---

# Failure Recipe: Frappe Cloud App Mirror Release Scope Drift

## Symptom

A release is described as "only the last commit" or "only the clean files," but
the Frappe Cloud app mirror target includes already-committed changes from
earlier app-mirror commits that were not part of the final source commit under
review.

## Trigger Conditions

- The local full repo is dirty and the release controller correctly avoids
  staging uncommitted files.
- The app-root mirror is updated from a reviewed source point.
- The previous live app hash is older than the target app mirror commit.
- Review checks `git show HEAD` or dirty status, but not the old-live-to-target
  app mirror diff.

## Known Instances

| Date | Project | Surface | Bad outcome | Evidence | Guard state | Status |
|---|---|---|---|---|---|---|
| 2026-05-16 | Locally Twisted | Frappe Cloud inquiry release | No current dirty workspace files were deployed, but the mirror target included broader already-committed app changes than the final two-file source commit | Previous live app hash `04de8212aa7dbf4895716717865fc6e1029c757b`; target app mirror `b4b3bf8`; final full repo commit `631f9a8`; local dirty overlaps in `hooks.py` and `patches.txt` were not in the target | release-scope guard documented | guarded |

## Root Pattern

Dirty-worktree safety and deployed-artifact scope are separate proof surfaces.
The first answers "did we stage uncommitted local files?" The second answers
"what diff is Frappe Cloud about to run compared with the current live app?"

## Detection Signals

- A release statement says "only commit X" when the app mirror has its own
  history.
- The app mirror previous-live hash is not the parent of the target commit.
- Current local dirty files overlap app paths but are not staged.
- Frappe Cloud update contains expected hotfixes plus unrelated already-pushed
  mirror changes.

## Required Guard

Before live promotion, capture:

1. current live app hash/source point;
2. target app mirror commit;
3. `git diff --name-status <live-hash>..<target-commit>` categories in the app
   mirror;
4. current dirty-worktree overlap audit from the full repo;
5. Frappe Cloud site update/migrate result;
6. live verifier or intentional smoke receipt.

## Recovery Recipe

1. Stop claiming release scope from `git show HEAD`.
2. Compare previous live app hash to target mirror commit.
3. Separate already-committed mirror scope from current uncommitted dirty files.
4. If target scope is too broad for the approved release, prepare a narrower
   source/mirror commit before site update.
5. If the broad target already went live, document the actual categories and
   run the matching smoke/verifier coverage before further promotion.

## What Not To Do

- Do not use dirty status as proof the deployed app diff is narrow.
- Do not use the full-repo final commit as proof of app mirror scope.
- Do not silently include product, marketing, or access changes in a form-only
  release explanation.
- Do not pull or reset the shared dirty worktree just to make the release story
  easier.

## Cross-links

- `../../workstreams/inquiry-form-live-release-2026-05-16.md`
- `../../workstreams/frappe-cloud-cloudflare-stripe-launch-2026-05-11.md`
- `../../LT-LAUNCH-RUNBOOK.md`
- `../recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`
- `frappe-cloud-release-site-migration-drift.md`

## Evidence Quality

Verified during the 2026-05-16 live inquiry release. The deployed release did
not include current uncommitted dirty files, but the old-live-to-target app
mirror scope was broader than the final source commit.
