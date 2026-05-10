---
name: Claude reference library
level: recipe
last_verified: 2026-05-02
---

## What it does

Gives Codex agents a safe way to use the older Claude workspace as a reference library without treating it as project truth or copying it into Codex wholesale.

## When to reach for it

Use this when a Locally Twisted task may benefit from older cross-project procedures, especially Frappe/ERPNext safety work, launch checks, accessibility, code review, research workflows, or design guidance.

## Safe reference paths

- `C:\Users\baenb\.claude\skills\README.md` - older skill index.
- `C:\Users\baenb\.claude\skills\<skill-name>\SKILL.md` - specific older skill guidance.
- `C:\Users\baenb\.claude\rules\reach-paths.md` - older routing guide.
- `C:\Users\baenb\.claude\templates\`, `plans\`, `research\`, and `briefings\` - reference only when the current task calls for them.

Do not broadly read `.claude`. It contains runtime state, logs, caches, session data, screenshots, and secret-named files.

## High-value LT references

For this ERPNext/Frappe launch, the most relevant older Claude skills are:

- `frappe-payment-safety` - before Stripe, checkout, Payment Request, Sales Order, payment-success, webhook, or PDF/email payment work.
- `frappe-form-integrity` - before public form route, API submit, smoke form, or Lead-intake work.
- `frappe-fixture-discipline` - before fixture, Custom Field, Property Setter, operator-owned label, or transfer/handoff work.
- `frappe-migration-guard` - before DocType, schema, fixture, patch, or migrate-sensitive work.
- `frappe-deploy-safety` - before deploy, bench migrate, force-recreate, image/build, or production smoke work.
- `accessibility`, `webapp-testing`, `code-review`, `vibe-security-audit`, and `launch-visibility` - when those lanes are explicitly in scope.

## Rules

1. Treat Claude files as evidence and prior technique, not truth.
2. Verify claims against current LT files, git state, the running ERPNext site, and source-of-truth business materials before acting.
3. Do not read, print, move, or rewrite secrets, tokens, auth files, session IDs, runtime logs, cache data, or broad session history.
4. Do not copy Claude-era guidance wholesale into Codex. Translate only the useful behavior into project `AGENTS.md`, workstreams, queue entries, Codex capabilities, tests, or implementation.
5. Keep Claude as a parallel collaborator/reference, not a deprecated source to purge.

## Failure modes

- Copying stale Claude text into current docs creates confident-but-wrong handoffs.
- Reading broad `.claude` runtime/session data wastes attention and risks exposing private or secret material.
- Treating an old Frappe skill as current proof can miss repo-specific changes. Use it to decide what to check, then verify locally.
