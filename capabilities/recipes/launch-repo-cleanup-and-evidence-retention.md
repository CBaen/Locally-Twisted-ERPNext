---
id: launch-repo-cleanup-and-evidence-retention
name: Launch Repo Cleanup And Evidence Retention
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted launch repo cleanup, raw asset intake, generated evidence retention, stale artifact deletion, and forbidden branch/worktree cleanup
currently_true: true
verification_level: 2
last_verified: 2026-05-17
evidence_quality: direct
successful_uses: 3
failed_uses: 0
regressions: 0
depends_on:
  - codex-browser-verification-surface
  - fail-loud-operating-law
used_by: []
tags:
  - Locally Twisted
  - launch cleanup
  - stale artifacts
  - raw assets
  - evidence retention
  - main-only git hygiene
---

# Launch Repo Cleanup And Evidence Retention

Use this recipe when the LT repo needs cleanup before launch, handoff, commit, or client review.

## Rule

The repo keeps production source, executable verification, source evidence that is still active, and durable handoffs. It does not keep duplicate generated output, stale research mirrors, raw local drops, or one-off evidence files after their useful claims have moved into tracked docs/verifiers.

GitHub is the archive for tracked historical experiments. Local holding folders outside the repo are acceptable for raw client/photo drops that are not ready to become production source.

## Use When

- GL asks to make the repo lighter or client-ready.
- Raw photo/design drops appear under `assets/`.
- Generated reports, Playwright screenshots, mirror folders, build outputs, or verifier debris accumulate.
- A research/contest/prototype output has already been translated into production app files or durable docs.
- A launch handoff references ignored `.tmp/` or `output/` evidence that has been deleted.
- A forbidden branch or linked worktree appears during launch cleanup.

## Procedure

1. Verify branch and repo state first. LT work happens on `main`.
2. Inventory before deleting. Separate production source, active work, ignored/generated output, raw drops, and stale tracked experiments.
3. Delete only regenerable ignored output directly: caches, build output, screenshots, stale local verifier reports, and generated preview folders.
4. Move large raw photo drops outside the repo when they may still be useful but are not production source.
5. Delete tracked experiment output only when the implemented production source and durable handoffs already exist. Git history remains the archive.
6. For a forbidden branch or linked worktree, do not keep it as a bookmark. Prove whether it has unique work first: inspect the linked worktree, check staged/unstaged/untracked files, and run `git merge-base --is-ancestor <branch-or-head> main` before removal.
   - For detached worktrees, also verify the feature value is already present in current source/docs/verifiers. A clean ancestor check proves commit containment; it does not prove the topic was reviewed.
   - Get explicit approval for the exact worktree path before deletion.
7. Before committing tracked asset deletions, prove the asset is preserved by Git history, an exact local holding copy, or an intentional production replacement.
8. Add `.gitignore` guards for raw/drop paths that should not re-enter the launch repo.
9. Update the feature handoff, queue, decisions, lessons, and capability index when the cleanup changes future-agent behavior.
10. Run the narrow verifiers that prove cleanup did not break launch posture.
11. In a shared worktree with unrelated active changes, commit with explicit files or an isolated index. Do not stage unrelated agent work.

## Keep

- Frappe app source, route controllers, Jinja templates, CSS/JS assets, fixtures, patches, and seed/verify scripts.
- Current feature handoffs and capability cards.
- Active research/audit files still referenced by current ecommerce, design, security, launch, or OpenClaw lanes.
- Secrets/runtime state protections: do not read, print, move, or delete `.env` or auth/session files as cleanup.

## Remove Or Move

- `.tmp/`, `output/`, `test-results/`, `test invoices/`, `__pycache__/`, compiled frontend `dist/`, and local `node_modules/` only when safe to regenerate.
- Raw local image/drop folders under `assets/` unless they are intentionally curated and committed as source.
- Stale legacy_source mirrors, browser render galleries, contest outputs, and prototype/research folders after the relevant production translation lands.

## 2026-05-10 Receipt

The launch cleanup removed regenerable outputs, stale mirrors/audits, old app clones, research throwaways, and tracked audience-page contest output. Raw photo drops were moved to `C:\Users\baenb\projects\Built_by_Cameron\_CLIENTS\locally-twisted-local-drops\`. `.gitignore` now blocks the known raw/drop paths from returning. `ecommerce_pause_contract.py`, `nav_ia.py`, and cleanup-owned `git diff --check` passed.

## 2026-05-11 Receipt

Follow-up cleanup removed the forbidden linked worktree/branch `ecommerce-phase-1-4-hygiene-20260510` after ancestry and worktree-state checks proved it did not hold unique unstaged/untracked work. The three deleted tracked `assets/what we do photos/` raw images were removed from repo source after `git hash-object` proved exact copies in `C:\Users\baenb\projects\Built_by_Cameron\_CLIENTS\locally-twisted-local-drops\landing-page-pics-20260510\`. Ignored forensic screenshot folders from regression research were deleted after the findings moved into tracked docs.

## 2026-05-17 Receipt

Repo history cleanup reconciled local `main` to `origin/main` after clean-clone
publishing left duplicate local commits. Local duplicates were skipped only
after mapping them to pushed equivalents. Two detached Codex worktrees were
then reviewed for feature value, proven clean and ancestor-contained, approved
by GL for deletion, removed with `git worktree remove`, and pruned from the
registry. Closeout proof showed `HEAD == origin/main == d541a0c`, no staged or
unstaged changes, no untracked files, no conflict markers, and only the main
LT worktree remaining. Handoff:
`workstreams/repo-history-and-worktree-cleanup-2026-05-17.md`.
