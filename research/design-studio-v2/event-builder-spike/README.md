# Nostalgic Isometric Event Builder Spike

Research-only prototypes for fixed-camera event-space builder work.

This folder now contains:

- `playcanvas.html` and `babylon.html`: the original engine-comparison spike.
- `classic-playcanvas.html`: the first classic-only PlayCanvas corporate-stage builder slice.
- `classic-playcanvas-v2.html`: the rebuilt classic stage-builder route using official PlayCanvas camera controls, a real `stageRoot`, piece roots, and push-apart balloon packing.
- `event-playground.html`: the hidden-route/OpenClaw handoff preview. It uses
  `Plan Custom Decor` copy, emits `event-playground-v2`, includes a nested
  `design-studio-v1` future Frappe adapter contract, and keeps quote math
  gated behind LT review.

This is not a Frappe route. It does not create Leads, save designs, share links, quote prices, touch checkout, or write ERPNext data.

## Run

From this folder:

```powershell
npm install
npm run dev
```

Open:

- `http://127.0.0.1:5173/playcanvas.html`
- `http://127.0.0.1:5173/babylon.html`
- `http://127.0.0.1:5173/classic-playcanvas.html`
- `http://127.0.0.1:5173/classic-playcanvas-v2.html`
- `http://127.0.0.1:5173/event-playground.html`

## Verify

From this folder:

```powershell
npm run build
npm run verify
npm run test:classic
npm run verify:classic
npm run verify:v2
npm run verify:event-playground
```

The original verifier starts Vite, checks both engine-comparison pages at desktop and mobile widths, verifies the shared sales payload, drags the arch, and writes screenshots under:

```text
../../../output/playwright/design-studio-v2-event-builder-spike/
```

The classic verifier checks `classic-playcanvas.html` at desktop and mobile widths, verifies nonblank PlayCanvas output, confirms no horizontal overflow, exercises direct stage turn, direct stage move, direct piece move, direct piece spin, duplicate, and delete, and verifies the classic-only payload. It writes screenshots under:

```text
../../../output/playwright/design-studio-v2-classic-stage-builder/
```

The v2 verifier checks `classic-playcanvas-v2.html` at desktop and mobile widths, verifies nonblank PlayCanvas output, confirms no horizontal overflow, turns the full stage through `stageRoot`, duplicates and deletes the selected piece, and writes screenshots under:

```text
../../../output/playwright/design-studio-v2-classic-stage-builder-v2/
```

The Event Playground verifier checks `event-playground.html` at desktop and
mobile widths, verifies nonblank and visually varied PlayCanvas output, confirms
no horizontal overflow, checks the `event-playground-v2` payload and
`design-studio-v1` adapter contract, verifies the quote-honesty warning, and
exercises rotate, duplicate, delete, and color update behavior. It writes
screenshots under:

```text
../../../output/playwright/event-playground/
```

## Decision Rule

If both engines pass the verifier, this spike defaults to PlayCanvas because the long-term direction is closer to a mini event-space game. If PlayCanvas fails and Babylon passes, use Babylon. If both fail, stop and report blockers before building further.

Current verified outcome: both engines pass the spike verifier, so the prototype recommendation is PlayCanvas.

## Classic PlayCanvas Slice

`classic-playcanvas.html` is the first PlayCanvas-only implementation direction after the engine decision.

`classic-playcanvas-v2.html` is the rebuild direction after the first lab proved the wrong contact behavior. It uses official PlayCanvas camera controls and a simpler full-canvas UX. The stage and decor are parented under one `stageRoot`, and classic balloon clusters use push-apart packing for balloon centers instead of visual cut patches.

Scope:

- Corporate stage, 24 ft x 12 ft, fixed isometric camera, 1 ft grid.
- Classic arch and classic column pair only.
- Free drag placement.
- Free stage turn and stage move without changing production placement coordinates.
- Free piece move and piece spin with mouse/touch pointer gestures.
- Precision sliders for stage turn and selected-piece spin.
- Duplicate and delete selected pieces.
- Desktop planning sidebar and mobile bottom sheet.
- Construction-aware payload using structured 4-balloon quad rules.
- Balloon bodies render as latex body plus neck forms rather than single spheres.

Deferred:

- Organic garland.
- Balloon drop.
- AR/photo overlay.
- Save/share, Lead writes, Quote writes, pricing, checkout, and production route exposure.
- Customer-visible final balloon counts from render density.

## Event Playground / Plan Custom Decor Contract

`event-playground.html` is the forward OpenClaw handoff preview. It is still a
research preview. It is not a production route, not a save/share flow, and not a
quote engine.

Rules:

- Local schema is `event-playground-v2`.
- Nested future Frappe contract is `design-studio-v1`.
- Render counts are visual planning density only.
- Production estimates are candidate-only, internal, `quote_ready: false`, and
  `customer_visible: false`.
- Final balloon count, install method, safety, pricing, and availability are
  confirmed by Locally Twisted before booking.
- Future Frappe submit must validate server-side and create exactly one Lead
  only after required contact and design facts pass validation.

## Balloon Visual Model

The rejected material-lab route was deleted. The useful durable pieces remain as pure source modules and tests:

- 11 inch round latex is modeled as a sized balloon with body, neck, knot, material, inflation, tension, and contact metadata.
- Inflation samples distinguish underinflated, properly inflated teardrop, and overinflated states.
- Standard, reflex, pearl, and jewel finishes use different latex material responses; all keep metalness at zero.
- Duplets, classic quads, and nested quads come from tested cluster geometry instead of hand-placed spheres.

Do not revive contact flattening as a visible cut patch. The forward prototype is `classic-playcanvas-v2.html`, with push-apart packing as the first acceptable classic-cluster behavior.
