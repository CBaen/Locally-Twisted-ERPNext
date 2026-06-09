# Launch Repo Cleanup - 2026-05-10

## Scope

Keep the Locally Twisted launch repo light enough for client handoff while preserving production source, executable verification, and durable handoff knowledge. This lane is about repo hygiene for launch, not product-page buildout, Memorial Balloons, or broad research retention.

## Current Boundary

- Locally Twisted launch remains the priority.
- Memorial Balloons is a separate side business and must not be mixed into the LT launch repo or launch proof.
- GitHub is the archive for old LT experiment output. The working repo should not keep duplicate generated research, raw local drops, stale mirrors, or one-off verifier debris after their production value has been translated.

## Cleanup Completed

- Removed regenerable local output and verifier debris: `.tmp/`, `output/`, `test-results/`, `test invoices/`, Python `__pycache__/`, old generated build folders, and stale local verification artifacts.
- Moved large raw photo drops out of the repo, without deleting them, to `C:\Users\baenb\projects\Built_by_Cameron\_CLIENTS\locally-twisted-local-drops\`.
- 2026-05-11 follow-up: removed the tracked duplicate raw launch photos from `assets/what we do photos/` after verifying exact blob-hash copies in `C:\Users\baenb\projects\Built_by_Cameron\_CLIENTS\locally-twisted-local-drops\landing-page-pics-20260510\`.
- Added `.gitignore` guards for raw/drop folders: `assets/landing page pics/`, `assets/landing page assets/`, `assets/hero assets/`, `balloon drop/`, and `balloon drop.zip`.
- Removed old ignored legacy_source mirror/reference output, old Chrome/audit render output, upstream app clones, and research throwaways that were no longer source of truth.
- Removed the tracked `contests/audience-pages-2026-05-08/**` contest output from the launch repo. Use Git history if that old contest material is ever needed.
- Updated launch docs that pointed to deleted `.tmp` evidence so future agents rerun the verifier instead of chasing a removed local snapshot.
- 2026-05-11 follow-up: removed the forbidden linked worktree/branch `ecommerce-phase-1-4-hygiene-20260510` only after verifying the branch tip was already contained in `main` and the linked worktree had no unstaged or untracked files.
- 2026-05-11 follow-up: removed the ignored forensic screenshot folders generated during route-regression research after the durable findings were documented.

## Kept On Purpose

- Production app source, route controllers, templates, static assets, verifiers, capability cards, and feature handoffs.
- Active ecommerce/customer-portal/design-app work owned by other agents.
- `.env`, runtime secrets, local stack state, and ignored dependency folders needed for current test execution.
- Remaining `research/` material that is still active or modified by other workstreams. Do not delete it as a broad sweep.

## Verification

- `python scripts/verify/ecommerce_pause_contract.py` passed after the cleanup.
- `python scripts/verify/nav_ia.py` passed after the cleanup.
- `git diff --check` passed for the cleanup-owned docs and `.gitignore`; Git warned that `workstreams/website-launch.md` will normalize CRLF to LF when touched.
- 2026-05-11 follow-up: `git merge-base --is-ancestor ecommerce-phase-1-4-hygiene-20260510 main` passed before branch deletion; `git branch --list` and `git branch -r` then showed only `main` / `origin/main`. `git hash-object` proved the three removed image assets match the copies under `locally-twisted-local-drops\landing-page-pics-20260510\`.

## Next Safe Cleanup Slice

After launch, review remaining `research/`, `audits/`, and active ecommerce-audit material one lane at a time. Keep only files that are still source evidence, executable proof, or active handoff material. Do not bulk-delete modified work from other agents.
