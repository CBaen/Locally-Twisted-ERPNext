# Balloon Render Pilot Show Pack

Date: 2026-05-01

## Purpose

This is the first showable package for the Locally Twisted render system. It turns the Balloon Render Bible into five pilot prompts that can be reviewed before any generated images are attached to ERPNext products.

The goal is not to make random pretty balloon pictures. The goal is to make images that respect Jeff's real work, professional balloon construction, size logic, and customer expectations.

## Research Base

Local LT references:

- `_resources/catalog-source/images/classic-arch.png` and 22 extra classic-arch images.
- `_resources/catalog-source/images/classic-column.png` and 5 extra classic-column images.
- `_resources/catalog-source/images/classic-organic-balloon-garland.png`.
- `_resources/catalog-source/images/birthday-deliveries.png` and 14 extra birthday-delivery images.

Catalog facts from `_resources/catalog-source/catalog.json`:

| Product | Relevant options | Source images |
|---|---|---:|
| `classic-arch` | Arch Size: 20ft, 25ft, 30ft, 35ft; Design: Swirl or Layered; LED option | 23 |
| `classic-column` | Column Height: 5ft-10ft; topper choices | 6 |
| `classic-organic-balloon-garland` | Garland Length: 6ft, 9ft, 12ft | 1 |
| `birthday-deliveries` | Delivery Size; theme; foil number; bouquet add-on | 15 |

Construction references:

- Burton + Burton states swirl arches use three- or four-balloon latex clusters attached to monofilament, with the swirl created by moving the contrast color one quarter turn as clusters are packed on the line: https://www.burtonandburton.com/education/PDF/Howto_Ball_Arch.pdf
- Burton + Burton's arch guide gives a useful 11-inch spiral-arch estimate of 6 balloons per foot and emphasizes uniform sizing, tight cluster packing, and anchored ends: https://www.burtonandburton.com/education/PDF/Howto_Ball_Arch.pdf
- HICO's garland guide frames organic garlands by density, size mix, and mounting method; mixed-size garlands commonly use 5-inch, 11-inch, and 16-inch balloons with filler balloons closing gaps: https://hicomemphis.com/academy/balloon-garland-balloons-per-foot/
- Burton + Burton's organic garland guide shows varied-size inflation, duplets/quads, monofilament wrapping, and pole/base attachment as buildable structure: https://www.burtonandburton.com/blog/organic-balloon-garland.aspx
- Amazing Balloon Decorations describes organic choices as size, up to four colors, and pattern type such as color-blocked or confetti: https://www.amazingballoonsmn.com/organics

## Shared Visual Direction

Use a consistent, premium LT-compatible background system:

- Smaller/studio products: bright studio catalog setup, warm white or very pale blush wall, subtle molding or clean sweep, no clutter.
- Large installs: professional venue mockup with controlled color family, clean floor, believable scale cue, and no busy lifestyle-photo clutter.

All generated images should be treated as illustrative unless they are explicitly real LT installs. Do not use generated images as proof images.

## GL Feedback Incorporated: Classic Arch Density

Classic arch scale changes the span and opening, not the default construction density. A parade-clearance classic arch should usually be the same classic quad/spiral build logic as a doorway classic arch, only larger and properly anchored.

Dense layered rainbow arches are a separate custom/high-density direction unless the customer explicitly orders that density. Do not use the dense rainbow wall look as the default `classic-arch` render for large sizes.

## Prompt 1: Classic Arch, Single-Door Scale

Product target:

- `classic-arch`
- Size interpretation: entry/single-door scale, mapped to the lower-size arch option.
- Design: Swirl, up to 4 colors.
- Use: first-image candidate for smaller arch option.

Prompt:

```text
Create a realistic premium product render of a classic balloon arch for Locally Twisted, built for a single standard doorway or narrow event entrance. The arch is a traditional classic spiral construction made from repeated 4-balloon latex clusters on a concealed monofilament/frame line. Use uniform 11-inch round balloons. The arch should read as one standard classic arch row, not a thick wall of balloons. The spiral pattern must be readable: each cluster advances the contrast color by one quarter turn, creating a clean diagonal candy-stripe effect across the arch, not random color scatter.

Use 3 or 4 coordinated colors from a polished event palette: teal, soft cream, blush pink, and reflex gold. Keep balloon size uniform because this is classic, not organic. Show subtle but believable support logic at the two bases: small low-profile weighted bases or plates, partially hidden by balloon clusters. The arch opening should clearly fit one standard doorway with comfortable head clearance.

Set the arch in a clean professional venue mockup with a warm white wall, simple doorway outline, pale neutral floor, and soft commercial catalog lighting. Product centered, straight-on three-quarter camera, enough negative space around the arch for ecommerce cropping. The image should feel more polished and business-capable than a casual party photo while still looking physically buildable by a professional balloon decorator.

Negative constraints: no floating unsupported arch, no organic mixed-size balloons, no thick multi-row balloon wall, no random confetti color placement, no impossible twisting, no toy plastic shine, no tiny doorway opening, no messy background, no fake brand text, no people.
```

Hard review checks:

- The arch must read as classic quad/spiral work, not organic garland.
- It must not be thicker than the default classic product.
- Door scale must be obvious without feeling miniature.
- Bases/support must be believable but not visually dominant.

## Prompt 2: Classic Arch, Parade / Truck-Clearance Scale

Product target:

- `classic-arch`
- Size interpretation: the highest-scale option, visually equivalent to parade/truck-clearance usage.
- Design: Swirl, up to 4 colors. Layered/rainbow density belongs to custom/high-density work, not the default classic-arch size render.
- Use: size-specific variant image, not generic template lead.

Prompt:

```text
Create a realistic premium product render of a very large classic balloon arch for Locally Twisted, scaled for a parade route or vehicle-clearance entrance where two trucks could pass under it. The arch is a professional air-filled classic balloon structure, not helium floating. It uses the same default classic quad/spiral build logic as a doorway classic arch, scaled wider and taller on a strong hidden frame, with clearly anchored feet on both sides. It should not become a dense multi-row rainbow wall unless ordered as custom high-density decor.

Use a clean classic spiral pattern with 3 or 4 coordinated colors such as teal, soft cream, blush pink, and reflex gold. Each cluster should look like a uniform 4-balloon quad and rotate one quarter turn per cluster. The opening must be very wide and tall, with a subtle scale cue such as a marked parade street, distant curb, or small neutral traffic cones near the base. Do not include readable event signage or brand text.

Set the scene in a controlled professional outdoor venue mockup: clean parade street or school/city event approach, bright but soft daylight, pale neutral sky, minimal background distraction. The arch should dominate the frame, centered and symmetrical, with enough margin for ecommerce crop. Support plates, sandbagged bases, or low frame anchors should be visible enough to make the structure believable.

Negative constraints: no unsupported floating arch, no narrow doorway scale, no dense rainbow wall unless custom, no random balloon sizes, no chaotic confetti colors, no ambiguous arch opening, no crowd, no vehicles blocking the product, no generated text, no impossible wind-blown structure.
```

Hard review checks:

- The scale must not be confused with a doorway arch.
- The large arch must keep default classic-arch build density unless explicitly custom.
- Anchoring must be visible enough that Jeff would not reject the physics.

## Prompt 3: Classic Column, Spiral With Topper

Product target:

- `classic-column`
- Size interpretation: 8ft classic column.
- Topper: large round latex topper.
- Use: template lead or height-specific variant image.

Prompt:

```text
Create a realistic premium product render of a classic 8-foot balloon column for Locally Twisted. The column is built on a vertical pole and weighted base, using stacked 4-balloon latex quads wrapped tightly around the pole. The spiral pattern must rotate consistently by one balloon position per cluster from bottom to top. Use uniform 11-inch balloons in royal blue, deep navy, white, and warm gold, matching the disciplined gym/corporate style of the source photos.

Place a large round white latex topper securely on the pole at the top of the column. The topper must sit on the structure, not float. The bottom should imply a stable base, mostly hidden by the first balloon clusters. Keep the column straight, vertical, and clean, with no lumpy organic massing.

Set the column in a professional venue mockup with a clean gym, school lobby, or corporate entrance feel: pale neutral wall, polished floor, soft overhead lighting, minimal background. Product centered, full column visible, enough blank space around it for an ecommerce product card.

Negative constraints: no organic balloon column, no changing spiral direction, no disconnected topper, no huge unsupported top balloon, no random color scatter, no tilted pole, no unreadable logo, no people.
```

Hard review checks:

- The 4-balloon quad stack must be readable.
- Spiral direction must be consistent from base to topper.
- Topper must look structurally attached.

## Prompt 4: Classic Organic Balloon Garland

Product target:

- `classic-organic-balloon-garland`
- Size interpretation: 9ft wall-mounted garland.
- Use: lead image for organic garland family.

Prompt:

```text
Create a realistic premium product render of a 9-foot organic balloon garland for Locally Twisted, mounted above and around a clean focal wall or media-console backdrop. This is organic balloon decor, not a classic arch. Use mixed balloon sizes with a believable structure: larger 11-inch and 16-inch balloons form the main mass, smaller 5-inch balloons fill gaps and create detail. The garland should look attached to a wall or hidden support points, with believable gravity and no floating sections.

Use a controlled professional color distribution inspired by the real LT garland photo: bright blue, white, black, and metallic silver. Group colors in weighted masses rather than evenly alternating every balloon. Blue and white should form the primary structure; black should create bold clustered accents; metallic silver should appear as small accent pops, not everywhere.

Set the piece in a consistent premium interior mockup: pale warm wall, simple modern console or neutral event backdrop, clean floor, soft catalog lighting. The composition should show the garland as the product, centered with enough margin for ecommerce cropping. Keep real-world installation logic visible through wall placement and natural contact points.

Negative constraints: no classic uniform quad arch, no evenly spaced same-size balloons, no random confetti color, no impossible floating garland, no messy living-room clutter, no garbled wall text, no fake logo, no people.
```

Hard review checks:

- It must read organic through size mix and controlled masses.
- It must not look like a classic cluster arch.
- Rigging/contact points must make physical sense.

## Prompt 5: Birthday Deliveries, Premium Studio Catalog

Product target:

- `birthday-deliveries`
- Size interpretation: medium delivery with foil number and bouquet base.
- Theme: cheerful rainbow birthday.
- Use: studio lead image and future theme/number variant pattern.

Prompt:

```text
Create a realistic premium studio product render of a birthday balloon delivery arrangement for Locally Twisted. The arrangement includes two large rose-gold foil number balloons, a round birthday-themed foil balloon, rainbow accent foil shapes, and a grounded latex balloon base. The latex base should physically support and visually anchor the composition, using teal, yellow, blush pink, soft cream, and a few small neutral filler balloons.

The foil balloons should look helium-filled or securely attached by stems/line into the latex base. The number balloons must have correct shape, perspective, seams, and reflective foil material. Use only intentional readable text if it is clean and correct; otherwise avoid lettering on the generated foil surfaces. The design should look deliverable, not digitally pasted together.

Set the product against a consistent premium studio catalog backdrop: warm white paneled wall, pale wood or light neutral floor, soft shadow under the base, bright commercial product lighting, no clutter. Product centered, cropped to show the full arrangement with enough negative space above and around for ecommerce display.

Negative constraints: no garbled readable text, no malformed numbers, no disconnected foils, no latex base floating away from the foils, no random balloon clutter, no dark background, no people, no fake brand logo.
```

Hard review checks:

- Foil number shape and perspective must be believable.
- Latex base must support the composition.
- Any generated text must either be correct or absent.

## GL Review Sheet

Use this for each pilot image:

| Check | Pass / Revise / Reject | Notes |
|---|---|---|
| Resembles LT source product family |  |  |
| Construction is physically plausible |  |  |
| Color logic matches the product style |  |  |
| Scale matches the selected size option |  |  |
| Background feels consistent with the LT system |  |  |
| Does not mislead as real LT proof photo |  |  |

Recommended decisions:

- Approve for next pilot round.
- Revise prompt and regenerate.
- Reject because construction is wrong.
- Reject because style/brand is wrong.
- Reject because it is too likely to mislead customers.

## Next Step

Generate only these five pilot images. Do not create a full catalog batch, do not attach media to ERPNext, and do not update product images until GL approves the generated direction.
