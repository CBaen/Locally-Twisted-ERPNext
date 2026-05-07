---
id: frappe-portfolio-proof-reel
name: Frappe Portfolio Proof Reel
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted ERPNext/Frappe portfolio and proof-gallery visual work
currently_true: true
verification_level: 2
last_verified: 2026-05-06
evidence_quality: direct
successful_uses: 3
failed_uses: 1
regressions: 2
depends_on:
  - external-design-reference-translation
  - frappe-public-container-contract
  - cross-browser-motion-visual-verification
  - responsive-container-audit
used_by: []
tags:
  - Locally Twisted
  - portfolio
  - proof gallery
  - Frappe
  - visual QA
---

# Frappe Portfolio Proof Reel

Use this recipe when `/portfolio` or another proof-gallery route is being redesigned from a visual reference or prototype.

First read `external-design-reference-translation`. The portfolio reel is a
special case of that broader rule: the approved Frappe export is the visual and
motion source of truth. Translate fake placeholder content, fake locations,
fake image URLs, and unsafe production details into LT reality, but do not
replace the export's typography, spacing, cursor, hero structure, motion
constants, or side/scale rhythm with generic LT page styling.

## Pattern

1. Preserve the approved Frappe export before preserving older local grid/card UI or later Codex reinterpretations.
2. Keep the editorial serif hero, portfolio row, muted paper/ink palette, custom cursor, slow drift, click-to-front behavior, and small italic captions from the export.
3. Replace only what is fake or unsafe: placeholder image URLs, fake Brooklyn/contact copy, nonexistent sections, and broken asset paths.
4. Translate into Frappe-owned files: route template, route controller, metadata, CSS, JS, optimized images, and verifiers.
5. The real public site header/footer still wrap the Frappe page, but the portfolio body may include the export's internal portfolio row and footer-like contact band as part of the route treatment.
6. Display real installed-work photos with `object-fit: contain`; keep the export's muted frame/image surfaces unless GL rejects that visual treatment.
7. Use optimized derivatives for the public reel, but do not crop proof photos to satisfy layout convenience.
8. Mobile should become a full-width natural-ratio stream with stacked captions, not a tiny desktop reel squeezed into a phone viewport.
9. Keep the reference folder in `research/` while external critique is active. Delete it only after GL approves cleanup.
10. Verify browser behavior, not just source shape. A row of images is a failed translation even if the assets load.

## Locked Reel Contract

For the approved LT portfolio reel, the source of truth is
`research/design_handoff_locally_twisted_portfolio/frappe/`. The locked design
settings are:

- `SETTINGS.density = 1.10`
- `SETTINGS.variant = "drift"`
- `SETTINGS.driftSmoothing = 0.02`
- `SETTINGS.opacitySpeed = 4.0`
- `BASE_UNIT = 640`
- `VERTICAL_SPACING = 80`
- `OVERLAP = 0.55`
- `CENTER_BREATH = 140`

At 1366px wide, the current production baseline has the first left photo around
436px wide, the first right photo around 521px wide, and the first center photo
around 648px wide. Photos begin below the editorial hero and drift/fade in from
the edges as the visitor scrolls. Do not "improve" this into an immediate
three-column masonry grid, a compact `What We Do` header, or a generic
full-opacity card wall.

Use the approved side/scale rhythm in photo-array order:

- sides: `left, right, left, center, left, right, left, right, center, right, left, right, left, right, left, center, left, right, left, right`
- scales: `0.62, 0.74, 0.58, 0.92, 0.60, 0.64, 0.74, 0.58, 0.96, 0.55, 0.62, 0.76, 0.60, 0.62, 0.72, 0.94, 0.56, 0.60, 0.62, 0.78`
- aspect sequence: `4:5, 3:2, 2:3, 16:10, 4:5, 3:4, 5:4, 2:3, 16:9, 3:4, 4:5, 3:2, 4:5, 3:4, 5:4, 16:10, 2:3, 3:4, 4:5, 3:2`

The durable lesson from the failed translation is that "productionizing" a
design by replacing its actual composition with numeric approximations produces
a technically passing page that looks wrong. The approved export's values are
the contract unless GL explicitly changes them.

## Verification Checklist

Run these after editing portfolio layout, image metadata, source/reference translation, or the proof-gallery CSS/JS:

```powershell
python scripts/dev/clear_website_cache.py --restart
npm run test:portfolio-reel
npm run test:layout-fit -- --grep portfolio
npm run test:interactive-layout -- --grep portfolio
```

Also inspect desktop and mobile screenshots before launch claims, especially after photo-order or image-quality changes. For this reel, include Chrome and Brave captures when the failure report or user feedback mentions cross-browser differences.

The latest verified use passed `npm run test:portfolio-reel` (4/4), `npm run test:layout-fit -- --grep portfolio` (13/13), and `npm run test:interactive-layout -- --grep portfolio` (4/4). Fresh screenshots and metrics were captured under `output/playwright/portfolio-export-port-desktop.png`, `output/playwright/portfolio-export-port-scroll.png`, and `output/playwright/portfolio-export-port-mobile.png`. The route-specific verifier now checks the approved export behavior: Google font links, custom cursor, large editorial hero, locked first/second/fourth photo sizes from the `640 * scale * 1.10` math, optimized whole-photo assets, initial fade-in state, scroll-driven drift/opacity, click-to-front behavior, and mobile full-width stream.

## LT Receipt

On 2026-05-06, `/portfolio` moved from a cropped card grid toward a proof-first floating photo reel. The first Codex correction overrode the approved Frappe export with a compact hero and giant immediate columns; GL rejected that as unlike the export. The kept production source is now the live Frappe translation of `research/design_handoff_locally_twisted_portfolio/frappe/` into `apps/locally_twisted/locally_twisted/www/portfolio.html`, `apps/locally_twisted/locally_twisted/www/portfolio.py`, `apps/locally_twisted/locally_twisted/public/css/lt-portfolio-reel.css`, `apps/locally_twisted/locally_twisted/public/js/lt-portfolio-reel.js`, optimized images under `apps/locally_twisted/locally_twisted/public/images/portfolio/optimized/`, and `scripts/verify/portfolio_reel.spec.js`.
