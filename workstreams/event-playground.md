# Event Playground Internal Preview Workstream

Last updated: 2026-05-08 by Codex after gating the internal Frappe preview route.

## Status

`/event-playground` is a hidden internal-preview route for the PlayCanvas event-decor planner. It is not in public navigation and is not a customer launch surface yet. The Frappe wrapper now redirects guests to `/login` and requires `Administrator` or `System Manager` before it exposes the local Vite iframe.

OpenClaw now owns the next PlayCanvas/Event Playground pass. For the Locally Twisted website launch lane, treat this workstream as parked unless GL explicitly brings it back into scope.

The isolated PlayCanvas prototype lives in `research/design-studio-v2/event-builder-spike/`. The Frappe route wraps the local Vite preview in an iframe so GL/Jeff/OpenClaw can review the experience without deciding production bundle storage, save/share persistence, pricing, checkout, or Lead automation.

Current naming boundary:

- `Event Playground` remains the internal workstream/route name.
- The browser preview now presents itself as `Plan Custom Decor` because that is the consultative customer language.
- Do not rename the production route or public navigation until OpenClaw/GL deliberately approves a route/name decision.

## Architecture

- PlayCanvas/Vite owns the interactive game runtime.
- Frappe owns only the hidden route shell, iframe boundary, and contact-form handoff.
- Balloon construction truth lives in pure source modules before PlayCanvas renders it. For classic quad slots, use `research/design-studio-v2/event-builder-spike/src/event-playground-construction.js`.
- The iframe sends a `LT_EVENT_PLAYGROUND_CONTACT_HANDOFF` message to the Frappe wrapper.
- The wrapper stores `lt_event_playground_handoff_v1` in Frappe-site `sessionStorage` and redirects to `/contact?intent=quote&source=event-playground`.
- `/contact` pre-fills the existing inquiry form with customer contact details, ISO event date when present, event location/city, Balloon Decor / Events Inquiry services, colors, decor type, package notes, and the free-text design summary.

Current source handoff contract:

- Local payload schema: `event-playground-v2`.
- Future Frappe adapter contract: nested `design_studio_contract.schema_version = design-studio-v1`.
- Recommended future Frappe route in payload metadata: `/plan-custom-decor`.
- Contact fields now include customer name, email, phone, event date, and event city/venue. The Frappe contact form receives ISO `YYYY-MM-DD` event dates in `x_event_date` and event city/venue in `x_event_location`; non-ISO date text stays in the notes summary.
- Render counts are visual planning facts only.
- Production estimates are candidate-only, internal, `quote_ready: false`, and `customer_visible: false` until LT approves formula sources, overage, fill/support method, venue review, safety, and pricing.
- Warnings must travel with the payload. The current required warning is `quote_math_pending_lt_approval`.
- The integration adapter says future submit should create exactly one Lead only after server validation; no current endpoint exists.

## Construction Capability

Use `.codex/capabilities/recipes/event-playground-construction-truth.md` before changing Event Playground geometry, renderer code, payload facts, or visual verification.

Use `.codex/capabilities/recipes/event-playground-planning-contract.md` before changing the payload, warnings, contact handoff, Frappe adapter metadata, or quote-readiness behavior.

Current captured regression: arch balloons were rendering with generic downward neck/knot orientation. That is not a manufacturing-faithful classic quad. The current rule is that each classic quad slot points the balloon neck and knot toward the shared tie center, and the PlayCanvas renderer consumes that tested slot data instead of inventing orientation inline.

Current quote-honesty regression risk: the PlayCanvas render density is fuller than public pro production formulas. That is acceptable only as visual density. It must not become quote math, ERPNext Item quantity, material planning, or customer-visible final balloon count.

## Explicit Non-Goals

- No new DocType.
- No backend save API.
- No Lead/Quote/Sales Order creation from the game.
- No production asset bundle committed under the Frappe app.
- No checkout, pricing, room scanning, CAD, share links, or automatic quote generation.
- No customer-visible final balloon counts from render density.

## Audit Packet

Committed audit notes for OpenClaw and future Codex agents:

- `research/design-studio-v2/audits/visual-gameplay-mobile-desktop-audit.md`
- `research/design-studio-v2/audits/frappe-cloud-integration-audit.md`
- `research/design-studio-v2/audits/manufacturer-physics-audit.md`
- `research/design-studio-v2/audits/next-version-build-notes-2026-05-07.md`

These are research/handoff notes, not production proof. The Frappe Cloud audit did not inspect the live database. Re-run DB/schema checks before implementing save/share/Lead behavior.

## Verification

Nested prototype checks:

```powershell
cd research/design-studio-v2/event-builder-spike
npm run test:classic
npm run build
npm run verify:event-playground
npm run verify:v2
```

Frappe wrapper and handoff check:

```powershell
python scripts/dev/clear_website_cache.py --restart
python scripts/verify/event_playground_gate.py
npm run test:event-playground
```

`event_playground_gate.py` proves guest access redirects/denies without exposing the local iframe URL. The root Playwright spec always runs the guest gate. The authenticated canvas/control/handoff checks require `LT_DESK_TEST_USER` and `LT_DESK_TEST_PASSWORD`; without those env vars they are skipped instead of reopening guest access.

## Next Decisions

Owned by OpenClaw unless GL reassigns this lane:

- Whether `Event Playground` is the final customer-facing name.
- Whether the route should become public, sales-shared only, or remain internal.
- Whether to build a production bundle/deploy strategy for the PlayCanvas app.
- Whether saved designs need a DocType, Frappe File screenshots, private share links, and Desk review.
- Whether `design-studio-v1` becomes the server contract unchanged or is revised before Frappe implementation.
- Which production formulas LT approves for arches, columns, walls, centerpieces, welcome signs, and future organic/twisting work.
- Which additional venues, prop packs, and balloon families can be modeled honestly without faking construction physics.
