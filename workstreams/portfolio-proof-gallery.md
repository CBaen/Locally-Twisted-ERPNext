# Portfolio Proof Gallery

Last updated: 2026-05-06 by Codex.

## Outcome

`/portfolio` is the public proof gallery for LT's installed event work. The current route uses large natural-ratio photos in a floating reel instead of cropped card tiles with visible captions. The photos carry the proof.

## Current State

- `apps/locally_twisted/locally_twisted/www/portfolio.html` renders the Frappe page shell, intro, reel mount, no-script fallback, empty state, and JSON-LD.
- `apps/locally_twisted/locally_twisted/www/portfolio.py` owns gallery records, display order, optimized image URLs, real image dimensions, left/right/center reel metadata, metadata, and server-side query filtering for category/event links.
- `apps/locally_twisted/locally_twisted/public/css/lt-portfolio-reel.css` and `apps/locally_twisted/locally_twisted/public/js/lt-portfolio-reel.js` own the shipped reel styling and interaction.
- `apps/locally_twisted/locally_twisted/public/images/portfolio/optimized/` contains web-ready full-aspect WebP derivatives for the reel.
- `scripts/verify/portfolio_reel.spec.js` verifies desktop reel behavior, approved staggered side/scale rhythm, scroll-driven reveal instead of a static row, optimized image usage, mobile full-width stacking, image aspect handling, query filtering, and empty-state layout.
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

Latest focused local verification on 2026-05-06: `/portfolio` returned 200; portfolio CSS, JS, and optimized images returned 200; portfolio reel 4/4 passed; layout-fit grep portfolio 13/13 passed; interactive-layout grep portfolio 3/3 passed. Fresh visual evidence from the running Frappe site is under `output/playwright/portfolio-live-fixed-v3-desktop-hero-1366.png`, `output/playwright/portfolio-live-fixed-v3-desktop-collage-1366.png`, and `output/playwright/portfolio-live-fixed-v3-mobile-390.png`.

## Remaining

- GL/Jeff should review final photo order, image quality, and whether any current photos should be removed before launch.
- Send the production implementation paths back to the designer for critique against the original reference.
- Designer review packet: `research/design_handoff_locally_twisted_portfolio/CODEX_PRODUCTION_REVIEW_PACKET.md`.
- Decide whether the untracked research/reference folders should be deleted, ignored, or committed as source evidence after that critique.
- Capture desktop/mobile screenshots for launch evidence after that review.
- Do not turn this into product checkout, pricing, or a fixed service menu. Portfolio remains proof and inquiry support.
