# Phase 17 Critical Review - Desk Catalog Readiness Summary

Date: 2026-07-01

Status: critical review artifact only. No script, app code, queue, handoff,
capability, coordination, runtime, provider, payment, DNS, cache, deploy,
customer-message, product-scope, variant, or live record change occurred.

## Findings

A read-only Desk catalog readiness summary is a reasonable next source-only
slice after Phases 15 and 16, but only as an operator blocker map. Phase 15
already made catalog readiness visible over saved authority-packet evidence.
Phase 16 then proved that even a product with no dashboard blockers still needs
fresh target-site proof, rollback review, owner approval, developer release
review, target-environment approval, and customer-impact approval before any
mutation. A Desk summary can bring that same blocker-first information closer
to the operator workflow without creating a write path.

The safe value is triage, not readiness approval. The summary should help Jeff
or staff answer: which products are blocked, why they are blocked, which next
step is owner-facing, which next step needs developer help, and which saved
artifact or validation packet produced the answer. It must keep saved/source
evidence visibly separate from current public route, cart, checkout, payment,
document, cache, provider, deploy, and live proof.

The proposed UI becomes unsafe if it reads like a publish queue, a release
dashboard, or a success receipt. Counts such as "zero blockers" or "ready" must
not imply that the customer-facing site changed, that checkout is safe, or that
an apply action may run. The summary should prefer "blocked", "needs proof",
"source-only", and "review next step" language over scores or green-light
phrasing.

The existing Product Setup Desk code is a good boundary pattern: `Show
Readiness` reads saved validation JSON, shows public-success and live-apply
permissions, lists blockers, and does not add publish/apply behavior. Phase 17
should reuse that posture at catalog scope, not introduce a new authority model.

Witness process note: this review used the degraded witness mode from the
project's witnessed-work guidance because this runtime has no subagent tool.
Intent and technical checks were separated in this artifact, but this is not an
independent multi-agent witness.

## Required Acceptance Criteria

Before any Phase 17 implementation is committed, all criteria below must hold.

- Scope remains source-only and read-only: no ERPNext mutation, no live/API
  collection, no cache clear, no deploy, no provider/payment/DNS action, no
  customer message, no product-scope choice, and no delete/disable/rename/
  collapse/replace/revive/retire action.
- The Desk summary consumes only saved validation/catalog dashboard/release
  packet evidence or static fixture data. If it uses a saved artifact, the UI
  and JSON must show the artifact source and freshness/staleness state.
- The summary must show proof mode prominently: source/saved evidence only, no
  current live proof.
- The summary must show catalog-level counts as triage counts, not readiness
  scores: total products represented, blocked products, blocker groups,
  variant-shape risks, products missing public proof, and products missing
  rollback/release proof.
- Product rows must show product identifier, route when known, owner-facing
  state, top blocker codes/messages, developer-help-needed flag, next owner
  step, next developer step, and artifact timestamp if present.
- The UI must keep all approval flags false for source-only output: local apply,
  staging apply, live apply, mutation, cache clear, deploy, provider action,
  payment action, document/customer-send action, and public-success claim.
- The UI must not promote `source_declared` operating brand into live brand-lane
  proof.
- The UI must not promote same-brand source uniqueness into live/global
  uniqueness proof.
- The UI must not treat saved `/tmp` artifacts, dashboard counts, packet
  completeness, source branch/commit, owner approval, or technical verifier pass
  as current catalog truth or live release proof.
- The summary must make these actions impossible from the UI: publish, apply,
  live apply, cache clear, deploy, provider/payment action, customer message,
  product retirement/revival, variant collapse, and direct raw catalog mutation.
- If the summary has links or buttons, they may only navigate to existing
  Product Setup or target record views, refresh the source-only display, or open
  a no-write detail dialog. Button labels must not imply public success.
- The UI copy must avoid the forbidden ERP terms named in `AGENTS.md`.
- The implementation must not weaken the existing `Show Readiness`, Product
  Setup validation JSON, authority packet, catalog dashboard, or release packet
  false-approval contracts.
- Commit proof must include `Capability gate: PASS` with
  `capabilities/INDEX.md` and
  `capabilities/failures/product-setup-projection-authority-drift.md` loaded.

Verifier behavior that should block commit:

```bash
python /home/guidingl/codex-framework/tools/capability_context_gate.py --cwd "$PWD" --task "Phase 17 source-only Desk catalog readiness summary critical review and implementation" --loaded "capabilities/INDEX.md" --loaded "capabilities/failures/product-setup-projection-authority-drift.md"
python -m py_compile <new-or-edited-python-files>
python scripts/verify/product_blueprint_contract.py
python scripts/verify/product_setup_publish_readiness_contract.py
python scripts/verify/product_setup_catalog_readiness_contract.py
python scripts/verify/product_setup_release_packet_contract.py
<new-desk-summary-contract-verifier>
git diff --check
```

The new verifier must exit nonzero if:

- source-only output sets any approval flag true;
- any publish/apply/cache/deploy/provider/payment/customer-send code path is
  introduced;
- the UI or JSON calls a product live, live-applied, customer-visible, safe to
  sell, or ready for public change without target-site proof;
- saved artifacts are shown without a source/freshness label;
- source-declared brand, source uniqueness, dashboard counts, packet existence,
  branch/commit identity, or owner approval is treated as live proof;
- blocked known fixtures can appear as public-ready or mutation-ready;
- a zero-dashboard-blocker fixture can bypass the Phase 16 missing release
  gates;
- forbidden ERP terms appear in new Desk UI labels or docs.

## Residual Risk

The biggest remaining risk is organized false confidence. A clean Desk summary
can still make unsafe work feel close to done if operators see counts without
the proof boundary.

Saved artifacts can be stale. A Desk summary over Phase 15/16 JSON may miss
current Product Setup edits, public route drift, cart behavior, cache behavior,
provider state, payment/document state, or live site state that changed after
the artifact was captured.

Owner usability remains unproved until a non-developer operator reviews the
actual Desk surface. A technically correct blocker map can still fail if the
wording does not make the next safe step obvious.

This slice still will not choose product scope, repair the known
`large-head-missionary` drift, collapse Birthday Deliveries variants, approve a
release, or prove target-site behavior. Current-data refresh or live/staging
release work remains a separate gate.

## Recommendation

Proceed with Phase 17 only as a read-only Desk catalog readiness summary that
surfaces the existing Phase 15 blocker map and Phase 16 release-gate boundary
inside the operator workflow.

Stop if the proposed UI implies publish/apply ability, live success, current
public readiness, checkout/payment safety, customer-message readiness, or
product-scope approval. The correct outcome is a clearer operator map of what
is still blocked, not a path to mutation.

Capability gate: PASS.

Loaded resources:

- `capabilities/INDEX.md`
- `capabilities/failures/product-setup-projection-authority-drift.md`
