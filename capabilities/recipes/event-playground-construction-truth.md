---
id: event-playground-construction-truth
name: Event Playground Construction Truth
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted Event Playground and PlayCanvas balloon-construction rendering
currently_true: true
verification_level: 2
last_verified: 2026-05-07
evidence_quality: direct
successful_uses: 1
failed_uses: 0
regressions: 1
depends_on:
  - balloon-material-visual-physics
  - playcanvas-event-builder-stage-physics
used_by:
  - workstreams/event-playground.md
tags:
  - Locally Twisted
  - Event Playground
  - PlayCanvas
  - balloon construction
  - classic quads
---

# Event Playground Construction Truth

Use this recipe before changing Event Playground balloon geometry, renderer code, payload facts, or visual verification.

## Core Rule

The renderer must not invent manufacturing facts.

For classic balloon structures, the smallest visible construction unit is a tied/twisted quad. Every balloon in that quad has a body, neck, and knot/nozzle direction. The neck and knot point toward the shared quad tie center, not generically downward.

Render density is not production math. A visually full PlayCanvas arch or column
may keep a denser render count, but the payload must label it as render density
and keep production estimates separate, candidate-only, and not quote-ready until
Locally Twisted approves the formula.

## Procedure

1. Read `research/design-studio-v2/design-studio-physics-rules.md`.
2. Read `research/design-studio-v2/balloon-material-visual-physics-guide.md`.
3. Check the active workstream: `workstreams/event-playground.md`.
4. Put construction facts in pure modules before renderer code.
5. For Event Playground classic quads, use `src/event-playground-construction.js`.
6. For shared/lab cluster truth, use `src/classic-cluster-geometry.js`.
7. Keep PlayCanvas functions as consumers of construction slots; they may place meshes but must not own tie-center rules.
8. Add or update pure tests before judging the canvas.
9. Keep render counts separate from `production_estimate`.
10. Run the nested package tests and Event Playground browser verifier.
11. Capture screenshots for GL/Jeff when the change is visual.

## Required Construction Invariants

- Classic arches are sequences of quad clusters along a frame.
- Classic columns are stacked quad clusters around a pole/base.
- Adjacent clusters may rotate to make spiral/banded color behavior.
- Every visible balloon in a classic quad has a tie center.
- Neck/knot direction points from the balloon body toward the tie center.
- No Event Playground renderer may default every arch balloon neck/knot downward.
- Organic garland, balloon twisting, drops, and walls need their own construction rules before being promoted as production-plausible.

## Failure Signs

- Arch balloons all point down.
- A classic arch looks like loose round balloons rather than quad clusters on a frame.
- The renderer calculates construction orientation inline instead of consuming tested construction slots.
- A visual bug can pass tests because tests only check canvas nonblank output.
- Payload says `production-plausible` while render facts omit construction basis or orientation basis.
- Payload exposes render balloon counts as quote-ready production counts.

## Verification

From `research/design-studio-v2/event-builder-spike/`:

```powershell
npm run test:classic
npm run build
npm run verify:event-playground
npm run verify:v2
```

From the repo root:

```powershell
npm run test:event-playground
```

The minimum proof is not just a nonblank canvas. Tests must cover pure construction slots and prove quad balloon neck/knot vectors point toward the shared tie center.

## First Regression Captured

On 2026-05-06, GL caught Event Playground arch balloons pointing down. Root cause: the PlayCanvas renderer used a default downward neck/knot vector for every balloon, even inside classic quad clusters. The fix introduced tested construction slots and made the renderer consume tie-center orientation data.
