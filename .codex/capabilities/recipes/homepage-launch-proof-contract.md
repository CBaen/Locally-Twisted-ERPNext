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
successful_uses: 1
failed_uses: 0
regressions: 0
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
- The cookie notice is inline after `.lt-hero` on the homepage. It must not be a
  fixed overlay covering CTAs there. Other pages may still use the fixed banner.
- The authority proof band uses approved brand mask SVGs, not ad hoc inline
  SVGs.
- Recent Celebrations appears before review cards so real installed work leads
  the proof story.
- Review cards and trusted-business names are full-stage crawls. Both move
  left-to-right at `540s` in normal motion; reduced-motion checks preserve a
  matched horizontal/static fallback so neither banner stacks or diverges.
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
- Reduced-motion mode changes one proof band but not the other.
- The hero reintroduces hidden H1 plus visible rotating headings.
- The hero grows back into a first-viewport wall or uses page-local min-height,
  oversized padding, or giant title clamps.
- The cookie notice blocks primary CTAs on mobile.
- Event Playground, blog-title cycling, or design-studio language returns to the
  launch hero without a fresh GL decision.
- The homepage relies on generic/generated scenery when a real optimized install
  photo is available.

## LT Receipt

On 2026-05-07, GL reported that review cards were a scrollbar on one platform
and stacked on another, while trusted-business proof was not crawling. The repair
gave both proof banners the same full-stage left-to-right `540s` normal-motion
behavior, stabilized the reduced-motion fallback, stabilized the hero around a
single visible H1 and real install photo, moved the cookie notice inline after
the hero, and added homepage/cookie Playwright coverage. Focused homepage checks
passed first; follow-up full-site closeout then passed `npm run test:website-verify`
with `layout-fit` 247/247 and `interactive-layout` 88/88 after the compact hero
contract was added. Do not carry forward
the earlier temporary portfolio-blocked caveat unless a fresh run fails again.
