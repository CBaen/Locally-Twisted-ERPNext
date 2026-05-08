# Round 1 Complete — Contestant 5

## Concept summary

**Proof-First Buyer Suite.** Each page opens by naming the buyer's world in specific terms — their context, their pressure, their language — and then delivers real client proof immediately. Not a welcome mat. A credential check.

The four pages share a visual grammar (hero → dark proof band → photo proof → editorial story → audience-specific functional section → icon bar → CTA) but diverge substantially in tone, proof type, visual surface, and copy register:

- **Civic & Community** — dense credential grid (26 named clients), civic editorial copy, seasonal calendar note, and a service note covering outdoor durability and multi-location events. Dark Ink proof band. Photos: Pride columns, parade arches.
- **Corporate Events** — sector-labeled client grid (30 clients across 10 sectors), brand-safe editorial story calling out specific named clients and what those relationships required, 4-step numbered process section, and a unique AP/billing section (the only page with one). Slate Blue proof band.
- **Schools & Campuses** — small roster (3 named clients) displayed at editorial H2 scale with context labels, school calendar occasions grid with brass left-border cards, and a dedicated school color discipline section. Ink proof band.
- **Private Celebrations** — no named clients (privacy). Category-level proof with brass icon cards, portrait-oriented 6-photo grid on Sandstone background, 4 real testimonials from the review archive, and a dedicated memorial/celebration-of-life section that is the most emotionally careful writing in the suite.

## Technical compliance checklist

- ✓ Hero contract: 220px mobile / 250px tablet / 280px desktop, all four pages
- ✓ All styles in page-scoped `<style>` blocks with unique root class per page (`.lt-page-civic`, `.lt-page-corp`, `.lt-page-school`, `.lt-page-priv`)
- ✓ No `!important` anywhere
- ✓ No new global CSS files
- ✓ Extends `templates/web.html`
- ✓ Controllers: `no_cache = 1`, `sitemap = 1`, `get_context(context)` per pattern
- ✓ Container modes declared per section (fullbleed, band, visual-field)
- ✓ No two adjacent full-width colored sections
- ✓ All clients from approved roster only — no invented clients
- ✓ All photos reference real files (optimized portfolio + Odoo source paths)
- ✓ Cormorant Garamond headings, Lato body/UI throughout
- ✓ No light-blue, blush, pastel, or off-guide colors
- ✓ No sing-songy copy, no feature claims without proof
- ✓ `aria-hidden` on decorative icons, `aria-labelledby` on sections, min-height 44px on interactive elements
- ✓ `loading="lazy"` and `decoding="async"` on all below-fold images

## Distinctive moves

1. **Memorial section on private celebrations** — named explicitly, two paragraphs, invitation copy. Most competitors don't address this at all. It earns trust from the most emotionally vulnerable buyer.
2. **AP/billing section on corporate** — the only page with a procurement-specific section because it's the only audience where AP approval is a real hurdle before the quote can proceed.
3. **School color discipline section** — addresses the actual objection that burns school buyers with other vendors. Direct language: "School colors aren't suggestions."
4. **Sandstone background on private photos** — warmest palette surface, used only on this page. Signals that private celebrations are treated differently from civic/corporate work.
5. **Sector labels in corporate client grid** — "Banking & Finance" with four named clients in that sector does more work than an alphabetical list of 30 names.
