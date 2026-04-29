# Round 2 Choice — Contestant 2

**Path chosen: B-lean (commit harder to the cascading-ghost signature)**

---

## What I'm keeping

The cascading-ghost mechanic is the right idea. The field summary confirms no other contestant chose it, and NN/G's progressive disclosure research still grounds it. I am not pivoting away from it.

The bottom-sheet picker, hue-family tabs, loud-failure error path, and the full `buildInquiryPayload()` handoff spec are all solid. They stay.

---

## What PRODUCT-DETAILS.md forces me to change (not optional)

Two load-bearing corrections from Section 2 + Section 4:

**1. The 53 named LT latex colors replace my generic hex swatches.**
Section 2.8 names all 53 colors verbatim. Section 4 is explicit: color NAME is the supplier-actionable identifier. Hex is downstream eyeball-matching. My Round 1 COLOR_CATALOG used invented generic hex names (Light Pink, Hot Pink, etc.) — those aren't LT's catalog. Updated catalog maps to the actual family clusters the spec provides: Reflex metallics, Dusk muted tones, Pastel soft tints, Brights, Neutrals, Deep tones.

**2. Centerpiece must be removed from the composition.**
Section 2.7 is unambiguous: "drop centerpieces from the design tool." My 04-composition.html had an explicit Centerpiece piece with its own SVG. That piece comes out. The ghost suggestion after Arch + Column becomes a Garland ghost (organic construction only per Section 2.3), which is a legitimate third piece.

---

## What I'm sharpening (the B-lean work)

**Ghost inherits Design style from the preceding piece.**

Round 2's B-lean directive: "sharpen the cascading-ghost mechanic — a ghost column suggested next to a Swirl arch picks up the same Swirl style by default."

This is the right sharpening. The ghost is more compelling when it says "a Column in Swirl, matching your arch" rather than just "Add a column?" The customer sees: the ghost is ALREADY their design. The gap between "what I could add" and "what this would look like" collapses.

Mechanics:
- When the arch Design attribute is Swirl, the ghost column renders with a Swirl spiral preview tinted in the arch's colors
- When it's Organic, the ghost column renders with irregular organic balloon arrangement tinted in the arch's palette
- When it's Layered, the ghost column renders with the banded layer arrangement

This extends naturally: when the ghost is a Garland, it renders as an organic doublet arrangement pre-tinted in the composition's palette.

**Design attribute selector on the coloring screen.**

Section 2.1: Design attribute = Swirl (up to 4 colors) | Layered (up to 8 colors) | Organic (palette-driven). This selector belongs on screen 02 (the coloring screen), before the customer starts picking colors. Color cap enforcement gates the picker accordingly — trying to add a 5th color to a Swirl shows a "Swirl is limited to 4 colors — try Layered for more" nudge.

**Color picker surfaces color NAME first, hex second.**

Section 4 is the standing rule. In Round 1, my hex chip showed hex as the primary large text, name as small secondary. That's backwards for Jeff's Tuesday morning supplier call. Swap: color NAME is the prominent label, hex is the smaller monospace annotation.

---

## What I am explicitly NOT doing

- Not touching the bottom-sheet picker structure (it's sound)
- Not changing the composition layout (strip + canvas works)
- Not adding layout templates (Section 5.2 is OPTIONAL; my ghost mechanic is already a composition-building mechanic — they serve the same goal by different means)
- Not touching `buildInquiryPayload()` — it already carries hex + name per Section 4's requirement
- Not changing the handoff spec — color NAME is already stored alongside hex in the palette string

---

## Files I will change

| File | Change |
|---|---|
| `script.js` | Replace COLOR_CATALOG with 53 actual LT named colors; add Design attribute state; add ghost-inheritance logic; fix hex-chip label priority |
| `04-composition.html` | Remove Centerpiece piece + Centerpiece strip chip; replace with Garland ghost; update ghost label/style to inherit Design context |
| `02-color-one.html` | Add Design attribute selector (Swirl/Layered/Organic); add color cap enforcement copy |
| `REASONING.md` | Add Round 2 section documenting B-lean choice + product-physics alignment + ghost-inheritance rationale |

---

*Choice locked. Executing Round 2 refinements.*
