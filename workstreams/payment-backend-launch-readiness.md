# Payment Backend Launch Readiness

Last updated: 2026-05-02

This workstream is the payment-specific handoff lane for launch readiness. It is intentionally separate from `PROJECT-STATUS.md`, because that file mixes current receipts with stale historical state.

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

Expected current local result: fail until live Stripe keys, live site config, and production host values are configured.

## Current Live-Mode Blockers

The local verifier currently reports these live-mode blockers:

- Stripe Settings are still test mode (`Test`, `pk_test_...` / `sk_test_...`).
- `lt_stripe_settings_name` is not explicitly set in site config.
- `lt_payment_gateway_account` is not explicitly set in site config.
- `lt_stripe_payment_method_configuration` is not explicitly set in site config.
- `lt_operator_email` is not explicitly set in site config.
- `host_name` is local-only: `http://localhost:8081`.

The verifier intentionally does not print secrets.

## Remaining Payment Work

Next without GL:

- Keep the payment verifier suite current if more backend payment logic changes.
- Audit payment docs for stale language only when editing the relevant document anyway; do not chase full parity in `PROJECT-STATUS.md`.

Needs GL or client account access:

- Confirm live Stripe account setup and live key names.
- Create or identify the live Stripe Payment Method Configuration that keeps Link disabled, if the no-Link decision still stands.
- Configure the production Stripe webhook endpoint and store its `whsec_...` in site config.
- Wire Stripe Dashboard privacy and terms URLs after GL/legal approval.
- Run the real Stripe CLI or Dashboard-backed checkout test when the project enters the testing phase.

## Trust Boundary

Do not say "payments are live-ready" until `payment_launch_readiness.py --mode live` passes and a real checkout has been completed through Stripe in the intended environment.

Safe wording right now: "local payment backend structure is ready for the next Stripe test; live cutover configuration is not complete."
