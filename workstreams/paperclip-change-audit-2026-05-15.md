# Paperclip Change Audit - 2026-05-15

## Purpose

This packet separates the current Paperclip-created or Paperclip-adjacent
changes so the contact form can be handled first without accidentally dragging
catalog, backend, checkout, or Odoo-derived changes into the same review.

Status: active dirty-file cleanup coordination. Bucket 3 was resolved locally on
2026-05-15 because `patches.txt` referenced an untracked migration patch, which
was a deploy/migrate stop condition.

## Current Order

1. Resolve one bucket at a time.
2. Do not stage, commit, deploy, or live-verify mixed buckets as one release.
3. Treat any `patches.txt` entry pointing at an untracked or missing patch file
   as the next cleanup target because it can break migrate/deploy.

## Bucket 1 - Contact Form: Now

Priority: P0, active now.

Files currently dirty:

- `apps/locally_twisted/locally_twisted/www/contact.html`
- `apps/locally_twisted/locally_twisted/www/contact.py`

Dirty changes found:

- form heading changed from `Free Event Quote` to
  `Tell us what you're planning`;
- page title/meta/intro changed from free-quote language to
  tell-us-about-your-event language.

Recent committed form behavior found:

- phone is required;
- preferred contact method was added;
- event date, location, and occasion are required;
- event time controls were made more structured;
- email typo warning was added;
- frontend validation fails louder before submit;
- backend Lead intake maps the new required fields.

Local verification passed against `http://localhost:8081/contact`:

- `python -m py_compile ...`
- `python scripts/verify/contact_service_logic.py --base-url http://localhost:8081`
- `python scripts/verify/lead_backend_intake_parity.py`
- `npm run test:form-experience`
- `python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --form-path /contact --skip-newsletter`
- `python scripts/verify/customer_email_policy_contract.py`
- `python scripts/verify/book_form_repeat_email_photos.py --base-url http://localhost:8081`

Local/live difference found:

- local has preferred contact method, email typo hint, structured visible time
  controls, and newer form assets;
- live `https://locallytwisted.com/contact` is still the older release.

Next decision for GL:

- approve, revise, or reject the current form copy and required-field behavior
  before any deploy or mixed cleanup.

## Bucket 2 - Inquiry Photo Hotfix: Deploy/Live Verify

Priority: P0 after form review, unless GL decides production photo handling is
the emergency release before copy polish.

Known state:

- source fix is documented in
  `workstreams/inquiry-photo-storage-owner-attachments-2026-05-15.md`;
- full repo and app mirror commits were pushed before this audit;
- production is not protected until Frappe Cloud deploy, site update/migrate,
  and live repeat-email/five-photo verification pass.

Do not claim production fixed from local tests, GitHub pushes, or route health
alone.

## Bucket 3 - Catalog/Color Typo Patch: Resolved Locally

Priority: resolved before other buckets because of the missing-tracked-patch
stop condition.

Files touched:

- `_resources/odoo-live/catalog.json`
- `_resources/odoo-live/value_normalize_map.json`
- `apps/locally_twisted/locally_twisted/catalog_contract/color_rules.py`
- `apps/locally_twisted/locally_twisted/fixtures/item_attribute.json`
- `apps/locally_twisted/locally_twisted/product_page_runtime.py`
- `apps/locally_twisted/locally_twisted/product_quote_request.py`
- `apps/locally_twisted/locally_twisted/verify/product_page_runtime_contract.py`
- `apps/locally_twisted/locally_twisted/verify/product_quote_customization_contract.py`
- `scripts/verify/cart_checkout_contract.py`
- `scripts/verify/product_quote_first_experience.spec.js`
- `apps/locally_twisted/locally_twisted/patches.txt`
- untracked:
  `apps/locally_twisted/locally_twisted/patches/rename_reflex_champagne_color_20260515.py`

Finding:

- appears to rename `Reflex Champage` to `Reflex Champagne` across source,
  fixtures, Odoo-derived reference data, runtime expectations, and verifiers.

Risk:

- resolved: `patches.txt` and
  `apps/locally_twisted/locally_twisted/patches/rename_reflex_champagne_color_20260515.py`
  are now staged together;
- `_resources/odoo-live/*` changes are inside this ERPNext repo, but they are
  Odoo-derived reference data and should not be treated as casual form work.

Resolution:

- corrected customer-facing source/reference spelling from `Reflex Champage`
  to `Reflex Champagne`;
- kept a backwards-compatible alias so old payloads and old local DB values
  canonicalize to the corrected display name;
- added an idempotent Frappe patch to rename existing Item Attribute Value and
  Item Variant Attribute records during migrate;
- local patch execute returned exit 0 against `frontend`;
- local post-patch checks returned `Reflex Champagne` counts for 1 Item
  Attribute Value and 123 Item Variant Attribute rows.

Verification:

- `python -m compileall ...`
- `python scripts\verify\cart_checkout_contract.py`
- `docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.verify.product_quote_customization_contract.run`
- `docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.verify.product_page_runtime_contract.run`
- `cmd /c scripts\verify\run_playwright.cmd test scripts/verify/product_quote_first_experience.spec.js --reporter=line`

## Bucket 4 - Backend Workspace/Persona Permissions: Resolved Locally

Priority: resolved as backend/access-lane cleanup.

Files touched:

- `apps/locally_twisted/locally_twisted/seed/sync_backend_workspaces.py`
- `scripts/verify/backend_workspace_parity.py`
- `scripts/verify/persona_desk_routes.spec.js`
- untracked:
  `apps/locally_twisted/locally_twisted/verify/persona_workspace_permissions.py`

Finding:

- employee `Booking Calendar` access appears to be removed or forbidden by the
  workspace/persona checks;
- a new persona permission verifier exists but is not tracked yet.

Risk:

- resolved: Employee Home is intentionally narrowed to assigned tasks and event
  jobs; Manager retains booking visibility; Owner Product/Add Product shortcuts
  now route through `LT Product Blueprint` instead of raw `Item`;
- the new `persona_workspace_permissions` verifier is tracked and included in
  `backend_workspace_parity.py`, so visible workspace shortcuts must match each
  persona's actual permissions.

Verification:

- `python -m compileall apps\locally_twisted\locally_twisted\seed\sync_backend_workspaces.py apps\locally_twisted\locally_twisted\verify\persona_workspace_permissions.py scripts\verify\backend_workspace_parity.py`
- `python scripts\verify\backend_workspace_parity.py`
- `docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.verify.persona_workspace_permissions.run`
- `$env:LT_DESK_TEST_PASSWORD='LocalTemp2026!'; npm run test:desk-personas`
- `python scripts\verify\product_blueprint_contract.py`

## Bucket 5 - Checkout Verifier Pause Override: Resolved Locally

Priority: resolved as a verifier-only cleanup.

File touched:

- `apps/locally_twisted/locally_twisted/verify/checkout_lead_conversion_contract.py`

Finding:

- verifier code monkeypatches ecommerce pause state to exercise checkout/Lead
  conversion behavior while the customer-facing ecommerce lock may still be on.

Risk:

- resolved: the pause bypass is scoped to
  `locally_twisted.verify.checkout_lead_conversion_contract.run`, restores the
  original pause function in `finally`, and now fails loudly if the bypass is
  not active inside the verifier;
- this is verifier-only proof and does not reopen checkout, Stripe, or live
  ecommerce.

Verification:

- `python -m compileall apps\locally_twisted\locally_twisted\verify\checkout_lead_conversion_contract.py`
- `docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.verify.checkout_lead_conversion_contract.run`

## Bucket 6 - Maintenance Heartbeat Role Change: Resolved Locally

Priority: resolved as maintenance boundary parity.

File touched:

- `apps/locally_twisted/locally_twisted/locally_twisted/report/lt_maintenance_heartbeat/lt_maintenance_heartbeat.json`

Finding:

- report role metadata adds `LT Maintenance Admin Access`.

Risk:

- resolved: `LT Maintenance Admin Access` is the existing narrow maintenance
  role, and the report role now matches the sanitized Maintenance Admin
  boundary.

Verification:

- `docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute frappe.db.exists --args "['Role', 'LT Maintenance Admin Access']"`
- `python scripts\verify\maintenance_heartbeat.py`
- `python scripts\verify\maintenance_admin_boundary.py`

## Bucket 7 - External Odoo Project Concern

Concern:

- GL is worried Paperclip reached into the old Odoo project without permission.

Read-only check performed:

- external repo checked at `C:\Users\baenb\projects\locally-twisted-odoo`;
- no current tracked dirty changes were found there during this audit;
- the repo is already ahead of origin and has an older untracked `CODEX_REPLY.md`
  from 2026-05-06, which should not be attributed to Paperclip without deeper
  history review.

Important distinction:

- Paperclip did touch `_resources/odoo-live/*` inside the ERPNext repo. That is
  Odoo-derived reference material, but it is not the external Odoo project.

## Stop Conditions

- Stop if a requested form fix requires staging/live deploy before the non-form
  buckets are separated.
- Stop if `patches.txt` references an untracked or missing patch file.
- Stop if any form success state is shown without current Lead plus customer
  and owner Email Queue proof.
- Stop if a live claim depends only on local tests.
