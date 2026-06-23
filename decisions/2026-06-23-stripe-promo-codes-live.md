# 2026-06-23 - Stripe Promo Codes Are The Live Gift-Card Mechanism

## Decision

Use Stripe coupon/promotion codes for the current five one-time `$100.00 USD`
gift cards. Enable those codes on the live Stripe Checkout page with
`allow_promotion_codes: True`.

Do not build a separate ERPNext gift-card ledger for this immediate need.
Do not call Stripe promotion codes formal ERPNext gift-card liabilities.

## Reasoning

GL needed five usable one-time gift-card/coupon codes immediately for live
checkout. Stripe already owns the payment page and has built-in coupon and
promotion-code redemption. The safe fast path is to discount the Stripe
Checkout Session before payment rather than build a new ERPNext stored-value
system under time pressure.

The current gift-card need is operational redemption, not accounting-system
liability management. Formal gift-card liability tracking can be designed
later if LT needs accountant-facing balances, breakage handling, or ERPNext
reports.

## Implementation Boundary

Implemented:

- Five live Stripe promotion codes under coupon
  `LT 100 Gift Cards - June 2026`.
- Each code is unique and one-time-use.
- Checkout Sessions now include `allow_promotion_codes: True`.
- Payment success and webhook reconciliation accept Stripe sessions that may
  complete with `paid` or `no_payment_required` states after a full discount.
- Contract verifier now checks promo-code support and rejects
  `payment_method_collection` on one-time sessions.
- Live Frappe Cloud deployment completed to app branch
  `live-shop-discovery-20260529` at `5d7c952`.

Not implemented:

- ERPNext gift-card liability ledger.
- Gift-card sale/redemption accounting reports.
- Automatic customer-facing gift-card balance lookup.
- Burning a one-time code in proof.

## Critical Stripe Lesson

`payment_method_collection: "if_required"` is not valid for this one-time
payment Checkout Session path in live Stripe. The first live attempt failed
before redirect with:

`You can only set payment_method_collection if there are recurring prices.`

Keep `allow_promotion_codes: True`. Do not set `payment_method_collection` for
one-time LT product checkout.

## Account Proof

Frappe Cloud identity must come from internal/provider evidence, not a Google
chooser alone. For this release:

- Internal docs and setup code identify `locallytwisted@gmail.com` as the
  Frappe Cloud/Jeff account.
- Frappe Cloud OTP was received through `locallytwisted@gmail.com`.
- Frappe Cloud dashboard showed the active account as
  `locallytwisted@gmail.com`.
- The release pipelines were created by `locallytwisted@gmail.com`.

## Receipts

- Full repo commits: `9d89c34`, `3498fef`
- App mirror `main` commits: `5b04784`, `7e3ab00`
- App mirror live branch commits: `4c5fe7c`, `5d7c952`
- Frappe Cloud pipelines: `64v1t42tmv`, `3e3e0b8she`
- Final live app version: `5d7c952`, `Latest Version`
- Live route proof: `frappe.ping` returned `pong` from Frappe Cloud.
- Live checkout proof: Stripe page rendered `Add code`.
- Handoff: `workstreams/ecommerce-audit/stripe-promo-codes-live-2026-06-23.md`

## Alternatives Considered

- Build gift cards inside ERPNext immediately. Rejected for this urgent need
  because it would add accounting and redemption complexity before the client
  needed that system.
- Create only the coupon in Stripe but leave checkout unchanged. Rejected
  because customers could not enter codes without Stripe Checkout promotion
  code support enabled.
- Redeem one live code as proof. Rejected because each code has only one
  redemption and proof could be obtained by verifying the live Stripe
  promotion-code field without consuming value.

## Decided By

Guiding Light asked for the five one-time `$100` codes and live checkout field.
Codex implemented and verified the Stripe/Frappe Cloud release on
2026-06-23.
