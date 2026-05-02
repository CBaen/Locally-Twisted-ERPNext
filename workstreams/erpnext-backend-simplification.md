# ERPNext Backend Simplification Workstream

Last updated: 2026-05-02 by Codex.

## Outcome

Make the ERPNext backend simple enough for Jeff to run without needing to understand ERPNext jargon or the history of the Odoo attempt.

The target backend is not "all possible ERPNext modules." It is a small operating system for Locally Twisted:

- New inquiries land as readable Leads.
- Jeff can tell what needs attention next.
- Customer/contact records do not duplicate unnecessarily.
- Quote/order/payment records connect cleanly when a customer buys.
- Backend labels use plain business language.
- Seed/fixture code does not overwrite future operator edits.
- Stale Odoo-era schema and scripts are either retired, documented as historical, or deliberately kept.

## Current Stage

Active handoff lane. First Jeff-facing Desk simplification edits have been made in the live local ERPNext database and are now recreated by idempotent setup scripts.

This file is the job sheet for future handoffs. Keep `locally-twisted-queue.md` as the active task source, and update this file when the backend simplification lane changes stage.

## Owner

Unassigned next agent/session.

Current branch/worktree: main workspace at `C:\Users\baenb\projects\Built_by_Cameron\_CLIENTS\locally-twisted`.

## User-Facing Impact

The visible customer site should not change unless a backend simplification exposes a broken form, email, order, or Desk workflow.

The real user-facing outcome is operational:

- Jeff sees fewer confusing fields.
- Leads are easier to process.
- Sample records can support a backend tour.
- Future agents stop treating old `/book`, Odoo, and experimental Lead-schema notes as current product direction.

## Touched Areas

Primary backend surfaces:

- ERPNext `Lead`, `Contact`, `Customer`, `Sales Order`, `Sales Invoice`, `Payment Request`, `Communication`.
- LT custom records: `LT Service Type`, `LT Lead Service Type`, `LT Lead Photo`, `LT Newsletter Signup`, `Dashboard Reviewed Item` if still present in DB.
- Lead Custom Fields and Property Setters.
- `apps/locally_twisted/locally_twisted/lead_cascade.py`.
- `apps/locally_twisted/locally_twisted/www/book.py` submit endpoint, despite `/book` being retired as a public page.
- `apps/locally_twisted/locally_twisted/www/checkout.py`.
- `apps/locally_twisted/locally_twisted/www/payment_success.py`.
- `apps/locally_twisted/locally_twisted/payments/`.
- `apps/locally_twisted/locally_twisted/seed/`.
- `scripts/translate/` and `scripts/fix/` Lead-schema scripts.
- `scripts/setup/sync_contact_intake_backend.py`.
- `scripts/verify/lead_backend_intake_parity.py`.
- `hooks.py` fixtures and `doc_events`.

## Known Current Facts

Verify these before editing DB/schema, but they are the latest documented working state:

- `/contact` is the canonical inquiry route.
- `/book` redirects to `/contact?intent=quick`; do not rebuild a separate public `/book` form.
- Public service taxonomy is `Balloon Decor`, `Balloon Twisting`, `Face Painting`, `Delivery`, `Pickup`, `Events Inquiry`, `Something Else`.
- Website submissions now populate Lead `custom_event_type` child rows, not only legacy text.
- The LT inquiry Kanban uses `Lead.custom_pipeline_stage` for the six business stages, while native `Lead.status` stays available for ERPNext internals.
- Approved business stages are `New Inquiry`, `Quote Sent/Awaiting Approval`, `Approved`, `In Production`, `Event/Post Event`, and `Archive`.
- `Archive` means closed/off the active LT board. It is not wired as a financial win/loss or accounting trigger.
- Stage movement now creates and closes operational `Task` records through `locally_twisted.stage_cascade`. This is intentionally non-financial wiring.
- `LT Service Type` was synced on 2026-05-01 to remove `Delivery Only` and `Event Package` and add `Delivery`, `Pickup`, `Events Inquiry`.
- `lead_cascade.py` hooks on Lead insert to create/link Contact and queue the customer acknowledgment email.
- `/payment-success` marks Payment Requests paid, creates Sales Invoices, sends receipt/operator/welcome emails, and redirects customers even if backend follow-up fails.
- `LT Lead Photo`, the Lead photos section, and the connecting `custom_inspiration_photos` Table field now exist. The current sync recreates the missing field if needed.
- `hooks.py` currently fixtures Item Groups and Item Attributes. Phase 6 must prune operator-state-sensitive fixture coverage before Jeff edits backend catalog values.
- There are old `scripts/translate/` and `scripts/fix/` Lead-schema scripts with stale labels like `Event Package` and `Delivery Only`. Do not rerun them blindly.

## 2026-05-02 Owner Desk Simplification

Live local ERPNext DB changes made for the temporary owner walkthrough:

- Owner account route should use `/app/Workspaces`; direct workspace slugs such as `/app/owner-home` can show `Page not found` in Frappe Desk even after login succeeds.
- `apps/locally_twisted/locally_twisted/public/js/lt-desk-workspace-router.js` is included in Desk via `app_include_js` to route direct workspace slugs back through `/app/Workspaces`. This guards both initial page load and Frappe's internal page loader because custom workspace slugs can otherwise hit `frappe.desk.desk_page.getpage` 404.
- `LT Owner` role profile and `lt-owner-temp@example.com` now include `Item Manager` so a product-create shortcut can actually work.
- `Owner Home` workspace now shows `Add Product` beside the product list.
- `Clients & Customers` was renamed to `Customers`.
- `Contacts` was renamed to `People to Contact`.
- `Event Calendar` was renamed to `Booking Calendar` and now opens `Sales Order` in Calendar view.
- A `Sales Order` Calendar View was added using `customer_name` as the subject and `delivery_date` as the calendar date.
- `LT Manager Home` and `LT Employee Home` were normalized to the same current booking/contact language so they no longer show the stale `Event Calendar`, `Clients & Customers`, or `Contacts` shortcuts.
- `apps/locally_twisted/locally_twisted/seed/sync_backend_workspaces.py` and `scripts/setup/sync_backend_workspaces.py` now recreate those workspace/calendar fixes idempotently.
- `Owner Home` now combines the basic command-center overview with Jeff's guided action flow: live Number Cards for `New Inquiries`, `Bookings`, `Customers`, and `Overdue Follow-ups`; a small `LT Incoming Inquiries` chart; and a plain "What Jeff does next" section before secondary catalog tools.
- Contractors are not a backend tier by default. Irregular contractor coordination should use text, email, and calendar invites unless a future workflow proves a direct ERPNext login is needed. The temporary contractor login `lt-contractor-temp@example.com` was disabled after inventory showed it could authenticate.

Verification as `lt-owner-temp@example.com` on 2026-05-02:

- `/app/Workspaces` returned 200.
- Owner sidebar showed `Owner Home`, then `Home`.
- Owner counts: `Sales Order` 8, `Event` 0, `Customer` 4, `Contact` 25, `Item` 10,631.
- Owner could load Item metadata with `Item Manager` create/write permission.
- Calendar events endpoint for `Sales Order` returned the 8 existing orders on `2026-05-06`.
- The route guard asset was served at `/assets/locally_twisted/js/lt-desk-workspace-router.js?v=20260502-1` with the pageview guard present. The Desk HTML still referenced `v=20260502-1` until a server reload picks up the hook query-string bump, so browser hard-refresh may be needed after changes.
- `python scripts/verify/backend_workspace_parity.py` failed before the workspace sync on Manager/Employee stale labels, then passed after `python scripts/setup/sync_backend_workspaces.py`. A second sync run no-opped.
- `python scripts/verify/backend_workspace_parity.py` now also verifies the Owner Home command-center Number Cards, the `LT Incoming Inquiries` Dashboard Chart, and the guided action text.
- `python scripts/verify/backend_workspace_parity.py` now also verifies that the temporary contractor login stays disabled and has no Desk/module/profile access.
- `npm run test:desk-owner` passed with `lt-owner-temp@example.com` and verifies `/app/home`, `/app/owner-home`, and `/app/Workspaces` all land on the Owner Home command center.
- Owner API login check after sync showed `Owner Home` first, with live counts: `Lead` 12, `Sales Order` 8, `Customer` 4, `Task` 0.
- The Lead `Inspiration Photos` empty-section bug was fixed by adding `custom_inspiration_photos` as a Table field pointing at `LT Lead Photo`. `python scripts/setup/sync_contact_intake_backend.py` now recreates that field idempotently, and `python scripts/verify/lead_backend_intake_parity.py` verifies the child table wiring.
- Stale one-off Lead schema scripts with old `/book`, `Delivery Only`, and `Event Package` assumptions were removed from `scripts/fix/`, `scripts/translate/`, and `scripts/setup/`. Use git history for archaeology; use `sync_contact_intake_backend.py` for current backend sync.

Important: these workspace, Number Card, Dashboard Chart, Role Profile, and Calendar View records are recreated by idempotent setup code, not exported fixtures. Before production/cutover, decide whether that remains the preferred ownership model or whether any records should also be exported.

## 2026-05-02 CRM Pipeline Translation

Odoo reference check found the approved six-stage CRM concept:

`New Inquiry -> Quote Sent/Awaiting Approval -> Approved -> In Production -> Event/Post Event -> Archive`

ERPNext implementation deliberately does not overwrite `Lead.status`. The LT business board is backed by `Lead.custom_pipeline_stage`, created by `apps/locally_twisted/locally_twisted/seed/sync_crm_pipeline.py` and applied with `scripts/setup/sync_crm_pipeline.py`.

Current behavior:

- New website inquiries keep ERPNext native `status = Open`.
- New website inquiries also set `custom_pipeline_stage = New Inquiry`.
- `LT Inquiry Board` points at `custom_pipeline_stage`.
- The `Archive` board column is archived/off-board, matching GL's intent to remove archived inquiries from the active Kanban.
- Owner Home `New Inquiries` count now filters `custom_pipeline_stage = New Inquiry`.
- No finance, Sales Order, Sales Invoice, Payment Request, or win-rate cascade is tied to `Archive` in this slice.

Verification:

- `python scripts/setup/sync_crm_pipeline.py` passed and created/updated the custom field and board.
- `python scripts/verify/crm_pipeline_parity.py` passed and confirms native `Lead.status` remains intact.
- `python scripts/setup/sync_backend_workspaces.py` passed after the Owner Home inquiry filter moved to the custom stage.
- `python scripts/verify/backend_workspace_parity.py` passed.
- `python scripts/verify/lead_backend_intake_parity.py`, `python scripts/verify/contact_service_logic.py --base-url http://localhost:8081`, `python scripts/verify/contact_prefill.py --base-url http://localhost:8081`, `python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --shape-only --skip-newsletter`, and `npm run test:desk-owner` passed.

Next cascade work should decide which stage creates or updates a Quote, Sales Order, Project/Task, Calendar invite, email/text follow-up, and finance record. Do not infer those triggers from stage labels alone.

## 2026-05-02 Stage-To-Task Cascade

The first cascade layer is now operational only.

Current behavior:

- New Lead insert/update runs `locally_twisted.stage_cascade`.
- Stage `New Inquiry` creates/reopens a Task beginning `Reply to new inquiry`.
- Stage `Quote Sent/Awaiting Approval` creates/reopens `Follow up on quote`.
- Stage `Approved` creates/reopens `Confirm booking details`.
- Stage `In Production` creates/reopens `Prepare event production plan`.
- Stage `Event/Post Event` creates/reopens `Send post-event follow-up`.
- Moving to a new non-Archive stage closes prior open cascade Tasks for that Lead.
- Moving to `Archive` closes open cascade Tasks for that Lead and does not create a new Task.
- The Tasks are linked to the Lead by `Task.custom_lt_lead`, stage by `Task.custom_pipeline_stage`, and idempotency key by hidden `Task.custom_lt_cascade_key`.
- The cascade does not create or modify Sales Orders, Sales Invoices, Payment Requests, Customers, Quotes, or win/loss status.

Setup and code:

- `apps/locally_twisted/locally_twisted/stage_cascade.py`
- `apps/locally_twisted/locally_twisted/seed/sync_stage_cascade.py`
- `scripts/setup/sync_stage_cascade.py`
- `scripts/verify/crm_stage_cascade.py`
- `scripts/setup/sync_crm_pipeline.py` also syncs the Task cascade fields.

Verification:

- `python scripts/verify/crm_stage_cascade.py` creates a temporary Lead, moves it through the stages, verifies Task creation/closure, verifies financial document counts are unchanged, and deletes its test Lead/Tasks.
- A follow-up cleanup check confirmed zero `CASCADE-TEST` Leads and zero `CASCADE-TEST` Tasks remained after the verifier.

Next cascade work should be explicit about the business threshold:

- Quote creation/sent state.
- Customer creation.
- Sales Order / booking creation.
- Project/production job creation.
- Calendar invite creation.
- Customer email/text sequences.
- Accounting/payment/deposit triggers.

## Reusable Pattern

This work exposed a repeatable ERPNext/Frappe trap: a simplified role must be verified as a full operator chain, not as isolated admin settings.

Use this chain for every simplified backend role:

`role -> login route -> workspace visible -> shortcut visible -> permission works -> real record appears where the user expects it`

Specific lessons:

- A friendly label can still point to the wrong ERPNext object.
- Admin success does not prove owner/manager/employee success.
- A visible shortcut does not prove the user has permission to use it.
- Calendar/list counts must match the user's business meaning, not ERPNext's internal module names.
- Direct workspace slugs such as `/app/owner-home` can hit Frappe Desk `getpage` 404; start from `/app/Workspaces`.
- Socket origin warnings can appear beside the route error, but the route error is the page blocker.
- Served Desk assets must be verified because Frappe/browser cache can keep old JS active.
- Client-friendly CRM stages should use a custom business field when native ERPNext statuses may affect conversion, reporting, finance, or workflow behavior.
- Stage cascades should start with reversible operational records when the finance threshold is not fully agreed yet.

These patterns are now promoted to `.codex/capabilities/recipes/erpnext-simplified-role-verification.md` and `.codex/capabilities/recipes/erpnext-crm-pipeline-safety.md`, and both are indexed in `.codex/capabilities/INDEX.md`.

## Dependencies And Collision Points

- Customer site/contact work: backend simplification must preserve `/contact` submission behavior.
- Webshop/cart work: checkout dedup and payment-success cascade already connect Customers, Contacts, SOs, SIs, and Communications.
- Catalog media/layout work: do not change Item Group or Item Attribute fixtures casually; catalog data integrity is already verified separately.
- Phase 6 cutover: fixture pruning belongs before Jeff's first post-takeover deploy.
- Legal/Stripe readiness: privacy/terms dashboard wiring is separate; do not mix it into backend simplification unless the task is specifically about Stripe operations.
- Multi-agent work: avoid shared edits to `PROJECT-STATUS.md`, `HANDOFF.md`, and queue unless a handoff boundary requires it.

## First Pass Scope

The next agent should do this in small verified slices:

1. Inventory the actual live ERPNext backend schema.
   - Count LT custom DocTypes, Lead Custom Fields, Property Setters, Custom Fields on Customer/Website Item, and fixtures.
   - Compare DB state to `hooks.py`, `scripts/translate/`, and `scripts/fix/`.
   - Mark scripts that are historical and unsafe to rerun. First stale Lead-script cleanup and workspace idempotent-sync pass completed 2026-05-02; remaining inventory should focus on DB-only schema and fixture/export decisions.

2. Decide the simplest Jeff-facing Lead layout.
   - Keep fields that receive real website data or support immediate follow-up.
   - Hide or demote stale Odoo-era fields that no current form populates.
   - Preserve plain-language labels from project rules.
   - Keep the six-stage business board on `custom_pipeline_stage`; do not repurpose native `Lead.status`.

3. Fix the Lead photos gap or deliberately remove the empty section. Done 2026-05-02.
   - `custom_inspiration_photos` now connects Lead to `LT Lead Photo`.
   - Thumbnail UX is still a separate product choice; the backend table wiring is no longer the blocker.

4. Verify Lead cascade behavior.
   - Create a controlled test Lead through the same endpoint used by `/contact`.
   - Confirm Contact dedup/link behavior.
   - Confirm acknowledgment email queues as expected, or document the mail-queue blocker.
   - Delete test records unless they are intentionally promoted to sample demo data.

5. Build backend tour sample data only after simplification.
   - A few realistic Leads.
   - One paid order path.
   - One upcoming event/operator follow-up shape.
   - Clearly mark demo/sample records so they can be deleted before production.

## Do Not Do

- Do not rerun old Lead translation/fix scripts until they are audited for stale taxonomy.
- Do not reintroduce `/book` as a separate public page.
- Do not add custom DocTypes just to mirror old Odoo models.
- Do not fixture Singles or operator-owned settings just because it is convenient.
- Do not rename customer-facing service values without updating frontend form logic, backend `LT Service Type`, Lead Custom Fields, and verification scripts together.
- Do not hide errors behind "probably." If a DB check cannot be run, mark that state as unverified.

## Verification

Minimum checks after backend simplification edits:

```powershell
python scripts/setup/sync_contact_intake_backend.py
python scripts/setup/sync_crm_pipeline.py
python scripts/setup/sync_stage_cascade.py
python scripts/setup/sync_backend_workspaces.py
python scripts/verify/lead_backend_intake_parity.py
python scripts/verify/crm_pipeline_parity.py
python scripts/verify/crm_stage_cascade.py
python scripts/verify/backend_workspace_parity.py
$env:LT_DESK_TEST_USER='lt-owner-temp@example.com'; $env:LT_DESK_TEST_PASSWORD='LocalTemp2026!'; npm run test:desk-owner
python scripts/verify/contact_service_logic.py --base-url http://localhost:8081
python scripts/verify/contact_prefill.py --base-url http://localhost:8081
```

For contact submission and backend records:

```powershell
python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --form-path /contact --skip-newsletter
```

If backend record verification is needed, set `LT_ADMIN_PASSWORD` first. Previous `smoke_forms.py` backend Basic-auth verification returned HTTP 401 in one session, so do not count that path as passing unless it is freshly verified.

When Python modules change:

```powershell
python -m compileall apps\locally_twisted\locally_twisted scripts\verify scripts\setup
```

After Jinja/CSS/Web Page changes:

```powershell
python scripts/dev/clear_website_cache.py
```

## Decisions And References

- `AGENTS.md` - project rules and ERPNext/Frappe constraints.
- `CODING-HANDOFF.md` - compact current technical state.
- `locally-twisted-queue.md` - active task source.
- `PROJECT-STATUS.md` - project map and historical receipts.
- `locally-twisted-decisions.md` - durable reasoning, especially 2026-05-01 service taxonomy and 2026-04-30 fixture decisions.
- `lessons-learned.md` - project-specific traps.
- `.codex/capabilities/INDEX.md` - capability routing.

Relevant code:

- `apps/locally_twisted/locally_twisted/hooks.py`
- `apps/locally_twisted/locally_twisted/lead_cascade.py`
- `apps/locally_twisted/locally_twisted/www/book.py`
- `apps/locally_twisted/locally_twisted/www/checkout.py`
- `apps/locally_twisted/locally_twisted/www/payment_success.py`
- `apps/locally_twisted/locally_twisted/seed/sync_contact_intake_backend.py`
- `apps/locally_twisted/locally_twisted/seed/sync_backend_workspaces.py`
- `scripts/setup/sync_contact_intake_backend.py`
- `scripts/setup/sync_backend_workspaces.py`
- `scripts/verify/lead_backend_intake_parity.py`
- `scripts/verify/backend_workspace_parity.py`
- `scripts/verify/owner_desk_routes.spec.js`

## Next Handoff Stage

Continue with a read-only backend inventory.

Recommended first command set:

```powershell
git status --short
Select-String -Path .\scripts\fix\*.py,.\scripts\setup\*.py,.\apps\locally_twisted\locally_twisted\seed\*.py -Pattern 'Event Package','Delivery Only','Pickup Only','custom_event_type','LT Lead Photo','Custom Field'
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute frappe.client.get_count --kwargs "{'doctype':'Custom Field','filters':{'dt':'Lead'}}"
```

Then write down what is code-owned, what is DB-only, what still needs fixture/export decisions, and what Jeff actually needs for the first backend walkthrough.
