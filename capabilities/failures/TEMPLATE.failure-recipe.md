---
name: Human-readable Failure Recipe name
type: failure
failure_kind: recurring_pattern
schema_version: 0.1
date_discovered: YYYY-MM-DD
last_updated: YYYY-MM-DD
status: open | guarded | probation | controlled | obsolete
scope: global | agency | project | workstream | adapter
owner_context: optional human/project context
related_capabilities: []
related_failures: []
tags: []
---

# Failure Recipe: Human-readable name

## Symptom

What it looks like when this failure pattern appears.

## Trigger conditions

What kind of work, instruction, workflow, tool behavior, or project state tends
to cause the pattern.

## Known instances

Catalog only recurring, high-cost, misleading, cross-surface, or
process-significant failures. Do not catalog isolated typos unless they reveal a
reusable trigger.

| Date | Project | Surface | Action being taken | Bad outcome | Evidence | Guard state | Status |
|---|---|---|---|---|---|---|---|
| YYYY-MM-DD | Project name | File/page/process | What the agent/tool/human was doing | What went wrong | Link/path/commit/report | missing/weak/bypassed/rewritten/added | open/recovered/guarded/probation |

## Root pattern

The deeper process/control/memory/verification failure underneath the individual
bug.

## Why it seemed reasonable at the time

What assumption made the bad action look valid to the agent or contributor.
This helps future agents recognize the trap before repeating it.

## Detection signals

Search terms, diffs, test smells, runtime events, user language, timeout shapes,
missing artifacts, or CI failures that indicate this pattern may be active.

## Required guard

The check, verifier, approval gate, source lookup, artifact requirement, or
human decision boundary that should prevent recurrence.

## Recovery recipe

1. Stabilize any live safety/business issue only as much as needed.
2. Record the instance before smoothing over the evidence.
3. Identify whether the guard was missing, weak, bypassed, or rewritten.
4. Repair the smallest safe surface.
5. Add or strengthen the guard.
6. Revalidate with named evidence.
7. Update linked capabilities/workstreams and watch/probation status.

## What not to do

- Do not treat a launched task as evidence.
- Do not rewrite tests to match the bad outcome.
- Do not remove the instance just because the immediate bug was fixed.
- Do not fork this schema into agent-specific variants.

## Cross-links

- Related capability:
- Related principle:
- Related recipe:
- Related workstream:
- Related adapter note:
- Related Failure Recipe:

## Evidence quality

State what is verified, inferred, stale-risk, unresolved, or blocked.
