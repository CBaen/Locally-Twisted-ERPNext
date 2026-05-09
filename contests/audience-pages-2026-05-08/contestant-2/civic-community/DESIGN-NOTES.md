# Civic & Community — Design Notes

## Audience
City events coordinators, Pride organizers, chambers of commerce, county events teams, public-facing community organizations across the Wasatch Front.

## Buyer posture
These buyers are public-facing planners. They need vendors who understand permit windows, shared spaces, civic scale, and political neutrality within a visual scope. They are comparing vendors and looking for proof that LT has done city-scale work before — not birthday party work at city scale, but actual municipal, civic, and Pride events with the visual footprint to match.

The page needs to make them feel: "This company has done work like mine. They know what I'm dealing with."

## Concept: "Built for public events. Designed to photograph."
The twin anchors for civic buyers are (1) operational reliability — will they show up, handle permits, coordinate with city logistics? — and (2) visual impact — the installation needs to photograph well for city social media, local press, and community memory. The headline names both.

## Section decisions

### Hero
- Image: Pride columns — the most obviously civic, publicly visible work in the portfolio. Immediately signals the page is for this audience.
- Eyebrow: "Civic & Community Events · Wasatch Front" — places them geographically and confirms the audience.
- H1: "Built for public events. Designed to photograph." — Names the two things civic buyers care about most.
- Lede: Specifics (parade arches, plaza moments, Pride, community fairs) — no generic "events" language.
- Single CTA to /contact with intent=civic-community pre-fill.

### Client proof grid
- Four category groups match the actual client roster in the brief: Cities & Counties, Pride & Equality, Chambers & Civic Orgs, Community Venues & Events.
- 4-column on desktop (even, no orphan rows), 2-column on mobile.
- Brass-ruled category labels with client names in soft gray — reads as a reference table, not a badge cluster.
- This is the "we've done your exact work" moment. A Sandy City coordinator sees Sandy City.

### Brass divider
- Three-dot with flanking rules — keeps section transitions quiet without adjacent full-width color sections.

### Proof stories
- Three installations chosen for civic scale: SLC Pride parade, Gallivan Center plaza, Ogden City municipal.
- Image → client attribution → headline → story body. Clean editorial pattern.
- 3-column on desktop. Each story is a real installation with honest copy — not inflated claim language.
- Ogden City story uses the Odoo library parade arch image (will be copied to production tree post-winner).

### Trust pillars (dark authority band)
- Navy band — single visual break in the warm-white dominant layout.
- Headline names the problem: "What public-event coordinators need from a balloon vendor" — speaks directly to the buyer's job.
- Four pillars: Parade & Street Events, Stage & Ribbon-Cutting, Professionally Invoiced (COI available — this is what city procurement needs), Utah Rooted.
- Brass icons from the brand icon suite.

### Audience service notes (stone band)
- Answers the "but how does it actually work?" question a coordinator asks before calling.
- Stone background separates from warm white without being a dark band — satisfies the "no adjacent colored full-width sections" rule since the trust band is navy and this is stone.
- Four cards with left brass border — civil, organized, easy to scan.

### Photo gallery
- 4-image 1:1 grid — pride columns, photo-moment, logo arch, seasonal.
- Shows civic and public-event range without over-claiming.
- Link to /portfolio for the deeper bench.

### Closing CTA
- Slate Blue background (distinct from the navy trust band above the service section, separated by two warm sections).
- Copy addresses the coordinator directly: "your team can focus on the event itself."
- Single berry CTA — plan your event quote.

## Photo choices
- `seasonal-pride-columns.webp` — hero + gallery: civic, publicly visible, immediately places the page
- `corporate-weberstock-photo-opt.webp` — proof story + gallery: scale, outdoor public event
- `corporate-logo-arch.webp` — gallery: branded arch, professional
- `seasonal-easter-rabbit-arch.webp` — gallery: community seasonal, family-safe civic range
- Odoo: `Parades/Standard arch for parade.png` — proof story for Ogden City (to be moved post-winner)

## Civic Procurement Cards — Render Hierarchy

The four Civic Procurement Notes cards each carry two heading levels inside the card. Build instances must render them as follows — do not collapse them to the same visual weight:

- **Italic category title** (e.g., "*City & County Accounts*") — eyebrow treatment: Lato, tracked uppercase, small (0.75rem / 11px), slate color, no bold
- **Bold card label** (e.g., "Invoicing") — card H3: Cormorant Garamond or Lato semibold, ~1.1rem, near-black
- **Body text** — Lato regular, base size

If both heading levels render at the same weight, the card collapses into a wall of text and the hierarchy is lost.

---

## Voice decisions
- "Built for public events" — not "perfect for" or "great for." Built implies engineering intent.
- "Designed to photograph" — honest and specific. Civic planners want the Instagram moment for the city.
- "Professionally invoiced" — not "easy billing." Directly names what city AP departments need.
- COI available on request — names the document without making it the centerpiece.
- No inflated client count claims (no "50+ Utah cities"). Only named clients from the approved roster.
