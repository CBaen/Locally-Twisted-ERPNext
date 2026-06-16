# Kubuntu Recovery Closeout - 2026-06-15 MDT

## Current State

The LT repo has been reconciled after the Windows-to-Kubuntu move.

- Branch: `main`
- Upstream relationship before the final documentation commit: local `main` is
  ahead of `origin/main` by 4 commits.
- Working tree before the final documentation commit: clean.
- Staged changes: none.
- Stale Windows worktree registry: pruned.
- Branch refs: still present after prune.
- Stash retained: `lt kubuntu reset-helper collision preserve 2026-06-15`

## Local Commits

- `7ad632a Preserve Kubuntu verifier and reset email guard`
- `8b9d6f3 Classify remaining Kubuntu WIP`
- `0ba474d Preserve Kubuntu browser and reset copy fixes`
- `23fe30a Close out Kubuntu recovery cleanup`

These commits were local only when the recovery closeout was written. The final
documentation/source-archive commit follows this closeout in Git history.

## What Was Reconciled

- Fast-forwarded local `main` to `origin/main`.
- Preserved Kubuntu-safe Playwright commands.
- Preserved password-reset email guard/template/source verification.
- Preserved Linux browser discovery in `playwright.config.js`.
- Preserved clearer forgot-password copy on `/login`.
- Removed CRLF/LF-only working-tree noise from 139 tracked files.
- Removed the unused untracked `scripts/verify/run_playwright.js` wrapper.

## Verification

Fast checks passed:

- `npm run test:verifier-cli`
- `npm run test:nav-ia`
- `node -e "JSON.parse(require('fs').readFileSync('package.json','utf8'))"`
- `npm run test:password-reset-template`

The password-reset template check was verify-only. It confirmed:

- configured template: `Locally Twisted Password Reset`
- subject: `Reset your Locally Twisted website password`
- account email shown in rendered copy
- generic fallback blocked

## Not Done

- No successful push. A push attempt after rebase failed because the Kubuntu
  shell has no working GitHub auth: HTTPS rejected credentials, `gh` is logged
  out, SSH is denied, and no `GH_TOKEN`/`GITHUB_TOKEN` is present.
- No staging/live/provider/DNS/payment action.
- No email send.
- No destructive Git reset/clean.
- No database mutation beyond the read-only password reset template verifier.

## Next Practical Step

Authenticate GitHub for this Kubuntu shell, then push local `main` without
force. This is still source archive, not staging or live release.
