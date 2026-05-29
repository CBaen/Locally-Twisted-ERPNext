# Staging Shop Discovery Verification - 2026-05-29

Status: PASS for Locally Twisted staging shop-discovery review only.

This is not live approval. It does not approve live deployment, live checkout,
live Stripe, DNS, Search Console, product/catalog mutation, production data
mutation, ERPNext production record mutation, or email sending outside
staging/test-mode verification.

## Plain Meaning

Staging now proves the intended safe shop-discovery mode:

- customers can browse the shop and product pages;
- cart and checkout remain paused;
- direct checkout APIs are blocked before creating customer, order, payment, or
  email records;
- staging stays `noindex` while the live site remains the only public-indexing
  target.

## Source And Provider Identity

- Staging URL: `https://locallytwisted-staging.frappe.cloud`
- Frappe Cloud site status: `Active`
- Frappe Cloud bench: `bench-40102-000028-f4-virginia`
- App: `locally_twisted`
- App mirror branch: `live-shop-discovery-20260529`
- App mirror hash deployed on staging:
  `cc5426401b4d3f69a57b8efb77320d943c5c95ea`
- App release: `c81v7r3b67`
- Approved source branch for the staged app code:
  `codex/lt-live-shop-discovery-gate`
- Approved source commit for the staged app code:
  `423bd044353cb7170508bbaa22ea4326afc30b2b`

Repo verifier fixes were made after the staging app deployment so the local
release checks understand shop-discovery mode. Those verifier changes do not
change the staged Frappe app hash above.

## Staging Site Config

Frappe Cloud site config confirmed:

- `lt_ecommerce_paused=1`
- `lt_shop_discovery_open=1`
- `lt_checkout_paused=1`
- `lt_public_indexing_enabled=0`

Plain meaning: staging can prove browse-only shop behavior, but staging must
remain `noindex`. Live indexability still has to be verified on
`https://locallytwisted.com` after a separate live approval sets live indexing.

## Hosted Route Proof

Verified hosted route shape:

- `/` returns `200`.
- `/shop` returns `200`.
- `/shop-items/garlands/graduation-grab-n-go` returns `200`.
- `/cart` lands on `/ready-to-order-paused`.
- `/checkout` lands on `/ready-to-order-paused`.
- `/ready-to-order-paused` returns `200`.
- `/sitemap.xml` returns `200`.
- `/robots.txt` returns `200`.

Rendered control proof:

- `/shop` has `0` visible purchase controls on desktop and mobile.
- representative product page has `0` visible enabled purchase controls on
  desktop and mobile.
- product page shows a disabled quote-oriented primary control plus a visible
  `Request a Quote` path.

## No-Checkout Mutation Proof

Direct staging API probes:

- `preview_checkout_totals`: HTTP `403`
- `submit_guest_order`: HTTP `403`
- API body contains the customer-safe paused checkout message when checked with
  `curl`.

Record counts before and after the API probes:

| Record | Before | After | Delta |
|---|---:|---:|---:|
| Customer | 15 | 15 | 0 |
| Contact | 19 | 19 | 0 |
| Address | 8 | 8 | 0 |
| Sales Order | 11 | 11 | 0 |
| Payment Request | 11 | 11 | 0 |
| Email Queue | 29 | 29 | 0 |
| Communication | 11 | 11 | 0 |

Fail-loud proof:

- `tabError Log` gained the expected `LT paused checkout API blocked` entries.
- No recent unexpected ERPNext Error Log methods were found after the release;
  the only recent method was `LT paused checkout API blocked`.

## Test Evidence

Passed:

- `npm run test:release-prevention`
- `python scripts\release\release_status_report.py`
- `npm run test:shop-discovery-gate`
- `python scripts\verify\verifier_cli_contract.py`
- `npm run test:seo-contract`
- `npm run test:search-contract`
- `npm run test:a11y`
- `npm run test:checkout-experience`
- `npm run test:product-gallery-experience`
- `python scripts\verify\public_asset_integrity.py --base-url https://locallytwisted-staging.frappe.cloud`
- `python scripts\verify\public_home_identity.py --base-url https://locallytwisted-staging.frappe.cloud`
- `scripts\verify\run_playwright.cmd test scripts/verify/layout_fit.spec.js --reporter=line --workers=4`
- `npm audit --omit=dev --audit-level=high`
- `git diff --check 312e75475f9ba3d44351ba9736e7deab9477e7e7..423bd044353cb7170508bbaa22ea4326afc30b2b`
- `python -B -m py_compile` for changed Python app and verifier files
- `node --check` for changed JavaScript verifier files

Not used as staging proof:

- `python scripts\verify\website_launch_verify.py --base-url ...`

Reason: the umbrella launch verifier still includes local-bench and full
checkout assumptions that are broader than this staging shop-discovery mode.
The failing parts were narrowed into direct staging checks above, and the
mode-aware verifier gaps were fixed.

## SEO, AEO, GEO, And Sitemap Proof

- SEO/AEO/GEO contract passed `13/13`.
- Sitemap includes the current canonical shop/category routes:
  `/shop`, `/all-products`, `/shop-items`, `/shop-items/arches`,
  `/shop-items/balloon-drops`, `/shop-items/bouquets`,
  `/shop-items/columns`, `/shop-items/garlands`,
  `/shop-items/photo-ops-backdrops`, `/shop-items/stands-easels`, and
  `/shop-items/table-decor`.
- Sitemap excludes cart, checkout, pause route, and legacy category routes such
  as `/shop-items/seasonal-specialty`.
- `robots.txt` advertises the current-host sitemap.
- Staging pages remain `noindex, follow` by config.

## Accessibility And Layout Proof

- Axe accessibility passed `48` route/viewport results with `0` violations.
- Full passive layout matrix passed `312/312` staging checks.
- A focused shop-discovery route/mobile pass also showed `0` layout failures
  across home, contact, shop, representative product, cart, checkout, and pause
  pages at mobile and desktop sizes.

## Provider Job And Log Proof

Recent Frappe Cloud staging jobs:

- `Update Site Migrate`: `Success`
- `Update Site Configuration`: `Success`
- `Clear Cache`: `Success`

Recent ERPNext Error Log review:

- only expected paused-checkout API block entries were found in the checked
  release window.

## Security Gate

- No secrets were printed.
- No live provider, DNS, Search Console, live Stripe, or production data
  surfaces were touched.
- `npm audit --omit=dev --audit-level=high` found `0` vulnerabilities.
- Checkout API guard blocks before customer/order/payment/email mutation.
- Payment readiness check reported Stripe test-mode configuration, not live
  Stripe release approval.

## Decision

PASS for staging shop-discovery verification and owner-review/live-prep
evidence.

The next professional step is a separate live release decision packet for
`https://locallytwisted.com`, using the same browse-only mode:

- `lt_ecommerce_paused=1`
- `lt_shop_discovery_open=1`
- `lt_checkout_paused=1`
- `lt_public_indexing_enabled=1`

That later live decision still must not include live checkout, live Stripe,
DNS, Search Console submission/removal, product/catalog mutation, production
data mutation, ERPNext production record mutation, or email sending beyond
passive live site behavior.
