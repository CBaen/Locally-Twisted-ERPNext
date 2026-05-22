# Locally Twisted Balloon Color Addendum

**Date:** 2026-05-22
**Applies to:** product drawers, color-chart work, generated shop/category hero briefs, customer-facing color matching, and any design asset that represents LT balloon colors.

This addendum belongs to the main style guide. It exists because balloon colors are product truth, not decorative website colors.

## Authority Order

1. **Owner/Odoo swatch image and exact source color name.** This is the authority for generated images and customer-facing balloon matching.
2. **Supplier-style balloon color naming.** Names such as `Reflex Champagne`, `Dusk Green Tea`, and `Pastel Melon` must be passed to image prompts in text. Do not brief only with hex.
3. **Best web-match hex.** Hex is a CSS/customer approximation sampled from the local Odoo swatch image. It helps businesses match closely on screens and documents, but it is not the balloon authority.

External vendor context: Sempertex's public product pages use the same kind of texture/color naming, including [Reflex Champagne](https://sempertex.com/en/products/globo-para-fiesta-latex-redondo-reflex-champana), and its color articles name lines such as [Dusk Green Tea](https://sempertex.com/en/blogs/enterate/verde-te-y-verde-aurora). The LT source of truth remains the local Odoo export and owner swatch map.

## Verified Source

Source files:

- `_resources/odoo-live/catalog.json`
- `apps/locally_twisted/locally_twisted/catalog_contract/odoo_color_swatch_map.json`
- `apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/`

Verification command:

```powershell
python scripts\verify\odoo_color_swatch_contract.py
```

Current verified result:

- `latex colors` drawer exposes 53 owner/Odoo options.
- 51 distinct source swatch images are used for those 53 options.
- `Blue Slate` / `Blue slate` share one source swatch.
- `Smoke Grey` / `Smoke grey` share one source swatch.
- The product drawer groups the colors into 8 drawers: Reflex, Dusk, Pastels, Blues + Teals, Greens, Pinks + Purples, Neutrals, and Brights.

## Generated Image Rule

When generating category hero images, the prompt must include:

- the category shape, for example balloon columns, balloon arch, balloon bouquet, table decor, drop, easel/stand, or delivery arrangement;
- the relevant balloon color names from this addendum;
- the owner/Odoo swatch image references or contact sheet when the generation workflow supports image references;
- the target hero ratio and breakpoint crop, not a generic square or portrait composition.

Do not prompt only with hex values. Do not let the model invent unnamed colors. If the result does not visually match the source swatches, regenerate or reject it.

## Color Catalog

### Reflex

| Swatch | Source balloon color name | Web-match hex | Notes |
|---|---|---:|---|
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/210efeaea3e3d166d68caadf.jpg" alt="Reflex Champagne swatch" width="42"> | Reflex Champagne | `#B19F94` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/71873000d99dae895e82d356.jpg" alt="Reflex Truffle swatch" width="42"> | Reflex Truffle | `#7A615F` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/e02310ebb488aebdccb808af.jpg" alt="Reflex Silver swatch" width="42"> | Reflex Silver | `#9A9D9C` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/7e54731a8b01a8eaf9c2a08d.jpg" alt="Reflex Gold swatch" width="42"> | Reflex Gold | `#AB8B69` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/bf03351f73dbba94b8df9f65.jpg" alt="Reflex Blue swatch" width="42"> | Reflex Blue | `#437A95` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/fd3f6a11f867198c21b2ca8b.jpg" alt="Reflex green swatch" width="42"> | Reflex green | `#519589` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/18710d8a8683ed3401a7fc1e.jpg" alt="Reflex Violet swatch" width="42"> | Reflex Violet | `#796997` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/4826c93a9a2513757ca0abfe.jpg" alt="Reflex Red swatch" width="42"> | Reflex Red | `#D14C3C` |  |

### Dusk

| Swatch | Source balloon color name | Web-match hex | Notes |
|---|---|---:|---|
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/1230d7d984fce9f7ad2ad35d.jpg" alt="Dusk Cream swatch" width="42"> | Dusk Cream | `#C5C5B9` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/1121172628058b91214321ef.jpg" alt="Dusk Green Tea swatch" width="42"> | Dusk Green Tea | `#A7D2BC` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/20d983805c3c14d7a05da7fc.jpg" alt="Dusk Blue swatch" width="42"> | Dusk Blue | `#80A0AB` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/694c0e2f5a3fc4a5d72ab780.jpg" alt="Dusk Lilac swatch" width="42"> | Dusk Lilac | `#B795B4` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/cc5d0a79cfc68c27617389ae.jpg" alt="Dusk Rose swatch" width="42"> | Dusk Rose | `#D5ABC4` |  |

### Pastels

| Swatch | Source balloon color name | Web-match hex | Notes |
|---|---|---:|---|
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/0f5722005da4219177661054.jpg" alt="Pastel Pink swatch" width="42"> | Pastel Pink | `#F5DFE6` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/9903767634d3d8221edb3080.jpg" alt="Pastel Blue swatch" width="42"> | Pastel Blue | `#AADAF2` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/36684c4a081dee9b31a0eddb.jpg" alt="Pastel Green swatch" width="42"> | Pastel Green | `#C7E6DE` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/d69a0a99a3eaa6c6ebc6520c.jpg" alt="Pastel Purple swatch" width="42"> | Pastel Purple | `#D5CFE4` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/79bc7787311df5788772380a.jpg" alt="Pastel Yellow swatch" width="42"> | Pastel Yellow | `#F9F5CF` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/7931e53c1d668fceec2b03f7.jpg" alt="Pastel Melon swatch" width="42"> | Pastel Melon | `#F9C6BF` |  |

### Blues + Teals

| Swatch | Source balloon color name | Web-match hex | Notes |
|---|---|---:|---|
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/fa50cb9a638ed786b81201d8.jpg" alt="Teal swatch" width="42"> | Teal | `#50C3C0` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/4b7f304dd53f43516a64084a.jpg" alt="Blue Slate swatch" width="42"> | Blue Slate | `#98B8C8` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/b757f49f214861d6021f13a8.jpg" alt="LT Blue swatch" width="42"> | LT Blue | `#2AC7F1` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/9ce7912f199303f4e7f88388.jpg" alt="Periwinkle swatch" width="42"> | Periwinkle | `#6E75B6` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/5a46d52a86d65ff75a00c947.jpg" alt="Royal Blue swatch" width="42"> | Royal Blue | `#1467AB` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/454ffb3f4c39bd6ae9ccde49.jpg" alt="Robin's Egg swatch" width="42"> | Robin's Egg | `#73C6C5` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/829f5c79a6c57914294b1ca5.jpg" alt="Deep Teal swatch" width="42"> | Deep Teal | `#176078` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/4b7f304dd53f43516a64084a.jpg" alt="Blue slate swatch" width="42"> | Blue slate | `#98B8C8` | Source duplicate of `Blue Slate`; same swatch. |

### Greens

| Swatch | Source balloon color name | Web-match hex | Notes |
|---|---|---:|---|
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/172f82db46a9d33a06bb4b1c.jpg" alt="eucalyptus swatch" width="42"> | eucalyptus | `#99AC89` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/73c5676dec11c780eb6fea4d.jpg" alt="Forest swatch" width="42"> | Forest | `#178A5E` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/c2676852587c2365312d585e.jpg" alt="Shamrock swatch" width="42"> | Shamrock | `#29AE59` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/c403420103345214b45ade51.jpg" alt="Wintergreen swatch" width="42"> | Wintergreen | `#52BF99` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/c9a6d7ca5845a1b1c9c2ea37.jpg" alt="Lime swatch" width="42"> | Lime | `#9BCB73` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/f4aeb8fbf180108d2d644959.jpg" alt="Empowermint swatch" width="42"> | Empowermint | `#BAD0C3` |  |

### Pinks + Purples

| Swatch | Source balloon color name | Web-match hex | Notes |
|---|---|---:|---|
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/53123e7b87bd099fe30ecb26.jpg" alt="raspberry swatch" width="42"> | raspberry | `#EE4872` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/c236c8fa5a11dbd0e4463970.jpg" alt="fuchsia swatch" width="42"> | fuchsia | `#E572AA` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/707c6454a57c11edfed9c877.jpg" alt="bubble Gum swatch" width="42"> | bubble Gum | `#F6B2D2` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/12d28f09294e08822f0f375c.jpg" alt="Violet swatch" width="42"> | Violet | `#5D3B8B` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/d01f196d81d73dcd1874d520.jpg" alt="Orchid swatch" width="42"> | Orchid | `#A9348F` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/fea956089d95115d721776fb.jpg" alt="Lilac swatch" width="42"> | Lilac | `#AB98C9` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/8512c6fd4a9d1b914c07319a.jpg" alt="Blush swatch" width="42"> | Blush | `#EFD1B4` |  |

### Neutrals

| Swatch | Source balloon color name | Web-match hex | Notes |
|---|---|---:|---|
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/851d059aee03853bbf521a8c.jpg" alt="Smoke Grey swatch" width="42"> | Smoke Grey | `#929397` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/1024fc160b381431d09c0da8.jpg" alt="White swatch" width="42"> | White | `#DBE9EF` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/7fc429aa5afe3b74a4c51a28.jpg" alt="black swatch" width="42"> | black | `#2F2F2F` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/1f041741ee1363bcbcd54ac2.jpg" alt="Chocolate swatch" width="42"> | Chocolate | `#47312E` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/591dbbd27a22d4ee80c2cb14.jpg" alt="Brown swatch" width="42"> | Brown | `#916749` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/521b367477f1f83684c7e2b7.jpg" alt="Latte swatch" width="42"> | Latte | `#C8A26A` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/db8109d9ff5e896c8fa4d11c.jpg" alt="Grey swatch" width="42"> | Grey | `#B1B3B9` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/e069683e7e69049799e7ef06.jpg" alt="Clear swatch" width="42"> | Clear | `#ECECEC` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/851d059aee03853bbf521a8c.jpg" alt="Smoke grey swatch" width="42"> | Smoke grey | `#929397` | Source duplicate of `Smoke Grey`; same swatch. |

### Brights

| Swatch | Source balloon color name | Web-match hex | Notes |
|---|---|---:|---|
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/51bab5d180e631e3e80b80ff.jpg" alt="Red swatch" width="42"> | Red | `#EC373E` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/9b10496ff72ee3e9d3b0f3e8.jpg" alt="Orange swatch" width="42"> | Orange | `#F27C3A` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/650d46d274d5d233f4c68bad.jpg" alt="yellow swatch" width="42"> | yellow | `#FAE348` |  |
| <img src="../apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/0a7947218a72d95979d0296a.jpg" alt="Honey swatch" width="42"> | Honey | `#F2C72E` |  |
