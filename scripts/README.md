# Locally Twisted — scripts/

All operational scripts for the LT ERPNext build live here. Each script is a self-contained Python file with a docstring at the top explaining purpose, usage, and the receipts behind why it exists.

Run scripts from the project root: `python scripts/<dir>/<name>.py`.

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
| `install_webshop.py` | Installs `frappe/webshop` + `frappe/payments` (a hard dependency). Also re-runs editable pip install for `locally_twisted`/`payments`/`webshop` in all 4 frappe-image services after `docker compose up --force-recreate`. | (a) Once on initial install, with `--fetch --site-install` flags. (b) After every container recreation, with no flags. |

### `dev/`

| Script | Purpose | Run when |
|--------|---------|----------|
| `clear_website_cache.py` | Clears Frappe site + website cache so edited Jinja templates / CSS / Web Page records take effect on the next request. Optional `--restart` for `hooks.py` changes. | After editing any Jinja template, SCSS, or Web Page record |

### `fix/`

| Script | Purpose | Run when |
|--------|---------|----------|
| `patch_nginx_socketio_origin.py` | Patches the LT frontend container's nginx config to pass through the original `Origin` header (frappe_docker rewrites it to `http://frontend`, breaking socketio CORS at non-default ports) | After every recreation of the frontend container |
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
| `playwright_home_screenshot.py` | Real-Chromium full-page screenshot capture at desktop + mobile viewports + DOM facts dump | Before declaring any visible change "done." Mandatory per `anti-gl-patterns.md` section 0. |

## Standing rules

- **Always Read the screenshot file via the Read tool and describe the pixel content** before declaring a visible change done. DOM `is_visible: True` ≠ rendered pixels show the content. (Receipt: 2026-04-26 Slice 2 build session.)
- **Idempotency over magic.** Every script in `setup/` and `dev/` should be safe to re-run. If state matters, the script either checks-then-acts or no-ops cleanly.
- **Loud errors.** If a script's API call returns an error, surface it. No silent swallowing. (Loud-failure rule per global `C:\Users\baenb\.claude\rules\loud-failure.md`.)
- **No deploy.py yet.** Frappe Cloud cutover is Phase 6. Until then, all "deploy"-like operations live as discrete scripts in `setup/` or `dev/`.
