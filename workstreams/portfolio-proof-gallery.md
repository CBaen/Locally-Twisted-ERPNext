# Portfolio Proof Gallery

Last updated: 2026-05-07 by Codex after GL clarified that the collage/movement
was approved, not the copied full page shell.

## Outcome

`/portfolio` is the public proof gallery for LT's installed event work. The
current route keeps the approved collage/movement behavior from the
Claude/Frappe export while returning the page shell to Locally Twisted's current
brand system: native site chrome, compact branded hero copy, sitewide Cormorant
+ Lato fonts, no copied internal nav, no route-local Google font imports, and no
custom cursor artifacts.

## Current State

- `apps/locally_twisted/locally_twisted/www/portfolio.html` renders the native
  Frappe page shell, branded compact portfolio hero, reel mount, no-script
  fallback, empty state, JSON-LD, and LT-translated contact band.
- `apps/locally_twisted/locally_twisted/www/portfolio.py` owns gallery records, display order, optimized image URLs, approved export side/scale/aspect rhythm, metadata, and server-side query filtering for category/event links.
- `apps/locally_twisted/locally_twisted/public/css/lt-portfolio-reel.css` and `apps/locally_twisted/locally_twisted/public/js/lt-portfolio-reel.js` own the shipped reel styling and interaction. Current locked constants: `density = 1.10`, `BASE_UNIT = 640`, `VERTICAL_SPACING = 80`, `OVERLAP = 0.55`, `CENTER_BREATH = 140`, drift smoothing `0.02`, opacity speed `4.0`.
- `apps/locally_twisted/locally_twisted/public/images/portfolio/optimized/` contains web-ready full-aspect WebP derivatives for the reel.
- `scripts/verify/portfolio_reel.spec.js` verifies the current contract: no
  portfolio Google font links, no custom cursor artifacts, no copied internal
  nav, branded compact hero copy, export photo sizing math, optimized image
  usage, fade/drift motion, click-to-front state, visible captions below photos,
  mobile full-width stacking with stacked captions, image aspect handling, query
  filtering, and empty-state layout.
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

Latest local verification on 2026-05-07: backend restarted after controller/CSS
hook work, `python scripts/dev/clear_website_cache.py` completed, the first
aggregate website gate exposed a real mobile compact-hero overflow, and the
follow-up fix passed `npm run test:interactive-layout` 88/88,
`npm run test:portfolio-reel` 4/4, and
`npm run test:layout-fit -- --grep "portfolio fits"` 13/13. Fresh visual
evidence is in `output/playwright/home-portfolio-corrections-20260507/`.

The current receipt specifically checked:

- the first viewport uses LT's compact branded portfolio hero;
- the route does not render the copied internal portfolio row/nav;
- the route has no portfolio-specific Google font links or custom desktop cursor;
- the reel uses the exact approved density/base/spacing/overlap/center-breath constants instead of the rejected compact-hero/giant-column reinterpretation;
- photos drift/fade from the edges and center according to the approved export rhythm;
- captions are visible below the photos and do not cover the product;
- mobile starts with the branded compact hero and then becomes a full-width,
  natural-ratio photo stream with stacked caption text.

## Remaining

- GL/Jeff should review final photo order, image quality, and whether any current photos should be removed before launch.
- Send the production implementation paths back for review against the clarified
  contract: movement/collage fidelity, not full-page-shell fidelity.
- Active designer handoff source: `research/design_handoff_locally_twisted_portfolio/frappe/` and the duplicate `research/a unique portfolio page for a high end corporate balloon events_/design_handoff_locally_twisted_portfolio/`.
- Decide whether the untracked research/reference folders should be deleted, ignored, or committed as source evidence after that critique.
- Capture desktop/mobile screenshots for launch evidence after that review.
- Do not turn this into product checkout, pricing, a fixed service menu, or a
  copied prototype shell. Portfolio remains proof and inquiry support.
