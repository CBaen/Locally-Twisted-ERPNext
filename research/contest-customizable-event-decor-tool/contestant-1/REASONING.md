# REASONING.md — Contestant 1

Concept name: **The Color Stage**
Elevator: *A customer taps a shape, colors it like a coloring book, taps "add another," and watches their event assemble piece by piece on a shared stage — ends with "send this to Jeff."*

---

## Question 1: What does coloring ONE shape look like?

The customer arrives at the tool and sees a gallery of the 7 shapes as stylized illustration thumbnails — not product cards with prices, not dropdowns, just the illustrations. They tap "Balloon Arch."

The arch illustration expands to fill most of the screen. The SVG has 2-3 labeled fill regions: **Main Cluster** (the balloon body), **Accent Cluster** (smaller bubbles at the ends), and optionally **Stem** (the base). Each region shows a thin animated pulse on first load — a "tap me" affordance that disappears after 3 seconds.

The customer taps **Main Cluster**. The region highlights (stroke thickens, slight brightening). A color picker slides up from the bottom of the screen — a horizontal scrolling row of 12 swatches showing the most popular balloon colors (derived from LT's catalog), with a "More colors →" chip at the right end that opens the full palette sheet.

They tap a swatch. The fill region immediately repaints. No "apply" button needed — tap is commit. The hex code appears briefly as a small tooltip below the selected swatch.

**Why this approach (citation):** The Pigment coloring app (RESEARCH-NOTES Source 7) validates the two-step region-activation mechanic: the review describes "tap a section of an illustration to activate the 'color-inside-the-lines' feature, which highlights the spot so that it is the only part of the illustration that will be affected." This confirms that tap → activate/highlight is an established, intuitive pattern. Precision note: after activation, Pigment uses freeform brush strokes; my design uses a swatch tap for instant flat fill. The citation supports step one (tap to activate and isolate a region). Step two — swatch tap commits a flat fill immediately — is a design choice suited to balloon context (a balloon zone is a single color, not a gradated brushstroke; instant fill is faster and more satisfying).

Fill regions are consciously limited to 2-3 per shape. The brief allows "many (per-balloon control)" but I'm advocating for the minimum level. More than 3 fill regions per shape creates cognitive overload on a 375px screen — the picker would have to reopen for every single balloon. The 2-3 zone approach gives the feel of customization without the burden of configuration.

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

**Inquiry payload specification (from Proxy Loop 1-2):**

The pre-filled design notes field includes hex codes alongside color names. Format:

```
Column: Lavender (#C3B1E1) + Blush (#F4A0A0)
Balloon Arch: Coral (#FF6B6B) + Champagne (#F7E7CE)
Backdrop: Mint (#88FED0) + Sage (#9DC08B)
```

Color names alone are ambiguous to a balloon supplier — "Coral" maps to multiple product SKUs. The hex code gives Jeff (and his supplier) a precise reference. The JS that builds this string iterates the stage pieces array: for each piece, `${piece.label}: ${piece.colors.map(c => c.name + ' (' + c.hex + ')').join(' + ')}`. This is the same data already held in the client-side `DesignStudio.stagePieces` state object — no additional work at form-submit time.

For the V1 mailto path (single shape, no stage), the format simplifies to: `Balloon Arch: Coral (#FF6B6B) [main] + Champagne (#F7E7CE) [accent]` — bracket-labeling the region so Jeff knows which color goes where on the shape. The mailto body is URL-encoded from this string.

**Stage 2 inquiry enhancements:**

Two items worth flagging for Stage 2, both requiring state that doesn't exist in V1:

1. **"Pieces you considered" field.** When the upsell stage surfaces suggestion chips and the customer doesn't tap any, those suggestions could appear in the inquiry as: `Also suggested by the tool (customer didn't select): Garland, Bouquet.` Jeff reading "the tool offered a garland and the customer passed" gets useful signal — this customer was shown the option and didn't want it, which saves a pitch step. Implementation: the upsell JS records which suggestions were surfaced, and the inquiry-builder appends them if non-empty.

2. **Design snapshot.** A rasterized or data-URI PNG of the customer's assembled composition, attached to the inquiry, means Jeff has the visual without navigating back to the tool. This requires either canvas-based SVG rasterization (client-side, via `<canvas>` + `drawImage` of a serialized SVG blob) or a server-side render step — both cross into Stage 2 scope. Flag it, don't implement in V1. The composition is already visible on the tool if Jeff needs it; the text payload carries the essential information.

---

## Question 5: What's the discovery upsell mechanic?

After the customer finishes coloring their first piece (e.g., a column), the composition stage shows their column plus **one empty placeholder slot** with a dashed border and a gentle label: "Something that belongs next to this?"

Below the placeholder, 2-3 shape suggestions appear as small illustration chips — the shapes most commonly paired with whatever they just colored. For a column: "Arch" and "Garland" appear. Each chip shows the suggestion in *their current colors* — the column's coral-and-gold palette applied to the arch illustration.

This is the key move: **the suggestion already shows their colors**. The customer doesn't see a blank "Add an Arch?" prompt — they see *their arch* waiting to be confirmed. The discovery mechanic works because it collapses the gap between "what I could add" and "what this would look like."

**Why this works (first-principles reasoning):** Color inheritance — showing a suggested piece already rendered in the customer's in-progress palette — is a design invention, not a pattern sourced from the research. Fanfaire variants (Source 14) show Jeff's pre-made design alternatives, not a customer's live palette projected onto new pieces. Gemar Creator presets (Source 4) are starting-point compositions the customer then modifies from zero. Neither source describes this mechanic.

The reasoning that makes it defensible without a citation: the gap between "imagining what this would look like" and "deciding to add it" is the abandonment point. Showing a blank arch chip next to a colored column asks the customer to do mental work. Showing a coral-and-champagne arch chip — already matching their column — collapses that gap. The suggestion looks like it already belongs, because it does. This is a Stage 2 feature (see Q6), not V1 — it requires the tool to hold the customer's palette choices in memory and apply them to untouched shape templates at the moment of suggestion.

On mobile, the suggestion chips appear in a horizontal scroll below the stage. On desktop, they appear as a persistent sidebar panel.

---

## Question 6: What's the simplest version that captures the essence?

**V1 scope (minimum viable):**
- 1 shape: Balloon Arch only
- 2 fill regions: Main Cluster + Accent Cluster
- 12 color swatches (no Tier 2 full palette, no hex code display, just the quick row)
- Composition view: just the arch, no multi-piece stage
- Done moment: "Send to Jeff" button opens a mailto link with the color choices in the body
- No upsell mechanic
- No color inheritance (Stage 2 — requires palette state management across multiple shapes)

**What you get with V1:** A customer can pick colors for a balloon arch and send an inquiry with those colors. Jeff opens his email and knows what the customer wants. That alone eliminates the "I don't know what I want, can you show me options?" call.

**Why this is the floor:** Every piece above V1 is additive. The multi-piece composition, the Tier 2 palette, the upsell suggestions, and color inheritance — all of these deepen the experience but aren't required to deliver "customer arrives, picks colors, sends inquiry." The floor produces value independently.

**Where I'd cut vs. keep:**
- Cut first: color inheritance in upsell chips (Stage 2 — needs palette state held across shapes; upsell chips still work in V2 without color inheritance, showing shapes in neutral/default colors)
- Cut second: upsell mechanic entirely (Stage 2; adds complexity; delivers only after core is working)
- Cut third: Tier 2 full palette (12 colors covers most customers; full palette is for the color-matcher edge case)
- Keep always: the inline SVG illustration, the stage view, the "Send to Jeff" inquiry bridge

**Frappe flags (none for V1):** The V1 scope is fully implementable as a single Web Page DocType with inline SVG, a page-scoped `<style>` block, and a Script section. No `web_include_css` needed at V1. No Node.js build step. No external dependencies.

---

## Technical approach notes

All interaction logic is vanilla JS with jQuery available from Frappe's bundle. The SVG illustration for each shape is a hand-drawn-style simplified vector with named path groups: `<g data-region="main">`, `<g data-region="accent">`. Color change: `document.querySelectorAll('[data-region="main"] path').forEach(p => p.setAttribute('fill', color))`. This is standard DOM manipulation — no libraries needed, no build step.

The color configuration is a JS array at the top of the script: `const LT_COLORS = [{name: "Coral", hex: "#FF6B6B"}, ...]`. Adding a color is editing one line. No backend interaction during design. The inquiry form submission is a Frappe Web Form POST — standard Frappe infrastructure.

The one Frappe caveat flagged for GL: the CSS theme conflict (RESEARCH-NOTES Source 20). Solution chosen: page-scoped `<style>` block in the Web Page HTML content, not `web_include_css`. This avoids the known cascade conflict entirely.
