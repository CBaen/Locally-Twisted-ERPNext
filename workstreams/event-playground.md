# Event Playground Internal Preview Workstream

Last updated: 2026-05-06 by Codex after GL assigned PlayCanvas/Event Playground follow-up to OpenClaw.

## Status

`/event-playground` is a hidden internal-preview route for the PlayCanvas event-decor planner. It is not in public navigation and is not a customer launch surface yet.

OpenClaw now owns the next PlayCanvas/Event Playground pass. For the Locally Twisted website launch lane, treat this workstream as parked unless GL explicitly brings it back into scope.

The isolated PlayCanvas prototype lives in `research/design-studio-v2/event-builder-spike/`. The Frappe route wraps the local Vite preview in an iframe so GL/Jeff can review the experience without deciding production bundle storage, save/share persistence, pricing, checkout, or Lead automation.

## Architecture

- PlayCanvas/Vite owns the interactive game runtime.
- Frappe owns only the hidden route shell, iframe boundary, and contact-form handoff.
- Balloon construction truth lives in pure source modules before PlayCanvas renders it. For classic quad slots, use `research/design-studio-v2/event-builder-spike/src/event-playground-construction.js`.
- The iframe sends a `LT_EVENT_PLAYGROUND_CONTACT_HANDOFF` message to the Frappe wrapper.
- The wrapper stores `lt_event_playground_handoff_v1` in Frappe-site `sessionStorage` and redirects to `/contact?intent=quote&source=event-playground`.
- `/contact` pre-fills the existing inquiry form with customer contact details, Balloon Decor / Events Inquiry services, colors, decor type, package notes, and the free-text design summary.

## Construction Capability

Use `.codex/capabilities/recipes/event-playground-construction-truth.md` before changing Event Playground geometry, renderer code, payload facts, or visual verification.

Current captured regression: arch balloons were rendering with generic downward neck/knot orientation. That is not a manufacturing-faithful classic quad. The current rule is that each classic quad slot points the balloon neck and knot toward the shared tie center, and the PlayCanvas renderer consumes that tested slot data instead of inventing orientation inline.

## Explicit Non-Goals

- No new DocType.
- No backend save API.
- No Lead/Quote/Sales Order creation from the game.
- No production asset bundle committed under the Frappe app.
- No checkout, pricing, room scanning, CAD, share links, or automatic quote generation.

## Verification

Nested prototype checks:

```powershell
cd research/design-studio-v2/event-builder-spike
npm run test:classic
npm run build
npm run verify:event-playground
```

Frappe wrapper and handoff check:

```powershell
python scripts/dev/clear_website_cache.py --restart
npm run test:event-playground
```

The root Playwright spec starts the local Vite preview on `127.0.0.1:4306`, loads `/event-playground`, verifies the iframe canvas is nonblank at mobile and desktop widths, exercises basic controls, and verifies Submit Inquiry lands on `/contact` with the design summary prefilled.

## Next Decisions

Owned by OpenClaw unless GL reassigns this lane:

- Whether `Event Playground` is the final customer-facing name.
- Whether the route should become public, sales-shared only, or remain internal.
- Whether to build a production bundle/deploy strategy for the PlayCanvas app.
- Whether saved designs need a DocType, Frappe File screenshots, private share links, and Desk review.
- Which additional venues, prop packs, and balloon families can be modeled honestly without faking construction physics.
