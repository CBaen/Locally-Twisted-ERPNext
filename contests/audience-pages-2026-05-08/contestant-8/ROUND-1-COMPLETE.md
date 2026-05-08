# Round 1 Complete — Contestant 8

## Concept summary

The suite's organizing principle is **"Made For You"** — each page's hero H1 speaks in
vocabulary the buyer uses about themselves. A civic coordinator lands on "Balloon decor
built for Utah's civic scale." A school activity director lands on "Spirit events deserve
the real thing." A corporate marketing manager sees "Balloon decor that respects your brand."
A private celebration planner sees "Every detail matters." None of these could swap pages.

## Signature moves by page

**Civic:** 26 named real clients rendered as a full roster in an Ink-background authority band.
"12 Utah cities" anchored in the case study. Pride organizations named specifically.
Three photos chosen for outdoor civic/community range.

**Corporate:** The three-word tagline "Brand-safe. Repeatable. On your colors." in brass uppercase
below the H1 — the exact language a marketing director thinks in. Case study frames clients by
industry category (broadcasters, financial institutions, restaurant groups) rather than a single
story, so multiple buyer types self-identify. Left navy border on service cards reads as professional.

**Schools:** The "School Colors, Respected" section with the subhead "Not close enough. Exactly
right." — a named promise specific to the school buyer's real anxiety. Weber State named
specifically. Client band uses larger Cormorant type (short roster gets more presence, not less).

**Private:** The memorial/celebration-of-life section. Named directly, written with dignity, anchored
by the KJSCOTT review ("very tasteful and meaningful"). No other page in this contest is likely to
name this audience — and no buyer researching balloon decor for a memorial forgets the page that
did. CTA is "Start a conversation" rather than "Request a quote" — softer invitation for a buyer
who may still be deciding whether balloons are right at all.

## Technical contract compliance

- All four pages extend `templates/web.html`
- All four controllers: `no_cache = 1`, `sitemap = 1`, `get_context(context)` function
- Hero contract enforced: 220px mobile / 250px tablet / 280px desktop via explicit
  min-height/height/max-height in colocated CSS
- All section CSS scoped under page-root class (`.lt-page-civic`, `.lt-page-corp`,
  `.lt-page-school`, `.lt-page-private`) — no new global CSS
- No `!important`, no `head_html` injection
- Container mode declared in DESIGN-NOTES and in CSS comments for each section
- Real images only — full paths referenced, no invented files
- Real clients only — no invented names
- No lorem ipsum copy anywhere
