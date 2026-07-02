---
id: homepage-launch-proof-contract
name: Homepage Launch Proof Contract
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted ERPNext/Frappe homepage hero, proof crawls, cookie placement, and launch CTAs
currently_true: unknown
verification_level: 2
last_verified: 2026-05-11
evidence_quality: direct
successful_uses: 5
failed_uses: 1
regressions: 1
depends_on:
  - frappe-public-container-contract
  - responsive-container-audit
  - compact-hero-contract
  - cross-browser-motion-visual-verification
used_by:
  - website-launch
tags:
  - Locally Twisted
  - homepage
  - launch
  - proof crawl
  - Frappe
  - Playwright
---

# Homepage Launch Proof Contract

Use this recipe before changing the Locally Twisted homepage hero, proof bands,
review crawl, trusted-client crawl, cookie notice placement, or launch CTAs.

## Current Contract

- The hero uses one visible stable H1, not hidden page-title plus rotating
  headings.
- Public heroes normally use generated lifestyle hero photos made through the
  project image-generation API and cropped per breakpoint. A seasonal homepage
  hero may use a real, source-recorded balloon-decor photo only when GL's
  approval/rejection is explicitly about realism and the source/crops are
  retained with private metadata stripped. As of the 2026-06-24 follow-up, the
  rejected Fourth of July slide is removed from local source; the old
  `/assets/locally_twisted/images/heroes/july-4-home-hero-*.webp` crop set is
  retained only as historical/recoverable source and is no longer referenced by
  the homepage.
- The first viewport must leave a hint of the next band visible on desktop and
  small mobile widths.
- The hero must obey the compact hero contract: 220px mobile, 250px tablet, and
  280px desktop standard heights, with no route-local oversized padding or title
  scale.
- Review proof is the first homepage band immediately after `.lt-hero`.
- The platform strip above the crawl shows GigSalad, Google, and Facebook as
  logos with platform-appropriate proof marks. It must not show exact counts,
  visible `reviews` labels, or card/container treatments around the logos.
- The review crawl uses curated five-star customer quote records from
  `home.py`. The template renders one readable copy and one duplicate copy for
  the marquee; both copies must use the same card markup, include a visible
  five-star row, and avoid placeholder/pending cards.
- On mobile, the review band is intentionally compact. The current
  interactive contract caps the total review block at 380px, the marquee at
  240px, review cards at 270px wide and 240px high, and prevents global
  `section` padding from leaking into `.lt-reviews-block__quotes`.
- On desktop, `.lt-reviews-block__quotes` must also neutralize global
  `section` padding. A leaked 4rem top/bottom section rule makes the review
  band look broken even when the cards are correct.
- The homepage currently does not render a trust/authority bar. Keep the
  approved brand SVG icon assets for future proof sections, but do not put the
  trust bar back into the homepage unless GL explicitly reopens that choice.
- The cookie notice is inline after `.lt-reviews-block` on the homepage. It must
  not be a fixed overlay covering CTAs there, and it must not sit between the
  hero and the Google review proof band. Other pages may still use the fixed
  banner.
- `Customer Favorites` appears after Google reviews and before Live
  Entertainment. It must use approved Website Item routes and source-backed
  `From` prices, with four cards across on desktop and 2x2 on mobile.
- `One of a Kind Designs` appears after Live Entertainment as a wide
  installed-work proof band. Real custom installation proof is still important,
  but the launch homepage now leads with social proof, product favorites, and
  live-service cross-sell before custom-install proof.
- Custom Event Decor is hidden from the current homepage behind
  `show_custom_event_decor = False`. The block's recovery archive is
  `_resources/homepage-custom-event-decor-2026-05-11/`, including the before-hide
  screenshot and extracted SVG icons.
- Future `One of a Kind Designs` photo replacements must render whole photos
  with shadows only. Do not use `background-image` crop surfaces, fixed-height
  image boxes, text overlays, captions inside the photo surface, or card
  containers that clip balloon art.
- Review cards and trusted-business names are full-stage crawls. Both move
  left-to-right. Review cards use the canonical `540s` loop, and the
  trusted-business crawl is measured in the browser so its pixel speed matches
  the review-card crawl even though its track width is different.
- The homepage proof crawls are a project-specific reduced-motion exception:
  they stay slow, linear, full-stage, and scrollbar-free in both
  `no-preference` and `reduce` media states unless GL explicitly changes the
  business-proof contract. Do not restore the static/scrollbar fallback.
- Homepage launch copy should speak to corporate, school, civic, community,
  venue, and private-event buyers without turning the page into technical
  planner language.

## Source Files

- `apps/locally_twisted/locally_twisted/www/home.html`
- `apps/locally_twisted/locally_twisted/www/home.py`
- `apps/locally_twisted/locally_twisted/public/css/lt-theme.css`
- `apps/locally_twisted/locally_twisted/public/css/lt-page-containment.css`
- `apps/locally_twisted/locally_twisted/public/js/lt-site-preferences.js`
- `scripts/verify/interactive_layout.spec.js`
- `_resources/homepage-custom-event-decor-2026-05-11/`

## Verification

Run after homepage/Jinja/CSS/JS changes:

```bash
python scripts/dev/clear_website_cache.py
npm run test:interactive-layout -- --grep "homepage review marquee|homepage client crawl banner|homepage reduced motion keeps"
npm run test:interactive-layout -- --grep "mobile review proof"
npx playwright test scripts/verify/layout_fit.spec.js --reporter=dot --grep "home fits"
npm run test:interactive-layout -- --grep "homepage|cookie notice"
npm run test:interactive-layout -- --grep "compact hero height contract"
```

After hiding or restoring Custom Event Decor, also verify that the intended
visibility state is true in the live DOM and rerun the homepage layout gate:

```bash
npx playwright test scripts/verify/layout_fit.spec.js --grep "home fits" --reporter=line --workers=1
```

If `home.py` route-controller constants such as `PAGE_CSS` changed, restart the
Frappe backend container before final browser inspection:

```bash
docker restart locally-twisted-erpnext-v15-backend-1
python scripts/dev/clear_website_cache.py
```

Capture and inspect at least desktop, 375px mobile, and 320px mobile screenshots
before marking the homepage ready for GL review.

## Red Flags

- Review cards expose a native horizontal scrollbar.
- Mobile review cards or padding grow until the Google review proof dominates
  the first mobile scroll.
- Trusted-business names stack instead of crawling.
- The two crawls differ in direction or speed.
- Either crawl moves right-to-left.
- Reduced-motion mode stops either proof crawl, exposes a scrollbar, stacks the
  cards/names, or lets one proof band diverge from the other.
- The hero reintroduces hidden H1 plus visible rotating headings.
- The hero grows back into a first-viewport wall or uses page-local min-height,
  oversized padding, or giant title clamps.
- A trust/authority bar appears between the hero and reviews.
- The installed-work proof band appears before reviews.
- Custom Event Decor returns to the homepage without an explicit flag change,
  archive review, and fresh desktop/mobile layout proof.
- The platform proof strip adds visible review counts, visible `reviews`
  labels, card shells, borders, shadows, or padded boxes around the logos.
- `One of a Kind Designs` photos are placed in crop containers, card shells, or
  text-overlay treatments that cut off balloon art.
- The cookie notice blocks primary CTAs on mobile or sits between the hero and
  Google reviews.
- Event Playground, blog-title cycling, or design-studio language returns to the
  launch hero without a fresh GL decision.
- The homepage uses reserved real/proof photos as hero crops instead of the
  generated lifestyle hero asset.
- A seasonal hero uses cartoon, flat illustration, novelty patriotic art, or a
  generic background when GL requested realistic balloon decor.
- A homepage product-merchandising row shows a `From` price that does not match
  product-page/source truth.

## LT Receipt

On 2026-05-07, GL reported that review cards were a scrollbar on one platform
and stacked on another, while trusted-business proof was not crawling. The first
repair accidentally documented/protected a static reduced-motion fallback. The
follow-up repair added the correct speed-sync and no-scrollbar mechanics, then
GL clarified the intended direction: both crawls should move left-to-right. The
current contract keeps the review crawl at the canonical `540s`, syncs the
trusted-business crawl to the review-card pixel speed with a homepage-only
measurement script, and makes the reduced-motion branch keep both proof crawls
slow, horizontal, moving, and scrollbar-free. Final corrected-direction
verification passed: left-to-right red run failed 5/5 against the previous
direction, then focused crawl regression 5/5, home layout 13/13,
homepage/cookie 12/12, compact hero 14/14, full `npm run test:website-verify`,
and live diagnostics showed positive left-to-right deltas with hidden overflow
and matched visible speed in `no-preference` and `reduce`. Screenshots are in
`output/playwright/home-crawl-left-to-right-20260507/`. The same-day proof-order
correction removed the homepage trust/authority bar, made Google reviews the
first post-hero band, moved the cookie notice after reviews, and moved Recent
Celebrations after the reviews block. Do not carry forward the earlier temporary
portfolio-blocked caveat unless a fresh run fails again.

On 2026-05-08, GL reframed the installed-work band as custom art instead of
ecommerce-adjacent cards. `Recent Celebrations` became `One of a Kind Designs`,
and `.lt-featured__inner` was given a wider visual-proof containment override
so the three desktop photos stretch across the stage while mobile remains a
single readable column. The focused homepage verifier now guards the heading,
three-wide desktop row, restrained gap, landscape image crop, and zero document
overflow.

Later on 2026-05-08, GL flagged that the mobile Google review section, cards,
and padding were too large. Live 320px measurement showed the review band at
about 693px tall. The repair tightened mobile review typography/padding,
neutralized inherited global `section` padding on `.lt-reviews-block__quotes`,
and added a compact mobile review sizing contract to
`interactive_layout.spec.js`. After cache clear/restart, live measurements at
320px, 375px, 390px, and 414px showed the review block at about 364px tall.
Targeted interactive review checks and targeted home layout-fit passed.

On 2026-05-10, GL flagged excessive landing-page Google review spacing and
inconsistent card content. Live desktop measurement found the nested review
carousel was inheriting the global desktop `section` padding, adding 64px above
and below the cards, and the visible-at-load duplicate marquee copy lacked the
per-card star row. The repair made review cards render through one template
macro for both marquee copies, removed placeholder-card rendering, zeroed the
carousel padding at every breakpoint, tightened desktop/mobile card spacing,
and added an interactive verifier for the curated review count, non-empty
review text, five-star rows in both marquee copies, and compact desktop
spacing. After cache clear/restart, live desktop measurement showed the review
band at about 444px tall with 19 unique curated reviews and 38 rendered marquee
cards; focused review tests passed 5/5 and homepage layout-fit passed 13/13.


## 2026-05-10 seasonal-carousel override

GL changed the launch homepage hero from a single static hero to a rotating seasonal/audience carousel. The first slide was updated on 2026-06-21 to a Fourth of July seasonal hero, followed by the four event audience lanes. On 2026-06-24 GL rejected that hero image and asked to remove the Fourth of July hero entirely; local source now opens with Civic & Community and has four total audience slides. The old "one stable generated lifestyle hero image" verifier expectation remains obsolete for this slice; the active guard is one visible page-level H1 on the first slide, compact hero sizing, reduced-motion fallback, quote-led CTAs, and no platform leakage. Feature handoffs: `workstreams/homepage-seasonal-hero-carousel-2026-05-10.md` and `workstreams/homepage-hero-photoreal-refresh-2026-06-24.md`.

## 2026-05-11 Custom Event Decor hide

GL directed that the homepage Custom Event Decor block be hidden while keeping a
screenshot and all eight icons recoverable. The current controller flag is
`show_custom_event_decor = False`; the guarded Jinja block remains in
`home.html`; recovery assets are in
`_resources/homepage-custom-event-decor-2026-05-11/`. The next photo work on
`One of a Kind Designs` must preserve whole photos and avoid crop/card/text
treatments.

## 2026-05-11 review platform proof and hub route cleanup

GL corrected the homepage review proof to be logo-only platform proof. The
current strip shows GigSalad, Google, and Facebook logos with proof marks, no
visible counts, no visible `reviews` label, and no platform cards/containers.
Feature handoff: `workstreams/homepage-review-platform-proof-2026-05-11.md`.

The graduation hero secondary CTA no longer points to `/event-balloons`, and
the hidden Custom Event Decor heading no longer links there. The removed route
is documented at `workstreams/event-balloons-route-removal-2026-05-11.md`.

## 2026-06-24 homepage July favorites and nav live release

GL rejected the current Fourth of July hero image as too cartoony and confirmed
that the replacement must look like real balloon decor. The source
implementation replaced the first-slide crop set with a real red/white/blue
balloon-decor photo source, stripped EXIF/GPS/device metadata from source and
crops, and kept the compact hero/image-overlay contract. The same parent
implementation adds a Customer Favorites row between Reviews and Live
Entertainment, then moves Live Entertainment before One of a Kind Designs. The
protected homepage rule still holds: Reviews remain the first post-hero proof
band.

Customer Favorites pricing must use product-page/source truth. The row was
revised on 2026-06-24 to replace quote-first Classic Arch with Minion Bouquet
after live proof showed Minion Bouquet returns HTTP 200 and exposes `from $
35.00`. The local implementation queries published Website Items by approved
route and formats `get_variant_starting_price` as `From $XX.XX`. Future swaps
must keep the same price-parity guard.

Source verification passed py_compile, `npm run test:nav-ia`, `npm run
test:ecommerce-pause`, `npm run test:search-contract`, `npm run
test:container-contract` `72 passed`, `npm run test:interactive-layout` `159
passed, 1 skipped`, `npm run test:layout-fit` `312 passed`, `.venv/bin/python
scripts/verify/smoke_shop.py`, `npm run test:public-assets`, and
desktop/mobile screenshot inspection. Live release then advanced app mirror
tracked branch `live-shop-discovery-20260529` from `5d7c952` to `8d8d205` with
`press-deploy-bench-40102`. Live route/content proof passed on
`https://locallytwisted.com/`: Customer Favorites renders with all four prices,
section IDs prove the requested order, old `Balloons-to-Order` copy is absent,
Cloudflare route gate passed, live SEO contract passed, and targeted July hero
WebP assets return `200 image/webp`.

Implementation handoff:
`workstreams/homepage-july-favorites-nav-plan-2026-06-24.md`.

## 2026-06-24 homepage hero photoreal follow-up

GL rejected the live Fourth of July hero and asked to remove it, then requested
3 or 4 generated photoreal options for each replacement lane before final image
selection. Local source removes the July slide and updates the carousel to four
audience slides. Browser screenshot proof is repaired through Playwright
1.61.1 and Brave/Chromium/Chrome fallback, with managed Chromium verified on
Wardenclyffe and Banebook. Built-in Codex image output extraction is repaired:
normal image generation is OAuth/session backed, and
`scripts/dev/save_latest_codex_image.py` extracts
`image_generation_call.result` session payloads into normal project files
without `OPENAI_API_KEY`.

GL later selected Civic & Community redo option 05, Schools & Campuses option
03, and Private Celebrations option 02, and those selected crops are now live.
For future replacements, still use
`capabilities/recipes/lt-photoreal-balloon-homepage-hero-contract.md` to
generate stored options through built-in Codex image generation, reject
AI-looking/physics failures, and record GL's selection before wiring public
crops. Follow-up handoff:
`workstreams/homepage-hero-photoreal-refresh-2026-06-24.md`.

## 2026-06-24 live root and Birthday Deliveries media repair

Current live proof after the later same-day repair: `https://locallytwisted.com/`
returns `x-page-name: home`, not the login page, and the public root is the
canonical homepage URL. The homepage hero set now uses the GL-selected
photoreal Civic & Community, Corporate Events, Schools & Campuses, and Private
Celebrations carousel. The Birthday Deliveries Customer Favorites card uses
`/files/birthday-deliveries--extra-12.webp`; `/files/birthday-deliveries.png`
is absent from fresh homepage HTML.

For future homepage merchandising/product-card image work, homepage proof must
check both the homepage card reference and the product page's primary-media
authority chain. The 2026-06-24 repair showed that Product Setup gallery rows
can be clean while `Website Item.website_image`, `Item.image`,
`LT Product Blueprint.primary_image`, and File attachment state still leave an
old main image live. Load
`capabilities/failures/product-primary-media-attachment-drift.md` for that
case. Handoff:
`workstreams/live-homepage-birthday-media-repair-2026-06-24.md`.
