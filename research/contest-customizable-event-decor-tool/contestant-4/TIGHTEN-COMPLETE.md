# Tighten Complete — Contestant 4

Four targeted changes applied per Proxy tightening notes. No redesign, no structural changes.

**1. Empty recently-used row fixed (`02-color-one.html` + `script.js`).** The 8 hardcoded `.swatch-circle.empty` divs — which read as a loading failure on first open — are replaced with a hide-until-populated pattern. The recents section (`#picker-recents-section`) is hidden by default and shown only when `_buildRecents()` finds at least one color in `DesignState.recentColors`. A placeholder line ("Colors you pick will appear here") occupies the space when the row is empty, so the customer understands the space's purpose without seeing a broken-looking blank row.

**2. Entry screen warmth pass (`01-entry.html`).** Added a welcoming headline above the instruction band in DM Serif Display: "Pick your piece, pick your colors — we'll take it from there." with a secondary line "No experience needed. Nothing to buy." This gives the first-time parent the emotional permission slip the entry screen was missing — the Proxy's note that it was "most functionally clear but least emotionally inviting" is addressed without touching the shape grid or instruction band.

**3. Centerpiece removed from entry screen (`01-entry.html`).** The Centerpiece shape card was still present in the entry grid despite being out of scope per PRODUCT-DETAILS.md Section 2.7. Removed. The grid now shows the 6 in-scope shapes (Arch, Column, Garland, Backdrop, Balloon Drop, Bouquet) plus the View Design card.

**4. Ghost arch inherits customer palette at legible opacity (`06-upsell.html`).** Ghost arch opacity raised from 0.25 to 0.35 and the circles now alternate the customer's actual Teal (`#007878`) and Reflex Gold (`#D4A017`) colors in an A-B pattern matching the column's palette — same colors the customer already picked, already on the arch they're being invited to add. This lifts the upsell from "generic ghost prompt" to "this is what your arch would look like," without building the full cascade or breaking the 2-region simplicity argument.
