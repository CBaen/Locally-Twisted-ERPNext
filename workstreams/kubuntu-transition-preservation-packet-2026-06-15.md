# Kubuntu Transition Preservation Packet - 2026-06-15 MDT

## Scope

This packet preserves the Git and worktree reality before cleanup. It is a
read-only decision record for the next cleanup slice.

No `git pull`, `git worktree prune`, branch deletion, file deletion, reset,
checkout, staging, commit, push, database mutation, or provider action was done
for this packet.

## Current Git State

- Repo root:
  `/home/guidingl/projects/Built_by_Cameron/_CLIENTS/locally-twisted`
- Current branch: `main`
- Local HEAD: `29b64b2 Fix live login layout and cookie notice`
- Upstream state: `main` is behind `origin/main` by 2 commits.
- Dirty surface: 162 changed/untracked paths.
  - 152 modified tracked paths.
  - 10 untracked paths.
- `git fsck --no-dangling` passed in the transition health pass.

Pending upstream commits:

| Commit | Meaning | Files touched |
|---|---|---|
| `85c88b1` | Add fail-loud Locally Twisted reset helper | `marketing_access_reset.py`, `marketing_vendor_access.py`, `package.json`, `scripts/setup/send_marketing_access_reset.py`, `scripts/setup/sync_marketing_vendor_access.py` |
| `228a721` | Guard live account reset API calls | `marketing_access_reset.py`, `marketing_vendor_access.py` |

## Pull Collision Map

Four untracked local files already exist on `origin/main`. A blind pull would
force Git to reconcile paths that are currently untracked locally.

| Path | Working tree vs `origin/main` | Preservation decision |
|---|---|---|
| `apps/locally_twisted/locally_twisted/marketing_access_reset.py` | Differs from upstream. Local copy changes the reset subject/header/body to say "Locally Twisted website password" and adds copy clarifying that only the website account is reset. | Preserve and merge deliberately before pull. This is the only colliding untracked file with real local content drift. |
| `apps/locally_twisted/locally_twisted/marketing_vendor_access.py` | Byte-identical to `origin/main`. | Safe to adopt upstream after preserving evidence. |
| `scripts/setup/send_marketing_access_reset.py` | Byte-identical to `origin/main`. | Safe to adopt upstream after preserving evidence. |
| `scripts/setup/sync_marketing_vendor_access.py` | Byte-identical to `origin/main`. | Safe to adopt upstream after preserving evidence. |

Additional untracked local-only paths:

- `apps/locally_twisted/locally_twisted/password_reset_email.py`
- `apps/locally_twisted/locally_twisted/patches/configure_password_reset_email.py`
- `scripts/setup/sync_password_reset_template.py`
- `scripts/verify/browser_runtime.py`
- `scripts/verify/run_playwright.js`
- `workstreams/kubuntu-transition-health-2026-06-15.md`

The first three look related to password/reset email work and should be reviewed
with the upstream reset-helper commits before any cleanup. The verifier and
workstream files are Kubuntu transition artifacts from this pass.

## Modified WIP Buckets

Tracked modified files by broad bucket:

| Bucket | Count |
|---|---:|
| App code/templates/CSS/doctype/seed/verify under `apps/` | 23 |
| Setup scripts | 3 |
| Verification scripts | 12 |
| Audit artifacts | 64 |
| `_resources` artifacts | 4 |
| Workstream artifacts | 41 |
| Capability/docs files | 2 |
| Other repo/config files | 3 |

This is mixed feature work plus generated evidence. It should be treated as
preservation-first, not as a single coherent change set.

## Stale Worktree Registry

`git worktree prune --dry-run --verbose` reports 14 stale worktree registrations
whose `gitdir` files point to old Windows locations under
`C:/Users/baenb/agent-worktrees/builtbycameron-lt/...`.

Dry-run prunable entries:

- `grad`
- `codex-20260524-lt-clean-recovery-1f4520b__clean-recovery-1f4520b`
- `release-candidate`
- `i3scope`
- `codex-20260529-lt-checkout-penny-match__checkout-penny-match`
- `release-packet`
- `pv`
- `codex-20260529-lt-shared-inquiry-gate__shared-inquiry-gate`
- `pfg`
- `codex-20260528-lt-live-seo-indexing-patch__live-indexing-release`
- `i4scope`
- `i5scope`
- `codex-20260529-lt-erpnext-catalog-cleanup__legacy-catalog-cleanup`
- `live-shop-discovery-gate`

Do not run real prune until branch preservation is complete.

## Branch Preservation Map

Remote-backed branches with no visible ahead/behind drift:

- `codex/checkout-penny-match`
- `codex/item3-product-diversity-scope`
- `codex/item4-internal-processing-scope`
- `codex/item5-staging-release-packet-scope`
- `codex/lt-graduation-support-packet`
- `codex/lt-live-indexing-release`
- `codex/lt-live-shop-discovery-gate`
- `codex/lt-staging-release-controller-packet`

Branches needing care before any prune/delete:

| Branch | Risk |
|---|---|
| `codex/lt-staging-release-candidate-freeze` | Tracks a remote but is 2 commits ahead locally: `8ddc66c Document local staging commerce mode divergence`, `9a5f7f1 Record LT staging issue checkpoint`. |
| `codex/clean-recovery-1f4520b` | No upstream; 1 commit not in `origin/main`: `f71d842 Fix LT install and portal migration hooks`. |
| `codex/erpnext-catalog-cleanup` | No upstream; 2 commits not in `origin/main`: `eaff81c fix: restore ERPNext catalog audit artifacts`, `740db29 chore: remove retired platform references from LT repo`. |
| `codex/lt-pause-verifier-selective-indexing` | No upstream; 1 commit not in `origin/main`: `4742d83 Align ecommerce pause verifier with indexing gate`. |
| `codex/portfolio-proof-reel-gate` | No upstream; 1 commit not in `origin/main`: `1b15f88 Promote portfolio proof reel verifier gate`. |
| `codex/shared-inquiry-gate` | No upstream; 1 commit not in `origin/main`: `c325333 Promote shared inquiry form gate definition`. |

## Stop Gates

Do not do these until the relevant packet step is complete:

- Do not run `git pull` until the upstream-colliding untracked files are either
  preserved and removed/adopted, or deliberately merged.
- Do not run `git worktree prune` until the six at-risk branches above are
  preserved or explicitly retired.
- Do not delete untracked password/reset files until their relationship to the
  upstream reset-helper commits is understood.
- Do not stage or commit the dirty tree as a whole. It mixes runtime app edits,
  setup scripts, verifier changes, generated audits, resources, and workstreams.

## Recommended Next Mutation Sequence

1. Preserve the colliding reset-helper files:
   - Keep the local copy diff for `marketing_access_reset.py`.
   - Confirm the three byte-identical files can be adopted from upstream.
   - Review local-only password reset files beside upstream commits `85c88b1`
     and `228a721`.
2. Make a narrow Kubuntu/tooling preservation slice:
   - `package.json` Playwright script repair.
   - Python verifier `--help` import repairs.
   - `scripts/verify/browser_runtime.py`.
   - transition workstream artifacts.
   This should stay separate from password reset, catalog, ecommerce, and
   generated audit WIP.
3. After collision files are protected, update `main` from `origin/main`.
4. Preserve or retire local-only branch commits with explicit evidence.
5. Only then run `git worktree prune` to remove stale Windows worktree registry
   entries.
6. Reconcile docs that still encode Windows paths and stale catalog counts.

## Related Artifact

See `workstreams/kubuntu-transition-health-2026-06-15.md` for the broader
post-migration health pass, runtime counts, verifier repairs, and current
Kubuntu operating notes.

## Continuation Update - 2026-06-15 19:50 MDT

After this packet was created, the reset/package collision group was preserved
with a path-limited stash:

`stash@{Mon Jun 15 19:43:52 2026}: On main: lt kubuntu reset-helper collision preserve 2026-06-15`

Then local `main` was fast-forwarded from `29b64b2` to `228a721`, matching
`origin/main` with no merge commit and no push.

Restored from the stash after the fast-forward:

- `package.json` local Kubuntu-safe Playwright command changes and local
  password reset template scripts.
- `apps/locally_twisted/locally_twisted/marketing_access_reset.py` local copy
  clarification that the link resets only the Locally Twisted website account.
- `apps/locally_twisted/locally_twisted/password_reset_email.py`
- `apps/locally_twisted/locally_twisted/patches/configure_password_reset_email.py`
- `scripts/setup/sync_password_reset_template.py`

Left as upstream-tracked files because the preserved local copies were
byte-identical to `origin/main`:

- `apps/locally_twisted/locally_twisted/marketing_vendor_access.py`
- `scripts/setup/send_marketing_access_reset.py`
- `scripts/setup/sync_marketing_vendor_access.py`

Current post-fast-forward state:

- `origin/main...HEAD`: `0 0`
- `HEAD`: `228a721 Guard live account reset API calls`
- Dirty surface: 153 modified tracked paths and 7 untracked paths.
- The stash remains in place as a backup. Do not drop it until the reset-helper
  and Kubuntu tooling slices are either committed or deliberately retired.

## Local Preservation Commit And Prune - 2026-06-15 20:00 MDT

Created local commit:

- `Preserve Kubuntu verifier and reset email guard`

This commit preserves:

- Kubuntu-safe Node Playwright npm scripts.
- Python browser verifier `--help` safety and shared browser launcher.
- Branded password-reset email template helper, migration patch, and generic
  reset-email guard.
- Reset-helper copy clarification that the link resets only the Locally Twisted
  website account.
- This transition health packet and the preservation packet.

The commit is local only:

- `origin/main...HEAD`: `0 1`
- No push was performed.
- No staging/live/provider/database/payment/DNS action was performed.

After the branch preservation map above was written and verified, the stale
Windows worktree registry was pruned with `git worktree prune --verbose`.

Post-prune verification:

- `git worktree list --porcelain` shows only the main Kubuntu worktree.
- `git branch -vv` still lists all previously mapped branches.
- The six at-risk local branch heads still resolve:
  `f71d842`, `eaff81c`, `4742d83`, `8ddc66c`, `1b15f88`, and `c325333`.
- `git fsck --no-dangling` passed.
