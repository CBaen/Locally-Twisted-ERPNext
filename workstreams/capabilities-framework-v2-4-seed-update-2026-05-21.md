# Capability Framework v2.4 Seed Update - 2026-05-21

## Status

Seed propagation completed; project-local validation debt remains.

Source package handoff:
`C:\Users\baenb\projects\capabilities-framework\workstreams\project-root-seed-propagation-2026-05-21.md`

## What Changed

- Refreshed `capabilities/SCHEMA.md` from the canonical source package.
- Added v2.4 seed recipes for organic growth, Perfect Bite contests, and
  source/provenance adoption.
- Added source/provenance guidance to `capabilities/INDEX.md`.
- Added missing base seed cards required by the new recipes.
- Added the `ship-internal-tool` / `deploy-static-site-to-cloudflare` dependency
  and backlink where this root already carried both cards.
- Regenerated `capabilities/registry/capability-registry.jsonl`.

## Validation

- Registry: `ok=false`, 32 warnings.
- Graph: `ok=false`, 35 errors, 45 warnings.
- Whitespace check: `git diff --check -- capabilities` returned clean.

## Residual Debt

The remaining findings are older LT-specific references, backlinks, and trust
metadata. Examples include missing references such as
`erpnext-intake-form-parity`, `erpnext-checkout-commerce-rules`, and
`website-launch` from existing LT cards.

Do not treat this seed update as permission to repair LT trust metadata. Open a
separate LT capability-graph cleanup workstream and verify each reference
against current LT files before editing.
