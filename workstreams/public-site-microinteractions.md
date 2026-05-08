# Public Site Microinteractions

Last updated: 2026-05-08 by Codex after balloon cursor and whole-card product navigation closeout.

## Outcome

Add small public-site delight and easier product browsing without weakening launch-critical routes, accessibility, cart behavior, or Frappe/Webshop ownership.

This is the focused feature handoff for sitewide public microinteractions. It does not replace `workstreams/website-launch.md`, `workstreams/shop.md`, or the responsive/container capability recipes.

## Current Stage

Complete for this slice.

- A sitewide balloon cursor is active for fine-pointer desktop users only.
- Touch/coarse-pointer devices keep normal behavior.
- Reduced-motion users do not get the click-ring animation.
- The cursor is production code in LT app assets, not the source demo HTML.
- Product cards on `/shop` and Webshop-rendered category pages navigate from non-interactive card areas.
- Existing links and controls keep their own behavior: `Add to cart`, `Choose options`, `Request quote`, selectors, and other controls are not hijacked.
- The transient reference file `assets/balloon cursor/Red Balloon Cursor.html` was deleted after production assets landed.

## Touched Files

- `apps/locally_twisted/locally_twisted/public/css/lt-balloon-cursor.css`
- `apps/locally_twisted/locally_twisted/public/js/lt-balloon-cursor.js`
- `apps/locally_twisted/locally_twisted/public/js/lt-product-card-click.js`
- `apps/locally_twisted/locally_twisted/public/css/lt-shop-showroom.css`
- `apps/locally_twisted/locally_twisted/hooks.py`

Related launch verifier work from the same session:

- `scripts/verify/website_launch_verify.py`
- `package.json`
- `playwright.config.js`

## Current Contract

### Balloon Cursor

- Keep it in focused CSS/JS files; do not paste the demo page into Frappe templates.
- Load only through `web_include_css` and `web_include_js`.
- Bump the hook cache key when changing cursor CSS or JS.
- Do not run on touch/coarse-pointer devices.
- Keep the cursor `aria-hidden` and `pointer-events: none`.
- Clamp decorative cursor and click-ring positions inside the viewport so layout gates do not report overflow.
- Keep motion gentle enough for a brand flourish; avoid fast whipping or large tilt.

### Product Card Clicks

- Use delegated JS for card-wide navigation.
- Do not wrap entire cards in anchors when cards contain buttons or action links.
- Ignore clicks from links, buttons, form controls, role buttons, summaries, contenteditable nodes, and `data-no-card-click` areas.
- Resolve only same-origin `/shop-items/` product links.
- Preserve text selection and modified clicks.
- Mark clickable cards with `.lt-product-card-clickable` for the pointer affordance.

## Verification

Latest closeout passed on 2026-05-08:

- Syntax: `node --check` for both JS files and `python -m py_compile` for `hooks.py`.
- Cache: `python scripts/dev/clear_website_cache.py`.
- Served assets: home/shop HTML includes the new cache-busted CSS/JS URLs, and the asset URLs return `200`.
- Targeted browser check: all 53 `/shop` cards became clickable, Webshop category cards became clickable after render, single-SKU add-to-cart stayed on the page and added the item, cursor tilt capped at 12 degrees, no console errors.
- `npm run test:shop-smoke`.
- `npm run test:layout-fit` passed 247/247.
- `npm run test:interactive-layout` passed 88/88 after an intentional fix for cursor overflow.
- `npm run test:a11y` passed 38 route/viewport axe results with 0 violations.
- `npm run test:a11y-manual` passed.

## Open Follow-Up

None for this slice.

Future microinteractions should be treated as production UX only when they improve launch confidence or customer ease. Keep demos, experiments, and generated references out of the repository after their production code is extracted.
