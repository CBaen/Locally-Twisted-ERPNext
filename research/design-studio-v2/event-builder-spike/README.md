# Nostalgic Isometric Event Builder Spike

Research-only prototype comparing PlayCanvas and Babylon.js for a fixed-camera event-space builder.

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

## Verify

From this folder:

```powershell
npm run build
npm run verify
```

The verifier starts Vite on `127.0.0.1:4177`, checks both engines at desktop and mobile widths, verifies the shared sales payload, drags the arch, and writes screenshots under:

```text
../../../output/playwright/design-studio-v2-event-builder-spike/
```

## Decision Rule

If both engines pass the verifier, this spike defaults to PlayCanvas because the long-term direction is closer to a mini event-space game. If PlayCanvas fails and Babylon passes, use Babylon. If both fail, stop and report blockers before building further.

Current verified outcome: both engines pass the spike verifier, so the prototype recommendation is PlayCanvas.
