# Mood — Synthesis Design

## Concept Name
**The Studio**

(Not "The Studio Archive." Not "The Atelier." This is the synthesis — the studio where the archive and the atelier converge, rendered in the existing brand's own light.)

## Five Adjectives

1. **Considered** — nothing placed without reason; every section earns its space
2. **Unhurried** — authority doesn't need urgency; no "Book Now" energy anywhere
3. **Earned** — 28 years shows in economy, not volume; specificity over superlatives
4. **Luminous** — the page is a frame; the balloons bring the color
5. **Warm** — never performing warmth; understated, material, present

## What the Site Feels Like

A working studio that has been open a long time. Clean walls, good natural light. The portfolio is hung without ceremony — not because it's been displayed carelessly, but because the work doesn't need framing to make its point. The phone number is on the door. The person who answers knows what they're doing.

It's Anthropologie, not a party-supply store. Etsy's quality-over-quantity editorial mode, not Amazon's everything-visible density. It's a maker's workspace, not a storefront.

## What Came From Where

| Element | Source | What was taken |
|---|---|---|
| Site-wide density and intentionality | D3 (The Studio Archive) | Every section earns space. Hero: photo-led, copy anchors bottom-left. Proof strip: authority through specificity. Brand story as landing section, not nav item. |
| Configurator UX | D7 (The Atelier) | 4-step mood-first flow. No text on images. Portfolio grid + category filter. "Something else in mind?" inquiry close. |
| Shop page pattern | D5 (The Studio) | Filter pills, slide-in cart drawer, "Custom event? Start a conversation" cross-link. Honest small SKU set with editorial tone. |
| Balloon twisting page | D3 (The Studio Archive) | Dense editorial approach. Dual-service at equal weight. `<dl>` spec tables. Occasion type rows. Accordion FAQ. Pre-select URL builder. |
| Visual language (everything visible) | LT STYLE-GUIDE.md | DM Serif Display + Raleway. Teal CTA-only. Near-white ground. Soft-blue footer. Accent palette as thin bands (40–80px). White cards. 8px spacing grid. |

## What Was Explicitly Refused

- **D3's near-black surface** — powerful for the Studio Archive concept; wrong for LT's existing brand, which is white and airy. The darkness was a concept choice, not a brand choice.
- **D3's three-register typography** (Cormorant + DM Sans + DM Mono) — the DM Mono catalog register is distinctive, but LT's existing STYLE-GUIDE specifies DM Serif Display + Raleway. The synthesis honors the existing system.
- **D5's left-rail navigation** — structurally interesting (borrowed from editorial magazine layout); GL chose top nav. Not imported.
- **D5's dark charcoal palette and dusty-rose accents** — the shop structure was the contribution; the palette wasn't.
- **D7's Cormorant typography and amber-copper accents** — D7's mood-first configurator UX and no-text-on-images discipline were the contributions; the parchment/amber palette wasn't.

## The Visual Ground (Non-Negotiable)

All color and typography from `_resources/STYLE-GUIDE.md`. Reproduced verbatim in `globals.css` `@theme` block. No hardcoded hex outside that block.

- **Teal `#008080`**: CTA buttons only. One color, one job.
- **Near Black `#1A1A1A`**: Headings, nav labels, emphasis.
- **Soft Gray `#595A5C`**: Body text only.
- **White `#FFFFFF`**: Cards, content surfaces.
- **Near White `#FBFBFB`**: Page background.
- **Accent palette** (Blush, Lime Pastel, Aqua, Soft Blue): Thin bands (40–80px) between sections only. Never full-height backgrounds. Never card backgrounds. Never competing with photography.
- **Soft Blue `#C3DCF3`**: Footer background per STYLE-GUIDE.
