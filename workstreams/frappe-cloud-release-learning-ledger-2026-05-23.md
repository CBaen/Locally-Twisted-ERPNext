# Frappe Cloud Release Learning Ledger - 2026-05-23

Status: **required-read learning ledger, not release approval**.

This file records the good, bad, and important lessons from the May 23 Frappe
Cloud staging failure review. It exists so future agents do not have to infer
the lesson from scattered packet notes.

Current local source at creation: `d7b00453b327669607f9ae7944e9ede27ddaac42`.
Current mode: forensic-freeze, local/offline only. Provider mutation is not
allowed without a fresh approval artifact.

## 2026-05-24 Handoff Stop

GL stopped release execution and moved the session into handoff-only cleanup.
Future agents must not continue provider/staging/live actions from this thread.
This stop is not a pause inside the same attempt; it is a boundary requiring a
fresh goal check, fresh source freeze, and fresh explicit approval before any
mutation-capable release work resumes.

The e87a6b1 owner-review recovery proved the app hash can reach staging, but it
did not produce a Jeff-ready shop. The active blocker is not "staging link
missing"; it is that the staging bootstrap path still depended on local
reference material under `_resources/odoo-live`. Odoo/reference material is
evidence, not deployable ERPNext app data. The next release attempt must first
create and verify a Locally Twisted / ERPNext-owned seed artifact.

Plain correction for future agents: "data mutation" was raised as a risk class
around bootstrap/live protection, not as evidence that production data was
changed in this handoff phase. After GL stopped the attempt, the only allowed
work was local docs/code cleanup and git publish.

## Current Update After Approved Staging App Deploy

Later on 2026-05-23, GL approved staging-only app mirror sync from source
`5edb641de4a3f09cc6c292904fb70551c87db3df`, then staging-only Frappe Cloud
deploy/update from app mirror
`5dd674c5ae9d6b3cb125ecf7ba2dd2e4e65e3831`. The deploy/update completed:
Frappe Cloud deploy `eu92fvbhpp` and site update job `41ftn09ocp` succeeded,
and staging now has the expected app hash.

This is still not owner-review readiness. Hosted preflight now reaches the
right app code and fails safely on missing `LT Marketing Review Access`,
`Webshop Settings.enable_checkout=0`, and missing backup/zero-data proof for
destructive catalog seed. No bootstrap/import, live, DNS, Stripe, Search
Console, checkout unpause, manual migrate, or manual cache clear happened.

## Good

- The repo now has a release lock, release controller, identity proof helper,
  status reporter, approval helper, failure ledger helper, app mirror sync plan
  helper, packet prep helper, and release-prevention test suite.
- `npm run test:release-prevention` passes as local prevention proof. This is
  useful infrastructure, but it is not staging proof.
- `python scripts\release\release_status_report.py` gives a plain result. At
  this source it correctly reports `NO-GO` because no fresh mutation-capable
  packet exists.
- Guiding Light's two-account model is now documented as expected:
  `cameronbpaul@gmail.com` and `locallytwisted@gmail.com`. This is not a
  personal failure and must not be treated as suspicious by default.
- The approved app mirror sync and deploy/update proved the clean source can
  reach staging when the packet is current, the controller is used, and the
  provider site update job is verified.
- The first deploy/update attempt revealed a precise guard gap without
  touching live surfaces: typed JSON is not enough when the Frappe Cloud
  `sites[]` row only contains `name`. The payload contract now requires the
  complete provider site object.
- Official Frappe Cloud docs refreshed on 2026-05-23 support the guard shape:
  private benches control custom apps/updates, bench deploys are separate from
  source commits, app/site updates have their own deploy/update flow, custom
  app GitHub permissions can block fetching updates, and arbitrary SSH bench
  commands are risky outside debugging.

## Bad

- Staging is still **NO-GO** for owner review.
- The latest staging app deploy archive is
  `workstreams/release-artifacts/2026-05-23-staging-reopen-5edb641-use-now/`.
  It is source-bound archive evidence after commit, not current-source mutation
  authority for later steps.
- Docs-only commits moved repo `HEAD` after that packet. That is fine, but it
  makes "current-source packet" wording dangerous unless the text clearly says
  the packet is historical staging evidence.
- The app-root mirror/deployed staging app are now at
  `5dd674c5ae9d6b3cb125ecf7ba2dd2e4e65e3831`, but hosted preflight still
  returns `ok=false`.
- Owner-review proof was missing: zero catalog/Product Setup/gallery rows,
  required owner/marketing users missing, and representative product/category
  routes returned `404`.
- The current preflight blockers are missing `LT Marketing Review Access`,
  `Webshop Settings.enable_checkout=0`, and no backup/zero-data proof for
  destructive catalog seed.
- Repeated read-only no-go packets can become noise if they only chase docs-only
  commits. Fresh packets are for changed release input state, explicit reopen
  approval, or a real mutation-capable attempt.

## Important Rules

- Do not use any archived packet as release authority after `HEAD` moves.
- Do not turn GL's dual-account workflow into an account-mismatch blocker by
  itself. The identity proof documents account context; it does not require
  Codex, GitHub, Frappe Cloud, and owner/reviewer email to all match.
- Do not treat local tests, GitHub commits, app mirror hashes, deploy IDs,
  HTTP 200 shells, or `/shop` visibility as owner-review readiness.
- Do not treat a successful staging app-hash deploy as owner-review readiness.
  App hash proof only proves code reached the target; data, roles, settings,
  backup/zero-data proof, routes, and owner-review gates still decide readiness.
- Do not treat typed JSON as a sufficient Frappe Cloud payload proof. For
  deploy/update, `sites[]` must include `name`, `server`, `bench`,
  `skip_backups`, and `skip_failing_patches` from the current provider site
  object.
- Do not call Frappe Cloud, sync the app mirror, deploy/update, bootstrap,
  migrate, clear cache, touch live/DNS/Stripe/Search Console, unpause checkout,
  or create users while forensic-freeze is active.
- Do not use SSH or bench commands on Frappe Cloud as a shortcut for normal
  release flow. Official docs describe SSH as debugging-only and warn arbitrary
  bench commands can break the managed bench flow.
- Always refresh official Frappe Cloud docs before release execution. The
  current doc set checked on 2026-05-23:
  - `https://docs.frappe.io/cloud/benches`
  - `https://docs.frappe.io/cloud/what-are-benches-and-bench-groups`
  - `https://docs.frappe.io/cloud/benches/updating_a_bench`
  - `https://docs.frappe.io/cloud/sites/how-to-update-an-app-site-on-a-private-bench`
  - `https://docs.frappe.io/cloud/faq/custom_apps`
  - `https://docs.frappe.io/cloud/benches/debugging`

## What GL Needs To Provide

Nothing is needed from GL for local documentation/guard work.

Later, only when GL wants to reopen staging execution, the process needs:

- fresh explicit approval for the exact staging-only action;
- Frappe Cloud/GitHub account session availability or MFA if required;
- confirmation of the intended account/team/site context if the safe surfaces
  are ambiguous.

Until then, the next safe action remains local guard/documentation work or
read-only forensics.
