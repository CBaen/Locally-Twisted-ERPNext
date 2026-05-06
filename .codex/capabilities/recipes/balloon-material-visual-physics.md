---
id: balloon-material-visual-physics
name: Balloon Material Visual Physics
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted event-builder balloon material, shape, tension, and visual fidelity modeling
currently_true: yes
verification_level: 1
last_verified: 2026-05-06
evidence_quality: direct
successful_uses: 0
failed_uses: 0
regressions: 0
depends_on:
  - playcanvas-event-builder-stage-physics
used_by: []
tags:
  - Locally Twisted
  - balloon physics
  - visual fidelity
  - PlayCanvas
  - latex balloons
  - construction rules
---

# Balloon Material Visual Physics

Use this recipe before changing how balloons look in the event-builder game.

Full guide: `research/design-studio-v2/balloon-material-visual-physics-guide.md`.

## When To Use

- A renderer change affects balloon shape, size, color, material, shine, knot, neck, deformation, or contact.
- A new balloon size family is introduced.
- Classic quad cluster visuals are being improved.
- Organic or twisting-balloon visuals are being designed.
- The game is moving from placeholder spheres toward public visual fidelity.

## Core Rule

A balloon is not a generic sphere.

It is a sized latex object with inflation state, material finish, neck/knot orientation, tension, and contact deformation. The renderer may approximate those properties, but it must not erase them.

## Procedure

1. Read `research/design-studio-v2/balloon-material-visual-physics-guide.md`.
2. Keep balloon visual facts in pure modules before renderer code.
3. Start with `round_latex_11_standard`.
4. Store `nominal_size_in` and `sized_diameter_in` separately.
5. Add visible neck/knot/nozzle direction.
6. Add material finish categories before final color polish.
7. Add contact/tension hints at cluster generation time.
8. Render duplets, quads, and nested clusters before broad piece polish.
9. Capture close-up screenshots for GL/Jeff review.
10. Do not launch public visuals until Level 2 or higher on the visual truth ladder.

## Failure Signs

- All balloons are perfect spheres.
- Balloons overlap instead of compressing.
- A quad cluster has no shared center pressure or twist/lock hint.
- All finishes use the same material.
- Reflex/chrome balloons render as metal.
- Organic pieces are random loose circles.
- Twisting balloons reuse the round-balloon primitive.
- The prototype looks acceptable only from one far camera angle.

## Verification

The first verifier for this recipe should prove:

- isolated 11 inch balloon has body, neck, knot, and material;
- under/proper/over-inflated states render differently;
- a duplet has tied/twist orientation;
- a quad has center compression;
- nested clusters rotate and contact without obvious intersections;
- at least standard and reflex/metallic material settings differ visibly;
- screenshots are captured at close-up and stage-view scale.

This recipe is not yet proven by runtime tests. It is a candidate contract for the next material/visual fidelity slice.
