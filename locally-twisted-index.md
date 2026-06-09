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

## Resources (canonical for the migration destination — `_resources/`)

| File | Purpose |
|------|---------|
| `_resources/STYLE-GUIDE.md` | Current visual authority: Civic Celebration + Slate Blue/Berry + Brand Direction, Cormorant Garamond + Lato, page treatments, professional icon suite, photo rules, voice, accessibility |
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
| Retired Lead schema scripts | Old one-off `translate_crm_lead.py` and `fix_crm_lead_*` scripts were removed because they contained stale `/book` and service-taxonomy logic. | Git history only |
| `scripts/setup/sync_contact_intake_backend.py` | Current idempotent sync for Lead service taxonomy, conditional fields, and Inspiration Photos table wiring | Active |
| `scripts/verify/lead_backend_intake_parity.py` | Current verifier for Lead service taxonomy, conditional fields, submit mapping, and LT Lead Photo wiring | Active |
| `scripts/setup/sync_backend_workspaces.py` | Current idempotent sync for simplified Owner/Manager/Employee workspace labels and Sales Order booking calendar | Active |
| `scripts/verify/backend_workspace_parity.py` | Current verifier for simplified workspace labels and booking calendar wiring | Active |
| `scripts/fix/patch_nginx_socketio_origin.py` | nginx /socket.io/ Origin pass-through patch | Active; persistence via compose override is P2 backlog |
| `scripts/translate/translate_dashboard_review.py` | Dashboard Reviewed Item DocType (early proof-of-pattern) | Done; no current Phase depends on it |

## Subdirectories

| Path | Contents |
|------|----------|
| `Locally-Twisted-Backend/frappe_docker/` | LT's ERPNext v15.105.0 install (cloned from frappe/frappe_docker, pwd.yml pinned + port `8081:8080`); compose project `locally-twisted-erpnext-v15` running on `:8081`. Gitignored. |
| `Locally-Twisted-Frontend/` | Reserved for LT decoupled frontend if needed (empty). Gitignored. |
| `_resources/` | Canonical resources — see Resources section above |
| `workstreams/` | Feature/outcome handoffs for multi-agent work. Start with `website-launch.md` and `launch-v1-success-contract.md` for current website launch scope. |

## Active workstream anchors

| File | Purpose |
|------|---------|
| `workstreams/launch-v1-success-contract.md` | V1 launch scope contract: website-first quality, buyer priority, commercial lanes, quality targets, deferred 10-year ERPNext maturity, and immediate redesign sequence. |
| `workstreams/coordination-safety-pilot-2026-05-21.md` | Protected child/client repo pilot for the neutral multi-agent coordination workflow; no product or release approval. |
| `workstreams/website-launch.md` | Launch controller board and verification gates. |
| `workstreams/domain-provider-reindex-cleanup-2026-05-19.md` | Current provider-chain and reindex cleanup handoff: GoDaddy registrar, Cloudflare authoritative DNS/email routing, Frappe Cloud hosting, Hetzner/legacy_source old-reference status, Bluehost cleanup target, and live sitemap/canonical vanity-host blocker. |
| `workstreams/launch-repo-cleanup-2026-05-10.md` | Launch cleanup handoff for raw drops, stale generated evidence, removed contest output, and repo-light client handoff rules. |
| `workstreams/ecommerce-audit/README.md` | Front-door ecommerce infrastructure/evidence map, including the 2026-05-17 all-legacy_source sellable reimport proof, product repair map, and local-only launch gates. |
| `workstreams/ecommerce-audit/legacy_source-sellable-product-reimport-2026-05-17.md` | Current all-legacy_source local import closeout: 53/53 legacy_source products included as sellable checkout targets, 0 exclusions, 290 priced sale units, all 53 routes browser-proved in batches, no live deploy. |
| `workstreams/ecommerce-audit/product-family-certification-truth-table-2026-05-17.md` | Historical staged certification truth table, superseded by the all-legacy_source sellable reimport closeout for current product scope. |
| `workstreams/ecommerce-audit/product-source-repair-map-2026-05-17.md` | legacy_source-export-backed repair queue for all 53 products; every product targets purchasable behavior and held products are blocked until certified. |
| `workstreams/ecommerce-audit/simple-purchasable-rehearsal-2026-05-17.md` | Rollback-safe backend proof for the first simple repair tranche: four products, 33 source-backed sale SKU lines, SO/SI preservation, no browser/payment/live approval yet. |
| `workstreams/ecommerce-audit/simple-purchasable-browser-proof-2026-05-17.md` | Local open-mode browser proof for the first simple repair tranche: desktop/mobile product pages, cart, checkout preview, and restoration verified; payment/live approval still pending. |
| `workstreams/ecommerce-audit/simple-purchasable-payment-cascade-2026-05-17.md` | Rollback-safe payment cascade proof for the first simple repair tranche: all 33 sale lines through PR/PE/SI/receipt/operator/welcome/idempotency; final approval still pending. |
| `workstreams/ecommerce-audit/complex-checkout-scaffold-2026-05-12.md` | Source-backed checkout-planning scaffold: direct-checkout guards, simple purchasable rehearsal candidates, multi-color UI, add-on/conditional blockers, and needs-review products. |
| `workstreams/inquiry-photo-storage-owner-attachments-2026-05-15.md` | Public inquiry photo storage and owner-attachment hotfix boundary: production incident facts, local proof, source commits, live deploy gate, and cross-links. |
| `workstreams/brand-audience-style-reset.md` | Brand/audience reset, proof inventory, and reference-site lessons. |
| `workstreams/brand-style-guide-consolidation.md` | Current feature handoff for the 2026-05-05 style-guide cleanup, deleted conflicting references, and new icon-suite direction. |
| `workstreams/shop.md` | Shop, catalog, product, variant, media, and ecommerce confidence lane. |
| `workstreams/policy-trust.md` | Policy, trust, Stripe/legal readiness lane. |

## Reference Disposition (READ before citing anything outside this folder)

The four reference surfaces below are **temporary** and will be retired. See `CLAUDE.md` "Reference Disposition" for full rule.

| Path / URL | Disposition |
|------|------|
| `C:\Users\baenb\projects\locally-twisted-legacy_source` | Local clone of prior platform attempt. Read-only. Will be archived to GitHub and removed from disk. |
| `http://5.78.136.133/` | Failed legacy_source/Hetzner test deployment of prior attempt. Not current public DNS. Keep read-only until archive/decommission proof is complete. |
| `https://github.com/CBaen/locally-twisted-legacy_source` | Prior attempt's source repo. Will be archived as read-only. |
| `https://locallytwisted.com` | Current customer-facing Frappe Cloud site served through Cloudflare. Source is this ERPNext project and the Frappe app mirror. |

**Future instances:** if you reach into the prior-platform dir for anything other than the resources already copied to `_resources/`, stop. The thing you need lives here, or it's not needed.

## Related external paths

| Path | Relationship |
|------|--------------|
| `C:\Users\baenb\projects\Built_by_Cameron` | Parent agency folder. Holds cross-client rules, port allocations, agency decisions log |
| `C:\Users\baenb\projects\Built_by_Cameron\_CLIENTS\bbc-personal-website` | Peer client folder (BBC the agency's own ERPNext install). Pre-staged 2026-04-26; not started. Uses port `:8080`. |
| `https://github.com/CBaen/Locally-Twisted-ERPNext` | This project's GitHub repo (canonical source for the migration destination) |

## External resources

| Resource | URL / Location |
|----------|----------------|
| Local LT ERPNext | http://localhost:8081 |
| Frappe Cloud pricing | https://frappe.io/cloud/pricing |
| ERPNext v15 image | https://hub.docker.com/r/frappe/erpnext/tags?name=v15 |
| frappe_docker upstream | https://github.com/frappe/frappe_docker |
