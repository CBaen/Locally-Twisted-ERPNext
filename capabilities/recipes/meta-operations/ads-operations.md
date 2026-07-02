---
name: Meta ads operations
level: recipe
maturity: candidate
verification_level: local-api-read-only-plus-source-rail
last_verified: 2026-07-01
currently_true: true
---

# Meta Ads Operations

## Purpose

Run paid Facebook/Instagram advertising as a supervised workflow: inventory,
diagnose, draft, approve, mutate, then verify. The default is read-only until
GL approves an exact live ad-account change.

## Current Access

The current system-user token can read the ad account, campaigns, ad sets, ads,
insights endpoint, pixels, and custom conversions endpoint. The inventory
verifier saw 72 campaigns, 73 ad sets, 85 ads, 2 pixels, and 0 custom
conversions.

## Operating Flow

1. Inventory current campaigns, ad sets, ads, spend, insights, pixels, final
   URLs, and policy issues.
2. Separate active business decisions from platform mechanics:
   objective, offer, audience, creative, landing page, budget, tracking, and
   reporting window.
3. Draft changes in a review packet.
4. Get exact approval for the exact change.
5. Apply only the approved change.
6. Verify the object, status, budget/spend, URLs, and tracking after mutation.

## Product Campaign Rails

For any product-specific paid campaign, create or update a dedicated
workstream rail before draft/build work. Keep campaign copy, budget, geography,
creative, final URLs, UTM labels, tracking state, launch blockers, and final
approval status in that rail. Do not bury a paid campaign packet inside broad
Meta account aftercare, ecommerce repair, or website-launch handoffs.

Current rail:
`workstreams/meta-missionary-sales-campaign-2026-06-30.md`.

Current state: the Large head Missionary Sales campaign has approved
source-prep decisions but is blocked from live launch while website work is in
progress. Do not create, schedule, enable, or spend on Meta campaign/ad
set/ad/ad creative objects from this approval packet alone.

## Approval Required

- Create, pause, enable, delete, duplicate, or edit a campaign, ad set, or ad.
- Change budget, bid, bid strategy, optimization event, audience, location,
  placement, schedule, attribution, creative, final URL, UTM, or status.
- Upload creative or connect a catalog.
- Use customer lists, lookalikes, offline conversions, or lead/customer data.

## Safe Read-Only Work

- Performance reporting.
- Campaign structure inventory.
- Policy/final URL review.
- Pixel/custom conversion inventory.
- Drafting campaign briefs.

## Draft Brief Shape

- Objective:
- Offer:
- Audience:
- Creative:
- Landing page:
- Budget:
- Tracking:
- Approval needed:
- Verification after change:

## Revalidation

Run `scripts/verify/meta_operations_inventory.py` before each campaign work
session and after any approved mutation.
