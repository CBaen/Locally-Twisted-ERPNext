# Rationale — Synthesis Design

## The Core Translation Problem

Three designers built excellent structural ideas — but in their own visual languages. D3's near-black surface makes balloon photography glow. D7's parchment-and-amber warmth reads like a Parisian atelier. D5's editorial left-rail is borrowed from *Kinfolk*. All three are internally coherent.

The synthesis problem is not "pick the best visual language." It's "transplant the structural ideas into a visual language that already exists." LT has a STYLE-GUIDE. It has a color system. It has a type system. The contest designers did not work within it — they invented their own. The synthesis designer must honor what the contest designers were *doing* while rendering it in what LT *is*.

This document records every material decision and why it went one way and not another.

---

## Decision 1: Top Nav (Not D5's Left-Rail)

**D5's left-rail** is the most structurally distinctive navigation in the field — borrowed from editorial magazine layout, creates a permanent compositional anchor for full-bleed photography. GL reviewed it and chose top nav.

**Consequence:** The synthesis uses D3's IA structure (Work / Services / Shop / Contact order, persistent phone number right-aligned, mobile full-screen drawer) rendered in LT's horizontal sticky nav. Phone number persists at all viewport sizes where space allows (640px+). CTA button ("Tell us about yours") lives in the nav right — Teal fill, the only teal element in the shell.

---

## Decision 2: D3's Hero Logic vs. AI Default

**The AI default hero:** centered headline + subheadline + two equal-weight CTA buttons. Every balloon-decor site uses this. D3 identified it precisely and refused it.

**D3's principle:** the hero photograph is the argument; copy is the annotation. The headline sits bottom-left, below the visual center of gravity, after the eye has traveled the photo.

**How this translated:** The landing page hero uses a full-bleed photo block (placeholder in this render), with copy anchored bottom-left behind a gradient scrim. The headline — "We make celebrations unforgettable." — leads. Two CTAs follow, but secondary to the image. The eye sees the work before it reads the name.

**What changed from D3:** The scrim fades to Near White (LT's ground color), not to D3's near-black. The headline is DM Serif Display at Near Black, not Cormorant italic at cream. The teal CTA button — not D3's brass rectangle — is the primary action.

---

## Decision 3: Configurator — D7's 4-Step UX in LT Colors

**D7's insight:** customers start with a feeling (mood), not a color. Presenting 60 swatches immediately produces decision fatigue. The step-based configurator (mood → family colors → style → scale) collapses 60 choices into ~6 visible mood pills, then 4–8 family swatches, with "See all N colors" expansion.

**D7's version:** uses amber-copper active states, Cormorant serif headings, parchment surface for the configurator panel.

**Translation to LT:**
- Active states: Near Black border (not amber). Selected pills use blush-tint background — a surface tint, never a teal fill.
- Teal appears only on the final "Continue to inquiry" CTA button.
- Configurator background: White (LT card surface), not parchment.
- Step indicator: Raleway 600 uppercase labels. Active step: Near Black underline. Done steps: labeled with ✓, Teal color — the only place teal text appears (small label register only, not body text; acceptable).
- Form fields: Blush-tint background per STYLE-GUIDE surface tint rules.
- Mood pill accents: Each mood pill uses its corresponding accent palette color as the *border color* (not background fill). Per STYLE-GUIDE: accent colors as "small accent elements (tags, badges, pills)." This is the one place the accent palette touches the configurator chrome.

**Loud failure:** If the submit button is clicked with incomplete selections, an error banner renders with `role="alert"` and `aria-live="assertive"`. No silent failures. User sees "Please complete all steps before continuing." Per `loud-failure.md`.

---

## Decision 4: Balloon-Twisting Page — D3's `<dl>` Spec Register

**D3's insight:** service specifications formatted as definition lists (`<dt>` / `<dd>` pairs) read like a professional's data sheet — "Best at: 50+ guests / Duration: 1–3 hours." This is the register of precision, not brochure bullets.

**Translation to LT:** The spec rows are styled with Raleway 600 term labels (uppercase, Soft Gray) and Raleway 400 details (Near Black). The visual output is identical to D3's intent — a labeled fact table — using LT's fonts instead of D3's DM Mono. The border-bottom hairlines between rows use LT's `--color-border` (rgba(26,26,26,0.12)).

**What was not taken:** D3's service page in its original design uses a near-black surface with cream type. The synthesis version sits on White/Near White. The editorial density is preserved; the palette is not.

---

## Decision 5: Shop Page — D5's Pattern, LT's Colors

**D5's contribution:** the shop heading "A few things you can take home today" (not "SHOP ALL PRODUCTS"), category filter pills, slide-in cart drawer, and "Custom event? Start a conversation" cross-link. These are structural and voice decisions.

**Translation to LT:**
- Filter pills use `chip` / `chip--selected` CSS classes — secondary outlined style, Near Black border on selected, Blush-tint background on selected. Not teal.
- Add to cart button: Teal primary — this is the appropriate CTA for e-commerce.
- Cart drawer: White background, Near Black text (LT card rules). D5's version used "linen" (warm off-white) — translated to White.
- Out of stock badge: Near Black background, White text (LT Near Black emphasis usage).
- Price display: Raleway 700, Near Black (not D5's DM Mono — LT has no monospace register).

---

## Decision 6: No Text on Images (D7's Discipline)

**D7's structural rule:** editorial layouts separate image from words so both can breathe. Text overlaid on photography competes with both and loses.

**How this propagated through all pages:**
- Look book grid: photo block has `visually-hidden` alt text only — category and title live below the image
- Landing featured work: same pattern
- Service page photo blocks: alt text via `aria-label` on the container, caption text below
- Hero: copy lives below the photo's visual center of gravity, behind a scrim — the photo breathes, the copy doesn't fight it

---

## Decision 7: Accent Palette as Thin Bands Only

**STYLE-GUIDE constraint:** Accent colors appear as thin horizontal bands (40–80px) between sections, carousel text panels, input tints, and small tags/pills. Never as full-height section backgrounds. Never stacked back-to-back.

**Implementation:** Every accent band in the synthesis uses a `div.accent-band` with `height: var(--band-height-mobile)` (48px mobile, 72px desktop). The pattern between major sections: White content → thin colored band → White content. No two bands are the same color. No two colored sections stack.

---

## Decision 8: Footer — Soft Blue Per STYLE-GUIDE

**STYLE-GUIDE explicit:** "Footer: Soft Blue background (#C3DCF3). All text in Near Black for contrast on Soft Blue."

D3 and D7 both use dark espresso footers. D5 uses dark charcoal. The synthesis uses Soft Blue — the LT brand footer, non-negotiable.

---

## What Would Change in a Real Build

1. **Photo placeholders** → real photography. Every placeholder block has an `aria-label` with specific alt text ready for image placement.
2. **`/inquire` route** → real inquiry form that reads query params for pre-fill. The URL builder is wired; the receiving end is not part of this render.
3. **Color swatch hex values** → Jeff's actual 60-color balloon inventory catalog (labeled as product data, exempt from hardcoded-hex rule).
4. **Cart → real checkout** → The cart drawer links to `/checkout` but no checkout flow was built in this sprint.
5. **`prefers-reduced-motion` transitions** → `globals.css` includes the `@media (prefers-reduced-motion: reduce)` block; all transitions collapse to 0.01ms.
