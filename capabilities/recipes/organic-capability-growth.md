---
id: organic-capability-growth
name: Organic Capability Growth
schema_version: 2.3
profile: foundation
level: recipe
maturity: candidate
scope: capability framework
currently_true: unknown
last_verified: 2026-05-21
used_by:
  - source-provenance-and-adoption
tags:
  - organic growth
  - metadata
  - proposal
  - discovery
  - capability graph
---

## What it does

Uses optional flat metadata and read-only reports to find where capabilities
could combine into better recipes, meals, feasts, or action items.

## When to reach for it

Use this when a root has enough ingredients that agents need help spotting
valuable connections across projects, subjects, features, or agent surfaces.

## How to use it

Add optional metadata only when it helps discovery:

```yaml
building_block_type: action
composition_roles: [speed, safety]
portability: cross-project
combination_potential: high
```

Add source/provenance metadata only when origin affects trust, rights,
attribution, or local adoption:

```yaml
source_kind: external_research
adoption_state: adapted
source_refs: [research/source-note.md]
rights_status: unchecked
attribution_required: unknown
```

Then run the growth index:

```powershell
python tools\capability_growth_index.py --root capabilities --root-alias local --json
python tools\capability_growth_index.py --root capabilities --root-alias project --related-root shared=C:\Users\<user>\capabilities --json
```

Read the report as a pantry map:

- `optional_metadata_fields` shows which growth fields are present.
- `provenance_metadata_fields` shows which source/adoption fields are present.
- `metadata_field_proposals` can suggest fields without standardizing them.
- `top_growth_opportunities` lists promising cards for review.
- `source_adoption_opportunities` lists borrowed or researched cards that need
  source review, local verification, or adoption/rejection decisions.
- `trusted_root_writes` and `qdrant_writes` must stay false/zero for report
  runs.

Do not add nested dependency metadata. Real dependency chains still use
flat-string `depends_on` and `used_by` references. The registry and graph
validator should warn when optional growth metadata is nested instead of a
plain scalar or flat list.

## What it depends on

- [Capability File Schema](../SCHEMA.md)
- [Cross-Project Capability Composition](cross-project-capability-composition.md)
- [Failure Cascade And Watch Status](failure-cascade-and-watch-status.md)

## Failure modes

- Turning optional fields into required paperwork makes the framework heavy.
- Treating a metadata match as proof skips evidence and revalidation.
- Standardizing every clever field too early creates a messy substrate.
- Treating provenance as permission to copy source material creates rights and
  attribution risk.

## Rollback / revalidation path

Remove or ignore optional metadata fields that do not improve agent discovery.
Rerun the growth index and graph validator after any schema or metadata change.
