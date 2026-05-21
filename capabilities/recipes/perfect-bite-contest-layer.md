---
id: perfect-bite-contest-layer
name: Perfect Bite Contest Layer
schema_version: 2.3
profile: foundation
level: recipe
maturity: candidate
scope: capability framework
currently_true: unknown
last_verified: 2026-05-21
used_by:
  - source-provenance-and-adoption
tags:
  - perfect bite
  - contest
  - proposal
  - capability composition
  - research brief
---

## What it does

Defines Perfect Bite as a high-bar contest candidate: a proposed combination of
capabilities that may create more value together than they create separately.

## When to reach for it

Use this when agents are reviewing ingredients, recipes, meals, or principles
and need to surface unusually valuable combinations for GL review.

## How to use it

Run the contest report after the growth index has enough metadata or edges to
work with:

```powershell
python tools\capability_perfect_bite_contest.py --root capabilities --root-alias local --json
python tools\capability_perfect_bite_contest.py --root capabilities --root-alias project --related-root shared=C:\Users\<user>\capabilities --json
```

A candidate must include:

- combined ingredient, recipe, meal, feast, or principle refs
- why the combination is better than separate use
- the prize it competes for: speed, safety, revenue, learning, reliability,
  creativity, or leverage
- evidence state, provenance state, and traffic-light status
- failure points and repair path
- reuse scope
- whether current internet, official-source, rights, or provenance/adoption
  review is required

Low-score tag overlap is not enough. A candidate should either have explicit
high `combination_potential` or enough evidence, utility, safety, and novelty
to clear the contest threshold.

Candidate IDs should include root-qualified refs so same-name cards from
different roots do not collide. Research brief holds are emitted when the
candidate depends on current or official-source facts, unchecked or restricted
rights, or external-source provenance that has not been locally verified.

Perfect Bite candidates are report items. They can create action items,
research brief holds, or proposed cards, but they cannot promote themselves or
write trusted capability roots.

## What it depends on

- [Organic Capability Growth](organic-capability-growth.md)
- [Capability Evidence And Promotion](capability-evidence-and-promotion.md)
- [Probationary Revalidation](probationary-revalidation.md)

## Failure modes

- The contest rewards novelty without evidence.
- A candidate with red dependencies is treated like a ready recipe.
- Current facts are stale because no research brief was required.
- Someone else's ingredient is treated as ours without provenance, rights, or
  local-adoption boundaries.

## Rollback / revalidation path

Delete or ignore a weak contest candidate. For a strong one, run any required
research brief, repair red/yellow dependencies, add evidence-backed uses, and
route promotion through the normal gates.
