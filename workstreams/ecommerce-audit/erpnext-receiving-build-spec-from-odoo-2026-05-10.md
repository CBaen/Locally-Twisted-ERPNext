D:2026-05-10 | Check:live Odoo backend/public extraction + ERPNext runtime inspection 2026-05-10 | Confidence:high
# ERPNext receiving build spec from Odoo backend logic

## Purpose

Turn the Odoo backend witness into concrete ERPNext/Frappe build requirements. This is the “stop reading, build the receiver” spec.

Odoo is not the implementation source. Odoo is the behavior witness.

## Architecture target

ERPNext/Frappe should use native Webshop only as the shell. The `locally_twisted` app owns the contract/runtime layer:

1. Product-page contract describes product type, commerce lane, variants, options, media, add-ons, warnings.
2. Runtime resolves true variants and safe checkout eligibility.
3. No-variant customer choices are preserved as structured payloads.
4. Quote-first bridge creates Lead/Quotation context for custom work.
5. Checkout bridge refuses fake success when intent/pricing/storage is incomplete.
6. Invoice/project handoff copies product meaning forward.

## Odoo witness → ERPNext object model

| Odoo concept | Observed behavior | ERPNext/Frappe receiving object |
|---|---|---|
| `product.template` | Public product page, media, base copy, variant axes | Website Item + Item template + LT Product Page Contract |
| `product.product` | Real SKU variant for true variant axes only | ERPNext Item Variant |
| Variant attribute line, `create_variant=always` | Size/topper/add-on axes that affect SKU matrix | Item Variant Attribute + resolver |
| No-variant attribute line | 53 colors, design, LED, foil numbers, custom choices | LT option group / runtime JSON payload / child table if promoted |
| `product_no_variant_attribute_value_ids` | Backend order-line preservation of selected options | custom LT configuration fields on Sales Order Item / Quotation Item / Sales Invoice Item |
| `product_custom_attribute_value_ids` | Backend preservation of custom text | custom LT payload field, redaction-safe summary, quote-first for unpriced custom text |
| Product inquiry form → `crm.lead` | Quote-first lane with event/product context | Lead + LT product quote payload + draft Quotation bridge |
| Delivery carrier | Delivery as separate service line | ERPNext Shipping Rule / service Item / delivery line guard |
| Payment provider route | Payment only after cart/order/delivery/tax | Payment Request / payment integration behind final gate |
| Sale-order automation guard | `if order.website_id: continue` | explicit separation of website checkout vs quote/deposit/service invoicing |
| CRM/task/calendar automations | Fulfillment context after confirmation | Opportunity/Project/Task/Event handoff fields and automation |

## Existing ERPNext runtime already aligned

Current code inspected:

- `apps/locally_twisted/locally_twisted/catalog_contract/models.py`
- `apps/locally_twisted/locally_twisted/product_page_runtime.py`
- `apps/locally_twisted/locally_twisted/product_quote_runtime.py`

Good signs:

- Product-page contract already has:
  - `commerce_lane`,
  - `product_page_type`,
  - required/customization axes,
  - add-ons,
  - dependency matrices,
  - gallery/media contracts.
- Runtime already uses `CONFIG_VERSION = lt-product-config-v1`.
- Runtime already writes line payload fields:
  - `custom_lt_product_template_item`,
  - `custom_lt_product_page_type`,
  - `custom_lt_configuration_version`,
  - `custom_lt_configuration_summary`,
  - `custom_lt_configuration_json`.
- Runtime already blocks quote-first products from paid checkout.
- Runtime already caps configuration payload size.
- Runtime already copies Sales Order Item configuration to Sales Invoice Item.
- Quote runtime already creates draft Quotation from Lead and preserves payload.

## Gaps / build checks forced by Odoo evidence

### 1. Catalog-wide no-variant options

Odoo has 48 templates with no-variant attributes and 45 with multi-select attributes. This is not a corner case.

Build requirement:

- Import/build contract must capture no-variant option groups separately from ERPNext Item Variant attributes.
- Runtime payload must support:
  - multi-select color values,
  - image/radio design values,
  - LED/no-LED values,
  - foil-number multi choices,
  - custom text fields.

Gate:

- A verifier must prove a 53-color product has small variant count and large option-group count.

### 2. Variant resolver

Odoo true variants are small and intentional.

Build requirement:

- Variant resolver should resolve only `create_variant=always` axes into item code.
- No-variant selections must never be used to create or require Item Variants.

Gate:

- Classic Arch resolves 20/25/30/35ft to four ERPNext variants or equivalent priced choices, while 53 colors do not change item identity.

### 3. Option pricing

Odoo can price no-variant add-ons, e.g. LED +$50.

Build requirement:

- Option payload must support price extras and canonical server-side pricing.
- Paid no-variant add-ons must either map to service/add-on Item rows or be blocked as quote-first until priced.

Gate:

- LED +$50 either becomes a priced line/add-on or page routes quote-first; it must not silently become free.

### 4. Custom text

Odoo stores custom text separately from enumerated choices.

Build requirement:

- Custom text is redaction-sensitive.
- Direct paid checkout may reject customizations until storage/pricing/fulfillment is approved.
- Quote-first can carry custom text into Lead/Quotation payload.

Gate:

- Custom text appears in backend payload/summary redacted where appropriate, and does not leak into logs/artifacts.

### 5. Cart/order-line backend proof

Odoo proves line payload exists in backend, not only DOM.

Build requirement:

- ERPNext Sales Order Item/Quotation Item/Sales Invoice Item must store the configuration JSON and customer-safe summary.

Gate:

- Verifier creates or inspects a test line and confirms all LT line fields are present and copied forward.

### 6. Quote-first path

Odoo product inquiry creates CRM Lead with product/event context.

Build requirement:

- Quote-first form captures product code, selected options, event date/type/details, and optional upload references.
- Draft Quotation bridge must preserve original payload.

Gate:

- Lead → draft Quotation retains product-page payload and does not submit/email/request payment automatically.

### 7. Delivery mapping

Odoo has duplicate-ish delivery choices: LT-defined Standard Delivery plus a default/free Standard delivery.

Build requirement:

- ERPNext delivery options must have a single approved set.
- Delivery options map to service items/rules.
- Out-of-area/quote delivery must be allowed as manual review, not fake certainty.

Gate:

- Checkout page shows only approved delivery choices for the test region/mode.

### 8. Payment boundary

Odoo payment form contains final transaction route and access token only at `/shop/payment`.

Build requirement:

- Payment intent/transaction should not be created before cart/order/delivery/tax proof.
- Payment tokens/access tokens must never be written into artifacts/logs.

Gate:

- No “checkout works” claim without transaction/backend proof from a deliberate payment test.

### 9. Automation guard

Odoo skips website orders in custom SO invoicing automation.

Build requirement:

- ERPNext automations must distinguish:
  - website direct checkout,
  - quote-first draft quote,
  - deposit/manual review,
  - internal service order.

Gate:

- Website order does not trigger quote/deposit duplicate invoice automation.

## Immediate coding order

1. Verify/extend DocType custom fields for line payload on Quotation Item, Sales Order Item, Sales Invoice Item.
2. Verify/extend product-page contract builder to carry no-variant option groups from source contracts.
3. Add a product option resolver that separates:
   - variant axes,
   - no-variant option axes,
   - custom text axes,
   - priced add-ons.
4. Extend `sales_order_line_configuration_fields` to preserve approved no-variant selections when checkout is allowed.
5. Keep unapproved custom/priced options quote-first with customer-safe error text.
6. Add verifier fixtures for Classic Arch pattern:
   - 4 variant choices,
   - 53 no-variant colors,
   - LED +$50 behavior,
   - quote-first fallback for custom text.
7. Add checkout verifier for delivery/tax/payment boundary without submitting payment.

## Non-negotiables

- No full catalog purge/reimport until this receiver passes.
- No public payment launch until payment is deliberately tested and recorded.
- No logs/artifacts containing live checkout PII, access tokens, or Stripe tokens.
- No color explosion into ERPNext Item Variants.

## Bottom line

ERPNext already has the bones of the receiver. The Odoo witness tells us what must be generalized and verified: no-variant option preservation, line-level payload proof, checkout boundary proof, and quote-first as a valid success lane.
