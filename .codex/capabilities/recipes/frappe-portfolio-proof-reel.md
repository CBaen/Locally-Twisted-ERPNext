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
successful_uses: 2
failed_uses: 1
regressions: 1
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
special case of that broader rule: the designer reference is the visual contract,
while the kept production source is the Frappe implementation.

## Pattern

1. Preserve the approved photo-placement behavior before preserving older local UI.
2. Do not reintroduce cards, boxed grids, visible captions over photos, or modal/filter UI unless GL explicitly asks for them.
3. Translate into Frappe-owned files: route template, route controller, metadata, CSS, JS, optimized images, and verifiers.
4. Keep the real site header/footer from Frappe/LT partials. Ignore designer header/footer code unless the task specifically asks for shell changes.
5. Preserve real installed-work aspect ratios through image width/height metadata.
6. Use optimized derivatives for the public reel, but do not crop proof photos to satisfy layout convenience.
7. Mobile should become a full-width natural-ratio stream, not a tiny desktop reel squeezed into a phone viewport.
8. Keep the reference folder in `research/` while external critique is active. Delete it only after GL approves cleanup.
9. Verify browser behavior, not just source shape. A row of images is a failed translation even if the assets load.

## Locked Reel Contract

For the approved LT portfolio reel, the left/right edge-anchor math is part of the design contract. Do not clamp left/right photos into safe containers and do not center them just to avoid intentional viewport bleed.

Use the approved side/scale rhythm in photo-array order:

- sides: `left, right, left, center, left, right, left, right, center, right, left, right, left, right, left, center, left, right, left, right`
- scales: `0.62, 0.74, 0.58, 0.92, 0.60, 0.64, 0.74, 0.58, 0.96, 0.55, 0.62, 0.76, 0.60, 0.62, 0.72, 0.94, 0.56, 0.60, 0.62, 0.78`

The durable lesson from the failed translation is that "protecting" photos from edge clipping can destroy this design. Frappe's normal header/footer stay native, but the portfolio reel itself is intentionally full-bleed inside the Frappe page shell.

## Verification Checklist

Run these after editing portfolio layout, image metadata, source/reference translation, or the proof-gallery CSS/JS:

```powershell
python scripts/dev/clear_website_cache.py --restart
npm run test:portfolio-reel
npm run test:layout-fit -- --grep portfolio
npm run test:interactive-layout -- --grep portfolio
```

Also inspect desktop and mobile screenshots before launch claims, especially after photo-order or image-quality changes. For this reel, include Chrome and Brave captures when the failure report or user feedback mentions cross-browser differences.

The latest verified use passed `npm run test:portfolio-reel` (4/4), `npm run test:layout-fit -- --grep portfolio` (13/13), and `npm run test:interactive-layout -- --grep portfolio` (3/3). Fresh Chrome/Brave screenshots and metrics were captured under `output/playwright/portfolio-strict-v5/`. The route-specific verifier now checks the approved staggered side/scale rhythm, hidden-by-default captions, mobile full-width stream, and scroll-driven reveal so a static row cannot pass as a successful translation.

## LT Receipt

On 2026-05-06, `/portfolio` moved from a cropped card grid toward a proof-first floating photo reel. The kept production source is `apps/locally_twisted/locally_twisted/www/portfolio.html`, `apps/locally_twisted/locally_twisted/www/portfolio.py`, `apps/locally_twisted/locally_twisted/public/css/lt-portfolio-reel.css`, `apps/locally_twisted/locally_twisted/public/js/lt-portfolio-reel.js`, optimized images under `apps/locally_twisted/locally_twisted/public/images/portfolio/optimized/`, and `scripts/verify/portfolio_reel.spec.js`.

The active reference source is still under `research/portfolio-design-cla/` and `research/design_handoff_locally_twisted_portfolio/` while GL sends the implementation back for designer critique. Do not claim it was deleted, and do not commit it as production source unless GL explicitly changes its status.
