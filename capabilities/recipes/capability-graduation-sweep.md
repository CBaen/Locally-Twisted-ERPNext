---
id: capability-graduation-sweep
name: Capability Graduation Sweep
schema_version: 2.5
profile: foundation
level: recipe
maturity: candidate
scope: capability framework projects
currently_true: unknown
last_verified: 2026-05-21
depends_on: [capability-graduation-ladder, capability-evidence-and-promotion]
used_by: []
graduation_stage: verifier_backed
graduation_status: active
graduation_required: false
supporting_artifacts: [/home/guidingl/projects/capabilities-framework/tools/capability_graduation_audit.py]
graduation_reason: agents need a repeatable audit path for deciding what has become a skill verifier gate automation architecture or release gate
graduation_review: 2026-05-21
tags:
  - graduation
  - audit
  - verifier
  - architecture
  - support
---

## What it does

Audits a capability root for cards that have already graduated, cards that
claim graduation without support artifacts, and cards whose wording suggests
they may need graduation review.

## When to reach for it

Use this after adding or changing capabilities, before a broad repo capability
sweep, when a lesson feels too important to remain prose, or when a project
starts accumulating gates, verifiers, automations, templates, or architecture
around a capability.

## How to use it

Run the read-only audit from the framework source package or a project that has
the tool available:

```bash
python /home/guidingl/projects/capabilities-framework/tools/capability_graduation_audit.py --root <project>/capabilities --json
```

For a project that has already marked some cards with
`graduation_required: true`, use the blocking mode in local checks:

```bash
python /home/guidingl/projects/capabilities-framework/tools/capability_graduation_audit.py --root <project>/capabilities --json --fail-on-required
```

Interpret the output this way:

- `graduation_candidates` are proposals, not edits.
- `required_blockers` are cards that already say graduation is required but do
  not yet name enough actionable metadata.
- `active_without_artifacts` means a card claims an active support stage but
  does not point at the supporting skill, verifier, gate, automation, template,
  or architecture.

After the audit, create small action packets. Do not mass-retrofit every card.
Use the lightest graduation stage that reduces real future friction.

## What it depends on

- [Capability Graduation Ladder](../principles/capability-graduation-ladder.md) - the support-stage model.
- Source package tool:
  `/home/guidingl/projects/capabilities-framework/tools/capability_graduation_audit.py`.

## Failure modes

- Treating audit suggestions as automatic promotion.
- Marking `graduation_required: true` everywhere and creating noise.
- Claiming `graduation_status: active` without a real artifact that future
  agents can run, inspect, or follow.
- Forgetting that a support system may strengthen or automate work, not only
  block dangerous work.

## Rollback / revalidation path

If the audit produces false positives, keep the card unedited and record the
reason in the project workstream. If a card was over-graduated, change
`graduation_status` to `blocked` or `retired`, add evidence, and rerun the
audit.
