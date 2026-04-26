---
gsd_state_version: 1.0
milestone: v0.1
milestone_name: customer-site-storefront
status: in_progress
stopped_at: Phase 1 Slice 2 attempted then paused mid-build; framework study + webshop install underway
last_updated: "2026-04-26T18:00:00.000Z"
last_activity: 2026-04-26 — Slice 2 (header+footer) attempted and paused after band-aid pattern surfaced; custom Frappe app `locally_twisted` scaffolded + bind-mounted + installed; theme CSS migrated to app via web_include_css; agency capability `frappe-conventions.md` written; framework study + webshop install in flight
progress:
  total_phases: 6
  completed_phases: 0
  deferred_phases: 0
  total_plans: 1
  completed_plans: 0
  percent: 5
---

# Project State

## Project Reference

See: `.planning/PROJECT.md` (frame reset 2026-04-26)

**Core value:** Jeff's first interaction with the new system makes him feel equipped — like he finally has the tools he should have had years ago. End result must look obvious, professional, trustworthy.

**Current focus:** Phase 1 — Customer site + storefront (the proof point). If ERPNext can't deliver this, GL pivots before building backend.

## Current Position

Phase: 1 of 6 (Customer site + storefront)
Plan: `.planning/phases/01-customer-site-and-storefront/PLAN.md` (9 slices, all decision gates resolved 2026-04-26)
Status: in flight. Slice 1 (brand foundation) DONE. Slice 2 (header + footer) attempted then paused mid-build — visible state is broken-honest pending framework study + Jinja partial override approach. Framework study + webshop app install are the active work.
Last activity: 2026-04-26 — Slice 2 build session ended on meta-pause after band-aid pattern surfaced; agency capability `frappe-conventions.md` written; HANDOFF + lessons-learned + anti-gl-patterns updated with full forensic; current session resumes via study-then-build path.

Progress: [█░░░░░░░░░] ~5% (Slice 1 of 9 done; framework study + webshop install in progress)

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

Phase 1 decision gates (all RESOLVED 2026-04-26 — see `locally-twisted-decisions.md`):

- ✓ Header navigation structure — Option B (single What-We-Make + occasion landing pages)
- ✓ Accessibility statement nuance — Option B (brief intent + actually meet WCAG 2.1 AA)
- ✓ Blog presence in Phase 1 — yes, framework + live posts (Slice 5b)
- ✓ Real photography sourcing — placeholders generated, real photos for a future iteration
- ✓ Customer-inquiry email destination — `locallytwisted@gmail.com`
- ✓ Pricing calculator placement — embedded in Slice 4 (Balloon Twisting + Face Painting page), no standalone /pricing
- ✓ ERPNext user cleanup — done (Jeff Kimber renamed; yahoo placeholder disabled)

Active work (this session):

- Bookkeeping cleanup of CLAUDE.md / STATE.md / queue staleness
- `frappe/webshop` app install (required for Slices 7-9 + Phase 4 cart/checkout/payment)
- Verify agency `frappe-conventions.md` claims against actual Frappe source in container
- Document webshop module structure (which Jinja files to override for Slices 7-9 visual customization)
- Build reusable dev scripts (editable-pip-reinstall, asset-rebuild)
- Reposition HANDOFF / PROJECT-STATUS for next session

Cross-cutting (deferred):

- Persist nginx Origin patch via docker-compose override (P2 — only matters on container recreation)
- Inspiration Photos Table field on Lead — empty section heading; tied to deferred photo UX decision

### Blockers/Concerns

Slice 2 redo (the right way, via Jinja partial overrides) blocked on completing the framework verification task. Slices 7-9 unblock when webshop is installed and its module structure is documented.

## Deferred Items

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Custom Frappe app | Packaging/containerization for transfer | DEFERRED until critical mass of customizations | 2026-04-25 |
| Production hosting | Frappe Cloud signup + DEPLOY-01 | DEFERRED until Phase 6 (cutover) | 2026-04-25 |

## Session Continuity

Last session: 2026-04-26 (Slice 2 build attempt, paused mid-execution)
Stopped at: Slice 2 visible state broken-honest (`.web-footer` height constrained, footer brand block rendering on white background). HANDOFF, anti-gl-patterns section 0, lessons-learned 2026-04-26 entry, and agency capability `frappe-conventions.md` capture the full forensic.
Resume file: `HANDOFF.md` (project root) — load-bearing for next instance
Next concrete step: Resume Slice 2 the right way — override Jinja partials at `apps/locally_twisted/locally_twisted/templates/includes/footer/footer.html` (and `footer_grouped_links.html`, `footer_info.html`, `footer_logo_extension.html`) replicating the approved Odoo structure (centered logo, two-tier header, 3-column footer, hours block, 3 social icons). Use the verified findings from this session's framework study, NOT more CSS overrides.
