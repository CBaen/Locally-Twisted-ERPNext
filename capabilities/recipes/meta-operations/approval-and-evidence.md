---
name: Meta approval and evidence
level: recipe
maturity: candidate
verification_level: local-process
last_verified: 2026-06-28
currently_true: true
---

# Meta Approval And Evidence

## Purpose

Make Meta operations reliable without making them unsupervised. Every live
change should have a clear request, exact approval, bounded action, and proof.

## Approval Packet

Use this shape before a live action:

```text
Platform:
Object:
Current state:
Proposed change:
Business reason:
Data touched:
Spend/billing impact:
Customer-visible impact:
Rollback:
Exact approval needed:
```

## Evidence Packet

Use this shape after an approved action:

```text
Approved action:
Object changed:
Before:
After:
Verification:
What was not changed:
Rollback available:
Follow-up needed:
```

## Exact Approval Examples

Acceptable:

- "Approve pausing campaign X today."
- "Approve publishing this exact Facebook post at 3 PM."
- "Approve reading leads from form X for routing setup."

Not enough:

- "Do the ads."
- "Handle social."
- "Use the broad token however you need."

Broad authority means we can prepare, inspect, draft, and operate the whole
surface. It does not replace the approval step for live writes, spend, customer
messages, lead records, or access changes.

## Closeout Requirements

Every Meta operation closeout should state:

- what was verified;
- what was changed, if anything;
- whether ENB access was untouched;
- whether customer messages or leads were read/exported;
- whether spend, billing, campaigns, posts, pixels, or datasets changed;
- what remains blocked or needs the next token lane.

## Revalidation

If a Meta action fails, stop and classify the failure before retrying. Do not
turn retries into live-account experimentation.
