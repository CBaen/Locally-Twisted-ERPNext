# Round 1 Complete — Contestant 2

Contestant 2's round 1 submission is complete. The concept is **"The Coloring Book That Assembles Itself"** — a tap-to-fill SVG composition tool where a customer colors individual balloon regions via a bottom-sheet color picker, builds a multi-piece event composition with ghost-placeholder discovery upsells, and sends a design card to Jeff as an inquiry (no checkout, no price, no commitment).

All six deliverables are present and render without a server, build step, or NPM install:

- `RESEARCH-NOTES.md` — 6 research areas, 25+ cited URLs, all verified via WebSearch/WebFetch
- `REASONING.md` — ~700 words answering all 6 brief questions with research citations
- `mockup/index.html` — gallery linking all screens with iframe previews
- `mockup/01-entry.html` — shape selection grid (7 pieces) + starter combo cards
- `mockup/02-color-one.html` — SVG arch with tappable fill regions + bottom color bar
- `mockup/03-picker.html` — full bottom-sheet picker: recent-used row + hue-family tabs + 30-swatch grid + hex chip
- `mockup/04-composition.html` — 3-piece composition (arch + column + centerpiece) + strip selector + ghost placeholder
- `mockup/05-done.html` — design card capture moment + "Send to Jeff" CTA + Jeff's personal note
- `mockup/06-upsell.html` — discovery moment: colored arch + animated ghost column + suggestion panel with pre-colored preview
- `mockup/styles.css` — single CSS file, LT brand tokens, 8px scale, mobile-first
- `mockup/script.js` — vanilla JS + jQuery only, no build step, no CDN module imports

Stack: Frappe-native throughout. Inline SVG in HTML content type, jQuery from Frappe's bundle, `<style>` and `<script>` blocks on the page. No React, no TypeScript, no webpack, no forbidden primitives.
