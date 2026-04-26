# Locally Twisted — Index

Pointer index. Links to artifacts that live elsewhere or that are easy to lose track of.

---

## Project files (this folder)

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Client project rules, voice & language, reading order |
| `PROJECT-STATUS.md` | Current state + dated update log |
| `HANDOFF.md` | Instance-to-instance handoff (overwrite, ~40 lines) |
| `lessons-learned.md` | Append-only LT-specific lessons |
| `anti-gl-patterns.md` | Project-local instance-authored anti-pattern catalog |
| `locally-twisted-decisions.md` | Append-only decision log with reasoning |
| `locally-twisted-queue.md` | Active work queue (delete completed items) |
| `locally-twisted-index.md` | This file |
| `.env` | LT secrets (gitignored at agency root; should also be gitignored here) |

## GSD planning artifacts

| Path | Purpose |
|------|---------|
| `.planning/PROJECT.md` | Source of truth — project context, requirements, decisions, evolution rules |
| `.planning/REQUIREMENTS.md` | 13 v1 reqs across 7 categories with REQ-IDs and traceability |
| `.planning/ROADMAP.md` | 10 phases with goals, requirement mapping, success criteria |
| `.planning/STATE.md` | Current execution pointer |
| `.planning/config.json` | YOLO mode, fine granularity, parallel exec, Quality model profile |
| `.planning/phases/01-inventory/01-RESEARCH.md` | Phase 1 research findings — kept as reference even though Phase 1 is deferred |
| `.planning/phases/01-inventory/01-VALIDATION.md` | Phase 1 threat model — kept for when INV-02 reactivates near cutover |

## Scripts (this folder)

| Path | Purpose |
|------|---------|
| `scripts/setup/setup_lt_company.py` | One-shot LT setup wizard completion + Company seeding |
| `scripts/translate/translate_dashboard_review.py` | Dashboard Reviewed Item DocType (pattern proof) |
| `scripts/translate/translate_crm_lead.py` | Initial 42 Custom Fields on Lead |
| `scripts/fix/fix_crm_lead_multiselect.py` | iter 2: Table MultiSelect + depends_on |
| `scripts/fix/fix_crm_lead_match_book_form.py` | iter 3: align with live /book form |
| `scripts/fix/fix_crm_lead_iteration_3.py` | iter 3 follow-on: reorder, AM/PM, Delivery Window |
| `scripts/fix/fix_crm_lead_iteration_4.py` | iter 4: Time fieldtype, photos, label renames, hide Additional Info, +25MB |
| `scripts/fix/fix_lead_photo_thumbnail.py` | Attempted thumbnail (blocked by Frappe; reverted; offering 3 paths to GL) |
| `scripts/fix/patch_nginx_socketio_origin.py` | nginx /socket.io/ Origin pass-through patch (run via docker cp + exec) |

## Subdirectories

| Path | Contents |
|------|----------|
| `Locally-Twisted-Backend/frappe_docker/` | LT's ERPNext v15.105.0 install (cloned from frappe/frappe_docker, pwd.yml pinned + port `8081:8080`); compose project `locally-twisted-erpnext-v15` running on `:8081` |
| `Locally-Twisted-Frontend/` | Reserved for LT decoupled frontend if needed (empty as of 2026-04-26) |

## Related external projects

| Path | Relationship |
|------|--------------|
| `C:\Users\baenb\projects\locally-twisted-odoo` | The Odoo install being migrated FROM. **Read-only reference.** Continues running normally throughout the migration. Source files at `addons/locally_twisted/` are the spec we translate from. Do not modify any file there from this project. |
| `C:\Users\baenb\projects\Built_by_Cameron` | Parent agency folder. Holds cross-client rules, port allocations, Voice & Language general rule, agency decisions log. |
| `C:\Users\baenb\projects\Built_by_Cameron\_CLIENTS\bbc-personal-website` | Sibling client folder (BBC the agency's own ERPNext install). Pre-staged 2026-04-26; not started. Uses port `:8080`. |

## Research / Expedition archive

| Topic | Location |
|-------|----------|
| Off-Odoo replacement evaluation (5-researcher extended expedition, MODERATE confidence, ERPNext recommended) | `C:\Users\baenb\projects\locally-twisted-odoo\research\extended-expedition-off-odoo-replacement\` |
| Phase 1 inventory research (gap-fill against the expedition) | `.planning/phases/01-inventory/01-RESEARCH.md` |

## External resources

| Resource | URL / Location |
|----------|----------------|
| Live customer-facing booking form (production) | http://5.78.136.133/book |
| Local LT ERPNext | http://localhost:8081 |
| LT business website (live) | https://locallytwisted.com |
| Frappe Cloud pricing | https://frappe.io/cloud/pricing |
| Frappe Cloud site transfer mechanism | Forum: https://discuss.frappe.io/t/transfer-ownership-on-frappe-cloud/122800 ; Docs: https://docs.frappe.io/cloud/role-permissions and https://docs.frappe.io/cloud/managing_team_members |
| ERPNext v15.105.0 image on Docker Hub | https://hub.docker.com/r/frappe/erpnext/tags?name=v15 |
| frappe_docker upstream | https://github.com/frappe/frappe_docker |
| Trust-context for any Odoo-side work (READ before any LT prod touch) | `C:\Users\baenb\.claude\projects\C--Users-baenb-projects-jakenfriends\memory\feedback_odoo_deployment_trust.md` |
