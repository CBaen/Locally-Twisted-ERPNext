# Frappe Cloud Doc Head Correction - 2026-05-23

Status: **documentation/source-history correction only**.

Current repository head at correction time:
`5e11003d5cf8cd0d81e3d8e5acd4087a7d104c24` on `main` / `origin/main`.

Underlying template-fix commit:
`f5e2e91e576f5aec11beb2c11f8b71df83a603e6`.

No provider, staging, live, DNS, Stripe, Search Console, app mirror,
bootstrap, migrate, cache, checkout, or secret-reading mutation was performed.

## What Was Corrected

Some front-door handoffs still named `f5e2e91` as the latest GitHub archive
after `5e11003` had already documented the template parity work. That was a
source-history drift, not a release-state change.

The corrected model:

- `5e11003` is the current GitHub archive / documentation parity commit.
- `f5e2e91` is the source commit that updated the staging-freeze packet
  template.
- Neither commit is freeze-reopen approval, app mirror freshness, provider
  deploy/update completion, hosted bootstrap preflight proof, staging data
  proof, owner-review readiness, or live approval.

## Provider Witness Recheck

Provider Witness rechecked after `5e11003`:

- repo clean on `main`, matching `origin/main`
- app-root mirror still
  `181076c239b2d1d3d508a41ac471c71f9d2b5158`
- mirror freshness against current source still `ok=false`
- staging still provider-stable but not owner-review ready
- controller `read_only_forensics` passed
- controller `app_mirror_sync` remained blocked with missing
  `freeze-reopen-approval.json`

The current goal/chat context is not enough to create
`freeze-reopen-approval.json`. A future release attempt needs a fresh
artifact-bound approval that passes the controller.

## Updated Files

- `CODING-HANDOFF.md`
- `ECOMMERCE-SHOP-HANDOFF.md`
- `locally-twisted-queue.md`
- `locally-twisted-decisions.md`
- `lessons-learned.md`
- `capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`
- `capabilities/failures/release-controller-churn-after-stop.md`
- `capabilities/evidence/capability-evidence.jsonl`
- `scripts/release/release_guard_common.py`
- `scripts/release/frappe_cloud_release_controller.py`
- `scripts/verify/release_controller_contract.py`
- `scripts/README.md`

## Follow-Up Guard Hardening

Gate/Fixer added cross-artifact release chain binding after this source-history
correction began. The implementation is documented in
`workstreams/frappe-cloud-release-artifact-chain-binding-2026-05-23.md` and was
verified with `python scripts\verify\release_controller_contract.py` plus
`npm run test:release-prevention`.

## Backlinks

- `workstreams/frappe-cloud-release-artifact-template-parity-2026-05-23.md`
- `workstreams/frappe-cloud-release-artifact-chain-binding-2026-05-23.md`
- `workstreams/frappe-cloud-release-prevention-action-items-2026-05-23.md`
- `workstreams/frappe-cloud-staging-release-failure-forensics-2026-05-23.md`
- `release_locks/locally-twisted-staging-forensic-freeze.json`
