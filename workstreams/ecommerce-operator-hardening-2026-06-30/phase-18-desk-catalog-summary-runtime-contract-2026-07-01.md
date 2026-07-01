# Phase 18 Desk Catalog Summary Runtime Contract

Date: 2026-07-01

Status: source-only refactor and verifier complete.

## Route Record

Mode: triadic-review with implementation and critical-witness subagents.
Decision needed: move the Phase 17 Desk catalog readiness row and summary construction out of the Frappe controller without weakening source-only approval blockers.
Scope owner: Locally Twisted child/client repo, Product Setup authority hardening lane.
System/project/runtime classification: single project, source-only Desk/readiness contract.
Allowed actions: edit the owned Python source, verifier, and this workstream note; run pure/source verifiers.
Forbidden actions: deploy, live mutation, cache clear, provider, payment, DNS, customer-message, ERPNext record mutation, Frappe Cloud, or public-route proof claims.
Evidence bar: py_compile, pure runtime-shaped verifier, static Product Blueprint contract, diff whitespace check, and restricted term scans.
Stop condition: any required proof needing live/public/provider/runtime mutation, or any summary path that turns saved validation JSON into public/live approval.

Lane owner: `codex-20260630-lt-product-setup-brand-authority`.
Artifact path: this file.
Coordination path: `/home/guidingl/agent-coordination/LIVE-BOARD.md` and `SESSION-REGISTRY.md`.
File/system ownership: only the Phase 18 owned files named by GL.
Dependencies: Phase 17 Desk catalog readiness summary and Product Setup projection authority drift guard.
Anti-overlap rule: do not touch public site, app mirror, release, provider, payment, DNS, or customer-message lanes.
Escalation trigger: any need for live proof, Desk runtime mutation, or product-scope decision.

## Capability Gate

Capability gate: PASS.

Loaded resources:

- `capabilities/INDEX.md`
- `capabilities/recipes/erpnext-product-blueprint-authoring.md`
- `capabilities/failures/product-setup-projection-authority-drift.md`

## Triadic Review

### Review Type

Real subagent tooling was used by the parent orchestration. The builder lane
implemented the pure helper/verifier slice; the critical witness lane wrote the
Phase 18 review artifact.

### Decision

Whether the Phase 17 Desk catalog readiness summary should remain inline in the whitelisted Frappe controller or move into a Frappe-independent pure module.

### Lens Findings

Source-boundary lens:
The whitelisted method should only prove permission handling and read the saved Product Setup fields. Row parsing, malformed JSON handling, counts, and false approval flags are deterministic source logic and belong in a pure module.

Fail-loud lens:
Malformed validation JSON and missing validation JSON must not become quiet green states. Bad JSON blocks the row, missing JSON blocks the row, and both tell the developer to re-save the Product Setup so validation JSON can be regenerated.

Adversarial approval lens:
Saved validation JSON is not trusted as an approval source. Even if a runtime-shaped row contains true public/live/apply/cache/deploy/provider/payment/customer-message flags, the Desk catalog summary blocks that row and clamps summary and row approval flags to false in this phase.

### Convergence

All lenses point to extracting a pure builder and testing it directly with runtime-shaped rows. This keeps Desk behavior read-only and makes the string contract executable without Frappe.

### Disagreement Or Dissent

The only material tightening from Phase 17 is that missing validation JSON is now blocked instead of merely falling back to the row validation status. That is intentional: no saved validation packet means no source proof.

### Recommended Path

Use `product_setup_catalog_readiness.py` as the deterministic summary builder. Keep the Desk method as permission plus `frappe.get_all` plus `build_catalog_readiness_summary(...)`.

### Remaining Risk

This still summarizes saved Product Setup validation rows only. It does not prove current public catalog state, cart, checkout, payment, provider, deploy, cache, DNS, customer messages, or rollback readiness.

## Files

- `apps/locally_twisted/locally_twisted/product_setup_catalog_readiness.py`
- `apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_product_blueprint/lt_product_blueprint.py`
- `scripts/verify/product_setup_desk_catalog_summary_contract.py`
- `scripts/verify/product_blueprint_contract.py`
- `workstreams/ecommerce-operator-hardening-2026-06-30/phase-18-desk-catalog-summary-runtime-contract-2026-07-01.md`

## Behavior

`product_setup_catalog_readiness.py` has no Frappe import. It accepts row-like mappings shaped like `frappe.get_all` results and builds row plus catalog summary payloads.

The whitelisted Desk method still requires `System Manager` or `Item Manager`, performs one `frappe.get_all` over `CATALOG_READINESS_FIELDS`, and delegates summary construction to the pure builder.

Malformed validation JSON becomes a blocked row with `Saved validation JSON could not be read.` Missing validation JSON becomes a blocked row with a re-save blocker. Both produce the developer step `Re-save this Product Setup so validation JSON can be regenerated.`

Saved validation JSON that claims any source-only approval flag is also blocked
with `Saved validation JSON included source-only approval claims; release proof
is still required.` The output still clamps every approval flag false.

The summary remains `proof_mode: source_saved_validation_only` and `source: saved_validation_json`. Public success claim counts and live apply counts are always `0`, and all summary/row approval booleans remain false.

## Verification

Commands run from the linked worktree:

```bash
python /home/guidingl/codex-framework/tools/capability_context_gate.py --cwd "$PWD" --task "Phase 18 source-only Product Setup Desk catalog readiness runtime-shaped contract proof with no live mutation" --loaded "capabilities/INDEX.md" --loaded "capabilities/recipes/erpnext-product-blueprint-authoring.md" --loaded "capabilities/failures/product-setup-projection-authority-drift.md"
python -m py_compile apps/locally_twisted/locally_twisted/product_setup_catalog_readiness.py apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_product_blueprint/lt_product_blueprint.py scripts/verify/product_setup_desk_catalog_summary_contract.py scripts/verify/product_blueprint_contract.py
python scripts/verify/product_setup_desk_catalog_summary_contract.py
python scripts/verify/product_blueprint_contract.py
```

Exit: `0` for all. The new verifier ran 4 tests. `product_blueprint_contract.py` ran 29 tests.

Final closeout checks:

```bash
git diff --check
if rg -n "Q[u]alification Status|Q[u]alified By|Q[u]alified On|L[e]ad Owner|P[i]peline Stage|O[p]portunity" apps/locally_twisted/locally_twisted/product_setup_catalog_readiness.py apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_product_blueprint/lt_product_blueprint.py scripts/verify/product_setup_desk_catalog_summary_contract.py scripts/verify/product_blueprint_contract.py workstreams/ecommerce-operator-hardening-2026-06-30/phase-18-desk-catalog-summary-runtime-contract-2026-07-01.md; then exit 1; else echo "no forbidden UI labels"; fi
if rg -n '"(local_apply_approved|staging_apply_approved|live_apply_approved|mutation_approved|cache_clear_approved|deploy_approved|provider_approved|payment_approved|customer_message_approved|public_success_claim_allowed)"[[:space:]]*:[[:space:]]*True' apps/locally_twisted/locally_twisted/product_setup_catalog_readiness.py apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_product_blueprint/lt_product_blueprint.py; then exit 1; else echo "no true approval flags in runtime source"; fi
```

Exit: `0` for `git diff --check`; both restricted scans printed no-match messages and exited `0`.

## Residual Risk

This is source-only/read-only. It does not approve publish/apply, live repair, cache clearing, deploy, provider work, payment work, DNS changes, customer messaging, or ERPNext record mutation.

Saved validation JSON can still be stale until the Product Setup row is revalidated. The new pure verifier proves the summary construction contract, not live catalog correctness.
