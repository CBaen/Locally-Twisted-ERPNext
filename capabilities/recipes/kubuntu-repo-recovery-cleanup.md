---
title: Kubuntu Repo Recovery Cleanup
layer: recipe
status: verified
last_verified: 2026-06-15
scope: locally-twisted source repo after Windows-to-Kubuntu or similar host moves
supports:
  - source stabilization
  - git cleanup
  - multi-agent handoff
graduation:
  level: verifier_backed
  evidence:
    - workstreams/kubuntu-recovery-closeout-2026-06-15.md
---

# Kubuntu Repo Recovery Cleanup

Use this when the LT checkout has moved machines or operating systems and the
repo needs reconciliation before normal work continues.

## When To Use

- The host moved from Windows to Kubuntu or another Linux environment.
- Git status shows many changed files after a machine move.
- A branch, stash, or worktree collision exists around a previous agent's work.
- A future agent needs to decide what is real source change versus migration
  noise.

## Operating Rules

- Keep the task in the LT Git root unless GL explicitly widens scope.
- Do not broad-stage. Stage exact files only after classification.
- Treat push to GitHub as source archive, not staging/live release.
- Do not touch Frappe Cloud, DNS, Stripe, provider dashboards, Search Console,
  production data, or customer communications from this recipe.

## Steps

1. Prove the source position:
   `git status --short --branch --untracked-files=all`,
   `git log --oneline --decorate -8`, and `git remote -v`.
2. Inspect push side effects before any push, especially `.github/workflows/`.
3. Preserve collision work before fast-forwarding or rebasing. Prefer a named
   stash or exact-scope commit over destructive reset.
4. Classify real content separately from line-ending churn with
   `git diff --ignore-cr-at-eol`.
5. Commit real behavior/docs changes in small source commits with clear
   subjects.
6. Restore CRLF/LF-only tracked-file noise from HEAD after confirming it has no
   content diff.
7. Remove unused untracked wrappers or generated files only when verified
   unused.
8. Prune stale worktree metadata only after checking `git worktree list`.
9. Run fast local proof that matches the touched surfaces.
10. Write/update the feature handoff, queue, decision log, lessons learned, and
    capability index before source archive.

## 2026-06-15 LT Recovery Receipts

Preserved commits:

- `7ad632a Preserve Kubuntu verifier and reset email guard`
- `8b9d6f3 Classify remaining Kubuntu WIP`
- `0ba474d Preserve Kubuntu browser and reset copy fixes`
- `23fe30a Close out Kubuntu recovery cleanup`

Final fast checks:

- `npm run test:verifier-cli`
- `npm run test:nav-ia`
- `node -e "JSON.parse(require('fs').readFileSync('package.json','utf8'))"`
- `npm run test:password-reset-template`

The password-reset verifier was read/verify-only. No email was sent.
