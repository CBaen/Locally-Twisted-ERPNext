# Phase 1 Plan — Customer Site (Lookbook-Forward, with Small Shop)

> **Stale planning snapshot.** This file is retained as planning history, not as the current work queue. Current route decisions supersede several sections below: `/contact` is the primary inquiry path, `/book` is alias-only, current nav has no Gallery/About/Book Event surface, and completed slice state must be verified against git/files/routes plus `CODING-HANDOFF.md` and `locally-twisted-queue.md`.

**Phase goal (from ROADMAP.md):** A first-time visitor lands on the site, immediately understands LT does custom event balloon decor at the level visible in the portfolio, knows how to inquire for custom work, and can browse a small set of pre-configured themed items if they're shopping for a casual celebration. Jeff sees the result and says *"yes — show this to my next corporate prospect."*

**Off-ramp gate:** if any slice exposes that Frappe / ERPNext can't deliver the visual / UX bar, GL pivots before building further.

**Strategic shape:** lookbook-forward + small shop sidebar. See `.planning/decisions/site-shape.md` for rationale and `_resources/competitor-survey-2026-04-26.md` for the 9 competitor sites that exemplify the pattern.

## Slicing strategy

Phase 1 is sliced into ~14 deliverables. Each slice ends in something visible GL can react to. Slices completed in earlier sessions are marked DONE; remaining slices are listed in priority order.

Build pattern for every new portal page: the meal at `Built_by_Cameron/.claude/capabilities/meals/build-frappe-portal-page.md` is the binding shape. Read approved content first, write controller, write template extending `templates/web.html`, append BEM CSS, smoke-test the form (if any), Playwright at mobile + desktop, hand to GL with hard-refresh instruction.

| # | Slice | State | Surface | Notes |
|---|---|---|---|---|
| 1 | Brand foundation | DONE | Theme CSS via `web_include_css` | `apps/locally_twisted/.../public/css/lt-theme.css` |
| 2 | Header + footer chrome | DONE | Jinja partial overrides | Two-tier desktop + mobile single-row + 3-col footer |
| 4 | BTFP service page (with embedded pricing calculator) | DONE | `/balloon-twisting-and-face-painting` | Form-bearing; carries forward |
| 5 | Contact page | DONE | `/contact` | Form-bearing; AJAX → Lead + Communication |
| 6a | Accessibility statement | DONE | `/accessibility` | Static portal page |
| **3** | **Homepage (lookbook-forward)** | DONE | `/` | The demo-to-Jeff page |
| **7** | **Lookbook** | DONE | `/lookbook` | Full portfolio, organized by event type |
| **8** | **Service category pages** | TODO | `/services/<event-type>` (×5) | Corporate, Weddings, Birthdays, Schools, Seasonal |
| **9** | **Color Chart** | TODO | `/color-chart` | Static reference page |
| **10** | **`/book` form page** | RETIRED | `/book` -> `/contact?intent=quick` | `/contact` is the primary inquiry route; `/book` redirects only |
| **11** | **Small Shop browse + detail** | DONE | `/shop` (webshop default routes) | Sub-$200 themed bouquets + gift items |
| **12** | **Cart + checkout shell** | DONE | webshop default routes | Stripe Checkout Sessions live in test mode |
| **13** | **Refund Policy + FAQ pages** | DONE | `/refund-policy`, `/faq` | Small static portal pages |
| **14** | **Blog framework + 2-3 posts** | TODO (deferrable) | `/blog/...` | "Kindergarten Teacher" voice |

## What changed from the prior PLAN.md (2026-04-26 morning version)

The prior plan had Slices 7–9 as "Products listing / Individual product pages / Cart + checkout" — a full e-commerce surface as the dominant Phase 1 work. The lookbook-forward decision (recorded at `.planning/decisions/site-shape.md`) reshapes those slices:

- The old "Products listing" page becomes the **Lookbook** (Slice 7) — visual portfolio organized by event type, not a product catalog.
- The old "Individual product pages" become the **Service category pages** (Slice 8) — depth by what LT *makes* (decor for corporate / weddings / etc.), not by SKU. These are inquiry-bound, not cart-bound.
- The **small shop** lives at the same webshop URL (`/shop`) but is a deliberate sidebar — sub-$200 pre-configured items only. Configurator UI is explicitly out of scope.
- The **`/book` form** was later retired as a standalone customer surface; `/contact` is the primary inquiry path and `/book` redirects to `/contact?intent=quick`.
- Phase 2 reframes from "build /book" to "form-handling depth" (dedup, ack email, loud-failure audit, monitor alerts).

## Slice 3 — Homepage (lookbook-forward)

**Goal:** First-time visitor lands and immediately understands LT does custom event balloon decor at the level visible in the portfolio. Single primary CTA above the fold: *"Request a Quote."* No featured products, no configurator, no shopping cart in the header above the fold.

**Source content:**
- Hero copy + tagline: review `_resources/STYLE-GUIDE.md` first. The deleted `_resources/design-guide/` synthesis is no longer a valid visual reference because it conflicted with the approved Civic Celebration + Slate Blue/Berry + Brand Direction system. Some copy carries from approved Odoo XML, some is GL-confirmed fresh.
- Hero imagery: from `_resources/images/` (placeholders) until Jeff provides real photography.
- Corporate logos for trust strip: TBD — needs a list of corporate clients Jeff has served (LinkedIn, Microsoft, etc. — Atlanta Balloon Designer's pattern is the reference).

**Scope — page sections (top to bottom):**

1. **Hero** — full-width portfolio image (or rotating carousel if compelling), tagline, single primary CTA: "Request a Quote." No secondary CTA above the fold (no "Shop" button, no "Browse Products"). Pattern source: Partistry Balloons.
2. **Trust strip** — corporate logo wall ("Trusted by …") if Jeff has the client list to support it. Pattern source: Atlanta Balloon Designer / Balloon Emporium.
3. **What we make (services teaser)** — three or four cards (Corporate Events, Weddings, Birthdays, Special Occasions) each linking to its service category page. Photo-led, short copy, no prices.
4. **Featured work (case-study previews)** — 3 case studies linking to the Lookbook. Each with photo + event type + 1-line caption.
5. **About snippet** — 2–3 sentences on who LT is, since 1998, Wasatch Front. (No standalone About page; this snippet replaces it.)
6. **Closing CTA** — "Tell us about your event" with Inquire button. Mirrors the Soulflora pattern of repeated inquiry CTAs.

**Schema/SEO baseline:**
- LocalBusiness JSON-LD with service area (Davis, Weber, Salt Lake, Utah counties)
- OpenGraph + Twitter card meta tags
- Unique title + meta description

**Success criteria:**
1. Page renders end-to-end with no layout breaks at 375px and 992px+
2. Single primary CTA above the fold; no e-commerce affordances above the fold
3. All copy follows "Quiet Confidence" voice (no exclamation points; present tense)
4. WCAG 2.1 AA contrast on every text element (auto-verified)
5. LocalBusiness JSON-LD validates against schema.org
6. Page title + meta description are unique and descriptive
7. **GL viewing the result says "yes — show this to Jeff."**

## Slice 7 — Lookbook (full portfolio)

**Goal:** `/lookbook` — visual heart of the site. All event work organized by event type. Visitor browses by category and clicks into individual case studies.

**Scope:**
- Top-level filter / nav by event type: Corporate, Weddings, Birthdays, Schools, Seasonal.
- Grid or masonry layout, image-led, 3 columns desktop / 2 mobile.
- Each card: photo, event name, year, brief tagline. Clicks into a case study page (or expands inline as lightbox — to be decided in build).
- Real photos from Jeff's archive when available; placeholders from `_resources/images/` otherwise.
- Schema.org ImageGallery / CreativeWork markup for SEO.

**Open question for build:** does each lookbook card open a full case-study page (`/lookbook/<event-slug>`), or does it expand inline as a lightbox? Pattern survey suggests both work; the case-study page approach lets each event have its own URL for sharing. Decide at build time based on how much copy Jeff has for each event.

**Success criteria:**
1. Listing renders at 375px (2-col) and ≥992px (3-col) without horizontal scroll
2. Filter by event type works (URL changes; SEO-friendly per-category pages)
3. Each card has alt text describing the event
4. WCAG 2.1 AA passes on every page in the surface
5. Page-level schema markup validates

## Slice 8 — Service category pages

**Goal:** Five service category pages — `/services/corporate`, `/services/weddings`, `/services/birthdays`, `/services/schools`, `/services/seasonal`. Each tells a visitor "yes, LT does this kind of event well; here's what's possible; ready to talk?"

**Scope (per page):**
- H1: e.g., "Corporate Event Balloon Decor"
- Hero image: type-specific
- 3–5 paragraphs of copy: what LT brings to this category, characteristic installations, scale range, planning lead time
- Featured case studies from this category (linking into the Lookbook)
- Color Chart link ("All 70 colors available — see our Color Chart")
- Inquiry CTA: "Tell us about your event" → `/book` (with category pre-selected via URL param)
- FAQ specific to category (if applicable)

**Success criteria:**
1. Each page renders at 375px and ≥992px without breaks
2. Inquiry CTA pre-fills `/book` with the right event category
3. Each page has unique title + meta description
4. WCAG 2.1 AA on every page
5. Case study cards link cleanly into the Lookbook

## Slice 9 — Color Chart

**Goal:** `/color-chart` — static reference page that satisfies the "what colors are possible?" question without forcing a configurator UI. Visitors see all 70 balloon colors with names; can use the chart in conversation with Jeff.

**Scope:**
- Visual swatch grid (10 columns × 7 rows or similar)
- Each swatch: color sample + color name (e.g., "Hot Pink", "Antique Gold")
- Brief intro paragraph: "All balloon colors LT stocks. For exact color matching to a brand or event palette, share a swatch with us when you inquire."
- Print-friendly stylesheet (so customers can print the chart)
- Inquiry CTA at the bottom

**Source data:** Jeff's existing color list (TBD where this lives — possibly in the Odoo dir as a structured list, or pulled from supplier color cards).

**Success criteria:**
1. Page renders at 375px (≤4 columns) and ≥992px (10 columns) without horizontal scroll
2. Each swatch has color name as alt text + visible label
3. WCAG 2.1 AA contrast on color names (against page background, not against swatch)
4. Print stylesheet renders the grid cleanly on Letter and A4

## Slice 10 — `/book` form page

**Goal:** The primary inquiry conversion path on the site. Form-bearing portal page using the existing 45-field Lead schema in ERPNext. Submission creates a Lead + Communication; visitor sees a confirmation page.

**Source content:** GL designed this form. The field set lives in the existing ERPNext Lead schema (45+ Custom Fields, sectioned, plain-language relabels). The form's structural source is the Odoo `/book` page — but per anti-gl-patterns receipt 2026-04-26, the live `/book` (Odoo `arch_db`) diverged from source XML; cross-check both before final field list. **GL to confirm the canonical field list during build.**

**Scope — page sections (top to bottom):**

1. H1: "Tell us about your event" (or similar — voice review at build time)
2. Brief intro paragraph: 1–2 sentences setting expectations ("share what you have in mind; we'll respond within…")
3. **The form** — sectioned per the Lead schema. Sections to mirror:
   - Contact (name, email, phone)
   - Event basics (type, date, venue, address, time)
   - Services (multi-select with conditional sub-sections per selected service)
   - Decor specifics (per-service detail blocks)
   - Inspiration photos upload (child table)
   - Additional details / questions
4. Submit button (primary CTA color; disabled state during submission)
5. Confirmation page on successful submit — never blank screen on failure (loud-failure rule)

**Implementation pattern:**
- Use the meal at `build-frappe-portal-page.md`
- Form posts via AJAX to a whitelisted controller method (mirrors `/contact` and BTFP)
- Field names match ERPNext Lead Custom Field names natively (no legacy name-mapping)
- File upload (Inspiration Photos) wired to ERPNext attachment system
- Loud-failure: error states show real messages; exceptions logged at ERROR level with sanitized payload

**Success criteria:**
1. Submission creates a Lead in ERPNext with every field populated correctly — verified by completing one of each branch (decor, twisting, painting, delivery-only, package, other)
2. Inspiration photo upload attaches to the Lead correctly
3. Customer sees a confirmation page (never a blank screen) — loud-failure verified
4. Form fields match the existing Lead schema 1:1 — no orphan fields, no missing fields
5. Form passes WCAG 2.1 AA: labels on every input, error messages associated with fields, keyboard navigation
6. Mobile (375px): form fields stack vertically; touch targets ≥44px
7. **Phase 2 will add:** Contact dedup (link to existing Contact by email/phone or create new) + acknowledgment email automation + monitor alerts. Phase 1 ships the form + the Lead creation; Phase 2 adds the depth around it.

## Slice 11 — Small Shop (browse + detail)

**Goal:** Webshop-driven browse + detail surface for ~6–12 sub-$200 pre-configured items. **No configurator.** Customer can pick a themed bouquet (Lilo & Stitch, Marvel, Harry Potter, etc.), see what's in it, and add to cart.

**Scope:**
- Frappe webshop product list at `/shop` (or whatever the webshop default route is)
- Brand-styled overrides for product cards (white card on Near White page, photo on top, name in Near Black, price below, hover state)
- 3-col grid desktop / 2-col mobile
- Product detail page: photo gallery, name, price, what's-included description, "Add to cart" button. **No variant selector** beyond simple options like "deliver" vs "pickup" if applicable.
- ~6–12 Website Items seeded for first ship: themed birthday bouquets (Lilo & Stitch, Marvel, Harry Potter, generic kids, generic adult), simple yard signs, gift bouquets

**Implementation:**
- Webshop primitives (we already have Webshop installed and bundles compiling)
- Customization via `templates/pages/product.html` override (per `frappe-conventions.md` "Customizing webshop pages" map)
- No new portal-page meal here — this is webshop's territory

**Success criteria:**
1. `/shop` renders the seeded items with brand styling (not default webshop look)
2. Item detail page renders with photo, description, price, "Add to cart"
3. Cart fills correctly when items are added
4. Mobile: 2-col grid with no horizontal scroll
5. Each item has unique title + meta description for SEO

## Slice 12 — Cart + checkout shell

**Goal:** Customer can add to cart, view cart, proceed through checkout to a confirmation. Stripe is stubbed (real payment integration is Phase 4).

**Scope:**
- Cart page: line items, qty adjustment, subtotal, "+ Utah sales tax (calculated at checkout)" annotation, "Checkout" CTA
- Checkout pages: shipping/event address, contact info, order review, place order
- Order confirmation page
- Payment step: stub a "Payment integration coming soon — order received, we'll be in touch" message instead of a real Stripe form

**Success criteria:**
1. Cart correctly reflects what was added (qty, price)
2. Cart updates without a full page reload
3. Checkout reaches a confirmation page without a real payment
4. Order is recorded in ERPNext with status "Pending payment integration"
5. Tax annotation visible per `_resources/policies/tax.md`

## Slice 13 — Refund Policy + FAQ pages

**Goal:** Two small legal/policy content pages built from `_resources/policies/`.

**Scope:**
- **Refund Policy:** plain-language version of the cancellation rules from `legal-interview-answers.md` Part 2C
- **FAQ:** consolidated questions from `_resources/policies/`:
  - Pricing math + no-combination-discount framing
  - Any-character / theme rules (per `theme-and-character-rules.md`)
  - Service area + travel fee
  - Deposit + cancellation policy summary (links to refund page for full)
  - Outdoor weather policy
- FAQ uses Question / Answer schema markup for AEO

**Implementation:** Each is a static portal page via the meal pattern. ~15–30 minutes of mechanical work each.

**Success criteria:**
1. Each page renders with brand styling
2. Refund policy text matches the canonical source in `_resources/policies/`
3. FAQ schema validates against schema.org
4. Each page has unique title + meta description

## Slice 14 — Blog framework + 2–3 posts

**Goal:** Frappe blog framework live with 2–3 first posts in the "Kindergarten Teacher" voice (per the style guide). Deferrable — can ship before or after the demo to Jeff depending on bandwidth.

**Scope:**
- Frappe `Blog Post` DocType configured
- Brand-styled blog post template (`templates/blog_post.html` override)
- Blog index page (`/blog`)
- 2–3 first posts on topics from the style guide: introductory educational content, balloon-twisting how-to behind-the-scenes, color theory for events
- RSS feed
- Schema.org BlogPosting markup

**Success criteria:**
1. Blog index renders with the first 2–3 posts
2. Individual blog post pages render with brand styling and schema
3. Voice matches "Kindergarten Teacher" per `_resources/STYLE-GUIDE.md`
4. RSS feed validates

## Cross-cutting Phase 1 expectations

These apply to every slice — not separate work items:

- **Voice:** Quiet Confidence on every visible string (Kindergarten Teacher in blog only). See `_resources/STYLE-GUIDE.md` voice section.
- **Loud failure:** every form (contact, book, cart, checkout) shows a real error message on failure, never a blank screen. Failures log at ERROR level with sanitized payload.
- **Mobile-first:** 375px is the design starting point. Desktop enhances.
- **Accessibility:** WCAG 2.1 AA non-negotiable per the style guide. Every slice gets an automated accessibility scan + manual keyboard test before declaring done.
- **SEO baseline:** unique title + meta description per page, semantic HTML, schema.org markup where applicable, OpenGraph + Twitter cards.
- **Inquiry CTA repetition:** every service surface ends with the inquiry CTA (Soulflora pattern). Don't bury it.
- **Hard-refresh in handoff to GL:** every CSS-touching change handed to GL with explicit hard-refresh instruction (anti-gl-pattern receipt 2026-04-26).

## Open questions / pending GL input

- **Corporate client list for the homepage trust strip** (Slice 3). Atlanta Balloon Designer / Balloon Emporium pattern. Need real names with Jeff's permission.
- **Color Chart source data** (Slice 9). Where does the canonical 70-color list with names live? Possibly Odoo dir, possibly supplier card.
- **`/book` field-list canonical source** (Slice 10). Confirm with GL during build whether to mirror the live Odoo `/book` form (curl the public URL + cross-check) or work directly from the ERPNext Lead Custom Field schema.
- **Lookbook card depth** (Slice 7). Do cards open full case-study pages (each event gets a URL) or lightbox in place? Decide at build based on how much per-event copy Jeff has.
- **Real photography arrival timing.** Affects Slices 3, 7, 8. Placeholders ship until photos arrive; real photos drop in via re-encode, not redesign.
- **Blog topic list and first-post copy** (Slice 14). Voice is set; topics need GL.

---
*Draft v2 — 2026-04-26. Replaces the prior v1 (which had Slices 7–9 as a full e-commerce surface). Refines as slices complete.*
