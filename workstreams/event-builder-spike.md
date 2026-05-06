# Event Builder Spike Workstream

Last updated: 2026-05-06 by Codex.

## Status

Complete as a research-only engine comparison spike. The follow-on internal preview is now `Event Playground` at hidden `/event-playground`; use `workstreams/event-playground.md` for the active route, non-goals, and verification lane.

This original spike is not a production Frappe route. It does not touch `apps/`, customer routes, Leads, checkout, save/share, or ERPNext data. Later files in the same nested package now include separate Event Playground and classic PlayCanvas prototypes; do not confuse those with this engine-comparison receipt.

## Purpose

Compare PlayCanvas and Babylon.js for a fixed-camera, nostalgic isometric corporate-stage builder:

- 24 ft wide x 12 ft deep corporate stage.
- 1 engine unit = 1 ft.
- Fixed orthographic isometric camera, with no customer orbit controls.
- 1 ft tile grid for scale.
- Draggable balloon installations.
- Sales-ready payload shared by both engines.

## Built

Prototype package:

- `research/design-studio-v2/event-builder-spike/`

Primary entry points:

- `playcanvas.html`
- `babylon.html`

Shared core:

- `src/scene-spec.js` owns stage rules, balloon math, piece facts, generated render objects, payload shape, and drag projection math.
- `src/shared-ui.js` owns payload sync, runtime state, and pointer-drag behavior.
- `src/render-playcanvas.js` renders the shared scene through PlayCanvas.
- `src/render-babylon.js` renders the shared scene through Babylon.js.
- `verify_spike.cjs` starts Vite and verifies both engine pages with Playwright.

## Render Facts Captured

- Classic 25 ft arch: 200 balloons, 50 quad clusters, 11 inch balloons, two-color candy-cane spiral.
- Column pair: two 8 ft columns, 64 balloons per column, 128 balloons total.
- Organic garland: 9 ft, 97-balloon planning estimate, 11 inch body balloons, 16/24 inch anchors, 5 inch filler.
- Backdrop wall placeholder: whole-cell dense balloon grid.

## Payload Contract

Both engines produce the same payload except for the `engine` field:

```json
{
  "scene_version": "event-builder-spike-v1",
  "venue": "corporate_stage",
  "engine": "playcanvas|babylon",
  "camera": "fixed_isometric",
  "pieces": [],
  "sales_summary": "Corporate stage concept with arch, columns, and garland."
}
```

The verifier confirms the arch and garland facts specifically because those are the highest-risk math/scale promises.

## Verification

Run from `research/design-studio-v2/event-builder-spike/`:

```powershell
npm run build
npm run verify
```

Latest verified result on 2026-05-03:

- `npm run build` passed.
- `npm run verify` passed.
- Desktop and mobile screenshots for both engines were captured under `output/playwright/design-studio-v2-event-builder-spike/`.
- The verifier checked no console/page errors, nonblank canvas output, fixed-camera runtime state, 1 ft grid facts, payload parity, required render facts, drag-updated placement, and mobile overflow.

## Engine Decision

Both engines passed the spike verifier. Under the agreed rule, the recommendation is PlayCanvas because the long-term product direction is closer to a mini event-space game than a one-off static renderer.

Babylon remains viable as a fallback if future PlayCanvas work fails on production integration, bundle size, or interaction constraints.

## Next Actions

- Historical next action has been completed for the first route: PlayCanvas was chosen and hidden `/event-playground` now mounts the local Event Playground Vite preview in a Frappe iframe.
- Continue from `workstreams/event-playground.md`, not from the engine-comparison spike, for current implementation work.
- Do not add pricing, checkout, or full organic/twisting physics until those production behaviors are separately approved and can be represented honestly.
- Keep balloon construction facts in shared code or shared data; do not duplicate arch/garland math separately per renderer.
