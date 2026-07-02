# Repo History And Worktree Cleanup - 2026-05-17

## Purpose

Close out the repository hygiene track after cleanup commits were published from clean clones while the main local checkout still had duplicate local commits. This handoff is for future Codex/OpenClaw agents that need to understand why local `main` was reconciled, which stale worktrees were reviewed, and what proof was used before deletion.

## Scope

This was repo operations work only. It did not change ERPNext app behavior, owner access behavior, Product Setup behavior, checkout behavior, live Frappe Cloud state, or public website behavior.

Touched cleanup surfaces:

- Local git history alignment for `main`.
- Stale detached Codex worktrees under `/home/guidingl/.codex/worktrees/`.
- Cleanup documentation and capability receipts.

## What Was Done

1. Verified the active repo was on `main` and the working tree had no file changes.
2. Confirmed local `main` and `origin/main` had the same file content but a divergent graph caused by local duplicate commits and clean-clone pushed equivalents.
3. Rebasing local `main` onto `origin/main` skipped or dropped duplicate commits after comparing each local commit to the pushed remote equivalent.
4. Verified local `main` and `origin/main` both resolved to `d541a0c6fdb12ac280ec7eb044b7a4397be7fd8c`.
5. Reviewed two detached worktrees before removal:
   - `/home/guidingl/.codex/worktrees/84e7/locally-twisted`
   - `/home/guidingl/.codex/worktrees/lt-backend-checkout-docs-20260503`
6. Confirmed both worktrees were clean, their HEAD commits were ancestors of `main` and `origin/main`, and their visible feature value already existed in the current repo.
7. Deleted only those two approved stale worktrees and pruned the worktree registry.

## Duplicate Commit Mapping

These local commits were already represented by pushed remote commits and were not replayed as new work:

| Local duplicate | Remote/current commit | Topic |
|---|---|---|
| `9a0a542` | `5234763` | Owner phone action access |
| `5eb175d` | `90762f3` | Reflex Champagne catalog spelling |
| `661cef0` | `de95a3f` | Checkout conversion verifier pause bypass |
| `2c01db9` | `ce130df` | Maintenance admin heartbeat report role |
| `79c15ba` | `c3cbf31` | Persona workspace shortcut permissions |
| `cec81f2` | `4870fab` | Local contact form copy update |
| `914aa90` | `924ac6c` | Generic Product Setup runtime |
| `7a36e54` | `d541a0c` | Queue cleanup notes |

## Worktree Value Review

`/home/guidingl/.codex/worktrees/84e7/locally-twisted`

- HEAD: `5ff6964 feat: prefill contact form from service links`.
- State before deletion: clean, detached, ancestor of `main` and `origin/main`.
- Value check: contact prefill behavior and documentation are already present in current `main`, including `scripts/verify/contact_prefill.py`, `/contact` prefill docs, and service-link references.

`/home/guidingl/.codex/worktrees/lt-backend-checkout-docs-20260503`

- HEAD: `683b2d6 Align checkout lead conversion docs`.
- State before deletion: clean, detached, ancestor of `main` and `origin/main`.
- Value check: checkout lead conversion verifier, docs, and backend simplification references are already present in current `main`.

## Verification

Commands/results used for closeout:

- `git status -sb` -> `## main...origin/main`
- `git rev-parse HEAD` and `git rev-parse origin/main` -> both `d541a0c6fdb12ac280ec7eb044b7a4397be7fd8c`
- `git status --porcelain=v1` -> no output
- `git diff --exit-code` -> exit 0
- `git diff --cached --exit-code` -> exit 0
- `git ls-files --others --exclude-standard` -> no output
- `rg -n "^(<<<<<<<|>>>>>>>|=======$)" ...` -> no conflict markers
- `git worktree list --porcelain` -> only the main LT worktree remains
- `Test-Path` for both removed worktree paths -> `False`

## Current State

- `main` is aligned with `origin/main`.
- Working tree is clean.
- No linked stale LT Codex worktrees remain.
- No app code changed in this handoff.
- No live deploy was performed.

## Future-Agent Rule

Do not delete a detached worktree just because it is merged. First check:

1. Worktree status is clean.
2. Worktree HEAD is an ancestor of both `main` and `origin/main`.
3. The latest visible feature/topic from that worktree is already present in current source, docs, or verifiers.
4. GL has explicitly approved deleting that exact worktree path.

Capability reference: `capabilities/recipes/launch-repo-cleanup-and-evidence-retention.md`.

Agency backlink: `/home/guidingl/projects/Built_by_Cameron/lessons-learned.md`
now records the cross-client lesson for stale worktree value review before
deletion.
