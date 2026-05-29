---
id: frappe-portfolio-proof-reel
name: Frappe Portfolio Proof Reel
schema_version: 2.5
profile: foundation
level: recipe
maturity: candidate
scope: Locally Twisted ERPNext/Frappe portfolio and proof-gallery visual work
currently_true: true
verification_level: 2
last_verified: 2026-05-10
evidence_quality: direct
successful_uses: 8
failed_uses: 1
regressions: 3
graduation_stage: verifier_backed
graduation_status: active
graduation_required: true
supporting_artifacts:
  - ../../verifier-manifest.json
  - ../../scripts/verify/portfolio_reel.spec.js
  - ../../scripts/verify/layout_fit.spec.js
  - ../../scripts/verify/container_contract.spec.js
  - ../../scripts/verify/interactive_layout.spec.js
graduation_reason: approved item 2 review found repeated portfolio visual regressions and strong local verifier coverage; keep as LT-local verifier-backed capability, not a live-release gate
graduation_review: 2026-05-29
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

## Verifier Status

As of 2026-05-29, Guiding Light approved this as an LT-local
verifier-backed capability. The verifier protects the local browser contract
for the portfolio proof reel; it does not approve staging, live launch, DNS,
CDN/cache, photo/content approval, or customer-facing release readiness.

Use the project root `verifier-manifest.json` for the current tier boundary.
The `lt-portfolio-proof-reel-contract` bundle is Tier 2 local integrated proof
and should stay manual-only.

First read `external-design-reference-translation`. The portfolio reel is a
special case of that broader rule: the approved external reference supplies the
collage/movement behavior and the installed-photo proof rhythm. It does not own
the whole public page shell. Translate fake placeholder content, fake locations,
fake image URLs, unsafe production details, copied internal nav, custom cursor
artifacts, route-local font imports, and off-brand hero copy back into LT's
native Frappe shell and current style guide.

## Pattern

1. Preserve the approved collage/movement behavior before preserving older local grid/card UI or later Codex reinterpretations.
2. Keep the scroll-triggered entry, click-to-front pop, large whole-photo sizing, side/scale rhythm, no-captions photo proof, desktop image-only depth treatment, and mobile full-width slide-in stream.
3. Replace what is fake, unsafe, or not LT-owned: placeholder image URLs, fake Brooklyn/contact copy, copied internal navigation, page-local Google font imports, custom cursor artifacts, prototype-only palette choices, route-specific Inquire/Studio/Index footer blocks, and broken asset paths.
4. Translate into Frappe-owned files: route template, route controller, metadata, CSS, JS, optimized images, and verifiers.
5. The real public site header/footer wrap the Frappe page. Do not add a second internal page header/nav copied from the prototype, and do not add a second route-local contact/index footer inside the portfolio field.
6. Display real installed-work photos as the image itself. Do not add visible frame wrappers, card backgrounds, caption overlays, or forced aspect boxes that create letterbox stripes. A light desktop edge fade and shadow are allowed only when they are applied to the photo/pseudo-layer itself and do not create a new visible container. Use LT's approved warm-white, navy, brass, berry, Cormorant, and Lato system for the branded route shell around the reel.
7. Use optimized derivatives for the public reel, but do not crop proof photos to satisfy layout convenience.
8. Mobile should become a full-width natural-ratio slide-in stream with no captions and no side gutters, not a static stack and not a tiny desktop reel squeezed into a phone viewport.
9. Keep the reference folder in `research/` while external critique is active. Delete it only after GL approves cleanup.
10. Verify browser behavior, not just source shape. A row of images is a failed translation even if the assets load.

## Locked Reel Contract

For the approved LT portfolio reel movement, the source reference is
`research/design_handoff_locally_twisted_portfolio/frappe/`. Only the movement,
scale, side rhythm, and whole-photo proof behavior are locked from that
reference. The page shell is LT-owned. The locked reel settings are:

- `SETTINGS.density = 1.10`
- `SETTINGS.photoScale = 1.5`
- `SETTINGS.variant = "drift"`
- `SETTINGS.driftSmoothing = 0.02`
- `SETTINGS.opacitySpeed = 4.0`
- `BASE_UNIT = 640`
- `VERTICAL_SPACING = 80`
- `OVERLAP = 0.55`
- `CENTER_BREATH = 140`

At 1366px wide, the current production baseline has the first left photo around
655px wide, the first right photo around 781px wide, and the first center photo
around 972px wide. The larger photo size is controlled by `photoScale`, not by
raising `density`; `density` stays at 1.10 so the older looser vertical rhythm
survives. Photos begin below the branded compact hero and drift/fade in
from the edges as the visitor scrolls, but they must not follow the pointer or
keep swaying while the visitor is trying to look. Click-to-front motion is a
short pop/angle animation that settles into a stable front photo. Do not "improve" this into an immediate
three-column masonry grid, copied prototype shell, custom cursor experience,
captioned card wall, or generic full-opacity card wall.

Desktop depth is part of the current contract, but it is not a return to framed
cards. Each photo may carry a subtle black edge fade and image-level shadow;
the clicked front photo gets the stronger shadow. The portfolio hero must sit
above the reel's stacking plane so the top photos cannot cover the hero when
clicked forward. Mobile is intentionally separate and should not inherit new
desktop depth behavior without a mobile-specific review.

Use the approved side/scale rhythm in photo-array order:

- sides: `left, right, left, center, left, right, left, right, center, right, left, right, left, right, left, center, left, right, left, right`
- scales: `0.62, 0.74, 0.58, 0.92, 0.60, 0.64, 0.74, 0.58, 0.96, 0.55, 0.62, 0.76, 0.60, 0.62, 0.72, 0.94, 0.56, 0.60, 0.62, 0.78`
- image aspect ratios come from `PORTFOLIO_REEL_META`, which must match the optimized image assets. The old handoff aspect sequence is not allowed to override real photo dimensions because that creates visible stripes.

The durable lesson from the failed translation is that "productionizing" a
design reference by preserving the wrong parts produces a technically passing
page that looks wrong. For this route, the collage/movement and photo rhythm are
the contract; the copied page shell, custom cursor, local font imports, and
off-brand hero are not.

## Verification Checklist

Run these after editing portfolio layout, image metadata, source/reference translation, or the proof-gallery CSS/JS:

```powershell
python scripts/dev/clear_website_cache.py --restart
npm run test:portfolio-reel
npm run test:layout-fit -- --grep portfolio
npm run test:container-contract -- --grep portfolio
npm run test:interactive-layout -- --grep portfolio
npm run test:a11y-manual
```

Also inspect desktop and mobile screenshots before launch claims, especially after photo-order or image-quality changes. For this reel, include Chrome and Brave captures when the failure report or user feedback mentions cross-browser differences.

The latest verified use on 2026-05-10 added 59 optimized proof photos from the
ignored raw `assets/New Balloon Pics 3.7.26/` drop without changing the locked
reel rhythm. `/portfolio` now renders 74 total photos. The new batch lives in
`portfolio_new_balloon_pics.py` instead of expanding the route controller, and
the public assets are curated WebP derivatives under
`public/images/portfolio/optimized/`.

The 2026-05-10 verification passed full `npm run test:portfolio-reel` 6/6,
`npm run test:layout-fit -- --grep portfolio` 13/13,
`npm run test:container-contract -- --grep portfolio` 3/3, and
`npm run test:a11y-manual`. A live route/asset probe returned 200 for
`/portfolio` plus representative new WebP assets, and a focused rendered DOM
check found all 59 new portfolio records loaded from `/optimized/` with no
desktop or mobile document overflow. Later 2026-05-10 launch verification
repaired the unrelated homepage accessibility blocker; `npm run test:a11y`
now passes 50 route/viewport axe checks with 0 violations.

The prior verified use passed full `npm run test:portfolio-reel` 6/6,
`npm run test:interactive-layout -- --grep portfolio` 6/6, and
`npm run test:layout-fit -- --grep "portfolio fits"` 13/13 after GL rejected
all photo captions, visible photo frame wrappers, old desktop sizing, the
route-specific Inquire/Studio/Index footer block, pointer-follow sway, top
photos covering the hero, and the mobile view not visibly changing in Brave.
The route-specific portfolio verifier guards the
removed footer block directly. A clean Brave mobile pass returned
200 with the cache-busted `20260508-no-captions-scale-2` assets, 15 photos, 0
frame wrappers, 0 captions, first photo visible at full viewport width, second
photo waiting for scroll, and no page errors. The route-specific verifier now
checks the current contract: no portfolio-specific Google font links, no custom
cursor artifacts, no copied internal page nav, branded compact hero copy,
readable primary CTA contrast, no caption/frame wrappers, transparent photo
backgrounds, image rect equals photo rect, locked first/second/fourth photo
sizes from the `640 * scale * 1.10 * 1.5` math, original-density vertical
spacing, optimized whole-photo assets, initial fade-in state, scroll-triggered
desktop entry/opacity, click-to-front pop behavior that settles and ignores
later pointer movement, image-level desktop shadow, light desktop edge fade, a
hero stacking plane above clicked front photos, no route-specific portfolio
contact/index footer, and mobile full-width slide-in reveal instead of a static
stack. The fifth portfolio verifier proves the click-to-front pop still changes
the transform, then the settled front photo does not change when the pointer
moves. The sixth portfolio verifier proves clicked top photos remain behind the
portfolio hero.

## LT Receipt

On 2026-05-06, `/portfolio` moved from a cropped card grid toward a proof-first
floating photo reel. A later correction over-preserved the Claude/Frappe export
and copied too much of the page design: internal nav, page-local font imports,
custom cursor, and hero copy that did not match LT. On 2026-05-07, GL clarified
that the approved part was the collage and movement, not the entire page shell.
On 2026-05-08, GL rejected the static mobile stream and captions-below-photo
treatment. Later the same day GL rejected captions entirely, rejected visible
photo containers, asked for desktop photos 1.5x larger, and identified the
white bands as unacceptable. GL then clarified that larger photos must not mean
higher reel density. The current protected behavior is no captions, no frame
wrappers, actual image dimensions, desktop `photoScale = 1.5` with
`density = 1.10`, no route-specific Inquire/Studio/Index footer block, and
mobile full-width slide-in reveal.
The latest accessibility correction removed pointer-follow parallax and
front-photo pointer tilt. Keep the click pop, but the front photo must settle
after the short animation.
The latest desktop depth correction added an image-only edge fade, image-level
shadows, stronger front-photo overlap shadow, and a hero-above-reel stacking
plane. It is desktop-only and must not be translated into mobile until mobile is
reviewed separately.
The kept production source is now the live Frappe translation into
`apps/locally_twisted/locally_twisted/www/portfolio.html`,
`apps/locally_twisted/locally_twisted/www/portfolio.py`,
`apps/locally_twisted/locally_twisted/public/css/lt-portfolio-reel.css`,
`apps/locally_twisted/locally_twisted/public/js/lt-portfolio-reel.js`,
optimized images under
`apps/locally_twisted/locally_twisted/public/images/portfolio/optimized/`, and
`scripts/verify/portfolio_reel.spec.js`.
On 2026-05-10, the raw `assets/New Balloon Pics 3.7.26/` drop remained ignored
as source material and 59 curated optimized WebPs were added to the public
portfolio reel. The batch-specific records live in
`apps/locally_twisted/locally_twisted/www/portfolio_new_balloon_pics.py`.
