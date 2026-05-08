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

**Section 3 — Occasions grid (stone, 6-up with photos):** Six cards, each with a real portfolio photo. This is the most photo-rich section of any page because private buyers are buying by visual fit. 3-column on desktop (3+3 — balanced), 2-column on tablet (2+2+2), 1-column on mobile. Each card: photo → occasion name → short description. Photos chosen for taste elevation: organic half-arch, foil heart arch, floral arch, dolphin backdrop, smurfs arch (custom theme), birthday bouquets.

**Section 4 — Testimonials (white):** Four real Google reviews selected for private celebration relevance — the "balloon guy for 7 years" (loyalty), the "sports themed funeral stand" (celebration of life), the "blown away" wedding/birthday (milestone quality), the delivery fix (service recovery/care). 2-column grid. `<blockquote>` with `<footer>` for semantic correctness. Privacy-friendly attribution (abbreviated).

**Section 5 — CTA (navy):** CTA is "Tell us what you're imagining" — same phrasing as the hero CTA, reinforcing the invitation posture. Body copy: "Share the occasion, date, and palette — or just the feeling you're going for." The phrase "or just the feeling you're going for" is the key differentiator — it tells the buyer they don't need to know exactly what they want, which reduces purchase anxiety for private buyers.

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

## Container Contract

| Section | Mode |
|---------|------|
| Hero | fullbleed |
| Intro + stats | band (contained inner) |
| Occasions | visual-field (fullbleed wrapper, inner max-width) |
| Testimonials | band (contained inner) |
| CTA | fullbleed (inner max-width) |
