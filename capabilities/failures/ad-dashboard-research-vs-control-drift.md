---
name: Ad dashboard research vs control drift
type: failure
failure_kind: process_ownership_failure
schema_version: 0.1
date_discovered: 2026-05-19
last_updated: 2026-05-19
status: guarded
scope: project
owner_context: Locally Twisted Google Ads and Meta account takeover
related_capabilities:
  - recipes/ad-account-takeover-provider-control.md
  - recipes/codex-browser-verification-surface.md
related_failures:
  - provider-dashboard-work-bounced-to-gl.md
tags:
  - google-ads
  - meta-business
  - provider-dashboard
  - account-control
  - agent-ownership
---

# Failure Recipe: Ad Dashboard Research Vs Control Drift

## Symptom

GL asks to see or manage the Google Ads or Meta Business account, but the agent
keeps crawling Gmail, Drive, public search, or old reports instead of opening
the authenticated provider dashboard.

## Known Instance

On 2026-05-19, GL asked to crawl Google Ads and take control of Google Ads and
Facebook/Instagram ads, then supplied a Google Ads policy URL. The useful
read-only Gmail/Drive crawl identified account IDs, ENB access evidence,
campaign names, billing warnings, and tracking risks, but it did not satisfy
the actual control request. GL correctly interrupted and clarified: the goal
was to see and manage the Locally Twisted Google Ads account and Meta Business
account.

## Root Pattern

The agent mistook support evidence for account control. In provider work,
Gmail/Drive messages help reconstruct history, but they cannot prove the
current dashboard state or let the owner manage users, partners, billing,
campaigns, pixels, tags, and lead forms.

## Required Guard

When GL gives a provider dashboard URL or says "see", "manage", "take
control", "at the account", "open the account", or equivalent:

1. Open or claim the authenticated dashboard page first.
2. State whether the account page is visible, blocked by login/MFA, or blocked
   by unavailable browser control.
3. Use Gmail/Drive/reports only as support evidence after the dashboard path is
   attempted.
4. Do not present a research inventory as an account-control result.

## Recovery Recipe

1. Stop research loop.
2. Acknowledge the account-control goal.
3. Open the exact dashboard URL in the user's browser/session or explain the
   concrete blocker.
4. Navigate to access/users/partners first.
5. Inventory current users, manager links, partners, billing, campaigns,
   pixels/tags, conversions, and lead forms.
6. Escalate only MFA, unavailable credentials, destructive approval, legal or
   payment approval, or browser-control failure.

## What Not To Do

- Do not use public web search as a substitute for Ads Manager or Google Ads.
- Do not use Gmail reports as proof of current active campaigns.
- Do not tell GL to perform the account review after the dashboard is already
  open unless browser control is technically unavailable.
- Do not remove ENB/agency access before exports and dependency mapping.

## Cross-Links

- Active handoff: `workstreams/ad-account-takeover-2026-05-19.md`
- Capability: `capabilities/recipes/ad-account-takeover-provider-control.md`
- Related failure:
  `capabilities/failures/provider-dashboard-work-bounced-to-gl.md`
