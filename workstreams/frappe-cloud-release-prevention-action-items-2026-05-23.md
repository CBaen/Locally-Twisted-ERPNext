# Frappe Cloud Release Prevention Action Items - 2026-05-23

Status: **forensic-freeze action list with the first local/offline prevention
guard layer implemented at commit `58258fd`. Do not use this as permission to
deploy.**

This document exists because notes were present, but the release process still
continued. The next agent must convert these items into executable gates before
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
- `scripts/verify/frappe_cloud_provider_snapshot.py`
- `scripts/verify/staging_owner_review_gate_contract.py`
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

Source incident:
`workstreams/frappe-cloud-staging-release-failure-forensics-2026-05-23.md`.

## Absolute Boundaries

- Do not touch live, DNS, Stripe, Search Console, production indexing, or live
  checkout from this action list.
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
    `provider-snapshot.json` artifact. The script has not been run against
    Frappe Cloud in this guard-hardening pass; the next release packet must run
    real read-only mode with current target and rollback hashes before any
    mutation.

## P1 Actions

1. Wire the release lock and owner-review gate into `npm run` scripts so future
   agents discover them through normal package commands. Local prevention is
   now wired as `npm run test:release-prevention`; the real staging gate
   remains `npm run test:staging-owner-review` and must be run only when a
   provider-backed staging verification phase is explicitly reopened.
2. Add a CI-safe docs lint that fails when launch/staging docs say
   owner-review ready without referencing the owner-review gate artifact.
3. Create sanitized provider evidence packet templates under a named
   release-artifacts folder.
4. Add rollback proof to the controller output before any provider mutation.
5. Add a "proof vocabulary" checker for release docs:
   `local`, `GitHub archive`, `app mirror`, `deploy candidate`,
   `site migrate`, `cache/config`, `staging owner-review`, and `live release`
   cannot be used interchangeably.

## Suggested File Targets

These targets are now split between implemented local guards and still-open
future release work.

Implemented local/offline guards:

- `scripts/release/frappe_cloud_release_controller.py`
- `scripts/verify/frappe_cloud_payload_contract.py`
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
controller CLI contract, emergency-handoff writer, docs-language gate,
circuit-breaker helper, provider snapshot producer/self-test, offline staging
owner-review gate contract, hosted bootstrap preflight/source contract, and
artifact directory contract are implemented locally. The owner-review target is
still not proved, and provider mutation is still blocked.
