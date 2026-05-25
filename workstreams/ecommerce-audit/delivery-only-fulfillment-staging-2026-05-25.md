# Delivery-Only Fulfillment Staging - 2026-05-25

Status: implemented, pushed, deployed to Frappe Cloud staging, and hosted
checkout proof passed.

## Scope

Delivery-only product behavior now applies to these primary product categories:

- Garlands
- Arches
- Columns
- Balloon Drops
- Photo Ops & Backdrops

These products show delivery-only product-page copy and checkout treats their
cart lines as delivery-only. Mixed carts must stay mixed: delivery-only lines
require delivery details, while pickup-eligible lines can still be picked up.
Do not collapse a mixed cart into delivery-only.

## Source Points

- Full repo source commit:
  `4722a1c Add delivery-only fulfillment rules`
- Frappe app mirror commit:
  `3ca46bb Add delivery-only fulfillment rules press-deploy-bench-40102`
- Frappe Cloud staging site:
  `https://locallytwisted-staging.frappe.cloud`
- Frappe Cloud site update:
  `Migrate`, `Success`, created by `locallytwisted@gmail.com` on
  2026-05-25.
- Installed staging app commit after update:
  `3ca46bb`.

## Files

- `apps/locally_twisted/locally_twisted/commerce_rules.py`
- `apps/locally_twisted/locally_twisted/checkout_fulfillment.py`
- `apps/locally_twisted/locally_twisted/api/cart.py`
- `apps/locally_twisted/locally_twisted/www/checkout.py`
- `apps/locally_twisted/locally_twisted/www/checkout.html`
- `apps/locally_twisted/locally_twisted/seed/sync_commerce_rules.py`
- `apps/locally_twisted/locally_twisted/patches/sync_delivery_only_fulfillment_20260525.py`
- `apps/locally_twisted/locally_twisted/product_page_runtime.py`
- `apps/locally_twisted/locally_twisted/templates/generators/item/item_details.html`
- `apps/locally_twisted/locally_twisted/verify/checkout_fulfillment_contract.py`
- `scripts/verify/checkout_experience.spec.js`

## Verification

Local proof before source freeze:

```powershell
python -m py_compile apps/locally_twisted/locally_twisted/commerce_rules.py apps/locally_twisted/locally_twisted/checkout_fulfillment.py apps/locally_twisted/locally_twisted/api/cart.py apps/locally_twisted/locally_twisted/www/checkout.py apps/locally_twisted/locally_twisted/seed/sync_commerce_rules.py apps/locally_twisted/locally_twisted/patches/sync_delivery_only_fulfillment_20260525.py apps/locally_twisted/locally_twisted/verify/checkout_fulfillment_contract.py
git diff --check
python scripts/verify/frappe_cloud_preflight.py
python scripts/verify/commerce_rules_contract.py
python scripts/verify/product_page_runtime_contract.py
python scripts/verify/cart_checkout_contract.py
python scripts/verify/checkout_fulfillment_contract.py
python scripts/verify/payment_backend_config_contract.py
python scripts/verify/payment_webhook_contract.py
python scripts/verify/stripe_amount_parity_contract.py
npm run test:checkout-experience
```

Hosted staging proof after app mirror update, migration, and cache clear:

```powershell
$env:LT_BASE_URL='https://locallytwisted-staging.frappe.cloud'
npm run test:checkout-experience
```

Result: `4/4` passed.

Direct staged product probes:

- `/shop-items/arches/classic-organic-arch` returned `200`, showed
  `Delivery only`, and did not show old pickup-request copy.
- `/shop-items/garlands/graduation-grab-n-go` returned `200`, showed
  `Delivery only`, and did not show old pickup-request copy.
- `/shop-items/balloon-drops/balloon-drop` returned `200`, showed
  `Delivery only`, and did not show old pickup-request copy.

The hosted checkout test also proves a mixed cart keeps pickup available for
pickup-eligible items while marking delivery-only items correctly.

## Boundaries

- Staging only.
- No live deploy.
- No DNS change.
- No Search Console change.
- No live Stripe change.
- No production data mutation.
- No real payment test was run for this 2026-05-25 slice.

## Backlinks

- `CODING-HANDOFF.md`
- `ECOMMERCE-SHOP-HANDOFF.md`
- `locally-twisted-queue.md`
- `locally-twisted-decisions.md`
- `decisions/2026-05-25-delivery-only-line-fulfillment.md`
- `workstreams/frappe-cloud-staging-owner-review-2026-05-24.md`
- `workstreams/ecommerce-audit/staging-checkout-product-flow-2026-05-24.md`
