# LT Brand Copy Audience Pages

Status: draft contract
Last verified: 2026-05-11
Scope: Locally Twisted public event audience pages that sit between portfolio proof and `/contact`.

Use this when writing or reviewing audience-page copy such as:

- `/corporate-events`
- `/schools-campuses`
- `/civic-community`
- `/private-celebrations`
- future event-type pages that sit between portfolio proof and the `/contact` inquiry path

Do not use this as the main source for product descriptions, checkout copy,
legal policies, invoices, customer emails, or the BTFP service page. Those have
separate contracts.

## Source Order

When sources conflict, use this order:

1. Current route and launch-scope decisions in `CODING-HANDOFF.md`,
   `locally-twisted-queue.md`, and active `workstreams/*.md` files.
2. `_resources/STYLE-GUIDE.md` for brand voice, visual posture, and route
   treatment.
3. `workstreams/brand-audience-style-reset.md` for audience strategy and proof
   rules.
4. Current page source in `apps/locally_twisted/locally_twisted/www/` and shared
   includes in `apps/locally_twisted/locally_twisted/templates/includes/`.
5. legacy_source, Localo, Drive, or legacy-site material only as claims to verify before
   publishing.

## Core Voice

Locally Twisted sounds experienced, local, and calm. The copy should make the
company feel like a practical event partner, not a novelty shop and not a
founder-only craft booth.

Write as:

- Company-first: Locally Twisted, the team, our process, our install work.
- Buyer-aware: name the audience's real pressure before naming decor ideas.
- Proof-led: use actual installed-work categories, client categories, and route
  evidence before slogans.
- Quote-led: custom event work starts with inquiry and planning, not checkout.
- Specific: date, venue, audience, access, scale, timing, weather, teardown,
  invoice needs, and photo moments.
- Warm but restrained: useful, clear, lightly human, never hype-heavy.

Avoid:

- Founder-dependent framing such as "Book Jeff" or "Jeff makes it special."
- Generic party-store language such as "amazing balloons for every party."
- Unverified superlatives such as "Utah's #1" or exact review counts unless
  rechecked during the same launch pass.
- Copy that implies logo permission, endorsement, or an active customer
  relationship from a proof-crawl name alone.
- Product-purchase framing for V1 launch audience pages.
- Backend CRM labels such as Lead, Opportunity, Qualified, or Pipeline.

## Copy Shape

Each audience page should answer these questions in order:

1. Who is this page for?
2. What makes this event type operationally different?
3. What proof shows Locally Twisted belongs in this lane?
4. What does the buyer need to tell us so the quote can be shaped correctly?
5. What is the next safe step?

Current data-model copy atoms:

- `eyebrow`: audience label, not a slogan.
- `title`: short, direct, and page-specific. Prefer one concrete idea over a
  long sales headline.
- `lede`: one or two sentences naming the buyer pressure and the decor role.
- `proof`: labeled proof points with context. Do not turn client names into
  endorsement claims.
- `clients`: relevant proof names only when the source lane supports them; use
  text/category proof if permission is uncertain.
- `plan_title`: what this audience needs, not what Locally Twisted wants to
  sell.
- `plan`: practical planning concerns and likely use cases.
- `CTA`: route to `/contact` as the quote path, with `/portfolio` as supporting
  proof when needed. Do not route CTAs to `/event-balloons`; that hub was
  removed before launch.

## Audience Angles

### Route boundary

`/event-balloons` is not a current public route. Use the four audience pages
below plus `/portfolio` and `/contact` instead of recreating a hub by copy
drift.

### Corporate Events

Corporate buyers need brand-safe impact, reliable arrival, clean photography,
and invoice or purchasing workflow support.

Emphasize:

- color discipline and brand awareness
- load-in windows, access rules, and stakeholder timing
- openings, launches, employee events, receptions, booths, and ribbon cuttings
- invoice needs without overpromising a finance path

Avoid:

- playful party-first tone
- implying a named company endorsed the site unless the proof source supports
  that exact claim

### Schools And Campuses

School and campus buyers need school-color clarity, fast setup, safe placement,
and decor that works for students, staff, families, and visitors.

Emphasize:

- graduations, assemblies, athletics, dances, back-to-school, and campus events
- bell schedules, gym/stage access, family arrival times, and teardown
- joyful but contained designs

Avoid:

- childish styling as the default
- language that sounds like the page is only for kids' birthday parties

### Civic And Community

Civic buyers need public-facing decor that reads from a distance and respects
access, traffic, weather, visibility, and venue rules.

Emphasize:

- cities, counties, chambers, fairs, festivals, Pride, public celebrations, and
  community gathering spaces
- wayfinding, entrances, stages, photo points, and guest flow
- friendly without looking casual

Avoid:

- novelty patriot language
- costume Americana or flag-wall cliches unless the proof photo is real client
  work and the page context calls for it

### Private Celebrations

Private-event buyers need personal, polished focal points and help choosing
scale. This lane can be warmer than corporate/civic pages while staying premium.

Emphasize:

- birthdays, weddings, showers, memorials, hosted home events, and venue
  celebrations
- one strong photo moment or room anchor
- color, delivery, indoor/outdoor conditions, and setup fit

Avoid:

- making private work feel less professional than public or corporate work
- overpromising emotional outcomes instead of describing the useful decor role

## Proof Rules

Use proof in this order:

1. Real installed work and portfolio images.
2. Buyer-context proof such as corporate, school, civic, venue, public,
   church, family, or delivery.
3. Text-only client/category proof where source and permission allow.
4. Reviews as support, not as the whole argument.

Do not publish exact Google review counts in durable copy unless reverified in
the current run. Stable wording like `100+ Google reviews` is safer.

Client names from a crawl can show breadth, but wording must stay careful:

- Good: "Named in the site proof crawl."
- Good: "Relevant proof names for this lane include..."
- Bad: "Trusted by [name]" unless the source explicitly supports that public
  claim and logo/endorsement use is approved.

## Verification

Before closeout after editing audience-page copy:

1. Confirm the repo is on `main`.
2. Check the active launch scope and route decisions.
3. Read the exact page source being changed.
4. Run a source search for banned drift:
   `rg -n "Utah's #1|Book Jeff|amazing|WOW|Delivery Only|Event Package|Process" apps/locally_twisted/locally_twisted/www apps/locally_twisted/locally_twisted/templates/includes`
5. If rendered copy length or section structure changed, run the relevant
   public layout gates for those routes. At minimum, use the focused route
   verifier or the route grep in `npm run test:interactive-layout` /
   `npm run test:container-contract` that owns the changed pages.
6. Do not claim a route is visually correct without rendered browser evidence.

## Current Implementation Notes

As of 2026-05-10, the audience-page content model lives in:

- `apps/locally_twisted/locally_twisted/www/event_type_pages.py`
- `apps/locally_twisted/locally_twisted/templates/includes/event_type_page.html`
- route wrappers such as `corporate_events.html` and `schools_campuses.html`

The current shared include is useful because it keeps each page's copy atoms
consistent. If a future page needs a structurally different story, create a new
focused include or helper instead of turning the shared include into a mixed
concern.
