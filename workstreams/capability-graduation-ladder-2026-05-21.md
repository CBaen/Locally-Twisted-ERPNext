# Capability Graduation Ladder - 2026-05-21

## Status

Adopted as cleanup-first project infrastructure. No LT capability was promoted,
downgraded, marked verified/staple, or cleared from watch/probation in this
pass.

Source package handoff:
`/home/guidingl/projects/capabilities-framework/workstreams/capability-graduation-ladder-2026-05-21.md`

## What Changed

- Refreshed `capabilities/SCHEMA.md` to schema v2.5.
- Added [Capability Graduation Ladder](../capabilities/principles/capability-graduation-ladder.md).
- Added [Capability Graduation Sweep](../capabilities/recipes/capability-graduation-sweep.md).
- Updated `capabilities/INDEX.md` so future agents know LT uses graduation
  metadata for support systems.
- Updated project queue, decisions, lessons, and coding handoff to make this a
  real cleanup lane instead of another reference note.

## Why Cleanup-First

Read-only review found LT already has valuable gates, verifiers, and
architecture-like capability patterns, but the capability graph still has older
project-local debt from before the v2.4 seed propagation. That debt includes
missing local references, backlink gaps, and trust metadata mismatches.

Because of that, LT should not mass-promote cards into `verified` or `staple`
from graduation language alone. The right first move is to classify which cards
are gate-required, verifier-backed, automation-backed, architecture-backed, or
release/live approval-backed, then repair evidence and dependencies in small
approved packets.

## High-Priority Graduation Review Targets

- `frappe-cloud-cloudflare-stripe-launch-gate` - likely
  `release_live_approval_backed`; public launch, DNS, Stripe, and Frappe Cloud.
- `frappe-public-storefront-security` - likely `gate_backed` or
  `architecture_backed`; public inputs, uploads, receipt pages, preview bridges,
  checkout trust.
- `erpnext-ecommerce-receiving-architecture` - deleted from current capability
  guidance at `d099f3f4bb8d5b24ba41af0aa1403d87f67eb70b`; current project
  handoff: `workstreams/erpnext-ecommerce-receiving-architecture.md`.
- `erpnext-webshop-guest-party-contract` - deleted from current capability
  guidance at `d099f3f4bb8d5b24ba41af0aa1403d87f67eb70b`; current guard:
  `capabilities/failures/webshop-guest-party-cleanup-regression.md`.
- `shared-inquiry-form-experience` - likely `verifier_backed` plus
  `gate_backed`; user-facing form success must not lie.
- `multi-agent-coordination-safety` - likely `architecture_backed`; protects
  child/client repo boundaries and parallel work.

## Validation Commands

Read-only first:

```bash
python /home/guidingl/projects/capabilities-framework/tools/capability_graduation_audit.py --root /home/guidingl/projects/Built_by_Cameron/_CLIENTS/locally-twisted/capabilities --json
python /home/guidingl/projects/capabilities-framework/tools/validate_capability_graph.py --root /home/guidingl/projects/Built_by_Cameron/_CLIENTS/locally-twisted/capabilities --json
python /home/guidingl/projects/capabilities-framework/tools/capability_registry.py --root /home/guidingl/projects/Built_by_Cameron/_CLIENTS/locally-twisted/capabilities --json
```

## Latest Validation Snapshot

Checked 2026-05-21:

- `capability_graduation_audit.py` exited 0 and reported `ok: true`,
  71 cards, 27 graduation candidates, 2 declared graduated cards, 0 required
  blockers, and 0 active cards missing support artifacts.
- `validate_capability_graph.py` exited 1 and reported `ok: false`, 71 cards,
  38 graph errors, and 48 warnings. This confirms the pre-existing graph debt
  noted by the read-only LT audit and is why this lane remains cleanup-first.
- `capability_registry.py --json` exited 0 but reported `ok: false`, 93
  records, 32 warnings, and mixed legacy/warn/retrofit-needed records.
- No registry write was run. Do not write the LT registry until the local graph
  debt is intentionally addressed or a narrower approved refresh is opened.

After LT explicitly marks any cards with `graduation_required: true`, blocking
mode can be used:

```bash
python /home/guidingl/projects/capabilities-framework/tools/capability_graduation_audit.py --root /home/guidingl/projects/Built_by_Cameron/_CLIENTS/locally-twisted/capabilities --json --fail-on-required
```

## Boundaries

- No ERPNext database edits.
- No product, checkout, payment, Stripe, DNS, Frappe Cloud, staging, live, or
  provider dashboard changes.
- No capability trust promotion from memory.
- No registry write until the local graph debt is intentionally addressed or a
  narrower approved registry refresh is opened.

## Next Safe Step

Run the graduation audit and convert the top findings into small action
packets. Each packet should name the target card, proposed graduation stage,
supporting artifact needed, evidence required, and rollback/revalidation path.
