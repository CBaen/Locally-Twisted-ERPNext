---
name: Release controller churn after stop
type: failure
failure_kind: process_failure
schema_version: 0.1
date_discovered: 2026-05-23
last_updated: 2026-05-23
status: open
scope: project
owner_context: Locally Twisted Frappe Cloud staging owner-review release
related_capabilities:
  - ../recipes/frappe-cloud-cloudflare-stripe-launch-gate.md
  - ../recipes/take-live-coordinated-workflows.md
related_failures:
  - artifactless-subagent-release-triad.md
  - staging-proof-surface-conflation.md
  - frappe-cloud-api-payload-shape-drift.md
  - frappe-cloud-release-site-migration-drift.md
  - frappe-cloud-permission-role-fixture-order-drift.md
tags:
  - locally-twisted
  - release
  - staging
  - frappe-cloud
  - provider
  - process
  - forensic-freeze
---

# Failure Recipe: Release Controller Churn After Stop

## Symptom

A release process keeps patching, polling, deploying, bootstrapping, or
reframing progress after the correct next action is to stop. The session may
produce useful fixes, but it is no longer a trustworthy release controller.

## Trigger Conditions

- Frappe Cloud, staging, live, DNS, Stripe, Search Console, or provider work is
  active.
- One provider/bootstrap failure has already happened.
- A second related failure appears, or GL explicitly says stop.
- The controller keeps treating "one more check" or "one more fix" as harmless.
- Docs have stop rules, but they are prose instead of executable locks.

## Known Instances

| Date | Project | Surface | Bad outcome | Evidence | Guard state |
|---|---|---|---|---|---|
| 2026-05-22/23 | Locally Twisted | Frappe Cloud staging owner-review push | The release controller continued through repeated payload, migration, role, data, and hosted-bootstrap failures instead of freezing release execution and producing prevention gates first | `../../workstreams/frappe-cloud-staging-release-failure-forensics-2026-05-23.md`; `../../workstreams/frappe-cloud-release-prevention-action-items-2026-05-23.md`; `../../release_locks/locally-twisted-staging-forensic-freeze.json` | local executable lock/controller/provider-snapshot/owner-gate/bootstrap contracts added; provider mutation remains blocked |

## Root Pattern

Warnings were present, but the system had no mechanical stop. A human-readable
doc can tell an agent to stop, but it does not prevent release mutation unless
release scripts check a lock, enforce circuit breakers, and require evidence
artifacts before proceeding.

## Detection Signals

- "Staging deployed" is used near "owner-review ready" without the owner-review
  gate output.
- A provider request is sent without a sanitized payload artifact.
- A retry follows a failed provider/bootstrap attempt before the failure class
  has a written guard.
- A triad is named, but no witness artifact exists.
- GL says stop and the next action is polling, deploying, bootstrapping, or
  asking for another provider detail.
- A release lock lists reopen requirements but has no executable reopen
  transition or approval-artifact validator.
- A precondition requires proof that can only exist after the blocked action
  runs, such as requiring passing app mirror freshness before app mirror sync.
- Request payload validation is treated as provider job completion proof.
- Release packet artifacts include raw previous traceback text instead of a
  sanitized current-state summary.

## Required Guard

- Add a machine-readable forensic-freeze lock.
- Add a release controller that refuses mutation while the lock is active.
- Add a one-failure and two-failure circuit breaker.
- Require read receipts for the relevant forensics/action-item docs.
- Require artifact-owning triad outputs before mutation.
- Require owner-review readiness to come only from the staging owner-review
  gate, not from app hashes, deploy IDs, or local proof.
- Provide an explicit freeze-reopen transition and contract test before
  provider mutation can resume.
- Split app mirror sync into pre-sync approval/source proof and post-sync
  freshness proof.
- Require a post-deploy/update completion artifact before hosted preflight.
- Sanitize owner-review gate artifacts used in release packets.

Current local guard implementation:

- `../../release_locks/locally-twisted-staging-forensic-freeze.json`
- `../../scripts/release/frappe_cloud_release_controller.py`
- `../../scripts/verify/release_lock_contract.py`
- `../../scripts/verify/release_controller_contract.py`
- `../../scripts/verify/frappe_cloud_payload_contract.py`
- `../../scripts/verify/frappe_cloud_provider_snapshot.py`
- `../../scripts/verify/frappe_cloud_deploy_completion_contract.py`
- `../../scripts/verify/staging_owner_review_gate_contract.py`
- `../../scripts/verify/staging_owner_review_bootstrap_contract.py`
- `../../scripts/verify/release_claim_language_contract.py`
- `npm run test:release-prevention`

This is still not provider proof. It is the local stop layer future release
work must satisfy before a fresh release plan can reopen mutation.

As of the follow-up guard closure, the local stop layer also prevents the
specific reopen failure modes discovered after `ebb7151`: mutation requires a
freeze-reopen approval artifact, app mirror sync has separate pre-sync and
post-sync gates, staging bootstrap requires a post-deploy/update completion
artifact, and owner-review release artifacts can be sanitized with
`--release-artifact`.

As of `f5e2e91`, the staging-freeze release packet template also names those
required artifacts and includes their validator-shaped examples. This prevents
the next release packet from starting from stale prose, but it is not a real
approval or provider/staging artifact.

## Recovery Recipe

1. Stop mutation immediately.
2. Record current known provider/source state without assuming final state.
3. Write or update the forensic timeline.
4. Write action items that become executable gates.
5. Update queue, handoffs, decisions, lessons, capabilities, and coordination
   docs with backlinks.
6. Implement and run the offline release-prevention gates.
7. Commit and push the documentation/action-item state if repo workflows do not
   deploy.
8. Reopen release only under a new release controller and fresh read-only
   current-state snapshot.
9. Before reopening, prove the controller is not deadlocked by impossible
   preconditions and that every release-packet artifact is sanitized.
10. Confirm the copied release packet template matches the current controller
    contracts before producing real artifacts.

## Cross-links

- `../../workstreams/frappe-cloud-staging-release-failure-forensics-2026-05-23.md`
- `../../workstreams/frappe-cloud-release-prevention-action-items-2026-05-23.md`
- `../../release_locks/locally-twisted-staging-forensic-freeze.json`
- `../recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`
- `artifactless-subagent-release-triad.md`
- `staging-proof-surface-conflation.md`

## Evidence Quality

This entry is documented from the 2026-05-22/23 release failure and local repo
state. It does not prove current Frappe Cloud staging state. Future release
work must start with a fresh read-only provider snapshot.
