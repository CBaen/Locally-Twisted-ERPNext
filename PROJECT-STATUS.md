# Locally Twisted — Project Status

**Repo:** `git init` 2026-04-26 at `C:\Users\baenb\projects\Built_by_Cameron\_CLIENTS\locally-twisted` (separate from BBC agency repo per the 2026-04-26 isolation rule)
**Tech:** ERPNext v15.105.0 + Frappe v15 (bundled in Docker image), MariaDB 11.8, Redis 6.2, nginx — running via `frappe_docker` upstream + custom port pinning
**Purpose:** Migrate Locally Twisted's business platform from Odoo → ERPNext, with isolation/transferability built in.

---

## Current State

**What works:**
- LT ERPNext v15.105.0 running locally at `http://localhost:8081`
- WSL2 tuned: 8 GB RAM, 4 CPU, swap 2 GB, dropcache (`C:\Users\baenb\.wslconfig`)
- `pwd.yml` pinned to `frappe/erpnext:v15.105.0`
- LT Company record exists with full contact info (phone, email, website, address, tagline, Services domain)
- 3 active Users: Administrator, Cameron Paul (System Manager), Jeff Baen (System Manager, pre-created for transfer)
- 1 placeholder User: Jeff Kimber (`locallytwisted@yahoo.com`) — created by an earlier wizard run, awaiting GL decision (delete/rename/keep)
- LT Address record linked to Company (West Jordan HQ)
- Fiscal Year 2026 (Jan 1 – Dec 31)
- Chart of Accounts: Standard with Numbers
- 2 custom DocTypes ported: `Dashboard Reviewed Item`, `LT Service Type` (+ `LT Lead Service Type` child + `LT Lead Photo` child)
- `Lead` DocType extended with 46 Custom Fields + relabeled standard qualification fields, "Additional Information" tab hidden
- nginx Origin pass-through patched on the LT frontend container (socket.io now works)

**What doesn't work yet:**
- 6 of 9 Odoo models still need translation (next: `res_partner`, `product_template`, `project_task`, `calendar_event`, `hr_expense`, `res_config_settings`)
- `twilio_service` not implemented (Phase 3 work — abstract service class, not DocType)
- Native payroll: ERPNext HRMS module to be configured post-cutover (agency-wide standard 2026-04-26)
- 15–17 base.automations not ported (Phase 3)
- Utah tax (16 rates + 105 fiscal positions) not ported (Phase 3)
- Portal not built (Phase 4)
- Storefront rebuild not started (Phase 5)
- Payments not wired (Phase 7)
- Verification harness not built (Phase 8)

**Known bugs:** None yet — nothing built that's broken.

---

## Architecture Decisions

See `locally-twisted-decisions.md` for full reasoned log. Summary table:

| Date | Decision | Reasoning |
|------|----------|-----------|
| 2026-04-26 | LT lives at `_CLIENTS/locally-twisted/` with its own git repo | Per the agency isolation rule — transferability is the load-bearer of project value |
| 2026-04-26 | GSD execution mode for translations: direct script-write-and-run | Trellis's burnt-tokens drift was the receipt; planner-checker loops on mechanical work add no value |
| 2026-04-26 | `gusto_service` + `twilio_service` are NOT new DocTypes — abstract service classes | They store no records in Odoo; in Frappe they become Python helpers / Server Scripts |
| 2026-04-25 | ERPNext v15.105.0 pinned (latest stable v15 patch) | Past Stripe-broken window; latest patch on a mature line |
| 2026-04-25 | Local Docker for build, Frappe Cloud Sites plan ($5/mo) for prod | Local is free + breakable; Frappe Cloud is managed + transferable per-site |
| 2026-04-25 | Skip Phase 1 entirely (use existing off-Odoo expedition inventory) | Phase 1 was elaborate planning that never produced code — drift |
| 2026-04-25 | Build everything locally first; defer bench/transfer concerns | Build the *thing* before the *packaging* — GL explicit |
| 2026-04-25 | Don't modify anything in `locally-twisted-odoo/` | GL explicit; preserves Odoo deploy gates and trust history with Jeff |

## Research Archive

| Topic | Location | Status |
|-------|----------|--------|
| Off-Odoo replacement candidates (5-researcher extended expedition, MODERATE confidence) | `C:\Users\baenb\projects\locally-twisted-odoo\research\extended-expedition-off-odoo-replacement\` | DONE — drives PROJECT.md framing; recommended ERPNext |
| Phase 1 Inventory research (gap-fill against the off-Odoo expedition) | `.planning\phases\01-inventory\01-RESEARCH.md` | KEEP for reference |
| Phase 1 Validation strategy + threat model | `.planning\phases\01-inventory\01-VALIDATION.md` | KEEP — threat model still applicable when INV-02 reactivates near cutover |

## Key Files

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Client project rules, voice & language, reading order |
| `HANDOFF.md` | Instance-to-instance handoff (overwrite, ~40 lines) |
| `PROJECT-STATUS.md` | This file — current state, architecture decisions, dated update log |
| `lessons-learned.md` | Append-only project lessons (LT-specific) |
| `anti-gl-patterns.md` | Project-local anti-pattern catalog (peer register, GL doesn't read) |
| `locally-twisted-decisions.md` | Append-only decision log with reasoning |
| `locally-twisted-queue.md` | Active work queue (delete completed items) |
| `locally-twisted-index.md` | Pointer index for client artifacts |
| `.planning/PROJECT.md` | GSD source-of-truth |
| `.planning/ROADMAP.md` | 10 phases with success criteria |
| `.planning/REQUIREMENTS.md` | 13 v1 requirements with REQ-IDs and traceability |
| `.planning/STATE.md` | Current execution pointer |
| `.planning/config.json` | GSD config |
| `scripts/setup/setup_lt_company.py` | One-shot wizard completion + LT company seeding |
| `scripts/translate/translate_dashboard_review.py` | Dashboard Reviewed Item DocType (Trellis pattern proof) |
| `scripts/translate/translate_crm_lead.py` | Initial 42 Custom Fields on Lead |
| `scripts/fix/fix_crm_lead_multiselect.py` | iter 2: Table MultiSelect + depends_on |
| `scripts/fix/fix_crm_lead_match_book_form.py` | iter 3: align with live /book form |
| `scripts/fix/fix_crm_lead_iteration_3.py` | iter 3 follow-on: reorder, AM/PM, Delivery Window |
| `scripts/fix/fix_crm_lead_iteration_4.py` | iter 4: Time fieldtype, photos, label renames, hide Additional Info tab, +25MB upload |
| `scripts/fix/fix_lead_photo_thumbnail.py` | Attempted thumbnail (blocked by Frappe; reverted) |
| `scripts/fix/patch_nginx_socketio_origin.py` | nginx /socket.io/ Origin pass-through patch (run via docker cp + exec) |

## Rules

- **Build everything locally first.** No bench/Frappe-Cloud/transfer work until there's something real to ship. (GL explicit, 2026-04-25)
- **`locally-twisted-odoo/` is read-only reference.** Do not modify any file there from this project. (GL explicit, 2026-04-25)
- **No deployment-tier work right now.** Production DB read, SSH paths, Frappe Cloud signup — all deferred. The work is the REBUILD.
- **Voice & Language: plain language, no jargon.** See `CLAUDE.md`.
- **Trust constraint inherited from `feedback_odoo_deployment_trust.md`.** Verify before claiming done. Repeat-failure is project-killing.

---

## Updates

### 2026-04-26 — Restructure: BBC root → agency-level; LT lives in `_CLIENTS/locally-twisted/`

- All LT-specific artifacts (`.planning/`, `scripts/`, decisions, queue, lessons, anti-patterns, HANDOFF) moved from BBC root into this folder
- `git init` here for separate transferable repo
- BBC root refactored to be agency-level (rules across all clients, port allocations, v15 standard, Voice & Language general rule)
- `_CLIENTS/bbc-personal-website/` pre-staged as a separate client folder (BBC's own ERPNext install for agency-internal ops; not started)

### 2026-04-26 — Phase 2 in flight: crm.lead translated, refined across 4 iterations

- Initial translation: 42 Custom Fields on Lead with sectioned layout
- iter 2: Multi-select via Table MultiSelect → "LT Service Type" + conditional sub-section visibility
- iter 3: Realigned to live `/book` form spec; dropped 6 obsolete fields from older booking forms; +`custom_anything_else`
- iter 4: Time fieldtype, +Delivery Window Start/End, +Internal Only Notes, +Inspiration Photos child, label renames via Property Setter, hidden "Additional Information" tab, max upload 25 MB
- nginx /socket.io/ Origin pass-through patched (Trellis's earlier `bench set-config host_name` was incomplete; the actual culprit was nginx rewriting Origin to internal Docker hostname)
- LT setup wizard finalized; Cameron + Jeff users + Jeff Kimber placeholder + Address + Company contact details all populated
- 2 deferred items: photo thumbnail UX path; GL's "this is one Lead!" realization (no specific direction yet)

### 2026-04-25 evening — GSD scaffolding done; Phase 1 skipped; ready to translate

- Initialized GSD project (PROJECT.md, REQUIREMENTS.md, ROADMAP.md, STATE.md, config.json) via `/gsd-new-project`
- Phase 1 (Inventory) plans created but never executed; pivot to "skip Phase 1" after GL named the drift
- 6 Phase 1 plan files deleted; `01-RESEARCH.md` + `01-VALIDATION.md` retained
- Two background planner agents from earlier session were spawned and killed when their work no longer fit GL's direction

### 2026-04-25 day — ERPNext install + setup wizard

- Installed LT ERPNext at `:8081` (compose project `locally-twisted-erpnext-v15`, frappe_docker pwd.yml pinned to v15.105.0); first business account created
- Off-Odoo expedition findings located and read (5-researcher convergence; ERPNext recommended)
- Frappe Cloud pricing verified: $5/mo Sites plan, self-service site transfer via Actions tab
