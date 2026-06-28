---
name: Meta measurement and assets
level: recipe
maturity: candidate
verification_level: local-api-read-only
last_verified: 2026-06-28
currently_true: true
---

# Meta Measurement And Assets

## Purpose

Keep Meta pixels, datasets, domains, custom conversions, UTMs, and Frappe
tracking changes under one approval-led measurement lane.

## Current State

The API inventory can read the ad account's pixels and custom conversions. It
saw two pixels and zero custom conversions. The last-7-day insights endpoint
returned zero rows.

On 2026-06-28, read-only API proof found:

- Pixel `1079085392230103`, named `locally twisted`, created 2018-05-05,
  last fired 2026-05-31. This is the preferred Locally Twisted Pixel candidate.
- Pixel `149178523772697`, named `Ads Pixel for Shopify Facebook Ad`, created
  2021-03-28, last fired 2021-07-21. Treat as historical unless GL approves a
  reason to reuse it.
- Custom conversions: `0`.
- Source support for browser Meta Pixel PageView tracking exists in
  `lt-marketing-measurement.js`, but it is disabled until a Pixel ID is
  configured in tracking settings, optional tracking consent is accepted, and
  the approved release path is used.

## Rules

- Do not install, activate, replace, share, delete, or rename pixels/datasets
  without exact approval.
- Do not enable Frappe-side tracking, Meta Pixel, Conversions API, webhooks, or
  server events without an approved measurement plan.
- Do not upload offline events, customer lists, or conversion data without a
  separate customer-data approval.
- Keep UTMs and final URLs aligned with campaign reporting and landing-page
  reality.

## Safe Work

- Inventory pixels, datasets, custom conversions, and domains.
- Draft an event taxonomy.
- Audit final URLs and UTM templates.
- Prepare Frappe measurement bridge design while disabled.
- Compare ad promise, landing page, and conversion event.

## Approval Required

- Pixel/dataset/domain/custom conversion changes.
- Frappe site tracking activation.
- Conversions API or webhook setup.
- Offline conversion upload.
- Any customer-data-based audience or event sync.

Exact approval packet for the current Pixel activation:

> Approve configuring LT Meta Pixel `1079085392230103` for Locally Twisted
> PageView tracking on the approved site.

## Revalidation

Run the Meta inventory and the LT site tracking verifier before measurement
changes. After any approved change, verify the Meta asset, site event behavior,
and logs without exposing PII.
