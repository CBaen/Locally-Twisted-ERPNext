# Design Notes — Corporate Events Page

## Audience Read

The corporate buyer is a marketing coordinator, event manager, or executive assistant booking for a brand activation, store opening, company party, or sponsored event. They care about:
- Brand safety: will this match our colors?
- Process: can I get an itemized quote for AP?
- Reliability: will they show up and clean up professionally?
- Credibility: have they worked at brand-level before?

The roster (KSL, KUTV, FOX13, Zions Bank, America First CU, Chick-Fil-A, Utah Jazz, IHC, Ancestry) answers credibility hard. The three callouts answer process. The process steps answer reliability.

## Structural Logic

**Section 1 — Hero (fullbleed):** Uses the corporate-logo-arch.webp — strongest brand-activation image in the library. H1 "On-brand. On-time. Invoice-ready." is the corporate buyer's three mental checkboxes named directly. CTA uses Deep Navy (not Crimson) — corporate buyers respond better to confidence than urgency.

**Section 2 — Intro + callouts (warm white):** Two-column layout on desktop. Left column is two prose paragraphs naming broadcasters, financial institutions, healthcare systems — specific industry credibility. Right column is three brass-rule callouts: brand-color matched, AP-invoiceable, clean strike included. These are the friction points a corporate buyer anticipates before they even read the copy.

**Section 3 — Gallery (near white):** Four installs that show scale and brand context: logo arch, Weberstock photo op, WSU arch/bouquets, IHC mockup. All four have clear corporate/sponsor context. Near white background keeps focus on the photos.

**Section 4 — Process steps (slate blue band):** Three numbered steps in the actual corporate procurement order: (1) color matching brief, (2) AP-structured quote, (3) professional install and strike. Slate blue creates authority without being as heavy as Navy — right for a process/workflow section.

**Section 5 — Client roster (white, chip format):** The full 30-client corporate roster displayed as tag chips. Chip format is more readable for a long list than a grid of rows. Chips are rectangular (0-border-radius), stone-tint background — premium, not playful.

**Section 6 — CTA (navy):** "Ready to brief us on your event?" mirrors the language of corporate briefing processes. The body copy says "brand guide, event date, venue" — speaks directly to what a marketing manager already has ready.

## Color Sequence

Ink hero → warm white → near white → slate blue → white → navy

No two adjacent full-width colored sections (warm white/near white are close but distinct; slate blue/white create clear break).

## Photo Choices

- **Hero bg:** portfolio/optimized/corporate-logo-arch.webp — strongest brand-activation image, large arch in corporate colors
- **Gallery 1:** portfolio/optimized/corporate-logo-arch.webp — branded entrance
- **Gallery 2:** portfolio/optimized/corporate-weberstock-photo-opt.webp — sponsored festival photo op
- **Gallery 3:** portfolio/optimized/corporate-wsu-arch-bouquets.webp — corporate sponsor install
- **Gallery 4:** odoo/Mock up IHC.png — healthcare/corporate mockup proof

## Voice Notes

- "Your brand guide is the brief" — concise, direct, assumes the buyer knows what a brand guide is
- "Not a close equivalent" — specific assurance that addresses the real fear
- "What goes up reflects your brand. What comes down leaves nothing behind." — parallel structure, quiet confidence
- Process steps are in buyer sequence: brief → approve → receive. Not vendor sequence.
- CTA "brief us" is deliberate corporate language

## Container Contract

| Section | Mode |
|---------|------|
| Hero | fullbleed |
| Intro + callouts | band (contained inner) |
| Gallery | visual-field (fullbleed wrapper, inner max-width) |
| Process | band (fullbleed wrapper, inner max-width) |
| Roster | band (contained inner) |
| CTA | fullbleed (inner max-width) |
