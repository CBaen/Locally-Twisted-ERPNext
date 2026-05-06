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
successful_uses: 1
failed_uses: 0
regressions: 0
depends_on:
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

## Pattern

1. Treat the reference artifact as temporary input, not as a kept source of truth.
2. Translate the useful behavior into Frappe-owned files: route template, route controller, metadata, CSS, JS, and verifiers.
3. Delete raw generated/reference folders after translation unless GL explicitly says they remain source material.
4. Preserve real installed-work aspect ratios through image width/height metadata.
5. Keep visible gallery text off busy proof photos. Put labels in filters, modal captions, screen-reader-only text, or surrounding copy.
6. Keep filters quiet and customer-friendly; changing filters must relayout the reel and keep an accessible empty state.
7. Mobile should become a full-width natural-ratio stream, not a tiny desktop reel squeezed into a phone viewport.
8. Verify browser behavior, not just source shape.

## Verification Checklist

Run these after editing portfolio layout, image metadata, filters, modal behavior, or the proof-gallery CSS/JS:

```powershell
python scripts/dev/clear_website_cache.py --restart
npm run test:portfolio-reel
npm run test:layout-fit
npm run test:interactive-layout
```

Also inspect desktop and mobile screenshots before launch claims, especially after photo-order or image-quality changes.

The first verified use passed `npm run test:portfolio-reel` (3/3), `npm run test:layout-fit` (260/260), and `npm run test:interactive-layout` (42/42).

## LT Receipt

On 2026-05-06, `/portfolio` moved from a cropped card grid toward a proof-first floating photo reel. The kept source is `apps/locally_twisted/locally_twisted/www/portfolio.html`, `apps/locally_twisted/locally_twisted/www/portfolio.py`, and `scripts/verify/portfolio_reel.spec.js`. The temporary generated/reference folder under `research/` was deleted after translation.
