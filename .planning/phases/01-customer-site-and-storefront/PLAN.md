# Phase 1 Plan — Customer Site + Storefront

**Phase goal (from ROADMAP.md):** A customer can land on the site, browse what LT makes, learn enough to choose LT, and either complete a small purchase through the store or know how to start a custom booking conversation. The site looks and feels professional enough that Jeff says "yes, this is the LT experience" without prompting.

**Off-ramp gate:** if any slice exposes that ERPNext can't deliver the visual / UX bar, GL pivots away from ERPNext before building further.

## Slicing strategy

Phase 1 is sliced into 9 deliverables. Each slice ends in something visible GL can react to. Slices that depend on a decision gate are flagged.

Build order is sequential, but slices 6 (legal pages) and 9 (cart/checkout) can run in parallel with the slices before them once their dependencies clear.

| # | Slice | Dependencies | Decision gate? |
|---|---|---|---|
| 1 | Brand foundation (theme tokens, fonts, colors installed) | DONE | no |
| 2 | Header + footer | Slice 1 | no (nav option B locked) |
| 3 | Landing page | Slices 1–2 | no (placeholders set) |
| 4 | Balloon Twisting + Face Painting service page **with embedded pricing calculator** | Slices 1–2 | no (combined per GL 2026-04-26) |
| 5 | Contact page (with brief about summary embedded) | Slices 1–2 | no |
| 5b | Blog framework + first 2-3 live posts | Slices 1–2 | no (blog yes/no resolved 2026-04-26) |
| 6 | Accessibility + Refund Policy + FAQ pages | Slices 1–2 | no (accessibility option B resolved 2026-04-26) |
| 7 | Products listing (browse) | Slices 1–2 | no (URL structure: `/shop/<product-type>/<slug>`) |
| 8 | Individual product pages | Slice 7 | no |
| 9 | Cart + checkout shell (Stripe stubbed until Phase 4) | Slice 8 | no |

**No more standalone Slice 10.** GL's call 2026-04-26: the pricing calculator lives **embedded on the Balloon Twisting + Face Painting service page** (Slice 4). Customers learning about artist services see the price math right there — better placement than a separate /pricing URL.

## Slice 1 — Brand foundation

**Goal:** ERPNext theme installed with LT's color tokens, typography, and spacing scale matching `_resources/STYLE-GUIDE.md`. Verifiable by opening any default ERPNext page and seeing LT's fonts and colors applied.

**Scope:**
- Install DM Serif Display + Raleway via Google Fonts (or self-hosted) on the ERPNext frontend
- Define CSS custom properties for the full color palette (Teal, Soft Gray, Near Black, White, Near White + 7 accent colors + 4 surface tints)
- Apply 8px spacing scale
- Set the default theme overrides for Frappe's website module
- Add a `:focus-visible` outline rule (2px solid Near Black, 2px offset) per accessibility section
- Add `prefers-reduced-motion` media query

**Success criteria:**
1. ERPNext default homepage at `:8081` renders with DM Serif Display headings and Raleway body
2. CSS variables for all palette colors are defined and inspectable in browser dev tools
3. Default Frappe buttons render as Teal-on-white (primary CTAs) — verified visually
4. Keyboard tab through the page shows the focus indicator

## Slice 2 — Header + footer

**Goal:** Site-wide header and footer in place, matching the prior approved visual pattern, navigation structure resolved per GL's decision.

**Blocked on:** Header navigation decision (`.planning/decisions/header-navigation.md`).

**Scope:**
- Header: logo (links to `/`), nav structure per GL's choice, "Sign in" link, mobile hamburger
- Footer: Soft Blue background, brand name in DM Serif Display, columns (Shop / Services / Company / Contact), social icons, accessibility link, copyright
- Newsletter input in footer (deferred wiring — input only for now)
- Tagline "Utah's Balloon Specialists since 1998"

**Success criteria:**
1. Header + footer render on every page at `:8081`
2. Logo links to `/`
3. Nav structure matches GL's decision
4. Footer accessibility link points to `/accessibility`
5. Mobile (375px) header collapses to hamburger; footer columns stack vertically
6. Tab order through header → main → footer is logical and focus indicators are visible

## Slice 3 — Landing page

**Goal:** Homepage delivers the brand promise in one scroll. Hero, services, featured products, social proof, closing CTA. Style-guide-driven build.

**Partially blocked on:** Real photography sourcing (placeholder slots if photos not available).

**Scope:**
- Hero: split layout (photo left, text panel right), tagline "Make Your Celebration Unforgettable", primary CTA Teal button
- Services snapshot: Balloon Decor / Twisting / Face Painting cards with photos and short copy
- Featured products row (pulls from Phase 1 Slice 7 product data)
- Social proof: "Trusted by Utah's Best Since 1998" with photo strip
- Closing CTA section: "Make Your Celebration Unforgettable" headline, two CTAs (Shop / Contact)
- Schema.org LocalBusiness markup with service area (4 counties)
- OpenGraph + Twitter card meta tags

**Success criteria:**
1. Page renders end-to-end with no layout breaks at 375px and 992px+
2. All copy follows "Quiet Confidence" voice (no exclamation points; present tense)
3. WCAG 2.1 AA contrast on every text element (auto-verified)
4. LocalBusiness JSON-LD is present and validates against schema.org
5. Page title + meta description are unique and descriptive

## Slice 4 — Balloon Twisting + Face Painting service page

**Goal:** Carry forward the prior approved page content + visuals. This was already correct.

**Scope:**
- H1: "Balloon Twisting & Face Painting"
- Two H2 sections: "Face Painting" / "Balloon Twisting"
- "Tell us about your event" CTA (links to /book or contact form)
- "Frequently Asked Questions" section pulling from `_resources/policies/`
- Pricing per artist (no combination discount framing per `pricing-formula.md`)

**Success criteria:**
1. Page reads cleanly at every breakpoint
2. Pricing math is correct (1 hr = $130; +$115/hr after) and "no combination discount" framing is prominent
3. FAQ section uses Question/Answer schema for AEO

## Slice 5 — Contact page (with brief about summary)

**Goal:** Contact page that doubles as the discovery surface for who LT is. Form + brief about + service area + business hours.

**Scope:**
- H1: "Contact us" or similar (style-guide voice: "Tell us what you're imagining")
- Brief about paragraph: 2-3 sentences on who LT is, since 1998, Wasatch Front
- Contact form: Name, Email, Phone, Event Type (select), Event Date, "Tell us about your event" textarea
- Form posts to ERPNext Lead (Phase 2 will wire the form-handler; for now form-action is stubbed)
- Service area display: "Free delivery in Davis, Weber, Salt Lake, and Utah counties"
- Business contact: phone, email, address, hours
- Map embed (Google Maps or OpenStreetMap)

**Success criteria:**
1. Contact form renders with all fields and validation hints
2. Form submission stub returns a confirmation page (no blank screen)
3. Service area copy matches `_resources/policies/service-area.md`
4. LocalBusiness schema includes the address and service area on this page too

## Slice 6 — Accessibility + Refund Policy + FAQ pages

**Goal:** Three legal/policy content pages built from `_resources/policies/`.

**Blocked on:** Accessibility statement decision (`.planning/decisions/accessibility-statement.md`).

**Scope:**
- **Accessibility page:** text per GL's chosen option (A/B/C from the decision brief)
- **Refund Policy page:** plain-language version of the cancellation rules from `legal-interview-answers.md` Part 2C
- **FAQ page:** consolidated questions from `_resources/policies/`:
  - Pricing math + no-combination-discount framing
  - Any-character / theme rules
  - Service area + travel fee
  - Deposit + cancellation policy summary (links to refund page for full)
  - Outdoor weather policy
- FAQ uses Question / Answer schema markup

**Success criteria:**
1. Each page renders with brand styling
2. Refund policy text matches the canonical source in `_resources/policies/`
3. FAQ schema validates against schema.org
4. Accessibility page is itself accessible (screen-reader test)

## Slice 7 — Products listing page

**Goal:** Customer can browse all products on the new ERPNext webshop, filtered by category (per the header-nav decision).

**Blocked on:** Header navigation decision (determines URL structure).

**Scope:**
- Frappe webshop product list page
- Brand styling overrides (the default `oe_product_*` Odoo styling becomes LT's product card pattern)
- Products in 3-column grid on desktop, 2-column on mobile
- Filter sidebar: by category (and by occasion/season if Option B from header-nav decision)
- Each product card: photo, name, price, "View Details" link

**Success criteria:**
1. Listing page renders the actual products in the ERPNext system (need to seed or import a small set first — sub-task)
2. Filter by category works
3. Visual matches brand: white cards on Near White page, photo on top, name in Near Black, hover underline on name
4. Mobile: 2-column grid with no horizontal scroll
5. Page title + meta description are dynamic per category

## Slice 8 — Individual product pages

**Goal:** Customer can view a product, see details, select variants, see correct price, add to cart.

**Scope:**
- Product detail layout: photo gallery on left, info column on right (title, price, variant selector, "Add to cart" button)
- Variant selector with `price_extra` math (e.g., size selection updates displayed price)
- Description section (from Item.description)
- Related products / recently viewed (deferred — placeholder slot)
- Schema.org Product markup for SEO

**Success criteria:**
1. At least 1 multi-variant product can be displayed and the price updates correctly when a variant is selected
2. "Add to cart" button works (cart ends up populated)
3. Product schema validates
4. Mobile: photo, info, CTA stack vertically; touch targets ≥44px

## Slice 9 — Cart + checkout shell

**Goal:** Customer can add to cart, view cart, proceed through checkout to a confirmation page. Stripe is stubbed (real payment integration is Phase 4).

**Scope:**
- Cart page: line items, quantity adjustment, subtotal, "+ Utah sales tax (calculated at checkout)" annotation, primary CTA "Checkout"
- Checkout pages: shipping/event address, contact info, order review, place order
- Order confirmation page
- Payment step: stub a "Payment integration coming soon — order received, we'll be in touch" message instead of a real Stripe form

**Success criteria:**
1. Cart correctly reflects what was added (quantity, price)
2. Cart updates without a full page reload (UX expectation)
3. Checkout reaches a confirmation page without a real payment
4. Order is recorded in ERPNext with status "Pending payment integration"
5. Tax annotation visible in cart per `_resources/policies/tax.md`

## Slice 10 — Pricing calculator (CONDITIONAL)

**Goal:** Customer can play with "how many artists × how many hours" and see the price update in real time. Per-artist line-item math; "no combination discount" framing prominent.

**Decision gate:** include in Phase 1 or defer?

**Scope (if included):**
- Frappe Web Form or custom widget on a `/pricing` page
- Inputs: number of twisters, number of painters, hours per artist
- Output: per-artist line items + subtotal + "+ Utah sales tax (calculated at checkout)" annotation
- "Why no combination discount?" callout per `pricing-formula.md`
- "Get a quote" CTA leading to the contact form pre-filled

**Success criteria:**
1. Math matches `_resources/policies/pricing-formula.md`
2. Subtotal updates as inputs change without a full reload
3. Page passes WCAG 2.1 AA (the inputs need labels, the result needs `aria-live`)

## Cross-cutting Phase 1 expectations

These apply to every slice — not separate work items:

- **Voice:** Quiet Confidence on every visible string. See `_resources/STYLE-GUIDE.md` voice section.
- **Loud failure:** every form (contact, booking-stub, cart, checkout) shows a real error message on failure, never a blank screen. Failures log at ERROR level with the payload (PII-safe).
- **Mobile-first:** 375px is the design starting point. Desktop enhances.
- **Accessibility:** WCAG 2.1 AA non-negotiable per the style guide. Every slice gets an automated accessibility scan + manual keyboard test before declaring done.
- **SEO baseline:** unique title + meta description per page, semantic HTML, schema.org markup where applicable, OpenGraph + Twitter cards.

## All Phase 1 decision gates resolved 2026-04-26

| Slice | Was blocked on | Resolution |
|---|---|---|
| 2 (header) | Header navigation decision | **Option B** — single What-We-Make + occasion landing pages |
| 3 (landing) | Real photography sourcing | **Placeholders generated** — `_resources/images/home-*.png` |
| 5b (blog) | Blog presence in Phase 1? | **Yes** — ship framework + live posts |
| 6 (accessibility) | Accessibility statement decision | **Option B** — brief intent-only + actually meeting AA |
| 7 (products) | Header navigation; products to seed | URL structure: `/shop/<product-type>/<product-slug>`. Seed catalog: 6 products matching `_resources/images/product-*.png` |
| 10 (pricing calc) | Yes/no decision | **Awaiting explanation** — GL asked for more info before deciding |

**All slices are unblocked except Slice 10 (pricing calc — awaiting GL's call after explanation).**

---
*Draft v1 — 2026-04-26. Refines as slices complete.*
