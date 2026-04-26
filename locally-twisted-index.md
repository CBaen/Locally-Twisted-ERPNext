# Locally Twisted — Index

Pointer index. Links to artifacts that live elsewhere or that are easy to lose track of.

---

## Project files (this folder)

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Client project rules, voice & language, reading order, Reference Disposition |
| `PROJECT-STATUS.md` | Current state + dated update log |
| `HANDOFF.md` | Instance-to-instance handoff (overwrite, ~40 lines) |
| `lessons-learned.md` | Append-only LT-specific lessons |
| `anti-gl-patterns.md` | Project-local instance-authored anti-pattern catalog |
| `locally-twisted-decisions.md` | Append-only decision log with reasoning |
| `locally-twisted-queue.md` | Active work queue (delete completed items) |
| `locally-twisted-index.md` | This file |
| `.env` | LT secrets (gitignored) |

## Resources (canonical for the new build — `_resources/`)

| File | Purpose |
|------|---------|
| `_resources/STYLE-GUIDE.md` | Design system: color palette, typography, components, "Quiet Confidence" voice, blog "Kindergarten Teacher" voice, accessibility (WCAG 2.1 AA), photography rules |
| `_resources/utah-tax-rates-2026q2.md` | Utah destination-based sales tax research, per-jurisdiction rates |
| `_resources/policies/INDEX.md` | Pointer to the 6 business policy files |
| `_resources/policies/legal-interview-answers.md` | Master legal interview — sufficient for attorney to draft v1 contract |
| `_resources/policies/pricing-formula.md` | Per-artist pricing math; "no combination discount" rule |
| `_resources/policies/deposits.md` | Deposit structure by client type and service |
| `_resources/policies/service-area.md` | Free service zone (4 counties); travel fee rules |
| `_resources/policies/tax.md` | Utah sales tax behavior — city-based, calculated at checkout |
| `_resources/policies/theme-and-character-rules.md` | "Any character, any request" — no theme limits |

## GSD planning artifacts

| Path | Purpose |
|------|---------|
| `.planning/PROJECT.md` | Source of truth — project context, requirements, decisions, evolution rules (frame reset 2026-04-26) |
| `.planning/REQUIREMENTS.md` | Requirements with REQ-IDs and traceability — needs refresh against new ROADMAP |
| `.planning/ROADMAP.md` | 6 workflow-centric phases (frame reset 2026-04-26) |
| `.planning/STATE.md` | Current execution pointer |
| `.planning/config.json` | YOLO mode, fine granularity, parallel exec, Quality model profile |
| `.planning/decisions/header-navigation.md` | Phase 1 decision gate: super-menus vs. consolidated nav |
| `.planning/decisions/accessibility-statement.md` | Phase 1 decision gate: statement options + small-business legal risk |
| `.planning/phases/01-customer-site-and-storefront/PLAN.md` | Phase 1 slice plan (drafted; awaiting decision gates before some slices proceed) |
| `.planning/phases/01-inventory/01-RESEARCH.md` | Legacy reference from prior framing — kept for historical context only |

## Scripts (this folder)

Built before the frame reset; some still active, some legacy reference.

| Path | Purpose | Status |
|------|---------|--------|
| `scripts/setup/setup_lt_company.py` | One-shot LT setup wizard completion + Company seeding | Done; reusable on fresh installs |
| `scripts/translate/translate_crm_lead.py` | Initial 42 Custom Fields on Lead | Done; produced the active Lead schema |
| `scripts/fix/fix_crm_lead_multiselect.py` | iter 2: Table MultiSelect + depends_on | Done |
| `scripts/fix/fix_crm_lead_match_book_form.py` | iter 3: align with live /book form | Done |
| `scripts/fix/fix_crm_lead_iteration_3.py` | iter 3 follow-on: reorder, AM/PM, Delivery Window | Done |
| `scripts/fix/fix_crm_lead_iteration_4.py` | iter 4: Time fieldtype, photos, label renames, hide Additional Info, +25MB | Done |
| `scripts/fix/fix_lead_photo_thumbnail.py` | Attempted thumbnail (blocked by Frappe; reverted; offering 3 paths to GL) | Reverted; UX path TBD |
| `scripts/fix/patch_nginx_socketio_origin.py` | nginx /socket.io/ Origin pass-through patch | Active; persistence via compose override is P2 backlog |
| `scripts/translate/translate_dashboard_review.py` | Dashboard Reviewed Item DocType (early proof-of-pattern) | Done; no current Phase depends on it |

## Subdirectories

| Path | Contents |
|------|----------|
| `Locally-Twisted-Backend/frappe_docker/` | LT's ERPNext v15.105.0 install (cloned from frappe/frappe_docker, pwd.yml pinned + port `8081:8080`); compose project `locally-twisted-erpnext-v15` running on `:8081`. Gitignored. |
| `Locally-Twisted-Frontend/` | Reserved for LT decoupled frontend if needed (empty). Gitignored. |
| `_resources/` | Canonical resources — see Resources section above |

## Reference Disposition (READ before citing anything outside this folder)

The four reference surfaces below are **temporary** and will be retired. See `CLAUDE.md` "Reference Disposition" for full rule.

| Path / URL | Disposition |
|------|------|
| `C:\Users\baenb\projects\locally-twisted-odoo` | Local clone of prior platform attempt. Read-only. Will be archived to GitHub and removed from disk. |
| `http://5.78.136.133/` | Failed test deployment of prior attempt. Serves HTTP 200 but no customers depend on it. Will be decommissioned. |
| `https://github.com/CBaen/locally-twisted-odoo` | Prior attempt's source repo. Will be archived as read-only. |
| `https://locallytwisted.com` | Current customer-facing site. Damaged beyond repair. Out of scope for editing; replaced at cutover. |

**Future instances:** if you reach into the prior-platform dir for anything other than the resources already copied to `_resources/`, stop. The thing you need lives here, or it's not needed.

## Related external paths

| Path | Relationship |
|------|--------------|
| `C:\Users\baenb\projects\Built_by_Cameron` | Parent agency folder. Holds cross-client rules, port allocations, agency decisions log |
| `C:\Users\baenb\projects\Built_by_Cameron\_CLIENTS\bbc-personal-website` | Sibling client folder (BBC the agency's own ERPNext install). Pre-staged 2026-04-26; not started. Uses port `:8080`. |
| `https://github.com/CBaen/Locally-Twisted-ERPNext` | This project's GitHub repo (canonical source for the new build) |

## External resources

| Resource | URL / Location |
|----------|----------------|
| Local LT ERPNext | http://localhost:8081 |
| Frappe Cloud pricing | https://frappe.io/cloud/pricing |
| ERPNext v15 image | https://hub.docker.com/r/frappe/erpnext/tags?name=v15 |
| frappe_docker upstream | https://github.com/frappe/frappe_docker |
