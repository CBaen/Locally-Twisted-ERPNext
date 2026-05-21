---
id: capability-evidence-and-promotion
name: Capability Evidence And Promotion
schema_version: 2.0
level: recipe
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
  - current-truth-needs-evidence
used_by:
  - source-provenance-and-adoption
  - capability-graduation-sweep
tags:
  - capability promotion
  - upvote
  - downvote
  - staple
  - kitchen
  - evidence
---

## What it does

Defines how a capability moves from kitchen idea to foundation, governed,
verified, staple, deprecated, or failure without losing history or inventing
proof.

## When to reach for it

Use this before promoting a capability, marking something as currently true,
adding an upvote or downvote, changing confidence, or retrofitting an older
capability file.

## How to use it

1. Put rough ideas in `kitchen/` with the date, scope, and what would prove them.
2. Promote to a formal level only when the idea has a reusable shape:
   - `atomic_ingredients/` for the smallest behavior, field, event, or check.
   - `ingredients/` for small building blocks.
   - `principles/` for rules that constrain many capabilities.
   - `recipes/` for repeatable workflows.
   - `meals/` for complete project shapes.
   - `feasts/` for mature operating systems composed from multiple meals.
3. New formal files normally start as `profile: foundation` and
   `maturity: candidate`.
4. Upgrade to `profile: governed` when the card carries confidence, promotion,
   repeated-use, or cross-session trust claims.
5. Use `profile: composition` or `profile: cascade` when dependencies and
   inherited risk need watch status.
6. Record compact evidence events after real use.
7. Add an upvote only when the use achieved the intended result, verification
   was recorded, and no known bug, regression, privacy issue, or mismatch was
   introduced.
8. Add a downvote when the capability failed, was mis-scoped, caused friction,
   caused a regression, or needs redesign.
9. Promote to `verified` only after at least 3 successful evidence-backed uses
   in the stated scope with no open regression.
10. Promote to `staple` only after verified behavior becomes the preferred path
   for future work and has survived repeated reuse.
11. Deprecate rather than delete when the history would help future agents avoid
   repeating the same path.
12. Before changing trust-bearing fields, record evidence, date, result,
    confidence, and rollback or revalidation path.
13. When retrofitting old cards, use `evidence_quality: retrofitted` and keep
    unknowns unknown.
14. Treat organic growth opportunities and Perfect Bite candidates as proposals.
    They can become cards or action items only after review, evidence, and the
    normal promotion gates.

## What it depends on

- [Evidence Ledger Event](../atomic_ingredients/evidence-ledger-event.md) - the atomic event format.
- [Current Truth Needs Evidence](../principles/current-truth-needs-evidence.md) - the rule that blocks false certainty.

## Failure modes

- Upvoting without verification turns the system into preference notes.
- Promoting old files from memory alone creates false certainty.
- Treating "evolves" as "mutates constantly" makes rollback and confidence
  impossible to reason about.
- Keeping failed approaches out of the ledger hides useful negative evidence.
- Making feasts too early creates heavy abstractions before the smaller pieces
  have proven themselves.
- Letting a contest score substitute for real use, verification, and rollback
  makes the trust layer decorative.
