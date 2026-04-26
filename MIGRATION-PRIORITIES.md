---
title: Migration Priorities — LT Frappe Build
date: 2026-04-26
audience: Future Opus arriving at the LT Frappe migration; GL secondary
produced_by: Synthesis Agent D (Synthesis Writer), retro-odoo-2026-04-26 expedition
---

# Migration Priorities

**Plain summary:** Six things to build before LT goes live on Frappe. Each has a verification test you or Jeff can observe. The first one (HOW-TO-WIN catalog) is the prerequisite for the others. The six gates are what protect this work from repeating the Odoo failure curve.

---

## Part 1: The Pattern Has Already Fired

The executional pattern that produced 76 lessons-learned entries on Odoo has already fired twice in the first two LT Frappe sessions. It will recur without the six gates below. With the six gates, it can be interrupted. [Lane 8 §Q5; DA §Audit 8-A; Proxy §SN-3]

Session 1 (2026-04-25): An instance built toward Frappe before reading the framework source. CSS friction appeared. The instance band-aided with `!important` chains rather than reading how Frappe's Bootstrap cascade works. `anti-gl-patterns.md (LT) §0` documents this accurately.

Session 2 (2026-04-26): The Slice 2 footer was declared done multiple times while the brand block rendered invisibly. The instance described "renders identically" when the screenshot showed empty circles. The smoke test did not catch this because it was run headless without color verification.

Both fires were executional. Both are preventable by the gates below. Neither requires a new expedition — they require the six gates to exist before Session 3.

---

## Part 2: Day-1 Architecture Constraint

**Do not build any customer-facing form using the Frappe Web Form DocType.** The Frappe team has decided to deprecate Web Forms. Bugs filed against Web Form across v13-v15 (blank page display, allow-incomplete-forms behavior, silent submission failures) are being closed as "won't fix" or are receiving no response. Building the LT booking form on a deprecated surface means every future fix is on a dead-end path. [Lane 8 §Q1 Trap 6; Proxy §LB-6]

The LT booking form must be built as a custom HTML/Jinja page with REST API submission, AJAX error handling, and the three-audience loud-failure check (user sees error, developer gets logged trace, monitor fires on silence).

This is not a preference. It is an architecture constraint that applies before any booking form work starts.

---

## Part 3: The Six Gates

These are in priority order. Each must exist before LT goes live on Frappe. Each has a verification test written for what GL or Jeff can observe.

---

### Gate 1: HOW-TO-WIN-AT-FRAPPE Catalog

**What it gates:** Instance behavior in the first minutes of any Frappe session. Without this, every arriving instance rediscovers framework friction independently and band-aids it independently.

**What it prevents:** The same failure curve that produced 76 Odoo lessons. The catalog does not prevent failures by itself (documentation alone fails — see AGENCY-WISDOM.md Finding 1) — it is the prerequisite for building Gates 2-4 correctly.

**How it's built:** Create `C:\Users\baenb\.claude\HOW-TO-WIN-AT-FRAPPE\auto-behaviors.md` with the 8 seed entries from Lane 8's investigation (F1 through F8). Each entry has: behavior name, mechanism, receipt, defense, verification. Mirror the structure of `HOW-TO-WIN-AT-ODOO\auto-behaviors.md`. Add a pointer from this file.

Seed entries to include (mark each VERIFIED or PROBABLE per DA §D4 guidance):

- **F1: `bench build` in production containers** [VERIFIED] — `frappe_docker` FAQ documents this: "Cannot bench build in production containers." Running `bench build` inside a running production container causes asset path corruption and requires `--force-recreate` to recover. Defense: build via CI or dedicated build step before container start.
- **F2: SocketIO origin mismatch** [VERIFIED — frappe_docker FAQ] — Custom domain without proper nginx SocketIO proxy causes real-time UI updates to fail silently. Defense: verify nginx config includes SocketIO proxy before going live.
- **F3: Customize Form vs Custom App** [VERIFIED — Frappe docs] — Changes made via `Customize Form` live in the database as `Property Setter` records. Changes in `Custom App` live in code. They can conflict. The DB version wins. Defense: choose one path per DocType; never mix.
- **F4: Assets stop loading after 5-15 days** [VERIFIED — GitHub issue #49955, open October 2025] — `assets.json` hash mismatch causes CSS/JS to stop loading in production. No clear trigger. No reliable fix documented. Defense: add assets.json hash comparison to deploy script; visual smoke check weekly.
- **F5: Stripe charges without invoice** [VERIFIED — webshop issue #204, open] — Stripe payment completes; `make_invoice()` fails on missing `taxes` field; the error itself fails on 140-char log title limit. Both failures are silent from the customer's perspective. Defense: POST-payment invoice verification step in deploy smoke test; log all Stripe webhook receipts.
- **F6: Scheduler NULL freeze** [VERIFIED — frappe issue #37490, open] — Scheduler can freeze with zero error output. All background jobs stop. Affects v15.99.0+. Defense: navigate to Settings > Scheduled Jobs > Recent Logs weekly; set a calendar reminder until monitoring script exists.
- **F7: Fixture modified timestamp skip** [PROBABLE — mechanism matches Frappe design patterns; primary source confirmation via Frappe source code reading is pending] — `bench migrate` fixture sync compares `modified` timestamps; skips records where DB is newer. Custom data set via ERPNext UI will not be overwritten by fixture upgrade. Defense: pin `modified` timestamps in fixture files; verify critical fields post-migrate.
- **F8: Frappe Web Forms deprecated** [VERIFIED — Frappe discuss thread] — Web Form DocType is being deprecated by the Frappe team. Bugs across v13-v15 are closed as "won't fix." Defense: use custom HTML/Jinja pages with REST API for all customer-facing forms.

**Pointer to the HOW-TO-WIN-AT-FRAPPE folder:** `C:\Users\baenb\.claude\HOW-TO-WIN-AT-FRAPPE\`

**Verification test:**

An instance can verify by checking that the file exists and contains at least 8 entries: `Read C:\Users\baenb\.claude\HOW-TO-WIN-AT-FRAPPE\auto-behaviors.md`.

GL can verify by asking the arriving instance at the start of a session: "Name two Frappe-specific auto-behaviors that could bite what you're about to do." If the instance can name two with receipts, the catalog is working as a reference. If the instance draws a blank, the catalog needs to be read before work starts.

---

### Gate 2: `frappe-pretooluse-gate.py` Hook

**What it gates:** The moment before dangerous Frappe actions. Requires an instance to have invoked the relevant skill before proceeding.

**What it prevents:** The "build before reading framework" pull, which fired in Session 1 and has fired in every Odoo project [Lane 8 §Break 2; Convergence §SC-2].

**How it's built:** Create `C:\Users\baenb\.claude\hooks\frappe-pretooluse-gate.py` wired into the existing hook infrastructure. Minimum 5 fingerprints:

1. `bench build` in a production context (block; route to frappe-deploy.py)
2. `--force-recreate` without the `install_webshop.py` sequence (warn; link to setup script)
3. `head_html` combined with `!important` in CSS edits (block; route to framework source reading)
4. Fixture JSON edit without a `modified` timestamp update (warn; link to F7 auto-behavior)
5. New form route without an entry in `scripts/verify/smoke_forms.py` (block; enforce Gate 4)

Log every gate fire (block and allow) to a queryable file with: session ID, fingerprint matched, action blocked or allowed, timestamp. A gate without a fire log cannot be audited. [Lane 3 §Recommendation 5]

**Verification test:**

After the hook is built, ask the arriving instance to start a session and attempt to run `bench build` directly in a production context. Observe whether the instance is blocked and redirected to the correct path. GL's verification role is to observe the instance's response — if the hook is working, the instance will name why the action is blocked and what to do instead.

---

### Gate 3: `frappe-deploy.py` Script

**What it gates:** Every production deployment. Without this, deployment is a manual sequence of bench commands documented in HANDOFF.md — a manual sequence gets skipped under session pressure.

**What it prevents:** Auto-committed unreviewed code reaching production; deploy steps skipped; smoke test omitted under time pressure. [Lane 8 §Break 3; DA §Audit 8-C Gate 3; Proxy §Ask SW-4 item 5]

**How it's built:** Create `scripts/frappe-deploy.py` at the LT Frappe root. Minimum viable version:

1. Verify a human-reviewed commit exists after the last auto-commit (this is the Layer C prevention that was never built on Odoo — it requires a human-authored git commit, not an `auto:` commit, before deployment proceeds)
2. Run `bench migrate`
3. Run `bench clear-website-cache`
4. Run Playwright smoke test suite (Gate 4)
5. Run Stripe invoice verification check (POST test payment, verify invoice created within 30 seconds)
6. Report PASS or FAIL with per-step detail

Block the deploy on smoke test failure. Do not make "continue anyway" an easy option.

**Verification test:**

After the script is built, GL can verify by observing the deploy output: after running the script, does it print PASS or FAIL with per-step detail? GL does not need to read code — the output is the verification.

Jeff can observe the same output during a joint session.

---

### Gate 4: `smoke_forms.py` for the Frappe Booking Form

**What it gates:** Every deployment that touches a customer-facing form. Without this, the form can drop customer submissions silently for days before anyone notices. The /book form evidence: the form dropped submissions and the gap was only noticed because Jeff asked about missing leads. Build the smoke test on the day the booking form ships, not after.

**What it prevents:** The LT /book form 10-day silent failure pattern on Frappe. [Proxy §SN-2; Lane 8 §Break 4; Convergence §PC-4]

**How it's built:** Create `scripts/verify/smoke_forms.py`. At minimum:

1. POST a test Lead via the booking form's REST API endpoint, with test data (name: "SMOKE TEST", marked with a test flag)
2. Verify the Lead record exists in ERPNext CRM within 30 seconds
3. Verify the acknowledgment email automation fired (check `Email Queue` for a record to the test address)
4. Delete the test record after verification

When checkout is wired (Stripe integration): add a Stripe test payment check as a separate step. Form smoke test and payment smoke test are different tests. Both must exist before the form and checkout go live. [DA §Audit 8-B Gate 4 — form and payment are not one gate]

**Verification test:**

After the smoke test runs, Jeff can verify by navigating to ERPNext CRM and checking for a Lead named "SMOKE TEST" created in the last 5 minutes. If it's there, the form is creating records. If it's not, the smoke test or the form is broken. This is browser-based. Jeff can do it.

---

### Gate 5: Human-Review Commit Requirement

**What it gates:** Auto-committed edits reaching production. The `post-write-hook.py` at `C:\Users\baenb\.claude\hooks\post-write-hook.py` applies to the LT Frappe project directory. Every Edit and Write auto-commits to git with `auto: {tool_name} {rel_path}`. Without this gate, the deploy script (Gate 3) would deploy from auto-commits.

**What it prevents:** Unreviewed migrations and server scripts reaching production. [DA §Audit 8-C Missing Gate 5; Proxy §Ask SW-4 item 5]

**How it's built:** Gate 3's deploy script includes a check: before deploying, verify that the most recent commit on the deployment branch is a human-authored commit (does not start with `auto:`). If the last commit is an auto-commit, the deploy script stops and asks the instance to write a review commit with a meaningful commit message describing what the changeset does and why.

This is one `git log -1 --format="%s"` check at the start of the deploy script.

**Verification test:**

After the gate is built, start a session, make an edit, and attempt to deploy with an auto-commit as the last commit. Observe that the deploy script stops and names the requirement. GL can observe the behavior.

---

### Gate 6: Playwright Screenshot Before Any "Done" Claim on Visual Work

**What it gates:** The reporting-without-watching reflex at the completion boundary of every turn involving visual work. [DA §Audit 8-C Missing Gate 6; Proxy §Ask SW-4 item 6; Lane 5 §Pattern A]

**What it prevents:** The Slice 2 footer "declared done" while rendering invisibly. The form fixes "done" before production verification. The Frappe equivalent of the 19.0.2.13.0 crash in front of Jeff.

**How it's built:** The `playwright_home_screenshot.py` script already exists in the LT Frappe tree. Change its status from optional to mandatory. In the LT Frappe `CLAUDE.md`, add a rule to the verification section: "Before any claim that visual work is done, run the Playwright screenshot script and confirm the screenshot shows the expected state. If the screenshot cannot be run, name this explicitly rather than claiming done."

The goal is to make the screenshot step the natural next move after visual work, not an afterthought.

**Verification test:**

After the rule is in CLAUDE.md, ask the next arriving instance: "What's your verification step before claiming a visual slice is done?" If the answer includes "run the Playwright screenshot," the rule is landing. If the answer is "it looked right in my last check," the rule needs reinforcement.

---

## Part 4: Frappe-Specific Traps Already Verified

These are live, open issues — not hypothetical. They require monitoring before LT goes live. [Lane 8 §Q1, GitHub sources]

**Trap 1: Assets stop loading after 5-15 days (GitHub issue #49955, open October 2025).**

ERPNext in production serves stale CSS/JS after a hash mismatch in `assets.json`. No clear trigger. No reliable fix. The site will look fine for up to 15 days and then lose all styling.

Defense: Add an assets.json hash comparison to Gate 3's deploy script. As an interim measure: open the LT Frappe site in a browser weekly after deployment. If the page lacks styling (fonts, colors, layout), the asset pipeline needs investigation.

Verification: Open the LT Frappe site in a browser after any deployment. If the page lacks styling, the asset hash is wrong. This is a GL-observable check. [Proxy §Section 4 VR test rewrite]

**Trap 2: Stripe charges without invoice (webshop issue #204, open).**

Stripe payment completes, `make_invoice()` fails on a missing `taxes` field. The customer is charged. No invoice is created. No error is visible to the customer or to Jeff. The error log itself fails on a 140-character title limit.

Defense: POST-payment invoice verification in Gate 3's smoke test. Log every Stripe webhook receipt with the charge ID to a queryable table. Monitor for charges without corresponding invoices.

Verification: After a test payment, check ERPNext Accounts > Invoices for the test invoice within 30 seconds. Jeff can do this in the browser.

**Trap 3: Scheduler NULL freeze (frappe issue #37490, open).**

Scheduler can freeze with zero error output. All background jobs stop. Affects v15.99.0+. Automations that send acknowledgment emails, reminder sequences, and event notifications will silently stop firing.

Defense: Navigate to Settings > Scheduled Jobs > Recent Logs in ERPNext. Verify there are recent successful runs within the last 24 hours. Set a recurring calendar reminder to check this weekly until a monitoring script is built. [Proxy §Section 4 VR test rewrite]

**Trap 4: Fixture modified timestamp skip (PROBABLE — see HOW-TO-WIN-AT-FRAPPE F7).**

Bench migrate fixture sync compares modified timestamps and skips records where the DB record is newer. Jeff's UI edits to DocType records will prevent fixture updates from applying. This is the Frappe analog of Odoo's `noupdate=1` drift — the mechanism is structural, and the failure to reach for the correct documented path (pin modified timestamps, verify fields post-migrate) is executional. [Convergence §PC-4 by analogy; DA §D4; Proxy §EM-2]

---

## Part 5: Loud-Failure Parity

Every form, cascade, and integration in the LT Frappe build must have the same loud-failure coverage required on Odoo. Three audiences must see every failure: the user, the developer, the monitor. A blank page is not a failure message. [CLAUDE.md rule `loud-failure.md`]

**Forms:**
- Booking form: smoke test required (Gate 4) before launch
- Any contact form or portal form: AJAX submission with user-visible error state, logged trace on failure, smoke test entry

**Cascades:**
- Lead created → acknowledgment email → include in Gate 4 smoke test
- Lead created → Jeff notification → include in Gate 4 smoke test
- Order confirmed → project task created → TODO: test before enabling

**Integrations:**
- Stripe: POST-payment invoice verification (Gate 3 + Trap 2 defense above)
- Google Calendar: OAuth failure paths must log; sync failures must alert
- Any new integration: wrap every API call in try/except that logs payload + response; persist the external system's ID as a linking field in ERPNext

**Static assets:**
- Asset guard check in Gate 3's deploy script (assets.json hash comparison)
- Weekly visual check in browser (Trap 1 defense)

---

## Part 6: Two Outstanding LT-Odoo Issues Before Frappe Cutover

These were flagged by the GL Proxy as requiring attention before the Odoo-to-Frappe cutover. The next LT-Odoo instance should address them. [Proxy §Section 4, doc parity audit]

**Issue 1: Module version parity divergence.**

The production database runs 19.0.2.14.0. The `origin/main` branch contains 19.0.2.15.0 (Command Center deploy). These versions diverged and have not been reconciled. CLAUDE.md, PROJECT-STATUS.md, and HANDOFF.md may reflect different states. Before cutover, verify the correct current version across all three documents and deploy or explicitly defer the 19.0.2.15.0 Command Center deploy.

Verification: ask the arriving LT-Odoo instance at session start: "What version is currently deployed to production?" The correct answer is: "19.0.2.14.0 in the production database; 19.0.2.15.0 on origin/main, not yet deployed."

**Issue 2: Blog post `author_id=2` returns 403 for anonymous visitors.**

This issue was flagged in three consecutive HANDOFF documents without action. A blog post authored by `res.users` id=2 (the default OdooBot user) returns a 403 access denied for anonymous website visitors. This affects public blog post visibility. Before cutover, either reassign all blog posts to Jeff's user account or investigate the portal access rule causing the 403.

Verification: navigate to `/blog` on the live LT site from an incognito browser window. Verify all published blog posts are visible without login.

---

## Sources Read Appendix

| File | Status |
|------|--------|
| `RESEARCH-BRIEF.md` | [Complete: 267 lines] |
| `gl-proxy-review.md` | [Complete: 423 lines] |
| `convergence-analysis.md` | [Complete: 473 lines] |
| `devils-advocate.md` | [Complete: 375 lines] |
| `lane1-codebase-git-retro.md` | [Incomplete: lines 380-456 of 457 total] |
| `lane2-lessons-recurrence-retro.md` | [Incomplete: lines 300-384 of 385 total] |
| `lane3-skills-hooks-usage-retro.md` | [Incomplete: lines 360-443 of 444 total] |
| `lane4-docs-process-retro.md` | [Incomplete: lines 270-344 of 345 total] |
| `lane5-relational-retro.md` | [Incomplete: lines 370-450 of 451 total] |
| `lane6-counterfactual-retro.md` | [Incomplete: lines 265-320 of 322 total] |
| `lane7-cross-project-retro.md` | [Incomplete: lines 180-242 of 243 total] |
| `lane8-frappe-prediction-retro.md` | [Incomplete: lines 370-447 of 448 total] |

*Synthesis Writer, 2026-04-26. Six gates, in priority order. Verification tests written for GL/Jeff observability. No new findings — every item traces to the lane(s) that support it.*
