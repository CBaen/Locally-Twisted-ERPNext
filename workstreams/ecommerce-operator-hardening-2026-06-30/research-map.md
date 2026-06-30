# Ecommerce Research Map

Date: 2026-06-30

Status: active expedition map.

## Research Question

How should LT model products, options, variants, prices, media, add-ons, and publishing so a non-developer backend user can run the ecommerce shop without variant explosion or developer-only projection work?

## Evidence Lanes

### Lane 1 - LT Ground Truth

Use repo/source/live evidence to map what LT actually does.

Primary roots:

- `workstreams/ecommerce-operator-hardening-2026-06-30/`
- `workstreams/ecommerce-audit/`
- `research/expedition-ecommerce-platform-fit/`
- `research/expedition-erpnext-ecommerce-receiving-architecture/`
- `research/owner-product-operations-break-lab/`
- `capabilities/recipes/erpnext-ecommerce-receiving-architecture.md`
- `capabilities/recipes/erpnext-product-blueprint-authoring.md`
- `capabilities/recipes/erpnext-catalog-variant-price-parity.md`

Key local conclusions:

- Product Setup is the owner-facing product-authoring path, but not yet complete live publishing.
- Server-side Item Price is checkout authority, but it can faithfully propagate wrong source price data.
- Product Setup already distinguishes SKU-defining selections, configuration-only groups, add-ons, measurements/uploads, and review-only payloads.
- Media has several authorities and needs one owner workflow for roles.
- Cart/checkout/document/payment propagation exists but requires upstream authority correctness.

### Lane 2 - Prior ERP Research

Use as architecture research only. Do not copy code, field names, paths, or product names into LT implementation.

Local pointers found:

- `/home/guidingl/projects/Built_by_Cameron/retro-[prior-ERP]-2026-04-26/`
- `workstreams/ecommerce-audit/legacy-backend-architecture-and-checkout-logic-2026-05-10.md`
- `research/expedition-ecommerce-platform-fit/synthesis.md`

Useful architecture lessons:

- True variants are sellable units.
- Multi-color/customization choices can be selectable without creating variants.
- Option payloads must survive cart/order/invoice.
- Attribute display type, variant-creation behavior, image option display, and price extras are owner-facing concepts worth translating.
- The backend UX matters: owner can create product, edit product, set price, upload media, choose main image, set option images, and publish without developer intervention.

Known gap:

- The external-drive docs and live prior ERP backend access are not fully mapped from this machine yet. Shallow search found the retro folder, but not a complete external-drive source tree.

### Lane 3 - Official / Primary External Ecommerce Sources

Use only official docs or primary repos for current-world comparison.

Current source pointers:

- Prior ERP variant docs: official vendor documentation, URL intentionally omitted from tracked LT docs because the platform name is restricted.
- Saleor product configuration docs: https://docs.saleor.io/developer/products/configuration
- commercetools product modeling docs: https://docs.commercetools.com/learning-model-your-product-catalog/product-modeling/products
- Medusa Admin variant/media docs: https://docs.medusajs.com/user-guide/products/variants

Extracted lessons:

- Variant creation modes can distinguish instant full combinations, dynamic creation, and no automatic variant creation.
- Variant-selection attributes should be explicit, not inferred.
- Product variants represent distinct SKUs/sellable goods, and some platforms warn against too many variants per product.
- Variant media is an expected admin feature: choose images for a variant from product media, make thumbnails, and show selected variant image to customers.
- Owner/admin bulk editing for variant price, stock, and media is a normal ecommerce expectation.

### Lane 4 - Future Research Targets

Research next, using official docs or primary repos only:

- Vendure product variants, options, facets, asset assignment, channel publishing, and custom fields.
- Spree product option types, variants, prices, images, stock, and availability states.
- Shopify product options/variants, combined listings, high-variant storefront guidance, media, and publishing/channel behavior.
- BigCommerce modifiers vs variants, option sets, variant images, price adjusters, and catalog publishing.
- WooCommerce variable products, variations, defaults, images, prices, stock, and bulk edit UX.

## Research Deliverables

- `external-source-notes.md`: official-source summaries with links and no copied implementation.
- `owner-backend-ux-patterns.md`: concrete admin UX behaviors to adapt.
- `variant-option-taxonomy.md`: LT-specific taxonomy for SKU-defining variants, configuration-only groups, colors, add-ons, quote context, and unsupported fields.
- `media-behavior-patterns.md`: main image, gallery, selected variant image, option image, cart/payment/receipt image rules.
- `price-publishing-patterns.md`: price edit, projection, approval, channel/list, add-on, and proof patterns.

## Immediate Research Tasks

1. Locate complete prior ERP external-drive docs/source tree.
2. Capture screenshots or notes of the prior backend product editing workflow if access is still available and credentials are provided by the user.
3. Map owner workflows from official ecommerce docs into LT Product Setup requirements.
4. Convert each accepted lesson into one Significant Change Register entry or acceptance test.
