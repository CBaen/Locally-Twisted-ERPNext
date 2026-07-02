# ERPNext Ecommerce Receiving Architecture Research Synthesis

Status: Codex-owned research synthesis, 2026-05-09.

Decision informed: how to build two product page types for Locally Twisted on ERPNext/Frappe v15 without silently flattening catalog_data product behavior.

This is not a rendered product-page review. It is not an catalog_data field import plan. It is the backend product architecture research needed before product pages are rebuilt.

## Research Question

What backend product contract must LT add around ERPNext/Webshop so two product-page types can preserve option meaning, prices, add-ons, media, cart payloads, checkout totals, Sales Order lines, invoice meaning, fulfillment/operator meaning, and fail-loud reporting?

## Evidence Lanes

### Official ERPNext/Frappe docs

- ERPNext Item Templates are not transactional. If an Item has variants, only the variant Items can be used in Sales Orders, Delivery Notes, invoices, and similar transactions. Source: https://docs.frappe.io/erpnext/item-variants.
- ERPNext Shopping Cart follows that same split: non-variant Items can be added directly, while variant templates require a configure step to choose a specific sellable variant. Source: https://docs.frappe.io/erpnext/shopping-cart.
- ERPNext Item Price is the selling/buying rate record. Sales transactions fetch rates from the selected price list. Source: https://docs.frappe.io/erpnext/item-price.
- ERPNext Selling Settings can enforce same-rate behavior across Sales Order, Delivery Note, and Sales Invoice, and can keep transaction price-list rate non-editable by default. Source: https://docs.frappe.io/erpnext/selling-settings.
- ERPNext Product Bundle is a sales-side bundle/packing-list mechanism with a virtual non-stock parent and child items. It is useful for fixed bundles, not a general answer for customer-configured custom decor. Source: https://docs.frappe.io/erpnext/product-bundle.
- Frappe customization supports Custom Fields, Property Setters, client/server scripts, custom DocPerms, and child tables. Child DocTypes are the right shape for many-to-one structured payloads that need to live on a parent document. Sources: https://docs.frappe.io/framework/v15/user/en/basics/doctypes/customize, https://docs.frappe.io/framework/v15/user/en/basics/doctypes/child-doctype, https://docs.frappe.io/framework/v15/user/en/basics/doctypes/fieldtypes.

### Official catalog_data docs as behavior witness

- catalog_data product variants combine template, attributes, and values; variant records carry SKU/barcode, inventory, price impact, and images. Source: https://www.catalog_data.com/documentation/18.0/applications/sales/sales/products_prices/products/variants.html.
- catalog_data attribute values can carry price extras and exclusions; attribute display types include pills, color, radio, select, image, and multi-checkbox in current docs. Source: https://www.catalog_data.com/documentation/master/applications/sales/sales/products_prices/products/variants.html.
- catalog_data optional, accessory, and alternative products are separate ecommerce behaviors shown at different points in the customer journey. Source: https://www.catalog_data.com/documentation/18.0/applications/websites/ecommerce/products/cross_upselling.html.

### LT live ERPNext ground truth

Live DB rechecked through bench console on 2026-05-09:

- Website Items: 53
- Items total: 10,672
- Active variant templates: 49
- Active variants: 10,227
- All variant records: 10,617
- Active non-variant root Items: 6
- Item Prices: 10,654
- Item Variant Attribute rows: 32,028
- Item Attributes: 26

Custom field reality from live ERPNext:

- `Website Item` has only `lt_brand_description` and `lt_product_details` for product-page copy.
- `Sales Order` has fulfillment fields: method, delivery zone, pickup location, requested date/window, fulfillment status.
- `Sales Order Item` has no LT custom fields.
- `Sales Invoice Item` has no LT custom fields.

Current cart/checkout path:

- `apps/locally_twisted/locally_twisted/api/cart.py` resolves a client item code into a server-priced sellable Item/variant, parent Website Item display fields, variant options, and checkout lane.
- `apps/locally_twisted/locally_twisted/www/checkout.py` reduces cart payload to `item_code`, `item_group`, `qty`, and `rate` Sales Order rows. Fulfillment goes onto the Sales Order header. Product configuration/add-on/customization meaning is not preserved as structured line data.
- `apps/locally_twisted/locally_twisted/payments/stripe_session.py` builds Stripe line items from Sales Order item names and rates. It preserves amount parity, not configuration semantics.

Current product contract starter:

- `apps/locally_twisted/locally_twisted/catalog_contract/models.py` defines a starter `ProductPageContract` with required axes, customization axes, add-ons, gallery, source variant count, resolver-price flag, and warnings.
- `catalog_contract/source_builder.py` separates color axes into customization, GL-confirmed add-ons into add-on contracts, and unknown axes into warnings.
- `catalog_contract/addon_rules.py` only treats `Add Foil Number` as confirmed. `Add ons`, `Plush add ons`, `Orbz toppers`, and `Add Bouquet` are still needs-review.
- `product_options.py` and `item_configure.html` are a frontend bridge around Webshop variant selection. The color drawer still maps one color to one SKU for price/cart lookup and explicitly says multi-color recipes must move out of SKU axes.

Source contract verifier results on 2026-05-09:

- `python scripts/verify/proof_product_contract.py` passed.
- `python scripts/verify/product_page_contract_source_audit.py` blocked source import.
- Source audit counts: 53 source products, 49 with alternate/gallery image evidence, 14 with confirmed add-on contracts, 0 variant products with resolver-backed prices in the source artifact, and 53 products with warnings/blockers.
- Warning buckets: 49 missing resolver prices, 49 unclassified gallery images, 25 color-axis customization blockers, 9 axes needing review.

Proof products:

- `unicorn-bouquet`: required axis `Bouquet Size`; add-on `foil_number`; source contract has two gallery images; still warns for missing resolver-backed source prices and gallery classification.
- `classic-arch`: required axes `Arch Size`, `Design`, and `LED Lights`; customization axis `latex colors`; 23 source gallery images; color drawer contract includes Reflex, Dusk, Pastels, Blues + Teals, Greens, Pinks + Purples, Neutrals, and Brights.

## Convergence

ERPNext's native transactional unit is too narrow for LT's two product-page types. It can sell a concrete Item/variant at a server price, but LT needs extra product meaning to survive beyond the UI.

catalog_data's richer product behavior should be treated as a behavioral witness, not a field schema to copy. Some concepts map cleanly to ERPNext native records. Others need LT-owned custom structure.

The current LT frontend can choose an ERPNext variant and add it to cart, but it does not have a backend contract for selected add-ons, multi-color recipes, dependencies, customer-entered configuration, or operator/invoice detail.

The hard backend gap is line-level preservation. Header fulfillment fields exist. Product page copy fields exist. Line-level product configuration fields do not.

## Product Page Types

### Type 1: Ready-To-Order Product Page

Purpose: fixed-price products where the customer can safely pay now.

Backend contract:

- One sellable ERPNext Item/variant must be resolved server-side.
- Required axes must map to ERPNext Item Variant Attributes or a deliberately approved custom selector that still resolves to a sellable line.
- Optional add-ons must be separate priced line semantics, not hidden required variant axes.
- Server pricing must calculate variant base price plus approved add-ons/modifiers before cart, checkout, Sales Order, and Stripe.
- The final line payload must preserve selected required axes, add-ons, quantities, and customer-facing summary on Sales Order Item and Sales Invoice Item.

Proof fit: bouquet family after resolver-backed size pricing and foil-number add-on architecture.

### Type 2: Custom / Quote-First Product Page

Purpose: custom decor where the customer is shaping a request and operator meaning matters more than immediate checkout.

Backend contract:

- Product configuration is an inquiry/quote payload first, not a paid SKU shortcut.
- Required design decisions, customization axes, dependencies, color recipes, customer notes, install context, and media inspiration must map to Lead/Quotation or a custom product-configuration child table.
- Some choices may still use ERPNext variants for base price/range, but the quote payload must preserve full customer intent.
- The page must expose quote-required states plainly and must not create false cartability when pricing, availability, or install requirements are unresolved.

Proof fit: Classic Arch with size/design/LED axes, high-cardinality latex colors as multi-select customization, and quote-safe handling for unresolved price/media/dependency gaps.

## Architecture Recommendation

Build an LT-owned Product Configuration Contract around ERPNext, not inside the product page template.

Minimum backend pieces:

- `lt_product_page_type` on `Website Item` or an LT Product Page Settings child/config record: `ready_to_order`, `quote_first`, `hybrid`, `needs_review`.
- `LT Product Option Axis` source/config model, or equivalent code-owned contract, to classify each axis as `required_variant`, `customization`, `optional_addon`, `backend_only`, or `needs_review`.
- `LT Product Add On` contract for key, label, eligibility, dependencies, unit price, tax class, quantity rules, and line behavior.
- Line-level custom fields on `Sales Order Item` and `Sales Invoice Item` for configuration summary and machine-readable configuration JSON, or a child table attached to Sales Order/Sales Invoice with parent row linkage.
- Server pricing resolver that accepts product, selected variant axes, add-ons, and modifiers, then returns a priced, validated sale/quote payload.
- Cart payload versioning so old localStorage carts fail loudly instead of silently dropping configuration.
- Quote payload bridge for custom pages so Classic Arch-style intent goes to Lead/Quotation with structured option records instead of `order_notes`.
- Import/readiness report that classifies every product as `checkout_ready`, `quote_ready`, `needs_review`, `blocked`, or `unverifiable`.

Do not rely on:

- Product group as a quote gate.
- Frontend JS as the owner of price or option truth.
- Product Bundle as the general add-on/customizer mechanism.
- catalog_data JSON-LD/base page price.
- Website Item copy fields as storage for executable product behavior.
- Sales Order header notes as the only place selected product meaning survives.

## Build Order

1. Add line-level preservation fields/child table and verifier.
2. Build server-side product configuration resolver for the two proof products only.
3. Add cart payload version + validation for configuration payloads.
4. Make checkout write the structured line configuration to Sales Order Item and copy it to invoice path.
5. Add source/readiness verifier gates for backend field existence, option reachability, add-on pricing, source price resolver coverage, media classification, cart payload, checkout totals, Sales Order/Invoice preservation, and quote payload preservation.
6. Only then update product page rendering to consume the backend contract.

## Confidence And Gaps

Confidence: high for the backend gap and implementation direction. ERPNext official docs, live DB metadata, local code, and proof verifiers all point to the same missing layer.

Gaps before build:

- Exact GL decision needed for whether `classic-arch` is quote-first only, hybrid, or checkoutable for selected sizes after price resolver repair.
- Add-on review needed for `Add ons`, `Plush add ons`, `Orbz toppers`, and `Add Bouquet`.
- Media classification needed before declaring gallery/variant image completeness.
- Full non-bouquet resolver price repair still needed before any product-family checkout claim.
- Need a deliberate choice between JSON fields on transaction rows versus a child table with row linkage. Child table is more reportable; JSON is faster but weaker for Desk/reporting.

## Next Action

Do not inspect rendered product pages yet. The next implementation slice should be a backend preservation proof:

1. Add the smallest Sales Order Item / Sales Invoice Item configuration preservation contract.
2. Prove `unicorn-bouquet` can carry Bouquet Size plus optional foil-number meaning through cart, checkout, Sales Order, invoice, and Stripe amount parity.
3. Prove `classic-arch` blocks checkout and creates/validates a structured quote payload until price/media/dependency gaps are resolved.
