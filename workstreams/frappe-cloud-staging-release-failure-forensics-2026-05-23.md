# Frappe Cloud Staging Release Failure Forensics - 2026-05-23

Status: **release execution stopped by GL; forensic/prevention mode only.**

This document is intentionally blunt for future agents. The 2026-05-22 to
2026-05-23 staging push attempt failed as a release process. It produced useful
source fixes and provider evidence, but the controller session repeatedly
continued provider/bootstrap churn after the work should have stopped for a
forensic review. Do not use this session as launch authority.

Action-item handoff for the next fix agent:
`workstreams/frappe-cloud-release-prevention-action-items-2026-05-23.md`.

Later guard handoffs added after this original forensic report:

- `workstreams/frappe-cloud-freeze-reopen-approval-helper-2026-05-23.md`
- `workstreams/frappe-cloud-staging-reopen-packet-prep-2026-05-23.md`
- `workstreams/frappe-cloud-app-mirror-sync-plan-helper-2026-05-23.md`
- `workstreams/release-artifacts/README.md`

Agents starting here must read those before attempting any freeze reopen,
app-mirror sync, provider deploy/update, hosted preflight, bootstrap/import,
or owner-review proof.

## Scope Boundary

- Applies to: Locally Twisted Frappe Cloud staging owner-review push,
  ecommerce/Product Setup/gallery bootstrap, app-root mirror deployment, and
  release gate behavior.
- Does not approve: live release, DNS, Stripe, Search Console, public indexing,
  live checkout, or owner-review readiness.
- Current required posture: freeze release execution until a new approved
  release controller runs the gates in this document.

## Current Known State At Stop

| Surface | Evidence |
|---|---|
| Full source repo | `origin/main` reached `a5fb5f5 Reload staging seed modules during bootstrap` |
| App-root mirror | `CBaen/Locally-Twisted-Frappe-App` reached `181076c239b2d1d3d508a41ac471c71f9d2b5158` |
| Last known provider observation before stop | Deploy `52caqn2v57` was `Running`; installed staging hash was still `3fd5a87eca6a6d2e23c95592f07d41196e4cd68f` |
| Release execution | Stopped by GL during provider polling |
| Owner-review status | Unproved; must be treated as **not ready** |
| Live/DNS/Stripe/Search Console | Not part of this failure lane and not approved |

Do not infer the final provider state from the interrupted poll. A future
release controller may check Frappe Cloud read-only state, but must not resume
mutation from this session's momentum.

## Failure Timeline

1. **Wrong provider payload shape.**
   `press.api.bench.deploy_and_update` was first called with nested `apps` and
   `sites` as stringified JSON instead of typed JSON arrays/objects. Frappe
   Cloud accepted the request far enough to create async work, then failed with
   `'str' object has no attribute 'get'`. Recorded release pipeline:
   `6podv9kvbn`.

2. **Migration reached real staging drift.**
   Typed JSON reached site update/migrate, then failed because
   `Portal Settings.default_portal_home` drifted during migration. Failed jobs:
   `8vspcanje0`, `63lqkkrppt`. Source fix: `0f6fcad`; app mirror fix:
   `9ddcb45`.

3. **Role fixture/order failure.**
   The next migrate failed because permission sync referenced `LT Owner Access`
   and `LT Manager Access` before roles existed. Failed job: `6itfpob0ra`.
   Source/app mirror fix: `2ca1b85` / `3e86bc1`.

4. **Provider app update succeeded, owner review still blocked.**
   Provider proof later showed app hash
   `409a64758dd8377e5541bf2ad019b0ba59042aef` deployed successfully on staging
   with deploy/candidate `2b78t20pnb`, `Active` site, and `0` running jobs.
   Worker F correctly recorded that this was provider proof only, not
   owner-review readiness.

5. **Bootstrap failed on hosted standard-report constraints.**
   Staging bootstrap then failed before catalog mutation with:
   `ValidationError: Standard reports can only be created in developer mode.`
   The failure occurred while syncing backend setup records before catalog
   import, leaving counts at `Item=0`, `Website Item=0`,
   `Website Slideshow=0`, `Website Slideshow Item=0`, and `User=2`.

6. **Process failure: repeated churn after the stop condition.**
   The controller patched, redeployed, and retried instead of stopping after the
   repeated provider/bootstrap failure pattern and documenting prevention gates.
   GL then stopped release execution.

## Root Causes

### Technical

- Frappe Cloud enqueue/API success was treated too close to terminal release
  proof. Async job status, site migration, config/cache, installed hash, app
  order, and running-job state are separate proof layers.
- Local ERPNext state masked fresh hosted-site failures. Local developer mode
  and existing records hid standard-report and role-order constraints.
- The staging bootstrap path mixed setup sync, user provisioning, catalog
  import, Product Setup projection, and gallery projection into one large
  mutation path without a preflight dry-run that could fail before provider
  mutation.
- Early staging gates had loose thresholds and weak gallery/account proof.
  Worker D and Worker G identified this before the process was truly complete.

### Process

- The release controller did not enforce a hard stop after repeated failed
  provider/bootstrap attempts.
- Subagents produced useful evidence, but not every helper owned a blocking
  artifact before mutation. The controller still carried too much critical path
  work alone.
- Documentation had correct warnings, but they were not mechanical gates. A
  future agent could still proceed while reading warnings as prose.
- User stop signals were not treated as an immediate process boundary quickly
  enough. Future agents must stop execution first, then investigate.

## Required Prevention Architecture

These are gates, not suggestions.

1. **Release controller quarantine.**
   This session and its release execution pattern are not approved launch
   authority. A future launch/staging controller must start from a clean
   release plan and explicitly cite this forensics document.

2. **One-failure-class stop rule.**
   After one provider mutation fails, the next action is forensic classification
   and prevention control. A second attempt is allowed only after the new guard
   is written or an independent artifact-owning triad signs the exact retry.
   After two related failures, all provider mutation stops.

3. **Provider mutation preflight artifact.**
   Before `deploy_and_update`, save a sanitized payload-shape artifact proving:
   bench group, site, site bench, app source, app release, target hash, typed
   JSON body shape, rollback hash, live boundary, and expected terminal checks.

4. **Fresh-site bootstrap preflight.**
   Bootstrap must have a dry-run/preflight mode that checks hosted constraints
   before catalog mutation:
   standard Report save rules, required roles, Portal Settings, Website
   Settings, `installed_apps` order, required app hooks, and exact expected
   catalog baselines.

5. **Staging owner-review gate remains hard blocking.**
   Owner-review ready requires staging evidence for required users, exact
   catalog baseline, Product Setup rows, Website Slideshow rows, product
   galleries, authenticated owner/backend routes, guest pause behavior, disabled
   public indexing, app order, installed hash, and zero running provider jobs.

6. **Triad must own artifacts.**
   Required roles:
   Controller, Provider Witness, Gate/Fixer, Recorder. Provider Witness must
   own provider-state proof. Gate/Fixer must own executable gate evidence or a
   blocking patch. Recorder must own docs parity. Advisory-only comments do not
   satisfy release triad.

7. **No launch continuation after GL stops execution.**
   If GL says stop, no polling, no deploys, no bootstrap, no "one more check."
   Future work becomes read-only forensic investigation until GL explicitly
   reopens release execution.

8. **Machine-readable lock, not prose-only warning.**
   The action items in
   `workstreams/frappe-cloud-release-prevention-action-items-2026-05-23.md`
   must become an executable release lock and controller guard before staging
   release execution is reopened. Documentation by itself failed here.

2026-05-23 local guard update: the first executable offline layer now exists:
`release_locks/locally-twisted-staging-forensic-freeze.json`,
`scripts/release/frappe_cloud_release_controller.py`,
`scripts/verify/release_lock_contract.py`,
`scripts/verify/release_controller_contract.py`,
`scripts/verify/frappe_cloud_payload_contract.py`, and
`scripts/verify/release_claim_language_contract.py`. Run
`npm run test:release-prevention` to prove this local prevention architecture.
This does not prove staging owner-review readiness and does not reopen
provider mutation.

2026-05-23 template parity update: `f5e2e91` updated
`workstreams/release-artifacts/2026-05-23-staging-freeze/TEMPLATE.md` so the
starter packet now includes the current required artifact shapes for
`freeze-reopen-approval.json`, `app-mirror-sync-plan.json`,
`deploy-completion.json`, and hosted preflight `checks`. This closes a local
documentation/template gap only. It does not create real release artifacts or
reopen provider mutation.

## Evidence Sources

- `CODING-HANDOFF.md`
- `ECOMMERCE-SHOP-HANDOFF.md`
- `locally-twisted-queue.md`
- `locally-twisted-decisions.md`
- `workstreams/frappe-cloud-staging-owner-review-2026-05-22.md`
- `workstreams/ecommerce-audit/staging-account-proof-2026-05-22.md`
- `workstreams/ecommerce-audit/staging-bootstrap-gate-worker-d-review-2026-05-22.md`
- `workstreams/ecommerce-audit/staging-bootstrap-gate-worker-g-review-2026-05-23.md`
- `workstreams/ecommerce-audit/staging-provider-job-proof-2026-05-23.md`
- `capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`
- `capabilities/failures/release-controller-churn-after-stop.md`
- `workstreams/frappe-cloud-release-prevention-action-items-2026-05-23.md`
- `workstreams/frappe-cloud-release-artifact-template-parity-2026-05-23.md`

## Next Safe Step

The next safe step is not another deploy. It is running the local prevention
contracts, then having a new release controller perform a read-only
current-state snapshot and produce a fresh artifact-backed release plan that
satisfies the prevention gates above. Provider mutation remains blocked while
`release_locks/locally-twisted-staging-forensic-freeze.json` is active.
