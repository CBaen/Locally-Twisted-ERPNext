# School And Seasonal Color Preset Product Logic - 2026-05-18

## Purpose

Turn raw 50+ latex-color product axes into customer-usable preset choices
without pretending every high-complexity decor product belongs in direct
checkout.

This is now a local source + local ERPNext repair/proof. The local `frontend`
database was intentionally mutated through the idempotent repair script named
below. No Frappe Cloud update, staging/live checkout change, Stripe change,
DNS change, or public exposure change has been performed.

## Verified Current State

Checked against local ERPNext on 2026-05-18.

Original mismatch: many high-complexity products were stored as
`complex_custom_product` but still have `lt_commerce_lane=checkout`. They expose
raw `latex colors` axes instead of business-safe preset choices.

Current local result after repair:

- `graduation-grab-n-go`: 4 active college preset checkout variants, $85 each.
- `6-graduation-stands`: 8 active checkout variants, 2 designs x 4 college
  presets, $45 each.
- 19 high-cardinality school/corporate/seasonal/baby products moved to
  quote-request flow through the internal `quote_first` lane.
- Direct cart resolution for those quote-request products returns
  `quote_required`.
- `catalog_variant_contract.py` now expects 10,186 active customer-facing
  variants and passed against local ERPNext.

Important current runtime surface:

- Checkout line configuration is stored on Sales Order Item / Sales Invoice Item
  through `custom_lt_product_template_item`,
  `custom_lt_product_page_type`, `custom_lt_configuration_version`,
  `custom_lt_configuration_summary`, and `custom_lt_configuration_json`.
- Product-page quote requests preserve `selected_options`, `add_ons`,
  `customizations`, and `color_recipes` from Lead to draft Quotation and later
  Sales Order when accepted.
- Color choices must stay grouped as one recipe/preset. They must not split into
  detached single-color choices that lose meaning downstream.

## Working Rule

Products stay real products. The question is the customer flow:

- `checkout`: fixed enough for cart, payment, order, invoice, and receipt.
- `quote_request`: still a product, but the customer sends a request and the
  operator reviews price, sizing, color fit, delivery/install, and availability
  before invoice/payment.

Do not use school logos, mascots, trademarks, or official marks in product art
unless the business has permission. Color-inspired presets are the safe path.

## College Presets For Graduation Checkout

Use official brand colors as reference, but map the checkout choice to LT's
balloon color names. The hex values are reference/proof only, not raw customer
variant values.

| Preset key | Customer label | Official reference | LT balloon-color target |
|---|---|---|---|
| `weber_state` | Weber State Purple and White | Weber Wildcat Purple `#4B2682`, White | implemented local mapping: `Violet`, `White` |
| `university_of_utah` | University of Utah Red, Black, and White | Utah Red `#CC0000`, Black, White | implemented local mapping: `Red`, `black`, `White` |
| `byu` | BYU Blue and White | BYU Navy `#002E5D`, White | implemented local mapping: `Royal Blue`, `White` |
| `utah_state` | Utah State Aggie Blue and White | USU Aggie Blue `#0F2439`, White | implemented local mapping: `Blue Slate`, `White` |

No high-school presets for now. High schools and corporate colors route to a
quote request with an organization/name field and color notes.

## Checkout Products

These are direct checkout locally after implementation and proof:

| Product | Current shape | Target shape |
|---|---|---|
| `graduation-grab-n-go` | 51 raw `latex colors` variants | implemented: 4 checkout variants for college presets; custom school/company colors route to quote request |
| `6-graduation-stands` | 2 `Graduation stands` variants | implemented: 2 designs x 4 college presets = 8 checkout variants; custom school/company colors route to quote request |

Current checkout cascade:

1. Product page shows college preset chips, not 51 raw color buttons.
2. Cart line stores the preset label as
   `selected_options["College Color Preset"]` inside the versioned line
   configuration payload.
3. Cart API resolves the new preset variant and price from the server.
4. Browser proof confirmed Add to Cart stores the selected preset line config.

Remaining before release-readiness if GL wants explicit structured preset
fields instead of relying on the selected option label:

1. Enrich line config with `color_preset_key`, `color_preset_label`,
   `color_preset_category=college`, `balloon_color_values`, and
   `source_brand_color_refs`.
2. Prove the enriched payload through checkout, Sales Order Item, Sales
   Invoice Item, receipt helper, and customer email.

## Quote Request Products

These are not direct checkout while local UI/UX and operator flow are being
reviewed. The current implementation blocks cart checkout for them. Quote-page
preset/custom-color UI is still pending; do not claim that part is complete.

School/corporate decor products:

| Product | Current shape | Target customer flow |
|---|---|---|
| `classic-arch` | 816 variants: size, design, 51 colors, LED | quote request with school/corporate preset chips |
| `classic-column` | 1,836 variants: height, 51 colors, topper | quote request with school/corporate preset chips |
| `classic-organic-arch` | 612 variants: size, 51 colors, add-ons | quote request with school/corporate preset chips |
| `classic-organic-columns` | 306 variants: height, 51 colors | quote request with school/corporate preset chips |
| `classic-organic-balloon-garland` | 153 variants: length, 51 colors | quote request with school/corporate preset chips |
| `premium-organic-arch` | 408 variants: size, 51 colors, add-ons | quote request with school/corporate preset chips |
| `premium-organic-garland` | 153 variants: length, 51 colors | quote request with school/corporate preset chips |
| `pemium-organic-column` | 612 variants: height, 51 colors, add-ons | quote request with school/corporate preset chips |
| `number-balloon-columns` | 357 variants: 51 colors, number colors | quote request with school/corporate preset chips |
| `7-butterfly-column` | 51 raw colors | quote request with preset/custom color handoff |
| `7-epic-column` | 51 raw colors | quote request with preset/custom color handoff |
| `classic-organic-for-easel` | 51 raw colors | quote request with preset/custom color handoff |
| `logo-3-layered-bouquet` | 51 raw colors | quote request with preset/custom color handoff |

Seasonal and baby products:

| Product | Current shape | Target customer flow |
|---|---|---|
| `halloween-arch` | 204 variants: size, 51 colors | quote request with Halloween scheme presets |
| `baby-shower-garland` | 153 variants: length, 51 colors | quote request with baby scheme presets |
| `baby-shower-combination-photo-opt` | 51 raw colors | quote request with baby scheme presets |
| `sleepy-baby-column` | 51 raw colors | quote request with baby scheme presets |
| `baby-table-decor` | 2 variants: blue, pink | can remain checkout if pricing/fulfillment is fixed; consider adding bounded baby presets later |

Required quote cascade:

1. Product page shows preset choices plus custom color notes.
2. Selected preset enters product quote payload as:
   - `color_preset_key`
   - `color_preset_label`
   - `color_preset_category`
   - `balloon_color_values`
   - `custom_color_notes` when applicable
   - `organization_name` for school/corporate requests
3. Lead stores the preset in `custom_lt_product_quote_payload` and child quote
   rows.
4. Draft Quotation stores the same preset payload and readable summary.
5. Accepted quote copies the same payload to Sales Order Item.
6. Any later invoice/receipt copy preserves the preset label and color recipe.

## Seasonal Preset Candidates

These names are proposed for local review. They should be visually checked
against real balloon inventory before becoming checkout variants.

Halloween:

| Preset key | Customer label | LT balloon-color target |
|---|---|---|
| `classic_halloween` | Classic Halloween | `Orange`, `black` |
| `haunted_neutral` | Haunted Neutral | `black`, `White`, `Grey` or `Reflex Silver` |
| `purple_potion` | Purple Potion | `Violet`, `Orange`, `black` |
| `pumpkin_patch` | Pumpkin Patch | `Orange`, `Forest` or `Shamrock`, `Brown` |
| `custom_halloween` | Custom Halloween Colors | quote request only |

Baby:

| Preset key | Customer label | LT balloon-color target |
|---|---|---|
| `baby_boy` | Baby Boy | `Pastel Blue`, `White` |
| `baby_girl` | Baby Girl | `Pastel Pink`, `White` |
| `gender_reveal` | Gender Reveal | `Pastel Blue`, `Pastel Pink`, `White` |
| `neutral_baby` | Neutral Baby | `White`, `Blush`, `Latte` |
| `teddy_neutral` | Teddy Neutral | `Brown`, `Latte`, `Dusk Cream` |
| `custom_baby` | Custom Baby Shower Colors | quote request only |

## Implementation Plan

1. Add a source-owned color-preset registry. **Done.**
   - Keep official brand source refs and LT balloon-color mappings together.
   - Do not scatter hardcoded preset lists across templates, seed scripts, and
     verifiers.

2. Add a verifier before mutation. **Done.**
   - Fail if any direct-checkout product exposes a 50+ raw `latex colors` axis.
   - Prove graduation checkout products expose only approved college presets.
   - Prove quote-request products cannot enter checkout through cart API,
     direct checkout URL, stale localStorage, or malformed payload.
   - Prove preset payloads cascade to Lead/Quotation/Sales Order/Invoice fields.

3. Update source import / repair logic. **Done for first guarded slice.**
   - Convert graduation products from raw latex-color variants to college preset
     variants.
   - Move high-complexity school/corporate/seasonal/baby products to
     quote-request flow.
   - Preserve current source product identity and pricing evidence. Do not
     delete products as the way to make them safe.

4. Update product UI. **Partially done.**
   - Use preset chips/cards.
   - Add a custom colors quote handoff for schools/corporate customers.
   - Do not show 51 raw color options to customers on these products.

5. Run local proof. **Done for first guarded slice.**
   - DB/source verifier.
   - Product page browser proof.
   - Cart/checkout proof for graduation products.
   - Quote request proof for arches/columns/seasonal/baby products.
   - Sales Order / Sales Invoice / receipt cascade proof.

## Owner Review Needed Before Coding

- Pick/refine the real LT balloon-color match for Weber purple if `Violet` is
  not the correct production mapping.
- Pick/refine the real LT balloon-color match for BYU blue if `Royal Blue` is
  not the correct production mapping.
- Pick/refine the real LT balloon-color match for Utah State Aggie Blue if
  `Blue Slate` is not the correct production mapping.
- Confirm whether Utah Valley University or any other Utah college belongs in
  the first preset set.
- Confirm whether `baby-table-decor` stays checkout-only or joins the baby
  preset review.

## Stop Conditions

- Stop if a planned checkout product cannot prove price, image, cart, checkout,
  Sales Order, Sales Invoice, and receipt payload preservation locally.
- Stop if a quote-request product can still be forced into checkout.
- Stop if a preset uses logos, mascots, or official marks instead of color-only
  language.
- Stop before staging/live until GL approves the local UI/UX and logic.

## Implementation Receipts

Files:

- `apps/locally_twisted/locally_twisted/color_preset_rules.py`
- `apps/locally_twisted/locally_twisted/seed/repair_school_seasonal_color_presets.py`
- `apps/locally_twisted/locally_twisted/verify/school_seasonal_color_preset_contract.py`
- `scripts/verify/school_seasonal_color_preset_contract.py`
- `scripts/verify/catalog_variant_contract.py`
- `apps/locally_twisted/locally_twisted/catalog_contract/source_builder.py`
- `apps/locally_twisted/locally_twisted/hooks.py`
- `apps/locally_twisted/locally_twisted/fixtures/item_attribute.json`

Green proof:

- New verifier failed before repair on raw checkout color axes, graduation raw
  color variants, wrong classifications, and quote products still resolving to
  cart.
- `bench --site frontend execute locally_twisted.seed.repair_school_seasonal_color_presets.execute`
  applied the local repair.
- `python scripts/verify/school_seasonal_color_preset_contract.py` passed.
- `python scripts/verify/catalog_variant_contract.py` passed with 53 products,
  10,186 expected variants, and 10,186 live variants.
- Browser proof showed:
  - `/shop-items/grab-go/graduation-grab-n-go`: 4 college preset chips, no raw
    `latex colors`, Weber State selection enables `graduation-grab-n-go-WSU`
    at `$ 85.00`, and cart storage keeps the selected preset label.
  - `/shop-items/stands-easels/6-graduation-stands`: 2 design chips, 4 college
    preset chips, no raw `latex colors`, Congrats + Weber State enables
    `6-graduation-stands-CON-WSU` at `$ 45.00`.
  - `/shop-items/arches/classic-arch`: quote form renders, `Request a Quote`
    is present, `Add to Cart` is absent, and `data-commerce-lane=quote_first`.

Broad classification note:

- `python scripts/verify/website_item_classification_contract.py` still shows
  planned changes in dry-run because that older broad verifier covers more
  than this color-preset slice. Do not apply it as part of this slice without
  a separate review of its non-color product effects.
