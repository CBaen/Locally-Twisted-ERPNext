# Peer Scoring — Contestant 3
## Scoring the other three contestants per BRIEF.md Section 8

Rubric dimensions (1-10 each):
- **Experience quality** — does the customer come away feeling "I made this"?
- **Scope discipline** — minimum viable, not maximalist?
- **Frappe-native fit** — recreatable in production stack? No forbidden primitives?
- **Customer clarity** — would a non-designer arriving cold understand the tool in <30s?

---

## Contestant 1 — "The Color Stage"

**Experience quality: 8/10.**
The color-inheritance upsell is the strongest "I made this" moment in the field — seeing a suggested next piece already wearing your own named palette (Raspberry + Reflex Champagne on a ghost garland) collapses the gap between imagining and deciding in a way that empty grey ghosts do not. The "pieces considered" payload adds a level of signal richness no other contestant has: Jeff knows the customer saw the garland in their colors and still said no. The horizontal stage strip is mobile-native and non-wizard. What keeps this from a 9: the color-one screen physics reconciliation (Arch/Column/Garland use style-chip UX instead of tap-region) is correct but adds conceptual complexity the customer must navigate before they color anything. The Backdrop as V1 demo shape is the most physics-honest demonstration but isn't the shape most customers arrive curious about.

**Scope discipline: 8/10.**
V1 floor is well-defined: 1 shape (Backdrop), 2 regions, 12 colors, mailto inquiry. The cuts are correctly identified in priority order. Color inheritance is flagged as Stage 2 (requires palette state across shapes) — this is honest and shows the contestant knows which pieces are additive vs. load-bearing. The "pieces considered" field and the data-URI snapshot are also correctly scoped to Stage 2. One note: the Design style selector (Swirl/Layered/Organic) added to the coloring screen is the right product-physics move but adds UI state the contestant explicitly called Stage 2 in the original V1 floor — the Round 2 scope expanded slightly beyond what the V1 floor committed to, though the expansion is defensible.

**Frappe-native fit: 9/10.**
Rigorous. `$('[data-region="main"]').find('path, circle, ellipse, rect').attr('fill', hex)` is exactly how Frappe-native jQuery SVG manipulation works. The page-scoped `<style>` block over `web_include_css` is the right cascade-conflict avoidance strategy (documented with reasoning — "avoids the known cascade conflict entirely"). The color catalog is a JS array at the top of the Script section — editable without UI changes. No CDN imports, no NPM, no build step. The Frappe CSS theme conflict flag is explicitly documented. Deducted 1 point because the Stage 2 data-URI canvas rasterization is mentioned as a v2 feature without flagging the implementation complexity for that specific path in Frappe.

**Customer clarity: 8/10.**
After Loop 2-1, the entry screen now has "Most people start with an arch. Not sure? Pick anything." which is a clean fix for the undecided parent. The "Popular colors" label above the Quick Row resolves what was a genuinely unlabeled row. The physics reconciliation (style-chip UX for Arch vs tap-region for Backdrop) is honest but introduces two interaction patterns in the same tool — the customer coloring an Arch encounters color-slot chips while the customer coloring a Backdrop encounters tap-regions. At midnight on a 375px screen, that variance requires cognitive switching. The fix is correct architecturally; the clarity cost is real.

**Total: 33/40**

**Notes:** The "pieces considered" payload is the most novel artifact in the entire field — no other contestant named it. It belongs in GL's synthesis as a Jeff-side enhancement that costs almost nothing to implement but gives his pitch substantially more signal. Color inheritance is the warmest upsell mechanic in the field; it doesn't show what the customer could add, it shows what their event already is. The physics reconciliation is honest and thorough; the complexity cost is minor compared to the integrity gain.

---

## Contestant 2 — "The Coloring Book That Assembles Itself"

**Experience quality: 9/10.**
The cascading ghost is the best customer-journey design in the field. The moment where the ghost column appears — already dressed in the arch's palette and Design style — and the customer taps it to confirm is the closest any contestant gets to the brief's "I made this, I want to talk about it now" feeling. The composition grows by invitation only, which is the most respectful version of discovery upselling (no text prompt, no explicit "add this" button, just the obvious next shape already waiting). The B-lean work in Round 2 deepened this: the ghost now inherits not just the palette but the Design style ("a Column in your Swirl style"), which makes it feel like the tool is completing the customer's thought rather than interrupting it with a suggestion. After Loop 2-1, the "Want to add more? totally optional" framing and the "No thanks, I'm done" skip label removed the obligation pressure. The loud-failure error path was added proactively (not required by the brief) — this is the most engineering-mature entry in the field on that dimension.

**Scope discipline: 8/10.**
V1 floor is clean and well-defined: one shape at a time, no composition, flat 20-color grid, inquiry pre-fill. The cascade ghost and multi-piece composition are correctly identified as additive. The `buildInquiryPayload()` and `initDoneScreen()` functions with full Lead field spec is thorough — possibly slightly ahead of V1 scope for the mockup phase, but it demonstrates Frappe-native Lead creation which is production-relevant. The Design-style selector (Swirl/Layered/Organic) with color cap enforcement and the ghost-style-inheritance (`initGhostInheritance()`) are both Round 2 additions that expand the mockup scope — they're well-implemented and physics-honest, but they represent the mockup reaching toward implementation depth that not all contestants matched.

**Frappe-native fit: 10/10.**
The most implementation-complete entry in the field. `frappe.call('frappe.client.insert', ...)` for Lead creation is the correct production path. The explicit Frappe Lead DocType field mapping (`lead_name`, `email_id`, `phone`, `custom_design_ref`, `custom_pieces`, `custom_palette`, `source`) is production-ready — not a placeholder, not a `console.log('would create lead')`. The loud-failure `showSendError()` path is implemented, not just described. The page-scoped single `www/design-studio.html` + controller pattern is confirmed Frappe-native. Zero forbidden primitives. This is the only entry in the field that actually writes the Lead creation code at production quality.

**Customer clarity: 8/10.**
After Loop 2-1, the entry screen with "What are you dreaming of?" and the "Most loved" permission-slip badge is warm and low-anxiety. The Proxy called it "Strongest midnight-entry experience in the field" — that credit is earned. The Design-style pills with descriptor lines ("spiral pattern" / "color bands" / "mixed & flowing") are a solid Loop 2-1 response. The full pre-tinted ghost with Style inheritance is compelling but requires the customer to understand that a faded arch-in-their-colors means "you could add this" — that visual affordance is learnable but requires one mental step. The hue-family tabs (6 small tabs) on the bottom-sheet picker are compact on mobile; the Proxy confirmed they work but the tap targets at 375px are narrow for any tab count above 4.

**Total: 35/40**

**Notes:** This is the highest-quality production implementation in the field. The Lead creation code alone elevates it above mockup territory into working prototype territory. The cascading ghost with Design-style inheritance is the signature move that belongs in GL's synthesis — not as a UX pattern to copy wholesale, but as the principle that the ghost should already be the customer's event, not a neutral blank. The loud-failure error path should be in every form on every screen regardless of whose design wins.

---

## Contestant 4 — "The Coloring Book"

**Experience quality: 7/10.**
The horizontal piece-card composition is the most mobile-native layout in the field — thumb-swiping through colored piece-cards is tactile in a way that vertical stacks and strip+canvas aren't. The "Discuss This Design" done screen is warm and well-framed. The per-piece attribution table (piece × Main × Accent rows with name-first hex-secondary) is clean and Jeff-readable. What keeps this from higher: the 2-region simplicity, while physics-honest for the Swirl default, means the customer's completed design has less visual complexity to feel proud of — a 2-color arch next to a 2-color column is pleasant but doesn't produce the "I made something specific to me" feeling at the same intensity as designs with 3-4 colors + style variation. The discovery upsell (contextual text suggestion in the Add card) is the weakest in the field — it's text-only, and after seeing C1's color-inheritance chips and C2's pre-tinted ghosts, a text suggestion feels like a step back toward the configurator model.

**Scope discipline: 9/10.**
The tightest V1 floor in the field: 2 shapes, 1 region each, 12 swatches, composition of 2 pieces side-by-side, "Discuss This Design" → inquiry. The "~100 lines of CSS and ~80 lines of JS" commitment is backed up by the simplicity of the design — this is genuinely achievable in that footprint. Path A (Refine) was the right call for this entry: the physics grounding added by Round 2 strengthens the 2-region defense without scope creep. The Organic → palette-only branch is correctly scoped (no fill regions, just color swatches) and honestly flags what the tool cannot represent (controlled-random arrangement). The explicit "floor I would not cut below: SVG illustrations must be good enough" is the right bottom constraint.

**Frappe-native fit: 9/10.**
Clean. Inline SVG in Jinja `www/` template, jQuery event binding, CSS via co-located file or `web_include_css`, no NPM, no build step, no CDN chain imports. The bottom sheet as CSS-positioned `<div>` with `transform: translateY` toggle is the correct Frappe-native implementation. The SVG illustration art dependency is explicitly flagged ("the illustrations need to be drawn specifically for this tool with named fill regions — this is design work outside the code scope") — the most honest and complete art-direction flag in the field. Deducted 1 point because the `localStorage`-backed Recently Used row is mentioned in REASONING but the contest brief explicitly excludes persistence mechanisms during the design experience; localStorage is not a forbidden primitive but it crosses into state persistence territory the brief flags as "downstream."

**Customer clarity: 9/10.**
The strongest customer clarity in the field after Loop 2-1. The visual thumbnails inside style toggle buttons ("Alternating" with A-B-A-B circle pattern / "Mixed" with 4-color irregular pattern) is the move the Proxy called the crown jewel — and it earns that description. A parent at midnight sees the pattern before they read the label. The construction vocabulary is fully translated into customer vocabulary: "Swirl" → "Alternating," "Organic" → "Mixed," "Design Style" → "How do you want the colors arranged?" The 2-region simplicity is a genuine customer-clarity advantage: two things to color, one at a time, is lower anxiety than three or four. The horizontal piece-cards at ~1.3 visible cards is a clean "scroll for more" signal. The hint text simplification ("Two colors take turns all the way around. You pick both — Jeff makes it happen.") is the best plain-language copy in the field.

**Total: 34/40**

**Notes:** The visual-thumbnail-inside-style-button principle is the most universally applicable synthesis item from this entry — it should propagate to every style choice in the final tool regardless of whose design wins. C4's explicit art-direction dependency flag is the most honest and complete version of this acknowledgment in the field; GL should treat the illustration quality as the make-or-break constraint the contestant correctly identifies it as. The 2-region simplicity is genuinely more accessible at midnight but genuinely less expressive for the customer who wants specificity — GL's synthesis should hold both instincts in tension.

---

## Summary table

| Contestant | Experience | Scope | Frappe | Clarity | Total |
|---|---:|---:|---:|---:|---:|
| C1 "The Color Stage" | 8 | 8 | 9 | 8 | 33/40 |
| C2 "Assembles Itself" | 9 | 8 | 10 | 8 | 35/40 |
| C4 "The Coloring Book" | 7 | 9 | 9 | 9 | 34/40 |

---

## Self-Reflection — Where My Work is Weakest Relative to the Field

**Implementation depth.** C2 wrote actual `frappe.call()` Lead creation code at production quality. My done screen fires an inquiry form pre-populated with design data — the concept is right, the code is a placeholder (`$(this).text('Opening inquiry form…')`). C2's entry is a working prototype; mine is a mockup that describes what a working prototype would do. GL building from my design would have to write the Lead creation layer from scratch; GL building from C2's design has it already.

**Discovery upsell warmth.** C1's color-inheritance chips and C2's pre-tinted ghost are both warmer than my Zeigarnik empty-slot silhouettes at the composition level. My silhouettes are grey and neutral — they show the shape of what's missing, not what it would look like in the customer's palette. The distinction matters at midnight: a grey column silhouette says "there's a space here"; a Raspberry + Reflex Champagne column says "this is what your event looks like with one more piece." My silhouettes exploit the incompleteness feeling; the peers' colored ghosts exploit the completion feeling. The completion feeling is warmer and more specific to this customer's event.

**Entry screen orientation.** C2's "What are you dreaming of?" headline with "Most loved" permission badge, and C1's "Most people start with an arch. Not sure? Pick anything." both do more work than my three-step ①②③ how-it-works row at helping the undecided parent commit to a first tap. My entry screen tells the parent what the tool does; theirs tells the parent what to do first. The gap is one line of copy — small but real.
