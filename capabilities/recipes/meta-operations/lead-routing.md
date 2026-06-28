---
name: Meta lead routing
level: recipe
maturity: candidate
verification_level: token-lane-identified
last_verified: 2026-06-28
currently_true: true
---

# Meta Lead Routing

## Purpose

Map and eventually operate Meta lead forms without prematurely exporting lead
records or breaking existing ENB/HighLevel dependencies.

## Current State

- The current system-user token can read the ad account and Page identity.
- Lead-form metadata on the Page is blocked with a Page Access Token
  requirement.
- No lead records have been read or exported.
- The historical `Facebook Painting Leads` path still needs dependency
  mapping: native Meta lead form, HighLevel, ENB routing, or a combination.

## Operating Flow

1. Prove Page Access Token access for lead-form metadata only.
2. Inventory forms, questions, privacy links, CRM integrations, and routing.
3. Map ENB/HighLevel dependencies before changing anything.
4. Draft an approved target path into ERPNext/CRM.
5. Export or route real lead records only after GL approves the lead-data lane.

## Approval Required

- Reading, exporting, downloading, syncing, or storing lead records.
- Changing lead form questions, privacy policy links, CRM integrations, or
  webhook subscriptions.
- Disabling or replacing ENB/HighLevel lead routing.
- Importing lead data into ERPNext, a CRM, sheets, email, or automation.

## Safe Work

- Token readiness checks.
- Form metadata inventory after Page token exists.
- Dependency maps.
- Fake-data routing prototypes.
- Approval packet drafting.

## Revalidation

After Page-token setup, add a metadata-only verifier first. Lead-record export
must remain a separate explicit approval and security gate.
