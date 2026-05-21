# Menu And Content Coordination

Last updated: 2026-05-10 by Codex.

## Purpose

This is the live coordination board for agents touching the public menu, header, footer, page content, and related verifiers during the authority-first site replacement.

Before editing any nav, chrome, public page hero/body copy, footer links, or nav/content verifier, update this file with your lane, files, and status. If two agents need the same file, mark it here before editing.

## Active Rules

- Add your session/name, timestamp, lane, and intended files before editing.
- Do not edit another active lane's files without adding a note here first.
- Treat `workstreams/website-launch.md` as the broader launch lane; use this file for menu/content collisions.
- Keep `/contact` as the shared conversion path unless Guiding Light explicitly changes the architecture.
- Current public chrome includes `Twisting & Face Painting` pointing to `/balloon-twisting-and-face-painting`, an event-audience dropdown linking only to `/civic-community`, `/corporate-events`, `/schools-campuses`, and `/private-celebrations`, `Ready-to-Order` pointing to `/shop` while ecommerce is open for testing, `Contact Us` pointing to `/contact`, and top-banner-only `Free Event Quote` pointing to `/contact`. `Ready-to-Order` menu/search/drawer entries are category discovery sourced from visible `Item Group` children of `Shop Items`; do not restore product quick links or ERPNext/backend copy in the public dropdown. The short-notice sentence `SHORT NOTICE? LET US KNOW. WE CAN OFTEN HELP WITH 24 HOURS NOTICE!` is a centered deep-navy `/contact` link on desktop and a matching visible deep-navy `/contact` strip on mobile; the account link remains on the desktop right. The old prepared-design proof copy and delivery/truck icon are removed. `Ready-to-Order`, `Cart`, and `Recent Work` do not belong in the top banner, and `Free Event Quote` must not appear in primary nav, mobile drawer, or search quick results. Banner text stays warm-white on navy; brass is accent only. Mobile safe-area left/right padding must match the physical sides. Do not remove, hide, rename, or replace the BTFP lane unless GL explicitly approves the exact action and `workstreams/nav-service-removal-approvals.md` records the required marker. Do not restore standalone `/process` or `/event-balloons` pages or links without explicit GL approval.
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
| Nav/chrome and live menu assets | Codex current session | `templates/includes/navbar/navbar.html`, `navbar_context.py`, header portions of `public/css/lt-theme.css`, `hooks.py`, `public/js/lt-megamenu.js`, `public/css/lt-mega-menu.css`, `scripts/verify/nav_ia.py`, `scripts/verify/smoke_shop.py` | Complete 2026-05-11: public ecommerce chrome is open for local testing, `Ready-to-Order` points to `/shop`, `Twisting & Face Painting` remains in public chrome, `Contact Us` points to `/contact`, top-banner `Free Event Quote` points to `/contact`, the 24-hour short-notice message is a centered deep-navy `/contact` link on desktop and a visible deep-navy `/contact` strip on mobile, account link remains, the prepared-design proof copy/truck icon are removed, Process is removed from customer-facing chrome, mobile search lives at the bottom of the drawer, and navy banner color is guarded in source and rendered tests. |
| Authority page content and route pages | Codex current session | `www/home.*`, deleted `www/event_balloons.*`, `www/balloon_twisting_and_face_painting.*`, `www/portfolio.*`, `www/contact.*`, `www/shop.*`, supporting public content pages | Complete 2026-05-11: standalone Process route files remain removed; `/event-balloons` route files are deleted with no redirect; BTFP remains the approved live-service route and the four event audience pages remain live. |
| Owner package and screenshots | Unclaimed | `_resources/brand-direction-architecture-2026-05/`, desktop/mobile renders, route map, builder notes | Pending. Use screenshots from the actual Frappe pages after route/content replacement, not disconnected mockups. |

Feature handoff for the BTFP/Process correction: `workstreams/nav-btfp-process-correction.md`.
Feature handoff for mobile search/review compactness:
`workstreams/mobile-nav-review-compactness.md`.
Feature handoff for the top banner and quote-label contract:
`workstreams/public-header-banner-contract-2026-05-10.md`.
Feature handoff for the removed Event Balloons hub route:
`workstreams/event-balloons-route-removal-2026-05-11.md`.
Feature handoff for the homepage review platform proof strip:
`workstreams/homepage-review-platform-proof-2026-05-11.md`.
Feature handoff for the Ready-to-Order category menu correction:
`workstreams/ready-to-order-category-menu-2026-05-21.md`.

## Current Conflict Notes

- `navbar_context.py` is restored and is part of the active mega-menu contract.
- `scripts/verify/smoke_shop.py` now verifies the deliberate mega-menu contract, not the retired simple-nav contract.
- `lt-megamenu.js` is served through `hooks.py` with the current cache key and must stay cache-busted when edited.

## Evidence Recorded This Session

- 2026-05-07 BTFP/Process correction: direct route check returned 200 for `/`, `/event-balloons`, `/portfolio`, `/balloon-twisting-and-face-painting`, `/contact`, `/shop`, and `/faq`; `/process` returned 404.
- 2026-05-11 Event Balloons hub removal supersedes the old `/event-balloons` 200 route receipt: `/event-balloons` and `/event_balloons` now return 404 with no redirect, and there are no live app-source links, route rules, canonical mappings, sitemap entries, footer links, search quick links, hero CTAs, or portfolio buttons pointing to the removed hub.
- 2026-05-07 compact hero follow-up: `python scripts/verify/nav_ia.py` passed; `python scripts/verify/smoke_shop.py` passed; `npm run test:portfolio-reel` passed 4/4; `npm run test:checkout-experience` passed 2/2; `npm run test:interactive-layout` passed 88/88; `npm run test:layout-fit` passed 247/247.
- 2026-05-07 BTFP/Process correction: manual Playwright audit saved screenshots to `output/playwright/nav-btfp-restored-20260507/`, checked desktop/mobile BTFP nav links, 32 BTFP page images, 19 chrome/footer internal links, and no Process anchors in inspected chrome or BTFP page.
- Route sweep returned 200 for `/`, `/event-balloons`, `/portfolio`, `/contact`, `/shop`, `/faq`, `/balloon-twisting-and-face-painting`, `/privacy`, `/terms-of-service`, `/refund-policy`, `/accessibility`, `/cart`, `/checkout`, `/payment-success`, `/thank-you`, `/shop-items/arches`, and `/shop-items/garlands/baby-shower-garland`.
- `python scripts/verify/nav_ia.py` passed after the authority-first nav update.
- `npm run test:layout-fit` initially passed 80/80 after the header/product/page containment repair; this is superseded by the 260/260 responsive follow-up below.
- `python scripts/verify/contact_service_logic.py --base-url http://localhost:8081` passed.
- `python scripts/verify/contact_prefill.py --base-url http://localhost:8081` passed.
- `python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --shape-only --skip-newsletter` passed.
- `python scripts/verify/cart_checkout_contract.py` passed.
- `python scripts/verify/smoke_shop.py` passed after updating the verifier to the restored mega-menu contract.
- `npm run test:layout-fit` initially passed 80/80 after adding `/checkout` and `/thank-you`; this is superseded by the 260/260 responsive follow-up below.
- Responsive follow-up originally expanded the passive layout gate to 260/260 and added `npm run test:interactive-layout` at 39/39. After the 2026-05-07 Process removal, homepage/nav proof checks, and compact hero contract, the current website gate is `layout-fit` 247/247 and `interactive-layout` 88/88. Future menu/content work should use the responsive-container workstream and `npm run test:website-verify`, not the old 80-check gate.
- `python scripts/verify/smoke_shop.py` now verifies fixed-price product pages do not invent product-level quote gates, and still checks retail variant add-to-cart pages.
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

### 2026-05-21 - Codex ready-to-order category menu
Lane: Ready-to-Order dropdown category source and customer-facing submenu copy.
Files: `navbar_context.py`, `navbar.html`, `lt-mega-menu.css`, `lt-megamenu.js`, `hooks.py`, `nav_ia.py`, `smoke_shop.py`, and related docs/verifiers as needed after source tracing.
Intent: Replace product-heavy Ready-to-Order submenu behavior with category-level customer-facing navigation from the real ERPNext/Frappe category source, with no ERPNext/internal wording in the dropdown.
Conflicts: Stay out of unrelated public chrome, BTFP service lane, event audience menu, checkout/payment flow, and catalog import/reclassification unless source tracing proves a direct dependency.
Verification: Branch-level checks passed from `C:\Users\baenb\agent-worktrees\builtbycameron-lt\codex-20260521-rom`: `python -m py_compile apps\locally_twisted\locally_twisted\navbar_context.py scripts\verify\nav_ia.py scripts\verify\smoke_shop.py scripts\verify\ecommerce_pause_contract.py`; `node --check apps\locally_twisted\locally_twisted\public\js\lt-megamenu.js`; `node --check scripts\verify\search_contract.spec.js`; `python scripts\verify\nav_ia.py`. Codex repointed the local Docker stack with a temporary compose override so `http://localhost:8081/` mounts this worktree, then `python scripts/dev/clear_website_cache.py` and `python scripts/verify/smoke_shop.py` passed. Direct homepage HTML probe confirmed category links are present, product links are absent, and ERPNext/Website Item/backend-approved wording is absent.
Status: Accepted locally by GL on `http://localhost:8081/`; not staging/live-release-ready.

### 2026-05-11 - Codex current session event hub and review proof cleanup
Lane: Removed `/event-balloons` hub route, homepage review platform strip, and
route/documentation parity.
Files: `home.*`, deleted `event_balloons.*`, `portfolio.html`, navbar/footer
partials, `hooks.py`, `seo.py`, route/verifier files, and related launch docs.
Intent: Delete the unapproved `/event-balloons` page and every public
discovery path to it with no redirect; keep the four event audience pages
live; show GigSalad, Google, and Facebook review proof as unboxed logos with no
counts and no visible `reviews` label.
Conflicts: The shared worktree also contains unrelated ecommerce/header/catalog
edits. Do not broad-stage this file set without reviewing scope.
Verification: Direct no-redirect HTTP checks returned 404 for
`/event-balloons` and `/event_balloons`; sitemap search was clean;
`python scripts/verify/nav_ia.py` passed; focused SEO sitemap/removed-route
contract passed; focused search/event-mega Playwright checks passed; focused
home/portfolio/event-audience layout-fit passed.
Status: Complete.

### 2026-05-10 - Codex current session top-banner short-notice update
Lane: Desktop top utility banner and BTFP route crawl placement.
Files: `navbar.html`, `lt-mega-menu.css`, `balloon_twisting_and_face_painting.*`, `lt-page-containment.css`, `nav_ia.py`, `smoke_shop.py`, `contact_prefill.py`, `interactive_layout.spec.js`, `layout_helpers.js`, and this coordination note.
Intent: Add the short-notice 24-hour message to the top menu banner in the old proof slot while keeping `Free Event Quote` and the account link, remove the old prepared-design proof copy/truck icon, remove the static BTFP phone/email short-notice band, move the BTFP event crawl into that former slot, expand the crawl event list, and guard that the crawl does not pause.
Conflicts: This supersedes stale wording that treated `Free Event Quote` as a primary nav or mobile drawer item; it is now top-banner-only while `Contact Us` remains the primary conversion CTA. The short-notice message must not be inserted inside the utility-link list.
Verification: `python scripts/dev/clear_website_cache.py --restart` passed; `python scripts/verify/nav_ia.py` passed; `python scripts/verify/contact_prefill.py --base-url http://localhost:8081` passed; focused `npx playwright test scripts/verify/interactive_layout.spec.js --grep "twisting and face painting" --reporter=line --workers=1` passed 9/9; focused BTFP `npm run test:layout-fit` passed 13/13; focused BTFP `npm run test:container-contract` passed 3/3; `python scripts/verify/smoke_shop.py` passed; full `npm run test:public-verify` passed 12/12 website launch steps. Follow-up correction after GL clarified the old proof slot: `python scripts/dev/clear_website_cache.py --restart`, `python scripts/verify/nav_ia.py`, and `python scripts/verify/smoke_shop.py` passed; direct Playwright metrics showed `proofCount: 0`, `topAlertCount: 0`, `deliveryIconCount: 0`, and `oldCopyPresent: false`. 2026-05-11 correction after GL caught the brass/yellow regression: `python scripts/verify/nav_ia.py`, `npx.cmd playwright test scripts/verify/interactive_layout.spec.js --grep "header breakpoint contract" --reporter=line`, `python scripts/verify/smoke_shop.py`, and live browser probes passed with desktop/mobile short-notice strips at `rgb(14, 34, 64)` and warm-white text.
Launch-gate follow-up: the stale homepage Custom Event Decor hide-switch was removed, focused `container_contract.spec.js` passed 75/75, and full `python scripts\verify\website_launch_verify.py` passed all 12 website steps with open ecommerce testing enabled.
Status: Complete.

### 2026-05-10 - Codex current session banner CTA/accessibility closeout
Lane: Top banner ownership, quote-label dedupe, hover/focus contrast, and mobile safe-area guard.
Files: `navbar.html`, `lt-mega-menu.css`, `nav_ia.py`, `public-header-banner-contract-2026-05-10.md`, and capability failure cards.
Intent: Keep `Free Event Quote` top-banner-only, keep `Contact Us` as the menu/drawer CTA, block `Ready-to-Order`, `Cart`, and `Recent Work` from the top banner, and guard the navy banner interaction/mobile padding contract after the gold/brass regression was identified as wrong.
Conflicts: SEO/GEO/AEO work must not mutate header/footer/menu/search quick links unless the task explicitly names those surfaces and approval evidence.
Verification: Superseded by the 2026-05-11 navy correction. `python scripts/verify/nav_ia.py`, focused header breakpoint Playwright, `python scripts/verify/smoke_shop.py`, and live browser probes now guard desktop/mobile navy strips.
Status: Complete.

### 2026-05-10 - Codex current session nav CTA copy adjustment
Lane: Public header/menu CTA label alignment.
Files: `navbar.html`, `nav_ia.py`, `workstreams/menu-content-coordination.md`.
Intent: Change the visible menu CTA from `Free Event Quote` to `Contact Us`, change the adjacent/above `Twisting & Face Painting` menu entry to `Free Event Quote`, and keep both conversion labels pointed at `/contact`.
Conflicts: Small copy/link update only; do not reopen broader mega-menu architecture, footer IA, or service-page content.
Verification: Red check failed before the patch for all four expected labels. After the patch, `python -m py_compile scripts/verify/nav_ia.py` passed, `python scripts/verify/nav_ia.py` passed, `python scripts/dev/clear_website_cache.py` passed, live `http://localhost:8081/` HTML contained desktop/mobile `Free Event Quote` and `Contact Us` links to `/contact`, and focused `npx.cmd playwright test scripts/verify/interactive_layout.spec.js --reporter=line --grep "header breakpoint|header search overlay|desktop mega panels|mobile and tablet drawer" --workers=1` passed 26/26.
Status: Complete.

### 2026-05-10 - OpenClaw/Moji canonical service lane restoration
Lane: Public nav canonical service guardrail after GL caught BTFP removal.
Files: `navbar.html`, `nav_ia.py`, `locally-twisted-decisions.md`, `workstreams/nav-service-removal-guard.md`, `workstreams/nav-service-removal-approvals.md`, FAQ/nav docs.
Intent: Restore `Twisting & Face Painting` to desktop nav, mobile drawer, and search quick links; keep `Free Event Quote` and `Contact Us` as `/contact` conversion labels; make service-lane removal fail loudly without an explicit approval marker.
Conflicts: This supersedes the earlier same-day note that treated BTFP as non-primary header wording. A quote-label request is not removal approval.
Verification: `python scripts/verify/nav_ia.py` passed; live `http://localhost:8081/` rendered checks found one desktop and one mobile `Twisting & Face Painting` link to `/balloon-twisting-and-face-painting`; focused Playwright header/drawer/menu checks passed.
Status: Complete.

### 2026-05-08 - Codex current session mobile search relocation
Lane: Mobile public chrome, drawer search, and nav verifier parity.
Files: `navbar.html`, `lt-mega-menu.css`, `lt-megamenu.js`, `www/search.*`, `nav_ia.py`, `smoke_shop.py`, `interactive_layout.spec.js`, and this coordination note.
Intent: Remove search from the cramped mobile header action row, keep logo/cart/menu clear at 320px, place search at the bottom of the drawer, keep `/search` retired as a no-cache 404, and guard the exact regression.
Conflicts: Worktree contains unrelated event-menu, product-page, and catalog changes; do not broad-stage this file set without reviewing scope.
Verification: `python scripts/verify/nav_ia.py` passed; targeted interactive Playwright mobile/header/search/drawer checks passed 5/5 within the focused 8-test run; focused mobile drawer smoke helper passed.
Status: Complete. Source feature handoff is `workstreams/mobile-nav-review-compactness.md`.

### 2026-05-08 - Codex current session event-menu specialization
Lane: Event Balloons mega-menu IA, event-type landing pages, and header proof-row readability.
Files: `navbar.html`, `navbar_context.py`, `lt-mega-menu.css`, `hooks.py`, `www/event_type_pages.py`, `www/*event-type*`, `layout_helpers.js`, `interactive_layout.spec.js`, `nav_ia.py`, `smoke_shop.py`, and this coordination note.
Intent: Move Portfolio after Ready-to-Order and before FAQ, give each Event Balloons dropdown item its own route/page, rename Corporate Entrances to Corporate Events, connect page proof to the approved homepage client crawl, and make the blue top proof banner readable.
Conflicts: Staying out of catalog recovery, product visual-first styling, and unrelated homepage proof-crawl mechanics already dirty in the worktree.
Verification: `python -m py_compile` for touched Python files passed; `node --check` for touched verifier JS passed; route sweep returned 200 for `/`, `/civic-community`, `/corporate-events`, `/schools-campuses`, and `/private-celebrations`; `python scripts/dev/clear_website_cache.py --restart` passed; `python scripts/verify/nav_ia.py` passed; focused interactive Playwright event-menu/compact-hero checks passed 23/23; `npm run test:container-contract -- --workers=1` passed 69/69; `npm run test:layout-fit -- --workers=4` passed 299/299. Browser metric pass showed the top proof strip at 17.16:1 contrast, 15px/900 text, 49px height, nav order `Event Balloons`, `Twisting & Face Painting`, `Ready-to-Order`, `Portfolio`, `FAQ`, and four event cards linking only to the specialized routes. `python scripts/verify/smoke_shop.py` verified this menu/event/search/drawer slice but still exits 1 on unrelated product-detail contracts: variant checkbox markup, desktop product image size, and boxed option background.
Status: Complete for menu/event specialization; product-detail smoke failures remain out of scope.

### 2026-05-08 - Codex current session homepage featured-work width repair
Lane: Homepage installed-work proof band below reviews.
Files: `home.html`, `home.py`, `hooks.py`, `lt-page-containment.css`, `interactive_layout.spec.js`, `homepage-launch-proof-contract.md`, `landing-page-repair.md`, `website-launch.md`, `locally-twisted-queue.md`, `locally-twisted-decisions.md`, `lessons-learned.md`, `workstreams/menu-content-coordination.md`.
Intent: Rename `Recent Celebrations` to a custom-art installation frame and widen the three featured photos so they read as a full desktop proof band instead of isolated cards.
Conflicts: Staying out of catalog recovery, product visual-first work, and the existing homepage review/client crawl mechanics.
Verification: `python -m py_compile apps\locally_twisted\locally_twisted\www\home.py`, `node --check scripts\verify\interactive_layout.spec.js`, and `git diff --check` passed. `python scripts/dev/clear_website_cache.py --restart` passed. Live Playwright measurements on `/` showed `One of a Kind Designs`, `lt-page-containment.css?v=20260508-featured-2`, zero document overflow, and featured card/image widths of 426/424px at 1366, 504/502px at 1600, and 553/551px at 1920; mobile stayed single-column at 375 and 320. Focused homepage interactive checks passed 8/8, homepage layout-fit passed 13/13, homepage crawl plus compact-hero checks passed 19/19, container contract passed 57/57, and axe passed 38 route/viewport results with 0 violations. Screenshots saved under `output/playwright/home-featured-work-20260508/`.
Status: Complete.

### 2026-05-08 - Codex current session header-to-hero gap repair
Lane: Public shell spacing between restored mega-menu chrome and first hero/content band.
Files: `lt-theme.css`, `home.py`, `hooks.py`, `interactive_layout.spec.js`, `workstreams/menu-content-coordination.md`.
Intent: Remove the default Frappe/Bootstrap `main.container.my-4` top gap that appears above non-home heroes and guard it across the compact hero route set.
Conflicts: Staying out of catalog recovery and product visual-first files currently dirty in the worktree. This keeps the existing premium mega-menu architecture.
Verification: `python -m py_compile apps\locally_twisted\locally_twisted\www\home.py` passed; `node --check scripts\verify\interactive_layout.spec.js` passed; `python scripts/dev/clear_website_cache.py --restart` passed. Live Playwright measurement across `/`, `/event-balloons`, `/portfolio`, `/balloon-twisting-and-face-painting`, `/contact`, `/shop`, `/shop-items/arches`, `/faq`, `/privacy`, `/cart`, and `/checkout` showed `gapHeaderToMain=0`, `gapHeaderToHero=0`, and `mainMarginTop=0px` using `lt-theme.css?v=20260508-shell-gap-2`. `npx playwright test scripts/verify/interactive_layout.spec.js --reporter=line --grep "compact hero height contract" --workers=1` passed 14/14. `npm run test:container-contract` passed 57/57. Targeted `layout_fit.spec.js` for affected public routes passed 104/104; full `npm run test:layout-fit` was attempted but hit the shell timeout before completion, so it is not counted as passing.
Status: Complete.

### 2026-05-06 - Codex current session review marquee repair
Lane: Homepage reviews visual behavior.
Files: `www/home.py`, `interactive_layout.spec.js`, `workstreams/menu-content-coordination.md`, `CODING-HANDOFF.md`.
Intent: Respond to GL's direction that homepage reviews should crawl slowly left-to-right, not stack. Keep the existing duplicate-track marquee structure and accessibility pause/reduced-motion behavior, but remove the mobile stacked fallback and reverse the normal animation direction.
Conflicts: Staying out of checkout/commerce/design-studio dirty files. This does not reopen nav/chrome structure.
Verification: `python -m py_compile apps\locally_twisted\locally_twisted\www\home.py` passed; `node --check scripts\verify\interactive_layout.spec.js` passed; after `python scripts/dev/clear_website_cache.py --restart`, live Playwright check showed `lt-reviews-scroll` at `540s`, `topDelta=0`, and transform moving right on 375px and 1366px. `npx playwright test scripts/verify/interactive_layout.spec.js --reporter=line` passed 42/42. `npm run test:layout-fit` passed 260/260.
Status: Superseded on 2026-05-07. Current homepage proof crawls move left-to-right, the trusted-business crawl is speed-synced to the review cards, and reduced-motion keeps both proof crawls slow, moving, horizontal, and scrollbar-free.

### 2026-05-06 - Codex current session header color repair
Lane: Nav/chrome visual repair.
Files: `lt-mega-menu.css`, `hooks.py`, `interactive_layout.spec.js`, `workstreams/menu-content-coordination.md`, `CODING-HANDOFF.md`.
Intent: Respond to GL's live observation that the header reads black and does not fit the style guide. Keep the deliberate premium mega-menu contract, but move the chrome to a Civic/Slate/Berry treatment with a slim deep-navy proof row, warm-white main nav, berry CTA, brass rules, and warm-white mobile header.
Conflicts: Staying inside the existing mega-menu decision. Not editing checkout/commerce or design-studio files already dirty in the worktree.
Verification: Served page after `python scripts/dev/clear_website_cache.py --restart` loaded `lt-mega-menu.css?v=20260506-mega-5`; desktop/mobile computed `.lt-mega-header` as `rgb(250, 247, 242)` and desktop `.lt-mega-header__top` as `rgb(14, 34, 64)`. `node --check scripts/verify/interactive_layout.spec.js` passed; `python scripts/verify/nav_ia.py` passed; `npm run test:public-verify` passed with nav IA, layout-fit 260/260, interactive-layout 40/40, checkout-experience 1/1, and shop smoke.
Status: Complete.

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
Files: `layout_helpers.js`, `layout_fit.spec.js`, `interactive_layout.spec.js`, `smoke_shop.py`, `package.json`, `_resources/STYLE-GUIDE.md`, `capabilities/recipes/responsive-container-audit.md`, and docs.
Intent: Make breakpoint-edge and stateful container fit a standing gate for menu/content/product/page work.
Conflicts: Does not reopen the restored mega-menu decision. The product smoke update follows the current commerce rule: custom installs quote, retail variants cart.
Verification: `npm run test:layout-fit` passed 260/260; `npm run test:interactive-layout` passed 39/39; `npm run test:checkout-experience` passed 1/1; `python scripts/verify/smoke_shop.py` passed; `npm run test:public-verify` passed with quieter Playwright output.
Status: Complete. Use `npm run test:public-verify` for broad public-site closeout.
