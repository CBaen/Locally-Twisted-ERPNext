# Frappe Sitewide Visual Overhaul

Use this recipe when changing the shared look of the LT public site across Frappe, Jinja, and Webshop routes.

## When To Use

- Shared header, footer, theme CSS, homepage, shop, product, cart, checkout, contact, or policy pages are changing together.
- The work changes the visual authority of the site, not only a single typo or copy edit.
- The outcome must be launch-safe enough for GL or Jeff to review in a browser.

## Pattern

1. Read `_resources/STYLE-GUIDE.md` and the active visual workstream before editing.
2. Identify every route family affected: static pages, Webshop listings, product detail, cart, checkout, contact, success pages.
3. Keep the implementation Frappe-native:
   - shared CSS in the app asset bundle,
   - Jinja partial overrides for header/footer,
   - route controllers under `apps/locally_twisted/locally_twisted/www/`,
   - Webshop hooks/templates where Webshop owns the flow.
4. Bump the theme CSS query string in `hooks.py`.
5. Clear the website cache after Jinja/CSS edits.
6. Restart the backend if Python controller constants changed.
7. Verify routes by status and behavior.
8. Run layout and contract checks that cover the touched route families.
9. Capture desktop and mobile screenshots and inspect them before claiming the visual pass is ready.
10. Update the relevant workstream, queue, decisions, lessons, and handoff docs in the same closeout.

## Verification Checklist

- `python scripts/dev/clear_website_cache.py --restart`
- Main route status checks, including `/`, `/contact`, `/shop`, product detail, `/cart`, `/checkout`, policies, and success pages.
- `python scripts/verify/nav_ia.py`
- `npm run test:layout-fit`
- `python scripts/verify/smoke_shop.py`
- Cart, checkout, catalog, variant media, and contact/form contract checks when those surfaces changed.
- Desktop and mobile screenshots saved under `output/playwright/<feature-slug>/`.

## LT Receipt

The first complete use was the 2026-05-03 Civic Celebration site-wide overhaul. It produced the current V1 visual direction, added `hero-wasatch-city-20260503.png`, replaced the old script header treatment with a stronger wordmark, and verified the customer-facing route set with route checks, layout checks, contracts, and screenshots.
