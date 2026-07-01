# Phase 16 Release Packet Design

Date: 2026-07-01

Status: source-only/offline release packet tooling complete.

## Scope

This phase added a deterministic product-specific pre-mutation release packet
report over saved Phase 15 catalog readiness dashboard JSON. It does not collect
live data and does not change Product Setup, Website Item, Item, Item Price,
provider, payment, DNS, cache, deploy, or customer-message state.

No live mutation was performed.

## Capability Gate

Capability gate: PASS.

Loaded resources:

- `capabilities/INDEX.md`
- `capabilities/recipes/erpnext-product-blueprint-authoring.md`
- `capabilities/failures/product-setup-projection-authority-drift.md`

## Files

- `scripts/dev/lt_product_setup_release_packet_report.py`
- `scripts/verify/product_setup_release_packet_contract.py`
- `workstreams/ecommerce-operator-hardening-2026-06-30/phase-16-release-packet-design-2026-07-01.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/phase-16-critical-review-2026-07-01.md`

## Behavior

The report consumes saved output from
`scripts/dev/lt_product_setup_catalog_readiness_dashboard.py` and emits a
single-product release packet with:

- product identifiers and route slug;
- source dashboard summary;
- proof gates and missing gates;
- rollback requirements;
- target environment approvals;
- no-downtime and customer-impact requirements;
- stop condition;
- owner and developer allowed actions;
- false mutation, live apply, cache clear, deploy, provider, payment, and
  customer-message approvals.

The product filter matches `product_setup`, `item_code`, route slug, or full
route. `--fail-on-blocker` exits `1` while the selected packet remains blocked.
Malformed, non-dashboard, missing, or ambiguous input exits `2`.

Even when a selected product has zero Phase 15 dashboard blockers, the release
packet remains blocked until fresh target-site proof, rollback review, owner
approval, developer release review, target environment approval, and no-downtime
customer-impact approval exist. The script does not invent an approved path.

## Verification

Commands run from the linked worktree:

```bash
python /home/guidingl/codex-framework/tools/capability_context_gate.py --cwd "$PWD" --task "Phase 16 source-only offline LT Product Setup pre-mutation release packet report from saved Phase 15 catalog readiness dashboard JSON" --loaded "capabilities/INDEX.md" --loaded "capabilities/recipes/erpnext-product-blueprint-authoring.md" --loaded "capabilities/failures/product-setup-projection-authority-drift.md"
```

Exit: `0`.

```bash
python scripts/verify/product_setup_release_packet_contract.py
```

Exit: `0`. Six tests passed. Covered blocked dashboard product output,
product filter matching by `product_setup`, `item_code`, route slug, and full
route, non-dashboard input rejection, deterministic output, zero-dashboard-blocker
products remaining blocked without target proof, and the saved
`/tmp/lt-catalog-readiness-dashboard.json` artifact when present.

```bash
python -m py_compile scripts/dev/lt_product_setup_release_packet_report.py scripts/verify/product_setup_release_packet_contract.py
```

Exit: `0`.

```bash
python scripts/dev/lt_product_setup_release_packet_report.py --dashboard /tmp/lt-catalog-readiness-dashboard.json --product large-head-missionary --output /tmp/lt-product-setup-release-packet-large-head-missionary.json --pretty --fail-on-blocker
```

Exit: `1`, expected because the saved dashboard product remains blocked.
Output summary: product `large-head-missionary`, seven dashboard blockers, nine
missing release gates, and all apply/cache/deploy/mutation/provider/payment and
customer-message approvals false.

```bash
python scripts/verify/product_setup_catalog_readiness_contract.py
python scripts/verify/product_setup_publish_readiness_contract.py
python scripts/verify/product_setup_authority_packet_contract.py
python scripts/verify/product_blueprint_contract.py
```

Exit: `0` for all. Covered the adjacent Phase 15 dashboard contract, owner
publish readiness contract, authority packet contract, and Product Setup source
contract.

```bash
git diff --check
```

Exit: `0`.

Forbidden ERP UI terms check against the three Phase 16 files found no matches.

## Witness Notes

Phase 16 used a real spawned builder lane and a real spawned critical witness
lane from the parent session. The critical witness artifact labels its internal
review as degraded because that subagent could not see subagent tooling from
inside its own context; parent orchestration still treated it as an independent
witness artifact, not as proof by itself.

## Residual Risk

This is a reporting surface over saved dashboard data. It does not prove current
live catalog state, target-site route behavior, cart, checkout, payment labels,
documents, customer receipts, media files, cache state, provider-hosted deploy
state, or rollback execution.

Saved `/tmp` dashboard artifacts are useful when present but can go stale. A
passing release-packet contract proves the report logic and blockers; it does
not approve any write.
