# Staging Checkout Product Flow - 2026-05-24

Status: product/cart/checkout route flow is repaired on hosted staging; Stripe
test-mode checkout and ERPNext payment cascade passed on hosted staging.

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

```bash
$env:LT_BASE_URL='https://locallytwisted-staging.frappe.cloud'
npm run test:checkout-experience
```

Observed result: `3/3` passed.

Raw staging checkout HTML also contained:

- `Preferred contact method`
- `pickupWindowRules`

Additional hosted proof after the staging provider settings were repaired:

- Re-entered the staging Stripe test secret key for `Stripe Settings / Test`.
- Confirmed `Stripe-Test - USD - LT` still points at `Locally Twisted`, USD,
  default payment account `Stripe-Test - LT`.
- Ran a hosted configured-bouquet cart checkout from
  `/shop-items/bouquets/encanto-bouquet` to Stripe Checkout.
- Completed one Stripe test-mode payment with Stripe's documented success test
  card.
- Stripe returned to staging `/thank-you?order=SAL-ORD-2026-00024`.
- Desk proof for `SAL-ORD-2026-00024`:
  - Sales Order status: `To Deliver`.
  - Item: `encanto-bouquet-SMA`, qty `1`, rate `$35.00`.
  - Tax: `7.450%`, `$2.61`.
  - Grand total: `$37.61`.
  - Requested pickup: West Jordan, `2026-05-26`, `12:00-12:30`.
- Payment Request `ACC-PRQ-2026-00021` is `Paid`.
- Sales Invoice `ACC-SINV-2026-00004` is `Paid`, grand total `$37.61`,
  outstanding amount `$0.00`.
- Receipt Email Queue `cchsjbegpi` and operator Email Queue `cchtiiieuk`
  reached `Sent` after re-entering the staging Email Account app password.

## Resolved Staging Blockers

The product setup blocker is resolved for the tested configured bouquet route.
The Stripe Settings blocker is resolved on staging as of 2026-05-24 after the
test secret key was re-entered.

During the recovery lane, final submit first reached the payment setup layer
and failed because staging could not decrypt `Stripe Settings.Test.secret_key`.
Treat that pattern as provider/site configuration drift. It is not a Product
Setup or checkout variant bug.

Official Frappe Cloud migration documentation describes the site encryption
key as required for decrypting password fields after site restores/migrations:
`https://docs.frappe.io/cloud/sites/migrate-an-existing-site#encryption-key`.
For staging, the practical repair is either restore the correct encryption key
for the copied site context or re-enter the test secret key in staging.

The same restored-site encrypted-password drift also hit `Email Account /
Locally Twisted`. Re-entering the local `GMAIL_APP_PASSWORD` value in the
staging Email Account repaired Frappe-side SMTP send acceptance for the test
receipt/operator messages. Email Queue `Sent` proves SMTP acceptance, not
inbox-visible delivery. A human with the `locallytwisted@gmail.com` inbox should
still confirm inbox receipt if that experience matters for owner review.

## Required Follow-Up

Before live approval:

```bash
$env:LT_BASE_URL='https://locallytwisted-staging.frappe.cloud'
npm run test:checkout-experience
python scripts/verify/payment_backend_config_contract.py
python scripts/verify/payment_webhook_contract.py
python scripts/verify/stripe_amount_parity_contract.py
```

Then repeat an authorized Stripe test-mode checkout after any further staging
provider changes. Do not promote this to live checkout authority without the
live-mode payment launch gate and explicit live Stripe approval.

## Boundaries

- This does not approve live checkout.
- This does not authorize live payment keys.
- This does not touch DNS or Search Console.
- Do not hide the payment blocker by calling it a generic product setup issue.
- Do not treat Email Queue `Sent` as inbox proof; it is SMTP acceptance only.

## Backlinks

- `workstreams/frappe-cloud-staging-owner-review-2026-05-24.md`
- `workstreams/payment-backend-launch-readiness.md`
- `capabilities/failures/frappe-cloud-staging-stripe-secret-drift.md`
- `capabilities/failures/frappe-cloud-staging-email-secret-drift.md`
- `capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`
- `decisions/2026-05-24-staging-owner-review-recovery.md`
- `ECOMMERCE-SHOP-HANDOFF.md`
