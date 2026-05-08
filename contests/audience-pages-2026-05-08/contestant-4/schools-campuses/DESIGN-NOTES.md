# /schools-campuses — Design Notes

## Audience

Activity directors, athletic department staff, PTAs, college student life coordinators, graduation committee members. Buyer posture: spirit-driven, schedule-tight, school colors disciplined, family-friendly.

Key concern: "Will this look good in parents' photos and not embarrass the school?" Secondary: "Will they show up on time and not require hand-holding?"

## Structural Decision

7 sections (one fewer than other pages, matching the briefer client roster):
1. Hero — fullbleed, back-to-school stage photo
2. Proof pillars — deep navy, 4 pillars centered on school-specific concerns
3. School moments — 3 case cards covering graduation, back-to-school, spirit events
4. Gallery strip — visual-field, 6 school-context images
5. Client roster — stone, named-relationship cards (not a 30-item chip list)
6. Services — two-column, audience-specific copy + service grid
7. CTA — deep navy, school calendar framing

## The Roster Treatment

The school client roster is intentionally short (5 entries), per the brief: "lean into specific named relationships and graduation/back-to-school context rather than padding with weak items." I treated the roster as named-relationship cards (larger chip format with context labels) rather than a dense chip list — a shorter list that looks confident is better than a padded list that looks desperate.

## Hero

- Background: `school-back-to-school-stage.webp` — this is literally the strongest school-context image in the portfolio, shows scale immediately
- H1 focuses on "holds up to school-event standards" — addresses the school buyer's implicit worry about professionalism
- Lede enumerates the 4 main school event types: graduation, back-to-school, homecoming, spirit events
- CTA: `/contact?intent=school`

## Proof Pillars

Deep Navy (#0E2240) ground — authority but warmer than Ink, appropriate for school/educational context. Four pillars designed for an activity director:
- "School Colors" → color accuracy, not aesthetic
- "Event Ready" → venue-scale (auditoriums, gyms)
- "Schedule-Safe" → facility access, class schedules
- "Family-Friendly" → appropriate for all audiences = no parent complaints

## School Moments

The three case study cards cover the three most common school hire contexts:
1. Back-to-school (WSU, named, repeat client)
2. Graduation (UofU + WSU, ceremony scale)
3. Spirit events (St. Joseph's, homecoming/pep rally/athletic)

Image for case 3 is `Weber Welcome bouquets.png` from Odoo — shows school-color bouquets at a student welcome event, directly relevant.

## Gallery

6 images: 3 from optimized portfolio (back-to-school stage, grad garland, WSU arch+bouquets), 3 from Odoo source (2 more back-to-school stage variants, grad organic garland). All school context.

## Client Roster

Stone ground. Named-relationship chip list — 5 entries displayed with enough whitespace to read as confident and specific, not sparse. Context labels in parentheses for "Ogden City (school events)" and "Tree House Museum (education days)" — makes clear why these appear in a schools section.

## Services Section

Same two-column layout as corporate. School-specific services in a 4+4 grid (8 items = balanced, no orphan rows).

Key service differentiation from other pages:
- "Graduation Arches & Garlands" and "Back-to-School Stage Displays" are named specifically
- "Color-Matched School Spirit" names the promise that matters most to this buyer

## CTA

Deep Navy (same as proof bar) — consistent with the school page's tone. CTA copy is practical: "Tell us the event type, date, and your school's colors" — gives the buyer exactly what to have ready before they fill out the form.

## What This Page Does NOT Do

- Does not invent school clients beyond the approved roster
- Does not claim sports team relationships (e.g., "University of Utah football") as specific clients unless evidenced — UofU football image exists in Odoo but the context is unclear, so it's not used as a named case study
- Does not use "we love working with schools" phrasing
- Does not add clip-art graduation caps or mascot imagery

## Accessibility

- One H1
- Headings: H1 → H2 (pillars band label, as a `p`, not a heading — it's a label, not structural heading) → H2 (moments) → H3 (moment cards) → H2 (clients) → H2 (services) → H2 (CTA)
- Gallery: `aria-label`
- Service list: `aria-label`
- Client list: `aria-label`
- All images: descriptive alt or `aria-hidden` for decorative
- CTAs: min 44px / 48px
- `prefers-reduced-motion`: gallery hover transition disabled
