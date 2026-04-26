# HANDOFF — Locally Twisted (Odoo→ERPNext Migration)

**Last updated:** 2026-04-26 (Opus 4.7, Trellis-successor — no name chosen)

Overwrite-not-append. ~40 lines. Git is the changelog.

## Live state

**LT ERPNext v15.105.0 running:** http://localhost:8081 — compose project `locally-twisted-erpnext-v15`. Setup wizard complete. Logins per `CLAUDE.md`.

**Phase 2 (Backend Models) — in flight.** Custom models translated:
- ✓ `dashboard_review` → `Dashboard Reviewed Item` DocType (Trellis, prior session)
- ✓ `crm_lead` → 46 Custom Fields on `Lead` after 4 iterations:
  - iter 1: 42 Custom Fields, sectioned but Select-only
  - iter 2: Multi-select via Table MultiSelect → "LT Service Type" (6 canonical services after iter 3)
  - iter 3: Realigned to live `/book` form, dropped 6 obsolete fields, +`custom_anything_else`, conditional sections per service
  - iter 4: Time fields → Time fieldtype, +Delivery Window Start/End, +Internal Only Notes, +Inspiration Photos child table, qualification labels relabeled, "Additional Information" tab hidden, max upload 25 MB
- ☐ `res_partner`, `product_template`, `project_task`, `calendar_event`, `hr_expense`, `res_config_settings` (next translations)
- ☐ `twilio_service` is an abstract service class — implement as Python helpers / Server Scripts, NOT a new DocType (per 2026-04-26 decision)

**Two open items deferred from this session, awaiting user decision before resuming:**
1. **Inspiration Photos thumbnail UX** — Frappe blocks `in_list_view` on Attach Image AND Image fieldtypes in child tables. Three paths offered to GL: (a) click-to-expand (current state), (b) Frappe Client Script for inline gallery rendering, (c) drop child table for built-in attachments sidebar. GL hasn't picked yet.
2. **GL's "this is one Lead!" realization** — was thinking each tab was a Lead category; reality is sections of one Lead form. GL hasn't said what they actually wanted to model differently. **Don't redesign without their explicit direction.**

## Hot direction (load-bearing for next session)

1. **GL is leading less, partnering more.** "You are my partner and collaborator with all things technical. I need you to lead!" (2026-04-26). Make calls; surface choices that need GL input; don't ask permission for obvious moves.
2. **Verify in UI before claiming done.** GL caught the multi-select bug because they actually opened the form. Use `python C:/Users/baenb/.claude/scripts/screenshot.py` (primary monitor) or the virtual-screen one-liner in PowerShell. Browser is on a separate monitor.
3. **Translation pattern (now agreed mode):** read Odoo source → write `scripts/translate/translate_<model>.py` → run via `python` → verify in UI → commit. Revisions land as `scripts/fix/fix_<thing>.py`. NO formal GSD plan files for translations.
4. **Voice & Language:** plain language, no business jargon (see `CLAUDE.md`). LT is a balloon business; Jeff is not corporate.
5. **The customer-facing `/book` form (Odoo side) needs to mirror the new Lead schema** — add `x_event_end_time`, switch all time inputs to AM/PM-friendly, add the new fields per iter 3+4. **Coordinate with GL on which session/instance does this** — `locally-twisted-odoo/` is read-only from this project per directive 2026-04-25.

## Major architectural change in this session

The whole BBC repository was restructured 2026-04-26 (this session) per GL's epiphany: BBC is purely an ERPNext design agency; LT is a CLIENT (not part of BBC). All LT-specific work moved from BBC root to `_CLIENTS/locally-twisted/`. Each client now has its own git repo, own CLAUDE.md, own standard project files. Litmus test: if it stays useful when transferred to the client owner, it lives in the client folder. See `Built_by_Cameron/CLAUDE.md` for the agency-level rule.

## Not in flight

No spawned processes. Docker daemon runs LT compose stack detached. No background agents.

## Reading order on arrival

See `CLAUDE.md` reading order section.
