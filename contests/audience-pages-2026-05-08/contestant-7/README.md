# Contestant 7 — Audience Pages Suite

## Concept: The Proof is in the Place

Each page is built around the specific people, places, and occasions that Locally Twisted actually serves. The concept refuses generic event-company copy in favor of specificity: named cities, named institutions, named networks of organizations, named calendar moments. Every section answers a real buyer question rather than pitching.

The suite has a deliberate visual architecture that makes each page feel distinct for its buyer while maintaining the brand system across all four.

---

## Design Signature

### What makes this suite distinct

**1. Buyer-calibrated authority posture.**
Each page speaks in the register its buyer uses in their professional life.

- Civic buyers get the language of municipal procurement and event operations.
- Corporate buyers get brand-accountability language: PMS values, AP billing, repeatable process.
- School buyers get academic-calendar language: venue windows, institutional colors, ceremony timing.
- Private buyers get emotional acknowledgment with operational specificity underneath.

**2. Roster-as-proof, not roster-as-decoration.**
The named client lists are presented in ways that support the specific buyer's pattern-matching, not as generic credential walls. Civic clients appear as tags because a city coordinator will scan for peer cities. Corporate clients appear in sector groups because a marketing director will scan for peer-industry relationships. School clients appear in an editorial ledger because three named schools deserve three named moments, not a thin tag cloud.

**3. Photo choices matched to buyer context.**
No photo appears on a page where it doesn't speak to the audience's world. The corporate page uses the branded arch and WSU institutional work. The school page uses the stage backdrop and graduation garland. The private page uses wedding arches because those are the tasteful, intimate installations that a private buyer is imagining.

**4. Privacy as an explicit commitment on the private page.**
The brief says the private buyer expects privacy. This suite names it directly in two places: the intro copy and the capability bar. "Private by Default" is a promise, not a footnote.

**5. Consistent container discipline across the suite.**
Every page follows the same fullbleed/band/visual-field pattern. Hero contract (220/250/280px) enforced on all four. No adjacent full-width colored bands. No `!important`. No new global CSS — all styles are page-scoped under `.lt-page-civic`, `.lt-page-corp`, `.lt-page-school`, `.lt-page-private`.

---

## Page-by-page summary

### `/civic-community`
**Buyer:** City coordinators, Pride organizers, chambers, county events teams.
**Anchor photo:** `seasonal-pride-columns.webp` (Pride parade columns — civic scale established immediately)
**Distinctive move:** All 26 civic/community clients from the approved roster presented as scannable tags. Client roster is the biggest on any page — this buyer has the widest peer network to scan.
**Key copy:** "When the city puts it on a banner, the balloons have to hold up." — Civic accountability in one sentence.

### `/corporate-events`
**Buyer:** Marketing directors, brand managers, event planners at companies.
**Anchor photo:** `corporate-logo-arch.webp` (branded entrance arch — brand-accountability framing established immediately)
**Distinctive move:** Corporate clients grouped by industry sector (Financial Services, Media & Broadcast, Hospitality & Dining, Healthcare) — a marketing director finds their sector, sees peer brands, stops scanning.
**Key copy:** "On brand. On time. On record." — Three corporate buyer concerns in three beats.

### `/schools-campuses`
**Buyer:** Activity directors, graduation coordinators, athletics staff, student life offices.
**Anchor photo:** `school-back-to-school-stage.webp` (stage backdrop — assembly/event scale for activity directors)
**Distinctive move:** Three named schools presented as an editorial ledger with brass rule separators — the small roster is presented with dignity rather than hidden in a tag cloud. Academic calendar moments (Graduation, Back-to-School, Campus Events) drive the proof section.
**Key copy:** "School colors mean something. The installation should too." — Color-matching commitment in two sentences.

### `/private-celebrations`
**Buyer:** Birthday families, wedding planners, baby shower hosts, memorial organizers.
**Anchor photo:** `wedding-organic-half-arch.webp` (organic wedding arch — intimacy and taste established immediately)
**Distinctive move:** No named client roster (brief explicitly says privacy expected). Uses category-level proof (300+ birthday installs, weddings across the Wasatch Front), anonymized testimonials (first name + event type only), and the explicit "Private by Default" capability claim.
**Key copy:** "The room should feel like it was made for this moment." — The most editorial H1 in the suite. This buyer reads differently.

---

## Technical notes

All four pages:
- Extend `templates/web.html`
- Use `no_cache = 1`, `sitemap = 1`
- Include `get_context(context)` with appropriate meta tags
- Use only page-scoped CSS (`<style>` block at template top, scoped under page-specific root class)
- Reference real images from the optimized portfolio library (`/assets/locally_twisted/images/portfolio/optimized/`)
- Reference real brand icons from the SVG suite (`/assets/locally_twisted/icons/brand/`)
- Honor the hero contract (220px mobile / 250px tablet / 280px desktop)
- Use `lt-fullbleed` for full-bleed bands
- Include `aria-labelledby` on all major sections
- Use `aria-hidden="true"` on decorative icons and bg images
- Include `min-height: 44px` on all interactive elements (CTAs)
- Pass `?intent=` parameter on all CTA links for contact form pre-population
