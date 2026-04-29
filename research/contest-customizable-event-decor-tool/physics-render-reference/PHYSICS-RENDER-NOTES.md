# Physics Render Reference - Notes

This directory holds **binding render references** for the eventual Frappe Design Studio implementation. The contest mockups stayed in *abstract pretty circles* register and did not render the actual balloon construction physics. This reference is the corrective: GL's actual implementation, ported from the existing `locally-twisted-app` source.

## Origin: GL's existing implementation

GL has a working balloon physics renderer at:

> `C:\Users\baenb\projects\locally-twisted-app\` — Next.js + React Three Fiber (which is a React wrapper over Three.js 0.182.0).

Specifically:
- `src/components/balloon-preview-3d.tsx` — `generateArchBalloons`, `generateColumnBalloons`, `BalloonScene`, `BalloonInstances` (Three.js)
- `src/app/design/page.tsx` — `balloonColors` constant (the 48-color real LT catalog)

The Next.js framework is superseded by the current LT ERPNext build, but the physics math + Three.js scene setup are correct and load-bearing. Anyone implementing the Design Studio in Frappe must port from this code, not invent.

## What lives here

| File | Status | What it proves |
|---|---|---|
| `swirl-arch.html` | Built 2026-04-29 (Three.js port) | Vanilla Three.js (CDN via importmap) rendering of `generateArchBalloons` + `BalloonScene`. Visual fidelity matches GL's actual render at `localhost:3000/design`. |
| `column.html` | Not built | Vertical quad-cluster stack with 45-degree spiral. Math: port from `generateColumnBalloons` in balloon-preview-3d.tsx. |
| `garland.html` | Not built | Flowing horizontal with wave path + 3 depth layers. |
| `wall.html` | Not built | Honeycomb grid with 3 depth layers. |
| `capture_ground_truth.py` | Built 2026-04-29 | Captures GL's actual app render at `localhost:3000/design` for comparison. Requires GL's dev server running. |
| `render.py` | Built 2026-04-29 | Captures my port at mobile + desktop; saves to `_render/physics-reference/swirl-arch-{mobile,desktop}.png`. |
| `COMPARISON.md` | Built 2026-04-29 | Side-by-side comparison of my port vs GL's actual render with what matches and what differs. |

LT's Design Tool catalog has **4 product types**: Balloon Arch, Balloon Garland, Balloon Column, Organic Display Wall.

## Why this exists (and why two earlier iterations were wrong)

The contest produced 4 strong UX framework references but ZERO physics-faithful renderings. Without a binding reference, the implementation phase risks the same drift: rendering abstract circles and calling it good.

This file went through **two wrong iterations** before landing on the correct one. Both are worth documenting so the next instance doesn't repeat:

1. **Iteration 1 (CSS3D-with-invented-knobs):** Rendered using HTML divs with `radial-gradient` backgrounds + CSS3D transforms. Added a render-cap slider (40-320 balloons) that wasn't in any source. Used balloon size 22 px when GL's source uses 15 px. Self-assessed as "looks like a balloon arch" without comparing to GL's actual render. GL caught it: *"This isn't even close. I don't know why you added multiple balloon sizes."*

2. **Iteration 2 (CSS3D, stripped):** Removed the slider, fixed balloon size to 15 px, constrained container to 600 px. Still CSS3D. Still shortcut: `radial-gradient` cannot match Three.js photorealistic lighting + shadow + perspective. Closer than iteration 1 but not faithful to source.

3. **Iteration 3 (current — Three.js port):** Loads Three.js 0.182.0 from CDN via importmap. Same library GL uses. Direct port of `generateArchBalloons` math and `BalloonScene` setup. Visual fidelity now matches the source implementation. Verified by capturing both my port and GL's actual `localhost:3000/design` at the same viewport sizes — see `COMPARISON.md`.

## The math (binding for Frappe build)

### Constants

```
11" balloon = 0.458 ft radius = 0.917 ft diameter
Industry standard: 40 balloons per 5 ft of arch
Render cap (arch): 160 balloons (constant in GL's source)
balloonsPerCluster = 4
spiralAngle = PI / 4   (45 degrees, fixed)
offsetFromCenter = balloonRadius * 0.85   (slight compression for density)
```

### `generateArchBalloons(balloonCount, colors, style, archLength)` — direct port

```js
const archWidth  = archLength * 0.5;
const archHeight = archLength * 0.4;
const totalClusters = Math.ceil(balloonCount / balloonsPerCluster);

for (let i = 0; i < balloonCount; i++) {
  const clusterIndex = Math.floor(i / balloonsPerCluster);
  const balloonInCluster = i % balloonsPerCluster;

  const t = totalClusters > 1 ? clusterIndex / (totalClusters - 1) : 0.5;
  const angle = t * Math.PI;     // 0 left foot -> PI right foot

  // Position on the rope curve
  const curveX = Math.cos(angle) * (archWidth / 2);
  const curveY = Math.sin(angle) * archHeight;
  const curveZ = 0;

  // Outward normal at this point
  const normalX = Math.cos(angle);
  const normalY = Math.sin(angle);

  // 45-degree spiral rotation per cluster
  const clusterRotation = clusterIndex * spiralAngle;

  // 4 balloons in quad, 90 degrees apart, plus spiral rotation
  const angleInCluster = (balloonInCluster * Math.PI) / 2 + clusterRotation;

  // Local offset perpendicular to arch tangent
  const offsetRadial = Math.cos(angleInCluster) * offsetFromCenter;
  const offsetZ      = Math.sin(angleInCluster) * offsetFromCenter;

  // Apply radial offset along normal direction
  const offsetX = normalX * offsetRadial;
  const offsetY = normalY * offsetRadial;

  // Plus organic jitter (radius and position)
  // ... (see source for exact jitter values)

  const x = curveX + offsetX * radiusJitter + posJitterX;
  const y = curveY + offsetY * radiusJitter + posJitterY;
  const z = curveZ + offsetZ * radiusJitter + posJitterZ;
}
```

### Color logic by Style

**Swirl** (max 4 colors):

```
colorIndex = balloonInCluster % colors.length
```

Colors cycle within each quad. With 2 colors -> A-B-A-B; with 4 -> A-B-C-D. The 45-degree physical rotation makes this read as a barber-pole twist.

**Layered** (max 8 colors):

```
clustersPerBand = 2
bandIndex = Math.floor(clusterIndex / clustersPerBand)
colorIndex = bandIndex % colors.length
```

ALL balloons in a cluster get the SAME color. 2 quads (8 balloons) per band. Pattern: AA-BB-CC-DD across the arch.

### Three.js scene setup (verbatim from `BalloonScene` + `BalloonInstances`)

| Element | Setup |
|---|---|
| Sphere geometry | `new THREE.SphereGeometry(0.5, 32, 32)` |
| Material | `MeshStandardMaterial({ roughness: 0.6, metalness: 0.0 })` |
| Per-balloon scale | `balloonDiameter * sizeVariation` (sizeVariation 0.95-1.0) |
| Per-balloon rotation | random in (0..0.2, 0..2*PI, 0..0.2) for organic feel |
| Background | `0xE5E4E2` (Platinum Grey, GL's --muted) |
| Fog | linear, color = bg, near = `size * 1.5`, far = `size * 4` |
| Ambient light | `0xFFFFFF` intensity 0.6 |
| Directional light | `0xFFFFFF` intensity 0.8 at position (5, 10, 5), castShadow |
| Ground | plane size `Math.max(size * 3, 20)`, color `0x046307` (emerald), roughness 0.9 |
| Camera | perspective, fov 45, near 0.1, far 1000, position (0, size*0.35, size*0.9), target (0, size*0.2, 0) |
| OrbitControls | minDistance size*0.3, maxDistance size*1.2, polar angle 0.1*PI to 0.55*PI |
| Renderer | antialias true, ACES tone mapping, shadowMap enabled, devicePixelRatio min(window, 2) |

### How to load Three.js in vanilla HTML (Frappe-compatible)

```html
<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.182.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.182.0/examples/jsm/"
  }
}
</script>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
// ...
</script>
```

Pinned to 0.182.0 to match GL's package.json. Frappe portal pages support this — they accept any HTML/JS, including module scripts and CDN imports.

## Real LT 48-color catalog (verbatim from app/design/page.tsx)

| Category | Count | Examples |
|---|---:|---|
| Standard | 17 | White, Black, Red, Raspberry, Fuchsia, Bubble Gum, Orange, Yellow, Forest, Shamrock, Lime, Teal, Turquoise, Caribbean, Navy, Sapphire, Periwinkle |
| Pastels | 12 | Pastel Pink, Spring Lilac, Lavender, Pink, Coral, Coral Blush, Peach, Apricot, Mint Bliss, Sage, Dusty Blue, Fog |
| Neutrals | 9 | Ivory, Grey, Caramel, Buttercup, Mustard, Gold, Vintage Rose, Nude, Wild Berry |
| Chrome | 10 | Chrome Gold, Chrome Silver, Chrome Rose Gold, Chrome Pink, Chrome Red, Chrome Blue, Chrome Violet, Chrome Green, Champagne, Chrome Fuchsia |

Total: 48 named colors. The contest brief mentioned 53 — reconcile with GL before finalizing the DocType seed.

## How the eventual Frappe build uses this

The Design Studio portal page (post-Phase-1, scoped per `.planning/decisions/site-shape.md`) will:

1. **Load Three.js from CDN** in the page template via importmap (Frappe portal pages accept this).
2. **Port the math directly** from this file's `generateArchBalloons` (and analogous functions for column/garland/wall) into `apps/locally_twisted/locally_twisted/www/design-studio.js` (or via `PAGE_JS` attribute).
3. **Use Three.js InstancedMesh** for the balloons (matches GL's source — efficient for 160+ instances).
4. **Source colors from a DocType** — `LT Balloon Color` with fields: name, hex, category. Seed it from this app's `balloonColors`. Lets Jeff edit colors in the desk.
5. **Wire to customer selection** — `frappe.call()` to a whitelisted method that creates a Lead with `design_studio_payload` Custom Field (Long Text JSON).

Same file shape as `/contact` and `/checkout` already shipped, plus an external script tag for Three.js.

**Do not deviate from this math during implementation without first updating this reference AND syncing with the locally-twisted-app source.**

## Caveats

### Three.js bundle size

Three.js 0.182.0 module is ~150 KB minified + ~50 KB for OrbitControls. Loaded from CDN, this is one-time per visitor and cached. For a Design Studio page, this is acceptable — well under the typical image-asset weight on similar pages.

### Color count: 48 vs 53

The `balloonColors` constant has 48 colors. The contest brief mentioned 53. Confirm with GL before finalizing.

### What this prototype does NOT show

The arch shape proves quad-cluster geometry + 45-degree spiral + Swirl/Layered color logic. It does NOT prove:
- Vertical column gravity (column.html will, when ported)
- Garland wave-path with depth layers (garland.html will)
- Honeycomb wall packing (wall.html will)
- AR overlay onto a real-world photo (`BalloonARViewer` component in GL's app)
- Customer photo upload as backdrop (separate UX feature)

Each needs its own port before its respective shape can be safely implemented.

---

*Reference rewritten 2026-04-29 (afternoon, third iteration) by the Opus 4.7 instance who first built a CSS3D shortcut, was corrected by GL ("the rendering of the balloons is bad — there's a 3D modeling I made"), found GL's existing locally-twisted-app code, ported faithfully to Three.js, and verified against ground truth captured from GL's running dev server. The wrong versions are preserved only in git history.*
