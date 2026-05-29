# Live Shop Discovery Deployment Execution - 2026-05-29

Status: NO-GO. Live shop discovery did not launch.

This record covers the approved live shop-discovery app-only release for
`https://locallytwisted.com` / `locallytwisted.v.frappe.cloud`.

## Approval Boundary

Approved live target:

- Frappe Cloud site: `locallytwisted.v.frappe.cloud`
- app: `locally_twisted`
- Frappe Cloud release: `c81v7r3b67`
- approved app hash: `cc5426401b4d3f69a57b8efb77320d943c5c95ea`
- live mode must remain browse-only:
  - `lt_ecommerce_paused=1`
  - `lt_shop_discovery_open=1`
  - `lt_checkout_paused=1`
  - `lt_public_indexing_enabled=1`

Not approved:

- live checkout
- live Stripe
- DNS or Search Console changes
- product/catalog mutation
- production data mutation
- ERPNext production record mutation
- product data changes
- email sending
- live payment tests
- framework app updates
- full checkout release `app-mirror-release-20260529` / `ad0a408`

## First Provider Attempt

First Frappe Cloud release pipeline:

- pipeline: `fh5upf86a3`
- status: `Failure`
- failure stage: pre-release checks
- notification: `ehifrn828g`
- failure message:
  `Each app must have a release and hash to run deploy and update!`

Plain meaning: Frappe Cloud rejected the request shape before it created a
deploy candidate, updated the bench, migrated the site, or installed new live
code.

Provider status after the failed attempt:

- site status: `Active`
- deploy in progress: `false`
- running candidate: `null`
- installed live app did not advance to the approved shop-discovery hash

## Corrected Retry Guard

The corrected retry remains inside the approval because it uses the same
approved live target and adds the already-approved app hash to the request:

- app: `locally_twisted`
- release: `c81v7r3b67`
- hash: `cc5426401b4d3f69a57b8efb77320d943c5c95ea`

No broader app list, framework update, checkout opening, data mutation, DNS,
Search Console, Stripe, email, or payment action is permitted by this guard.

## Corrected Provider Attempt

Corrected Frappe Cloud release pipeline:

- pipeline: `56qgv7c8hm`
- status: `Success`
- deploy candidate observed during polling: `27f6g2d7vh`
- app requested:
  - `locally_twisted`
  - release `c81v7r3b67`
  - hash `cc5426401b4d3f69a57b8efb77320d943c5c95ea`

Plain meaning: Frappe Cloud accepted the corrected app update and built the
approved release candidate, but the live site still had to migrate onto it.

## Live Site Migration Failure

The live site update failed during `Update Site Migrate`:

- failed job: `7b0egjdlkn`
- failed step: `Migrate Site`
- failed patch: `locally_twisted.patches.sync_shop_taxonomy_20260524`
- recovery job: `ec084t4jgs`
- recovery result: `Success`

Failure cause:

The taxonomy migration tried to apply the approved 2026-05-24 product taxonomy
to live ERPNext records, but live is missing the expected product `Item`
records. Frappe Cloud correctly recovered the site back to the prior live app
state.

Plain meaning: this is not a checkout failure and not a DNS/indexing failure.
It is a live data-parity blocker. Staging had the catalog records required by
the taxonomy patch; live does not.

## Live-After Proof

Provider proof after recovery:

- site status: `Active`
- running jobs: none
- installed live `locally_twisted` app:
  - branch `live-seo-indexing-20260528`
  - hash `5bbdc484d86729c4f2afdf7776e9f6649b02c080`

Hosted live snapshot:

- `.tmp/release-snapshots/lt-live-after-shop-discovery-provider-recovery-2026-05-29.json`

Key hosted live result after recovery:

- `/shop` still redirects to `/ready-to-order-paused?from=%2Fshop`
- `/all-products` still redirects to `/ready-to-order-paused?from=%2Fall-products`
- `/shop-items` still redirects to `/ready-to-order-paused?from=%2Fshop-items`
- representative category/product routes still redirect to the pause page
- `/cart` and `/checkout` remain paused
- no snapshot HTTP failures were recorded

Comparison artifact:

- `.tmp/release-snapshots/lt-staging-final-vs-live-after-shop-discovery-provider-recovery-2026-05-29.json`

Decision meaning: live remains customer-safe, but the shop-discovery release is
not live.

## Stop Decision

Do not retry this live release unchanged.

Do not use `skip_failing_patches=true` as a shortcut. That would hide a real
live catalog mismatch and could leave the app/data contract unproven.

The next release must be a new remediation slice with staging proof and a new
live approval. The remediation must choose one of these paths:

- approve and prove a live catalog/product-data migration before reopening shop
  discovery; or
- change the taxonomy patch/source behavior so it can safely deploy on live
  without the missing product records, then prove what the live shop will show
  when product data is absent.

The first path is more likely to satisfy the marketing/indexing goal because
shop discovery needs actual product records to index.
