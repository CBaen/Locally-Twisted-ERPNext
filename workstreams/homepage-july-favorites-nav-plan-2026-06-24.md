# Homepage July Favorites And Pickups Navigation Plan Brief

Date: 2026-06-24
Owner: Codex technical lead
Status: planning complete, implementation not started

## Route Record

Mode: plan-brief plus plan-deepen with real multi-agent triad review.
Decision needed: approve the implementation packet after reviewing the Classic Arch price hard stop and final image direction.
Scope owner: Locally Twisted public site source and live release lane.
System/project/runtime classification: single project, public site, client production surface.
Allowed actions in this slice: create planning, plan-deepen, triad, queue, handoff, capability, lesson, and decision documentation.
Forbidden actions in this slice: source implementation, ERPNext data mutation, Frappe Cloud deploy, live cache clear, provider changes, payment changes, product visibility changes, and customer communication.
Evidence bar: current repo files, current live public pages, capability recipes, and user-confirmed business direction.
Stop condition: stop before implementation if pricing, image approval, live release permission, or product-page parity is unclear.

## Outcome

Prepare the implementation-ready plan for a coordinated homepage and navigation update:

1. Replace the current weak Fourth of July hero image with realistic balloon decor.
2. Add a professional `Customer Favorites` product row between Reviews and Live Entertainment.
3. Reorder the relevant homepage bands to Reviews, Customer Favorites, Live Entertainment, then One of a Kind Designs.
4. Rename the public shop-category supermenu label from `Balloons-to-Order` to `Pickups & Deliveries`.

Implementation is intentionally separate from this planning slice.

## Current Verified State

- Live homepage already uses Fourth of July copy on the first hero slide.
- Live homepage still exposes `Balloons-to-Order` and `All Balloons-to-Order` in desktop, search, and mobile navigation surfaces.
- Live homepage currently renders the relevant order as Reviews, One of a Kind Designs, trusted-client crawl, closing CTA, then Live Entertainment.
- Local source stores the Fourth of July first-slide copy and asset paths in `HOME_HERO_SLIDES[0]` in `apps/locally_twisted/locally_twisted/www/home.py`.
- Local homepage template renders One of a Kind Designs before the client crawl, CTA, and Live Entertainment in `apps/locally_twisted/locally_twisted/www/home.html`.
- Local navigation labels and verifier expectations still include `Balloons-to-Order`, `All Balloons-to-Order`, and `All Ready-to-Order`.
- All four requested product URLs return HTTP 200 on live `locallytwisted.com`.
- Three requested products expose visible starting prices on the live product page:
  - Birthday Deliveries: `from $ 90.00`
  - Large head Missionary: `from $ 175.00`
  - Bandage "GET WELL" Bouquet (Latex free): `from $ 35.00`
- Classic Arch returns HTTP 200, but the live product page is quote-first and does not expose a visible starting price. It says the design needs a quick quote before checkout.
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
  - `https://locallytwisted.com/shop-items/arches/classic-arch`
  - `https://locallytwisted.com/shop-items/bouquets/bandage-get-well-bouquet-latex-free`

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
  3. Classic Arch
  4. Bandage "GET WELL" Bouquet (Latex free)
- Desktop: 4 cards across.
- Mobile: 2x2 grid. This is the technical recommendation because 4-across on phone widths would make text, images, and tap targets cramped.
- Cards should use product image, name, short category or product-type label, `From $XX.XX` when product-page parity exists, and a direct link to the product page.
- Price source should come from the same product/variant starting-price logic that product pages use, not a separately hand-typed value.
- If a curated literal is temporarily needed for launch, it must be backed by current product-page/ERPNext evidence and documented as a temporary implementation choice.

Hard stop:

- Classic Arch currently has no visible product-page starting price. Product-page/source parity is the recommended path. Do not show a homepage `From $XX.XX` for Classic Arch until either:
  - the product page also exposes a verified starting price, or
  - GL explicitly approves a homepage-only exception with the amount and reason recorded.

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
- Risks found: Classic Arch is quote-first and currently does not expose a visible starting price, while the user request asks for `From $XX.XX` prices.
- Plan adjustment: derive favorite-card prices from product-page/ERPNext starting-price truth. Block Classic Arch price display until product-page parity exists or GL explicitly approves a homepage-only exception.
- Open question or escalation: GL approval is required only if implementation cannot make Classic Arch price/page parity true but still wants a homepage `From` price; the amount and reason must be recorded.

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

### Lens Findings

Design/CRO/customer lens:

- The parent release structure is sound because it leads with trust, then
  shoppable favorites, then live-service upsell, then custom-install proof.
- The client crawl and CTA should not interrupt the requested four-band
  sequence. They should sit after One of a Kind Designs unless GL changes the
  flow.
- Mobile Customer Favorites should be 2x2, not 4-across.
- Classic Arch needs either an approved starting price or a non-price treatment.

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

- Classic Arch is the hard stop. It is quote-first and does not expose a live
  visible starting price, while the other three products do.
- Homepage-only Classic Arch pricing is not a normal implementation branch. The
  safer path is product-page parity first; a homepage-only price requires an
  explicit exception with the approved amount and reason recorded.
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
- Treat Classic Arch price parity as the only current business-data blocker.

### Disagreement Or Dissent

The only meaningful dissent is about Classic Arch pricing. The planning
baseline allowed product-page parity or explicit GL approval. The risk lane
strengthened this: product-page parity is the recommended default, and
homepage-only pricing should be treated as an exception, not the normal path.

### Recommended Path

Resolve Classic Arch before implementation by either:

1. adding a source-backed starting price that is also clear on the Classic Arch
   product page, then using the same `From $XX.XX` on the homepage card; or
2. getting explicit GL approval for a homepage-only `From` price and recording
   the approved amount; or
3. changing that one card to a quote-forward treatment, such as `Request a
   quote`, if GL approves deviating from the all-price row.

Option 1 is the technical recommendation because it keeps the homepage and
product page honest.

### Remaining Risk

- Image quality remains subjective enough that GL should review the final
  hero image before live release.
- If the local runtime is down during implementation, verifiers must not be
  skipped; start the stack, clear website cache, and run the focused route
  checks before any readiness claim.

## Verification And Acceptance

Planning acceptance for this slice:

- Parent plan exists in this workstream.
- Child features and hard stops are explicit.
- Capability gate is recorded.
- Queue, handoff, decisions, lessons, and capability docs point future agents here.
- Real triad findings are integrated before final commit.

Implementation acceptance for the future build:

- Homepage first slide uses realistic Fourth of July balloon decor, not a cartoon/illustration.
- Customer Favorites renders four cards with stable image sizes, professional spacing, working links, and 4-across desktop / 2x2 mobile layout.
- Favorite prices match product-page/source truth and use `From $XX.XX`.
- Classic Arch price treatment has product-page parity or explicit GL exception approval with the amount and reason recorded.
- Relevant homepage order is Reviews, Customer Favorites, Live Entertainment, One of a Kind Designs.
- Active customer-facing nav/search/mobile/footer surfaces say `Pickups & Deliveries`, not `Balloons-to-Order`.
- Existing shop category discovery stays category-based, not product-list-based.
- Focused verifiers and screenshots pass locally before any staging/live step.
- Live proof on `https://locallytwisted.com/` happens only after approved release.

## Open Questions Or Assumptions

- Assumption: mobile Customer Favorites should be 2x2 for readability and professional tap targets.
- Assumption: derivative labels should use `All Pickups & Deliveries`.
- Open question: Classic Arch homepage card price cannot safely be finalized until product-page price parity exists or GL explicitly approves a homepage-only exception with the amount and reason recorded.
- Open question: final hero image should be reviewed by GL before live publication because the rejection was visual-quality based.

## Next Safe Step

After this plan is accepted, implement child features in this order:

1. Fourth of July hero image asset replacement.
2. Customer Favorites data/source/card section, with Classic Arch price hard stop resolved.
3. Homepage flow reorder.
4. Pickups & Deliveries nav contract rename.
5. Focused local verification and screenshots.
6. Documentation closeout.
7. Separate release path only after explicit live/staging approval.

Before implementation starts, resolve Classic Arch pricing treatment or accept
that the first implementation pass will stop at that hard stop.
