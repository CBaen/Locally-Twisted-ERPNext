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

**Number of fill regions: 2 per shape by default — grounded in construction physics, not just customer mental model inference.**

Balloon arches and columns are built in 4-balloon clusters (one triplet cluster + one accent balloon per knot-tying unit). This is the atomic unit of classic arch/column/wall construction. Given a cluster size of 4, the minimum repeat length for a color pattern is `min_repeat = C ÷ gcd(C, 4)`, where C is the number of colors in the pattern. For 2 colors: `gcd(2, 4) = 2`, so `min_repeat = 2 ÷ 2 = 1` — a single cluster completes the full pattern. The 2-color Swirl is mathematically the cleanest case: one primary balloon, one accent balloon, repeating A B A B along the arch with no partial clusters and no remainder. It is also the most common arrangement LT builds for everyday events.

This construction physics is why the tool defaults to Swirl mode with 2 fill regions. It is not a simplification for simplicity's sake — it is the simplification that matches the physics of how the product is actually constructed. The Tangled Balloons configurator (https://tangledballoons.com/products/arch) naming its arches in pattern terms ("4 color spiral arch," "4 color spiral arrow arch") confirms customers already encounter and think in terms of color patterns rather than individual balloon selection — a UX observation consistent with the physics, though the page offered no customer-choice statistics and its 3D configurator was broken at the time of review.

For Organic arrangements (mixed-size clusters, no fixed repeat), the tool switches to a palette-only mode — the customer picks a set of colors and Jeff arranges them with natural variation. This is the honest path for organic work: no fill-region UI can accurately represent a controlled-random arrangement, so the tool doesn't attempt one. The toggle between Swirl (2 regions, A B A B) and Organic (palette only) is visible on the color-one screen, making the distinction explicit to the customer.

---

## Q2: What does the COMPOSITION view look like?

The composition view is a **horizontal scroll of piece-cards**. Each card is approximately 280px wide × 320px tall on mobile — fitting ~1.3 cards visible at 375px, giving a clear "scroll right for more" affordance. On desktop (1280px), 3-4 cards are visible simultaneously.

Each card shows:
- The SVG illustration with the customer's chosen colors applied
- The piece name ("Arch", "Column", "Garland")
- An "Edit Colors" affordance (a small paint palette icon, or a tap anywhere on the illustration re-opens the color view)

The horizontal scroll is my design judgment, not a direct finding from the moodboard app research. What the DesignFiles article (https://blog.designfiles.co/moodboard-apps/) actually establishes is a distinction between apps that feel like "digital scrapbooking" (Shuffles — layered, tactile, process-joyful) versus apps that feel like "design tools" (output-focused, workflow-driven). The brief explicitly calls for the former. The article does not compare horizontal vs. vertical scroll direction or claim any layout outperforms another.

The horizontal scroll is my application of that scrapbooking spirit to mobile constraints: a free 2D canvas on a 375px touchscreen invites accidental drag (the browser can't always distinguish a scroll-drag from a rearrange-drag without careful implementation that adds complexity); a horizontal strip of cards matches the "spread across a table" or "pages in a scrapbook" feeling the brief names; and thumb-swiping horizontally is natural on a phone held vertically. Each piece-card is discrete and independent, which maps to how balloon decor actually works — an arch is not attached to a column, a column is not attached to a centerpiece. The composition is additive, not spatially locked.

An "Add a Piece" card sits at the rightmost position — outlined, with a "+" icon and the names of available shapes below. Always visible as a next step, never as an onboarding prompt.

---

## Q3: How does the color picker handle 50+ colors?

The picker opens as a **bottom sheet** (slides up from below the SVG illustration, covering ~55% of the screen on mobile). It has three sections stacked vertically:

1. **Recently Used** (top row, up to 8 swatches, horizontal): populated as the customer picks colors. Empty on first visit — slots are shown as light gray circles. This directly addresses the first complaint in the iDownloadBlog Pigment review's "The Bad" section (https://www.idownloadblog.com/2016/01/05/pigment-review/): "there is no way to access recently used colors, which is incredibly frustrating when you've made a custom color." It is one of only two major flaws the reviewer identifies, opening that section with strong language — not a passing mention. The recents row is a small feature with outsized impact on the experience of coloring multiple shapes.

2. **Full Palette** (grid, scrollable): all 53 real LT latex balloon colors, organized by family — Reflexes (metallics), Dusks (muted/dusty), Pastels, Brights, Greens, Blues & Purples, Neutrals. Each family has a header label; swatches are circles ~56px each with color name below in 10px Raleway. Families are separated visually so the customer can scan "I want something dusty and muted" → go straight to Dusks without reading all 53 names. Color names are the supplier-actionable identifiers (verbatim from LT's catalog); hex values are approximate eyeball-matching aids displayed as a secondary badge on tap. This meets the 44px minimum tap target (iOS HIG, confirmed by UIinkits color picker research at https://www.uinkits.com/blog-post/what-is-a-color-picker-and-how-to-use-it-in-ui-ux-design) while fitting 4 across at 375px (4 × 56px + 3 × 12px gap ≈ 260px, fits with horizontal padding).

3. **Hex display** (appears when a swatch is tapped, shown as a small badge near the swatch before committing): the hex code surfaces on swatch selection, not on hover (hover doesn't exist on touch — per SVG micro-interaction research at https://www.svggenie.com/blog/svg-micro-interactions-ux-guide). Customer can see "Teal — #008080" before the color applies.

The flat grid of named swatches (not a color wheel) is the right pattern for a finite curated catalog — confirmed by color picker research at https://mobbin.com/glossary/color-picker. A color wheel implies infinite choice; a swatch grid implies "these are your options," which matches balloon color reality.

---

## Q4: What does the "I'm done for now" moment look like?

The customer finishes coloring 2-3 pieces and arrives at the "I'm done" feeling naturally — the composition scroll shows their work, each piece colored. At this moment, the tool shows a **summary card** that slides up or navigates to a full-screen "Your Design" view:

- A horizontal strip showing all colored pieces together (the composition)
- Two CTAs: "Discuss This Design" (teal fill, primary) and "Keep Designing" (text link)
- A light note: "Your design is remembered while you're here. Ready to bring it to life? Jeff can make this happen."

The "discuss" CTA pre-populates an inquiry form with the customer's design state — structured per piece, per region, so Jeff can act on it without a disambiguation call. The payload format:

```
Design reference: LT-4728
Pieces:
  Arch    — main balloons: Teal (#007878) / accent balloons: Reflex Gold (#D4A017)
  Column  — main balloons: Teal (#007878) / accent balloons: Reflex Gold (#D4A017)
  Garland — main balloons: Blush (#F4DFD7) / accent balloons: Dusk Blue (#8CA8C0)
```

Each row gives Jeff: piece identity, which balloon region, color name, and hex. The region label ("main balloons" / "accent balloons") comes directly from the `data-region` attributes already in the SVG — no new data needed, just a rendering decision. Jeff can take this to a supplier conversation or pre-fill a balloon order without calling the customer back to ask "which color goes where."

The customer never sees this structured breakdown during their design experience — they see the composition spread and a friendly done-screen. The per-piece attribution appears only in the Design Summary section (visible on the done-screen as a reference for both customer and Jeff) and in the inquiry payload. The customer-facing framing stays warm and simple; the Jeff-facing structure is precise.

No price, no commitment language anywhere. The output is a **lead for Jeff**, not a cart item.

The "captured" feeling comes from the composition view itself — seeing 3 colored pieces laid out together is the moment of "I made this." The UI doesn't need a dramatic "save complete" animation; the act of seeing the composition IS the capture moment. (Persistence mechanism is deliberately out of scope per brief Section 4.)

---

## Q5: What's the discovery upsell mechanic?

After a customer colors their first piece (e.g., a column), the "Add a Piece" card at the end of the composition scroll shows a **contextual suggestion** beneath the standard shape list:

> "Columns look great next to an arch — they pair beautifully. Add one to your design?"

Tapping this suggestion adds an arch to the composition, pre-populated with the same primary and accent colors the customer just chose for their column. They can then adjust the colors independently.

This is the "coloring one thing makes you want to color the next thing" dynamic from the brief. The trigger is: after any shape is colored, the Add card's suggestion updates to name a complementary piece. The pairings (arch + column, garland + arch, drop + backdrop) are hardcoded — no ML needed for v1.

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
