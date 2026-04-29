# ROUND-1-COMPLETE — Contestant 1

Round 1 deliverables are complete. All four required files have been written to the `contestant-1/` directory.

## What was built

Concept: **The Color Stage** — a customer-facing balloon decor design tool where customers tap a shape, color it like a coloring book with a curated palette of LT's actual balloon colors, and assemble multiple pieces on a shared visual "stage." The experience ends with a pre-filled inquiry form sent to Jeff — not a cart.

## Files produced

- `RESEARCH-NOTES.md` — 20 cited sources across all 6 research areas. Key findings from Virtualoon, BalloonBuilder, Gemar Creator, Fanfaire Design Studio, Baymard (mobile swatch UX), Pigment coloring app, Smashing Magazine (SVG pointer events), Frappe v15 documentation, and Milanote mood boarding.
- `REASONING.md` — ~900 words answering all 6 brief questions, each major design choice cited to a RESEARCH-NOTES source URL.
- `mockup/index.html` — gallery page linking all 6 screens with inline SVG previews and design principles summary.
- `mockup/styles.css` — single CSS file, brand-compliant (Teal #008080 CTA only, DM Serif Display 400, Raleway, 8px spacing scale), mobile-first 375px baseline, desktop 1280px expansion.
- `mockup/script.js` — single vanilla JS + jQuery file. No NPM, no build step. Color catalog array (50+ colors in 6 groups), DesignStudio state object, event delegation for SVG region taps, bottom sheet palette, swatch render helpers.
- `mockup/01-entry.html` — 7-shape gallery with SVG illustration cards.
- `mockup/02-color-one.html` — Balloon arch with 2 interactive fill regions, region chips, quick swatch row, bottom sheet palette.
- `mockup/03-picker.html` — Full 50+ color palette view with grouped families, hex code tooltip, recently used row, selected color callout.
- `mockup/04-composition.html` — 3-piece composition stage (Column + Arch + Backdrop) with piece list, edit-in-place tapping.
- `mockup/05-done.html` — Design summary with mini stage banner, plain-language piece list, pre-filled inquiry form, "Send to Jeff" CTA.
- `mockup/06-upsell.html` — Discovery moment: after coloring arch, suggested pieces (Garland, Bouquet, Centerpiece) shown in the CUSTOMER'S palette colors.

## Frappe-recreatable verdict (self-assessed)

PASS. All screens use only inline SVG, plain CSS, vanilla JS with jQuery (already in Frappe bundle), and standard HTML. No React, Vue, build step, or NPM module imports. CSS theme conflict risk mitigated by using page-scoped `<style>` blocks rather than `web_include_css`.

## Distinct angle

The key mechanic no other contestant is likely to have is the **color-inheritance discovery upsell**: when a customer finishes coloring a piece, the suggested next pieces are rendered in the customer's chosen colors — not in blank/neutral state. The customer doesn't see "add a Garland?" — they see *their* garland, in coral and champagne, already looking like it belongs. This collapses the gap between imagining and deciding.

Ready for Proxy reflective loops.
