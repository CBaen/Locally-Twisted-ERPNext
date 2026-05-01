# Locally Twisted — scripts/

All operational scripts for the LT ERPNext build live here. Most scripts are self-contained Python files with a docstring at the top explaining purpose, usage, and the receipts behind why it exists. The layout-fit gate is a Playwright Test spec and runs through npm.

Run scripts from the project root: `python scripts/<dir>/<name>.py`.
Run the layout-fit gate from the project root: `npm run test:layout-fit`.

## Layout

| Dir | Purpose |
|-----|---------|
| `setup/` | One-time-or-occasional install/configuration scripts. Idempotent — safe to re-run. |
| `dev/` | Day-to-day development helpers. Run during a build session. |
| `fix/` | Patches that work around upstream bugs or recreate transient state. |
| `translate/` | Historical: scripts that built the existing Lead schema. Reference for "how to use Frappe API to translate a model." Not active work. |
| `verify/` | Verification scripts (Playwright screenshots, etc.). Run before declaring anything done. |

## What's where

### `setup/`

| Script | Purpose | Run when |
|--------|---------|----------|
| `setup_lt_company.py` | One-shot wizard completion + LT Company seeding | Once, on a fresh install |
| `setup_slice2_header_footer.py` | Wires `Website Settings` (top_bar_items, footer_items, brand_html, address, copyright, home_page) for Slice 2's first attempt | **Stale — represents the band-aid Slice 2 attempt. The Slice 2 redo will use Jinja partial overrides instead. Don't re-run without reading `lessons-learned.md` 2026-04-26 (Slice 2 build) and `anti-gl-patterns.md` section 0 first.** |
| `install_webshop.py` | Historical/fallback installer for `frappe/webshop` + `frappe/payments` on a fresh bind-mount style stack. Current local runtime uses the custom `locally-twisted-erpnext:v15` image with `payments` and `webshop` image-owned, plus a live-edit bind mount for `locally_twisted`. | Do not run as a routine post-recreate step. Use only when deliberately rebuilding a bind-mount install path, then verify `installed_apps` order keeps `locally_twisted` last. |
| `export_odoo_catalog.py` | One-shot HTML scraper for the live LT Odoo catalog (`http://5.78.136.133/`). Outputs `_resources/odoo-export/catalog.json` (51 products with attributes + variant data) and downloads product images to `_resources/odoo-export/images/`. Idempotent — re-running overwrites JSON, skips already-downloaded images. Also a candidate agency-tier capability (cross-client Odoo migration pattern). | (a) Once at session 2026-04-26 — already run. (b) Re-run before Hetzner Odoo is decommissioned to refresh image set. |

| `sync_contact_intake_backend.py` | Runs the in-app `locally_twisted.seed.sync_contact_intake_backend.execute` sync so ERPNext Lead/CRM metadata matches the current `/contact` service taxonomy. | After changing public contact service labels or backend Lead conditional logic |

### `dev/`

| Script | Purpose | Run when |
|--------|---------|----------|
| `clear_website_cache.py` | Clears Frappe site + website cache so edited Jinja templates / CSS / Web Page records take effect on the next request. Optional `--restart` for `hooks.py` changes. | After editing any Jinja template, SCSS, or Web Page record |

### `fix/`

| Script | Purpose | Run when |
|--------|---------|----------|
| `patch_nginx_socketio_origin.py` | Historical/fallback patch for the LT frontend container's nginx config to pass through the original `Origin` header. The current custom image already contains this line. | Only if verifying a rebuilt frontend image shows `proxy_set_header Origin $http_origin;` is missing from `/etc/nginx/conf.d/frappe.conf`. |
| `fix_crm_lead_*.py` | Iterative fixes applied to the Lead schema during initial build. Historical reference only. | Don't re-run; the Lead schema is now stable |
| `fix_lead_photo_thumbnail.py` | Inspiration Photos thumbnail UX experiment | Historical |

### `translate/`

| Script | Purpose | Status |
|--------|---------|--------|
| `translate_crm_lead.py` | Built the active Lead schema (45+ Custom Fields, plain-language relabels, sectioned layout) | DONE — Lead schema is stable, do not re-run |
| `translate_dashboard_review.py` | Built the `Dashboard Reviewed Item` DocType | DONE |

### `verify/`

| Script | Purpose | Run when |
|--------|---------|----------|
| `layout_fit.spec.js` | Playwright Test gate for 15 public/shop/cart routes across 320px, 375px, tablet, and desktop. Fails on HTTP errors, document horizontal overflow, visible element overflow, and direct text overflow. | Before visual claims, after customer-facing CSS/Jinja/template changes |
| `contact_service_logic.py` | Verifies `/contact` service-specific conditional logic: stackable services, Events Inquiry labels, live-artist-only shade/environment fields, Pickup/Delivery wording, and absence of stale `Event Package` / `Only` labels. | After editing contact form labels, service choices, conditionals, or Lead payload mapping |
| `contact_prefill.py` | Verifies guided contact URLs preselect the intended service checkboxes and reveal the matching panels for BTFP, twisting, and face painting. | After editing service-page CTAs or `/contact?service=...` parsing |
| `lead_backend_intake_parity.py` | Verifies live ERPNext Lead/CRM metadata matches `/contact`: service type records, Lead Custom Field labels/depends_on logic, and submit helper mapping into `custom_event_type`. | After editing backend Lead fields or public service taxonomy |
| `smoke_forms.py` | Browser smoke test for public forms. Use `--form-path /contact --skip-newsletter` for the current canonical inquiry form; set `LT_ADMIN_PASSWORD` when backend Lead/Communication verification is required. | Before claiming form submissions work end-to-end |
| `playwright_home_screenshot.py` | Real-Chromium full-page screenshot capture at desktop + mobile viewports + DOM facts dump | Before declaring any visible change "done." Mandatory per `anti-gl-patterns.md` section 0. |

## Standing rules

- **Always Read the screenshot file via the Read tool and describe the pixel content** before declaring a visible change done. DOM `is_visible: True` ≠ rendered pixels show the content. (Receipt: 2026-04-26 Slice 2 build session.)
- **Layout fit is necessary but not sufficient.** `npm run test:layout-fit` catches geometry regressions; it does not replace screenshot review or GL's real-browser check.
- **Idempotency over magic.** Every script in `setup/` and `dev/` should be safe to re-run. If state matters, the script either checks-then-acts or no-ops cleanly.
- **Loud errors.** If a script's API call returns an error, surface it. No silent swallowing. (Loud-failure rule per global `C:\Users\baenb\.claude\rules\loud-failure.md`.)
- **No deploy.py yet.** Frappe Cloud cutover is Phase 6. Until then, all "deploy"-like operations live as discrete scripts in `setup/` or `dev/`.
