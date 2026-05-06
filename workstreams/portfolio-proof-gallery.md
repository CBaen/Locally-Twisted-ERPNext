# Portfolio Proof Gallery

Last updated: 2026-05-06 by Codex.

## Outcome

`/portfolio` is the public proof gallery for LT's installed event work. The current route keeps the collage-of-imagery idea from the external prototype, but uses the real LT shell, compact native intro, and site typography. The page opens with a compact `What We Do` hero band plus SEO-useful Utah balloon decor copy, then moves directly into a large, tight three-column field of whole installed-work photos.

## Current State

- `apps/locally_twisted/locally_twisted/www/portfolio.html` renders the Frappe page shell, compact `What We Do` intro, reel mount, no-script fallback, empty state, and JSON-LD.
- `apps/locally_twisted/locally_twisted/www/portfolio.py` owns gallery records, display order, optimized image URLs, larger left/right/center slot rhythm, frequent center-column moments, approved aspect sequence, metadata, and server-side query filtering for category/event links.
- `apps/locally_twisted/locally_twisted/public/css/lt-portfolio-reel.css` and `apps/locally_twisted/locally_twisted/public/js/lt-portfolio-reel.js` own the shipped reel styling and interaction. Current contract: the hero stays around 2.5-3x the live menu/header height or smaller, no giant hero image is introduced, desktop photos are about 1.5x larger than the earlier small reel, and the first viewport starts with left/right/center columns instead of delaying the center image.
- `apps/locally_twisted/locally_twisted/public/images/portfolio/optimized/` contains web-ready full-aspect WebP derivatives for the reel.
- `scripts/verify/portfolio_reel.spec.js` verifies desktop reel behavior, compact `What We Do` hero, no portfolio-specific Google font imports, no custom cursor artifacts, matched page/frame/image backgrounds, larger left/right/center rhythm, optimized image usage, visible captions below photos, mobile full-width stacking with stacked captions, image aspect handling, query filtering, and empty-state layout.
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

Latest focused local verification on 2026-05-06: `python scripts/dev/clear_website_cache.py` completed; portfolio reel 4/4 passed; layout-fit grep portfolio 13/13 passed; interactive-layout grep portfolio 4/4 passed. Fresh visual evidence from the running Frappe site is under `output/playwright/portfolio-tight-after-desktop.png` and `output/playwright/portfolio-tight-after-mobile.png`.

The current receipt specifically checked:

- the first viewport uses a compact `What We Do` hero band, not a huge hero image and not the tall prototype hero;
- the route has no portfolio-specific Google font imports or custom cursor artifacts;
- photos are roughly 1.5x larger on desktop than the earlier small reel, full opacity, tighter to the center, and start immediately in left/right/center columns;
- contained image letterboxing matches the warm page background instead of creating gray slabs;
- captions are visible below the photos and do not cover the product;
- mobile starts with the portfolio hero and then becomes a full-width, natural-ratio photo stream with stacked caption text.

## Remaining

- GL/Jeff should review final photo order, image quality, and whether any current photos should be removed before launch.
- Send the production implementation paths back to the designer only for collage/image-flow critique, not for copying the full prototype styling.
- Active designer handoff source: `research/a unique portfolio page for a high end corporate balloon events_/design_handoff_locally_twisted_portfolio/`, as critique input only.
- Decide whether the untracked research/reference folders should be deleted, ignored, or committed as source evidence after that critique.
- Capture desktop/mobile screenshots for launch evidence after that review.
- Do not turn this into product checkout, pricing, or a fixed service menu. Portfolio remains proof and inquiry support.
