# REASONING.md — Contestant 1

Concept name: **The Color Stage**
Elevator: *A customer taps a shape, colors it like a coloring book, taps "add another," and watches their event assemble piece by piece on a shared stage — ends with "send this to Jeff."*

---

## Question 1: What does coloring ONE shape look like?

The customer arrives at the tool and sees a gallery of the 7 shapes as stylized illustration thumbnails — not product cards with prices, not dropdowns, just the illustrations. They tap "Balloon Arch."

**Round 2 update — Physics reconciliation (PRODUCT-DETAILS.md §3 + §5.3):**

The real balloon construction physics distinguishes two fundamentally different shape families:

- **Grid-mapped shapes (Backdrop/Wall):** Each 4-balloon cluster in the grid IS a tappable region. Region-tap UX maps directly to build reality. Two tap regions (background + pattern stripe/block) cover all Backdrop design variants. This is where the tap-to-color metaphor is most honest.
- **Sequence-distributed shapes (Arch, Column, Garland):** The customer doesn't tap spatial regions; they pick a **Design style** (Swirl / Layered / Organic) and a **color count**, then the tool auto-distributes colors across the cluster sequence using the `min_repeat = C ÷ gcd(C, 4)` math. The customer doesn't choose which cluster gets which color — the distribution formula handles that.

I'm taking Option (a) from PRODUCT-DETAILS §5.3: for the screen-02/coloring view of Arches, Columns, and Garlands, the UI presents a **style chip** (Swirl / Layered / Organic) above the illustration, and **color slot chips** below the illustration (2 slots for Swirl, up to 4 for Layered, palette-open for Organic). The tap-to-activate-region metaphor is replaced for these shapes by a tap-a-color-slot mechanic: the customer taps a numbered slot, opens the picker, assigns a color; the illustration re-renders showing the auto-distributed result. This is more honest to the physics and still coloring-book in spirit — the customer is choosing the palette and watching the design respond.

For **Backdrops**, the tap-region UX is preserved intact: two named SVG regions (background clusters + pattern clusters) are genuinely tappable because each corresponds to real construction zones in the cluster grid.

For **Garlands** (organic, doublet-on-strip), the customer picks a style (Solid / Two-tone / Ombré / Multi-color blend) and assigns colors to slots; the illustration shows a randomized but constraint-compliant preview (no-touching-twins rule applied).

The 2-screen mockup (02-color-one.html) shows a Backdrop as the demonstration shape — the tap-region mechanic is fully valid there. The REASONING note below covers how this extends to other shapes.

---

The arch/column/garland illustrations in the coloring screen show the **result** of the customer's color choices, not tappable regions. The customer interacts with the color slot chips, not directly with the SVG. This keeps the "coloring book" feel (you see the design fill with your colors) without pretending the customer is painting individual balloons.

**Why this approach (citation):** The Pigment coloring app (RESEARCH-NOTES Source 7) validates the two-step region-activation mechanic: the review describes "tap a section of an illustration to activate the 'color-inside-the-lines' feature, which highlights the spot so that it is the only part of the illustration that will be affected." This confirms that tap → activate/highlight is an established, intuitive pattern. Precision note: after activation, Pigment uses freeform brush strokes; my design adapts this to swatch-tap for instant flat fill. The citation supports step one (tap to activate and isolate a region). For Backdrop, both steps apply directly. For Arch/Column/Garland, I use a color-slot chip as the activation surface instead of an SVG region — same two-step structure, different tap target.

Fill regions are consciously limited to 2-3 per shape for Backdrops. For Arches/Columns: 2 slots for Swirl (main + accent), up to 4 for Layered. For Garlands: style determines the slot count (Solid=1, Two-tone=2, Ombré=2-3, Multi-color=3-4). This keeps cognitive load manageable on a 375px screen.

---

## Question 2: What does the COMPOSITION view look like?

The composition view — called "Your Event Stage" — is a horizontal scroll canvas at the top of the page. Each piece the customer has colored appears as a thumbnail illustration with its chosen colors applied.

On mobile (375px), the stage is a 160px-tall horizontal strip. Each piece card is ~120px wide. The customer scrolls horizontally to see all their pieces. An "+" card at the end invites the next piece. The active piece (being colored) shows a teal border.

On desktop (1280px), the stage expands to ~260px tall and the pieces arrange side-by-side, showing the assembled event at a glance. The horizontal scroll persists for consistency, but more pieces fit before overflow.

Each piece on the stage is independently re-tappable — tap it to return to editing that piece. This is the "not a wizard" implementation: the customer can always go back and change any piece. No linear lock-in.

**Why this approach (citation):** BalloonBuilder's fundamental failure was separating pieces into separate apps — customers couldn't see the arch and column together (RESEARCH-NOTES Source 2). The horizontal stage directly addresses this: every piece the customer has designed lives together on the stage. Milanote's research (RESEARCH-NOTES Source 12) confirmed that accumulation without freeform arrangement removes mobile friction — customers just add; the stage handles display.

---

## Question 3: How does the color picker handle 50+ colors?

**Two-tier picker.**

**Tier 1 — Quick Row:** 12 swatches in a horizontally scrollable row below the shape illustration. These are the 12 most popular LT colors (defined in the JS config, not hardcoded UI). The row is truncated with visible fade-out on the right edge signaling more exist. Each swatch is 44px × 44px — above the 7mm minimum touch target threshold from Baymard's button/touch-target research (https://baymard.com/learn/button-design), applied here to swatches as tappable elements. The swatch-specific post (RESEARCH-NOTES Source 9) describes "large hit areas and generous spacing" qualitatively but gives no numerical threshold. Hit area: generous.

**Tier 2 — Full Palette Sheet:** Tapping "More colors →" opens a bottom sheet with all 50+ colors organized into named groups: Neutrals, Pastels, Brights, Metallics. Each group is a wrapped 6-per-row grid of 40px swatches. The hex code for any swatch appears on long-press or hover.

**Hex code display:** When a swatch is selected (Tier 1 or Tier 2), a small hex tag appears inline beneath the selected swatch row: `#FF6B9D`. This is the direct cite from the Pigment app (RESEARCH-NOTES Source 7) — Pigment allows hex entry for custom colors, proving customers at this price point DO reference hex codes to match venue/brand colors.

**No color wheel.** The design philosophy from the color picker research (RESEARCH-NOTES Source 10): the palette IS the product. LT has ~50 specific balloon colors in their actual inventory. A color wheel would let customers pick colors LT can't source. The catalog browser framing is not a limitation — it's honest.

**Scalability:** The JS config holds the full color array. Adding more colors to the catalog means adding to the array. The Tier 2 grouped grid reflows automatically. No UI changes needed for 60 or 70 colors.

---

## Question 4: What does the "I'm done for now" moment look like?

When the customer taps "Save My Design" (or the back button on mobile — intercepted with a dialog), they see a **Design Summary screen**:

- A full-width banner image auto-generated from their composition (the stage illustration at 2x scale)
- A plain-language list: "Your event stage includes: Arch in Coral + Gold, Column in Coral, Backdrop in White"
- A large teal CTA: "Send This to Jeff"

The CTA opens a pre-filled inquiry form with the design description embedded in the notes field. Jeff sees what they designed. The customer feels their work was captured.

**What it does NOT show:** No price. No "Add to Cart." No session token. No "create an account to save."

**Why this works without persistence (citation):** The Fanfaire Design Studio (RESEARCH-NOTES Source 5) proves the inquiry-from-design flow — the design IS the inquiry. LT's version strips the pricing layer and makes the design purely the customer's creative expression. The "captured moment" feeling comes from the summary screen, not from actual DB persistence. The form submission is the persistence event — Jeff's CRM receives the inquiry with the design description as a text payload.

The brief explicitly says not to design the persistence mechanic — just show what "captured" looks like. The summary screen achieves that.

**Inquiry payload specification (Round 2 update — PRODUCT-DETAILS.md §4):**

Color name is the primary supplier-actionable identifier. "Reflex Champagne" is a distinct SKU from "Champagne" or "Pastel Yellow." Jeff orders against names; his supplier call maps names to inventory. Hex codes in the catalog are not yet sourced — Jeff will provide Pantone/hex mappings later. The tool's hex values are approximations used for visual rendering in the picker only.

The pre-filled design notes field therefore shows names as primary, with approximate hex as a parenthetical visual aid:

```
Column: Dusk Lilac + Blush
Balloon Arch: Raspberry + Reflex Champagne
Backdrop: Empowermint + Eucalyptus
(Hex approximations for visual reference only — Jeff orders by color name)
```

The JS that builds this string iterates the stage pieces array: for each piece, `piece.label + ': ' + piece.colors.map(c => c.name).join(' + ')`. Hex is stored in client state for rendering the swatch dots in the summary; it is not included in the inquiry payload text. If Jeff wants to cross-reference the visual, the approximate hex can appear in a separate "for reference" line.

For the V1 mailto path (single shape, no stage), the format simplifies to: `Balloon Arch: Raspberry [main] + Reflex Champagne [accent]` — bracket-labeling the region so Jeff knows which color goes where. The mailto body is URL-encoded from this string.

**Credit:** C3's dual-audience design card framing (FIELD-AT-ROUND-1.md) prompted this correction — the name-first requirement was present in the real product spec but my Loop 1-2 reply had prioritized hex. C3 had the right instinct from Round 1: the inquiry text must be supplier-readable without translation.

**Stage 2 inquiry enhancements:**

Two items worth flagging for Stage 2, both requiring state that doesn't exist in V1:

1. **"Pieces you considered" field.** When the upsell stage surfaces suggestion chips and the customer doesn't tap any, those suggestions could appear in the inquiry as: `Also suggested by the tool (customer didn't select): Garland, Bouquet.` Jeff reading "the tool offered a garland and the customer passed" gets useful signal — this customer was shown the option and didn't want it, which saves a pitch step. Implementation: the upsell JS records which suggestions were surfaced, and the inquiry-builder appends them if non-empty.

2. **Design snapshot.** A rasterized or data-URI PNG of the customer's assembled composition, attached to the inquiry, means Jeff has the visual without navigating back to the tool. This requires either canvas-based SVG rasterization (client-side, via `<canvas>` + `drawImage` of a serialized SVG blob) or a server-side render step — both cross into Stage 2 scope. Flag it, don't implement in V1. The composition is already visible on the tool if Jeff needs it; the text payload carries the essential information.

---

## Question 5: What's the discovery upsell mechanic?

After the customer finishes coloring their first piece (e.g., a column), the composition stage shows their column plus **one empty placeholder slot** with a dashed border and a gentle label: "Something that belongs next to this?"

Below the placeholder, 2-3 shape suggestions appear as small illustration chips — the shapes most commonly paired with whatever they just colored. For a column: "Arch" and "Garland" appear. Each chip shows the suggestion in *their current colors* — the column's palette applied to the arch illustration.

This is the key move: **the suggestion already shows their colors AND uses their real color names.** The customer doesn't see a blank "Add an Arch?" prompt — they see *their arch* waiting to be confirmed, with the color name labels showing "Raspberry + Reflex Champagne." The discovery mechanic works because it collapses the gap between "what I could add" and "what this would look like" AND because it shows the customer that the system already knows their palette by name, not just by visual approximation.

**Round 2 sharpening of the mechanic:** The color inheritance chips are rendered via JS: when the upsell screen loads, it reads the most recently completed piece's color assignments (`data-color-name` and `data-color-hex` attributes stored on the region chips by `DesignStudio.selectColor()`), then sets the `fill` attributes on the suggestion SVGs to those hex values and the dot labels to those names. The customer sees their exact named colors reflected back in the suggestion. The upsell copy reads: "These pair beautifully with your Raspberry + Reflex Champagne." — using the catalog names, not generic "your colors."

**Why this works (first-principles reasoning):** Color inheritance — showing a suggested piece already rendered in the customer's in-progress palette — is a design invention, not a pattern sourced from the research. Fanfaire variants (Source 14) show Jeff's pre-made design alternatives, not a customer's live palette projected onto new pieces. Gemar Creator presets (Source 4) are starting-point compositions the customer then modifies from zero. Neither source describes this mechanic.

The reasoning that makes it defensible without a citation: the gap between "imagining what this would look like" and "deciding to add it" is the abandonment point. Showing a blank arch chip next to a colored column asks the customer to do mental work. Showing a Raspberry-and-Reflex-Champagne arch chip — already matching their column, labeled with the names they already chose — collapses that gap. The suggestion looks like it already belongs, because it does. This is a Stage 2 feature (see Q6), not V1 — it requires the tool to hold the customer's named palette choices in memory and apply them to untouched shape templates at the moment of suggestion.

**Bouquet is different (Round 2 correction per PRODUCT-DETAILS.md §2.6):** Bouquets are theme-locked, not palette-customizable in the same sense. The customer browses available themes (Unicorn, Football, Stitch, etc.) — the theme determines the latex palette. Foil colors (Star, Heart, Number shapes) are picker-able within shape-specific palettes. Logo bouquets are the custom-palette exception. The gallery card for Bouquet in the entry screen notes "Pick a theme" rather than inviting region-tap coloring. The upsell suggestion for Bouquet would show the Reflex Gold / Reflex Champagne foil styling (the metallic family being the most broadly complementary), with copy noting "theme and size chosen at inquiry."

On mobile, the suggestion chips appear in a horizontal scroll below the stage. On desktop, they appear as a persistent sidebar panel.

---

## Question 6: What's the simplest version that captures the essence?

**V1 scope (minimum viable):**
- 1 shape: Backdrop (chosen because tap-region UX maps directly to real construction physics — two regions: background clusters + pattern clusters)
- 2 fill regions: Background + Pattern
- 12 popular swatches from the real 53-color LT catalog (Quick Row, no Tier 2 full palette)
- Color names shown as primary on selection; approximate hex for visual rendering only
- Composition view: just the one piece, no multi-piece stage
- Done moment: "Send to Jeff" button opens a mailto link with color NAMES in the body (`Backdrop: Empowermint + Eucalyptus`)
- No upsell mechanic
- No color inheritance (Stage 2 — requires palette state management across multiple shapes)

**What you get with V1:** A customer can pick named colors for a backdrop and send an inquiry with those names. Jeff opens his email and can place the supplier order directly — "Empowermint + Eucalyptus" is the SKU identifier, not an approximation. That alone eliminates the "I don't know what I want, can you show me options?" call.

**Why Backdrop over Arch for V1 floor:** The Backdrop's tap-region mechanic is the most honest mapping between UX and physics — two cluster zones genuinely correspond to two tappable SVG regions. An Arch V1 would require explaining the style-then-colors mechanic, which adds one more concept. The Backdrop V1 is the clearest demonstration of the coloring-book metaphor with zero physics mismatch.

**Why this is the floor:** Every piece above V1 is additive. The multi-piece composition, the Tier 2 palette, the upsell suggestions, and color inheritance — all of these deepen the experience but aren't required to deliver "customer arrives, picks colors, sends inquiry with correct names." The floor produces value independently.

**Where I'd cut vs. keep:**
- Cut first: color inheritance in upsell chips (Stage 2 — needs palette state held across shapes; upsell chips still work in V2 without color inheritance, showing shapes in neutral/default colors)
- Cut second: upsell mechanic entirely (V2; adds complexity; delivers only after core is working)
- Cut third: Tier 2 full palette (12-swatch Quick Row covers most customers; full 53-color palette is for the color-matcher edge case)
- Keep always: the inline SVG illustration, the real LT color names in the picker, the "Send to Jeff" inquiry bridge with names as primary

**Frappe flags (none for V1):** The V1 scope is fully implementable as a single Web Page DocType with inline SVG, a page-scoped `<style>` block, and a Script section. No `web_include_css` needed at V1. No Node.js build step. No external dependencies. The color catalog is a JS array at the top of the Script section — adding colors means editing one array entry.

---

## Technical approach notes

All interaction logic is vanilla JS with jQuery available from Frappe's bundle. The SVG illustration for each shape is a hand-drawn-style simplified vector with named path groups: `<g data-region="main">`, `<g data-region="accent">`. Color change: `$('[data-region="main"]').find('path, circle, ellipse, rect').attr('fill', hex)`. This is standard jQuery DOM manipulation — no libraries needed, no build step.

**Color catalog (Round 2):** The color configuration is the actual 53-color LT named catalog (per PRODUCT-DETAILS.md §2.8), stored as a JS object `var LT_COLORS = { popular: [...], groups: [...] }` at the top of the script. Each entry: `{ name: "Reflex Champagne", hex: "#D4C09A" }`. The hex value is an approximation for visual rendering; the name is the supplier-actionable identifier. Adding or adjusting a color means editing one array entry — no UI changes needed.

**Color name storage on region chips:** When a customer selects a color, `DesignStudio.selectColor()` stores `data-color-name` and `data-color-hex` on the active region chip. The inquiry payload builder reads these name attributes, not the hex. The hex is used only for the dot preview in the summary list.

**Inquiry payload assembly:** `DesignStudio.buildPayloadLine(pieceName, regions)` iterates region chips and outputs `"Piece: Color Name + Color Name"` — names as primary, hex as optional parenthetical. This is the text that pre-fills the inquiry form's design field and, in V1, the mailto body.

**Color inheritance (Stage 2 only):** The upsell screen reads `data-color-name` + `data-color-hex` from the most recently completed piece's region chips, applies those hex values to the suggestion SVG fills, and uses the names in the upsell copy ("These pair beautifully with your Raspberry + Reflex Champagne"). All reads are from DOM attributes already set during the coloring flow — no additional state object needed.

No backend interaction during design. The inquiry form submission is a Frappe Web Form POST — standard Frappe infrastructure.

The one Frappe caveat flagged for GL: the CSS theme conflict (RESEARCH-NOTES Source 20). Solution chosen: page-scoped `<style>` block in the Web Page HTML content, not `web_include_css`. This avoids the known cascade conflict entirely.
