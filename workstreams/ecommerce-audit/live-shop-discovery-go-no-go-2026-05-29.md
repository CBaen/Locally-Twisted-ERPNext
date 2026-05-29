# Live Shop Discovery Go/No-Go Packet - 2026-05-29

Status: SUPERSEDED BY LIVE EXECUTION NO-GO.

The approved live execution was attempted after this packet and did not launch.
Use `live-shop-discovery-deployment-execution-2026-05-29.md` as the current
release-control record before any further live action. The blocker is live
catalog/data parity: Frappe Cloud recovered after
`locally_twisted.patches.sync_shop_taxonomy_20260524` failed on missing live
product `Item` records.

Do not deploy from this packet without a new remediation slice, staging proof,
and fresh live approval.

This packet is for `https://locallytwisted.com` only. It prepares the live
shop-discovery release decision after staging passed browse-only shop proof.
It does not approve live checkout, live Stripe, DNS, Search Console,
product/catalog mutation, production data mutation, ERPNext production record
mutation, product data changes, email sending, or live payment tests.

## Plain Meaning

The safe launch target is:

- customers and search engines can see the shop, category, and product pages;
- cart and checkout stay paused;
- direct checkout APIs stay blocked before creating customer, order, payment,
  Stripe, or email records;
- live public indexing stays enabled.

This is the professional next slice because marketing and indexing need public
shop discovery now, while live buying still deserves a separate payment and
operations release.

## Current Approval State

Live mutation is not approved by this packet.

Older approval text referenced an earlier shop-discovery hash. The current
staging-tested target is the newer Frappe Cloud next release:

- app mirror branch: `live-shop-discovery-20260529`
- app mirror target hash:
  `cc5426401b4d3f69a57b8efb77320d943c5c95ea`
- Frappe Cloud app release: `c81v7r3b67`
- release message: `Add live shop discovery host fallback`

Any live approval must name this exact hash and release. A branch name alone is
not enough because the branch already had an older hash on live release-group
state.

## Source And App Mirror Proof

- Source evidence branch:
  `codex/lt-staging-release-candidate-freeze`
- Source evidence commit:
  `3eb8294dd88157e7483832c88c632bb40497b686`
- Staged app source branch:
  `codex/lt-live-shop-discovery-gate`
- Staged app source commit:
  `423bd044353cb7170508bbaa22ea4326afc30b2b`
- App mirror repo:
  `https://github.com/CBaen/Locally-Twisted-Frappe-App.git`
- App mirror branch `live-shop-discovery-20260529`:
  `cc5426401b4d3f69a57b8efb77320d943c5c95ea`
- App mirror `main` remains:
  `ad0a408c2df5ecb711062f35887b94520220b2c8`
- Prior live SEO branch remains:
  `5bbdc484d86729c4f2afdf7776e9f6649b02c080`

## Live Provider Proof

Frappe Cloud API proof used the local `.env` credential without recording secret
values in this packet. Current Frappe Cloud docs require `Authorization` and
`X-Press-Team` headers for API requests. The docs also warn that some API
endpoints may shift with UI refactors, so this packet used the currently
working redirected API host `cloud.frappe.io` after `frappecloud.com` returned a
permanent redirect.

Provider state:

- API account context: `locallytwisted@gmail.com`
- Frappe Cloud site object: `locallytwisted.v.frappe.cloud`
- Public live domain: `https://locallytwisted.com`
- Site status: `Active`
- Release group: `bench-39776`
- Current live bench: `bench-39776-000016-f94-virginia`
- Server: `f94-virginia.frappe.cloud`
- Region: `N. Virginia, USA`
- Last deployed: `2026-05-29 22:51:20.833770`

Current installed live app:

- app: `locally_twisted`
- installed branch: `live-seo-indexing-20260528`
- installed hash: `5bbdc484d86729c4f2afdf7776e9f6649b02c080`

Current release-group app state:

- branch: `live-shop-discovery-20260529`
- current release-group hash:
  `26ef3d32ea70ddec18ede25261f2431dde22adbb`
- update available: `true`
- next release: `c81v7r3b67`
- next release hash:
  `cc5426401b4d3f69a57b8efb77320d943c5c95ea`
- deploy in progress: `false`
- running release pipeline: `false`

Important release-control meaning: live has not yet installed the
shop-discovery app hash. The release group can see the correct next release,
but the live site is still serving the older SEO indexing app commit.

## Live Site Config

Live site config already confirms:

- `lt_ecommerce_paused=1`
- `lt_shop_discovery_open=1`
- `lt_checkout_paused=1`
- `lt_public_indexing_enabled=1`

Plain meaning: live settings are already in the desired browse-only mode, but
the installed app code is still too old for `/shop` to open. The app update is
what should move live shop pages from paused to discoverable.

## Recent Provider Jobs

Recent live Frappe Cloud jobs:

| Job | Status | Created |
|---|---|---|
| `Migrate Site` | `Success` | `2026-05-29 23:07:13.495197` |
| `Clear Cache` | `Success` | `2026-05-29 22:58:19.185162` |
| `Update Site Configuration` | `Success` | `2026-05-29 22:58:18.019556` |
| `Clear Cache` | `Success` | `2026-05-29 22:56:23.420066` |
| `Update Site Configuration` | `Success` | `2026-05-29 22:56:22.080279` |
| `Recover Failed Site Migrate` | `Success` | `2026-05-29 22:52:55.134451` |
| `Update Site Migrate` | `Failure` | `2026-05-29 22:51:21.039181` |
| `Update Site Migrate` | `Success` | `2026-05-29 20:07:52.786418` |

Release meaning: there was a live migrate failure, but Frappe Cloud later
recorded a successful recovery and a newer successful migrate/cache/config
sequence. This is not hidden; it must be watched after release.

## Staging Final Snapshot

Snapshot file:
`.tmp/release-snapshots/lt-staging-final-shop-discovery-2026-05-29.json`

Staging URL: `https://locallytwisted-staging.frappe.cloud`

Key route shape:

| Route | Staging final result |
|---|---|
| `/` | `200`, home title |
| `/shop` | `200`, `Ready-to-Order Balloon Decor` |
| `/all-products` | `200`, `Ready-to-Order Balloon Decor` |
| `/shop-items` | `200`, `Ready-to-Order Balloon Decor` |
| `/shop-items/garlands` | `200`, `Garlands` |
| `/shop-items/table-decor` | `200`, `Table Decor` |
| `/shop-items/garlands/graduation-grab-n-go` | `200`, product title |
| `/cart` | `200`, final URL `/ready-to-order-paused?from=%2Fcart` |
| `/checkout` | `200`, final URL `/ready-to-order-paused?from=%2Fcheckout` |
| `/ready-to-order-paused` | `200`, paused title |
| `/sitemap.xml` | `200` |
| `/robots.txt` | `200` |

No snapshot HTTP failures were recorded.

## Live Before Snapshot

Snapshot file:
`.tmp/release-snapshots/lt-live-before-shop-discovery-2026-05-29.json`

Live URL: `https://locallytwisted.com`

Key route shape before live deployment:

| Route | Live-before result |
|---|---|
| `/` | `200`, home title |
| `/shop` | final URL `/ready-to-order-paused?from=%2Fshop` |
| `/all-products` | final URL `/ready-to-order-paused?from=%2Fall-products` |
| `/shop-items` | final URL `/ready-to-order-paused?from=%2Fshop-items` |
| `/shop-items/garlands` | final URL `/ready-to-order-paused?from=%2Fshop-items%2Fgarlands` |
| `/shop-items/table-decor` | final URL `/ready-to-order-paused?from=%2Fshop-items%2Ftable-decor` |
| `/shop-items/garlands/graduation-grab-n-go` | final URL `/ready-to-order-paused?from=%2Fshop-items%2Fgarlands%2Fgraduation-grab-n-go` |
| `/cart` | final URL `/ready-to-order-paused?from=%2Fcart` |
| `/checkout` | final URL `/ready-to-order-paused?from=%2Fcheckout` |
| `/ready-to-order-paused` | `200`, paused title |
| `/sitemap.xml` | `200` |
| `/robots.txt` | `200` |

No snapshot HTTP failures were recorded.

## Snapshot Comparison

Comparison file:
`.tmp/release-snapshots/lt-staging-final-vs-live-before-shop-discovery-2026-05-29.json`

Result:

- `ok: true`
- critical changes: none
- expected differences: staging shop/category/product pages are open; live
  shop/category/product pages still land on the paused page.

Plain meaning: this is exactly the gap the live release is supposed to close.

## Staging Verification Reference

Use `staging-shop-discovery-verification-2026-05-29.md` as the staging proof
packet.

That packet records:

- hosted staging deployed app hash
  `cc5426401b4d3f69a57b8efb77320d943c5c95ea`;
- `/shop` and representative product/category routes open;
- `/cart` and `/checkout` remain paused;
- direct checkout APIs return `403`;
- Customer, Contact, Address, Sales Order, Payment Request, Email Queue, and
  Communication counts do not change after blocked API probes;
- expected fail-loud Error Log entries are created for blocked checkout API
  attempts;
- SEO/AEO/GEO, search, accessibility, layout, asset, home identity, and
  security checks passed for staging browse-only mode.

## GO Conditions For Live Approval

The release is GO only if all of these remain true immediately before mutation:

- live installed `locally_twisted` app is still
  `5bbdc484d86729c4f2afdf7776e9f6649b02c080` or another explicitly reviewed
  predecessor;
- live Frappe Cloud next release for `locally_twisted` is still
  `c81v7r3b67` at
  `cc5426401b4d3f69a57b8efb77320d943c5c95ea`;
- app mirror branch `live-shop-discovery-20260529` still points to
  `cc5426401b4d3f69a57b8efb77320d943c5c95ea`;
- no deploy or release pipeline is already running;
- Frappe Cloud will update only the `locally_twisted` app for this release;
- Frappe, ERPNext, Payments, and Webshop framework/app dependency upgrades stay
  out of this live slice;
- site config remains browse-only:
  `lt_ecommerce_paused=1`, `lt_shop_discovery_open=1`,
  `lt_checkout_paused=1`, `lt_public_indexing_enabled=1`.

## NO-GO Conditions

Stop before live mutation if:

- the target release hash differs from
  `cc5426401b4d3f69a57b8efb77320d943c5c95ea`;
- Frappe Cloud tries to bundle Frappe, ERPNext, Payments, or Webshop updates
  into this slice;
- a deploy or release pipeline is already running;
- recent provider jobs show a newer unrecovered failure;
- live site config cannot be read without exposing secrets;
- the public domain no longer resolves to the expected Frappe Cloud site;
- live route proof changes in a way that makes the expected before/after
  comparison unreliable.

## Live Execution Plan After Exact Approval

1. Re-read live provider identity and target release hash.
2. Confirm app mirror branch head still equals
   `cc5426401b4d3f69a57b8efb77320d943c5c95ea`.
3. Confirm live config flags still match browse-only mode.
4. Update/deploy only `locally_twisted` to Frappe Cloud release `c81v7r3b67`.
5. Run the required live site update/migrate/cache-clear steps once.
6. Create a live-after snapshot.
7. Compare staging-final against live-after.
8. Run hosted live verification.
9. Watch provider jobs and ERPNext Error Logs after release.

## Hosted Live Verification Required After Deployment

Run against `https://locallytwisted.com`:

- `/` returns `200`.
- `/shop`, `/all-products`, `/shop-items`, representative category routes, and
  representative product route return `200` and are indexable.
- `/cart` and `/checkout` land on `/ready-to-order-paused`.
- `/ready-to-order-paused` returns `200` and remains `noindex, follow`.
- `/sitemap.xml` includes current public shop/category/product discovery URLs.
- `/sitemap.xml` excludes cart, checkout, pause route, and legacy categories.
- `/robots.txt` advertises the live-domain sitemap.
- `npm run test:seo-contract` passes with `LT_BASE_URL=https://locallytwisted.com`.
- `npm run test:search-contract` passes with `LT_BASE_URL=https://locallytwisted.com`.
- `python scripts\verify\public_asset_integrity.py --base-url https://locallytwisted.com` passes.
- `python scripts\verify\public_home_identity.py --base-url https://locallytwisted.com` passes.
- A no-checkout live guard proves direct checkout APIs remain blocked before
  customer/order/payment/email mutation.
- Recent Frappe Cloud jobs are successful or have explicit recovered status.
- Recent ERPNext Error Logs contain only expected paused-checkout guard entries
  from verification.

## Rollback Plan

Fast config rollback:

1. Set `lt_shop_discovery_open=0`.
2. Keep `lt_ecommerce_paused=1` and `lt_checkout_paused=1`.
3. Clear website cache.
4. Confirm `/shop`, category routes, product routes, `/cart`, and `/checkout`
   return to the paused page.

Code rollback if config rollback is not enough:

1. Restore `locally_twisted` live app to branch `live-seo-indexing-20260528`
   at `5bbdc484d86729c4f2afdf7776e9f6649b02c080`.
2. Run required migrate/cache-clear steps once.
3. Confirm the live-before paused route shape has returned.
4. Record the rollback packet with provider job IDs and route proof.

## Decision

READY FOR EXACT LIVE APPROVAL.

Recommended approval text:

> I approve the Locally Twisted live shop-discovery release for
> https://locallytwisted.com only, using Frappe Cloud site
> locallytwisted.v.frappe.cloud, app mirror branch
> live-shop-discovery-20260529 at
> cc5426401b4d3f69a57b8efb77320d943c5c95ea, and source evidence branch
> codex/lt-staging-release-candidate-freeze at
> 3eb8294dd88157e7483832c88c632bb40497b686 / staged app source branch
> codex/lt-live-shop-discovery-gate at
> 423bd044353cb7170508bbaa22ea4326afc30b2b. This approval includes using the
> local Frappe Cloud credential without printing secrets, re-verifying current
> live source identity, updating only the locally_twisted app to Frappe Cloud
> release c81v7r3b67 at
> cc5426401b4d3f69a57b8efb77320d943c5c95ea, keeping
> lt_ecommerce_paused=1, lt_shop_discovery_open=1, lt_checkout_paused=1, and
> lt_public_indexing_enabled=1, running required live app update/site
> update/migrate/cache-clear steps, and running hosted live verification
> afterward. This does not approve live checkout, live Stripe, DNS, Search
> Console submission/removal, product/catalog mutation, production data
> mutation, ERPNext production record mutation, product data changes, email
> sending, live payment tests, framework app updates, or deployment of
> app-mirror-release-20260529/ad0a408 as a full live checkout release.

## Sources Checked

- Frappe Cloud API authentication docs:
  `https://docs.frappe.io/cloud/api/authentication`
- Frappe Cloud API sites docs:
  `https://docs.frappe.io/cloud/api/sites`
- Frappe Cloud app/site update docs:
  `https://docs.frappe.io/cloud/sites/how-to-update-an-app-site-on-a-private-bench`
