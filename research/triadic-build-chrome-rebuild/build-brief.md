# Build Brief — Chrome Rebuild (Phase 1 of Mirror Rebuild)

**Date:** 2026-04-30
**Orchestrator:** Opus 4.7 (autonomous run; GL asleep, pre-authorized)
**Skill:** triadic-construction-v2
**Phase 0 gate:** GL pre-authorized autonomous chrome rebuild per session directive *"using capabilities, I want you to rebuild the whole site... use agent teams use the triadic build team."*

---

## What we're building

The persistent header + footer chrome for Locally Twisted's ERPNext site, Hetzner-faithful in structure and content. Replaces the current intermediate-state navbar.html and footer.html. Overhauls lt-theme.css (replaces ~340 lines of dead code targeting Frappe's native chrome that no longer renders). Adds 3-panel mega menus, newsletter strip, megamenu JS, newsletter JS + endpoint + DocType.

**Mirror reference:** `_resources/retired-source-mirror/pages/index.html` (header lines ~286-635, footer lines ~1111-1223). **Inventory reference:** `_resources/retired-source-mirror/INVENTORY.md` sections 2 + 3.

**Architectural decisions logged 2026-04-30 in `MIRROR-REBUILD-PLAN.md` Research Notes** — both reversible:
- **Decision A** — Mega menus populated via template-level grouping over the existing flat 11-Item-Group hierarchy. NOT restructuring the catalog.
- **Decision B** — Category URLs stay `/shop-items/<slug>` (ERPNext native). Redirects from `/shop/category/<slug>` added separately.

---

## Team composition

3 builders + 3 reviewers (3+3 = 6 agents). Multi-domain feature size.

### Builders (parallel, distinct file ownership)

| Builder | Domain | Files (strict ownership) |
|---|---|---|
| **Builder Jinja** | HTML/Jinja templates + Python context | `apps/locally_twisted/locally_twisted/templates/includes/navbar/navbar.html` (REPLACE wholesale), `apps/locally_twisted/locally_twisted/templates/includes/footer/footer.html` (REPLACE wholesale), `apps/locally_twisted/locally_twisted/navbar_context.py` (EXTEND only) |
| **Builder CSS** | Stylesheet | `apps/locally_twisted/locally_twisted/public/css/lt-theme.css` (REWRITE — replace dead blocks + add chrome blocks) |
| **Builder JS** | Client-side scripts + hooks.py asset registration + newsletter endpoint + DocType | `apps/locally_twisted/locally_twisted/public/js/lt-megamenu.js` (NEW), `apps/locally_twisted/locally_twisted/public/js/lt-newsletter.js` (NEW), `apps/locally_twisted/locally_twisted/api/newsletter.py` (NEW), `apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_newsletter_signup/` (NEW DocType, 3 files), `apps/locally_twisted/locally_twisted/hooks.py` (EXTEND `web_include_js` only) |

**File-ownership rule:** No two builders edit the same file. If a task requires touching another builder's file, the builder STOPS and reports. Orchestrator reassigns.

### Reviewers (parallel, distinct personas; isolated)

| Reviewer | Persona | Focus |
|---|---|---|
| **Reviewer A** | Architect | Structural integrity, CSS architecture, JS pattern coherence, BEM discipline |
| **Reviewer B** | SecOps Analyst | XSS in newsletter form, sanitizer interactions, CSRF, link/redirect safety, prompt injection in `frappe.log_error` |
| **Reviewer C** | Execution Engine | Sequential trace through mega menu open/close, mobile drawer state machine, newsletter submit flow |

---

## Model tiering

| Role | Model | Override applied? |
|---|---|---|
| Orchestrator | Opus 4.7 | (current instance) |
| Builders | Opus 4.7 | default |
| Reviewers | Sonnet 4.6 | default — chrome is not auth/migration/money/calming-engine; no escalation |
| Proxy (Phase 2.5) | Opus 4.7 | mandatory |

---

## API Contract

### Functions / interfaces builders MUST create

**Builder Jinja:**
- `navbar_context.update_website_context(context)` — extend existing function. Must continue to populate `context["shop_categories"]` and `context["shop_root_route"]` (existing). MUST also populate three new keys:
  - `context["mega_special_occasions"]` — list of `{label, route}` dicts representing the "Special Occasions" mega panel's leaf links (Birthdays, Showers, Graduations, Missionary, Get-Well — content-only routes, may not all resolve to real pages yet)
  - `context["mega_holidays_seasons"]` — list of `{label, route, item_group_route}` dicts mapping holiday-themed leafs to Item Groups where applicable
  - `context["mega_what_we_make"]` — list of `{label, route}` dicts referencing the 11 Item Group children of "Shop Items" via their existing `route` field (so links go to `/<route>`)
- All template references to category URLs use `/{{ cat.route }}` (NOT `/shop/category/<slug>`).

**Builder JS:**
- `window.LT.megamenu.init(panelSelector, triggerSelector)` — vanilla JS, no jQuery. Exposes `init`, `openPanel(id)`, `closePanel(id)`, `closeAll()`. Uses `hidden` attribute toggle (NOT class-only). Hover-open desktop with debounce; click-toggle mobile.
- `window.LT.newsletter.submit(email)` — returns a Promise that resolves to `{ok: true, message: "..."}` or `{ok: false, error: "..."}`. Calls `frappe.call('locally_twisted.api.newsletter.signup', {email})`. Sends `X-Frappe-CSRF-Token` header.
- Server endpoint `locally_twisted.api.newsletter.signup(email: str)`:
  - `@frappe.whitelist(allow_guest=True)`, `@rate_limit(limit=10, seconds=60*60)`
  - Validates email format (RFC 5322 light)
  - Creates `LT Newsletter Signup` record (DocType created in this build) with fields `email` (Data, unique, required), `signed_up_at` (Datetime, auto-now), `source_url` (Data, optional)
  - Returns `{ok: True}` or `{ok: False, error: <user-safe message>}`
  - Wraps record creation in try/except + `frappe.log_error` with sanitized payload (no full email in log if validation already passed)
- `LT Newsletter Signup` DocType: 3 files at `apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_newsletter_signup/`:
  - `lt_newsletter_signup.json` (DocType definition)
  - `lt_newsletter_signup.py` (controller — minimal, default Document)
  - `__init__.py` (empty)
- `hooks.py` `web_include_js` extended to include both new JS files with `?v=20260430-1` cache-bust.

### Interfaces builders MUST honor (don't break)

- `web_include_css` line in hooks.py points at `/assets/locally_twisted/css/lt-theme.css?v=YYYYMMDD-N` — Builder 2 bumps the version when CSS changes (current `?v=20260430-3` → next `?v=20260430-4`).
- `installed_apps` global JSON list MUST keep `locally_twisted` LAST. Builder JS must NOT change this.
- Existing `lt-theme.css` rules outside the dead-code blocks (homepage `.lt-home__*`, BTFP `.lt-btfp__*`, contact `.lt-contact__*`, accessibility `.lt-policy__*`, refund-policy `.lt-faq__*`, shop `.lt-shop__*`, product `.lt-product*`) MUST be preserved. Only the chrome-related dead blocks get replaced. Other section CSS stays.
- `apps/locally_twisted/locally_twisted/public/js/lt-guest-cart.js` is loaded via `web_include_js` and exposes `window.LT_CART` — Builder JS must not touch it; just add new files alongside.

### Hard constraints (non-negotiable)

1. **No `!important` in CSS** except: (a) the existing prefers-reduced-motion block (lines ~202-205), (b) the existing `.product-code { display: none !important }` hide for webshop's compiled JS jargon. ALL other `!important` flags in the dead `.navbar.*` and `.web-footer` blocks get removed when those blocks are deleted.
2. **No `data-bs-*` attributes** in HTML — Frappe ships Bootstrap 4-flavored utilities, not BS5. Use BS4 `data-toggle`/`data-target` if Bootstrap component behavior is needed (but prefer custom vanilla JS — already the established pattern).
3. **No `gap-*`, `ms-*`/`me-*`, `g-col-*`, `gx-*`** Bootstrap 5 utility classes — they silently no-op in Frappe's BS4 bundle. Use explicit CSS `gap`, `margin-left`, `margin-right` rules in lt-theme.css instead.
4. **No inline SVG with `<path d=...>` in any CMS-editable field** — Frappe's HTML sanitizer strips SVG path attributes. Real SVG files in `public/icons/` referenced via CSS background-image OR via `<img src>` in templates is fine.
5. **No inline `<style>` blocks in templates** — fold them into lt-theme.css. Specifically: the current `navbar.html` lines ~141-176 inline style block for `.lt-cart-count` MUST be removed and the rules moved into lt-theme.css.
6. **No `font-weight` overrides on heading classes** when the heading uses DM Serif Display (single-weight, weight 400 only). Heading emphasis comes from size, not synthetic-bold weight.
7. **No `color-mix()`** in any SCSS file (we don't use SCSS for chrome but flag for awareness — plain CSS only here).
8. **Loud-failure rule** — newsletter submit must show user-visible error on failure (red banner with phone fallback). Server endpoint logs payload + IP via `frappe.log_error` on exception.
9. **Frappe sanitizer awareness** — anything written to `Website Settings.head_html`, Web Page `main_section`, or any CMS-editable field is sanitized. We're NOT writing to those fields. We're writing to template files in the app, which are NOT sanitized. But Builder Jinja must NOT introduce any code paths that round-trip user content through CMS-editable fields.
10. **Frappe v15 + Bootstrap 4 utilities only**. Confirmed conventions in `Built_by_Cameron/capabilities/recipes/frappe-conventions.md`.
11. **Loud-failure rule for newsletter** is non-negotiable per `capabilities/recipes/fail-loud-operating-law.md` and `frappe-form-integrity` skill.

### Post-build invariants (must remain true)

- `localhost:8081/` returns HTTP 200 and renders the homepage with the new chrome.
- `localhost:8081/book` continues to return HTTP 200 (chrome change must not break unrelated routes).
- Frappe website cache cleared after the build (`scripts/dev/clear_website_cache.py`).
- Backend container restarted if `hooks.py` changed (Builder JS bumps `web_include_js`, requires restart).
- All existing `lt-theme.css` rules outside the replaced blocks render unchanged.
- `installed_apps` list still has `locally_twisted` LAST.
- No new `!important` flags introduced beyond the documented exceptions.
- No console errors on `/` page load (Playwright check happens in Phase 4 verification).

---

## Required skills (each builder MUST invoke before editing)

The agency gate fires on edits to Frappe app files. Each builder MUST invoke the relevant safety skill BEFORE their first Edit/Write:

- **Builder Jinja:** invoke `frappe-form-integrity` (covers form/template safety).
- **Builder CSS:** invoke `frappe-asset-pipeline` (covers stylesheet pipeline).
- **Builder JS:** invoke BOTH `frappe-form-integrity` (newsletter is a form) AND `frappe-asset-pipeline` (hooks.py asset registration).

---

## Test command

For all builders: after their edits, run:

```bash
docker restart locally-twisted-erpnext-v15-backend-1 && sleep 12 && python "/home/guidingl/projects/Built_by_Cameron/_CLIENTS/locally-twisted/scripts/dev/clear_website_cache.py"
```

Then verify routes still load:

```bash
curl -sS -o /dev/null -w "home %{http_code}\n" "http://localhost:8081/"
curl -sS -o /dev/null -w "book %{http_code}\n" "http://localhost:8081/book"
```

If frontend is in 502 (sticky upstream IP after backend restart):

```bash
docker restart locally-twisted-erpnext-v15-frontend-1
```

Reviewers run their own verification per persona.

---

## Build report paths

- Builder Jinja → `research/triadic-build-chrome-rebuild/round-1/builder-jinja-build.md`
- Builder CSS → `research/triadic-build-chrome-rebuild/round-1/builder-css-build.md`
- Builder JS → `research/triadic-build-chrome-rebuild/round-1/builder-js-build.md`

## Review report paths

- Reviewer A (Architect) → `research/triadic-build-chrome-rebuild/review-architect.md`
- Reviewer B (SecOps Analyst) → `research/triadic-build-chrome-rebuild/review-secops.md`
- Reviewer C (Execution Engine) → `research/triadic-build-chrome-rebuild/review-execution.md`
