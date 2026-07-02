D:2026-05-10 | Check:live catalog_data read-only extraction + ERPNext verifier rerun 2026-05-10 14:06 MDT | Confidence:high
# Ecommerce infrastructure readiness packet — Locally Twisted

## Executive read

ERPNext/Frappe can receive the Locally Twisted ecommerce meaning **if** the custom `locally_twisted` contract/runtime layer remains in charge around native Webshop.

The correct target is not “copy catalog_data” and not “native Webshop product rows only.” The target is:

> true variants for SKU/price identity + no-variant structured options for customer choices + backend-preserved cart/order intent + quote-first fallback + guarded checkout/payment + CRM/project fulfillment handoff.

## Current proof status

| Area | Status | Evidence |
|---|---|---|
| catalog_data backend/source witness | Present | `catalog_data-backend-architecture-and-checkout-logic-2026-05-10.md` |
| Lane E convergence | Present | `catalog_data-docs-agent-action-convergence-2026-05-10.md` |
| ERPNext readiness verifier | Passing now | `output/product-page-architecture-readiness-infrastructure-research-20260510.json` |
| Verifier failure diagnosis | Present | `product-page-architecture-readiness-failure-diagnosis-2026-05-10.md` |
| Payment success | Not claimed | catalog_data payment page observed only; no transaction submitted |
| Product purge/import/public launch | Still gated | Business/product approval + final launch checklist still required |

Latest parent verifier rerun:

```bash
python scripts/verify/product_page_architecture_readiness.py --report output/product-page-architecture-readiness-infrastructure-research-20260510.json
```

Result:

- Exit code `0`.
- `ok=true`.
- `technical_architecture_ok=true`.
- `import_reopen_ok=true`.
- `pass=14`, `blocked=0`, `deferred=1`.
- Deferred: finance/bank/payment integration remains backburnered.

## catalog_data logic we must preserve

### Product/variant logic

Classic Arch proves the core pattern:

- Product template id `57` has 4 real variants only.
- Variant axis: `Arch Size`.
- Size variant pricing:
  - 20ft: $260
  - 25ft: $325
  - 30ft: $390
  - 35ft: $455
- `latex colors`: 53 values, multi-select, no variants.
- `Design`: 2 image choices, no variants.
- `LED Lights`: 2 image choices, no variants; `Add LED Lights` adds $50.

Catalog-wide extraction confirms this is systemic:

- 128 saleable product templates checked.
- 58 published templates.
- 59 templates with attributes.
- 48 templates with no-variant attributes.
- 45 templates with multi-select attributes.
- 49 option-heavy products.

ERPNext build rule: do not explode color/design/lights/large customer choices into Item Variants. Store them as structured configuration.

### Cart/order-line logic

catalog_data stores selected meaning on sale order lines:

- No-variant selections are stored as `product_no_variant_attribute_value_ids`.
- Custom text values are stored as `product_custom_attribute_value_ids`.
- Display line text is generated from structured selections.
- Delivery is a separate order line with `is_delivery=true`.

ERPNext build rule: selected product meaning must survive product page → cart → quotation → sales order → invoice/project handoff as backend records, not just visible text.

### Quote-first logic

catalog_data adds a product inquiry form to product pages:

- Posts to CRM Lead.
- Carries product context.
- Captures contact, occasion, event date, vision/details, and optional inspiration photos.

ERPNext build rule: quote-first is not a fallback failure. It is a valid success path for custom work.

### Checkout/payment logic

catalog_data observed flow:

1. Cart
2. Address/delivery
3. Payment

Payment page:

- Stripe test provider visible.
- Route pattern `/shop/payment/transaction/<order_id>`.
- Landing `/shop/payment/validate`.
- No payment submitted in this audit.

ERPNext build rule: no “checkout works” claim without backend proof of cart/order/delivery/tax and, when tested, transaction state.

### Delivery logic

Live delivery choices include:

- Pickup (Free)
- Standard Delivery ($15)
- Park City Delivery ($50)
- Out-of-Area Quote ($35)
- A second live `Standard delivery` default-ish carrier at $0 that needs cleanup/mapping attention before launch.

ERPNext build rule: delivery services must map to explicit service items and avoid duplicate/confusing choices.

### Automation logic

Critical source guard:

```python
if order.website_id:
    continue
```

This keeps custom SO invoice/deposit automation from running on website-shop orders.

ERPNext build rule: direct ecommerce orders, quote/deposit invoices, and service automation must be separated by explicit guards.

## What is ready vs not ready

### Ready to use as build direction

- The architecture pattern.
- The Classic Arch product/variant/no-variant proof slice.
- The ERPNext receiving-layer requirement list.
- The verifier passing state as of 14:06 MDT.
- Lane E convergence as a source-backed artifact.

### Not ready / do not do yet

- Do not purge/reimport full catalog based only on this packet.
- Do not claim live checkout/payment success.
- Do not expose customer/admin checkout details in artifacts.
- Do not copy catalog_data code/schema directly.
- Do not launch publicly until final product, delivery, payment, security, and operator-review gates are checked.

## Immediate next engineering actions

1. Implement or verify ERPNext product option group model for no-variant choices:
   - multi color choices,
   - image/radio design choices,
   - LED/add-on price extras,
   - custom text fields.
2. Add/verify server-side canonical pricing for variant + options.
3. Add/verify line-level structured payload fields on Quotation Item, Sales Order Item, and Sales Invoice Item.
4. Add/verify quote-first product inquiry bridge into Lead/Opportunity.
5. Add/verify delivery service mapping and duplicate-carrier guard.
6. Add/verify checkout gate that refuses fake success when cart/order intent is missing.
7. Add/verify automation separation between website orders and quote/deposit service orders.
8. Preserve current verifier artifact and rerun before any import/public launch decision.

## Decision

Proceed with ERPNext/Frappe ecommerce infrastructure work using the catalog_data source witness as a behavioral map.

Do **not** proceed to destructive catalog operations or public payment launch until final gates pass with artifacts.
