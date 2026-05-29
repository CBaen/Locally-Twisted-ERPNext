# Live Shop Discovery Release - 2026-05-29

Status: historical planning record. Current live decision packet is
`live-shop-discovery-go-no-go-2026-05-29.md`.

Do not deploy from this planning note. Some anchors below were correct when
written but are now stale. The current exact live target is Frappe Cloud release
`c81v7r3b67` at app mirror hash
`cc5426401b4d3f69a57b8efb77320d943c5c95ea`.

No live deployment, provider change, site-config change, product-data mutation,
ERPNext production mutation, Stripe change, DNS/Search Console action, or email
sending has been performed by this slice.

## Plain-English Goal

Get the public shop visible enough for customers, Google, and marketing work
without opening live buying yet.

This release separates two things that were previously tied together:

- shop/category/product discovery can be public;
- cart, checkout, payment, order creation, email, and ERPNext purchase mutation
  remain blocked.

## Why This Is The Safe Next Step

The site needs public product discovery for indexing and campaigns, but live
checkout still needs its own production payment and operations release packet.
Opening the whole ecommerce switch would expose cart and checkout at the same
time as the shop. That is too much blast radius for this moment.

The safer live mode is:

- `lt_ecommerce_paused=1`
- `lt_shop_discovery_open=1`
- `lt_checkout_paused=1`
- `lt_public_indexing_enabled=1`

That means the broad ecommerce lock stays on, the shop-discovery door opens,
and checkout has an explicit lock of its own.

## Current Verified Anchors

- Live public site currently runs app mirror branch
  `live-seo-indexing-20260528` at
  `5bbdc484d86729c4f2afdf7776e9f6649b02c080`.
- Live is attached to Frappe Cloud bench
  `bench-39776-000016-f94-virginia` in the latest provider proof.
- Hosted live `/shop`, `/cart`, `/checkout`, and product routes currently
  redirect to `/ready-to-order-paused` with `noindex, follow`.
- Staging currently runs app mirror `main` at
  `ad0a408c2df5ecb711062f35887b94520220b2c8` on
  `bench-40102-000027-f4-virginia`.
- Staging `/shop`, `/cart`, `/checkout`, and representative product routes
  rendered successfully after the approved staging release execution.

## Blast Radius

There are two layers of blast radius.

The already-approved staging release candidate is much larger than the current
live indexing hotfix: the app-mirror diff from live `5bbdc48` to staged
`ad0a408` is `243` files, `33,530` insertions, and `828` deletions.

This source slice is intentionally smaller on top of that staged candidate:
it changes pause controls, SEO/sitemap behavior, navigation/footer exposure,
shop/product CTAs, checkout API guarding, and mode verifiers.

## Source Implementation Boundary

This slice may change:

- `ecommerce_pause.py` exposure helpers;
- SEO and sitemap indexing rules;
- navigation/footer shop/cart visibility;
- shop-card and product-page CTAs while checkout is paused;
- checkout API guard source;
- source-level verifiers and package scripts;
- this release planning record.

This slice must not change:

- Stripe keys or payment provider mode;
- DNS or Search Console;
- production data or product catalog records;
- ERPNext production records;
- customer/order/payment/email sending behavior;
- live provider state without separate release approval.

## Verification Required Before Live Approval

Source-only:

```powershell
python -m py_compile apps\locally_twisted\locally_twisted\ecommerce_pause.py apps\locally_twisted\locally_twisted\seo.py apps\locally_twisted\locally_twisted\www\sitemap.py apps\locally_twisted\locally_twisted\website_context.py apps\locally_twisted\locally_twisted\navbar_context.py apps\locally_twisted\locally_twisted\www\checkout.py scripts\verify\ecommerce_expected_mode.py scripts\verify\ecommerce_pause_contract.py scripts\verify\shop_discovery_checkout_pause_contract.py
npm run test:shop-discovery-gate
git diff --check
```

Hosted live after explicit approval and deployment:

```powershell
$env:LT_BASE_URL='https://locallytwisted.com'
npm run test:seo-contract
npm run test:search-contract
python scripts\verify\cloudflare_launch_readiness.py --base-url https://locallytwisted.com
python scripts\verify\public_asset_integrity.py --base-url https://locallytwisted.com
```

Manual hosted route expectations after release:

- `/shop` returns `200`, is indexable, and shows product discovery.
- representative `/shop-items/...` routes return `200`, are indexable, and show
  product details without add-to-cart purchase controls.
- `/cart` and `/checkout` still redirect to `/ready-to-order-paused`.
- checkout APIs still return a customer-safe blocked response and do not create
  Customer, Contact, Address, Sales Order, Payment Request, Stripe Session, or
  email records.
- `sitemap.xml` includes public shop/product discovery URLs and excludes cart,
  checkout, and pause routes.

## Live Approval Needed Later

The next approval, when requested, must be specific to Locally Twisted live
only and must include:

- using the local Frappe Cloud credential without printing secrets;
- re-verifying current live source identity immediately before mutation;
- updating the app mirror to the reviewed shop-discovery source;
- deploying/updating `locally_twisted` on `locallytwisted.com`;
- setting the live site-config flags listed above;
- running the required update/migrate/cache-clear steps;
- running hosted live verification afterward.

It must still exclude live checkout, live Stripe, DNS, Search Console,
production data mutation, ERPNext production record mutation, product catalog
changes, email sending beyond passive system behavior, and live payment tests.

## Rollback Shape

Rollback is simple if this release misbehaves:

1. Set `lt_shop_discovery_open=0`.
2. Keep or set `lt_checkout_paused=1`.
3. Clear website cache.
4. Confirm `/shop`, `/cart`, `/checkout`, and representative product routes
   return to `/ready-to-order-paused`.
5. If code rollback is needed, restore live app source to the prior live
   indexing hotfix commit `5bbdc484d86729c4f2afdf7776e9f6649b02c080`.
