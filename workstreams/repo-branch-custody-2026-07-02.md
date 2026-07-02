# LT Branch Custody Review - 2026-07-02

Purpose: preserve the branch/worktree facts found during accessibility-mode
cleanup so future agents do not rediscover or accidentally flatten them.

Source state checked from:
`/home/guidingl/projects/Built_by_Cameron/_CLIENTS/locally-twisted`

Commands used:

```bash
git branch -vv --sort=refname
git for-each-ref --format='%(refname:short)|%(upstream:short)|%(committerdate:iso8601)|%(subject)' refs/heads refs/remotes/origin
git worktree list --porcelain
git branch --merged main --format='%(refname:short)'
git branch --no-merged main --format='%(refname:short)'
for b in $(git for-each-ref --format='%(refname:short)' refs/heads | grep -v '^main$'); do
  git rev-list --count main..$b
  git rev-list --count $b..main
  git log --oneline --max-count=5 main..$b
  git diff --name-status main...$b
done
```

## Current decision

Do not merge, prune, delete, or force-push any LT side branch from this packet
without a fresh branch-specific review and explicit approval. The branches are
not clean bookmarks: every side branch is unmerged relative to current `main`,
and several branches are old enough that their docs/code may conflict with the
July 2026 source-of-truth state.

GitHub history is the archive, but branch deletion still needs proof that the
branch's unique value is already present in current `main`, another approved
branch, a durable handoff, or an external backup. Follow
`capabilities/recipes/launch-repo-cleanup-and-evidence-retention.md` before
any deletion.

## High-attention branches

| Branch | State | Why it matters | Next action |
|---|---|---|---|
| `codex/lt-product-setup-brand-authority-20260630` | local + remote, active linked worktree, `15` commits ahead of current `main`, `14` behind | Product Setup Desk/catalog authority work: blueprint runtime fields, readiness dashboard, product setup APIs/verifiers, catalog authority docs. | Review against current P0 Product Setup authority lane before merge. Do not assume it is superseded by the July 2 emergency live repair. |
| `codex/lt-meta-pixel-source-support-20260628` | local + remote, active linked worktree, `1` commit ahead, `21` behind | Consent-gated Meta Pixel source support. | Keep separate from live ad/spend approval. Review only after website/ecommerce stabilization path is clear. |
| `codex/lt-meta-bouquet-ad-groundwork-20260628` | local + remote, active linked worktree, `2` commits ahead, `21` behind | Builds on Meta Pixel support and adds missionary bouquet ad landing-page groundwork, ad verifiers, SEO/contact/FAQ touches. | Review as source prep only; not campaign launch approval. |
| `codex/lt-staging-release-candidate-freeze` | local + remote, local branch is `2` commits ahead of remote, `38` ahead of current `main`, `75` behind | Old staging release/no-go/freeze chain. Local-only commits are `Document local staging commerce mode divergence` and `Record LT staging issue checkpoint`. | Preserve until a release-controller review decides whether any no-go/freeze evidence still matters. Do not push or delete casually. |

## Local-only branches

These branches have no upstream tracking branch. That does not mean they are
safe to delete; it only means they are local custody risks.

| Branch | Unique commits from `main` | Apparent contents | Next action |
|---|---:|---|---|
| `codex/clean-recovery-1f4520b` | `1` | LT install and portal migration hook fixes. | Compare against current install/portal code before prune. |
| `codex/erpnext-catalog-cleanup` | `2` | Large cleanup/restoration branch including catalog artifact path movement and many docs. | Treat as high-risk/stale; review only if a catalog-artifact question reopens. |
| `codex/lt-pause-verifier-selective-indexing` | `1` | Ecommerce pause verifier alignment with indexing gate. | Compare with current pause verifier before prune. |
| `codex/portfolio-proof-reel-gate` | `1` | Portfolio proof reel capability/verifier manifest update. | Compare with current capability/verifier state before prune. |
| `codex/shared-inquiry-gate` | `1` | Shared inquiry capability/verifier manifest update. | Compare with current capability/verifier state before prune. |

## Older checkout / release audit branches

These are all unmerged relative to current `main` and mostly date from
2026-05-29. They appear to be proof packets and staged checkout/release audit
work rather than current implementation direction.

| Branch | Unique commits from `main` | Apparent contents |
|---|---:|---|
| `codex/checkout-penny-match` | `3` | Checkout preview penny rounding, fulfillment contract, proof docs. |
| `codex/item3-product-diversity-scope` | `7` | Checkout product diversity proof, builds on penny branch. |
| `codex/item4-internal-processing-scope` | `12` | Internal processing proof, witness gate, staging shop audit list. |
| `codex/item5-staging-release-packet-scope` | `17` | Staging release no-go packet, source identity proof, recovery proof. |
| `codex/lt-staging-release-controller-packet` | `1` | Staging release controller packet docs. |
| `codex/lt-live-shop-discovery-gate` | `31` | Shop discovery vs checkout pause split, release status report, ecommerce pause verifier, nav/footer/shop/checkout touches. |
| `codex/lt-graduation-support-packet` | `4` | Fail-loud/shared inquiry/portfolio proof capability graduation packet. |
| `codex/lt-live-indexing-release` | `4` | Live indexing release packet and proof JSON/docs. |

## Detached linked worktree

Path:
`/home/guidingl/agent-worktrees/builtbycameron-lt/codex-20260629-lt-missionary-release-main__publish`

State as checked:

```text
HEAD detached at f231c90 Document Meta ad foundation readiness
dirty file: AGENTS.md
```

The detached HEAD commit is contained by current `main` and by
`codex/lt-product-setup-brand-authority-20260630`, but the worktree has a dirty
`AGENTS.md`. Do not remove this worktree until the dirty file is inspected and
either preserved, discarded with approval, or proven to be a no-op.

## Safe cleanup procedure for the next agent

1. Stay on LT `main` in the main checkout.
2. Re-run the branch/worktree inventory commands above.
3. For each candidate branch, compare `main...branch` and check whether its
   value is already present in current source/docs/verifiers.
4. For linked worktrees, check staged, unstaged, and untracked files in the
   worktree itself.
5. For detached worktrees, prove both commit containment and dirty-file custody.
6. Bring a short delete/keep list to GL for explicit approval before removing
   branches or worktrees.
7. After approved cleanup, update this packet, `CODING-HANDOFF.md`,
   `locally-twisted-queue.md`, `decisions/INDEX.md`, and `lessons-learned.md`.

## Verification performed for this packet

- LT capability context gate passed with:
  - `capabilities/INDEX.md`
  - `capabilities/recipes/launch-repo-cleanup-and-evidence-retention.md`
  - `capabilities/recipes/fail-loud-operating-law.md`
- No branch was merged, deleted, pushed, rebased, or checked out.
- No runtime, provider, ERPNext, Frappe Cloud, Stripe, Meta, DNS, or customer
  data state was changed.
