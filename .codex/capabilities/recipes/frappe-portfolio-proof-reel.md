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
special case of that broader rule: the external reference is useful for the
floating image-collage behavior, but the kept production source is the Frappe
implementation and the current LT site shell. Do not copy prototype fonts,
custom cursors, fake headers/footers, or full-page styling into production.

## Pattern

1. Preserve the approved floating photo-collage behavior before preserving older local grid/card UI.
2. Keep the hero compact and SEO-useful. Current default H1 is `What We Do`; supporting copy should say Utah balloon decor plainly.
3. Do not reintroduce the full prototype hero, prototype font imports, custom cursor, fake shell, marketing-page decoration, boxed grids, captions that cover photos, or modal/filter UI unless GL explicitly asks for them.
4. Translate into Frappe-owned files: route template, route controller, metadata, CSS, JS, optimized images, and verifiers.
5. Keep the real site header/footer and global LT typography from Frappe/LT partials.
6. Display real installed-work photos with `object-fit: contain`; keep frame and image backgrounds matched to the page background so mismatched aspect ratios do not read as gray boxes.
7. Use optimized derivatives for the public reel, but do not crop proof photos to satisfy layout convenience.
8. Mobile should become a full-width natural-ratio stream with stacked captions, not a tiny desktop reel squeezed into a phone viewport.
9. Keep the reference folder in `research/` while external critique is active. Delete it only after GL approves cleanup.
10. Verify browser behavior, not just source shape. A row of images is a failed translation even if the assets load.

## Locked Reel Contract

For the approved LT portfolio reel, the page starts with a compact `What We Do` hero band, not a giant hero image and not a collapsed no-hero stub. Keep the hero within roughly 2.5-3x the live menu/header height, then let the photo reel carry the page.

Desktop photos must use a true left/right/center three-column rhythm immediately from the first viewport. Keep the columns closer to the center than the old edge-biased version, but allow large photos to overlap or slightly exceed the viewport when that preserves scale. The current desktop baseline is intentionally about 1.5x the earlier small reel: at 1366px wide, the first left photo measures about 861px wide and the opening center photo measures about 1255px wide. Do not shrink the desktop photos back into small safe cards. Do not make the page feel like the full external prototype; use only the collage behavior.

Use the approved side/scale rhythm in photo-array order:

- sides: `left, right, center, left, right, center, left, right, center, left, right, center, left, right, center, left, right, center, left, right`
- scales: `0.70, 0.84, 1.02, 0.66, 0.72, 0.98, 0.78, 0.66, 1.00, 0.72, 0.84, 0.96, 0.70, 0.74, 0.98, 0.66, 0.70, 0.96, 0.72, 0.86`
- aspect sequence: `4:5, 3:2, 16:10, 2:3, 3:4, 16:9, 5:4, 3:4, 16:10, 4:5, 3:2, 16:9, 4:5, 3:4, 16:10, 2:3, 3:4, 16:9, 4:5, 3:2`

The durable lesson from the failed translation is that over-protecting photos from edge placement makes them look small and cheap, while copying the whole external page makes the route feel off-brand. Keep the native LT shell and compact intro; let the image collage carry the page.

## Verification Checklist

Run these after editing portfolio layout, image metadata, source/reference translation, or the proof-gallery CSS/JS:

```powershell
python scripts/dev/clear_website_cache.py --restart
npm run test:portfolio-reel
npm run test:layout-fit -- --grep portfolio
npm run test:interactive-layout -- --grep portfolio
```

Also inspect desktop and mobile screenshots before launch claims, especially after photo-order or image-quality changes. For this reel, include Chrome and Brave captures when the failure report or user feedback mentions cross-browser differences.

The latest verified use passed `npm run test:portfolio-reel` (4/4), `npm run test:layout-fit -- --grep portfolio` (13/13), and `npm run test:interactive-layout -- --grep portfolio` (4/4). Fresh screenshots and metrics were captured under `output/playwright/portfolio-tight-after-desktop.png` and `output/playwright/portfolio-tight-after-mobile.png`. The route-specific verifier now checks the compact `What We Do` hero against the live menu height, no portfolio-specific Google font imports, no custom cursor artifacts, matched page/frame/image backgrounds, larger desktop left/right/center rhythm, optimized whole-photo assets, mobile full-width stream, and scroll-driven layout so a static row cannot pass as a successful translation.

## LT Receipt

On 2026-05-06, `/portfolio` moved from a cropped card grid toward a proof-first floating photo reel, then GL narrowed the standard: keep the collage of imagery, but do not carry over the full Claude/designer page styling. The kept production source is `apps/locally_twisted/locally_twisted/www/portfolio.html`, `apps/locally_twisted/locally_twisted/www/portfolio.py`, `apps/locally_twisted/locally_twisted/public/css/lt-portfolio-reel.css`, `apps/locally_twisted/locally_twisted/public/js/lt-portfolio-reel.js`, optimized images under `apps/locally_twisted/locally_twisted/public/images/portfolio/optimized/`, and `scripts/verify/portfolio_reel.spec.js`.

The active reference source remains useful as critique input for collage behavior only. The fake reference header/footer, prototype typography, custom cursor, oversized hero, and placeholder photo feed are not production source unless GL explicitly changes their status.
