# Schools & Campuses — Design Notes

## Audience posture
Activity directors, athletic departments, PTAs, college student life, graduation organizers.
Buyer's real anxieties: will the colors be right, will it be there on time, will it look good in
the photo that goes to parents/admin, is this family-appropriate. They are NOT worried about
impressing a marketing director — they're worried about not embarrassing the school.

## Distinctive move
The "School Colors, Respected" block: a named promise that LT matches school colors exactly.
Weber State purple, U of U red — not "a purple" or "a red." The brief says the roster is short;
this page leans INTO the short roster by making each relationship feel more significant rather
than padding with weak additions.

The client band uses larger Cormorant type for the school names (instead of the small Lato
list used for civic/corporate) — because there are only 5, each name can breathe and feel
substantial.

## Section decisions

### Hero
- Image: `school-back-to-school-stage.webp` — stage installation, school scale, immediately
  reads as school event context.
- H1: "Spirit events deserve the real thing." — "spirit events" is vocabulary an activity
  director uses. "The real thing" sets up the school-color promise.
- Deep Navy overlay (not Ink) — school events are community/family, not corporate-austere.

### Client proof band
- Deep Navy background (the warmest of the three dark options used across the suite)
- Larger Cormorant type for school names — given the short list, each name gets presence.
- "Schools and campuses we've worked with" — honest, not padded.

### Photo row
Three photos directly from the school context: back-to-school stage, WSU arch with bouquets,
graduation garland. These map directly to the three primary school buyer moments:
welcome events, campus events, graduation.

### School Colors block (distinctive section)
Named Weber State specifically (purple and white) and UofU (implied by the roster). The copy
says "not a generic purple — Weber State purple" which is the specific promise that differentiates
LT from a generic vendor. Two paragraphs of quiet, confident copy.

**This section is architecture, not copy. Do not paraphrase or soften "Not close enough. Exactly right." or the Weber State specificity.** The activity director reading this page is measuring LT against that commitment on every job. Softening the language breaks the mechanism invisibly.

Stone background — same as civic/corporate case study block for visual rhythm, without competing
with their stone sections (each page is viewed independently).

### Service notes
Four cards in grid format:
- Graduation Ceremonies (the highest-value school moment)
- Spirit Events & Homecoming
- Back-to-School & Campus Welcome
- PTA & Family Events (the lower-scale, family-friendly tier)

No invented services. No claims about how many schools LT has served (not in the brief data).

### Icons
Slate Blue background, 4 brass icons:
- School Spirit (the color-match promise)
- Event Stage (gymnasium/auditorium scale)
- Professional (family-friendly context)
- Delivered Cleanly (on-time, which is the schedule anxiety)

### CTA
"Tell us your colors and your event." — puts colors first because that's the first thing this
buyer is thinking about. "Graduation season books early" — a practical constraint for this buyer,
not a pressure tactic.

## Color sequence
Hero (Deep Navy overlay) → Clients (Deep Navy) → Photos (Warm White) → School Colors (Stone) →
Services (White) → Icons (Slate Blue) → CTA (Navy)

Note: Hero and Clients are both Deep Navy but hero is a separate section. The photo row separates
them from the case study. The sequence is clean per the no-adjacent-full-width-color rule — the
hero is a visual image band, not a solid color band in the same sense; nonetheless the photo row
creates the necessary visual break.

## Container contract
- `.lt-school-hero` — fullbleed
- `.lt-school-clients` — fullbleed (inner wrapper)
- `.lt-school-photos` — band (max-width 1200px)
- `.lt-school-colors` — band (max-width 900px)
- `.lt-school-services` — band (max-width 1100px)
- `.lt-school-icons` — fullbleed (inner wrapper grid)
- `.lt-school-cta` — fullbleed (inner wrapper max-width 680px)
