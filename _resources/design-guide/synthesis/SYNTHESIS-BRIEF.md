# Locally Twisted — Hybrid Synthesis Brief

**Date:** 2026-04-26
**Project:** zoho-locally-twisted (decision project for Locally Twisted)
**Status:** Final design synthesis — this becomes the build target.

Guiding Light reviewed the 7 design competition outputs and chose a **hybrid synthesis** rather than a single winner. This brief specifies what to take from where, all rendered in the **existing LT visual language** (NOT any contest designer's palette/typography).

---

## The Mandate

Translate three contributing designers' best ideas into Locally Twisted's existing visual system. **The visual language is the existing LT brand. The structural ideas are the contest contributions.** Do not import the contest designers' palettes or fonts. Import their layout decisions, configurator UX, navigation/IA patterns, and copy approach.

---

## What to Take From Where

| Element | Source | What specifically |
|---|---|---|
| **Conceptual frame** (overall site structure + density + intentionality) | **Designer 3** ("The Studio Archive") | Editorial/gallery-catalog structure; URL-prefill inquiry-builder pattern (configurator selections pass into the inquiry form via query params); intentional density (no excessive whitespace, every section earns its space) |
| **Lookbook page** | **Designer 7** ("The Atelier") | Mood-first 4-step configurator (mood → family colors → style → scale); no-text-on-images structural rule; portfolio grid with category filter; "Something else in mind?" inquiry redirect at bottom |
| **Shop page** | **Designer 5** ("The Studio") | D5's shop page pattern: product grid with category filter pills, color family pulldown per item, slide-in cart drawer, "Custom event? Start a conversation" cross-link to inquiry for big-ticket items |
| **Balloon-twisting / Face-painting page** | **Designer 3** ("The Studio Archive") | D3's dense editorial approach for this page: dual-service detail (twisting + face painting), spec tables, occasion types (birthday/corporate/community), accordion FAQ, pre-select inquiry builder passing event-type/guest-count/service into URL |
| **Top nav + IA** | **Existing LT** + synthesizer's judgment | Sticky horizontal top nav with phone number + inquiry CTA persistent. NOT D5's left-rail. Apply your own judgment on menu items based on the 95%-inquiry / 5%-shop split. |
| **Visual language** (colors, typography, voice) | **`_resources/STYLE-GUIDE.md`** | The existing LT system below |

---

## Visual Ground (existing LT — non-negotiable)

### Typography

| Role | Font | Fallback | Weight |
|------|------|----------|--------|
| Headings | DM Serif Display | Georgia, serif | 400 |
| Body | Raleway | system sans-serif | 300, 400, 500, 600, 700 |

**Type scale:**
- H1: 1.75rem mobile / 3rem desktop, DM Serif Display, Near Black
- H2: 1.5rem / 2.25rem, DM Serif Display, Near Black
- H3: 1.25rem / 1.75rem, DM Serif Display, Near Black
- H6 (labels): 0.875rem / 1rem, Raleway 600, Near Black
- Body: 1rem / 1.125rem, Raleway 400, Soft Gray
- Small (captions): 0.75rem / 0.8125rem, Raleway 400, Soft Gray

**Rules:**
- Headings use Near Black `#1A1A1A`, never pure black
- Body uses Soft Gray `#595A5C`, never pure black
- Left-align all body, never justify
- Line length 40–60 characters per line on desktop

### Colors

| Token | Hex | Usage |
|-------|-----|-------|
| Teal | `#008080` | **CTA buttons ONLY** (solid fill). Never text, never borders, never backgrounds, never outlines. One color, one job. |
| Soft Gray | `#595A5C` | Body text only |
| Near Black | `#1A1A1A` | H1–H3 headings, emphasis, navigation labels |
| White | `#FFFFFF` | Cards, content surfaces |
| Near White | `#FBFBFB` | Page background |

**Accent palette** (warm: Blush `#F4DFD7`, Soft Lemon `#F9F871`, Lime Pastel `#B8FF9E`; cool: Seafoam `#88FED0`, Aqua `#80F5F3`, Sky Cyan `#A0E9FF`, Soft Blue `#C3DCF3`):

| DO | DON'T |
|----|-------|
| Thin horizontal bands (40–80px) between sections | Full-height section backgrounds |
| Carousel/slider text panels | Large chunky color blocks |
| Input field, search bar, mega menu backgrounds (use surface tints — see below) | Card backgrounds (use white) |
| Small accent elements (tags, badges, pills) | Competing with photography |

**Surface tints** for inputs/menus: Blush Tint `#FBF5F2`, Blue Tint `#EEF4FB`, Mint Tint `#EEFEF5`, Lemon Tint `#FDFDE3`.

### Spacing — 8px increments

| Token | Mobile | Desktop |
|-------|--------|---------|
| Section padding | 32px | 64–80px |
| Thin band height | 40–60px | 60–80px |
| Card padding | 16px | 24px |
| Element gap | 12px | 16px |

### Voice — Quiet Confidence

Every word of copy must pass the three rules. The Creator archetype (Anthropologie/Etsy/Crayola/Lego). Conversational, intriguing, invites without pushing.

1. **Present tense, not promises.** "Happily delivering along the Wasatch Front" not "We'll deliver to you!"
2. **Invite, never push.** "Tell us what you're imagining" not "Call for a free quote!"
3. **Warm, not performing.** "Every detail matters" not "We LOVE what we do!!!"

If copy sounds like a brochure, a LinkedIn post, or a "BOOK NOW!" salesperson — rewrite.

**Headline anchors:**
- Homepage hero: "We make celebrations unforgettable."
- Categorical: "Something for every season."
- 404: "This page floated away. Let's get you back."

---

## Anti-Defaults (still in force)

- No centered hero + headline + subheadline + 2 buttons (the AI default)
- No gradient backgrounds — solid color blocking only
- No stock photos of "diverse teams at laptops"
- No rainbow backgrounds, Comic Sans, kid-party clipart, tacky banners
- No flashing animations, glitter GIFs, balloons-floating-across-screen
- No "fun balloon party rental" energy — Jeff is the **28-year authority**
- No emoji in headlines, no exclamation marks in body copy
- No hardcoded hex outside CSS `@theme` block
- Mobile-first (375px starting point)

---

## What to Read (in order)

1. **This brief** — the mandate
2. **`_resources/STYLE-GUIDE.md`** at `C:\Users\baenb\projects\Built_by_Cameron\_CLIENTS\locally-twisted\_resources\STYLE-GUIDE.md` — the full visual system (read in detail; you'll be implementing it)
3. **Designer 3** at `C:\Users\baenb\projects\zoho-locally-twisted\gallery\designer-3\` — read `mood.md`, `rationale.md`, `menu.md`, `page-balloon-twisting.tsx` (or equivalent), and the lookbook for reference on the editorial/density approach. **DO NOT import D3's typography (Cormorant + DM Sans + DM Mono) or palette (near-black + brass) — only the structural patterns.**
4. **Designer 5** at `gallery\designer-5\` — read `mood.md`, `rationale.md`, the shop page TSX, and `menu.md`. **DO NOT import D5's left-rail nav (we chose top nav), the dark charcoal palette, or the dusty-rose accents.** Just the shop page pattern.
5. **Designer 7** at `gallery\designer-7\` — read `mood.md`, `rationale.md`, the lookbook page TSX (especially the mood-first 4-step configurator), and the no-text-on-images rule. **DO NOT import D7's parchment/amber palette or Cormorant typography.** The configurator UX and image discipline are what to take.
6. **`_render` Next.js scaffold** at `gallery\_render\` — see how the gallery's render project is structured (Tailwind 4, Next.js 16, App Router). Your output should drop into it cleanly as `_render/src/app/synthesis/`.

---

## Output

Write to: `C:\Users\baenb\projects\zoho-locally-twisted\gallery\synthesis\`

### Required files

```
synthesis/
├── SYNTHESIS-BRIEF.md          (this file — don't modify)
├── layout.tsx                  (shared shell with sticky top nav + footer)
├── globals.css                 (CSS @theme block defining ALL color/font tokens from LT STYLE-GUIDE.md)
├── landing/page.tsx            (homepage — your design, honoring D3-conceptual)
├── lookbook/page.tsx           (D7-derived: mood-first 4-step configurator, no-text-on-images)
├── shop/page.tsx               (D5-derived: shop page pattern)
├── balloon-twisting/page.tsx   (D3-derived: dense editorial twisting + face painting page)
├── mood.md                     (synthesis design personality, what specifically came from where)
├── voice.md                    (3+ headline examples, addressing each visitor type)
├── menu.md                     (IA tree, top nav structure, mobile menu, footer)
├── rationale.md                (design decisions justified — including translation choices from contributors)
└── SYNTHESIS-COMPLETE.md       (one-paragraph summary when done)
```

### After completion

The `_render` project is already scaffolded. Add a route at `_render/src/app/synthesis/` that imports your files. The dev server can be re-started to render. (Orchestrator will handle rendering + screenshots after you complete; you don't need to do that.)

---

## Configurator Specs (from D7 + remap)

The mood-first 4-step configurator on the lookbook page:

- **Step 1:** "Start with a feeling." 5–7 mood pills (e.g., Romantic, Bold, Soft, Festive, Elegant, Playful, Modern). Single-select. Use accent palette colors as PILL accents (not full backgrounds — the pill border or a small swatch).
- **Step 2:** "Family colors." Filtered by step-1 mood. 5 family tabs (Whites/Pinks/Blues/Greens/Metallics or similar). 4–8 swatches per family visible by default. **"See all 60 colors" link** opens a `<details>` expansion (or modal) with the full library grouped by family.
- **Step 3:** "What style?" Single-select chips (Organic / Structured / Minimal / Maximalist).
- **Step 4:** "What scale?" Single-select chips with sample copy (Intimate gathering / Corporate event / Wedding / Large gala).
- **Submit:** Serializes selections to query params and redirects to inquiry form (`/inquire?mood=romantic&colors=pink+gold+cream&style=organic&scale=wedding`). Inquiry form pre-fills via GET params (verified working in v15.105.0 staging tests).

**Loud failure:** the inquiry form must show an explicit user-visible error if submission fails. No silent failures. (Per `C:\Users\baenb\.claude\rules\loud-failure.md` — this is non-negotiable.)

---

## Configurator-as-Inquiry Pre-Fill (from D3)

D3's pattern for the balloon-twisting page: pre-select inquiry builder passing event-type / guest-count / service into the inquiry URL. Apply same pattern to the twisting/face-painting CTA — when customer clicks "Tell us about your event" from the twisting page, query params pre-populate event-type and service in the inquiry form.

---

## Don't-Copy Discipline

You are synthesizing; not picking. Honor the explicit attributions:
- D3 = conceptual frame + balloon-twisting page approach
- D5 = shop page pattern only
- D7 = lookbook + configurator only
- LT existing = visual ground (fonts, colors, usage rules, voice)

If you find yourself wanting to use D3's typography (Cormorant + DM Mono) — DON'T. Use DM Serif Display + Raleway.
If you find yourself wanting D5's left-rail nav — DON'T. Use top nav.
If you find yourself wanting D7's amber-copper accent — DON'T. Use Teal-on-CTA + accent palette as bands/tints.

The visual language IS the existing LT brand. The structural ideas are the contest contributions. Mix them.

---

## Tools

- `Read` — this brief, STYLE-GUIDE.md, contributing designer dirs (D3, D5, D7), `_render` scaffold
- `Write` / `Edit` — your output files at `gallery/synthesis/`
- `WebSearch` / `WebFetch` — only if you need a competitive reference for a specific UX pattern

---

## When You're Done

Write `SYNTHESIS-COMPLETE.md` with a one-paragraph summary of what you built and the most important decisions you made. The orchestrator will then render + screenshot for GL.
