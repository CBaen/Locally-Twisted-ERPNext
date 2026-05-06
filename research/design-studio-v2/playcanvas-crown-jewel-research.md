# PlayCanvas Crown Jewel Research Guide

Last updated: 2026-05-06 by Codex.

Scope: deeper PlayCanvas research and product guidance for turning the Locally Twisted event builder into a website centerpiece. This is a planning and architecture guide for the game layer. It does not make the current prototype correct by itself.

## Why This Matters

This game cannot be a decorative widget. It is the interactive proof that Locally Twisted understands real event decor at professional scale.

The customer should feel:

- "I can actually design my stage."
- "This is playful enough that I want to keep trying things."
- "This company knows what they are doing."
- "My idea can become a real conversation with Jeff."

The business should get:

- construction-aware intent;
- fewer vague inquiry forms;
- stronger customer confidence;
- a sales payload that is useful without promising impossible physics, pricing, or installation guarantees.

If the physics is wrong, the tool creates bad expectations. If the gameplay is dull, the website loses the feature that should make it memorable.

## Current PlayCanvas Reality

Official docs checked on 2026-05-06:

- PlayCanvas Engine overview: <https://developer.playcanvas.com/user-manual/engine/>
- Engine standalone with Vite: <https://developer.playcanvas.com/user-manual/engine/standalone/>
- Hierarchy and transformations: <https://developer.playcanvas.com/user-manual/ecs/hierarchy-and-transformations/>
- Manipulating entities: <https://developer.playcanvas.com/tutorials/manipulating-entities/>
- Entity picking: <https://developer.playcanvas.com/tutorials/entity-picking/>
- Raycast docs/API: <https://developer.playcanvas.com/user-manual/physics/> and <https://api.playcanvas.com/engine/classes/RigidBodyComponentSystem.html>
- UI input: <https://developer.playcanvas.com/user-manual/user-interface/input/>
- Orbit camera tutorial: <https://developer.playcanvas.com/tutorials/orbit-camera/>
- Loading and unloading assets: <https://developer.playcanvas.com/user-manual/assets/loading-unloading/>
- Supported formats: <https://developer.playcanvas.com/user-manual/assets/supported-formats/>
- Editor workflow: <https://developer.playcanvas.com/user-manual/editor/getting-started/workflow/>
- Batching: <https://developer.playcanvas.com/user-manual/graphics/advanced-rendering/batching/>
- Hardware instancing: <https://developer.playcanvas.com/user-manual/graphics/advanced-rendering/hardware-instancing/>
- Optimization: <https://developer.playcanvas.com/user-manual/optimization/>
- Device pixel ratio: <https://developer.playcanvas.com/user-manual/optimization/runtime-devicepixelratio/>
- Profiler: <https://developer.playcanvas.com/user-manual/optimization/profiler/>
- MiniStats: <https://developer.playcanvas.com/user-manual/optimization/mini-stats/>
- Screens and UI scaling: <https://developer.playcanvas.com/user-manual/user-interface/screens/>

Local package reality:

- `research/design-studio-v2/event-builder-spike/package.json` requests `playcanvas: ^2.12.3`.
- `package-lock.json` currently resolves `playcanvas` to `2.18.1`.
- Before production integration, pin the PlayCanvas version exactly and record the upgrade policy. A crown-jewel site feature should not shift engine behavior because a semver range floated under us.

Balloon visual-physics companion guide:

- `research/design-studio-v2/balloon-material-visual-physics-guide.md`

## Recommendation

Use PlayCanvas Engine directly in the repo with Vite-built modules.

Do not make the PlayCanvas Editor the source of truth for product logic. The Editor can be useful for staging art assets, checking GLBs, lighting experiments, templates, or animator collaboration. The website game itself should remain repo-owned and testable because it must integrate with Frappe, project docs, automated verifiers, and future ERPNext payloads.

This matches PlayCanvas's own standalone guidance: Engine + NPM + Vite is a first-class path, not a hack.

## The Product Shape

Think of the event builder as a "decor stage game" with professional rules.

The first customer experience should be:

1. A real venue surface loads immediately.
2. The customer adds a classic arch or column pair.
3. They drag it, spin it, duplicate it, and change colors without friction.
4. The stage can be turned with mouse or finger like a physical tabletop model.
5. Everything stays anchored.
6. Warnings appear as useful guidance, not scolding.
7. The output is a clear, construction-aware concept Jeff can review.

The satisfying part is not points or cartoon reward loops. The satisfying part is direct control, beautiful motion, believable scale, and immediate visual feedback.

## Core Architecture

Use these layers:

```text
Frappe page shell
  HTML/CSS route, server-safe public content

Builder UI
  controls, bottom sheet/sidebar, selected-piece inspector, summary

Gesture controller
  pointer state, touch/mouse normalization, drag modes, pick results

Scene state
  stage dimensions, selected piece, view state, placements, warnings

Construction engines
  classic quad math
  organic recipe math later
  drop package/representational logic later

Scene graph contract
  stageRoot
  pieceRoots
  local balloon/cluster geometry
  pick colliders

PlayCanvas renderer
  entity creation/update
  parent-child transforms
  materials
  camera/lights
  raycast/picking helpers

Verifier
  unit tests
  Playwright interaction tests
  screenshots
  canvas-pixel checks
  payload checks
```

The construction engines should know nothing about PlayCanvas. The renderer should know nothing about pricing, quote workflow, or balloon-count formulas.

## Transform Law

The stage is a parent entity.

```text
app.root
  cameraRig
  lights
  stageRoot
    stageFloor
    stageGrid
    stageBackWall
    pieceRoot:arch_1
      arch cluster children
    pieceRoot:column_pair_1
      column children
```

Interaction ownership:

- turning the stage changes `stageRoot` yaw;
- moving the stage in the viewport changes `stageRoot` view position or camera rig target;
- dragging a piece changes that `pieceRoot` local position;
- spinning a piece changes that `pieceRoot` local yaw;
- balloon children inherit from their piece root;
- production placement remains stage-local and survives view changes unchanged.

This is not optional. Official PlayCanvas docs say local transforms are relative to the parent, world transforms combine through the hierarchy, and moving a parent affects children. That is exactly the model this game needs.

## Physics Model

Do not use full rigid-body physics for normal stage design placement.

Use math and transform constraints for:

- stage turn/pan;
- piece drag/spin;
- grid placement;
- overlap warnings;
- off-stage warnings;
- construction counts;
- classic arch/column shape generation.

Use raycasting/picking for:

- selecting a piece;
- projecting pointer movement to the stage plane;
- selecting handles;
- possibly placing pieces on future venue surfaces.

Use PlayCanvas/Ammo rigid-body physics only when it solves a real physical problem:

- a future balloon-drop release simulation;
- collision triggers for specialized interactions;
- physics-based demo effects separate from production math.

Do not let simulated physics become the source of production truth. For balloons, production truth is construction method plus customer intent, not whatever a real-time solver happened to do.

## Screen To Stage Math

For a pointer drag, the correct pipeline is:

1. Read pointer position in screen pixels.
2. Convert through the active camera to a ray.
3. Intersect that ray with the stage plane or selected handle plane.
4. Convert the world hit point into `stageRoot` local space.
5. Apply the state change to the correct owner:
   - stage turn: `stageRoot.rotation.y`;
   - stage pan: `stageRoot.position` or camera target;
   - piece move: selected piece local position;
   - piece spin: selected piece local yaw.

Never infer production placement from raw screen delta after the camera or stage has turned unless the delta is converted back through the current transform.

## Camera Strategy

The camera should feel helpful, not like an empty 3D sandbox.

Recommended for the first serious prototype:

- default orthographic isometric view;
- audience-side framing;
- stage turn by dragging empty stage;
- optional camera orbit/look mode only if it does not confuse production placement;
- reset-view control;
- no free-fly camera;
- no perspective distortion that makes stage scale unreadable.

PlayCanvas orbit camera examples support mouse and touch with scroll/pinch zoom. For LT, treat orbit behavior as a view tool, not the core design mechanic. The customer is designing the stage, not piloting a camera.

## Input Strategy

Use one gesture state machine for mouse, pen, and touch.

Recommended modes:

- stage: turn;
- stage: move;
- piece: move;
- piece: spin.

Recommended interaction details:

- pointer down first picks a piece root or stage plane;
- selected piece gets visible handles;
- handles are larger than the visible balloons;
- touch targets stay usable on mobile;
- touch should not double-fire as simulated mouse input in Chrome;
- UI controls stop propagation so clicking a button does not also select the scene.

PlayCanvas UI input docs specifically call out Chrome touch-to-mouse duplication. Keep this in the verifier. Touch bugs here will feel broken to customers immediately.

## Visual Quality Standards

The current primitive spheres are acceptable for early behavior tests. They are not enough for the crown jewel.

The next visual standard is stricter: balloons are sized latex objects under tension, not balls. The first serious primitive is `round_latex_11_standard`, with explicit nominal size, sized diameter, inflation state, neck, knot, material finish, and contact deformation hints.

Visual direction:

- latex balloons should use glossy but not metallic materials;
- balloons need believable squash/variation, knots, and soft highlights;
- balloons need visible neck/knot orientation and contact compression where they twist or press into a cluster;
- standard, pearl, metallic/reflex, jewel, pastel, and oxidized states should not all share one material model;
- stage should feel like a venue surface, not a developer grid;
- lighting should make balloon forms legible;
- materials should stay warm and professional, aligned with the LT style guide;
- color names remain production identifiers; hex values are display approximations.

Asset path:

1. Start with generated primitives for testable geometry.
2. Introduce one reusable 11 inch latex balloon primitive with body, neck, knot, and orientation.
3. Add duplet and quad contact/tension deformation.
4. Use material variants for named colors and finishes.
5. Use GLB assets for stage props, room shells, and any brandable environment pieces.
6. Keep all assets optimized and documented.

PlayCanvas supports GLB as the recommended 3D model format. Use GLB for authored assets, not ad hoc OBJ/FBX in the runtime path.

## Performance Strategy

Performance is part of the design, not a cleanup pass.

Targets:

- fast first load;
- stable interaction latency;
- mobile battery sanity;
- no blank canvas;
- no tab crash from memory pressure;
- graceful reduction on lower-tier devices.

Use PlayCanvas features deliberately:

- static batching for stage/environment geometry where it will not change;
- hardware instancing for repeated balloon meshes when entity count becomes heavy;
- material reuse by color and material type;
- no destroy/recreate-all loop per state update;
- dynamic batches only for groups that actually move;
- asset preload for the first scene essentials;
- runtime loading for optional venue packs or advanced pieces;
- texture compression for larger art assets;
- device pixel ratio caps on mobile;
- MiniStats or profiler during development.

Important tradeoff: hardware instancing is strong for repeated balloons, but official docs note all instances are submitted with no camera frustum culling. For a bounded stage, that is probably fine. For a huge future venue, split instances by piece or zone.

## Gameplay Standards

The game should reward exploration without fake gamification.

Good gameplay here means:

- immediate response under the pointer;
- drag feels anchored, not floaty;
- stage turn feels like rotating a tabletop model;
- duplicate creates a useful next piece, not a random pile;
- warnings explain tradeoffs without blocking intent;
- visual changes preserve construction rules;
- the summary makes the customer's effort feel captured.

Useful delight:

- subtle hover/selection glow;
- ghost preview before placement;
- gentle snap suggestion, not hard snapping;
- animated duplicate offset;
- visible anchor pin for selected piece;
- smooth reset-view motion;
- before/after color changes without layout jump;
- optional "presentation view" that hides controls and lets the customer admire the design.

Bad gamification:

- points for adding balloons;
- rewards that push unbuildable layouts;
- random confetti over a professional sales tool;
- toy-like copy;
- blocking warnings that make the customer fight the tool.

## Construction Engines

Classic first:

- classic arches use 4-balloon quad clusters along a frame;
- classic columns use quads around a pole/base;
- 11 inch standard latex is the first visual baseline;
- packed classic clusters need visible center pressure and contact compression;
- color patterns are slot/cluster math;
- counts are whole clusters and whole balloons;
- stage placement is free with warnings.

Organic later:

- organic garlands and columns use density tiers, size mix, controlled randomness, rigging/support method, and filler/detail layers;
- stable random seed is required for saved concepts;
- no-touching-twins and art-directed massing matter more than clean formula output;
- do not reuse classic quad placement.

Drop later:

- preview the pre-release package and color mix;
- do not promise post-release spatial patterns;
- if simulating release, label it as representational;
- package size, balloon size, net capacity, and color ratio must stay explicit.

## Frappe Integration Path

Keep the game isolated until it earns production trust.

Suggested path:

1. Research package under `research/design-studio-v2/event-builder-spike/`.
2. Hidden Frappe route with no writes.
3. Hidden route with payload download/copy only.
4. Internal save-to-Lead draft action behind review.
5. Public route with clear CTA and no pricing promises.
6. Later: saved design links, if approved.

The first production bridge should capture intent, not automate quote commitments.

Payload should include:

- stage/venue ID;
- stage dimensions;
- view state;
- piece instances;
- construction engine per piece;
- requested dimensions;
- colors by production name;
- cluster/balloon estimates;
- warnings;
- browser/device metadata for debugging.

## Verification Gates

Automated checks must prove the real paths.

Unit tests:

- construction counts;
- color distribution;
- scene graph hierarchy;
- transform ownership;
- warnings;
- payload stability.

Browser tests:

- desktop and mobile load;
- nonblank canvas;
- no console/page errors;
- stage turn by pointer;
- stage pan by pointer;
- piece move by pointer;
- piece spin by pointer;
- duplicate/delete;
- mobile bottom sheet/control usability;
- no horizontal overflow;
- screenshots saved.

Architecture assertions:

- `stageRoot` exists and owns stage geometry plus pieces;
- pieces are children of `stageRoot`;
- balloons are children of piece roots;
- stage turn changes child world positions but not piece payload placement;
- piece move changes only selected piece local placement;
- no per-object stage transform flattening.

Manual review:

- GL reviews screenshots/video after each meaningful interaction change;
- Jeff or professional balloon review is needed before public claims about production feasibility;
- organic and drop engines require their own review, not classic-engine signoff.

## Current Prototype Diagnosis

Useful:

- PlayCanvas is installed and working.
- Vite research page exists.
- Classic construction math exists.
- Payload exists.
- Desktop/mobile verifier exists.
- Direct interaction work exists.

Not yet acceptable:

- balloons are still placeholder-level primitives, not believable latex under tension;
- renderer destroys and recreates child entities every render;
- stage transform is flattened into each render object;
- stage is not yet a true moving parent;
- piece roots are not yet first-class PlayCanvas entities;
- picking is screen-projection based, not robust PlayCanvas raycast/pick collider flow;
- visual fidelity is still prototype-level.

The next code task is still the stage-root anchoring refactor. In parallel or immediately after, keep the source-level balloon material model covered for one 11 inch standard latex balloon, a duplet, a quad, and nested cluster pairs. Visual polish should wait until transform truth is fixed, but visual physics cannot wait until the end. Do not revive the rejected material-lab route as archive-only code.

## Codex Best Practices For This Game

For any future Codex instance:

1. Read this guide and `playcanvas-event-builder-physics-guide.md`.
2. Verify the current code path before claiming behavior.
3. Do not flatten hierarchy transforms.
4. Do not put production math inside renderer code.
5. Write tests before refactoring interaction ownership.
6. Run browser verification after runtime changes.
7. Capture screenshots at desktop and mobile.
8. Say what is unverified.
9. Keep production Frappe writes out until explicitly approved.
10. Treat this as a product system, not a visual demo.

## Recommended Next Three Slices

1. Stage-root anchoring refactor.
   - Build `classic-scene-graph.js`.
   - Update PlayCanvas renderer to maintain entities.
   - Add hierarchy tests and browser assertions.

2. Picking and gesture upgrade.
   - Add pick colliders.
   - Convert pointer rays to stage-local hits.
   - Use selected-piece handles for move/spin.
   - Add touch-specific verification.

3. Balloon material and quad visual-physics lab.
   - 11 inch standard latex primitive.
   - Inflation states.
   - Neck/knot orientation.
   - Duplet/quad contact compression.
   - Finish/material comparison.

4. Visual fidelity pass.
   - Better stage/environment.
   - Lighting/tone mapping pass.
   - Performance instrumentation.

Only after those should we treat the prototype as ready for a hidden website route.
