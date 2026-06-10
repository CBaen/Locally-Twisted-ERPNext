---
name: Stale provider surface poison
type: failure
failure_kind: release_cleanup_gap
schema_version: 0.1
date_discovered: 2026-06-10
last_updated: 2026-06-10
status: guarded
scope: project
owner_context: Locally Twisted Frappe Cloud, staging/live, app mirror, and release cleanup
related_capabilities:
  - ../recipes/provider-release-surface-cleanup.md
  - ../recipes/frappe-cloud-cloudflare-stripe-launch-gate.md
  - ../recipes/launch-repo-cleanup-and-evidence-retention.md
related_failures:
  - frappe-cloud-release-site-migration-drift.md
  - frappe-cloud-app-mirror-release-scope-drift.md
  - frappe-cloud-staging-website-settings-drift.md
tags:
  - locally-twisted
  - frappe-cloud
  - staging
  - live
  - cleanup
  - provider-state
  - fail-loud
---

# Failure Recipe: Stale Provider Surface Poison

## Symptom

Agents keep seeing old benches, staging sites, app mirrors, deploy markers, or
temp clones and treat them as current truth. The extra surfaces then cause bad
deployment choices, stale blocker language, wrong verification targets, or
fear that deleting the wrong thing could break the live site.

## Root Pattern

Release work creates surfaces that outlive their usefulness. If they are not
inventoried, labeled, retired, or deleted after launch, the project gains
hidden decision debt. Future agents then argue with stale infrastructure
instead of working from the live system.

## Detection Signals

- A provider site named `staging` appears to have `host_name:
  locallytwisted.com`.
- Multiple Frappe Cloud benches are active but only one public site should
  matter.
- App mirror commits keep accumulating without a clear "current production
  source" note.
- Local `.codex/tmp` app mirror clones remain after their commits are pushed.
- Old queue/runbook language says checkout, Search Console, or live release is
  blocked even after GL/live proof says it is complete.
- A proposed cleanup target is identified by name only, not by public-domain
  and live-record evidence.

## Required Guard

Before deleting, deploying, rolling back, or treating a provider surface as
truth, run the provider release cleanup recipe:

`../recipes/provider-release-surface-cleanup.md`

The minimum proof is:

1. customer-facing public domain behavior;
2. Frappe Cloud site/bench ownership;
3. latest known live business proof record;
4. app mirror/source commit identity;
5. explicit keep/archive/delete decision for each surface.

## Recovery Recipe

1. Stop provider mutation and deletion.
2. State which site is verified live from the customer side.
3. Inventory provider sites and benches with non-secret fields only.
4. Identify which labels are untrusted or stale.
5. Update queue/runbook/capability docs so old blockers do not outrank live
   proof.
6. Remove local generated/temp artifacts only after they are proven pushed,
   clean, and nonessential.
7. Ask GL for exact approval before deleting any Frappe Cloud site, bench,
   provider app, DNS setting, Stripe setting, or production-like data surface.
8. Re-prove the public domain after cleanup.

## What Not To Do

- Do not delete a site or bench because it is called staging.
- Do not assume `locallytwisted.v.frappe.cloud` is production just because the
  vanity URL looks older.
- Do not assume `locallytwisted-staging.frappe.cloud` is disposable if it owns
  or serves `locallytwisted.com`.
- Do not keep stale queue blockers after live proof supersedes them.
- Do not let cleanup become a broad Docker, WSL, browser, cache, or machine
  prune.

## Known Instance

| Date | Project | Surface | Bad outcome risk | Guard state | Status |
|---|---|---|---|---|---|
| 2026-06-10 | Locally Twisted | Frappe Cloud sites/benches after live shop launch | The site titled `LT Staging - Inquiry Filter` appeared to carry `host_name: locallytwisted.com`; deleting by label could have broken the correct live site | provider cleanup recipe created | guarded |

## Evidence Quality

Direct provider API read and live-site/customer-side verification on
2026-06-10. GL confirmed `locallytwisted.com` is currently correct.
