# Stripe Promo Codes Live Checkout - 2026-06-23

## Status

Live release complete.

`locallytwisted.com` now creates live Stripe Checkout Sessions with Stripe's
promotion-code entry control enabled. The Stripe-hosted checkout page showed
`Add code` during live proof. No one-time gift-card code was redeemed during
verification.

## Account And Provider Proof

Frappe Cloud account identity was verified from internal and live provider
evidence, not only from a Google account chooser.

- Internal records point to `locallytwisted@gmail.com` as the Frappe
  Cloud/Jeff account:
  - `.planning/ROADMAP.md`
  - `.planning/REQUIREMENTS.md`
  - `scripts/setup/setup_lt_company.py`
  - `decisions/2026-05-25-delivery-only-line-fulfillment.md`
- Gmail connector profile showed `Jeffery Kimber <locallytwisted@gmail.com>`.
- Frappe Cloud OTP login was completed through
  `locallytwisted@gmail.com`.
- Frappe Cloud dashboard displayed the active session as
  `locallytwisted@gmail.com`.
- Frappe Cloud site dashboard showed `locallytwisted.com` on bench group
  `bench-40102`, title `LT Staging - Inquiry Filter`, region N. Virginia.

Future agents: do not treat a Google login account picker as provider-account
truth. Use internal project records and the provider dashboard's logged-in
account/team/site evidence.

## Stripe Gift-Card / Promotion-Code Setup

Live Stripe now has a coupon/promotion-code set for five one-time `$100.00 USD`
discount gift cards.

- Stripe coupon name: `LT 100 Gift Cards - June 2026`
- Coupon shape: `$100.00 USD off once`
- Coupon max redemptions: `5`
- Promotion codes: five unique one-time codes, each max redemption `1`
- Exact code values are intentionally not committed to git because they are
  live stored-value instruments. Verify or recover them from the Stripe
  Dashboard promotion-code list or the operator-maintained gift-card sheet.

These are Stripe promotion codes, not formal ERPNext gift-card liability
records. They discount the Stripe Checkout total before payment. Separate
accounting/liability handling is required if LT wants formal gift-card
accounting in ERPNext.

## Source Changes

Full repo source commits on `main`:

- `9d89c34 Enable Stripe promo codes in checkout`
- `3498fef Fix Stripe promo checkout session params`

App mirror commits:

- `5b04784 Enable Stripe promo codes in checkout` on app mirror `main`
- `7e3ab00 Fix Stripe promo checkout session params` on app mirror `main`
- `4c5fe7c Enable Stripe promo codes in checkout` on live-tracking branch
  `live-shop-discovery-20260529`
- `5d7c952 Fix Stripe promo checkout session params` on live-tracking branch
  `live-shop-discovery-20260529`

Frappe Cloud was tracking app mirror branch
`live-shop-discovery-20260529`, not app mirror `main`. The live branch had to
receive the fix directly. Future releases must compare the previous live app
hash to the target app mirror commit instead of assuming source `main` or app
mirror `main` is the live target.

## Code Contract

`apps/locally_twisted/locally_twisted/payments/stripe_session.py` now creates
one-time Stripe Checkout Sessions with:

- `mode: "payment"`
- `allow_promotion_codes: True`
- no `payment_method_collection`

The first live attempt set `payment_method_collection: "if_required"`. Live
Stripe rejected that one-time Checkout Session with:

`You can only set payment_method_collection if there are recurring prices.`

The fix removed `payment_method_collection` and strengthened
`apps/locally_twisted/locally_twisted/verify/stripe_amount_parity_contract.py`
so it now requires `allow_promotion_codes is True` and fails if
`payment_method_collection` is present.

## Frappe Cloud Release Proof

First Frappe Cloud pipeline:

- Pipeline: `64v1t42tmv`
- Created by: `locallytwisted@gmail.com`
- Purpose: deploy `4c5fe7c Enable Stripe promo codes in checkout`
- Result: `Success`
- Duration: `5m 42s`
- Issues: `0`
- Site update pull: `Success`

Second Frappe Cloud pipeline:

- Pipeline: `3e3e0b8she`
- Created by: `locallytwisted@gmail.com`
- Purpose: deploy `5d7c952 Fix Stripe promo checkout session params`
- Result: `Success`
- Start shown in Frappe Cloud: Monday, June 22, 2026 7:20 PM MDT
- End shown in Frappe Cloud: Monday, June 22, 2026 7:27 PM MDT
- Duration: `7m 5s`
- Issues: `0`

Post-release Frappe Cloud Apps tab:

- App: `Locally Twisted`
- Repository: `CBaen/Locally-Twisted-Frappe-App`
- Branch: `live-shop-discovery-20260529`
- Version: `5d7c952`
- Status: `Latest Version`

## Live Verification

Public route proof after the second deployment:

- `https://locallytwisted.com/api/method/frappe.ping` returned HTTP `200` and
  `{"message":"pong"}` from `Server: Frappe Cloud`.
- `https://locallytwisted.com/` returned HTTP `200` from `Server: Frappe Cloud`.
- Frappe Cloud Apps tab showed Locally Twisted at `5d7c952`, `Latest Version`.

Live checkout proof:

- Test URL:
  `https://locallytwisted.com/checkout?item=encanto-bouquet-SMA&qty=1`
- Test fulfillment: delivery to West Jordan, Utah on 2026-07-01.
- Live preview totals returned `subtotal: 35.0`, `delivery_fee: 15.0`,
  `tax_amount: 2.61`, `total: 52.61`.
- `submit_guest_order` returned HTTP `200`.
- Browser redirected to `https://checkout.stripe.com/...`.
- Stripe page showed `Pay Locally Twisted`, `$52.61`, and `Add code`.
- Screenshot artifact, local-only and gitignored:
  `output/playwright/live-stripe-promo-field-proof.png`.
- JSON proof artifact, local-only and gitignored:
  `output/playwright/live-stripe-promo-field-proof.json`.

No payment details were entered and no one-time code was consumed.

## Verification Commands Run

Local/source verification:

```bash
python -m py_compile \
  apps/locally_twisted/locally_twisted/payments/stripe_session.py \
  apps/locally_twisted/locally_twisted/verify/stripe_amount_parity_contract.py

python scripts/verify/stripe_amount_parity_contract.py
git diff --check
```

Live route proof:

```bash
curl -sS -D - https://locallytwisted.com/api/method/frappe.ping
curl -sS -I https://locallytwisted.com/
```

Frappe Cloud/dashboard and live Stripe page proof were performed through a
temporary Brave CDP session with repo-local Playwright. The browser session was
closed after proof. The local LT Docker workshop stack was stopped after work
with `client-stack stop lt`.

## Follow-Up Boundaries

- Do not burn a one-time code for proof unless GL explicitly approves losing
  one redemption.
- If a future agent must prove code application, use the smallest eligible
  live order and stop before final payment unless GL approves a real redemption
  or payment.
- Do not call these formal gift cards in ERPNext accounting. They are Stripe
  discount/promotion codes.
- Do not reintroduce `payment_method_collection` on one-time payment Checkout
  Sessions.
- Do not assume app mirror `main` is live; check Frappe Cloud's tracked branch
  and installed app hash.
- Do not claim live release from source/app push alone. Require successful
  Frappe Cloud deploy/update and public live route/checkout proof.

## Related Docs

- `CODING-HANDOFF.md`
- `locally-twisted-decisions.md`
- `locally-twisted-queue.md`
- `capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`
- `capabilities/recipes/erpnext-checkout-commerce-rules.md`
- `capabilities/failures/stripe-checkout-one-time-promo-param-drift.md`
- `capabilities/failures/frappe-cloud-app-mirror-release-scope-drift.md`
- `capabilities/failures/frappe-cloud-release-site-migration-drift.md`
