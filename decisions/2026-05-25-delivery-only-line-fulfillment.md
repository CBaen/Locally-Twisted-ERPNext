# 2026-05-25 Delivery-Only Line Fulfillment Decision

Audience: peer Codex/GPT agents working Locally Twisted ecommerce, checkout,
staging, and live promotion.

## Decision

Delivery-only eligibility is product-line behavior, not whole-cart behavior.

Products in Garlands, Arches, Columns, Balloon Drops, and Photo Ops &
Backdrops require delivery. Product pages for those categories must say
`Delivery only`.

Mixed carts must stay mixed. If a cart contains one delivery-only item and one
pickup-eligible item, checkout must keep pickup available for the eligible
item while still collecting delivery details for the delivery-only item.

## Reasoning

Forcing a whole mixed cart into delivery-only hurts conversion and can make
customers abandon orders. The business need is to prevent impossible pickup
for installed or oversized products without punishing customers who also buy
pickup-friendly products.

## Implementation Boundary

- Do not make all mixed carts delivery-only.
- Do not use delivery or pickup as a product category.
- Do not rely on visible Website Item copy alone; checkout needs source-owned
  fulfillment policy data.
- Store line-level fulfillment on Sales Order Item / Sales Invoice Item custom
  fields when those fields exist.
- Keep live promotion separate from staging proof.

## Receipts

- Full repo source: `4722a1c Add delivery-only fulfillment rules`
- App mirror source: `3ca46bb Add delivery-only fulfillment rules press-deploy-bench-40102`
- Frappe Cloud staging migration: `Migrate`, `Success`, created by
  `locallytwisted@gmail.com` on 2026-05-25.
- Hosted staging checkout proof:
  `LT_BASE_URL=https://locallytwisted-staging.frappe.cloud npm run test:checkout-experience`
  passed `4/4`.
- Feature handoff:
  `workstreams/ecommerce-audit/delivery-only-fulfillment-staging-2026-05-25.md`

## Decided By

Guiding Light business correction and refusal of whole-cart delivery-only
fallback; Codex implementation and staging release on 2026-05-25.
