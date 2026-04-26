# Locally Twisted — Work Queue

Current work only. **When an item is completed, DELETE it from this file.** Git tracks completion history. Queues are not for history.

Format: `- [priority] description — context / blocking notes`

LT-specific work only. Cross-client / agency-wide work lives at `Built_by_Cameron/built-by-cameron-queue.md`.

---

## Active

### Phase 2 (Backend Models) — in flight

`crm_lead` translated (46 Custom Fields, 4 iterations). Remaining work below.

- [P0] **Translate `res_partner.py`** — 7 fields on `res.partner` (3 computed health-status + 4 stored). Target ERPNext: split between Customer + Contact DocTypes (Odoo's `res.partner` is collapsed; ERPNext separates). Health-status computed fields → Server Script + cache field, OR Frappe Virtual DocField.
- [P0] **Translate `product_template.py`** — no new fields; just a CRUD override syncing `description_sale` → `website_description`. Target ERPNext: Server Script on Item with hook on `before_save`.
- [P0] **Translate `project_task.py`** — 14 custom fields. Target ERPNext: Custom Fields on Task DocType. Pattern follows `translate_crm_lead.py`.
- [P0] **Translate `calendar_event.py`** — 1 computed field. Target ERPNext: Custom Field + Server Script on Event DocType.
- [P0] **Translate `hr_expense.py`** — 12 lines, minor extension. Target ERPNext: Custom Fields on Expense Claim DocType.
- [P0] **Translate `res_config_settings.py`** — Twilio credential fields. Target ERPNext: new Single DocType "LT Settings" with the credential fields, accessed via `frappe.db.get_single_value('LT Settings', '...')`.
- [P0] **Implement `twilio_service`** — NOT a new DocType (per 2026-04-26 decision). Implement as Python helper in a future LT custom Frappe app, or as Server Script hooked to relevant events. Defer until Phase 3 (Automations) is in flight, since it's called BY automations.
- [P2] **Configure ERPNext HRMS for native payroll** — agency-wide standard (2026-04-26). Defer until post-cutover; salary structures, payroll periods, direct deposit, etc. North Peak (accountant) needs heads-up that payroll moves to the native ERPNext module.

### Open iterations on already-translated work

- [P1] **Inspiration Photos thumbnail UX decision** — Frappe blocks `in_list_view` on Attach Image AND Image fieldtypes in child tables. GL hasn't picked among: (a) click-to-expand (current state), (b) Frappe Client Script for inline gallery rendering, (c) drop child table for built-in attachments sidebar. Resume after GL chooses.
- [P1] **GL's "this is one Lead!" realization** — GL was thinking each tab was a Lead category; reality is sections of one Lead form. GL hasn't said what they actually wanted to model differently. Don't redesign without their explicit direction. Resume conversation when GL is ready.

### Cross-cutting / housekeeping

- [P0] **Customer-facing /book form (Odoo side) needs to mirror the new Lead schema** — add `x_event_end_time` field, switch all time inputs to AM/PM display, relabel `x_event_time` → "Event Start Time (even an estimate is helpful!)" + add the matching End Time field. **This work happens on `locally-twisted-odoo/`, which is read-only from this project per 2026-04-25 directive — coordinate with GL on which session/instance does it.** Until done, the live form posts the OLD shape (no end_time field; 24-hour times); ERPNext side accepts it but loses end-time data.
- [P1] **Contact dedup logic on Lead `before_insert`** — Odoo's `crm_lead.create()` looks up `res.partner` by email/phone, attaches if found, creates if not. ERPNext equivalent: Server Script on Lead. Look up Contact by `email_id`/`mobile_no`/`phone`; set Lead's `contact` field to the matched Contact, or create a new one. Phase 3 work (automation layer). GL: "the input should directly map to these exact fields (not just in CRM but also contact unless it's a duplicate contact)."
- [P1] **Form-handler routing layer (when we cut the customer form to ERPNext-served).** Live Odoo form posts: `contact_name`, `phone`, `email_from`, `partner_name`, `description`, `x_*` fields. ERPNext Lead expects: `lead_name`, `phone`, `email_id`, `company_name`, `custom_anything_else`, `custom_*`. Build the field-rename mapping in the Web Form / API endpoint that replaces /book on the ERPNext side (Phase 5 storefront rebuild).
- [P0] **Clean up ERPNext user accounts.** Two fixes: (a) delete the `locallytwisted@yahoo.com` placeholder user — no such account exists in reality, was wizard-generated phantom; (b) rename the `locallytwisted@gmail.com` user record's full_name from "Jeff Baen" to "Jeff Kimber" in ERPNext (currently mis-labeled). Note: the actual owner of LT is Jeff Kimber. "Baen" is GL's middle name (Cameron Baen) that got tangled with Jeff's record by a prior instance.
- [P2] **Persist the nginx Origin patch across container recreation.** Currently the fix at `scripts/fix/patch_nginx_socketio_origin.py` is applied via `docker exec` and only survives until the frontend container is recreated. Cleaner long-term: docker-compose override that mounts a custom `frappe.conf` with the pass-through line. Acceptable to defer since recreations are rare in local dev.

## Blocked

*nothing*

## Waiting on GL

- **Inspiration Photos thumbnail UX path** — pick (a)/(b)/(c) above
- **"This is one Lead" realization** — what did you want to model that you thought was happening?

## Deferred (intentional, not blocked)

- **Custom Frappe app scaffolding for LT.** When there's a critical mass of DocTypes/Custom Fields/Server Scripts worth packaging. Per GL: "we will deal with the bench and transferables when THERE ARE."
- **INV-02 — production `arch_db` read.** Reactivate near cutover (Phase 9-ish). Captures Jeff's UI-edited content (blog posts, page text) that lives only in production DB.
- **Frappe Cloud signup + production deployment** (DEPLOY-01). After local rebuild has the critical paths working.
- **Updating ROADMAP.md to formally renumber phases.** Phase 1 is marked DEFERRED inline; full renumber can wait — phases 2-10 still cover the work, the only orphan is INV-02 which can slot before Phase 10 cutover.
