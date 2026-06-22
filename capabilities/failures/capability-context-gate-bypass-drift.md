---
id: capability-context-gate-bypass-drift
name: Capability Context Gate Bypass Drift
schema_version: 2.1
profile: foundation
level: failure
maturity: candidate
scope: LT agent scope control and capability routing
currently_true: unknown
last_verified: 2026-06-22
tags:
  - capability
  - scope
  - release-safety
  - fail-loud
  - agent-process
---

## Failure pattern

An agent receives a narrow LT request, then substitutes ad hoc repo discovery,
old handoffs, local confidence, or broad release instincts for the actual
capability framework. The task expands, live/source boundaries blur, and GL has
to spend energy forcing the agent back to the requested scope.

## Seen in this project

The 2026-06 product/hero slice was narrow: retire four products, update the
landing hero, and keep parity docs/counts consistent. Source and app-mirror
commits were pushed, and local proof passed, but the live site stayed stale
because Frappe Cloud site update proof did not run. The work then broadened
into checkout/layout/live-provider discussion without first forcing the
capability path.

## Required counter-move

Run the executable capability context gate before edits or release action:

```bash
python /home/guidingl/codex-framework/tools/capability_context_gate.py \
  --cwd "$PWD" \
  --task "<plain-English LT task>" \
  --loaded "capabilities/INDEX.md" \
  --loaded "<specific LT recipe/failure/skill used for this task>"
```

If the gate fails, stop. Do not keep exploring, deploying, logging into
providers, or claiming readiness.

## What not to do

- Do not treat old handoffs as proof.
- Do not treat local proof or GitHub source push as live proof.
- Do not load any random capability file to satisfy the gate.
- Do not reopen live/provider/Frappe Cloud work unless the live/provider
  capability path is loaded and the user has actually asked for that path.

## Revalidation

Revalidate this failure recipe when:

- a future agent completes a high-risk LT task using the gate without scope
  drift;
- a future release proves source/app mirror/site update/live route proof as
  separate states;
- the gate gains stronger semantic matching or project-local policy support.
