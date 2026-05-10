# Locally Twisted - scripts/

Operational scripts for the LT ERPNext build live here. Most scripts are self-contained Python files with a docstring at the top explaining purpose, usage, and why it exists. The layout-fit gate is a Playwright Test spec and runs through npm.

Run scripts from the project root: `python scripts/<dir>/<name>.py`.
Run the layout-fit gate from the project root: `npm run test:layout-fit`.
Run the public axe accessibility gate from the project root: `npm run test:a11y`.
Run the verifier CLI contract from the project root: `python scripts/verify/verifier_cli_contract.py`.

Verification scripts must treat `--help` as a safe, fast, non-mutating command.
If a verifier needs a browser, Docker, ERPNext, fake-data writes, or network
access for its normal run, its help path must exit before any of that work
starts. The `verifier_cli_contract.py` gate enforces this for tracked,
maintained Python verifiers. Throwaway `_oneshot_*` scripts are excluded and
should not be used as launch proof.

## Layout

| Dir | Purpose |
|-----|---------|
| `setup/` | One-time-or-occasional install/configuration scripts. Idempotent scripts are safe to re-run. |
| `dev/` | Day-to-day development helpers. Run during a build session. |
| `fix/` | Patches that work around upstream bugs or recreate transient state. |
| `translate/` | Historical translation scripts were removed; git history is the archive. |
| `verify/` | Verification scripts. Run before declaring anything done. |

## setup/

| Script | Purpose | Run when |
|--------|---------|----------|
| `setup_lt_company.py` | One-shot wizard completion + LT Company seeding. | Once, on a fresh install |
| `setup_slice2_header_footer.py` | Stale Slice 2 Website Settings wiring attempt. | Do not re-run without reading the current header/footer rules |
| `install_webshop.py` | Historical/fallback installer for `frappe/webshop` + `frappe/payments`. | Only when deliberately rebuilding a bind-mount install path |
| `export_odoo_catalog.py` | One-shot HTML scraper for the old live LT Odoo catalog. | Re-run only before the old source is decommissioned |
| `sync_contact_intake_backend.py` | Runs the in-app `locally_twisted.seed.sync_contact_intake_backend.execute` sync so ERPNext Lead/CRM metadata matches the current `/contact` service taxonomy, including plain-text estimated time fields and the `LT Lead Photo` child table connection. | After changing public contact service labels or backend Lead conditional logic |
| `sync_crm_pipeline.py` | Runs the in-app `locally_twisted.seed.sync_crm_pipeline.execute` sync so LT's six-stage CRM board uses `Lead.custom_pipeline_stage` instead of repurposing ERPNext's native `Lead.status`. | After changing CRM stages, the LT Inquiry Board, or Owner Home inquiry-count behavior |
| `sync_stage_cascade.py` | Runs the in-app `locally_twisted.seed.sync_stage_cascade.execute` sync so Task has the Lead/stage fields required by safe CRM stage cascades. `sync_crm_pipeline.py` also runs this sync. | After changing CRM stage-to-Task cascade fields |
| `sync_backend_workspaces.py` | Runs the in-app `locally_twisted.seed.sync_backend_workspaces.execute` sync so simplified Owner, Manager, and Employee workspaces use current business labels, the Sales Order booking calendar, and the Owner Home command-center cards/chart/checklist. | After changing simplified backend workspaces, role profiles, number cards, charts, or calendar shortcuts |
| `sync_finance_workspace.py` | Runs the in-app `locally_twisted.seed.sync_finance_workspace.execute` sync so Accountant Home has finance cards, accounting shortcuts, and the internal customer reminder review report shortcut. | After changing accountant workspace shortcuts, finance cards, report records, or reminder review report Desk wiring |
| `sync_site_branding.py` | Runs the in-app `locally_twisted.seed.sync_site_branding.execute` sync so public/login favicon, logo, splash, app name, and source-level head chrome stay Locally Twisted branded. | After changing public/login branding, favicon assets, or rebuilding Website/System Settings |
| `sync_invoice_branding.py` | Runs the in-app `locally_twisted.seed.sync_invoice_branding.execute` sync so Sales Invoices use the branded Locally Twisted print format, default print-format property, and letterhead. | After changing invoice print copy, invoice styling, letterhead, or rebuilding setup records |
| `sync_maintenance_package.py` | Runs the in-app `locally_twisted.seed.sync_maintenance_package.execute` sync so the sanitized Maintenance Admin role, heartbeat report, workspace shortcuts, and read-only DocPerm boundary are present. | After changing maintenance heartbeat DocTypes, report wiring, workspace shortcuts, or Maintenance Admin access rules |
| `sync_variant_media.py` | Stages Odoo product images and applies conservative variant image mappings. | After reviewing or refreshing catalog media mappings |
| `sync_category_media.py` | Writes an approval template from category candidates, then stages and dry-runs or applies approved Item Group image selections through Frappe. `--apply` refuses unapproved selections. | After Jeff/GL approve category browse images |

## dev/

| Script | Purpose | Run when |
|--------|---------|----------|
| `clear_website_cache.py` | Clears Frappe site + website cache so edited Jinja templates / CSS / Web Page records take effect on the next request. Optional `--restart` for `hooks.py` changes. | After editing Jinja templates, SCSS/CSS, Web Page records, or hooks |

## fix/

| Script | Purpose | Run when |
|--------|---------|----------|
| `patch_nginx_socketio_origin.py` | Historical/fallback patch for the LT frontend container's nginx config to pass through the original `Origin` header. The current custom image should already contain this line. | Only if a rebuilt frontend image is verified missing `proxy_set_header Origin $http_origin;` |
| `fix_crm_lead_*.py` | Removed. These one-off Lead-schema scripts used stale service labels and are preserved only in git history. | Use `setup/sync_contact_intake_backend.py` instead |
| `fix_lead_photo_thumbnail.py` | Removed. The child table connection is now handled by `setup/sync_contact_intake_backend.py`; thumbnail UX remains a separate product choice. | Use git history only if researching the old experiment |

## translate/

| Script | Purpose | Status |
|--------|---------|--------|
| `translate_crm_lead.py` | Removed. It built an early Lead schema with stale service values. | Git history only |
| `translate_dashboard_review.py` | Built the `Dashboard Reviewed Item` DocType. | Historical |

## verify/

| Script | Purpose | Run when |
|--------|---------|----------|
| `a11y_audit.js` | Playwright + axe-core gate for the public launch route list at desktop and mobile widths. Writes `output/a11y/a11y-desktop.json`, `output/a11y/a11y-mobile.json`, and `output/a11y/a11y-summary.json`; fails nonzero on any axe violation. | Before closing public route/template changes, especially landmarks, headings, links, forms, breadcrumbs, checkout, shop, or customer-facing CSS |
| `layout_fit.spec.js` | Playwright Test gate for public/shop/cart routes across mobile, tablet, and desktop widths. | Before visual claims, after customer-facing CSS/Jinja/template changes |
| `search_contract.spec.js` | Playwright Test gate for header search overlay product suggestions and submitted `/shop?q=...` results. | After changing header search, shop search, Website Item search context, or product-card discovery behavior |
| `portfolio_reel.spec.js` | Playwright Test gate for `/portfolio` floating proof-reel behavior: natural-ratio images, no photo captions/frame wrappers, no route-specific portfolio contact/index footer, larger desktop entry/click-to-front behavior that settles without pointer-follow sway, mobile full-width slide-in reveal, filter relayout, and empty state. | After editing portfolio layout, image metadata, filters, or modal behavior |
| `owner_desk_routes.spec.js` | Playwright Test gate for owner Desk route recovery and Owner Home content. | After Desk JS, workspace, or simplified owner role changes |
| `contact_service_logic.py` | Verifies `/contact` service-specific conditional logic and absence of stale service labels. | After editing contact form labels, choices, conditionals, or Lead payload mapping |
| `contact_prefill.py` | Verifies guided contact URLs preselect the intended service checkboxes and panels. | After editing service-page CTAs or `/contact?service=...` parsing |
| `lead_backend_intake_parity.py` | Verifies live ERPNext Lead/CRM metadata matches `/contact`: service type records, Lead Custom Field labels/depends_on logic, plain-text time entry, `LT Lead Photo` table wiring, and submit helper mapping into `custom_event_type`. | After editing backend Lead fields or public service taxonomy |
| `crm_pipeline_parity.py` | Verifies LT's Odoo-approved six-stage inquiry board is backed by `Lead.custom_pipeline_stage`, leaves native `Lead.status` intact, removes stale status columns from `LT Inquiry Board`, and ensures website Leads start at `New Inquiry`. | After editing CRM stage sync, inquiry Kanban behavior, or Owner Home inquiry filters |
| `crm_stage_cascade.py` | Verifies stage movement creates/closes only operational Tasks, leaves Sales Orders, Sales Invoices, and Payment Requests unchanged, and cleans up its temporary test records. | After editing `stage_cascade.py`, Lead hooks, or CRM stage-to-Task behavior |
| `backend_schema_inventory.py` | Read-only live ERPNext backend inventory: counts core records/schema records, classifies Custom Fields as code-owned vs unclassified DB/app-owned, maps current CRM/checkout cascade surfaces, and separates intentional old-label guardrails from stale references. | Before deciding backend fixture/export ownership, Lead layout simplification, or new stage-to-finance cascades |
| `backend_schema_inventory_contract.py` | Unit contract for `backend_schema_inventory.py` helper logic. | After editing the backend inventory classifier or stale-term scanner |
| `verifier_cli_contract.py` | Fast meta-contract proving tracked maintained Python verifiers expose safe `--help` output instead of launching browser/backend work. | After adding or changing Python verifier entrypoints, and before trusting a timeout as a product failure |
| `backend_workspace_parity.py` | Verifies simplified backend workspaces no longer show stale ERPNext labels, booking calendars point at Sales Orders by delivery date, and Owner Home includes the command-center number cards/chart/checklist. | After editing workspaces, role profiles, number cards, charts, or Desk calendar behavior |
| `customer_documents_contract.py` | Verifies policy lane anchors and code-owned customer email policy blocks without creating ERPNext setup records. | After editing customer emails, receipts, checkout notices, or policy pages |
| `customer_email_policy_contract.py` | Static no-send check for inquiry acknowledgment, receipt, operator, and welcome email policy lanes, queue behavior, and no-PDF/no-attachment boundaries. | After editing customer/operator email bodies, receipt handling, welcome copy, or payment cascade email tests |
| `maintenance_heartbeat.py` | Verifies the sanitized client operations heartbeat: public boot, scheduler, notification preferences, Maintenance Admin boundary, and optional heavy paperwork/business digest checks. | After changing maintenance heartbeat code, scheduler hooks, checkup topics, or owner digest boundaries |
| `maintenance_admin_boundary.py` | Verifies the Maintenance Admin role can read only sanitized maintenance DocTypes/report/workspace shortcuts and cannot read raw logs, customer records, files, communications, or finance records. | After changing maintenance role permissions, DocTypes, workspace shortcuts, or report roles |
| `paperwork_status.py` | Read-only paperwork/backend status report for invoices, payment requests, email queues, non-live setup gaps, and cutover-deferred payment items. It does not run live payment readiness in synthetic mode. Outputs optional JSON to ignored `output/`. | When reviewing back-office launch readiness before adding finance automation |
| `quote_proposal_draft_packet.py` | Draft-only quote/proposal packet renderer. Produces internal review packets from existing Quotation data while proving no PDF, customer send, or finance mutation happens. | Before building proposal PDF output, sender UX, quote approval automation, or any customer-facing proposal delivery |
| `quote_proposal_draft_packet_contract.py` | Fake-data contract for normal/outlier quote and proposal review packets, including missing acceptance path and malformed send-ready source behavior. | After changing quote/proposal packet copy, packet shape, send-readiness rules, or review-gate boundaries |
| `unpaid_invoice_review.py` | Draft-only unpaid/overdue invoice review surface. Produces reminder and statement candidates from Sales Invoices plus the outbound document registry while proving no customer send or accounting mutation happens. | Before creating payment reminders, statement drafts, or any collections/reconciliation review queue |
| `unpaid_invoice_draft_packet.py` | Draft-only unpaid invoice packet renderer. Produces JSON and optional Markdown review packets from unpaid invoice candidates while proving no customer send or accounting mutation happens. | Before building an internal Desk queue, scheduled digest, or any reminder/statement send path |
| `unpaid_invoice_draft_packet_contract.py` | Fake-data contract for normal/outlier unpaid invoice draft packet behavior, including missing payment requests and malformed human-approval gates. | After changing unpaid invoice packet copy, packet shape, or review-gate rules |
| `paperwork_review_digest.py` | Read-only internal digest combining paperwork status, automation index, unpaid invoice review, draft packets, and audience-specific operations readiness rows into one review payload. It verifies the digest uses the automation index without runtime fake-data contracts. | Before creating a Desk queue or scheduled internal digest and after changing paperwork review surfaces |
| `customer_reminder_dry_run.py` | No-live internal customer reminder review queue. Builds cadence suggestions, blockers, and draft sections without enabling customer delivery. | Before any reminder UX, scheduled internal report, or future customer-send approval work |
| `customer_reminder_dry_run_contract.py` | Fake-data contract for no-live customer reminder queue behavior, including overdue/current/missing-payment-path/malformed-send scenarios. | After changing reminder cadence rules, blockers, queue shape, or dry-run boundaries |
| `customer_reminder_review_report.py` | No-live customer reminder report data source. Turns dry-run queue items into table rows, review/hold groups, optional JSON/Markdown/CSV output, and the internal Desk report path without customer delivery. | Before changing the Desk report, internal report, or scheduled internal-only reminder review surface |
| `customer_reminder_review_report_contract.py` | Fake-data contract for customer reminder report rows/groups, including empty queues and malformed send-enabled source rows. | After changing reminder report columns, groups, or no-live row boundaries |
| `record_level_failure_contract.py` | Rollback-safe fake-data contract proving backend partial failures create record-level Comments plus Error Log calls through the reusable failure recorder. | After changing fail-loud recorder behavior, Lead cascade failure handling, checkout partial-failure handling, paid-order receipt handling, or automation-index record health rows |
| `inquiry_upload_failure_contract.py` | Rollback-safe fake-data contract proving invalid inspiration photo uploads return a customer-visible summary and create record-level Lead evidence. | After changing public inquiry upload handling, accepted file types, upload limits, success-modal copy, or record-level failure reporting |
| `payment_success_reconciliation_contract.py` | No-live contract proving browser-return paid checkout shows a reconciliation-pending thank-you state when invoice/receipt/email follow-up is not fully complete. | After changing `/payment-success`, `/thank-you`, paid-order reconciliation, receipt email handling, or payment-success automation checks |
| `business_automation_index.py` | Read-only cross-system automation map for intake, CRM, checkout, payment, paperwork, finance, and scheduled checkups, including the sanitized maintenance heartbeat. Fails nonzero when launch-required surfaces are missing or disconnected. Full verifier runs execute runtime fake-data contracts; internal digest/report callers use non-runtime mode. | Before adding backend automation, before Frappe Cloud readiness claims, and when reviewing cascading information paths |
| `synthetic_business_pipeline.py` | Synthetic no-live pipeline audit for fake-data and rollback-safe backend flows. It runs/currently indexes record-level failure evidence, inquiry upload failure evidence, Stripe amount parity, checkout-to-Lead conversion, checkout fulfillment, paid-order cascade, payment-success reconciliation pending state, mocked Stripe webhook behavior, customer document policy, customer email policy boundaries, outbound document templates, outbound document send-readiness, quote/proposal packet outliers, unpaid invoice packet outliers, customer reminder dry-run outliers, and customer reminder review-report outliers while keeping live cutover checks deferred. | When flushing out cascading data, broken piping, fake-data cleanup, and no-live operating readiness |
| `stripe_amount_parity_contract.py` | Contract test proving Stripe Checkout line items equal the ERPNext Sales Order grand total, including tax/charges adjustment and loud rejection when item lines exceed the expected total. | After editing Stripe checkout, Sales Order totals, taxes/charges, delivery fees, or payment request creation |
| `invoice_branding_contract.py` | Verifies the branded Sales Invoice Print Format, default Sales Invoice print-format property, Letter Head, logo asset, and rendered invoice HTML against an existing Sales Invoice. | After editing `sync_invoice_branding.py`, invoice copy/styling, letterhead, or invoice setup records |
| `outbound_documents_contract.py` | Verifies the answer-first standard outbound document registry and source templates under `locally_twisted/outbound_documents/`. | After adding or changing invoices, receipts, proposals, packets, statements, reminders, work orders, or other files sent outside the company |
| `outbound_document_send_readiness_contract.py` | Fake-data contract proving external documents block missing fields, recipient confirmation, payment path, branding, human approval, sensitive attachments, and record-level blocker evidence before any customer delivery. | Before building or changing any sender, reminder Desk page, proposal generator, W-9 packet path, or Frappe Cloud paperwork trust claim |
| `render_outbound_document_previews.py` | Renders fake-data normal and outlier previews for every outbound document template to ignored `output/playwright/outbound-documents-YYYYMMDD/` as HTML, PDF, and PNG, with `Key fields to review` in the high-visibility slot. | When reviewing invoice, receipt, proposal, packet, statement, reminder, work order, contract summary, or follow-up design before automation |
| `smoke_forms.py` | Browser smoke test for public forms. Use `--form-path /contact --skip-newsletter` for the current canonical inquiry form. Local localhost runs verify the Lead through the Docker/Frappe bench container and delete the generated smoke Lead plus linked LT cascade Task; non-local authenticated runs can use `LT_ADMIN_PASSWORD`. | Before claiming form submissions work end-to-end |
| `category_media_candidates.py` | Builds a no-mutation JSON/Markdown approval packet for empty customer-facing Item Group images from existing Odoo product-source and portfolio-proof media. Outputs to ignored `output/category-media-candidates.*`. | When preparing category browse imagery for Jeff/GL review before assigning live Item Group images |
| `playwright_home_screenshot.py` | Real-Chromium full-page screenshot capture at desktop + mobile viewports + DOM facts dump. | Before declaring a visible change done |

## Standing Rules

- Layout fit is necessary but not sufficient. `npm run test:layout-fit` catches geometry regressions; it does not replace screenshot review or GL's real-browser check.
- Axe is part of public-site closeout for route/template changes. Accessibility launch blockers include contrast, landmarks, link names, heading order, breadcrumb regions, and keyboard/screen-reader semantics — not only visible styling.
- Idempotency over magic. Every script in `setup/` and `dev/` should check-then-act or no-op cleanly when state already exists.
- Loud errors. If a script's API call returns an error, surface it.
- No `deploy.py` yet. Frappe Cloud cutover is Phase 6. Until then, deployment-like operations live as discrete scripts in `setup/` or `dev/`.
