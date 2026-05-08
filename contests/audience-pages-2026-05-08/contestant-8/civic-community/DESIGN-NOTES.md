# Civic & Community — Design Notes

## Audience posture
City events coordinators, Pride organizers, county events, chambers, community orgs.
Buyer expects: proof of public-scale work, outdoor durability, no-coordination-burden service.
They're comparing vendors on reliability and photographability, not price alone.

## Section decisions

### Hero
- Image: `seasonal-pride-columns.webp` — rainbow columns, civic scale, outdoors, immediately
  legible as community event work.
- H1: "Balloon decor built for Utah's civic scale." — names the scale, names the geography,
  doesn't sound like a party-supply shop.
- Eyebrow: "Wasatch Front · Civic & Community Events" — context for coordinators who may be
  searching regionally.
- CTA passes `?intent=civic` so the contact form can pre-select event type.

### Client proof band
- Dark ink background with brass-accented typography — authority, not decoration.
- 26 named clients in a wrapped list with brass dot separators. The sheer count of city
  and org names does the credibility work without a single invented claim.
- "12 Utah cities" subtext in case study reinforces the geographic breadth without inflating.

### Photo row
Three images selected for civic/outdoor range:
1. `seasonal-pride-columns.webp` — Pride event, Utah, columns, outdoor
2. `corporate-weberstock-photo-opt.webp` — community festival, photo backdrop scale
3. Odoo: Progress Flag arch — civic, outdoor, genuine Pride work

All three represent different civic moments without repeating each other.

### Public-Event Ready named-promise section
The eyebrow "Your event. Our accountability." and H2 "Three things your city needs from a vendor. All three, every time." are named promises addressed directly to the coordinator — not capability labels about LT. The three columns (weather-anchored, one-vendor full service, invoice-ready documentation) are commitments the coordinator can hold LT to. **This section is architecture, not copy. Do not paraphrase or soften these commitments.** Changing the language removes the mechanism.

### Case study block
Named the Pride organizations specifically (SLC Pride, Pride Center, Equality Utah, LGBT Chamber)
because that's a buyer-verifiable claim. "Multiple years running" is conservative (doesn't invent
frequency) but signals continuity of relationship. The paragraph about 12 Utah cities grounds the
statewide service claim without a numbered list.

Stone background — one step removed from warm white, creates visual separation without introducing
a second full-width color violation (stone is used as a quiet band, warm white sections flank it).

### Service notes
Four cards in a 2×2 (mobile), 4×1 (desktop) grid. Cover the four actual civic needs:
- Parade/outdoor arches
- Civic entrance columns
- Photo ops
- Full-service install (the operational differentiator)

No invented services. No "fleet of vans" or "50,000 events" claims.

### Icons band
Slate Blue (`--lt-slate`) background with brass icons. Grid: 2×2 mobile, 4×1 desktop.
Icons chosen: Utah Rooted (local authority), Civic Parade (context), Professional (operations),
Delivered Cleanly (the no-coordination-burden claim). These four answer the four unspoken buyer
questions for a civic coordinator.

### CTA
Deep Navy background, crimson button. Copy acknowledges that civic events book early — that's
a practical fact for this buyer type, not a pressure tactic. "Tell us what you're planning" is
the Quiet Confidence voice.

## Color sequence
Hero (Dark/Navy overlay) → Client Band (Ink) → Photos (Warm White) → Case Study (Stone) →
Services (White) → Icons (Slate Blue) → CTA (Navy)

No two adjacent colored full-width sections. Stone and White are different enough to pass.
The Slate Blue icons band breaks the White/Navy adjacency correctly.

## Container contract (each .page_content direct child)
- `.lt-civic-hero` — fullbleed
- `.lt-civic-clients` — fullbleed (inner wrapper)
- `.lt-civic-photos` — band (max-width 1200px inner)
- `.lt-civic-case` — band (max-width 900px inner)
- `.lt-civic-services` — band (max-width 1100px inner)
- `.lt-civic-icons` — fullbleed (inner wrapper grid)
- `.lt-civic-cta` — fullbleed (inner wrapper max-width 680px)

## Photo reference rationale
- Production optimized library used first (two photos)
- Odoo library used for one image (Progress Flag arch) that has no equivalent in optimized set
- Full Odoo source path preserved for implementation-phase copy
- No images invented, no images moved in this contest phase
