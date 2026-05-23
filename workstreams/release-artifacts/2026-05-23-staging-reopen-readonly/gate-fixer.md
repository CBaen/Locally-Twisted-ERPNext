# Gate/Fixer Artifact

Target: staging owner-review gate and hosted bootstrap preflight gate.

Evidence:

- `scripts/verify/staging_owner_review_gate.py --expected-hash-from-mirror --json` now emits strict JSON even on failure.
- The regenerated read-only gate artifact is `staging-owner-review-gate-readonly.json`.
- The gate failed on the actual staging site with zero catalog/Product Setup/gallery rows, missing `locallytwisted@gmail.com`, missing `marketing@exploringnotboring.com`, and representative product/category routes returning `404`.
- The hosted preflight probe failed with HTTP `417` because `locally_twisted.staging_owner_review_bootstrap.preflight_staging_owner_review_bootstrap` is absent on the deployed app.
- Local contracts still pass after the verifier fix: `python scripts/verify/staging_owner_review_gate_contract.py` and `npm run test:release-prevention`.

BLOCK:

Do not bootstrap/import the staging catalog from the currently deployed app. It lacks the non-mutating hosted preflight method and the current source split.

Next safe fixer action:

When release execution is explicitly reopened, sync and deploy the current app-root mirror first. Then run the hosted preflight endpoint before any catalog seed/import path.
