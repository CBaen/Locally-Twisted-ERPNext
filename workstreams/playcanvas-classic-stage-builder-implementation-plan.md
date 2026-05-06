# PlayCanvas Classic Stage Builder Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first PlayCanvas-only classic corporate-stage prototype without touching production Frappe routes.

**Architecture:** Keep the old PlayCanvas/Babylon comparison spike intact. Add a new `classic-playcanvas.html` page backed by pure construction math, scene state, payload generation, a PlayCanvas renderer, and a responsive planning UI. Tests cover the pure math/state first; browser verification covers the canvas interactions and breakpoints.

**Tech Stack:** Vite, PlayCanvas, vanilla JavaScript modules, Node's built-in `node:test`, Playwright via the existing verifier pattern.

---

### Task 1: Classic Construction And Scene Tests

**Files:**
- Create: `research/design-studio-v2/event-builder-spike/test/classic-construction.test.js`
- Create: `research/design-studio-v2/event-builder-spike/test/classic-scene.test.js`
- Modify: `research/design-studio-v2/event-builder-spike/package.json`

- [x] **Step 1: Write failing tests for classic arch/column math**

Test that a 25 ft 11 inch classic arch produces 50 clusters / 200 balloons, that an 8 ft column pair produces 16 clusters per column / 128 total balloons, and that pattern metadata is preserved.

- [x] **Step 2: Write failing tests for scene actions**

Test free drag clamping, arbitrary-degree piece spin, arbitrary-degree stage turn, stage view pan, audience-side camera orientation, duplicate with a new instance ID, delete selected instance, and payload warnings.

- [x] **Step 3: Add `test:classic` script**

Run: `npm run test:classic`

Expected before implementation: fails because modules do not exist.

### Task 2: Pure Classic Engine

**Files:**
- Create: `research/design-studio-v2/event-builder-spike/src/classic-construction.js`
- Create: `research/design-studio-v2/event-builder-spike/src/classic-scene.js`

- [x] **Step 1: Implement classic construction math**

Implement structured-quad arch and column-pair facts with whole build units, color names, display hex values, and pattern metadata.

- [x] **Step 2: Implement scene state**

Implement corporate-stage defaults, selected piece state, drag placement, arbitrary-degree piece rotation, arbitrary-degree stage view rotation, duplication, deletion, and warnings.

- [x] **Step 3: Implement payload builder**

Generate the scene payload defined in `workstreams/playcanvas-classic-stage-builder.md`. Current implementation lives in `classic-scene.js` until payload growth justifies a separate module.

- [x] **Step 4: Run `npm run test:classic`**

Expected after implementation: all classic unit tests pass.

### Task 3: PlayCanvas Classic Renderer And UI

**Files:**
- Create: `research/design-studio-v2/event-builder-spike/classic-playcanvas.html`
- Create: `research/design-studio-v2/event-builder-spike/src/main-classic-playcanvas.js`
- Create: `research/design-studio-v2/event-builder-spike/src/render-classic-playcanvas.js`
- Create: `research/design-studio-v2/event-builder-spike/src/classic-builder-ui.js`
- Create: `research/design-studio-v2/event-builder-spike/src/classic-styles.css`

- [x] **Step 1: Build the classic PlayCanvas page**

Add the corporate stage canvas, selected-piece controls, floating selected-piece actions, responsive sidebar/bottom-sheet behavior, and summary panel.

- [x] **Step 2: Wire interactions**

Support select, direct piece move, direct piece spin, direct stage turn, direct stage move, duplicate, delete, pattern/color changes, and payload sync.

- [x] **Step 3: Keep renderer as consumer**

Renderer consumes generated render objects only; it does not own construction math or warnings.

### Task 4: Browser Verification

**Files:**
- Create: `research/design-studio-v2/event-builder-spike/verify_classic.cjs`
- Modify: `research/design-studio-v2/event-builder-spike/package.json`
- Modify: `research/design-studio-v2/event-builder-spike/README.md`
- Modify: `workstreams/playcanvas-classic-stage-builder.md`

- [x] **Step 1: Add `verify:classic` script**

Run Playwright against `classic-playcanvas.html` at desktop and mobile widths.

- [x] **Step 2: Verify canvas and interactions**

Check nonblank canvas, no console/page errors, no horizontal overflow, direct stage-turn payload update, direct stage-pan payload update, direct piece-move payload update, direct piece-spin payload update, duplicate unique instance, delete selected instance, and mobile controls visibility.

- [x] **Step 3: Run final verification**

Run:

```powershell
npm run test:classic
npm run build
npm run verify:classic
```

Expected: all commands exit 0.

### Task 5: Stage-Root Anchoring Refactor

**Files:**
- Modify: `research/design-studio-v2/event-builder-spike/src/classic-scene.js`
- Create: `research/design-studio-v2/event-builder-spike/src/classic-scene-graph.js`
- Modify: `research/design-studio-v2/event-builder-spike/src/render-classic-playcanvas.js`
- Modify: `research/design-studio-v2/event-builder-spike/src/classic-builder-ui.js`
- Create or modify: `research/design-studio-v2/event-builder-spike/test/classic-scene-graph.test.js`
- Modify: `research/design-studio-v2/event-builder-spike/verify_classic.cjs`
- Modify: `workstreams/playcanvas-classic-stage-builder.md`

- [ ] **Step 1: Write hierarchy tests**

Test that the render contract exposes one `stageRoot`, stage geometry children, and one `pieceRoot` per decor instance. Test that stage view transforms are represented on `stageRoot`, while piece placement and spin are represented on `pieceRoot`.

- [ ] **Step 2: Replace flattened render-object view transforms**

Stop applying stage turn/pan to every render object in `classic-scene.js`. Keep construction geometry local to piece roots and stage geometry local to the stage root.

- [ ] **Step 3: Build PlayCanvas parent-child entities**

Create or update `stageRoot` as the single parent entity. Attach stage geometry and piece roots as children. Attach balloon/cluster geometry under the correct piece root.

- [ ] **Step 4: Update direct manipulation**

Stage drag updates `stageRoot` view transform. Piece drag/spin updates only the selected piece root and payload placement/rotation. Pointer-to-stage math must account for the current stage root transform.

- [ ] **Step 5: Verify anchored behavior**

Run:

```powershell
npm run test:classic
npm run build
npm run verify:classic
```

Expected: verification proves stage turn/pan moves pieces with the stage while preserving their production placement coordinates.

### Task 6: Balloon Material And Quad Visual Physics Lab

**Files:**
- Create: `research/design-studio-v2/event-builder-spike/src/balloon-visual-model.js`
- Create: `research/design-studio-v2/event-builder-spike/src/classic-cluster-geometry.js`
- Create: `research/design-studio-v2/event-builder-spike/test/balloon-visual-model.test.js`
- Modify: `research/design-studio-v2/event-builder-spike/src/render-classic-playcanvas.js`
- Modify: `research/design-studio-v2/event-builder-spike/verify_classic.cjs`
- Modify: `research/design-studio-v2/event-builder-spike/README.md`

- [x] **Step 1: Write visual model tests**

Test that `round_latex_11_standard` stores `nominal_size_in`, `sized_diameter_in`, inflation profile, finish, neck/knot metadata, and deformation inputs separately.

- [x] **Step 2: Write classic cluster geometry tests**

Test that a duplet and a quad produce local balloon slots with center pressure, knot/nozzle direction, and contact hints instead of independent spheres.

- [x] **Step 3: Build source-level material model coverage**

Cover isolated 11 inch balloon states, a duplet, a quad, and two nested clusters in pure modules and tests. Include standard and reflex material comparison without treating latex as metal.

- [x] **Step 4: Update PlayCanvas render primitives**

Render the balloon primitive with body, neck, knot, material finish, and basic contact compression. Keep construction and deformation facts outside the renderer.

- [x] **Step 5: Verify source-level visual truth**

Keep source tests in place for isolated balloon, duplet, quad, and nested cluster contracts. Browser verification belongs to the forward classic routes; rejected lab routes should not be retained as archive-only code.

Completed 2026-05-06:
- Added tested balloon visual model and classic cluster geometry modules.
- Updated the classic PlayCanvas renderer so current balloons render as body plus neck forms instead of single spheres.
- Deleted the rejected material-lab route after GL rejected visible contact-cut behavior.
- Verified with `npm run test:classic`, `npm run build`, `npm run verify:classic`, and `npm run verify:v2`.
