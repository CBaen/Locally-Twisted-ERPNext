# Design Notes — Schools & Campuses Page

## Audience Read

The school buyer is an activity director, graduation coordinator, athletic department staffer, or PTA organizer. Their distinct pressures:
- Schedule rigidity: commencement has a fixed time and the arch cannot be late
- Color matching: school colors must be right, not approximate
- Reliability: they cannot chase a vendor during event setup
- Family-friendliness: everything must be appropriate for all ages

The buyer is not looking for inspiration — they know they need balloon decor. They're looking for proof that this vendor will execute exactly as promised.

## Structural Logic

**Section 1 — Hero (fullbleed):** school-back-to-school-stage.webp is the strongest school-context image in the library. H1 names the three buying criteria directly: "School colors. Real installations. On your schedule." Three things, not a tagline — speaks to the functional buyer.

**Section 2 — Intro prose (warm white):** Addresses the activity director's real concern first: "Activity directors don't have margin for late vendors." Then credentials. Then the school-color matching promise is specific: "Share your mascot colors and we'll come back with options that are actually on-palette." The word "actually" is doing work — it names the disappointment they've had with other vendors.

**Section 3 — Gallery (stone):** Four installs in school/campus contexts: two back-to-school stages (different angles/events), graduation garland, WSU corporate arch. The graduation garland is particularly important — graduation buyers have one shot and want to see that commencement context exists.

**Section 4 — Occasions grid (white, 3-column):** Six cards covering the full school event calendar. Layout is 3x2 on desktop (balanced, no orphans). Cards use near-white background with stone border — clean without being clinical. Each card names the specific occasion and then describes exactly what that install looks like for that context.

**Section 5 — Client band (navy):** Short named roster (UofU, WSU, St. Joseph's) extended by honest context items ("back-to-school stage installs across the Wasatch Front") rather than invented clients. Navy band gives the short list authority; the bullet points are honest about range without overclaiming.

**Section 6 — CTA (ink):** "Tell us your school colors." is the most specific CTA of all four pages — it directly names the action the buyer needs to take first. "Mascot colors and schedule" — puts them in the frame immediately.

## Photo Choices

- **Hero bg:** portfolio/optimized/school-back-to-school-stage.webp — stage install, outdoor, community scale
- **Gallery 1:** portfolio/optimized/school-back-to-school-stage.webp — strong school stage
- **Gallery 2:** odoo/Parades/Back to school stage display.png — second angle, outdoor stage
- **Gallery 3:** portfolio/optimized/school-grad-garland.webp — graduation ceremony context critical
- **Gallery 4:** portfolio/optimized/corporate-wsu-arch-bouquets.webp — named university client

## Voice Notes

- "On your schedule" is functional, not promotional — it names a real fear
- "Actually on-palette" — the word "actually" implies the failure mode others deliver
- "Disappears cleanly" — specific, not generic professionalism
- "We've installed for the University of Utah, Weber State, and St. Joseph's" — naming specific institutions is more credible than "Utah schools"
- CTA "Tell us your school colors" — action-specific, not generic "contact us"

## Container Contract

| Section | Mode |
|---------|------|
| Hero | fullbleed |
| Intro | band (contained inner) |
| Gallery | visual-field (fullbleed wrapper, inner max-width) |
| Occasions | band (contained inner) |
| Clients | band (fullbleed wrapper, inner max-width) |
| CTA | fullbleed (inner max-width) |
