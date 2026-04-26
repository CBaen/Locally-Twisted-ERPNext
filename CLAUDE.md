# Locally Twisted — Client Project CLAUDE.md

**Client:** Locally Twisted
**Owner:** Jeff Baen
**Business:** Custom balloon decor (arches, garlands, walls, drops), balloon twisting, face painting — Wasatch Front, Utah
**Phone:** (801) 285-0860
**Email:** hi@locallytwisted.com
**Address:** 8969 S 2700 W, West Jordan, UT 84088
**Website:** https://locallytwisted.com
**Project type:** Odoo → ERPNext migration (backend, automations, portal, storefront, payments — end-to-end)
**Status:** ACTIVE — in flight
**Currently working on:** Phase 2 (Backend Models) — Lead schema customization done; next translations queued

## Local stack

| Item | Value |
|------|-------|
| Compose project name | `locally-twisted-erpnext-v15` |
| Host port | **`:8081`** |
| Stack location | `Locally-Twisted-Backend/frappe_docker/` (relative to this folder) |
| ERPNext image pin | `frappe/erpnext:v15.105.0` (latest stable v15 patch) |
| Frappe site | `frontend` |
| URL | http://localhost:8081 |
| Logins | `Administrator` / `admin` (superuser) · `cameron@builtbycameron.com` / `LocalDev2026!` (Cameron — System Manager dev account) · `locallytwisted@gmail.com` (Jeff Baen — pre-created for transfer, no password yet) |

## This folder is structured per the agency isolation rule

See `Built_by_Cameron/CLAUDE.md` for the agency-level standing rule. **Litmus test:** every file in this folder is scoped to Locally Twisted and will be transferred to Jeff Baen on cutover. Don't add cross-client references; don't depend on agency-internal tooling that won't transfer with the folder.

## Voice & Language — LT-specific

LT is a balloon business run by Jeff Baen, who is not a tech operator. Take ALL business jargon out of the ERPNext UI. Customers and Jeff alike will use plain language.

| Avoid | Use instead |
|-------|-------------|
| "Qualification Status" | "Status of Inquiry" |
| "Qualified By" | "Reviewed and First Contact By" |
| "Qualified On" | "Reviewed On" |
| "Lead Owner" | "Who's Handling This" (or similar) |
| "Pipeline Stage" | "Where We Are" / "What Stage" |
| "Opportunity" | (Don't use; rename to "Booking" or similar) |

This applies to: Custom Field labels, Property Setter relabels of standard fields, Server Script messages, mail.template subject + body, document title customizations, status workflow names. **When in doubt, ask: would Jeff or a customer-base socialite balloon-party-thrower understand this?** If not, reword.

## Legacy Odoo system — three reachable sources, NONE authoritative

The Odoo system being migrated FROM has three surfaces you may want to consult:

| Source | Location | Notes |
|--------|----------|-------|
| Live production | `http://5.78.136.133/` | Currently serving real customers; verified UP via `curl -sI` HTTP 200 (2026-04-26) |
| GitHub repo | `https://github.com/CBaen/locally-twisted-odoo` | Remote source-of-record (last-pushed state) |
| Local clone | `C:\Users\baenb\projects\locally-twisted-odoo` | Working copy on Wardenclyffe; `git status` may diverge from prod and from GitHub |

**Read this twice: NONE of these can be considered the source of truth.** Production drifted from committed code via manual hotfixes and `noupdate=1` data records that XML updates could not retouch. The local clone may have unpushed work or be behind GitHub. GitHub may not reflect what's actually deployed on Hetzner. The last Odoo crash was the trigger for this migration; treat any single source as a hint, not ground truth.

**When the new ERPNext system needs to mirror legacy behavior, verify the same fact in at least two of the three sources before relying on it.** If they disagree, prefer the live production HTML over the local clone over GitHub (production is what customers actually saw).

**Do NOT modify any file in `locally-twisted-odoo/` from this project** (per directive 2026-04-25). It has its own deploy gates and trust history with Jeff. ERPNext-side scripts only, in this folder.

## Reading order on arrival

1. Global `C:\Users\baenb\.claude\CLAUDE.md` (auto-injected)
2. `Built_by_Cameron\CLAUDE.md` (agency-level rules)
3. **This file**
4. `HANDOFF.md` (last instance's continuity notes)
5. `.planning\PROJECT.md` (GSD project source-of-truth)
6. `locally-twisted-decisions.md` (LT decisions with reasoning)
7. `git log --oneline -20`

## Loud Failure Coverage

Per global rule at `C:\Users\baenb\.claude\rules\loud-failure.md`. LT-specific surfaces tracked as they're built. The Odoo `/book` form silent-failure incident (2026-04-22) is the founding receipt for this rule — never repeat that pattern.

## Customer / Contact dedup (Phase 3 work)

When the customer-facing form lands a Lead in ERPNext, the Lead must auto-link to a Contact: lookup by email_id / mobile_no / phone; attach if found, create if not. Mirrors Odoo's `_find_matching_partner` + `_create_partner_from_lead`. Implementation: Server Script on Lead `before_insert`. Tracked in queue.

## Form-handler routing (Phase 5 work)

The live customer-facing `/book` form (currently on Odoo) posts to Odoo field names: `contact_name`, `phone`, `email_from`, `partner_name`, `description`, `x_*` fields. ERPNext Lead expects: `lead_name`, `phone`, `email_id`, `company_name`, `custom_anything_else`, `custom_*`. Build the field-rename mapping in the Web Form / API endpoint that replaces /book on the ERPNext side. Tracked in queue.

## Project Skills

No project-specific skills yet. Add to `.claude/skills/` as patterns emerge.

## GSD Workflow Note

Translation phases (Phase 2 onward) execute via direct script-write-and-run (not `/gsd-execute-phase` planner-checker loops). Strategic GSD frame stays intact (PROJECT.md, ROADMAP.md, REQUIREMENTS.md, STATE.md, decisions log). See `locally-twisted-decisions.md` 2026-04-26 entry for full reasoning.
