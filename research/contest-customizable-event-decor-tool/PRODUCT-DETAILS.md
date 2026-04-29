# Product Details — Customizable Event Decor Design Tool Contest

**Status:** Updated 2026-04-29 between Round 1 reflective loops and Round 2 dispatch. Replaces the earlier draft. Contains the actual product specs + construction physics + GL's directives + optional architecture suggestions from external AI research.

**Sources:** Catalog export at `_resources/odoo-export/catalog.json` (51 products), GL's clarifications and corrections, and two independent AI research dumps (Claude.ai + ChatGPT) commissioned by GL on balloon construction physics. Sources cited in Section 6.

---

## 1. How to read this file

This file has three layers, distinguished by what they require of you:

| Layer | What it is | Status for Round 2 |
|---|---|---|
| **Section 2 — Product specs** | The actual catalog reality per shape, GL-corrected | LOAD-BEARING. Your designs must match these specs. |
| **Section 3 — Construction physics math** | The real construction rules (4-cluster atomic unit, gcd color cycles, organic placement, etc.) | LOAD-BEARING. Designs that violate physics produce un-buildable mockups. |
| **Section 4 — Required UX surface** | The one customer-facing rule you must honor | LOAD-BEARING. Color names are the supplier-actionable identifier. |
| **Section 5 — Optional architecture suggestions** | Ideas from ChatGPT (without seeing the contest) on engine model, layout templates, UX shifts, Frappe code architecture | OPTIONAL. Use if useful; ignore if not. ChatGPT didn't have the contest context. |
| **Section 6 — Source appendix** | Verbatim research dumps for deeper reference | TRACEABILITY. Open if you want to verify a specific claim. |

**The contest is still collaborative, not competitive.** Don't pivot away from your Round 1 distinctive move just because new info landed. Use the new info to either tighten your existing design or, if it forces a re-frame, document why in `ROUND-2-CHOICE.md`.

---

## 2. Per-shape product specs

### 2.1 Arch

GL's directive: **Classic Arch and Classic Organic Arch are ONE product.** "Organic" is a Design option alongside Swirl and Layered, not a separate product. The Odoo catalog separated them; the business reality merges them.

| Attribute | Options |
|---|---|
| **Size** | Customer-specified length, sqft-priced. Common reference points: 20ft, 25ft, 30ft, 35ft. Customer can request any length. |
| **Design** | **Swirl (up to 4 colors)** \| **Layered (up to 8 colors)** \| **Organic (palette-driven, varied balloon sizes)** |
| **Balloon Size** (per Design + size) | 5", 9", 11", 14-16" — affects per-foot count |
| **latex colors** | 53 named colors (shared catalog — Section 2.8) |
| **Add-ons** | OUT OF SCOPE for this contest (LED Lights, Foil stars, themed foils — handled in Jeff's pitch conversation) |

**Pricing tier reference (informational only):** Classic ($260 base), Organic ($500), Premium Organic ($720). Pricing scales by size/scale; the contest tool doesn't display price.

**Themed/preset arches** (Basketball, Easter, Halloween, Pride, Pride Progress, Rainbow) are out of contest scope — they're "Browse our occasion arches" gallery-pick routes.

### 2.2 Column

GL's directive: same merge. Classic Column and Classic Organic columns are one product family. Design distinguishes them.

| Attribute | Options |
|---|---|
| **Height** | Customer-specified, sqft-priced. Common reference points: 5ft, 6ft, 7ft, 8ft, 9ft, 10ft. Customer can request any height. |
| **Design** | **Classic (with 4-cluster spiral/chunk + topper)** \| **Organic (mixed-size, no topper, no fixed cluster)** |
| **Topper (Classic only)** | OUT OF SCOPE for this contest (handled in conversation) |
| **Add-ons (Premium Organic only)** | OUT OF SCOPE for this contest |
| **latex colors** | 53 named colors (shared catalog) |

**Pricing tier reference:** Classic Organic ($125), Premium Organic ($180), variants up to $220.

**Themed/preset columns** (Number Balloon, Star, Sleepy Baby, Butterfly, Epic, Mother's Day) are out of contest scope.

### 2.3 Garland

| Attribute | Options |
|---|---|
| **Length** | Customer-specified, sqft-priced. Common reference points: 6ft, 9ft, 12ft. Customer can request any length. |
| **Design** | Always organic. Style choices: Solid \| Tonal/Monochromatic \| Two-tone alternation \| Multi-color organic blend \| Ombré/gradient \| Color-blocked \| Accent-cluster \| Tapered/asymmetric |
| **Density tier** | Light (4-6 balloons/ft) \| Standard (7-9 balloons/ft) \| Lush (10-12 balloons/ft) \| Mixed-size premium (12-14/ft) |
| **Size mix** | Default 50% mid (9"/11") + 30% small (5") + 20% large (16"+); adjustable for chunkier/denser looks |
| **latex colors** | 53 named colors (shared catalog) |

**Construction unit:** Doublets (two balloons tied at necks) on a decorating strip or fishing-line backbone, with 5" balloons added as filler last. Not a fixed cluster; the unit is "doublet + filler."

**Color distribution rule:** Controlled randomness with no-touching-twins constraint (no two same-color same-size balloons adjacent). For ombré, zoned with feathered overlap.

### 2.4 Backdrop / Wall

GL's directive: **any size, sqft-priced.** No fixed dropdowns.

| Attribute | Options |
|---|---|
| **Dimensions** | Customer-specified width × height. Common reference points: 8x8 ft, 10x10 ft, 10x30 ft. Pricing scales by sqft. |
| **Design** | Solid \| Vertical Stripes (≥2 stripes) \| Horizontal Stripes (≥2 stripes) \| Color Blocks (chunks of solid color, e.g., top/middle/bottom thirds) \| Diagonal Stripes \| Lattice/Criss-cross (2-3 colors: background + 1-2 accent diagonals) |
| **latex colors** | Per Design: Solid=1 \| Stripes=2-N (one per stripe) \| Color Blocks=2-3 \| Diagonal=2 \| Lattice=2-3 |

**Construction:** 4-balloon cluster grid where each cluster = 1 "pixel" in the grid. Math:
- `clusters = width_ft × height_ft`
- `balloons = clusters × 4`
- 8x8 = 64 clusters / 256 balloons (~285-300 with 10-15% extra)
- 10x10 = 100 clusters / 400 balloons (~440-460 with 10-15% extra)

**Lattice color ratio:** Background 60-75%, accent 25-40%. Three-color lattice = background + diagonal A + diagonal B with chosen dominance at intersections.

### 2.5 Drop

| Attribute | Options |
|---|---|
| **Drop Size** | 250 \| 500 \| 1000 (literal balloon counts in 9" balloons; 11" balloons cut capacity ~50%) |
| **Design** | Classic mix (proportional random) \| Confetti/multi-size mix \| Foil accent mix \| Themed packs \| Confetti-filled balloons |
| **Color count cap (recommended)** | 250: 2-3 colors \| 500: 3-4 colors \| 1000: 4-6 colors |
| **latex colors** | 53 named colors (shared catalog) |

**Construction:** Pre-strung ceiling drop net (rectangular folded or tunnel/tube format) with pull-cord release. **Air-filled, not helium.** Colors mix randomly once released — no spatial pattern survives gravity.

**Customer-facing rendering:** Representational (not literal balloon-count). 250-1000 balloons can't render at 375px; show a stylized cloud-of-balloons with proportional color mix.

**Most common customer color counts:** 2 colors (team/wedding/brand) > 3 colors (corporate + accent) > 4+ (rainbow/themed). Default to 2-color picker with "add color" affordance up to the cap.

**Optional: ratio sliders** when 3+ colors selected so customer can specify 60/30/10 instead of equal thirds — research-recommended UX upgrade.

### 2.6 Bouquet

GL's directive: **mostly themed, not palette-customizable in the contest's sense.** The customer picks a theme; the theme determines the latex palette. Foil colors are picker-able. Logo bouquets are the custom-palette exception.

| Attribute | Options |
|---|---|
| **Theme/Super-Shape** | Inventory-based pick — customer browses available themes (Unicorn, Mickey Mouse, Stitch, Encanto, Football, Soccer, Elsa, Paw Patrol, Holy Cow, Get Well, Logo, etc.). Catalog of available super-shapes is Jeff-side; **leave a place in the design for it**. |
| **Bouquet Size** | Small (1 super shape, 2 foils, 7 latex) \| Medium (2 super shapes, 4 foils, 14 latex) \| Large (3 super shapes, 5 foils, 16 latex) |
| **Foil colors** | Star: Red, Blue, Green, Yellow, Black \| Heart: Red, Blue, White, Pink \| Number: Silver, Gold |
| **Number digit (optional)** | 0-9 (anniversary/birthday) |
| **latex colors** | Theme-locked (set by super-shape). Exception: Logo bouquet uses 53-color palette for custom corporate colors. |
| **Plush add-ons (Get Well only)** | Teddy Bear option |

**Construction model (per ChatGPT research):** SKU bundle/stem recipe — not a tap-color picker. Customer browses themes (gallery-pick), selects size, selects foil colors per shape type, optionally adds a number digit.

### 2.7 Centerpiece — OUT OF CONTEST SCOPE

GL's directive: **drop centerpieces from the design tool.** The catalog reveals they're themed/preset (Marble combos with Orbz toppers, Baby table decor with 2 colors). Not customizable in the same sense as the other shapes. Treat as "Browse our centerpiece collection" gallery-pick — out of the design tool's design responsibility.

### 2.8 Shared Latex Colors Catalog (53 colors)

Same set across every palette-customizable product (Arches, Columns, Garlands, Backdrops, Drops, Logo bouquets). **No hex codes in the export.** Names verbatim from the catalog:

```
Reflex Champagne, Reflex Truffle, Reflex Silver, Reflex Gold, Reflex Blue,
Reflex Green, Reflex Violet, Reflex Red, Dusk Cream, Dusk Green Tea,
Dusk Blue, Dusk Lilac, Dusk Rose, Teal, Blue Slate, Smoke Grey, White,
Black, Red, Orange, Yellow, Raspberry, Fuchsia, Bubble Gum, Eucalyptus,
Forest, Shamrock, Wintergreen, Lime, LT Blue, Periwinkle, Royal Blue,
Robin's Egg, Deep Teal, Honey, Violet, Orchid, Lilac, Chocolate, Brown,
Latte, Pastel Pink, Pastel Blue, Pastel Green, Pastel Purple,
Pastel Yellow, Pastel Melon, Grey, Clear, Blush, Empowermint
```

**Subset palettes for specific products:** Star Column = 29 colors, Number Balloon Columns = 7 colors, Baby Table decor = 2 colors. The 53-palette applies to large installations; smaller items use curated subsets. For the contest, design against the 53 set.

**Family clusters in the palette (natural groupings for picker organization):**
- **Reflex*** — metallics
- **Dusk*** — muted/desaturated
- **Pastel*** — soft tints
- **Brights** — Red, Orange, Yellow, Lime, Royal Blue, Fuchsia, etc.
- **Neutrals** — White, Black, Grey, Smoke Grey, Latte, Brown, Chocolate
- **Deep tones** — Forest, Wintergreen, Deep Teal, Royal Blue, Violet

---

## 3. Construction physics math

The constraints designs must respect. Designs that violate these produce un-buildable mockups.

### 3.1 The 4-balloon cluster (atomic unit for classic arches, columns, walls)

A 4-balloon cluster ("quad") is built from two doublets (pairs of balloons tied at the neck) twisted together at 90°, forming a plus/X shape. The cluster is then attached to a frame (arch, column, or backdrop grid). Adjacent clusters interlock by rotation.

This is the atomic unit for:
- **Classic Arches** (clusters along the arch frame)
- **Classic Columns** (clusters stacked around the central pole)
- **Backdrops/Walls** (clusters in a 2D grid, each cluster = 1 "pixel")

Organic shapes (Organic Arch, Organic Column, Garlands) DO NOT use the 4-cluster. They use mixed-size doublets + filler, an artist-led organic placement.

### 3.2 Per-foot balloon counts (arches and columns)

| Balloon size | Balloons per foot | Clusters per foot |
|---|---:|---:|
| 5" | 12-13 | 3 |
| 9" | 7-8 | 2 |
| 11" | 6-7 | 1.5-1.75 |
| 14-16" | 4-5 | 1-1.25 |

**Formula:** `total_balloons = arch_length_ft × balloons_per_foot`. `clusters = total_balloons ÷ 4`.

Columns may pack ~1 cluster/ft tighter than arches because they're viewed from all sides. Treat column counts as minimum.

### 3.3 Color distribution math (4-cluster designs)

For any number of colors C, the minimum cluster repeat to distribute evenly:

```
minimum_cluster_repeat = C ÷ gcd(C, 4)
```

| Colors | Min repeat | Pattern |
|---:|---:|---|
| 1 | 1 | A A A A |
| 2 | 1 | A B A B |
| 3 | 3 | (A A B C) (A B B C) (A B C C) |
| 4 | 1 | A B C D |
| 5 | 5 | 5-cluster cycle |
| 6 | 3 | 3-cluster cycle with each color twice |
| 8 | 2 | 2-cluster cycle, all 8 colors |

**3-color spiral:** the cycle (A A B C) → (A B B C) → (A B C C) repeats every 3 clusters. Each color appears 4 times across the 3-cluster repeat — balanced.

**Customer-facing implication:** the customer picks a color count; the tool distributes via this math. The customer doesn't pick which cluster gets which color — the math handles slot distribution.

### 3.4 Spiral rotation (arches and columns)

```
position = (cluster_number × spiral_step) mod 4
```

- `spiral_step = 1`: Swirl/spiral candy-cane effect (1/4 turn per cluster)
- `spiral_step = 0`: Chunk/banded effect (no rotation, color blocks)
- `spiral_step = 2`: Vertical-stripe effect (alternating sides)

Spiral arches need at least 3 full cycles to read clearly. A 5-foot column with a 4-color spiral may show only 1-2 cycles — visually weak. Long arches and tall columns scale better for spiral patterns.

### 3.5 Backdrop grid math

```
clusters = width_ft × height_ft
balloons = clusters × 4
```

Each cluster occupies ~1 sqft. Designs treat the cluster grid as a pixel grid:

- **Solid:** all clusters same color
- **Vertical Stripes:** column-of-clusters per stripe (e.g., 8x8 wall with 4 vertical stripes = 2 clusters wide × 8 tall = 16 clusters per stripe = 64 balloons per stripe)
- **Horizontal Stripes:** row-of-clusters per stripe
- **Color Blocks:** large rectangular regions (e.g., top third, middle third, bottom third)
- **Diagonal Stripes:** clusters on the diagonal axis colored together
- **Lattice:** background fill + diagonal lines crossing both directions; intersection cluster takes one of the two colors or a 2+2 mixed cluster

### 3.6 Organic garland placement

No fixed cluster. Construction is doublet-on-strip + 5" filler. Color placement follows controlled randomness:

- **Total count:** `length_ft × density_per_ft` (Light 4-6, Standard 7-9, Lush 10-12)
- **Size mix:** typically 50% mid-size + 30% small + 20% large, adjustable
- **Color distribution:** weighted random (per customer-chosen palette + ratios) with **no-touching-twins** constraint (no two same-color-same-size balloons adjacent)
- **For ombré:** zoned with feathered overlap (e.g., 30% A → 15% A+B blend → 30% B → 15% B+C blend → 30% C)
- **For accent-cluster:** intentionally clumped at one or both ends

True random looks worse than artist-curated placement. The tool should use weighted random + adjacency constraint, not uniform random.

### 3.7 Drop math

- 250-balloon drop = 250 9" balloons (or ~125 11" balloons)
- 500-balloon drop = 500 9" balloons (or ~250 11" balloons)
- 1000-balloon drop = 1000 9" balloons (or ~500 11" balloons)

Color distribution: proportional random to customer's color count (or ratios if specified). Once released, all spatial pattern is lost to gravity — no patterning survives the drop.

### 3.8 Bouquet recipe

Per size:
- **Small:** 1 super-shape + 2 foils + 7 latex
- **Medium:** 2 super-shapes + 4 foils + 14 latex
- **Large:** 3 super-shapes + 5 foils + 16 latex

The latex palette is theme-locked (set by super-shape) for themed bouquets, customer-pickable from the 53-palette for Logo bouquets only. Foils are picker-able from foil-shape-specific palettes (Star, Heart, Number).

---

## 4. Required UX surface — color name as primary identifier

**The one thing every contestant must do:** show the **color name** alongside the swatch in the picker. Hex codes are eyeball-matching aids only and are not yet sourced for the catalog (Jeff will provide hex/Pantone mappings later).

**Why:** Jeff orders against names. "Reflex Champagne" is a different SKU than "Champagne" or "Pastel Yellow." When a customer's design lands in Jeff's CRM, the color name flows through to his supplier call. Names are supplier-actionable; hex is downstream eyeball-fidelity.

**For contestants:** ensure your picker UI surfaces the color name on selection (and on hover/long-press for not-yet-selected swatches if your design supports it). Render with reasonable approximation hex (your call) but treat the name as the load-bearing identifier in the inquiry payload.

**Customer concern this addresses:** corporate clients and schools want to match brand/team colors. The color-match conversation will happen between Jeff and the customer post-inquiry; the tool's job is to capture which catalog colors the customer chose by NAME, not to certify that "Reflex Gold" matches Pantone 871.

---

## 5. Optional — architecture and UX suggestions from external research

**Framing:** these ideas come from ChatGPT and Claude.ai dumps GL commissioned. Neither AI saw the contest brief or your Round 1 work. **Use them if useful; ignore if not.** The physics in Sections 2-3 is grounded and required; everything in Section 5 is proposal.

### 5.1 The four-engine model (ChatGPT)

ChatGPT proposed organizing the design tool around four rendering engines, each handling a structurally distinct physics:

| Engine | Shapes | Customer flow it implies |
|---|---|---|
| **StructuredClusterEngine** | Classic Arches, Classic Columns, Backdrops | Pick Style → pick color count (capped by Style) → pick colors → tool auto-distributes via 4-cluster + gcd math |
| **OrganicRecipeEngine** | Garlands, Organic Arches, Organic Columns | Pick density tier → pick design style (solid/two-tone/ombre/accent) → pick palette → tool generates with controlled randomness + no-touching-twins |
| **DropMixEngine** | Balloon Drops | Pick count tier → pick color count (capped by drop size) → pick colors + ratios → tool shows representational mix |
| **BouquetSkuEngine** | Themed bouquets | Pick theme/super-shape (gallery) → pick size → pick foil colors + optional number digit |

**This isn't a required architecture.** Some contestants may prefer a unified UX that presents differently based on shape; others may keep their Round 1 single-engine "tap and color" model and translate to physics behind the scenes. Both can be valid.

### 5.2 Layout templates (ChatGPT)

Instead of free drag-and-drop or per-shape standalone designs, ChatGPT suggested **layout templates**: pre-defined scenes the customer picks from before customizing pieces.

| Example template | Components |
|---|---|
| Entrance Arch | 1 arch |
| Arch + 2 Columns | 1 arch + 2 columns (mirrored, color-coordinated by default) |
| Backdrop + Garland | 1 backdrop + 1 garland (garland framing the bottom) |
| Backdrop + 2 Columns | 1 backdrop + 2 columns flanking |
| Balloon Wall + Bouquets | 1 wall + 2-3 floor bouquets |
| Drop + Stage Decor | 1 drop + supporting pieces |
| Full Party Scene | All-in: arch + columns + drops + bouquets |

**The customer picks a template first** ("I have an entrance" → pick an entrance template), then customizes each component with the per-shape physics rules. This gives the customer a starting frame instead of a blank canvas.

**Trade-off:** layout templates compete with C2's cascading-ghost mechanic and C3's empty-slots-from-the-start as solutions to the "how does the customer build a multi-piece composition" problem. None is wrong; they're different framings. Round 2 contestants may fold layout templates in OR defend their existing mechanic — both valid.

### 5.3 Customer-UX shift (the "Option B" framing)

Round 1 contestants used "tap a region, color a region" UX. Under physics constraints, this is fine for Backdrops (each cluster IS a tappable region) and Bouquets (gallery-pick, no region tapping).

For Arches, Columns, and Garlands, the physics doesn't have spatial regions. Three valid responses:

- **(a) Keep region-tap UX**, translate regions to physics math behind the scenes. Customer taps "main region," picks 3 colors total; tool distributes those 3 colors across the actual cluster sequence using gcd.
- **(b) Shift to pick-style-then-colors UX.** Customer picks Style → picks color count → picks colors → tool renders auto-distributed result. More constrained but more honest.
- **(c) Hybrid** — region-tap with the color cap visibly enforced (e.g., "this Swirl arch supports 4 color slots; pick 4").

All three are valid. Round 2 contestants choose what fits their distinctive move.

### 5.4 Sliders for "any size"

GL confirmed: backdrops, columns, arches, garlands are all "any size, sqft-priced." Sliders for dimension input are an option; fixed-dropdown chips ("8x8 / 10x10 / 12x12 / custom") are also valid. Contestants who use sliders should show live cluster-count + balloon-count alongside.

### 5.5 ChatGPT's Frappe-native architecture sketch

For the implementation phase (post-contest), ChatGPT proposed:

```
Frappe Website Page → customer-facing design board
DocTypes              → Decor Color, Decor Product Type, Decor Style,
                        Decor Rule, Decor Layout Template,
                        Decor Proposal, Decor Proposal Item
Client Script         → live preview + design rules in browser
Server Script         → final counts + save proposal server-side
Print Format          → shareable proposal page output
```

The idea: store rules in DocTypes so non-developers can add styles, color caps, formula adjustments without code changes. Read rules at runtime; render via vanilla SVG.

**This is implementation guidance, not contest scope.** Mockups don't need to instantiate this architecture — but if your mockup design hints at how the rules-driven approach would work, that's a plus for the implementation phase.

### 5.6 Other ideas surfaced in the research

- **Ratio sliders for drops** — when 3+ colors selected, let customer specify 60/30/10 instead of equal distribution
- **Density tier picker for garlands** — Light/Standard/Lush as a customer-facing choice
- **Per-design min/max color enforcement** — UI greys out additional swatches once cap is hit (or shows soft warning, which converts better)
- **No-touching-twins constraint validator** — runs after color placement, swaps adjacent duplicates
- **Themed packs for drops** — "New Year's" (black/silver/gold), "Wedding" (white/blush/champagne), "Corporate" (two brand colors + metallic) — pre-curated 2-color packs that customer can pick whole-cloth

---

## 6. Source appendix

The construction physics in Sections 2-3 was synthesized from two independent AI research dumps GL commissioned 2026-04-29. Both dumps converged on the same physics, raising confidence that this is industry-standard practice. Verbatim source citations:

### 6.1 Claude.ai dump — balloon construction physics

Sources cited in that dump:
- HICO Memphis garland count guide: `https://hicomemphis.com/academy/balloon-garland-balloons-per-foot/`
- Balloon Concierge organic vs. traditional: `https://www.balloonconcierge.com/the-difference-between-organic-balloon-garlands-and-traditional-balloon-arches-and-which-is-right-for-your-event`
- Pop & Drop style categories: `https://www.popanddroptx.com/balloon-styles-colors`
- Bargain Balloons organic notes: `https://support.bargainballoons.com/support/solutions/articles/27000066950-organic-balloons-design`
- Balloon Decoration Guide arch instructions: `https://www.balloon-decoration-guide.com/balloon-arch-instructions.html`
- Balloon Decoration Guide column counts: `https://www.balloon-decoration-guide.com/how-many-11-balloons-per-foot-in-a-column.html`
- Balloon Decoration Guide column construction: `https://www.balloon-decoration-guide.com/balloon-column.html`
- Bargain Balloons 5-balloon clusters: `https://support.bargainballoons.com/support/solutions/articles/27000057652-what-is-a-five-balloon-cluster-`
- Bargain Balloons drop net instructions: `https://support.bargainballoons.com/support/solutions/articles/27000056474-balloon-drop-nets`
- BOSS 250 net: `https://silverrainbow.com/product/boss-250-balloon-drop-net-2ft-x-30ft/`
- BOSS 500 net: `https://balloondropnet.com/product/boss-500-balloon-drop-net-4ft-x-14ft/`
- BOSS 1000 net: `https://balloondropnet.com/product/boss-1000-balloon-drop-net-4ft-x-23ft/`
- Anagram products catalog: `https://anagramballoons.com/products/`
- Anagram licensed releases: `https://support.bargainballoons.com/support/solutions/articles/27000057515-anagram-s-licensed-balloons-new-release-`
- Qualatex Balloon Basics: `https://us.qualatex.com/en-us/education/balloon-basics/`
- IBAC spiral arch tutorial: `balloon.com.tw IBAC` (search reference)
- PartyCalcs balloon quantities (citation reference only, URL not provided in dump)

### 6.2 ChatGPT dump — balloon construction + architecture

Sources cited:
- HICO garland: `https://hicomemphis.com/academy/balloon-garland-balloons-per-foot/`
- Balloon Decoration Guide arch/column: same URLs as above
- Bargain Balloons drop: same URL as above
- BalloonDropNet 14x25 capacity: `https://balloondropnet.com/product/balloon-drop-net-14ft-x-25ft/`
- OSHA sprinkler clearance: `https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.159`
- SG Balloons column sizing: `https://www.balloons.com.sg/article/the-ultimate-guide-to-balloon-sizes-for-balloon-columns`
- BOSS 500/1000: same URLs as above

### 6.3 LT-specific catalog

- Local export: `_resources/odoo-export/catalog.json` (51 products, extracted 2026-04-26)
- Live Hetzner deployment (read-only reference): `http://5.78.136.133/shop/what-we-make-3/`
- Per-product attribute extraction (saved 2026-04-29): `C:/Users/baenb/AppData/Local/Temp/classic-products-extracted.json`

### 6.4 GL-provided directives (this session)

- Classic Arch and Classic Organic Arch are one product; Organic is a Design option (2026-04-29)
- Same merge for Columns
- Backdrop is "any size, sqft-priced" (2026-04-29) — same applies to all linear/area products
- Foils are bouquet-only in this contest (2026-04-29)
- Add-ons are out of scope for this contest (LED Lights, Toppers, Foil stars, themed foils, Plush add-ons)
- Centerpieces are out of contest scope (gallery-pick instead)
- Color name is primary; hex is downstream Stage 2 (Jeff to source actual Pantone/hex)

---

*PRODUCT-DETAILS.md updated 2026-04-29 by orchestrator after GL surfaced the catalog gap and commissioned the two AI research dumps. Replaces the prior draft. Required reading for Round 2 contestants alongside BRIEF.md and FIELD-AT-ROUND-1.md.*
