---
id: capability-registry-generation
name: Capability Registry Generation
schema_version: 2.0
level: recipe
maturity: candidate
scope: capability framework
currently_true: unknown
verification_level: 1
last_verified: 2026-05-05
evidence_quality: direct
successful_uses: 1
failed_uses: 0
regressions: 0
depends_on:
  - current-truth-needs-evidence
used_by: []
tags:
  - registry
  - retrieval
  - validation
  - compact index
  - jsonl
---

## What it does

Generates a compact machine-readable registry so an agent can discover
capability ids, profiles, levels, maturity, watch status, tags, and paths
without reading every capability file.

## When to reach for it

Use this after adding, moving, promoting, or retrofitting capability files.

## How to use it

From a repository root that contains `tools/capability_registry.py`, run:

```bash
python tools/capability_registry.py --root capabilities --write-registry
```

For an installed project that copied only the `capabilities/` folder, run the
tool from the framework source:

```bash
python <framework-source>/tools/capability_registry.py --root <project>/capabilities --write-registry
```

Read the terminal summary. `legacy` and `retrofit_needed` mean the file is still
usable, but it has not earned the v2 maturity fields yet.

## What it depends on

- [Current Truth Needs Evidence](../principles/current-truth-needs-evidence.md) - keeps generated registries from becoming proof.

## Failure modes

- A registry is a lookup aid, not the source of truth.
- Generated files can become stale if they are not regenerated after edits.
- Tags should help retrieval; they should not become a second documentation
  system.
