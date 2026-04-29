# Render Comparison — My Three.js Port vs GL's Actual App

After GL named "the rendering of the balloons is bad. There's a 3D modeling I made," I:

1. Found GL's existing implementation: `C:\Users\baenb\projects\locally-twisted-app\src\components\balloon-preview-3d.tsx` (Three.js + React Three Fiber).
2. Started GL's Next.js dev server (`npm run dev` in that project).
3. Captured ground-truth screenshots of `http://localhost:3000/design` at mobile (375 px) and desktop (1280 px) viewports.
4. Rewrote my prototype using Three.js directly (CDN-loaded via importmap), porting `generateArchBalloons` + the Three.js scene setup verbatim.
5. Re-rendered and captured my port at the same viewport sizes.

## Side by side

### Desktop

| GL's actual app (ground truth) | My Three.js port |
|---|---|
| `_render/physics-reference/GL-actual-desktop.png` | `_render/physics-reference/swirl-arch-desktop.png` |

### Mobile

| GL's actual app (ground truth) | My Three.js port |
|---|---|
| `_render/physics-reference/GL-actual-mobile.png` | `_render/physics-reference/swirl-arch-mobile.png` |

## What matches

- Quad-cluster arch geometry — 4 balloons per cluster radiating outward from rope
- 45-degree spiral rotation per cluster
- Same color palette default (Pastel Pink, Chrome Gold, White, Nude — the "Blush & Gold" preset)
- Same color logic per Style (Swirl: cycle within quad; Layered: bands of 2 quads)
- Same Three.js library version (0.182.0), same scene setup (lights, materials, fog, camera)
- Same `generateArchBalloons()` math, same constants, same render cap (160 for arch)

## What still differs

- **Page chrome**: GL's screenshot shows the full design page (header, controls panel, AR button, fan-favorite palettes). My screenshot shows only the prototype's reference page (header, controls, math notes). Different surrounding UI; same canvas.
- **Ground plane visibility**: GL's render shows mostly platinum-grey background; mine shows the emerald green ground plane more prominently in the lower half. Cause: my render area ends slightly below the arch base, exposing the ground; GL's Card-clipped canvas crops higher. Same scene, different framing.
- **Visual fidelity at small sizes**: GL's actual canvas is ~500×375 px in their layout; mine is up to 600×450 px. At higher resolution, individual balloons read more distinctly; at lower resolution they blur into a denser cluster. Same balloon geometry, different rendered pixel density.

## What was wrong before this iteration

The first version of `swirl-arch.html` (CSS3D-based, written earlier this session) used `radial-gradient` backgrounds on HTML divs to fake 3D balloons. That approach can never match Three.js — it loses real lighting, shadow, occlusion, and perspective foreshortening. GL caught it: *"This isn't even close."*

The second version (this one) loads Three.js from CDN and uses the exact same scene setup as GL's React Three Fiber code. Visual fidelity now matches the source.

## Verifying

To regenerate both renders:

```
# 1. Start GL's app (if not running)
cd C:/Users/baenb/projects/locally-twisted-app
npm run dev

# 2. In a separate shell, capture both ground truth + my port
cd C:/Users/baenb/projects/Built_by_Cameron/_CLIENTS/locally-twisted/research/contest-customizable-event-decor-tool/physics-render-reference
python capture_ground_truth.py    # captures GL-actual-{mobile,desktop}.png
python render.py                  # captures swirl-arch-{mobile,desktop}.png
```

Both scripts save to `_render/physics-reference/`.

---

*Comparison built 2026-04-29 after GL's correction. The Three.js port is the binding render reference; the prior CSS3D version is preserved only in git history.*
