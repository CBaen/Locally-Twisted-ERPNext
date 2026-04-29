# Field at End of Round 1 — Customizable Event Decor Design Tool Contest

**Status:** Round 1 (blind) complete. Two reflective loops applied. Contestants are about to enter Round 2 (mutual visibility).

**Purpose of this file:** Cheat sheet for Round 2 contestants. Read this instead of deep-reading every peer directory. You may still Read specific peer files if a differentiator below catches your eye, but the field is summarized here so you can spend Round 2 on your own response, not on re-deriving what peers did.

---

## One-line elevator per contestant

| | Concept name | Elevator |
|---|---|---|
| **C1** | "The Color Stage" | Customer taps shape → colors it → taps "add another" → watches event assemble piece-by-piece on a shared horizontal stage. Distinctive move: **color inheritance** (Stage 2) — suggested next pieces render in the customer's chosen palette. |
| **C2** | "The Coloring Book That Assembles Itself" | Canvas already has one blank shape; coloring it reveals a ghost placeholder for the next piece; cascading ghosts grow the composition by invitation. Distinctive move: **cascading ghost upsells** triggered by completion. |
| **C3** | "The Coloring Page Frame" | Tool is a coloring page for grown-ups, not a configurator. Stylized SVG outlines wait to be filled. Distinctive moves: **Zeigarnik empty-slots from the start** + **mirror-circle propagation** (color one balloon → siblings adopt) + **handoff-design leadership** (the only contestant specifying full data payload for Jeff's supplier call). |
| **C4** | "The Coloring Book" | Composition view as horizontal scroll of "piece-cards" — literalizing the brief's "spread" metaphor. Distinctive move: **2-fill-region simplicity** (primary + accent only) defended as matching customer "2-color alternating" mental model + per-piece attribution table for Jeff's CRM. |

---

## Convergence — what all 4 chose

Every contestant independently arrived at:

- **Coloring-book / page metaphor** (taking the brief's framing literally — sound)
- **Inline SVG with named fill regions + jQuery event delegation** (the most Frappe-native approach)
- **Tap-region-to-activate-then-color mechanic** (Pigment-derived)
- **Bottom-sheet or expanded color picker pattern** (vs. flat 50-swatch grid)
- **Hue/family chunking** for 50+ colors
- **Hex code display alongside swatch** (matched against external venue/brand color)
- **Ghost-or-empty placeholder upsell** (no explicit "Add this!" buttons — vary in trigger condition)
- **Inquiry-form-with-design-payload** as the "done" output (no checkout)
- **All declare Frappe-recreatable PASS** (no React, no build step, no NPM, no module imports)
- **All flag the SVG illustration art as an art-direction dependency outside code scope**

This convergence is not laziness — it's research grounding. The brief's frame is well-chosen, and the Frappe constraints push toward a narrow primitive set.

---

## Divergence — genuine differentiators per contestant

| Dimension | C1 | C2 | C3 | C4 |
|---|---|---|---|---|
| **Fill regions per shape** | 2-3 | 4 | 3 + mirror propagation | 2 (primary + accent) |
| **Color picker organization** | Two-tier: Quick Row 12 + Full Sheet by group | 3-component: Recents + 6 hue-family tabs (~5-8 each) + Hex chip | 16-hot 4×4 grid + family rows | 3-section: Recents (8) + Full grid (4-col) + Hex on tap |
| **Composition layout (mobile)** | Horizontal scroll "Event Stage" 160px strip | Tile strip + canvas above | Vertical stack 40% viewport each | Horizontal scroll piece-cards 280×320 |
| **Composition layout (desktop)** | Stage expands to 260px; horizontal persists | Strip → left sidebar; canvas centered; right summary | 3-up grid centered "design book spread" | 3-4 cards visible, same horizontal scroll |
| **Upsell trigger** | After 1st piece completes; suggestion chip pre-colored in customer's palette | After EACH piece completes; ghost cascades unlock more | From the START — empty silhouettes always visible (Zeigarnik) | After 1st piece; updated text suggestion + ghost preview |
| **V1 floor (lowest scope)** | 1 shape (Arch), 2 regions, 12 colors, mailto | 1 shape at a time, no composition, flat 20-color grid | 1 shape, 1 region, full palette, inquiry | 2 shapes (Arch + Column), 1 region each, 12 colors, 2-piece composition |
| **Jeff handoff payload** | Per-piece per-region with hex; Stage 2: "pieces considered" + design snapshot data-URI | Frappe Lead doctype: name, contact, design ref, piece list, palette w/ hex; loud-failure error path | Two-path: form (full payload) + screenshot card (customer's emotional moment) | Per-piece attribution table: Piece × Main × Accent rows |

---

## Distinctive moves to remember

- **C1's color inheritance** (Stage 2): suggestions appear pre-colored in the customer's chosen palette. The customer sees *their* garland already in coral, not a blank "Add a garland?" The discovery move collapses the gap between "what I could add" and "what this would look like."
- **C2's cascading ghosts**: each completion unlocks the NEXT ghost. Composition grows by invitation only — never by explicit prompt. Plus loud-failure error path proactively implemented (not asked for in brief — they did it because the global standing rule lives in the project).
- **C3's Zeigarnik open-from-start + dual-audience design card**: empty silhouettes visible BEFORE the first piece is colored, exploiting the brain's discomfort with incomplete tasks. Plus the design card serves both customer (emotional capture) AND Jeff (supplier-call sourcing) on a single screen with full per-region color name + hex + label payload.
- **C4's spread metaphor + 2-region simplicity**: literalizing the "design book spread" through horizontal piece-cards that match thumb-swipe naturally. 2 fill regions defended as matching the "2-color alternating pattern" mental model that covers most balloon designs (the original "~80%" claim was withdrawn under Loop 1; the underlying argument is sound without the number).

---

## What shifted under Round 1 reflective loops

### Loop 1 — Research-quality probe

Every contestant had at least one citation that did less work than implied. Every contestant addressed the gap honestly:

- **C1**: color inheritance reframed as own first-principles design invention (Fanfaire/Gemar didn't actually demonstrate it). Pigment cite holds with verbatim passage. Baymard 7mm misattributed; corrected URL.
- **C2**: Fanfaire SWAP "inversion" reframed as own design move + NN/G progressive-disclosure citation. UXPin "10-11 per group" was extrapolation; reframed as reasoned constraint. DIY Candy/Recolor mis-cite replaced with NN/G bottom-sheet article.
- **C3**: Medium Zeigarnik source replaced with Laws of UX + ux-bulletin (which explicitly lists "empty states that reference incomplete workflows" as a Zeigarnik application). Baymard cite corrected; Adobe Spectrum picked up for family-grouping. IxDF "2026" guidance discovered to be SEO date marker, not real guidance — replaced.
- **C4**: "~80%" figure was unsupported invention from a broken competitor page; **removed outright**. DesignFiles "horizontal favored" was inference, not finding — reframed as design reasoning. Pigment "no recents" cite strengthened with accurate review-structure characterization.

Net: the field's research grounding tightened materially. Several weak citations replaced with NN/G, Laws of UX, Adobe design systems. Several extrapolations explicitly framed as design judgment rather than pretending to be findings.

### Loop 2 — Jeff's-perspective probe

The Proxy found a cross-cutting issue only visible by reading mockup HTML, not REASONING.md: **three of four contestants designed the customer's emotional moment but didn't follow the data all the way to Jeff's Tuesday morning.** C3 was the exception — already had per-region color name + hex + label payload spec, making them the strongest handoff in the field at end of Round 1. Loop 2 closed the gap for C1, C2, C4:

- **C1** now has hex codes in the form pre-fill + Stage 2 design snapshot data-URI + "pieces considered" field
- **C2** fully fleshed out the `initDoneScreen()` stub with `buildInquiryPayload()`, full Frappe Lead structure, contact-capture in the same screen, and explicit loud-failure error path
- **C3** explicitly claimed handoff-design leadership in REASONING.md; named the dual-audience design card (customer emotional moment + Jeff supplier call)
- **C4** replaced the flat "Main Colors" row with a per-piece attribution table; reframed upsell copy ("in your colors" → "they pair beautifully")

---

## Patterns observed for Round 2

1. **Convergence is real and healthy.** Don't pivot away from the coloring-book frame just to be different — peers all chose it independently for sound reasons. If you pivot, pivot to a stronger frame, not just a contrastive one.
2. **The Jeff-side handoff is the dimension where the field most naturally separates.** C3 leads here; the others closed gaps in Round 1 but C3's two-path design (form for Jeff + screenshot for customer-side sharing) is conceptually distinct.
3. **Fill region count is a real choice with real trade-offs.** 2 (C4) defends as covering the "2-color alternating" mental model. 3 (C3) adds region differentiation. 4 (C2) gives richest customer expression. None are wrong; they serve different audiences.
4. **Color picker organization has 4 different defensible answers.** No clear winner. GL will likely synthesize across multiple if the contest delivers a synthesis-friendly final.
5. **Composition layout splits along scroll-axis lines.** Horizontal (C1, C4) feels mobile-native; vertical-stacked (C3) honors the design-book spread metaphor more literally; canvas-with-strip (C2) is the most "design tool" feeling. Each has a defensible mobile story.
6. **Upsell trigger condition is genuinely contested.** From-the-start (C3) vs. after-first-completion (C1, C2, C4) is a meaningful disagreement about how to balance discovery against blank-canvas anxiety.

---

## What Round 2 should target

Each contestant chooses Path A (Refine), B-lean (commit harder to unique signature), or B-pivot (change conceptual frame). The brief is collaborative — score peers generously, find what to BORROW, sharpen what's distinctly yours.

- **If you Refine (Path A)**: tighten what's already strong. Don't fix what isn't broken.
- **If you Lean (B-lean)**: sharpen the signature move. C1's color inheritance, C2's cascading ghosts, C3's Zeigarnik+dual-audience handoff, C4's 2-region simplicity — these are your distinctive territory. Lean into them.
- **If you Pivot (B-pivot)**: rewrite as needed. Note the prior approach in CHOICE.md for traceability. Pivot toward a gap in the field that's not yet served, not toward a peer's territory.

The field summary above intentionally surfaces what's converged (don't waste round 2 fighting consensus) and what's divergent (your round 2 territory). Read it, then read your own work, then choose your path.

---

*Field summary written by orchestrator at end of Round 1, before Round 2 dispatch.*
