# 2026-08-23 - ERP Capability Card Deletion

## Decision

Retire eight project capability cards from current guidance. Public `main`
moved from parent `d72785d39fddfd5cfb2299f152c30c1a4bf20ff0` to its single
child `d099f3f4bb8d5b24ba41af0aa1403d87f67eb70b` for this deletion.

| Capability ID | Deleted path |
|---|---|
| `erpnext-business-automation-index` | `capabilities/recipes/erpnext-business-automation-index.md` |
| `erpnext-ecommerce-receiving-architecture` | `capabilities/recipes/erpnext-ecommerce-receiving-architecture.md` |
| `erpnext-finance-controlled-automation` | `capabilities/recipes/erpnext-finance-controlled-automation.md` |
| `erpnext-inquiry-photo-delivery-contract` | `capabilities/recipes/erpnext-inquiry-photo-delivery-contract.md` |
| `erpnext-live-product-visibility-retirement` | `capabilities/recipes/erpnext-live-product-visibility-retirement.md` |
| `erpnext-no-live-customer-reminders` | `capabilities/recipes/erpnext-no-live-customer-reminders.md` |
| `erpnext-record-level-failure-recorder` | `capabilities/recipes/erpnext-record-level-failure-recorder.md` |
| `erpnext-webshop-guest-party-contract` | `capabilities/recipes/erpnext-webshop-guest-party-contract.md` |

The same commit removed 26 generated/index rows and no others:

- 8 from `capabilities/INDEX.md`;
- 8 from `capabilities/registry/capability-registry.jsonl`;
- 10 from `capabilities/evidence/capability-evidence.jsonl`.

## Effect And Non-Effect

This was capability-document retirement only. It did not delete or change
ERPNext runtime code, business logic, workstreams, public behavior, customer or
provider state, or historical implementation evidence. The commit changed only
the eight card paths and the three reference artifacts above, with 1,342 lines
deleted and no additions. BTFP and non-ERP capability content remained present.

Public readback after the commit confirmed all eight card paths absent and all
three reference artifacts free of the eight IDs and paths. Their JSONL syntax
remained valid.

## Current Navigation

Current project documents and surviving capability cards must not route agents
to the deleted files. They should point to the narrower surviving failure,
recipe, verifier, decision, or workstream that owns the behavior. In particular:

- live product visibility: `2026-06-23-live-product-visibility-disable.md`,
  `../workstreams/ecommerce-audit/live-product-disable-2026-06-23.md`, and
  `../capabilities/failures/owner-catalog-guard-live-disable-drift.md`;
- inquiry photos and owner attachments:
  `../workstreams/inquiry-photo-storage-owner-attachments-2026-05-15.md` and
  `../capabilities/failures/public-form-photo-storage-owner-attachment-gap.md`;
- ecommerce receiving: `../workstreams/erpnext-ecommerce-receiving-architecture.md`
  plus the surviving product, price, checkout, media, and storefront guards;
- business automation and record-level failure evidence:
  `../workstreams/business-automation-index.md`,
  `../workstreams/fail-loud-record-level-hardening.md`, and their current
  verifiers;
- Webshop Guest cleanup: the surviving
  `../capabilities/failures/webshop-guest-party-cleanup-regression.md` and
  `../capabilities/recipes/frappe-public-storefront-security.md`.

## Historical Reference Policy

Dated research, implementation receipts, and append-only records may retain
then-true references. Those references are historical, not current navigation.
Resolve a deleted card's original bytes against parent commit
`d72785d39fddfd5cfb2299f152c30c1a4bf20ff0` rather than recreating a current
pointer or adding a tombstone to the active index, registry, or evidence ledger.

## Recovery And Rollback

The pre-deletion 11-file slice is retained outside the repository at:

`/home/guidingl/backups/capability-graduation-matrix/erp-delete-20260823T2109-d72785d3.zICepJ`

- `affected-files.tar` SHA-256:
  `3159037e12b4a651a9f4efcde17170c5906103d23a99d74b585711983f31702f`
- `manifest.json` SHA-256:
  `ea13c3f54c09169464d297ab17314b96b70a0e5520b1ecf943cdd5d41975cd21`

Two recovery methods are valid:

1. Revert commit `d099f3f4bb8d5b24ba41af0aa1403d87f67eb70b` with a new
   non-force commit.
2. Restore the exact 11 archived files according to the retained manifest and
   verify every file hash before committing.

If either recovery method is used after this decision, update the current
navigation surfaces in the same rollback so restored cards and active docs do
not disagree. Do not overwrite unrelated later changes.

## Capability Gate

Capability gate: PASS. Loaded `capabilities/INDEX.md`,
`capabilities/recipes/capability-registry-generation.md`, and the shared
`dirty-repo-documentation-parity-closeout` recipe.

## Decided By

Guiding Light authorized the exact eight-card retirement and the project-local
documentation parity closeout. No runtime, provider, customer, deployment, or
payment change is part of this decision.
