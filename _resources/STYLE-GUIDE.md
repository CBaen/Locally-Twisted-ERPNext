# Locally Twisted - ERPNext/Frappe Style Guide

**Version:** 3.0
**Last Updated:** 2026-05-02
**Build Target:** ERPNext v15.105.0 + Frappe v15 / Webshop
**Primary Viewport:** Mobile-first, 375px base

This is the canonical style guide for the current Locally Twisted ERPNext build.
The older Odoo guide is reference material only. Claude-era notes and design
competition files can provide useful history, but they are not authority unless
their claims are verified against this repo and the running ERPNext site.

Use this guide when writing customer-facing copy, building Frappe/Jinja pages,
styling Webshop surfaces, reviewing visual work, or briefing GPT/Codex-style
coding agents.

---

## Quick Rules

1. **Photography is the star.** The website frames the work; balloons bring the color.
2. **Teal is earned.** `#008080` appears only as solid fill on primary CTA buttons.
3. **White space dominates.** Most surfaces are white or near-white.
4. **Accent color is light-touch.** Use it for thin bands, panels, tints, and small chips.
5. **Quiet confidence.** Copy invites, explains, and states facts without hype.
6. **ERPNext first.** Work with Frappe/Webshop templates, hooks, and route rules.
7. **Verify visible work.** Do not claim a route, layout, or visual state works without checking it.

---

## Agent Usage

### For GPT/Codex Agents

- Treat this file as the brand and UI source of truth.
- Treat old Odoo, Claude, handoff, and design-competition files as claims to verify.
- Do not copy implementation language from the Odoo guide into ERPNext work.
- When this file conflicts with current verified route/form decisions, check
  `locally-twisted-decisions.md` and the running site before editing.
- Before customer-facing frontend edits, read:
  - `_resources/design-guide/README.md`
  - `_resources/design-guide/synthesis/voice.md`
  - `_resources/design-guide/synthesis/mood.md`
  - `_resources/design-guide/synthesis/rationale.md`
- The design guide is taste calibration, not a mandate to copy Next.js TSX into Frappe.

### Frappe/ERPNext Implementation Rules

- Theme CSS lives in the `locally_twisted` app and is registered through `web_include_css`.
- Header/footer customization should use Jinja partial overrides.
- Static pages should live in `apps/locally_twisted/locally_twisted/www/`.
- Webshop pages should use Frappe/Webshop hooks, route rules, API wrappers, and template overrides.
- Avoid `head_html` CSS injection.
- Avoid `!important` chains. The known exception is the contained `.product-code` hide for Webshop's compiled product-card JS.
- After Jinja, CSS, or Web Page edits, run `python scripts/dev/clear_website_cache.py`.
- Before declaring visual work done, run the layout-fit gate and inspect desktop/mobile screenshots.

---

## Current Customer Surfaces

- `/contact` is the canonical inquiry page.
- `/book` is legacy compatibility only and redirects to `/contact?intent=quick`.
- Customer CTAs should normally point to `/contact`, not `/book`.
- `/balloon-twisting-and-face-painting` is an editorial service page that leads to contact.
- `/privacy` and `/terms-of-service` are static Frappe routes for Stripe readiness.
- `/accessibility` is the public accessibility statement.
- `Plan by Occasion` is product-discovery navigation, not a shortcut to inquiry.

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

1. **Photography is the star.** The site is a quiet frame for real balloon work.
2. **Color is used sparingly.** Thin bands, text panels, input tints, and chips only.
3. **Teal is earned.** One color, one job: primary CTA fill.
4. **Soft, never harsh.** No pure black body text. No loud backgrounds.
5. **Mobile-first, always.** Start at 375px; desktop enhances.
6. **Specificity beats salesmanship.** Details, service areas, process, and constraints build trust.

---

## Color System

### Core Palette

| Name | Hex | Role |
|---|---:|---|
| Teal | `#008080` | Primary CTA button fill only |
| Soft Gray | `#595A5C` | Body text |
| Near Black | `#1A1A1A` | Headings, nav labels, emphasis |
| White | `#FFFFFF` | Content and card surfaces |
| Near White | `#FBFBFB` | Page background |

### Accent Palette

Use accents for thin bands, partial panels, tints, and small UI elements. Do not
use them as full-section backgrounds unless the section is a trust bar or footer.

| Name | Hex | Temperature | Primary Use |
|---|---:|---|---|
| Blush | `#F4DFD7` | Warm | Bands, soft SVG illustration fills |
| Soft Lemon | `#F9F871` | Warm | Highlights and occasional bands |
| Seafoam | `#88FED0` | Cool-neutral | Bands and success-adjacent accents |
| Sky Cyan | `#A0E9FF` | Cool | Bands and small accents |
| Soft Blue | `#C3DCF3` | Cool | Footer, trust/value bar, secondary borders |

Removed colors: Aqua `#80F5F3` and Lime Pastel `#B8FF9E` were removed on
2026-04-29 because they read too candy-pop for the current LT brand.

### Surface Tints

| Name | Hex | Derived From | Use |
|---|---:|---|---|
| Blush Tint | `#FBF5F2` | Blush | Search bars, newsletter inputs, menu backgrounds |
| Blue Tint | `#EEF4FB` | Soft Blue | Form fields and dropdowns |
| Mint Tint | `#EEFEF5` | Seafoam | Success-adjacent surfaces |
| Lemon Tint | `#FDFDE3` | Soft Lemon | Highlight backgrounds and promo bars |

### Color Rules

- Teal appears only as solid fill on primary CTA buttons.
- Do not use teal for links, borders, focus rings, headings, icons, or decorative fills.
- Body text is Soft Gray on light surfaces.
- Headings and emphasis are Near Black.
- Accent colors are not body text on white or near-white; they do not pass contrast.
- Near Black text works on Soft Blue, Blush, and most light accent bands.
- Never stack two different colored full-width sections back-to-back.

Pattern:

```text
White content -> thin accent band -> White content -> image + partial color panel -> White content
```

---

## Typography

| Role | Font | Fallback | Weight |
|---|---|---|---|
| Headings | DM Serif Display | Georgia, serif | 400 |
| Body/UI | Raleway | system sans-serif | 300, 400, 500, 600, 700 |

### Type Scale

| Level | Mobile | Desktop | Font | Color | Use |
|---|---:|---:|---|---|---|
| H1 | 28px | 48px | DM Serif Display | Near Black | Page hero titles |
| H2 | 24px | 36px | DM Serif Display | Near Black | Section headings |
| H3 | 20px | 28px | DM Serif Display | Near Black | Card/service titles |
| Label | 14px | 16px | Raleway 600 | Near Black | Labels and short UI headings |
| Body | 16px | 18px | Raleway 400 | Soft Gray | Paragraphs |
| Small | 12px | 13px | Raleway 400 | Soft Gray | Captions and fine print |

Rules:

- Left-align body text.
- Do not justify text.
- Keep desktop line length around 40-60 characters.
- Do not skip heading levels.
- Do not scale font sizes with viewport width.
- Letter spacing should be `0` unless a specific existing component requires otherwise.

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
- Stable fixed-format UI needs stable dimensions: boards, grids, icon buttons, counters, swatches, and form controls should not shift when states change.
- Text must not overflow or overlap on 320px, 375px, tablet, or desktop widths.
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

## Components

### Buttons

| Type | Background | Text | Border | Use |
|---|---|---|---|---|
| Primary | Teal | White | none | Main CTAs: Contact Us, Add to Cart, Continue |
| Secondary | Transparent | Near Black | 1px Soft Blue | Supporting actions |
| Tertiary | Transparent | Soft Gray | 1px Soft Gray | Low-emphasis actions |

Rules:

- One primary button per section unless a transactional Webshop flow requires more.
- Minimum touch target is 44px by 44px.
- Mobile buttons can stack full-width; desktop buttons can sit inline.
- "Read More" and "View Details" are secondary, not primary.

### Forms

- Field backgrounds use Blush Tint or Blue Tint, not plain white.
- Borders are subtle: light gray or none.
- Focus states use a visible Near Black outline or Soft Blue border/ring.
- Placeholder text is lighter gray.
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
- Card names use Near Black.
- Body copy uses Soft Gray.
- Border radius: 8px unless an existing Frappe/Webshop component requires otherwise.

### Header And Navigation

- Logo/brand element always links to `/`.
- Primary nav order is currently:
  - Shop Balloon Decor
  - Plan by Occasion
  - Balloon Twisting & Face Painting
  - FAQ
  - Blog
  - Search
- The utility area keeps the main `Contact Us` CTA.
- Do not add Gallery, About, Book an Event, or What We Make links unless scope is reopened.
- Occasion links should route to product/category discovery pages, not `/contact?occasion=...`.

### Footer

- Background: Soft Blue `#C3DCF3`.
- Text and links: Near Black.
- Brand name can use DM Serif Display.
- Social icons need 44px targets.
- Footer should link to `/privacy`, `/terms-of-service`, and `/accessibility`.

### Trust/Value Bar

- Soft Blue band, not a chunky section.
- Titles use styled non-heading elements when they are decorative/repeated.
- Descriptions use Near Black or sufficiently contrasting text.
- Custom blush-toned SVG illustrations may use:
  - Fill: `#F4DFD7`
  - Mid: `#D4A899`
  - Outline: `#B8877A`

### Hero / Featured Media

- Prefer real photography.
- The photo carries the argument; copy annotates.
- Text may sit in a partial color panel or a carefully legible overlay, but avoid fighting the image.
- If using carousel behavior, include visible controls, touch support, and at least 5 seconds per slide.

---

## Photography

- Use natural, well-lit balloon photography.
- Show balloons in real settings: events, homes, venues, storefronts, schools, churches, and Utah locations where possible.
- Avoid heavy filters, dark crops, blurred stock-like atmosphere, and over-saturation.
- Product photos are the color; the site should not compete with them.
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

Reference mood: considered, unhurried, earned, luminous, warm.

---

## Accessibility

Target WCAG 2.1 AA.

### Contrast

| Context | Minimum | Approved Example |
|---|---:|---|
| Normal text | 4.5:1 | Soft Gray on White |
| Large text | 3:1 | Near Black on accent bands |
| UI controls | 3:1 | Near Black focus outline |

Avoid:

- Accent color text on white or near-white.
- Soft Gray small text on Soft Blue.
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
3. Run `npm run test:layout-fit` for customer-site layout fit.
4. Capture and inspect desktop and mobile screenshots.
5. Verify the actual route or user flow, not a proxy page.

Useful commands:

```powershell
python scripts/dev/clear_website_cache.py
npm run test:layout-fit
python scripts/verify/nav_ia.py
python scripts/verify/contact_service_logic.py --base-url http://localhost:8081
python scripts/verify/contact_prefill.py --base-url http://localhost:8081
```

Do not say "working", "fixed", "ready", or "verified" unless the relevant command,
route check, database check, or screenshot review actually happened.

---

## Quick Reference: What Color Do I Use?

| Building | Background | Text | Button |
|---|---|---|---|
| Hero/feature panel | Accent panel or image | Near Black / White if verified | Primary Teal |
| Trust/value bar | Soft Blue | Near Black | None |
| Product grid | White cards on Near White | Soft Gray, Near Black links | Transactional only |
| Category section | White/Near White | Soft Gray, Near Black links | Secondary |
| Contact form | White with tinted fields | Soft Gray labels, Near Black headings | Primary Teal |
| CTA section | White or thin accent band | Soft Gray / Near Black | Primary Teal |
| Footer | Soft Blue | Near Black | None |
| Search/menu | Blush Tint or Blue Tint | Soft Gray, Near Black active | None |
| General content | White/Near White | Soft Gray body, Near Black headings | Secondary |

---

## Future / Not Yet Canonical

Dark mode, printed collateral, social templates, signage, and expanded photo art
direction are not fully specified in this file yet. Do not invent those systems
as if they are approved. Add them deliberately when that scope opens.
