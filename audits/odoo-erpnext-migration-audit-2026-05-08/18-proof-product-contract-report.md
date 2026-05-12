# Proof Product Contract Report

Read-only contract verification for GL-selected proof products.

## Unicorn Bouquet

- Template: Ready-to-order page (`simple_product`)
- Commerce lane: Online checkout (`checkout`)
- Required axes: Bouquet Size
- Add-ons: foil_number
- Gallery images in source contract: 2
- Warnings: 2

## Classic Arch

- Template: Custom quote page (`complex_custom_product`)
- Commerce lane: Quote request first (`quote_first`)
- Required axes: Arch Size, Design, LED Lights
- Customization axes: latex colors
- Gallery images in source contract: 23
- Dependency matrices: 1
- Warnings: 3

### Classic Arch latex color drawers

Selector type: `multi_select_drawer`

- Reflex: 8 colors
- Dusk: 5 colors
- Pastels: 6 colors
- Blues + Teals: 8 colors
- Greens: 6 colors
- Pinks + Purples: 7 colors
- Neutrals: 9 colors
- Brights: 4 colors

### Unicorn Bouquet foil-number add-on

- Item code: `ADDON-FOIL-NUMBER`
- Quantity bounds: `1` to `4`
- Requires value: `True`
- Receipt label: `Foil number add-on`

## Gate result

**PASS for proof-product contract shape.** Source import is still blocked by price/media review gates elsewhere.