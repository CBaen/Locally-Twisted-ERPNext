# 2026-07-02 LT Branch Custody: Document First, No Merge/Prune Without Approval

## Decision

Do not merge, prune, delete, or force-push the discovered LT side branches as a
bulk cleanup action. Document the branch inventory, preserve the custody facts,
and require a branch-specific review plus explicit approval before deletion or
merge.

## Reason

Current LT `main` is clean and tracking `origin/main`, but every local side
branch checked on 2026-07-02 is unmerged relative to current `main`. Some are
old proof/release packet branches, some are local-only, some have active linked
worktrees, and one staging-freeze branch is ahead of its remote by two local
commits. Bulk deletion would risk losing evidence or unreviewed work; bulk
merge would risk reintroducing stale May/June assumptions into the July source
of truth.

## Source Packet

`workstreams/repo-branch-custody-2026-07-02.md`

## Current High-Risk Facts

- `codex/lt-product-setup-brand-authority-20260630`,
  `codex/lt-meta-pixel-source-support-20260628`, and
  `codex/lt-meta-bouquet-ad-groundwork-20260628` have active linked worktrees.
- `codex/lt-staging-release-candidate-freeze` is ahead of its remote by two
  local commits.
- Five local-only branches have no upstream tracking branch.
- One detached worktree under `/home/guidingl/agent-worktrees/builtbycameron-lt/`
  has a dirty `AGENTS.md`.

## Boundaries

- This decision does not approve keeping branches forever.
- This decision does not approve merging any side branch into `main`.
- This decision does not approve deleting any branch or worktree.
- This decision does not prove any branch's runtime, staging, live, provider,
  catalog, checkout, payment, or advertising readiness.

## Required Next Step

When GL approves branch cleanup, use
`capabilities/recipes/launch-repo-cleanup-and-evidence-retention.md` and start
from `workstreams/repo-branch-custody-2026-07-02.md`.
