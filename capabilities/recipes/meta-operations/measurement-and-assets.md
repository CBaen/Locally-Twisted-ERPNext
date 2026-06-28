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

## Revalidation

Run the Meta inventory and the LT site tracking verifier before measurement
changes. After any approved change, verify the Meta asset, site event behavior,
and logs without exposing PII.
