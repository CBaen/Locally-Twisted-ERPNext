# Balloon Render Bible Design

Date: 2026-05-01

## Purpose

Locally Twisted needs a premium, consistent first-image system for products. The goal is not generic AI balloon art. The goal is a controlled render system that uses Jeff's actual work as the visual baseline, respects professional balloon construction, and creates product lead images that feel more polished and business-capable than the current mixed source-photo catalog.

GL is the approval proxy for Jeff on this render system.

## Source Of Truth Order

1. Jeff/LT actual photos in `_resources/catalog-source/images/`.
2. Balloon construction and physics rules from professional references.
3. Product catalog metadata in `_resources/catalog-source/catalog.json`.
4. LT brand/style guidance in `_resources/STYLE-GUIDE.md` and `_resources/design-guide/`.
5. Generated image judgement by GL before any broad product rollout.

Do not let image-generation aesthetics override the first two sources.

## Initial Reference Products

Use these products first because they expose the hardest image problems:

| Product | Why it matters |
|---|---|
| `classic-arch` | Largest image set, scale-critical, classic cluster/rainbow/spiral logic, event-entrance and parade-scale variants. |
| `classic-column` | Clear classic column construction: quads around pole/base, spiral logic, topper/base relationship. |
| `classic-organic-balloon-garland` | Organic massing, mixed balloon sizes, controlled color clusters, rigging to a wall/fixture. |
| `birthday-deliveries` | Studio-like product staging with foils, latex base, number balloons, and themed birthday composition. |

## Construction Anchors

Classic arches and columns must render as physically buildable decor. Professional references support these baseline rules:

- Classic swirl/spiral arches use 3- or 4-balloon latex clusters, tightly packed on a line/frame, with a quarter-turn color rotation creating the spiral. Reference: Burton + Burton Balloon Arches, https://www.burtonandburton.com/education/basics/balloon-basics/arches.aspx
- A packed standard arch with 11-inch balloons is roughly 16-20 balloons per meter, while organic/garland arches use mixed balloon sizes and higher density. Reference: PartyCalcs quantity guide, https://partycalcs.uk/reference/balloon-quantities/
- Commercial large cluster arches can be specified by dimensions, e.g. 25 ft wide x 13 ft high, built with 4-balloon clusters of 11-inch latex, with 2-4 colors in spiral or block patterns. Reference: BalloonPlanet cluster arch product, https://www.balloonplanet.com/products/large-cluster-arch-hf/

These are prompt constraints, not customer-facing copy.

## Product-Family Rules

### Classic Arch

Construction:
- Repeating quads or tight cluster rows, not loose random balloons.
- Balloons should be uniform within a classic row/layer unless the product is explicitly organic.
- A spiral design must show a readable phase shift, not random color scatter.
- A layered/rainbow design must keep clean color bands with consistent spacing.

Scale cues:
- Door/single entrance scale.
- Double-door or lobby entrance scale.
- School/gym/corporate entrance scale.
- Parade/truck-clearance scale.

Hard rejects:
- Unsupported floating arch.
- Random balloon sizes in a classic arch.
- Color confetti without pattern.
- No visible support logic for a large outdoor or parade-scale arch.
- Arch opening too narrow for the named size.

### Classic Column

Construction:
- Vertical pole/base structure implied.
- Repeating 4-balloon quads around the pole.
- Spiral pattern rotates consistently by cluster.
- Topper must sit on top of the column, not float independently.

Hard rejects:
- Lumpy organic column when product is classic.
- Spiral direction changing mid-column.
- Topper too large for the base or visually unsupported.

### Organic Garland / Organic Arch

Construction:
- Mixed balloon sizes.
- Controlled cluster massing, not mathematically uniform quads.
- Large balloons form the primary structure; smaller balloons fill gaps and add detail.
- Color is weighted and grouped in masses, not random confetti.
- Rigging must make sense: wall, frame, doorway, pipe, ceiling, or install surface.

Hard rejects:
- Classic quad formula presented as organic.
- Evenly spaced uniform balloons.
- Impossible floating mass without rigging.
- Random all-over color distribution.

### Birthday Deliveries / Bouquets

Construction:
- Foil number balloons and themed foils must look helium-filled or structurally attached.
- Latex base should ground the composition.
- Letter foil text should not be generated unless legible and intentional.
- Designs can be studio-style, but should still look deliverable and not digitally pasted.

Hard rejects:
- Garbled readable text on foils.
- Number balloons with wrong shape or perspective.
- Latex base disconnected from foil structure.

## Backdrop System

Use two controlled lead-image styles:

1. Premium studio catalog for smaller products: bouquets, balloon cups, table decor, grab-and-go pieces.
2. Professional venue mockup for large installs: arches, garlands, columns, drops, easels, storefront/school/corporate/parade scale.

Both styles should use a restrained, consistent LT-compatible background color family. Avoid a mixed lifestyle-photo catalog as the first image. Real photos remain useful in galleries and proof sections.

## Variant And Gallery Model

Products can need more than one image per sellable option. The image model should support:

- A consistent lead image for the template/product family.
- Size-specific images for variants where size changes the construction or customer expectation.
- Multiple images per variant when a size option needs alternate angles, scale proof, or real install examples.
- Real LT photos as gallery/proof images, separate from generated illustrative renders when needed.

For scale-sensitive products, the variant image should usually be tied to the size option, not only the color option. A single-door classic arch, double-door classic arch, and parade/truck-clearance classic arch must not share one generic arch render if the customer would infer the wrong scale.

## Prompt Architecture

Each render prompt should be assembled from these blocks:

1. Product identity: product family, variant/size, intended use.
2. Construction: classic quad, organic mixed-size, bouquet base, drop net, etc.
3. Physical support: frame, pole/base, monofilament/line, wall fixture, stand, net.
4. Color logic: spiral, block, rainbow bands, controlled organic clusters, accent-only.
5. Scale environment: single door, double doors, gym entrance, corporate lobby, parade street.
6. Backdrop: studio catalog or controlled venue mockup.
7. Camera and composition: lead product image, product centered, enough negative space for card crop.
8. Negative prompt: impossible physics, random color scatter, malformed balloons, unsupported arch, garbled text, toy-like plastic, tiny scale.

## Pilot Scope

Do not generate all products first. The pilot is:

1. `classic-arch` small/door-scale render.
2. `classic-arch` parade/truck-clearance render.
3. `classic-column` classic spiral render.
4. `classic-organic-balloon-garland` organic controlled-cluster render.
5. `birthday-deliveries` studio catalog render.

GL approves or rejects these as Jeff's proxy. Only after approval should the system expand to the rest of the catalog.

## Review Rubric

Each generated image must answer yes to all required checks:

- Does it resemble Jeff's actual product family, not a generic balloon decoration?
- Is the construction physically plausible?
- Is the color placement consistent with the product style?
- Is the scale legible for the selected size?
- Does the background feel consistent with the LT lead-image system?
- Would the image mislead a customer into believing it is a real LT install? If yes, label as illustrative or do not use it as proof.

## Implementation Boundary

This spec does not implement image generation, DB attachment, or storefront rendering. It defines the approval system and prompt architecture. Implementation should follow as a separate plan after GL approves this spec.
