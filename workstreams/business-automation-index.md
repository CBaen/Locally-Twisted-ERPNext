# Business Automation Index

Last updated: 2026-05-10 by Codex after adding the product quote operator send control.

## Outcome

Make Locally Twisted's business system inspectable before it is trusted in Frappe Cloud:

- every important intake, CRM, checkout, payment, paperwork, and finance surface is classified
- connected launch surfaces are backed by a verifier command
- partially built surfaces are named instead of implied
- missing useful surfaces are listed as deliberate next slices
- payment and document paths fail loudly instead of silently drifting
- fake-data test paths are explicit and safe to run during development

Operating law: if it can fail, it must fail loudly. In this lane, "loud" means
the index, scheduled checkup, synthetic pipeline, or surface-specific verifier
names the broken connection and exits nonzero or writes operational evidence
instead of letting a missing handoff look connected.

GL clarified on 2026-05-07 that all current LT records are fake/test data for
automation testing. Keep using fake data aggressively, but do not treat it as
business truth. The next index upgrade is record-level health rows from
`workstreams/fail-loud-record-level-hardening.md`: exact Leads, Sales Orders,
Payment Requests, Sales Invoices, Email Queue rows, and documents whose
expected downstream automation failed or is blocked.

This workstream is the cross-system map. It coordinates with `paperwork-backend-automation.md`, `synthetic-business-pipeline.md`, `payment-backend-launch-readiness.md`, `finance-payroll-quickbooks-migration.md`, `erpnext-backend-simplification.md`, and `website-launch.md`.

## Current Verified Result

Latest report:

```powershell
python scripts/verify/business_automation_index.py --report output/business-automation-index.json
```

Current result on 2026-05-10:

- `ok: true`
- 30 total surfaces indexed
- 12 launch-required surfaces
- 27 surfaces exist and are connected
- 3 surfaces exist but are not connected
- 0 launch-required missing surfaces
- 0 useful future surfaces missing
- 0 loud-failure gaps
- `runtime_contracts_executed: true` for the full verifier command.

Internal report/digest callers now use `run_runtime_contracts=False`. That mode still checks files, hooks, DocTypes, setup records, and open record-level blockers, but it does not execute rollback-heavy fake-data contracts while rendering accountant/operator review surfaces.

The report is read-only and writes the current JSON snapshot to `output/business-automation-index.json`.

Fresh closeout verification also confirmed:

- record-level backend failure evidence writes rollback-safe Error Log and record blocker evidence.
- rejected inquiry inspiration uploads now return a customer-visible upload summary and write Lead-level evidence.
- `/contact` smoke submission verified backend Lead creation and cleanup with marker `SMOKE-TEST-1778371709633066300`.
- Frappe's hook registry includes `locally_twisted.verify.business_automation_index.scheduled_checkup` under `daily`.
- Live Stripe keys, webhook secrets, production host checks, and real operator/customer data are cutover-only and are not part of the current synthetic readiness gate.
- `paperwork_status.py` reports 46 sent Email Queue rows, 1 unpaid/overdue Sales Invoice, 8 expected Payment Requests, no pending email queue rows, and `live_cutover_checked: False`.
- `unpaid_invoice_review.py` reports 1 overdue-review candidate and creates draft-only reminder/statement candidate data without sending or mutating records.
- `unpaid_invoice_draft_packet.py` renders the overdue-review candidate into draft-only reminder and statement packet sections without sending or mutating records.
- `unpaid_invoice_draft_packet_contract.py` verifies normal/outlier packet behavior with fake data, including missing payment links and malformed approval gates.
- `paperwork_review_digest.py` combines the paperwork status, automation index, unpaid review, and draft packets into one internal read-only review payload. It includes `operations_readiness` rows for company/operator, vendor/contractor, accountant/finance reviewer, and customer/public-user readiness, and consumes the automation index with `run_runtime_contracts=False`.
- `customer_reminder_dry_run.py` builds 1 internal-review-only reminder queue item locally, with no customer delivery enabled.
- `customer_reminder_dry_run_contract.py` verifies no-live reminder queue behavior with fake overdue/current/missing-payment-path/malformed-send scenarios.
- `customer_reminder_review_report.py` turns the dry-run queue into 1 internal review report row grouped under `review_now`, with no customer delivery enabled.
- `customer_reminder_review_report_contract.py` verifies report rows/groups with fake mixed/empty/malformed-send source scenarios.
- `customer_email_policy_contract.py` verifies inquiry acknowledgment, paid receipt, operator notification, first-order welcome, and paid-order email cascade policy/no-PDF boundaries without sending email or mutating records.
- `maintenance_heartbeat.py` verifies the sanitized client operations heartbeat, owner-selected notification topics/cadence surface, approval tiers, and Maintenance Admin raw-log/customer-data boundary.
- `synthetic_business_pipeline.py` runs 16 active no-live synthetic readiness contracts with 0 broken piping and keeps 9 cutover items deferred.
- Product-page quote operator review, accepted-quote-to-draft-order, customer quote delivery, and operator send-control checks are indexed through `business_automation_product_quote.py`, so the main automation index stays a registry instead of absorbing feature-specific checkers.

## Connected Launch Spine

These are currently classified as existing and connected:

- `/contact` public form to ERPNext Lead fields
- Lead insert to Contact dedup/link, acknowledgment email, and operational Task
- custom CRM stage movement to operational Tasks only
- guest checkout to Customer, Contact, Address, Sales Order, Payment Request, and Stripe redirect without final Lead conversion before payment
- paid checkout reconciliation to Lead conversion, Payment Request, Payment Entry, Sales Invoice, receipt email, operator notification, and welcome email
- Stripe Checkout amount parity with ERPNext Sales Order grand total
- Stripe webhook reconciliation through the paid-order helper
- branded Sales Invoice print output
- outbound document registry and source templates
- outbound document send-readiness blockers
- draft-only quote/proposal review packets
- product-page quote operator-review readiness with no send/order/payment
- accepted product-page quotes to draft Sales Orders with no invoice/payment/email side effects
- `/quote-accept` real-token customer failure/success UX gate
- customer quote approval-link delivery with required business BCC
- operator-owned Quotation send control for reviewed product-page quotes
- read-only paperwork status checkup
- draft-only unpaid/overdue invoice review candidates
- draft-only unpaid invoice reminder/statement packet rendering
- internal paperwork review digest
- no-live customer reminder dry-run queue
- no-live customer reminder Desk Script Report
- no-live customer/operator email policy boundary contract
- sanitized client operations heartbeat and Maintenance Admin access boundary
- no-live synthetic business pipeline audit
- scheduled daily business automation checkup plus hourly light/daily full maintenance heartbeat
- Accountant Home workspace parity
- record-level backend failure recorder
- inquiry upload rejection/failure evidence
- payment-success pending reconciliation copy

## Exists But Not Connected

These should not be described as operational yet:

- Vendor setup/W-9 packet generation: template exists, but no Supplier/vendor data, approved W-9 registry, or secure-send workflow is connected.
- Bank reconciliation cutover: ERPNext banking DocTypes exist, but LT has no Bank Account record or Company default bank account.
- Payroll/HRMS: payroll belongs in the future all-in-one system, but HRMS is not installed and payroll DocTypes are missing.

## Missing But Should Connect

No currently indexed useful surface is missing. Future useful surfaces should be added here deliberately instead of buried in handoff prose.

## Loud Failure Contract

Launch-required surfaces should fail loudly when required files, hooks, whitelisted methods, setup records, amount parity, maintenance boundaries, or scheduler wiring are missing.

Important current guardrails:

- `business_automation_index.py` exits nonzero when a launch-required surface is missing or disconnected.
- `business_automation_index.run(run_runtime_contracts=False)` is the correct mode for internal report/digest callers. Use the full default runtime-contract mode only from explicit verification, scheduled checkups, or synthetic readiness gates.
- Frappe scheduler runs `locally_twisted.verify.business_automation_index.scheduled_checkup` daily, the light maintenance heartbeat hourly, and the full maintenance heartbeat daily.
- The scheduled checkup writes a Frappe Error Log when launch-required failures, missing required connections, or loud-failure gaps appear.
- The maintenance heartbeat writes only sanitized Maintenance Run/Event rows and compact Error Log evidence; raw logs and customer records stay outside the Maintenance Admin role.
- `stripe_line_items_for_sales_order()` now raises `frappe.ValidationError` if Stripe line items would charge less or more than the ERPNext Sales Order grand total.
- Live payment readiness is cutover-only. Do not use live keys, real operator details, or real customer data as blockers for synthetic pipeline work.

## Fake Data Contracts

Safe fake-data verifiers are part of the operating model:

- `synthetic_business_pipeline.py` runs the current no-live operating-readiness suite and fails if broken piping appears.
- `record_level_failure_contract.py` creates rollback-safe record-level backend failure evidence and proves exact resolution comments close a grouping key without deleting the original evidence.
- `inquiry_upload_failure_contract.py` proves rejected inspiration photos produce customer-visible and Lead-level evidence.
- `smoke_forms.py` creates and deletes a test Lead and linked cascade Task.
- `checkout_lead_conversion_contract.py` creates rollback-only checkout records, proves the Lead stays pending before payment, then proves paid-order conversion.
- `payment_cascade_contract.py` creates rollback-only paid-order cascade records.
- `crm_stage_cascade.py` creates rollback-only CRM/Task cascade records.
- outbound document preview rendering uses fake normal and outlier data under ignored `output/`.
- outbound document send-readiness uses fake payloads and rollback-safe record-level blocker evidence.
- `customer_reminder_dry_run_contract.py` uses in-memory fake reminder queue payloads and creates no database records.
- `customer_reminder_review_report_contract.py` uses in-memory fake reminder report payloads and creates no database records.
- `product_quote_operator_review_contract.py` uses in-memory fake product quote review payloads and creates no database records.
- `product_quote_acceptance_contract.py` creates rollback-safe Lead, Quotation, Customer, and draft Sales Order records, then proves invoices, payment requests, Email Queue rows, and Communications do not change.
- `product_quote_customer_delivery_contract.py` creates rollback-safe Lead and Quotation records, stubs `frappe.sendmail`, requires a delivery-safe business BCC, rejects routed-alias BCCs such as `hi@locallytwisted.com`, and proves order/finance/email counts do not change.
- `product_quote_operator_send_control_contract.py` creates rollback-safe Lead and Quotation records, verifies the Quotation Desk button hook plus whitelisted operator method, stubs `frappe.sendmail`, requires a delivery-safe business BCC, and proves order/finance/email counts do not change.
- `customer_email_policy_contract.py` is a static source contract and creates no database records.
- `maintenance_heartbeat.py` can run read-only, and scheduled writes persist sanitized heartbeat summaries only.

Use fake data aggressively in local verification, but do not leave generated business records behind.

## Verification Commands

Core automation map:

```powershell
python scripts/verify/business_automation_index.py --report output/business-automation-index.json
python scripts/verify/synthetic_business_pipeline.py --report output/synthetic-business-pipeline.json
python scripts/verify/record_level_failure_contract.py --report output/record-level-failure-contract.json
python scripts/verify/inquiry_upload_failure_contract.py --report output/inquiry-upload-failure-contract.json
python scripts/verify/payment_success_reconciliation_contract.py --report output/payment-success-reconciliation-contract.json
python scripts/verify/customer_email_policy_contract.py
python scripts/verify/outbound_document_send_readiness_contract.py
python scripts/verify/quote_proposal_draft_packet.py --report output/quote-proposal-draft-packet.json
python scripts/verify/quote_proposal_draft_packet_contract.py
python scripts/verify/product_quote_operator_review.py --report output/product-quote-operator-review.json
python scripts/verify/product_quote_operator_review_contract.py
python scripts/verify/product_quote_acceptance_contract.py
npm run test:quote-accept-experience
python scripts/verify/product_quote_customer_delivery_contract.py
python scripts/verify/product_quote_operator_send_control_contract.py
python scripts/verify/stripe_amount_parity_contract.py
python scripts/verify/paperwork_status.py --report output/paperwork-status.json
python scripts/verify/unpaid_invoice_review.py --report output/unpaid-invoice-review.json
python scripts/verify/unpaid_invoice_draft_packet.py --report output/unpaid-invoice-draft-packet.json
python scripts/verify/unpaid_invoice_draft_packet_contract.py
python scripts/verify/paperwork_review_digest.py --report output/paperwork-review-digest.json
python scripts/verify/customer_reminder_dry_run.py --report output/customer-reminder-dry-run.json
python scripts/verify/customer_reminder_dry_run_contract.py
python scripts/verify/customer_reminder_review_report.py --report output/customer-reminder-review-report.json
python scripts/verify/customer_reminder_review_report_contract.py
python scripts/setup/sync_maintenance_package.py
python scripts/verify/maintenance_heartbeat.py --heavy
python scripts/verify/maintenance_admin_boundary.py
```

Launch money path:

```powershell
python scripts/verify/payment_backend_config_contract.py
python scripts/verify/payment_webhook_contract.py
python scripts/verify/payment_cascade_contract.py
python scripts/verify/checkout_lead_conversion_contract.py
python scripts/verify/checkout_fulfillment_contract.py
```

Public intake and CRM:

```powershell
python scripts/verify/lead_backend_intake_parity.py
python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --form-path /contact --skip-newsletter
python scripts/verify/crm_stage_cascade.py
```

Paperwork and finance visibility:

```powershell
python scripts/verify/customer_documents_contract.py
python scripts/verify/customer_email_policy_contract.py
python scripts/verify/invoice_branding_contract.py
python scripts/verify/outbound_documents_contract.py
python scripts/verify/outbound_document_send_readiness_contract.py
python scripts/verify/quote_proposal_draft_packet.py --report output/quote-proposal-draft-packet.json
python scripts/verify/quote_proposal_draft_packet_contract.py
python scripts/verify/product_quote_operator_review.py --report output/product-quote-operator-review.json
python scripts/verify/product_quote_operator_review_contract.py
python scripts/verify/product_quote_acceptance_contract.py
npm run test:quote-accept-experience
python scripts/verify/product_quote_customer_delivery_contract.py
python scripts/verify/product_quote_operator_send_control_contract.py
python scripts/verify/unpaid_invoice_review.py --report output/unpaid-invoice-review.json
python scripts/verify/unpaid_invoice_draft_packet.py --report output/unpaid-invoice-draft-packet.json
python scripts/verify/unpaid_invoice_draft_packet_contract.py
python scripts/verify/paperwork_review_digest.py --report output/paperwork-review-digest.json
python scripts/verify/customer_reminder_dry_run.py --report output/customer-reminder-dry-run.json
python scripts/verify/customer_reminder_dry_run_contract.py
python scripts/setup/sync_finance_workspace.py
python scripts/verify/customer_reminder_review_report.py --report output/customer-reminder-review-report.json
python scripts/verify/customer_reminder_review_report_contract.py
python scripts/verify/finance_workspace_parity.py
python scripts/verify/backend_workspace_parity.py
python scripts/setup/sync_maintenance_package.py
python scripts/verify/maintenance_heartbeat.py --heavy
python scripts/verify/maintenance_admin_boundary.py
```

Cutover-only check:

```powershell
python scripts/verify/payment_launch_readiness.py --mode live
```

Run this only during cutover work. It is intentionally not part of the current synthetic readiness gate.

## Next Safe Slices

- Keep no-send paperwork/reporting and sanitized maintenance checkups green while reviewing any remaining read-only report surfaces.
- Keep vendor/W-9 generation, bank reconciliation cutover, payroll/HRMS, and stage-to-finance automation explicitly disconnected until their approval/setup gates are real.
- Quote/proposal packets and product quote operator review are connected only as draft-only/internal review output. The operator send control can send a reviewed submitted quote approval link, but it still does not create a Sales Order, invoice, payment request, PDF, or payment path.
