# Frappe Cloud Integration Audit

Status: read-only integration audit for Design Studio V2.
Scope: `research/design-studio-v2/` plus locally-twisted Frappe app files already named by `frappe-native-design-studio-architecture.md`. No external web used. No live Frappe/ERPNext database inspection performed.

Files inspected:

- `.codex/capabilities/recipes/erpnext-intake-form-parity.md`
- `.codex/capabilities/recipes/erpnext-crm-pipeline-safety.md`
- `research/design-studio-v2/README.md`
- `research/design-studio-v2/frappe-native-design-studio-architecture.md`
- `research/design-studio-v2/prototype/README.md`
- `research/design-studio-v2/prototype/REVIEW-QA.md`
- `research/design-studio-v2/prototype/js/payload.js`
- `research/design-studio-v2/prototype/js/state.js`
- `apps/locally_twisted/locally_twisted/hooks.py`
- `apps/locally_twisted/locally_twisted/www/book.py`
- `apps/locally_twisted/locally_twisted/www/contact.py`
- `apps/locally_twisted/locally_twisted/templates/includes/book_form.html`
- `apps/locally_twisted/locally_twisted/lead_cascade.py`
- `apps/locally_twisted/locally_twisted/seed/sync_contact_intake_backend.py`
- `scripts/verify/lead_backend_intake_parity.py`
- `scripts/verify/crm_pipeline_parity.py`

## 1) Executive verdict

The next Design Studio version should remain Frappe-native, but it is **not ready to be wired directly into Frappe Cloud as a Lead-creating production surface** without an integration pass.

The good news: the existing app already has the right pattern for Frappe Cloud compatibility: website routes in `apps/locally_twisted/locally_twisted/www/`, app-owned hooks in `hooks.py`, guest-safe whitelisted methods with rate limiting, server-created ERPNext `Lead` records, `Contact` dedup/linking, Lead timeline `Communication`, and backend parity verifiers.

The risk: the current Design Studio research/prototype payload does not yet match the proposed production architecture. The prototype is intentionally static and says it does not save, share, create Leads, quote, or modify ERPNext. Its payload is review-oriented (`selected_pieces`, `render_facts`, `source_products`, `declined_suggestions`) while the architecture spec proposes a richer nested contract (`event`, `customer`, `palette`, `pieces`, `suggestions`, `render`, `sales_summary`, `disclaimers`) plus new DocTypes and API endpoints.

Recommended verdict: **build a thin Frappe integration adapter next, not a full public launch.** The adapter should normalize the prototype/review payload into the architecture contract, save it to a future `LT Decor Design` record, then create exactly one Lead through a server-side submit endpoint only after required contact and sales fields are present.

## 2) Current prior build architecture

Current state is a research/prototype lane, not production:

- `research/design-studio-v2/README.md` explicitly frames this folder as background research for a future `Plan Custom Decor` studio and warns not to treat it as proof that production has a working design studio.
- `research/design-studio-v2/prototype/README.md` says the prototype is static/dormant and does not create Leads, save designs, share designs, quote prices, or modify ERPNext records.
- `research/design-studio-v2/prototype/REVIEW-QA.md` repeats that no real save, share, Lead, contact, checkout, or backend behavior is implemented.
- `prototype/js/state.js` seeds a single browser-side state object with `schema_version: "design-studio-prototype-v2"`, review scenario, event context, product family, design ID, selected colors, pieces considered, and disclaimer.
- `prototype/js/payload.js` builds a review payload with `source: "research_prototype"`, `customer_facing_path: "Plan Custom Decor"`, `selected_pieces`, `pieces_considered`, `declined_suggestions`, `render_summary`, `sales_summary`, and `customer_summary`.

Current Frappe app integration pattern:

- `hooks.py` uses `website_route_rules` for friendly route aliases and wires `Lead` doc events to `lead_cascade.before_insert`, `lead_cascade.after_insert`, and `stage_cascade.on_update`.
- `contact.py` defines `/contact` as the surviving customer inquiry surface.
- `book.py` exposes `submit_book_inquiry` as `@frappe.whitelist(allow_guest=True)` and `@rate_limit(limit=20, seconds=60 * 60)`, validates required name/email, creates an ERPNext `Lead`, attaches valid photos, records a timeline `Communication`, and returns `{ok: true, lead: <name>}`.
- `book_form.html` posts to `/api/method/locally_twisted.www.book.submit_book_inquiry`, handles visible errors, and has a sessionStorage handoff path from an internal Event Playground preview into `/contact?intent=quote&source=event-playground`.
- `lead_cascade.py` deduplicates or creates `Contact` by email/phone, links Contact -> Lead using Frappe dynamic links, sends the website auto-ack email, and triggers CRM stage cascade.
- `sync_contact_intake_backend.py` and `lead_backend_intake_parity.py` encode the current Lead intake field/Desk parity contract.
- `crm_pipeline_parity.py` confirms the business board should use `custom_pipeline_stage` and leave native `Lead.status` available for ERPNext internals.

## 3) Frappe Cloud fit risks

1. **Static prototype is not deployable as-is.** The prototype is a direct-file research artifact. Frappe Cloud wants app-owned website pages/assets/endpoints, not a dormant local HTML prototype treated as production.

2. **No production DocTypes exist in audited files.** The architecture recommends `LT Decor Design`, `LT Decor Design Piece`, and optional `LT Decor Design Share`, but the inspected app files only prove current Lead/Contact/Communication patterns. Missing DocType fixtures/migrations are the main Frappe Cloud gap.

3. **Payload storage cannot live only on Lead.** `frappe-native-design-studio-architecture.md` warns not to put raw full JSON only in a free-text field. Frappe Cloud production needs an app-owned design record with the full JSON and a Lead link.

4. **Guest endpoint hardening must be explicit.** Existing `book.py` shows rate limiting and validation. The future `save_design`, `create_share_link`, and `submit_design_inquiry` endpoints must repeat that discipline: size caps, schema allowlist, server-side color/piece validation, email validation before Lead creation, and sanitized error logging.

5. **Share tokens are sensitive.** The architecture calls for high-entropy tokens, token hashes only, expiry, revoke behavior, `noindex`, and no PII on public share pages. That is required before Frappe Cloud public exposure.

6. **Asset inclusion can regress launch pages.** The architecture says route-specific assets are preferable; global `web_include_js/css` is only acceptable if scripts self-detect `[data-lt-design-studio]` and exit. This matters on Frappe Cloud because global website assets affect every public route.

7. **No live metadata proof in this pass.** I did not query the Frappe database. Field existence and current Custom Field options must be re-verified before implementation using the existing parity scripts or bench/API checks.

## 4) Contact/Lead handoff gaps

- **Design Studio has no direct handoff yet.** The current prototype produces a payload but has no submit button that posts to Frappe, no save/share endpoint, and no Lead creation.
- **Existing Event Playground handoff is lossy.** `book_form.html` converts a sessionStorage handoff into form fields: customer name/phone/email, checks `Balloon Decor` and `Events Inquiry`, sets `x_decor_types`, colors, package notes, and description. That proves a lightweight path, but it collapses structured design data into text fields.
- **Lead service truth must remain child rows.** `book.py` maps services into `custom_event_type: _service_child_rows(services)`. Future Design Studio submit must do the same, not just write a text echo.
- **Contact linking is downstream of Lead insert.** `lead_cascade.py` creates/dedups Contact after Lead insert. A future design submit should not separately invent a competing contact link path unless it deliberately reuses Frappe Contact dynamic links.
- **Source channel needs a new value.** Current `/contact` writes `custom_source_channel: "Website Form"`; architecture recommends `Plan Custom Decor`. Add/verify this value deliberately so the CRM can distinguish studio inquiries.
- **Communication body needs richer design context.** Current `_record_inquiry_communication` is form-field oriented. Design Studio needs selected pieces, dimensions, colors with roles, pieces considered/declined, disclaimer, and internal design link.
- **Failure semantics must avoid false success.** The architecture says no partial silent Lead creation. If design save succeeds but Lead creation fails, UI must say the inquiry was not sent and provide phone/email fallback.

## 5) Payload/schema gaps

Current prototype payload shape (`prototype/js/payload.js`):

- `schema_version`
- `source: "research_prototype"`
- `customer_facing_path`
- `review_scenario` / `review_scenario_label`
- `event_context`
- `selected_pieces[]` with product family, source products, variant count, variant axes, selected colors, and render facts
- `pieces_considered[]`
- `declined_suggestions[]`
- `render_summary`
- `sales_summary`
- `customer_summary`

Proposed production contract (`frappe-native-design-studio-architecture.md`):

- nested `event` object with date/location/guest/environment fields
- nested `customer` object with name/email/phone/company
- nested `palette` object with context, notes, color names, roles, approximate hex, match status
- `pieces[]` with stable `piece_id`, `piece_type`, dimensions, style, selected colors, region assignments, rules summary, and summary
- `suggestions.pieces_shown[]` and `suggestions.pieces_declined[]`
- `render` object with renderer, thumbnail SVG, and alt summary
- `customer_notes`
- `sales_summary` object with short summary, pieces considered, and follow-up questions
- `disclaimers` booleans

Main gaps:

- Prototype has no `customer` block, so it cannot create a valid Lead without a separate contact capture step.
- Prototype has only `event_context`, not date, location, guest count, indoor/outdoor, or venue notes.
- Prototype uses `selected_pieces` and `product_family`; architecture expects `pieces` with `piece_type`, dimensions, style, region assignments, and rules summary.
- Prototype color data is names only; architecture expects palette context and optional role/match metadata.
- Prototype has review-oriented `source_products` and `variant_count`; these are useful internally but need a production-safe home in `design_json` or `rules_summary`, not necessarily Lead fields.
- Prototype `sales_summary` is a string; architecture expects structured short summary, considered pieces, and follow-up questions.
- Prototype has no stable design/session ID beyond browser state and no server-owned design ID/link.
- Prototype has no payload size cap, schema validator, or server allowlist because it is not yet posting to a server.

## 6) Concrete next-version recommendations

1. **Create a Frappe-owned adapter module before public route work.** Add a future `locally_twisted.api.design_studio` module with pure normalization/validation helpers first, then expose whitelisted methods after tests exist.

2. **Define `design-studio-v1` as the server contract.** Do not submit the prototype payload directly. Write a mapper from `design-studio-prototype-v2` to the architecture's `design-studio-v1` shape and fail loudly when required fields are missing.

3. **Add app-owned DocTypes before Lead creation.** Implement fixtures/migrations for `LT Decor Design` and `LT Decor Design Piece` first. Store canonical JSON on `LT Decor Design.design_json`; link Lead back through `LT Decor Design.lead` or a reciprocal Lead custom field if approved.

4. **Keep Lead creation thin and readable.** On submit, create exactly one Lead with:
   - `source = Website`
   - `custom_source_channel = Plan Custom Decor`
   - `custom_event_type` child row including `Balloon Decor` and, if approved, `Events Inquiry`
   - current event basics mapped to existing Lead fields where available
   - `custom_decor_types`, `custom_colors`, `custom_indoor_outdoor`, and `custom_anything_else` populated from validated summaries
   - a Lead `Communication` containing selected pieces, dimensions, colors/roles, considered/declined suggestions, disclaimers, and the internal design link

5. **Do not reuse `/book` as the studio route.** Follow the architecture recommendation: future customer route `/plan-custom-decor`, `/contact` as fallback, `/shop` for ready-to-order ecommerce, `/book` as legacy compatibility only.

6. **Make save/share separate from submit.** Implement `save_design`, `create_share_link`, and `submit_design_inquiry` as separate endpoints so draft persistence cannot accidentally imply a submitted inquiry.

7. **Use strict server validation.** Enforce recognized `schema_version`, allowed piece types/styles, approved color names, sane dimension bounds, non-empty pieces before submit, valid email before Lead creation, JSON size caps, and SVG sanitization/no-executable trust.

8. **Preserve CRM guardrails.** Do not overload native `Lead.status`. Keep business workflow in `custom_pipeline_stage` and leave checkout/conversion logic aligned with the existing CRM pipeline safety contract.

9. **Add dedicated verifiers.** Extend the current pattern with checks for: route loads; no global asset regressions; guest save disabled-or-working visibly; submit creates one Lead; `custom_event_type` child rows are correct; Communication includes design facts; invalid color/piece/email/payload-size are rejected; share pages are redacted, expiring, and `noindex`.

10. **Delay public Frappe Cloud exposure until decisions are approved.** Still-open approvals from the architecture file matter: guest share/account save rules, public route timing, customer-visible color approximations, CRM labels/service tagging, first-piece scope, and whether pricing/construction math appears to customers.
