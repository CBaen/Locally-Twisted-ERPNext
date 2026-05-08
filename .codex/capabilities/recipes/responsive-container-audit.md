---
id: responsive-container-audit
name: Responsive Container Audit
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted ERPNext/Frappe public-site responsive layout, containment, and stateful UI checks
currently_true: yes
verification_level: 2
last_verified: 2026-05-08
evidence_quality: direct
successful_uses: 2
failed_uses: 0
regressions: 0
depends_on:
  - frappe-public-container-contract
  - compact-hero-contract
used_by:
  - lt-brand-style-guide-consolidation
  - frappe-shop-showroom-symmetry
  - website-launch
tags:
  - Locally Twisted
  - responsive layout
  - container integrity
  - Playwright
  - accessibility
  - Frappe
  - Webshop
---

# Responsive Container Audit

Use this recipe when changing any public page layout, container, card grid, nav, drawer, modal, form, product selector, cart/checkout surface, or shared CSS that can affect how content fits at different widths.

Read `frappe-public-container-contract.md` first when the work touches Frappe's page shell, `.lt-fullbleed`, Webshop surfaces, crawls, marquees, or route-level containment. The audit verifies the chosen contract; it does not decide whether a section should be contained or full-bleed.

## When To Use

- Text, controls, images, chips, cards, menus, or form fields appear tight against a container edge.
- A page hero, intro, masthead, or marketing header changes height, padding, copy density, or title scale.
- A component changes layout across mobile, tablet, desktop, or near a breakpoint.
- Header/nav/drawer/mega-menu behavior changes.
- Product, category, cart, checkout, contact, portfolio, FAQ, policy, or homepage containers change.
- A fix passed one mobile width but may still fail at 320px, 390px, 414px, tablet, or desktop breakpoint edges.

## Core Rule

Every visible container is at risk until verified. Do not assume a page is stable because the default mobile and desktop screenshots look acceptable.

The current LT gate uses:

- `scripts/verify/layout_helpers.js` for shared route/viewport/layout audit logic.
- `scripts/verify/layout_fit.spec.js` for passive public route fit.
- `scripts/verify/container_contract.spec.js` for the executable route-level
  container contract: visible top-level `.page_content` children, full-bleed
  declarations, inner wrapper max widths, clipping surfaces, and Frappe wrapper
  neutralization.
- `scripts/verify/interactive_layout.spec.js` for stateful UI: header breakpoints, desktop mega panels, mobile drawer accordions, shop filters/product selectors, contact conditionals, portfolio front-photo state, and reduced-motion homepage checks.
- `scripts/verify/checkout_experience.spec.js` for checkout state behavior and preview consistency.
- `scripts/verify/a11y_audit.js` / `npm run test:a11y` for axe-core public route checks at desktop and mobile widths.
- `scripts/verify/manual_a11y_probe.js` / `npm run test:a11y-manual` for manual-style keyboard focus, visible-focus proxy, image-load, landmark, H1, and zoom-pressure checks across public routes.
- `npm run test:public-verify` for the aggregate public verification chain.

## Required Viewport Families

Use the helper viewport set before claiming a broad visual fix:

- 320px small phone pressure check.
- 360px Android.
- 375px iPhone baseline.
- 390px modern iPhone.
- 414px large phone.
- 768px tablet portrait.
- 820px tablet modern.
- 991px just below the legacy desktop breakpoint.
- 992px legacy breakpoint edge.
- 1024px tablet landscape.
- 1199px just below the active desktop nav breakpoint.
- 1200px active desktop nav breakpoint.
- 1366px common laptop.

Add route-specific widths when the changed surface has its own breakpoint.

## What The Audit Flags

- Document-level horizontal overflow.
- Visible elements extending outside the viewport unless inside an intentional clipping container.
- Direct text overflow inside its own box.
- Optional container-internal overflow for known risk areas.
- Small interactive targets where selectors are supplied.
- Stateful failures after drawers, accordions, mega panels, modals, filters, or option controls are opened.
- Hidden or offscreen focused elements, especially in crawls, carousels, portfolio reels, and label-proxied product selectors.

## Implementation Pattern

1. Read `_resources/STYLE-GUIDE.md`, especially the layout and verification sections.
2. Read `frappe-public-container-contract.md` when the work touches the Frappe shell, full-bleed bands, Webshop surfaces, or shared containment.
3. Identify all route families touched by the change.
4. Classify each changed section as contained workflow/reading surface or deliberate full-bleed band before writing CSS.
5. Add or update route-specific checks in `interactive_layout.spec.js` when the problem only appears after interaction.
6. Keep helper changes in `layout_helpers.js`; do not duplicate viewport lists or overflow logic in multiple specs.
7. Fix the actual container math: grid tracks, `min-width: 0`, `box-sizing`, padding, wrapping, max-width, image aspect ratios, and stable control dimensions.
8. For showcase rows, verify symmetry as well as fit. Equal-width category tiles, balanced card rows, and no single-card orphan row are part of the layout contract when products are being shown.
9. Avoid body-wide `overflow-x: hidden` as the primary fix.
10. Treat accessibility failures as layout closeout blockers too: color contrast, nested landmarks, unnamed links, heading order, breadcrumb regions, hidden focused elements, and offscreen tab stops must be fixed before launch claims.
11. Run cache clear after Frappe/Jinja/CSS changes.
12. Verify with the commands below.
13. Update the workstream/queue/decision/lesson docs if the fix changes the project standard.

## Verification Commands

```powershell
python scripts/dev/clear_website_cache.py
npm run test:a11y
npm run test:a11y-manual
npm run test:layout-fit
npm run test:container-contract
npm run test:interactive-layout
npm run test:checkout-experience
python scripts/verify/smoke_shop.py
npm run test:public-verify
```

Use `npm run test:public-verify` when closing a broad public-site visual change. It runs nav IA, passive layout fit, the route-level container contract, interactive layout fit, checkout experience, portfolio reel, and shop smoke with quieter Playwright output.

## Triage Notes

- If only one route fails, inspect that route's rendered DOM and container hierarchy before changing shared CSS.
- If several pages fail at the same width, suspect shared chrome, section wrappers, global grid rules, or Webshop defaults.
- If a carousel/track reports overflow but the document does not scroll and an ancestor clips it intentionally, tune the allowlist rather than hiding real failures.
- If native checkboxes/radios are visually hidden but the label/chip is the actual target, the visible label must receive the focus style and the manual a11y probe should treat it as the focus proxy.
- If a moving crawl/carousel item is not interactive, do not put it in the tab order. If it is interactive, it must not become focusable until it is visible.
- If a hero changes, run the `compact hero height contract` grep in
  `interactive_layout.spec.js`; route-local hero sizing is not allowed to drift
  outside the approved viewport-family standard.
- If a verifier fails because the business contract changed, update the verifier to the new source-of-truth behavior and preserve coverage for the old risk in the correct lane.

## LT Receipt

The first use on 2026-05-05 expanded `npm run test:layout-fit` from a narrow route/viewport pass to 260 checks across 20 public routes and 13 viewport families. It also added `npm run test:interactive-layout` with stateful checks for header breakpoint behavior, desktop mega panels, mobile drawer accordions, shop/product controls, contact conditionals, portfolio state, and reduced-motion homepage states. On 2026-05-06, the portfolio state check moved from the superseded modal behavior to the current proof-reel front-photo behavior. On 2026-05-07, the unapproved `/process` route was removed and homepage/nav proof checks expanded the gate to `layout-fit` 247/247 and `interactive-layout` 74/74; the compact hero contract then expanded the current interactive gate to 88/88. `python scripts/verify/smoke_shop.py` was corrected to respect the quote-required custom install lane while still verifying retail inline variant selection and cart writes.

The 2026-05-06 shop showroom repair added a symmetry-specific supplement, then the same-day UX repair superseded the button-grid category controls: `/shop` and `/shop-items/<group>` now use a desktop category rail plus native mobile select, and category/product grids must not leave a single desktop orphan card when a balanced 2-up split is available.

On 2026-05-07, the route-level container contract became executable via
`scripts/verify/container_contract.spec.js` and `npm run
test:container-contract`. The gate currently passes 57/57 checks across the
launch public route list at 320px, 820px, and 1366px, and is now part of
`npm run test:website-verify` / `npm run test:public-verify`.
