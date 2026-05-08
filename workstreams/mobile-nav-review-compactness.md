# Mobile Nav And Review Compactness

Last updated: 2026-05-08 by Codex.

## Purpose

This handoff owns the mobile public chrome correction GL requested on
2026-05-08: keep the Locally Twisted logo clear, keep cart/menu usable, move
search to the bottom of the mobile drawer, and make the homepage Google review
proof section compact on mobile.

This is a launch-surface feature handoff, not a new broad visual direction.

## Current State

Complete as of 2026-05-08:

- Mobile header contains only the logo, cart button, and menu button.
- The mobile search control lives at the bottom of `#lt-mobile-nav` as
  `.lt-mega-drawer__search`.
- Drawer search is a button, not an anchor. It opens `#lt-site-search-panel`
  and must not link to Frappe's bundled `/search` page.
- Opening search from the drawer closes the drawer before focusing the search
  input.
- `/search` is intentionally overridden by `www/search.py` / `www/search.html`
  as a no-cache 404 fallback so public navigation cannot accidentally expose
  the bundled Frappe search page.
- Mobile Google review proof is compact: live browser measurements after cache
  clear showed the review block at about `364px` high across 320px, 375px,
  390px, and 414px viewports. Before this pass, 320px measured about `693px`.
- The review marquee explicitly neutralizes global `section` padding on mobile
  so the cards cannot inherit the old 2rem top/bottom padding.
- `interactive_layout.spec.js` now guards the mobile review sizing contract:
  review block <= 380px, marquee <= 240px, cards <= 270px wide and <= 240px
  high, compact badge <= 76px, compact section padding, and no global section
  padding leakage into `.lt-reviews-block__quotes`.

## Source Files

- `apps/locally_twisted/locally_twisted/templates/includes/navbar/navbar.html`
- `apps/locally_twisted/locally_twisted/public/css/lt-mega-menu.css`
- `apps/locally_twisted/locally_twisted/public/js/lt-megamenu.js`
- `apps/locally_twisted/locally_twisted/www/search.py`
- `apps/locally_twisted/locally_twisted/www/search.html`
- `apps/locally_twisted/locally_twisted/www/home.py`
- `scripts/verify/nav_ia.py`
- `scripts/verify/smoke_shop.py`
- `scripts/verify/interactive_layout.spec.js`

Related capability contracts:

- `.codex/capabilities/recipes/frappe-public-nav-business-route-contract.md`
- `.codex/capabilities/recipes/homepage-launch-proof-contract.md`
- `.codex/capabilities/recipes/responsive-container-audit.md`

## Verification Receipt

Fresh verification run on 2026-05-08:

```powershell
python scripts/dev/clear_website_cache.py --restart
python -m py_compile scripts/verify/nav_ia.py scripts/verify/smoke_shop.py apps/locally_twisted/locally_twisted/www/home.py
node --check apps/locally_twisted/locally_twisted/public/js/lt-megamenu.js
python scripts/verify/nav_ia.py
npx playwright test scripts/verify/interactive_layout.spec.js --grep "small mobile header|search opens as an overlay|expanded drawer fits at 320px|expanded drawer fits at 390px|mobile review proof|reviews crawl left-to-right" --reporter=line --workers=1
npx playwright test scripts/verify/layout_fit.spec.js --grep "home fits at mobile-320|home fits at mobile-390|home fits at desktop-1200" --reporter=line --workers=1
```

Results:

- `nav_ia.py` passed.
- Targeted interactive Playwright checks passed 8/8.
- Targeted homepage layout-fit checks passed 3/3.
- Mobile drawer smoke helper passed by direct invocation of
  `check_mobile_drawer`.
- Screenshot-backed browser pass at 320px and 1366px returned non-empty
  screenshots, mobile drawer visible at x ~= 49 with width 272, and mobile
  search overlay visible after clicking the bottom drawer search button.

## Rules For Future Agents

- Do not put search back into `.lt-mega-header__mobile-actions`; the mobile
  header is space-constrained and must remain logo plus cart/menu.
- Do not restore a public `/search` nav link. Search is an overlay that submits
  to `/shop?q=...`.
- Do not remove the bottom drawer search verifier when changing menu order.
- Do not let global `section` padding apply to `.lt-reviews-block__quotes` on
  mobile.
- If the review copy/cards change, rerun the compact sizing test and live
  mobile measurements before claiming the section still fits.
- Full `smoke_shop.py` may be affected by unrelated active shop/product lanes in
  this shared worktree. Use the focused drawer smoke path for this feature, and
  do not claim the full shop smoke is green unless it is rerun and passes.
