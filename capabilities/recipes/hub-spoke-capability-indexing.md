---
id: hub-spoke-capability-indexing
name: Hub/Spoke Capability Indexing
schema_version: 2.1
profile: foundation
level: recipe
maturity: candidate
scope: capability framework
currently_true: unknown
last_verified: 2026-05-07
tags:
  - hub
  - spoke
  - token protection
  - index
  - retrieval
---

## What it does

Keeps capability roots useful as they grow by protecting context. The hub routes;
the spokes hold detail.

## When to reach for it

Use this when an `INDEX.md` is getting long, a capability root has many cards,
or an agent/runtime eagerly loads linked files.

## How to use it

1. Keep the root `INDEX.md` short: purpose, how to use, and one-line links.
2. Move detailed lists into layer or domain spokes:
   - `recipes/README.md`
   - `principles/README.md`
   - `finance/INDEX.md`
   - `workstreams/<feature>/capabilities/INDEX.md`
3. Prefer one-line summaries in hubs. Put procedures, examples, and failure
   modes in the capability cards.
4. Use generated registries for machine lookup when available.
5. For eager-loading agents, avoid transitive links from the top hub to every
   detail file when that creates context load.
6. For on-demand agents, still keep hubs slim so arrival and search stay fast.

## What it depends on

- [Capability Registry Generation](capability-registry-generation.md)

## Failure modes

- A hub that becomes a manual makes agents read too much before acting.
- A spoke without a backlink becomes hard to discover.
- Optimizing only for one agent runtime can make the framework less portable.
