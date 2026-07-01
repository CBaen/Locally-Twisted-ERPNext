# Phase 18 Critical Review - Pure Runtime-Shaped Desk Catalog Summary Contract

Date: 2026-07-01

Status: critical review artifact only. No code, script, app, queue, handoff,
capability, coordination, runtime, provider, payment, DNS, cache, deploy,
customer-message, product-scope, variant, or live record change occurred.

Capability gate: PASS.

Loaded resources:

- `capabilities/INDEX.md`
- `capabilities/failures/product-setup-projection-authority-drift.md`
- `capabilities/recipes/erpnext-product-blueprint-authoring.md`

## Review Type

Critical witness subagent lane. The lenses below are kept separate for
discipline and were integrated by the parent agent with the implementation
subagent's output.

Route record:

- Mode: `triadic-review`
- Decision needed: whether Phase 18 can safely accept a pure
  runtime-shaped Desk catalog summary contract without overclaiming readiness.
- Scope owner: this LT worktree and the requested Phase 18 artifact only.
- System/project/runtime classification: single-project source review with
  client-surface risk.
- Allowed actions: create this review artifact only.
- Forbidden actions: code edits, runtime mutation, live reads/writes, cache
  clear, deploy, provider/payment/DNS action, customer message, product-scope
  decision, commit, and push.
- Evidence bar: current repo files, current Phase 17 docs, Product Setup
  doctype/client code, verifier source, loaded capabilities, and memory only as
  non-authoritative context.
- Stop condition: any need to choose product scope, approve release, mutate
  records, or prove the live/customer-facing site.

## Decision

Phase 18 should proceed only if the proposed pure runtime-shaped contract proves
that the Desk catalog summary is a read-only saved/source evidence surface. It
may shape output like a runtime/Desk API response so the UI and verifier can
exercise real row cases, but it must not become live proof, mutation approval,
release approval, product-scope approval, or a replacement for Phase 16 target
site gates.

## Lens Findings

Intent lens:

The safe intent is to make Phase 17's Desk summary more testable and less
fragile by moving the summary behavior into a pure contract that can be checked
with crafted rows. The unsafe intent would be to make the summary feel more
"real" by treating saved `validation_json` as current catalog truth. The
contract must help an operator see blockers and proof mode; it must not tell
Jeff that Save, zero blockers, `Staging Ready`, `Approved For Live`, source
brand fields, or a branch commit changed the public shop.

Technical lens:

Current Phase 17 code is mostly bounded. `get_catalog_readiness_summary` reads
only `LT Product Blueprint` fields, labels `proof_mode` as
`source_saved_validation_only`, returns false read-only approvals, and turns
malformed saved JSON into blocked rows. The client calls only that read method
from `Show Catalog Readiness`.

The weak spots are review-worthy:

- `public_success_claim_allowed_count` and `live_apply_allowed_count` are
  derived from saved JSON before the response also returns false approvals.
  Since current validation sets those values false, this is safe today, but a
  stale or malformed future saved packet could make the summary display risky
  counts unless the pure contract clamps them false or flags them as invalid.
- The Desk dialog uses a green indicator when `blocked_count` is zero and says
  "No blocked Product Setup rows were found in the saved readiness summary."
  That is source-only language, but the visual green state can still imply
  readiness if Phase 18 does not require proof-boundary wording.
- The existing verifier mainly performs static string checks against the
  controller and client. That catches forbidden call paths, but it does not
  fully prove row-by-row behavior for stale saved packets, hostile true
  approval flags, parse errors, zero-blocker rows, or runtime-shaped output.

Adversarial lens:

The biggest overclaim path is not a hidden write. It is a polished operator
summary that organizes source data so well that agents or staff treat it as a
release lane. A pure runtime-shaped helper could accidentally widen trust if it
normalizes saved rows into fields named `ready`, `approved`, `live_apply`, or
`success` without hard false approvals and source-only proof labels. Phase 18
should assume future saved validation packets can be stale, inconsistent, or
too optimistic, then prove the summary fails closed anyway.

## What Phase 18 Must Prove

Phase 18 must prove all of the following before commit:

- The summary builder is pure and deterministic from provided rows or fixtures.
  It must not call Frappe DB, local apply preview, local apply, cache clear,
  deploy, provider, payment, DNS, customer-message, browser, Docker, network, or
  live/customer-facing routes.
- The Frappe whitelisted method remains a thin read-only wrapper: permission
  check, bounded `frappe.get_all` over explicit fields, pure summary call, and
  return.
- The output shape is Desk/runtime-friendly but source-only: every catalog
  summary and product row carries proof mode, evidence source, saved evidence
  timestamp when available, and false approval fields.
- Saved JSON parse errors, missing JSON, non-object JSON, stale-looking saved
  evidence, unknown states, and any true approval/public-success flags in saved
  input become blockers or invalid-source warnings, not green states.
- Zero product blockers in saved data does not approve public success, local
  apply, staging apply, live apply, mutation, cache clear, deploy, provider
  action, payment action, document/customer send, or product-scope changes.
- `source_declared` operating brand remains source evidence only. It must not
  become live brand-lane proof.
- Same-brand source uniqueness remains source evidence only. It must not become
  global/live uniqueness proof.
- The summary never chooses product inclusion, exclusion, retirement, revival,
  rename, disablement, variant collapse, route replacement, or release scope.
- UI language keeps the outcome as saved/source triage. Green indicators or
  "allowed" labels should be blocked unless paired with unambiguous text that
  no public/live/customer-facing action is approved from this summary.

## Required Acceptance Criteria

Before any Phase 18 implementation is committed:

- The only code behavior allowed is source-only summary shaping and verifier
  coverage. No Product Setup save/apply behavior, product records, Website
  Items, Items, Item Prices, provider/payment/DNS state, cache, deploy, customer
  messages, or live records may be touched.
- The contract must include synthetic fixtures for at least these rows:
  blocked saved packet, parse-error packet, missing validation packet,
  zero-blocker packet, stale/fresh timestamp examples, saved packet with true
  `public_success_claim_allowed`, saved packet with true
  `publish_apply_allowed`, saved packet with true `live_apply_approved`, and a
  source-declared brand/uniqueness row.
- The pure summary must clamp or explicitly invalidate all source-only approval
  claims so top-level and row-level approvals remain false.
- The summary must expose counts as triage counts only. Names like "ready
  product" or "live apply allowed" should either be removed from UI-facing
  labels or guarded by tests that prove they cannot be interpreted as action
  approval.
- Product rows must include product identifier, owner state, source proof mode,
  evidence source, saved evidence time, parse/staleness status, blocker count,
  clipped blocker messages, next owner step, next developer step, developer-help
  flag, public-success flag forced false, and false approvals.
- The verifier must exercise the pure helper behavior, not just grep for strings
  in the controller.
- Existing Phase 13-17 guarantees must remain intact:
  `owner_publish_readiness`, `publish_apply_approval`, `Show Readiness`,
  Phase 15 dashboard false approvals, and Phase 16 release packet blockers.
- Capability gate evidence must be recorded with the Product Setup projection
  authority failure loaded.

## Verifier Behavior That Should Block Commit

Required commands for a Phase 18 implementation commit:

```bash
python /home/guidingl/codex-framework/tools/capability_context_gate.py --cwd "$PWD" --task "Phase 18 source-only pure runtime-shaped Desk catalog summary contract" --loaded "capabilities/INDEX.md" --loaded "capabilities/failures/product-setup-projection-authority-drift.md" --loaded "capabilities/recipes/erpnext-product-blueprint-authoring.md"
python scripts/verify/product_blueprint_contract.py
python scripts/verify/product_setup_publish_readiness_contract.py
python scripts/verify/product_setup_catalog_readiness_contract.py
python scripts/verify/product_setup_release_packet_contract.py
python scripts/verify/product_setup_authority_packet_contract.py
python -m py_compile <new-or-edited-python-files>
node --check apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_product_blueprint/lt_product_blueprint.js
git diff --check
```

The verifier should exit nonzero if:

- Any source-only summary output sets local/staging/live apply, mutation, cache
  clear, deploy, provider, payment, customer-message, document-send, or
  public-success approval true.
- Any source-only output calls a product live, live-applied, publicly changed,
  customer-visible, safe to sell, or ready for public change.
- Any publish/apply/cache/deploy/provider/payment/customer-send/customer-facing
  route-read code path is introduced into the summary builder or Desk summary
  method.
- Saved `validation_json` can make top-level or row-level public-success or
  live-apply counts appear action-approved.
- A zero-blocker saved packet can bypass Phase 16 missing target-site proof,
  rollback review, owner scope approval, developer release review, target
  environment approval, or no-downtime/customer-impact approval.
- Parse errors, non-object JSON, missing saved packets, stale evidence, or
  unknown owner states can appear as ready, approved, or non-blocking.
- `source_declared` brand, same-brand source uniqueness, saved timestamps,
  dashboard counts, release packet existence, source commit identity, or owner
  approval is treated as live proof.
- The UI uses green/approval language without explicit source-only and
  no-approval boundaries.
- Product-scope actions such as delete, disable, rename, collapse, replace,
  revive, retire, reroute, or broaden are implied by summary data.
- Any forbidden ERP UI terms from `AGENTS.md` appear in new Desk labels or this
  artifact.

## Convergence

All lenses agree that Phase 18 is useful only as a hardening layer for Phase 17
testability. The contract should make overclaiming harder by proving row
behavior against adversarial saved packets. It should not add a new operator
workflow, release step, or authority model.

## Disagreement Or Dissent

The only real tension is whether the Phase 17 UI should continue showing counts
named `public_success_claim_allowed_count` and `live_apply_allowed_count`.
Technically, those fields can be useful as a danger signal if they ever become
nonzero. Operationally, they are risky labels in a Desk dialog. Phase 18 should
prefer explicit "source packet tried to claim X; summary blocked it" wording
over "X allowed" wording.

## Recommended Path

Implement Phase 18, if at all, as a narrow pure-helper and verifier phase:

1. Extract or add a pure catalog summary builder that accepts row dictionaries.
2. Keep the whitelisted Desk method as read-only row retrieval plus pure helper.
3. Add contract tests with hostile saved-packet fixtures.
4. Fail closed on every approval/public-success/live/mutation implication.
5. Leave UI buttons, local apply, release packets, catalog scope, runtime
   product data, and live/provider surfaces unchanged unless a later approved
   phase explicitly reopens them.

## Remaining Risk

This review and any Phase 18 pure contract remain source-only. They will not
prove current public routes, shop listing, product page copy, price display,
cart, checkout, payment, documents, customer receipts, cache state, provider
deploy state, rollback execution, or live site behavior.

Saved `LT Product Blueprint.validation_json` can be stale. A correct pure
summary can only label and block stale or optimistic saved evidence; it cannot
refresh target-site truth without a separate approved read path.

Owner usability remains unproven. Even with stronger tests, the Desk dialog may
still need operator review to ensure Jeff reads it as a blocker map and not a
release queue.

No product-scope decision is made here. Birthday Deliveries variant collapse,
Large head Missionary repair, product retirement/revival, and any live release
remain separate approval gates.
