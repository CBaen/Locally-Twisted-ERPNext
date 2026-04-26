---
phase: 1
slug: inventory
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-25
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for the Inventory phase. This phase produces two structured documents (`INVENTORY.md` and `ARCHDB-INVENTORY.md`); validation here is *coverage verification* against the source artifacts, not unit tests.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | bash + grep + Python (for DB read verification) |
| **Config file** | none — coverage checks are inline shell scripts |
| **Quick run command** | `bash .planning/phases/01-inventory/scripts/coverage-check.sh` |
| **Full suite command** | `bash .planning/phases/01-inventory/scripts/coverage-check.sh --full` |
| **Estimated runtime** | ~30 seconds (codebase scan); ~10 seconds (DB query verification) |

The `coverage-check.sh` script is created as part of the phase's first plan (Wave 0).

---

## Sampling Rate

- **After every task commit:** Run quick coverage check on the section just written (e.g., "models inventoried" → grep INVENTORY.md for every model file in `addons/locally_twisted/models/`).
- **After every plan wave:** Run full coverage check across all sections completed so far.
- **Before `/gsd-verify-work`:** Full suite must show 100% coverage of source artifacts.
- **Max feedback latency:** 30 seconds.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| (filled by planner) | | | INV-01 | n/a (read-only) | No production write attempts | coverage-check | `grep -c '^### ' INVENTORY.md` matches source file count | (pending) | pending |
| (filled by planner) | | | INV-02 | TM-01 (DB read isolation) | Read-only connection used; no DDL/DML | db-read-check | `python scripts/verify_inventory.py` exits 0 | (pending) | pending |

---

## Coverage Heuristic — INV-01

For each artifact category in the LT Odoo codebase, INVENTORY.md must include a heading and entry per source file:

| Source pattern | INVENTORY.md section | Verify command |
|---|---|---|
| `addons/*/models/*.py` | `## Models` | every `*.py` file in models/ produces at least one `### {filename}` heading |
| `addons/*/views/*.xml` | `## Views` | every `*.xml` in views/ produces at least one `### {filename}` heading |
| `addons/*/controllers/*.py` | `## Controllers` | every controller `*.py` listed |
| `addons/*/data/*.xml` | `## Data Files` | every data XML listed with its noupdate flag |
| `addons/*/security/*.csv,*.xml` | `## Security` | every ACL file listed |
| `addons/*/migrations/*/*.py` | `## Migration Scripts` | every migration script summarized |
| `addons/*/static/src/**` | `## Static Assets` | each frontend asset categorized |

**Production status annotations:** every entry must end with one of: `[in-prod]`, `[in-prod-but-broken]`, `[in-repo-not-prod]`, `[half-finished]`, `[unused]`.

---

## Coverage Heuristic — INV-02

ARCHDB-INVENTORY.md must catalog every record that holds UI-edited content not present in the git repo:

| Source table | Coverage requirement |
|---|---|
| `ir.ui.view` where `arch_db != arch_fs` | every divergent record listed with rebuild plan |
| `blog.post.website_description` | every blog post's website-edited content captured |
| `website.page.arch_db` | every page's UI-edited arch captured |
| `mail.template.body_html` | every customized email template captured |
| `product.template.description_sale` and `description` | every product description captured if non-empty and not in source data XML |
| `report.layout` and custom report templates | inventoried |

For each catalogued record: include record ID, model name, current arch_db (or summary), source XML location (if any), and rebuild strategy (`port-as-is` / `rewrite` / `confirm-with-jeff` / `discard`).

---

## Threat Model

| ID | Threat | Mitigation |
|---|---|---|
| TM-01 | Production DB read causes load spike or accidental write | Use read-only DB connection (no INSERT/UPDATE/DELETE). All queries SELECT-only. Limit row count where appropriate. |
| TM-02 | Inventory leaks customer PII into committed planning files | Strip emails, phones, addresses from any record content captured in ARCHDB-INVENTORY.md. Hash or redact. |
| TM-03 | Inventory files become stale during downstream phases | Each downstream phase that reads INVENTORY.md must check git timestamp against last LT Odoo commit; if Odoo changed since inventory, flag for re-inventory of affected sections. |

---

## Out of Scope for Phase 1 Validation

- No functional testing — no code is written in this phase except the coverage-check script and inventory document.
- No Odoo runtime testing — we don't bring up Odoo in this phase, only read its source + production DB.
- No ERPNext-side validation — that begins in Phase 2.

---

## Sign-off Criteria

- [ ] `INVENTORY.md` exists and passes coverage-check.sh against the LT Odoo codebase
- [ ] `ARCHDB-INVENTORY.md` exists and passes verify_inventory.py against production DB
- [ ] PII redaction verified — no emails, phones, or addresses in committed files
- [ ] Automation count discrepancy (15 actual vs 17 in REQUIREMENTS.md) resolved with documented explanation
- [ ] Production-vs-repo state divergence flagged where it matters (Command Center removal, etc.)
- [ ] No write operations performed against the production database (verified via deploy.py prod_shell logs)
