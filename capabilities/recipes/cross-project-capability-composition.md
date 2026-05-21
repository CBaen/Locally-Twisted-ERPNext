---
id: cross-project-capability-composition
name: Cross-Project Capability Composition
schema_version: 2.1
profile: foundation
level: recipe
maturity: candidate
scope: capability framework
currently_true: unknown
last_verified: 2026-05-07
tags:
  - cross-project
  - hyperlinks
  - backlinks
  - composition
  - multi-root meal
---

## What it does

Makes clear that capabilities are not silos. Ingredients, recipes, meals, and
feasts may link across roots, projects, agents, and subjects when that reflects
how work actually happens.

## When to reach for it

Use this when a capability in one project depends on a capability somewhere
else, or when a meal composes ingredients from multiple roots.

## How to use it

1. Put a composed meal in the consuming capability root: the root that
   references and uses the ingredient chain.
2. If multiple roots consume the same meal, either keep local meal cards in each
   consuming root or create one explicitly shared meal with every consuming root
   linked in metadata and prose.
3. Link ingredients and recipes directly, even when they live in another
   capability root.
4. Add backlinks from the dependency when the relationship is durable enough to
   matter.
5. Use `depends_on` and `used_by` for stable relationships. Use normal Markdown
   links for explanatory or loose relationships.
6. If a linked dependency fails, use watch status on every consuming card that
   inherits the risk.
7. Use optional flat growth metadata when it improves discovery:
   `building_block_type`, `composition_roles`, `portability`, and
   `combination_potential`.
8. Keep those metadata fields descriptive. They can help agents notice unusual
   cross-root combinations, but they do not replace evidence, backlinks, or
   promotion gates.

## What it depends on

- [Failure Cascade And Watch Status](failure-cascade-and-watch-status.md)
- [Hub/Spoke Capability Indexing](hub-spoke-capability-indexing.md)
- [Cross-Root Meal Placement And Trust](cross-root-meal-placement-and-trust.md)

## Failure modes

- Putting the meal where the ingredient lives hides the consuming capability
  owner.
- Avoiding cross-project links causes duplicate, drifting copies.
- Linking without scope makes a local fact look universal.
- Treating a clever metadata match as a trusted dependency creates invisible
  drift. Promote only after evidence and review.
