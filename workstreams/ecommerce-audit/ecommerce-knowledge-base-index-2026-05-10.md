D:2026-05-10 | Check:memory recall + local artifact readback + legacy_source source + ERPNext official docs 2026-05-10 | Confidence:[LOCAL-PROOF]

# Locally Twisted Ecommerce Knowledge Base Index

Purpose: single source map for the launch-critical legacy_source → ERPNext ecommerce rebuild research. This is a research/index artifact only: no code changes, no legacy_source/ERPNext writes, no product purge/import permission.

## Current operating rule

- Parent-led research only until delegation is stable.
- Completion text is not evidence.
- Named artifact + direct readback is evidence.
- Missing artifact is `[NO EVIDENCE]`.
- legacy_source is a read-only source witness for commerce meaning; ERPNext/Frappe must receive that meaning natively.

## Durable memory recalled

- `memory/2026-05-06.md#L30-L32`: previous broad subagent swarm failure led to a knowledge-base-first correction; local `locally-twisted-legacy_source` was verified and added to the Event Space Balloon Designer knowledge base as a source inventory.
- `memory/2026-05-08.md#L45-L52`: prior LT product-page/catalog lane identified proof products Unicorn Bouquet and Classic Arch; Classic Arch has required `Arch Size`, `Design`, `LED Lights`, and `latex colors` as customization; Unicorn Bouquet has required `Bouquet Size` and optional `foil_number`; blockers included missing resolver prices, unclassified gallery images, ambiguous axes, and color customization work.

## Local source repos verified

- ERPNext/Frappe destination repo: `C:\Users\baenb\projects\Built_by_Cameron\_CLIENTS\locally-twisted` — present.
- legacy_source source-witness repo: `C:\Users\baenb\projects\locally-twisted-legacy_source` — present.

## Core ecommerce audit artifacts verified on disk

| Artifact | State | Use |
|---|---:|---|
| `workstreams/ecommerce-audit/legacy_source-source-commerce-map-2026-05-10.md` | present, read back | legacy_source source/product/page/option/pricing/media/cart meaning map. |
| `workstreams/ecommerce-audit/erpnext-receiving-parity-matrix-2026-05-10.md` | present | Destination parity and receiving blockers. |
| `workstreams/ecommerce-audit/cart-checkout-intent-preservation-audit-2026-05-10.md` | present | Existing cart/checkout/backend intent proof slice. |
| `workstreams/ecommerce-audit/native-frappe-product-template-architecture-2026-05-10.md` | present | Native Frappe product template architecture. |
| `workstreams/ecommerce-audit/cart-checkout-verification-gates-2026-05-10.md` | present | Launch-proof verification gate definitions. |
| `workstreams/ecommerce-audit/erpnext-receiving-rebuild-requirements-2026-05-10.md` | present | Receiving staging/register requirements. |
| `workstreams/ecommerce-audit/ecommerce-rebuild-safety-referee-2026-05-10.md` | present | Safety blockers and no-go rules. |
| `workstreams/ecommerce-audit/gl-proxy-ecommerce-rebuild-acceptance-2026-05-10.md` | present | Customer/operator/business acceptance criteria. |
| `workstreams/ecommerce-audit/user-provided-legacy_source-surfaces-2026-05-10.md` | present | GL-supplied legacy_source read-only surface list. |

## Current legacy_source source-witness facts

From `legacy_source-source-commerce-map-2026-05-10.md` and local legacy_source source:

- legacy_source local module version: `19.0.2.15.0`.
- legacy_source source depends on `website_sale`, `delivery`, `payment_stripe`, and `sale_loyalty`; this is real ecommerce, not a static theme.
- Public legacy_source shop surfaces show categories, products, variant selectors, inquiry forms, cart state, and product images.
- `deploy.py` exports/imports product categories, attributes, values, templates, and `product.template.attribute.value.price_extra` shape.
- `deploy.py` product export includes template `name`, `list_price`, `sale_ok`, `purchase_ok`, `is_published`, `description_sale`, `website_description`, primary `image_1920`, public category names, attribute lines, and non-zero `price_extra` rows keyed by template/attribute/value.
- `deploy.py` import recreates template records and attribute lines, then applies `price_extra` only when the destination PTAV price is still zero; it explicitly does not overwrite already-set production price extras.
- Product pages expose product/template IDs and legacy_source attribute-line field names such as `product_template_id`, `product_id`, and `ptal-*` inputs.
- Backend product `Images` tab uses `product_template_image_ids`, but inspected deploy path only proved primary image export/import; additional gallery image parity remains risk.

## legacy_source commerce meaning already identified

| Product/family | Known axes/options | Known pricing evidence | ERPNext implication |
|---|---|---|---|
| Classic Arch | `Arch Size`, `latex colors`, `Design`, `LED Lights` | base $260; 25ft +$65, 30ft +$130, 35ft +$195 | Complex/quote-first unless full option/cart/backend proof exists; colors are customization, not flat ERPNext dropdown. |
| Unicorn Bouquet | `Bouquet Size`, duplicate `Add Foil Number` groups | base $35; Medium +$35; Large +$50; each foil number +$12 | Good checkout proof candidate, but repeated option groups must not collapse by label. |
| Organic Garland | `Garland Length`, latex/color customization | base observed $150; deltas not fully captured | Needs full source export for price extras and color behavior. |
| Number Balloon Columns | number selection, number colors, latex colors | price extras not fully captured | Personalized product; likely quote-first/needs review until option/backend proof. |
| Balloon Drop | `Drop Size`, latex colors | deltas not fully captured | Event-moment product; likely quote-first/needs review pending proof. |

## Destination ERPNext/Frappe architecture facts

From local code readback:

- `catalog_contract/models.py` defines the needed product-page contract shape: `ProductPageContract`, required axes, customization axes, add-ons, dependency matrices, gallery images, commerce lane labels, warnings.
- `catalog_contract/source_builder.py` already separates:
  - required axes,
  - customization/color axes,
  - optional add-ons,
  - resolver-backed prices,
  - dependency matrices,
  - gallery images needing classification,
  - checkout vs quote-first lanes.
- `verify/product_page_architecture_readiness.py` treats architecture as separate from launch/import readiness and explicitly requires business/import/public-reopen gates.

## Official ERPNext docs checked 2026-05-10

- ERPNext v15 ecommerce docs redirect to `set_up_e_commerce` and state that v15 ecommerce requires the Frappe `webshop` app.
- ERPNext Item docs state an Item can be a product or service, and standard selling rate creates/fetches Item Price behavior.
- ERPNext Item Variants docs state templates cannot be used directly in transactions; only variants can be used. Variants are generated from Item Attributes.

ERPNext implication: legacy_source's product-template/page meaning cannot be mapped as one flat Website Item. ERPNext must use Item templates/variants where appropriate, plus a custom product-page contract layer for legacy_source semantics that ERPNext variants do not natively express: repeated add-on groups, multi-select color customization, gallery classification, quote-first workflows, and line-level intent payloads.

## Current blockers / no-evidence list

1. Complete live legacy_source product/attribute/value/price-extra export is still not verified into a full 53-product matrix.
2. Full valid-combination matrix for every product is not yet proven.
3. Color max-count validation is copy-observed but not server/source-proven.
4. Variant-specific image switching is still `[UNKNOWN]` until browser before/after image URL proof.
5. Additional gallery image parity is risky because inspected legacy_source deploy sync path proves primary images, not `product_template_image_ids` export.
6. Public checkout/payment/live email remains intentionally untested.
7. ERPNext full catalog remains `needs_review` until product proof matrix and import gates clear.
8. legacy_source production version may differ from local module version; label `[VERSION-MISMATCH]` until resolved.

## Next research actions

1. Build `ecommerce-product-proof-matrix-2026-05-10.md` from current artifacts and safe source reads: one row per product/family where evidence exists, with `[NO EVIDENCE]` cells explicit.
2. Read and summarize the existing ERPNext audit artifacts into one launch-blocker matrix.
3. Treat local `deploy.py` as a useful source-shape witness for categories/attributes/price extras, but not enough for gallery parity because it exports primary `image_1920` only.
4. Run browser-only media/variant proof on representative public product pages only if it can be done without cart/payment/admin mutation.
5. Do not purge/import/rebuild products until the receiving matrix, price matrix, media matrix, and GL/Jeff review packets exist.
