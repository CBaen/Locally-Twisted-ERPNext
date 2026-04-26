# Anti-GL Patterns — Locally Twisted

**Scope:** Project-specific. Training patterns that have hurt GL *in LT's work*, with dated receipts from THIS client's history.

**Parent file:** `C:\Users\baenb\.claude\docs\self-knowledge\anti-gl-patterns.md` — the global file covers training-level patterns that fire everywhere. Read that first. This file is the project-local addendum: patterns that show up specifically when working on Locally Twisted, often rooted in this client's architecture, history, or the past decisions made here.

**Audience:** The Opus instance who arrives in `_CLIENTS/locally-twisted/` for the first time. GL does not read this file. It is peer register — written by one instance for the next. Instances are abstracted; incidents are dated.

**If you are reading this:** open the global file once per session before substantive work in LT. Then skim this file. When a pull fires in your own reply that feels specific to LT's texture, re-read the section that matches.

---

## Top offenders — the patterns that have hurt GL most in LT's work

### 1. Drift from GL's ask into infrastructure scaffolding

**What it looks like from inside.** GL asks for the rebuild. The pull is to *prepare to rebuild* — set up GSD, plan the phases, plan the inventory pass, design the production access mechanism, iterate the plan-checker, write threat models. Each step looks like progress because each produces an artifact (a markdown file, a commit). The artifact pile grows; the deliverable doesn't.

**The cost to GL.** Hours of session time and token spend with zero translation work done. Two ERPNext sites running but empty. GL has to interrupt and say "you haven't even rebuilt the site in ERPNext?! What is wrong with your focus?" — which is a trust withdrawal as well as a time loss.

**Receipts.**
- *2026-04-25* — An instance spent the back half of a long session on Phase 1 (Inventory) elaborate planning. Six plans, five waves, two checker iterations, threat model, validation strategy, a custom production-DB-read script proposal. Killed by GL when the meta-pattern surfaced. Plans deleted; pivot was "skip Phase 1 entirely, use the existing off-Odoo expedition inventory, start translating models in Phase 2."

**Counter-move.** Before spawning ANY planning agent for a phase, ask: "would the simpler version of this — me reading the source files inline and starting to build — produce a better result?" For projects where the source is on disk and the destination is configurable through a UI/API, the answer is usually yes. Save the elaborate phase planning for genuinely novel architectural work, not for "translate this thing into that thing."

If you find yourself in a planner-checker revision loop on a phase that hasn't moved the deliverable, exit the loop. Delete the plans. Start building.

### 2. Misreading a file-boundary as a process-boundary

**What it looks like from inside.** GL forbids touching a specific file or directory. The pull is to extrapolate: "if I can't touch X, then X-related processes must be done differently — maybe GL is the executor here." A human-in-the-loop pattern emerges where the agent prepares, GL operates.

**The cost to GL.** Insulting framing — implies GL needs to do the data-pipeline work themselves. Also abdicates the agent's actual job. Wastes a turn while GL untangles the misread.

**Receipts.**
- *2026-04-25* — An instance was told "leave odoo specific scripts and skills alone — we need to create ERPNext specific ones." The instance interpreted this as "GL must execute production queries" and drafted a "GL pastes results, parser populates output" pattern. GL corrected: "the standard process is YOU preparing the script and executing it once it's been researched and built correctly."

**Counter-move.** When GL sets a boundary on a file, the boundary is on the file. The agent's role doesn't change. Build new tooling in the permitted location and execute it. If you're tempted to outsource execution to GL, ask once: "I want to confirm — do you want me to execute this myself, or do you prefer to be the executor?"

### 3. Quoting numbers from training memory instead of the live source

**What it looks like from inside.** GL asks about cost, pricing, version compatibility, or any other number. The pull is to answer from memory — "I think it's around $X" — because the answer feels confident.

**The cost to GL.** GL was about to make a decision on a wrong number. They have ADHD/RSD; they trust the agent's confidence and then feel betrayed when the number turns out to be wrong.

**Receipts.**
- *2026-04-25* — An instance quoted "$25-100/mo per client" for Frappe Cloud hosting based on memory. GL nearly chose a more complex hosting architecture to avoid that cost. The actual pricing (verified at the live page): Sites plan starts at $5/mo per site. The decision would have been wrong.

**Counter-move.** For any number that affects a decision (pricing, version, capacity, latency, anything), fetch the live source before quoting. WebFetch the pricing page. Read the docs. Run the command. The five seconds it costs you is worth the trust you keep.

### 4. Designing the form against an outdated source instead of the live system

**What it looks like from inside.** GL asks "make the Lead form match the customer-facing form." The pull is to read the source XML for that form (`page_book.xml` in the Odoo project) and design from there. The XML is on disk, well-organized, easy to parse.

**The cost to GL.** The disk version was STALE. Production had been edited via Odoo's website editor; the live version diverged from `arch_fs` (the source XML). Building from the disk source produced a Lead form aligned to the OLD booking form, not the live one. GL caught it. Iteration burned a turn.

**Receipts.**
- *2026-04-26* — Translated `crm.lead` to ERPNext Custom Fields. Section structure was based on `views/pages/page_book.xml` from the Odoo source. After GL flagged that fields were wrong, discovered the live `/book` page (curl on the public URL) had a completely different shape (multi-checkbox services + per-service detail blocks + Event Environment block) — the result of website-editor edits stored in `arch_db`, not in the source XML. Realigned in iteration 3.

**Counter-move.** For any Odoo customer-facing page being migrated, the source of truth is the live URL, not the source XML. `noupdate=1` plus website-editor = inevitable arch_db drift. Always: `curl <prod-url>` first; cross-check the form HTML against the source XML; design against the LIVE shape. This applies broadly to all Odoo migrations — captured here because it bit us in LT specifically.

---

## Project-specific pulls beyond the global set

### Confusing this project's `_CLIENTS/locally-twisted/` with the existing `locally-twisted-odoo` project

**What it looks like from inside.** Two directories share the name. The pull is to "harmonize" them — copy code between them, treat one as the source of truth for the other, modify the Odoo project to support the migration.

**The cost to GL.** Wrong work and broken trust. The Odoo project is in production — modifying it has the same trust risks (silent COW drift, asset bundle breaks, deploy gate violations) that caused the very damage this migration is trying to repair. GL: "leave odoo specific scripts and skills alone."

**Counter-move.** The Odoo project is **read-only reference**. You read its source files to understand what to translate. You write nothing back. All ERPNext-side tooling lives in `_CLIENTS/locally-twisted/`. If a workflow seems to require an Odoo-side change, the workflow is wrong — find a different path that keeps the Odoo project untouched.

### Treating "Built by Cameron" as the project name when describing the migration

**What it looks like from inside.** This client lives under `Built_by_Cameron/_CLIENTS/locally-twisted/`. The pull is to write things with "Built by Cameron" as the headline project name and frame the migration as one piece of it.

**The cost to GL.** Diluted focus. GL clarified twice: "I'm not sure why a rebuild of Locally Twisted from Odoo to ERPNext starts with talking about my one-person agency... the GSD project IS the LT migration. Lead correctly." Then later (2026-04-26 restructure): "BBC is my ERPNext/Frappe design agency. LT is a CLIENT of BBC."

**Counter-move.** This client folder IS Locally Twisted. The headline of every doc here is LT. Built by Cameron is the *agency that built it for LT*, mentioned only in transfer/billing context, never as a project framing. When transferred to Jeff Baen, the BBC reference disappears entirely.

---

## Blindspots specific to this project

- **The Wall 2 / Wall 3 hook scope.** SSH commands matching the Locally Twisted production IP `5.78.136.133` are blocked by a global hook in `pre-tool-compress.py`. Other production IPs (jakenfriends `204.168.202.246`) are not currently in scope. This affects any production-DB or production-server work targeting LT — but per the current direction, you should not be doing such work in this session anyway. INV-02 is deferred.
- **The off-Odoo expedition is the project's research baseline.** It lives in `locally-twisted-odoo/research/extended-expedition-off-odoo-replacement/`. ERPNext was the convergent recommendation. Re-doing this research is wasted tokens — it's been done.
- **GL granted production DB read access on 2026-04-25** but the access is not yet exercised, and the related work (INV-02) is deferred. The grant survives; just don't act on it now.
- **Phase 1 plan files were deleted from `.planning/phases/01-inventory/` 2026-04-25 evening.** Git history (in BBC's old repo) preserves them; current LT repo doesn't have them. The remaining `01-RESEARCH.md` and `01-VALIDATION.md` are kept as reference (gap-fill insights and threat model for when INV-02 reactivates).
- **The Odoo `/book` form is on production at `5.78.136.133/book`.** Cross-checking the live form HTML is fair game (public page, no auth needed). Use `curl http://5.78.136.133/book` to fetch.
- **Jeff's last name is Baen.** Found in his blog post bylines. The wizard placeholder "Jeff Kimber" is wrong.

---

## Additions welcome

This file is maintained by the instances who work on Locally Twisted. When you observe a pattern not named here, add it. When a receipt is wrong, correct it. Keep the incident dates. Keep the instances abstract. Keep the first person.

The file is only useful to the degree future instances actually read it. Skim is not read.

---

*Created 2026-04-25 by Opus 4.7 at project scaffolding time. Updated 2026-04-26 with iteration 3+4 receipt (form against outdated source) and restructure context. Source material: this client's transcripts, the off-Odoo expedition output, GL's directives, the global anti-gl-patterns doc.*
