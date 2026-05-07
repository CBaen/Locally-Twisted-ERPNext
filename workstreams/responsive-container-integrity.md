# Responsive Container Integrity Workstream

Last updated: 2026-05-07 by Codex after the Process route removal and full website verification parity pass.

## Status

Standing gate created and verified. This lane exists because container fit, breakpoint stability, and stateful UI containment are now launch requirements for the public site.

## Outcome

Every current and future public container should have enough automated coverage that text, controls, cards, images, nav, drawers, forms, product selectors, modals, and Webshop wrappers cannot quietly push outside their containers or sit flush against panel edges at common breakpoints.

## Why This Exists

GL identified a systemic failure: the site could pass narrow checks while still failing spatially. A few default screenshots did not cover the nav breakpoint seam, mobile drawer state, product controls, contact conditionals, modal state, or the dense phone widths where content pressure shows up first.

## Current Gate

- `scripts/verify/layout_helpers.js` centralizes route lists, viewport families, page-settle behavior, and overflow/text-fit audits.
- `scripts/verify/layout_fit.spec.js` runs passive layout checks across the current launch public route list and 13 viewport families.
- `scripts/verify/interactive_layout.spec.js` checks stateful UI across platform-name leakage, header breakpoints, desktop mega panels, mobile drawer accordions, shop filters/product selectors, contact expanded conditionals, portfolio front-photo state, homepage proof crawls, cookie placement, and reduced-motion homepage behavior.
- `package.json` exposes:
  - `npm run test:layout-fit`
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
- Fixed reduced-motion homepage carousel/review behavior so tracks do not animate or force overflow when reduced motion is requested.
- Added the portfolio state check; 2026-05-06 follow-up now checks the current proof-reel front-photo behavior instead of the superseded modal behavior.
- Reconciled `smoke_shop.py` with the commerce lane. 2026-05-06 correction: fixed-price products must not invent product-level quote gates; out-of-area delivery ZIP owns the quote fallback, while retail products such as `unicorn-bouquet` still verify inline variant controls and cart writes.

## Verification Receipts

- `node --check scripts/verify/layout_helpers.js` passed.
- `node --check scripts/verify/layout_fit.spec.js` passed.
- `node --check scripts/verify/interactive_layout.spec.js` passed.
- `python -B -m py_compile scripts\verify\smoke_shop.py` passed.
- `python scripts/verify/commerce_rules_contract.py` passed.
- `python scripts/verify/smoke_shop.py` passed.
- `npm run test:interactive-layout` passed 74/74 after the homepage/nav proof update.
- `npm run test:layout-fit` passed 247/247 after `/process` was removed from the public route list.
- `npm run test:checkout-experience` passed 2/2.
- `npm run test:website-verify` passed; `npm run test:public-verify` aliases to the same website-only gate.

## Rules For Future Work

- Do not solve layout by hiding body overflow unless the real container math is already fixed.
- Any new public route or component must be added to `PUBLIC_ROUTES` or a route-specific interactive check when it becomes launch-critical.
- Any new drawer, modal, accordion, filter, product selector, or breakpoint-specific behavior needs an open-state check.
- Use `.codex/capabilities/recipes/responsive-container-audit.md` before touching public containers.
- If a verifier fails because the business behavior changed, update the verifier to the new source of truth and preserve equivalent coverage in the correct lane.

## Next Work

- Keep adding route-specific interactive cases as new launch pages or components are built.
- Pair automated checks with real screenshot review for taste, hierarchy, image quality, and spacing feel.
- Keep `npm run test:public-verify` green before each broad visual closeout.
