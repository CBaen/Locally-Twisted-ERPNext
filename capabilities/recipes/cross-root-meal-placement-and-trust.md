---
id: cross-root-meal-placement-and-trust
name: Cross-Root Meal Placement And Trust
schema_version: 2.1
profile: foundation
level: recipe
maturity: candidate
scope: capability framework
currently_true: unknown
last_verified: 2026-05-07
tags:
  - cross-root
  - meal placement
  - dependency trust
  - composition
  - capability root
---

## What it does

Defines where composed meals live when ingredients come from multiple
capability roots, and how trust changes when any linked ingredient fails.

## When to reach for it

Use this when a meal uses an ingredient from another project, another agent
surface, another feature root, or another subject/domain capability root.

## How to use it

1. Put the meal in the consuming capability root: the root that references the
   ingredient chain and uses the meal for its own work.
2. Do not place the meal at the project level unless the project root is the
   actual consuming capability root.
3. Do not place the meal where an external ingredient happens to live unless
   that root is also the consumer.
4. If multiple roots consume the same meal, either keep local meal cards in each
   consuming root or create one explicitly shared meal with each consuming root
   linked in `used_by`, `related_roots`, tags, and prose.
5. If an external ingredient fails, downgrade or watch every consuming meal that
   inherits that ingredient.
6. If a local ingredient works but the external match fails, treat the
   relationship as the problem to investigate. The composed capability remains
   unreliable until the connection is revalidated.
7. Use `composition_roles`, `portability`, and `combination_potential` as
   discovery hints when an ingredient in one root may strengthen a meal in
   another root. Keep the actual dependency in `depends_on` only after the
   relationship is real enough to track.
8. Use growth and Perfect Bite reports as proposal surfaces. They may bring a
   promising meal to GL or a steward agent, but they do not move the meal's
   trust state.

## What it depends on

- [Visible Capability Root Contract](visible-capability-root-contract.md)
- [Probationary Revalidation](probationary-revalidation.md)

## Failure modes

- Project-level meals hide which capability actually owns the behavior.
- Meals placed with external ingredients look trustworthy to the wrong root.
- Cross-root failures get treated as local success because only one ingredient
  was tested.
- Proposal metadata gets mistaken for an actual ingredient chain.
- A consuming meal is greenlit before the external ingredient has three
  post-repair successful uses.
