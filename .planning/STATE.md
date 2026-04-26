---
gsd_state_version: 1.0
milestone: v15.105.0
milestone_name: milestone
status: in_progress
stopped_at: Phase 2 in flight; crm.lead translated, 5 model translations + 1 settings DocType + 2 service helpers remaining
last_updated: "2026-04-26T02:00:00.000Z"
last_activity: 2026-04-26 -- LT setup wizard finalized; crm.lead Custom Fields translated; multi-select + conditional visibility revision applied; nginx Origin pass-through patched
progress:
  total_phases: 10
  completed_phases: 0
  deferred_phases: 1
  total_plans: 0
  completed_plans: 0
  percent: 0
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-04-25)

**Core value:** Jeff's next experience with this system makes him feel relieved, not nervous — the migration lands as a visible upgrade
**Current focus:** Phase 2 — Backend Models (Phase 1 deferred)

## Current Position

Phase: 2 of 10 (Backend Models) — Phase 1 deferred per 2026-04-25 evening pivot
Plan: translation execution mode — no formal PLAN files (per 2026-04-26 GSD execution-mode decision)
Status: in flight. crm.lead Custom Fields done (incl. multi-select + conditional visibility revision). 5 model translations + 1 settings DocType + 2 service helpers remaining for Phase 2.
Last activity: 2026-04-26 -- LT setup wizard finalized (Cameron + Jeff users, Address, Company contacts populated); crm.lead translated as first Custom Field set; nginx Origin pass-through patched (socket.io fix #2)

Progress: [█░░░░░░░░░] ~10% (1 of 9 custom models translated; setup wizard done; 2 cross-cutting fixes shipped)

## Performance Metrics

**Velocity:**

- Total plans completed: 0
- Average duration: —
- Total execution time: 0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| - | - | - | - |

**Recent Trend:**

- Last 5 plans: —
- Trend: —

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table and in `built-by-cameron-decisions.md` (full reasoned log).
Recent decisions affecting current work:

- 2026-04-26: GSD execution mode for translation = direct script-write-and-run (no formal PLAN files); heavier process reserved for architectural choices
- 2026-04-26: `twilio_service.py` is NOT a new DocType — it's an abstract service class; implement as Python helper / Server Script
- 2026-04-26: All clients default to ERPNext native payroll (HRMS); Gusto removed from project scope (GL directive)
- 2026-04-25 evening: Skip Phase 1 entirely; use existing off-Odoo expedition inventory as baseline
- 2026-04-25 evening: Build everything locally first; defer bench/Frappe-Cloud/transferable concerns until something is real to ship
- 2026-04-25 evening: Don't modify anything in `locally-twisted-odoo/` (read-only reference)
- 2026-04-25: ERPNext v15.105.0 pinned (latest stable v15 patch)
- 2026-04-25: Frappe Cloud Sites plan ($5/mo) chosen for production hosting; transfer is self-service via dashboard Actions tab

### Pending Todos

Phase 2 translation queue (in priority order — see `built-by-cameron-queue.md` for full context):

- Translate `res_partner.py` (7 fields; ERPNext Customer + Contact split)
- Translate `product_template.py` (CRUD override → Server Script on Item)
- Translate `project_task.py` (14 Custom Fields on Task)
- Translate `calendar_event.py` (1 computed field)
- Translate `hr_expense.py` (Custom Fields on Expense Claim)
- Translate `res_config_settings.py` → new "LT Settings" Single DocType for Twilio + Gusto credentials
- Implement `twilio_service` and `gusto_service` (Python helpers, deferred to Phase 3 when automations call them)

Cross-cutting:

- Decide on Jeff Kimber placeholder user (`locallytwisted@yahoo.com`) — delete, rename, or leave (P1)
- Persist nginx Origin patch via docker-compose override (P2)

### Blockers/Concerns

None blocking. Awaiting GL visual verification of crm.lead Custom Fields revision (multi-select + conditional sub-sections) before formally closing Phase 2 first-translation milestone.

## Deferred Items

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Inventory | Phase 1 (INV-01, INV-02) | DEFERRED | 2026-04-25 evening |
| Production read | INV-02 specifically — slots before Phase 10 cutover | DEFERRED | 2026-04-25 evening |
| Packaging | Custom Frappe app for LT (containerization for transfer) | DEFERRED until critical mass of customizations | 2026-04-25 evening |
| Production hosting | Frappe Cloud signup + DEPLOY-01 | DEFERRED until local rebuild has critical paths working | 2026-04-25 evening |
| Other BBC concerns | Lawyer template, future clients, BBC own ops project | OUT OF SCOPE for this GSD project | 2026-04-25 |
| jakenfriends migration | Archived (friend not interested; expedition flagged JNF as poor ERPNext fit anyway) | ARCHIVED | 2026-04-25 |

## Session Continuity

Last session: 2026-04-26
Stopped at: crm.lead translated (Custom Fields + multi-select revision); LT setup wizard finalized; nginx Origin pass-through patched. Awaiting GL visual verification.
Resume file: HANDOFF.md (project root) — load-bearing for next instance
Next concrete step: Continue Phase 2 — pick the next model to translate (recommend `project_task.py` since its 14 fields are tightly coupled to the crm.lead → task automation chain, OR `res_partner.py` since it's the partner ↔ customer bridge). Use the same script pattern: read source → write `scripts/translate/translate_<model>.py` → run → verify.
