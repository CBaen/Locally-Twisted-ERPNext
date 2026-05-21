---
id: current-truth-needs-evidence
name: Current Truth Needs Evidence
schema_version: 2.0
level: principle
maturity: candidate
scope: capability framework
currently_true: unknown
verification_level: 1
last_verified: 2026-05-05
evidence_quality: direct
successful_uses: 1
failed_uses: 0
regressions: 0
depends_on:
  - evidence-ledger-event
used_by:
  - capability-evidence-and-promotion
  - no-monolith-files
  - source-provenance-and-adoption
  - capability-registry-generation
tags:
  - currently true
  - verification
  - false certainty
  - scope
  - evidence
---

## What it does

Prevents capability files from becoming false certainty by requiring scoped,
repeatable evidence before a claim is treated as currently true.

## When to reach for it

Use this when writing, updating, promoting, or relying on a capability claim
that could drift across projects, tools, machines, or time.

## How to use it

1. State the scope of the claim.
2. Record whether the claim is `true`, `false`, or `unknown` in that scope.
3. Use `currently_true: true` only after at least 3 successful, evidence-backed
   uses with no open regression.
4. Keep `currently_true: unknown` for retrofitted files, remembered claims, old
   handoffs, and untested ideas.
5. If a capability fails, add a downvote, failure, fix, or deprecation event.
6. If scope changes, reassess instead of carrying old certainty forward.

## What it depends on

- [Evidence Ledger Event](../atomic_ingredients/evidence-ledger-event.md) - records the proof events that support or weaken the claim.

## Failure modes

- A true claim in one repo may be false in another.
- A once-true tool instruction may drift after package, API, machine, or project
  changes.
- Three weak uses do not outweigh one unresolved regression.
