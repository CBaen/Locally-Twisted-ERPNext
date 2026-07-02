D:2026-05-10 | Check:live catalog_data read-only extraction + local catalog_data source + ERPNext verifier 2026-05-10 | Confidence:high
# Lane E — catalog_data / docs / agent-action convergence

## Status

Recovered parent-created Lane E artifact. This replaces the previous missing `[NO EVIDENCE]` lane with directly verified sources and live read-only catalog_data observations.

This is not permission to copy catalog_data code. catalog_data is the source witness for business behavior; ERPNext/Frappe receives the behavior through native DocTypes, custom fields, services, templates, and verifiers.

## Inputs checked

- Live catalog_data backend/public read-only witness:
  - `workstreams/ecommerce-audit/catalog_data-backend-architecture-and-checkout-logic-2026-05-10.md`
- Local catalog_data addon source:
  - `/home/guidingl/projects/external-catalog-data/addons/locally_twisted/__manifest__.py`
  - `models/product_template.py`
  - `models/crm_lead.py`
  - `models/project_task.py`
  - `views/website_sale_templates.xml`
  - `views/product_views.xml`
  - `data/automation_data.xml`
  - `data/delivery_data.xml`
  - `data/ir_config_parameter.xml`
  - `data/ir_asset.xml`
  - `static/src/js/payment_post_processing.js`
  - `controllers/main.py`
- Existing infrastructure artifacts:
  - `ecommerce-infrastructure-doc-map-and-synthesis-2026-05-10.md`
  - `ecommerce-infrastructure-plan-v2-2026-05-10.md`
  - `ecommerce-infrastructure-research-synthesis-2026-05-10.md`
  - `erpnext-receiving-parity-matrix-2026-05-10.md`
  - `native-frappe-product-template-architecture-2026-05-10.md`
  - `cart-checkout-intent-preservation-audit-2026-05-10.md`
- Fresh verifier:
  - `python scripts/verify/product_page_architecture_readiness.py --report output/product-page-architecture-readiness-infrastructure-research-20260510.json`
  - latest parent rerun: PASS, 14 pass / 0 blocked / 1 deferred.

## Convergence decision

The evidence converges on one architecture:

> ERPNext/Frappe should not recreate catalog_data's exact backend. It should recreate the business invariants: small true variant axes, structured no-variant customer options, line-level cart/order intent preservation, quote-first escape hatches, guarded checkout/payment boundaries, and CRM/project fulfillment handoff.

Native ERPNext Webshop alone is not enough for Locally Twisted's meaning. The `locally_twisted` custom app must remain the contract/runtime layer around Webshop.

## Convergence matrix

| catalog_data behavior witnessed | Source proof | ERPNext/Frappe receiving action | Gate |
|---|---|---|---|
| Classic Arch has only 4 real variants despite 53 colors. | Live product template id 57; variants 91-94; attribute line 115 has 53 no-variant color PTAVs. | Use ERPNext Item Variants only for SKU/price identity. Store colors in product option/configuration tables. | A 50+ color product must not create 50+ SKU variants. |
| Size changes variant and price. | Arch Size PTAVs 201-204 map to variants 91-94; extras $0/$65/$130/$195. | Variant selection drives item identity and canonical price. | Product page and backend item resolution agree. |
| LED lights is a no-variant add-on with price extra. | LED PTAV 237 `Add LED Lights`, price extra $50, no variant ids. | Add-ons/options need their own pricing service and line payload. | Cart line total includes option extras and records source option id. |
| Design is no-variant image choice. | PTAVs 234/235, display image, no variants. | Product option group supports image/radio choices independent of SKU. | Selected design survives cart/quote/order. |
| Product page contains quote-first inquiry form. | `website_sale_templates.xml` posts `/website/form/` to `crm.lead`, with product name, contact, occasion, event date, description, upload. | Product pages need a quote/request path separate from direct checkout. | Lead/Opportunity created with product context and event fields; no fake checkout success. |
| Current cart stores no-variant colors and custom text on sale order line. | Live draft order read: `product_no_variant_attribute_value_ids` and `product_custom_attribute_value_ids`; line name includes colors and custom text. | Cart/quotation/order item must store structured option rows and generated display copy. | Backend proof required before checkout claim. |
| Checkout has delivery-service lines and tax/payment steps. | Cart/checkout/payment pages + delivery carrier records. | Delivery choices map to service items and must be persisted distinctly from product lines. | Delivery/tax proof before payment intent. |
| Payment page creates transaction only at final step. | Payment form route `/shop/payment/transaction/<order_id>`, landing `/shop/payment/validate`, Stripe test provider. | ERPNext payment intent should be last-mile after cart/order validity. | No payment-success claim without transaction/backend proof. |
| SO invoice automation skips website orders. | `automation_data.xml`: `if order.website_id: continue`. | Direct webshop checkout and service/deposit invoice automation need separate guards. | No duplicate invoice/deposit from website order. |
| CRM/task are fulfillment backbone. | `crm_lead.py`, `project_task.py`, active automations. | Product/order capture must feed CRM, task/event, crew/internal fields. | Fulfillment handoff includes event/location/setup/crew context. |
| Public route hardening exists. | `controllers/main.py` redirects `/website/info`, profile pages, `/terms`; slides auth=user. | ERPNext launch checklist must include public-route/security negative space. | Public routes audited before go-live. |
| Cart summary is hardened against deposit/non-product lines. | `lt_cart_summary_fix` guards missing `product_template_id`. | ERPNext cart/order UI must tolerate product, service, delivery, deposit, section, and quote lines. | No crash on non-product checkout/order lines. |

## Agent-action correction

Earlier child-agent lane completion without a durable artifact is not acceptable evidence. The parent action now is:

1. Directly inspect live catalog_data backend/public read-only.
2. Read local catalog_data source files.
3. Write durable source-witness artifact.
4. Re-run ERPNext readiness verifier directly.
5. Converge the decision in this Lane E artifact.

That closes the process hole: no artifact, no evidence.

## Current verifier state

The prior `[PRODUCT PAGE ARCHITECTURE READINESS] FAIL - bench execute failed` no longer reproduces.

Parent rerun result:

- `ok=true`
- `technical_architecture_ok=true`
- `import_reopen_ok=true`
- `summary.pass=14`
- `summary.blocked=0`
- `summary.deferred=1`

The remaining deferred item is finance/bank/payment integration, explicitly backburnered. This does not prove live payment success and does not authorize product purge/import/public launch by itself.

## Build instruction from convergence

Implement/review ERPNext ecommerce as a receiving ecosystem, not as product-row migration:

1. Product contract layer: source-backed item, variant axis, option groups, media, copy.
2. Product configurator runtime: variant resolution + no-variant option payload + canonical pricing.
3. Cart intent layer: structured child rows for selections/custom values; generated display copy.
4. Quote-first bridge: product-context lead/opportunity + event fields + inspiration uploads.
5. Checkout bridge: delivery/tax/payment gates; no payment intent before valid cart/order.
6. Automation guard layer: keep direct webshop orders separate from quote/deposit invoice automation.
7. Fulfillment handoff: CRM/order to project/task/calendar/crew prep fields.
8. Security/negative-route audit: block or redirect public surfaces that should not exist.

## Final Lane E conclusion

Lane E is now present and converged: catalog_data, source files, live checkout observation, existing ERPNext artifacts, and the latest readiness verifier agree on the same infrastructure-first path.

Full catalog import/reimport and public launch remain product/business approval decisions downstream of these gates, not automatic consequences of this artifact.
