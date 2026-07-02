# Meta Missionary Product Sales Campaign Rail - 2026-06-30

## Rail Boundary

Brand lane: `locally_twisted`.

This is the canonical marketing/advertising handoff for the Large head
Missionary Meta campaign. Keep it separate from Product Setup, ecommerce
repair, launch proof, and general Meta account aftercare handoffs.

Goal: sell the Large head Missionary product on `locallytwisted.com`, not
generic traffic or vague web conversions.

Primary destination:
`https://locallytwisted.com/missionary-balloon-gift`

Product route:
`https://locallytwisted.com/shop-items/bouquets/large-head-missionary`

Current launch status: blocked. Do not create, schedule, enable, or spend on
Meta campaign/ad set/ad/ad creative objects while the website work is still in
progress. This source packet is a preparation/archive rail only.

## Capability Gate

PASS on 2026-07-01 from the clean publish worktree with:

- `capabilities/INDEX.md`
- `capabilities/recipes/meta-operations/INDEX.md`
- `capabilities/recipes/meta-operations/access-governance.md`
- `capabilities/recipes/meta-operations/ads-operations.md`
- `capabilities/recipes/meta-operations/measurement-and-assets.md`
- `capabilities/recipes/meta-operations/approval-and-evidence.md`
- `capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`
- `capabilities/recipes/lt-seo-geo-aeo-contract.md`
- `capabilities/recipes/frappe-product-page-company-first.md`
- `capabilities/recipes/frappe-public-container-contract.md`
- `capabilities/recipes/responsive-container-audit.md`
- `capabilities/recipes/compact-hero-contract.md`
- `capabilities/failures/ad-dashboard-research-vs-control-drift.md`

## Approved Campaign Decisions

Approved by GL for planning/source prep:

- Campaign type: Sales, not Traffic.
- Product: Large head Missionary only.
- Platforms: Facebook and Instagram.
- Budget: `$5/day` Facebook and `$5/day` Instagram.
- Duration: 30 days.
- Spend cap: `$300` total unless GL approves more.
- Geography: standard local delivery range only: Davis, Weber, Salt Lake, and
  Utah counties.
- Exclusion: Park City and ZIPs `84060`, `84068`, and `84098`; do not include
  broader Summit County or Wasatch Back targeting.
- Audience: adults only, broad local buyer/event/gift signals.
- Sensitive targeting guard: do not target religion, LDS, Mormon, missionary
  religion interests, church membership, or similar personal-attribute signals.
- Creative: approved current product creative.
- Copy winners: Ad 1 and Ad 3, with pricing removed.
- Tracking: consent-gated sales-event tracking approved.

Not approved:

- Live Meta object creation, scheduling, enabling, or spend.
- Exact start/end schedule.
- Final Meta preview objects.
- Customer-data uploads, custom audiences, lookalikes, lead export, message
  reading, ENB access change, billing change, pixel/dataset change, or offline
  conversion upload.

## Live And Source Status

Verified earlier in this rail:

- `/missionary-balloon-gift` returns HTTP 200 on `locallytwisted.com`.
- The landing page has `robots: index, follow`, canonical metadata, social
  metadata, schema, and CTAs to product/contact.
- The live sitemap includes
  `https://locallytwisted.com/missionary-balloon-gift` with `lastmod`
  `2026-07-01`.
- The product route returns HTTP 200 and is checkout-commerce/cartable.
- Meta read-only inventory can see Business `1327185764080942`, ad account
  `act_27813262`, Page `110889248970340`, 72 campaigns, 73 ad sets, 85 ads,
  2 pixels, and 0 custom conversions.
- The connected Instagram business account is `locally_twisted`
  (`17841401301951205`).

Important release distinction:

- The landing page source is already archived and publicly available.
- This rail adds source support for consent-gated Meta sales events:
  `ViewContent`, `AddToCart`, `InitiateCheckout`, and paid-order `Purchase`.
- That tracking support is not a live-site claim until the normal Frappe
  release path updates the site and fresh public-route proof shows the new
  asset versions/events.
- Fresh public proof still showed the old live asset versions:
  `lt-guest-cart.js?v=20260510-cart-line-key-1`,
  `lt-marketing-bridge.js?v=20260609-1`, and
  `lt-marketing-measurement.js?v=20260610-config-1`.
- Google reindexing is not needed to run Meta ads. Search Console URL
  inspection/request-indexing is optional organic SEO cleanup after the site
  work stabilizes.

## A/B Test Structure

Use one Sales campaign with two platform-controlled ad sets to honor the
approved budget split:

- Facebook-only ad set: `$5/day`, local delivery geography.
- Instagram-only ad set: `$5/day`, local delivery geography.

Use four ads:

- Facebook Ad 1:
  `/missionary-balloon-gift?utm_source=meta&utm_medium=paid_social&utm_campaign=missionary_sales_2026&utm_content=fb_photo_moment`
- Facebook Ad 3:
  `/missionary-balloon-gift?utm_source=meta&utm_medium=paid_social&utm_campaign=missionary_sales_2026&utm_content=fb_local_gift`
- Instagram Ad 1:
  `/missionary-balloon-gift?utm_source=meta&utm_medium=paid_social&utm_campaign=missionary_sales_2026&utm_content=ig_photo_moment`
- Instagram Ad 3:
  `/missionary-balloon-gift?utm_source=meta&utm_medium=paid_social&utm_campaign=missionary_sales_2026&utm_content=ig_local_gift`

Schedule only after GL approves exact America/Denver start and end times and
the final Meta preview objects.

## Approved Copy

### Ad 1 - Photo Moment

Primary text:

Make the mission call, farewell, airport pickup, or welcome-home porch easy to
spot. Order a custom Elder or Sister large-head balloon gift from Locally
Twisted. Choose the look, check out online, and schedule pickup or local
delivery.

Headline:

Custom Missionary Balloon Gift

Description:

Order online for pickup or local delivery.

CTA:

Shop Now

### Ad 3 - Local Gift

Primary text:

Need a photo-ready gift for a mission call, farewell, or open house? Locally
Twisted makes personalized Elder and Sister balloon gifts for Wasatch Front
pickup or local delivery.

Headline:

Order a Missionary Balloon

Description:

Pickup or local delivery available.

CTA:

Shop Now

## Creative Notes

Use the approved product creative first. The current product image URL has had
a MIME/extension mismatch (`.png` URL returning WebP bytes), so before final
Meta preview either:

- upload the creative directly in Ads Manager, or
- verify/fix the image asset so Meta link preview uses the intended file type
  and crop.

Do not substitute CBD, Memorial Balloons, or non-LT brand visuals.

## Tracking Boundary

Approved source behavior:

- consent-gated Meta Pixel loader reads only the configured Meta Pixel ID;
- no Pixel ID is hard-coded in JS source;
- `ViewContent` can fire on product pages after optional consent;
- `AddToCart` fires through the guest cart helper after optional consent;
- `InitiateCheckout` fires from checkout state after optional consent;
- `Purchase` fires only from `/thank-you` after paid Sales Order context and
  uses a public-safe product/order payload.

Forbidden in this rail:

- customer email, phone, address, ZIP, message text, lead record, customer
  list, offline conversion file, or custom audience upload;
- Conversions API/server events without a separate approved measurement plan;
- claiming live sales tracking from a source commit alone.

## Next Safe Steps

1. Finish or freeze the website work that currently blocks ad launch.
2. Release this source through the normal Frappe path only when that release is
   approved.
3. Verify live public asset versions and event behavior after release.
4. Verify final product creative preview/crop/MIME behavior.
5. Prepare Meta draft objects only when a current approval explicitly opens
   that step.
6. Get GL approval for exact start/end schedule and final previews before any
   spend starts.
