# Contest Brief — Customizable Event Decor Design Tool

**Format:** 4 collaborative contestants. Synthesis (not winner-pick) presented to client.
**Mode:** stylized mockups + concise reasoning. No working code in this phase.

---

## 1. Want

A first-time customer arrives at the tool unsure what their event will look like. Within ~30 seconds they're picking colors and seeing a stylized illustration of a balloon arch in those colors. They pick a column shape and place it next to the arch — the column adopts colors they can adjust independently. They keep adding pieces — a centerpiece, a backdrop. The composition grows into THEIR event setup, viewable side-by-side. They walk away feeling "I made this. I want to talk about it now."

Two business effects:

- **The merchant opens the customer's saved composition and starts their pitch from THAT** — not from blank.
- **Customers add pieces they didn't come in for.** Coloring a column makes them realize a matching arch belongs there; adding the arch makes them realize a backdrop completes the look. The tool is a discovery mechanic, not just a configurator.

The aesthetic frame is **"design book / coloring book that's slightly nicer."** Stylized illustrations of each shape with discrete fill regions, colored from a curated palette. Browseable, scrapbook-feel, return-and-rearrange. Not a wizard. Not a configurator. Not a checkout.

## 2. Have

**Stack constraints:**
- Frappe v15 / ERPNext v15 (Python 3.11, Jinja templates).
- Plain CSS via `web_include_css`. Inline `<style>`/`<script>` permitted on individual pages.
- Vanilla JS + jQuery available. SVG inline rendering supported.
- Bootstrap 4 utility classes available.
- **No Node.js in production image** — no esbuild, no Webpack, no React/Vue build step. Anything more elaborate than vanilla JS + DOM/SVG would require infrastructure work this contest is not deciding.
- **Mobile is the primary surface.** Customers discover decor on phones (Pinterest browsing, planning during commutes). Desktop is secondary.

**The 7 parametric shapes in scope:**
- Balloon Arches
- Columns
- Garlands
- Picture Perfect Backdrops (also called walls)
- Balloon Drops
- Balloon Bouquets
- Centerpieces

**The color catalog:** 50+ unique balloon colors with hex codes. Customers must be able to see the hex while picking — they're often matching a venue, a dress, or a brand color and need to verify against an external swatch.

**The composition surface:** customers can design ONE shape, multiple shapes of the same type, or a mix of types. They place pieces near each other to see how they relate. Light arrangement (scrapbook feel), not architectural drawing.

**The output:** a design state that flows into a merchant's quote process. The format of that state — image render, JSON config, shareable URL, generated PDF — is downstream of this contest and intentionally out of scope. Design for the experience; persistence is a separate problem.

## 3. Won't Accept

- **Configurator-as-checkout.** Anti-pattern reference: `http://5.78.136.133/shop/what-we-make-balloon-arches-26/classic-organic-arch-99` — cascading attribute selectors that end in "Add to Cart." This is what to AVOID. No "buy now" button. No price displayed during design. The customization happens BEFORE the conversation, not at point of sale.
- **Photoreal rendering.** Stylized illustration only. Photoreal is the wrong fidelity (overpromises fixed dimensions/textures) and infeasible to build.
- **Wizard / linear flow.** No "step 1 of 4" framing. Customers must enter, do a little, leave, come back, do more — at any point.
- **Single-product focus.** This is a multi-piece composition tool. A design that only works for "your one arch" misses the point of the tool.
- **Visual overload.** Endless dropdowns, walls of 50+ swatches at once, overlapping selectors. Holds up at mobile width or it doesn't ship.
- **Hardware dependencies.** No camera, AR, or device-specific features. Runs on a typical mobile browser.
- **Build-pipeline dependencies.** Anything requiring `bench build` / Node-in-production / framework compilation is out of scope. Keep to vanilla JS + SVG + Jinja.
- **Save/share/return persistence design.** That's a separate problem; don't propose mechanisms for it. Show what the "captured" moment LOOKS like to the customer; how it's actually stored is downstream.

## 4. Open To

The contest is **collaborative, not competitive.** Every contestant wants every other contestant to win. Bring your distinct angle; score peers generously. The synthesis output is "absorb the best of all 4 into one recommendation," not "pick the winner."

Open architecturally:
- **SVG-based composition** is the likely strongest fit, but other directions (CSS grid + sprite color-mask, canvas, etc.) are welcome if a contestant believes they're better.
- **Color picker patterns** — palette tiles, hex-input boxes, recently-used row, eyedropper-from-image — propose what fits the "design book" feel.
- **Composition layout patterns** — fixed grid, free-arrange, horizontal scroll of "pages" — propose what holds up on mobile and feels book-like.
- **Number of fill regions per shape** — 1 (whole shape one color), 2-3 (e.g., main + accent), or many (per-balloon control) — your call. Argue for the level you pick.
- **The Proxy coach can suggest pivots** if a direction isn't producing the experience above. Listen.
- **Flag where you'd want to escape Frappe-native** if a primitive can't carry your experience cleanly. Don't silently exceed scope; raise it explicitly so synthesis can weigh the trade.

## 5. Questions

Each contestant produces stylized mockups + concise reasoning answering:

1. **What does coloring ONE shape look like?** Show the customer entering, picking a shape, applying colors from the palette. How do fill regions communicate themselves? How does the shape respond to selection?

2. **What does the COMPOSITION view look like?** Show 2-3 colored shapes living together — an arch + matching column + centerpiece. How does the customer see them side-by-side? How does the surface scale on mobile vs. desktop?

3. **How does the color picker handle 50+ colors?** Show how many are visible at once, how the customer navigates them, how the hex code surfaces, how a chosen color gets committed. Address scaling without overwhelming.

4. **What does the customer's "I'm done for now" moment look like?** They've designed something. They want to walk away (and probably return later). What does the tool show them? How does the design feel "captured" without specifying the persistence mechanic?

5. **What's the discovery upsell mechanic?** A customer who came for a column finishes coloring one. How does the tool surface that "an arch in these same colors would belong here"? Subtle suggestion? Visual hint? Empty placeholder waiting to be filled?

6. **What's the simplest version that captures the essence?** Articulate a v1 scope that's MINIMUM viable for the experience — not maximalist. Where would you cut to ship sooner? The "design book" frame argues for constrained surfaces; defend your floor.

## Format expected

- **Stylized mockups** for each key state: entry, single-shape coloring, color picker open, composition view (multi-shape), "done for now" state, upsell moment. Mobile + desktop where they meaningfully differ.
- **~500-700 words** of reasoning per contestant covering the 6 questions.
- **Peer scoring** of the other 3 contestants on: experience quality, scope discipline (no maximalism), Frappe-native fit, customer clarity. Score generously — finding what to BORROW is more valuable than what to reject.

The synthesis pass produces ONE recommendation that absorbs the best across all 4 + the Proxy coach's pivots. That recommendation is the input to the implementation phase (separate session).
