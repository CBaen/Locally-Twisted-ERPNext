# Landing Page Repair Workstream

Last updated: 2026-05-07 by Codex.

## Outcome

Make the homepage launch-safe without reopening Event Playground or another
broad visual direction. The page should show real Locally Twisted work, explain
the business quickly, let corporate/school/civic/community buyers trust the
company, and avoid platform-specific crawl or cookie-overlay failures.

## Current State

Completed on 2026-05-07:

- The hero has one visible stable H1 over a real optimized installed-work photo.
- The first viewport shows a hint of the next band on desktop and 320px mobile.
- The homepage cookie notice is inline after the hero, not covering primary CTAs.
- Authority proof icons use approved brand mask SVGs.
- Recent Celebrations now appears before review cards.
- Review cards and trusted-business names both crawl full-stage, left-to-right,
  at `540s` in normal motion.
- Reduced-motion verification keeps both proof bands horizontal/full-stage and
  static instead of letting one stack, scroll oddly, or diverge from the other.
- Event Playground/design-studio and rotating blog-title language are out of the
  launch hero.

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
```

The homepage internal-link check inspected 37 links with no failures.
Screenshots for desktop, 375px mobile, 320px mobile, and the first after-hero
band are in `output/playwright/landing-fixes-20260507/`.

Important caveat: a broad `layout_fit` run is not green right now because
unrelated `/portfolio` work is failing at breakpoint-edge widths. Do not treat
that as a homepage regression, but do not call the full site gate green until
portfolio is reconciled.

## Next Safe Moves

- Review the homepage screenshots with GL/Jeff/designer for proof hierarchy and
  photo choice.
- Verify exact Google review count only if launch copy needs a number. Otherwise
  keep stable non-count language.
- Keep future blog work out of the hero unless GL explicitly reopens rotating
  headlines.
- Do not change the crawl speed or direction without updating the capability
  contract and the Playwright checks in the same slice.
