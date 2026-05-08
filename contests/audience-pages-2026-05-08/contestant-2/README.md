# Contestant 2 — Round 1 Submission

## Concept name: "The Right Room"

Each audience page is designed so the buyer immediately knows they are in the right room — not in a generic events company lobby, but in the specific space built for their kind of event, their kind of constraint, their kind of proof.

The suite's governing principle: **make the buyer feel recognized before they read a word.** Image choice, hero line, client proof grid structure, and the emotional register of the body copy are all calibrated to the specific buyer posture described in the brief.

---

## Signature moves

### 1. Buyer-specific card treatment variation
Each page uses a different brass accent treatment for its service/info cards:
- Civic: left brass border (authority, document-like)
- Corporate: top brass border (header-style, AP-document)
- Schools: bottom brass border (footer-like, understated — appropriate for tighter budgets)
- Private: full brass border (all-around, enclosing — personal, envelope-like)

Same design system. Different posture per audience.

**The posture logic (for build instances — do not apply the wrong border to a new section):**

- **Left-rule** signals "here is information I trust you to receive." The card presents itself as a document or reference — lateral, deferential, civic in register. Used for an audience that processes information through official channels (coordinators, permitting offices, chamber staff).
- **Top-rule** signals "this leads; you follow." The card presents itself as a header — authoritative, agenda-setting, appropriate for a B2B professional audience that expects vendor communications to be structured and AP-formatted.
- **Bottom-rule** signals "this supports, it does not headline." The card is a quiet footnote — present but not demanding attention, appropriate for an audience where budget sensitivity means the vendor shouldn't perform more authority than the buyer has.
- **Full-border** signals "this is for you, personally." The card encloses — envelope-like, all-around — appropriate for an audience making personal, emotionally-weighted decisions where the decor matters because the moment matters.

A build instance adding a new card section to one of these pages MUST use the border direction assigned to that page's audience. Mixing border directions across sections on the same page breaks the posture signal without the buyer consciously noticing — but they will feel it.

### 2. Honest proof posture
- Civic and corporate: large named-client tables showing industry breadth
- Schools: short roster presented as a feature ("deep relationships, not a long shallow list")
- Private: no named clients (privacy preserved), substituted with Google review voice and category-level proof
- No inflated claims, no invented clients, no padded stats

### 3. Copy calibration per emotional register
- Civic: operational/civic authority ("publicly photographable," "coordinated delivery and strike")
- Corporate: B2B professional ("load-in window," "invoiced through accounts payable," "COI available")
- Schools: school-specific operational language ("before the first bell," "before the custodians need the space"), and honest budget acknowledgment
- Private: invitation and care ("Tell us what you're imagining," "It is not a department. It is part of the work")

### 4. Dark band placement strategy
Every page has one dark authority band (navy or slate), placed at a different position in the section sequence so the visual rhythm doesn't feel formulaic:
- Civic: trust band is section 5 of 8 (middle)
- Corporate: trust band is section 4 of 8 (before service notes), process bar is navy section 7
- Schools: trust band is section 4 of 8 (same structural slot)
- Private: trust band is section 5 of 8 — after the customer voice, before service notes

### 5. Hero image discipline
All four heroes use distinct images that immediately signal the audience:
- Civic: Pride columns (most obviously civic, public, Utah)
- Corporate: Corporate logo arch (brand-matched professional install)
- Schools: Back-to-school stage (gym scale, unambiguously school)
- Private: Wedding organic half arch (elevated taste, private register)

---

## Page summaries

### /civic-community
Eight sections. Hero (Pride columns) → Named client table in four civic categories → Three proof stories (SLC Pride, Gallivan Center, Ogden City) → Navy trust band (four civic pillars) → Stone service cards with left brass border → 4-image gallery → Slate CTA. Voice: operational civic authority with honest logistics language.

### /corporate-events
Eight sections. Hero (corporate logo arch) → Five-column industry client table → Three proof stories (WeberStock, Brand Entrances, IHC/Healthcare) → Slate trust band → Warm-white service cards with top brass border → Stone photo strip → Navy process bar (inline step sequence) → Ink closing CTA. Voice: B2B professional. AP-language throughout.

### /schools-campuses
Eight sections. Hero (back-to-school stage) → Honest small-roster pill display with explanatory note → Three proof stories (WSU, Back-to-School Stage, Graduation) → Navy trust band with school-specific pillars → Warm-white event type matrix (8-chip, 4×2 grid) → Sandstone service cards with bottom brass border → Warm-white gallery → Navy CTA. Voice: operational school-logistics language; honest budget acknowledgment.

### /private-celebrations
Eight sections. Hero (wedding organic half arch) → Four celebration-type panels in 2×2 grid (Birthdays/Weddings/Showers/Celebrations of Life) → Brass divider → Stone customer voice grid (four real Google reviews, first-name attribution) → Navy trust band → Warm-white service cards with full brass border → Sandstone gallery → Slate CTA. Voice: warm invitation, elevated care for the grief context.

---

## Technical contract (per section, per page)

All pages:
- Extend `templates/web.html`
- `no_cache = 1`, `sitemap = 1`
- Hero: 220px mobile / 250px tablet / 280px desktop (hard-coded via page-scoped CSS)
- All `.page_content` direct children have declared container modes in comments
- Page-specific CSS scoped to `.lt-page-{slug}` root class
- No `!important` chains
- No new global stylesheets introduced
- All images referenced by path (not copied)
- Icon SVGs from `/assets/locally_twisted/icons/brand/` suite
- `aria-hidden="true"` on all decorative icons and images
- One `<h1>` per page; no skipped heading levels
- All interactive elements have visible focus states (via page-scoped `:focus-visible` inheriting from global)
- Minimum 44px touch targets on CTAs

---

## Odoo library images referenced (require moving to production tree post-winner)

- Civic proof story (Ogden City): `C:/Users/baenb/projects/locally-twisted-odoo/assets/image assets/photos for website/Parades/Standard arch for parade.png`
- Corporate proof story (IHC): `C:/Users/baenb/projects/locally-twisted-odoo/assets/image assets/photos for website/Mock up IHC.png`

Both images exist and are confirmed in the Odoo library. The implementation phase will copy them to `apps/locally_twisted/locally_twisted/public/images/portfolio/`.
