# Phase 15 Catalog Readiness Dashboard

Date: 2026-07-01

Status: source-only/offline dashboard tooling complete.

## Scope

This phase added a deterministic catalog readiness dashboard over saved Product
Setup authority packet report JSON. It does not collect live data and does not
change Product Setup, Website Item, Item, Item Price, provider, payment, DNS,
cache, deploy, or customer-message state.

No live mutation was performed.

## Capability Gate

Capability gate: PASS.

Loaded resources:

- `capabilities/INDEX.md`
- `capabilities/recipes/erpnext-product-blueprint-authoring.md`
- `capabilities/failures/product-setup-projection-authority-drift.md`

## Files

- `scripts/dev/lt_product_setup_catalog_readiness_dashboard.py`
- `scripts/verify/product_setup_catalog_readiness_contract.py`
- `workstreams/ecommerce-operator-hardening-2026-06-30/phase-15-catalog-readiness-dashboard-2026-07-01.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/phase-15-critical-review-2026-07-01.md`

## Behavior

The dashboard consumes saved output from
`scripts/dev/lt_product_setup_authority_packet_report.py` and emits:

- catalog-level counts;
- product rows for owner/developer triage;
- blocker group counts;
- variant explosion summary;
- owner-safe actions;
- developer next actions;
- false local/staging/live apply, cache clear, deploy, mutation, and public-success approvals.

`--fail-on-blocker` exits `1` while blockers remain. Malformed or missing input
exits `2`.

## Verification

Commands run from the linked worktree:

```bash
python /home/guidingl/codex-framework/tools/capability_context_gate.py --cwd "$PWD" --task "Phase 15 source-only offline LT Product Setup catalog readiness dashboard from saved authority packet reports" --loaded "capabilities/INDEX.md" --loaded "capabilities/recipes/erpnext-product-blueprint-authoring.md" --loaded "capabilities/failures/product-setup-projection-authority-drift.md"
```

Exit: `0`.

```bash
python scripts/verify/product_setup_catalog_readiness_contract.py
```

Exit: `0`. Covered synthetic blocked dashboard behavior,
collector-index rejection, `--fail-on-blocker`, deterministic output, false
approvals, and the saved full-catalog authority packet when present. Four tests
passed.

```bash
python -m py_compile scripts/dev/lt_product_setup_catalog_readiness_dashboard.py scripts/verify/product_setup_catalog_readiness_contract.py
```

Exit: `0`.

```bash
python scripts/dev/lt_product_setup_catalog_readiness_dashboard.py --packet-report /tmp/lt-catalog-authority-full-20260630/authority-packet-report.json --output /tmp/lt-catalog-readiness-dashboard.json --pretty --fail-on-blocker
```

Exit: `1`, expected because the saved catalog report still has blockers.
Output summary: 47 products, 47 blocked products, 284 blockers, six
variant-explosion products, and all apply/cache/deploy/mutation approvals
false.

```bash
python scripts/verify/product_setup_authority_packet_contract.py
python scripts/verify/product_setup_publish_readiness_contract.py
```

Exit: `0` for both.

## Residual Risk

This is a dashboard over saved authority packet data. Older saved Phase 4 packet
reports do not include newer source-authority fields, so those counts stay
empty until a newer packet report is generated. The dashboard is triage evidence
only and does not approve publish/apply, cache clear, deploy, provider action,
or catalog mutation.
