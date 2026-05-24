# Frappe Cloud Staging Route Map - 2026-05-23

Status: **local/offline staging-leg map, not deployment approval**.

2026-05-23 correction: this route map covers the staging leg only. The full
business goal is a repeatable Frappe Cloud code/app-only update release:
staging owner review, explicit approval, then live app promotion while
protecting production data/settings/provider state. Use
`workstreams/frappe-cloud-app-update-release-process-2026-05-23.md` for the
full staging-to-live process.

This document turns the May 23 staging failure into a route map: which paths
are known-bad, which paths are allowed next, and which literal staging routes
proved owner-review is still blocked.

Official Frappe Cloud docs refreshed on 2026-05-23:

- `https://docs.frappe.io/cloud/benches`
- `https://docs.frappe.io/cloud/what-are-benches-and-bench-groups`
- `https://docs.frappe.io/cloud/benches/updating_a_bench`
- `https://docs.frappe.io/cloud/sites/how-to-update-an-app-site-on-a-private-bench`
- `https://docs.frappe.io/cloud/faq/custom_apps`
- `https://docs.frappe.io/cloud/benches/debugging`

Current Frappe Cloud rule that matters here: on private bench/custom-app work,
source/app changes must flow through the bench/app deploy-update path and site
update/install state before they are staging proof. A source commit, GitHub
push, app mirror hash, or deploy ID is only one evidence piece.

## Current State

Current local source after the dual-account documentation update:
`d7b00453b327669607f9ae7944e9ede27ddaac42`.

Latest staging app deploy archive:
`workstreams/release-artifacts/2026-05-23-staging-reopen-5edb641-use-now/`.

It proves the approved staging-only app mirror sync and Frappe Cloud
deploy/update completed: source `5edb641de4a3f09cc6c292904fb70551c87db3df`,
app mirror `5dd674c5ae9d6b3cb125ecf7ba2dd2e4e65e3831`, Frappe Cloud deploy
`eu92fvbhpp`, site update job `41ftn09ocp`, and installed staging app hash
`5dd674c5ae9d6b3cb125ecf7ba2dd2e4e65e3831`.

It is still **NO-GO** for owner-review. Hosted preflight blocks on missing
`LT Marketing Review Access`, `Webshop Settings.enable_checkout=0`, and
missing backup/zero-data proof for destructive catalog seed. It does not
authorize live, DNS, Stripe, Search Console, bootstrap/import, migrate, cache,
checkout, indexing, user, or secret mutation after commit.

Previous staging-reality source-bound packet:
`workstreams/release-artifacts/2026-05-23-staging-reopen-a5ed680-readonly/`.

It is **NO-GO** and read-only. It does not authorize provider, app mirror,
staging, live, DNS, Stripe, Search Console, bootstrap, migrate, cache,
checkout, indexing, user, or secret mutation.

Good/bad/important learning ledger:
`workstreams/frappe-cloud-release-learning-ledger-2026-05-23.md`.

## Bad Routes

These are the paths future agents must treat as stop signs:

- Using an archived read-only packet after repo `HEAD` moved.
- Treating local Docker, source code, GitHub, app mirror, or deploy ID as
  staging owner-review proof.
- Treating `/app`, `/shop`, or `/shop-items` returning HTTP 200 as enough.
- Running or retrying Frappe Cloud mutation after repeated provider/bootstrap
  failures without first making a prevention artifact.
- Hand-authoring release JSON from chat, prose, an old packet, or a template.
- Sending typed JSON Frappe Cloud deploy/update payloads whose `sites[]` rows
  only contain `name`; use the current provider site object with `name`,
  `server`, `bench`, `skip_backups`, and `skip_failing_patches`.
- Continuing after a Codex/GitHub/Frappe Cloud account switch without a fresh
  release identity proof artifact.
- Running bootstrap/import/migrate/cache clear before deploy-completion and
  hosted-preflight proof from the actual staging site.
- Touching live, DNS, Stripe, Search Console, production indexing, or checkout
  unpause during a staging-only recovery.
- Ignoring truncated logs, diffs, handoffs, provider output, or conversation
  history.

## Good Route

The next mutation-capable attempt must use this order:

1. Finish and push local guard/source/doc changes first.
2. Freeze source changes for the release attempt.
3. GL gives fresh explicit approval for the exact staging-only action.
4. Create a new dated release packet in the working tree.
5. Generate `release-identity-proof.json` with
   `scripts/release/release_identity_artifact.py`.
6. Generate `freeze-reopen-approval.json` with
   `scripts/release/freeze_reopen_approval_artifact.py`.
7. Generate a current `read-receipt.json` covering the release lock's required
   documents.
8. Generate or validate `failure-ledger.json`, app mirror sync plan, and
   artifact-owned triad files.
9. Run `python scripts\release\release_status_report.py` and stop unless it is
   at least `READY_FOR_CONTROLLER`.
10. Let `scripts/release/frappe_cloud_release_controller.py` evaluate the next
   requested staging action.
11. For app mirror sync, create post-sync app mirror freshness proof before
   deploy/update.
12. For deploy/update, build `sanitized-payload.json` from the current provider
    site object, not a name-only row; then capture post-deploy completion proof
    before hosted preflight.
13. For bootstrap/import, run hosted preflight first, then the staging
    owner-review gate after mutation.
14. Stop immediately on any `NO-GO`, `BLOCKED`, HTTP 417, stale hash, missing
    route, zero catalog/user/gallery count, or repeated failure class.

Source-bound artifacts are use-now evidence. If an agent commits the packet,
repo `HEAD` moves and the committed packet becomes archive evidence for the
pre-commit source. Do not use a committed packet for mutation after `HEAD`
changes; regenerate artifacts for the current source freeze.

## Account Model

Guiding Light's ERPNext/Frappe/Frappe Cloud work uses a known dual-account
operating model:

- `cameronbpaul@gmail.com`
- `locallytwisted@gmail.com`

This is normal, not an error. A release identity proof must not require the
Codex account, GitHub account, Frappe Cloud account, and owner/reviewer email
to all be the same. It must clearly state the active or intended account
context, and if the active Codex account cannot be proven from a safe surface,
it should state the dual-account model rather than invent a single-account
claim.

Safe identity wording for future LT release packets:

- Codex account label: `Guiding Light dual Codex account model:
  cameronbpaul@gmail.com / locallytwisted@gmail.com`
- Release operator: `Codex under Guiding Light direction`
- Evidence: `GL confirmed on 2026-05-23 that she always switches between
  cameronbpaul@gmail.com and locallytwisted@gmail.com for NextERP/Frappe/Frappe
  Cloud work; this is expected account context, not a blocker by itself.`

## Literal Staging Route Evidence

Current post-deploy hosted preflight evidence from
`workstreams/release-artifacts/2026-05-23-staging-reopen-5edb641-use-now/hosted-bootstrap-preflight.json`:

- `target_hash` passed: deployed app hash matches
  `5dd674c5ae9d6b3cb125ecf7ba2dd2e4e65e3831`.
- `app_order`, `app_hooks`, and `standard_report` passed.
- Blockers: missing `LT Marketing Review Access`,
  `Webshop Settings.enable_checkout=0`, and missing backup/zero-data proof for
  destructive catalog seed.
- Counts remain zero for `Item`, `Item Price`, `LT Product Blueprint`,
  `Website Item`, `Website Slideshow`, and `Website Slideshow Item`.

From
`workstreams/release-artifacts/2026-05-23-staging-reopen-a5ed680-readonly/staging-owner-review-gate-readonly.json`:

Reachable but **not readiness proof**:

| Route | Status | Meaning |
|---|---:|---|
| `/app` | 200 | Desk shell exists; not owner-review proof. |
| `/shop` | 200 | Shop/category shell exists with zero thumbnails. |
| `/shop-items` | 200 | Shop-items shell exists with zero thumbnails. |

Known-bad owner-review routes:

| Route | Status | Meaning |
|---|---:|---|
| `/shop-items/bouquets/mickey-mouse-bouquet` | 404 | Product route missing. |
| `/shop-items/arches/classic-arch` | 404 | Product route missing. |
| `/shop-items/garlands/large-garland` | 404 | Product route missing. |
| `/shop-items/columns` | 404 | Category/product route missing. |

The same packet also records `Item=0`, `Item Price=0`,
`LT Product Blueprint=0`, `Website Item=0`, `Website Slideshow=0`, missing
`locallytwisted@gmail.com`, missing `marketing@exploringnotboring.com`, stale
deployed/app-mirror hash `181076c239b2d1d3d508a41ac471c71f9d2b5158`, and
hosted preflight HTTP `417`.

## Safe Closeout Language

Use this wording unless fresh proof changes reality:

> LT staging is in forensic-freeze. Current evidence is NO-GO for owner-review
> and NO-GO for mutation without a fresh packet. Local guard tests pass, but
> local guard tests are not staging proof.
