# Frappe Cloud Staging Route Map - 2026-05-23

Status: **local/offline release map, not deployment approval**.

This document turns the May 23 staging failure into a route map: which paths
are known-bad, which paths are allowed next, and which literal staging routes
proved owner-review is still blocked.

Official Frappe Cloud docs refreshed on 2026-05-23:

- `https://docs.frappe.io/cloud/installing-an-app`
- `https://docs.frappe.io/cloud/sites/how-to-update-an-app-site-on-a-private-bench`
- `https://docs.frappe.io/cloud/benches/updating_a_bench`

Current Frappe Cloud rule that matters here: on private bench/custom-app work,
source/app changes must flow through the bench/app deploy-update path and site
update/install state before they are staging proof. A source commit, GitHub
push, app mirror hash, or deploy ID is only one evidence piece.

## Current State

Current save point before this local guard update:
`447b2ae93f0c493c24ffcd6132edfcfb87e92a45`.

The current source-bound packet is:
`workstreams/release-artifacts/2026-05-23-staging-reopen-a5ed680-readonly/`.

It is **NO-GO** and read-only. It does not authorize provider, app mirror,
staging, live, DNS, Stripe, Search Console, bootstrap, migrate, cache,
checkout, indexing, user, or secret mutation.

## Bad Routes

These are the paths future agents must treat as stop signs:

- Using an archived read-only packet after repo `HEAD` moved.
- Treating local Docker, source code, GitHub, app mirror, or deploy ID as
  staging owner-review proof.
- Treating `/app`, `/shop`, or `/shop-items` returning HTTP 200 as enough.
- Running or retrying Frappe Cloud mutation after repeated provider/bootstrap
  failures without first making a prevention artifact.
- Hand-authoring release JSON from chat, prose, an old packet, or a template.
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

1. GL gives fresh explicit approval for the exact staging-only action.
2. Create a new dated release packet.
3. Generate `release-identity-proof.json` with
   `scripts/release/release_identity_artifact.py`.
4. Generate `freeze-reopen-approval.json` with
   `scripts/release/freeze_reopen_approval_artifact.py`.
5. Generate a current `read-receipt.json` covering the release lock's required
   documents.
6. Generate or validate `failure-ledger.json`, app mirror sync plan, and
   artifact-owned triad files.
7. Run `python scripts\release\release_status_report.py` and stop unless it is
   at least `READY_FOR_CONTROLLER`.
8. Let `scripts/release/frappe_cloud_release_controller.py` evaluate the next
   requested staging action.
9. For app mirror sync, create post-sync app mirror freshness proof before
   deploy/update.
10. For deploy/update, capture post-deploy completion proof before hosted
    preflight.
11. For bootstrap/import, run hosted preflight first, then the staging
    owner-review gate after mutation.
12. Stop immediately on any `NO-GO`, `BLOCKED`, HTTP 417, stale hash, missing
    route, zero catalog/user/gallery count, or repeated failure class.

## Literal Staging Route Evidence

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
