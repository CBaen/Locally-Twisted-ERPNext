# Business Automation Index

Last updated: 2026-05-06 by Codex after creating the first read-only automation index, adding the daily Frappe scheduler checkup, wiring the Stripe amount-parity contract, and completing the closeout verification pass.

## Outcome

Make Locally Twisted's business system inspectable before it is trusted in Frappe Cloud:

- every important intake, CRM, checkout, payment, paperwork, and finance surface is classified
- connected launch surfaces are backed by a verifier command
- partially built surfaces are named instead of implied
- missing useful surfaces are listed as deliberate next slices
- payment and document paths fail loudly instead of silently drifting
- fake-data test paths are explicit and safe to run during development

This workstream is the cross-system map. It coordinates with `paperwork-backend-automation.md`, `payment-backend-launch-readiness.md`, `finance-payroll-quickbooks-migration.md`, `erpnext-backend-simplification.md`, and `website-launch.md`.

## Current Verified Result

Latest report:

```powershell
python scripts/verify/business_automation_index.py --report output/business-automation-index.json
```

Current result on 2026-05-06:

- `ok: true`
- 17 total surfaces indexed
- 11 launch-required surfaces
- 12 surfaces exist and are connected
- 4 surfaces exist but are not connected
- 0 launch-required missing surfaces
- 1 useful future surface missing
- 0 loud-failure gaps

The report is read-only and writes the current JSON snapshot to `output/business-automation-index.json`.

Fresh closeout verification also confirmed:

- `/contact` smoke submission verified backend Lead creation and cleanup with marker `SMOKE-TEST-1778091063`.
- Frappe's hook registry includes `locally_twisted.verify.business_automation_index.scheduled_checkup` under `daily`.
- `payment_launch_readiness.py --mode live` fails for the expected cutover blockers: live Stripe keys, explicit site config keys, operator email config, and production host.
- `paperwork_status.py` reports 30 sent Email Queue rows, 1 unpaid/overdue Sales Invoice, 8 expected Payment Requests, and no pending email queue rows.

## Connected Launch Spine

These are currently classified as existing and connected:

- `/contact` public form to ERPNext Lead fields
- Lead insert to Contact dedup/link, acknowledgment email, and operational Task
- custom CRM stage movement to operational Tasks only
- guest checkout to Customer, Contact, Address, Sales Order, Payment Request, and Stripe redirect
- paid checkout reconciliation to Payment Request, Payment Entry, Sales Invoice, receipt email, operator notification, and welcome email
- Stripe Checkout amount parity with ERPNext Sales Order grand total
- Stripe webhook reconciliation through the paid-order helper
- branded Sales Invoice print output
- outbound document registry and source templates
- read-only paperwork status checkup
- scheduled daily business automation checkup
- Accountant Home workspace parity

## Exists But Not Connected

These should not be described as operational yet:

- Quote/proposal generation: templates exist, but no Quotation-to-PDF generation or approval queue is wired.
- Vendor setup/W-9 packet generation: template exists, but no Supplier/vendor data, approved W-9 registry, or secure-send workflow is connected.
- Bank reconciliation cutover: ERPNext banking DocTypes exist, but LT has no Bank Account record or Company default bank account.
- Payroll/HRMS: payroll belongs in the future all-in-one system, but HRMS is not installed and payroll DocTypes are missing.

## Missing But Should Connect

- Unpaid/overdue invoice review surface: this should turn `paperwork_status.py` output into a review queue and draft reminder/statement candidates. It must not send reminders or submit accounting records.

## Loud Failure Contract

Launch-required surfaces should fail loudly when required files, hooks, whitelisted methods, setup records, amount parity, or scheduler wiring are missing.

Important current guardrails:

- `business_automation_index.py` exits nonzero when a launch-required surface is missing or disconnected.
- Frappe scheduler runs `locally_twisted.verify.business_automation_index.scheduled_checkup` daily.
- The scheduled checkup writes a Frappe Error Log when launch-required failures, missing required connections, or loud-failure gaps appear.
- `stripe_line_items_for_sales_order()` now raises `frappe.ValidationError` if Stripe line items would charge less or more than the ERPNext Sales Order grand total.
- Live payment readiness is expected to fail until production Stripe keys, explicit site config, operator email, and production host are configured.

## Fake Data Contracts

Safe fake-data verifiers are part of the operating model:

- `smoke_forms.py` creates and deletes a test Lead and linked cascade Task.
- `checkout_lead_conversion_contract.py` creates rollback-only checkout/Lead conversion records.
- `payment_cascade_contract.py` creates rollback-only paid-order cascade records.
- `crm_stage_cascade.py` creates rollback-only CRM/Task cascade records.
- outbound document preview rendering uses fake normal and outlier data under ignored `output/`.

Use fake data aggressively in local verification, but do not leave generated business records behind.

## Verification Commands

Core automation map:

```powershell
python scripts/verify/business_automation_index.py --report output/business-automation-index.json
python scripts/verify/stripe_amount_parity_contract.py
python scripts/verify/paperwork_status.py --report output/paperwork-status.json
```

Launch money path:

```powershell
python scripts/verify/payment_backend_config_contract.py
python scripts/verify/payment_webhook_contract.py
python scripts/verify/payment_launch_readiness.py
python scripts/verify/payment_cascade_contract.py
python scripts/verify/checkout_lead_conversion_contract.py
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
python scripts/verify/invoice_branding_contract.py
python scripts/verify/outbound_documents_contract.py
python scripts/verify/finance_workspace_parity.py
python scripts/verify/backend_workspace_parity.py
```

Cutover-only check:

```powershell
python scripts/verify/payment_launch_readiness.py --mode live
```

Expected current result: fail until live Stripe/site configuration is set.

## Next Safe Slice

Build the unpaid/overdue invoice review surface:

- read from `paperwork_status.py`
- show invoices needing attention
- create draft reminder or statement candidates from the outbound document registry
- require review before any customer-facing send
- add a verifier that proves no reminders or accounting mutations happen without approval
