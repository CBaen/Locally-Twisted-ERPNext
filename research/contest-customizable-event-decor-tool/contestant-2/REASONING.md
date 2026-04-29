# Reasoning — Contestant 2
# Customizable Event Decor Design Tool

~600 words covering the 6 design questions from Brief Section 7. Each major choice cites a URL from RESEARCH-NOTES.md.

---

## Distinct Angle

My framing: **the Coloring Book That Assembles Itself**. The customer arrives at a canvas that already contains one illustrated shape — a blank arch ready to be colored. They tap a region, the bottom picker slides up, they choose teal. The arch comes alive. They notice an empty "ghost" column placeholder to the right. They tap it, it materializes, they color it. The composition grows by invitation, not by instruction.

This is distinct from the pro-tool model (BalloonBuilder, Virtualoon) which requires learning layers and generators. It's distinct from the configurator model (dropdown cascades ending in Add to Cart). It's closest to PilaMania's inquiry flow — but instead of a 3D render, it uses flat illustrated SVG that feels like a coloring book page, which has lower production cost and works better inside Frappe.

---

## Q1: What does coloring ONE shape look like?

The customer taps on any region of the SVG illustration — say, the main body of a balloon arch. The region highlights (a soft teal ring appears around it, 2px). A bottom sheet slides up from below. The bottom sheet is chosen because, per NN/G's research on this pattern (https://www.nngroup.com/articles/bottom-sheet/), it "preserves some of the user's current context" — unlike navigating to a separate page, the arch stays visible behind the sheet while the customer picks. They never lose sight of what they're coloring.

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
2. **Hue-family filter tabs** — 6 small tabs (Reds/Pinks | Blues/Purples | Greens | Yellows/Oranges | Neutrals | Darks). Each shows ~5-8 swatches — a reasoned estimate, not a research-backed spec. The UXPin color system article (https://www.uxpin.com/create-design-system-guide/build-color-palette-for-design-system) supports organizing palettes by family and ensuring complete coverage, but does not prescribe a specific count per group. The ~5-8 estimate comes from dividing LT's 50-color catalog across 6 families and verifying each tab stays scannable at a glance on a 375px screen — the constraint drives the number, not the source.
3. **Hex code display** — tapping any swatch shows its hex code in a read-only chip below the swatch grid. Customers matching venue colors can verify hex (confirmed as essential by https://mobbin.com/glossary/color-picker and the Pigment guide https://emma-rose-portfolio.com/blog/pigment).

I explicitly omit a custom hex input field in v1 (see "simplest version" below). A read-only hex display meets "customers need to verify their hex" without the complexity of hex-input validation.

Selection indicator: a 2px teal ring around the chosen swatch (Mobbin pattern). Commit by tapping "Apply Color" or by tapping a second swatch (previous apply auto-commits).

---

## Q4: What does the "I'm done for now" moment look like?

The customer has colored 2-3 pieces. They tap "I love this — save my design." A full-screen snapshot summary appears: the composition at full-width with a color palette strip below it (showing every hex they used). Below that: two options — "Start over" (ghost button) and "Send this to Jeff" (teal CTA button).

The "captured" feeling comes from the snapshot layout — it looks like a design card, like something that could be printed or shared. No discussion of persistence mechanics to the customer. The experience reads as "this is done, it's saved, Jeff will see it."

This pattern draws from PilaMania's "add to your request... you decide when it's ready" framing (https://www.pilamania.com/en/products/3d-color-designs/): no purchase pressure, just capture.

### What actually travels to Jeff — the inquiry payload

When the customer taps "Send this design to Jeff," the tool calls Frappe's Lead creation endpoint via `frappe.call('frappe.client.insert', { doc: { doctype: 'Lead', ... } })`. The Lead record receives these fields:

```
lead_name:        customer's name (collected via a two-field prompt on the send screen — name + phone/email)
email_id:         customer's email
phone:            customer's phone
custom_design_ref: "LT-{timestamp}" — the reference number shown on the card
custom_pieces:    "Balloon Arch, Column, Centerpiece" — comma-separated piece names
custom_palette:   "#FFB6C1 (Light Pink), #87CEEB (Sky Blue), #FFFFFF (White)" — hex + name for every color used
custom_design_notes: freeform text (optional — a single textarea on the send screen, "Anything else Jeff should know?")
source:           "Design Studio"
```

The `custom_palette` field carries **hex codes, not just color names**. "Pink" is ambiguous across balloon catalogs; `#FFB6C1` is not. Jeff takes the hex to his supplier and matches SKUs directly.

Jeff's inbox view (ERPNext CRM Lead list): the Lead title shows the customer name + reference number. Opening the Lead shows the custom fields in a "Design Studio" section: piece list, palette with hex codes, optional notes. Jeff's first sentence on the call is "I loved what you designed — I'm looking at your arch in Light Pink (#FFB6C1) and Sky Blue (#87CEEB), tell me about the event." The design reference gives both parties shared vocabulary; the hex codes remove the color-matching step from Jeff's supplier conversation.

**No screenshot or image is sent.** The SVG composition is not captured as an image in v1 — the text payload (pieces + hex codes) gives Jeff everything he needs to open a pitch. A visual capture (dom-to-image to a data URL, or a server-side render) is a v2 enhancement worth flagging but not load-bearing for v1: if Jeff wants to see the visual, the customer can return to the tool and share their browser view. The reference number makes that conversation possible.

**The contact fields:** To avoid the "send without a name" problem, the "Send this design to Jeff" button shows a lightweight inline prompt (not a new page) — two fields below the card: "Your name" and "Best way to reach you (phone or email)." Both required. The teal CTA only activates after both are filled. This is the minimum viable identity capture for the Lead record and keeps the send flow on one screen.

---

## Q5: What's the discovery upsell mechanic?

After a customer finishes coloring an arch, a ghost placeholder column appears to the right of it in the canvas — sketched in light gray, labeled "+ Add a column?" with a small "matches your colors" note. This is always visible, never modal or forced.

The customer taps the ghost → the column materializes with the arch's primary color pre-applied. They can adjust independently. The column's appearance unlocks a ghost backdrop behind both pieces.

This cascading ghost pattern is my own design move, inspired by the concept of customer-initiated element substitution that Fanfaire implements (https://www.fanfaire.io/design-studio — "Let clients swap elements"). Fanfaire's SWAP is also customer-facing, so the surface similarity is real, but my mechanism is structurally different: the ghost appears as a consequence of completing the previous piece, not from a decorator-curated alternative set.

The cascade (one ghost at a time, unlocked by completion) is a design judgment, not a researched pattern. The argument for it over showing all ghosts at once: NN/G's progressive disclosure research (https://www.nngroup.com/articles/progressive-disclosure/) notes that "the very fact that something appears on the initial display tells users that it's important." Two or three ghost shapes competing for attention dilute the signal of each. A single ghost, appearing after the arch is colored, has the full weight of "this is the logical next step" — the customer's eye goes there because there is nowhere else to look. The sequence also keeps the composition from appearing overwhelming before anything is colored.

The key is that the ghost column is already in the right visual position relative to the arch — the customer doesn't have to imagine placement.

---

## Q6: Simplest version — the minimum viable floor

**v1 scope**: one shape at a time, no composition. The customer picks ONE shape (arch, column, garland, backdrop, drop, bouquet, centerpiece) from 7 illustrated tiles. They color it using the bottom picker. They tap "Send this to Jeff" which pre-fills a contact form with the shape name + hex codes.

What this removes: composition canvas, ghost placeholders, multi-piece side-by-side view, recently-used row, hue-family tabs (flat grid of 20 colors instead).

**Defense**: the brief's core want — "within 30 seconds they're picking colors and seeing a stylized illustration in those colors" — is fully met. The "I made this, I want to talk about it now" moment happens even without multi-piece composition. The inquiry outcome (Jeff sees what the customer envisioned) is fully achieved. Everything beyond v1 is discovery/upsell layering that increases inquiry value but isn't load-bearing for the core experience.

---

## Frappe-Native Fit

The full tool lives in a single `www/design-studio.html` portal page with a `www/design-studio.py` controller. Inline SVG is in the page HTML (confirmed: Web Page HTML content type supports arbitrary HTML including SVG). CSS is in a `<style>` block on the page. JS uses jQuery (already in Frappe's bundle) with vanilla DOM. No CDN fetches, no NPM, no build step. The inquiry form submits via Frappe's `frappe.call()` to create a Lead — consistent with the LT form-handler routing in CLAUDE.md.

No forbidden primitives used. No flags to raise.

---

## Round 2 — B-lean: Sharpening the Cascading Ghost

**Path chosen:** B-lean. The cascading ghost is the distinctive move. Round 2 commits harder to it rather than pivoting.

Two product-physics corrections were load-bearing and non-optional:

### Correction 1: 53 named LT colors replace generic hex swatches

PRODUCT-DETAILS §2.8 provides the actual LT latex color catalog verbatim. PRODUCT-DETAILS §4 is explicit: **color NAME is the supplier-actionable identifier, not hex.** Jeff calls his supplier with "Blush" and "Dusk Blue" — not "#F4C2C2" and "#7FA3C0."

Round 1's COLOR_CATALOG used invented generic names (Light Pink, Hot Pink, Sky Blue) that are not in LT's catalog. That was wrong. Round 2 replaces the entire catalog with the 53 actual named colors organized into the natural family clusters the spec provides: Reflex metallics, Dusk muted tones, Pastel soft tints, Brights, Neutrals, Deep tones.

The UX implication is significant. The hex chip in the color picker now shows **NAME prominently (large, bold) with hex as a smaller secondary annotation**. The done screen's palette row shows NAME first ("Blush"), hex second ("#F4C2C2 "). The inquiry payload sent to Jeff's CRM formats palette as "Blush #F4C2C2, Dusk Blue #7FA3C0, White #FFFFFF" — name leads, hex follows. This is what Jeff reads to his supplier.

### Correction 2: Centerpiece removed from composition

PRODUCT-DETAILS §2.7: "drop centerpieces from the design tool." The Round 1 composition (arch + column + centerpiece) had an out-of-scope piece. Round 2 removes centerpiece. The composition is now arch + column. The cascading ghost after both pieces is a **Garland** — organic construction, doublet + filler, which is a legitimate third piece per §2.3.

The ghost garland in 04-composition.html renders as an organic doublet arrangement pre-tinted in the arch's palette. This is more honest than a dashed box with a "+" because it shows what a garland *actually looks like* — irregular sizes, organic spacing — already in the customer's colors.

### The B-lean sharpening: ghost inherits Design style

The field summary for B-lean: "sharpen the cascading-ghost mechanic — a ghost column suggested next to a Swirl arch picks up the same Swirl style by default."

This is implemented via `initGhostInheritance()` in script.js:

1. `buildGhostPreviewColors()` — returns the composition's live palette as an array of `{hex, name}` objects
2. The ghost column SVG has `[data-ghost-balloon]` attributes on each ellipse — `initGhostInheritance()` iterates these and sets `fill` to the palette colors in cycle order
3. `buildGhostSuggestionLabel(pieceType, precedingDesign)` — constructs "A Column in your Swirl style" or "A Column in your Organic style" depending on which Design attribute the arch was given
4. The suggestion panel headline (`.suggestion-panel__headline`) is updated with this label + " — they pair beautifully"
5. The `.suggestion-palette-dots` container is populated with live-tinted circles, each titled with the actual LT color name

The result: the ghost column is not a generic blank invitation — it is a Swirl column, in Blush and Dusk Blue and White, labeled "A Column in your Swirl style." The customer sees their design already extended. The gap between "what I could add" and "what this would look like" collapses.

This sharpens the cascading ghost's core claim: **the ghost is not an upsell prompt. It is a preview of the customer's own event, already built, waiting for a tap.**

### Design attribute selector added to coloring screen

PRODUCT-DETAILS §2.1: Design = Swirl (≤4 colors) | Layered (≤8 colors) | Organic (palette-driven). This selector belongs on screen 02 as the first decision, before color picking begins — because Design governs the color cap.

Three pill buttons (Swirl / Layered / Organic) appear below the nav on the coloring screen. Selecting a pill:
- Sets `DesignStudio.currentDesign`
- Updates the cap hint text ("up to 4 colors" / "up to 8 colors" / "palette-driven")
- Enables `wouldExceedCap()` enforcement in `selectSwatchColor()`: if the customer already has 4 colors and tries a 5th on a Swirl arch, a nudge appears ("Swirl uses up to 4 colors. Switch to Layered for more.") rather than silently applying or silently blocking

The Design attribute also flows into the ghost suggestion: `DesignStudio.currentDesign` is passed to `buildGhostSuggestionLabel()` so the ghost column knows to say "Swirl style" vs "Organic style."

### What was NOT changed

- Bottom-sheet picker structure — sound, stays
- `buildInquiryPayload()` and `initDoneScreen()` — already had full payload spec from Loop 1-2; updated only to use real LT color names in the demo fallback and to format palette as NAME-first
- Loud-failure error path (`showSendError()`) — unchanged, still present
- Composition layout (strip + canvas) — unchanged
- Frappe-native constraints — unchanged, still zero forbidden primitives
