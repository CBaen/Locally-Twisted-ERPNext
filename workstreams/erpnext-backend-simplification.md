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

Active handoff lane. First Jeff-facing Desk simplification edits have been made in the live local ERPNext database.

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
- `LT Service Type` was synced on 2026-05-01 to remove `Delivery Only` and `Event Package` and add `Delivery`, `Pickup`, `Events Inquiry`.
- `lead_cascade.py` hooks on Lead insert to create/link Contact and queue the customer acknowledgment email.
- `/payment-success` marks Payment Requests paid, creates Sales Invoices, sends receipt/operator/welcome emails, and redirects customers even if backend follow-up fails.
- `LT Lead Photo` and a Lead photos section exist, but the queue says the connecting Table field is missing. Treat that as unverified but likely still open.
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

Verification as `lt-owner-temp@example.com` on 2026-05-02:

- `/app/Workspaces` returned 200.
- Owner sidebar showed `Owner Home`, then `Home`.
- Owner counts: `Sales Order` 8, `Event` 0, `Customer` 4, `Contact` 25, `Item` 10,631.
- Owner could load Item metadata with `Item Manager` create/write permission.
- Calendar events endpoint for `Sales Order` returned the 8 existing orders on `2026-05-06`.
- The route guard asset was served at `/assets/locally_twisted/js/lt-desk-workspace-router.js?v=20260502-1` with the pageview guard present. The Desk HTML still referenced `v=20260502-1` until a server reload picks up the hook query-string bump, so browser hard-refresh may be needed after changes.

Important: these are live DB changes, not fixtures yet. Before production/cutover, decide which workspace, role profile, and Calendar View records should be exported or recreated by an idempotent setup script.

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

This pattern is now promoted to `.codex/capabilities/recipes/erpnext-simplified-role-verification.md` and indexed in `.codex/capabilities/INDEX.md`.

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
   - Mark scripts that are historical and unsafe to rerun.

2. Decide the simplest Jeff-facing Lead layout.
   - Keep fields that receive real website data or support immediate follow-up.
   - Hide or demote stale Odoo-era fields that no current form populates.
   - Preserve plain-language labels from project rules.

3. Fix the Lead photos gap or deliberately remove the empty section.
   - If photos are still needed: add the missing Table field to connect `LT Lead Photo`.
   - If photos are not part of the next backend tour: remove/hide the empty section and log why.

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
python scripts/verify/lead_backend_intake_parity.py
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
- `scripts/setup/sync_contact_intake_backend.py`
- `scripts/verify/lead_backend_intake_parity.py`

## Next Handoff Stage

Start with a read-only backend inventory.

Recommended first command set:

```powershell
git status --short
Select-String -Path .\scripts\translate\*.py,.\scripts\fix\*.py,.\scripts\setup\*.py -Pattern 'Event Package','Delivery Only','Pickup Only','custom_event_type','LT Lead Photo','Custom Field'
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute frappe.client.get_count --kwargs "{'doctype':'Custom Field','filters':{'dt':'Lead'}}"
```

Then write down what is code-owned, what is DB-only, what is stale historical scaffolding, and what Jeff actually needs for the first backend walkthrough.
