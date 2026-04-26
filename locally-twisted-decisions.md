# Locally Twisted — Decisions Log

**Append-only.** Newest entries at the top. Each entry: date, decision, reasoning, alternatives considered, and who decided.

Reasoning matters more than the decision itself. A future instance reading this should be able to tell whether the decision still applies given new context, or whether the conditions that justified it have changed.

LT-specific decisions only. Cross-client / agency-wide decisions live at `Built_by_Cameron/built-by-cameron-decisions.md`.

---

## 2026-04-26 (Slice 2 build) — Custom Frappe app scaffolding is on; only Frappe Cloud cutover stays deferred

**Decision:** Custom Frappe app scaffolding (`locally_twisted` as an installable app inside the local bench) is part of the active build, not deferred. What stays deferred until Phase 6 is the Frappe Cloud signup, production deployment, and transfer-to-Jeff machinery.

**Reasoning:** GL clarified directly during the Slice 2 build session: "Frappe can and should be added. It's the cloud migration that isn't a priority until there's something to show." The earlier 2026-04-25 evening entry below conflated two things — local app scaffolding and cloud cutover — and deferred both. Only the latter should have been deferred.

The shape of the work changes with this correction:
- Theme CSS migrates from `Website Settings.head_html` (current Slice 2 implementation) to a real bundled asset at `apps/locally_twisted/locally_twisted/public/css/lt-theme.css`, registered via `hooks.py`, served through Frappe's asset pipeline.
- Custom DocTypes (`Dashboard Reviewed Item`, `LT Service Type`, `LT Lead Photo`) export as fixtures owned by the app.
- The 45+ Custom Fields on Lead export as Custom Field fixtures.
- Future Server Scripts (Phase 2 lead intake, Phase 3 cascades) live in the app, not as one-off DocType records.
- The whole customization surface becomes one installable unit (`bench install-app locally_twisted`).

**What this means in practice for Slices 3-9:** Better to scaffold the app *before* Slice 3 (landing page) so Slices 3-9 build natively into the app structure rather than as records that later need migration. Doing it now is hours of work; deferring it costs more later when the customization surface is larger.

**Supersedes:** the relevant clauses of the 2026-04-25 evening entry below ("No custom Frappe app scaffolding, no bench planning"). What that entry got right: keep all build work against the local `:8081` install, defer Frappe Cloud / transfer machinery until Phase 6. What it got wrong: lumping app scaffolding in with the cloud-side deferrals.

**Decided by:** GL directive during Slice 2 build, 2026-04-26.

---

## 2026-04-26 (later) — Phase 1 decision gates resolved

**Decision:** All four Phase 1 decision gates surfaced earlier today are resolved.

1. **Header navigation:** Option B — single "What We Make" mega-menu by product type; "Special Occasions" and "Holidays & Seasons" become filtered landing pages reachable from a "Browse by occasion" header link. See `.planning/decisions/header-navigation.md` for the full analysis.

2. **Accessibility statement:** Option B — brief intent-only statement with a working `accessibility@locallytwisted.com` contact + actually meeting WCAG 2.1 AA on the live site. Statement text drafted. See `.planning/decisions/accessibility-statement.md`.

3. **Blog presence in Phase 1:** YES — ship the blog framework with live posts (not deferred, not empty framework). Adds Slice 5b to the Phase 1 plan.

4. **Real photography sourcing:** placeholders. GL's exact words: "Generate fake quality images please... leave most images blank except everything on the main pages and 1 product image on product pages." 15 placeholder images generated via Together AI's FLUX.1-schnell, committed to `_resources/images/`. Real photography is "possibly a project for another instance" — these placeholders carry the demo until then.

5. **Customer-inquiry email destination:** `locallytwisted@gmail.com` (GL's account; GL handles inquiries currently).

6. **Pricing calculator placement:** embedded in the Balloon Twisting + Face Painting service page (Slice 4), NOT a standalone `/pricing` URL. GL's call: "the pricing calculator would be perfect for the face painting and balloon twisting page!" Better placement — customers already on that page are asking the cost question. Standalone Slice 10 removed; calculator scope folded into Slice 4.

**Reasoning:** GL chose all four answers explicitly in the green-light turn. Recommendations from `.planning/decisions/header-navigation.md` (Option B) and `.planning/decisions/accessibility-statement.md` (Option B) were accepted. Blog framework + live posts gives Phase 1 more substance for Jeff's eventual demo. Placeholder images close the visual-demo gap without committing to real photography sourcing yet.

**Decided by:** GL directive 2026-04-26.

---

## 2026-04-26 (later) — All clients default to ERPNext native payroll; Gusto removed from project scope

**Decision:** All Built by Cameron client builds default to ERPNext's native HRMS / Payroll module. Gusto is removed from the LT ERPNext-side project scope: no Gusto credential fields, no `gusto_service` Python helper, no Gusto CSV export job. The Gusto integration in the failed Odoo attempt was **never wired or used** (per GL clarification 2026-04-26) — the Odoo files are dead code on a never-launched test deployment.

**Reasoning:** GL directive 2026-04-26: "All clients will default to the ERP's native payroll. Please delete anything labeled 'Gusto.'" ERPNext HRMS supports salary structures, payroll periods, leave, attendance, and direct deposit natively. One less third-party integration to learn, configure, document, and hand off. Since Gusto never went live, there is no production behavior to preserve — clean slate.

**Alternatives considered:** Keep Gusto on ERPNext side as a CSV-export Server Script (rejected — perpetuates a third-party-payroll pattern the agency standard now overrides).

**What this means in practice:**
- `res_config_settings.py` translation drops any `gusto_*` fields; only `twilio_*` credentials carry over.
- A future phase (after the core build is stable) installs Frappe HRMS and configures it for LT.
- No accountant conversation needed — Gusto was never the system of record for LT's payroll.

**Supersedes:** the earlier 2026-04-26 entry that treated `gusto_service` as Phase 3 scope. The earlier entry has been rewritten to cover only `twilio_service`.

**Decided by:** GL directive 2026-04-26.

---

## 2026-04-26 — `twilio_service.py` is NOT a new DocType — it's an abstract service class

**Decision:** When the Phase 2 translation reaches `twilio_service.py`, do NOT create a new DocType for it. It was `models.AbstractModel` in Odoo (no records, only methods bound to a model namespace for `env["..."].method()` invocation). The Frappe-equivalent is Python helper functions inside a custom Frappe app, OR Server Scripts bound to a hook — not a DocType.

**Reasoning:** HANDOFF.md and the queue originally claimed "3 custom domain models need new DocTypes" — counting `dashboard_review` (done), `twilio_service`, and (formerly) `gusto_service`. Reading the actual sources confirmed that only `dashboard_review` stores records. `twilio_service` is a stub-and-ready service abstraction: it reads `ir.config_parameter` for credentials and calls the Twilio SDK. In Frappe it becomes a Python utility module referencing `frappe.db.get_single_value('LT Settings', '...')`.

**Alternatives considered:** Create an empty DocType that holds nothing and exists just to namespace the methods (rejected — pointless, breaks the Frappe pattern). Skip Twilio entirely (rejected — SMS notifications are real product scope).

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
