# Frappe Cloud Release Prevention Action Items - 2026-05-23

Status: **forensic-freeze action list with the first local/offline prevention
guard layer implemented at commit `58258fd`, expanded through the current
read-only no-go archive `ceab908`, the post-`ebb7151` read-only packet, the
release packet template parity fix `f5e2e91`, and the release artifact
chain-binding guard plus freeze-reopen approval timestamp guard. Do not use
this as permission to deploy.**

This document exists because notes were present, but the release process still
continued. The first executable local gates now exist; the next agent must keep
them green and finish the still-open provider/staging prerequisites before
reopening Locally Twisted Frappe Cloud staging release work.

2026-05-23 guard implementation update: the first local/offline prevention
layer now exists. It blocks release mutation while forensic-freeze is active,
validates `application/json` typed Frappe Cloud payload shape before provider
calls, checks required-doc read receipts, requires artifact-owned triad
evidence, can write an emergency handoff artifact on controller failure, and
fails docs that collapse provider success into owner-review readiness.

Implemented local guard paths:

- `release_locks/locally-twisted-staging-forensic-freeze.json`
- `scripts/release/frappe_cloud_release_controller.py`
- `scripts/verify/release_lock_contract.py`
- `scripts/verify/release_controller_contract.py`
- `scripts/verify/frappe_cloud_payload_contract.py`
- `scripts/verify/frappe_cloud_app_mirror_freshness.py`
- `scripts/verify/frappe_cloud_provider_snapshot.py`
- `scripts/verify/frappe_cloud_deploy_completion_contract.py`
- `scripts/verify/staging_owner_review_gate_contract.py`
- `scripts/verify/staging_owner_review_hosted_preflight.py`
- `scripts/verify/staging_owner_review_bootstrap_contract.py`
- `scripts/verify/release_claim_language_contract.py`
- `workstreams/release-artifacts/README.md`
- `workstreams/release-artifacts/2026-05-23-staging-freeze/TEMPLATE.md`

Local guard command:

```powershell
npm run test:release-prevention
```

This command is not staging proof. It proves the local prevention architecture
exists before future release execution is reopened.

2026-05-23 read-receipt widening:
Recorder/Security review found the required read receipt was narrower than the
packet-authoring docs agents now need. The lock and controller now require
front-door handoffs, launch runbook, release-artifact README, artifact-chain
binding handoff, scripts README, action list, forensic report,
staging-owner-review history, launch capability, and queue before mutation can
pass.

2026-05-23 read-only current-state packet:
`workstreams/release-artifacts/2026-05-23-staging-reopen-readonly/`.
This packet produced a real read-only provider snapshot and a strict JSON
staging owner-review gate artifact. It did not mutate provider/staging/live
state. Result: staging is provider-stable but still owner-review blocked, and
the hosted bootstrap preflight cannot run because the deployed app hash/app
mirror `181076c239b2d1d3d508a41ac471c71f9d2b5158` does not include the current
source preflight module from `ceab908` (first introduced in `e44ecc2`).
Docs parity handoff:
`workstreams/frappe-cloud-doc-parity-ceab908-2026-05-23.md`.
Post-`ebb7151` read-only packet:
`workstreams/release-artifacts/2026-05-23-staging-reopen-post-ebb7151-readonly/`.
That packet confirms the current source guard commit did not change provider
reality: app mirror freshness is still `ok=false`, hosted preflight still
returns HTTP `417`, staging owner-review rows/users are still missing, and
provider mutation remains blocked.

2026-05-23 packet-template parity:
`workstreams/frappe-cloud-release-artifact-template-parity-2026-05-23.md`.
`workstreams/release-artifacts/2026-05-23-staging-freeze/TEMPLATE.md` now
includes the current required shapes for freeze reopen approval, app mirror
sync planning, deploy completion, and hosted preflight `checks`. This closes a
local template gap only. A future release attempt still needs real current
artifacts generated for its own dated packet.

2026-05-23 artifact-chain binding:
`workstreams/frappe-cloud-release-artifact-chain-binding-2026-05-23.md`.
The local controller now rejects mutation-capable packets whose reopen
approval, app mirror sync plan/freshness, provider snapshot, deploy payload,
deploy completion, or hosted preflight artifacts describe different source
commits, rollback hashes, target hashes, or staging sites. This closes a local
offline guard gap only. It did not reopen forensic-freeze and did not mutate
provider/staging/live/DNS/Stripe/Search Console/app mirror/bootstrap/migrate/
cache/checkout/secrets.

2026-05-23 freeze-reopen approval timestamp guard:
`workstreams/frappe-cloud-freeze-approval-timestamp-guard-2026-05-23.md`.
The local controller now rejects `freeze-reopen-approval.json` files whose
approval timestamps are missing, malformed, timezone-less, expired,
future-dated beyond clock skew, reversed, or longer than 24 hours. This closes
another local offline guard gap only. It did not create a valid approval,
reopen forensic-freeze, or mutate provider/staging/live/DNS/Stripe/Search
Console/app mirror/bootstrap/migrate/cache/checkout/secrets.

2026-05-23 latest archived read-only packet:
`workstreams/release-artifacts/2026-05-23-staging-reopen-fa38bc3-readonly/`.
This packet updates no-go evidence at source
`fa38bc31a120f6d52f1e21e4ab011d5b03c2d74d`. It confirms the app-root
mirror/deployed staging app remains at
`181076c239b2d1d3d508a41ac471c71f9d2b5158`, hosted preflight still returns
HTTP `417`, owner-review data/users/routes are still missing, and
`app_mirror_sync` is still blocked by missing `freeze-reopen-approval.json`.
This is not provider mutation, owner-review readiness, or mutation proof for a
later commit.

2026-05-23 archived snapshot-source read-only packet:
`workstreams/release-artifacts/2026-05-23-staging-reopen-current-head-readonly/`.
This packet updates the no-go evidence at source
`69e4e9f2cf3c97e337b9e8046d4cd86cc5e1b68c`. The folder name is historical:
after the packet was committed, repo `HEAD` moved. It includes a valid read
receipt for that packet, provider snapshot, app mirror sync plan, failure
ledger, and triad artifacts, plus fresh no-go app mirror freshness, hosted
preflight, and owner-review gate artifacts. The controller still blocks
`app_mirror_sync` because `freeze-reopen-approval.json` is missing. This is not
provider mutation, owner-review readiness, or mutation proof for a later commit.

Source incident:
`workstreams/frappe-cloud-staging-release-failure-forensics-2026-05-23.md`.

## Absolute Boundaries

- Do not touch live, DNS, Stripe, Search Console, production indexing, or live
  checkout from this action list.
- Do not sync the app-root mirror while forensic-freeze is active.
- Do not resume the interrupted deploy/bootstrap sequence.
- Do not call staging owner-review ready from hashes, deploy IDs, job IDs, or
  local Docker proof.
- If Guiding Light says stop, all mutation stops. Read-only forensics only.

## P0 Actions

Status key: `implemented-local` means the guard exists and is covered by
`npm run test:release-prevention`; it is not provider/staging proof.
`open-before-provider-mutation` means still required before any release
execution can leave forensic-freeze.

1. **Create a machine-readable release lock.** `implemented-local`
   Add a local/repo release-lock mechanism that blocks Frappe Cloud deploy,
   bootstrap, migration, DNS, Stripe, Search Console, and live actions while a
   forensic freeze is active. The lock must be checked by every release script.

2. **Build one approved release controller gate.** `implemented-local; open-before-provider-mutation`
   Route all future Frappe Cloud staging/live work through one controller gate
   instead of ad hoc API calls. The current controller is deliberately offline:
   it checks the active lock, required read receipt, typed payload artifact,
   provider snapshot artifact, failure ledger, and artifact-owned triad inputs.
   A future provider-executing controller still needs to bind those artifacts
   to the exact target site, target app hash, app order, migration/cache state,
   safety flags, and owner-review gate output before mutation.

3. **Add a required-doc read gate.** `implemented-local`
   Before any release command runs, the controller must require an explicit
   local state receipt that these files were read for the current attempt:
   this file, the forensic report, the staging owner-review workstream, the
   project launch capability, and the project queue. Missing receipt exits
   nonzero.

4. **Validate Frappe Cloud payloads before API calls.** `implemented-local`
   Add a payload schema validator that proves nested `apps` and `sites` are
   typed JSON arrays/objects. Stringified nested JSON must fail locally before
   a provider request can be sent.

5. **Add the failure-class circuit breaker.** `implemented-local`
   After one provider/bootstrap failure, the next permitted step is failure
   classification plus a written guard. After two related failures, all
   provider mutation is blocked until a fresh artifact-owning release plan is
   approved.

6. **Require a read-only provider snapshot before mutation.** `implemented-local; open-before-provider-mutation`
   The controller must record current team/account, site, bench group, bench,
   installed app hash, release ID, running jobs, app order, site status,
   rollback hash, and staging/live separation before mutation. The controller
   now requires and validates this artifact shape, but the next release attempt
   still needs a fresh current-state snapshot from the actual provider. No
   snapshot, no deploy.

7. **Make the triad artifact-owned.** `implemented-local; open-before-provider-mutation`
   Controller, Provider Witness, Gate/Fixer, and Recorder must each own an
   artifact. Acceptable artifacts include provider-state proof, sanitized
   payload proof, executable verifier output, patch/diff review, rollback
   proof, docs parity update, or blocker report. Advice-only helpers do not
   count. The controller now requires the artifact set; future release work
   must populate it for the current attempt.

8. **Finish the staging owner-review gate before reopening release.** `open-before-provider-mutation`
   `scripts/verify/staging_owner_review_gate.py` must remain the owner-review
   stop gate. It must prove the actual staging site has required users,
   nonzero catalog rows, Product Setup rows, Website Slideshow rows, product
   gallery projection, paused ecommerce, disabled public indexing, correct app
   hash/order, and authenticated owner-visible routes.

9. **Add fresh-site bootstrap preflight.** `open-before-provider-mutation`
   Bootstrap must have a dry-run/preflight mode that checks hosted constraints
   before catalog mutation: standard Report save rules, required roles, Portal
   Settings, Website Settings, app hooks, installed app order, and expected
   catalog baselines.

10. **Separate provider success from owner-review readiness.** `implemented-local`
    Add wording and gate checks so deploy success, migration success, cache
    success, route health, account proof, catalog proof, and owner-review
    readiness are distinct states. The controller must reject broader claims.

11. **Add an emergency handoff format.** `implemented-local`
    When a release fails, the handoff must answer: current state, last
    mutation, active locks, known blockers, what not to touch, exact next safe
    action, and whether any provider/bootstrap failure class was repeated.

12. **Remove release authority from the failed controller pattern.** `implemented-local`
    A session that caused a release-process failure cannot continue as release
    controller for the same release. It may only write forensics, handoff, or
    prevention docs unless GL explicitly reopens execution under a new plan.

13. **Add an offline staging owner-review gate contract.** `implemented-local`
    `scripts/verify/staging_owner_review_gate_contract.py` now uses fake
    provider/staging fixtures to prove zero catalog rows, missing
    owner/marketing users, wrong app order, wrong installed hash, stale
    bootstrap hash, and paused/exposure mismatches all fail before any
    owner-review-ready claim is possible. It is wired into package scripts and
    the release-prevention suite.

14. **Add hosted bootstrap preflight and destructive-seed proof.** `implemented-local; open-before-provider-mutation`
    Bootstrap now exposes a whitelisted non-mutating preflight and records the
    preflight before catalog seed. The source contract checks standard Report
    save behavior, required roles, Portal/Website Settings, app hooks, app
    order, target hash, expected baseline counts, and either a real current
    staging backup artifact or explicit zero-data proof. The destructive seed
    path no longer passes descriptive backup text. This still needs real
    staging preflight execution in a future release packet before mutation.

15. **Require payload artifacts for future provider deploy/update actions.** `implemented-local`
    The current local controller now requires `--payload-file` for
    `frappe_cloud_deploy` actions and validates the sanitized payload before
    the action can proceed to any later gate. A future provider-executing
    controller must preserve this rule before it can reach any provider API
    call.

16. **Add a provider snapshot producer.** `implemented-local; open-before-provider-mutation`
    `scripts/verify/frappe_cloud_provider_snapshot.py` now has an offline
    self-test and a real read-only mode that can write the sanitized
    `provider-snapshot.json` artifact. The 2026-05-23 read-only packet ran real
    provider mode for the current staging target and wrote
    `workstreams/release-artifacts/2026-05-23-staging-reopen-readonly/provider-snapshot.json`.
    Any future release packet still needs a fresh snapshot after app mirror
    sync and before mutation.

17. **Fix staging owner-review JSON artifacts.** `implemented-local`
    `scripts/verify/staging_owner_review_gate.py --json` now emits strict JSON
    even when the gate fails. This was required because the read-only staging
    artifact initially appended human failure lines after the JSON object,
    making it unsuitable as a machine-readable release packet artifact.

18. **Block on stale app-root mirror before hosted bootstrap.** `open-before-provider-mutation`
    Read-only proof shows staging/app mirror hash `181076c...` lacks
    `locally_twisted/staging_owner_review_preflight.py`, and the hosted
    preflight endpoint fails with no such attribute. Future release execution
    must sync the app-root mirror from reviewed source before deploy/update,
    hosted preflight, bootstrap/import, or cache action.

19. **Add app-root mirror freshness verifier.** `implemented-local; open-before-provider-mutation`
    `scripts/verify/frappe_cloud_app_mirror_freshness.py` now has an offline
    self-test wired into `npm run test:release-prevention` and a real
    read-only GitHub mode that writes `app-mirror-freshness.json`. The
    2026-05-23 read-only packet at
    `workstreams/release-artifacts/2026-05-23-app-mirror-freshness-readonly/`
    proves mirror hash `181076c...` is missing
    `locally_twisted/staging_owner_review_preflight.py` and has a stale
    `locally_twisted/staging_owner_review_bootstrap.py` relative to source
    `24c8465`. This is a no-go artifact, not sync approval.

20. **Add hosted bootstrap preflight probe.** `implemented-local; open-before-provider-mutation`
    `scripts/verify/staging_owner_review_hosted_preflight.py` now has an
    offline self-test wired into `npm run test:release-prevention` and a real
    read-only staging mode that writes `hosted-bootstrap-preflight.json`. The
    2026-05-23 readiness refresh at
    `workstreams/release-artifacts/2026-05-23-staging-reopen-readiness-refresh/`
    proves the current staging app still returns HTTP `417` for
    `preflight_staging_owner_review_bootstrap`. The release controller now
    requires a passing hosted preflight artifact before `staging_bootstrap`,
    and validates that it is from the same staging site/hash as the provider
    snapshot and app-mirror freshness artifacts with the full hosted
    `required_checks` payload.

21. **Add an explicit freeze-reopen transition.** `implemented-local; open-before-provider-mutation`
    The controller now requires `--reopen-approval` for mutating actions while
    forensic-freeze is active. The artifact must be bound to the active lock,
    staging target, source commit, approved staging-only actions, and must keep
    live/DNS/Stripe/Search Console blocked. It is covered by
    `release_lock_contract.py` and `release_controller_contract.py`. A future
    release packet still needs a real current approval artifact; chat approval
    alone is not the transition.

22. **Split app mirror sync into pre-sync and post-sync gates.** `implemented-local; open-before-provider-mutation`
    The controller now treats `app_mirror_sync` as a special mutating action:
    it requires `--app-mirror-sync-plan` before sync instead of requiring
    passing app-mirror freshness before sync. All downstream mutation still
    requires post-sync `app-mirror-freshness.json` with `ok=true` before
    deploy/update, hosted preflight, bootstrap/import, or cache work.

23. **Add post-deploy/update completion artifact contract.** `implemented-local; open-before-provider-mutation`
    `scripts/verify/frappe_cloud_deploy_completion_contract.py` now validates a
    sanitized post-deploy/update artifact for provider job success, installed
    hash, app order, empty running jobs, staging flags, provider snapshot
    binding, app mirror hash binding, and no raw traceback/body/secret fields.
    The release controller now requires `--deploy-completion` before
    `staging_bootstrap`.

24. **Sanitize owner-review gate release artifacts.** `implemented-local; open-before-provider-mutation`
    `staging_owner_review_gate.py --json --release-artifact` now omits raw
    previous bootstrap traceback/body diagnostics while preserving counts,
    hashes, users, route evidence, bootstrap state, and actionable failure
    summaries. The sanitizer is covered by
    `staging_owner_review_gate_contract.py`.

25. **Bind release packet artifacts into one source/hash chain.** `implemented-local; open-before-provider-mutation`
    The controller now validates cross-artifact consistency after individual
    shape checks. Reopen approval, app mirror sync plan, and app mirror
    freshness source commits must match the current repository `HEAD`; the app
    mirror sync rollback hash must match the provider snapshot rollback hash;
    deploy payload app hash/site must match provider and mirror artifacts; and
    deploy completion/hosted preflight hashes must stay bound to the same
    chain. This prevents stale approval, plan, mirror, provider, and payload
    artifacts from being mixed into a release packet.

## P1 Actions

1. Wire the release lock and owner-review gate into `npm run` scripts so future
   agents discover them through normal package commands. Local prevention is
   now wired as `npm run test:release-prevention`; the real staging gate
   remains `npm run test:staging-owner-review` and must be run only when a
   provider-backed staging verification phase is explicitly reopened.
2. Add a CI-safe docs lint that fails when launch/staging docs say
   owner-review ready without referencing the owner-review gate artifact.
3. Create sanitized provider evidence packet templates under a named
   release-artifacts folder. Implemented for the staging-freeze template in
   `f5e2e91`; future release attempts must copy it into a fresh dated packet
   and populate real artifacts, not edit the template as proof.
4. Add rollback proof to the controller output before any provider mutation.
5. Add a "proof vocabulary" checker for release docs:
   `local`, `GitHub archive`, `app mirror`, `deploy candidate`,
   `site migrate`, `cache/config`, `staging owner-review`, and `live release`
   cannot be used interchangeably.
6. Add release-packet producers for real freeze-reopen approval and app mirror
   sync plan artifacts once GL explicitly reopens staging execution.

## Suggested File Targets

These targets are now split between implemented local guards and still-open
future release work.

Implemented local/offline guards:

- `scripts/release/frappe_cloud_release_controller.py`
- `scripts/verify/frappe_cloud_payload_contract.py`
- `scripts/verify/frappe_cloud_app_mirror_freshness.py`
- `scripts/verify/frappe_cloud_deploy_completion_contract.py`
- `scripts/verify/staging_owner_review_hosted_preflight.py`
- `scripts/verify/release_lock_contract.py`
- `scripts/verify/release_controller_contract.py`
- `scripts/verify/release_claim_language_contract.py`
- `workstreams/release-artifacts/<date>-<target>/`
- `capabilities/failures/release-controller-churn-after-stop.md`

Still mandatory before any provider mutation is reopened:

- `scripts/verify/staging_owner_review_gate.py`
- fresh read-only provider snapshot for the actual staging target
- real read-only `provider-snapshot.json` from
  `scripts/verify/frappe_cloud_provider_snapshot.py` or an equivalent
  artifact-owned Provider Witness command packet, without
  bootstrap/deploy/migrate/cache mutation
- real hosted bootstrap preflight execution and artifact from the actual
  staging target
- current app-root mirror containing the reviewed source preflight module
- real freeze-reopen approval artifact bound to the active lock and staging
  target
- real app mirror pre-sync plan before app_mirror_sync
- real post-deploy/update completion artifact before hosted preflight
- fresh app mirror freshness artifact proving required hosted-preflight source
  files match the app-root mirror
- fresh artifact-backed release plan
- staging bootstrap preflight for hosted constraints
- staging database/account/product/gallery proof on the actual target site

## Completion Criteria

This prevention work is complete only when a fresh run proves:

- release lock blocks provider mutation during forensic freeze;
- required-doc receipt is missing and the controller exits nonzero;
- stringified nested Frappe Cloud payloads fail before API calls;
- the one-failure and two-failure circuit breaker blocks retries;
- artifact-owning triad outputs are required and present;
- owner-review gate fails on zero catalog/users on the actual staging target;
- provider success cannot be reported as owner-review readiness;
- emergency handoff is produced automatically after a failed release attempt;
- no live, DNS, Stripe, Search Console, production indexing, or live checkout
  mutation is reachable from the staging owner-review path.

Current state after the local guard pass: the release lock, payload validator,
controller CLI contract, explicit freeze-reopen approval validator, app mirror
pre-sync/post-sync split, emergency-handoff writer, docs-language gate,
circuit-breaker helper, provider snapshot producer/self-test, post-deploy
completion contract, offline staging owner-review gate contract, owner-review
release-artifact sanitizer, hosted bootstrap preflight/source contract, and
artifact directory contract are implemented locally. The owner-review target is
still not proved, and provider mutation is still blocked.
