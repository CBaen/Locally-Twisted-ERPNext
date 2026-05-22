---
id: lt-frappe-erpnext-quirks-library
name: LT Frappe ERPNext Quirks Library
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted Frappe and ERPNext implementation quirks that repeatedly cause false debugging paths
currently_true: unknown
verification_level: 1
last_verified: 2026-05-22
evidence_quality: mixed
successful_uses: 0
failed_uses: 0
regressions: 0
depends_on:
  - large-source-document-intake
  - fail-loud-operating-law
used_by: []
tags:
  - Locally Twisted
  - Frappe
  - ERPNext
  - debugging
  - codegen
---

# LT Frappe ERPNext Quirks Library

Use this as a candidate triage card for recurring LT framework traps.

## What It Does

Keeps known LT Frappe/ERPNext gotchas in one short card so an agent can run a
direct check before changing code.

## When To Reach For It

Use this when a symptom repeats from old LT sessions and you suspect a framework
or stack behavior mismatch.

## How To Use It

1. Match the symptom to an entry.
2. Run the direct check command first.
3. If a verifier exists, run it before claiming the fix.
4. Apply the guardrail in the owning recipe/failure lane.
5. If the entry is marked historical, reverify in the current stack before use.

## No-Monolith Split Rule

This card is a triage index, not a long-form history dump. Keep each entry to:
status, symptom, root cause, source/evidence, direct check/verifier command,
guardrail, and owner link. Move deep receipts to workstreams, lessons, or
dedicated failure cards.

## Quirk Entries

### 1) Web Page body looks blank even though the record saved

- Status: historical claim - verify before use.
- Symptom: Web Page title renders, but article/body is empty.
- Root cause: `content_type` routes output to a specific field; HTML pages read
  `main_section_html`, Rich Text pages read `main_section`.
- Source / evidence:
  `lessons-learned.md` section `2026-04-26 (Slice 2 build) - Frappe / ERPNext quirks discovered while building the website shell` (`content_type` entry).
- Direct check command:
  ```powershell
  docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute frappe.client.get_value --kwargs "{'doctype':'Web Page','filters':{'route':'contact'},'fieldname':['name','content_type','main_section','main_section_html']}"
  ```
- Verifier command: none currently dedicated.
- Guardrail: when writing page fixtures/seeds, set `content_type` explicitly and
  assert the expected body field is non-empty.
- Owner card:
  [large-source-document-intake](large-source-document-intake.md)

### 2) Header/footer parent menu rows throw validation errors

- Status: historical claim - verify before use.
- Symptom: save/update fails with parent row errors for top bar or footer rows.
- Root cause: parent rows that have children must exist in-table and must not
  carry a destination URL.
- Source / evidence:
  `lessons-learned.md` section `2026-04-26 (Slice 2 build)` (`Top Bar Item parent rows` and `Footer Items` entries).
- Direct check command:
  ```powershell
  python scripts/verify/nav_ia.py
  ```
- Verifier command:
  ```powershell
  python scripts/verify/smoke_shop.py
  ```
- Guardrail: model parent rows as label-only grouping rows (`url=""`), with URLs
  on child rows only.
- Owner card:
  [frappe-public-nav-business-route-contract](frappe-public-nav-business-route-contract.md)

### 3) Inline SVG icons vanish in CMS-editable HTML fields

- Status: historical claim - verify before use.
- Symptom: icon wrappers render, but `<path d="...">` data is stripped.
- Root cause: Frappe sanitizer removes risky inline SVG content in CMS fields.
- Source / evidence:
  `lessons-learned.md` section `2026-04-26 (Slice 2 build)` (`Frappe HTML sanitizer strips inline SVG` entry).
- Direct check command:
  ```powershell
  rg -n "<path d=|navbar-toggler-icon|icon-menu" apps/locally_twisted/locally_twisted/templates apps/locally_twisted/locally_twisted/public
  ```
- Verifier command:
  ```powershell
  npm run test:layout-fit
  ```
- Guardrail: use file-based SVG assets in app `public/icons` and reference them
  by CSS or template includes.
- Owner card:
  [lt-brand-style-guide-consolidation](lt-brand-style-guide-consolidation.md)

### 4) CSS changes in `head_html` do not consistently win

- Status: historical claim - verify before use.
- Symptom: rules appear in the page source, but bundled styles still override.
- Root cause: `head_html` styles load early and can lose cascade precedence.
- Source / evidence:
  `lessons-learned.md` section `2026-04-26 (Slice 2 build)` (`head_html styles load BEFORE Frappe bundled stylesheets` entry) and `AGENTS.md` Frappe rule `Avoid head_html CSS injection`.
- Direct check command:
  ```powershell
  rg -n "head_html|web_include_css|website_theme_scss" apps/locally_twisted/locally_twisted/hooks.py AGENTS.md
  ```
- Verifier command:
  ```powershell
  npm run test:container-contract
  ```
- Guardrail: keep production styling in app-managed assets (`web_include_css` or
  `website_theme_scss`) and use `head_html` only for narrow temporary fallback.
- Owner card:
  [frappe-public-container-contract](frappe-public-container-contract.md)

### 5) Mobile menu icon CSS targets do not work

- Status: historical claim - verify before use.
- Symptom: `.navbar-toggler-icon` rules do nothing on LT/Frappe public pages.
- Root cause: Frappe renders an SVG/use-based toggler, not Bootstrap's usual
  `.navbar-toggler-icon` span.
- Source / evidence:
  `lessons-learned.md` section `2026-04-26 (Slice 2 build)` (`navbar-toggler markup` entry).
- Direct check command:
  ```powershell
  python scripts/verify/nav_ia.py
  ```
- Verifier command:
  ```powershell
  npm run test:interactive-layout
  ```
- Guardrail: style `.navbar-toggler` and hide/replace its inner SVG intentionally
  when custom icon treatment is required.
- Owner card:
  [frappe-public-nav-business-route-contract](frappe-public-nav-business-route-contract.md)

### 6) App imports fail after container recreate

- Status: historical claim - verify before use.
- Symptom: backend/worker services start, but app import raises
  `ModuleNotFoundError` for `locally_twisted`.
- Root cause: older bind-mount/editable-install workflow could lose install
  state after recreate; current stack may differ.
- Source / evidence:
  `lessons-learned.md` section `2026-04-26 (Slice 2 build)` (`Editable pip install...` entry),
  with architecture correction in `locally-twisted-decisions.md` `2026-04-30 (late evening) - Container reversion...`.
- Direct check command:
  ```powershell
  docker exec locally-twisted-erpnext-v15-backend-1 python -c "import locally_twisted; print('ok')"
  ```
- Verifier command:
  ```powershell
  python scripts/verify/nav_ia.py
  ```
- Guardrail: treat this as a historical trap until reverified under the current
  custom-image stack; if it reappears, capture it as a dedicated failure card.
- Owner card:
  [failures/README](../failures/README.md)

### 7) Webshop build looks done but frontend still serves broken assets

- Status: rechecked in current LT stack.
- Symptom: build command succeeds, but customer routes still show missing/mismatched
  JS/CSS assets.
- Root cause: shared asset map and per-container public files drift when build is
  done in the wrong service context.
- Source / evidence:
  `CODING-HANDOFF.md` Webshop asset-map correction note and `workstreams/shop.md`
  Webshop build-path receipt (frontend/nginx-serving container last).
- Direct check command:
  ```powershell
  python scripts/verify/smoke_shop.py
  ```
- Verifier command:
  ```powershell
  npm run test:website-verify
  ```
- Guardrail: execute the final Webshop build in the frontend-serving path,
  clear `assets_json`/site cache, and recheck console/network state.
- Owner card:
  [frappe-sitewide-visual-overhaul](frappe-sitewide-visual-overhaul.md)

### 8) Logged-in website pages can load without the CSRF token

- Status: rechecked in current LT stack.
- Symptom: category pages return `200`, but Webshop startup calls log
  `POST / 400 (BAD REQUEST)` from `show_cart_navbar` or
  `get_item_filter_data` after the same browser has been logged into Desk.
- Root cause: LT's custom `templates/base.html` must preserve Frappe's
  `<!-- csrf_token -->` marker. Frappe's website renderer replaces that marker
  with `frappe.csrf_token = "..."`; without it, logged-in website pages do not
  send the `X-Frappe-CSRF-Token` header that `frappe.call` expects.
- Source / evidence:
  `workstreams/ecommerce-break-lab-2026-05-21.md` incident note for
  Webshop startup POST 400s and stale hashed asset.
- Direct check command:
  ```powershell
  npm run test:public-network
  ```
- Verifier command:
  ```powershell
  npm run test:public-network
  ```
- Guardrail: keep the marker in the LT base template, clear website/asset
  caches after template edits, and keep the logged-in Desk-session Webshop CSRF
  regression in `scripts/verify/public_network_integrity.spec.js`.
- Owner card:
  [frappe-sitewide-visual-overhaul](frappe-sitewide-visual-overhaul.md)

## Add A New Quirk

For each new entry, include:

- status (`rechecked`, `candidate`, or `historical claim - verify before use`)
- symptom in plain language
- true root cause
- exact source/evidence pointer
- direct check command and verifier command (or `none`)
- guardrail fix that prevents silent recurrence
- owner recipe or failure-card link

If uncertain, keep it as historical claim and do not present it as verified.

## Source Receipts

- `lessons-learned.md` section `2026-04-26 (Slice 2 build) - Frappe / ERPNext quirks discovered while building the website shell`
- `CODING-HANDOFF.md` notes around Webshop build targeting, cache clear flow, and verifier expectations
- `locally-twisted-decisions.md` 2026-04-30 container architecture correction
