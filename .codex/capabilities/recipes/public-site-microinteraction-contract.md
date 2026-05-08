---
id: public-site-microinteraction-contract
name: Public Site Microinteraction Contract
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted ERPNext/Frappe public-site card-click and small interaction flourishes
currently_true: true
verification_level: 2
last_verified: 2026-05-08
evidence_quality: direct
successful_uses: 1
failed_uses: 1
regressions: 0
depends_on:
  - frappe-public-container-contract
  - responsive-container-audit
  - cross-browser-motion-visual-verification
used_by:
  - website-launch
  - shop
tags:
  - Locally Twisted
  - Frappe
  - Webshop
  - microinteractions
  - product cards
  - launch verification
---

# Public Site Microinteraction Contract

Use this recipe when adding small public-site interactions such as card-wide navigation, hover affordance, or other motion/behavior that is not core checkout/form logic but still ships to customers.

## Contract

Microinteractions must improve feel or ease without creating false success, invalid HTML, inaccessible behavior, route overflow, or a second source of truth.

Production behavior belongs in focused app assets loaded through Frappe hooks:

- CSS under `apps/locally_twisted/locally_twisted/public/css/`.
- JS under `apps/locally_twisted/locally_twisted/public/js/`.
- Hook entries in `apps/locally_twisted/locally_twisted/hooks.py` with cache-busted URLs.

Do not paste prototype/demo pages into route templates. Extract the useful behavior, then delete transient reference files unless they are intentionally kept under `_resources/` as approved source material.

## Retired Cursor And Motion Rules

- The red balloon cursor is retired. Do not re-enable it without a fresh GL decision.
- If a future custom cursor is approved, hide the system cursor only for fine-pointer desktop users.
- Do not run future custom cursors on touch/coarse-pointer devices.
- Keep any future cursor elements `aria-hidden` and `pointer-events: none`.
- Respect `prefers-reduced-motion`; remove decorative animations that are not needed for use.
- Clamp decorative cursor and click-ring positions inside the viewport. Layout gates treat offscreen decorative elements as real overflow.
- Keep motion restrained. If fast pointer movement makes the cursor whip or jitter, lower spring response, reduce sway force, increase return, and cap rotation.

## Product Card Rules

- Whole-card navigation must not wrap cards that contain buttons or action links.
- Use delegated click handling from a focused JS file.
- Ignore real interactive descendants: links, buttons, inputs, selects, labels, summaries, role buttons, contenteditable nodes, and any `data-no-card-click` zone.
- Preserve add-to-cart, quote, and choose-options behavior.
- Restrict inferred card links to same-origin `/shop-items/` URLs.
- Add a class for pointer affordance, but keep keyboard navigation through the existing links/buttons.

## Verification

After microinteraction changes:

1. Run syntax checks for changed JS and Python hook files.
2. Clear website cache with `python scripts/dev/clear_website_cache.py`.
3. Verify served HTML contains the cache-busted asset URLs and each asset URL returns `200`.
4. Use a browser check for the actual behavior:
   - retired cursor assets are absent unless a new cursor has been explicitly approved,
   - any approved decorative elements stay inside the viewport,
   - product-card body clicks navigate,
   - add-to-cart/quote/options controls still do their original action,
   - no console or page errors.
5. Run the relevant public gates:
   - `npm run test:shop-smoke` for product card behavior,
   - `npm run test:layout-fit`,
   - `npm run test:interactive-layout`,
   - `npm run test:a11y`,
   - `npm run test:a11y-manual`.

Use `npm run test:public-verify` or `npm run test:launch-verify` when the change is broad enough to need the full website story.

## Receipt

On 2026-05-08, a red balloon cursor demo was briefly translated into focused production assets, then retired the same day at GL's request. The transient demo HTML stayed deleted, and the production cursor CSS/JS plus hook entries were removed so the site uses the normal system cursor.

The same slice added delegated whole-card navigation for `/shop` and Webshop category cards. The implementation preserved `Add to cart`, `Choose options`, and `Request quote` behavior instead of wrapping cards in invalid nested anchors. Verification proved 53 `/shop` cards clickable, category cards clickable after Webshop render, add-to-cart still working, `shop-smoke` passing, `layout-fit` 247/247, `interactive-layout` 88/88, axe 38 route/viewport results with 0 violations, and manual accessibility passing.
