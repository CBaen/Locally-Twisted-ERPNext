# Kubuntu Recovery Closeout - 2026-06-15 MDT

## Current State

The LT repo has been reconciled after the Windows-to-Kubuntu move.

- Branch: `main`
- Upstream relationship: local `main` is ahead of `origin/main` by 3 commits.
- Working tree: clean.
- Staged changes: none.
- Stale Windows worktree registry: pruned.
- Branch refs: still present after prune.
- Stash retained: `lt kubuntu reset-helper collision preserve 2026-06-15`

## Local Commits

- `b009760 Preserve Kubuntu verifier and reset email guard`
- `a04c55d Classify remaining Kubuntu WIP`
- `cee139b Preserve Kubuntu browser and reset copy fixes`

These commits are local only at this closeout. No push was performed.

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

- No push.
- No staging/live/provider/DNS/payment action.
- No email send.
- No destructive Git reset/clean.
- No database mutation beyond the read-only password reset template verifier.

## Next Practical Step

Review and push the 3 local recovery commits when ready to archive this Kubuntu
stabilization work to GitHub. This is still source archive, not staging or live
release.
