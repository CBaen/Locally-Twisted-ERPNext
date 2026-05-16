# ERPNext Backend Simplification Workstream

Last updated: 2026-05-15 by Codex after owner phone-action access closeout.

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

2026-05-15 access-audit addendum: the current working frontier is not another
workspace label pass. It is permission hardening behind the simplified views:
real DocType/User Permission matrix checks, explicit external-review role
boundaries, test-user cleanup, and small role changes only after failing
verifiers prove the exact exposure.

2026-05-15 GL correction: access work is now owner-first. The active access
design target is Jeff/business-owner use, with Cameron/Built by Cameron support
access preserved for build and maintenance. Manager, Employee, Accountant,
Customer, Supplier, Maintenance Admin, and Marketing Reviewer profiles are
boundary/audit context unless they directly protect or unblock owner/support
use. Keep profile work inside this lane and
`workstreams/user-access-audit-2026-05-15.md`; do not propagate it into other
handoffs unless a specific owner workflow, verifier, or permission boundary
requires the cross-link.

This file is the job sheet for future handoffs. Keep `locally-twisted-queue.md` as the active task source, and update this file when the backend simplification lane changes stage.

2026-05-15 owner phone-action update: the current owner-first slice now has a
local `/owner-actions` page, owner-safe business DTOs, a narrow whitelisted API
adapter, and fake local records for a quality localhost owner tour. Feature
handoff: `workstreams/owner-phone-action-center-2026-05-15.md`. Capability:
`capabilities/recipes/erpnext-owner-business-access-api.md`.

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
- Cameron/Built by Cameron can still maintain the system without turning
  support access into the normal client/operator experience.

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
- human-access guard surfaces:
  `apps/locally_twisted/locally_twisted/owner_business_access.py`,
  `apps/locally_twisted/locally_twisted/api/owner_business.py`,
  `apps/locally_twisted/locally_twisted/www/owner-actions/`,
  `apps/locally_twisted/locally_twisted/seed/owner_demo_data.py`,
  `apps/locally_twisted/locally_twisted/verify/owner_business_access_contract.py`,
  `apps/locally_twisted/locally_twisted/marketing_review_access.py`,
  `apps/locally_twisted/locally_twisted/www/me.py`,
  `apps/locally_twisted/locally_twisted/verify/marketing_review_access_boundary.py`,
  and `workstreams/user-access-audit-2026-05-15.md`.

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
- Checkout/Lead conversion parity is verified across the payment boundary: when checkout reuses a Contact linked to a Lead, the Lead stays `Open` / `New Inquiry` until the paid-order cascade runs. After payment reconciliation, native `Lead.status` becomes `Converted`, `Lead.customer` is set, `Lead.custom_pipeline_stage` moves to `Approved`, the old New Inquiry task closes, and the Approved follow-up task becomes active. The verifier rolls back its generated Customer, Sales Order, and Payment Request.
- Owner phone actions are provider-neutral DTOs first. `/owner-actions` uses
  the same DTO layer intended for future ChatGPT/OAuth/API-compatible adapters.
  ChatGPT is not the architecture; future providers must authenticate through
  their own adapter/token verifier before reading this surface. Initial write
  scope is only `log_contact_attempt`, which records a Comment and does not
  send customer messages or mutate business state.
- Local owner demo data is intentionally fake and marker-owned. Run
  `python scripts/setup/sync_owner_demo_data.py` to refresh it and
  `python scripts/setup/sync_owner_demo_data.py --cleanup` to remove it.
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
- Owner counts: `Sales Order` 8, `Event` 0, `Customer` 4, `Contact` 25, `Item` 10,633.
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

## 2026-05-09 Login / Portal Reality Check

- `/login#login` is still the Frappe auth route, but the customer-facing page is now LT-branded through the customer/client portal slice. The URL fragment does not change the server route. Current customer login visual/auth proof lives in `workstreams/customer-client-portal-translation-2026-05-10.md`.
- As of 2026-05-15, the real owner email `locallytwisted@gmail.com` has the
  temporary local password `LocalTemp2026!` and passes `npm run test:desk-owner`
  against Owner Home. This is the immediate account for lead handling until GL
  changes the password later.
- The local owner/client test account is `lt-owner-temp@example.com` with the `LT Owner` role profile. Fresh `npm run test:desk-owner` passed with the documented local test password and proved `/app/home`, `/app/owner-home`, and `/app/Workspaces` land on the Owner Home command center.
- `cameron@builtbycameron.com` is an enabled System User with support/admin roles. No local User records existed for `hi@locallytwisted.com` or `cameron@locallytwisted.com` in the 2026-05-09 check.
- The temporary contractor account `lt-contractor-temp@example.com` remains disabled. Contractors are still not a backend-login tier by default.
- Public customer flows do not require login: `/cart`, `/checkout`, and `/contact` returned HTTP 200 as guest routes with no redirect to `/login`, and `python scripts/verify/cart_checkout_contract.py` passed.

## 2026-05-11 Backend Persona Workspace Simplification

Current local ERPNext Desk state is now persona-focused rather than only
owner-focused:

- `LT Owner Home` keeps the command center, Jeff next-action flow, and secondary
  catalog tools including `Add Product`.
- `LT Manager Home` keeps inquiry, booking, customer/contact, event job, task,
  and add-inquiry/customer actions, but no longer exposes `Products`,
  `Product Prices`, or `Add Product`.
- `LT Employee Home` is narrowed to `My Tasks`, `Task Board`, `Booking
  Calendar`, and `Event Jobs`; it no longer exposes customer/contact, inquiry,
  or catalog administration shortcuts.
- `LT Accountant Home` is narrowed to invoices, payment requests, payment
  entries, customers, reminder review, journal entries, and chart of accounts.
  It no longer exposes bank, vendor, payment-terms, statement-reminder, or
  employee/payroll shortcuts while those lanes remain incomplete.
- `LT Maintenance Home` remains the sanitized maintenance surface. The
  `LT Maintenance Heartbeat` report was re-synced so it includes
  `LT Maintenance Admin Access`; maintenance, heartbeat, and finance parity
  gates now pass.
- Temp persona users now have explicit default workspaces: Owner, Manager,
  Employee, and Accountant route to their matching LT workspaces instead of
  depending on workspace ordering.

Code ownership and guards:

- `apps/locally_twisted/locally_twisted/seed/sync_backend_workspaces.py`
  now owns deterministic Manager and Employee workspace shortcut/content sets.
- `apps/locally_twisted/locally_twisted/seed/sync_finance_workspace.py`
  now owns the reduced Accountant Home shortcut/content set and prunes removed
  finance/payroll setup links.
- `scripts/verify/backend_workspace_parity.py` now fails if Manager/Employee
  workspaces regain non-persona shortcuts.
- `scripts/verify/finance_workspace_parity.py` now fails if Accountant Home
  regains unfinished bank/vendor/payroll setup shortcuts.
- `scripts/verify/persona_desk_routes.spec.js` and `npm run test:desk-personas`
  prove Manager, Employee, and Accountant temp accounts land on the expected
  personalized Desk views.
- The backend and finance syncs both touch `User.default_workspace`; run them
  serially when applying both in the same session.

Verification receipt on 2026-05-11:

- `python scripts/setup/sync_maintenance_package.py`
- `python scripts/setup/sync_backend_workspaces.py`
- `python scripts/setup/sync_finance_workspace.py`
- `python scripts/verify/backend_workspace_parity.py`
- `python scripts/verify/finance_workspace_parity.py`
- `python scripts/verify/maintenance_admin_boundary.py`
- `python scripts/verify/maintenance_heartbeat.py`
- `$env:LT_DESK_TEST_PASSWORD='LocalTemp2026!'; npm run test:desk-personas`
- `$env:LT_DESK_TEST_USER='lt-owner-temp@example.com'; $env:LT_DESK_TEST_PASSWORD='LocalTemp2026!'; npm run test:desk-owner`

Next permission work should not start from custom Frappe `User Type` records.
Frappe still uses standard `System User` and `Website User`; LT's backend
personas are role/profile/workspace packages. The next safe slice is to tighten
DocType permissions and user permissions behind these views with failing
verifiers first.

## 2026-05-15 Human Access Audit

The latest access review is
`workstreams/user-access-audit-2026-05-15.md`.

Current verified access state:

- Owner, Manager, Employee, and Accountant temp Desk personas all pass browser
  route proof after backend restart.
- Customer Website User portal contracts pass and keep customer accounts out of
  Desk/backend records.
- The marketing reviewer lane is separate from customer accounts:
  `Website User` plus explicit `LT Marketing Review Access`,
  `desk_access = 0`, no DocPerm rows, `/marketing-review` only.
- `User Permission` rows are currently empty. Restrictions are role/profile,
  workspace, portal-code, and hook based.
- No enabled Supplier user, permanent marketing reviewer user, or enabled
  Maintenance Admin user was found in the local DB.
- One enabled customer visual test account remains:
  `lt-portal-visual-1778476910635718999@example.invalid`.

Important finding:

- Manager workspace does not surface catalog tools, but the current role matrix
  still grants Manager `Item Price` create/write/delete. Treat this as the next
  access-hardening target. Add a failing permission-matrix verifier before
  removing or rewriting broad ERPNext roles.

Verification receipt on 2026-05-15:

- `python scripts/verify/customer_portal_inventory.py --base-url http://localhost:8081 --strict-menu`
- `python scripts/verify/custom_doctype_permission_boundary.py`
- `python scripts/verify/backend_workspace_parity.py`
- `python scripts/verify/finance_workspace_parity.py`
- `python scripts/verify/maintenance_admin_boundary.py`
- `python scripts/verify/maintenance_heartbeat.py`
- `python scripts/verify/customer_portal_v1_contract.py`
- `python scripts/verify/customer_portal_home_contract.py`
- `python scripts/verify/customer_account_provisioning_contract.py`
- `python scripts/verify/customer_documents_contract.py`
- `python scripts/verify/customer_contact_points_contract.py`
- `python scripts/verify/marketing_review_access_boundary.py`
- `npm run test:marketing-review-access`
- `$env:LT_DESK_TEST_PASSWORD='LocalTemp2026!'; npm run test:desk-personas`
- `$env:LT_DESK_TEST_USER='lt-owner-temp@example.com'; $env:LT_DESK_TEST_PASSWORD='LocalTemp2026!'; npm run test:desk-owner`

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

## 2026-05-02 Backend Schema Inventory And Trigger Map

Read-only inventory is now repeatable through `scripts/verify/backend_schema_inventory.py`.

Latest live inventory receipt:

- `Lead`: 12, all in `custom_pipeline_stage = New Inquiry`.
- `Contact`: 25.
- `Customer`: 4.
- `Sales Order`: 8, all currently on `delivery_date = 2026-05-06`.
- `Payment Request`: 8.
- `Sales Invoice`: 1.
- `Task`: 0.
- `Communication`: 14.
- `LT Service Type`: 7.
- `LT Lead Service Type`: 0.
- `LT Lead Photo`: 0.
- `LT Newsletter Signup`: 16.
- `Custom Field`: 94 total; 47 are on Lead, 3 are on Task.
- `Property Setter`: 102 total; 4 are on Lead.
- Custom/LT DocTypes found: `Dashboard Reviewed Item`, `LT Lead Photo`, `LT Lead Service Type`, `LT Service Type`, and `LT Newsletter Signup`.
- The inventory classifies 28 Custom Fields as code-owned by current fixtures/setup code and 66 as unclassified DB/app-owned records that need deliberate keep/hide/export decisions before production hardening.
- Stale service labels are not present as active stale code in the inventory scan. The remaining old-label references are intentional guardrails in rename maps or negative verifiers.

Current trigger map:

- `New Inquiry`: website Lead insert creates/links Contact, queues customer auto-ack email, sets the LT pipeline stage, and creates the first operational Task.
- `Quote Sent/Awaiting Approval`: currently Task-only. Do not create a Quote automatically until the quote creation/sent threshold is decided.
- `Approved`: currently Task-only. Do not attach Sales Order/payment automation here until the existing checkout flow is reconciled with manual/custom inquiry approvals.
- `In Production`: currently Task-only. Candidate future trigger is production job/project/checklist/calendar/staff coordination after the booking/deposit threshold is explicit.
- `Event/Post Event`: currently Task-only. Candidate future trigger is review/thank-you/post-event closeout after event date.
- `Archive`: off-board only. It closes open stage Tasks and must not imply won/lost/finance state.
- Existing `/checkout` is already a finance path: it creates/reuses Customer/Contact, creates Sales Order, creates Payment Request, and sends the customer to Stripe Checkout. `/payment-success` and the Stripe webhook reconcile paid orders by marking the Payment Request paid, creating Sales Invoice, and sending receipt/operator/welcome emails.
- Checkout/Lead conversion parity is now covered by `scripts/verify/checkout_lead_conversion_contract.py`. The checkout path creates/links the Customer and Contact but does not set native `Lead.status = Converted`, `Lead.customer`, or the `Approved` LT pipeline stage before payment. The paid-order cascade handles that conversion after payment reconciliation and lets the existing operational Task cascade close New Inquiry follow-up and open the Approved follow-up. This does not add stage-to-finance automation; checkout itself remains the finance path that creates the Customer, Sales Order, and Payment Request.

Important next-risk note: manual stage-to-finance automation still needs explicit threshold design. Do not create another stage-driven Customer, Sales Order, Payment Request, or invoice path until it is mapped against checkout and paid-order reconciliation.

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
- Inventory existing finance paths before wiring a stage to finance. This repo already has checkout/payment-success cascades, so stage automation must coordinate with them instead of creating parallel records.

These patterns are now promoted to `capabilities/recipes/erpnext-simplified-role-verification.md` and `capabilities/recipes/erpnext-crm-pipeline-safety.md`, and both are indexed in `capabilities/INDEX.md`.

## Dependencies And Collision Points

- Customer site/contact work: backend simplification must preserve `/contact` submission behavior.
- Webshop/cart work: checkout dedup and payment-success cascade already connect Customers, Contacts, SOs, SIs, and Communications.
- Catalog media/layout work: do not change Item Group or Item Attribute fixtures casually; catalog data integrity is already verified separately.
- Phase 6 cutover: fixture pruning belongs before Jeff's first post-takeover deploy.
- Legal/Stripe readiness: privacy/terms dashboard wiring is separate; do not mix it into backend simplification unless the task is specifically about Stripe operations.
- Multi-agent work: avoid shared edits to `PROJECT-STATUS.md`, `HANDOFF.md`, and queue unless a handoff boundary requires it.

## First Pass Scope

The next agent should do this in small verified slices:

1. Inventory the actual live ERPNext backend schema. Done 2026-05-02.
   - Count LT custom DocTypes, Lead Custom Fields, Property Setters, Custom Fields on Customer/Website Item, and fixtures.
   - Compare DB state to `hooks.py`, `scripts/translate/`, and `scripts/fix/`.
   - Mark scripts that are historical and unsafe to rerun. First stale Lead-script cleanup and workspace idempotent-sync pass completed 2026-05-02; repeatable backend inventory now lives at `scripts/verify/backend_schema_inventory.py`.

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
python scripts/verify/backend_schema_inventory.py
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
- `capabilities/INDEX.md` - capability routing.

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
- `scripts/verify/backend_schema_inventory.py`
- `scripts/verify/backend_schema_inventory_contract.py`
- `scripts/verify/lead_backend_intake_parity.py`
- `scripts/verify/backend_workspace_parity.py`
- `scripts/verify/owner_desk_routes.spec.js`

## Next Handoff Stage

Continue with explicit stage-threshold design before adding any manual stage-to-finance automation.

Recommended first command set:

```powershell
git status --short
python scripts/verify/backend_schema_inventory.py
python scripts/verify/checkout_lead_conversion_contract.py
python scripts/verify/crm_pipeline_parity.py
python scripts/verify/crm_stage_cascade.py
```

Then decide which manual stages, if any, should create or update Quote, Sales Order, Project/job, Calendar invite, customer follow-up, or finance records. Do not infer those triggers from stage labels alone.
