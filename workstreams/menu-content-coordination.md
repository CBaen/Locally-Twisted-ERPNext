# Menu And Content Coordination

Last updated: 2026-05-05 by Codex.

## Purpose

This is the live coordination board for agents touching the public menu, header, footer, page content, and related verifiers during the authority-first site replacement.

Before editing any nav, chrome, public page hero/body copy, footer links, or nav/content verifier, update this file with your lane, files, and status. If two agents need the same file, mark it here before editing.

## Active Rules

- Add your session/name, timestamp, lane, and intended files before editing.
- Do not edit another active lane's files without adding a note here first.
- Treat `workstreams/website-launch.md` as the broader launch lane; use this file for menu/content collisions.
- Keep `/contact` as the shared conversion path unless Guiding Light explicitly changes the architecture.
- Do not claim a route, drawer, form, or verifier is fixed without recording the command and result.

## Style-Guide Alignment Note For Menu/Content Agents

The coordination doc is a collision board, not a replacement style guide. The current visual authority is `_resources/STYLE-GUIDE.md` v4.2.

For this nav/content lane, stay inside these rules:

- Approved direction is Civic Celebration + Slate Blue/Berry + Image #3 Brand Direction quality.
- Do not revive the deleted light-blue/blush/pastel design-guide direction.
- Do not use generic weak icon sets for brand proof; use or extend the custom brass-line balloon/local/event icon system.
- Header/nav must feel premium and accessible: large brand/logo treatment, readable Lato nav labels, disciplined spacing, rectangular CTA, and no tiny text-company-name fallback.
- The real Locally Twisted logo/brand asset requirement is still active. If the logo asset cannot be used cleanly yet, mark that as an unresolved nav issue instead of shrinking the brand to plain tiny text.
- Treat missing `lt-megamenu.js` as a bug in the current architecture. GL reopened mega-menu IA and chose the deliberate premium mega-menu; if that changes later, update the style guide, nav verifier, and smoke tests together.
- Keep `/contact` as the quote/conversion route. Do not send event/custom-work CTAs back to `/book` or old occasion shortcut routes.
- Before changing `navbar.html`, header CSS, `hooks.py`, `nav_ia.py`, or `smoke_shop.py`, claim the nav/chrome lane here so agents do not fight each other.

## Active Lanes

| Lane | Owner | Files / Surface | Status |
|---|---|---|---|
| Nav/chrome and live menu assets | Codex current session | `templates/includes/navbar/navbar.html`, `navbar_context.py`, header portions of `public/css/lt-theme.css`, `hooks.py`, `public/js/lt-megamenu.js`, `public/css/lt-mega-menu.css`, `scripts/verify/nav_ia.py`, `scripts/verify/smoke_shop.py` | Complete for current takeover. Mega-menu is restored deliberately, served through hooks, and verified with desktop click-pin behavior plus mobile drawer accordions. Reopen only with a new claim. |
| Authority page content and route pages | Codex current session | `www/home.*`, `www/event_balloons.*`, `www/process.*`, `www/portfolio.*`, `www/contact.*`, `www/shop.*`, supporting public content pages | Current containment pass complete. Remaining work is photo/trust-count/content review, not emergency container overflow repair. |
| Owner package and screenshots | Unclaimed | `_resources/brand-direction-architecture-2026-05/`, desktop/mobile renders, route map, builder notes | Pending. Use screenshots from the actual Frappe pages after route/content replacement, not disconnected mockups. |

## Current Conflict Notes

- `navbar_context.py` is restored and is part of the active mega-menu contract.
- `scripts/verify/smoke_shop.py` now verifies the deliberate mega-menu contract, not the retired simple-nav contract.
- `lt-megamenu.js` is served through `hooks.py` with the current cache key and must stay cache-busted when edited.

## Evidence Recorded This Session

- Route sweep returned 200 for `/`, `/event-balloons`, `/portfolio`, `/process`, `/contact`, `/shop`, `/faq`, `/balloon-twisting-and-face-painting`, `/privacy`, `/terms-of-service`, `/refund-policy`, `/accessibility`, `/cart`, `/checkout`, `/payment-success`, `/thank-you`, `/shop-items/arches`, and `/shop-items/garlands/baby-shower-garland`.
- `python scripts/verify/nav_ia.py` passed after the authority-first nav update.
- `npm run test:layout-fit` initially passed 80/80 after the header/product/page containment repair; this is superseded by the 260/260 responsive follow-up below.
- `python scripts/verify/contact_service_logic.py --base-url http://localhost:8081` passed.
- `python scripts/verify/contact_prefill.py --base-url http://localhost:8081` passed.
- `python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --shape-only --skip-newsletter` passed.
- `python scripts/verify/cart_checkout_contract.py` passed.
- `python scripts/verify/smoke_shop.py` passed after updating the verifier to the restored mega-menu contract.
- `npm run test:layout-fit` initially passed 80/80 after adding `/checkout` and `/thank-you`; this is superseded by the 260/260 responsive follow-up below.
- Responsive follow-up expanded the passive layout gate to 260/260 and added `npm run test:interactive-layout` at 39/39. Future menu/content work should use the responsive-container workstream instead of relying on the old 80-check gate.
- `python scripts/verify/smoke_shop.py` now verifies quote-required custom install product pages separately from retail variant add-to-cart pages.
- Served asset check found `lt-mega-menu.css`, `lt-page-containment.css`, `lt-product-polish.css`, and `lt-megamenu.js?v=20260505-mega-4` in the running page.
- Post-fix Playwright screenshot/interaction pass saved to `output/playwright/full-site-fix-20260505-post/` and reported no failures across 13 routes at 320, 375, and 1366 widths, plus desktop event/product mega menus and the mobile drawer.

## Handshake Template

Add a short entry below before editing contested files:

```text
### 2026-05-05 - <agent/session>
Lane:
Files:
Intent:
Conflicts:
Verification:
Status:
```

## Session Notes

### 2026-05-05 - Worker A
Lane: Mega-menu header restoration.
Files: `navbar.html`, `navbar_context.py`, `lt-megamenu.js`, `lt-mega-menu.css`, `nav_ia.py`, this coordination note.
Intent: Restore the deliberate two-level premium header with real logo treatment, product/event mega panels, accessible mobile drawer, and verifier coverage for `/contact`, stale `/book`, and retired `/shop-by-category`.
Conflicts: Staying out of `hooks.py`, `lt-theme.css`, and `smoke_shop.py`; parent owns include integration and final browser/cache checks.
Verification: `python scripts/verify/nav_ia.py` passed; `python -m py_compile apps/locally_twisted/locally_twisted/navbar_context.py scripts/verify/nav_ia.py` passed; `node --check apps/locally_twisted/locally_twisted/public/js/lt-megamenu.js` passed.
Status: Worker A source contract complete. Parent still owns `hooks.py`/`lt-theme.css` include integration, cache clear, build, and browser screenshots.

### 2026-05-05 - Codex current session
Lane: Authority page content and route pages.
Files: `home.*`, `event_balloons.*`, `process.*`, `portfolio.*`, `contact.*`, `shop.*`, `lt-theme.css`, nav/footer templates, route/verifier files touched during the authority-first pass.
Intent: Replace catalog-first public positioning with Utah event authority while keeping products as the secondary ready-to-order lane.
Conflicts: Superseded by the nav/chrome claim and takeover closeout below.
Verification: See evidence above.
Status: Content/routes draft implemented; nav/chrome needs coordinated owner review.

### 2026-05-05 - Codex current session response to style-guide note
Lane: Authority page content and route pages.
Files: `workstreams/menu-content-coordination.md` only.
Intent: Acknowledge the style-guide alignment note and keep `_resources/STYLE-GUIDE.md` v4.2 as the visual authority for menu/content work.
Conflicts: No code files touched. Nav/chrome remains unclaimed and contested.
Verification: Read `_resources/STYLE-GUIDE.md`; header confirms version 4.2, last updated 2026-05-05, and the Civic Celebration + Slate Blue/Berry + Brand Direction contract.
Status: Notes aligned. I will keep content work inside the current style guide and will not restore or delete the mega-menu layer unless the nav/chrome lane is claimed and decided.

### 2026-05-05 - Codex current session nav/chrome claim
Lane: Nav/chrome and live menu assets.
Files: `navbar.html`, `navbar_context.py`, header CSS in `lt-theme.css`, `hooks.py`, `lt-megamenu.js`, `nav_ia.py`, `smoke_shop.py`, plus product-page CSS if containment defects trace there.
Intent: GL chose "mega-menu restore/build it deliberately." Restore the mega-menu as an intentional premium two-level header, fix the missing served JS asset, and address the visible container/text/product-page style defects.
Conflicts: This supersedes the simple authority-first nav cleanup. Other agents should pause edits to the files above until this lane posts verification.
Verification: Superseded by takeover closeout below.
Status: Superseded; see completed closeout.

### 2026-05-05 - Codex current session takeover closeout
Lane: Nav/chrome, containment, and product/shop visual repair.
Files: `hooks.py`, `navbar.html`, `navbar_context.py`, `website_context.py`, `lt-megamenu.js`, `lt-mega-menu.css`, `lt-page-containment.css`, `lt-product-polish.css`, `lt-theme.css`, `home.*`, `portfolio.py`, product/shop templates, `layout_fit.spec.js`, `nav_ia.py`, `smoke_shop.py`, and related docs.
Intent: Take over after the prior agent stopped, restore the deliberate premium mega-menu, fix served assets, repair cramped/overflowing mobile sections, and bring product/category/shop pages onto the current style guide.
Conflicts: Resolved for this lane. Future agents must not replace the mega-menu with a simple header without a fresh GL decision.
Verification: `python scripts/verify/nav_ia.py` passed; `python scripts/verify/smoke_shop.py` passed; initial `npm run test:layout-fit` passed 80/80 and was later expanded to 260/260; served asset checks returned 200; post-fix Playwright screenshot/interaction pass reported no failures.
Status: Complete for takeover. Remaining visual work is curated imagery/trust-count review, not broken container/menu repair.

### 2026-05-05 - Codex responsive container closeout
Lane: Responsive container integrity and public verification gates.
Files: `layout_helpers.js`, `layout_fit.spec.js`, `interactive_layout.spec.js`, `smoke_shop.py`, `package.json`, `_resources/STYLE-GUIDE.md`, `.codex/capabilities/recipes/responsive-container-audit.md`, and docs.
Intent: Make breakpoint-edge and stateful container fit a standing gate for menu/content/product/page work.
Conflicts: Does not reopen the restored mega-menu decision. The product smoke update follows the current commerce rule: custom installs quote, retail variants cart.
Verification: `npm run test:layout-fit` passed 260/260; `npm run test:interactive-layout` passed 39/39; `npm run test:checkout-experience` passed 1/1; `python scripts/verify/smoke_shop.py` passed; `npm run test:public-verify` passed with quieter Playwright output.
Status: Complete. Use `npm run test:public-verify` for broad public-site closeout.
