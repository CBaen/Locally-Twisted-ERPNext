---
id: visible-capability-root-contract
name: Visible Capability Root Contract
schema_version: 2.1
profile: foundation
level: recipe
maturity: candidate
scope: capability framework
currently_true: unknown
last_verified: 2026-05-07
tags:
  - capability root
  - visible root
  - index
  - token protection
  - agent discovery
---

## What it does

Defines the minimum contract for a capability root so agents can find it,
understand what it owns, and avoid treating it as a hidden project-wide junk
drawer.

## When to reach for it

Use this when installing the first capability root in a project, adding another
root, or reviewing whether a root is discoverable enough to keep.

## How to use it

1. Prefer visible top-level project roots for new project capability packages:
   `capabilities/`, `capabilities-<scope>/`, or another plain name that sorts
   clearly in the project root.
2. Use hidden runtime roots, such as `.codex/capabilities/` or
   `.openclaw/capabilities/`, only for agent adapter material, compatibility
   pointers, explicitly preserved legacy installs being migrated, or
   runtime-specific capability surfaces.
3. Give every root an `INDEX.md` with a short root label:
   - what this capability root does
   - what belongs here
   - what does not belong here
   - related roots and backlinks
4. Keep the index hub/spoke. The root index routes; cards and folder spokes hold
   detail.
5. Do not create a parent `capabilities/README.md` that hides many capability
   roots under another layer. If there are multiple roots, make them visible
   siblings at the project root.
6. Treat the full folder shape as a package ecosystem. It is a place where
   future behavior can evolve; it is not a demand to invent detailed task rules
   on day one.

## What it depends on

- [Hub/Spoke Capability Indexing](hub-spoke-capability-indexing.md)
- [Agent-Centered Infrastructure](../principles/agent-centered-infrastructure.md)

## Failure modes

- A hidden root exists but agents miss it.
- A single parent folder becomes a tiered manual that nobody opens.
- The base template keeps changing because root purpose was not labeled.
