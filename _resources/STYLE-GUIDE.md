# Locally Twisted - ERPNext/Frappe Style Guide

**Version:** 4.10
**Last Updated:** 2026-06-24
**Build Target:** ERPNext v15.105.0 + Frappe v15.106.0 / Webshop
**Primary Viewport:** Mobile-first, 375px base

This is the canonical style guide for the current Locally Twisted ERPNext build.
It translates GL's approved visual boards into durable implementation rules:
Civic Celebration is the structural foundation, Slate Blue and Berry is the
main palette discipline, and the Locally Twisted Brand Direction banner is the
quality bar for typography, icon work, and premium corporate finish.

The older legacy_source guide is reference material only. Claude-era notes and design
competition files can provide useful history, but they are not authority unless
their claims are verified against this repo and the running ERPNext site.
The old `_resources/design-guide/` synthesis was deleted on 2026-05-05 because
it conflicted with this visual direction and kept reintroducing light-blue/blush
styling.

Use this guide when writing customer-facing copy, building Frappe/Jinja pages,
styling Webshop surfaces, reviewing visual work, making image selections, drawing
icons, or briefing GPT/Codex-style coding agents. Version 4.10 keeps the
non-negotiable compact hero contract and adds the shared generated-photo hero
rule: public heroes use breakpoint-specific lifestyle crops made through the
project's built-in Codex image-generation flow under the black landing-page
readability overlay. If the built-in image appears only in the Codex session
instead of as a normal file, extract it with
`scripts/dev/save_latest_codex_image.py`; do not default to API-key CLI billing.
Existing real/proof photos are reserved for portfolio, product, and proof
surfaces unless GL explicitly rejects a seasonal homepage hero for lacking
realism; in that case, a real balloon-decor source photo may be used for the
seasonal homepage slot when source provenance is retained and private EXIF/GPS
metadata is stripped. The rejected Fourth of July homepage slide was removed on
2026-06-24; future homepage hero replacements must follow
`capabilities/recipes/lt-photoreal-balloon-homepage-hero-contract.md` with
stored option sets and GL selection before public crops are wired. Version 4.8
also recorded the `Pickups & Deliveries` shop-category label and the Customer
Favorites homepage row. It keeps the
portfolio correction:
portfolio photos carry the proof alone, without captions or visible frame
wrappers, while mobile keeps slide-in motion instead of becoming a static stack.
It also adds the balloon color addendum as the source for owner-approved swatches,
supplier-style color names, drawer grouping, and best web-match hex values.

---

## Quick Rules

1. **Civic Celebration is the base.** The site should feel like Utah civic/event authority: city, mountains, schools, public events, corporate entrances, and premium private celebrations.
2. **Brand Direction is the quality bar.** Use the premium banner feel: elegant wordmark scale, crisp brass line icons, disciplined spacing, and quiet corporate confidence.
3. **Slate Blue and Berry sharpen the palette.** Deep navy/slate, ink, warm white, brass, and crimson/berry are the working system. Balloon color belongs in photography, product choices, and customer-selected palettes.
4. **Typography is part of the premium signal.** Cormorant Garamond and Lato are the approved public-site pair. Do not replace them with a generic webapp font in visible brand surfaces.
5. **Photography proves authority.** Show real installed work in civic, school, corporate, venue, and upscale event contexts. The image should explain the scale before the copy does.
6. **Crisp brass line icons, not badge clutter.** Trust marks should look like Image #3's premium icon set, not clip-art circles or sticker badges. Use the new `public/icons/brand/` SVG suite for proof pillars, local/event context, and multiple balloon forms.
7. **Buttons are confident rectangles.** Deep navy, berry/crimson, and occasional brass-outline treatments. Avoid soft pill buttons and teal-heavy UI unless a specific transactional component already requires it.
8. **Locally Twisted is the brand.** Jeff can be founder/context; public copy should make the company and team own the promise.
9. **Every route has a treatment.** Home, shop, product, cart, checkout, contact, portfolio, BTFP, FAQ, policy, payment, header, footer, and drawer surfaces are all covered below.
10. **ERPNext first.** Work with Frappe/Webshop templates, hooks, and route rules.
11. **Fail loudly. Always.** Forms, automations, documents, customer messages, route contracts, containers, and agent claims must block false success and leave actionable evidence.
12. **Containers are launch-critical.** Text, images, controls, menus, cards, forms, chips, drawers, and modals must stay inside their containers at breakpoint edges and in open/expanded states.
13. **Verify visible work.** Do not claim a route, layout, or visual state works without checking it.
14. **Heroes are compact, photographic, and standardized.** A hero labels the page; it is not the page. Use the hero height contract below, use a generated lifestyle photo under the black landing-page readability overlay, and do not add page-local hero padding or giant title clamps without a documented exception. Seasonal hero images must read as realistic balloon decor, not cartoon art, flat illustration, or generic holiday graphics.
15. **Balloon color names and swatches outrank hex.** Use `_resources/STYLE-GUIDE-BALLOON-COLOR-ADDENDUM.md` when briefing generated images or matching customer colors. Hex values are best web approximations only.

---

## Approved Visual Target

The durable target is a blend of three GL-provided boards:

1. **Civic Celebration.** Use this for Americana authority, public-event scale, Utah geography, and the civic buyer posture. It supplies the "classic, bold, community driven" frame.
2. **Slate Blue and Berry.** Use this to keep the palette modern and corporate: near black/ink, crisp white or warm white, slate blue, crimson/berry, cool gray, and restrained photo color.
3. **Locally Twisted Brand Direction banner.** Use this as the quality standard. The banner's large premium wordmark, letterspaced labels, brass separator, dark ground, and four refined brass proof icons are closer to the intended finish than the current site.

Practical translation:

- The site should read as **premium Utah event infrastructure**, not a generic ecommerce theme.
- The first impression should say **experienced, local, corporate-safe, civic-scale, and tasteful**.
- The visual energy should come from **real balloon installations and Americana/Utah context**, not decorative UI color.
- The UI should feel **crisp, rectangular, editorial, and controlled**, matching the current professional homepage framework.
- The Brand Direction banner is the standard for icon quality, not just a decorative reference.

---

## Agent Usage

### For GPT/Codex Agents

- Treat this file as the brand and UI source of truth.
- Treat `If it can fail, it must fail loudly` as the operating law. A route,
  form, document, automation, container, or claim is not done if failure can
  look like success.
- Treat old legacy_source, Claude, handoff, and design-competition files as claims to verify.
- Do not copy implementation language from the legacy_source guide into ERPNext work.
- When this file conflicts with current verified route/form decisions, check
  `locally-twisted-decisions.md` and the running site before editing.
- Do not use the deleted `_resources/design-guide/` synthesis, old light-blue/blush screenshots, or its Next.js TSX files as current visual guidance.

### Frappe/ERPNext Implementation Rules

- Theme CSS lives in the `locally_twisted` app and is registered through `web_include_css`.
- Header/footer customization should use Jinja partial overrides.
- Static pages should live in `apps/locally_twisted/locally_twisted/www/`.
- Webshop pages should use Frappe/Webshop hooks, route rules, API wrappers, and template overrides.
- Avoid `head_html` CSS injection.
- Avoid `!important` chains. The known exception is the contained `.product-code` hide for Webshop's compiled product-card JS.
- After Jinja, CSS, or Web Page edits, run `python scripts/dev/clear_website_cache.py`.
- Before declaring visual work done, run the layout-fit, container-contract, and interactive-layout gates and inspect desktop/mobile screenshots.

---

## Hero Height Contract

This rule is non-negotiable for LT and rolls up to the Built by Cameron agency
standard. Product proof, forms, photos, and useful content sell the site; giant
heroes and repeated page-local padding do not.

| Viewport family | Standard hero height | Hard max | Vertical padding cap | Hero title cap |
|---|---:|---:|---:|---:|
| Mobile `< 768px` | 220px | 280px | 24px top / 24px bottom | 32px |
| Tablet `768px-1199px` | 250px | 300px | 28px top / 28px bottom | 40px |
| Desktop `>= 1200px` | 280px | 320px | 32px top / 32px bottom | 44px |

Expectations:

- If a page has a hero, it uses the same standard height as other heroes in
  that viewport family.
- Public page heroes use generated lifestyle photo layers with
  breakpoint-specific WebP crops: `*-mobile.webp`, `*-tablet.webp`, and
  `*-desktop.webp`. Do not source public hero crops from the reserved real
  work/proof photo library.
- The current generated hero sources, prompts, and contact sheet live in
  `_resources/generated-hero-sources/2026-05-10/`; only breakpoint-ready crops
  belong under the public `images/heroes/` asset path.
- Homepage photoreal replacement options now use the stricter source folder
  pattern under `_resources/generated-hero-sources/YYYY-MM-DD/homepage-photoreal-options/`.
  Store 3 or 4 distinct options per lane, reject AI-looking or physically
  impossible balloon installations, and wire public crops only after GL selects
  the option.
- Hero text must sit above the same black readability overlay pattern used by
  the landing page. Do not put hero text directly on a bare image.
- A hero may include an eyebrow, one H1, and one short lede at most.
- CTAs are allowed only if they fit inside the contract without crowding; move
  extra proof, delivery terms, route explanations, and secondary content below
  the hero.
- Do not use `section` defaults, route-local min-heights, large clamps, or
  oversized padding to make a hero fill the first viewport.
- On normal laptop viewports, the next section should be visible without the
  hero pretending to be the entire website.
- The verifier lives in `scripts/verify/interactive_layout.spec.js` under
  `compact hero height contract`.

---

## Public Container Contract

Every visible top-level customer-route section must have an explicit container
mode. This is launch-critical, not polish. The executable source is
`CONTAINER_CONTRACT_ROUTES` in `scripts/verify/layout_helpers.js`; the gate is
`npm run test:container-contract`.

Use these modes:

- `band`: normal section with a contained inner wrapper.
- `fullbleed`: deliberate full-stage visual band using `.lt-fullbleed`; readable
  content still needs an inner wrapper unless the surface is only a clipped
  track or visual field.
- `contained`: the element itself owns the readable/container width.
- `clip`: crawl/marquee viewport that clips overflow and never exposes a native
  scrollbar.
- `raw-band`: simple rule/cookie/support band that stays inside the viewport.
- `visual-field`: intentional visual exception such as the portfolio reel.

Rules:

- Do not depend on Frappe's `main.container` to create the visual page width.
  LT neutralizes it so each route owns its containers explicitly.
- Do not add a public route or direct `.page_content` child without adding it to
  the route contract.
- Do not add a full-bleed section without `.lt-fullbleed` and either an inner
  wrapper, a clipped track, or a documented `visual-field` exception.
- Keep the shared containment layer late in `web_include_css` so it remains the
  final public-site safety layer after theme/product/shop CSS.

---

## Existing Page And Element Coverage

This guide covers the customer-visible routes and reusable elements currently
present in the LT Frappe app and Webshop overrides. If a route or reusable
component is added, append it here before a broad implementation swarm begins.

### Current Routes And Templates

| Surface | Current route / file area | Brand role | Required treatment |
|---|---|---|---|
| Global header/nav | `templates/includes/navbar/navbar.html` | First brand contact and browse path | Two-level desktop nav may be used, but the logo must stay visually dominant, nav labels must meet accessible sizing, and the whole header should feel like the Image #3 banner translated to ecommerce. |
| Mobile header/drawer | `navbar.html` | Fast browse and cart access | Large logo, 44px controls, plain nav labels, dark/warm surfaces, no cramped menu text, no mystery icons. |
| Footer/newsletter | `templates/includes/footer/footer.html` | Closing brand trust and legal wayfinding | Deep navy/ink ground, warm text, brass labels, clean newsletter states, legal links visible. Use the logo/approved wordmark, not a random font fallback. |
| Home | `/`, `www/home.html`, `www/home.py` | Highest brand authority page | Civic/Utah hero image, Cormorant hero type, GigSalad/Google/Facebook review proof immediately after the hero, no homepage trust bar unless GL reopens it, large recent-work photos after reviews, custom decor discovery hidden for current launch, client proof, closing CTA. |
| Shop landing | `/shop`, `www/shop.html` | Pickups & Deliveries retail lane | Still premium but more practical. Keep category navigation, product cards, and add-to-cart clear; use restrained surfaces so product color carries the page. |
| Category / item group listing | `/shop-items/<group>`, Item Group generator | Product discovery | Use editorial shop header, left/sidebar filters on desktop, drawer filters on mobile, stable grid cards, visible count/sort state, and product color as the visual accent. |
| Product detail/configure | Webshop item overrides under `templates/generators/item/` | Conversion and product clarity | Product image first, Cormorant product name, Lato specs/options, clear price and stock. Fixed-price products stay cartable; product group alone must not create a quote-only failure. Out-of-area delivery redirects to a prefilled `/contact` quote path. Do not render generic Additional Info, Reviews, or Recommended Items panels unless GL explicitly reopens that ecommerce decision. Product option controls must be clear, not boxed; pickup/delivery is the approved framed product-detail exception. |
| Cart | `/cart` -> `www/lt_cart.html` | Review before checkout | Quiet transactional page with order-summary hierarchy, stable quantity controls, clear empty/error/loading states, and contact fallback. |
| Checkout | `/checkout`, `www/checkout.html` | Payment trust | Most restrained surface: secure, plain, readable, minimal ornament. Keep form labels clear, required states visible, summary grounded, and trust language factual. If delivery ZIP is outside the configured zone, show a delivery quote request path and carry checkout details into `/contact`; do not imply the product itself became unpurchasable. |
| Event Playground / Plan Custom Decor | Hidden `/event-playground`, `www/event_playground.html`, local Vite PlayCanvas iframe | Internal decor-planning preview and contact-form handoff; parked for OpenClaw | Game-like but premium. Keep the Frappe shell in Civic/Slate/Berry styling, isolate the local canvas preview from site CSS, keep mobile controls 44px+, and clearly say final quote, install method, measurements, weather limits, and availability are confirmed by Locally Twisted before booking. Browser-preview copy can say `Plan Custom Decor`; the workstream/route remain Event Playground until renamed by decision. Render counts are planning visuals, not quote math. Do not add public navigation, a production bundle, backend saves, automatic Lead/Quote/Sales Order creation, share links, pricing, or checkout behavior until approved. |
| Payment success | `/payment-success`, `www/payment_success.html` | Transitional utility page | Use the same typography and colors as thank-you; avoid inline one-off font/color styles in future cleanup. |
| Thank you | `/thank-you`, `www/thank_you.html` | Post-payment reassurance | Calm, premium confirmation with order facts, no confetti energy, clear next step. |
| Contact/inquiry | `/contact`, `templates/includes/book_form.html` | Main custom-work conversion | Dark civic intro, two-column form/info layout on desktop, large Cormorant heading, white form surface, warm/stone fields, Deep Navy primary action/focus, Brass focus ring, Berry only for required/error states, company/team copy. |
| Legacy book | `/book` | Compatibility path | Redirect or visually match contact if rendered. Do not make `/book` the primary public CTA unless the route decision changes. |
| Portfolio | `/portfolio`, `www/portfolio.html` | Proof gallery | Photos are the product. Keep the approved collage/movement and whole-photo reel, but use the native LT shell, sitewide Cormorant/Lato typography, and branded compact hero copy. Do not render captions, visible frame wrappers, letterbox bands, card containers, or a route-specific Inquire/Studio/Index footer block on the photos/page field. A subtle desktop edge fade and shadow are allowed only as image treatment, not as a visible container, and clicked desktop photos must not cover the hero. Mobile must reveal full-width photos with slide-in motion instead of becoming a static stack. Do not copy prototype page chrome, custom cursor, route-local Google font imports, or off-brand hero copy. |
| Balloon twisting / face painting | `/balloon-twisting-and-face-painting` | First-class live-service lane | Can be warmer and more playful in photos, but still structured: editorial intro, service cards, brand-blue support/event-type bands, shared inquiry section, calculator, and expectation card. The calculator uses one row per artist so service and hours can vary by artist. No red Process-era divider/banner. |
| FAQ | `/faq` | Objection handling | Clean grouped questions, generous line height, details/accordion states accessible, CTA to contact. No decorative clutter. |
| Policies | `/privacy`, `/terms-of-service`, `/refund-policy`, `/accessibility` | Legal and trust surface | Warm-white document layout, narrow readable measure, Cormorant H1/H2, Lato body, brass/berry links only where useful. |
| Search and Frappe utility pages | `/search`, login/account flows where Frappe owns chrome | Utility wayfinding | Keep global shell consistent. Do not invent a separate visual language for low-frequency utility screens. |

`/contact` is the canonical inquiry page. `/book` is legacy compatibility only
and should redirect to `/contact?intent=quick` unless a later route decision
changes that. Customer CTAs should normally point to `/contact`, not `/book`.
Current primary navigation includes a non-link `Event Balloons` audience
dropdown, `Pickups & Deliveries`, `Twisting & Face Painting`, `Portfolio`,
`About Us`, `FAQ`, and `Contact Us`, with top-banner `Free Event Quote` pointing to
`/contact`. The event dropdown links only to the four audience pages. Do not add
standalone `/process` or `/event-balloons` pages or links unless GL explicitly
approves them.

### Reusable Element Map

| Element | Exists as | Required treatment |
|---|---|---|
| Premium proof bar | Future trust/value bars | Dark ink/navy/slate band, brass line icons, short uppercase Lato titles, compact proof text. Use the Image #3 icon standard, but do not render a homepage trust bar in the current launch layout. |
| Hero sections | `lt-hero`, `lt-shop__hero`, `lt-portfolio__hero`, page intros | Cormorant headings, Lato labels, breakpoint-specific photo crops, and the black landing-page readability overlay. Generated lifestyle crops are the normal path. A seasonal homepage slot may use a real balloon-decor source photo only when GL explicitly rejects generated/cartoon realism, and source metadata must be stripped before commit. Dark authority feel stays consistent across public heroes; product/legal page warmth belongs below the hero unless a documented exception is approved. |
| Photo cards / proof reels | Featured work, portfolio reel, product cards, BTFP service cards | Preserve real work. Product cards can crop tighter; proof/portfolio surfaces need context, scale, natural image ratios, and movement where the route contract calls for it. Portfolio photos are not caption cards; use the image itself with no visible frame wrapper. Hidden/offscreen moving items must not be keyboard focusable. |
| Filters/chips | Shop chips, portfolio pills, category filters, product option chips | Rectangular or lightly rounded, Lato 700, visible selected state, and restrained selected/hover states. |
| Forms | Contact/book form, checkout, newsletter | Lato labels, white form surface, warm/stone inputs, visible Deep Navy/Brass focus, clear required text, loud Berry error state, no placeholder-only labels, no duplicate page-specific form systems. |
| CTAs | Hero/contact/shop/cart/checkout buttons | Primary is berry/crimson or deep navy. Secondary is transparent outline. Keep labels plain and short. |
| Accordions/details | FAQ and mobile nav accordions | Large hit areas, clear expanded state, keyboard support, no tiny chevrons as the only signal. |
| Drawers/modals | Mobile nav, portfolio modal, cart/filter drawers | Dark/warm brand surfaces, focusable close buttons, trapped/managed focus where modal, no visual jump or hidden overflow. |
| Reviews | Home review block, future testimonials | Support proof, do not lead the brand. The homepage platform strip is logo/proof only: no exact counts, no visible `reviews` labels, and no card/container treatments around GigSalad, Google, or Facebook. Verify current rating/count before publishing numbers. |
| Logo/client crawl | Home client proof | Use text/category proof unless logo permission is confirmed. Homepage proof crawls move left-to-right at matched visible speed; keep movement slow, linear, pauseable, scrollbar-free, and out of the tab order when items are not interactive unless the business-proof contract changes. |
| Empty/loading/error states | Cart, checkout, shop, forms, filters | Plain language, calm hierarchy, phone/contact fallback for customer blockers. |

Use plain customer labels. Avoid backend CRM language in public copy.

| Avoid | Prefer |
|---|---|
| Qualification Status | Status of Inquiry |
| Qualified By | Reviewed and First Contact By |
| Qualified On | Reviewed On |
| Lead Owner | Who's Handling This |
| Pipeline Stage | Where We Are / What Stage |
| Opportunity | Booking, inquiry, or event |

---

## Design Principles

1. **Civic Celebration sets the subject matter.** Lead with Utah territory, event scale, civic/public proof, school spirit, corporate entrances, and premium private-event installs.
2. **Brand Direction sets the finish.** Use the premium banner's serif presence, letterspaced labels, brass linework, dark authority bands, and clean icon hierarchy.
3. **Slate Blue and Berry sets restraint.** The site should lean ink/navy/slate/warm-white with berry/crimson action moments. Keep the interface structured and let product/media color carry the celebratory range.
4. **Photography is proof.** Use real installed work for credibility; use generated visuals only as labeled concepts or product visualization.
5. **Americana should be implied, not costume.** Mountains, city skylines, school colors, civic arches, parade routes, formal entrances, and public venues are the right imagery. Avoid flag-wall cliches or novelty patriot graphics unless they are real client work.
6. **Retail clarity is contained.** Ready-to-order shopping can be simple and practical; the company identity stays event-authority led.
7. **Mobile-first, always.** Start at 375px; desktop enhances.
8. **Specificity beats salesmanship.** Details, service areas, process, and constraints build trust.

---

## Color System

The approved blend is Civic Celebration plus Slate Blue and Berry. Use deep,
serious grounds with warm paper, brass detail, and berry/crimson action. Balloon
photos provide most color.

Balloon color selection, generated hero prompts, and customer color matching use
the separate addendum: [`STYLE-GUIDE-BALLOON-COLOR-ADDENDUM.md`](STYLE-GUIDE-BALLOON-COLOR-ADDENDUM.md).
The balloon color name and owner-approved swatch image are the authority; sampled
hex values are only web approximations.

### Core Palette

| Name | Hex | Role |
|---|---:|---|
| Ink | `#0A0A0B` | Highest-contrast headings, dark bands, premium footer |
| Deep Navy | `#0E2240` | Civic authority panels, header/nav emphasis, proof bands |
| Slate Blue | `#2F3A4A` | Corporate secondary dark, cards, filters, muted UI panels |
| Soft Gray | `#595A5C` | Body copy, secondary text, captions, quiet form help |
| Warm White | `#FAF7F2` | Main page background and warm content surfaces |
| Near White | `#FBFBFB` | Card stacks and neutral utility backgrounds |
| White | `#FFFFFF` | Product cards, form cards, clean content surfaces |
| Brass | `#B89A5B` | Line icons, dividers, proof highlights, secondary premium accents |
| Crimson / Berry | `#B31B34` | Main action color, civic/event energy, selected emphasis |
| Stone | `#E7E5E1` | Borders, subtle panels, neutral backgrounds |
| Sandstone | `#D9C7B3` | Warm section separation and secondary soft backgrounds |
| Deep Teal | `#0F3D3E` | Restricted secondary accent for legacy/product contexts, not the main brand signal |

### Accent Palette

Use accents for thin rules, icon strokes, small chips, and deliberate CTA contrast.
Do not build the company identity from color noise. Balloon colors belong
primarily in photography, product imagery, and customer-selected palettes.

Retired color behavior: the earlier small-catalog color system is no longer the
main company palette because the current buyer priority needs professional event
authority first.

### Surface Tints

| Name | Hex | Derived From | Use |
|---|---:|---|---|
| Warm Tint | `#F6F0E8` | Sandstone | Search bars, newsletter inputs, menu backgrounds |
| Stone Tint | `#F2F3F5` | Stone | Form fields and dropdowns |
| Slate Tint | `#EEF0F2` | Slate Blue | Filter surfaces and quiet utility panels |
| Brass Tint | `#F7F1E4` | Brass | Highlight backgrounds and promo bars |

### Color Rules

- Use ink, deep navy, and warm white as the main site structure.
- Use slate blue when black/navy would be too severe but the surface still needs corporate weight.
- Use brass for premium line icons, dividers, proof highlights, and small details.
- Use crimson/berry for the strongest public CTAs. Use deep navy for quieter CTAs. Use deep teal only where an existing transactional/product pattern specifically calls for it.
- Body text uses a controlled gray on light surfaces; headings use ink.
- Avoid pale-blue header/footer dominance.
- Avoid low-contrast color systems and playful color blocking in company-level chrome.
- Never stack two different colored full-width sections back-to-back.

Pattern:

```text
Warm White content -> thin brass/slate rule -> photo proof -> dark authority band -> Warm White content
```

---

## Typography

| Role | Font | Fallback | Weight |
|---|---|---|---|
| Brand Wordmark / Premium Mark | Cinzel | Georgia, serif | 600, 700 |
| Editorial Headings | Cormorant Garamond | Georgia, serif | 600, 700 |
| Body / UI / Labels | Lato | system sans-serif | 400, 700, 900 |

### Type Scale

| Level | Mobile | Desktop | Font | Color | Use |
|---|---:|---:|---|---|---|
| H1 | 32px | 56px | Cormorant Garamond | Ink or Warm White | Page hero titles |
| H2 | 26px | 40px | Cormorant Garamond | Ink | Section headings |
| H3 | 20px | 28px | Cormorant Garamond | Ink | Card/service titles |
| Label | 12px | 14-16px | Lato 700/900 | Ink, Brass, or Warm White | Navigation, proof labels, eyebrow text |
| Body | 16px | 18px | Lato 400 | Soft Gray | Paragraphs |
| Small | 12px | 13px | Lato 400 | Soft Gray | Captions and fine print |

Rules:

- Left-align body text.
- Do not justify text.
- Keep desktop line length around 40-60 characters.
- Do not skip heading levels.
- Do not scale font sizes with viewport width.
- Letter spacing should be `0` for paragraphs and normal headings.
- Letter spacing is allowed for premium wordmark/label treatments only, matching the Brand Direction banner.
- Do not replace public brand surfaces with Montserrat, Arial-like generic UI, or framework default fonts. If a component still uses Montserrat, treat that as legacy until intentionally migrated.
- Avoid oversized all-caps body copy. Use all-caps only for labels, eyebrow text, short proof titles, and brand/banner moments.

---

## Spacing And Layout

Use 8px increments.

| Token | Mobile | Desktop | Use |
|---|---:|---:|---|
| Section padding | 32px | 64-80px | Main content sections |
| Thin band height | 40-60px | 60-80px | Accent separators |
| Card padding | 16px | 24px | Cards and panels |
| Element gap | 12px | 16px | Heading-to-copy rhythm |
| Button padding | 12px 24px | 14px 32px | CTA buttons |

### Layout Rules

- Mobile-first CSS only; base styles target 375px.
- Use `min-width` media queries.
- Breakpoints: 768px tablet, 992px desktop, 1200px wide.
- Verification widths include 320, 360, 375, 390, 414, 768, 820, 991, 992, 1024, 1199, 1200, and 1366px. These catch tight containers that normal phone/desktop screenshots miss.
- Stable fixed-format UI needs stable dimensions: boards, grids, icon buttons, counters, swatches, and form controls should not shift when states change.
- Text must not overflow, overlap, or sit against container edges on 320px, 375px, tablet, desktop, or breakpoint-edge widths.
- Containers need real internal breathing room. If content touches the border, fix padding, grid tracks, wrapping, min-width, max-width, or state dimensions.
- Stateful UI must be checked while open: desktop mega panels, mobile drawer accordions, portfolio modal, contact conditionals, shop filters, and product option controls.
- Avoid body-wide `overflow-x: hidden` as a substitute for fixing layout.

### Balanced Collections

Even-count collections should form balanced rows where possible.

| Count | Mobile | Tablet | Desktop |
|---:|---|---|---|
| 2 | 2 across or stacked 1+1 | 2 across | 2 across |
| 4 | 2+2 | 2+2 or 4 across | 4 across or 2+2 |
| 6 | 2+2+2 | 3+3 or 2+2+2 | 3+3 or 6 across |
| 8 | 2+2+2+2 | 4+4 | 4+4 |

Avoid avoidable orphan rows such as 3+1 or 5+1.

---

## Professional Icon System

The Image #3 brass-line icons are a required part of the brand system, but the
site cannot stop at four generic proof marks. Locally Twisted is a balloon
company. The icon suite must include Utah/local proof, event-context proof, and
multiple balloon-specific forms so pages can speak in the business's actual
visual language.

### Core Proof Icons

Use these SVGs for banner-style proof pillars:

| Pillar | Label | Asset | Use |
|---|---|---|---|
| Utah rooted | `UTAH ROOTED` | `/assets/locally_twisted/icons/brand/utah-rooted.svg` | Header proof band, home authority bar, footer proof, civic/local claims |
| Design driven | `DESIGN DRIVEN` | `/assets/locally_twisted/icons/brand/design-driven.svg` | Design/process proof, custom decor explanations, proposal-style sections |
| Professional | `PROFESSIONAL` | `/assets/locally_twisted/icons/brand/professional.svg` | Trust, safety, on-time, insured/professional conduct claims |
| Trusted partner | `TRUSTED PARTNER` | `/assets/locally_twisted/icons/brand/trusted-partner.svg` | Corporate/civic buyer reassurance, process and collaboration sections |
| Event stage | `EVENT READY` | `/assets/locally_twisted/icons/brand/event-stage.svg` | Production, stage, venue, and planned-event sections |
| Delivery and install | `DELIVERED CLEANLY` | `/assets/locally_twisted/icons/brand/delivery-install.svg` | Delivery, setup, strike, and service-process sections |

### Balloon Icon Suite

These are the preferred icons for balloon-specific navigation, service cards,
portfolio filters, product-category introductions, and visual proof rows:

| Balloon form | Asset | Use |
|---|---|---|
| Balloon pair | `/assets/locally_twisted/icons/brand/balloon-pair.svg` | General balloon decor, brand marks, small proof rows |
| Balloon cluster | `/assets/locally_twisted/icons/brand/balloon-cluster.svg` | Organic clusters, color/grouping, material proof |
| Balloon arch | `/assets/locally_twisted/icons/brand/balloon-arch.svg` | Arches, entrances, parade/civic hero support |
| Organic garland | `/assets/locally_twisted/icons/brand/organic-garland.svg` | Garlands, organic decor, premium private events |
| Balloon column | `/assets/locally_twisted/icons/brand/balloon-column.svg` | Columns, entry markers, school/corporate installs |
| Balloon bouquet | `/assets/locally_twisted/icons/brand/balloon-bouquet.svg` | Ready-to-order, delivery, gifts, smaller retail pieces |

### Local And Event Context Icons

Use these to keep the Americana/authority posture specific instead of generic:

| Context | Asset | Use |
|---|---|---|
| Civic parade | `/assets/locally_twisted/icons/brand/civic-parade.svg` | City events, parades, civic arches, public installs |
| Corporate entrance | `/assets/locally_twisted/icons/brand/corporate-entrance.svg` | Corporate lobbies, branded entrances, professional buyers |
| School spirit | `/assets/locally_twisted/icons/brand/school-spirit.svg` | Schools, universities, graduations, team-color installs |
| Premium private event | `/assets/locally_twisted/icons/brand/premium-private-event.svg` | Weddings, showers, upscale private events |

### Icon Drawing Rules

- SVGs use `viewBox="0 0 64 64"`, `fill="none"`, `stroke="currentColor"`, rounded line caps, and 2.2-2.75px stroke width.
- The CSS color should usually be Brass `#B89A5B` on Ink/Deep Navy/Slate Blue.
- Icons should be 44-64px depending on surface, with enough surrounding space to feel premium.
- Use custom line geometry with enough business-specific detail to read as Utah, events, or balloon decor. Avoid filled badges, emoji-like marks, clip-art symbols, generic sticker circles, or a single two-balloon mark used everywhere.
- Balloon pages should use balloon-form icons first, not abstract trust icons.
- Decorative icons need `alt=""` or `aria-hidden="true"`. If the icon is the only visible label, provide an accessible label on the link/button/card.
- Do not mix icon families inside the same proof bar. If lucide icons are needed for utility controls, keep them in utility chrome, not brand proof.

### Future Icon Slots

If the Civic Celebration trust badges are rebuilt, draw them in this same
professional brass-line style. Likely future assets:

| Future label | Concept |
|---|---|
| Fully insured | Shield/check, if the insurance claim is verified and approved |
| Safety first | Warning triangle or cone, only if paired with real safety/process copy |
| Highly rated | Star/review mark, only with verified current rating/count |
| Timely and reliable | Clock/check or calendar/check |
| Premium materials | Diamond/material mark |

Do not use circular Civic Celebration badges as-is on the site. The content may
be useful; the execution needs to be redrawn to the Image #3 quality standard.

## Components

### Buttons

| Type | Background | Text | Border | Use |
|---|---|---|---|---|
| Primary | Crimson/Berry or Deep Navy | White | none | Main CTAs: Contact Us, Request a Quote, Continue |
| Secondary | Transparent | Ink | 1px Stone or Brass | Supporting actions |
| Tertiary | Transparent | Soft Gray | 1px Soft Gray | Low-emphasis actions |

Rules:

- One primary button per section unless a transactional Webshop flow requires more.
- Minimum touch target is 44px by 44px.
- Mobile buttons can stack full-width; desktop buttons can sit inline.
- "Read More" and "View Details" are secondary, not primary.
- Button shape should be rectangular and crisp: 0-4px radius for premium/civic surfaces, 8px maximum where the existing component system requires it.
- Button text uses Lato 700/900, short labels, and controlled letter spacing. Avoid soft playful button typography.

### Forms

- Shared inquiry forms use `templates/includes/book_form.html` and declare
  `data-form-contract="inquiry-v1"`. Do not fork a second public inquiry form
  for a service page; pass scoped context into the shared partial instead.
- The form surface is white with a thin Deep Navy top rule, restrained border,
  and no nested card-inside-card styling. Page sections own surrounding layout.
- Field backgrounds use Warm White or Stone, not blue-tinted inputs and not
  placeholder-only labels.
- Labels are visible, Lato, compact, and clear. Required markers use Berry;
  errors use Berry and must fail loudly.
- Focus states use Deep Navy with a Brass ring so keyboard users can see the
  active field without the form turning decorative.
- Service choices are structured options with selected state, not a loose list
  of raw checkboxes. Conditional panels use a Deep Navy left rule.
- Primary form actions are Deep Navy; Berry is reserved for hover/action energy,
  required marks, and loud failure states.
- Group related inputs with fieldsets and legends where appropriate.
- Public form copy should be plain and customer-friendly.

Current service taxonomy:

- Balloon Decor
- Balloon Twisting
- Face Painting
- Delivery
- Pickup
- Events Inquiry
- Something Else

Do not reintroduce `Delivery Only`, `Pickup Only`, or `Event Package`.

### Cards

- White background on Near White page background.
- Subtle border or shadow.
- Product/category photo first, text below.
- Card names use Ink.
- Body copy uses Soft Gray.
- Border radius: 8px unless an existing Frappe/Webshop component requires otherwise.
- Product detail pages are not card stacks. Product options such as size, latex
  color, add-on numbers, chips, selects, and price/add-to-cart groups must not
  be boxed. Keep the pickup/delivery notice as the approved framed exception;
  do not add recommendation or empty auxiliary product panels.

### Header And Navigation

- Logo/brand element always links to `/`.
- Header typography must follow the Brand Direction banner: premium wordmark, Lato nav labels, crisp spacing, and a controlled rectangular CTA.
- The logo should feel like a brand mark, not a tiny text label. Do not shrink it to solve layout problems; fix the layout.
- Desktop navigation can be one or two rows, but spacing must feel intentional. Avoid boxed/floating row fragments, cramped 12px nav labels, and disconnected rules.
- Primary nav order is currently:
  - Event Balloons audience dropdown
  - Pickups & Deliveries when ecommerce is open
  - Twisting & Face Painting
  - Portfolio
  - About Us
  - FAQ
  - Contact Us
- The utility area keeps `Free Event Quote` pointed at `/contact`.
- Do not add Gallery, Book an Event, or What We Make links unless scope is reopened.
- Do not revive the old mega-menu, Plan-by-Occasion model, standalone
  `/event-balloons` hub, or `/process` route unless GL explicitly reopens
  navigation IA.

### Footer

- Background: Deep Navy or Ink.
- Text and links: Warm White with Brass section labels.
- Brand mark uses the approved Locally Twisted logo asset. If a text fallback is required, use the premium wordmark rules from this guide, not Playfair Display, Montserrat, Raleway, or a framework default.
- Social icons need 44px targets.
- Footer should link to `/privacy`, `/terms-of-service`, and `/accessibility`.

### Trust/Value Bar

- Ink, Deep Navy, or Slate Blue band with brass line icons.
- Titles use styled non-heading elements when they are decorative/repeated.
- Descriptions use Warm White on dark bands or Ink on light bands.
- Use premium line icons for mountains/local roots, balloons/design, shield/professionalism, and partner/trust.
- Prefer the reusable SVG assets in `/assets/locally_twisted/icons/brand/` for those four pillars.
- Image #3 is the quality standard: thin brass strokes, simple geometry, enough detail to feel custom, never generic badge icons.
- Avoid circular Civic Celebration badge treatments unless intentionally redesigned into the premium brass-line system.

### Hero / Featured Media

- Prefer real photography.
- The photo carries the argument; copy annotates.
- Text sits over the shared black hero readability overlay; avoid fighting the image.
- The best homepage/hero direction is Americana authority: Wasatch mountains, Salt Lake or Utah city/civic context, formal entrances, parade arches, school/university installs, and public-event scale.
- Use Cormorant Garamond for large hero copy and keep the CTA rectangular. The hero should not feel like a party flyer.
- If using carousel behavior, include visible controls, touch support, and at least 5 seconds per slide.

---

## Photography

Photography is the proof layer. The current art direction should be edited and
selected to support Civic Celebration authority with Brand Direction quality.

### Subject Matter

- Prioritize real installed work in corporate, civic, school, venue, parade, city, church, university, and premium private-event settings.
- Prefer images with Utah or Americana authority cues: mountains, city skyline, civic buildings, public streets/parades, school/university signage, formal entrances, stages, lobbies, and community gathering spaces.
- Show complete structures when possible. Full arches, entrances, columns, organic garlands, photo ops, and stage installs should not be cropped so tightly that the scale is lost.
- Use people, doors, vehicles, stages, buildings, or skyline context as scale cues when they make the install feel larger and more professional.
- Family-party and novelty images can support the shop/BTFP lanes, but they should not lead the company-level brand.

### Editing Treatment

- Aim for the Image #3 quality bar: crisp, high-contrast, premium, clean, and controlled.
- Correct exposure and white balance so balloons and venue context are readable.
- Keep blacks rich, whites warm, and brass/berry details controlled. Avoid gray, muddy, or washed-out images.
- Remove or avoid photos that feel blurry, stretched, poorly cropped, over-saturated, or too phone-snapshot casual for the first impression.
- Do not apply heavy filters, fake blur, dark stock-style overlays, or color treatments that hide the balloon work.
- Use the shared black overlay where text sits over a hero image, and verify readability at mobile, tablet, and desktop sizes.
- Product photos are the color; the UI should not compete with them.

### Crop And Layout Rules

- Hero images: wide civic/authority compositions with a clear left or lower-left text zone. Ship explicit `mobile`, `tablet`, and `desktop` WebP crops for the actual 220px / 250px / 280px containers instead of stretching one source.
- Proof cards: show enough setting to understand buyer context, not only the balloon surface.
- Portfolio/detail images: preserve the full piece even if image heights vary. Full-piece visibility and natural aspect ratio matter more than perfect grid uniformity.
- Ready-to-order products can use cleaner catalog crops, but company-level pages need proof-rich installation imagery.
- Do not place text directly on busy product images unless readability is verified.

| Context | Aspect Ratio | Min Width | Format |
|---|---:|---:|---|
| Hero / feature | 16:9 or 4:3 | 1200px | WebP/JPEG |
| Product card | 1:1 or 4:3 | 600px | WebP/JPEG |
| Category thumbnail | 1:1 | 400px | WebP/JPEG |

---

## Brand Voice: Quiet Confidence

Locally Twisted sounds like someone who knows the work, respects the customer,
and does not need to shout.

### The Three Rules

1. **Present tense, not promises.**
   - No: "We will bring your vision to life."
   - Yes: "Custom balloon decor for celebrations along the Wasatch Front."

2. **Invite, never push.**
   - No: "Book now!"
   - Yes: "Tell us what you're imagining."

3. **Warm, not performing.**
   - No: "We LOVE what we do!!!"
   - Yes: "Every detail matters."

### Copy Examples

| Context | Avoid | Prefer |
|---|---|---|
| Hero | Utah's #1 Balloon Company - Book Today! | We make celebrations unforgettable. |
| Category intro | Check out our amazing holiday packages! | Something for every season. |
| Product copy | This STUNNING arch will WOW your guests! | Full balloon arch in your choice of colors. Includes delivery, setup, and teardown. |
| CTA | Call for a free quote! | Tell us what you're imagining. |
| Error page | Oops! Page not found! | This page floated away. Let's get you back. |

### Blog Voice

Blog writing can be softer and more teaching-oriented than product or service
copy. The reader may be worried they do not know the right terms. Reassure them,
explain the basics, translate jargon, and close toward the craft.

Rules:

- Lead with reassurance.
- Teach, do not lecture.
- Name jargon, then translate it.
- Keep the through-line close to craft: this is art, and Jeff knows how to make it.

Example:

- No: "Latex oxidizes faster in dry air."
- Yes: "Balloons can get a little chalky on the surface after a few hours. That is just the latex reacting to the air."

### Brand Archetype

Locally Twisted sits closest to **The Creator**:

- Makes beautiful things by hand.
- Values imagination and self-expression.
- Shares the work with quiet pride.
- Feels more like a working studio than a party-supply aisle.

Reference mood: considered, unhurried, earned, luminous, warm, premium, and civic-safe.

### Visual Voice Translation

Use copy and imagery together:

- "Big moments. Expertly executed." is aligned with the current visual target because it is short, civic, and authority-led.
- "Premium balloon decor for Utah events that matter" is aligned with the Image #3 banner tone.
- "Corporate, school, civic, and private celebrations" is better than generic "parties and events" when explaining range.
- Avoid copy that makes the site sound like a novelty shop, kids-party-only service, or founder-only craft booth.

---

## Accessibility

Target WCAG 2.1 AA.

### Contrast

| Context | Minimum | Approved Example |
|---|---:|---|
| Normal text | 4.5:1 | Soft Gray on White |
| Large text | 3:1 | Ink on accent bands |
| UI controls | 3:1 | Ink focus outline |

Avoid:

- Accent color text on white or near-white.
- Low-contrast small text on Stone, Deep Navy, or Ink.
- Low-contrast placeholder-only labels.

### Structure

- One `<h1>` per page.
- Do not skip heading levels.
- Decorative repeated labels should be styled `<p>` or `<span>` elements, not fake headings.
- Use landmarks: skip link, main region, nav, footer.
- Form groups use `<fieldset>` and `<legend>` where useful.
- Required fields need both visible indicators and machine-readable state.

### Interaction

- Every interactive element needs a visible focus state.
- Every hover state needs a keyboard-visible equivalent.
- Minimum touch target is 44px by 44px.
- Decorative icons use `aria-hidden="true"`.
- Links opening in new tabs include `rel="noopener"` and a screen-reader hint.
- Respect `prefers-reduced-motion: reduce`.

Suggested focus pattern:

```scss
a:focus-visible,
button:focus-visible,
.btn:focus-visible,
[tabindex]:focus-visible {
  outline: 2px solid $lt-near-black;
  outline-offset: 2px;
}
```

---

## CSS Conventions

- Keep custom CSS in the LT app.
- Prefix snippet/page classes with `lt-` or `s_lt_` according to existing local patterns.
- Prefer component-scoped selectors over broad global overrides.
- Do not hardcode new one-off colors when a token exists.
- Use CSS variables or SCSS variables for reusable color and spacing values.
- Avoid nested cards and decorative card-heavy section layouts.
- Avoid visible instructional copy that explains the UI rather than serving the customer.
- Keep cards at 8px radius unless matching an existing local component.

---

## Verification Before Completion

Before claiming visual/frontend work is complete:

1. Clear website cache after Jinja/CSS/Web Page edits.
2. Run relevant route or form checks.
3. Run `npm run test:layout-fit` for passive customer-site layout fit.
4. Run `npm run test:container-contract` for route-level section ownership, full-bleed/contained modes, and crawl clipping.
5. Run `npm run test:interactive-layout` for open menus, drawers, modals, forms, filters, product controls, and breakpoint behavior.
6. Run `npm run test:a11y` and `npm run test:a11y-manual` when public route accessibility, keyboard focus, moving proof surfaces, or form controls are in scope.
7. Run `npm run test:checkout-experience` when checkout layout or fulfillment preview behavior is in scope.
8. Run `npm run test:public-verify` before closing a broad public-site visual change.
9. Capture and inspect desktop and mobile screenshots.
10. Verify the actual route or user flow, not a proxy page.

Useful commands:

```powershell
python scripts/dev/clear_website_cache.py
npm run test:layout-fit
npm run test:container-contract
npm run test:interactive-layout
npm run test:a11y
npm run test:a11y-manual
npm run test:checkout-experience
npm run test:public-verify
python scripts/verify/nav_ia.py
python scripts/verify/smoke_shop.py
python scripts/verify/contact_service_logic.py --base-url http://localhost:8081
python scripts/verify/contact_prefill.py --base-url http://localhost:8081
```

Do not say "working", "fixed", "ready", or "verified" unless the relevant command,
route check, database check, or screenshot review actually happened.

---

## Quick Reference: What Color Do I Use?

| Building | Background | Text | Button |
|---|---|---|---|
| Hero/feature panel | Civic/Utah image with Ink/Navy overlay | Warm White if verified | Crimson/Berry or Deep Navy |
| Premium brand banner | Ink, Deep Navy, or Slate Blue | Warm White with Brass labels/icons | None or Crimson/Berry CTA |
| Trust/value bar | Ink, Deep Navy, or Slate Blue | Warm White with Brass icons | None |
| Product grid | White cards on Near White | Soft Gray, Ink links | Transactional only |
| Category section | White/Warm White | Soft Gray, Ink links | Secondary |
| Contact form | White with warm/stone fields | Soft Gray labels, Ink headings | Deep Navy or Crimson/Berry |
| CTA section | Deep Navy, Slate Blue, or Warm White | Warm White on dark / Ink on light | Crimson/Berry or Deep Navy |
| Footer | Deep Navy | Warm White with Brass labels | None |
| Search/menu | Warm Tint or Stone Tint | Soft Gray, Ink active | None |
| General content | White/Near White | Soft Gray body, Ink headings | Secondary |

---

## Future / Not Yet Canonical

Dark mode, printed collateral, social templates, signage, and expanded photo art
direction are not fully specified in this file yet. Do not invent those systems
as if they are approved. Add them deliberately when that scope opens.
