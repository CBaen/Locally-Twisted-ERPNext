# Staging Checkout Product Flow - 2026-05-24

Status: product/cart/checkout route flow is repaired on hosted staging; final
payment handoff is blocked by staging payment-secret configuration.

## Scope

This lane responds to the hosted staging checkout findings reported from:

- `https://locallytwisted-staging.frappe.cloud/shop-items/bouquets/encanto-bouquet`
- `https://locallytwisted-staging.frappe.cloud/checkout`

Covered issues:

- base product photos missing from configured product gallery behavior;
- add-to-cart not visibly updating the header cart state;
- checkout order-summary products not linking back to product pages;
- checkout email/phone helper copy and preferred contact method;
- pickup time display using business-friendly AM/PM windows;
- configured bouquet checkout failing with a product setup review message.

## Source Points

- Full repo checkout fix: `70b8869 Fix staging checkout product flow`
- Full repo safety fix: `203127a Hide unsafe checkout provider errors`
- App mirror checkout fix: `a4a0fc0 Fix staging checkout product flow press-deploy-bench-40102`
- App mirror safety fix: `5bb9326 Hide unsafe checkout provider errors press-deploy-bench-40102`
- App mirror deploy trigger: `9ce07f2 Trigger staging checkout safety deploy press-deploy-bench-40102`

## Files

- `apps/locally_twisted/locally_twisted/commerce_rules.py`
- `apps/locally_twisted/locally_twisted/product_setup_runtime.py`
- `apps/locally_twisted/locally_twisted/product_page_runtime.py`
- `apps/locally_twisted/locally_twisted/templates/generators/item/item_configure.html`
- `apps/locally_twisted/locally_twisted/templates/generators/item/item_image.html`
- `apps/locally_twisted/locally_twisted/templates/includes/navbar/navbar.html`
- `apps/locally_twisted/locally_twisted/www/checkout.html`
- `apps/locally_twisted/locally_twisted/www/checkout.py`
- `scripts/verify/checkout_experience.spec.js`
- `scripts/verify/product_gallery_experience.spec.js`

## Key Behavior

- Cart count is visible in the header after adding a product.
- Checkout order-summary product rows link back to the product route.
- Checkout contact copy says email/phone are used only for order updates.
- Checkout includes preferred contact method.
- Pickup times come from configured operating-hour windows and display in AM/PM
  form.
- For Product Setup groups that map to real priced ERPNext variants, checkout
  resolves by the priced ERPNext variant attributes instead of splitting stored
  display labels on commas.
- Unsafe provider/decryption wording is not meant for customer UI; checkout
  should show customer-safe failure copy while server logs keep the exact
  operator error.

## Hosted Staging Proof

Fresh staging command during this documentation pass:

```powershell
$env:LT_BASE_URL='https://locallytwisted-staging.frappe.cloud'
npm run test:checkout-experience
```

Observed result: `3/3` passed.

Raw staging checkout HTML also contained:

- `Preferred contact method`
- `pickupWindowRules`

## Current Blocker

The product setup blocker is resolved for the tested configured bouquet route.
The remaining blocker is payment configuration on staging. During the recovery
lane, final submit reached the payment setup layer and failed because staging
could not decrypt `Stripe Settings.Test.secret_key`.

Treat this as provider/site configuration drift. Do not send the owner through
card testing until the staging secret key/payment settings are repaired and the
payment proof gates pass.

Official Frappe Cloud migration documentation describes the site encryption
key as required for decrypting password fields after site restores/migrations:
`https://docs.frappe.io/cloud/sites/migrate-an-existing-site#encryption-key`.
For staging, the practical repair is either restore the correct encryption key
for the copied site context or re-enter the test secret key in staging.

## Required Follow-Up

Before owner checkout review:

```powershell
$env:LT_BASE_URL='https://locallytwisted-staging.frappe.cloud'
npm run test:checkout-experience
python scripts\verify\payment_backend_config_contract.py
python scripts\verify\payment_webhook_contract.py
python scripts\verify\stripe_amount_parity_contract.py
```

Then run one authorized Stripe test-mode checkout and verify ERPNext records,
tax, customer receipt, operator email, and payment state.

## Boundaries

- This does not approve live checkout.
- This does not authorize live payment keys.
- This does not touch DNS or Search Console.
- Do not hide the payment blocker by calling it a generic product setup issue.

## Backlinks

- `workstreams/frappe-cloud-staging-owner-review-2026-05-24.md`
- `workstreams/payment-backend-launch-readiness.md`
- `capabilities/failures/frappe-cloud-staging-stripe-secret-drift.md`
- `capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`
- `decisions/2026-05-24-staging-owner-review-recovery.md`
- `ECOMMERCE-SHOP-HANDOFF.md`
