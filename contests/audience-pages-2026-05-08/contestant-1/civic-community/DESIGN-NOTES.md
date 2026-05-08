# Civic & Community — Design Notes

## Concept signature: "Civic Authority"

The civic page is designed to feel like something a Salt Lake City events
coordinator or a Pride organization's events director would recognize
immediately as their professional tier. Not a party shop. A civic infrastructure
provider that has done this at scale, repeatedly, for organizations like theirs.

## Page structure rationale

### 1. Hero
- Background: `seasonal-pride-columns.webp` — the strongest civic proof image in the
  optimized library. Columns at a Pride event say civic scale and civic color immediately.
- Image position: center 30% — brings the installation into view rather than cropping to sky.
- Overlay: heavy left-to-right gradient so the text is readable on mobile without
  obscuring the installation. The right third of the image bleeds through on desktop.
- Copy: "Utah's civic and community events, visually led." — editorial, civic-authority,
  no exclamation points. References the work as visual infrastructure, not decoration.

### 2. Proof stats row
- Placed immediately after the hero on a Slate Blue band — the "dark authority" panel
  per style guide pattern. Creates a visual stop before the lighter story section.
- Four cells: cities served, years, Pride reach, Wasatch Front range.
- Numbers are provable from the roster (20+ cities confirmed). No inflation.

### 3. Case story
- Uses a two-column layout on tablet/desktop: photo left, narrative right.
- Narrative focuses on WHY civic installations are different: they get photographed
  by press, they represent the organization that hired LT.
- Names SLC Pride, Pride Center, Equality Utah, LGBT Chamber, and "8+ city governments"
  — all verifiable from the roster.

### 4. Photo gallery
- Visual-field mode. Stone background.
- 2-column mobile / 3-column desktop.
- First item spans 2 columns (wide aspect ratio) to give the Pride installation
  the hero treatment it deserves as the strongest visual.
- Includes notes to implementation team referencing Odoo library for additional
  civic photos (parades, Progress Flag backdrop, Rainbow heart parade).

### 5. Client name grid
- White background on a band — creates visual alternation with the stone gallery
  above and near-white services section below.
- 26 organizations displayed in a bordered grid, each with name and category.
- Heading: "Utah organizations that trust Locally Twisted" — possessive proof,
  not a boastful claim.

### 6. Audience services
- Near-white background. Four cards with brass top-border accent.
- Cards describe the SPECIFIC civic needs: outdoor durability, all-day anchoring,
  civic photography, clean strike. Not generic balloon descriptions.
- Icons from the brand suite.

### 7. CTA
- Deep Navy fullbleed. Berry button.
- Copy: "Tell us about your event." — per voice guide ("Invite, never push").
- CTA prefills `/contact?service=civic` so the form can scope the inquiry.

## Photo choices and reasoning
- Hero: `seasonal-pride-columns.webp` — biggest civic proof available
- Story: Same image (acceptable since it's a different crop/presentation)
- Gallery: Mixes civic-adjacent portfolio images from the optimized set;
  references Odoo library for additional civic-specific photos

## Audience-specific moves
- Uses the word "photographed" prominently in copy — this is what civic event
  coordinators think about. Press coverage, social media, constituent photography.
- "Clean strike" appears twice — facilities managers care about this.
- Client grid leads with Pride organizations before city governments — the
  most distinctive civic clients LT has, the ones that differentiate from
  every other balloon company in Utah.

## Container discipline
- Hero: fullbleed (lt-fullbleed class)
- Proof row: fullbleed (dark band — treated as fullbleed visual)
- Story: band (contained max-width inner)
- Gallery: visual-field
- Client grid: band
- Services: band (near-white)
- Buyer notes: band (slate-blue) — **added Loop 1-2**
- CTA: fullbleed (navy)

No two adjacent full-width colored sections — confirmed:
- Hero (dark on image) → proof row (slate, fullbleed) → story (warm white, band)
  — the proof row is a thin accent band, not a full content section;
  it reads as a visual separator between hero and story.
- Services (near-white) → buyer notes (slate-blue) → CTA (navy): three distinct
  bands, no adjacency conflict.

## Loop 1-2 change: Civic buyer notes section added

Proxy-Loop-1-2 identified that the civic page had aesthetic differentiation from
corporate but lacked the civic room's equivalent of corporate's operational-proof
section (AP invoicing, COI, brand color, multi-location). A Sandy City coordinator
also submits vendor documentation — she deserved the same operational specificity.

Added `CIVIC_BUYER_NOTES` with four cards: Vendor Documentation (W-9, COI),
Permit-Friendly Coordination, Invoicing for Government Accounts (PO, net-30,
department billing), and Multi-Venue or Annual Events. Rendered in a slate-blue
band with brass left-rules — visually distinct from the corporate buyer notes
(which are on a lighter stone band), but structurally parallel.

The civic room now has its own version of operational proof, not just different
aesthetics from corporate.
