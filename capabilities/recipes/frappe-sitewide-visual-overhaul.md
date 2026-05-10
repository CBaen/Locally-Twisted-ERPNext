---
id: frappe-sitewide-visual-overhaul
name: Frappe Sitewide Visual Overhaul
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted ERPNext/Frappe public site visual work
currently_true: yes
verification_level: 2
last_verified: 2026-05-07
evidence_quality: direct
successful_uses: 3
failed_uses: 0
regressions: 0
depends_on:
  - frappe-public-container-contract
  - frappe-public-nav-business-route-contract
  - responsive-container-audit
used_by: []
tags:
  - Locally Twisted
  - Frappe
  - Webshop
  - visual overhaul
  - launch verification
---

# Frappe Sitewide Visual Overhaul

Use this recipe when changing the shared look of the LT public site across Frappe, Jinja, and Webshop routes.

## When To Use

- Shared header, footer, theme CSS, homepage, shop, product, cart, checkout, contact, or policy pages are changing together.
- The work changes the visual authority of the site, not only a single typo or copy edit.
- The outcome must be launch-safe enough for GL or Jeff to review in a browser.

## Pattern

1. Read `_resources/STYLE-GUIDE.md` and the active visual workstream before editing.
2. Read `frappe-public-container-contract.md` and classify the affected sections as contained workflow/reading surfaces or deliberate full-bleed bands.
3. Identify every route family affected: static pages, Webshop listings, product detail, cart, checkout, contact, success pages.
4. Keep the implementation Frappe-native:
   - shared CSS in the app asset bundle,
   - Jinja partial overrides for header/footer,
   - route controllers under `apps/locally_twisted/locally_twisted/www/`,
   - Webshop hooks/templates where Webshop owns the flow.
5. Wire every new public asset in `hooks.py`; do not assume files under `public/` are being served.
6. Bump cache keys for every changed CSS/JS asset in `hooks.py`.
7. Clear the website cache after Jinja/CSS edits.
8. Restart backend/frontend if `hooks.py`, Python controllers, or website context hooks changed, then clear cache again.
9. Verify the served page HTML contains the expected cache-busted CSS/JS URLs.
10. Verify routes by status and behavior.
11. Run layout and contract checks that cover the touched route families.
12. For broad public-site changes, run the responsive container audit gate, including stateful UI checks.
13. Capture desktop and mobile screenshots and inspect them before claiming the visual pass is ready.
14. Update the relevant workstream, queue, decisions, lessons, and handoff docs in the same closeout.

## Verification Checklist

- Restart backend/frontend when hooks changed, then `python scripts/dev/clear_website_cache.py`
- Served HTML/asset checks for cache-busted CSS and JS URLs.
- Main route status checks, including `/`, `/contact`, `/shop`, product detail, `/cart`, `/checkout`, policies, and success pages.
- `python scripts/verify/nav_ia.py`
- `npm run test:layout-fit`
- `npm run test:interactive-layout`
- `npm run test:public-verify` for broad public-site visual changes.
- `python scripts/verify/smoke_shop.py`
- Cart, checkout, catalog, variant media, and contact/form contract checks when those surfaces changed.
- Desktop and mobile screenshots saved under `output/playwright/<feature-slug>/`.

## LT Receipts

The first complete use was the 2026-05-03 Civic Celebration site-wide overhaul. It produced the current V1 visual direction, added `hero-wasatch-city-20260503.png`, replaced the old script header treatment with a stronger wordmark, and verified the customer-facing route set with route checks, layout checks, contracts, and screenshots.

The second complete use was the 2026-05-05 mega-menu/product-containment takeover. It restored the deliberate two-level premium header, served `lt-mega-menu.css`, `lt-page-containment.css`, `lt-product-polish.css`, and `lt-megamenu.js` through hooks, fixed hover/click menu semantics, repaired mobile containment issues, and verified with `nav_ia.py`, `smoke_shop.py`, `layout_fit`, served asset checks, and post-fix Playwright screenshots.

The responsive-container follow-up on 2026-05-05 promoted breakpoint/container stability into a standing gate: `layout_fit` now covers 260 passive route/viewport checks, `interactive_layout` covers 39 stateful checks, and `test:public-verify` runs nav IA, passive layout, interactive layout, checkout experience, and shop smoke with quieter Playwright output.

The 2026-05-07 BTFP/Process correction showed that broad visual work must treat
navigation as business IA, not only layout chrome. The approved `Twisting & Face
Painting` service route was restored to the primary nav, the unapproved
standalone `/process` route files were deleted, and `nav_ia.py`/`smoke_shop.py`
now guard the replacement.
