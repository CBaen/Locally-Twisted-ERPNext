# Locally Twisted — Work Queue

Current work only. **When an item is completed, DELETE it from this file.** Git tracks completion history. Queues are not for history.

Format: `- [priority] description — context / blocking notes`

LT-specific work only. Cross-client / agency-wide work lives at `Built_by_Cameron/built-by-cameron-queue.md`.

---

## Active

### Phase 1 — Customer site + storefront (the proof point)

See `.planning/phases/01-customer-site-and-storefront/PLAN.md` for the full slice list. Highlights:

- [DONE 2026-04-26] **Slice 1 — Brand foundation.** Style-guide tokens installed; theme CSS now served by the `locally_twisted` custom Frappe app at `/assets/locally_twisted/css/lt-theme.css` (registered via `web_include_css` in `hooks.py`). Source at `apps/locally_twisted/locally_twisted/public/css/lt-theme.css` (~21 KB).
- [P0 — IN PROGRESS, NOT DONE] **Slice 2 — Header + footer.** Wiring via `Website Settings` exists (per `scripts/setup/setup_slice2_header_footer.py`) but VISUAL STATE IS BROKEN: `.web-footer` computed height constrained, `.footer-info` rendering on white background. The approved Odoo structure has substantively different copy + layout. **Resume order:** (1) framework verification (this session's task #3), (2) webshop install (this session's task #2), (3) override Jinja partials at `apps/locally_twisted/locally_twisted/templates/includes/footer/footer.html` etc. using approved Odoo structure as spec. Full forensic in `anti-gl-patterns.md` section 0 + `lessons-learned.md` 2026-04-26 (Slice 2 build).
- [P0] **Slice 3 — Landing page.** Partially blocked on real photography sourcing. Should not start until Slice 2 is genuinely complete.
- [P0] **Slice 4 — Balloon Twisting + Face Painting service page.** Carry-forward content.
- [P0] **Slice 5 — Contact page.** Brief about summary embedded.
- [P0] **Slice 6 — Accessibility + Refund Policy + FAQ pages.** Blocked on accessibility statement decision (see `.planning/decisions/accessibility-statement.md`).
- [P0] **Slice 7 — Products listing.** Blocked on header navigation decision (URL structure depends on it).
- [P0] **Slice 8 — Individual product pages.** Variant pricing must work.
- [P0] **Slice 9 — Cart + checkout shell.** Stripe stubbed until Phase 4.
- [P1?] **Slice 10 — Pricing calculator.** Conditional on GL decision: include in Phase 1 or defer.

### Open iterations on already-built Lead schema (carried into Phase 2)

- [P1] **Inspiration Photos thumbnail UX decision.** Frappe blocks `in_list_view` on Attach Image AND Image fieldtypes in child tables. GL hasn't picked among: (a) click-to-expand (current state), (b) Frappe Client Script for inline gallery rendering, (c) drop child table for built-in attachments sidebar. Resume after GL chooses.
- [P1] **GL's "this is one Lead!" realization.** GL was thinking each tab was a Lead category; reality is sections of one Lead form. GL hasn't said what they actually wanted to model differently. Don't redesign without their explicit direction. Resume conversation when GL is ready.
- [P0] **Connect the missing Inspiration Photos Table field.** The `LT Lead Photo` child DocType exists and the Section Break exists, but the Table field that connects them was never created — iter 4's step F failed silently. Right now there's an empty section heading on the Lead form. Tied to the thumbnail UX decision above.

### Cross-cutting / housekeeping

- [P2] **Persist the nginx Origin patch across container recreation.** Currently applied via `docker exec` in `scripts/fix/patch_nginx_socketio_origin.py` and only survives until the frontend container is recreated. Cleaner long-term: docker-compose override that mounts a custom `frappe.conf` with the pass-through line. Acceptable to defer since recreations are rare in local dev.

- [P1] **Extract Frappe/ERPNext patterns from this session to agency capabilities + lessons.** During Phase 1 Slice 2 build, hit ~8 reusable Frappe v15 / ERPNext-specific patterns that future BBC clients on the same stack will rediscover otherwise. After Slice 2 ships, write:
  - `Built_by_Cameron/.claude/capabilities/recipes/frappe-website-shell-setup.md` — recipe bundling Website Settings configuration (`top_bar_items`, `footer_items`, `brand_html`, `address`, `copyright`, `head_html`) with the gotchas inline.
  - Append cross-client entries to `Built_by_Cameron/lessons-learned.md` for the high-bite gotchas (Web Page `content_type` field-mapping trap, HTML sanitizer stripping SVG path data, head_html cascade-order vs Frappe bundles, Frappe auto-prepending © on copyright, navbar-toggler markup divergence from Bootstrap).
  Source material: this LT session's transcripts + `_resources/lt-theme.css` + `scripts/setup/setup_slice2_header_footer.py`.

- [P2] **Tidy the "Waiting on GL" queue section.** Every item in that section is already resolved per `locally-twisted-decisions.md` (2026-04-26 entries) and `HANDOFF.md`. Delete per the queue convention: "When an item is completed, DELETE it from this file."

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
