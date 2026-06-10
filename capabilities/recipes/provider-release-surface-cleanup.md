---
id: provider-release-surface-cleanup
name: Provider Release Surface Cleanup
schema_version: 2.5
profile: governed
level: recipe
maturity: candidate
scope: Locally Twisted Frappe Cloud, app mirror, staging/live, temporary clone, and release-surface cleanup after launch or failed deployment work
currently_true: true
verification_level: 2
last_verified: 2026-06-10
evidence_quality: direct
successful_uses: 1
failed_uses: 0
regressions: 0
depends_on:
  - frappe-cloud-cloudflare-stripe-launch-gate
  - launch-repo-cleanup-and-evidence-retention
  - fail-loud-operating-law
used_by: []
tags:
  - Locally Twisted
  - Frappe Cloud
  - cleanup
  - staging
  - live
  - app mirror
  - release hygiene
---

# Provider Release Surface Cleanup

Use this when LT has extra Frappe Cloud sites, benches, app mirrors, deploy
attempts, temp clones, staging rebuilds, or release branches after launch,
especially when GL says the surfaces feel like contamination or poison.

## Rule

Clean up after release work, but do not delete by label. A surface named
`staging`, `test`, `mirror`, `old`, or `temp` may still be carrying the public
domain, live settings, or the only working deployment path.

Production identity comes from current evidence:

1. the public domain that customers reach;
2. the provider site that owns or serves that domain;
3. live business records created by the verified shop/payment flow;
4. current app hash/source path actually installed on that provider site;
5. DNS and provider routing evidence.

Names and old handoffs are hints, not proof.

## Use When

- `locallytwisted.com` is correct, but Frappe Cloud still shows multiple sites
  or benches.
- A bench/site labeled staging appears to own `locallytwisted.com`.
- A release uses an app-root mirror such as
  `CBaen/Locally-Twisted-Frappe-App`.
- A deploy marker, temp clone, worktree, or `.codex/tmp` mirror remains after
  a release.
- A future agent might push, deploy, roll back, or verify against the wrong
  bench.
- GL asks whether old staging/mirror/build surfaces are poison.

## Required Inventory Before Cleanup

Record the inventory in a dated workstream or cleanup note before deleting
anything:

- public domain and `www` behavior;
- Frappe Cloud sites: `name`, `host_name`, `status`, `bench`, `group`, `title`;
- Frappe Cloud benches: `name`, `title`, `status`, number of sites/apps;
- which site contains the latest known live order/payment proof;
- which site has the current custom domain;
- app mirror remote URL and latest pushed commit;
- local temp app mirrors, worktrees, and release clones;
- active deploy/update jobs and their terminal status;
- what is proposed to keep, rename/label, archive, or delete.

Do not print secrets. Do not export customer data for cleanup proof unless GL
explicitly approves it.

## Safe Cleanup Order

1. Prove the current live site from the customer side:
   - `https://locallytwisted.com` returns the intended site;
   - `https://www.locallytwisted.com` redirects or serves as intended;
   - one known live proof artifact still exists, for example order
     `SAL-ORD-2026-00043` or a newer approved live order.
2. Prove provider ownership:
   - identify which Frappe Cloud site has the public custom domain;
   - identify which bench/group owns that site;
   - check whether a site title or group name is stale or misleading.
3. Rename or tag before deleting when the provider supports it:
   - mark the real production surface as production/current;
   - mark old surfaces as archive, retired, or pending-delete;
   - record why each label changed.
4. Freeze release inputs:
   - full source repo commit;
   - app mirror commit;
   - Frappe Cloud site/app hash if visible;
   - current live verification state.
5. Clean local surfaces first when safe:
   - generated `__pycache__`;
   - stale `.codex/tmp` app-mirror clones after their commit is pushed and the
     source path is recorded;
   - linked worktrees only after clean status and ancestry/feature-containment
     proof.
6. Clean provider surfaces only after explicit GL approval for each named
   site/bench:
   - backup/export status is known;
   - no public domain points to it;
   - no current app update or rollback path depends on it;
   - no live business data, settings, files, or payment/email state are needed
     from it;
   - deletion target path/name is repeated exactly in the approval.
7. After cleanup, re-prove:
   - public domain still works;
   - shop/payment still works if the release touched commerce;
   - Search Console/sitemap/canonical still point at the public domain;
   - the app mirror and source repo are clean/synced;
   - cleanup note lists what was deleted and what intentionally remains.

## Hard Stops

Stop and ask before cleanup when:

- Frappe Cloud metadata says a `staging` site has `host_name:
  locallytwisted.com`;
- the provider label conflicts with the public domain behavior;
- a deploy/update job is running, failed, or unclear;
- the surface may contain live orders, payments, customers, email settings,
  files, Stripe settings, DNS settings, or production custom domain settings;
- a local temp mirror contains unpushed commits;
- the target is a bench/site deletion rather than a local generated artifact.

## Current 2026-06-10 Lesson

During LT post-launch marketing work, live `https://locallytwisted.com` was
confirmed by GL as correct. Frappe Cloud API still showed two active sites:

- `locallytwisted-staging.frappe.cloud`, title `LT Staging - Inquiry Filter`,
  group `bench-40102`, with `host_name` set to `locallytwisted.com`;
- `locallytwisted.v.frappe.cloud`, group `bench-39776`, with `host_name` set
  to `locallytwisted.v.frappe.cloud`.

That means provider labels alone were unsafe. The correct action was not to
delete staging. The correct action was to inventory, prove which surface is
actually live, then build a cleanup protocol before any deletion.

## Closeout Language

Use plain status:

- `verified live`: public domain and live proof record match;
- `untrusted label`: provider name does not match current routing evidence;
- `safe local cleanup`: generated or temp artifact can be removed;
- `provider cleanup blocked`: deletion needs explicit approval and backup;
- `cleanup complete`: deleted targets and post-clean public proof are recorded.
