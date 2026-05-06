---
id: playcanvas-event-builder-stage-physics
name: PlayCanvas Event Builder Stage Physics
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted PlayCanvas event-builder game prototypes
currently_true: yes
verification_level: 1
last_verified: 2026-05-05
evidence_quality: direct
successful_uses: 0
failed_uses: 0
regressions: 0
depends_on:
  - prototype-engine-spike-verification
used_by: []
tags:
  - Locally Twisted
  - PlayCanvas
  - game prototype
  - stage physics
  - transform hierarchy
  - pointer input
---

# PlayCanvas Event Builder Stage Physics

Use this recipe before changing the Locally Twisted PlayCanvas event-builder game, especially anything involving stage turn/pan, piece drag/spin, direct manipulation, picking, camera controls, or balloon construction geometry.

Full guides:

- `research/design-studio-v2/playcanvas-event-builder-physics-guide.md`
- `research/design-studio-v2/playcanvas-crown-jewel-research.md`

## When To Use

- A stage, room, venue, or install surface needs to move as one object.
- Added decor pieces need to stay anchored while the stage turns or moves.
- Customers can drag/spin the stage or drag/spin individual pieces.
- The renderer contains PlayCanvas entity, transform, picking, or camera code.
- A future organic or balloon-drop engine is being discussed and must stay separate from classic quad math.

## Core Rule

Do not flatten stage movement into per-object world-coordinate rewrites.

The PlayCanvas hierarchy must express the interaction:

```text
app.root
  stageRoot
    stage geometry
    pieceRoot
      construction child geometry
```

Stage movement updates `stageRoot`. Piece movement updates the selected `pieceRoot`. Balloon children inherit from their piece root.

## Procedure

1. Read `research/design-studio-v2/playcanvas-event-builder-physics-guide.md`.
2. Read `research/design-studio-v2/playcanvas-crown-jewel-research.md` when the change affects engine choice, gameplay feel, visual fidelity, performance, or future website integration.
3. Check the active workstream: `workstreams/playcanvas-classic-stage-builder.md`.
4. Keep production placement in state/payload stage coordinates, not PlayCanvas world coordinates.
5. Keep construction math in pure modules such as `classic-construction.js`.
6. Build or update a render-tree contract before touching PlayCanvas renderer code.
7. Use shallow PlayCanvas parent-child hierarchy:
   - `stageRoot` owns stage turn/pan.
   - `pieceRoot` owns piece placement/spin.
   - child entities own local balloon/cluster geometry.
8. Use pointer or PlayCanvas mouse/touch input through one gesture state machine.
9. Use picking/raycasting or stage-plane projection to turn screen movement into stage-local movement.
10. Add tests that prove stage movement does not alter piece payload placement.
11. Run browser verification at desktop and mobile widths before calling behavior correct.

## Math Checks

- Normalize arbitrary yaw degrees; do not snap customer spin to 90-degree increments unless a future snap mode is explicit.
- Convert pointer movement through the current view/camera into stage-local deltas before moving a piece.
- Keep piece spin around the piece anchor by rotating the piece root, not every balloon child.
- Keep stage view movement separate from production placement.

## Failure Signs

- `stageRoot` exists but all render objects are destroyed and recreated under it every render.
- Stage turn is implemented by rotating every balloon/grid object manually.
- Piece move works at one camera angle but drifts after the stage is turned.
- Payload placement changes when the customer only rotates or pans the stage view.
- Individual balloons are pick targets for classic first-slice piece selection.
- Organic garland work is added to the classic quad renderer.
- Runtime code depends on a floating PlayCanvas version range without an explicit upgrade decision.
- Visual polish work starts before stage-root anchoring and picking are correct.

## Verification

From `research/design-studio-v2/event-builder-spike/`:

```powershell
npm run test:classic
npm run build
npm run verify:classic
```

Required behavior checks:

- Rotating the stage changes child world positions while preserving payload placement.
- Panning the stage moves stage geometry and pieces together.
- Moving a selected piece changes that piece's stage-local placement.
- Spinning a selected piece changes that piece's stage-local rotation.
- Duplicate/delete operate on whole piece roots.
- Desktop and mobile screenshots show nonblank canvas and usable controls.

## Current Caveat

As of 2026-05-05, the classic PlayCanvas prototype has useful controls and verification but still needs the stage-root/piece-root hierarchy refactor. Do not cite the current passing verifier as proof that the anchored-stage architecture is complete.
