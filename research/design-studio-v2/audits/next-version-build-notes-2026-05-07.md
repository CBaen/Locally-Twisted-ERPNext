# Next Version Build Notes — 2026-05-07

## Source audits used

- `audits/visual-gameplay-mobile-desktop-audit.md`
- `audits/frappe-cloud-integration-audit.md`
- `audits/manufacturer-physics-audit.md`

## Build verdict

The next preview keeps the PlayCanvas scene, but reframes it from “open quote/game builder” to **Plan Custom Decor**: a guided planning preview with visible quote-honesty gates and a Frappe integration contract.

## What changed

- Renamed the customer-facing route title from `Event Playground` to `Plan Custom Decor`.
- Added a guided four-step planning strip: venue → pieces → colors → send plan.
- Added event date and city/venue contact fields to support future Frappe Lead mapping.
- Added selected-piece stats for visual render count and quote gate.
- Added warnings/honesty gate UI.
- Upgraded payload schema to `event-playground-v2`.
- Added nested `design_studio_contract.schema_version = design-studio-v1` for a future Frappe adapter.
- Added `integration_adapter` metadata for `/plan-custom-decor`, `save_design`, and `submit_design_inquiry` routing.
- Split render density from production estimate math:
  - render counts preserve the fuller visual density;
  - production estimates are candidate-only and `quote_ready: false` until LT approval.
- Added candidate production math based on audit findings:
  - classic 11-inch arch candidate: 6 balloons/ft + 12% planning overage;
  - classic 11-inch column candidate: 4 balloons/ft per column + 12% planning overage.
- Preserved old `estimated_balloons` fields for compatibility but labeled the safer fields as `render_balloon_count`, `visual_density_basis`, and `production_estimate`.

## Verification run

From `event-builder-spike/`:

- `npm run test:classic` — passed, 24/24 tests.
- `npm run build` — passed.
- `npm run verify:event-playground` — passed; desktop + mobile screenshots generated under `output/playwright/event-playground/`.
- `npm run verify:v2` — passed; existing classic PlayCanvas v2 route still works.

## Known limits

- This is still a research preview, not a Frappe Cloud production route.
- It does not create Frappe DocTypes, save server drafts, create Leads, or post to ERPNext.
- Browser visual inspection through OpenClaw was blocked by local navigation policy, but Playwright verification loaded desktop and mobile, checked no horizontal overflow, checked nonblank canvas, exercised key controls, and captured screenshots.
- Public preview is running locally via Vite at `http://127.0.0.1:5173/event-playground.html` in this session.
