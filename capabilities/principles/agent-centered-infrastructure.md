---
id: agent-centered-infrastructure
name: Agent-Centered Infrastructure
schema_version: 2.1
profile: foundation
level: principle
maturity: candidate
scope: capability framework
currently_true: unknown
last_verified: 2026-05-07
tags:
  - agent infrastructure
  - blocker removal
  - trust
  - efficiency
---

## What it does

Sets the operating relationship for this framework: infrastructure exists to
make agents more effective and trustworthy, not to make the user manage agent
paperwork.

## When to reach for it

Use this when deciding whether a framework rule, template, memory, capability
root, or workflow belongs in the foundation.

## How to use it

1. Optimize for what future agents will actually find, read, and use.
2. Prefer visible, predictable files over clever hidden structure.
3. Ask the user for design, business, scope, risk, privacy, or priority
   decisions; own technical execution details when local evidence is enough.
4. If an agent needs better infrastructure, say what would remove the blocker:
   paths, indexes, test commands, examples, access, source-of-truth links, or
   verification receipts.
5. When local evidence is not enough, research current primary sources or
   proven patterns before turning a preference into a framework rule.
6. Do not freeze task-specific behavior into the base template. Put evolving
   "how to do X" knowledge in the capability root that owns that work.

## What it depends on

- [Capabilities Should Enhance, Not Become Chores](capabilities-should-enhance-not-become-chores.md)
- [Current Truth Needs Evidence](current-truth-needs-evidence.md)

## Failure modes

- The framework becomes user paperwork instead of agent leverage.
- Base templates keep mutating because task-specific behavior was installed as
  foundation.
- Agents hide their infrastructure needs, so the user cannot remove blockers.
