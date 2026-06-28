---
name: Meta messaging and engagement
level: recipe
maturity: candidate
verification_level: policy-lane-identified
last_verified: 2026-06-28
currently_true: true
---

# Meta Messaging And Engagement

## Purpose

Prepare Facebook Messenger and Instagram DM operations without accidentally
reading private customer conversations or sending unapproved replies.

## Current State

The token has messaging-related scopes, but no customer messages have been
read and no replies have been sent. Messaging must be treated as customer
communication, not generic account inventory.

## Operating Flow

1. Define the approved business voice and escalation rules.
2. Define who may approve replies and when GL wants live supervision.
3. Build a draft/review queue before any automated response.
4. Verify token and webhook requirements read-only.
5. Read or reply only after explicit approval for the messaging lane.

## Approval Required

- Reading customer message threads.
- Sending a reply, comment response, DM, saved response, or automated response.
- Connecting or changing webhooks.
- Exporting message data or storing customer conversation content.
- Changing inbox routing, assignment, or CRM sync.

## Safe Work

- Draft reply templates.
- Draft escalation categories.
- Build local fake-data review UI.
- Prepare webhook verification design.
- Review Meta policy constraints from official docs.

## Failure Modes

- Treating a scope grant as approval to read customer messages.
- Sending an automated reply without a human-approved script.
- Logging customer content into repo files, terminal output, or public traces.

## Revalidation

Before messaging goes live, require a separate security/customer-data gate and
a dry-run proof that logs do not expose private message content.
