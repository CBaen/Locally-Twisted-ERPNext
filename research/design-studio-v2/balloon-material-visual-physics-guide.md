# Balloon Material And Visual Physics Guide

Last updated: 2026-05-06 by Codex.

Scope: visual and physical modeling rules for the Locally Twisted event-builder game. This guide defines what a balloon must be in the game before the renderer can be trusted. It focuses on standard 11 inch latex balloons first, while leaving clean extension points for other round sizes, twisting balloons, organic work, and drops.

## Why This Exists

The event builder is a real balloon event design game. The renderer cannot treat balloons as generic balls.

Real latex balloons have:

- size standards;
- inflation shape;
- necks and knots;
- finish and color differences;
- internal pressure;
- latex tension;
- contact compression against other balloons;
- twist/lock deformation at construction points;
- oxidation, shine, and environmental behavior.

If the game cannot approximate what a real installation will look like, the rest of the tool does not matter. The preview can be representational, but it cannot be physically naive.

## Sources Checked

Professional/manufacturer references:

- Qualatex 11 inch product page: <https://us.qualatex.com/en-us/products/43756/?product_type=Qualatex+Latex+Balloons>
- Qualatex Balloon Basics: <https://us.qualatex.com/en-us/education/balloon-basics/>
- Qualatex Helium Chart PDF mirror: <https://www.balloons.com/docs/Qualatex-Helium-Chart.pdf>
- Balloons Everywhere Latex Balloon Hints and Techniques: <https://www.balloons.com/docs/2013-BE-LatexHintsTechniques.pdf>

Physics references:

- Mangan and Destrade, Gent models for the inflation of spherical balloons: <https://arxiv.org/abs/2009.08752>
- Modelling the Inflation and Elastic Instabilities of Rubber-Like Spherical and Cylindrical Shells: <https://link.springer.com/article/10.1007/s10659-021-09823-x>

Professional technique reference:

- Balloon HQ Twisting Balloons 102: <https://balloonhq.com/faq/twists_102/>

Local LT references:

- `research/design-studio-v2/design-studio-physics-rules.md`
- `research/contest-customizable-event-decor-tool/PRODUCT-DETAILS.md`
- `research/contest-customizable-event-decor-tool/physics-render-reference/PHYSICS-RENDER-NOTES.md`
- `research/design-studio-v2/playcanvas-crown-jewel-research.md`
- `research/design-studio-v2/playcanvas-event-builder-physics-guide.md`

## Start With 11 Inch Standard Latex

The first visual model should be 11 inch standard round latex.

Known manufacturer facts:

- Qualatex lists the 11 inch round inflated diameter as 11 inches / 28 cm.
- Qualatex lists 0.5 cubic feet / 0.015 cubic meters gas capacity for the 11 inch round.
- Professional sizing guidance uses templates, not guesswork.
- Properly inflated latex generally reads as round/teardrop, not light-bulb shaped.
- Overinflation increases popping risk and can push inflation into the neck.
- Underinflation changes appearance, float behavior, and shine.
- Pearl and metallic 9, 11, and 16 inch balloons may look different uninflated but are designed to inflate to the same listed size as standard colors.

Important modeling implication:

An 11 inch balloon is not always rendered as an 11 inch perfect sphere. The renderer needs both a `nominal_size_in` and a `sized_diameter_in`.

For example:

```json
{
  "nominal_size_in": 11,
  "sized_diameter_in": 10,
  "inflation_profile": "properly_sized_cluster",
  "shape_profile": "latex_teardrop_round",
  "finish": "standard"
}
```

Qualatex's basic garland instructions specifically size 11 inch balloons to 10 inches for a classic air-filled cluster garland. Jeff should confirm whether LT's classic arch and column default should render 11 inch balloons at 10 inches, 10.5 inches, or 11 inches. Until that is confirmed, store this as a sizing parameter instead of hardcoding one value.

## Balloon Primitive, Not Sphere Primitive

The game needs a reusable balloon primitive with these visible parts:

- body;
- neck;
- knot;
- nozzle direction;
- highlight area;
- contact deformation areas;
- optional seam/tension direction;
- color/finish material.

Minimum render fields:

```json
{
  "balloon_id": "arch_1_c12_b2",
  "type": "round_latex",
  "nominal_size_in": 11,
  "sized_diameter_in": 10,
  "color_name": "Red",
  "finish": "standard",
  "inflation": {
    "ratio": 0.91,
    "profile": "proper_teardrop",
    "neck_inflation": "minimal"
  },
  "tension": {
    "base_pressure": 0.55,
    "twist_pressure": 0.25,
    "contact_pressure": 0.2
  },
  "shape": {
    "body_scale": [1.0, 1.06, 0.96],
    "neck_scale": [0.26, 0.42, 0.26],
    "knot_scale": [0.18, 0.16, 0.18]
  },
  "contacts": []
}
```

The numbers above are not measured production constants. They are the shape of the data contract the renderer needs. Jeff/GL review and visual calibration should tune them.

## Inflation Shape Rules

Use visible inflation states:

| State | Visual | Meaning |
|---|---|---|
| `underinflated` | rounder, softer, less shiny | not ideal for standard decor unless intentionally used |
| `proper_teardrop` | round body with slight neck-side taper | normal professional sizing |
| `cluster_sized` | slightly smaller, firm, consistent | sized for quad cluster construction |
| `overinflated` | light-bulb/pear profile, neck bulge | warning state, higher pop risk |

Do not make all balloons perfect spheres. Even a round balloon should have an orientation: body toward viewer/light, neck/knot toward construction lock or tie point.

## Tension And Contact

The look of a balloon installation comes from contact.

In a classic quad:

- two duplets twist together;
- four balloons press into a shared center;
- adjacent clusters are rotated and nested;
- centers are pushed firmly against each other;
- balloons should compress, not intersect like ghost geometry;
- contact pressure should slightly flatten or dimple the visible contact side.

A practical render model does not need a full soft-body solver at first. It needs a deterministic deformation layer:

```text
base balloon mesh
  + inflation shape
  + knot/nozzle orientation
  + contact deformations
  + twist-center deformation
  + material finish
```

Contact deformation can be approximated by:

- non-uniform scale;
- local normal displacement around contact points;
- small flattened patches toward cluster center;
- slight elongation away from compression;
- color/roughness variation around stretched areas.

The renderer should be able to answer:

- Which balloons touch this balloon?
- Where is the cluster center?
- Which direction is the tie/twist force?
- Is this balloon on the outside face, inside face, top, or side?
- Is this cluster packed tightly or loosely?

## Twist And Lock Effects

Twisted balloons and twisted construction points are not just rotations.

A twist creates:

- local narrowing at the twist;
- increased local pressure near the twist;
- visible pinching;
- a lock against adjacent balloon segments;
- directional memory in the latex.

For classic round-balloon quads, the twist is mostly at the tied/twisted necks and the cluster center. For future twisting balloons, the whole asset family changes: 160, 260, 350, and 660 balloons are elongated latex tubes with bubble segments, pinch twists, lock twists, pressure shaping, and tail management.

Do not model twisting balloons using the round-balloon primitive.

## Color And Finish

Color is not only hex.

The renderer should represent:

- standard opaque latex;
- pearl;
- metallic/chrome/reflex;
- jewel/translucent;
- pastel/matte-leaning;
- oxidized outdoor state if ever previewed.

Material fields:

```json
{
  "color_name": "Reflex Gold",
  "display_hex": "#c59a2f",
  "finish": "reflex",
  "base_color": [0.77, 0.6, 0.18],
  "roughness": 0.32,
  "metalness": 0.0,
  "clearcoat": 0.35,
  "transmission": 0.0,
  "opacity": 1.0
}
```

Chrome/reflex balloons are not metal. They are latex with a stronger reflective finish. Do not set them to true metal. Use material tuning, environment reflections, and clearcoat-like highlights.

The game must preserve the production color name even if the visual approximation is imperfect.

## Size Families

Do not scale one sphere and call it done.

Round latex families need different visual profiles:

| Nominal size | Likely use | Render implication |
|---:|---|---|
| 5 in | filler/detail | small, often packed in crevices, high contact count |
| 9 in | tighter classic work, drops | smaller cluster rhythm, denser arch/column |
| 11 in | standard classic baseline | first serious model |
| 16 in | large accent / organic | stronger visibility, more deformation under support |
| 18+ in | focal/organic anchors | needs weight/scale cues |
| 24+ in | oversized anchors | should not behave like a normal cluster balloon |
| 260/160/350/660 | twisting balloons | separate tube/bubble physics engine |

For the first classic stage game, the `round_latex_11_standard` primitive is the baseline. Other sizes should derive from family-specific profiles, not blind uniform scaling.

## Construction Unit Rendering

Classic arch/column/wall rendering should create construction units first, then balloon primitives.

Correct hierarchy:

```text
pieceRoot
  clusterRoot
    balloonSlot0
    balloonSlot1
    balloonSlot2
    balloonSlot3
```

Cluster fields:

```json
{
  "cluster_id": "arch_1_c12",
  "construction_unit": "quad",
  "cluster_rotation_deg": 540,
  "center_pressure": 0.8,
  "packing": "nested_45_deg",
  "balloons": []
}
```

The cluster root owns:

- path placement;
- phase rotation;
- center compression;
- neighboring-cluster contact hints.

The balloon slot owns:

- color;
- knot direction;
- local offset;
- body deformation;
- contact list.

## Visual Truth Ladder

Use this ladder for prototype maturity:

| Level | Name | What it proves | Acceptable for |
|---:|---|---|---|
| 0 | Ball placeholders | count, placement, payload | early tests only |
| 1 | Sized latex primitive | 11 inch scale, neck/knot, proper inflation shape | classic refactor prototype |
| 2 | Quad contact model | 4-balloon cluster pressure, nested 45-degree rhythm | serious classic prototype |
| 3 | Piece-level compression | arch/column reads as built from tensioned units | hidden website route |
| 4 | Material/finish calibration | standard/pearl/reflex/color differences read correctly | public route candidate |
| 5 | Organic/twist engines | mixed sizes, filler, tube twists, controlled randomness | later product families |

Current prototype is Level 0 with some scale facts. It must reach Level 2 before the classic game can be trusted as a balloon design surface. It should reach Level 3 or 4 before public launch.

## Implementation Direction In PlayCanvas

Recommended technical path:

1. Build a `balloon-visual-model.js` pure module.
   - Converts product facts into balloon primitive facts.
   - Has no PlayCanvas imports.

2. Build a `classic-cluster-geometry.js` pure module.
   - Converts quad clusters into local balloon slots.
   - Adds contact/tension hints.

3. Update `classic-scene-graph.js`.
   - Emits `stageRoot`, `pieceRoot`, `clusterRoot`, and `balloon` nodes.

4. Update `render-classic-playcanvas.js`.
   - Creates reusable balloon mesh/materials.
   - Applies deformation fields.
   - Avoids destroy/recreate for every update.

5. Add a material/physics lab page.
   - Compare underinflated, proper, overinflated, standard, pearl, reflex.
   - Show one isolated balloon, one duplet, one quad, and one nested cluster pair.
   - This should be reviewed visually before broad game polish.

6. Add visual regression screenshots.
   - Desktop and mobile.
   - Color/finish rows.
   - Quad contact view.
   - Arch segment close-up.

## What Not To Do

- Do not render balloons as generic perfect spheres in the serious prototype.
- Do not hide intersections with camera angle.
- Do not make reflex/chrome balloons true metal.
- Do not make all colors share the same material roughness.
- Do not put deformation math directly in PlayCanvas entity code.
- Do not treat organic work as "random smaller spheres."
- Do not treat twisting balloons as scaled round balloons.
- Do not claim visual fidelity without screenshot review.

## Open Calibration Questions

These need GL/Jeff or visual-reference approval:

1. For LT classic arches and columns, should 11 inch rounds render at 10 inches, 10.5 inches, or 11 inches in packed clusters?
2. Which current color catalog is canonical for the game: 48-color GL app, 53-color contest catalog, or a revised ERPNext seed?
3. What finish categories should ship first: standard only, or standard plus reflex/metallic/pearl?
4. How much contact flattening looks right for a dense quad cluster?
5. Should the first public game show close-up balloon detail, or only enough fidelity at stage scale?
6. What real reference photos should become calibration targets for classic arch and column visuals?

## Bottom Line

The first serious PlayCanvas build should not chase more products first. It should prove that one 11 inch standard latex balloon, one duplet, one quad, and one nested cluster segment look believable.

Once that primitive is right, arches, columns, walls, organic pieces, and drops have a foundation. Without it, every larger feature inherits the wrong visual physics.
