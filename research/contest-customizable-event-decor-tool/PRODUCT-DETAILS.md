# Classic Product Details — Customizable Event Decor Design Tool Contest

**Status:** Surfaced 2026-04-29 BETWEEN Round 1 reflective loops and Round 2 dispatch. GL flagged that contestants designed against abstract shapes ("Balloon Arch") without the actual product structure. This file fills that gap.

**Source:** Live product pages on the Hetzner Odoo deployment (`http://5.78.136.133/shop/...`). Extracted from the page-embedded `mapped_attribute_names` dict — Odoo's full variant configuration for each product. The Hetzner site is reference-only (will be retired); these specs are accurate as of 2026-04-29.

**Why this file exists:** GL specifically named that the "Classic" versions of these products (Classic Arch, Classic Organic Arch, etc.) carry the actual structural choices a customer makes. The Design attribute (Swirl vs. Layered) is the swirl/chunk distinction. The color counts per Design type are load-bearing for fill-region decisions. Contestants designing without this knew "Balloon Arch needs colors" but didn't know the customer can choose Swirl-up-to-4 OR Layered-up-to-8.

**Scope:** 5 Classic products (the relevant subset for the contest's 7 parametric shapes).

---

## 1. Classic Arch — $260

> *"Every arch is built by hand, sized to your space, and designed around the colors you love. Structured spirals or layered bands — up to 4 colors, shaped to fit the entrance."*

| Attribute | Options |
|---|---|
| **Arch Size** | 20ft, 25ft, 30ft, 35ft |
| **Design** | **Swirl (up to 4 colors)** OR **Layered (up to 8 colors)** |
| **LED Lights** | No Lights, Add LED Lights |
| **latex colors** | 53 colors (see Section 6 — shared palette across all products) |

**The Design attribute is the swirl/chunk distinction.** Swirl = alternating spiral pattern around the arch frame. Layered = horizontal bands of color. The two designs answer different aesthetics; the customer chooses one. Their max-color counts differ meaningfully (4 vs 8). This is the most load-bearing structural choice in the catalog — and it's the one that a fill-region UX decision should respect.

Note the description says "up to 4 colors" while the configurator allows up to 8 in Layered. Customer-facing copy is conservative; the config option allows more. The design tool can offer either bound depending on which Design the customer picks.

---

## 2. Classic Organic Arch — $500

> *"Balloons up to 11 inches, built into a classic organic arch. The scale adds depth and dimension that a standard arch doesn't have."*

| Attribute | Options |
|---|---|
| **Arch Size** | 20ft, 25ft, 30ft, 35ft |
| **Add ons** | None, Foil stars, themed foils |
| **latex colors** | 53 colors (shared palette) |

**Note:** No Design attribute on the Organic version — the organic style is implicit (clusters of varied-size balloons rather than uniform spirals/bands). Color cluster decisions are designer-led for organic; the customer picks the palette but the arrangement is artistic.

This is a meaningful difference from the Classic Arch: organic = cluster aesthetic, no structured swirl/layer choice. **Fill-region UX for this shape should probably be palette-based ("pick 3-5 colors that work together") rather than per-region ("color the main, color the accent").**

---

## 3. Classic Column — (price not in catalog export)

| Attribute | Options |
|---|---|
| **Column Height** | 5ft, 6ft, 7ft, 8ft, 9ft, 10ft |
| **topper** | large topper, Burst, foil star, foil heart, bubble gum, Logo |
| **latex colors** | 53 colors (shared palette) |

**No Design attribute on Classic Column** — single style. The structural variable is height + topper choice.

The "topper" attribute is a **categorical add-on** the customer picks (an item that sits on top of the column — large topper, foil star, custom logo, etc.). For the design tool, a topper either gets its own slot in the composition or is left to the inquiry conversation. Both are defensible; up to each contestant.

---

## 4. Classic Organic columns — $125

| Attribute | Options |
|---|---|
| **Column Height** | 5ft, 6ft, 7ft, 8ft, 9ft, 10ft |
| **latex colors** | 53 colors (shared palette) |

**Lowest-config Classic product.** Color picks + height; no topper, no design. Mirrors the Classic Organic Arch pattern: organic style is implicit, decisions are palette + scale only.

---

## 5. Classic Organic Balloon Garland — (no price in catalog)

| Attribute | Options |
|---|---|
| **Garland Length** | 6ft, 9ft, 12ft |
| **latex colors** | 53 colors (shared palette) |

**Same minimal-config pattern as Classic Organic columns.** Length + palette only; organic arrangement is the artist's call.

---

## 6. Shared Latex Colors Catalog (all products)

53 named colors. Same set across every Classic product — and presumably the rest of the LT catalog. **This is the canonical 50+ catalog the brief referenced.** No hex codes are exposed in the Odoo product pages (Odoo stores those internally; they're not in the public HTML). The names alone:

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
- Color **names are essential** to surface in the picker — these are how Jeff orders from his supplier. "Reflex Champagne" is the SKU-level identifier; "champagne" alone is ambiguous across suppliers.
- Some colors **family-pair naturally**: Reflex* (metallic), Dusk* (muted), Pastel* (soft). A family-grouped picker organization (which 3 of 4 contestants chose) is structurally validated by the catalog itself.
- Hex codes don't exist in the export. **The customer's "I want to match my venue" need has to be solved by the swatch's visual color + the name + a future "best supplier match" pairing — not by a hex search.** This shifts the brief's "customers must see the hex while picking" requirement: the named-color match is what Jeff actually orders against. Hex display in the picker becomes a UX nicety (eyeball matching), not a supplier-call necessity.

---

## What this means for Round 2

### Dimensions where the new info matters

1. **Fill region count.** Classic Arch's Design = Swirl (up to 4) or Layered (up to 8). C4's "2 regions matches the 2-color mental model" defense was sound for Swirl-style arches — but doesn't accommodate Layered-up-to-8. C2's "4 regions" matches Swirl perfectly but undershoots Layered. None of the field designed for the Layered up-to-8 case. **Round 2 question:** does your tool support BOTH Designs gracefully? Does the customer need to choose Swirl/Layered before coloring, or is the fill-region count fixed and one Design dominates?

2. **Per-product fill-region behavior.** Classic Arch has 2 + Design + LED. Classic Organic Arch has Add-ons but NO Design attribute (organic style is implicit). Classic Column has 0 design choices but a Topper. **The fill-region UX may need to vary per shape.** A one-size-fits-all "every shape has 2-3 regions" is an oversimplification.

3. **Color naming.** Use the actual 53 names. Generic "Coral" or "Champagne" misses Jeff's supplier reality — Reflex Champagne is a different SKU than Dusk Cream than Pastel Yellow. Surface real names in your mockup picker.

4. **Hex display.** The brief assumed customers need hex to match venue colors. **The catalog has no hex.** Contestants who emphasized hex-as-supplier-action (C2, C3, C4) need to reframe — hex is for the customer's eyeball matching only; Jeff orders against the color NAME. That changes the priority of hex in the picker UI.

5. **Sizes and toppers and add-ons.** Out of brief scope for the design tool, BUT they exist in the actual product. Contestants might consider:
   - Quietly mentioning the size/length question is part of Jeff's pitch ("Jeff will figure out the right size for your space"), keeping the tool focused on color/composition
   - Adding a single-line scale indicator ("My space is...") if it helps the customer feel grounded
   - Explicitly NOT modeling these — defensibly, they're conversation territory

6. **Organic vs. Classic.** The "Organic" subset has a different structural model (artistic clusters, no structured spirals/bands). **The design tool may need to communicate this difference to the customer, OR may need to treat Organic as a separate flow with palette-only fill (no per-region picking).** The naming convention "Classic Organic Arch" vs. "Classic Arch" is itself a product-line distinction the customer encounters at inquiry time.

### Dimensions where the new info CONFIRMS prior choices

- **Family-grouped picker** (C2, C3, C4 chose this) — confirmed by the catalog's natural family clustering (Reflex*, Dusk*, Pastel*).
- **Real color names** in the picker — every contestant mentioned hex display; the catalog confirms the NAMES are also load-bearing.
- **53 colors** — fits the brief's "50+" estimate. The picker scaling logic in every contestant's mockup is valid.
- **Shape-by-shape decisions, not configure-everything-at-once** — the catalog confirms each shape has different attributes; the tool's per-shape entry pattern (every contestant chose this) is structurally right.

---

## Round 2 directive

**You may use this as a perspective shift OR as background.** It doesn't replace your existing work. But it may shift how you handle:

- The Design attribute (Swirl vs. Layered) on Classic Arch
- The Organic-vs-Classic structural difference
- Color name surfacing (real names, not generic)
- Hex display priority (eyeball matching for customer, not supplier-call for Jeff — Jeff orders against names)

Bring the product-detail awareness into your Refine / Lean / Pivot decision in Round 2. If you choose Pivot specifically because of this product-detail context, that's a valid path — note it in `ROUND-2-CHOICE.md`.

---

*Surfaced by orchestrator 2026-04-29 between Round 1 reflective loops and Round 2 dispatch. GL directive: contestants need product-detail grounding for the Round 2 work to be informed.*
