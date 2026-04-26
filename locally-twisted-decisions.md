# Locally Twisted — Decisions Log

**Append-only.** Newest entries at the top. Each entry: date, decision, reasoning, alternatives considered, and who decided.

Reasoning matters more than the decision itself. A future instance reading this should be able to tell whether the decision still applies given new context, or whether the conditions that justified it have changed.

LT-specific decisions only. Cross-client / agency-wide decisions live at `Built_by_Cameron/built-by-cameron-decisions.md`.

---

## 2026-04-26 (post-session research) — License posture clarified: ERPNext is GPL-3.0, Frappe is MIT, AGPL concern was Builder-specific (not installed)

**Decision:** The expedition's Flag 8 raised an AGPL concern. Research + direct verification against `apps/<app>/license.txt` in the running LT stack establishes the actual license set:

| App | License | Notes |
|---|---|---|
| frappe (Framework) | MIT | Custom code on Frappe sits closest to MIT territory |
| erpnext | GPL-3.0 | Derivative-work exposure if our app derives from ERPNext internals |
| webshop | GPL-3.0 | Same |
| payments | MIT | No copyleft pressure |
| locally_twisted (custom) | MIT | License placeholder in license.txt — owner field needs filling |

**The AGPL claim was specifically about Frappe Builder** (a separate optional app) — NOT about ERPNext or Frappe Framework core. Builder is not installed on LT. The AGPL concern only re-applies if a future BBC client adopts Builder; it does not apply to LT's current stack.

**Reasoning:** the expedition's Flag 8 left this ambiguous, and a downstream reading could have absorbed "ERPNext / Frappe might be AGPL." Direct verification corrects that. Our Build → Sell → Transfer model deals with GPL-3.0 derivative-work analysis (a more conventional, well-documented legal posture), not the AGPL network-use clause.

**Operational consequence for LT specifically:**
- Continue building `locally_twisted` as a Frappe-first custom app
- Interact with ERPNext / Webshop via documented hooks, public APIs, DocType reads, NOT by editing core or subclassing internals
- When Phase 4 (payments) wires up Stripe, that goes through the `payments` app's `Payment Gateway Account` DocType (MIT-licensed surface)
- When the catalog seeds, query through Webshop's `Website Item` API (GPL-3.0 read), don't copy Webshop internals into our app

**Open architectural question for the agency tier (not LT's call alone):** whether to split custom code into `agency_platform` (reusable) + `locally_twisted_connector` (thin adapter) for stronger license isolation. Tracked at `Built_by_Cameron/built-by-cameron-decisions.md` 2026-04-26 entry "License matrix verified..." Finding 3.

**Decided by:** Perplexity research surfaced the license question; verification done by reading license files directly in the running LT container 2026-04-26. Codified at agency-tier conventions doc.

---

## 2026-04-26 (session end) — Platform-direction question is OPEN; landing build approach was wrong on three counts

**Decision:** No platform direction decided this session. The question is now explicitly on GL's desk for the next conversation.

**The question, verbatim from the synthesis:** *Do you want to keep building the customer-facing website inside Frappe + webshop, OR explore a simpler front door (WordPress / Webflow / Next.js) with ERPNext quietly running the back office?*

**Reasoning:** A full expedition (3 source-separated researchers + convergence + devil's advocate + GL Proxy) found:

1. The Frappe theme ecosystem is THIN. No turnkey polished customer-facing themes exist. Every Frappe-built site that looks polished was built by Frappe employees for Frappe properties (frappe.io, fossunited.org, cloud.frappe.io). No documented case of a small business successfully running a polished customer-facing site on Frappe was found.
2. Two LT homepage builds have failed in two consecutive sessions. Both failed by the same pattern: invented placeholder copy + band-aid CSS overrides + declaring "done" off DOM facts before GL opened the page in a real browser. The architecture wasn't the problem; the technique was.
3. The Phase 1 off-ramp condition GL set ("if ERPNext can't deliver this visual + UX bar, GL pivots away from ERPNext") is exactly what the Devil's Advocate questioned. It has not been answered consciously.

The GL Proxy flagged the convergence's tendency to route past the platform question and steelman the Frappe path. This decision entry surfaces it as the open question it is.

**What's known:**
- Frappe + custom Jinja + custom CSS will work eventually but requires substantial custom CSS work and Jeff cannot maintain it post-handoff.
- WordPress + WooCommerce has the most off-the-shelf plugins for service booking + ecommerce but is the most-hacked CMS in the world (security maintenance burden).
- Webflow is designer-first and Jeff can edit pages himself, but its ecommerce is light for complex variant catalogs.
- Next.js + headless commerce (Vercel Commerce, Saleor, Medusa.js) gives best design freedom and best SEO but is Cameron-maintained forever and adds a sync layer to ERPNext.

**Alternatives considered:** Keep building on Frappe without surfacing the question (rejected — would repeat the two-session failure pattern). Pre-decide for GL based on convergence (rejected — the choice depends on trade-offs only GL can weigh). Run more research first (rejected — the expedition was thorough; what's missing is GL's input, not more data).

**Decided by:** No decision yet. GL is collecting more information. They asked specifically about webshop architecture, SEO/GEO/AEO of decoupled, service-scheduling needs, GitHub catalog import patterns, and whether Next.js works for ecommerce. All answered in the session transcript before this entry was written. They want to compare Vercel Commerce demo + Frappe Builder + Webflow templates side by side before deciding.

**Status:** PENDING. Blocks all build tasks (#11, #12, #13, #14 in the session-end queue). Next instance must read `research/expedition-frappe-theme/synthesis.md` and confirm direction with GL before any visible build work resumes.

---

## 2026-04-26 (session end) — Approved Jeff content is NEVER invented — pull from Odoo XML or live locallytwisted.com

**Decision:** All customer-facing copy on the LT site comes from one of two authoritative sources, never from instance imagination:
1. **`C:/Users/baenb/projects/locally-twisted-odoo/addons/locally_twisted/views/`** (XML view files in the local Odoo project) — the most recent Jeff-approved Odoo update, captured verbatim in `research/expedition-frappe-theme/ground-truth-findings.md`. Per CLAUDE.md, this is authoritative for the new build.
2. **`https://locallytwisted.com/`** (the live WordPress site Jeff still uses) — actively in front of customers today, captured verbatim in `research/expedition-frappe-theme/web-scout-findings.md`. The two sources diverge on hero copy, social icon count (3 vs 4), and credential framing ("since 1998" vs "Over 22 years"). GL has NOT yet picked which is "the" version.

**Reasoning:** Two consecutive instances invented placeholder copy ("Make Your Celebration Unforgettable", "Three services. One promise: you get the moment, we handle the magic", "Ready to plan something unforgettable?") when the actual approved copy was sitting on disk. GL caught both. The trust cost was real both times. The pattern needs to die.

**What this means in practice:**
- Before writing any text that will appear on a customer-facing page, READ the Odoo XML or scrape the live site and use the actual content.
- For copy that needs to be slightly adapted to fit a new layout, do the adaptation but preserve voice + key phrases verbatim.
- If neither source has copy for a new surface, ASK GL — do not invent.

**Open sub-decision for GL:** Which of the two sources is "the" approved version when they disagree? Specifically:
- Hero copy: "Utah's Balloon Specialists" / "Making celebrations unforgettable since 1998" (Odoo) vs "Make Your Party POP!" / "Anything you imagine, we can shape into reality" (live site)
- Social icons: 3 (Facebook, Instagram, Pinterest — Odoo) vs 4 (+ Twitter — live site)
- Credentials: "since 1998" / 28 years (Odoo) vs "Over 22 years" (live site)
- Tagline: "Utah's Balloon Specialists since 1998." (Odoo) vs different framings on live site

**Decided by:** Lessons-learned pattern from this session + GL's explicit "did you make it up?" callout. The decision becomes a standing rule once GL confirms which source is authoritative.

---

## 2026-04-26 (Web Page tabs finding) — Per-page interactivity belongs in the DocType, not a custom Web Template

**Decision:** All per-page interactivity (JavaScript, CSS, server-side data fetching) for one-off pages goes into the corresponding `Web Page` record's native tabs (`javascript`, `css`, `context_script`, `header`), NOT into a custom Web Template or a custom controller. Custom Web Templates are reserved for layouts that genuinely need cross-page reuse.

**Reasoning:** GL surfaced this 2026-04-26 after noticing that the previous instance's homepage Web Page record (`/app/web-page/locally-twisted`) used only `main_section` (Rich Text) and ignored the Script + Style + Page Builder tabs. Reading the actual `Web Page` DocType schema confirmed the framework natively provides:
- `javascript` (Code field) — per-page JavaScript at page load
- `css` (Code field) + `insert_style` (Check) — per-page CSS
- `page_blocks` (Table) — Page Builder for layout
- `header` (HTML editor) — custom hero HTML
- `context_script` (Code, Python) — server-side data fetching that injects into the Jinja context BEFORE render
- Plus full meta-tag, breadcrumb, and sidebar control

**Concrete impact on this project:**
- The pricing calculator on the BTFP service page was classified as the only tier-4 piece in Phase 1 (per the v2 website-page-index.md). It now collapses to tier 1: Page Builder for static layout + `javascript` field for math + `css` field for styling. No custom Web Template, no hooks, no app code.
- Phase 1 may have **zero tier-4 pieces**. Color swatches are the only remaining candidate, and even that may be reachable via `context_script` + a custom field on `Item Attribute Value`.
- Future page builds (landing, BTFP, contact) all use the right tabs from the start. The previous instance's content-field-only pattern is a documented anti-pattern.

**Alternatives considered:**
- Custom Web Template per interactive page (rejected — strictly worse than using the DocType's native fields; more files, more breakage surfaces, no benefit).
- Per-page `<script>` tags injected into `main_section_html` (rejected — works but harder to maintain than the dedicated `javascript` field; loses the structural separation Frappe provides).
- Custom controller per page (rejected — `context_script` does this natively without registering a controller).

**Generalizable to agency tier:** This decision motivated promoting "System-native first" to a standing principle at the top of `Built_by_Cameron/.claude/capabilities/recipes/frappe-conventions.md`, with a concrete rule: "before writing custom code, read the relevant DocType's full schema." Every BBC client benefits.

**Decided by:** GL directive 2026-04-26 ("you can use java on these pages!") + framework verification by reading the Web Page DocType schema.

---

## 2026-04-26 (webshop install + framework study) — Webshop installed durably; "work within Frappe" is the standing principle

**Decision:** Three reinforcing decisions taken in one session.

1. **`frappe/webshop` and `frappe/payments` are installed on the LT site as durable infrastructure** — bind-mounted in `pwd.yml` into all 8 frappe-image services, gitignored at the project level (the install script is the source-of-truth for HOW we installed them, not the upstream code itself). Reproducible via `python scripts/setup/install_webshop.py`. Phase 1 Slices 7-9 (products + cart + checkout) and Phase 4 (payments) are unblocked.

2. **"Work within Frappe, don't fight it" is the standing principle for all UI/template work.** GL directive 2026-04-26: *"I don't want to fight Frappe or ERPNext and their code. I want to work within it."* Operationalized as: use Jinja partial overrides (templates/includes/...) as the primary surface for header/footer/page customization; use `web_include_css` (loads after the bundle) or `website_theme_scss` (compiles into the bundle) for theme CSS; refuse `!important` chains as the receipt of fighting the framework; use Webshop's existing hooks for cart/checkout customization rather than replacing the cart pipeline.

3. **The `.web-footer` height "constraint" was never a framework constraint.** Reading `apps/frappe/frappe/public/scss/website/footer.scss` in the running container confirmed there is no `max-height` rule. The previous instance's observation came from `lt-theme.css`'s own `!important` chain interacting with the body's flex-column sticky-footer pattern. The `.web-footer` block in `lt-theme.css` (lines 477-503) and the related `.web-footer ul/li/footer-group` blocks (505-526) should be removed before the Slice 2 redo. Documented in `lessons-learned.md` 2026-04-26 entry (RESOLVED) + agency `frappe-conventions.md` "Verified against source" appendix.

**Reasoning:** Webshop install was already a known requirement (per the prior Slice 2 build session's queue + the agency capability). The install proved: (a) `bench get-app` requires `--skip-assets` to avoid the Node-not-in-image error; (b) `payments` is a hard `webshop` dependency missed in the original conventions doc; (c) `apps/` is NOT shared across frappe-image services in pwd.yml — each service needs its own bind-mount + editable pip install. All three discoveries are now in the agency conventions doc.

The "work within Frappe" principle locks in what the previous Slice 2 attempt failed to do. It is non-negotiable going forward — the band-aid pattern doubles trust damage by inheriting brittle code into the next session.

The `.web-footer` resolution unblocks the Slice 2 redo: the next instance can override the Jinja partial with their own structure (any class names, no inheritance from `.web-footer`'s SCSS) without needing to chase a phantom framework bug.

**Alternatives considered:**
- Skip webshop, run an external storefront (rejected — destroys the value of an integrated ERPNext build).
- Bake webshop into a custom Docker image instead of bind-mounting (deferred to Phase 6 Frappe Cloud cutover work — bind-mount is consistent with the existing `locally_twisted` pattern).
- Keep the `.web-footer` `!important` chains "just in case" (rejected — they actively interfere with the redo).

**Decided by:** GL directive 2026-04-26 ("we want the workshop", "I don't want to fight Frappe or ERPNext and their code. I want to work within it") + framework verification by current session.

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
