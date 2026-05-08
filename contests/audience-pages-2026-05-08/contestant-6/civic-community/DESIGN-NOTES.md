# Design Notes — Civic & Community

## Audience and buyer posture
City events coordinators, Pride organizers, chambers, county events, public-facing organizations. The buyer is often a staff coordinator who needs to justify the vendor to a committee. They need: evidence that LT has done civic-scale work before, confidence the install won't embarrass the city, and a quote process that respects their bureaucratic timing.

## Structural choices

### Hero
- Background: `seasonal-pride-columns.webp` — the cleanest civic-scale photo in the optimized library. Columns in public plaza context reads as authoritative without being narrowly scoped.
- Dark left gradient overlay maintains readability while letting the photo carry its own weight.
- Eyebrow: "Utah Civic & Community Events" — scopes the page for the right buyer immediately.
- H1: "Balloon decor built for Utah public life." — civic/geographic, no sticker language.
- CTA links to `/contact` with prefill `service=Balloon+Decor&intent=civic` to pre-scope the inquiry.

### Proof stats (dark ink band, section 3)
Four pillars, 2×2 mobile / 4-across desktop. Chose ink (not navy) as the background to visually separate from the navy roster section below. Pattern: warm-white → brass-dot divider → ink stats → warm-white photos → navy roster → warm-white services → sandstone process → slate CTA. No two adjacent colored full-width sections.

Stats chosen to answer civic coordinator concerns:
- "60+ civic events" — credibility number (cautious: said "60+" not a specific inflated count)
- "Since 1998" — longevity, Utah-rooted
- "Parade to Podium" — range of civic contexts covered
- "On-Site Install" — removes operational burden from the city coordinator

### Photo proof grid (section 4)
Six photos, 2-column mobile / 3-column desktop (balanced 2+2+2 / 3+3). Chose:
- `seasonal-pride-columns.webp` — Pride civic context
- `Progress Flag backdrop.png` (Odoo) — Equality Utah tie
- `Standard arch for parade.png` (Odoo) — literal parade arch, civic staple
- `rainbow columns.png` (Odoo) — Pride Center context
- `Love heart pride parade.png` (Odoo) — marching/parade proof
- `35_ Weberstock arch .png` (Odoo) — festival/community event

Captions name the client where known. No invented clients.

### Client roster (navy fullbleed, section 5)
All 26 civic clients listed with their category label. Grid layout so it reads as density of coverage, not a bulleted list. Navy ground separates visually from warm-white sections above and below without being another ink or slate surface.

The sub-copy handles the "if you're not listed" case — small civic orgs might self-exclude; this addresses that proactively.

### Service formats (section 6)
Four cards covering: arches, columns, parade float, stage backdrops. Chosen because these map to real civic event scenarios. Two-column desktop grid, full-width mobile. Icon + name + description — no prices, no SKUs.

### Process note (sandstone band, section 7)
Sandstone is the warmest surface in the palette — gives this section visual warmth without competing with the navy roster or ink stats. The 3-step process answers civic-coordinator concerns about timing and coordination. Copy avoids "we'll" — uses the company voice not the founder voice.

### CTA (slate blue fullbleed, section 8)
Slate blue is the third dark surface; by section 8 the eye has seen ink and navy. The CTA reiterates the specific civic contexts from the hero. CTA links to the same prefilled contact URL.

## Container contract
1. Hero — fullbleed
2. Brass-dot divider — raw-band
3. Stats — fullbleed (ink)
4. Photos — band (warm-white)
5. Roster — fullbleed (navy)
6. Services — band (warm-white)
7. Process — band (sandstone)
8. CTA — fullbleed (slate)

Adjacent fullbleed color check:
- Stats (ink) → Photos (warm-white): ✅ different
- Photos (warm-white) → Roster (navy): ✅ different
- Roster (navy) → Services (warm-white): ✅ different
- Services (warm-white) → Process (sandstone): ✅ different
- Process (sandstone) → CTA (slate): ✅ different

## Photo selection rationale
Led with Pride-context photos because SLC Pride, Pride Center, and Equality Utah are among LT's highest-visibility civic clients. Parade arch second because it's the most literal civic use case. Festival arch third to show non-Pride civic range. No photos invented or borrowed from irrelevant contexts.
