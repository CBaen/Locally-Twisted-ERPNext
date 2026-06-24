# Homepage July Favorites And Pickups Navigation Plan Brief

Date: 2026-06-24
Owner: Codex technical lead
Status: live verified on `https://locallytwisted.com/`

## Route Record

Mode: plan-brief plus plan-deepen with real multi-agent triad review, followed by local source implementation.
Decision needed: none for this release; GL approved moving forward on 2026-06-24.
Scope owner: Locally Twisted public site source and live release lane.
System/project/runtime classification: single project, public site, client production surface.
Initial source-slice allowed actions: homepage/nav source implementation, local Frappe cache clear/restart, local verification, queue/handoff/capability/lesson/decision documentation, commit, and push.
Initial source-slice forbidden actions: ERPNext catalog data mutation, Frappe Cloud deploy, live cache clear, provider changes, payment changes, product visibility changes, and customer communication.
Evidence bar: current repo files, current live public pages, capability recipes, and user-confirmed business direction.
Stop condition: do not perform additional provider, catalog, DNS, Stripe, or payment changes from this release.

## Outcome

Implemented the coordinated local source update:

1. Replace the current weak Fourth of July hero image with realistic balloon decor.
2. Add a professional `Customer Favorites` product row between Reviews and Live Entertainment.
3. Reorder the relevant homepage bands to Reviews, Customer Favorites, Live Entertainment, then One of a Kind Designs.
4. Rename the public shop-category supermenu label from `Balloons-to-Order` to `Pickups & Deliveries`.

This is live on `https://locallytwisted.com/` as of 2026-06-24.

## Live Release Closeout

Live release executed on 2026-06-24 after GL approved moving forward.

- Full source repo: `3b5c64a feat: update homepage favorites and pickup delivery nav`.
- Previous tracked live app mirror: `5d7c952 Fix Stripe promo checkout session params`.
- New tracked live app mirror: `8d8d205 Update homepage favorites and pickup delivery nav press-deploy-bench-40102`.
- Frappe Cloud tracked branch: `live-shop-discovery-20260529`.
- App mirror scope: 13 approved app files from `3498fef..3b5c64a`. A full
  app-root sync dry run showed unrelated seed/image additions and was rejected
  for this scoped release.
- Poll result: public site flipped between `2026-06-24T04:45:22Z` and
  `2026-06-24T04:46:25Z`; final poll had `favorites=yes`, `pickups=yes`,
  `old_label=no`, `minion=yes`.

Live proof:

- Snapshot `live-after-homepage-july-favorites-nav` returned HTTP `200` for
  `/`, `/shop`, `/contact`, `/balloon-twisting-and-face-painting`, and all four
  favorite product routes.
- Live homepage renders Customer Favorites, the four favorite product titles,
  and `From $90.00`, `From $175.00`, `From $35.00`, `From $35.00`.
- Stable section IDs prove Reviews, Customer Favorites, Twisting, One of a Kind
  Designs, client crawl, and CTA order.
- Old `Balloons-to-Order` / `All Balloons-to-Order` copy is absent from the
  fresh live homepage.
- `/shop` title is `Pickups & Deliveries Balloon Decor`.
- The three July hero WebP assets return `200 image/webp`.
- `python scripts/verify/cloudflare_launch_readiness.py --base-url https://locallytwisted.com`
  passed 10 checks with 0 blockers and 0 warnings.
- `LT_BASE_URL=https://locallytwisted.com npm run test:seo-contract` passed
  13/13.
- Before/after snapshot comparison:
  `.tmp/release-snapshots/live-before-vs-after-homepage-july-favorites-nav.json`
  with `critical_changes: []`.

Unavailable proof:

- Browser screenshots could not be captured on Wardenclyffe because no system
  Chromium was installed and Playwright refused the browser download for
  `ubuntu26.04-x64`.
- Broad live `public_asset_integrity.py` was stopped after hanging in DNS
  resolution; targeted updated hero asset GET checks passed.

## Current Verified State

- Live homepage already uses Fourth of July copy on the first hero slide.
- Live homepage still exposes `Balloons-to-Order` and `All Balloons-to-Order` in desktop, search, and mobile navigation surfaces.
- Live homepage currently renders the relevant order as Reviews, One of a Kind Designs, trusted-client crawl, closing CTA, then Live Entertainment.
- Local source now stores the Fourth of July first-slide copy and realistic balloon-decor asset paths in `HOME_HERO_SLIDES[0]` in `apps/locally_twisted/locally_twisted/www/home.py`.
- Local homepage template now renders Reviews, Customer Favorites, Live Entertainment, One of a Kind Designs, trusted-client crawl, and closing CTA in that order.
- Local navigation labels and verifier expectations now use `Pickups & Deliveries` / `All Pickups & Deliveries` for the public shop-category menu.
- All four current Customer Favorites product URLs return HTTP 200 on live `locallytwisted.com`.
- All four current Customer Favorites expose visible starting prices on the live product page:
  - Birthday Deliveries: `from $ 90.00`
  - Large head Missionary: `from $ 175.00`
  - Minion Bouquet: `from $ 35.00`
  - Bandage "GET WELL" Bouquet (Latex free): `from $ 35.00`
- Classic Arch was removed from the planned Customer Favorites row after GL requested Minion Bouquet instead, so the prior Classic Arch price hard stop no longer blocks this plan.
- Capability gate passed for this public-site planning lane with:
  - `capabilities/INDEX.md`
  - `capabilities/recipes/homepage-launch-proof-contract.md`
  - `capabilities/recipes/frappe-public-nav-business-route-contract.md`
  - `capabilities/recipes/frappe-shop-showroom-symmetry.md`
  - `capabilities/recipes/codex-browser-verification-surface.md`

## User-Confirmed Requirements

- The public menu label should be `Pickups & Deliveries`.
- Customer Favorites should show prices as `From $XX.XX` because customers still click through for option, add-on, and full pricing clarity.
- The Fourth of July image must look like real balloon decor. The current image is unacceptable because it reads as cartoony.
- The four Customer Favorites targets are:
  - `https://locallytwisted.com/shop-items/bouquets/birthday-deliveries`
  - `https://locallytwisted.com/shop-items/bouquets/large-head-missionary`
  - `https://locallytwisted.com/shop-items/bouquets/minion-bouquet`
  - `https://locallytwisted.com/shop-items/bouquets/bandage-get-well-bouquet-latex-free`

## Source Implementation Closeout

Implemented locally on 2026-06-24:

- Replaced the Fourth of July first-slide hero crop set with a real red/white/blue balloon-decor photo source copied to `_resources/generated-hero-sources/2026-06-24/july-4-home-hero-source-IMG_4341.jpeg`.
- Stripped EXIF/GPS/device metadata from the source copy and the three public WebP crops before commit.
- Rebuilt the desktop/tablet/mobile public hero crops at:
  - `apps/locally_twisted/locally_twisted/public/images/heroes/july-4-home-hero-desktop.webp`
  - `apps/locally_twisted/locally_twisted/public/images/heroes/july-4-home-hero-tablet.webp`
  - `apps/locally_twisted/locally_twisted/public/images/heroes/july-4-home-hero-mobile.webp`
- Added `CUSTOMER_FAVORITE_ROUTES` and `customer_favorites` in `home.py`.
- Favorite cards query published `Website Item` records by approved route and derive `From $XX.XX` through `get_variant_starting_price`.
- Added the `Customer Favorites` section in `home.html` after Reviews and before Live Entertainment.
- Added the section to the executable container contract and the interactive desktop/mobile layout contract.
- Renamed active customer-facing shop-category chrome to `Pickups & Deliveries` across desktop nav, mobile drawer, search quick links, footer, shop category rail/select, `/shop` copy, and source verifiers.
- Preserved category discovery; the public shop menu still comes from visible Item Group children under `Shop Items`, not product quick links.

Rendered local proof on `http://localhost:8081/`:

- Hero asset resolves to `july-4-home-hero-desktop.webp` on desktop and `july-4-home-hero-mobile.webp` on mobile.
- Section order metrics: Reviews before Customer Favorites, then Live Entertainment, then One of a Kind Designs.
- Favorite row cards:
  - Birthday Deliveries - `/shop-items/bouquets/birthday-deliveries` - `From $90.00`
  - Large head Missionary - `/shop-items/bouquets/large-head-missionary` - `From $175.00`
  - Minion Bouquet - `/shop-items/bouquets/minion-bouquet` - `From $35.00`
  - Bandage "GET WELL" Bouquet (Latex free) - `/shop-items/bouquets/bandage-get-well-bouquet-latex-free` - `From $35.00`
- Grid proof: 4 cards across on 1366px desktop; 2x2 on 390px mobile.
- Screenshot artifacts are local/ignored only at `output/homepage-july-favorites-nav/screenshots/`.

Local verification receipts:

- `python -m py_compile apps/locally_twisted/locally_twisted/www/home.py apps/locally_twisted/locally_twisted/www/shop.py apps/locally_twisted/locally_twisted/navbar_context.py apps/locally_twisted/locally_twisted/shop_taxonomy.py scripts/verify/nav_ia.py scripts/verify/ecommerce_pause_contract.py scripts/verify/smoke_shop.py`
- `npm run test:nav-ia`
- `npm run test:ecommerce-pause`
- `npm run test:search-contract`
- `npm run test:container-contract` -> `72 passed`
- `npm run test:interactive-layout` -> `159 passed, 1 skipped`
- `npm run test:layout-fit` -> `312 passed`
- `.venv/bin/python scripts/verify/smoke_shop.py`
- `npm run test:public-assets` -> `PASS (31 routes, 362 unique local asset URLs)`

Live release boundary:

- No Frappe Cloud app mirror push, Frappe Cloud deploy, site update/migration, live cache clear, provider change, payment change, or live route verification was performed in this source slice.
- Live `https://locallytwisted.com/` remains on the previous production state until an explicit release path is approved and completed.

## Scope And Ownership

### Parent Release

`homepage-july-favorites-nav`

This parent release coordinates four child features but keeps their acceptance separate.

### Child Feature 1: Fourth Of July Hero Image

Owner: homepage visual/content lane.

Implementation shape:

- Keep the approved Fourth of July copy unless GL requests copy edits.
- Replace only the failed image asset set or image references.
- Use realistic balloon decor imagery: red, white, and blue balloon installation, plausible photo lighting, event-ready scale, no text embedded in the image, no cartoon/illustration style, no flag-clip-art or novelty fireworks as the main subject.
- Produce and verify desktop, tablet, and mobile WebP crops.
- Update hero verifier expectations if filenames change.

Hard stop:

- Do not publish or mark ready if the image reads as illustration, toy render, flat AI graphic, or generic patriotic background instead of real balloon decor.

### Child Feature 2: Customer Favorites Product Row

Owner: homepage merchandising lane.

Implementation shape:

- Add `Customer Favorites` between Reviews and Live Entertainment.
- Use four product cards in the approved order:
  1. Birthday Deliveries
  2. Large head Missionary
  3. Minion Bouquet
  4. Bandage "GET WELL" Bouquet (Latex free)
- Desktop: 4 cards across.
- Mobile: 2x2 grid. This is the technical recommendation because 4-across on phone widths would make text, images, and tap targets cramped.
- Cards should use product image, name, short category or product-type label, `From $XX.XX` from product-page/source truth, and a direct link to the product page.
- Price source should come from the same product/variant starting-price logic that product pages use, not a separately hand-typed value.
- If a curated literal is temporarily needed for launch, it must be backed by current product-page/ERPNext evidence and documented as a temporary implementation choice.

Guard:

- The current four favorites all have visible live starting prices. If a future favorite is swapped in and lacks a product-page/source-backed starting price, block the homepage `From` price until parity exists or GL explicitly approves an exception with the amount and reason recorded.

### Child Feature 3: Homepage Flow Reorder

Owner: homepage structure lane.

Implementation shape:

- Move Live Entertainment above One of a Kind Designs.
- Insert Customer Favorites immediately after Reviews and before Live Entertainment.
- Preserve the existing review proof as the first post-hero band.
- Keep the trusted-client crawl and closing CTA in their existing relationship to One of a Kind Designs unless implementation inspection shows a safer placement is required.

Recommended final order for the affected block:

1. Hero carousel
2. Reviews
3. Customer Favorites
4. Live Entertainment
5. One of a Kind Designs
6. Trusted by Utah's Best Since 1998
7. Closing CTA
8. Newsletter/footer

Hard stop:

- Do not move Reviews away from first post-hero position.
- Do not cut or crop One of a Kind Designs proof photos during the reorder.

### Child Feature 4: Pickups & Deliveries Navigation Contract

Owner: public navigation contract lane.

Implementation shape:

- Rename customer-facing `Balloons-to-Order` to `Pickups & Deliveries`.
- Update derived customer labels intentionally:
  - Desktop primary trigger: `Pickups & Deliveries`
  - Mobile drawer accordion: `Pickups & Deliveries`
  - Search quick link: likely `All Pickups & Deliveries`
  - Footer link: likely `All Pickups & Deliveries`
- Preserve the existing category-discovery behavior under the menu. This is still an Item Group category surface, not a product dump.
- Keep `/shop` as the broad shop/category entry route unless GL explicitly changes route behavior.
- Do not change product categories, checkout behavior, delivery rules, or item visibility as part of this label rename.

Hard stop:

- Do not leave old customer-facing `Balloons-to-Order` text in active header, mobile drawer, search, footer, verifier expectations, or current docs.
- Do not turn the category menu into product merchandising while renaming it.

## Interfaces Or Artifacts

Likely implementation files:

- `apps/locally_twisted/locally_twisted/www/home.py`
- `apps/locally_twisted/locally_twisted/www/home.html`
- `apps/locally_twisted/locally_twisted/templates/includes/navbar/navbar.html`
- `apps/locally_twisted/locally_twisted/templates/includes/footer/footer.html`
- `apps/locally_twisted/locally_twisted/templates/includes/shop_category_nav.html`
- `apps/locally_twisted/locally_twisted/public/css/lt-theme.css`
- `apps/locally_twisted/locally_twisted/public/css/lt-page-containment.css`
- `scripts/verify/interactive_layout.spec.js`
- `scripts/verify/nav_ia.py`
- `scripts/verify/smoke_shop.py`
- `scripts/verify/ecommerce_pause_contract.py`
- Search-contract tests if quick links are asserted there.

Documentation to update after implementation:

- This workstream.
- `CODING-HANDOFF.md`.
- `ECOMMERCE-SHOP-HANDOFF.md` if product-card/source behavior changes.
- `locally-twisted-queue.md`.
- `locally-twisted-decisions.md`.
- `decisions/2026-06-24-homepage-july-favorites-nav-plan.md`.
- `lessons-learned.md` if new implementation behavior or verifier drift is found.
- `capabilities/recipes/homepage-launch-proof-contract.md`.
- `capabilities/recipes/frappe-public-nav-business-route-contract.md`.
- `capabilities/recipes/frappe-shop-showroom-symmetry.md`.
- `_resources/STYLE-GUIDE.md` if the hero image rule is clarified.

Agency/global decision docs were not changed in this planning slice because no
cross-client or agency-wide decision was made. The durable decision is scoped
to Locally Twisted public homepage/navigation behavior.

## Plan-Deepen Notes

### Structure

- Evidence checked: live homepage text, local `home.py`, local `home.html`, homepage capability recipe.
- Risks found: the requested order changes a protected homepage proof sequence; One of a Kind Designs currently carries installed-work proof and must not be visually degraded when moved.
- Plan adjustment: treat section order as its own child feature with screenshot proof at desktop, 375px, and 320px.
- Open question or escalation: none for order. Use the recommended order above unless GL changes it.

### Product Data And Pricing

- Evidence checked: live product route status and live product-page price text.
- Risks found: the original Classic Arch target was quote-first and lacked a visible starting price. GL replaced it with Minion Bouquet, which returns HTTP 200 and exposes `from $ 35.00` on the live product page.
- Plan adjustment: use Minion Bouquet as the third Customer Favorite and derive favorite-card prices from product-page/ERPNext starting-price truth.
- Open question or escalation: none for the current four-product row. If a future product lacks product-page/source price parity, block or record an explicit GL exception.

### Visual And Image Quality

- Evidence checked: user image rejection, style guide photo rules, homepage hero contract, image-continuity prompt sheet.
- Risks found: replacing copy without a realistic image fails the actual business request; generated images can drift into cartoon/AI-plastic if prompt and review criteria are loose.
- Plan adjustment: make photorealism an acceptance gate. Record continuity anchors before generation or selection: realistic balloon installation, Fourth of July palette, public/private Utah event context, black hero overlay compatibility, no embedded text, no cartoon look.
- Open question or escalation: GL review is recommended for the final hero image before live deployment because this is subjective brand quality.

### Navigation Contract

- Evidence checked: live homepage nav text, `navbar.html`, `footer.html`, nav/smoke/ecommerce verifier hits, nav capability recipe.
- Risks found: a simple label swap can leave stale old labels in paused-shop behavior, search quick links, mobile drawer, footer, and tests. Older docs still mix `Ready-to-Order`, `Balloons-to-Order`, and shop category wording.
- Plan adjustment: implement as a separate child feature with positive checks for `Pickups & Deliveries` and negative checks for active customer-facing `Balloons-to-Order`.
- Open question or escalation: none for the main label. Agent should recommend derivative labels during implementation, with `All Pickups & Deliveries` as the current plan.

### Release And Verification

- Evidence checked: browser verification capability, project AGENTS, current queue/handoff release guidance.
- Risks found: source push is not live proof. Frappe Cloud app mirror push, deploy, migration, cache clear, and live route checks are separate proof states.
- Plan adjustment: implementation closeout must name whether work is local-only, staging, or live. Do not claim live parity until public `https://locallytwisted.com/` proof passes after the actual release path.
- Open question or escalation: live deploy/update approval is required before production changes.

## Triadic Review

### Review Type

Real multi-agent triad was requested and tool support exists. Three read-only lanes were dispatched:

- Design/CRO/customer lens.
- Frappe source/test implementation lens.
- Risk/verification/documentation parity lens.

The synthesis must be updated with returned findings before implementation starts.

### Post-Triad Product Revision

After the triad returned, GL replaced Classic Arch with Minion Bouquet so the
Customer Favorites row fits the other three ready-to-order products. Live route
proof found `https://locallytwisted.com/shop-items/bouquets/minion-bouquet`
returns HTTP 200 and exposes `from $ 35.00`. The triad's Classic Arch hard
stop is superseded for this plan, but its broader price-parity guard remains:
do not show homepage `From` prices that are not backed by product-page/source
truth.

### Lens Findings

Design/CRO/customer lens:

- The parent release structure is sound because it leads with trust, then
  shoppable favorites, then live-service upsell, then custom-install proof.
- The client crawl and CTA should not interrupt the requested four-band
  sequence. They should sit after One of a Kind Designs unless GL changes the
  flow.
- Mobile Customer Favorites should be 2x2, not 4-across.
- The original Classic Arch price concern is resolved by the Minion Bouquet
  replacement.

Frappe source/test lens:

- Favorites should be data-backed from `home.py`, not hard-coded static HTML.
- Use fixed approved slugs/item codes, query published `Website Item` records
  for route/name/image, and use the same product/variant starting-price logic
  as product pages/shop listings.
- Keep the menu backed by `navbar_context.py` category discovery. Rename
  visible labels without turning the menu into product links.
- Update verifiers that currently assert the old nav label and homepage order:
  `nav_ia.py`, `smoke_shop.py`, `ecommerce_pause_contract.py`,
  `interactive_layout.spec.js`, `layout_helpers.js`, and search contracts if
  quick links are asserted there.
- The local LT ERPNext stack was not running during this planning review, so
  implementation must run browser/smoke proof after starting the local runtime.

Risk/verification/docs lens:

- The original Classic Arch target was the hard stop because it was quote-first
  and did not expose a live visible starting price. Minion Bouquet supersedes
  that target for the current plan.
- Final hero image review is a brand-quality gate before live publication.
- Source push, app mirror push, local proof, and live proof are separate states.

### Convergence

- Keep the parent release, but implement the four child features separately.
- Keep Reviews first after the hero.
- Use the final affected order: Reviews, Customer Favorites, Live
  Entertainment, One of a Kind Designs, trusted-client crawl, closing CTA.
- Use 4-across desktop and 2x2 mobile for Customer Favorites.
- Preserve category-discovery behavior while renaming the public menu to
  `Pickups & Deliveries`.
- Treat realistic hero imagery as required, not cosmetic polish.
- Treat product-page/source price parity as a standing guard. There is no
  current product-price blocker after the Minion Bouquet swap.

### Disagreement Or Dissent

The original dissent around Classic Arch pricing is resolved by the GL-approved
Minion Bouquet replacement. The standing dissent remains process-level: a
homepage-only `From` price should be treated as an explicit exception, not a
normal merchandising shortcut.

### Recommended Path

Use these four Customer Favorites in order:

1. Birthday Deliveries - `From $90.00`
2. Large head Missionary - `From $175.00`
3. Minion Bouquet - `From $35.00`
4. Bandage "GET WELL" Bouquet (Latex free) - `From $35.00`

### Remaining Risk

- Image quality remains subjective enough that GL should review the final
  hero image before live release.
- If the local runtime is down during implementation, verifiers must not be
  skipped; start the stack, clear website cache, and run the focused route
  checks before any readiness claim.

## Verification And Acceptance

Planning acceptance for this slice:

- Parent plan exists in this workstream.
- Child features and guards are explicit.
- Capability gate is recorded.
- Queue, handoff, decisions, lessons, and capability docs point future agents here.
- Real triad findings are integrated before final commit.

Implementation acceptance for the local source build:

- Homepage first slide uses realistic Fourth of July balloon decor, not a cartoon/illustration.
- Customer Favorites renders four cards with stable image sizes, professional spacing, working links, and 4-across desktop / 2x2 mobile layout.
- Favorite prices match product-page/source truth and use `From $XX.XX`.
- Current Customer Favorites are Birthday Deliveries, Large head Missionary, Minion Bouquet, and Bandage "GET WELL" Bouquet (Latex free).
- Relevant homepage order is Reviews, Customer Favorites, Live Entertainment, One of a Kind Designs.
- Active customer-facing nav/search/mobile/footer surfaces say `Pickups & Deliveries`, not `Balloons-to-Order`.
- Existing shop category discovery stays category-based, not product-list-based.
- Focused verifiers and screenshots pass locally before any staging/live step.
- Live proof on `https://locallytwisted.com/` happens only after approved release.

## Open Questions Or Assumptions

- Assumption: mobile Customer Favorites should be 2x2 for readability and professional tap targets.
- Assumption: derivative labels should use `All Pickups & Deliveries`.
- Open question: GL should review the final local hero image before live publication because the rejection was visual-quality based.

## Next Safe Step

This release is complete. Future changes should be opened as a new scoped
feature: either another seasonal hero/favorites change, a separate product
merchandising update, or a separate Frappe Cloud/provider release.
