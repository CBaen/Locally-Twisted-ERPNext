# Frappe Cloud Freeze Approval Timestamp Guard - 2026-05-23

## Status

Local guard implemented under active forensic-freeze. No provider, staging,
live, DNS, Stripe, Search Console, app mirror, bootstrap, migrate, cache,
checkout, or secret-reading mutation was performed.

## What Changed

- `scripts/release/release_guard_common.py` now parses
  `freeze-reopen-approval.json` timestamps as ISO-8601 values with timezone
  offsets.
- Reopen approval now fails when:
  - `approved_at` or `expires_at` is missing, malformed, or timezone-less.
  - `approved_at` is future-dated beyond controller clock skew.
  - `expires_at` is already expired.
  - `expires_at` is not after `approved_at`.
  - the approval window is longer than 24 hours.
- `scripts/verify/release_lock_contract.py` now covers valid dynamic approval
  windows plus expired, malformed, timezone-less, future-dated, and overlong
  approval failures.
- `scripts/verify/release_controller_contract.py` now creates dynamic bounded
  approvals instead of fixed 2026 timestamps.

## Documentation Parity

- `CODING-HANDOFF.md`, `ECOMMERCE-SHOP-HANDOFF.md`,
  `locally-twisted-queue.md`, `scripts/README.md`, and
  `workstreams/release-artifacts/README.md` now distinguish archived
  snapshot-source read-only packets from current mutation-capable release
  packets.
- `workstreams/release-artifacts/2026-05-23-staging-freeze/TEMPLATE.md` now
  names the approval timestamp contract directly.
- `capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`,
  `locally-twisted-decisions.md`, `lessons-learned.md`, and
  `capabilities/evidence/capability-evidence.jsonl` record the guard.

## Current Release Boundary

The active lock remains
`release_locks/locally-twisted-staging-forensic-freeze.json`. The current goal
or chat history is not a valid reopen artifact. A future mutation-capable
packet must include a fresh, artifact-bound `freeze-reopen-approval.json`,
fresh source-bound app mirror/provider/deploy/preflight artifacts, and a valid
read receipt.

## Verification

Run before trusting this guard:

```powershell
python -m py_compile scripts\release\release_guard_common.py scripts\release\frappe_cloud_release_controller.py scripts\verify\release_lock_contract.py scripts\verify\release_controller_contract.py
python scripts\verify\release_lock_contract.py
python scripts\verify\release_controller_contract.py
npm run test:release-prevention
python scripts\verify\verifier_cli_contract.py
git diff --check
```

For boundary proof, the release controller must still allow read-only
forensics with a valid receipt and block `app_mirror_sync` when
`freeze-reopen-approval.json` is missing.
