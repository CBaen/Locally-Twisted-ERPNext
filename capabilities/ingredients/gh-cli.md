---
id: gh-cli
name: GitHub CLI
schema_version: 2.1
profile: foundation
level: ingredient
maturity: candidate
scope: local or project environments with GitHub CLI installed
currently_true: unknown
last_verified: unknown
tags:
  - github
  - cli
  - repository
  - release
---

## What it does

Provides the `gh` command for GitHub repository, pull request, issue, release,
and workflow operations.

## When to reach for it

- A workflow needs to create or inspect GitHub repositories, PRs, issues, or
  releases.
- A deploy path uses GitHub as the source repository for CI.
- A package is ready to publish after identity and repository target are
  confirmed.

## How to use it

Check availability before relying on it:

```powershell
gh --version
gh auth status
```

Do not create repositories, push code, or change authentication identity without
the user's explicit target account and repo decision.

## What it depends on

GitHub CLI must be installed and authenticated for the intended account.

## Failure modes

- The active authenticated account may be the wrong identity for the package.
- GitHub CLI can be installed but unauthenticated.
- Some environments have a GitHub app connector but no local `gh` executable.
