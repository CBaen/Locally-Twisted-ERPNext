# Round 2 Complete — Contestant 3

## Path taken: B-lean (Commit Harder)

## What changed

### Private celebrations — structural surgery (primary fix)

The Round 1 private page named the memorial buyer in intro prose ("A memorial is how a community says goodbye") but then handed them card slot 5 of 6 in a uniform occasions grid. The architecture and the prose were out of sync.

Round 2 adds a dedicated `lt-priv-memorial` section (slate background, two-column desktop layout) positioned **between the intro band and the occasions grid**. The grief buyer is claimed before they ever encounter birthday or wedding content. KJSCOTT's review anchors the section as the structural proof — left brass-rule callout, italic quote, attribution with "Celebration of Life" context label. The CTA in that section reads "Start a conversation" rather than "Request a quote" — calibrated for emotional register.

KJSCOTT is not repeated in the testimonials section. One structural home, full weight.

The occasions grid is now 5 cards (memorial removed). Testimonials section is 3 cards (KJSCOTT absent).

The anxiety-first architecture is now fully executed on the private page: the buyer's specific fear (am I in the right place for something this heavy?) is answered before they have to self-select.

### Civic — category-grouped roster (secondary fix)

The Round 1 civic roster was a flat chip list. Round 2 groups into four labeled categories:
- Cities & Counties (9 entries)
- Pride & Equity Organizations (4 entries)
- Chambers & Economic Organizations (4 entries)
- Community Venues & Events (9 entries)

The city events coordinator's eye can now scan by type — a county fair coordinator finds herself in "Cities & Counties" immediately; a Pride organizer finds "Pride & Equity Organizations" without reading the full list. The category label acts as a proof signal on its own: breadth across four distinct civic types.

CSS added: `lt-civic-roster__groups` 4-column grid on desktop, each group with brass-rule category label separator.

### Corporate and Schools — held

Corporate's anxiety-first H1 ("On-brand. On-time. Invoice-ready.") is the most direct expression of the architecture in the suite and was not flagged as a weakness. Schools names the schedule anxiety in intro copy and service cards. Both held.

## The test this round must pass

A reviewer opening the private page should find the memorial buyer claimed in a dedicated structural section — with proof — before the occasions grid begins. Without being told where to look.

That test now passes.

## Files changed

- `private-celebrations/private_celebrations.py` — KJSCOTT separated from testimonials list, new `kjscott` context var, memorial section CSS added, occasions grid reduced to 5 cards
- `private-celebrations/private_celebrations.html` — new `lt-priv-memorial` section added between intro and occasions grid; section count 5→6
- `private-celebrations/COPY.md` — updated to reflect 6-section structure, KJSCOTT placement documented
- `private-celebrations/DESIGN-NOTES.md` — structural logic updated, container contract updated to 6 sections
- `civic-community/civic_community.py` — flat `CIVIC_CLIENTS` list replaced with `CIVIC_CLIENT_GROUPS` grouped dict, CSS added for grouped layout
- `civic-community/civic_community.html` — roster section updated to render groups with category labels
- `civic-community/COPY.md` — roster section updated to show grouped format
