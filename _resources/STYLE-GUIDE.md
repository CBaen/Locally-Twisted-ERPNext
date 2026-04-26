# Locally Twisted — Design System & Style Guide

**Version:** 2.1
**Last Updated:** 2026-02-12 (originally drafted for an earlier platform attempt; design decisions are platform-agnostic and apply to the current ERPNext build)
**Primary Viewport:** Mobile-first (375px base)

---

## Design Principles

1. **Photography is the star.** The website is a frame — balloons bring the color.
2. **Color is used sparingly.** Thin bands, slider panels, input tints — not chunky blocks.
3. **Teal is earned.** It only appears as the solid fill on CTA buttons.
4. **White space dominates.** Most of the page is white. Color accents create rhythm.
5. **Soft, never harsh.** No pure black text. No loud backgrounds. Everything breathes.
6. **Mobile-first, always.** 375px is the starting point. Desktop enhances.

---

## Color System

### Core Palette

| Name | Hex | Category |
|------|-----|----------|
| Teal | #008080 | Interactive |
| Soft Gray | #595A5C | Body text |
| Near Black | #1A1A1A | Headings, emphasis |
| White | #FFFFFF | Content, cards |
| Near White | #FBFBFB | Page background |

### Accent Palette (backgrounds, bands, slider panels)

| Name | Hex | Temperature |
|------|-----|-------------|
| Blush | #F4DFD7 | Warm |
| Soft Lemon | #F9F871 | Warm |
| Lime Pastel | #B8FF9E | Warm-neutral |
| Seafoam | #88FED0 | Cool-neutral |
| Aqua | #80F5F3 | Cool |
| Sky Cyan | #A0E9FF | Cool |
| Soft Blue | #C3DCF3 | Cool |

### Surface Tints (inputs, menus, subtle backgrounds)

Very light versions of the accent palette for form fields, search bars, dropdown menus, and mega menu backgrounds. These replace plain white to add warmth.

| Name | Hex | Derived from | Usage |
|------|-----|-------------|-------|
| Blush Tint | #FBF5F2 | Blush | Search bars, newsletter inputs, mega menu bg |
| Blue Tint | #EEF4FB | Soft Blue | Form inputs, dropdown backgrounds |
| Mint Tint | #EEFEF5 | Seafoam | Success-adjacent surfaces |
| Lemon Tint | #FDFDE3 | Soft Lemon | Highlight backgrounds, promo bars |

---

## Color Usage Rules

### Teal (#008080) — Solid CTA Buttons Only

| DO | DON'T |
|----|-------|
| Solid-fill CTA buttons (Contact Us, Shop Now, Add to Cart) | Text of any kind (links, labels, headings) |
| — | Button borders or outlines |
| — | Section backgrounds |
| — | Decorative fills or circles |
| — | Form focus rings or borders |
| — | Any non-button element |

**The rule:** Teal appears ONLY as the solid fill on standout CTA buttons. Never as text, never as a border, never as an outline. One color, one job.

### Soft Gray (#595A5C) — Body Text

| DO | DON'T |
|----|-------|
| All body paragraphs | Headings (use Near Black) |
| Descriptions, captions | Buttons |
| Form labels | Backgrounds |
| Fine print | — |

**Why not pure black?** Softer on the eyes. Feels warmer. Contrast on white: ~7:1 (passes WCAG AA).

### Near Black (#1A1A1A) — Headings & Emphasis

| DO | DON'T |
|----|-------|
| H1, H2, H3 headings | Body paragraphs (use Soft Gray) |
| Bold emphasis text | Backgrounds in light mode |
| Navigation labels | — |
| Footer headings | — |

### Accent Colors — Thin Bands, Panels, and Tints

**How to use accent colors (ALL of them follow these rules):**

| DO | DON'T |
|----|-------|
| Thin horizontal bands between sections | Full-height section backgrounds |
| Carousel/slider text panels (partial width) | Large chunky blocks of color |
| Input field and search bar backgrounds (use tints) | Card backgrounds (use white) |
| Mega menu backgrounds (use tints) | Competing with photography |
| Text color on dark backgrounds (WCAG permitting) | Text on light backgrounds (fails contrast) |
| Small accent elements (tags, badges, pills) | — |

**Thin bands:** A colored strip 40–80px tall, not a full section. Used as visual dividers or accent separators between white content areas.

**Slider panels:** Like in the hero carousel — the text panel gets a color, not the full section. Photo fills one side, color panel fills the other.

**Tinted surfaces:** Form inputs, search bars, and dropdown menus use surface tints (see table above) instead of plain white. This adds subtle warmth.

### Colors as Text

Accent colors CAN be used as text when the background provides enough contrast:

| Color as text | Works on | Contrast | Usage |
|---------------|----------|----------|-------|
| Soft Blue #C3DCF3 | Near Black bg, Dark Surface | 8.5:1 | Dark mode text accents |
| Aqua #80F5F3 | Near Black bg | 11:1 | Dark mode highlights |
| Seafoam #88FED0 | Near Black bg | 11.5:1 | Dark mode highlights |
| Lime Pastel #B8FF9E | Near Black bg | 12:1 | Dark mode highlights |
| Soft Lemon #F9F871 | Near Black bg | 12.5:1 | Dark mode highlights |

**Rule:** None of the accent colors work as text on white or light backgrounds — they fail contrast. Only use them as text on dark surfaces.

### Section Background Pattern

White dominates. Color is the exception, not the rule.

```
White content → thin color band → White content → slider with color panel → White content → thin color band → ...
```

**Rules:**
- Most sections sit on white or near-white
- Color appears as thin bands (40–80px) separating sections
- Color appears as partial panels in sliders/carousels
- Color appears as tinted surfaces in inputs and menus
- Never stack two different colored sections back-to-back
- Full-width colored backgrounds are rare — reserve for trust bars and footers only

---

## Typography

### Fonts

| Role | Font | Fallback | Weight |
|------|------|----------|--------|
| Headings | DM Serif Display | Georgia, serif | 400 |
| Body | Raleway | system sans-serif | 300, 400, 500, 600, 700 |

### Type Scale

| Level | Mobile (375px) | Desktop (992px+) | Font | Color | Usage |
|-------|---------------|-------------------|------|-------|-------|
| H1 | 1.75rem (28px) | 3rem (48px) | DM Serif Display | Near Black | Page hero titles |
| H2 | 1.5rem (24px) | 2.25rem (36px) | DM Serif Display | Near Black | Section headings |
| H3 | 1.25rem (20px) | 1.75rem (28px) | DM Serif Display | Near Black | Card titles |
| H6 | 0.875rem (14px) | 1rem (16px) | Raleway 600 | Near Black | Labels |
| Body | 1rem (16px) | 1.125rem (18px) | Raleway 400 | Soft Gray | Paragraphs |
| Small | 0.75rem (12px) | 0.8125rem (13px) | Raleway 400 | Soft Gray | Captions |

### Typography Rules

- Headings: Near Black (#1A1A1A)
- Body text: Soft Gray (#595A5C) — never pure black
- Left-align all body text, never justify
- Line length: 40–60 characters per line on desktop
- Don't skip heading levels

---

## Spacing

All spacing uses **8px increments**.

| Token | Mobile | Desktop | Usage |
|-------|--------|---------|-------|
| Section padding | 2rem (32px) | 4–5rem (64–80px) | Top/bottom of white content sections |
| Thin band height | 40–60px | 60–80px | Colored accent strips |
| Card padding | 1rem (16px) | 1.5rem (24px) | Internal card spacing |
| Element gap | 0.75rem (12px) | 1rem (16px) | Between heading and paragraph |
| Button padding | 0.75rem 1.5rem | 0.875rem 2rem | Internal button spacing |

---

## Components

### Buttons

| Type | Background | Text | Border | Usage |
|------|-----------|------|--------|-------|
| Primary | Teal (#008080) | White | none | Main CTAs (Contact Us, Shop Now, Add to Cart) |
| Secondary | transparent | Near Black | 1px Soft Blue (#C3DCF3) | Supporting actions (Read More, View Details) |
| Outline light | transparent | Soft Gray | 1px Soft Gray | Tertiary actions, form submits on colored bg |

**Rules:**
- One primary button per section maximum
- All buttons: 44px minimum height (touch target)
- Mobile: full-width stacked. Desktop: inline side-by-side.
- "Read More" and "View Details" are always secondary (outlined), never primary.

### Form Inputs & Search Bars

- Background: Surface tint (Blush Tint #FBF5F2 or Blue Tint #EEF4FB), NOT plain white
- Border: subtle, 1px light gray or none
- Focus state: Soft Blue border/ring (#C3DCF3)
- Placeholder text: lighter gray
- Rounded corners to match brand softness

### Cards (Product/Category)

- White background on Near White page
- Subtle shadow or light border
- Photo on top, text below
- Category name text in Near Black (underlined on hover)
- Rounded corners (0.5rem)

### Logo

- Always links to homepage (`/`)
- Odoo's `placeholder_header_brand` provides this by default — never override or unwrap the anchor

### Hero Carousel

- Split layout: photo left, text panel right
- Text panel uses an accent color (varies per slide — Soft Blue, Blush, etc.)
- Text panel is a partial-width panel, not a full-width background
- DM Serif Display for headline
- Navigation dots and arrows visible
- Touch-swipe enabled on mobile
- Auto-advance: 5+ seconds per slide

### Trust/Value Bar

- Thin Soft Blue band (not a chunky full section)
- Custom blush-toned SVG illustrations (64x64 viewBox: #F4DFD7 fill, #D4A899 mid, #B8877A outline)
- Titles use `.s_lt_trust_title` (not heading elements), descriptions use `.s_lt_trust_desc`
- Horizontal on desktop, 2x2 grid on mobile
- All text in Near Black (for contrast on Soft Blue)

### Mega Menu / Dropdowns

- Background: Surface tint (Blush Tint or Blue Tint)
- Active tab/category: Near Black text (bold)
- Category thumbnails: circular, with real product photos
- Soft Gray body text

### Footer

- Soft Blue (#C3DCF3) background
- Column titles use `.s_lt_footer_col_title` (not heading elements)
- Brand name uses `.s_lt_footer_brand` with DM Serif Display
- Body text and links in Near Black (for contrast on Soft Blue)
- Social media icons in brand colors (44px touch targets)
- Accessibility link in copyright bar

---

## Photography

- **Product photos are the color.** The site frames them, never competes.
- Natural, well-lit balloon photography
- Show balloons in real settings (events, homes, venues)
- Utah locations when possible
- No heavy filters or saturation — let the balloons speak

### Image Specs

| Context | Aspect Ratio | Min Width | Format |
|---------|-------------|-----------|--------|
| Hero carousel | 16:9 or 4:3 | 1200px | WebP/JPEG |
| Product card | 1:1 or 4:3 | 600px | WebP/JPEG |
| Category thumbnail | 1:1 (circle) | 400px | WebP/JPEG |

---

## Brand Voice: Quiet Confidence

**Version:** 1.0 — Established 2026-02-14

### What It Is

The Locally Twisted voice is **Quiet Confidence** — the voice of someone who knows they're good and doesn't need to prove it. It's conversational yet intriguing. It invites without pushing. It's warm without performing warmth.

### The Three Rules

**1. Present tense, not promises.**

| Don't | Do |
|---|---|
| "We'll deliver to you!" | "Happily delivering along the Wasatch Front" |
| "We can make custom designs!" | "We make custom designs" |
| "We will bring your vision to life" | "Your vision, our hands" |

Present tense says *this is who we are*, not *this is what we'll do if you hire us*. It removes the transaction. They're not hiring a vendor. They're meeting a maker.

**2. Invite, never push.**

| Don't | Do |
|---|---|
| "Book now!" | "What We Make" |
| "Check out our products!" | "Want to see?" |
| "Don't miss our holiday specials!" | "Something for every celebration" |
| "Call for a free quote!" | "Tell us what you're imagining" |

An invitation respects the other person's autonomy. A push assumes they need convincing. Customers are already looking for balloons — they don't need to be sold. They need to feel welcomed.

**3. Warm, not performing.**

| Don't | Do |
|---|---|
| "We LOVE what we do!!!" | "Every detail matters" |
| "We're SO passionate about balloons!" | "Making celebrations unforgettable since 1998" |
| "Delivering joy to your doorstep!" | "Happily delivering along the Wasatch Front" |
| "Making memories that last a lifetime!" | "Made with love" |

Performing warmth is exhausting to read and feels fake. Real warmth is understated. "Happily delivering" works because the word "happily" does all the work quietly — it tells you they enjoy it without screaming about it.

### Brand Archetype: The Creator

Based on Jung's 12 archetypes used in brand strategy, Locally Twisted is **The Creator**:

- Makes beautiful things by hand
- Values self-expression and imagination
- Shares work with quiet pride
- Motto: "If you can imagine it, it can be made"
- Brands in this family: Anthropologie, Etsy, Crayola, Lego

This fits because balloon art IS creation. Every piece is unique. The work speaks for itself.

### Copy Examples

**Homepage hero:**
- No: "Utah's #1 Balloon Company — Book Today!"
- Yes: "We make celebrations unforgettable."

**Category page intro:**
- No: "Check out our amazing holiday balloon packages!"
- Yes: "Something for every season."

**Product description:**
- No: "This STUNNING balloon arch will WOW your guests! Perfect for any birthday party! Order now and get free delivery!"
- Yes: "Full balloon arch in your choice of colors. Includes delivery, setup, and teardown. Tell us your palette and we'll handle the rest."

**Instagram caption:**
- No: "OMG look at this GORGEOUS arch we just made!! DM us to book yours!! Link in bio!!"
- Yes: "Easter pastels for a backyard brunch. Lavender, mint, blush. Happy Easter from our family to yours."

**Email subject line:**
- No: "Don't miss our AMAZING Mother's Day deals!!!"
- Yes: "Something for Mom."

**404 error page:**
- No: "Oops! Page not found!"
- Yes: "This page floated away. Let's get you back."

---

### Blog Voice — The Kindergarten Teacher

**Version:** 1.1 — Established 2026-04-16

**Scope:** The blog *only* (Behind the Balloons). Homepage, category pages, product descriptions, and all other surfaces keep the standard Quiet Confidence voice above.

#### What It Is

Blog writing is where someone is most likely to arrive confused, worried they'll ask a "dumb" question, or facing a topic they've never thought about before. The blog voice is **compassionate, knowledgeable, and never pretentious** — the voice of a kindergarten teacher talking to a kindergarten student. Warm. Unhurried. Patient with the basics. Trusting the reader to keep up without making them feel they have to.

Quiet Confidence still applies. This is its softer, more patient cousin — used when the reader needs reassurance as much as information.

#### The Four Blog Rules

**1. Lead with reassurance.**
Before the facts, name the worry. "Yes — and we promise it's not as tricky as it sounds." "Totally fine. Most people don't." Start with the answer the reader actually needs first: *you're okay, you can't mess this up, we've got you.*

**2. Teach, don't lecture.**
Explain the *why* behind the *what*. "Here's the thing about latex. It's a natural material — it stretches in the warmth and tightens up in the cold." Short sentences. Then more. No textbook voice. No "therefore" or "consequently." If a kindergarten teacher wouldn't say it to a kindergartener, rewrite it.

**3. Name the jargon, then translate.**
Never assume the reader knows a word. When you use one ("latex," "organic arch," "underinflate"), explain it in the same breath. Lean on specifics the reader can picture — "a 95°F July afternoon in Draper," not "hot conditions." Place names and numbers make the world feel real.

**4. It's art — and that's the through-line.**
Always close toward the feeling, not the sell. "It's art." "You don't need to learn the language before you walk into the studio. That's our job." "Tell us what you're imagining." The blog is where the reader falls in love with the *craft* — let the craft do the convincing.

#### What Not To Do

| Don't | Do |
|---|---|
| "Latex oxidizes faster in dry air." | "Balloons get a little chalky on the surface after a few hours. It's just the latex reacting to the air. It doesn't hurt them." |
| "UV radiation is measurably stronger at elevation." | "Up at elevation, the sun is stronger than at sea level." |
| "The key is understanding how our unique climate affects different types of balloon decor differently." | "The dry air, the altitude, the bright sun — they all matter. But none of it is a mystery once someone walks you through it." |
| "Schedule setup for early morning or late afternoon." | "We set up early morning or late afternoon." |
| "Not all balloon decor is created equal when it comes to outdoor durability." | "Not every kind of balloon decor loves the outdoors." |
| "Absolutely." | "Yes." |

#### The Test

Read the paragraph out loud as if you were sitting cross-legged on the floor of a kindergarten classroom, explaining something to a kid who just asked you a good question. If you sound like a brochure, a textbook, or a LinkedIn post — start over. If you sound like someone who *likes* the person asking — you're there.

#### The Through-Line

Every blog post ends somewhere near "it's art." Not always in those words. Sometimes it's "that's our job," or "we'll translate it into balloons." The reader leaves with the feeling that making something beautiful is a craft someone cares about — and that they're welcome in the room.

### How to Test If Copy Is On-Brand

Ask three questions:

1. **Would I say this to someone at a coffee shop?** If it sounds like a commercial, rewrite it.
2. **Does it invite or push?** If there's an exclamation mark, you're probably pushing.
3. **Is it present tense?** "We make" not "We can make." "Happily delivering" not "We'll deliver."

Yes, yes, yes — it's on-brand.

### Why This Voice Matters

This voice isn't a marketing strategy. It's an extension of who the people behind this brand are — people who believe honest kindness without drama has a genuine warmth that the world needs more of. In a landscape where everyone is shouting for attention, Locally Twisted just makes something beautiful and quietly shares it.

That's the whole brand. That's the whole voice.

---

## Accessibility (WCAG 2.1 AA)

**Standard:** WCAG 2.1 Level AA — the legal baseline for ADA web accessibility claims.

### Color Contrast Requirements

| Context | Minimum Ratio | Example |
|---------|---------------|---------|
| Normal text on white/near-white | 4.5:1 | Soft Gray #595A5C on White = 7:1 (**passes**) |
| Normal text on Soft Blue | 4.5:1 | Near Black #1A1A1A on Soft Blue = 8.5:1 (**passes**) |
| Large text (18px+) on any bg | 3:1 | Soft Gray on Soft Blue = 5.1:1 (**passes**) |
| Headings on white | 4.5:1 | Near Black on White = 16:1 (**passes**) |

**Failing combinations to avoid:**
- Soft Gray on Soft Blue = 5.1:1 (passes for large text only, fails for small text under 18px)
- Any accent color as text on white (all fail)

### Decorative Icons

All Font Awesome icons used as decoration (not conveying information) **must** have `aria-hidden="true"`:

```xml
<i aria-hidden="true" class="fa fa-heart"/>
```

Without this, screen readers announce gibberish characters.

### Heading Hierarchy

- One `<h1>` per page (set by page intro or hero)
- Never skip levels (no h1 then h3)
- Decorative "headings" that don't represent hierarchy use styled `<p>` or `<span>` with classes:
  - `.s_lt_trust_title` — trust bar item titles
  - `.s_lt_category_name` — category circle labels
  - `.s_lt_product_name` — product card names
  - `.s_lt_footer_brand` — footer brand name
  - `.s_lt_footer_col_title` — footer column titles
  - `.h2` (Bootstrap class on `<p>`) — carousel slide headlines (non-first slides)

### Focus Indicators

Every interactive element gets a visible focus ring for keyboard users:

```scss
a:focus-visible, button:focus-visible, .btn:focus-visible, [tabindex]:focus-visible {
    outline: 2px solid $lt-near-black;
    outline-offset: 2px;
}
```

**Rule:** Every `:hover` rule must have a matching `:focus-visible` state.

### Touch Targets

Minimum 44px x 44px for all interactive elements:
- Buttons: enforced by Bootstrap `.btn` padding
- Social icons: 2.75rem (44px) circles
- Footer link spacing: 0.375rem vertical padding per `<li>`
- Category circles: 72px+ diameter

### Motion Preferences

Animations and transitions respect `prefers-reduced-motion: reduce`:

```scss
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        transition-duration: 0.01ms !important;
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
    }
}
```

### Landmarks & Navigation

- Skip-to-content link as first focusable element: `<a href="#wrap" class="visually-hidden-focusable">Skip to main content</a>`
- Main content wrapped in `<div id="wrap" role="main">`
- Carousel: `role="region" aria-roledescription="carousel"` with labeled slides
- Form fieldsets with `<legend>` for grouped inputs
- Required fields marked with `aria-required="true"` and visible `*` indicators

### External Links

Links opening in new tabs must include a screen-reader hint:

```xml
<a href="..." target="_blank" rel="noopener" aria-label="Facebook">
    <i aria-hidden="true" class="fa fa-facebook"/>
    <span class="visually-hidden"> (opens in new tab)</span>
</a>
```

### Duplicate Content

Decorative duplicate content (e.g., crawl animation clones) must be hidden from assistive technology with `aria-hidden="true"`.

### Accessibility Statement

Published at `/accessibility` — describes WCAG 2.1 AA commitment, what we do, known limitations, and contact information. Linked from the footer copyright bar.

---

## Layout Rules

### Symmetry Rule (Even-Count Collections)

When a collection has an even number of items (products, images, buttons, cards), they must always display in **balanced, symmetric rows**. No orphaned items.

| Count | Mobile (375px) | Tablet (768px) | Desktop (992px+) |
|-------|---------------|----------------|-------------------|
| 2 | 2 across or 1+1 stacked | 2 across | 2 across |
| 4 | 2+2 | 2+2 or 4 across | 4 across or 2+2 |
| 6 | 2+2+2 | 3+3 or 2+2+2 | 3+3 or 6 across |
| 8 | 2+2+2+2 | 4+4 or 2+2+2+2 | 4+4 |

**Never:** 3+1, 5+1, 3+3+2 on mobile, or any layout where the last row has fewer items than other rows when a balanced split exists.

**CSS approach:** Use `grid-template-columns: repeat(2, 1fr)` on mobile for even collections. On desktop, ensure column counts divide evenly into the item count.

**Odd counts are exempt** — 3 items as 2+1 or 5 items as 3+2 are acceptable since no perfect split exists.

---

## CSS Conventions

- **Mobile-first only.** Base styles = 375px. Use `min-width` media queries.
- **Never use `max-width` media queries.** Enforced by Stylelint.
- **Breakpoints:** 768px (tablet), 992px (desktop), 1200px (wide)
- **Snippet classes** prefixed with `s_lt_` (e.g., `s_lt_hero`, `s_lt_trust_bar`)

---

## Quick Reference: "What Color Do I Use?"

| I'm building... | Background | Text | Buttons |
|-----------------|-----------|------|---------|
| Hero carousel panel | Any accent color | Near Black | Primary (Teal) |
| Trust/value bar | Soft Blue (thin band) | Soft Gray | — |
| Product grid | White | Soft Gray, Near Black links | — |
| Category section | White | Soft Gray, Near Black links | — |
| CTA section | Accent thin band or white | Soft Gray | Primary (Teal) |
| Footer | Soft Blue | Near Black (links + body) | — |
| Testimonials | White or Blush thin band | Soft Gray | — |
| Search bar | Blush Tint or Blue Tint | Soft Gray | — |
| Form inputs | Blush Tint or Blue Tint | Soft Gray | — |
| Mega menu | Blush Tint or Blue Tint | Soft Gray, Near Black active | — |
| General content | White or Near White | Soft Gray | Secondary (outlined) |
| Dark mode text | Dark bg | Accent colors OK | Teal (brightened) |

---

## Dark Mode Colors (for future implementation)

| Name | Hex | Maps to |
|------|-----|---------|
| Bright Teal | #00A3A3 | Interactive elements (replaces #008080) |
| Deep Warm Brown | #3D2A24 | Warm surfaces (replaces Blush) |
| Near Black | #1A1A1A | Page background |
| Dark Surface | #242424 | Cards and content areas |
| Deep Blue | #1E3A5F | Cool surfaces (replaces Soft Blue) |
| Off White | #F0F0F0 | Body text |
