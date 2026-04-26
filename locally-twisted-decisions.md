# Locally Twisted — Decisions Log

**Append-only.** Newest entries at the top. Each entry: date, decision, reasoning, alternatives considered, and who decided.

Reasoning matters more than the decision itself. A future instance reading this should be able to tell whether the decision still applies given new context, or whether the conditions that justified it have changed.

LT-specific decisions only. Cross-client / agency-wide decisions live at `Built_by_Cameron/built-by-cameron-decisions.md`.

---

## 2026-04-26 — `gusto_service.py` and `twilio_service.py` are NOT new DocTypes — they're abstract service classes

**Decision:** When the Phase 2 translation reaches `gusto_service.py` and `twilio_service.py`, do NOT create new DocTypes for them. They were `models.AbstractModel` in Odoo (no records, only methods bound to a model namespace for `env["..."].method()` invocation). The Frappe-equivalent is Python helper functions inside a custom Frappe app, OR Server Scripts bound to a hook — not a DocType.

**Reasoning:** HANDOFF.md and the queue claimed "3 custom domain models need new DocTypes" — counting `dashboard_review` (done), `gusto_service`, `twilio_service`. Reading the actual sources confirmed that only `dashboard_review` stores records. The other two are stub-and-ready service abstractions: Gusto reads `account.analytic.line` and writes a CSV; Twilio reads `ir.config_parameter` for credentials and calls the Twilio SDK. Both have config-param-backed credentials (Settings UI in Odoo). In Frappe these become Python utility modules referencing Frappe's equivalent (`frappe.db.get_single_value('LT Settings', '...')`).

**Alternatives considered:** Create empty DocTypes that hold nothing and exist just to namespace the methods (rejected — pointless, breaks the Frappe pattern). Skip Twilio + Gusto entirely (rejected — they're Phase 2 scope; just need to be implemented at the right layer).

**Decided by:** Trellis-successor (this session), 2026-04-26, after reading the actual model files. Documents the correction so the next instance doesn't re-introduce the wrong assumption.

---

## 2026-04-26 — GSD execution mode for translation work: lighter than `/gsd-execute-phase`

**Decision:** Translation phases (Phase 2 onward) execute via direct script-write-and-run rather than `/gsd-execute-phase`'s planner-checker-revision loop. Strategic GSD frame stays intact (PROJECT.md, ROADMAP.md, REQUIREMENTS.md, STATE.md, decisions log). Heavier GSD process is reserved for genuinely architectural choices.

**Reasoning:** Trellis's session burned tokens running `/gsd-execute-phase` on Phase 1 (inventory). The planner-checker-revision loop produced six PLAN files for what was conceptually mechanical work and never moved a deliverable. For translation work where the source is a file on disk and the destination is configurable through an API, the translation script *is* the plan: executable, testable, reviewable. The script doubles as commit-able evidence of the work.

The pattern that worked: read the Odoo source → write a Python script targeting Frappe's REST API → run it → verify in the UI → commit (auto-commit hook). When something needed revision (multi-select + conditional visibility, GL feedback), the revision was another script — keeps both the original translation and the revision as separate, replayable artifacts.

**Alternatives considered:** Stay on `/gsd-execute-phase` (rejected — caused the drift Trellis named). Drop GSD entirely for translation phases (rejected — the strategic artifacts answer "what does done look like" and stay valuable). Use `/gsd-quick` for each translation (acceptable but adds ceremony for what is single-file work).

**When to escalate to heavier GSD process:** When a decision is genuinely architectural and reversible-only-with-cost. Examples: choosing Server Script vs Notification framework for porting the 17 base.automations (Phase 3); the Phase 5 storefront UI direction; the Phase 9 Frappe Cloud deploy strategy.

**Decided by:** Trellis-successor proposed; GL accepted with "you are my partner and collaborator with all things technical. I need you to lead!" 2026-04-26.

---

## 2026-04-25 evening — Build locally first; defer bench/transferables until real

**Decision:** All translation work (Odoo → ERPNext) happens against the local LT install at `:8081`. No custom Frappe app scaffolding, no bench planning, no Frappe Cloud setup, no transfer-to-Jeff machinery until there is something real to transfer.

**Reasoning:** GL explicitly called this out after the session drifted: "we will deal with the bench and transferables when THERE ARE." Building deployment scaffolding for nothing wastes tokens and creates the illusion of progress. Local-first means: configure DocTypes/fields/automations/theme directly in the running ERPNext at `:8081`, prove each piece works, then formalize the packaging much later when the rebuild is far enough along to make packaging meaningful.

**Alternatives considered:** Set up custom Frappe app first (rejected — premature optimization for transfer when nothing exists yet). Plan elaborate phase machinery first (rejected — see other decision below).

**Decided by:** GL explicitly.

---

## 2026-04-25 evening — Skip Phase 1 entirely; use existing expedition inventory

**Decision:** Phase 1 (Inventory, INV-01 + INV-02) plans exist on disk but will NOT be executed. The off-Odoo expedition's `locally-twisted-odoo/research/extended-expedition-off-odoo-replacement/inventory-findings.md` is treated as the working inventory baseline. INV-02 (production arch_db read) is deferred to a late phase — content migration concern, not rebuild concern.

**Reasoning:** Phase 1 was elaborately planned (6 plans across 5 waves, parallel execution, threat models, validation strategies, two checker iterations) but it never produced code or DocTypes. GL named the drift: "you haven't even rebuilt the site in ERPNext?!" The expedition inventory covers ~65% of what INV-01 was meant to produce. The remaining 35% can be filled by reading source files inline during translation phases — no separate inventory document needed. INV-02 is about Jeff's UI-edited content, which only matters at content-migration time near cutover.

**Alternatives considered:** Compress Phase 1 to a single quick plan (rejected — even one plan is more inventory ceremony when we already have one). Stay the course on Phase 1 as planned (rejected — was the source of the drift GL just called out).

**Decided by:** GL chose "Skip Phase 1 entirely" from a pivot question.

---

## 2026-04-25 evening — Don't modify anything in locally-twisted-odoo

**Decision:** All scripts, tools, and code written in service of the migration go in `_CLIENTS/locally-twisted/`. The Odoo project at `C:\Users\baenb\projects\locally-twisted-odoo\` is read-only reference. Even "operational" tooling like `deploy.py` is off-limits.

**Reasoning:** GL: "leave odoo specific scripts and skills alone. we need to create ERPNext specific ones." The Odoo project is in production, has its own deploy gates and trust history with Jeff, and any modification — even additive — risks the same trust damage that motivated this migration. ERPNext-side tools are separate concerns and stay separate.

**Alternatives considered:** Modify `deploy.py` to add an `--inventory` subcommand (rejected by GL for the rule above). Use Odoo's MCP server (currently disconnected, status uncertain).

**Decided by:** GL explicitly.

---

## 2026-04-25 — LT Standard with Numbers chart of accounts; Calendar fiscal year; Services domain

**Decision:** ERPNext Company "Locally Twisted" uses Standard with Numbers chart of accounts, Calendar fiscal year (Jan 1 – Dec 31, 2026), Services as the industry domain.

**Reasoning:** Standard with Numbers matches Odoo's default convention (carryover for Jeff's familiarity). Calendar year is US small-business default; no indication LT has a different fiscal year. Services is the closest fit for event services (balloon decor, twisting, face painting); Retail is less natural (LT is mostly service work, not goods sale).

**Decided by:** GL confirmed via AskUserQuestion 2026-04-26.
