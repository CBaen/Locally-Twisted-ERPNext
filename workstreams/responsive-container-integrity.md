# Responsive Container Integrity Workstream

Last updated: 2026-05-11 by Codex after removing the standalone `/event-balloons` hub from launch route matrices.

## Status

Standing gate created and verified. This lane exists because container fit, breakpoint stability, and stateful UI containment are now launch requirements for the public site.

## Outcome

Every current and future public container should have enough automated coverage that text, controls, cards, images, nav, drawers, forms, product selectors, modals, and Webshop wrappers cannot quietly push outside their containers or sit flush against panel edges at common breakpoints.

Operating law: if it can fail, it must fail loudly. For containers, hidden
overflow, missing top-level route declarations, accidental native scrollbars,
and uncontained readable content must become verifier failures. A page is not
"close enough" if the break only appears on one viewport or browser.

## Why This Exists

GL identified a systemic failure: the site could pass narrow checks while still failing spatially. A few default screenshots did not cover the nav breakpoint seam, mobile drawer state, product controls, contact conditionals, modal state, or the dense phone widths where content pressure shows up first.

## Current Gate

- `scripts/verify/layout_helpers.js` centralizes route lists, viewport families, page-settle behavior, and overflow/text-fit audits.
- `scripts/verify/layout_fit.spec.js` runs passive layout checks across the current launch public route list and 13 viewport families.
- `scripts/verify/container_contract.spec.js` runs the route-level public container contract across the launch public route list at 320px, 820px, and 1366px. It requires every visible top-level `.page_content` child to be classified, every full-bleed surface to declare itself, contained inners to stay within their declared max width, crawl/marquee viewports to clip instead of scroll, and Frappe's `main.container` to stay neutralized.
- `scripts/verify/interactive_layout.spec.js` checks stateful UI across platform-name leakage, header breakpoints, desktop mega panels, mobile drawer accordions, shop filters/product selectors, contact expanded conditionals, portfolio front-photo state, homepage proof crawls, cookie placement, and reduced-motion homepage behavior.
- `scripts/verify/interactive_layout.spec.js` also enforces the compact generated-photo hero contract across the current named hero routes: 220px mobile, 250px tablet, and 280px desktop standard heights with padding/title caps, breakpoint-specific WebP crops, and the black landing-page readability overlay.
- `package.json` exposes:
  - `npm run test:layout-fit`
  - `npm run test:container-contract`
  - `npm run test:interactive-layout`
  - `npm run test:checkout-experience`
  - `npm run test:shop-smoke`
  - `npm run test:public-verify`

## Breakpoint Coverage

The standing viewport families are:

- 320 small phone
- 360 Android
- 375 iPhone baseline
- 390 modern iPhone
- 414 large phone
- 768 tablet portrait
- 820 tablet modern
- 991 just below legacy desktop
- 992 legacy breakpoint edge
- 1024 tablet landscape
- 1199 just below active desktop nav
- 1200 active desktop nav
- 1366 laptop

## Completed This Session

- Expanded passive layout coverage to 260 route/viewport checks, then refreshed it to 247 checks after the unapproved `/process` route was removed.
- Added 39 stateful layout checks, then refreshed the stateful gate to 74 checks after platform-name, homepage proof-crawl, cookie, and nav/BTFP guards were added.
- Fixed the 992-1199 header breakpoint mismatch by making the desktop/mobile CSS and JS agree on 1200px.
- Kept desktop mega panels inside the header/container instead of anchoring narrow product panels to individual nav item widths.
- Fixed reduced-motion homepage proof-crawl behavior so the two business-proof tracks keep the accepted slow crawl, stay horizontal/full-stage, and do not force overflow when reduced motion is requested.
- Added the portfolio state check; 2026-05-06 follow-up now checks the current proof-reel front-photo behavior instead of the superseded modal behavior.
- Added the compact hero contract after GL rejected oversized/inconsistent page heroes. The first red run failed 14/14; the later generated-photo/overlay expansion first failed against missing crops, then passed 66/66 for home, event audience pages, portfolio, BTFP, contact, shop, and category heroes. The old `/event-balloons` hub was later removed before launch and should stay out of route matrices.
- Repaired the former Event Balloons hub plus the four audience-page heroes after GL flagged the mobile view. The old real-photo panel path stacked inside the fixed compact hero and clipped title/CTA on phones; those panels are removed from the hero, real/proof photos remain in story/gallery sections, and the shared generated-photo hero layer owns the hero image. The four audience pages remain; the hub route does not.
- Reconciled `smoke_shop.py` with the commerce lane. 2026-05-06 correction: fixed-price products must not invent product-level quote gates; out-of-area delivery ZIP owns the quote fallback, while retail products such as `unicorn-bouquet` still verify inline variant controls and cart writes.
- Added the executable public container contract. The first red check failed because `CONTAINER_CONTRACT_VIEWPORTS` was missing; the full matrix then caught real drift in the homepage twisting spotlight, portfolio footer, contact Bootstrap container, document narrow-width specificity, BTFP route contract, and BTFP event-crawl data. Repairs landed in `layout_helpers.js`, `container_contract.spec.js`, `lt-page-containment.css`, `hooks.py`, `portfolio.html`, `lt-portfolio-reel.css`, `balloon_twisting_and_face_painting.py`, and `package.json`.

## Verification Receipts

- `node --check scripts/verify/layout_helpers.js` passed.
- `node --check scripts/verify/layout_fit.spec.js` passed.
- `node --check scripts/verify/interactive_layout.spec.js` passed.
- `python -B -m py_compile scripts/verify/smoke_shop.py` passed.
- `python scripts/verify/commerce_rules_contract.py` passed.
- `python scripts/verify/smoke_shop.py` passed.
- `npm run test:interactive-layout` passed 154/154 after the generated-photo hero repair.
- `npm run test:layout-fit` passed 299/299 after the public route and breakpoint matrix expansion.
- `npm run test:checkout-experience` passed 2/2.
- `npm run test:container-contract` passed 69/69 after the executable route contract repair and route matrix expansion.
- `npm run test:a11y` passed with 50 route/viewport axe results and 0 violations after the generated-photo hero selector leak and later homepage carousel accessibility blocker were fixed.
- `npm run test:website-verify` passed; `npm run test:public-verify` aliases to the same website-only gate.
- `npx playwright test scripts/verify/interactive_layout.spec.js --grep "compact hero height contract" --reporter=line --workers=1` passed 66/66 after the generated-photo hero repair.
- 2026-05-10 Event Balloons hero follow-up: `npx playwright test scripts/verify/event_hero_mobile.spec.js --reporter=line` passed 12/12, targeted Event Balloons `layout-fit` passed 65/65, targeted `container-contract` passed 15/15, and `npm run test:a11y-manual` passed. Later 2026-05-10 broad launch verification passed full `interactive_layout.spec.js` 163/163 inside `website_launch_verify.py`, `npm run test:a11y` 50 route/viewport axe checks with 0 violations, and `npm run test:a11y-manual`.

## Rules For Future Work

- Do not solve layout by hiding body overflow unless the real container math is already fixed.
- Do not let heroes grow by page-local padding, `min-height`, or large title clamps. A hero is a compact page label, not the page.
- Do not put public hero text over a bare image. Use breakpoint-specific generated lifestyle photo crops under the shared black readability overlay and verify the actual rendered crop.
- Any new public route or component must be added to `PUBLIC_ROUTES` or a route-specific interactive check when it becomes launch-critical.
- Any new public route or visible top-level `.page_content` section must be added to `CONTAINER_CONTRACT_ROUTES` with an explicit mode before the route is considered done.
- Any new drawer, modal, accordion, filter, product selector, or breakpoint-specific behavior needs an open-state check.
- Use `capabilities/recipes/responsive-container-audit.md` before touching public containers.
- If a verifier fails because the business behavior changed, update the verifier to the new source of truth and preserve equivalent coverage in the correct lane.

## Next Work

- Keep adding route-specific interactive cases as new launch pages or components are built.
- Pair automated checks with real screenshot review for taste, hierarchy, image quality, and spacing feel.
- Keep `npm run test:public-verify` green before each broad visual closeout.
