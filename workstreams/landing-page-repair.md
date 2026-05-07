# Landing Page Repair Workstream

Last updated: 2026-05-07 by Codex after removing the homepage trust bar and
moving Google reviews directly under the hero.

## Outcome

Make the homepage launch-safe without reopening Event Playground or another
broad visual direction. The page should show real Locally Twisted work, explain
the business quickly, let corporate/school/civic/community buyers trust the
company, and avoid platform-specific crawl or cookie-overlay failures.

## Current State

Completed on 2026-05-07:

- The hero has one visible stable H1 over a real optimized installed-work photo.
- The hero now obeys the sitewide compact hero contract: 220px mobile and 280px
  desktop in the current verifier, with the tablet standard documented at
  250px.
- The first viewport shows a hint of the next band on desktop and 320px mobile.
- Google reviews are the first band immediately after the hero.
- The homepage trust/authority bar is removed for now. The approved brand icon
  assets remain available for future proof sections.
- The homepage cookie notice is inline after the Google reviews band, not
  covering primary CTAs and not sitting between the hero and reviews.
- Recent Celebrations now appears after review cards.
- Review cards and trusted-business names both crawl full-stage, left-to-right,
  at `540s` in normal motion.
- Reduced-motion verification keeps both proof bands horizontal/full-stage and
  static instead of letting one stack, scroll oddly, or diverge from the other.
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

## Next Safe Moves

- Review the homepage screenshots with GL/Jeff/designer for proof hierarchy and
  photo choice.
- Verify exact Google review count only if launch copy needs a number. Otherwise
  keep stable non-count language.
- Keep future blog work out of the hero unless GL explicitly reopens rotating
  headlines.
- Do not change the crawl speed or direction without updating the capability
  contract and the Playwright checks in the same slice.
- Do not grow the homepage hero to carry proof/copy that belongs in the next
  section.
- Do not restore the homepage trust bar or put Recent Celebrations above Google
  reviews unless GL explicitly changes the launch proof order again.
