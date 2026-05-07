---
id: homepage-launch-proof-contract
name: Homepage Launch Proof Contract
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted ERPNext/Frappe homepage hero, proof crawls, cookie placement, and launch CTAs
currently_true: yes
verification_level: 2
last_verified: 2026-05-07
evidence_quality: direct
successful_uses: 2
failed_uses: 1
regressions: 1
depends_on:
  - frappe-public-container-contract
  - responsive-container-audit
  - compact-hero-contract
  - cross-browser-motion-visual-verification
used_by:
  - website-launch
tags:
  - Locally Twisted
  - homepage
  - launch
  - proof crawl
  - Frappe
  - Playwright
---

# Homepage Launch Proof Contract

Use this recipe before changing the Locally Twisted homepage hero, proof bands,
review crawl, trusted-client crawl, cookie notice placement, or launch CTAs.

## Current Contract

- The hero uses one visible stable H1, not hidden page-title plus rotating
  headings.
- The hero image is a real optimized Locally Twisted install photo:
  `/assets/locally_twisted/images/portfolio/optimized/corporate-weberstock-photo-opt.webp`.
- The first viewport must leave a hint of the next band visible on desktop and
  small mobile widths.
- The hero must obey the compact hero contract: 220px mobile, 250px tablet, and
  280px desktop standard heights, with no route-local oversized padding or title
  scale.
- Google reviews are the first homepage band immediately after `.lt-hero`.
- The homepage currently does not render a trust/authority bar. Keep the
  approved brand SVG icon assets for future proof sections, but do not put the
  trust bar back into the homepage unless GL explicitly reopens that choice.
- The cookie notice is inline after `.lt-reviews-block` on the homepage. It must
  not be a fixed overlay covering CTAs there, and it must not sit between the
  hero and the Google review proof band. Other pages may still use the fixed
  banner.
- Recent Celebrations appears after Google reviews. Real installed-work proof is
  still important, but the launch homepage now leads with social proof under the
  hero.
- Review cards and trusted-business names are full-stage crawls. Both move
  right-to-left. Review cards use the canonical `540s` loop, and the
  trusted-business crawl is measured in the browser so its pixel speed matches
  the review-card crawl even though its track width is different.
- The homepage proof crawls are a project-specific reduced-motion exception:
  they stay slow, linear, full-stage, and scrollbar-free in both
  `no-preference` and `reduce` media states unless GL explicitly changes the
  business-proof contract. Do not restore the static/scrollbar fallback.
- Homepage launch copy should speak to corporate, school, civic, community,
  venue, and private-event buyers without turning the page into technical
  planner language.

## Source Files

- `apps/locally_twisted/locally_twisted/www/home.html`
- `apps/locally_twisted/locally_twisted/www/home.py`
- `apps/locally_twisted/locally_twisted/public/css/lt-theme.css`
- `apps/locally_twisted/locally_twisted/public/css/lt-page-containment.css`
- `apps/locally_twisted/locally_twisted/public/js/lt-site-preferences.js`
- `scripts/verify/interactive_layout.spec.js`

## Verification

Run after homepage/Jinja/CSS/JS changes:

```powershell
python scripts/dev/clear_website_cache.py
npm run test:interactive-layout -- --grep "homepage review marquee|homepage client crawl banner|homepage reduced motion keeps"
npx playwright test scripts/verify/layout_fit.spec.js --reporter=dot --grep "home fits"
npm run test:interactive-layout -- --grep "homepage|cookie notice"
npm run test:interactive-layout -- --grep "compact hero height contract"
```

If `home.py` route-controller constants such as `PAGE_CSS` changed, restart the
Frappe backend container before final browser inspection:

```powershell
docker restart locally-twisted-erpnext-v15-backend-1
python scripts/dev/clear_website_cache.py
```

Capture and inspect at least desktop, 375px mobile, and 320px mobile screenshots
before marking the homepage ready for GL review.

## Red Flags

- Review cards expose a native horizontal scrollbar.
- Trusted-business names stack instead of crawling.
- The two crawls differ in direction or speed.
- Either crawl moves left-to-right.
- Reduced-motion mode stops either proof crawl, exposes a scrollbar, stacks the
  cards/names, or lets one proof band diverge from the other.
- The hero reintroduces hidden H1 plus visible rotating headings.
- The hero grows back into a first-viewport wall or uses page-local min-height,
  oversized padding, or giant title clamps.
- A trust/authority bar appears between the hero and reviews.
- Recent Celebrations appears before reviews.
- The cookie notice blocks primary CTAs on mobile or sits between the hero and
  Google reviews.
- Event Playground, blog-title cycling, or design-studio language returns to the
  launch hero without a fresh GL decision.
- The homepage relies on generic/generated scenery when a real optimized install
  photo is available.

## LT Receipt

On 2026-05-07, GL reported that review cards were a scrollbar on one platform
and stacked on another, while trusted-business proof was not crawling. The first
repair accidentally documented/protected a left-to-right/static reduced-motion
contract. The follow-up repair changed both proof banners to right-to-left,
kept the review crawl at the canonical `540s`, synced the trusted-business crawl
to the review-card pixel speed with a homepage-only measurement script, and made
the reduced-motion branch keep both proof crawls slow, horizontal, and
scrollbar-free. Verification passed: crawl regression 5/5, home layout 13/13,
homepage/cookie 12/12, compact hero 14/14, full `npm run test:website-verify`,
and live Playwright diagnostics for `no-preference` and `reduce` showed both
crawls moving right-to-left with hidden overflow and near-zero speed delta. Screenshots are in
`output/playwright/home-crawl-regression-20260507/`. The same-day proof-order correction removed the homepage trust/authority
bar, made Google reviews the first post-hero band, moved the cookie notice after
reviews, and moved Recent Celebrations after the reviews block. Do not carry
forward the earlier temporary portfolio-blocked caveat unless a fresh run fails
again.
