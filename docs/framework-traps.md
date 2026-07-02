# Framework Traps — Known Adversarial Defaults

**Purpose:** A portable catalog of known adversarial-default behaviors in this client's framework. This file ports cleanly with the repo. Future contractors and clients themselves can read it.

**Update rule:** When you encounter a framework behavior that bites you in a way the framework's documentation doesn't warn about, add an entry. Each entry needs: behavior, mechanism, defense, verification.

---

## How to use this file

- **Before doing substantive work in this codebase**, read this file end-to-end.
- **Before writing a migration, deploy script, or production script**, scan the relevant section.
- **When you discover a new trap**, add an entry. Pull request the addition; do not silently fix.

---

## Section structure

This file is split into two sections:

- **Agency baseline (below)** — traps that apply to every BBC Frappe v15 / ERPNext client. Maintained by the agency template; do not delete entries here. If an entry is wrong, fix it at the template (`Built_by_Cameron/_TEMPLATES/client-repo-gate-kit/docs/framework-traps.md`) and propagate to all client repos.
- **Client-specific traps (Locally Twisted)** — traps observed in this client's build. Listed after the agency baseline. These do not propagate to the template unless separately proposed for promotion.

---

## Agency baseline — Frappe v15 / ERPNext

### Trap 1: Assets stop loading after 5-15 days

**Status:** VERIFIED — GitHub frappe/frappe issue #49955 (open, October 2025)

**Mechanism:** A hash mismatch between `assets.json` and the actual built asset files causes ERPNext to serve stale CSS/JS in production. No clear trigger has been identified by the Frappe team. The site looks fine for up to 15 days, then loses all styling at once.

**Defense:** Asset hash comparison check in `scripts/deploy.py` Gate 4 (Visual screenshot). If the screenshot shows unstyled HTML, the asset bundle is broken.

**Verification:** Run `python scripts/deploy.py --dry-run` after a fresh `bench build`. The post-deploy screenshot gate will fail loudly if styles are not loading.

---

### Trap 2: Stripe charges complete without invoice creation

**Status:** VERIFIED — GitHub frappe/webshop issue #204 (open)

**Mechanism:** A Stripe payment completes successfully. ERPNext's `make_invoice()` is called and fails on a missing `taxes` field. The error itself fails on a 140-character log title limit. The customer sees a successful payment confirmation. Jeff sees no invoice. The money is in Stripe; the order is not in ERPNext.

**Defense:** Post-payment invoice verification step in `scripts/verify/smoke_forms.py` (or a dedicated `smoke_payments.py` if checkout is wired). After a test Stripe payment, query the ERPNext Sales Invoice list for the matching invoice within 30 seconds. Fail loudly if not found.

**Verification:** Make a test Stripe payment in test mode after deployment; navigate to ERPNext Accounts > Sales Invoices; verify the test invoice exists.

---

### Trap 3: Scheduler can freeze with no error output

**Status:** VERIFIED — GitHub frappe/frappe issue #37490 (open). Affects v15.99.0+.

**Mechanism:** The Frappe background scheduler can freeze. All scheduled jobs stop. Email queue stops draining. Automations stop firing. There is no error output; the scheduler appears healthy until you check the Recent Logs.

**Defense:** Weekly manual check of Settings > Scheduled Jobs > Recent Logs in ERPNext UI. Set a calendar reminder until a monitoring script is built. Long-term: add a heartbeat job that writes a timestamp to a known DocType every 5 minutes; alert if the timestamp ever falls more than 15 minutes behind.

**Verification:** Navigate to Settings > Scheduled Jobs in ERPNext; view Recent Logs; verify there are successful runs within the last 24 hours.

---

### Trap 4: `bench migrate` fixture sync skips records by `modified` timestamp

**Status:** PROBABLE — mechanism matches Frappe design patterns; primary source confirmation via Frappe source code reading is pending.

**Mechanism:** When `bench migrate` syncs fixture data, it compares the `modified` timestamp on the fixture file against the `modified` timestamp on the live DB record. If the DB record is newer, the fixture is silently skipped. This means: if anyone has edited the record via the ERPNext UI, future fixture updates will not apply.

**Defense:** When updating a fixture for a record that may have been edited in the UI, explicitly bump the `modified` timestamp in the fixture file to a value newer than the DB record. After the migrate, verify the field actually updated.

**Verification:** After `bench migrate`, query the affected record in ERPNext and verify the field shows the new value.

---

### Trap 5: Frappe Web Forms are being deprecated

**Status:** VERIFIED — Frappe discuss thread; multiple "won't fix" closures across v13-v15.

**Mechanism:** The Frappe Web Form DocType is being deprecated. Bugs filed against it (blank page display, allow-incomplete-forms behavior, silent submission failures) are receiving no response or being closed as "won't fix."

**Defense:** Do not build customer-facing forms using the Web Form DocType. Build them as custom HTML/Jinja pages with REST API submission, AJAX error handling, and the three-audience loud-failure check (user sees error, developer gets logged trace, monitor fires on silence).

**Verification:** Audit this repo for any `Web Form` DocType files: `find . -path '*doctype/web_form*'`. Should return zero results for any customer-facing form.

---

### Trap 6: `bench build` cannot run inside production containers

**Status:** VERIFIED — `frappe_docker` FAQ.

**Mechanism:** Running `bench build` inside a running production container causes asset path corruption that requires `--force-recreate` to recover.

**Defense:** Build assets via CI or a dedicated build step before container start. Never run `bench build` against a running production container.

**Verification:** `scripts/deploy.py` does not call `bench build` against a running prod container; it calls it as a pre-deploy step against a build target.

---

### Trap 7: Customize Form vs Custom App can conflict; DB version wins

**Status:** VERIFIED — Frappe docs.

**Mechanism:** Changes made via ERPNext UI > Customize Form live in the database as `Property Setter` records. Changes made in a Custom App live in code. They can disagree. The DB Property Setter wins.

**Defense:** Choose one path per DocType and never mix. For DocTypes BBC owns, all changes go in code. For DocTypes the client/Jeff edits, the changes are theirs to manage in the UI.

**Verification:** When a customization "doesn't apply" after deploy, query for `Property Setter` records on the affected DocType: `frappe.get_all("Property Setter", filters={"doc_type": "X"})`. If results exist, the UI version is overriding code.

---

### Trap 8: SocketIO origin mismatch breaks real-time UI

**Status:** VERIFIED — `frappe_docker` FAQ.

**Mechanism:** Custom domain configurations without proper nginx SocketIO proxy cause real-time UI updates (notifications, live dashboards) to fail silently. The site loads; only the real-time channel is broken.

**Defense:** Verify nginx config includes SocketIO proxy block before going live. The `frappe_docker` upstream provides a working example.

**Verification:** Open ERPNext in a browser, trigger an action that should produce a real-time UI update (e.g., a notification), and confirm it appears.

---

## Client-specific traps (Locally Twisted)

These have been observed in the LT build itself. They are receipts, not predictions.

### Trap LT-1: `.web-footer` band-aid `!important` chains masquerading as a framework constraint

**Status:** OBSERVED — receipt: 2026-04-26 Slice 2 build session; resolved entry in `lessons-learned.md`; `apps/locally_twisted/locally_twisted/public/css/lt-theme.css` lines 477-526 (the chains that need stripping).

**Mechanism:** During Slice 2, a footer rendering issue was observed (`.web-footer` computed bounding box ~305px while child `.container` was 755px — Soft-Blue band cut off after one row). The responsible instance attributed the gap to a Frappe framework `max-height` constraint and added `!important` chains to LT's `lt-theme.css` to "win the cascade." The actual cause was the LT theme's earlier `!important` overrides interacting with body's flex sticky-footer pattern. There is no max-height rule in Frappe's `footer.scss`. The fix is to remove the band-aid chains and override the footer Jinja partials at `apps/locally_twisted/locally_twisted/templates/includes/footer/`, not to add more CSS overrides.

**Defense:** Before adding `!important` to override Frappe styling, read the actual Frappe SCSS source inside the running container (`docker exec -it <frappe-svc> cat /home/frappe/frappe-bench/apps/frappe/frappe/public/scss/website/footer.scss`). If the rule you're fighting is not actually there, the friction is coming from your own code.

**Verification:** `grep -rn "!important" apps/locally_twisted/locally_twisted/public/css/` should return zero results once Slice 2 is redone correctly. GL's directive 2026-04-26: *"Work WITHIN Frappe and ERPNext, don't fight them."*

---

### Trap LT-2: nginx Origin patch is non-persistent across container recreation

**Status:** OBSERVED — receipt: HANDOFF.md 2026-04-26 ("nginx Origin patch... Re-applied this session post-recreate"); fix script at `scripts/fix/patch_nginx_socketio_origin.py`.

**Mechanism:** A correct browser-direct localhost setup requires nginx to receive the right `Origin` header for SocketIO upgrades. The default `frappe_docker` nginx config does not pass it through. The patch is currently applied via `docker exec` editing the container's nginx config — which means the patch is lost on every `docker compose up --force-recreate`, every container respawn, and every image upgrade. Without the patch, real-time UI features fail silently against `http://localhost:8081`.

**Defense:** After every `docker compose up --force-recreate` (or any container respawn): run `python scripts/fix/patch_nginx_socketio_origin.py`. Long-term: replace the docker-exec patch with a docker-compose override that bind-mounts a custom `frappe.conf` containing the pass-through line. Tracked as P2 in `locally-twisted-queue.md` ("Persist the nginx Origin patch...").

**Verification:** After container respawn, `curl -I http://localhost:8081/socket.io/` should return a 200 or 101 (not 502). `Access-Control-Allow-Origin: http://localhost:8081` should appear on responses.

---

### Trap LT-3: `/book` form silent-failure pattern (the founding receipt for the loud-failure rule)

**Status:** VERIFIED — receipt: prior legacy_source platform incident 2026-04-22 ("the /book form bug"). Documented in global `loud-failure.md` rule. The smoke test gate (`scripts/verify/smoke_forms.py`) exists specifically to prevent this on the new ERPNext build.

**Mechanism:** On the prior legacy_source platform, customers filled in the booking form. legacy_source's website form widget crashed on init with `TypeError: Cannot read properties of null`. The browser fell back to a plain HTML POST. The server returned `text/html` with an empty body. The customer saw a blank white page. No CRM lead was created. No acknowledgment email fired. Jeff was not notified. The form dropped customer submissions for ~10 days before Jeff asked about missing leads. **None of this was visible to Jeff until he asked** — every customer who hit this form had no way to reach him during the silence.

**Defense:** Build the new `/book` form (Phase 2 — Lead Intake) as custom HTML/Jinja with REST API submission, AJAX error handling, and the three-audience loud-failure check (user-visible error state, developer log entry, monitor alert). NEVER use the deprecated Frappe Web Form DocType (Trap 5 above). On the day the form ships, exercise `python scripts/verify/smoke_forms.py --base-url <url> --form-path /book` (full submission, not `--shape-only`) and confirm it creates a Lead in the backend.

**Verification:** After deploy, `python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --form-path /book` exits 0 and reports `BACKEND VERIFIED — record exists`. In ERPNext UI: navigate to CRM > Lead and find the `SMOKE-TEST-<timestamp>` record created within the last 5 minutes.

---

## Adding a new trap to this file

When you find a framework trap not listed above:

1. **Add an entry** with the same structure as those above (Status, Mechanism, Defense, Verification).
2. **Mark Status honestly:**
   - `VERIFIED` — you have a primary source (GitHub issue, official docs, framework source code) confirming it
   - `PROBABLE` — mechanism matches known patterns but primary source confirmation is pending
   - `OBSERVED` — you saw it happen but cannot yet point at a primary source
3. **Open a PR.** The trap catalog grows by review, not by silent edits.
4. **Propose a defense and a verification.** A trap entry without a defense is incomplete.
5. **Decide section:** is this client-specific (append to the LT section above), or does it apply to every BBC Frappe client (propose promotion to the agency template)?

---

*This file lives in the client's repo. It travels. Future contractors thank you for keeping it accurate.*
