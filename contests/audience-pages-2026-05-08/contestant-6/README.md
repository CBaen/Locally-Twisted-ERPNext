# Contestant 6 — Round 1 Submission

## Concept and Signature

**Design signature:** "Buyer-Scoped Authority"

Each page in this suite is designed to speak to one buyer and only one buyer, using their actual vocabulary, their actual concerns, and proof material specific to their world. The four pages share the same structural grammar (hero → dark authority stats band → photo proof → named proof → service formats → practical note → CTA) but vary every element of content, emotional register, dark-surface color choice, photo layout geometry, and unique sections to serve their specific audience.

The pages are a coherent suite — they look like siblings — but each one would make the right buyer feel immediately recognized.

---

## Page-by-Page Summary

### `/civic-community`
**Hero image:** `seasonal-pride-columns.webp` (civic plaza context)
**Stats band:** Ink dark ground
**Unique sections:** 26-named civic clients with category labels; process steps for civic event logistics (permits, wind exposure, load-in window)
**Emotional register:** Public-facing, Americana-proud, Utah civic authority
**Signature move:** The process steps section — civic coordinators have bureaucratic event structures; this page acknowledges the permit/timing reality explicitly

### `/corporate-events`
**Hero image:** `corporate-logo-arch.webp` (branded entrance)
**Stats band:** Ink dark ground
**Unique sections:** AP/accounts payable trust note (W-9s, Net-30, vendor registration); latex-free service card with named IHC/Mountain Star
**Photo layout:** Asymmetric — large hero photo left + 2×2 secondary grid right (editorial, not grid-uniform)
**Emotional register:** Brand-safe, billable through AP, professional
**Signature move:** The AP trust note — no other audience page has a section specifically addressing corporate vendor documentation requirements

### `/schools-campuses`
**Hero image:** `school-back-to-school-stage.webp` (stage backdrop)
**Stats band:** Slate blue ground (lighter than ink — family/K-12 appropriate)
**Unique sections:** Named institution cards (elevated treatment for 3 schools vs. flat list); scheduling practical note (bell schedules, gymnasium access, AV setups)
**Emotional register:** Spirit-driven, schedule-tight, school-colors-disciplined
**Signature move:** The scheduling note — the only page in the suite that mentions "bell schedules" and "custodial windows" by name; earns institutional credibility through operational knowledge

### `/private-celebrations`
**Hero image:** `wedding-organic-half-arch.webp` (intimate, personal, right-anchored)
**Stats band:** Ink dark ground
**Unique sections:** Four event-type moment blocks (Birthday / Weddings / Baby Showers / Milestones & Memorials) — each with full prose + 3-photo cluster; no named clients (privacy respected); quote notes list for buyer assurances
**Emotional register:** Personal, milestone-emotional, taste-elevated, gift-feeling
**Signature move:** Memorial/celebration-of-life treated as first-class occasion alongside birthdays and weddings — no other page on the LT site does this explicitly

---

## Suite Color Discipline

The dark authority band for each page uses a different ground color to reinforce the page's emotional register:
- Civic: Ink (public authority, historic)
- Corporate: Ink (professional severity)
- Schools: Slate Blue (lighter authority, family-appropriate)
- Private: Ink (intimate, dark/personal)

CTA sections rotate: Slate Blue (civic), Slate Blue (corporate), Navy (schools), Sandstone (private). No two adjacent full-width colored sections anywhere in the suite.

---

## Technical Compliance

- All 4 pages extend `templates/web.html`
- All 4 controllers: `no_cache = 1`, `sitemap = 1`, `get_context(context)`
- All heroes: mobile 220px / tablet 250px / desktop 280px
- All images: real file paths, no invented photos
- All clients: from the approved roster only, no inventions
- Page-specific styles scoped under `.lt-page-{name}` root class
- No `!important`, no global CSS, no new stylesheet files
- Container modes explicitly declared in template comments for every `.page_content` direct child
- No adjacent full-width colored sections anywhere across the four pages
- CTAs use `/contact` with prefill intent params (`?service=Balloon+Decor&intent=civic|corporate|school|private`)
- Accessibility: each section has `aria-labelledby`, decorative icons have `aria-hidden="true"`, images have meaningful alt text

---

## Image References

**From the optimized portfolio (production-ready):**
- `seasonal-pride-columns.webp` — civic hero + photos
- `corporate-logo-arch.webp` — corporate hero + photos
- `corporate-weberstock-photo-opt.webp` — corporate photos
- `corporate-wsu-arch-bouquets.webp` — corporate + school photos
- `school-back-to-school-stage.webp` — school hero + photos
- `school-grad-garland.webp` — school photos
- `birthday-smurfs-arch.webp` — private celebrations (birthday)
- `birthday-dolphin-backdrop.webp` — private celebrations (birthday)
- `birthday-balloon-bouquets.webp` — private celebrations (birthday)
- `wedding-organic-half-arch.webp` — private hero + photos
- `wedding-floral-half-arch.webp` — private celebrations (wedding)
- `wedding-foil-heart-arch.webp` — private celebrations (wedding)

**From the Odoo source library (path referenced, copy needed on win):**
- `Pride/20_ progress flag arch.png` — civic photos (Equality Utah)
- `Standard arch for parade.png` — civic photos (Sandy City)
- `Pride/rainbow columns.png` — civic photos (Pride Center)
- `Parades/Love heart pride parade.png` — civic photos (SLC Pride)
- `themed decor/35_ Weberstock arch .png` — civic photos (Ogden Weber Chamber)
- `themed decor/Logo arch.png` — corporate photos (retail activation)
- `latex free decor/ihc heart columns latex free.png` — corporate photos (IHC)
- `Photo opts/Back to school stage display.png` — school photos
- `Photo opts/Back to school stage display 2.png` — school photos
- `football/UofU football.png` — school photos (UofU)
- `Organic decor/Organic mothers day decor.png` — private (baby shower)
- `Organic decor/Organic half arch with white flowers.png` — private (baby shower)
- `Organic decor/organic column white flower add-ons.png` — private (baby shower)
- `Organic decor/Organic step and repeat.png` — private (milestones)
- `Organic decor/30_ Celebrate arch.png` — private (milestones)
- `Photo opts/Celebrate backdrop.png` — private (milestones)
