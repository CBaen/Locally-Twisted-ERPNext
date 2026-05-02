# Locally Twisted - scripts/

Operational scripts for the LT ERPNext build live here. Most scripts are self-contained Python files with a docstring at the top explaining purpose, usage, and why it exists. The layout-fit gate is a Playwright Test spec and runs through npm.

Run scripts from the project root: `python scripts/<dir>/<name>.py`.
Run the layout-fit gate from the project root: `npm run test:layout-fit`.

## Layout

| Dir | Purpose |
|-----|---------|
| `setup/` | One-time-or-occasional install/configuration scripts. Idempotent scripts are safe to re-run. |
| `dev/` | Day-to-day development helpers. Run during a build session. |
| `fix/` | Patches that work around upstream bugs or recreate transient state. |
| `translate/` | Historical translation scripts were removed; git history is the archive. |
| `verify/` | Verification scripts. Run before declaring anything done. |

## setup/

| Script | Purpose | Run when |
|--------|---------|----------|
| `setup_lt_company.py` | One-shot wizard completion + LT Company seeding. | Once, on a fresh install |
| `setup_slice2_header_footer.py` | Stale Slice 2 Website Settings wiring attempt. | Do not re-run without reading the current header/footer rules |
| `install_webshop.py` | Historical/fallback installer for `frappe/webshop` + `frappe/payments`. | Only when deliberately rebuilding a bind-mount install path |
| `export_odoo_catalog.py` | One-shot HTML scraper for the old live LT Odoo catalog. | Re-run only before the old source is decommissioned |
| `sync_contact_intake_backend.py` | Runs the in-app `locally_twisted.seed.sync_contact_intake_backend.execute` sync so ERPNext Lead/CRM metadata matches the current `/contact` service taxonomy, including plain-text estimated time fields and the `LT Lead Photo` child table connection. | After changing public contact service labels or backend Lead conditional logic |
| `sync_backend_workspaces.py` | Runs the in-app `locally_twisted.seed.sync_backend_workspaces.execute` sync so simplified Owner, Manager, and Employee workspaces use current business labels, the Sales Order booking calendar, and the Owner Home command-center cards/chart/checklist. | After changing simplified backend workspaces, role profiles, number cards, charts, or calendar shortcuts |
| `sync_variant_media.py` | Stages Odoo product images and applies conservative variant image mappings. | After reviewing or refreshing catalog media mappings |

## dev/

| Script | Purpose | Run when |
|--------|---------|----------|
| `clear_website_cache.py` | Clears Frappe site + website cache so edited Jinja templates / CSS / Web Page records take effect on the next request. Optional `--restart` for `hooks.py` changes. | After editing Jinja templates, SCSS/CSS, Web Page records, or hooks |

## fix/

| Script | Purpose | Run when |
|--------|---------|----------|
| `patch_nginx_socketio_origin.py` | Historical/fallback patch for the LT frontend container's nginx config to pass through the original `Origin` header. The current custom image should already contain this line. | Only if a rebuilt frontend image is verified missing `proxy_set_header Origin $http_origin;` |
| `fix_crm_lead_*.py` | Removed. These one-off Lead-schema scripts used stale service labels and are preserved only in git history. | Use `setup/sync_contact_intake_backend.py` instead |
| `fix_lead_photo_thumbnail.py` | Removed. The child table connection is now handled by `setup/sync_contact_intake_backend.py`; thumbnail UX remains a separate product choice. | Use git history only if researching the old experiment |

## translate/

| Script | Purpose | Status |
|--------|---------|--------|
| `translate_crm_lead.py` | Removed. It built an early Lead schema with stale service values. | Git history only |
| `translate_dashboard_review.py` | Built the `Dashboard Reviewed Item` DocType. | Historical |

## verify/

| Script | Purpose | Run when |
|--------|---------|----------|
| `layout_fit.spec.js` | Playwright Test gate for public/shop/cart routes across mobile, tablet, and desktop widths. | Before visual claims, after customer-facing CSS/Jinja/template changes |
| `owner_desk_routes.spec.js` | Playwright Test gate for owner Desk route recovery and Owner Home content. | After Desk JS, workspace, or simplified owner role changes |
| `contact_service_logic.py` | Verifies `/contact` service-specific conditional logic and absence of stale service labels. | After editing contact form labels, choices, conditionals, or Lead payload mapping |
| `contact_prefill.py` | Verifies guided contact URLs preselect the intended service checkboxes and panels. | After editing service-page CTAs or `/contact?service=...` parsing |
| `lead_backend_intake_parity.py` | Verifies live ERPNext Lead/CRM metadata matches `/contact`: service type records, Lead Custom Field labels/depends_on logic, plain-text time entry, `LT Lead Photo` table wiring, and submit helper mapping into `custom_event_type`. | After editing backend Lead fields or public service taxonomy |
| `backend_workspace_parity.py` | Verifies simplified backend workspaces no longer show stale ERPNext labels, booking calendars point at Sales Orders by delivery date, and Owner Home includes the command-center number cards/chart/checklist. | After editing workspaces, role profiles, number cards, charts, or Desk calendar behavior |
| `smoke_forms.py` | Browser smoke test for public forms. Use `--form-path /contact --skip-newsletter` for the current canonical inquiry form; set `LT_ADMIN_PASSWORD` when backend Lead/Communication verification is required. | Before claiming form submissions work end-to-end |
| `playwright_home_screenshot.py` | Real-Chromium full-page screenshot capture at desktop + mobile viewports + DOM facts dump. | Before declaring a visible change done |

## Standing Rules

- Layout fit is necessary but not sufficient. `npm run test:layout-fit` catches geometry regressions; it does not replace screenshot review or GL's real-browser check.
- Idempotency over magic. Every script in `setup/` and `dev/` should check-then-act or no-op cleanly when state already exists.
- Loud errors. If a script's API call returns an error, surface it.
- No `deploy.py` yet. Frappe Cloud cutover is Phase 6. Until then, deployment-like operations live as discrete scripts in `setup/` or `dev/`.
