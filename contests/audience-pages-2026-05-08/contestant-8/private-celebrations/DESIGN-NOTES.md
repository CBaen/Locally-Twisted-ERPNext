# Private Celebrations — Design Notes

## Audience posture
Birthday parents, wedding planners, baby shower hosts, milestone families,
memorial/celebration-of-life organizers.
Key tension: this buyer wants the decor to feel PERSONAL and elevated, not mass-market.
They're also paying out of pocket, not through a corporate budget — so the tone should be
warm and inviting, not professional-formal.

## Distinctive move
The memorial/celebration-of-life section. Few balloon companies acknowledge this audience at all —
it usually gets lumped into "all events" or ignored entirely. Naming it directly, with dignity
and without being maudlin, differentiates LT from any competitor who doesn't. The KJSCOTT review
("sports themed funeral stand... very tasteful and meaningful") is the only verified piece of
social proof for this context, and it's exactly right: specific, human, unsentimental about the
product, sentimental about the outcome.

## No named-client roster
By design. The brief specifies no named clients for private celebrations — buyers expect privacy.
The proof structure is category-level (300+ birthdays, Wasatch Front weddings) and one anonymized
review. This is the right call: a private buyer reading this page is reassured by privacy norms,
not by seeing other families' names.

## Section decisions

### Hero
- Image: `wedding-organic-half-arch.webp` — the most tasteful, premium, wedding-adjacent photo
  in the portfolio library. Sets the tone for elevated private work immediately.
- H1: "Every detail matters." — Short. Personal. The quietest H1 across the four pages. The
  private buyer doesn't want to feel sold to — they want to feel heard.
- Slate Blue overlay (more muted than the civic/corporate pages) — warmer, less authority-heavy.
- CTA copy: "Tell us what you're imagining" — uses the Quiet Confidence CTA voice verbatim.

### Celebration categories
Four cards in 2×2 (mobile) / 4×1 (desktop) grid:
- Birthday Celebrations: "300+ birthday installs" — supportable from the brief data and client
  history; conservative wording.
- Weddings & Showers: named specifically.
- Milestones & Anniversaries: retirement, anniversaries, life moments.
- Memorial & Celebration of Life: named clearly, without euphemism.

Small brass asterisk icon (&#10022;) used as the category marker — consistent, brand-appropriate,
not a clipart badge.

### Photo grid
Four photos in portrait (3:4) aspect ratio — wedding photos show better in portrait because
the full arch/garland needs vertical space. Grid: 2×2 mobile, 4×1 desktop (balanced 4-photo row).
- wedding-organic-half-arch.webp
- wedding-floral-half-arch.webp
- birthday-balloon-bouquets.webp
- wedding-foil-heart-arch.webp

The mix shows range (two wedding types, birthday, foil/milestone) without forcing a narrative.

### Memorial section
White background (the most neutral, quiet surface). Left brass rule on the review callout
instead of a card border — quieter, more editorial, appropriate for the gravity of the subject.

**This section is architecture, not copy. Do not soften, abbreviate, or reposition it.** The memorial section's placement immediately after the hero (Section 2, before categories) is a deliberate structural claim on the grief buyer before any birthday or wedding content appears. Moving it or softening "Jeff and the team have helped families do this work. They take it seriously." removes the mechanism. The KJSCOTT review is the only verified social proof for this context — do not replace it with a generic placeholder.

The opening paragraph uses the sentence "Jeff and the team have helped families do this work.
They take it seriously." — one of the few places where Jeff is named. It makes sense here because
the memorial buyer wants to feel like they're dealing with a person, not a company.

The review (KJSCOTT) is presented in a blockquote with proper semantic markup. Attribution
is "K.J.S., verified Google review" — privacy-friendly initials, verified source.

### Icons
Slate Blue background. Four icons from the brand system:
- Premium Private Event (taste-elevated promise)
- Organic Garland (the custom design language)
- Design Driven (the creative partnership claim)
- Delivered Cleanly (the logistics promise)

These four answer the four unspoken private buyer questions: Is this tasteful? Is it custom?
Does the designer understand what I'm going for? Will they handle the day-of logistics?

### CTA
"Start a conversation" — softer than "Request a quote." Private buyers are often in an early
exploratory phase. They don't want to feel committed by clicking a CTA. This language invites
rather than asks for commitment.

## Color sequence
Hero (Slate Blue/Ink overlay) → Categories (Warm White) → Photo Grid (Stone) →
Memorial (White) → Icons (Slate Blue) → CTA (Navy)

Stone → White adjacency: acceptable, both are light. White → Slate Blue → Navy: the icons
band (Slate) separates White from Navy. Sequence is clean.

## Container contract
- `.lt-private-hero` — fullbleed
- `.lt-private-cats` — band (max-width 1100px)
- `.lt-private-photos` — visual-field (max-width 1300px, wider for the 4-photo portrait grid)
- `.lt-private-memorial` — band (max-width 780px — narrow for intimate reading width)
- `.lt-private-icons` — fullbleed (inner wrapper grid)
- `.lt-private-cta` — fullbleed (inner wrapper max-width 680px)
