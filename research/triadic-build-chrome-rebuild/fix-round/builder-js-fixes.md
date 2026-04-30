# Builder JS — Fix Round Build Report

## Date: 2026-04-30
## Builder: Builder JS (Fix Round)

---

### Tasks Completed

---

#### Task A — `lt-megamenu.js` accordion legacy path: `querySelector` → `querySelectorAll`

- **File:** `apps/locally_twisted/locally_twisted/public/js/lt-megamenu.js` lines 434–458
- **Finding addressed:** Architect F004 / Execution F001 (Active Agreement — critical)
- **BEFORE (line 436):**
  ```javascript
  var legacyAccToggle = drawer.querySelector(".lt-header__mobile-accordion-toggle");
  if (legacyAccToggle) { /* single element — only first panel wired */ }
  ```
- **AFTER (lines 438–458):**
  ```javascript
  var legacyAccToggles = drawer.querySelectorAll(".lt-header__mobile-accordion-toggle");
  for (var la = 0; la < legacyAccToggles.length; la++) {
      (function (legacyAccToggle) { /* IIFE per-toggle — all three wired */ }(legacyAccToggles[la]));
  }
  ```
- **Approach:** Changed the legacy accordion fallback path from `querySelector` (singular, finds only first) to `querySelectorAll` with an IIFE loop, matching the pattern already used in the generic data-attribute path (lines 416–432). Each toggle now gets its own closure over its panel reference, so all three mobile accordion sections (Special Occasions, Holidays & Seasons, What We Make) are wired independently.
- **Note on generic path (lines 415–432):** The generic path already uses `querySelectorAll('[data-lt-drawer-accordion-trigger]')` and is correct. After Builder Jinja's fix-round rename of `data-lt-accordion-trigger` → `data-lt-drawer-accordion-trigger`, this path will handle all three panels. The legacy path is the fallback for the pre-fix-round template DOM; fixing it to `querySelectorAll` ensures both paths handle all toggles regardless of which attribute is present.
- **Cache-bust:** `lt-megamenu.js?v=20260430-1` → `?v=20260430-2` in `hooks.py`

---

#### Task B — `lt-newsletter.js` `showError`: preserve `<a href="tel:">` anchor

- **File:** `apps/locally_twisted/locally_twisted/public/js/lt-newsletter.js` lines 157–173
- **Finding addressed:** Execution F003 (important)
- **BEFORE (line 170):**
  ```javascript
  div.textContent = msg;  // strips ALL child nodes including the tel: anchor
  ```
- **AFTER:** `showError` now has two code paths:
  1. **Pre-built container path** (normal — Jinja built the footer): finds the `.lt-footer-newsletter__error-text` inner span, locates its first `Text` node and updates only that node's `.data`, leaving the sibling `<a href="tel:+18012850860">` anchor intact and clickable.
  2. **Fallback path** (no container in DOM): builds the error container from scratch using `document.createElement` + `document.createTextNode` + explicit `<a>` construction — never `textContent` on a parent that might have children.
- **Invariant held:** `<a href="tel:+18012850860">(801) 285-0860</a>` is present and clickable in the rendered error state on mobile. Loud-failure rule phone fallback is preserved.
- **Cache-bust:** `lt-newsletter.js?v=20260430-1` → `?v=20260430-2` in `hooks.py`

---

#### Task C — `api/newsletter.py` hash stability: `hash(email)` → `hashlib.sha256`

- **File:** `apps/locally_twisted/locally_twisted/api/newsletter.py` line 112
- **Finding addressed:** SecOps F002 / Execution F007 (important)
- **BEFORE:**
  ```python
  email_hash=hash(email),
  ```
- **AFTER:**
  ```python
  email_hash=hashlib.sha256(email.encode("utf-8")).hexdigest()[:16],
  ```
- **Also added:** `import hashlib` at module top (line 28).
- **Approach:** Python's built-in `hash()` is randomized per-process via `PYTHONHASHSEED` (PEP 456, enabled by default since Python 3.3). After any container restart the same email produces a different hash value — cross-restart log correlation is impossible. `hashlib.sha256(...).hexdigest()[:16]` is deterministic, collision-resistant for this use case, and not reversible without brute-force.

---

#### Task D — `api/newsletter.py` rate limit: defeat X-Forwarded-For bypass

- **File:** `apps/locally_twisted/locally_twisted/api/newsletter.py` line 50
- **Finding addressed:** SecOps F001 (important)
- **BEFORE:**
  ```python
  @rate_limit(limit=10, seconds=60 * 60)
  ```
- **AFTER:**
  ```python
  @rate_limit(limit=10, seconds=60 * 60, key="email", ip_based=False)
  ```
- **Rate-limit source verified:** Read `/home/frappe/frappe-bench/apps/frappe/frappe/rate_limiter.py` lines 105–170 from running container. Confirmed:
  - `ip_based=False` → `ip = None`
  - `key="email"` → `user_key = frappe.form_dict.get("email", "")`
  - `identity = user_key` (email value, since ip is None and key is set)
  - Cache key: `rl:locally_twisted.api.newsletter.signup:<email>`
- **Option chosen:** Option A (email-keyed). Option B (nginx-level XFF strip) is the higher-leverage fix — it would also protect `book.py`, `checkout.py`, `btfp.py` which share the same IP-based rate limit vulnerability. **Option B is flagged as an ops/infra follow-up** (out of JS domain; touches nginx container config).
- **Trade-off documented:** Email-keyed limiting accepts a "10/hr enumeration" trade-off — an attacker can determine whether a specific email address has hit its rate limit. For newsletter signup this is acceptable (no sensitive state is revealed).
- **Rate-limit test result:** 11 requests with identical email → requests 1–10 returned HTTP 200, request 11 returned HTTP 429. ✅

---

#### Task E — `scripts/verify/smoke_forms.py` newsletter smoke test

- **File:** `scripts/verify/smoke_forms.py`
- **Finding addressed:** SecOps F008 / Execution F009 (loud-failure rule — monitor channel was missing)
- **What was added:**
  - `smoke_newsletter(base_url)` function: POSTs a unique `smoke-newsletter-<timestamp>@bbc-test.invalid` email to the signup endpoint, verifies HTTP 200 + `{ok: true}` response, confirms record existence via the idempotency path (double-POST returning "already on list"), attempts cleanup via REST DELETE with `LT_ADMIN_PASSWORD` env var (best-effort, warn on skip).
  - `_find_newsletter_record(base_url, email)`: uses the endpoint's idempotency check as a proxy for DB verification (avoids requiring Admin credentials just to confirm existence).
  - `_delete_newsletter_record(base_url, record_name)`: best-effort DELETE via Frappe REST API using `LT_ADMIN_PASSWORD` env var if available.
  - `main()` updated to run both tests with `--skip-book` / `--skip-newsletter` flags for selective CI runs.
  - Added `import json`, `import urllib.error`, `import urllib.parse`, `import urllib.request` to support direct HTTP calls (no Playwright dependency for the API test).
- **Smoke test result:**
  ```
  [SMOKE] Newsletter endpoint: http://localhost:8081/...signup
          HTTP status: 200
          API response OK: Thanks — we'll be in touch.
          BACKEND VERIFIED — record '(confirmed via idempotency ...)' exists
          WARN — could not delete test record (no LT_ADMIN_PASSWORD set)
          SMOKE TEST PASS — newsletter
  [SMOKE] All smoke tests PASSED.
  ```
  Exit code 0 when run with `--skip-book`. ✅

---

### Tasks Not Completed

None. All five tasks (A–E) completed.

---

### Cross-Domain Dependencies

**Builder Jinja coordination (Task A):**
The generic accordion path at `lt-megamenu.js` line 415 queries `[data-lt-drawer-accordion-trigger]`. Builder Jinja's fix-round task #4 renames template accordion attributes from `data-lt-accordion-trigger` → `data-lt-drawer-accordion-trigger`. After that rename, the generic path handles all three panels and the legacy path is a no-op (finds no `.lt-header__mobile-accordion-toggle` elements). Both paths are safe regardless of which attribute is present in the DOM.

**No other cross-domain dependencies.**

---

### Decisions Made

1. **Task A — which path to fix:** Fixed the legacy path (`querySelector` → `querySelectorAll`) rather than changing the generic path's attribute query. The generic path already has the correct attribute name for the post-Builder-Jinja DOM. The legacy path needed the plural fix to cover the pre-fix-round template in the interim.

2. **Task B — how to preserve the tel: anchor:** Chose the "update first Text node in inner span" approach rather than innerHTML (XSS surface) or full DOM reconstruction (would discard the anchor's event listeners if any). The span structure from `footer.html` lines 91–95 is stable and known — the first `Text` node contains the user-visible message text; the `<a>` anchor is a sibling child. Updating `.data` on the text node is the least-destructive intervention.

3. **Task D — Option A vs B:** Chose Option A (email-keyed, `ip_based=False`) as it is entirely within the JS/Python domain and addresses the immediate finding. Documented Option B (nginx XFF strip) as a follow-up ops/infra task with a note that it is the higher-leverage fix covering other endpoints.

4. **Task E — verification strategy:** Used the idempotency path (double-POST) as the DB verification proxy rather than requiring Admin credentials for the List API. This keeps the smoke test self-contained and runnable without credentials. The trade-off is we get a description string rather than the real docname for cleanup — documented as a warn, not a fail.

---

### Test Results

```
# HTTP smoke checks
home 200       ✅
book 200       ✅
megamenu.js v=20260430-2: 200   ✅
newsletter.js v=20260430-2: 200 ✅

# Newsletter endpoint first call
{"message":{"ok":true,"message":"Thanks — we'll be in touch."}}  ✅

# Rate-limit test (11 requests, same email)
Requests 1–10: HTTP 200   ✅
Request 11:    HTTP 429   ✅ (email-keyed rate limit fired correctly)

# Newsletter smoke test (--skip-book)
Exit code: 0 — SMOKE TEST PASS  ✅

# Full smoke suite
Newsletter: PASS  ✅
/book Playwright: FAIL (pre-existing — submit button selector too generic for 3-form page)
  Note: /book returns HTTP 200 and has 3 submit buttons; the Playwright harness
  uses .first on a generic selector that doesn't disambiguate the main booking
  form from the two header search/nav forms. This failure predates this fix round
  and is tracked separately.
```

---

### Self-Review Concerns

1. **Task B edge case — `Node.TEXT_NODE` availability:** Used `Node.TEXT_NODE` constant (value 3). This is available in all browsers that support ES5+ and is safe in Frappe's Bootstrap 4 / vanilla JS environment. Belt-and-suspenders: the loop also guards with `nodes[n].nodeType === Node.TEXT_NODE` so non-text nodes are skipped.

2. **Task E — smoke test cleanup note for ops:** Test records (`smoke-newsletter-<timestamp>@bbc-test.invalid`) accumulate in the `LT Newsletter Signup` DocType on each smoke run unless `LT_ADMIN_PASSWORD` is set in the CI environment. Set `LT_ADMIN_PASSWORD=admin` (or the actual admin password) in the CI environment to enable automatic cleanup. On the local dev stack these are harmless (not real email addresses) but should be purged before production cutover.

3. **Option B follow-up (ops/infra):** Nginx-level `X-Forwarded-For` strip in the `frappe_docker` nginx config (`proxy_set_header X-Forwarded-For ""` or equivalent) would protect all rate-limited endpoints. This is the correct fix for production hardening. Tracked here as a reminder for the infrastructure pass.

4. **`/book` Playwright smoke test pre-existing failure:** Not introduced by this fix round. The `/book` page has 3 `<form>` elements (header search, main booking form, possibly a secondary form). The existing smoke harness uses `.first` on `button[type='submit'], input[type='submit']` which finds the wrong button. Fix in a separate pass — add a more specific selector like `form#lt-book-form button[type='submit']` or `form[data-lt-book] button[type='submit']`.
