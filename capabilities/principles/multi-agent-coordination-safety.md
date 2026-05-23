# Multi-Agent Coordination Safety

Status: foundation
Scope: Locally Twisted agent coordination
Last verified: 2026-05-21

## Principle

LT is a protected child/client repo in a repo forest. Agents must prove the
neutral coordination workflow before using LT for parallel edits.

## Use When

- Starting an LT session from the main checkout or a linked worktree.
- Creating or using an LT worktree.
- Touching files that another agent may reasonably claim.
- Distinguishing LT client work from Built by Cameron parent/company work.

## Contract

- Read `C:\Users\baenb\agent-coordination\STARTUP-CHECKLIST.md`.
- Check `LIVE-BOARD.md` and `SESSION-REGISTRY.md`.
- Name the Six-Box target before writing.
- Treat LT client work as Box 4: child/client repo.
- Use `C:\Users\baenb\agent-worktrees\builtbycameron-lt` for LT task worktrees.
- Do not edit parent/company repo files during an LT task unless explicitly requested.
- Do not treat local acceptance, GitHub archive, staging, and live release as the same gate.
- For release/provider work, a triad is valid only when the agents own
  artifacts that can block the next step. Advice-only helper agents do not
  satisfy release control.
- If release execution enters `forensic-freeze`, do not poll, deploy,
  bootstrap, or run one more provider check until a fresh artifact-backed plan
  explicitly reopens execution.

## Evidence

- `AGENTS.md` routes LT worktrees and claims through the neutral hub.
- `workstreams/coordination-safety-pilot-2026-05-21.md` records the pilot.
- `C:\Users\baenb\agent-coordination\REPO-READINESS.md` classifies LT as the
  protected clean child/client pilot.
- `workstreams/frappe-cloud-release-prevention-action-items-2026-05-23.md`
  records the release-lock and artifact-owner action items after the staging
  release process failure.
