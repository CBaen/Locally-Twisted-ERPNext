# Locally Twisted — Work Queue

Current work only. **When an item is completed, DELETE it from this file.** Git tracks completion history. Queues are not for history.

Format: `- [priority] description — context / blocking notes`

LT-specific work only. Cross-client / agency-wide work lives at `Built_by_Cameron/built-by-cameron-queue.md`.

---

## Active

### Phase 1 — Customer site + storefront (the proof point)

See `.planning/phases/01-customer-site-and-storefront/PLAN.md` for the full slice list. Highlights:

- [DONE 2026-04-26] **Slice 1 — Brand foundation.** Style-guide tokens (DM Serif Display, Raleway, full color palette as CSS variables, 8px spacing scale, focus-visible outline, prefers-reduced-motion, button + form input + card + section + thin-band patterns) installed via `Website Settings.head_html`. Source-of-truth at `_resources/lt-theme.css`. Verified via `curl http://localhost:8081/` — CSS present in served HTML head with `data-source="lt-brand-foundation"` marker. 7159 bytes injected. Survives until container recreation; promote to packaged Frappe app when there's a critical mass of customizations.
- [P0] **Slice 2 — Header + footer.** Blocked on header navigation decision (see `.planning/decisions/header-navigation.md`).
- [P0] **Slice 3 — Landing page.** Partially blocked on real photography sourcing.
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

## Blocked

*nothing*

## Waiting on GL (Phase 1 decision gates)

- **Header navigation structure** — see `.planning/decisions/header-navigation.md` (Claude recommends Option B)
- **Accessibility statement nuance** — see `.planning/decisions/accessibility-statement.md` (Claude strongly recommends Option B)
- **Blog presence in Phase 1** — ship framework + one seed post / framework only (hidden) / defer
- **Real photography sourcing** — where do good LT event photos live, or do we ship Phase 1 with placeholders?
- **Customer-inquiry email destination** — where do current `locallytwisted.com` contact-form submissions land? (Need this for Phase 2 acknowledgment routing)
- **Pricing calculator in Phase 1?** — Slice 10 yes/no/defer
- **Inspiration Photos thumbnail UX** — pick (a)/(b)/(c) from the Lead-schema iteration item above
- **"This is one Lead" realization** — what did you want to model that you thought was happening?

## Deferred (intentional, not blocked)

- **Custom Frappe app scaffolding for LT.** When there's a critical mass of customizations worth packaging.
- **Frappe Cloud signup + production deployment.** Phase 6 (cutover).
- **Reading Jeff's UI-edited content from any prior platform's database.** Not applicable — the prior platform never went live to customers, so there's no production-only content to migrate.
- **Translation of remaining Odoo models** (`res_partner`, `product_template`, `project_task`, `calendar_event`, `hr_expense`, `res_config_settings`, `twilio_service`). These are no longer "translations" under the new framing — the underlying capabilities (customer/contact split, sale order extension, project task customization, calendar event extension, expense tracking, Twilio SMS, settings DocType) get built fresh as part of Phase 2/3/4 when each is needed. The Odoo source files remain reference material in `_resources/`-adjacent inventory, but the work is fresh implementation, not translation.
