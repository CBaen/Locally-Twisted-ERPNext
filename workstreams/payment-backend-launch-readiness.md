# Payment Backend Launch Readiness

Last updated: 2026-05-24

This workstream is the payment-specific handoff lane for launch readiness. It is intentionally separate from `PROJECT-STATUS.md`, because that file mixes current receipts with stale historical state.

2026-05-24 staging owner-review update: product/cart checkout route proof now
passes on `https://locallytwisted-staging.frappe.cloud`, and one Stripe
test-mode checkout completed into paid ERPNext staging records. The earlier
blocker was staging encrypted-secret drift on `Stripe Settings.Test.secret_key`;
it was repaired by re-entering the staging test secret. A second encrypted
secret drift appeared on `Email Account.Locally Twisted.password`; re-entering
the staging Email Account app password allowed the receipt and operator Email
Queue records to reach `Sent`. This is staging provider/config drift, not
product setup failure and not live payment approval. Current handoff:
`workstreams/ecommerce-audit/staging-checkout-product-flow-2026-05-24.md`;
failure recipes:
`capabilities/failures/frappe-cloud-staging-stripe-secret-drift.md` and
`capabilities/failures/frappe-cloud-staging-email-secret-drift.md`.

2026-05-11 cutover update: live mode now requires an explicit HTTPS
`host_name` in site config, in addition to explicit live Stripe settings,
payment gateway account, Stripe payment method configuration, operator email,
and webhook signing secret. The production webhook endpoint remains
`/api/method/locally_twisted.payments.stripe_webhook.stripe_webhook`; use the
full `https://locallytwisted.com/...` URL only after the production host exists.

## Scope

Owns the backend payment path for the local ERPNext storefront:

- guest checkout creates Customer, Contact, Address, Sales Order, Payment Request, and Stripe Checkout Session
- Stripe return and webhook paths reconcile paid orders
- paid-order cascade creates Payment Entry, Sales Invoice, receipt email, operator email, welcome email, and keeps checkout notes visible
- launch-readiness checks verify non-secret config shape before real Stripe testing or live cutover

Does not own:

- public inquiry/contact form audit
- product page design or category page redesign
- real Stripe card checkout testing
- Stripe Dashboard changes requiring GL/client account approval
- legal approval of privacy or terms language

## Current Verified Local State

These are verified local/backend facts, not live-production claims:

- `scripts/verify/payment_backend_config_contract.py` passes against the local ERPNext site.
- `scripts/verify/payment_webhook_contract.py` passes against mocked Stripe webhook events.
- `scripts/verify/payment_cascade_contract.py` passes and rolls back its generated ERPNext records.
- `scripts/verify/cart_checkout_contract.py` passes for purchasable variants, single-SKU items, and shop card behavior.
- `scripts/verify/payment_launch_readiness.py` passes in local mode.
- `scripts/verify/payment_launch_readiness.py --mode live` fails, as expected, because the site is still configured for local Stripe test mode and localhost.
- Hosted staging route proof and one Stripe test-mode checkout passed on
  2026-05-24. Verified staging records: Sales Order `SAL-ORD-2026-00024`,
  Payment Request `ACC-PRQ-2026-00021` `Paid`, Sales Invoice
  `ACC-SINV-2026-00004` `Paid`, tax `$2.61`, grand total `$37.61`, and Email
  Queue rows `cchsjbegpi` / `cchtiiieuk` `Sent`.
- Staging owner login for `locallytwisted@gmail.com` was reset and verified in
  a clean browser session ending on `Owner Home`; owner Desk payment review can
  use that account during staging review.

Latest payment commits on `main`:

- `9209604` `Reconcile paid orders after Stripe payment`
- `9d10947` `Make payment backend settings configurable`
- `d7b9051` `Guard Stripe webhook fulfillment status`
- `2365b3e` `Require LT checkout metadata in Stripe webhook`

## Verified Commands

Use these from the repo root:

```powershell
python scripts\verify\payment_backend_config_contract.py
python scripts\verify\payment_webhook_contract.py
python scripts\verify\payment_cascade_contract.py
python scripts\verify\cart_checkout_contract.py
python scripts\verify\payment_launch_readiness.py
```

Expected current local result: all pass.

Before live cutover:

```powershell
python scripts\verify\payment_launch_readiness.py --mode live
```

Run this only during cutover work. It is intentionally outside the current fake-data/synthetic backend readiness gate.

## Cutover-Only Deferred Items

The live-mode verifier is the right tool later, after GL/Jeff/accounting are ready to configure production payment details. The deferred cutover checklist is:

- Stripe Settings are still test mode (`Test`, `pk_test_...` / `sk_test_...`).
- `lt_stripe_settings_name` is not explicitly set in site config.
- `lt_payment_gateway_account` is not explicitly set in site config.
- `lt_stripe_payment_method_configuration` is not explicitly set in site config.
- `lt_operator_email` is not explicitly set in site config.
- `host_name` is missing, local-only, or not HTTPS.

The verifier intentionally does not print secrets.

## Remaining Payment Work

Next without GL:

- Keep the payment verifier suite current if more backend payment logic changes.
- Audit payment docs for stale language only when editing the relevant document anyway; do not chase full parity in `PROJECT-STATUS.md`.

Needs GL or client account access:

- Have the owner/reviewer confirm inbox-visible receipt delivery if that is part
  of staging approval; current proof stops at SMTP acceptance.
- Confirm live Stripe account setup and live key names.
- Create or identify the live Stripe Payment Method Configuration that keeps Link disabled, if the no-Link decision still stands.
- Configure the production Stripe webhook endpoint and store its `whsec_...` in site config.
- Wire Stripe Dashboard privacy and terms URLs after GL/legal approval.
- Run the real Stripe CLI or Dashboard-backed checkout test when the project enters the testing phase.

## Trust Boundary

Do not say "payments are live-ready" until `payment_launch_readiness.py --mode live` passes and a real checkout has been completed through Stripe in the intended environment.

Safe wording right now: "local payment backend structure is ready for the next Stripe test; live cutover configuration is not complete."
