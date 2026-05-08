# Contestant 3 — Round 1 Submission

## Concept Name: "Made For You"

The four pages share a single structural discipline and a single voice register, but each one is built around the specific buyer's anxieties, vocabulary, and decision criteria — not around the company's generic message. Every page's H1, intro paragraph, CTA text, and proof selection is optimized for one buyer and would feel wrong on another page. That's the test: a civic coordinator reading the corporate page should feel like a guest in the wrong room.

---

## Architectural Skeleton — What "Made For You" Actually Means

The single most distinctive structural commitment across all four pages: **anxiety-first architecture**. Every page names the buyer's specific fear before it names any credential. The credential exists to answer the fear — not the other way around.

| Page | Buyer anxiety named first | Credential that answers it |
|------|--------------------------|---------------------------|
| Civic | Scale + weather + photographability | 26+ orgs / since 1998 / outdoor-capable |
| Corporate | Brand approximation / AP-invoice friction | Hex-matched, documented, AP-invoiceable |
| Schools | Late vendors / schedule disruption | "Shows up, installs, disappears cleanly" |
| Private | Personal weight / fear of generic | "Craft at personal scale" / specific occasion grid |

The test: a reviewer should be able to point to the anxiety-naming move on every page without being told where to look. If they can't, the architecture has failed.

This is what Contestant 8's version of "Made For You" cannot claim without doing the same editorial work. Generic "Made For You" concepts personalize the selling copy. This concept personalizes the *worry* first and lets the proof answer it.

---

## Suite Signature

**Structure:** Hero → Band(s) → Visual-field gallery → Dark authority band → CTA. The dark authority band changes position and color depending on the audience (slate for civic, slate for corporate, navy for schools, navy for private). No two adjacent full-width colored sections on any page.

**Voice register:** Quiet confidence throughout, but calibrated per audience:
- Civic: Americana authority, civic scale, public-facing
- Corporate: functional precision, AP-language, brand-safe
- Schools: schedule-aware, color-disciplined, reliability-focused
- Private: emotionally present, consideration-first, invitation posture

**Photo selection:** Every image is contextually matched. No generic balloon stock. Civic uses Pride parade/arch photos. Corporate uses logo arch, branded festival. Schools uses school stage and graduation garland. Private uses the most taste-elevated images in the library (organic arch, floral arch, foil heart).

**Proof strategy:** Each page uses the real roster aggressively but differently:
- Civic: full 26-client grid by city/org name
- Corporate: 30-client chip tags (breadth signal)
- Schools: short named roster extended by honest context items (not inflated)
- Private: no names (category-level proof + real testimonials selected for occasion-fit)

---

## Page Summaries

### /civic-community
Hero image: outdoor civic stage. H1 names the public-stage context. Slate stats band (26+ organizations, since 1998, outdoor-capable). Prose intro positions LT as civic infrastructure, not a party supplier. Pride + parade photo gallery. Full 26-client roster in navy grid. Four service cards (parade arches, civic columns, stage garlands, photo ops). Ink CTA with phone number.

### /corporate-events
Hero image: branded logo arch. H1 "On-brand. On-time. Invoice-ready." — three corporate mental checkboxes named directly. Two-column intro with prose left and three brass-rule callouts right (brand-color matched, AP-invoiceable, clean strike). Gallery shows brand activation work. Slate blue process steps (in buyer order: brief → approve → receive). 30-client chip roster. Navy CTA.

### /schools-campuses
Hero image: school stage display. H1 names the three school-buyer criteria: colors, installations, schedule. Warm-white intro addresses schedule anxiety first. Stone gallery with school/graduation/university work. 6-occasion cards covering the full school calendar (back-to-school through PTA). Short navy client band: named roster extended by honest context items. Ink CTA with specific action ("Tell us your school colors").

### /private-celebrations
Hero image: wedding organic half-arch (most elegant image in library). H1 is feeling-led: "The moment deserves something beautiful." Warm-white intro names the weight of private celebrations — including celebration of life — and promises craft at personal scale. Stats: 300+ birthdays, Wasatch Front weddings, "Every detail matters." Stone 6-up occasions grid with real portfolio photos. White testimonials selected for occasion-fit (loyalty, celebration of life, milestone quality, service recovery). Navy CTA: "Tell us what you're imagining."

---

## Technical Notes

- Every page: `no_cache = 1`, `sitemap = 1`, `get_context(context)` pattern from `home.py`
- CSS scoped to page namespace: `.lt-page-civic`, `.lt-page-corporate`, `.lt-page-schools`, `.lt-page-private`
- No new global CSS files. All styles delivered via `context.colocated_css` (matching home.py pattern)
- Hero heights: 220px mobile / 250px tablet / 280px desktop — contract enforced
- All image paths reference real files in the portfolio optimized tree or Odoo source tree
- All client names from the BRIEF curated roster — no invented clients
- Container modes documented per section in each DESIGN-NOTES.md
- No `!important`, no `head_html` injection, no off-guide fonts
