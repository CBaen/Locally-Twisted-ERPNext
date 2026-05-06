# PlayCanvas Classic Stage Builder

Last updated: 2026-05-06 by Codex.

## Status

First research implementation exists in `research/design-studio-v2/event-builder-spike/classic-playcanvas.html`.

2026-05-05 correction from GL: the stage must turn and move as one single parent piece, and every added balloon piece must stay anchored to it. The current first implementation is useful but still uses a render-object flattening shortcut for stage view transforms. It needs a stage-root / piece-root PlayCanvas hierarchy refactor before this interaction can be called correct.

2026-05-06 update: tested balloon visual-model modules now capture 11 inch latex balloon data, inflation states, material finish differences, duplet geometry, quad geometry, and nested quad samples. The classic builder renderer now uses body plus neck balloon forms instead of single spheres, but the full contact/soft-body solver is still deferred.

2026-05-06 reset: GL rejected visible contact-cut behavior because it cut balloons instead of pushing them back. The rejected material-lab route was deleted rather than retained as stale code. A rebuilt route now exists at `research/design-studio-v2/event-builder-spike/classic-playcanvas-v2.html`. The v2 route uses official PlayCanvas camera controls, keeps the stage and decor under one `stageRoot`, uses piece roots for decor, puts the camera on the audience side, replaces the solid backdrop with an open stage frame, and uses push-apart packing for classic quad centers. Treat v2 as the forward prototype lane.

This is the next development lane after `workstreams/event-builder-spike.md`. The engine decision is PlayCanvas. Babylon remains a fallback only if PlayCanvas fails on integration, bundle size, or interaction constraints.

This is not a production Frappe route. It does not write Leads, Quotes, checkout records, save/share records, pricing, or ERPNext data.

## Goal

Build a PlayCanvas-based corporate stage planner that feels game-like while staying faithful to professional balloon construction.

The customer should be able to arrange classic balloon decor on a corporate stage, adjust the scene, and produce a construction-aware summary that Jeff can use for follow-up.

## First Slice

Venue:

- Corporate or school stage.
- 24 ft wide x 12 ft deep stage.
- 1 engine unit = 1 ft.
- Fixed orthographic isometric camera.
- 1 ft grid.

Pieces:

- Classic arch.
- Classic column pair.

Interactions:

- Select a piece.
- Drag selected pieces anywhere on the usable stage grid.
- Drag the whole stage view to turn it or move it without changing production placement coordinates.
- Spin selected pieces freely with arbitrary-degree rotation.
- Drag selected pieces in move mode or spin mode.
- Duplicate selected pieces, preserving size, colors, pattern, and construction facts.
- Delete selected pieces.
- Change classic pattern and colors.
- Show warnings for awkward or risky layouts, but preserve customer intent.

Responsive layout:

- Desktop and wide tablet: canvas primary, selected-piece planning sidebar.
- Narrow tablet: canvas primary, collapsible selected-piece drawer.
- Mobile: full-width canvas with selected-piece bottom sheet.
- Small mobile: compact bottom action row for spin, duplicate, delete, and key edit actions.

## Explicitly Out Of Scope

- Organic garland.
- Balloon drop.
- AR or real-room photo overlay.
- Checkout.
- Pricing promises.
- Save/share links.
- Lead or Quote writes.
- Production route exposure.
- Customer orbit camera controls.

Organic work is intentionally deferred because it uses mixed-size doublets, filler, density tiers, controlled randomness, and support-method logic. It should not be collapsed into classic quad math.

## Construction Rules

The first slice uses only the structured classic construction family:

- Classic arch equals quads along a frame.
- Classic column equals quads stacked around a pole.
- Counts must be whole build units.
- Color names are production identifiers.
- Approximate hex values are display aids only.
- The preview is a planning visualization, not a guaranteed engineering drawing.

Classic engine responsibilities:

- Calculate arch clusters and balloon estimates from requested length and balloon size.
- Calculate column clusters and balloon estimates from requested height and balloon size.
- Assign colors at the balloon-slot level while exposing simple piece-level pattern controls.
- Support solid, two-color spiral/swirl, and band/chunk patterns where readable.
- Detect weak or awkward pattern readability.
- Never render classic arches or columns as random loose balloons.

## Placement Rules

The customer can place pieces wherever they want on the stage.

The game should warn instead of blocking when possible:

- Piece extends off the usable stage.
- Pieces overlap.
- Columns are too close to each other to read as a pair.
- Arch rotation or placement no longer reads as an entrance or stage feature.
- Piece appears to block a walkway, performer zone, or obvious stage front.

Hard blocks should be limited to UI/runtime errors such as a piece disappearing outside recoverable bounds.

## Architecture

Keep construction truth outside the PlayCanvas renderer.

Use the PlayCanvas hierarchy for interaction truth:

- `stageRoot` is the single moving parent for stage floor, grid, scrim, lip, and all placed decor.
- Each added decor instance is a `pieceRoot` child of `stageRoot`.
- Balloon clusters and visual geometry are children of the relevant `pieceRoot`.
- Turning or moving the stage updates `stageRoot`, not every child object individually.
- Dragging or spinning a piece updates only that piece's root transform and payload placement/rotation.
- Construction math remains in pure modules and should not depend on PlayCanvas world positions.

Recommended modules:

- `classic-construction.js`: pure structured-quad math for arch and column pieces.
- `scene-state.js`: stage dimensions, view rotation, piece instances, placement, rotation, duplicate/delete, and warning aggregation.
- `payload.js`: construction-aware sales payload.
- `classic-scene-graph.js`: render-tree contract with stage root, piece roots, and local child geometry.
- `render-playcanvas.js`: PlayCanvas scene renderer that builds and updates parent-child entities.
- `ui.js`: selected-piece controls, sidebar/bottom-sheet state, and summary display.

The renderer should consume already-computed scene graph data. It should not own balloon counts, construction basis, color rules, or warning logic.

## Payload Contract

Every piece instance should carry:

- Unique instance ID.
- Product family.
- Construction engine.
- Requested dimensions.
- Render dimensions if different.
- Balloon size preset.
- Pattern.
- Selected color names.
- Approximate display hex values.
- Placement in feet.
- Rotation in degrees, including arbitrary customer spin values.
- Estimated clusters.
- Estimated balloons.
- Warnings.

Scene payload should carry:

- Scene version.
- Venue ID.
- Stage dimensions.
- Grid size.
- Camera type.
- Stage view rotation.
- Piece instances.
- Warnings.
- Plain-language sales summary.

## Verification Expectations

Before calling the first implementation slice complete:

- Run the package build.
- Run automated browser verification at desktop and mobile widths.
- Confirm nonblank PlayCanvas canvas output.
- Confirm no console/page errors.
- Confirm drag updates placement in payload.
- Confirm direct stage turn updates view rotation without changing piece placement.
- Confirm direct stage move updates view pan without changing piece placement.
- Confirm stage turn/pan moves stage geometry and pieces through the `stageRoot` parent.
- Confirm stage turn/pan does not change piece local placement or production payload placement.
- Confirm direct piece spin updates rotation in payload.
- Confirm direct piece drag updates placement in payload.
- Confirm piece drag/spin updates only the selected `pieceRoot`.
- Confirm duplicate creates a new unique instance.
- Confirm delete removes only the selected instance.
- Confirm desktop sidebar does not crush the canvas.
- Confirm mobile bottom sheet does not make the stage unusable.
- Confirm construction facts remain stable across interaction changes.

Current verification commands from `research/design-studio-v2/event-builder-spike/`:

```powershell
npm run test:classic
npm run build
npm run verify:classic
npm run verify:v2
npm run verify
```

Last run by Codex on 2026-05-06:

- `npm run test:classic` passed: 20 tests.
- `npm run build` passed.
- `npm run verify:classic` passed for the first classic route.
- `npm run verify:v2` passed for the rebuilt route.
- `npm run verify` passed for the original engine-comparison spike.

## Source Rules

Use these as the current design and construction references:

- `workstreams/event-builder-spike.md`
- `research/design-studio-v2/playcanvas-event-builder-physics-guide.md`
- `research/design-studio-v2/playcanvas-crown-jewel-research.md`
- `research/design-studio-v2/playcanvas-template-source-intake.md`
- `research/design-studio-v2/balloon-material-visual-physics-guide.md`
- `.codex/capabilities/recipes/playcanvas-event-builder-stage-physics.md`
- `.codex/capabilities/recipes/balloon-material-visual-physics.md`
- `research/design-studio-v2/event-builder-spike/`
- `research/design-studio-v2/design-studio-physics-rules.md`
- `research/contest-customizable-event-decor-tool/PRODUCT-DETAILS.md`
- `research/contest-customizable-event-decor-tool/physics-render-reference/PHYSICS-RENDER-NOTES.md`

Do not treat the older contest mockups as construction truth unless they agree with the physics rules.
