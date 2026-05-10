# Website Launch Workstream

Last updated: 2026-05-10 by Codex after ecommerce business-block clearance, public ecommerce pause restoration, and header conversion-label closeout.

Scope correction 2026-05-10 (GL authoritative): V1 launch is no-purchase public
site scope. Ready-to-Order, shop, product, cart, and checkout surfaces are
publicly paused for launch while product-card/product-page/checkout bugs are
worked out internally. Any checkout/cart/payment notes below are historical
context unless GL explicitly reopens purchase scope.

## Outcome

Launch the Locally Twisted website as a polished business card and inquiry path:
customers can understand the offer, review proof, and submit inquiries without
broken routes, inaccessible layouts, stale docs, missing policy basics, or a
shop/checkout surface pretending to be stable.

This is the launch coordination lane. It does not replace `locally-twisted-queue.md`, `workstreams/shop.md`, or `workstreams/erpnext-backend-simplification.md`; it sequences the launch-critical parts of those lanes.

Launch scope contract: `workstreams/launch-v1-success-contract.md`. Use that
file to keep V1 focused on the public website, customer trust, inquiry
readiness, and measurable quality gates while preserving, but not prematurely
building, the 10-year saleability infrastructure vision.

## Current Stage

Active launch lane. Baseline pass started 2026-05-02.

Known collision: another agent is auditing the form. Do not make contact/form schema changes unless that audit is handed off or explicitly merged into this lane.

2026-05-10 public ecommerce pause closeout: Ready-to-Order was removed from
desktop/mobile public chrome, cart buttons were removed from public header
chrome, header search now submits to `/contact`, and footer/homepage/customer
copy now routes customers toward `/contact` or `/portfolio` instead of the
shop. Guest traffic to `/shop`, `/shop-items`, `/shop-by-category`,
`/all-products`, `/cart`, and `/checkout` redirects to
`/ready-to-order-paused` with a branded customer-facing message and quote CTA.
Logged-in operators can still open direct ecommerce URLs for repair work.
Verification passed: `python scripts/verify/ecommerce_pause_contract.py`,
`python scripts/verify/nav_ia.py`, `npm run test:search-contract`,
`npm run test:container-contract`, `npm run test:interactive-layout`, and full
`npm run test:public-verify`. The launch verifier now allows one Playwright
retry for transient browser-close/502 flakes while repeatable route/layout
failures still fail the gate.

2026-05-10 header conversion-label closeout: the public header/menu now shows
`Twisting & Face Painting`, `Free Event Quote`, and `Contact Us`.
`Twisting & Face Painting` points to `/balloon-twisting-and-face-painting`;
the two conversion labels point to `/contact`. Ready-to-Order source chrome is
config-gated and hidden while public ecommerce is paused. Coordination:
`workstreams/menu-content-coordination.md`; verifier: `scripts/verify/nav_ia.py`.

2026-05-10 ecommerce business-block closeout: GL cleared the remaining source
add-on, live-snapshot price, and source media/gallery approval blockers for
commerce-lane testing. With ecommerce temporarily open,
`python scripts/verify/product_page_architecture_readiness.py` passed with
`technical_architecture_ok: True`, `import_reopen_ok: True`, 14 pass rows, 0
blocked rows, and 1 finance deferral. The site was then restored to
`lt_ecommerce_paused=1`, cache was cleared, and
`python scripts/verify/ecommerce_pause_contract.py` passed. This does not
change V1 launch scope: public ecommerce stays paused unless GL explicitly
reopens purchase scope.

2026-05-10 SEO/GEO/AEO closeout: `npm run test:seo-contract` now guards
canonical aliases, sitemap canonical routes plus paused ecommerce URLs,
business/service JSON-LD without unverified ratings/hours, current FAQ visible
questions matched to FAQPage JSON-LD, and BTFP content-image alt text. Source
handoff: `workstreams/seo-geo-aeo-contract.md`; capability:
`.codex/capabilities/recipes/lt-seo-geo-aeo-contract.md`.

2026-05-08 accessibility closeout: the saved local axe scan findings were fixed across `/event-balloons`, `/portfolio`, `/shop`, product detail/category pages, and `/checkout`. `npm run test:a11y` now regenerates desktop/mobile axe reports for the 19 public launch routes and fails on any violation. `npm run test:a11y-manual` adds a manual-style keyboard/focus/zoom-pressure probe for public routes and caught the homepage review crawl plus portfolio hidden-photo tab-order failures. Durable rules: Frappe already provides the page-level main landmark, route templates must not add nested page-level `<main>` landmarks inside `page_content`, and moving proof surfaces must not leave hidden/offscreen items in the tab order.

2026-05-08 launch verifier and public microinteraction closeout: `npm run test:website-verify` now runs `scripts/verify/website_launch_verify.py`, serializing Playwright workers by default so the local ERPNext/Frappe stack is not overloaded by broad launch gates. `npm run test:public-verify` aliases to the same website gate, and `npm run test:launch-verify` adds accessibility plus contact smoke on top. Public microinteractions now have a focused feature handoff at `workstreams/public-site-microinteractions.md` and capability contract at `.codex/capabilities/recipes/public-site-microinteraction-contract.md`. The balloon cursor was retired at GL's request; product cards on `/shop` and category pages remain clickable from non-interactive areas, and the transient demo file `assets/balloon cursor/Red Balloon Cursor.html` remains deleted.

2026-05-08 mobile public chrome/review compactness closeout: mobile search now
lives at the bottom of the drawer instead of in `.lt-mega-header__mobile-actions`,
which keeps the mobile header to logo plus menu at 320px while public ecommerce
is paused. Search opens the overlay and now submits to `/contact`; `/search` is
a no-cache 404 fallback, not a public nav destination. The homepage Google
review proof band now has a
mobile component sizing contract. Feature handoff:
`workstreams/mobile-nav-review-compactness.md`.

2026-05-08 public security review: active P0 lane is
`workstreams/public-site-security-hardening.md` with capability contract
`.codex/capabilities/recipes/frappe-public-storefront-security.md`. First safe
fixes are in place for `/shop?q=` XSS, product-gallery image rendering, and new
private inquiry uploads. Follow-up closeout moved checkout Lead conversion to
the paid-order cascade and gated `/event-playground` behind login plus
Administrator/System Manager access. GL clarified current data/files are fake,
so the order-summary and existing fake public-file findings are hardening and
cleanup items rather than immediate launch blockers for the current fake-data
state. Credential rotation/doc cleanup remains GL-owned before broader
sharing/cutover.

Live menu/content coordination now lives in `workstreams/menu-content-coordination.md`. Agents touching menu, header, footer, public page content, or nav/content verifiers must update that file before editing so overlapping sessions do not overwrite each other.

2026-05-06 status reset after Event Playground handoff:

- Event Playground / PlayCanvas is no longer part of the immediate website launch path; OpenClaw is taking over that project. Keep `/event-playground` out of public launch decisions unless GL explicitly brings it back.
- Use `workstreams/website-launch.md` as the ASAP website launch lane.
- Website-specific launch gates verified on 2026-05-06: route sweep for `/`, `/contact`, policy pages, `/portfolio`, `/shop`, `/cart`, and `/checkout` returned 200; `/book` returned a 301 to `/contact?intent=quick`; `test:nav-ia` passed; `test:layout-fit` passed 260/260 after a portfolio mobile title fit patch; `test:interactive-layout` passed 42/42; `test:checkout-experience` passed 2/2; `test:shop-smoke` passed; contact prefill, service logic, and smoke form checks passed. Focused portfolio verification after the exact handoff retranslation passed `npm run test:portfolio-reel` 4/4, `npm run test:layout-fit -- --grep portfolio` 13/13, and `npm run test:interactive-layout -- --grep portfolio` 3/3.
- Payment posture: `payment_launch_readiness.py --mode local` passes in Stripe test mode. `--mode live` fails as expected because live Stripe keys, explicit live site config, payment method configuration, operator email config, and production host name are not in place.
- `npm run test:website-verify` is the website-only closeout gate through `scripts/verify/website_launch_verify.py`. `npm run test:public-verify` aliases to the same website-only gate, and `npm run test:launch-verify` adds accessibility plus contact smoke. Event Playground remains separately available through `npm run test:event-playground` for the OpenClaw lane.
- Do not assume the worktree is clean; check `git status -sb` before editing. Current LT work follows the main-only rule; do not use old feature-branch closeout notes as active git guidance. The active portfolio reference source is `research/a unique portfolio page for a high end corporate balloon events_/design_handoff_locally_twisted_portfolio/`; raw portfolio reference folders, if present, are critique input only. Do not treat raw reference folders as production source or launch evidence.
- `scripts/verify/smoke_forms.py` now verifies localhost `/contact` submissions through the local Docker/Frappe bench container and cleans up the generated smoke Lead plus linked LT cascade Task. Latest run on 2026-05-06 created marker `SMOKE-TEST-1778073366`, verified it, and reported cleanup OK.
- `scripts/verify/category_media_candidates.py` now generates a no-mutation approval packet for the 11 empty customer-facing category images. Latest run on 2026-05-06 wrote ignored local reports to `output/category-media-candidates.json` and `output/category-media-candidates.md`; the quick picks are ready for Jeff/GL approval before any live assignment.
- `scripts/setup/sync_category_media.py` now handles the post-approval path: write a selection template, dry-run Frappe Item Group image updates, and apply only rows marked `approved: true`. Safety proof on 2026-05-06: dry-run found 11 would-update rows; `--apply` with the unapproved template returned `not_approved: 11` and made 0 updates; live DB recheck still showed all 11 images as `null`.
- Paperwork/backend automation focus started 2026-05-06. Coordination lanes: `workstreams/paperwork-backend-automation.md` and `workstreams/business-automation-index.md`. Local/test paperwork spine is verified, Sales Invoice output now has a branded code-owned print format and letterhead, and the answer-first standard outbound document source lives at `apps/locally_twisted/locally_twisted/outbound_documents/`. `business_automation_index.py` now indexes the cascading intake/CRM/checkout/payment/paperwork/finance surfaces and the daily Frappe scheduler runs that checkup. The default invoice is restrained for accounting; larger corporate proof/patriotic growth positioning belongs in proposals, portfolio, and client pages. Live Stripe, bank account, suppliers/vendors, payroll/HRMS, reminder approval, and manual stage-to-finance thresholds remain incomplete.
- Landing page repair pass completed 2026-05-07 for the ASAP website lane; featured-work width/copy and mobile review compactness updated 2026-05-08; homepage hero changed on 2026-05-10 to GL's seasonal/audience carousel. Feature handoffs: `workstreams/landing-page-repair.md`, `workstreams/homepage-seasonal-hero-carousel-2026-05-10.md`; mobile compactness handoff: `workstreams/mobile-nav-review-compactness.md`; capability contract: `.codex/capabilities/recipes/homepage-launch-proof-contract.md`. Review cards and trusted-business names crawl full-stage left-to-right at matched visible speed: reviews keep the canonical `540s` loop, and trusted-business names use a measured proportional duration. Reduced-motion mode keeps these proof crawls slow, moving, horizontal, and scrollbar-free; the old static/scrollbar fallback is superseded. The hero now has one visible page-level H1 on the first graduation slide, followed by H2 audience slides for Civic & community, Corporate events, Schools & campuses, and Private celebrations; Google reviews sit immediately after the hero and stay compact on mobile; the homepage trust/authority bar is removed for now while the approved icon assets remain available; the cookie notice is inline after reviews; `One of a Kind Designs` follows reviews as the wide custom-install proof band; closing CTA copy is corporate/school/civic/community-first. The 2026-05-10 seasonal-carousel correction passed focused homepage/BTFP/white-label Playwright coverage plus the white-label surface verifier. Earlier compact hero/layout/container/a11y receipts remain relevant but the old static generated-hero expectation is obsolete for `/`.
- Same-day crawl mechanics follow-up now uses GL's corrected left-to-right direction. Verification proved both proof crawls move left-to-right, hide overflow, keep matched visible speed, and continue moving in reduced-motion mode. Full `npm run test:website-verify` passed after the direction correction.
- Compact hero contract completed 2026-05-07 after GL made same-height, low-padding heroes non-negotiable from agency level down; generated lifestyle hero overlay/crop follow-through completed 2026-05-10. Capability contract: `.codex/capabilities/recipes/compact-hero-contract.md`. `_resources/STYLE-GUIDE.md` v4.6 now keeps the 220px mobile, 250px tablet, and 280px desktop standard hero heights with padding/title caps, plus breakpoint-specific generated WebP lifestyle crops under the black landing-page readability overlay. The implemented route set is `/`, `/event-balloons`, event audience pages, `/portfolio`, `/balloon-twisting-and-face-painting`, `/contact`, `/shop`, and `/shop-items/<group>`. Focused verification passed `npx.cmd playwright test scripts/verify/interactive_layout.spec.js --grep "compact hero height contract" --reporter=line --workers=1` 66/66 after the generated crop/overlay guard enforced generated lifestyle filenames.
- Executable public container contract completed 2026-05-07 after GL flagged repeated unmanageable container drift. Capability contract: `.codex/capabilities/recipes/frappe-public-container-contract.md`. Every visible direct `.page_content` child on the 19 launch public routes is now declared in `CONTAINER_CONTRACT_ROUTES` with an explicit mode, and `npm run test:container-contract` is part of `npm run test:website-verify` / `npm run test:public-verify`. The first matrix exposed real drift in homepage twisting spotlight containment, portfolio footer markup, contact/location raw Bootstrap containers, document narrow-width selector specificity, BTFP route surfaces, and BTFP event-crawl data; those were repaired, the standalone gate passed 57/57, and the full website gate passed after the contract was added.
- Nav/BTFP correction completed 2026-05-07. Handoff: `workstreams/nav-btfp-process-correction.md`. It restored `/balloon-twisting-and-face-painting` as a 200 service route and removed the unapproved `/process` route. The current 2026-05-10 ecommerce-pause/conversion-label header now uses `Event Balloons`, `Free Event Quote`, `Portfolio`, `FAQ`, and `Contact Us`, with both conversion labels pointing to `/contact`.
- BTFP form/calculator follow-up completed 2026-05-08. Feature handoff: `workstreams/btfp-service-page.md`; capability contract: `.codex/capabilities/recipes/btfp-live-service-page-contract.md`. The support banner and event crawl are now brand-blue, the old red divider is removed, the page includes a customer-facing artist-time calculator using the published $130 first hour / $115 additional hour / $50 deposit per artist math, and the shared public inquiry partial now declares `data-form-contract="inquiry-v1"`. Calculator follow-up on 2026-05-08 changed the calculator to one row per artist so mixed twisting/painting services can use different hours and extra artists can be added without flattening the math. The durable form visual contract is in `_resources/STYLE-GUIDE.md` and `locally-twisted-decisions.md`. `contact_prefill.py` now guards the BTFP support banner, event crawl, calculator, per-artist mixed-duration math, add-artist math, minimum one-hour rule, no public deposit checkout CTA, BTFP-only service choices, and the shared form contract.

Latest verified controller baseline:

- Docker stack is running at `http://localhost:8081`.
- Route sweep returned 200 for `/`, `/contact`, `/privacy`, `/terms-of-service`, `/refund-policy`, `/accessibility`, `/shop`, `/shop-by-category` redirected to `/shop`, `/cart`, and `/checkout`.
- `/book` redirects to `/contact?intent=quick`.
- `python scripts/verify/nav_ia.py` passed.
- `npm run test:layout-fit` passed with 299 checks across the current public route list.
- `npm run test:container-contract` passed with 69 route/viewport checks across the launch public routes.
- `npm run test:website-verify` passed through `scripts/verify/website_launch_verify.py` with serialized Playwright workers after the container contract joined the website-only closeout gate.
- Public microinteraction closeout now keeps the balloon cursor retired and verifies whole-card product navigation, `npm run test:shop-smoke`, `npm run test:layout-fit` 299/299, `npm run test:interactive-layout` 154/154, `npm run test:a11y` with 46 route/viewport axe results and 0 violations, and `npm run test:a11y-manual`.
- Current favicon/cursor retirement pass on 2026-05-08 verified the served red dog favicon, absence of cursor assets/DOM, and product-card text click navigation. It also exposed that `python scripts/verify/smoke_shop.py` is not currently green in this shared worktree: it fails on the variant-chip checkbox contract and a homepage nav `Portfolio` assertion. Treat the full shop-smoke status as blocked until the active shop/menu lane repairs it.
- `python scripts/verify/smoke_shop.py` passed after updating stale chrome selectors to the current authority-first header/mobile drawer and retiring the category-card index.
- `nav_ia.py` now verifies the desktop/mobile `Event Balloons`, `Twisting & Face Painting`, `Free Event Quote`, `Portfolio`, `About Us`, `FAQ`, and `Contact Us` launch chrome while ecommerce is paused. `Ready-to-Order` remains source-gated and hidden in rendered public chrome unless the internal shop lane explicitly opens ecommerce.
- `python scripts/verify/cart_checkout_contract.py` passed after the cart/checkout item-code contract fix.
- `python scripts/verify/variant_media_contract.py` passed after the first variant-media reconciliation pass.
- `python scripts/verify/catalog_variant_contract.py` passed: 53 products checked, 10,227 expected active required-choice variants, 10,227 live active variants, 4 single-SKU products.
- Current commerce rules no longer make product group the quote gate. Fixed-price products stay cartable; out-of-area delivery ZIPs redirect to a prefilled `/contact` quote path instead of Stripe. Current smoke coverage verifies product pages do not invent product-level quote gates and retail `unicorn-bouquet` option selection writes a selected variant into `LT_CART`.
- ERPNext now has 1,712 variant `Item.image` mappings from `_resources/odoo-live/images/` where Odoo image labels clearly matched product options; product detail pages swap to selected variant media when present.
- Detailed media review was refreshed on 2026-05-06 with `python scripts/setup/sync_variant_media.py --dry-run --include-details --report output/catalog-media-review.json`; latest report checked 49 products, flagged 45 for review, left 1,712 variant images unchanged, and skipped 6,831 unsafe-to-infer image assignments.
- Category browse imagery is not assigned yet: live DB recheck on 2026-05-06 found all 11 customer-facing child Item Groups under `Shop Items` still have empty image fields. The no-mutation category candidate packet now has first-pass product-source quick picks for all 11 categories, and the post-approval sync helper is dry-run-first.
- Product option UX P0 pass completed 2026-05-02 and was reconciled with quote/retail lane rules on 2026-05-05: no per-attribute Jinja DB lookup, progressive invalid-option disabling is verified on a retail variant, and variant chips are radio/single-select where the product is checkout-enabled.
- Desktop/mobile launch screenshot baseline captured under `output/playwright/launch-baseline-20260502/`.
- Historical browser console baseline after the Webshop generated asset-map correction passed across `/`, `/shop`, `/shop-items/arches`, `/shop-items/arches/classic-arch`, `/cart`, `/checkout?item=6-color-rainbow-arch-20F&qty=1`, `/privacy`, `/refund-policy`, and `/accessibility`: all routes returned 200 with 0 console errors and 0 warnings. Current commerce behavior is governed by the 2026-05-06 delivery-zone decision: fixed-price product groups are not quote gates, and out-of-area delivery redirects to `/contact`. Report: `output/playwright/launch-baseline-20260502/console-report-after-asset-map-fix.json`.
- Webshop asset rebuild note: no Yarn package install was needed. Existing Yarn works when `/home/frappe/.nvm/versions/node/v20.19.2/bin` is added to `PATH`; build from the frontend/nginx container last so shared `assets.json` points to files nginx can actually serve.
- Final layout-fit rerun found and fixed a 320px overflow on `/shop-items/seasonal-specialty`; Webshop's stock `.item-card { min-width: 300px; }` needed the LT grid override `min-width: 0`. `npm run test:layout-fit` now passes 60/60 again.
- First brand-token reset pass completed 2026-05-02: `lt-theme.css` remaps the old pastel-heavy token values toward deep teal, slate, warm white, brass/gold, muted berry, and restrained supporting tints while preserving variable names for compatibility. Cache cleared, `nav_ia.py` passed, `npm run test:layout-fit` passed 60/60, and screenshots for `/`, `/shop`, `/contact`, and `/shop-items/arches/classic-arch` passed under `output/playwright/brand-token-20260502/`.
- Civic Celebration site-wide overhaul completed 2026-05-03. The current V1 visual direction is documented in `_resources/STYLE-GUIDE.md` and `workstreams/civic-sitewide-redesign.md`. The pass covers shared chrome, homepage, contact/book form, BTFP, portfolio, FAQ, policy/accessibility/success pages, shop, category/product pages, cart, and checkout. Screenshots were captured under `output/playwright/civic-overhaul-20260503-verified/`.
- Style-guide consolidation completed 2026-05-05. `_resources/design-guide/` was deleted because it conflicted with the approved Civic Celebration + Slate Blue/Berry + Brand Direction contract and kept reintroducing light-blue/blush styling. Current launch visuals must use `_resources/STYLE-GUIDE.md` only.
- Responsive container integrity gate completed 2026-05-05 and was refreshed after the 2026-05-07 BTFP/Process correction, compact hero repair, executable route-level container contract, 2026-05-08 manual accessibility closeout, and 2026-05-10 generated hero correction. `npm run test:layout-fit` now checks the current public route list across 13 viewport families (299 checks), `npm run test:container-contract` checks route-level container ownership across 69 route/viewport cases, `npm run test:interactive-layout` checks 154 stateful UI cases, `npm run test:a11y-manual` checks public-route keyboard focus/image/zoom-pressure exposure, and `npm run test:public-verify` aliases the full website-only closeout gate.
- Compact generated-photo hero verification is now part of the interactive visual gate. If any launch page adds or changes a hero, update `COMPACT_HERO_ROUTES`, keep hero imagery sourced from the project image-generation API rather than reserved real/proof photos, and keep the focused grep green before broad visual closeout.
- Container ownership verification is now part of the public website gate. If any launch page adds a visible direct `.page_content` child, changes full-bleed/contained structure, or adds a crawl/marquee viewport, update `CONTAINER_CONTRACT_ROUTES` and keep `npm run test:container-contract` green before broad visual closeout.
- `smoke_shop.py` now matches the current commerce split: fixed-price product pages stay checkoutable, and the delivery ZIP/city gate owns the quote fallback. Retail variants still prove inline option selection and cart writes.

## Owner

Unassigned next agent/session.

Work from:

`C:\Users\baenb\projects\Built_by_Cameron\_CLIENTS\locally-twisted`

## User-Facing Impact

Launch succeeds when a real customer can:

- land on the site and understand Locally Twisted quickly
- navigate on desktop and mobile without broken IA
- reach a clear branded pause page instead of unstable shop/product/cart/checkout pages
- submit an inquiry through `/contact`
- use `/book` only as a redirect/quick-intent alias, not a separate form
- view policy/legal pages needed for trust and Stripe readiness
- use portfolio/proof and quote paths while ecommerce remains out of launch scope

## Launch Gates

### Gate 1 - Reality Baseline

Verify before building:

- Current running site is reachable at `http://localhost:8081`.
- Current git status is understood; do not overwrite another agent's changes.
- Queue and workstreams are read.
- Form audit ownership is respected.
- Catalog counts or route states are rechecked before being quoted as current.

### Gate 2 - Inquiry Path

Launch blocker if broken:

- `/contact` loads and submits correctly.
- `/book` redirects to `/contact?intent=quick`.
- Lead records get the intended service/taxonomy values.
- Customer-facing success/error states are loud enough that silent failure is unlikely.

Coordinate with the active form audit before changing this area.

### Gate 3 - Trust And Policy Surface

Launch blocker if missing or obviously stale:

- `/privacy`
- `/terms-of-service`
- `/refund-policy`
- `/accessibility`
- Stripe Dashboard URLs after GL/legal approval.

Policy text must come from approved project resources or GL/legal approval. Do not invent legal terms.

### Gate 4 - Ecommerce Pause

Launch blocker if it leaks unstable purchase surfaces:

- Public chrome must not expose Ready-to-Order, cart, checkout, or product/category links.
- Guest `/shop`, `/shop-items`, `/shop-by-category`, `/all-products`, `/cart`, and `/checkout` traffic must land on `/ready-to-order-paused`.
- The pause page must be branded, clear, mobile-safe, and point customers to `/contact` and `/portfolio`.
- Logged-in operators may keep direct ecommerce URLs available for internal repair.

Primary coordination file: `workstreams/shop.md`.

### Gate 5 - Visual And Accessibility Quality

Launch blocker if customer-facing:

- Desktop and mobile layouts do not overlap, clip text, or show broken spacing.
- Header/footer/navigation are consistent.
- Core pages feel like one brand, not stitched-together ERPNext defaults.
- Important buttons, links, forms, and menus are keyboard and screen-reader reasonable.
- Axe checks pass for the public launch route set at desktop and mobile widths with `npm run test:a11y`.
- Images have usable alt text or are clearly decorative.

### Gate 6 - Backend Readiness For Jeff

Not every backend cleanup must block public launch, but Jeff-facing handoff should not be confusing or unsafe:

- Inquiry records are readable.
- Backend labels avoid ERPNext jargon where possible.
- Demo/sample data is only created after schema cleanup.
- Stale scripts are not rerun blindly.

Primary coordination file: `workstreams/erpnext-backend-simplification.md`.

## Launch Board

| Lane | Status | Current evidence | Blocker / next action |
|---|---|---|---|
| Controller baseline | Passing after current component gates | Route sweep 200s, `/book` redirect verified, `nav_ia.py` passed, `layout-fit` 299/299, `container-contract` 69/69, full `interactive-layout` 154/154, `a11y` 46 route/viewport results with 0 violations, earlier `checkout-experience` 2 passed, earlier `portfolio-reel` 4 passed, and `smoke_shop.py` passed | Keep this file current after every lane return |
| Form audit | Owned by separate agent | Do not edit `/contact` or Lead schema from this lane yet | Wait for form audit handoff before inquiry-path changes |
| Policy/trust | Routes load, content not launch-approved | Policy audit found `/privacy`, `/terms-of-service`, `/refund-policy`, `/accessibility` exist; source trace lives in `workstreams/policy-trust.md` | Get GL/legal decisions on unresolved privacy, cookie, shipping/delivery, and refund terms before Stripe URL wiring |
| Ecommerce/shop | Public ecommerce paused for launch; internal repair lane remains in `workstreams/shop.md` | `ecommerce_pause_contract.py` passed; full `npm run test:public-verify` passed with the pause contract included; guest shop/product/cart/checkout routes redirect to `/ready-to-order-paused`; logged-in operators can still access direct ecommerce URLs | Continue product-card/product-page/checkout repair internally; do not restore public Ready-to-Order/shop chrome until GL reopens ecommerce |
| Visual/accessibility QA | Civic site-wide visual pass implemented and locally verified; `/portfolio` proof-gallery reel added as a route-specific visual slice; homepage launch repair pass landed; compact generated-photo hero contract landed | `output/playwright/launch-baseline-20260502/`, `output/playwright/brand-token-20260502/`, `output/playwright/civic-overhaul-20260503-verified/`, `output/playwright/landing-fixes-20260507/`, `output/playwright/compact-heroes-20260507/`, `output/playwright/home-portfolio-corrections-20260507/`, and `output/playwright/generated-heroes-20260510/` are local screenshot evidence; current component gates pass with `layout-fit` 299/299, `container-contract` 69/69, `interactive-layout` 154/154, and `a11y` 46 route/viewport results with 0 violations after the generated hero correction | Do manual keyboard/focus/alt/zoom checks and rerun screenshots after final media/content changes |
| Backend readiness | Paperwork/backend focus active | `paperwork-backend-automation.md` and `business-automation-index.md` now record the 2026-05-06 baseline: finance inventory, customer documents, payment cascade, CRM stage guardrails, payment config/webhook/local readiness, checkout-to-Lead conversion, Accountant Home parity, read-only paperwork status, synthetic no-live pipeline audit, branded Sales Invoice print output, outbound document registry, automation index, scheduled checkup, and Stripe amount-parity contract passed; live Stripe/site setup is cutover-deferred, not a current fake-data blocker | Build reviewed internal digest/queue surfaces; do not send reminders, use live credentials/customer data, or wire CRM stages to finance until thresholds are explicit |
| Release gate | Not started | No integrated launch report yet | Run final route, form, shop, visual, accessibility, and policy-source gates after implementation lanes land |

## Higher-Quality Launch Additions

These are the best "more professional, more big business" upgrades before launch:

1. Review skipped/unmatched product/category media from `output/catalog-media-review.json` where source photos exist but labels were not safe enough to auto-map.
2. Representative category media for `/shop-items/<group>` pages or a future image-rich mega menu, using `python scripts/verify/category_media_candidates.py` to regenerate the current approval packet without reviving the retired category-card index.
3. Hetzner-faithful refresh of `/refund-policy` and `/accessibility`.
4. Webshop product-detail/layout cleanup after variant/media correctness.
5. Visual QA pass across homepage, portfolio, contact, policy pages, shop, category, product detail, cart, and checkout.
6. Accessibility pass focused on real customer paths, not theoretical coverage.

The broad Civic redesign has landed. Do not start another broad visual direction change before launch unless GL explicitly reverses the Civic decision; spend remaining launch time on proof photos, content accuracy, accessibility, and final verification.

## Coordinated Take-Live Workflow

Use this lane as the launch controller board when multiple agents or sessions are working at once.

### What Supports This

- Machine-wide Guiding Light Codex protocol: communication, attention protection, decision boundary, and verification discipline.
- Project `AGENTS.md`: LT-specific source routing, ERPNext/Frappe rules, and stale-doc warnings.
- Project capability: `.codex/capabilities/recipes/take-live-coordinated-workflows.md`.
- `locally-twisted-queue.md`: active work selection.
- `workstreams/*.md`: feature-lane handoffs by user-facing outcome.
- `workstreams/policy-trust.md`: policy source trace and Stripe/legal readiness lane.
- Superpowers-style parallel pattern: one controller, bounded sidecar agents, explicit ownership, review before integration.
- Existing verification scripts: nav, layout fit, shop smoke, contact/form checks, backend parity, compile checks, and browser screenshots.
- Optional read-only Claude reference library: `C:\Users\baenb\.claude\skills\README.md` and specific Frappe safety skills when they help decide what to verify.

### Controller Role

One agent/session must act as launch controller.

Controller owns:

- keeping this file current
- choosing the next non-colliding lane
- assigning read-only audits or implementation scopes
- preventing two agents from editing the same files or behavior
- integrating returned work in dependency order
- running or coordinating final release verification

The controller should continue doing non-overlapping work while sidecar agents run. Do not hand off the immediate blocking task if the controller cannot move forward without it.

### Parallel Lanes

| Lane | Parallel-safe work | Write scope rule | Launch value |
|---|---|---|---|
| Form audit | Read-only `/contact`, `/book` redirect, Lead/service behavior | No form/schema edits unless handed off by current form auditor | Protects inquiry conversion |
| Policy/trust | `/refund-policy`, `/accessibility`, `/privacy`, `/terms-of-service` review and refresh | Do not invent legal terms; use approved sources | Builds customer and Stripe trust |
| Shop/media | Variant correctness, product/category media inventory, category browse imagery | Coordinate through `workstreams/shop.md`; avoid checkout/form files unless assigned | Raises product confidence |
| Visual/accessibility QA | Screenshots, layout fit, nav, keyboard basics, image/alt checks | Read-only unless assigned a narrow CSS/template fix | Prevents launch embarrassment |
| Backend readiness | Jeff-facing Lead/Contact/order clarity, stale script audit, sample data timing | Coordinate through backend workstream; avoid public form edits unless assigned | Makes handoff usable |
| Paperwork/backend automation | Invoices, payment requests, receipt emails, operator notifications, unpaid/overdue review, synthetic pipeline audit, automation index, scheduled checkups, cutover-deferred live setup | Coordinate through `workstreams/paperwork-backend-automation.md` and `workstreams/business-automation-index.md`; no auto-submit, reminder sending, or live credential/customer-data use in fake-data audits | Turns back-office launch risk into reviewable queues |
| Release gate | Final integrated verification and launch-readiness report | Read-only except docs/checklist updates | Prevents false launch claims |

### Dispatch Rules

- Dispatch read-only auditors freely when their lanes do not depend on each other.
- Dispatch implementation agents only with a disjoint write scope.
- Never dispatch two implementation agents to the same template, CSS file, JS flow, DocType schema, seed script, fixture, checkout path, or form path at the same time.
- Each agent must return: changed files, exact verification run, evidence summary, blockers, and next handoff note.
- The controller reviews every returned result before treating it as launch evidence.

### Review Rules

Implementation lanes need two reviews before integration:

1. Spec review: did the work solve the assigned launch lane and stay in scope?
2. Quality review: is it maintainable, Frappe/ERPNext-native, accessible, and consistent with LT style?

Read-only audit lanes need evidence review:

- exact route or file checked
- exact command or browser path used
- clear pass/fail/blocker result
- no claims beyond what was checked

### Integration Order

Default launch order:

1. Reality baseline and collision check.
2. Inquiry/form audit result.
3. Policy/trust pages and Stripe URL readiness.
4. Shop variant/media correctness.
5. Product/category visual polish.
6. Visual/accessibility QA after visual changes.
7. Backend handoff readiness.
8. Final release gate from the integrated workspace.

Policy/trust and shop/media can run while the form audit continues, as long as they do not touch `/contact`, Lead schema, or reopened purchase-path behavior.

## Touched Areas

Launch-critical surfaces:

- `/`
- `/contact`
- `/book`
- `/privacy`
- `/terms-of-service`
- `/refund-policy`
- `/accessibility`
- `/shop`
- `/shop-by-category` compatibility redirect to `/shop`
- `/shop-items/<group>`
- `/shop-items/<group>/<slug>`
- `/cart` (out of V1 launch scope)
- `/checkout` (out of V1 launch scope)
- `/payment-success` (out of V1 launch scope)
- `/thank-you` (out of V1 launch scope)

Primary references:

- `AGENTS.md`
- `locally-twisted-queue.md`
- `CODING-HANDOFF.md`
- `locally-twisted-decisions.md`
- `workstreams/shop.md`
- `workstreams/erpnext-backend-simplification.md`
- `_resources/STYLE-GUIDE.md`
- `_resources/STYLE-GUIDE.md` version 4.2 or newer. The old `_resources/design-guide/` synthesis was deleted on 2026-05-05 and must not be used.
- `workstreams/responsive-container-integrity.md`
- `_resources/policies/`
- `_resources/odoo-live/`
- `C:\Users\baenb\projects\locally-twisted-odoo\` as the read-only business-detail source of truth for customer-facing business claims, policies, product/service details, voice, and legacy business decisions

## Dependencies And Collision Points

- Form audit owns current `/contact` and Lead-submission review until handed off.
- Shop lane owns catalog correctness, media, product detail, and browse-surface polish for V1.
- Backend simplification owns Jeff-facing Desk and stale Lead/schema cleanup.
- Policy/legal pages require the Odoo business-detail source, approved current project resources that trace back to it, or GL/legal approval.
- Business details from the old Odoo project drive are source-of-truth evidence for business meaning, not app-build instructions. Do not modify `C:\Users\baenb\projects\locally-twisted-odoo\` from this repo.
- Media/render work must stay honest to balloon construction and product reality; do not attach generated concepts to products as factual photos.

## Do Not Do

- Do not call the site launch-ready from docs alone.
- Do not rebuild `/book` as a separate public form.
- Do not change form schema while another agent owns the audit unless coordinated.
- Do not bury launch blockers in `PROJECT-STATUS.md`.
- Do not let beautiful visuals hide broken product options or inquiry submission.
- Do not invent policy/legal language, product capabilities, or business promises.

## Verification

Run the exact checks tied to the changed surface.

Core launch verification:

```powershell
python scripts/verify/nav_ia.py
npm run test:layout-fit
npm run test:interactive-layout
npm run test:portfolio-reel
python scripts/verify/smoke_shop.py
npm run test:website-verify
```

Form path verification, coordinated with the form audit:

```powershell
python scripts/verify/contact_prefill.py --base-url http://localhost:8081
python scripts/verify/contact_service_logic.py --base-url http://localhost:8081
python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --form-path /contact --skip-newsletter
```

Backend/contact parity verification when Lead schema or backend routing changes:

```powershell
python scripts/setup/sync_contact_intake_backend.py
python scripts/verify/lead_backend_intake_parity.py
```

Python syntax check after Python edits:

```powershell
python -m compileall apps\locally_twisted\locally_twisted scripts\verify scripts\setup
```

After Jinja/CSS/Web Page edits:

```powershell
python scripts/dev/clear_website_cache.py
```

Visual verification:

- Browser screenshots at desktop and mobile widths.
- Breakpoint-edge layout checks at 320, 360, 375, 390, 414, 768, 820, 991, 992, 1024, 1199, 1200, and 1366px through the shared layout helper.
- Open-state checks for nav, drawers, modals, filters, forms, product controls, and reduced-motion states where relevant.
- Check homepage, contact, policies, shop, category, product detail, cart, and checkout.
- Confirm no text overlap, clipped buttons, smashed images, placeholder category/detail surfaces where better media exists, or ERPNext-looking default surfaces on launch-critical pages.

## Decisions And References

- Active tasks: `locally-twisted-queue.md`.
- Project rules: `AGENTS.md`.
- Durable reasoning: `locally-twisted-decisions.md`.
- Compact technical startup: `CODING-HANDOFF.md`.
- Shop lane: `workstreams/shop.md`.
- Policy/trust lane: `workstreams/policy-trust.md`.
- Backend lane: `workstreams/erpnext-backend-simplification.md`.
- Take-live coordination recipe: `.codex/capabilities/recipes/take-live-coordinated-workflows.md`.
- Legacy whole-project maps: `HANDOFF.md`, `PROJECT-STATUS.md`.

## Next Handoff Stage

First non-colliding launch slice:

1. Do a read-only launch baseline across route availability, queue/workstreams, and current git state.
2. Confirm form audit ownership and avoid `/contact` edits unless handed off.
3. Work on policy/trust or shop/media quality while the form audit continues. For category media, use the generated `output/category-media-candidates.md` quick picks as the review packet, then `output/category-media-selection.template.json` as the approval file; neither is approval to mutate live Item Group images until rows are explicitly marked approved.
4. Update this file with exact changed surfaces, verification commands, and remaining launch blockers.
