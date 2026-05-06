# PlayCanvas Event Builder Physics And Math Guide

Last updated: 2026-05-05 by Codex.

Scope: PlayCanvas architecture, transform math, interaction rules, and Codex working practices for the Locally Twisted event-builder game. This guide is for the research prototype and future website integration. It is not a production Frappe route and does not create Leads, Quotes, prices, checkout records, save/share records, or ERPNext data.

## Source Status

Project sources used:

- `research/design-studio-v2/design-studio-physics-rules.md`
- `research/contest-customizable-event-decor-tool/PRODUCT-DETAILS.md`
- `research/contest-customizable-event-decor-tool/physics-render-reference/PHYSICS-RENDER-NOTES.md`
- `workstreams/playcanvas-classic-stage-builder.md`
- `research/design-studio-v2/event-builder-spike/`

Engine sources checked:

- PlayCanvas hierarchy and transformations: <https://developer.playcanvas.com/user-manual/ecs/hierarchy-and-transformations/>
- PlayCanvas manipulating entities: <https://developer.playcanvas.com/tutorials/manipulating-entities/>
- PlayCanvas entity picking: <https://developer.playcanvas.com/tutorials/entity-picking/>
- PlayCanvas ray casting: <https://developer.playcanvas.com/user-manual/physics/ray-casting/>
- PlayCanvas input: <https://developer.playcanvas.com/user-manual/user-interface/input/>
- PlayCanvas orbit camera tutorial: <https://developer.playcanvas.com/tutorials/orbit-camera/>
- PlayCanvas standalone Engine + Vite guidance: <https://developer.playcanvas.com/user-manual/engine/standalone/>
- PlayCanvas optimization, device pixel ratio, profiler, MiniStats, batching, and instancing docs:
  - <https://developer.playcanvas.com/user-manual/optimization/>
  - <https://developer.playcanvas.com/user-manual/optimization/runtime-devicepixelratio/>
  - <https://developer.playcanvas.com/user-manual/optimization/profiler/>
  - <https://developer.playcanvas.com/user-manual/optimization/mini-stats/>
  - <https://developer.playcanvas.com/user-manual/graphics/advanced-rendering/batching/>
  - <https://developer.playcanvas.com/user-manual/graphics/advanced-rendering/hardware-instancing/>
- Deep product/research guide: `research/design-studio-v2/playcanvas-crown-jewel-research.md`
- Balloon material/visual physics guide: `research/design-studio-v2/balloon-material-visual-physics-guide.md`

## Core Correction

The stage must be a single moving parent entity. All stage geometry and placed decor pieces must be children of that parent, so turning or moving the stage moves the whole design together.

Do not fake stage rotation by recalculating every balloon, grid line, and stage part independently. That flattening shortcut can look acceptable in a simple screenshot, but it violates the interaction model the game needs:

- pieces should stay anchored to the stage when the stage moves;
- the stage should behave as one object under the user's hand;
- production placement coordinates should not change when the customer turns the view;
- piece roots should be independently draggable and spinnable while remaining children of the stage.

PlayCanvas is built for this. Entity transforms are local to their parent, world transforms are combined through the hierarchy, and moving a parent affects children. That is the correct model for this game.

## Use PlayCanvas This Way

Use PlayCanvas Engine directly through the repo-owned Vite package. The PlayCanvas Editor can help stage assets, templates, lighting experiments, or GLB checks, but the customer-facing builder logic should live in this repository so it stays testable, reviewable, and Frappe-integrated.

Before production integration, pin the exact PlayCanvas version instead of relying on a broad semver range. The current research package requests `^2.12.3`, while the lockfile resolves to `2.18.1`.

The crown-jewel path is:

1. Correct hierarchy and math.
2. Robust picking and direct manipulation.
3. Beautiful balloon/stage materials.
4. Mobile performance instrumentation.
5. Hidden Frappe route after browser proof.

## Required Entity Hierarchy

Use a shallow hierarchy with clear transform ownership:

```text
app.root
  cameraRig
    camera
  lights
  stageRoot
    stageFloor
    stageGrid
    stageScrim
    stageFrontLip
    pieceRoot:arch_1
      archConstructionRoot
        clusterRoot:0
          balloon slot children
        clusterRoot:1
          balloon slot children
      selectionHandles
      pickCollider
    pieceRoot:column_pair_1
      leftColumnRoot
      rightColumnRoot
      selectionHandles
      pickCollider
```

Transform ownership:

| Layer | Owns | Must not own |
|---|---|---|
| `stageRoot` | user stage turn/pan, whole-stage local movement | balloon counts, piece production placement |
| `pieceRoot` | piece placement in stage feet, arbitrary piece yaw/spin | cluster count formulas, global view math |
| construction child roots | balloon/cluster local offsets and pattern geometry | customer placement or stage movement |
| camera/cameraRig | view inspection and zoom/orbit when used | production coordinates |
| payload/state | production facts and user intent | renderer-only world positions |

## Coordinate Systems

Keep four coordinate systems separate.

1. Stage coordinates in feet: durable customer/product placement. `x_ft` is stage left/right, `y_ft` or `z_ft` is stage depth. This is the payload coordinate system.
2. Piece-local coordinates: construction geometry relative to the piece root. Arch clusters, column quad slots, handles, and collision helpers live here.
3. PlayCanvas world coordinates: the result of stage root and piece root transforms. This is for rendering and picking only.
4. Screen coordinates: pointer positions in CSS pixels. These must be converted through camera rays, stage-plane intersections, or the current projection math before changing stage or piece state.

The payload should store stage coordinates and piece rotations, not the post-transform PlayCanvas world coordinates.

## Rotation And Drag Math

Use free yaw rotation, not 90-degree snapping.

Basic stage-plane yaw:

```text
radians = degrees * pi / 180
x2 = x * cos(radians) - z * sin(radians)
z2 = x * sin(radians) + z * cos(radians)
```

Stage turn:

- user drag changes `stageRoot` yaw or camera orbit, depending on the chosen view mode;
- if the UX says "turn the stage", rotate `stageRoot`;
- if the UX says "look around", orbit the camera around the stage target;
- either way, do not rewrite piece payload placement.

Stage pan:

- if panning the physical stage surface in the viewport, move `stageRoot` as one parent;
- if panning the camera view, move the camera rig target;
- keep the choice explicit in state so payload consumers know it is view state, not production placement.

Piece move:

- raycast or project the pointer onto the stage plane;
- convert the hit point into `stageRoot` local coordinates;
- update the selected `pieceRoot` local position and payload placement;
- clamp only to recoverable bounds, and prefer warnings over hard blocks.

Piece spin:

- keep the piece anchor fixed;
- adjust the selected `pieceRoot` local yaw by arbitrary degrees;
- store the exact normalized rotation in the payload;
- do not rotate every balloon child individually for customer spin. The children inherit the piece-root rotation.

## Picking And Touch Input

Use one interaction state machine for mouse, pen, and touch. Browser Pointer Events can remain the UI-level normalizer. If PlayCanvas engine input is used directly, initialize mouse and touch devices intentionally and guard against duplicate simulated mouse events on Chrome touch devices.

Recommended picking flow:

1. On pointer down, raycast from the camera through the screen point.
2. If a pick collider belongs to a `pieceRoot`, select that piece.
3. If no piece is hit, target the stage plane.
4. Track drag mode: `stage_turn`, `stage_pan`, `piece_move`, or `piece_spin`.
5. On pointer move, update only the owning transform layer.
6. On pointer up/cancel, clear the gesture.

Piece pick colliders should attach to the piece root, not individual balloons, unless the future UX needs balloon-slot editing. Classic first does not need balloon-slot editing.

## Balloon Construction Math

Classic structured decor uses the existing quad rules:

- classic arch equals quads along a frame;
- classic column equals stacked quads around a pole/base;
- colors are assigned to balloon slots and cluster phases;
- counts are whole clusters and whole balloons;
- visual render caps may exist for performance, but the true estimate must stay in the payload.

Visual construction must preserve latex behavior:

- a balloon primitive has body, neck, knot, material finish, and inflation state;
- a quad has center pressure and contact compression;
- adjacent clusters nest by rotation and should not visually intersect;
- 11 inch standard latex is the first baseline, but `nominal_size_in` and `sized_diameter_in` must remain separate;
- color names are production identifiers, while finish/material settings control how the color reads under light.

Organic later must be a separate engine. Organic garlands and organic columns use density tiers, size mix, controlled randomness, support method, and filler/detail layers. They must not be collapsed into classic 4-balloon-cluster math.

Balloon drops are also separate. A drop preview can show package scale and color mix before release, but released balloons cannot promise a stable spatial pattern, stripe, logo, spiral, or post-release arrangement.

## Current Prototype Refactor Target

The current `classic-playcanvas.html` prototype has useful construction math, payload behavior, controls, and browser verification. Its transform model still needs correction before it should be treated as the correct game architecture.

Known problem:

- `classic-scene.js` currently flattens render objects and applies stage view rotation/pan to each object.
- `render-classic-playcanvas.js` destroys and recreates each object under one root instead of maintaining `stageRoot` and `pieceRoot` transform ownership.

Required next refactor:

1. Replace flattened `createClassicRenderObjects` as the renderer contract with a scene graph or render tree contract.
2. Build `stageRoot` once in PlayCanvas and attach floor, grid, scrim, front lip, and every `pieceRoot` as children.
3. Build each piece as a parent entity with balloon/cluster children.
4. Stage turn/pan updates `stageRoot`.
5. Piece move/spin updates only the selected `pieceRoot`.
6. Payload placement remains unchanged when the stage root turns.
7. Verification proves child world positions move through parent transforms while child local transforms and payload placement remain stable.

## Verification Invariants

A prototype is not complete until these are true in automated checks and browser screenshots:

- Rotating `stageRoot` changes child world positions but does not change piece payload placement.
- Panning `stageRoot` moves the stage and all pieces together.
- Moving a selected `pieceRoot` changes only that piece's local placement and payload placement.
- Spinning a selected `pieceRoot` changes only that piece's local yaw and payload rotation.
- Balloon children stay local to their piece root.
- Duplicate creates a new piece root with copied construction facts and a unique ID.
- Delete removes only the selected piece root and its children.
- Desktop and mobile interactions use the same state functions.
- Touch interaction does not double-fire as both touch and mouse.
- Canvas output is nonblank at desktop, tablet, and mobile widths.
- No UI panel blocks the stage on small screens.

## Codex Working Rules

Use this guide before making event-builder game changes.

- Also read `research/design-studio-v2/playcanvas-crown-jewel-research.md`.
- Also read `research/design-studio-v2/balloon-material-visual-physics-guide.md` before changing balloon visuals.
- Keep construction math outside the renderer.
- Keep production coordinates in the state/payload, not in PlayCanvas world transforms.
- Do not flatten a parent-child interaction into per-object world rewrites.
- Build failing pure tests for transform invariants before refactoring renderer code.
- Add browser verification for the exact user path: drag/spin stage, drag/spin piece, duplicate, delete, mobile touch width.
- Keep research routes isolated under `research/design-studio-v2/event-builder-spike/` until GL approves production integration.
- Update `workstreams/playcanvas-classic-stage-builder.md` whenever interaction ownership changes.
- Treat organic and drop physics as future engines, not extensions of the classic renderer.
- If a route, interaction, or canvas state has not been verified in the browser, say so plainly.

## Minimum File Shape For The Refactor

Recommended modules:

```text
src/classic-construction.js
  pure quad/cluster math

src/classic-scene.js
  durable state, payload placement, warnings, duplicate/delete

src/classic-scene-graph.js
  render-tree contract: stageRoot, pieceRoots, child geometry definitions

src/render-classic-playcanvas.js
  PlayCanvas entity creation, parent/child transforms, materials, picking helpers

src/classic-builder-ui.js
  gesture state machine, controls, payload display

test/classic-scene-graph.test.js
  hierarchy and transform ownership tests

verify_classic.cjs
  browser proof at desktop and mobile widths
```

This is enough for classic. Organic should receive its own construction module and scene-graph tests later.
