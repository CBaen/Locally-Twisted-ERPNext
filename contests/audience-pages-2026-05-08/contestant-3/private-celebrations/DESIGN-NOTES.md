# Design Notes — Private Celebrations Page

## Audience Read

The private celebrations buyer is the most emotionally involved of all four audiences. They are:
- A parent planning a child's birthday who wants it to feel special, not generic
- A wedding planner or couple who needs elevated taste, not party-supply aisle decor
- A family hosting a baby shower who wants the decor to match the invitation
- A family planning a celebration of life, who needs "tasteful and meaningful" — not festive
- A milestone celebrant for whom this occasion won't repeat

The critical distinction: this buyer doesn't want the best price — they want the best result. The tone must be warmer than corporate but more considered than celebratory-generic. "Quiet confidence" applies most carefully here.

## Structural Logic

**Section 1 — Hero (fullbleed):** Uses wedding-organic-half-arch.webp — the most elegant, taste-elevated image in the library. H1 is "The moment deserves something beautiful." — nine words, entirely feeling-led, not functional. CTA is "Tell us what you're imagining" — a direct quote from the style guide's preferred CTA pattern. This is the one page where the CTA should feel like an invitation, not a transaction.

**Section 2 — Intro + stats (warm white):** Three paragraphs. First names the weight: "A first birthday only happens once. A wedding is the photograph people return to. A memorial is how a community says goodbye." The celebration-of-life buyer needs to know this is a safe vendor for a hard moment. Second paragraph promises the same craft at private scale. Stats strip uses `<dl>` semantics: "300+ birthday installs," "Wasatch Front weddings," "Every detail matters." The third stat is intentionally not a number — it's a value statement.

**Section 3 — Memorial / Celebration of Life band (slate, Round 2 addition):** A dedicated band that claims the grief buyer BEFORE the occasions grid. This is the anxiety-first architecture fully executed: the memorial buyer's specific weight is named ("When a celebration carries grief, the decor has to hold both"), their need is answered in prose ("Locally Twisted has helped families do this work"), and KJSCOTT's review anchors the section as structural proof — one home, full weight, not repeated below. The CTA in this section is softer: "Start a conversation" rather than "Request a quote." Two-column layout on desktop: prose left, KJSCOTT quote right with left brass-rule callout. Slate ground separates visually from warm white above and stone below.

**Section 4 — Occasions grid (stone, 5-up with photos):** Five cards (memorial removed — that buyer has been claimed above). 3-column on desktop with cards 4-5 centered in the second row, 2-column tablet, 1-column mobile. Each card: photo → name → body. Photos chosen for taste elevation: birthday bouquets, organic half-arch (wedding), floral half-arch (showers), dolphin backdrop (milestones), smurfs arch (custom themes).

**Section 5 — Testimonials (white):** Three reviews (KJSCOTT removed — it lives in the memorial band). Sara M. (loyalty/longevity), Mark T. (milestone quality), LuAnn K. (care/service recovery). 3-column grid. `<blockquote>` with `<footer>` semantics. Privacy-friendly attribution.

**Section 6 — CTA (navy):** Same invitation posture as hero CTA. "Or just the feeling you're going for" — the key phrase that reduces purchase barrier for buyers who can't articulate what they want.

## Color Sequence

Ink hero → warm white → stone occasions → white testimonials → navy CTA

No two adjacent full-width colored sections. Warm white / stone / white are three distinct surface treatments.

## Photo Choices

- **Hero bg:** portfolio/optimized/wedding-organic-half-arch.webp — most elegant image in library
- **Birthday occasions card:** portfolio/optimized/birthday-balloon-bouquets.webp
- **Wedding card:** portfolio/optimized/wedding-organic-half-arch.webp
- **Baby/Bridal shower card:** portfolio/optimized/wedding-floral-half-arch.webp
- **Milestone card:** portfolio/optimized/birthday-dolphin-backdrop.webp
- **Celebration of life card:** portfolio/optimized/wedding-foil-heart-arch.webp
- **Custom themes card:** portfolio/optimized/birthday-smurfs-arch.webp

## Voice Notes

- "The moment deserves something beautiful" — subject is the moment, not "we" or the company
- Celebration-of-life named explicitly in intro — lets the grief buyer feel seen, not othered
- "Backyard birthday" vs "corporate brand activation" — specifically says private scale is not lesser
- "Or just the feeling you're going for" — radically reduces the barrier for buyers who don't speak design
- Stats: the third "stat" is "Every detail matters" — not a number. That's intentional. Numbers would cheapen this page.

## Container Contract (Round 2 — 6 sections)

| Section | Mode |
|---------|------|
| Hero | fullbleed |
| Intro + stats | band (warm white, contained inner) |
| Memorial band | band (slate, 2-col inner on desktop) |
| Occasions grid | visual-field (stone, fullbleed wrapper, inner max-width) |
| Testimonials | band (white, contained inner) |
| CTA | fullbleed (navy, inner max-width) |

## Color Sequence (Round 2)

Ink hero → warm white intro → slate memorial → stone occasions → white testimonials → navy CTA

No two adjacent full-width colored sections. Warm white / slate / stone / white / navy — each section breaks from the prior surface.
