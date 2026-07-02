---
id: capability-graduation-ladder
name: Capability Graduation Ladder
schema_version: 2.5
profile: foundation
level: principle
maturity: candidate
scope: capability framework
currently_true: unknown
last_verified: 2026-05-21
depends_on: [capability-evolution-gates, capabilities-should-enhance-not-become-chores]
used_by: [capability-graduation-sweep]
graduation_stage: architecture_backed
graduation_status: active
graduation_required: false
supporting_artifacts: [../SCHEMA.md, ../recipes/capability-graduation-sweep.md, /home/guidingl/projects/capabilities-framework/tools/capability_graduation_audit.py]
graduation_reason: capabilities should become support systems when value or risk justifies it
graduation_review: 2026-05-21
tags:
  - graduation
  - architecture
  - gates
  - automation
  - verifiers
---

## What it does

Turns capabilities from passive references into the right level of support:
skill, verifier, gate, automation, architecture, or release approval boundary.

## When to reach for it

Use this when a capability pattern is repeatedly useful, repeatedly missed,
high-risk to touch accidentally, client-affecting, money-affecting,
publish/live-affecting, or valuable enough that agents should not rely on
memory alone.

## How to use it

Classify the capability at the lowest support level that solves the real
problem:

1. `reference_only` - prose is enough; no support system needed yet.
2. `skill_backed` - agents need a triggerable procedure, scripts, templates, or
   bundled references.
3. `verifier_backed` - the key support is a command or check that proves a
   claim.
4. `gate_backed` - unsafe progress should stop until proof is present.
5. `automation_backed` - repeated safe work should run through a tool, job, or
   packet.
6. `architecture_backed` - the system should make the safe path default, or
   isolate the risky path.
7. `release_live_approval_backed` - public, production, live, client, money,
   account, marketplace, publish, sale, upload, or permission-changing actions
   require explicit approval and proof.

Graduation can protect against harm, strengthen a workflow, reduce cognitive
load, speed repeated work, or create a safer default architecture. It is not
only for danger.

When a card graduates, add optional metadata:

```yaml
graduation_stage: verifier_backed
graduation_status: active
graduation_required: true
supporting_artifacts: [tools/example_verifier.py]
graduation_reason: future agents need proof before trusting this claim
graduation_review: 2026-05-21
```

Run the graduation sweep before and after major capability work:

```bash
python /home/guidingl/projects/capabilities-framework/tools/capability_graduation_audit.py --root capabilities --json
```

Use `--fail-on-required` in repo-local checks only after the project has marked
which cards truly require graduation support.

## What it depends on

- [Capability Evolution Gates](capability-evolution-gates.md) - trust-bearing changes still need evidence and rollback.
- [Capabilities Should Enhance, Not Become Chores](capabilities-should-enhance-not-become-chores.md) - graduation must reduce friction, not add ritual.

## Failure modes

- Treating graduation as paperwork instead of support architecture.
- Overbuilding hard gates for low-risk notes and teaching agents to work
  around the framework.
- Leaving high-risk live, client, money, account, or publish actions as prose
  when they need blocking checks or explicit approval.
- Treating an active graduation stage as proof that the underlying capability
  is currently true.

## Rollback / revalidation path

If a graduation stage creates friction or blocks safe work, downgrade the stage
or mark it `blocked`, record the evidence, and keep the capability itself on
watch until the support system is repaired or retired.
