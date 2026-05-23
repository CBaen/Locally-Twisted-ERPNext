# Frappe Cloud Post-`ebb7151` Staging Read-Only Proof - 2026-05-23

Status: **documented no-go; forensic-freeze remains active**.

This handoff records the current-state proof after commit
`ebb715132d2ac249c23163c5909c8e0f43228f13` added the hosted preflight release
guard. It is a read-only verification pass, not a staging release attempt.

No app mirror sync, provider deploy/update, site migrate, cache clear,
staging bootstrap/import, live release, DNS, Stripe, Search Console,
production indexing, or checkout unpause was performed.

## Evidence Packet

Packet:
`workstreams/release-artifacts/2026-05-23-staging-reopen-post-ebb7151-readonly/`

Artifacts:

- `read-receipt.json` - required release/freeze docs read for this pass.
- `release-controller-readonly.json` - controller allowed
  `read_only_forensics` and reported `provider_mutation_executed=false`.
- `provider-snapshot.json` - staging is Active, correct app order, paused,
  noindex, no running jobs, installed app hash
  `181076c239b2d1d3d508a41ac471c71f9d2b5158`.
- `app-mirror-freshness.json` - source `ebb7151` is not in the app-root
  mirror; mirror is missing `locally_twisted/staging_owner_review_preflight.py`
  and has a stale `staging_owner_review_bootstrap.py`.
- `hosted-bootstrap-preflight.json` - staging returns HTTP `417` because the
  deployed app does not expose `preflight_staging_owner_review_bootstrap`.
- `staging-owner-review-gate-readonly.json` - owner-review no-go: all catalog,
  Product Setup, Website Item, Website Slideshow, and slideshow item counts are
  zero; `locallytwisted@gmail.com` and
  `marketing@exploringnotboring.com` are missing; representative product and
  category routes return `404`.
- `preflight-local-snapshot.json` - local repo/file snapshot for this packet.

## Triad Review

Provider Witness result: no staging/provider mutation is currently allowed.
The active lock is `status=active`, `stage=forensic-freeze`, and blocks
`frappe_cloud_deploy`, `app_mirror_sync`, `provider_poll`,
`staging_bootstrap`, `site_migrate`, `cache_clear`, live/DNS/Stripe/Search
Console/indexing work, and checkout unpause. Witness confirmed source HEAD
`ebb7151`, the only dirty LT path was this new read-only packet, and current
app-mirror proof remains `ok=false`.

Gate/Fixer result at packet time: do not attempt to leave forensic-freeze yet.
Local contracts for `release-controller` and `release-lock` passed, but four
local capabilities were missing before mutation: an explicit freeze-reopen
transition, a pre-sync/post-sync split for app mirror sync, a post-deploy/update
completion artifact contract, and a sanitized owner-review release artifact
mode so raw previous traceback history does not become release evidence.

Follow-up local guard closure: those four gaps are now represented as local
contracts. `frappe_cloud_release_controller.py` requires `--reopen-approval`
for mutation under forensic-freeze, `app_mirror_sync` requires a pre-sync
`--app-mirror-sync-plan` instead of post-sync freshness, `staging_bootstrap`
requires `--deploy-completion`, and `staging_owner_review_gate.py --json
--release-artifact` sanitizes previous bootstrap diagnostics. These contracts
are local prevention only; they do not prove staging readiness or authorize
provider mutation.

Follow-up template parity: `f5e2e91` updated the staging-freeze packet
template so fresh release packets have starter shapes for those current
controller inputs. This is still template/source proof only; real current
artifacts must be produced in the next dated packet.

Recorder result: this handoff and the front-door docs must state that
`ebb7151` is source archive proof only. It does not prove app mirror freshness,
deployed app state, staging records, owner/marketing accounts, product routes,
or owner-review readiness.

## Current Gate

The next mutation-capable release packet needs explicit approval to leave
forensic-freeze. After that, the controlled order is app mirror sync from
reviewed source, fresh app-mirror freshness proof, fresh provider snapshot,
fresh hosted bootstrap preflight, then staging bootstrap/import only if the
release controller gates pass.

## Cleanup

No stale source/code file was created by this pass. The retained artifacts are
the evidence packet and this handoff. No generated scratch clone is present in
the repo.
