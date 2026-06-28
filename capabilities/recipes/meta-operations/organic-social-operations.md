---
name: Meta organic social operations
level: recipe
maturity: candidate
verification_level: token-lane-identified
last_verified: 2026-06-28
currently_true: true
---

# Meta Organic Social Operations

## Purpose

Handle Facebook Page and Instagram content through a draft-first, approval-led
workflow. Publishing is a live customer-facing action and is not covered by ad
account read access alone.

## Current State

- The Locally Twisted Page is visible as an owned Page.
- Page post reads are blocked through the current system-user token.
- The next connection is a Page Access Token obtained through the approved
  Meta Page flow.

## Operating Flow

1. Draft content plan, copy, assets, destination links, and timing.
2. Confirm the Page and Instagram asset the post belongs to.
3. Confirm whether the action is Facebook Page, Instagram feed, reel/story, or
   comment management.
4. Get GL approval for the exact post or engagement action.
5. Publish or schedule only the approved item.
6. Verify the live permalink or scheduled object.

## Approval Required

- Publish, schedule, update, delete, hide, or boost a Page/Instagram post.
- Reply to, hide, or delete comments.
- Change profile details, business info, links, category, or connected
  Instagram account.

## Safe Work

- Draft content calendars.
- Prepare post copy and creative.
- Audit Page-token readiness.
- Read official API requirements.
- Build dry-run/simulation tooling.

## Revalidation

After a Page Access Token exists, add a read-only verifier that proves Page and
Instagram endpoints without publishing.
