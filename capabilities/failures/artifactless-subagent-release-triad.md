---
name: Artifactless subagent release triad
type: failure
failure_kind: process_failure
schema_version: 0.1
date_discovered: 2026-05-22
last_updated: 2026-05-23
status: open
scope: project
owner_context: Locally Twisted Frappe Cloud staging and release processes
related_capabilities:
  - ../recipes/frappe-cloud-cloudflare-stripe-launch-gate.md
  - ../recipes/take-live-coordinated-workflows.md
related_failures:
  - provider-dashboard-work-bounced-to-gl.md
  - frappe-cloud-release-site-migration-drift.md
  - frappe-cloud-app-mirror-release-scope-drift.md
  - release-controller-churn-after-stop.md
tags:
  - locally-twisted
  - release
  - staging
  - frappe-cloud
  - subagents
  - triad
  - process
  - fail-loud
---

# Failure Recipe: Artifactless Subagent Release Triad

## Symptom

A release, staging, provider, or major-build task appears to have helper agents
or a triad, but the helpers only provide advice. The main agent still owns all
execution decisions, no helper owns a blocking artifact, and a provider
mutation proceeds without a required pre-mutation shape proof or post-mutation
success verifier.

## Trigger conditions

- A release/build failure is already stressful or time-sensitive.
- The main agent spawns read-only helpers but gives them advisory prompts only.
- Helper outputs say "pass", "block", or "recommend" without producing a
  required command, payload, verifier, checklist, patch, or handoff artifact.
- A helper is forbidden from touching every useful artifact class, so the
  Controller gets another opinion but no changed file, executable proof, or
  accepted blocker.
- The main agent treats a helper's opinion as equivalent to release-gate proof.
- Provider APIs, staging, live release, DNS, Stripe, Search Console, or Frappe
  Cloud deployment is in scope.

## Known instances

| Date | Project | Surface | Action being taken | Bad outcome | Evidence | Guard state | Status |
|---|---|---|---|---|---|---|---|
| 2026-05-22 | Locally Twisted | Frappe Cloud staging owner review | Helper agents reviewed Frappe Cloud staging/provider risk while main agent attempted staging update | Helpers did not prevent stale bench assumptions, an invalid API payload shape, or the gap between deploy hash and site update/migration proof because no helper owned a blocking artifact, payload-shape proof, or post-mutation verifier | Active thread facts; `workstreams/frappe-cloud-staging-owner-review-2026-05-22.md`; `capabilities/failures/provider-dashboard-work-bounced-to-gl.md`; `capabilities/failures/frappe-cloud-release-site-migration-drift.md` | missing | open |
| 2026-05-22 | Locally Twisted | Frappe Cloud staging recovery documentation | Worker C was explicitly scoped to failure/capability documentation only | This is the correct narrowed shape for a Recorder, but it also proves the process rule: a release triad is only real when each helper has an action artifact. A read-only-only triad cannot satisfy release control. | This failure card, `frappe-cloud-api-payload-shape-drift.md`, `frappe-cloud-release-site-migration-drift.md`, `frappe-cloud-permission-role-fixture-order-drift.md`, `staging-proof-surface-conflation.md` | Recorder artifact added; enforcement still manual | open |
| 2026-05-23 | Locally Twisted | Frappe Cloud staging release freeze | GL stopped the release process after repeated provider/bootstrap failure classes | The triad pattern did not become an executable release lock, so the process relied on the main controller stopping itself. Future release work must require artifacts that block commands. | `../../workstreams/frappe-cloud-staging-release-failure-forensics-2026-05-23.md`; `release-controller-churn-after-stop.md` | action list written; executable lock still required | open |

## Root pattern

"Having helpers" was mistaken for "having a release control system." Read-only
or advisory subagents can find risks, but they do not stop a provider failure
unless their output is wired into the critical path as a required artifact or
executable verification gate. A helper can be read-only for the dangerous
surface itself, but it still needs to produce an artifact the Controller must
consume: a sanitized provider-state proof, a file patch, a command result, a
blocker receipt, or an explicit no-go section.

The coordination failure is separate from the technical failure. The technical
failures were stale provider mapping, wrong Frappe Cloud API payload shape, and
deploy/hash proof being mistaken for site readiness. The coordination failure
was that no helper owned the exact evidence required before mutation or after
mutation.

## Why it seemed reasonable at the time

The task had multiple helper agents and several pieces of useful advice, so it
looked like the triad rule was being honored. The missing part was ownership:
no helper had an explicit write scope, executable verifier, payload fixture, or
artifact acceptance criterion that could block the main agent.

## Detection signals

- A helper says "pass" without attaching the exact artifact that passed.
- A helper says "block" but the main agent can still proceed without satisfying
  the block.
- The release path has no named controller-owned critical path.
- The provider mutation has no sanitized preflight payload receipt.
- The post-mutation state is described from a deploy/hash/job start instead of
  a terminal site update/migration/cache/app/runtime verifier.
- Subagent prompts are broad research prompts rather than narrow artifact
  prompts with a required output file, command, or validation result.
- A triad is announced, but only the Controller changes files or runs the
  decisive provider checks.

## Required guard

Release triads for LT must use owned roles, not generic helper vibes:

1. Controller owns the critical path, stage boundaries, stop/go decisions, and
   whether every required artifact exists before mutation.
2. Witness owns independent provider-state verification: current team, site,
   bench/group, live separation, running jobs, target app release/hash, and
   mutation safety.
3. Recorder owns docs and handoff parity: current state, old-versus-current
   drift, exact IDs, response IDs, unresolved blockers, and no false-ready
   language.
4. Fixer owns concrete patch/verifier changes: source fixes, focused scripts,
   executable checks, and post-fix proof.

For release/build failures, subagents must have one of these output contracts:

- a narrow write scope in named files;
- an executable verification command with pass/fail output;
- a sanitized payload/response artifact;
- a concrete patch plan with acceptance checks;
- or a blocking handoff section that the Controller cannot bypass.

Read-only is acceptable only for the dangerous surface itself. It is not
acceptable as the whole helper contract. A read-only Witness can still write a
sanitized proof artifact; a Recorder must write the docs; a Fixer must produce
or review concrete source/verifier changes.

Before provider mutation, the Controller must have a sanitized pre-mutation
receipt that proves:

- exact target environment and host;
- exact provider team/account;
- current staging and live site/bench/group mapping;
- no running conflicting job;
- exact apps/sites payload with correct data types;
- and the expected success response shape.

After provider mutation, the Controller must have executable proof that:

- deploy/build reached terminal success;
- site update/migration reached terminal success;
- cache clear or equivalent runtime refresh completed;
- target runtime reports the expected app code/hash/version;
- environment safety flags are correct;
- business/account gates pass;
- and live-only surfaces remained untouched unless explicitly approved.

## Recovery recipe

1. Stop provider/live mutation work until current state is named.
2. Preserve the actual failure sequence in a failure recipe and lane handoff.
3. Split the incident into technical failure and coordination failure.
4. Assign Controller, Witness, Recorder, and Fixer ownership for the recovery.
5. Require Witness provider-state proof before any new mutation.
6. Require Fixer executable verifier output for the failing technical surface.
7. Require Recorder doc parity before any staging-ready or owner-ready claim.
8. Mark the failure open/probation until the next release uses the new artifact
   contract successfully.

## What not to do

- Do not count read-only research as release control.
- Do not count "I asked helpers" as triad compliance unless their artifacts are
  present in the repo, provider evidence packet, or release gate output.
- Do not let a helper recommendation substitute for a required artifact.
- Do not let the main agent proceed past a helper's blocker without recording
  the exact artifact that satisfied it.
- Do not call a deploy candidate, app hash, or job start staging-ready.
- Do not make the triad larger if nobody owns a blocking output.

## Cross-links

- Related capability: `../recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`
- Related capability: `../recipes/take-live-coordinated-workflows.md`
- Related failure: `provider-dashboard-work-bounced-to-gl.md`
- Related failure: `frappe-cloud-release-site-migration-drift.md`
- Related failure: `frappe-cloud-app-mirror-release-scope-drift.md`
- Related workstream: `../../workstreams/frappe-cloud-staging-owner-review-2026-05-22.md`

## Evidence quality

Current evidence is from the active 2026-05-22 LT staging failure thread and
existing LT handoff/failure docs. Provider/live state is intentionally not
modified by this documentation entry. The guard remains open until a future
release proves the owned-artifact triad process end to end.
