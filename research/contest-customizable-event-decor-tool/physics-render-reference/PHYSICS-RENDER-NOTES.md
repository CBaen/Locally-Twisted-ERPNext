# Physics Render Reference - Notes

This directory holds **binding math references** for the eventual Frappe Design Studio implementation. The contest mockups demonstrated UX framework choices but stayed in *abstract pretty circles* register and did not render the actual balloon construction physics. This reference is the corrective: the math that the eventual build is bound to.

## What lives here

| File | Status | What it proves |
|---|---|---|
| `swirl-arch.html` | Built 2026-04-29 | 4-balloon cluster atomic unit + spiral color rotation + math-driven cluster placement on a half-circle arch curve. Vanilla JS + inline SVG, no React, no build step. Frappe-recreatable. |
| `column.html` | Not built | Column gravity rules + main-color-with-topper construction |
| `garland-organic.html` | Not built | Doublet-on-strip + 5" filler + 60/30/10 size mix + no-touching-twins controlled randomness |
| `backdrop.html` | Not built | `clusters = width_ft x height_ft` math + stripe / X-design patterns |
| `drop.html` | Not built | Helium-drop physics; ceiling anchor + cluster cascade |
| `bouquet.html` | Not built | Theme-locked anchor + inflation pattern (theme-locked per LT catalog) |

Each future shape file is binding for the implementation phase. Build instances must use these math references; they do not get to invent their own rendering.

## Why this exists

The contest produced 4 strong UX framework references but ZERO physics-faithful renderings. None of the mockups showed:

- A 4-balloon cluster rendered as 4 circles in a diamond pack
- Spiral color rotation across clusters following `(c * s + b) mod N`
- Garland doublet-on-strip + size mix + no-touching-twins
- Backdrop sqft x cluster count with the cluster grid as visual pixels
- Organic flow controlled randomness

GL provided this physics in two AI research dumps + direct conversation; the contestants documented it in `PRODUCT-DETAILS.md` but did not implement it visually. Without an explicit binding reference, the implementation phase risks the same drift: "we'll render abstract circles and call it good." This directory prevents that.

## Math captured in `swirl-arch.html`

### Arch curve (half-circle parametrization)

```
For cluster i in [0, N-1]:
  t = i / (N - 1)              // [0, 1]
  theta = pi * (1 - t)         // pi -> 0  (left foot -> right foot)
  x = cx + rx * cos(theta)
  y = cy - ry * sin(theta)     // SVG y-down; minus -> upward
```

### Cluster orientation (rotates to follow outward normal)

Closed form: `rotation = pi/2 - theta`

Verified at three positions:
- `theta = pi` (left foot): `rotation = -pi/2` -> diamond rotates -90, top points left (outward)
- `theta = pi/2` (top of arch): `rotation = 0` -> no rotation, top points up
- `theta = 0` (right foot): `rotation = pi/2` -> diamond rotates +90, top points right (outward)

### 4-balloon diamond cluster

Default positions (untransformed; T/R/B/L):

```
pos 0 (top):    ( 0, -offset )
pos 1 (right):  ( offset, 0 )
pos 2 (bottom): ( 0,  offset )
pos 3 (left):   (-offset, 0 )

offset = balloon_radius * 0.7   // intentional overlap -> reads as cluster
```

Apply 2D rotation matrix to each (dx, dy):

```
rotDx = dx * cos(rotation) - dy * sin(rotation)
rotDy = dx * sin(rotation) + dy * cos(rotation)

balloon.cx = center.x + rotDx
balloon.cy = center.y + rotDy
```

### Spiral color rotation

For balloon `b` in cluster `c` with N colors, spiral_step `s`:

```
color_index = (c * s + b) mod N
```

Examples (N=4, s=1):
- Cluster 0 -> [0, 1, 2, 3]
- Cluster 1 -> [1, 2, 3, 0]
- Cluster 2 -> [2, 3, 0, 1]
- Cluster 3 -> [3, 0, 1, 2]   (then repeats)

### Min repeat (informational)

Smallest cluster count before pattern repeats:

```
min_repeat = N / gcd(N, 4)

N=2: min_repeat = 1     (alternating)
N=3: min_repeat = 3
N=4: min_repeat = 1     (rotates one position per cluster; visual cycle = 4)
N=5: min_repeat = 5
N=6: min_repeat = 3
N=7: min_repeat = 7
N=8: min_repeat = 2
```

Note: `min_repeat * spiral_step` gives the visual cycle length when `gcd(spiral_step, N) = 1`.

## Visual rendering choices

These are aesthetic decisions in the prototype, NOT binding math:

| Choice | Value | Rationale |
|---|---|---|
| Balloon radius | 16 px | Reads cleanly at 800x500 viewBox; scales with viewport |
| Cluster overlap | 70% of radius | Tight enough to read as cluster, loose enough to distinguish individual balloons |
| Render order within cluster | bottom -> right -> left -> top | Natural visual stacking; top balloon overlaps |
| Balloon highlight | rgba(255,255,255,0.5) at 22% radius, upper-left | Faux-3D depth cue |
| Stroke | rgba(0,0,0,0.15) at 1px | Edge definition without harshness |
| Arch leg | 4px wide silver pole, 24x4 foot plate | Mimics real LT setup poles |

The implementation phase can adjust these without breaking the binding math. **The math is binding; the visual treatment is style.**

## Caveats

### Hex codes are placeholders

The `LT_COLORS` array in `swirl-arch.html` uses approximate hex values for 10 LT named colors:

```
Blush, Dusk Blue, Empowermint, Raspberry, Coral, Lilac,
Champagne, Soft Yellow, Sage, Eucalyptus
```

The actual hex codes for the 53-named-color LT catalog **are not yet locked**. Implementation must source these from:
1. Jeff's confirmed catalog (preferred)
2. A `LT Balloon Color` DocType seeded from the confirmed catalog (recommended for editability)
3. A static JSON file at `apps/locally_twisted/locally_twisted/data/balloon_colors.json` (acceptable fallback)

Do NOT hard-code the prototype's hex values into production. They were chosen for visual demonstration only.

### Ellipse vs. circle

The prototype uses `rx = archWidth/2` and `ry = archHeight`, producing an ellipse arch. The closed-form rotation `pi/2 - theta` is the exact tangent ONLY when `rx = ry` (true circle). For `rx != ry`, cluster orientations slightly drift from the perfect outward-normal at intermediate positions. Visually negligible at LT's typical proportions. If the implementation needs perfect ellipse tangents, use:

```
tangent_dx = -rx * sin(theta)
tangent_dy = -ry * cos(theta)
tangent_angle = atan2(tangent_dy, tangent_dx)
rotation = tangent_angle - pi   // perpendicular to tangent
```

### What the prototype does NOT show

These belong to other shape references (not this one):
- Garland organic-flow randomness
- No-touching-twins constraint
- 60/30/10 size mix (60% 11", 30% 5", 10% 16")
- Backdrop sqft -> cluster grid
- Column gravity / inflation order
- Drop ceiling-anchor cascade
- Bouquet anchor + helium dynamics

Each shape needs its own `physics-render-reference/<shape>.html` page before that shape can be safely implemented.

## How the eventual Frappe build uses this

The Design Studio portal page (post-Phase-1, scoped per `.planning/decisions/site-shape.md`) will:

1. **Inline this math directly** in `apps/locally_twisted/locally_twisted/www/design-studio.js` (or an equivalent module).
2. **Inline the SVG render functions** as JS functions that take `{colors, size, spiralStep}` and return SVG element trees.
3. **Wire to the customer's selected colors** from the LT catalog (sourced from `LT Balloon Color` DocType or equivalent).
4. **On "Send to Jeff"**: package the design state (shape + colors + size + spiral step + any other inputs) as a JSON payload on the Lead record's `design_studio_payload` Custom Field (Long Text).

The same file structure as `/contact` and `/checkout` already shipped: controller (`design-studio.py`) + template (`design-studio.html`) + page JS (referenced via `PAGE_JS` attribute) + appended BEM CSS in `lt-theme.css`.

**Do not deviate from this math during implementation without first updating this reference.**

## How to extend

To add a new shape reference:

1. Create `<shape>.html` in this directory using `swirl-arch.html` as the template.
2. Implement the shape's physics math at the top of the script section, with comments matching the math notes section.
3. Add the shape to the table at the top of this file.
4. Render via Playwright at mobile + desktop; save to `_render/physics-reference/<shape>-{mobile,desktop}.png`.
5. Read each render to verify (no reporting-without-watching).
6. Document caveats specific to that shape's math.

---

*Reference seeded 2026-04-29 by the Opus 4.7 instance who finished the contest render gallery + final surface and built this prototype after GL named the gap: "the framework of 1 is good. The rendering of the balloons is bad."*
