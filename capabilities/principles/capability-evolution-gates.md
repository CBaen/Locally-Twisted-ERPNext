---
id: capability-evolution-gates
name: Capability Evolution Gates
schema_version: 2.1
profile: foundation
level: principle
maturity: candidate
scope: capability framework
currently_true: unknown
last_verified: 2026-05-07
used_by: [capability-graduation-ladder]
tags:
  - mutation
  - evolution
  - rollback
  - confidence
  - evidence
---

## What it does

Separates healthy evolution from constant mutation. Capabilities may change,
but trust-bearing changes need a gate.

## When to reach for it

Use this before changing `maturity`, `currently_true`, `verification_level`,
promotion state, dependency watch status, or reusable contract wording.

## How to use it

Before changing a trust-bearing capability field, record or confirm:

1. Evidence: what was inspected, run, observed, or reviewed.
2. Date: when the evidence was gathered.
3. Result: what changed or what the check proved.
4. Confidence: the practical `verification_level`, not a fake percentage.
5. Rollback or revalidation: how to undo, mark stale, or prove the card again
   if the change fails.

If those are missing, keep the change in `kitchen/`, leave the card at
foundation, or mark the affected capability on watch instead of promoting it.

## What it depends on

None.

## Failure modes

- "Everything evolves" becomes a reason to rewrite live guidance casually.
- Agents change a contract but do not record how to recover if it fails.
- Confidence rises because prose improved, not because behavior was verified.
