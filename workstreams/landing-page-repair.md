# Landing Page Repair Workstream

Last updated: 2026-05-08 by Codex after compacting the mobile Google review
proof band and adding its sizing contract.

## Outcome

Make the homepage launch-safe without reopening Event Playground or another
broad visual direction. The page should show real Locally Twisted work, explain
the business quickly, let corporate/school/civic/community buyers trust the
company, and avoid platform-specific crawl or cookie-overlay failures.

## Current State

Completed on 2026-05-07:

- The hero has one visible stable H1 over a generated lifestyle hero photo from the project image-generation API. Existing installed-work photos are reserved for the proof bands and portfolio.
- The hero now obeys the sitewide compact hero contract: 220px mobile and 280px
  desktop in the current verifier, with the tablet standard documented at
  250px.
- The first viewport shows a hint of the next band on desktop and 320px mobile.
- Google reviews are the first band immediately after the hero.
- The homepage trust/authority bar is removed for now. The approved brand icon
  assets remain available for future proof sections.
- The homepage cookie notice is inline after the Google reviews band, not
  covering primary CTAs and not sitting between the hero and reviews.
- `One of a Kind Designs` now appears after review cards as a wide
  custom-install proof band, not a cramped ecommerce-style product card row.
- Review cards and trusted-business names both crawl full-stage, left-to-right.
  Review cards keep the canonical `540s` loop; trusted-business names are
  measured in the browser and assigned a proportional duration so the visible
  pixel speed matches the review-card crawl.
- Google review proof has a mobile compactness contract. The review block
  should stay under 380px tall at 390px width, the marquee should stay under
  240px, cards should stay under 270px wide and 240px high, and inherited
  global `section` padding must not leak into `.lt-reviews-block__quotes`.
- Reduced-motion verification keeps both proof bands slow, moving,
  horizontal/full-stage, and scrollbar-free. The old static/scrollbar fallback
  is superseded because it is the failure mode GL kept seeing in real browsers.
- Event Playground/design-studio and rotating blog-title language are out of the
  launch hero.
- The hero no longer inherits global `section` vertical padding or local
  oversized min-height behavior.

## Source Files

- `apps/locally_twisted/locally_twisted/www/home.html`
- `apps/locally_twisted/locally_twisted/www/home.py`
- `apps/locally_twisted/locally_twisted/public/css/lt-theme.css`
- `apps/locally_twisted/locally_twisted/public/css/lt-page-containment.css`
- `apps/locally_twisted/locally_twisted/public/js/lt-site-preferences.js`
- `scripts/verify/interactive_layout.spec.js`
- Capability contract: `.codex/capabilities/recipes/homepage-launch-proof-contract.md`

## Verification Receipt

Mobile review compactness correction on 2026-05-08:

```powershell
python scripts/dev/clear_website_cache.py --restart
python -m py_compile apps\locally_twisted\locally_twisted\www\home.py
npx playwright test scripts/verify/interactive_layout.spec.js --grep "mobile review proof|reviews crawl left-to-right" --reporter=line --workers=1
npx playwright test scripts/verify/layout_fit.spec.js --grep "home fits at mobile-320|home fits at mobile-390|home fits at desktop-1200" --reporter=line --workers=1
```

Result: live browser measurements showed the mobile review block at about
364px tall across 320px, 375px, 390px, and 414px widths, down from about 693px
at 320px before the repair. The targeted interactive review tests passed, and
the targeted home layout-fit checks passed 3/3. Full feature details live in
`workstreams/mobile-nav-review-compactness.md`.

Featured-work correction on 2026-05-08:

```powershell
python -m py_compile apps\locally_twisted\locally_twisted\www\home.py
node --check scripts\verify\interactive_layout.spec.js
python scripts/dev/clear_website_cache.py --restart
npx playwright test scripts/verify/interactive_layout.spec.js --reporter=line --grep "homepage installed-work proof|homepage leads with Google review|homepage hero uses one visible|small mobile homepage|mobile cookie notice|desktop homepage cookie|site-preferences" --workers=1
npx playwright test scripts/verify/layout_fit.spec.js --reporter=dot --grep "home fits" --workers=1
npm run test:container-contract
npm run test:a11y
```

Result: live `/` measurements showed `One of a Kind Designs`, the current
containment cache key, zero document overflow, desktop featured-image widths of
424px at 1366px, 502px at 1600px, and 551px at 1920px, with mobile staying
single-column at 375px and 320px. Focused homepage interactive checks passed
8/8, homepage layout-fit passed 13/13, container contract passed 57/57, and
axe passed 38 route/viewport results with 0 violations. Screenshots are in
`output/playwright/home-featured-work-20260508/`.

Passed:

```powershell
python scripts/dev/clear_website_cache.py
npx playwright test scripts/verify/layout_fit.spec.js --reporter=dot --grep "home fits"
npm run test:interactive-layout -- --grep "homepage|cookie notice"
npm run test:interactive-layout -- --grep "compact hero height contract"
```

Same-day correction after GL clarified the proof order:

```powershell
docker restart locally-twisted-erpnext-v15-backend-1
python scripts/dev/clear_website_cache.py
npm run test:interactive-layout -- --grep "homepage leads with Google review|homepage hero uses one visible|small mobile homepage|mobile cookie notice|desktop homepage cookie|site-preferences"
```

Result: 7/7 passed. This verifies no homepage trust bar, Google reviews directly
after the hero, cookie placement after reviews, and mobile/desktop CTA safety.

Broader follow-up after the portfolio mobile hero fix also passed:
`npm run test:interactive-layout` 88/88 and
`npm run test:layout-fit -- --grep "home fits|portfolio fits"` 26/26. Visual
evidence is in `output/playwright/home-portfolio-corrections-20260507/`.

The homepage internal-link check inspected 37 links with no failures.
Screenshots for desktop, 375px mobile, 320px mobile, and the first after-hero
band are in `output/playwright/landing-fixes-20260507/`.

Follow-up closeout on 2026-05-07 reconciled the earlier portfolio caveat:
`npm run test:website-verify` passed, including `layout-fit` 247/247,
`interactive-layout` 88/88, checkout 2/2, portfolio reel 4/4, and shop smoke.
Do not reintroduce the older "broad layout gate blocked by portfolio" caveat
unless a fresh failing run proves it again.

The compact hero contract was added after this repair because GL escalated the
same-height hero rule to agency level. First red run failed 14/14; after CSS
and copy-density changes the focused compact-hero gate passed 14/14.

2026-05-10 correction: the earlier photo-hero pass used reserved real/proof
photos as hero crops, which was wrong. Public heroes now use generated
lifestyle photos from the project image-generation API, with source files and
prompts stored in `_resources/generated-hero-sources/2026-05-10/`. Current
verification passed focused compact heroes 66/66, full
`npm run test:interactive-layout` 154/154, `npm run test:layout-fit` 299/299,
`npm run test:container-contract` 69/69, and `npm run test:a11y` with 46
route/viewport axe results and 0 violations. Rendered hero screenshots are in
`output/playwright/generated-heroes-20260510/`.

Same-day crawl regression follow-up: the old verifier protected a static
reduced-motion fallback, and a later correction briefly inverted the crawl
direction. The current contract now fails if either proof crawl moves
right-to-left, if either exposes a scrollbar, if either stops in reduced-motion
mode, or if the trusted-business crawl differs from the review-card pixel speed.

Current crawl verification:

```powershell
python -m py_compile apps\locally_twisted\locally_twisted\www\home.py
node --check scripts\verify\interactive_layout.spec.js
python scripts/dev/clear_website_cache.py --restart
npm run test:interactive-layout -- --grep "homepage review marquee|homepage client crawl banner|homepage reduced motion keeps"
npx playwright test scripts/verify/layout_fit.spec.js --reporter=dot --grep "home fits"
npm run test:interactive-layout -- --grep "homepage|cookie notice"
npm run test:interactive-layout -- --grep "compact hero height contract"
```

Earlier results from the right-to-left pass are superseded by GL's direction
correction. Current verification proves left-to-right deltas.

Left-to-right correction verification:

```powershell
npm run test:interactive-layout -- --grep "homepage review marquee|homepage client crawl banner|homepage reduced motion keeps"
npx playwright test scripts/verify/layout_fit.spec.js --reporter=dot --grep "home fits"
npm run test:interactive-layout -- --grep "homepage|cookie notice"
npm run test:interactive-layout -- --grep "compact hero height contract"
npm run test:website-verify
```

Results: the deliberate red run failed 5/5 against the previous right-to-left
direction, then the corrected implementation passed focused crawl regression
5/5, home layout 13/13, homepage/cookie 12/12, compact hero 14/14, and full
website closeout. Live diagnostics showed positive left-to-right deltas, hidden
overflow for both banners, and effectively identical speed deltas in
`no-preference` and `reduce`. Screenshots are in
`output/playwright/home-crawl-left-to-right-20260507/`.

## Next Safe Moves

- Review the homepage screenshots with GL/Jeff/designer for proof hierarchy and
  photo choice.
- Verify exact Google review count only if launch copy needs a number. Otherwise
  keep stable non-count language.
- Keep future blog work out of the hero unless GL explicitly reopens rotating
  headlines.
- Do not change crawl speed, direction, or reduced-motion behavior without
  updating the capability contract and Playwright checks in the same slice.
- Do not relax the mobile Google review compactness thresholds without a fresh
  GL visual decision and new mobile measurements.
- Do not grow the homepage hero to carry proof/copy that belongs in the next
  section.
- Do not restore the homepage trust bar or put the installed-work proof band
  above Google reviews unless GL explicitly changes the launch proof order
  again.
