# Locally Twisted — Work Queue

Current work only. **When an item is completed, DELETE it from this file.** Git tracks completion history. Queues are not for history.

Format: `- [priority] description — context / blocking notes`

LT-specific work only. Cross-client / agency-wide work lives at `Built_by_Cameron/built-by-cameron-queue.md`.

---

## Active

### Phase 1 — Customer site + storefront (the proof point)

See `.planning/phases/01-customer-site-and-storefront/PLAN.md` for the full slice list. Highlights:

- [DONE 2026-04-26] **Slice 1 — Brand foundation.** Style-guide tokens installed; theme CSS now served by the `locally_twisted` custom Frappe app at `/assets/locally_twisted/css/lt-theme.css` (registered via `web_include_css` in `hooks.py`). Source at `apps/locally_twisted/locally_twisted/public/css/lt-theme.css` (~21 KB).
- [P0 — READY FOR REDO] **Slice 2 — Header + footer.** Visual state still broken-honest, but the path forward is fully unblocked (webshop installed durably + framework verified + `.web-footer` height "constraint" resolved as a band-aid problem, not a framework bug). **Redo plan:**
  1. Strip `!important` chains from `apps/locally_twisted/locally_twisted/public/css/lt-theme.css` (specifically the `.web-footer` block lines 477-503 and `.web-footer ul/li/footer-group` blocks 505-526). They were band-aids around the wrong problem.
  2. Create override Jinja partials at `apps/locally_twisted/locally_twisted/templates/includes/footer/footer.html` (and `footer_grouped_links.html`, `footer_info.html`, `footer_logo_extension.html`) replicating the approved Odoo structure: two-tier centered-logo header, 3-column footer with hours block, 3 social icons (no Twitter), centered brand block.
  3. Same pattern for navbar — override `apps/locally_twisted/locally_twisted/templates/includes/navbar/navbar.html`.
  4. After every edit: `python scripts/dev/clear_website_cache.py`.
  5. Verify with `python scripts/verify/playwright_home_screenshot.py` + Read the screenshot file before declaring done.
  Reference: `Built_by_Cameron/.claude/capabilities/recipes/frappe-conventions.md` "Approved LT structure" table.
- [P0] **Slice 3 — Landing page.** Partially blocked on real photography sourcing. Should not start until Slice 2 is genuinely complete.
- [P0] **Slice 4 — Balloon Twisting + Face Painting service page.** Carry-forward content.
- [P0] **Slice 5 — Contact page.** Brief about summary embedded.
- [P0] **Slice 6 — Accessibility + Refund Policy + FAQ pages.** Blocked on accessibility statement decision (see `.planning/decisions/accessibility-statement.md`).
- [P0] **Slice 7 — Products listing.** Blocked on header navigation decision (URL structure depends on it).
- [P0] **Slice 8 — Individual product pages.** Variant pricing must work.
- [P0] **Slice 9 — Cart + checkout shell.** Stripe stubbed until Phase 4.

### Open iterations on already-built Lead schema (carried into Phase 2)

- [P1] **Inspiration Photos thumbnail UX decision.** Frappe blocks `in_list_view` on Attach Image AND Image fieldtypes in child tables. GL hasn't picked among: (a) click-to-expand (current state), (b) Frappe Client Script for inline gallery rendering, (c) drop child table for built-in attachments sidebar. Resume after GL chooses.
- [P1] **GL's "this is one Lead!" realization.** GL was thinking each tab was a Lead category; reality is sections of one Lead form. GL hasn't said what they actually wanted to model differently. Don't redesign without their explicit direction. Resume conversation when GL is ready.
- [P0] **Connect the missing Inspiration Photos Table field.** The `LT Lead Photo` child DocType exists and the Section Break exists, but the Table field that connects them was never created — iter 4's step F failed silently. Right now there's an empty section heading on the Lead form. Tied to the thumbnail UX decision above.

### Cross-cutting / housekeeping

- [P2] **Persist the nginx Origin patch across container recreation.** Currently applied via `docker exec` in `scripts/fix/patch_nginx_socketio_origin.py` and only survives until the frontend container is recreated. Cleaner long-term: docker-compose override that mounts a custom `frappe.conf` with the pass-through line. Acceptable to defer since recreations are rare in local dev.

### Gate-kit follow-ups (added 2026-04-26 by gate-kit install — see `docs/GATE-KIT-INSTALL-NOTES.md`)

- [P1] **Add `requirements.txt` at repo root.** Currently `playwright` and `requests` are install-time prerequisites for the gate kit but not declared anywhere. Minimum: `playwright>=1.40` and `requests>=2.31`. Decision needed: where does this file sit relative to bind-mounted Frappe apps and their own deps? Resolves "fresh clone" install friction.
- [P2] **Document the human-review-commit deploy ritual in `scripts/README.md`.** The gate at `scripts/deploy.py:gate_human_review_commit()` refuses to deploy when HEAD's commit message starts with `auto:`. Routine remediation: `git commit --allow-empty -m "review: <pre-deploy summary>"` before running deploy. Add a one-line note to `scripts/README.md` under operational rituals.
- [P2] **Set `STAGING_URL` secret in GitHub repo settings + uncomment the CI form-shape step.** `.github/workflows/ci.yml` lines 35-36 are commented out pending a staging URL. Ships staging-form-shape verification on every PR once enabled. Defer until staging exists.
- [P3] **At cutover (Phase 6): flip `scripts/deploy.py` `CONFIG["site_url"]` and `smoke_test_screenshot_paths`.** Currently `http://localhost:8081`; production URL TBD (likely `https://locallytwisted.com` or new subdomain). TODO comments in code mark both spots.
- [P3] **Wire `/book` smoke test the day Phase 2 ships.** `CONFIG["smoke_test_form_path"] = "/book"` is parked. The form smoke test will FAIL until the form exists; that's expected. Add `/book` to `smoke_test_screenshot_paths` at the same time.


## Blocked

*nothing*

## Waiting on GL

- **Inspiration Photos thumbnail UX** — pick (a)/(b)/(c) from the Lead-schema iteration item above (carries into Phase 2)
- **"This is one Lead" realization** — what did you want to model that you thought was happening? (carries into Phase 2)

*All Phase 1 decision gates resolved 2026-04-26 — see `locally-twisted-decisions.md`.*

## Deferred (intentional, not blocked)

- **Custom Frappe app scaffolding for LT.** When there's a critical mass of customizations worth packaging.
- **Frappe Cloud signup + production deployment.** Phase 6 (cutover).
- **Reading Jeff's UI-edited content from any prior platform's database.** Not applicable — the prior platform never went live to customers, so there's no production-only content to migrate.
- **Translation of remaining Odoo models** (`res_partner`, `product_template`, `project_task`, `calendar_event`, `hr_expense`, `res_config_settings`, `twilio_service`). These are no longer "translations" under the new framing — the underlying capabilities (customer/contact split, sale order extension, project task customization, calendar event extension, expense tracking, Twilio SMS, settings DocType) get built fresh as part of Phase 2/3/4 when each is needed. The Odoo source files remain reference material in `_resources/`-adjacent inventory, but the work is fresh implementation, not translation.
