---
gsd_state_version: 1.0
milestone: v0.1
milestone_name: customer-site-storefront
status: in_progress
stopped_at: Frame reset complete; Phase 1 plan slice draft pending
last_updated: "2026-04-26T03:45:00.000Z"
last_activity: 2026-04-26 — project reframed from Odoo migration to first-build; PROJECT.md and ROADMAP.md replaced with new 6-phase workflow-centric structure; Reference Disposition added to CLAUDE.md; policy + style + tax resources copied into _resources/ and scrubbed of platform refs
progress:
  total_phases: 6
  completed_phases: 0
  deferred_phases: 0
  total_plans: 0
  completed_plans: 0
  percent: 0
---

# Project State

## Project Reference

See: `.planning/PROJECT.md` (frame reset 2026-04-26)

**Core value:** Jeff's first interaction with the new system makes him feel equipped — like he finally has the tools he should have had years ago. End result must look obvious, professional, trustworthy.

**Current focus:** Phase 1 — Customer site + storefront (the proof point). If ERPNext can't deliver this, GL pivots before building backend.

## Current Position

Phase: 1 of 6 (Customer site + storefront)
Plan: `.planning/phases/01-customer-site-and-storefront/PLAN.md` (slice draft pending)
Status: pre-execution. Decision gates flagged in PLAN.md awaiting GL input. Brand foundation, header/footer, landing page, service page, contact, accessibility, refund, FAQ, products + product detail + cart sliced into independent deliverables.
Last activity: 2026-04-26 — frame reset; resources brought into project; PROJECT.md and ROADMAP.md promoted to v2 framing.

Progress: [░░░░░░░░░░] 0% (Phase 1 not yet started; brand resources pre-positioned in `_resources/`)

## Performance Metrics

**Velocity:**

- Total plans completed: 0
- Average duration: —
- Total execution time: 0 hours

## Accumulated Context

### Decisions

Recent decisions (full reasoned log in `locally-twisted-decisions.md`):

- 2026-04-26: Project reframed from "Odoo → ERPNext migration" to "First professional business platform for LT, built on ERPNext" (GL directive)
- 2026-04-26: Customer-facing site + storefront is Phase 1 — the proof point (GL directive)
- 2026-04-26: Drop standalone About page and standalone Services index — info distributes (GL directive)
- 2026-04-26: All clients default to ERPNext native HRMS payroll — agency-wide standard (GL directive)
- 2026-04-26: All policy/brand resources live in `_resources/` and are scrubbed of platform-specific references
- 2026-04-25: ERPNext v15.105.0 pinned (latest stable v15 patch)
- 2026-04-25: Frappe Cloud Sites plan ($5/mo) chosen for production hosting; transfer is self-service via dashboard

### Pending Todos

Phase 1 decision gates (need GL input):

- Header navigation structure — see `.planning/decisions/header-navigation.md`
- Accessibility statement nuance — see `.planning/decisions/accessibility-statement.md`
- Blog presence in Phase 1 (yes / framework only / defer)
- Real photography sourcing
- Customer-inquiry email destination
- Pricing calculator: in Phase 1 or deferred

ERPNext user cleanup (Claude can do; GL approved):

- Rename `locallytwisted@gmail.com` user "Jeff Baen" → "Jeff Kimber" via API
- Disable `locallytwisted@yahoo.com` placeholder user via API (reversible alternative to delete)

Cross-cutting:

- Persist nginx Origin patch via docker-compose override (P2 — only matters when LT container is recreated)

### Blockers/Concerns

Phase 1 build can begin on the brand-token install slice without resolving the decision gates. Header navigation, accessibility, blog, and photography decisions block their respective slices but not the foundation work.

## Deferred Items

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Custom Frappe app | Packaging/containerization for transfer | DEFERRED until critical mass of customizations | 2026-04-25 |
| Production hosting | Frappe Cloud signup + DEPLOY-01 | DEFERRED until Phase 6 (cutover) | 2026-04-25 |

## Session Continuity

Last session: 2026-04-26 (post-reframe)
Stopped at: Frame reset complete. PROJECT.md and ROADMAP.md promoted. Phase 1 slice plan draft and decision-gate analysis briefs pending in `.planning/phases/01-customer-site-and-storefront/` and `.planning/decisions/`.
Resume file: `HANDOFF.md` (project root) — load-bearing for next instance
Next concrete step: Execute Phase 1 Slice 1 (brand foundation — install style guide tokens into ERPNext theme). Then surface decision-gate briefs to GL for the next conversation.
