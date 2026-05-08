# Portfolio Proof Gallery

Last updated: 2026-05-08 by Codex after GL asked for the portfolio motion to
stop swaying for accessibility while preserving click-to-front pop.

## Outcome

`/portfolio` is the public proof gallery for LT's installed event work. The
current route keeps the approved collage/movement behavior from the
Claude/Frappe export while returning the page shell to Locally Twisted's current
brand system: native site chrome, compact branded hero copy, sitewide Cormorant
+ Lato fonts, no copied internal nav, no route-local Google font imports, and no
custom cursor artifacts. Photos carry the proof by themselves: no captions, no
visible frame wrappers, no forced aspect boxes, and no letterbox stripes. The
reel can animate photos into place and pop a clicked photo forward, but it must
not keep swaying with pointer movement after the visitor is trying to look.
Mobile must still feel like a moving collage stream instead of a static image
stack.

## Current State

- `apps/locally_twisted/locally_twisted/www/portfolio.html` renders the native
  Frappe page shell, branded compact portfolio hero, reel mount, no-script
  fallback, empty state, and JSON-LD. The route-specific Inquire/Studio/Index
  footer block was removed on 2026-05-08 after GL rejected it.
- `apps/locally_twisted/locally_twisted/www/portfolio.py` owns gallery records, display order, optimized image URLs, approved export side/scale/aspect rhythm, metadata, and server-side query filtering for category/event links.
- `apps/locally_twisted/locally_twisted/public/css/lt-portfolio-reel.css` and `apps/locally_twisted/locally_twisted/public/js/lt-portfolio-reel.js` own the shipped reel styling and interaction. Current locked constants: `density = 1.10`, `photoScale = 1.5`, `BASE_UNIT = 640`, `VERTICAL_SPACING = 80`, `OVERLAP = 0.55`, `CENTER_BREATH = 140`, drift smoothing `0.02`, opacity speed `4.0`; photo aspect ratios come from the optimized image dimensions in `PORTFOLIO_REEL_META`. Photo size and reel density are separate controls. Pointer-follow parallax and front-photo pointer tilt are not allowed; click-to-front motion must settle.
- `apps/locally_twisted/locally_twisted/public/images/portfolio/optimized/` contains web-ready full-aspect WebP derivatives for the reel.
- `scripts/verify/portfolio_reel.spec.js` verifies the current contract: no
  portfolio Google font links, no custom cursor artifacts, no copied internal
  nav, branded compact hero copy, export photo sizing math, optimized image
  usage, fade/entry motion, settled click-to-front state, no captions, no frame
  wrappers, 1.5x larger desktop image scale without higher reel density,
  mobile full-width slide-in reveal,
  image aspect handling, query filtering, and
  empty-state layout.
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

Latest local verification on 2026-05-08: `python
scripts/dev/clear_website_cache.py --restart` completed, `npm run
test:portfolio-reel` passed 5/5, `npm run test:layout-fit -- --grep
"portfolio fits"` passed 13/13, and `npm run test:interactive-layout -- --grep
portfolio` passed 6/6. After the route-specific footer block was removed, the
portfolio verifier passed with the footer guard. The new fifth portfolio test
proved the front-photo pop animation still changes transform and then settles so
later pointer movement does not change the front photo. A clean Brave mobile check returned 200 with the
cache-busted `20260508-no-captions-scale-2` assets, 15 photos, 0 frame wrappers,
0 captions, first photo visible at 390px wide, second photo waiting offscreen,
and no page errors. Footer-removal DOM evidence found `.lt-foot` count 0, no
`Portfolio contact` landmark, and none of the rejected footer labels. Fresh
visual evidence is in
`output/playwright/portfolio-brave-mobile-no-captions.png`,
`output/playwright/portfolio-desktop-no-captions-scale.png`, and
`output/playwright/portfolio-desktop-no-captions-scroll.png`; footer-removal
evidence is in `output/playwright/portfolio-footer-removed-desktop.png`.

The current receipt specifically checked:

- the first viewport uses LT's compact branded portfolio hero;
- the route does not render the copied internal portfolio row/nav;
- the route has no portfolio-specific Google font links or custom desktop cursor;
- the reel uses the approved side/scale/spacing/overlap/center-breath rhythm with 1.5x desktop photo scale and the original `density = 1.10` spacing;
- photos drift/fade from the edges and center according to the approved export rhythm;
- the reel does not sway with pointer movement, and a front photo stops moving after the click pop settles;
- captions and visible frame wrappers are absent;
- the route-specific Inquire/Studio/Index footer block is absent;
- image dimensions come from the optimized assets, not forced design-slot aspect boxes;
- mobile starts with the branded compact hero and then becomes a full-width,
  natural-ratio slide-in photo stream, not a static stack.

## Remaining

- GL/Jeff should review final photo order, image quality, and whether any current photos should be removed before launch.
- Send the production implementation paths back for review against the clarified
  contract: movement/collage fidelity, not full-page-shell fidelity.
- Active designer handoff source: `research/design_handoff_locally_twisted_portfolio/frappe/` and the duplicate `research/a unique portfolio page for a high end corporate balloon events_/design_handoff_locally_twisted_portfolio/`.
- Decide whether the untracked research/reference folders should be deleted, ignored, or committed as source evidence after that critique.
- Capture desktop/mobile screenshots for launch evidence after that review.
- Do not turn this into product checkout, pricing, a fixed service menu, or a
  copied prototype shell. Portfolio remains proof and inquiry support.
