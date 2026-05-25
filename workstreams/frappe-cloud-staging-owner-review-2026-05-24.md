# Frappe Cloud Staging Owner Review Recovery - 2026-05-24

Status: source and app-mirror fixes are pushed, hosted staging product/cart
proof passes, and hosted staging Stripe test-mode checkout now reaches paid
ERPNext records.

This is the umbrella handoff for the recovery that started from the trusted
restore point and moved the owner-review staging site forward again. Keep this
file short and link feature details instead of expanding it into a release
monolith.

## Source Points

| Surface | Restore point | Current point | Notes |
|---|---|---|---|
| Full repo | `c668543 Restore trusted staging source` | `8913160 Document shop taxonomy implementation` | `main` and `origin/main` include the approved shop taxonomy implementation and docs. |
| Frappe app mirror | `8d69683` | `bb19a4b` | App-root mirror was synced from current app root for staging-only owner review. |
| Hosted staging | `https://locallytwisted-staging.frappe.cloud` | owner-review candidate | Product/cart route tests pass; Stripe test-mode checkout and ERPNext paid-order records passed; approved taxonomy is staged. |

Full-repo commits after the trusted restore:

- `273cb25 Fix mobile footer columns`
- `4d5c287 Fix product gallery thumbnail copy`
- `70b8869 Fix staging checkout product flow`
- `203127a Hide unsafe checkout provider errors`
- `55942f0 Document approved shop taxonomy map`
- `1a72d27 Apply approved shop taxonomy`
- `8913160 Document shop taxonomy implementation`

App-mirror commits after the staging restore point:

- `37a3a24 Fix mobile footer columns`
- `0649139 Deploy mobile footer to staging press-deploy-bench-40102`
- `2f7e2c3 Fix product gallery thumbnail copy`
- `dd00249 Deploy product gallery to staging press-deploy-bench-40102`
- `a4a0fc0 Fix staging checkout product flow press-deploy-bench-40102`
- `5bb9326 Hide unsafe checkout provider errors press-deploy-bench-40102`
- `9ce07f2 Trigger staging checkout safety deploy press-deploy-bench-40102`
- `bb19a4b Sync shop taxonomy staging app`

## Feature Handoffs

- Mobile footer columns:
  `workstreams/mobile-footer-columns-staging-2026-05-24.md`
- Product gallery staging follow-up:
  `workstreams/ecommerce-audit/product-gallery-staging-followup-2026-05-24.md`
- Checkout product flow and payment proof:
  `workstreams/ecommerce-audit/staging-checkout-product-flow-2026-05-24.md`
- Approved primary/secondary shop taxonomy:
  `workstreams/ecommerce-audit/shop-primary-secondary-taxonomy-map-2026-05-24.md`
- Payment failure recipe:
  `capabilities/failures/frappe-cloud-staging-stripe-secret-drift.md`
- Email failure recipe:
  `capabilities/failures/frappe-cloud-staging-email-secret-drift.md`
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
8. Shop taxonomy:
   primary shop categories now use physical product types, secondary categories
   use broad occasions/use cases, and duplicate product routes for `easter-arch`
   and `pride-arch` stay gone. Product names were not changed.

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

Later hosted proof in the same lane repaired the staging provider config and
completed one Stripe test-mode payment:

- `Stripe Settings / Test` secret key was re-entered on staging.
- `npm run test:checkout-experience` passed `3/3` against staging after repair.
- Hosted checkout for `/shop-items/bouquets/encanto-bouquet` reached Stripe
  Checkout, completed a test-mode payment, and returned to
  `/thank-you?order=SAL-ORD-2026-00024`.
- ERPNext Desk showed Sales Order `SAL-ORD-2026-00024`, Payment Request
  `ACC-PRQ-2026-00021` as `Paid`, and Sales Invoice `ACC-SINV-2026-00004`
  as `Paid` with grand total `$37.61` and outstanding amount `$0.00`.
- Staging Email Account password was re-entered; receipt Email Queue
  `cchsjbegpi` and operator Email Queue `cchtiiieuk` reached `Sent`.
- The staging owner user `locallytwisted@gmail.com` was reset to the documented
  staging temporary password through Administrator/System Console and verified
  in a clean browser session. It landed at `/app/Workspaces/Owner%20Home` with
  title `Owner Home`.

Latest hosted taxonomy release proof:

- App mirror `bb19a4b` was selected as the only app update in Frappe Cloud.
- Bench deploy `2ve3dgt97a` succeeded.
- Site migration job `22jih1qaln` succeeded for
  `locallytwisted-staging.frappe.cloud`.
- Frappe Cloud cache clear completed through the site action.
- `npm run test:search-contract` passed `4/4` against staging.
- `npm run test:product-gallery-experience` passed `4/4` against staging.
- `npm run test:checkout-experience` passed `3/3` against staging.
- `shop_category_hero_images.spec.js` passed `25/25` against staging.
- `public_asset_integrity.py --base-url https://locallytwisted-staging.frappe.cloud`
  passed for `31` routes and `315` local asset URLs.
- Public route probes returned `200` for `/shop`,
  `/shop-items/photo-ops-backdrops`, `/shop-items/stands-easels`,
  `/shop-items/arches/easter-balloon-arch-bunny-ear`, and
  `/shop-items/arches/pride-progress-rainbow-balloon-arch`; duplicate routes
  `/shop-items/arches/easter-arch` and `/shop-items/arches/pride-arch`
  returned `404`.
- A transient Frappe Cloud Bad Gateway was observed once immediately after
  cache clear and cleared on the next public health probe; `/` and `/shop`
  returned `200` afterward, and hosted tests were rerun successfully.

Earlier failure evidence still matters as the guard: final submit first reached
the payment setup layer and failed because `Stripe Settings.Test.secret_key`
could not be decrypted in the current staging site context. Treat future
instances as staging provider/configuration drift, not Product Setup failure.

## Indexed Conversation And GitHub Review

Memory/indexed-conversation lookup was used as orientation for the older
checkout-path, ecommerce architecture, and product-page gallery lanes. Current
release facts in this handoff come from git history, GitHub compare evidence,
hosted staging tests, and the observed payment blocker.

Do not treat old handoffs, older indexed conversation claims, or local-only
proof as staging authority unless they are rechecked against the current source
and hosted staging URL.

## Next Safe Step

Before handing the owner a checkout review path, keep the boundaries explicit:
staging test checkout is usable; live checkout is not approved by this proof.
Rerun the route proof if more source or provider settings change:

```powershell
$env:LT_BASE_URL='https://locallytwisted-staging.frappe.cloud'
npm run test:checkout-experience
npm run test:product-gallery-experience
python scripts\verify\payment_backend_config_contract.py
python scripts\verify\payment_webhook_contract.py
python scripts\verify\stripe_amount_parity_contract.py
```

The connected Gmail MCP account was `cameronbpaul@gmail.com`, so it could not
verify inbox-visible delivery for `locallytwisted@gmail.com`. Email Queue
`Sent` proves Frappe/Gmail SMTP acceptance only. Ask the owner/reviewer to check
the recipient inbox during their staging review if inbox-visible receipt
delivery is part of the approval.

The owner can now review both the public storefront and the Desk owner surface
on staging. Keep any further credential changes staged/provider-local unless GL
explicitly approves live account work.

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
