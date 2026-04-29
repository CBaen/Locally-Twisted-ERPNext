# Reasoning — Contestant 2
# Customizable Event Decor Design Tool

~600 words covering the 6 design questions from Brief Section 7. Each major choice cites a URL from RESEARCH-NOTES.md.

---

## Distinct Angle

My framing: **the Coloring Book That Assembles Itself**. The customer arrives at a canvas that already contains one illustrated shape — a blank arch ready to be colored. They tap a region, the bottom picker slides up, they choose teal. The arch comes alive. They notice an empty "ghost" column placeholder to the right. They tap it, it materializes, they color it. The composition grows by invitation, not by instruction.

This is distinct from the pro-tool model (BalloonBuilder, Virtualoon) which requires learning layers and generators. It's distinct from the configurator model (dropdown cascades ending in Add to Cart). It's closest to PilaMania's inquiry flow — but instead of a 3D render, it uses flat illustrated SVG that feels like a coloring book page, which has lower production cost and works better inside Frappe.

---

## Q1: What does coloring ONE shape look like?

The customer taps on any region of the SVG illustration — say, the main body of a balloon arch. The region highlights (a soft teal ring appears around it, 2px). A bottom sheet slides up from below — this is the mobile-native pattern confirmed by Recolor's "swipe from bottom" mechanic (https://diycandy.com/best-adult-coloring-apps/).

Fill regions communicate themselves through subtle dotted outlines on uncolored areas — like a coloring book's black-line regions waiting for color. Selected regions get the ring indicator and a brief scale-pulse animation (CSS `transform: scale(1.03)` at 150ms, then back). The shape responds to selection by showing its region labels (e.g., "main balloons," "accent balloons," "base ring") as small tooltips on first visit.

Technically: inline SVG with named `<path>` elements. jQuery event delegation on the SVG container reads `event.target.dataset.region`. Fills set via `$(target).attr('fill', selectedColor)`. Confirmed feasible via https://gomakethings.com/detecting-click-events-on-svgs-with-vanilla-js-event-delegation/ and https://copyprogramming.com/howto/javascript-svg-fill-jquery-in-click. `pointer-events: none` on stroke paths prevents accidental taps (https://www.smashingmagazine.com/2018/05/svg-interaction-pointer-events-property/).

---

## Q2: What does the COMPOSITION view look like?

At 375px: a horizontally scrollable strip of shaped tiles at the bottom, with a larger "canvas area" above showing the current composition. Pieces appear as illustrated SVG thumbnails in the strip. Tap a piece in the strip to bring it to focus for coloring. The canvas above shows all added pieces side-by-side at a smaller scale.

At 1280px: the strip becomes a left sidebar. The canvas fills the center. A right panel shows color summary for the current piece.

The "growing board" metaphor comes from Milanote's pattern (https://milanote.com/templates/moodboards/wedding-moodboard): you start with one element; the composition expands as pieces are added. A ghost placeholder for the next-most-popular addition is always visible at the right edge of the canvas — the discovery upsell lives here.

I deliberately avoid free-drag positioning because (a) it's hard at 375px and (b) it introduces a spatial reasoning task that slows customers down. Fixed left-to-right arrangement with depth implied by illustration (arch behind, column to side) conveys "this is MY event setup" without requiring the customer to design space.

---

## Q3: How does the color picker handle 50+ colors?

Three-component picker in a bottom sheet:
1. **Recently Used** — a row of up to 6 swatches at top (localStorage-backed, confirmed feasible via https://bams-thinkery.ca/tools/color-picker)
2. **Hue-family filter tabs** — 6 small tabs (Reds/Pinks | Blues/Purples | Greens | Yellows/Oranges | Neutrals | Darks). Each shows ~8-10 swatches. Tabs scroll horizontally if needed. This solves the 50+ problem by chunking into 10-item groups, confirmed as the right chunk size by https://www.uxpin.com/create-design-system-guide/build-color-palette-for-design-system.
3. **Hex code display** — tapping any swatch shows its hex code in a read-only chip below the swatch grid. Customers matching venue colors can verify hex (confirmed as essential by https://mobbin.com/glossary/color-picker and the Pigment guide https://emma-rose-portfolio.com/blog/pigment).

I explicitly omit a custom hex input field in v1 (see "simplest version" below). A read-only hex display meets "customers need to verify their hex" without the complexity of hex-input validation.

Selection indicator: a 2px teal ring around the chosen swatch (Mobbin pattern). Commit by tapping "Apply Color" or by tapping a second swatch (previous apply auto-commits).

---

## Q4: What does the "I'm done for now" moment look like?

The customer has colored 2-3 pieces. They tap "I love this — save my design." A full-screen snapshot summary appears: the composition at full-width with a color palette strip below it (showing every hex they used). Below that: two options — "Start over" (ghost button) and "Send this to Jeff" (teal CTA button).

The "captured" feeling comes from the snapshot layout — it looks like a design card, like something that could be printed or shared. No discussion of persistence mechanics to the customer. The experience reads as "this is done, it's saved, Jeff will see it."

This pattern draws from PilaMania's "add to your request... you decide when it's ready" framing (https://www.pilamania.com/en/products/3d-color-designs/): no purchase pressure, just capture.

---

## Q5: What's the discovery upsell mechanic?

After a customer finishes coloring an arch, a ghost placeholder column appears to the right of it in the canvas — sketched in light gray, labeled "+ Add a column?" with a small "matches your colors" note. This is always visible, never modal or forced.

The customer taps the ghost → the column materializes with the arch's primary color pre-applied. They can adjust independently. The column's appearance unlocks a ghost backdrop behind both pieces.

This cascading ghost pattern draws from Fanfaire's SWAP mechanic (https://www.fanfaire.io/design-studio) but inverted: instead of swapping, we're offering the next natural complement. The key is that the ghost column is already in the right visual position relative to the arch — the customer doesn't have to imagine placement.

---

## Q6: Simplest version — the minimum viable floor

**v1 scope**: one shape at a time, no composition. The customer picks ONE shape (arch, column, garland, backdrop, drop, bouquet, centerpiece) from 7 illustrated tiles. They color it using the bottom picker. They tap "Send this to Jeff" which pre-fills a contact form with the shape name + hex codes.

What this removes: composition canvas, ghost placeholders, multi-piece side-by-side view, recently-used row, hue-family tabs (flat grid of 20 colors instead).

**Defense**: the brief's core want — "within 30 seconds they're picking colors and seeing a stylized illustration in those colors" — is fully met. The "I made this, I want to talk about it now" moment happens even without multi-piece composition. The inquiry outcome (Jeff sees what the customer envisioned) is fully achieved. Everything beyond v1 is discovery/upsell layering that increases inquiry value but isn't load-bearing for the core experience.

---

## Frappe-Native Fit

The full tool lives in a single `www/design-studio.html` portal page with a `www/design-studio.py` controller. Inline SVG is in the page HTML (confirmed: Web Page HTML content type supports arbitrary HTML including SVG). CSS is in a `<style>` block on the page. JS uses jQuery (already in Frappe's bundle) with vanilla DOM. No CDN fetches, no NPM, no build step. The inquiry form submits via Frappe's `frappe.call()` to create a Lead — consistent with the LT form-handler routing in CLAUDE.md.

No forbidden primitives used. No flags to raise.
