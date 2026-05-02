# Design Studio V2 Physics Rules

Last updated: 2026-05-02 by Codex

Scope: construction-rule spec for the future `Plan Custom Decor` / Design Studio renderer. This is background V2 research, not a V1 launch blocker and not implementation code.

## Source Status

Verified from repo sources:

- `research/contest-customizable-event-decor-tool/PRODUCT-DETAILS.md` defines the load-bearing construction rules for classic arches, classic columns, organic garlands, backdrops/walls, drops, bouquet recipes, and the shared named-color catalog.
- `research/contest-customizable-event-decor-tool/FINAL-SURFACE.md` says the contest mockups are useful UX source material but did not solve all construction gaps, especially backdrop sizing inputs and cluster-count math.
- `research/contest-customizable-event-decor-tool/physics-render-reference/PHYSICS-RENDER-NOTES.md` says the binding arch render reference is the Three.js port of GL's existing renderer, not the abstract contest-circle mockups.
- `workstreams/design-studio-v2.md` frames this as `Plan Custom Decor`: larger consultative multi-piece installs, separate from simple `Ready to Order` ecommerce.
- `workstreams/brand-audience-style-reset.md` frames Locally Twisted as the customer-facing brand and emphasizes professional event authority, scale, process, and technically correct balloon structures.

Inferred for renderer spec:

- The renderer should be a planning visualization and construction sanity check, not a final engineering drawing or installation guarantee.
- The renderer should prefer rule-driven, Frappe-native data structures later, but this document does not design the UI or implement code.
- The renderer should show enough structure that Jeff or another professional balloon decorator can reject unbuildable previews before they reach production.

Needs GL/Jeff approval:

- Exact approved color catalog and hex/Pantone mappings. Source files currently conflict between a 53-name contest catalog and a 48-color GL app catalog.
- Final size limits, safety disclaimers, outdoor/indoor constraints, and any customer-facing wording around what is physically possible.
- Whether cluster counts and balloon counts are customer-visible or only stored in the internal sales/production payload.

## Core Renderer Principle

The renderer must start from the build method, not from free drawing.

Classic balloon decor is made from repeated construction units. The renderer should not let a customer paint arbitrary circles if that would imply a build pattern Locally Twisted would not actually construct.

Use these engines conceptually:

| Engine | Pieces | Construction unit |
|---|---|---|
| Structured cluster | Classic arches, classic columns, backdrop/wall | 4-balloon cluster/quad |
| Organic recipe | Organic garlands, organic arches, organic columns | Doublets, mixed sizes, filler balloons, controlled randomness |
| Representational mix | Balloon drops | Proportional random color cloud, not stable spatial pattern |
| SKU recipe | Bouquets and themed items | Stem/super-shape recipe, not free decor physics |

This spec focuses on classic arches, classic columns, backdrop/wall, organic garland, color distribution, scale, and unbuildable-render rules.

## Shared Structured-Cluster Rules

The atomic unit for classic arches, classic columns, and backdrop/wall is a 4-balloon cluster, also called a quad.

Construction:

- One quad is two doublets twisted together at 90 degrees.
- Each quad has four balloon positions around the frame or grid point.
- Adjacent quads interlock by rotation.
- A renderer should store color at the balloon-slot level but expose style/color choices at the piece level.

Basic formulas:

```text
balloons = clusters * 4
clusters = ceil(balloons / 4)
minimum_cluster_repeat = color_count / gcd(color_count, 4)
```

Use `ceil` when converting from physical size to whole clusters. Never render fractional clusters.

Per-foot counts from `PRODUCT-DETAILS.md`:

| Balloon size | Balloons per foot | Clusters per foot |
|---|---:|---:|
| 5 inch | 12-13 | 3 |
| 9 inch | 7-8 | 2 |
| 11 inch | 6-7 | 1.5-1.75 |
| 14-16 inch | 4-5 | 1-1.25 |

For planning math:

```text
estimated_balloons = length_ft * balloons_per_foot
estimated_clusters = ceil(estimated_balloons / 4)
```

Columns may need tighter packing than arches because they are viewed from all sides. Treat column counts as a minimum until Jeff confirms the production factor.

## Classic Arch Rules

Use for classic arch designs, including the classic option inside the merged arch product family. Organic arch should use the organic recipe rules, not these structured-cluster rules.

Inputs:

- Length in feet. Common reference points from source: 20 ft, 25 ft, 30 ft, 35 ft. Customer can request other lengths.
- Balloon size or render preset. Source sizes: 5 inch, 9 inch, 11 inch, 14-16 inch.
- Design: swirl/spiral, layered/chunk, or organic. This section covers swirl and layered only.
- Colors: swirl up to 4 colors; layered up to 8 colors, per source.

Geometry:

- A classic arch is a sequence of quads along an arch frame.
- The visual path is a curve from one foot of the arch to the other.
- The renderer should rotate each quad around the frame path, not place flat circles on the front face only.
- The physics reference arch uses 4 balloons per cluster, a fixed 45-degree spiral rotation per cluster, and a render cap of 160 balloons in GL's existing app reference.

Reference Three.js math from `PHYSICS-RENDER-NOTES.md`:

```text
arch_width = arch_length * 0.5
arch_height = arch_length * 0.4
total_clusters = ceil(balloon_count / 4)
t = cluster_index / (total_clusters - 1)
angle = t * pi
spiral_angle = pi / 4
cluster_rotation = cluster_index * spiral_angle
balloon_angle_in_cluster = balloon_slot * pi / 2 + cluster_rotation
```

Renderer constraints:

- Show the arch as a 3D or 2.5D structure with depth. A flat front-only row is misleading.
- If using the GL physics-reference approach, port the Three.js math faithfully before changing visual assumptions.
- If the renderer caps displayed balloons for performance, store true estimated count separately and label the render as representational internally.
- Do not let customers place random isolated balloons along the arch. Every visible balloon belongs to a quad or organic recipe.

Swirl/spiral color logic:

- Use 1 to 4 colors.
- In each quad, assign slot colors by cycling through the selected colors.
- Rotate each quad one step along the frame so the color reads as a spiral/candy-cane effect.

Simple slot pattern examples:

```text
1 color: A A A A
2 colors: A B A B
3 colors: use the balanced 3-cluster repeat below
4 colors: A B C D
```

For 3 colors, use the balanced repeat from source:

```text
cluster 1: A A B C
cluster 2: A B B C
cluster 3: A B C C
repeat
```

Layered/chunk color logic:

- Use 1 to 8 colors.
- Each cluster or small cluster band should be visually dominant in one color.
- The physics reference uses 2 clusters per band for layered arch rendering:

```text
clusters_per_band = 2
band_index = floor(cluster_index / clusters_per_band)
color = colors[band_index mod color_count]
```

- Do not show layered arch colors as single-balloon confetti unless the style is explicitly organic.

Minimum readability:

- Spiral patterns need enough clusters to show multiple rotations.
- Source notes say spiral arches need at least 3 full cycles to read clearly.
- The renderer should warn internally or switch preview language when a short arch plus many colors creates a weak or unreadable pattern.

## Classic Column Rules

Use for classic columns with stacked clusters around a pole. Organic columns should use organic recipe rules and should not show a classic topper unless the selected style is classic and the topper is in scope.

Inputs:

- Height in feet. Common reference points from source: 5 ft, 6 ft, 7 ft, 8 ft, 9 ft, 10 ft. Customer can request other heights.
- Design: classic structured cluster or organic. This section covers classic.
- Colors for spiral, chunk, stripe, or solid patterns.
- Topper selection is out of scope for the contest/source brief and should not be invented by the renderer.

Geometry:

- A classic column is a vertical stack of quads around a central pole.
- Each quad wraps the pole in four directions.
- Adjacent quads rotate to create spiral, stripe, or banded effects.
- The renderer must show depth/sides, not only a front stripe column.

Count formula:

```text
estimated_balloons = height_ft * balloons_per_foot
estimated_clusters = ceil(estimated_balloons / 4)
```

Column planning caveat:

- Source says columns may pack about 1 cluster/ft tighter than arches and should be treated as minimum counts.
- Renderer should preserve a `count_basis` field such as `minimum_estimate` until Jeff approves exact column production factors.

Classic spiral:

```text
position = (cluster_number * spiral_step) mod 4
```

- `spiral_step = 1`: spiral/swirl, one quarter-turn per cluster.
- `spiral_step = 0`: chunk/banded, no rotation.
- `spiral_step = 2`: vertical stripe effect, alternating sides.

Color rules:

- Solid: all slots in all clusters use one color.
- Spiral: slot colors follow the structured-cluster repeat, and cluster rotation creates the spiral.
- Chunk/band: all balloons in a cluster or band share one color for a stacked block.
- Vertical stripe: colors must map to stable sides around the pole. Do not render a stripe that jumps sides between clusters.

Minimum readability:

- A 5 ft column with a 4-color spiral may show only 1-2 cycles and read weakly.
- The renderer should detect weak spiral readability when height or cluster count is too low for the selected color count.
- Tall columns are better candidates for multi-color spiral; short columns are better as solid, two-color spiral, or chunk/band.

## Backdrop / Wall Rules

Use for balloon walls, photo-op walls, and organic display wall planning when the construction method is a structured 4-balloon cluster grid. If a future product is truly organic/mixed-size, it should use a separate organic wall recipe.

Inputs:

- Width in feet.
- Height in feet.
- Design: solid, vertical stripes, horizontal stripes, color blocks, diagonal stripes, or lattice/criss-cross.
- Colors by design: solid 1; stripes 2 or more; color blocks 2-3; diagonal 2; lattice 2-3.

Source formula:

```text
clusters = width_ft * height_ft
balloons = clusters * 4
production_balloons = balloons * 1.10 to 1.15
```

Examples from source:

```text
8 ft x 8 ft = 64 clusters = 256 balloons, about 285-300 with overage
10 ft x 10 ft = 100 clusters = 400 balloons, about 440-460 with overage
```

Renderer grid:

- Treat one cluster as one visual pixel/cell.
- Use whole-number cluster dimensions.
- If the customer enters fractional dimensions, the renderer must round or normalize to whole cluster cells and store the original requested dimensions separately.
- The preview should not imply sub-cluster detail unless the renderer explicitly supports mixed-color clusters at a cell.

Pattern rules:

- Solid: every cell uses the same color.
- Vertical stripes: assign whole grid columns to stripe colors.
- Horizontal stripes: assign whole grid rows to stripe colors.
- Color blocks: assign large rectangular areas, such as top/middle/bottom thirds or left/center/right blocks.
- Diagonal stripes: assign cells along diagonal bands. Use a repeatable band-width rule; do not draw impossible thin vector lines over the balloon grid.
- Lattice/criss-cross: background fill plus diagonal cell bands in one or two accent colors.

Lattice ratio from source:

```text
background = 60% to 75%
accent_total = 25% to 40%
```

For three-color lattice:

- Color A is background.
- Color B is diagonal direction 1.
- Color C is diagonal direction 2.
- At intersections, choose one accent color by deterministic dominance or render a mixed 2+2 cluster only if Jeff approves that mixed-cluster detail.

Stripe and block constraints:

- Every stripe must be at least 1 cluster wide.
- A design with more stripes than grid columns or rows is invalid.
- Very thin diagonal or lattice lines may disappear at small sizes; renderer should keep minimum band width at 1 full cluster and warn internally when the result is visually weak.

## Organic Garland Rules

Organic garland is not classic 4-cluster math. Do not render it as a fixed row of quads.

Construction from source:

- Built from doublets on a decorating strip or fishing-line backbone.
- 5 inch balloons are added as filler last.
- Uses mixed balloon sizes and artist-led placement.
- The renderer should use controlled randomness, not uniform random and not a rigid grid.

Inputs:

- Length in feet. Common reference points from source: 6 ft, 9 ft, 12 ft; customer can request other lengths.
- Density tier.
- Size mix.
- Color style: solid, tonal/monochromatic, two-tone alternation, multi-color organic blend, ombre/gradient, color-blocked, accent-cluster, tapered/asymmetric.

Density from source:

| Density | Balloons per foot |
|---|---:|
| Light | 4-6 |
| Standard | 7-9 |
| Lush | 10-12 |
| Mixed-size premium | 12-14 |

Default size mix from source:

```text
50% mid-size balloons, usually 9 inch or 11 inch
30% small balloons, usually 5 inch
20% large balloons, usually 16 inch or larger
```

Count formula:

```text
estimated_balloons = length_ft * density_per_ft
small_count = estimated_balloons * 0.30
mid_count = estimated_balloons * 0.50
large_count = estimated_balloons * 0.20
```

Controlled randomness:

- Use weighted random placement based on customer color ratios.
- Enforce a no-touching-twins rule: no adjacent balloons with the same color and same size.
- Cluster accents intentionally when the selected style calls for accent clusters.
- Use a stable seed so the same saved design re-renders the same way.

Ombre/gradient:

- Use zones with feathered overlap.
- Example for A to B to C:

```text
zone A dominant
zone A+B feather
zone B dominant
zone B+C feather
zone C dominant
```

- Do not hard-split ombre into clean classic bands unless customer selected color-blocked.

Tapered/asymmetric:

- Vary density and balloon sizes along the path.
- One end may be larger/denser and the other smaller/lighter.
- Renderer must still preserve buildable attachment points and should not show unsupported floating masses.

## Color Distribution Rules

Color names are the load-bearing identifier. Hex values are only approximate visual aids until GL/Jeff approves the actual mappings.

Shared rules:

- Store selected colors by catalog name.
- Store color ratios or pattern style separately.
- Do not certify brand/Pantone matching from the renderer.
- The renderer should prevent impossible color counts for a selected construction style.

Structured-cluster balanced repeat:

```text
minimum_cluster_repeat = color_count / gcd(color_count, 4)
```

Examples from source:

| Colors | Minimum repeat | Valid balanced pattern |
|---:|---:|---|
| 1 | 1 | A A A A |
| 2 | 1 | A B A B |
| 3 | 3 | (A A B C), (A B B C), (A B C C) |
| 4 | 1 | A B C D |
| 5 | 5 | 5-cluster cycle |
| 6 | 3 | 3-cluster cycle with each color twice |
| 8 | 2 | 2-cluster cycle, all 8 colors |

Spiral:

- Color is assigned within quad slots and made visible by physical rotation between clusters.
- Works best with 2-4 colors.
- Needs enough length/height to show repeated cycles.

Layered/chunk:

- Color appears in contiguous cluster bands or zones.
- Works for larger color sets because each color gets visual mass.
- Band size must be whole clusters.

Stripe:

- Stripe colors map to stable sides for columns or grid rows/columns for walls.
- Do not simulate stripes by randomly alternating single balloons.

Balanced repeat constraints:

- Avoid long accidental runs of the same color unless the selected style is chunk, block, accent-cluster, or organic.
- Avoid tiny one-cluster accents in large installations unless the design calls for a stripe/lattice/accent.
- For customer-chosen ratios, convert ratios to whole clusters or whole balloons depending on engine, then adjust the final distribution to match the nearest buildable count.

## Scale References And Sizing Constraints

The renderer should keep scale honest enough for planning.

Known common sizes from source:

| Piece | Common reference sizes |
|---|---|
| Arch | 20 ft, 25 ft, 30 ft, 35 ft; any length request |
| Column | 5 ft, 6 ft, 7 ft, 8 ft, 9 ft, 10 ft; any height request |
| Garland | 6 ft, 9 ft, 12 ft; any length request |
| Backdrop/wall | 8x8 ft, 10x10 ft, 10x30 ft; any width x height request |

Scale rules:

- Always store actual requested size.
- Always derive cluster/balloon counts from actual size.
- Use common sizes as presets or reference points only; do not make them the only allowed sizes unless GL changes the product rule.
- Render people, doors, tables, or stage references only if their dimensions are known or clearly generic.
- Do not crop the preview so tightly that arch height, column height, or wall footprint becomes misleading.

Common approximation constraints needing approval:

- Whether 1 backdrop cluster should always equal 1 sq ft in production planning or only in early estimate math.
- Whether arch width/height ratios from the GL renderer should be exposed as production assumptions or kept as visualization geometry.
- Whether customer-facing previews should show exact counts, approximate counts, or no counts.

## What The Renderer Must Not Show

The renderer must not create visuals that imply impossible, unsafe, or misleading builds.

Do not show:

- Free-floating balloon pieces with no frame, pole, strip, wall grid, ceiling net, or other attachment logic.
- Classic arches, columns, or walls made from random loose circles instead of quads.
- Organic garlands rendered as fixed 4-balloon cluster math.
- Balloon drops with a stable logo, stripe, spiral, or spatial pattern after release. Drop colors become random under gravity.
- Backdrop stripes thinner than one cluster cell.
- Wall detail smaller than the grid can build.
- Fractional clusters.
- A column spiral that changes direction or side mapping unexpectedly.
- A classic arch with customer-painted local regions that the cluster math cannot reproduce.
- A wall or arch that certifies exact real-world fit without venue measurements.
- Outdoor/ceiling/sprinkler/installation safety promises unless GL/Jeff has approved the wording and constraints.
- Exact price, legal claims, or guaranteed install feasibility from this renderer.

The renderer should also avoid customer-facing visuals that make Locally Twisted look like a party-store toy. The balloon work can be colorful; the planning surface should stay professional, scale-aware, and construction-literate.

## Internal Payload Fields To Preserve

This is not implementation, but these data points should survive into any future Frappe design/session payload because they affect build accuracy:

- Piece type: arch, column, backdrop/wall, garland, drop, bouquet.
- Construction engine: structured cluster, organic recipe, representational mix, SKU recipe.
- Requested dimensions: length, width, height as relevant.
- Render dimensions if different from requested dimensions.
- Balloon size preset.
- Density tier for organic garland.
- Size mix for organic pieces.
- Selected color names.
- Approximate hex values only as display aids.
- Color ratios.
- Pattern style: spiral, layered/chunk, stripe, balanced repeat, ombre, organic blend, accent cluster.
- Cluster count.
- Balloon count.
- Overage assumption if shown internally.
- Random seed for organic placement.
- Warnings generated by the renderer.
- Pieces considered but not selected, if the UX uses that sales-context mechanic.

## Open Questions For GL/Jeff

1. Which catalog is canonical for Plan Custom Decor colors: the 53 names in `PRODUCT-DETAILS.md`, the 48-color GL app catalog in `PHYSICS-RENDER-NOTES.md`, or a revised list?
2. Should the first prototype port only GL's arch renderer, or should column, garland, and wall receive their own physics-reference ports before any customer-facing prototype?
3. Should customers see cluster and balloon counts, or should counts remain in the internal Locally Twisted summary?
4. What are the approved min/max sizes for arches, columns, walls, and garlands before the tool should say "talk with us" instead of rendering freely?
5. How should the renderer handle outdoor, ceiling, sprinkler, wind, doorway, and venue-clearance constraints?
6. Are mixed-color wall intersection clusters approved for lattice, or should intersections resolve to one dominant accent color?
7. What exact column packing factor should be used for production estimates?
8. Which scale references are acceptable for corporate, school, civic, venue, parade, and private event contexts?

## Bottom Line Constraints

The renderer is useful only if it protects the build method.

- Classic arch equals quads along a frame.
- Classic column equals quads stacked around a pole.
- Backdrop/wall equals a quad grid.
- Organic garland equals mixed-size doublets and filler with controlled randomness.
- Color names are production identifiers.
- Counts must be whole build units.
- The preview must remain a planning visualization, not a guaranteed engineering drawing.
