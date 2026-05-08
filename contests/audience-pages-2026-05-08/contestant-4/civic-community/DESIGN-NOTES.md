# /civic-community — Design Notes

## Audience

City events coordinators, Pride organizers, chambers (Ogden Weber, LGBT Chamber), county events staff (SLC County), and public-facing community organizations. Buyer posture: public-facing, civic-scale, photographable. Needs vendor who shows up on time and doesn't create a vendor-management problem.

## Structural Decision

7 sections:
1. Hero — fullbleed, civic photograph background, compact per contract
2. Authority band — dark ink ground, 4 proof pillars (icons from brand suite)
3. Case intro — warm-white, editorial heading to bridge to case cards
4. Case cards — 3-up grid, each anchored to a real client or cluster
5. Photo gallery — visual-field strip, 6 images, no captions (images are the proof)
6. Client roster — stone band, chip list of all 26 civic clients from roster
7. CTA — dark navy, direct contact invite

The page follows the approved color pattern:
`Warm White content → thin brass/slate rule → dark authority band → Warm White content → photo strip → stone → dark CTA`

No two adjacent full-width colored sections.

## Hero

- Background image: `seasonal-pride-columns.webp` — rainbow balloon columns, reads civic, photographable, community-scale
- Overlay: heavy left-side ink gradient so H1 is legible over the image
- Hero height: mobile 220px / tablet 250px / desktop 280px — strict contract adherence
- H1 intentionally avoids event-type enumeration in favor of a civic-civic posture statement
- CTA links to `/contact?intent=civic` to prefill context

## Authority Band

- Dark ink ground (#0A0A0B) creates authority anchor
- 4 pillars from approved icon suite: civic-parade, utah-rooted, professional, delivery-install
- Pillar body text explains what the label means to a city events buyer (not generic)
- "Insurance documentation available" — specific, meaningful to a procurement-minded buyer

## Case Studies

- 3 cases represent 3 distinct civic subsectors: Pride, City Events, Community Retail
- Each case names a real client cluster from the approved roster
- Images: optimized portfolio WebPs + Odoo source PNGs referenced by full path
- No invented clients, no inflated claims

## Photo Gallery

- 6 images in a horizontal strip — visual-field container mode
- Includes both optimized portfolio photos AND odoo-source images (by full path for implementation phase)
- No captions — per style guide: "Portfolio photos are not caption cards; use the image itself"
- Hover: gentle scale-up on individual photo (reduced-motion respected)

## Client Roster

- Stone (#E7E5E1) ground — visible separation from warm white without adjacent-dark-section violation
- All 26 civic clients from the approved brief roster appear
- Chip format: small bordered tags, not a paragraph list — scannable for a coordinator cross-checking their own network

## Service Note

- Audience-specific: explains city/public-event specific logistics (coordinated windows, insurance, city time)
- Service tag list anchors common formats without over-promising
- Lives on warm white, separated from clients by a 1px stone border rule

## CTA

- Deep Navy (#0E2240) ground — civic authority, not ink-heavy like authority band
- CTA links to `/contact?intent=civic` 
- Phone as secondary contact — civic buyers may prefer a direct call

## CSS

- All styles scoped to `.lt-page-civic` prefix — no global additions
- CSS lives in a `<style>` block at top of template — per brief requirement
- No `!important` used
- No new global stylesheets
- Uses CSS variables from lt-theme.css where available (`var(--lt-font-body)`, etc.)
- Fallback hex values used where var names may not cover: documented in code

## Photo Choices and Rationale

| Image | Source | Why |
|---|---|---|
| `seasonal-pride-columns.webp` | Optimized portfolio | Hero: pride columns = civic, community, public-scale |
| `seasonal-easter-rabbit-arch.webp` | Optimized portfolio | Case card: civic arch format proof |
| `corporate-weberstock-photo-opt.webp` | Optimized portfolio | Case card: community/retail event scale |
| `Progress Flag backdrop.png` | Odoo source | Gallery: pride community proof |
| `Parades/Rainbow heart parade.png` | Odoo source | Gallery: actual parade context |
| `Standard arch for parade.png` | Odoo source | Gallery: parade arch format |

All Odoo paths referenced as full Windows paths per brief: implementation phase handles copy.

## Accessibility

- One H1 on page
- Heading hierarchy: H1 → H2 (authority) → H2 (cases intro) → H3 (case cards) → H2 (clients) → H2 (service note) → H2 (CTA)
- All decorative images: `aria-hidden="true"`
- All content images: descriptive `alt` text
- Gallery section has `aria-label="Civic event photo gallery"`
- Client list: `role="list"` + `aria-label`
- All interactive CTAs: min 44px height
- Focus-visible states on all interactive elements
- `prefers-reduced-motion` respected for gallery hover
