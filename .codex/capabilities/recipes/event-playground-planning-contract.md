---
id: event-playground-planning-contract
name: Event Playground Planning Contract
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted Event Playground / Plan Custom Decor payload and Frappe handoff boundary
currently_true: true
verification_level: 2
last_verified: 2026-05-07
evidence_quality: direct
successful_uses: 1
failed_uses: 0
regressions: 0
depends_on:
  - event-playground-construction-truth
  - erpnext-intake-form-parity
used_by:
  - workstreams/event-playground.md
tags:
  - Locally Twisted
  - Event Playground
  - Plan Custom Decor
  - Frappe handoff
  - quote honesty
---

# Event Playground Planning Contract

Use this recipe before changing the Event Playground payload, contact handoff,
warnings, Frappe adapter metadata, or quote-readiness behavior.

## Core Rule

The preview is a planning visualization, not a quote engine.

Render counts may make the PlayCanvas scene useful. They must not become final
quote math, ERPNext Item quantities, material planning, or customer-visible
balloon counts unless LT has approved the formula and the code says
`quote_ready: true` through a deliberate future decision.

## Current Contract

- Internal route/workstream: `Event Playground` at hidden `/event-playground`.
- Browser-preview copy: `Plan Custom Decor`.
- Local payload schema: `event-playground-v2`.
- Future Frappe adapter contract: `design-studio-v1`.
- Current handoff storage: `lt_event_playground_handoff_v1` in Frappe-site
  `sessionStorage`.
- Current submit route: iframe `postMessage` to Frappe wrapper, then redirect to
  `/contact?intent=quote&source=event-playground`.
- Current backend methods: none.
- Current DocTypes: none.
- Current public navigation: none.

## Required Payload Boundaries

- Keep `render_facts.render_balloon_count` and `render_facts.render_cluster_count`
  separate from `production_estimate`.
- Keep legacy `estimated_balloons` fields only as compatibility aliases when
  needed; do not treat them as quote-safe.
- Keep every production estimate `quote_ready: false` and
  `customer_visible: false` until formulas are approved.
- Carry `warnings`, including `quote_math_pending_lt_approval`, into the payload.
- Carry the planning disclaimer into customer note, design contract, and warning
  surfaces.
- Keep contact facts structured: name, email, phone, event date, and event city
  or venue.
- Keep `integration_adapter.lead_creation_policy` at server validation only.

## Frappe Adapter Requirements Before Production

Future Frappe code must add all of these before public save/share/submit:

1. Server-side schema allowlist for `event-playground-v2` or its successor.
2. Strict piece/color/material/pattern allowlists.
3. JSON and screenshot size caps.
4. Email validation before Lead creation.
5. Exactly one Lead creation after validation, not during draft save.
6. A design record or other durable storage approved by the architecture lane.
7. Loud visible failure when save succeeds but submit/Lead creation fails.
8. No share token or public page without noindex, expiry/revoke behavior, and
   PII redaction decisions.

## Verification

From `research/design-studio-v2/event-builder-spike/`:

```powershell
npm run test:classic
npm run build
npm run verify:event-playground
npm run verify:v2
```

From the repo root, when the Frappe wrapper/contact handoff is in scope:

```powershell
npm run test:event-playground
```

## Failure Signs

- A verifier only checks nonblank canvas and ignores payload warnings.
- Render balloon counts appear in customer copy as final counts.
- A future API accepts arbitrary colors, piece types, or unknown schema versions.
- Draft save creates a Lead.
- A failed Lead submit looks successful to the customer.
- `/event-playground` is added to public navigation without a production bundle,
  backend validation, save/share decision, and GL approval.
