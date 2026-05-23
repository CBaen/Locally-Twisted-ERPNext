# Staging Provider Job Proof - 2026-05-23

Role: Worker F in the Locally Twisted staging release triad.

Scope: Frappe Cloud provider/job proof for staging only. This artifact does not
approve owner review, live release, DNS, Stripe, Search Console, Cloudflare, or
production checkout.

2026-05-23 freeze note: this provider proof is historical evidence only. The
release process was later stopped and superseded by
`../frappe-cloud-staging-release-failure-forensics-2026-05-23.md` and
`../frappe-cloud-release-prevention-action-items-2026-05-23.md`. Do not use
this proof to resume mutation or claim owner-review readiness.

Date boundary: 2026-05-22 America/Denver / 2026-05-23 UTC.

Credential source was a GL-provided local Frappe API file. The exact secret
path and secret contents are not needed in this artifact. Secrets, API tokens,
cookies, and session IDs were not printed or recorded.

## Decision

**PROVIDER UPDATE TERMINAL SUCCESS for the requested staging app hash.**

At the final provider poll, `locallytwisted-staging.frappe.cloud` was `Active`,
had `0` running jobs, and reported `locally_twisted` installed at the requested
hash `409a64758dd8377e5541bf2ad019b0ba59042aef` from app release
`07cmfo0803`.

This is not owner-review readiness. It only proves the provider app/site update
surface reached terminal success for the requested app hash. Owner-review
readiness still requires the staging owner-review gate, catalog/data proof,
required users, route/browser proof, and any separate release/security gates.

## Boundary Proof

- No Frappe Cloud mutation was run by Worker F.
- No live site, DNS, Stripe, Search Console, Cloudflare, or production provider
  state was changed.
- No git commit, push, merge, rebase, checkout, or reset was run.
- The only repo file Worker F owns in this pass is this artifact.

## Commands And API Surfaces Used

All commands were run from:

`C:\Users\baenb\projects\Built_by_Cameron\_CLIENTS\locally-twisted`

```powershell
git rev-parse --abbrev-ref HEAD
git rev-parse --show-toplevel
git status --porcelain=v1
git worktree list
git ls-remote https://github.com/CBaen/Locally-Twisted-Frappe-App.git HEAD refs/heads/main
```

Read-only Frappe Cloud API methods used:

```text
press.api.site.get
press.api.site.installed_apps
press.api.site.site_config
press.api.site.running_jobs
press.api.site.jobs
press.api.site.job
press.api.bench.deploy_information
press.api.bench.deploy_status
```

Reference basis:

- Frappe Cloud bench update docs:
  `https://docs.frappe.io/cloud/benches/updating_a_bench`
- Press bench API source:
  `https://github.com/frappe/press/blob/develop/press/api/bench.py`
- Press site API source:
  `https://github.com/frappe/press/blob/develop/press/api/site.py`

## Requested Target

| Field | Value |
|---|---|
| Release group | `bench-40102` |
| Staging site | `locallytwisted-staging.frappe.cloud` |
| App | `locally_twisted` |
| App release | `07cmfo0803` |
| Expected app hash | `409a64758dd8377e5541bf2ad019b0ba59042aef` |
| App mirror HEAD | `409a64758dd8377e5541bf2ad019b0ba59042aef` |

`git ls-remote` confirmed the app mirror `main`/`HEAD` was the same expected
hash.

## Final Provider Snapshot

Final checked-at timestamp from Worker F local UTC clock:
`2026-05-23T01:37:24.124489+00:00`.

| Field | Result |
|---|---|
| Site | `locallytwisted-staging.frappe.cloud` |
| Site status | `Active` |
| Site group | `bench-40102` |
| Server | `f4-virginia.frappe.cloud` |
| Running jobs | `0` |
| Deploy in progress | `false` |
| Deploy status candidate | `null` |
| Deploy status is_deploy_in_progress | `false` |
| Deploy status is_validating | `false` |
| Last deploy/candidate id | `2b78t20pnb` |
| Last deploy status | `Success` |
| Last deploy creation | `2026-05-23 08:00:34.469336` |

Provider timestamps above are recorded exactly as Frappe Cloud returned them.

## Installed App Proof

| App order | Result |
|---|---|
| 1 | `frappe` |
| 2 | `erpnext` |
| 3 | `payments` |
| 4 | `webshop` |
| 5 | `locally_twisted` |

| Field | Result |
|---|---|
| `locally_twisted` repository | `Locally-Twisted-Frappe-App` |
| `locally_twisted` branch | `main` |
| `locally_twisted` installed hash | `409a64758dd8377e5541bf2ad019b0ba59042aef` |
| Expected hash match | `true` |
| Installed commit message | `Harden staging owner review bootstrap gate` |

`locally_twisted` remains installed last, preserving the LT override order.

## Recent Site Jobs

Most recent staging jobs returned by `press.api.site.jobs`:

| Job id | Job type | Status | Provider end |
|---|---|---|---|
| `cegbm9sa1l` | Update Site Pull | Success | `2026-05-23 02:36:38.246505` |
| `03lfnu6bno` | Update Site Pull | Success | `2026-05-23 02:18:07.405261` |
| `ft2b7b4hms` | Update Site Pull | Success | `2026-05-23 02:06:50.421228` |
| `0mr7bmolq5` | Update Site Pull | Success | `2026-05-23 01:56:13.651011` |
| `eu27r8q4to` | Clear Cache | Success | `2026-05-23 01:13:46.649936` |
| `3u20303jfl` | Update Site Configuration | Success | `2026-05-23 01:13:44.242984` |
| `crn5pskff4` | Update Site Migrate | Success | `2026-05-23 01:10:52.104012` |
| `cjifa26m76` | Recover Failed Site Migrate | Success | `2026-05-23 00:56:01.871523` |

Worker F also opened details for `crn5pskff4`, `3u20303jfl`,
`eu27r8q4to`, `0mr7bmolq5`, `ft2b7b4hms`, and `03lfnu6bno`. The checked
steps were terminal success. For `crn5pskff4`, the migration step reported
DocType updates through `locally_twisted` and finished successfully.

## Config Proof

Final config values from `press.api.site.site_config`:

| Key | Value |
|---|---|
| `lt_ecommerce_paused` | `1` |
| `lt_public_indexing_enabled` | `0` |

Checkout remains paused and public indexing remains disabled by staging config.

## Notes

An intermediate poll at `2026-05-23T01:36:56.983259+00:00` already showed the
expected app hash installed, but the site still reported `Updating`. Worker F
waited and re-polled. The final poll showed `Active`.

`press.api.bench.deploy_information` still reported `update_available=true` on
the final target-hash poll. Because the installed `locally_twisted` hash matched
the requested hash, `press.api.bench.deploy_status` had no active candidate, and
the site had zero running jobs, Worker F does not treat that flag as failure of
this requested LT app-hash update. Do not use it to run a broad bench update
without separate explicit scope and release approval.

## Remaining Out Of Scope

This proof does not establish:

- staging owner-review readiness;
- catalog, Product Setup, Website Item, or gallery data presence;
- required owner or marketing users;
- guest/owner route/browser behavior;
- Stripe/payment readiness;
- DNS, Search Console, or live production readiness.

Run `scripts/verify/staging_owner_review_gate.py` against the actual staging
site before any owner-review-ready language.
