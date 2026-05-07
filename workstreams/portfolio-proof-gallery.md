# Portfolio Proof Gallery

Last updated: 2026-05-06 by Codex.

## Outcome

`/portfolio` is the public proof gallery for LT's installed event work. The current route is a high-fidelity Frappe translation of the approved Claude/Frappe export in `research/design_handoff_locally_twisted_portfolio/frappe/`: editorial portfolio row, large serif hero, muted paper/ink palette, custom desktop cursor, slow drifting photo reel, small italic captions, and real optimized LT install photos.

## Current State

- `apps/locally_twisted/locally_twisted/www/portfolio.html` renders the Frappe page shell, export-style portfolio row, editorial hero, reel mount, no-script fallback, empty state, JSON-LD, and LT-translated contact band.
- `apps/locally_twisted/locally_twisted/www/portfolio.py` owns gallery records, display order, optimized image URLs, approved export side/scale/aspect rhythm, metadata, and server-side query filtering for category/event links.
- `apps/locally_twisted/locally_twisted/public/css/lt-portfolio-reel.css` and `apps/locally_twisted/locally_twisted/public/js/lt-portfolio-reel.js` own the shipped reel styling and interaction. Current locked constants: `density = 1.10`, `BASE_UNIT = 640`, `VERTICAL_SPACING = 80`, `OVERLAP = 0.55`, `CENTER_BREATH = 140`, drift smoothing `0.02`, opacity speed `4.0`.
- `apps/locally_twisted/locally_twisted/public/images/portfolio/optimized/` contains web-ready full-aspect WebP derivatives for the reel.
- `scripts/verify/portfolio_reel.spec.js` verifies the approved export behavior: Google font links, custom cursor, editorial hero, export photo sizing math, optimized image usage, fade/drift motion, click-to-front state, visible captions below photos, mobile full-width stacking with stacked captions, image aspect handling, query filtering, and empty-state layout.
- `package.json` exposes the verifier as `npm run test:portfolio-reel`.
- Research/reference folders for the portfolio design are currently present as untracked files for designer critique. Do not commit raw reference artifacts unless GL explicitly wants them kept as current source material; do not delete them without explicit cleanup approval.

## Verification

Run after portfolio route changes:

```powershell
python scripts/dev/clear_website_cache.py --restart
npm run test:portfolio-reel
npm run test:layout-fit -- --grep portfolio
npm run test:interactive-layout -- --grep portfolio
```

Latest focused local verification on 2026-05-06: `python scripts/dev/clear_website_cache.py` completed; portfolio reel 4/4 passed; layout-fit grep portfolio 13/13 passed; interactive-layout grep portfolio 4/4 passed. Fresh visual evidence from the running Frappe site is under `output/playwright/portfolio-export-port-desktop.png`, `output/playwright/portfolio-export-port-scroll.png`, and `output/playwright/portfolio-export-port-mobile.png`.

The current receipt specifically checked:

- the first viewport uses the approved export's editorial serif hero and internal portfolio row;
- the route has the export's Google font links and custom desktop cursor;
- the reel uses the exact approved density/base/spacing/overlap/center-breath constants instead of the rejected compact-hero/giant-column reinterpretation;
- photos drift/fade from the edges and center according to the approved export rhythm;
- captions are visible below the photos and do not cover the product;
- mobile starts with the editorial hero and then becomes a full-width, natural-ratio photo stream with stacked caption text.

## Remaining

- GL/Jeff should review final photo order, image quality, and whether any current photos should be removed before launch.
- Send the production implementation paths back to the designer for fidelity review against the approved Frappe export.
- Active designer handoff source: `research/design_handoff_locally_twisted_portfolio/frappe/` and the duplicate `research/a unique portfolio page for a high end corporate balloon events_/design_handoff_locally_twisted_portfolio/`.
- Decide whether the untracked research/reference folders should be deleted, ignored, or committed as source evidence after that critique.
- Capture desktop/mobile screenshots for launch evidence after that review.
- Do not turn this into product checkout, pricing, or a fixed service menu. Portfolio remains proof and inquiry support.
