# Product Details — Customizable Event Decor Design Tool Contest

**Status:** Surfaced 2026-04-29 BETWEEN Round 1 reflective loops and Round 2 dispatch. GL flagged that contestants designed against abstract shapes ("Balloon Arch") without the actual product structure. This file fills that gap.

**Source:** `_resources/odoo-export/catalog.json` (51 products extracted from the Hetzner Odoo deployment 2026-04-26).

**GL's correction (2026-04-29):** *"The organic arch and full classic arch are the same. Organic is actually an option, not a product its own."* The Odoo catalog separated them as distinct products, but the business reality is they're a single product with Organic as a Design option (alongside Swirl and Layered). The same logic applies to Columns. **The product details below merge them per GL's framing.**

**Why this file exists:** The Design attribute (Swirl / Layered / Organic) is the swirl/chunk distinction GL named. The per-Design color counts are load-bearing for fill-region UX decisions. Contestants need this grounding for Round 2.

---

## The 7 contest shapes vs. the actual catalog

The brief listed 7 parametric shapes in scope. The catalog reveals **only ~4 are palette-customizable**. Bouquets and Centerpieces follow a different flow (themed pick, fixed palette per theme). Contestants should be aware:

| Brief shape | Catalog reality | Customization model |
|---|---|---|
| Balloon Arches | Arch (Classic, with Design = Swirl/Layered/Organic) | **Palette + structure** — per the Design choice |
| Columns | Column (Classic, with Design = Classic/Organic implicit) | **Palette + scale + topper** |
| Garlands | Garland | **Palette + length** |
| Picture Perfect Backdrops (walls) | One catalog entry, no Design/Size attributes | **Palette only** (custom-shaped per event) |
| Balloon Drops | Drop | **Palette + count** (balloons released) |
| Balloon Bouquets | **Mostly themed** (Unicorn, Mickey, Stitch...) | **Theme picker, fixed palette per theme** — NOT free-color |
| Centerpieces | Themed/preset Orbz combinations | **Theme picker, very limited free color** |

**Implication for the design tool:** the "tap any shape, color it" model fits Arches/Columns/Garlands/Backdrops cleanly. For Bouquets and Centerpieces, the customer flow is different (browse themes → pick one → see fixed palette). A v1 design tool may legitimately scope to the 4 palette-customizable shapes and treat Bouquets/Centerpieces as "Browse our themed collection" inquiry routes.

---

## 1. Arch — palette-customizable

GL's framing: Classic Arch and Classic Organic Arch are **one product**. Organic is a Design option, not a separate product.

**Canonical Arch attributes (merged):**

| Attribute | Options |
|---|---|
| **Arch Size** | 20ft, 25ft, 30ft, 35ft |
| **Design** | **Swirl (up to 4 colors)** \| **Layered (up to 8 colors)** \| **Organic (artistic clusters, varied balloon sizes)** |
| **LED Lights** | No Lights, Add LED Lights *(applies to Classic Designs; may not apply to Organic — confirm with Jeff if this matters)* |
| **Add-ons (Organic Design)** | None, Foil stars, themed foils |
| **latex colors** | 53 (shared catalog — see Section 6) |

**The Design attribute is the load-bearing structural choice.** Each Design has different max color counts:
- **Swirl:** alternating spiral pattern around the arch frame, up to 4 colors
- **Layered:** horizontal bands of color stacked along the arch, up to 8 colors
- **Organic:** clusters of varied-size balloons (no structured spirals/bands), palette-driven not region-driven

**Pricing reference:** Classic ($260 base), Organic ($500 base — the larger 11-inch balloon spec adds material cost), Premium Organic ($720 — bigger sizes / additional add-ons).

### Other arch products in the catalog (themed/preset, not palette-customizable)

These are **fixed-design occasion arches** — palette is the theme's, not the customer's:
- Basketball Arch ($340) — themed colors
- Easter Balloon Arch ($375), Easter Arch ($250) — themed
- Halloween arch ($300) — themed (uses 53-color palette though, so customer can recolor)
- Pride Progress Rainbow Arch ($260), Pride Arch ($325) — fixed rainbow
- 6 color rainbow arch ($340) — fixed rainbow

These are **out of scope for the design tool** in v1; they're "Browse occasion arches" inquiry routes.

---

## 2. Column — palette-customizable

Same merge: Classic Column and Classic Organic columns are one product family. Design is implicit (the Topper attribute appears on the Classic-style and not on the Organic-style — that's how the variants distinguish).

**Canonical Column attributes (merged):**

| Attribute | Options |
|---|---|
| **Column Height** | 5ft, 6ft, 7ft, 8ft, 9ft, 10ft |
| **Design** | Classic (with topper) \| Organic (no topper) |
| **Topper (Classic only)** | large topper, Burst, foil star, foil heart, bubble gum, Logo |
| **Add-ons (Premium Organic only)** | Foil stars, themed foils |
| **latex colors** | 53 (shared catalog) |

**Pricing:** Classic Organic ($125), Premium Organic ($180), Star Column / Sleepy Baby Column ($220), 7' Butterfly / Epic Column ($100-120).

### Other column products (themed/preset)

- **Number Balloon Columns** ($55) — uses single-digit number selection; only 7 colors available; small-scale display piece, not a customizable installation
- **Star Column** ($None) — uses Orbz toppers (themed: Red, Blue/Green, Black/gold, Purple, Pink Marble, etc.) + reduced 29-color palette
- **Sleepy Baby Column** ($220), **7' Butterfly Column** ($120) — themed; latex colors but no other config
- **Mother's Day front yard 7' Column** ($140) — themed/seasonal

These themed columns don't fit the "color my column" model cleanly; they're occasion-specific.

---

## 3. Garland — palette-customizable

Simplest of the customizable shapes. No Design / Topper / Add-on attributes — just length and palette.

**Canonical Garland attributes:**

| Attribute | Options |
|---|---|
| **Garland Length** | 6ft, 9ft, 12ft |
| **latex colors** | 53 (shared catalog) |

Multiple garland products exist (Classic Organic Balloon Garland, Premium Organic Garland $216, Baby Shower Garland $150, Large Garland $216) but their attribute sets are identical or close. The variation is in pricing tier (size/scale/tightness of the cluster) rather than customization options.

**Implication for the design tool:** Garlands are pure palette-driven. No structural choice (Swirl/Layered/Organic distinction doesn't apply — all garlands are organic). A simple palette-only fill UX serves this shape.

---

## 4. Picture Perfect Backdrop (Wall) — palette-only, custom-shaped

**Only one catalog entry: Baby Shower Combination Photo opt ($650).**

| Attribute | Options |
|---|---|
| **latex colors** | 53 (shared catalog) |

No Size, no Design, no Add-ons. The catalog suggests **backdrops are custom-shaped per event** — the conversation between Jeff and the customer determines the shape; the tool just establishes the palette. **Implication for the design tool:** the backdrop SVG illustration may want to be more abstract / rectangular / wall-shaped to communicate "we'll shape it for your space." Customer picks colors only; size/shape is conversation territory.

---

## 5. Balloon Drop — palette + count

| Attribute | Options |
|---|---|
| **Drop Size** | 250, 500, 1000 *(presumably balloon counts released)* |
| **latex colors** | 53 (shared catalog) |

**Pricing:** Balloon Drop ($375).

The Drop Size attribute is **discrete and quantitative** — 250/500/1000 balloons. The customer picks a tier; the tool may want to surface the count as part of the inquiry payload to Jeff.

---

## 6. Balloon Bouquets — THEMED (not palette-customizable in the contest's sense)

This is the biggest divergence from the brief. **Most bouquets are theme-locked** — the customer picks "Unicorn" and gets the unicorn palette. There's no fill-region UX for these.

### The themed bouquets (~13 products at $35 each)

Unicorn, Mickey Mouse, Minion, Encanto, Stitch, Flamingo, Football, Soccer, Over the Hill, Space, Paw Patrol, Elsa, Holy COW!!, etc.

**Shared attributes for themed bouquets:**

| Attribute | Options |
|---|---|
| **Bouquet Size** | Small (1 super shape, 2 foils, 7 latex) \| Medium (2 super shapes, 4 foils, 14 latex) \| Large (3 super shapes, 5 foil, 16 latex) |
| **Add Foil Number** | 0-9 *(for anniversaries/birthdays — adds a number balloon)* |

**No color picker.** The theme determines the palette.

### The exceptions

- **Logo 3 layered bouquet** ($90) — uses the 53-color palette, presumably for custom corporate-branded bouquets
- **Get Well bouquets (Latex free)** ($35) — Plush add-on (Teddy Bear); themed

**Implication for the design tool:** Bouquets do NOT fit the "tap a shape, color it" model. They're a **gallery-pick** experience: customer browses themed cards, picks one, picks size + optional number digit, sends inquiry. The design tool may want to either:
1. Treat Bouquets as a separate "Browse our bouquets" entry path (gallery, not configurator)
2. Include only the Logo bouquet as a custom-color option, and route themed bouquets to a different page
3. Scope Bouquets out of v1 entirely

---

## 7. Centerpieces — themed/preset

| Product | Attributes | Customization |
|---|---|---|
| **Baby Table decor** ($30) | 2 colors | Very limited — pick from 2 |
| **Marble table decor** ($75) | Orbz toppers (Red, Blue/Green, Black/gold, Purple, Blue/gold, Fantacy, Pink/gold, Gold Marble, Pink Marble, Blue Marble) | Pick a preset combo, not free color |

**Implication for the design tool:** Like Bouquets, centerpieces are **preset/themed pick**, not palette-customizable. A "tap a centerpiece, color it" UX would force the tool to fight the catalog. May want to:
1. Scope centerpieces out of v1
2. Treat them as gallery-pick (browse Marble combos, pick one, inquire)
3. Show the 2-color Baby Table decor as a minimal palette option, route Marble to gallery

---

## 8. Shared Latex Colors Catalog (53 colors)

Same set across every palette-customizable product. **This is the canonical 50+ catalog the brief referenced.** No hex codes are exposed in the Odoo product pages (Odoo stores those internally; not in the public HTML).

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

**Notes for the design tool:**

- Color **names are essential** to surface. These are how Jeff orders from his supplier. "Reflex Champagne" is the SKU-level identifier; "champagne" alone is ambiguous across suppliers.
- **Hex codes don't exist in the export.** This shifts the brief's "customers must see hex while picking" assumption: the named-color match is what Jeff orders against. Hex display in the picker becomes a UX nicety (eyeball matching for the customer), not a supplier-call necessity for Jeff.
- Some colors **family-pair naturally**: Reflex* (metallic), Dusk* (muted), Pastel* (soft). Family-grouped picker organization (3 of 4 contestants chose this) is structurally validated by the catalog itself.
- **Per-product color subsets exist**: Star Column = 29 colors (subset), Number Balloon Columns = 7 colors (small subset), Baby Table decor = 2 colors. The "53 universal palette" applies to the BIG installations; smaller items use curated subsets.

---

## What this means for Round 2

### Major shifts from the original brief

1. **The 7-shape "in scope" list overstates customization.** Only ~4 shapes (Arch, Column, Garland, Backdrop) are palette-customizable. Bouquets and Centerpieces are theme-pick experiences. Round 2 contestants may want to acknowledge this and either scope down to the 4 palette-customizable shapes, OR design two parallel flows (palette flow for Arch/Column/Garland/Backdrop + theme-pick flow for Bouquets/Centerpieces).

2. **Arch's Design attribute is the load-bearing fill-region decision.** Swirl (up to 4) vs Layered (up to 8) vs Organic (palette-only, no regions) shapes the entire UX:
   - **Swirl:** 2-4 fill regions makes sense (alternating pattern)
   - **Layered:** up to 8 horizontal bands (more regions OR sequential color picks)
   - **Organic:** palette-only, no per-region picking — pick 3-5 colors that work together
   - **The customer should pick the Design FIRST**, then color into the structure that Design implies. OR the tool defaults to one Design (likely Swirl as the simplest) and offers the others as Stage 2.

3. **Hex codes don't actually exist in the catalog.** Contestants who emphasized hex-as-supplier-action need to reframe — hex is for the customer's eyeball matching only; Jeff orders against the color NAME. This may shift the picker's information hierarchy: name > family > hex (visual fidelity only, not actionable specification).

4. **The Topper / Add-ons / LED Lights attributes are real.** These are categorical picks that exist in the actual product. Defensible options for the design tool:
   - Out of scope (conversation territory — Jeff handles these in the inquiry follow-up)
   - In scope as small "customize the extras" UI after color picking
   - Surfaced in the Jeff-side payload only ("here's the design + the customer hasn't picked toppers yet — discuss")

5. **Sizes (20-35ft arches, 5-10ft columns, 6-12ft garlands, 250/500/1000 drops) are real.** They're not palette-customization but they ARE customer-pickable. The design tool may want a single-line scale indicator or explicitly defer to Jeff's pitch.

### What this CONFIRMS in the contestants' Round 1 work

- **Family-grouped picker** (C2, C3, C4) — confirmed by catalog's natural family clustering.
- **Real color names** in the picker — every contestant mentioned hex; the catalog confirms NAMES are also load-bearing.
- **53 colors fits "50+"** — picker scaling logic is valid.
- **Per-shape entry pattern** — the catalog confirms each shape has different attributes; per-shape entry is structurally right.

### Round 2 directive

You have new context. You may use it as:
- **Refinement input** (Path A) — tighten what's already strong; adjust to use real catalog details (53 named colors, the Design choice on Arches, the Topper attribute on Columns, etc.)
- **Lean signal** (Path B-lean) — sharpen your distinctive move with the new context. Does the Design attribute amplify your fill-region argument or undermine it?
- **Pivot trigger** (Path B-pivot) — if the catalog's themed-bouquet model invalidates "all 7 shapes follow the same fill pattern" enough that you want to pivot to a different conceptual frame, that's valid. Note prior approach in `ROUND-2-CHOICE.md` for traceability.

The Design attribute (Swirl/Layered/Organic on Arches) is the most consequential shift. It may force a meaningful redesign of how customers enter a shape, OR it may strengthen your existing model as an "uses Swirl by default" simplification.

---

*Surfaced by orchestrator 2026-04-29 between Round 1 reflective loops and Round 2 dispatch. GL directive: contestants need product-detail grounding for Round 2 work. Updated to reflect GL's clarification that Organic is a Design option on Arch/Column, not a separate product.*
