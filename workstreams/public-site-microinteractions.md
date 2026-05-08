# Public Site Microinteractions

Last updated: 2026-05-08 by Codex after GL retired the balloon cursor and kept whole-card product navigation.

## Outcome

Add easier product browsing without weakening launch-critical routes, accessibility, cart behavior, or Frappe/Webshop ownership.

This is the focused feature handoff for sitewide public microinteractions. It does not replace `workstreams/website-launch.md`, `workstreams/shop.md`, or the responsive/container capability recipes.

## Current Stage

Complete for this slice.

- The sitewide balloon cursor is retired at GL's request. Do not re-enable it without a fresh decision.
- Touch/coarse-pointer devices and desktop users all keep the normal system cursor.
- Product cards on `/shop` and Webshop-rendered category pages navigate from non-interactive card areas.
- Existing links and controls keep their own behavior: `Add to cart`, `Choose options`, `Request quote`, selectors, and other controls are not hijacked.
- The transient reference file `assets/balloon cursor/Red Balloon Cursor.html` remains deleted.

## Touched Files

- `apps/locally_twisted/locally_twisted/public/js/lt-product-card-click.js`
- `apps/locally_twisted/locally_twisted/public/css/lt-shop-showroom.css`
- `apps/locally_twisted/locally_twisted/hooks.py`

Related launch verifier work from the same session:

- `scripts/verify/website_launch_verify.py`
- `package.json`
- `playwright.config.js`

## Current Contract

### Retired Balloon Cursor

- The red balloon cursor CSS/JS files and Frappe hook entries are removed.
- Do not restore a custom cursor from the old demo or from this handoff without GL explicitly reopening the interaction.
- If a future custom cursor is approved, treat it as a fresh production UX slice with cache-busted assets, accessibility boundaries, browser verification, and layout overflow gates.

### Product Card Clicks

- Use delegated JS for card-wide navigation.
- Do not wrap entire cards in anchors when cards contain buttons or action links.
- Ignore clicks from links, buttons, form controls, role buttons, summaries, contenteditable nodes, and `data-no-card-click` areas.
- Resolve only same-origin `/shop-items/` product links.
- Preserve text selection and modified clicks.
- Mark clickable cards with `.lt-product-card-clickable` for the pointer affordance.

## Verification

Cursor retirement closeout on 2026-05-08:

- Deleted `lt-balloon-cursor.css` and `lt-balloon-cursor.js`.
- Removed the cursor CSS/JS hook entries from `hooks.py`.
- Served homepage no longer contains `lt-balloon-cursor` assets or `.lt-balloon-cursor` DOM nodes after cache clear/restart.
- Red dog favicon serves from `/assets/locally_twisted/icons/lt-favicon.png?v=20260508-red-dog-1`, returns `200`, and is resized to 64x64.

Whole-card navigation closeout passed on 2026-05-08:

- Syntax: `node --check` for card-click JS and `python -m py_compile` for `hooks.py`.
- Cache: `python scripts/dev/clear_website_cache.py`.
- Targeted browser check: all 53 `/shop` cards became clickable, Webshop category cards became clickable after render, single-SKU add-to-cart stayed on the page and added the item, no console errors.
- `npm run test:shop-smoke`.
- `npm run test:layout-fit` passed 247/247.
- `npm run test:interactive-layout` passed 88/88 during the original closeout; rerun the relevant public gates after any future card-click or motion change.
- `npm run test:a11y` passed 38 route/viewport axe results with 0 violations.
- `npm run test:a11y-manual` passed.

Current caveat from the favicon/cursor retirement pass: a targeted browser
click on `/shop` card text still navigated to the product route, but the broad
`python scripts/verify/smoke_shop.py` gate is not currently green in the shared
worktree. It fails on the variant-chip checkbox contract and a stale/mismatched
homepage nav `Portfolio` assertion before this slice's behavior is reached.
Use the shop/menu lane to repair that gate before claiming a fresh full
shop-smoke pass.

## Open Follow-Up

None for this slice.

Future microinteractions should be treated as production UX only when they improve launch confidence or customer ease. Keep demos, experiments, and generated references out of the repository after their production code is extracted, and do not bring back custom cursors without a fresh GL decision.
