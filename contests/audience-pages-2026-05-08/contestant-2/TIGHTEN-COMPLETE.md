# C2 — The Right Room — Tighten Complete

## What was done

### 1. Civic H1 sharpened (Tighten #1)
`civic-community/COPY.md`

Old: "Built for public events. Designed to photograph."
New: "The decor the city photographs. The install the coordinator stands behind."

Proxy direction: name the civic-professional context more precisely, name what the city coordinator is actually protecting (her organization's public image), name the attribution chain. The new line names both the artifact (the decor, in the city's own photographs) and the professional stake (the coordinator's standing behind the install). More specific than the capability statement it replaces.

---

### 2. Civic procurement card render hierarchy documented (Tighten #3)
`civic-community/DESIGN-NOTES.md`

Added a "Civic Procurement Cards — Render Hierarchy" section specifying:
- Italic category title → eyebrow treatment (Lato, tracked, small, slate)
- Bold card label → card H3 (Cormorant Garamond or Lato semibold)
- Body → Lato regular

Without this spec, a build instance makes a guess and the card hierarchy collapses.

---

### 3. "It is not a department. It is part of the work." — layout constraint documented (Tighten #2)
`private-celebrations/DESIGN-NOTES.md`

Added an explicit layout constraint block specifying that this sentence must render as an isolated paragraph with no adjacent content on either side. Named the failure mode (Frappe Rich Text stripping `<p>` tags), named the mitigation (spacers, `<br>`, explicit margin — whatever the surface requires), and named what's at stake: the whitespace is the mechanism, not decoration.

---

### 4. Schools Service Notes differentiated from Trust Pillars (Tighten #4)
`schools-campuses/COPY.md`

The Trust Pillars carry the summary claim (one line each). The Service Notes cards now carry operational detail the pillar text doesn't:

- Card 1: How color-matching actually works (hex/Pantone/athletic department guide → sourced across latex and foil)
- Card 2: How scheduling is confirmed (in writing before the event, install window specifics, custodian clearance)
- Card 3: What "family-friendly and safe" means operationally (non-toxic materials, background-checked crew)
- Card 4: How budget conversations actually go (ceiling-first, then what's possible within it — not top-down from an inflated proposal)

Buyer reads the pillar heading, gets the summary. Buyer reads the service card, gets the how. No more reading the same content twice in two visual treatments.

---

### Stretch goal: SLC Pride visibility stakes sentence (Stretch)
`civic-community/COPY.md`

Added one sentence to the SLC Pride proof story body, before the multi-year relationship note:

"When the parade coverage runs, these arches are in every photograph."

This closes the circle the proxy flagged — the proof story now names the specific visibility stakes of the install, not just the operational facts. The multi-year relationship note follows and carries its own weight as proof of trust.

---

## What was not changed

- Border-direction posture system — untouched (left-rule civic, top-rule corporate, bottom-rule schools, full-border private)
- "Something beautiful for a hard day." — untouched
- Schools intentionally-short roster framing — untouched
- Corporate page — no proxy tightens assigned to C2 for this page; untouched
- All HTML/Python implementation files — untouched (copy and design notes only)
