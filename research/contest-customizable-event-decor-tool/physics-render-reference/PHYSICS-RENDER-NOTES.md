# Physics Render Reference - Notes

This directory holds **binding math references** for the eventual Frappe Design Studio implementation. The contest mockups demonstrated UX framework choices but stayed in *abstract pretty circles* register and did not render the actual balloon construction physics. This reference is the corrective: the math the eventual build is bound to.

## Origin: GL's existing implementation

GL had already built the correct balloon physics in a prior platform attempt at:

> `C:\Users\baenb\projects\locally-twisted-app\` — Next.js + Three.js + React Three Fiber + a CSS3D fallback. Frappe-recreatable path: the CSS3D version (no library required).

Specifically:
- `src/components/balloon-preview-3d.tsx` — `generateArchBalloons`, `generateColumnBalloons` (Three.js)
- `src/app/design/page.tsx` — `DesignPreview` (CSS3D, no library)
- `src/app/design/page.tsx` — `balloonColors` (the 48-color real LT catalog in 4 categories)

The Next.js framework is superseded by the current LT ERPNext build, but **the physics math is correct and load-bearing**. Anyone implementing the Design Studio in Frappe must port from this code, not invent.

## What lives here

| File | Status | What it proves |
|---|---|---|
| `swirl-arch.html` | Built 2026-04-29 (corrected) | Quad-cluster physics: 4 balloons radiate outward from center rope, 45-degree spiral rotation per cluster, Swirl + Layered color logic, real LT 48-color catalog. CSS3D transforms (translateZ + perspective + preserve-3d), no library, Frappe-recreatable. |
| `column.html` | Not built | Vertical quad-cluster stack with 45-degree spiral. Math: port from `generateColumnBalloons` in balloon-preview-3d.tsx. |
| `garland.html` | Not built | Flowing horizontal with wave path + 3 depth layers. Math: port from `DesignPreview` garland branch in app/design/page.tsx. |
| `wall.html` | Not built | Honeycomb grid with 3 depth layers. Math: port from `DesignPreview` wall branch. |

LT's actual Design Tool catalog has **4 product types**: Balloon Arch, Balloon Garland, Balloon Column, Organic Display Wall. (The earlier contest framing of 6 shapes — adding Backdrop, Drop, Bouquet — does not match the existing implementation. Confirm with GL before designing for shapes not in this list.)

Each future shape file is binding for the implementation phase. Build instances must port from GL's existing math; they do not get to invent their own rendering.

## Why this exists (and why the FIRST version of this prototype was wrong)

The contest produced 4 strong UX framework references but ZERO physics-faithful renderings. None of the contest mockups showed:

- A 4-balloon cluster rendered as a quad radiating outward from a rope
- 45-degree spiral rotation per cluster (the source of the dense interlocking pattern)
- Real-world balloon density (40 per 5 ft of arch)
- Real LT catalog colors with names

The first iteration of `swirl-arch.html` (built 2026-04-29 morning) made the same kind of error in a different form: it rendered a 2D diamond cluster on a 2D arch curve. Balloons appeared FLAT, like a hollow ring. GL caught this immediately and pointed at the existing 3D modeling. This file documents the corrected math so the next instance does not repeat the same drift.

**The wrong version (first iteration of this file):**
- Diamond pack lying flat on the curve plane
- Spiral effect implemented as color rotation `(c * s + b) mod N`
- Generic placeholder colors

**The correct version (current):**
- Quad cluster radiates outward from the rope in 3D (some balloons forward via translateZ, some backward — a tube structure, not a flat ring)
- Spiral effect implemented as a 45-degree PHYSICAL rotation per cluster
- Swirl color = balloon position within quad; Layered color = bands of 2 quads same color
- Real LT 48-color catalog

## Math captured in `swirl-arch.html`

### Real-world units (catalog-grounded)

```
11" balloon = 0.458 ft radius = 0.917 ft diameter
Industry standard: 40 balloons per 5 feet of arch
                 = 8 per foot
                 = 2 quad clusters per foot
```

### Quad cluster radiates outward from rope

Each cluster is 4 balloons tied at necks, with the tie point ON the rope and balloon centers offset radially OUTWARD. This produces a 3D tube around the rope, not a flat ring.

```
balloonsPerCluster = 4
tubeRadius = 4               // % of container width (offset from rope)
spiralAngle = PI / 4         // 45 degrees, fixed

For balloon b in cluster c:
  // Each balloon points in one of 4 directions (every 90 deg)
  // Plus the cluster's spiral rotation
  angleInCluster = b * (PI / 2) + (c * spiralAngle)
  
  // Local offset in cluster (outward in cluster plane)
  localX = cos(angleInCluster) * tubeRadius
  localZ = sin(angleInCluster)              // normalized for Z depth
```

The `localZ` value goes into a CSS `translateZ()` for actual 3D depth. With `perspective: 600px` on the parent, near balloons grow and far balloons shrink — the dense interlocking tube reads correctly.

### Arch curve (half-circle parametrization)

```
For cluster c (0 to totalClusters-1):
  t = c / (totalClusters - 1)        // [0, 1]
  angle = t * PI                     // 0 (left foot) -> PI (right foot)
  
  curveX = cos(angle)                // -1 to +1
  curveY = sin(angle)                // 0 -> 1 -> 0 (peaks at PI/2)
```

### Cluster offset rotates to follow tangent

The cluster's "outward-from-rope" direction must align with the local arch tangent. Tangent angle at any point on the half-circle is `angle - PI/2`.

```
tangentAngle = angle - PI/2

// Rotate the local offset to follow the arch
rotatedOffsetX = localX * cos(tangentAngle)
rotatedOffsetY = localX * sin(tangentAngle)

// Final container-% position (the on-curve point + the radial offset)
finalX = archCenterX + curveX * archRadius + rotatedOffsetX
finalY = archBaseY  - curveY * archRadius * 0.85 + rotatedOffsetY
finalZ = localZ * 15                 // depth in pixels
```

### Color logic by Style

**Swirl style (max 4 colors):**

```
colorIndex = balloonInCluster % colors.length
```

Within each quad, colors cycle by balloon position (0,1,2,3). With 2 colors → A-B-A-B; with 4 → A-B-C-D. The 45-degree physical rotation between clusters makes this read as a barber-pole twist.

**Layered style (max 8 colors):**

```
clustersPerBand = 2                          // 2 quads = 8 balloons per band
bandIndex = floor(clusterIndex / 2)
colorIndex = bandIndex % colors.length
```

ALL balloons in a cluster get the SAME color. Pattern across the arch: AA-BB-CC-DD. The physical 45-degree rotation still happens (it's structural to the cluster geometry) but does not produce a color twist.

### Back-to-front Z-sort (CSS3D layering)

After computing all balloon positions, sort by Z so the renderer draws from back to front:

```
balloons.sort((a, b) => a.z - b.z)
```

CSS3D does NOT auto-sort by Z. Without this, near balloons can render UNDER far ones, breaking the 3D illusion.

## Visual rendering (CSS3D + radial-gradient)

The HTML structure:

```
<div class="scene" style="perspective: 600px">
  <div class="scene-3d" style="transform-style: preserve-3d">
    <!-- one absolute-positioned div per balloon -->
    <div class="balloon" style="
      left: X%;
      top: Y%;
      transform: translate(-50%, -50%) translateZ(Zpx) rotate(deg);
      background: radial-gradient(...);
      border-radius: 50% 50% 50% 50% / 45% 45% 55% 55%;
    ">
      <div class="balloon-highlight"></div>
    </div>
  </div>
</div>
```

Visual choices ported from `DesignPreview` in app/design/page.tsx:

| Choice | Value | Source |
|---|---|---|
| Balloon size base | 22 px | tuned for 4:3 container |
| Balloon shape | `border-radius: 50% 50% 50% 50% / 45% 45% 55% 55%` | slightly elongated downward, like real latex balloon |
| Standard gradient | radial 3-stop with white highlight + base + dark | port |
| Chrome gradient | radial 5-stop with stronger reflections | port |
| Highlight overlay | 35% × 25% ellipse at top-left, 80% white opacity | port |
| Chrome secondary highlight | 22% × 15% ellipse at bottom-right, 50% opacity | port |
| Box-shadow standard | inset highlights + drop-shadow | port |
| Box-shadow chrome | stronger inset highlights + drop-shadow | port |
| Depth scale | `1 + z / 150` | closer balloons grow, far balloons shrink |
| Container perspective | `perspective: 600px` on `.scene` | port |
| Z-sort | back-to-front (smallest z first) | port |

### Chrome detection

```
isChrome(name) = name includes 'chrome' OR 'metallic' OR 'champagne'
```

Drives gradient selection and box-shadow strength.

## Real LT 48-color catalog (verbatim from app/design/page.tsx)

| Category | Count | Examples |
|---|---:|---|
| Standard | 17 | White, Black, Red, Raspberry, Fuchsia, Bubble Gum, Orange, Yellow, Forest, Shamrock, Lime, Teal, Turquoise, Caribbean, Navy, Sapphire, Periwinkle |
| Pastels | 12 | Pastel Pink, Spring Lilac, Lavender, Pink, Coral, Coral Blush, Peach, Apricot, Mint Bliss, Sage, Dusty Blue, Fog |
| Neutrals | 9 | Ivory, Grey, Caramel, Buttercup, Mustard, Gold, Vintage Rose, Nude, Wild Berry |
| Chrome | 10 | Chrome Gold, Chrome Silver, Chrome Rose Gold, Chrome Pink, Chrome Red, Chrome Blue, Chrome Violet, Chrome Green, Champagne, Chrome Fuchsia |

These are the names Jeff orders by. Hex codes are GL's confirmed values from the Locally Twisted color sheets — these are the real catalog values, not approximations.

The total is 48; if the canonical LT catalog says 53, the difference is 5 colors not yet in this app's data file. Confirm with GL before assuming 48 is final. The implementation should source from a `LT Balloon Color` DocType (recommended) or `apps/locally_twisted/locally_twisted/data/balloon_colors.json` rather than hard-coding the array.

## How the eventual Frappe build uses this

The Design Studio portal page (post-Phase-1, scoped per `.planning/decisions/site-shape.md`) will:

1. **Port the math directly** from this file's `generateArchBalloons` (and the analogous functions for column/garland/wall) into `apps/locally_twisted/locally_twisted/www/design-studio.js` (or an equivalent module).
2. **Use CSS3D** for the visual approach. Three.js is overkill for this use case + would add ~600 KB to the asset bundle. CSS3D + radial-gradient + back-to-front z-sort gives the same visual fidelity at near-zero asset cost.
3. **Source colors from a DocType** — `LT Balloon Color` with fields: name, hex, category. Seed it from this app's `balloonColors`. Lets Jeff edit colors in the desk.
4. **Wire to customer selection** — `frappe.call()` to a whitelisted method that creates a Lead with `design_studio_payload` Custom Field (Long Text JSON).

Same file shape as `/contact` and `/checkout` already shipped: controller (`design-studio.py`) + template (`design-studio.html`) + page JS (referenced via `PAGE_JS` attribute) + appended BEM CSS in `lt-theme.css`.

**Do not deviate from this math during implementation without first updating this reference AND syncing with the locally-twisted-app source.**

## How to extend

To add a new shape reference:

1. Identify the source function in `locally-twisted-app/` (e.g., `generateColumnBalloons` in balloon-preview-3d.tsx, or the column/garland/wall branch of `DesignPreview` in app/design/page.tsx).
2. Create `<shape>.html` here using `swirl-arch.html` as the template.
3. Port the math, keeping variable names + comments matching the source for traceability.
4. Render via Playwright at mobile + desktop; save to `_render/physics-reference/<shape>-{mobile,desktop}.png`.
5. Read each render to verify (no reporting-without-watching).
6. Update this file's table with what the new shape proves.

## Caveats

### Color count is 48 in app data, possibly 53 in canonical catalog

The `balloonColors` constant in app/design/page.tsx has 48 colors. The contest brief mentioned 53 named colors. Reconcile before finalizing the DocType seed — Jeff is the source of truth for the actual count.

### CSS3D performance ceiling

The prototype caps render at 160 balloons by default (slider goes to 320). Real installs use the full count (40 ft arch = 320 balloons). On lower-end devices CSS3D may stutter at 320; this is a runtime perf concern, not a math concern. The implementation can either keep the cap (visual-fidelity vs perf trade) or render at full count — confirm with GL.

### What this shape's prototype does NOT show

The arch shape proves quad-cluster geometry + 45-degree spiral + Swirl/Layered color logic. It does NOT prove:
- Vertical column gravity (column.html will)
- Garland wave-path with depth layers (garland.html will)
- Honeycomb wall packing with 3 depth layers (wall.html will)
- AR overlay onto a real-world photo (in app/design/page.tsx as the `BackdropPlane` + custom photo upload — different concern, not strictly physics)
- Customer-uploaded photo as backdrop (separate UX feature)

Each of those needs its own port before the implementation phase begins.

---

*Reference rewritten 2026-04-29 (afternoon) by the Opus 4.7 instance who first built a wrong version of this prototype, was corrected by GL ("the rendering of the balloons is bad — there's a 3D modeling I made"), found GL's existing locally-twisted-app code, and ported the actual physics. The wrong version is preserved only in git history.*
