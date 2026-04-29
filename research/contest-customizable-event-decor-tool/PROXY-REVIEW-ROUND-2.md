# Proxy Review — Round 2 Tightening Pass
## One section per contestant. Polish, not redesign.

---

## Contestant 1 — "The Color Stage"
**Crown jewel:** The pieces-considered payload field

### Tighten this

1. **Make the crown jewel visible.** Right now "pieces considered" lives in REASONING.md and nowhere a render-gallery viewer will see it. Add it to `05-done.html`: show a "Suggestions you considered" row with grayed-out color chips representing the suggestions the customer didn't pick. Even two or three grayed chips communicates the concept. This is the move that makes the Jeff-side payload visible without explaining it — GL can see it.

2. **Resolve the mockup/REASONING misalignment in `02-color-one.html`.** Your REASONING describes a style-chips-then-color-slots interaction. Your mockup shows tap-region UX. Pick one and make the file agree with the description. Either approach is defensible — the misalignment is what isn't. If the render gallery captures both, the contest record shows contradiction, not intention.

3. **Per-region attribution on the done screen.** C3's completion card shows which color goes on which region with a label. Borrowing even a minimal version of this (Main: Cobalt Blue / Accent: Blush) strengthens the Jeff-side handoff without redesigning your crown jewel.

### Don't change

The two-interaction-pattern split (Backdrop tap-region vs. Arch/Column/Garland style-then-color). It's ergonomically correct — different shapes genuinely warrant different interaction modes. Don't homogenize it under pressure.

### Stretch goal (optional)

Show a second contestant's ghost inheriting the C1-customer's palette in a preview frame — make the color-inheritance mechanic *visible in the mockup*, not just described in REASONING. That's the move that demonstrates the pipeline position.

---

## Contestant 2 — "The Coloring Book That Assembles Itself"
**Crown jewel:** Cascading ghost mechanic with pre-tinted color inheritance

### Tighten this

1. **Visual thumbnails inside Design pills.** Your Design selector (Swirl / Layered / Organic) still uses text-only labels. C4's visual-SVG-thumbnail approach is the field's most universally borrowable refinement — and it strengthens YOUR crown jewel by reducing style-selection friction before the ghost even appears. If a customer can't pick Swirl vs. Organic confidently, the ghost mechanic never gets to do its work. Add small SVG pattern previews inside the pills.

2. **Audit "permission to ignore" copy end-to-end.** You added it in R2 Loop 1 — good move. Now check every screen in the flow for residual obligation language that contradicts it. Look for anything phrased as "complete your design" or "add more" without a qualifier. The ghost is only invitation if nothing else in the flow says "you're not done."

3. **Done-screen portrait card.** C3's completion card is the field standard for handoff quality. Your done screen doesn't need to match it exactly, but borrowing the per-region color label structure (Main: [name] / Accent: [name]) strengthens the Jeff-side payload without touching the ghost mechanic at all.

### Don't change

The ghost with color inheritance. Do not simplify it to a neutral-fill ghost under polish pressure. The pre-tinting is the mechanic — a neutral ghost is a different, weaker idea. Hold it.

### Stretch goal (optional)

Show the ghost appearing mid-screen as an animation state in the mockup (even a static before/after frame). GL needs to SEE the ghost moment, not imagine it from a description. A two-frame static mockup of "screen before ghost" and "screen after ghost appears" would lock this into the render gallery as visually distinct.

---

## Contestant 3 — "The Coloring Page Frame"
**Crown jewel:** Dual-audience-card framing (one screen serving customer emotional moment AND Jeff supplier call)

### Tighten this

1. **Entry screen first-step affordance.** Your how-it-works row (①②③) orients parents to the process but doesn't tell them what to do *first*. Add one short line above the shape cards — something like "Start by picking your main piece" — so there's no moment of "now what?" between reading the steps and tapping. Multiple signals named this gap.

2. **Fix the hardcoded event title.** If a mockup screen shows a specific event title (e.g., "Emma's Birthday"), make it generic ("Your Event") or clearly parametric. A hardcoded name in a render gallery looks like a demo artifact, not a design decision.

3. **Remove centerpiece from upsell copy.** Centerpiece was dropped from scope. Any residual reference in the upsell screen misrepresents the tool's scope for GL and for Jeff. Find and replace.

4. **Warm up the upsell silhouettes.** The Zeigarnik empty-slots are doing good compositional work. Consider whether a light color wash (borrowing from C1's inheritance pattern) could make them feel like *invitations* rather than *voids* — without collapsing into C2's full ghost mechanic. A 20% opacity color hint is different from a pre-tinted ghost.

### Don't change

The dual-audience framing itself. Do not simplify the completion card by removing hex codes or role labels under "this is too much information for a customer" pressure. The framing says both audiences are served on one screen — simplifying for one audience breaks the principle.

### Stretch goal (optional)

Add a small "What Jeff sees" annotation to the completion card mockup — a callout arrow pointing to the supplier-call data block with the label "Jeff uses this to source your order." That annotation makes the dual-audience principle legible to GL without GL having to infer it.

---

## Contestant 4 — "The Coloring Book"
**Crown jewel:** Visual SVG thumbnails inside style buttons — the move that lets any parent make the right style choice with their eyes, not their vocabulary

### Tighten this

1. **Fix the empty recently-used row.** On first load, the recently-used color row is empty. Right now it reads as a loading failure — a blank space where something should be. Either hide the row entirely until it has content, OR add friendly placeholder copy: "Colors you pick will appear here." This is a small fix with a significant perception impact at first impression.

2. **Entry screen warmth pass.** Your entry screen is the most functionally clear of the four but the least emotionally inviting. Add one short line of welcoming copy above the shape cards — something that tells the parent why this is going to be easy, not just what they're about to do. "Pick your piece, pick your colors, we'll take it from there" is the register to aim for.

3. **Upsell color inheritance.** Your discovery mechanic is the weakest in the field (text suggestion, generic ghost). You don't need to build C2's full cascade — but consider whether your ghost could wear a light hint of the customer's existing palette. Even 30% opacity inheritance would lift the upsell from "generic prompt" to "this thing knows what I picked."

### Don't change

The visual SVG thumbnails inside style buttons. Do not let polish pressure collapse them back to text labels. This is your crown jewel's public face — the thing GL will see and borrow for the synthesis. If the thumbnails get removed, the distinctive disappears.

The 2-region floor. The physics argument is correct. Do not add a third region under "more options = more value" pressure. The simplicity is the point.

### Stretch goal (optional)

Show the Alternating vs. Mixed SVG thumbnails at a slightly larger scale in the mockup so the visual distinction reads clearly at mobile resolution. If the thumbnails are too small to distinguish on a 6.1-inch screen, the whole mechanic collapses to text anyway. Verify they're legible at actual phone size.
