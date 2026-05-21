---
id: evidence-ledger-event
name: Evidence Ledger Event
schema_version: 2.0
level: atomic_ingredient
maturity: candidate
scope: capability framework
currently_true: unknown
verification_level: 1
last_verified: 2026-05-05
evidence_quality: direct
successful_uses: 1
failed_uses: 0
regressions: 0
depends_on: []
used_by:
  - capability-evidence-and-promotion
  - current-truth-needs-evidence
tags:
  - evidence
  - upvote
  - downvote
  - jsonl
  - audit
---

## What it does

Defines the smallest durable evidence unit used to support capability maturity,
upvotes, downvotes, failures, fixes, promotion, watch status, rollback, and
revalidation.

## When to reach for it

Use this when a capability has been used in real work and the result should
affect whether future agents trust it.

## How to use it

Add one compact JSON object to `evidence/capability-evidence.jsonl` in the
nearest relevant capability root.

Required fields:

- `ts`: ISO timestamp with timezone when practical.
- `capability_id`: stable id from the capability frontmatter.
- `event`: `use`, `upvote`, `downvote`, `failure`, `fix`, `promotion`,
  `deprecation`, `retest`, `watch`, or `rollback`.
- `actor`: agent or user source.
- `scope`: project, machine, repo, client, or task scope.
- `result`: short outcome.
- `verification`: command, check, review, or explicit approval.
- `confidence`: practical confidence level `0`, `1`, `2`, or `3` when the
  event changes trust state.
- `rollback`: how to undo, mark stale, or revalidate when the event changes
  trust-bearing behavior.
- `notes`: short safe note.

Keep the event small. Do not include secrets, raw conversation logs, client
private data, or long command output.

## What it depends on

None.

## Failure modes

- Treating an upvote as praise instead of proof makes the registry unreliable.
- Storing raw private content in the ledger creates unnecessary privacy risk.
- Omitting scope makes future retrieval overgeneralize the evidence.
- Raising confidence without rollback or revalidation instructions makes later
  failures harder to contain.
