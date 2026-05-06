# Portfolio Proof Gallery

Last updated: 2026-05-06 by Codex.

## Outcome

`/portfolio` is the public proof gallery for LT's installed event work. The V1 route now uses large natural-ratio photos in a floating reel instead of cropped card tiles with visible captions. Filters remain available, but they are quiet utility controls; the photos carry the proof.

## Current State

- `apps/locally_twisted/locally_twisted/www/portfolio.html` renders the reel, filter controls, empty state, CTA, modal, and JSON-LD.
- `apps/locally_twisted/locally_twisted/www/portfolio.py` owns gallery records, display order, real image dimensions, left/right/center reel metadata, inline CSS, and inline JS.
- `scripts/verify/portfolio_reel.spec.js` verifies desktop reel behavior, mobile stacking, image aspect handling, filter relayout, and empty-state layout.
- `package.json` exposes the verifier as `npm run test:portfolio-reel`.
- The temporary generated/reference folder under `research/` was deleted after translation. Do not recreate or commit raw reference artifacts unless they are explicitly current source material.
- `apps/locally_twisted/locally_twisted/fixtures/item_attribute.json` now carries explicit `disabled: 0` values so fixture sync/migrate is not blocked by required ERPNext fields.

## Verification

Run after portfolio route changes:

```powershell
python scripts/dev/clear_website_cache.py --restart
npm run test:portfolio-reel
npm run test:layout-fit
npm run test:interactive-layout
python -m json.tool apps/locally_twisted/locally_twisted/fixtures/item_attribute.json > $null
```

Latest local verification on 2026-05-06: portfolio reel 3/3 passed, layout-fit 260/260 passed, interactive-layout 42/42 passed, fixture JSON parsed, and `bench --site frontend migrate` completed.

## Remaining

- GL/Jeff should review final photo order, image quality, and whether any current photos should be removed before launch.
- Capture desktop/mobile screenshots for launch evidence after that review.
- Do not turn this into product checkout, pricing, or a fixed service menu. Portfolio remains proof and inquiry support.
