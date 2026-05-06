# Codex Production Review Packet - Locally Twisted Portfolio

This file is for designer critique of the current Frappe implementation.

## What To Review

Review the live Frappe translation against the approved reference behavior:

- large whole photos, not cropped cards;
- left/right/center photo placement rhythm;
- slow drift/fade motion;
- click-to-front scale/lift/bounce behavior;
- no visible text covering the photos;
- mobile full-width natural-ratio photo stream.

The designer header/footer from the reference should be ignored. The live site keeps the real Locally Twisted Frappe header and footer.

## Production Files

These are the files Codex translated into production:

```text
apps/locally_twisted/locally_twisted/www/portfolio.html
apps/locally_twisted/locally_twisted/www/portfolio.py
apps/locally_twisted/locally_twisted/public/css/lt-portfolio-reel.css
apps/locally_twisted/locally_twisted/public/js/lt-portfolio-reel.js
apps/locally_twisted/locally_twisted/public/images/portfolio/optimized/
scripts/verify/portfolio_reel.spec.js
scripts/verify/interactive_layout.spec.js
```

## Reference Files

The approved/reference design package is still here:

```text
research/design_handoff_locally_twisted_portfolio/reference/
research/design_handoff_locally_twisted_portfolio/frappe/
research/portfolio-design-cla/frappe/
```

The reference folders are critique input only. They are not production source.

## Intentional Translation Choices

- Real LT header/footer are preserved.
- Real LT portfolio photos replace placeholder image sources.
- Optimized WebP derivatives are used for the public reel so the page does not load 12-17 MB originals.
- Category/event query links still filter the photo payload server-side, but there is no visible filter bar in the current translation.
- There is no lightbox modal in the current translation.
- Photo labels/captions are not visible over the gallery photos.

## Current Verification

Latest focused verification on the local Frappe site:

```powershell
npm run test:portfolio-reel
npm run test:layout-fit -- --grep portfolio
npm run test:interactive-layout -- --grep portfolio
```

These passed after the current retranslation. Passing tests do not mean design approval; they only prove the current route loads, uses optimized whole-photo assets, avoids horizontal overflow, and keeps the front-photo interaction measurable.

## Known Review Questions

- Does the live photo placement match the reference rhythm closely enough?
- Are the first visible photos too large, too low, too faded, or too clipped?
- Should the hero/title area be reduced so the photo collage starts sooner?
- Are any current photos too weak for a portfolio page?
- Does mobile need less title space and more immediate photo impact?
- Should any reference constants remain exact even if Frappe containment or real photos make the page feel different?
