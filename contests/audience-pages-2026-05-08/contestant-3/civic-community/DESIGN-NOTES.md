# Design Notes — Civic & Community Page

## Audience Read

The civic buyer is a city events coordinator, Pride organizer, chamber staffer, or county events manager. They care about:
- Scale: will this read across a public space?
- Weather: is this outdoor-capable?
- Photographability: will media get good images?
- Credibility: has this vendor worked at our scale before?

The roster answers all four implicitly. The proof stats band answers scale and longevity. The gallery shows real civic-context work.

## Structural Logic

**Section 1 — Hero (fullbleed):** Slate/Navy palette with the Back to School Stage image from Odoo (public-stage context, reads as civic-scale). Hero height strictly enforced: 220px mobile / 250px tablet / 280px desktop. One H1, eyebrow, short lede, one CTA.

**Section 2 — Stats band (slate):** Three numbers: 26+ orgs, since 1998, outdoor capable. Dark band breaks up the warm white sections. Compact — this is authority reinforcement, not a feature section.

**Section 3 — Intro prose (warm white):** Two paragraphs of quiet-confidence copy that name the civic context explicitly: parade floats that travel, stages that face thousands, outdoor conditions, clean strike. Positions LT as professional infrastructure, not a party supplier.

**Section 4 — Gallery (stone / visual-field):** Four real installed works from the roster. Pride float, Progress Flag arch, rainbow columns, back-to-school stage — all civic-context or community-facing. Photo captions use category label + title, no copy. The images do the work.

**Section 5 — Client roster (navy band):** Full 26-client civic roster displayed as a grid. Deep Navy ground with warm text creates authority. The sheer breadth of city names (SLC, Ogden, Sandy, Herriman, Kearns, Syracuse, Clinton, West Point, Hooper) signals Wasatch Front coverage.

**Section 6 — Services (warm white):** Four cards for the most civic-relevant pieces: parade arches, civic columns, stage garlands, photo ops. Body copy is functional and civic-specific ("parade-weight structures," "outdoor conditions," "community-facing photo ops"). No puffery.

**Section 7 — CTA (ink):** Dark closing panel with direct language. Phone number included because civic coordinators often need to call.

## Color Discipline

- No light blue, no blush, no pastel
- Sequence: civic image hero → slate stats → warm white → stone gallery → navy roster → warm white services → ink CTA
- No two adjacent full-width colored sections (stats/slate → intro/warm-white → gallery/stone etc. — each section breaks from the prior)

## Photo Choices

- **Hero bg:** Parades/Back to school stage display.png (civic stage, outdoor, community scale)
- **Gallery 1:** Pride/Iheart media pride float.png — real SLC Pride client, parade context
- **Gallery 2:** Pride/20_ progress flag arch.png — civic entrance, real Utah event
- **Gallery 3:** Pride/rainbow columns.png — community installation, colorful
- **Gallery 4:** portfolio/optimized/school-back-to-school-stage.webp — production install, stage scale

## Voice Notes

- "Utah's public stage" in H1 is civic Americana without being costume-patriot
- "Installations that hold up — and stand out" speaks to the coordinator's actual worry (outdoor durability) and the attendee's experience (visual impact)
- Roster label "Utah cities, organizations, and public venues that trust Locally Twisted" is a full claim — the list proves it

## Container Contract

| Section | Mode |
|---------|------|
| Hero | fullbleed |
| Stats | band (fullbleed wrapper, inner max-width) |
| Intro | band (contained inner) |
| Gallery | visual-field (fullbleed wrapper, inner max-width) |
| Roster | band (fullbleed wrapper, inner max-width) |
| Services | band (contained inner) |
| CTA | fullbleed (inner max-width) |
