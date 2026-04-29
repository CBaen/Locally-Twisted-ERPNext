# Contest Index — Customizable Event Decor Design Tool

**Status:** Phase 0 — Brief drafted, awaiting GL approval before dispatch.

## Phase tracker

| Phase | Status | Notes |
|---|---|---|
| 0. Pre-flight | IN PROGRESS | Brief written; awaiting GL approval |
| 1. Round 1 (blind) | — | 4 contestants, parallel persistent agents |
| 1a. Round 1 reflective loops | — | Proxy ↔ each contestant, 2-3 perspective shifts each |
| 2. Field summary | — | Orchestrator solo |
| 3. Round 2 (mutual visibility) | — | SendMessage to contestants |
| 3a. Round 2 reflective loops | — | Proxy ↔ each contestant, 2-3 deeper perspective shifts |
| 4. Mutual peer scoring | — | 4 dimensions × 3 peers each |
| 5. Aggregation | — | Orchestrator solo |
| 6. Dissent moment | — | Continue / Step Away / Wildcard Pivot per contestant |
| 7. Tightening pass (ALL 4) | — | Adapted: all 4 get tightening, not just top-K, since GL wants all surfaced |
| 8. Render gallery | — | Playwright screenshots all contestants × 6 screens × 2 viewports |
| 9. Surface to GL | — | All 4 with ratings + reasons; GL synthesizes |
| 10. (Skipped) Orchestrator synthesis | N/A | GL synthesizes downstream by picking pieces |

## Contestant directories

- `contestant-1/`
- `contestant-2/`
- `contestant-3/`
- `contestant-4/`

## Key files

| File | Purpose |
|---|---|
| `BRIEF.md` | The source of truth all contestants read |
| `INDEX.md` | This file — phase + status tracker |
| `research-brief.md` | The seed brief that initiated the contest (precursor to BRIEF.md) |
| `FIELD-AT-ROUND-1.md` | (To be written) Orchestrator's round-1 cheat sheet for round-2 contestants |
| `SCORING-RESULTS.md` | (To be written) Mutual peer scoring matrix |
| `DISSENT-RESULTS.md` | (To be written) Per-contestant Continue/Step Away/Wildcard choices |
| `PROXY-REVIEW-ROUND-2.md` | (To be written) Proxy tightening notes per contestant |
| `_render/` | (To be populated) Playwright screenshots — gallery for GL |
| `FINAL-SURFACE.md` | (To be written) The single doc GL reads to evaluate all 4 |

## Contest configuration (locked)

| Setting | Value |
|---|---|
| Mode | Standard (Proxy + reflective loops + dissent + tightening) |
| Contestants | N=4, persistent (one Agent spawn per contestant, advanced via SendMessage) |
| Proxy | Persistent, spawned once at contest start |
| Output | All 4 surfaced with ratings + reasons (not top-2, not synthesis) |
| Synthesis | GL does it downstream |
| Render | Static HTML mockups, double-click-to-open + Playwright screenshot gallery |
| Frappe-recreatable | Hard rule, audited per contestant |
| Research | Mandatory, citations required, Proxy probes for training-data-only claims |
| Cost ceiling | ~25-35 in Opus tokens (acceptable per GL 2026-04-29) |

## Dispatch readiness checklist

- [x] Brief written
- [x] Contestant directories scaffolded (placeholder READMEs)
- [x] Index.md tracking phases
- [ ] Persistent Proxy spawned with brief context
- [ ] GL approval on brief
- [ ] All 4 contestants spawned in parallel for Round 1

## Operational notes for the orchestrator

- The 4 contestants are persistent agents. Spawn ONCE per contestant; advance via SendMessage.
- The Proxy is persistent. Spawn ONCE; advance via SendMessage with each loop / tightening prompt.
- Round 1 is BLIND — contestants must NOT read each other's directories. Their tool list excludes peer dirs.
- Round 2 contestants read `FIELD-AT-ROUND-1.md` (the orchestrator's cheat sheet) instead of deep-Reading every peer.
- All file writes auto-commit via the post-write hook. Do NOT manually `git commit` during the contest.
- The Frappe-recreatable audit is a tightening-pass concern, not a Round 1 blocker. If a contestant uses React in Round 1, the Proxy flags it; they fix in Round 2 or Tightening.

---

*Index seeded 2026-04-29 by the orchestrator running the contest skill.*
