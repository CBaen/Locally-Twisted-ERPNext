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

- Read `/home/guidingl/agent-coordination/STARTUP-CHECKLIST.md`.
- Check `LIVE-BOARD.md` and `SESSION-REGISTRY.md`.
- Name the Six-Box target before writing.
- Treat LT client work as Box 4: child/client repo.
- Use `/home/guidingl/agent-worktrees/builtbycameron-lt` for LT task worktrees.
- Do not edit parent/company repo files during an LT task unless explicitly requested.
- Do not treat local acceptance, GitHub archive, staging, and live release as the same gate.

## Evidence

- `AGENTS.md` routes LT worktrees and claims through the neutral hub.
- `workstreams/coordination-safety-pilot-2026-05-21.md` records the pilot.
- `/home/guidingl/agent-coordination/REPO-READINESS.md` classifies LT as the
  protected clean child/client pilot.
