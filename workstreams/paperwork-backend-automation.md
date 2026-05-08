# Paperwork And Backend Automation

Last updated: 2026-05-08 by Codex after outbound document send-readiness blockers were added to the paperwork/automation spine.

## Outcome

Make Locally Twisted's paperwork path reliable enough for launch and simple enough for Jeff to run:

- customer inquiries get clear acknowledgment emails
- paid ready-to-order checkout creates the expected ERPNext records
- receipts, operator notifications, and welcome emails are queued once
- invoices and payment requests are visible for review
- customer reminders can be prepared as an internal dry-run queue and report rows without going live
- Sales Invoice print output is branded and policy-aligned
- corporate/event invoice language stays aligned with public policy pages
- backend automation creates reviewable work, not surprise accounting entries
- every handoff fails loudly when a required record, recipient, approval,
  payment path, send blocker, or mutation guard is missing

This lane coordinates paperwork, receipts, invoices, payment records, customer emails, reminder dry runs, reminder review reports, and backend automation boundaries. It does not replace `workstreams/finance-payroll-quickbooks-migration.md`, `workstreams/synthetic-business-pipeline.md`, `workstreams/customer-reminder-dry-run.md`, `workstreams/customer-reminder-review-report.md`, `workstreams/payment-backend-launch-readiness.md`, `workstreams/customer-document-policy-lanes.md`, or `workstreams/erpnext-backend-simplification.md`; it sequences the launch-critical parts of those lanes.

## Current Verified Baseline

Fresh local verification on 2026-05-06:

- `python scripts/verify/finance_inventory.py --json` passed.
- `python scripts/verify/customer_documents_contract.py` passed.
- `python scripts/verify/payment_cascade_contract.py` passed and rolled back generated records.
- `python scripts/verify/crm_stage_cascade.py` passed.
- `python scripts/verify/backend_schema_inventory.py` passed.
- `python scripts/verify/payment_backend_config_contract.py` passed.
- `python scripts/verify/payment_webhook_contract.py` passed.
- `python scripts/verify/payment_launch_readiness.py` passed in local/test mode.
- `python scripts/verify/checkout_lead_conversion_contract.py` passed and rolled back generated records.
- `python scripts/verify/finance_workspace_parity.py` passed.
- `python scripts/verify/finance_inventory_contract.py` passed.
- Live Stripe keys, webhook secret, production host, and real operator/customer data are cutover-only and were not used as current fake-data/backend readiness gates.
- `python scripts/verify/paperwork_status.py --report output/paperwork-status.json` passed in `synthetic_without_live_credentials` mode and generated a read-only paperwork status report with `live_cutover_checked: False`.
- `python scripts/verify/record_level_failure_contract.py --report output/record-level-failure-contract.json` passed and proved rollback-safe record-level backend blocker evidence.
- `python scripts/verify/inquiry_upload_failure_contract.py --report output/inquiry-upload-failure-contract.json` passed and proved rejected inquiry inspiration photos produce customer-visible and Lead-level evidence.
- `python scripts/verify/payment_success_reconciliation_contract.py --report output/payment-success-reconciliation-contract.json` passed and proved browser-return reconciliation errors show pending receipt/invoice copy on `/thank-you`.
- `python scripts/verify/synthetic_business_pipeline.py --report output/synthetic-business-pipeline.json` passed with 14 no-live synthetic contracts, 0 broken piping, 9 inefficiencies/partial connections, and 3 cutover-deferred items.
- `python scripts/verify/business_automation_index.py --report output/business-automation-index.json` passed and now maps 24 surfaces indexed, 14 launch-required, 20 connected, 4 exists-but-not-connected, 0 launch-required missing, 0 useful future surfaces missing, and 0 loud-failure gaps.
- `python scripts/verify/unpaid_invoice_review.py --report output/unpaid-invoice-review.json` passed and generated 1 overdue-review candidate for `ACC-SINV-2026-00001`. The candidate includes draft-only `payment_reminder_draft` and `statement_of_account` data, requires human review, and proves no customer send or accounting mutation happens.
- `python scripts/verify/unpaid_invoice_draft_packet.py --report output/unpaid-invoice-draft-packet.json --markdown output/unpaid-invoice-draft-packet.md` passed and rendered that candidate into draft-only `payment_reminder_draft` and `statement_of_account` packet sections for human review, while proving no customer send or accounting mutation happens.
- `python scripts/verify/unpaid_invoice_draft_packet_contract.py` passed and now covers fake normal/outlier packet behavior without touching ERPNext records, including PO references, multiple open invoices, missing payment requests, paid-invoice exclusion, and malformed human-approval gates.
- `python scripts/verify/paperwork_review_digest.py --report output/paperwork-review-digest.json` passed and combines paperwork status, business automation index, unpaid invoice review, and draft packet output into one internal read-only review payload with live payment setup labeled as `cutover_deferred_not_blocking`.
- `python scripts/verify/customer_reminder_dry_run_contract.py` passed and now covers no-live reminder queue behavior with fake overdue/current/missing-payment-path/malformed-send scenarios.
- `python scripts/verify/customer_reminder_dry_run.py --report output/customer-reminder-dry-run.json --markdown output/customer-reminder-dry-run.md` passed and generated 1 internal-review-only queue item for `ACC-SINV-2026-00001`, with `send_allowed: false`, `customer_delivery_enabled: false`, and `automatic_delivery_enabled: false`.
- `python scripts/verify/customer_reminder_review_report_contract.py` passed and now covers no-live reminder report rows/groups with fake mixed/empty/malformed-send source scenarios.
- `python scripts/verify/customer_reminder_review_report.py --report output/customer-reminder-review-report.json --markdown output/customer-reminder-review-report.md --csv output/customer-reminder-review-report.csv` passed and generated 1 internal-review-only report row for `ACC-SINV-2026-00001`, grouped under `review_now`.
- `python scripts/verify/stripe_amount_parity_contract.py` passed. Stripe Checkout line items now include a tax/charges adjustment when needed and must equal the ERPNext Sales Order grand total.
- `python scripts/verify/invoice_branding_contract.py` passed after syncing the branded Sales Invoice print format and Letter Head. The contract now requires gray vertical callouts for secondary/AP information, the exact black customer-service support bar, and no gold, navy, berry, soft promo colors, dog-logo markers, or old W-9/vendor wording in Sales Invoice print output.
- `python scripts/verify/outbound_documents_contract.py` passed after creating the standard outbound document source folder and templates. The contract now requires every outbound template to include `## Answer First`, and rendered previews put `Key fields to review` where the internal automation metadata used to appear.
- `python scripts/verify/outbound_document_send_readiness_contract.py` passed and proves every registered external document family blocks missing required fields, recipient confirmation, company branding, payment path, sensitive attachments, and human approval before any customer delivery; blocked documents can write record-level evidence.
- `python scripts/verify/render_outbound_document_previews.py --slug outbound-documents-answer-first-20260506 --no-open` rendered 20 fake-data review previews as HTML, PDF, and PNG under ignored `output/playwright/outbound-documents-answer-first-20260506/`.

Current live-data facts from the fresh finance inventory:

- Installed apps: `frappe`, `erpnext`, `payments`, `webshop`, `locally_twisted`.
- Counts: 4 Customers, 8 Sales Orders, 1 Sales Invoice, 8 Payment Requests, 0 Payment Entries, 0 Journal Entries, 0 Bank Accounts, 0 Bank Transactions, 0 Suppliers, 0 Employees.
- Collections: 1 unpaid Sales Invoice, 1 overdue Sales Invoice, 8 expected Payment Requests, 0 paid Payment Requests.
- Payment Terms now exist locally: 2 Payment Terms and 2 Payment Terms Templates.
- Email Queue status counts: 30 Sent, 0 pending in the latest paperwork status report.
- Company default bank account is not set.
- Payroll is not ready: HRMS is not installed and `Payroll Entry`, `Salary Slip`, and `Salary Structure` are missing.
- Sales Invoices now default to the code-owned `Locally Twisted Sales Invoice` print format. The format itself includes the visible logo/contact header so the normal default print view is branded; the branded `Locally Twisted` Letter Head also exists as a reusable setup record. The default invoice is intentionally restrained, black/white/gray, and accounts-payable friendly: one-line invoice number, a title-associated date/due/status/balance summary, padded item headers, PO/reference, expense category, itemized lines, clear totals, invoice/receipt terms, gray vertical callouts for secondary information, and a solid black customer-service/repeat-order support banner.
- The first AP-friendly pass still looked container-heavy because Frappe's print stylesheet imposed generous table padding and the custom format used a large boxed title/terms treatment. The current format flattens the document with horizontal rules, tighter scoped table padding, smaller logo/title sizing, fewer outlined containers, and neutral gray left-rule callouts so ordinary invoices fit a one-page PDF.

## Current Paperwork Map

### Inquiry paperwork

- Public `/contact` creates Leads.
- `lead_cascade.py` creates or links Contact records and queues customer acknowledgment emails.
- Inquiry acknowledgment emails include code-owned policy blocks from `locally_twisted.policy_documents`.
- Lead payment guidance fields exist for service/deposit timing, but they do not create money records.

### Ready-to-order checkout paperwork

- `/checkout` creates or reuses Customer, Contact, Address, Sales Order, and Payment Request records.
- Stripe checkout is the payment surface.
- `/payment-success` and the Stripe webhook reconcile paid orders.
- Paid-order cascade creates Payment Entry, submitted Sales Invoice, receipt email queue, operator notification queue, and first-order welcome email queue.
- The cascade is idempotent and covered by `payment_cascade_contract.py`.

### CRM and backend automation

- The LT business pipeline uses `Lead.custom_pipeline_stage`.
- Stage movement creates/closes operational Tasks only.
- Stage movement does not create or modify Customers, Quotes, Sales Orders, Sales Invoices, Payment Requests, Payment Entries, or win/loss reporting.
- Checkout-to-Lead conversion is coordinated: checkout can convert a matched Lead, move the custom stage to `Approved`, and keep the operational Task cascade aligned.

### Customer document policy blocks

- `policy_documents.py` owns reusable customer-facing policy blocks for inquiry emails and receipt emails.
- Public anchors are covered by `customer_documents_contract.py`.
- No ERPNext Terms and Conditions or Email Template records are currently added for these policy blocks.
- The branded Sales Invoice print format embeds the corporate invoicing lane and links to `/terms-of-service#corporate-invoicing`, `/refund-policy#corporate-invoicing`, and `/privacy`.

### Invoice print output

- `locally_twisted.seed.sync_invoice_branding` owns the `Locally Twisted Sales Invoice` Print Format, `Locally Twisted` Letter Head, and Sales Invoice `default_print_format` Property Setter.
- `scripts/setup/sync_invoice_branding.py` is idempotent and safe to re-run after invoice copy or style changes.
- `scripts/verify/invoice_branding_contract.py` verifies the setup records, default print-format resolution, visible logo/contact header, AP-friendly fields, gray callout treatment, black support-banner copy/treatment, forbidden gold/dog/promo markers, item-header padding, served logo asset, title-associated invoice summary placement, and rendered invoice HTML against the current sample Sales Invoice.
- External document standards now live in `.codex/capabilities/recipes/external-document-audience-contract.md`: every invoice, receipt, proposal, packet, and accounting document should be designed around the recipient's workflow before brand flourish.

### Outbound document source folder

- `apps/locally_twisted/locally_twisted/outbound_documents/` is the standard app-owned folder for external document source.
- `registry.py` lists the supported document families, record sources, delivery channels, and review gates.
- `send_readiness.py` is the no-send gate every future sender/review queue should call before treating an external document as ready.
- `templates/` now has source templates for Sales Invoice, Payment Receipt, Quote / Estimate, Event Proposal Packet, Vendor Setup / W-9 Packet, Statement Of Account, Payment Reminder Draft, Event Install Work Order, Contract Acceptance Summary, and Post-event Reorder Follow-up.
- These templates are generator-ready with review gates; they do not authorize automatic sending. Future automation should consume the registry to create drafts, PDFs, or review candidates before any live delivery.
- `scripts/verify/outbound_documents_contract.py` verifies the registry, required frontmatter, required body sections, no-auto-send boundary, placeholder presence, and unregistered-template guard.
- `scripts/verify/outbound_document_send_readiness_contract.py` verifies missing-field blockers, complete-payload readiness, payment-path blockers, vendor/W-9 secure-attachment blockers, and rollback-safe record-level blocker evidence.
- `scripts/verify/render_outbound_document_previews.py` renders normal and outlier fake-data previews for every registered document type. The current review set lives at `output/playwright/outbound-documents-20260506/index.html` and includes HTML, PDF, and PNG artifacts for each scenario.

### Unpaid invoice review

- `locally_twisted.paperwork.unpaid_invoice_review.run` is the first review-only surface for unpaid/overdue invoice follow-up.
- The host verifier is `scripts/verify/unpaid_invoice_review.py`.
- It reads submitted Sales Invoices with outstanding balance and returns reminder/statement draft candidate data from the outbound document registry.
- It does not create Email Queue rows, Communications, Payment Entries, Journal Entries, Payment Requests, or Sales Invoice mutations.
- Current local output: 1 overdue-review candidate for `ACC-SINV-2026-00001`, using `payment_reminder_draft` and `statement_of_account`.
- `statement_of_account.md` now explicitly includes `human_approval` in `do_not_send_without`, matching the no-send review contract.

### Unpaid invoice draft packets

- `locally_twisted.paperwork.unpaid_invoice_draft_packet.run` is the first renderer for the unpaid invoice review surface.
- The host verifier is `scripts/verify/unpaid_invoice_draft_packet.py`.
- Fake normal/outlier behavior is covered by `scripts/verify/unpaid_invoice_draft_packet_contract.py`.
- It reads the unpaid invoice review result, renders internal review packet sections for `payment_reminder_draft` and `statement_of_account`, and can write ignored JSON/Markdown review artifacts under `output/`.
- It does not create Email Queue rows, Communications, Payment Entries, Journal Entries, Payment Requests, or Sales Invoice mutations.
- Current local output: 1 draft-only packet for `ACC-SINV-2026-00001`, with `send_status: draft_only_not_sent`, `human_approval_required: true`, and a review checklist for invoice status, recipient, cadence, copy, and payment path.

### Customer reminder dry run

- `locally_twisted.paperwork.customer_reminder_dry_run.run` is the no-live customer reminder queue surface.
- The host verifier is `scripts/verify/customer_reminder_dry_run.py`.
- Fake normal/outlier behavior is covered by `scripts/verify/customer_reminder_dry_run_contract.py`.
- It reads the paperwork digest and unpaid invoice draft packets, then builds internal review queue items with cadence suggestions, draft sections, and explicit blockers.
- It does not create Email Queue rows, Communications, Payment Entries, Journal Entries, Payment Requests, Error Logs, or Sales Invoice mutations.
- Current local output: 1 internal-review-only queue item for `ACC-SINV-2026-00001`, with recommended cadence `review_now_payment_reminder`, `send_status: draft_only_not_sent`, `customer_delivery_enabled: false`, and blockers for human approval, recipient, invoice status, cadence, copy, and payment path where needed.

### Customer reminder review report

- `locally_twisted.paperwork.customer_reminder_review_report.run` is the no-live report-row source above the customer reminder dry-run queue.
- The host verifier is `scripts/verify/customer_reminder_review_report.py`.
- Fake normal/outlier behavior is covered by `scripts/verify/customer_reminder_review_report_contract.py`.
- It reads the dry-run queue, then builds table columns, rows, and `review_now` / `hold` / `blocked_send` groups for a future Desk page or internal-only report.
- It does not create Email Queue rows, Communications, Payment Entries, Journal Entries, Payment Requests, Error Logs, or Sales Invoice mutations.
- Current local output: 1 internal-review-only report row for `ACC-SINV-2026-00001`, with recommended cadence `review_now_payment_reminder`, `send_status: draft_only_not_sent`, and `customer_delivery_enabled: false`.

### Business automation index

- `workstreams/business-automation-index.md` is the cross-system map for intake, CRM, checkout, payment, paperwork, finance, and checkup surfaces.
- `locally_twisted.verify.business_automation_index.run` classifies each surface as `exists_and_connected`, `exists_but_not_connected`, `missing_needs_connection`, or `missing_should_connect`.
- The host wrapper is `scripts/verify/business_automation_index.py`.
- `hooks.py` now includes a daily Frappe scheduler entry for `locally_twisted.verify.business_automation_index.scheduled_checkup`.
- The scheduled checkup writes a Frappe Error Log if a launch-required connection breaks or a loud-failure gap appears.
- Current exists-but-not-connected surfaces are quote/proposal generation, vendor setup/W-9 packet generation, bank reconciliation cutover, and payroll/HRMS.
- No currently indexed useful surface is missing; outbound document send-readiness, unpaid/overdue invoice review, unpaid invoice packet rendering, paperwork digest, customer reminder dry-run queue, and customer reminder review report are connected as draft-only/no-live paperwork surfaces.

### Accountant and finance workspace

- Accountant Home parity is verified.
- It exposes unpaid invoices, overdue invoices, expected payments, recent paid orders, Sales Invoices, Payment Requests, and Payments.
- This is visibility and review, not automatic collections.

## Active Risks

- Live Stripe cutover is intentionally deferred from this lane. Live Stripe keys, webhook secret, production host, and real operator/customer details are checked only during cutover work, not during fake-data pipeline audits.
- Bank setup is missing: no Bank Account records and no Company default bank account.
- Supplier/vendor setup is missing, so contractor/1099 paperwork is not operational.
- Payroll is feasibility-only until HRMS/payroll DocTypes exist and accountant/provider approval is in place.
- One unpaid and overdue Sales Invoice exists in local data. Treat it as a review target, not as approval to send reminders.
- Automated customer reminders are not approved. Copy, cadence, audience, edge cases, and opt-out handling need approval before sending.
- Manual stage-to-finance automation still needs explicit threshold design. Do not duplicate the checkout money path from CRM stage movement.

## First Safe Slices

1. **Business automation index.** First pass done. `scripts/verify/business_automation_index.py` is the launch spine map and daily checkup source. Keep this green before adding new automations.
2. **Paperwork status report.** First pass done. `scripts/verify/paperwork_status.py` summarizes current invoices, payment requests, email queues, overdue records, and bank/supplier/payroll gaps without printing secrets or mutating ERPNext. It reports live payment setup as cutover-deferred and does not run live readiness in synthetic mode.
3. **Synthetic business pipeline audit.** First pass done. `scripts/verify/synthetic_business_pipeline.py` runs no-live fake-data/rollback-safe contracts for record-level backend evidence, inquiry upload failure evidence, checkout-to-Lead, checkout fulfillment, payment cascade, payment-success pending reconciliation, mocked webhook behavior, document policy, outbound templates, outbound send-readiness, unpaid invoice outliers, customer reminder dry-run outliers, and customer reminder review-report outliers. It fails on broken piping or fake-data cleanup leaks.
4. **Unpaid invoice review queue.** First pass done as a draft-only report surface. Draft packet rendering is also done. Next is reviewed Desk UX or scheduled internal review digest, still no reminder sending.
5. **Paperwork review digest.** First pass done as a read-only internal review payload. Next is a real reviewed Desk queue or scheduled internal-only report UI, still no customer sending.
6. **Customer reminder dry run.** First pass done as a no-live internal review queue payload.
7. **Customer reminder review report.** First pass done as no-live report rows/groups above the dry-run queue. Next is a real Desk page using the report rows, still no customer sending.
8. **Receipt/operator email audit.** Extend verifier coverage so receipt, operator, welcome, and inquiry acknowledgment email bodies keep the right policy lanes and do not attach PDFs.
9. **Outbound document template registry.** Done for the first standard set. Extend this folder before creating any new outbound document family elsewhere.
   - Standing rule: every outbound document is answer-first. The recipient should see the practical fields they care about before internal automation notes or policy mechanics.
10. **Outbound document send-readiness.** Done as a reusable no-send gate. Future senders must pass it before customer delivery.
11. **Corporate invoice packet design.** Source template exists. Remaining work is generator/rendering design for larger events without creating an ERPNext Terms record yet.
12. **Stage threshold design.** Document which stage should create/update Quote, Sales Order, Project/job, Calendar invite, customer follow-up, invoice, or payment request. Do not implement until the threshold is explicit.

## Do Not Do

- Do not auto-submit Sales Invoices, Purchase Invoices, Journal Entries, Payment Entries, payroll records, or write-offs from CRM stages.
- Do not send customer reminders from overdue invoices until the exact copy, timing, audience, and approval path are accepted.
- Do not enable bank sync or Plaid credentials during ordinary launch work.
- Do not claim payroll readiness from the `Employee` DocType alone.
- Do not import QuickBooks transaction history beyond accountant-approved active cutover data.
- Do not add ERPNext Terms/Email Template records unless a verified customer-facing invoice path truly needs them.

## Verification

Core paperwork/backend baseline:

```powershell
python scripts/verify/finance_inventory.py --json
python scripts/verify/customer_documents_contract.py
python scripts/verify/payment_cascade_contract.py
python scripts/verify/crm_stage_cascade.py
python scripts/verify/backend_schema_inventory.py
python scripts/verify/payment_backend_config_contract.py
python scripts/verify/payment_webhook_contract.py
python scripts/verify/payment_launch_readiness.py
python scripts/verify/synthetic_business_pipeline.py --report output/synthetic-business-pipeline.json
python scripts/verify/business_automation_index.py --report output/business-automation-index.json
python scripts/verify/stripe_amount_parity_contract.py
python scripts/verify/checkout_lead_conversion_contract.py
python scripts/verify/finance_workspace_parity.py
python scripts/verify/finance_inventory_contract.py
python scripts/verify/paperwork_status.py --report output/paperwork-status.json
python scripts/verify/unpaid_invoice_review.py --report output/unpaid-invoice-review.json
python scripts/verify/unpaid_invoice_draft_packet.py --report output/unpaid-invoice-draft-packet.json
python scripts/verify/unpaid_invoice_draft_packet_contract.py
python scripts/verify/paperwork_review_digest.py --report output/paperwork-review-digest.json
python scripts/verify/customer_reminder_dry_run.py --report output/customer-reminder-dry-run.json
python scripts/verify/customer_reminder_dry_run_contract.py
python scripts/verify/customer_reminder_review_report.py --report output/customer-reminder-review-report.json
python scripts/verify/customer_reminder_review_report_contract.py
python scripts/setup/sync_invoice_branding.py
python scripts/verify/invoice_branding_contract.py
python scripts/verify/outbound_documents_contract.py
python scripts/verify/outbound_document_send_readiness_contract.py
python scripts/verify/render_outbound_document_previews.py --slug outbound-documents-20260506
```

Cutover-only payment check:

```powershell
python scripts/verify/payment_launch_readiness.py --mode live
```

Run this only during cutover work. It is not part of the current synthetic/backend readiness gate.

## Next Handoff Stage

Next no-approval slice: turn the customer reminder review report rows into a reviewed Desk page for Jeff/accounting. It should show candidate invoices, rendered reminder/statement sections, setup gaps, cutover-deferred items, and review checkboxes for recipient/status/cadence/copy/payment path. It must not send reminders, submit/cancel accounting records, or use live credentials/real customer data.
