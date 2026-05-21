---
id: probationary-revalidation
name: Probationary Revalidation
schema_version: 2.1
profile: foundation
level: recipe
maturity: candidate
scope: capability framework
currently_true: unknown
last_verified: 2026-05-07
tags:
  - probation
  - revalidation
  - failure
  - dependency
  - three successes
---

## What it does

Defines what happens after a capability, ingredient, dependency link, or
composed meal fails without creating a permanent scraps archive.

## When to reach for it

Use this when a capability chain breaks, an external ingredient drifts, or a
linked root no longer supports a meal that used to work.

## How to use it

1. Mark the affected card or relationship as `watch_status: probation` when it
   has been repaired enough to retry but not enough to trust.
2. Record the failure in the affected card, evidence ledger, or a short failure
   note only while it is useful for repair or preventing repeated waste.
3. Do not create a permanent scraps pile. If the failed approach is not a
   durable warning or active revalidation target, remove it.
4. Re-test the full chain: atomic ingredients, ingredients, recipes, meals, and
   any external roots named in `depends_on` or prose links.
5. Require three subsequent evidence-backed successful uses before greenlighting
   the card again with `currently_true: true`, `watch_status: clear`, or
   verified/staple maturity.
6. If the local ingredient works but the external linked ingredient fails,
   investigate the connection before blaming the local capability.
7. Treat `probation`, `watch`, `revalidating`, and `unknown` as yellow in
   reports. Yellow can guide work, but it is not greenlit trust.
8. If the meal works but a declared ingredient link fails to resolve, create a
   metadata repair action before changing trust. The broken link may be the
   failure, not the ingredient.
9. Rerun the cascade report after repair and keep the chain on probation until
   the three-success rule is met.

## What it depends on

- [Failure Cascade And Watch Status](failure-cascade-and-watch-status.md)
- [Capability Evolution Gates](../principles/capability-evolution-gates.md)

## Failure modes

- Keeping broken ideas forever makes agents repeat old clutter.
- Deleting all failure context makes agents rediscover the same problem.
- Clearing probation after one lucky success restores trust too early.
- Fixing only the upward meal leaves a lower ingredient uninspected.
- Treating metadata repair as trust repair skips the real revalidation step.
