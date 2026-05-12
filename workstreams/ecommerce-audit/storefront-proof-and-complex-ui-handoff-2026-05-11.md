D:2026-05-11 | Check:local rendered ERPNext/Frappe Webshop evidence | Confidence:[LOCAL-PROOF]
# Storefront Proof And Complex Product UI Handoff

Use this handoff for GPT-5.5/OpenClaw peers working on the Locally Twisted
Ready-to-Order storefront after the local V1 import proof. It captures the
front-end/storefront evidence only. Backend import, payment, Frappe Cloud, and
live Stripe gates remain separate.

## Current Proof State

- Ready-to-Order menu/search logic was corrected to follow backend executable
  product eligibility instead of blanket bouquet-only, cups, or high-variant
  exclusions. 2026-05-12 review closeout tightened this further: owner include
  codes are not a checkout bypass, and filtered backend-approved search links
  are asserted hidden instead of absent.
- Rendered Ready-to-Order/search proof passed for the priority products:
  Easter Balloon Cups, 7' Butterfly Column, 6' Graduation stands, and
  Graduation Grab n Go. Classic exclusions stayed out of quick links.
- Final post-import checkout proof passed for Easter Balloon Cups,
  7' Butterfly Column, Graduation Grab n Go, 6' Graduation stands, and
  Unicorn Bouquet.
- All-priced-page storefront audit rendered 53 published priced product routes:
  18 passed option selection, `data-item-code`, add-to-cart, cart line
  configuration, and checkout summary preservation; 35 stopped at the first
  rendered layer because they are currently `quote_first`.
- `quote_first` is a lane/setting flag. It is not proof that a product cannot
  ever be purchasable. It means the current storefront does not expose direct
  checkout controls for that product.
- Classic Arch is visible and priced at
  `/shop-items/arches/classic-arch`, but currently renders
  `complex_custom_product` / `quote_first`; downstream checkout is untested for
  that product until the lane and configuration contract are changed.

## Evidence Artifacts

These files are ignored runtime evidence and should be regenerated when fresh
proof is needed. They are useful for peer orientation and should not be deleted
as stale while this lane is active.

- `output/playwright/40cb0889-ready-menu.png`
- `output/playwright/40cb0889-search-balloon-cups.png`
- `output/playwright/post-import-checkout-proof.json`
- `output/playwright/10b8b2df-product-front-end-audit.json`
- `output/playwright/10b8b2df-search-balloon.png`
- `output/playwright/10b8b2df-ready-menu.png`
- `output/playwright/10b8b2df-classic-arch-route.png`
- `output/playwright/c849adb7-classic-arch-checkout-proof.json`
- `output/playwright/c849adb7-classic-arch-page.png`
- `output/playwright/0784b926-all-priced-product-checkout-proof.json`
- `output/playwright/0784b926-products/`

## Current Product-Level Boundary

The all-priced-page audit found 53 published priced routes.

Direct checkout passed for 18 pages:

- `6-graduation-stands`
- `7-butterfly-column`
- `easter-balloon-cups`
- `elsa-bouquet`
- `encanto-bouquet`
- `flamingo-bouquet`
- `football-bouquet`
- `graduation-grab-n-go`
- `holy-cow-bouquet`
- `mickey-mouse-bouquet`
- `minion-bouquet`
- `mothers-day-bouquet`
- `over-the-hill-bouquet`
- `paw-patrol-bouquet`
- `soccer-bouquet`
- `space-bouquet`
- `stitch-bouquet`
- `unicorn-bouquet`

The other 35 priced pages are currently quote-gated at the rendered storefront
layer. No `no price`, `no add control`, resolver, cart-preservation, or
checkout-preservation failures were observed among products that expose direct
checkout controls.

## If Quote-First Is Flipped To Checkout

Likely to pass with the existing UI, assuming backend variant records/prices
exist and the visible axes are truly required sale-unit axes:

- `6-color-rainbow-arch`
- `baby-table-decor`
- `basketball-arch`
- `easter-arch`
- `easter-balloon-arch-bunny-ear`
- `large-head-missionary`
- `mothers-day-front-yard-7-column`
- `pride-arch`
- `pride-progress-rainbow-balloon-arch`

Likely to technically resolve but be incomplete or wrong without new UI because
the current color drawer preserves only one color:

- `7-epic-column`
- `baby-shower-combination-photo-opt`
- `baby-shower-garland`
- `balloon-drop`
- `classic-arch`
- `classic-column`
- `classic-organic-balloon-garland`
- `classic-organic-columns`
- `classic-organic-for-easel`
- `halloween-arch`
- `large-garland`
- `large-organic-column`
- `logo-3-layered-bouquet`
- `number-balloon-columns`
- `organic-grab-n-go`
- `premium-organic-garland`
- `sleepy-baby-column`

Unsafe to flip until add-on or conditional pricing contracts are mapped:

- `bandage-get-well-bouquet-latex-free`
- `butterfly-get-well-bouquet-latex-free`
- `shooting-star-get-well-bouquet-latex-free`
- `birthday-deliveries`
- `classic-organic-arch`
- `pemium-organic-column`
- `premium-organic-arch`
- `marble-table-decor`
- `star-column`

## Reusable Existing Controls

Keep and extend these current product-page controls:

- Chips/radio controls for small required option sets.
- Select controls for medium/high-cardinality non-visual axes.
- Grouped color drawer for large color lists.
- Variant resolver pipeline:
  `get_next_attribute_and_values` -> exact match -> `data-item-code` ->
  backend price -> variant media -> structured cart configuration.
- Status live region and disabled add-to-cart states.
- Structured `LT_CART` configuration with `schema_version`,
  `website_item_code`, `item_code`, `selected_options`, `add_ons`, and
  `customizations`.

## UI Pieces Still Required

1. Product-page checkout contract per complex product:
   required axes, customization axes, confirmed add-ons, review-only add-ons,
   image sources, price sources, and cart summary fields.
2. Multi-slot color recipe builder:
   named color slots using the existing grouped swatch drawer. Classic Arch
   needs design-dependent limits: Swirl up to 4 colors, Layered up to 8 colors.
3. Palette picker:
   palette cards with swatches/labels for `Color Palette` axes, preserving the
   selected palette name and any selected color details.
4. Add-on contract UI:
   toggles, quantities, values, item codes, unit prices, and eligibility for
   approved add-ons only. `Add ons`, `Plush add ons`, `Orbz toppers`, and
   `Add Bouquet` stay blocked until mapped.
5. Conditional pricing panel:
   base price, required-option price, add-on rows, total, and fail-loud missing
   price states. LED Lights must stay blocked or priced; never sell an upgrade
   as free because a surcharge is missing.
6. Backend-driven image updates:
   use variant/media maps where available; otherwise keep the primary image and
   avoid implying visual parity that is not backed by data.
7. Cart, checkout, receipt, and ERPNext document summary parity:
   product name, resolved item code, required options, color recipe swatches and
   names, add-ons with quantities/unit price/total, and the same summary stored
   on downstream Sales Order/Sales Invoice lines.

## Proof Ladder

1. Preserve regression proof for the 18 currently passing direct-checkout pages.
2. Flip and prove the likely-pass simple-axis/no-add-on group on staging/local.
3. Add and prove multi-color recipe UI on a simpler complex product such as
   Baby Shower Garland or Balloon Drop.
4. Prove Classic Column for height plus large colors plus topper meaning.
5. Prove Birthday Deliveries for theme, Foil Number, and Add Bouquet mapping.
6. Prove Classic Arch last as the full stress case: size, design,
   design-dependent multi-color recipe, LED pricing, image behavior, cart,
   checkout, and downstream document summary.

## Remaining Front-End Work

- Decide category/browse/search rules for accepted quote-first products. The
  2026-05-11 storefront audit found accepted quote-first products have live
  routes and `/shop?q=` search hits but do not populate Ready-to-Order quick
  links. Keep `ready-to-order-nav-search-backend-gate-2026-05-12.md` as the
  nav/search guard while making that decision. If category browsing should show
  all accepted product pages, that
  requires a deliberate browse contract.
- Build complex-product UI components above instead of treating a lane flip as
  enough.
- Add a regression verifier that captures product-page selection, price/image
  update, cart configuration, checkout summary, and downstream ERPNext line
  fields for every product admitted to checkout.
- Keep final real catalog approval separate from local import/proof fixtures.
