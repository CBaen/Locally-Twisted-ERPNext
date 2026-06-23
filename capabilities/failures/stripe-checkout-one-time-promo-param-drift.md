---
name: Stripe Checkout one-time promo parameter drift
type: failure
failure_kind: recurring_pattern
schema_version: 0.1
date_discovered: 2026-06-23
last_updated: 2026-06-23
status: guarded
scope: project
owner_context: Locally Twisted live Stripe Checkout promotion-code releases
related_capabilities:
  - ../recipes/frappe-cloud-cloudflare-stripe-launch-gate.md
  - ../recipes/erpnext-checkout-commerce-rules.md
related_failures:
  - frappe-cloud-app-mirror-release-scope-drift.md
  - frappe-cloud-release-site-migration-drift.md
tags:
  - locally-twisted
  - stripe
  - checkout
  - promotion-codes
  - gift-cards
  - payment
  - fail-loud
---

# Failure Recipe: Stripe Checkout One-Time Promo Parameter Drift

## Symptom

Live checkout fails before redirecting to Stripe even though the local/source
contract says promotion codes are enabled.

Customer-facing checkout shows a generic form-level failure such as:

`Tiny snag: we could not start checkout just now...`

The exact Stripe error is:

`You can only set payment_method_collection if there are recurring prices.`

## Trigger Conditions

- A one-time Stripe Checkout Session uses `mode: "payment"`.
- The code adds `allow_promotion_codes: True` for Stripe promotion codes.
- The code also adds `payment_method_collection: "if_required"` based on an
  assumed no-cost-order or subscription/free-trial pattern.
- Verification stops at local capture tests and does not perform a live Stripe
  API call or live checkout redirect.

## Known Instances

| Date | Project | Surface | Action being taken | Bad outcome | Evidence | Guard state | Status |
|---|---|---|---|---|---|---|---|
| 2026-06-23 | Locally Twisted | Live Stripe Checkout | Enable five one-time `$100` promotion-code gift cards | Live `submit_guest_order` returned HTTP `500`; Stripe rejected the Session before redirect | Live traceback from `checkout.submit_guest_order`; Frappe Cloud app at `4c5fe7c`; Stripe request `req_L9cYPacufrQlKh`; repaired source `3498fef`; repaired live app `5d7c952`; live Stripe page then showed `Add code` | contract verifier strengthened and live redeploy proof added | recovered/guarded |

## Root Pattern

Stripe Checkout parameters are mode-sensitive. A parameter that looks useful
for no-payment or subscription-like flows can be invalid for one-time payment
Checkout Sessions. Local monkeypatch tests can prove the code builds a kwargs
object, but they cannot prove live Stripe accepts those kwargs.

## Why It Seemed Reasonable At The Time

The goal was to allow `$100` codes to reduce a small order to zero dollars.
Stripe has no-cost order behavior, and `if_required` reads like the right
payment-method collection behavior. In this live one-time Checkout path,
Stripe rejected it.

## Detection Signals

- `payment_method_collection` appears in
  `payments/stripe_session.py`.
- `stripe_amount_parity_contract.py` captures Checkout Session kwargs but does
  not fail on `payment_method_collection`.
- Live checkout returns HTTP `500` from
  `/api/method/locally_twisted.www.checkout.submit_guest_order`.
- Stripe exception mentions recurring prices.

## Required Guard

For LT one-time product checkout:

- Require `allow_promotion_codes: True` when promotion codes are intentionally
  enabled.
- Reject `payment_method_collection` in the one-time Checkout Session contract.
- For live payment-surface changes, prove Stripe accepts the live Session by
  reaching `checkout.stripe.com`; do not rely on local kwargs capture alone.
- Do not redeem one-time codes unless GL explicitly approves consuming a code.

## Recovery Recipe

1. Remove `payment_method_collection` from one-time Checkout Session kwargs.
2. Keep `allow_promotion_codes: True`.
3. Strengthen the contract verifier so the bad parameter cannot return.
4. Push the full source and the actual Frappe Cloud tracked app mirror branch.
5. Deploy/update the Frappe Cloud site.
6. Verify the Frappe Cloud Apps tab shows the target app hash as
   `Latest Version`.
7. Verify `frappe.ping`, homepage route health, and a live checkout redirect
   to Stripe.
8. Stop before redeeming a one-time code unless explicitly approved.

## What Not To Do

- Do not assume Stripe docs or memory about another Checkout mode applies to
  this one-time payment Session.
- Do not treat local captured kwargs as live Stripe acceptance.
- Do not burn a one-time gift-card code just to prove the field exists.
- Do not call source/app mirror pushes live proof before Frappe Cloud deploy
  and public checkout proof.

## Cross-links

- Related recipe: `../recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`
- Related recipe: `../recipes/erpnext-checkout-commerce-rules.md`
- Related failure: `frappe-cloud-app-mirror-release-scope-drift.md`
- Related failure: `frappe-cloud-release-site-migration-drift.md`
- Related handoff:
  `../../workstreams/ecommerce-audit/stripe-promo-codes-live-2026-06-23.md`
- Related decision:
  `../../decisions/2026-06-23-stripe-promo-codes-live.md`

## Evidence Quality

Direct live failure and direct live recovery proof. The final live proof showed
Stripe Checkout at `checkout.stripe.com` with `Add code` visible. A code was
not redeemed, by design, because all five codes are one-time-use.
