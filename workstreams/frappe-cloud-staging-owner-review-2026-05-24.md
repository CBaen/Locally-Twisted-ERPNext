# Frappe Cloud Staging Owner Review Recovery - 2026-05-24

Status: source and app-mirror fixes are pushed, hosted staging product/cart
proof passes, and final payment handoff is blocked by staging payment-secret
configuration.

This is the umbrella handoff for the recovery that started from the trusted
restore point and moved the owner-review staging site forward again. Keep this
file short and link feature details instead of expanding it into a release
monolith.

## Source Points

| Surface | Restore point | Current point | Notes |
|---|---|---|---|
| Full repo | `c668543 Restore trusted staging source` | `203127a Hide unsafe checkout provider errors` | `main` and `origin/main` matched at this point before documentation work. |
| Frappe app mirror | `8d69683` | `9ce07f2` | GitHub compare showed the mirror ahead by 7 commits and behind by 0. |
| Hosted staging | `https://locallytwisted-staging.frappe.cloud` | owner-review candidate | Product/cart route tests pass; payment provider handoff is blocked. |

Full-repo commits after the trusted restore:

- `273cb25 Fix mobile footer columns`
- `4d5c287 Fix product gallery thumbnail copy`
- `70b8869 Fix staging checkout product flow`
- `203127a Hide unsafe checkout provider errors`

App-mirror commits after the staging restore point:

- `37a3a24 Fix mobile footer columns`
- `0649139 Deploy mobile footer to staging press-deploy-bench-40102`
- `2f7e2c3 Fix product gallery thumbnail copy`
- `dd00249 Deploy product gallery to staging press-deploy-bench-40102`
- `a4a0fc0 Fix staging checkout product flow press-deploy-bench-40102`
- `5bb9326 Hide unsafe checkout provider errors press-deploy-bench-40102`
- `9ce07f2 Trigger staging checkout safety deploy press-deploy-bench-40102`

## Feature Handoffs

- Mobile footer columns:
  `workstreams/mobile-footer-columns-staging-2026-05-24.md`
- Product gallery staging follow-up:
  `workstreams/ecommerce-audit/product-gallery-staging-followup-2026-05-24.md`
- Checkout product flow and payment blocker:
  `workstreams/ecommerce-audit/staging-checkout-product-flow-2026-05-24.md`
- Payment failure recipe:
  `capabilities/failures/frappe-cloud-staging-stripe-secret-drift.md`
- Launch/payment gate:
  `capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`
- Decision packet:
  `decisions/2026-05-24-staging-owner-review-recovery.md`

## What Changed After The Restore

1. Mobile footer:
   the mobile footer link groups were returned to a three-column layout instead
   of stacking as one column.
2. Product gallery:
   the visible "Other product photos" label was removed, and configured
   products keep the base product photo available after selecting another
   gallery or variant image.
3. Cart/header:
   add-to-cart now updates a visible cart-count badge in the header.
4. Checkout summary:
   product rows in checkout order summary now link back to the original product
   route.
5. Checkout contact and pickup UX:
   email/phone helper copy says the contact fields are used only for order
   updates, checkout has a preferred-contact-method field, and pickup windows
   render in AM/PM from operating-hour rules.
6. Configured product checkout:
   checkout resolves priced ERPNext variants for SKU-defining Product Setup
   groups even when option labels contain commas, so valid configured bouquet
   selections no longer fail as product setup review errors.
7. Checkout error safety:
   source now shields provider/decryption wording from customer-facing checkout
   errors. Operators still need the exact server-side error in logs.

## Hosted Staging Proof

Fresh public staging proof during the documentation pass:

```powershell
$env:LT_BASE_URL='https://locallytwisted-staging.frappe.cloud'
npm run test:checkout-experience
npm run test:product-gallery-experience
```

Observed results:

- `test:checkout-experience` passed `3/3`.
- `test:product-gallery-experience` passed `4/4`.
- Raw staging checkout HTML included `Preferred contact method` and
  `pickupWindowRules`.

Earlier recovery proof in the same lane found the final submit reached the
payment setup layer and failed on staging payment-secret configuration:
`Stripe Settings.Test.secret_key` could not be decrypted in the current staging
site context. Treat that as a staging provider/configuration blocker, not as a
product setup blocker.

## Indexed Conversation And GitHub Review

Memory/indexed-conversation lookup was used as orientation for the older
checkout-path, ecommerce architecture, and product-page gallery lanes. Current
release facts in this handoff come from git history, GitHub compare evidence,
hosted staging tests, and the observed payment blocker.

Do not treat old handoffs, older indexed conversation claims, or local-only
proof as staging authority unless they are rechecked against the current source
and hosted staging URL.

## Next Safe Step

Repair staging payment configuration before owner card-path testing:

1. In staging Desk/provider context, re-enter the test secret key for
   `Stripe Settings` or restore the correct site encryption key if this staging
   database was restored/copied from another site.
2. Confirm the staging Payment Gateway Account and payment method configuration
   point at the intended test-mode settings.
3. Clear staging website/cache after settings repair.
4. Rerun:

```powershell
$env:LT_BASE_URL='https://locallytwisted-staging.frappe.cloud'
npm run test:checkout-experience
npm run test:product-gallery-experience
python scripts\verify\payment_backend_config_contract.py
python scripts\verify\payment_webhook_contract.py
python scripts\verify\stripe_amount_parity_contract.py
```

5. Only after staging payment config passes, run one authorized test checkout
   all the way through Stripe test mode and verify the ERPNext records, customer
   receipt, operator email, tax, and payment status before owner review.

## Boundaries

- This is staging-owner-review work only.
- This does not approve live checkout.
- This does not authorize DNS, Search Console, live Stripe, live payment keys,
  or production data mutation.
- The app mirror is a deploy artifact, not the full repo source of truth.
- A source push or mirror push is not enough. Hosted staging proof must still
  pass after Frappe Cloud deploy/update/cache behavior settles.

## Backlinks

- `CODING-HANDOFF.md`
- `ECOMMERCE-SHOP-HANDOFF.md`
- `LT-LAUNCH-RUNBOOK.md`
- `locally-twisted-queue.md`
- `decisions/2026-05-24-staging-owner-review-recovery.md`
- `locally-twisted-decisions.md`
- `lessons-learned.md`
- `workstreams/frappe-cloud-cloudflare-stripe-launch-2026-05-11.md`
- `workstreams/payment-backend-launch-readiness.md`
