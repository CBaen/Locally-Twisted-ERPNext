# Reasoning — Contestant 4
## "The Coloring Book" Design Concept

---

## Concept Frame

The tool is called a Design Studio in LT's decisions log, but the metaphor I'm designing toward is a **coloring book page**. The customer arrives at an open spread. There are a few outlined illustrations of balloon pieces waiting for color. They tap a shape, pick colors from a curated palette, watch it come alive. They add another piece next to it. The spread fills in. When they're done, they screenshot it or tap "Discuss This Design" — and Jeff gets a lead with a visual attached.

This frame is grounded in the brief's own language: "design book / coloring book that's slightly nicer." I am taking that literally.

---

## Q1: What does coloring ONE shape look like?

The customer taps a shape card on the entry screen (e.g., "Balloon Arch"). A dedicated color view opens with an inline SVG illustration of the arch. The arch is drawn with 2-3 named fill regions: the main balloon body fill, an accent balloon fill (every third balloon in the pattern), and optionally a trim fill. These regions are distinguished by a thin outline — the same visual language coloring books use.

When the customer taps the main region, it pulses with a subtle scale animation (1.0 → 1.02 → 1.0, CSS transition) and the color picker opens at the bottom of the screen. The region is visibly "active" — its fill becomes semi-transparent white (#FFFFFF at 40% opacity) to signal it awaits color, without disappearing. When a color is tapped in the picker, the fill applies with a 200ms transition. No "apply" button — the color commits on tap, with a small undo affordance.

This is informed by Pigment's tap-to-fill model (https://www.idownloadblog.com/2016/01/05/pigment-review/) which confirmed that region-highlight-before-fill is the universal success pattern in coloring apps. The region must confirm intent before color applies.

SVG fill regions work via `addEventListener("click", ...)` + `setAttribute("fill", hex)` — confirmed viable on mobile via https://svg-tutorial.com/svg/interaction and the Frappe portal pages confirmation at https://docs.frappe.io/framework/v15/user/en/portal-pages (inline SVG has full DOM access in Frappe templates).

**Number of fill regions: 2 per shape by default.** Research on existing balloon tools (Virtualoon at https://www.virtualoon.com/, BalloonBuilder at https://balloonbuilder.com/balloonbuilder-overview/) shows that professional tools offer per-balloon control, but this overwhelms customers. The Tangled Balloons configurator (https://tangledballoons.com/products/arch) confirms customers think in terms of "4-color spiral" patterns, not individual balloon selection. Two regions (primary + accent) captures the "2-color alternating" mental model that covers ~80% of LT's arch and garland designs.

---

## Q2: What does the COMPOSITION view look like?

The composition view is a **horizontal scroll of piece-cards**. Each card is approximately 280px wide × 320px tall on mobile — fitting ~1.3 cards visible at 375px, giving a clear "scroll right for more" affordance. On desktop (1280px), 3-4 cards are visible simultaneously.

Each card shows:
- The SVG illustration with the customer's chosen colors applied
- The piece name ("Arch", "Column", "Centerpiece")
- An "Edit Colors" affordance (a small paint palette icon, or a tap anywhere on the illustration re-opens the color view)

This horizontal scroll pattern is informed by the moodboard app research at https://blog.designfiles.co/moodboard-apps/ — mobile scrapbook tools favor horizontal arrangement because it matches the thumb's natural left-right swipe gesture, avoids accidental drag on a 2D canvas, and creates a "spread" feeling rather than a stack. The brief's "design book" metaphor maps perfectly to this — it feels like flipping through pages of a spread.

An "Add a Piece" card sits at the rightmost position — outlined, with a "+" icon and the names of available shapes below. Always visible as a next step, never as an onboarding prompt.

---

## Q3: How does the color picker handle 50+ colors?

The picker opens as a **bottom sheet** (slides up from below the SVG illustration, covering ~55% of the screen on mobile). It has three sections stacked vertically:

1. **Recently Used** (top row, up to 8 swatches, horizontal): populated as the customer picks colors. Empty on first visit — slots are shown as light gray circles. This directly addresses the Pigment frustration (https://www.idownloadblog.com/2016/01/05/pigment-review/): "no way to access recently used colors, which is incredibly frustrating."

2. **Full Palette** (grid, 4 columns × N rows, scrollable): all 50+ balloon colors as circles, ~56px each, with color name below each swatch in 10px Raleway. This meets the 44px minimum tap target (iOS HIG, confirmed by UIinkits color picker research at https://www.uinkits.com/blog-post/what-is-a-color-picker-and-how-to-use-it-in-ui-ux-design) while fitting 4 across at 375px (4 × 56px + 3 × 12px gap ≈ 260px, fits with horizontal padding).

3. **Hex display** (appears when a swatch is tapped, shown as a small badge near the swatch before committing): the hex code surfaces on swatch selection, not on hover (hover doesn't exist on touch — per SVG micro-interaction research at https://www.svggenie.com/blog/svg-micro-interactions-ux-guide). Customer can see "Teal — #008080" before the color applies.

The flat grid of named swatches (not a color wheel) is the right pattern for a finite curated catalog — confirmed by color picker research at https://mobbin.com/glossary/color-picker. A color wheel implies infinite choice; a swatch grid implies "these are your options," which matches balloon color reality.

---

## Q4: What does the "I'm done for now" moment look like?

The customer finishes coloring 2-3 pieces and arrives at the "I'm done" feeling naturally — the composition scroll shows their work, each piece colored. At this moment, the tool shows a **summary card** that slides up or navigates to a full-screen "Your Design" view:

- A horizontal strip showing all colored pieces together (the composition)
- Two CTAs: "Discuss This Design" (teal fill, primary) and "Keep Designing" (text link)
- A light note: "Your design is remembered while you're here. Ready to bring it to life? Jeff can make this happen."

The "discuss" CTA pre-populates an inquiry form with: the customer's design state (piece types + hex colors), no price, no commitment language. The output is a **lead for Jeff**, not a cart item.

The "captured" feeling comes from the composition view itself — seeing 3 colored pieces laid out together is the moment of "I made this." The UI doesn't need a dramatic "save complete" animation; the act of seeing the composition IS the capture moment. (Persistence mechanism is deliberately out of scope per brief Section 4.)

---

## Q5: What's the discovery upsell mechanic?

After a customer colors their first piece (e.g., a column), the "Add a Piece" card at the end of the composition scroll shows a **contextual suggestion** beneath the standard shape list:

> "Columns look great next to a matching arch — add one in your colors?"

Tapping this suggestion adds an arch to the composition, pre-populated with the same primary and accent colors the customer just chose for their column. They can then adjust the colors independently.

This is the "coloring one thing makes you want to color the next thing" dynamic from the brief. The trigger is: after any shape is colored, the Add card's suggestion updates to name a complementary piece. The pairings (arch + column, garland + backdrop, centerpiece + arch) are hardcoded — no ML needed for v1.

The visual empty placeholder in the "Add" card also carries suggestion weight: the outlined/ghosted shape preview in the same proportions as the completed pieces communicates "something belongs here" without explicit text. Both mechanisms (text suggestion + visual placeholder) work together.

---

## Q6: What's the simplest version that captures the essence?

**Minimum viable: 2 shapes, 1 fill region each, 12 swatches in the picker.**

The essence of the tool is "tap a shape → color it → see it next to another colored shape → want to book." All of that is achievable with:
- 2 shapes: Arch + Column (the two most common LT pieces)
- 1 fill region per shape (whole-shape color, no accent)
- 12 balloon colors (a representative subset)
- A composition view showing the 2 colored shapes side by side
- A "Discuss This Design" button leading to the inquiry form

No recently-used row. No hex display. No horizontal scroll — just two pieces visible simultaneously on mobile at a comfortable size.

This v1 is Frappe-native with ~100 lines of CSS and ~80 lines of JS. It ships and validates the discovery mechanic. Everything else (more shapes, more fill regions, more colors, recents row, hex display, composition scroll, upsell suggestion) is additive and can land in subsequent slices without breaking the v1 experience.

The floor I would NOT cut below: the SVG illustrations must be good enough to feel satisfying to color. Low-quality or ambiguous outlines break the coloring book metaphor entirely. If the SVG illustrations aren't solid, nothing else matters.

---

## Frappe Compatibility Notes

All primitives used in the mockup are Frappe-recreatable:
- Inline SVG embedded in a Jinja `www/` page template
- Color state managed in a vanilla JS module (`script.js`)
- CSS via co-located `.css` file or `web_include_css`
- jQuery available from Frappe's bundle (used for DOM selectors and event binding)
- Bottom sheet implemented as a CSS-positioned `<div>` with `transform: translateY` toggle — no framework needed
- No NPM, no build step, no CDN chain imports

One flag: the SVG balloon illustrations need to be drawn specifically for this tool with named fill regions (`id="fill-primary"`, `id="fill-accent"`). This is design work outside the code scope — the illustrations themselves are the hard dependency. I flag this explicitly per Brief Section 3: if the illustration quality doesn't meet the brief's "coloring book that's slightly nicer" standard, the implementation is technically Frappe-native but experientially broken.
