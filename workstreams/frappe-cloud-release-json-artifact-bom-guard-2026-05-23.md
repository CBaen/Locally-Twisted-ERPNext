# Frappe Cloud Release JSON Artifact BOM Guard - 2026-05-23

Status: **implemented local/offline guard hardening; no provider mutation**.

## Scope

During the `9e63fef` read-only staging packet, PowerShell wrote
`read-receipt.json` with a UTF-8 BOM. The release controller blocked while
parsing the JSON before it reached the intended no-go gate:
missing `freeze-reopen-approval.json`.

This work keeps the controller focused on release authority and staging proof,
not artifact encoding noise.

## Changes

- `scripts/release/release_guard_common.py` now reads JSON artifacts with
  `utf-8-sig`.
- `scripts/verify/release_controller_contract.py` now writes a BOM-bearing
  read-receipt fixture and proves `read_only_forensics` accepts it.

## Boundaries

- No provider, staging, app mirror, live, DNS, Stripe, Search Console,
  bootstrap, migrate, cache, indexing, checkout, or secret-reading mutation.
- This does not create approval or reopen forensic-freeze.
- Packet writers should still prefer UTF-8 without BOM.

## Evidence

- `python -m py_compile scripts\release\release_guard_common.py scripts\verify\release_controller_contract.py`
- `python scripts\verify\release_controller_contract.py`

## Cross-References

- Latest read-only packet:
  `workstreams/release-artifacts/2026-05-23-staging-reopen-9e63fef-readonly/`
- Decision:
  `locally-twisted-decisions.md`
- Lesson:
  `lessons-learned.md`
- Capability:
  `capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`
