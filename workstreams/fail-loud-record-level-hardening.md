# Fail-Loud Record-Level Hardening

Last updated: 2026-05-07 by OpenClaw/Moji from GL + Codex direction.

## Operating Truth

All current Locally Twisted ERPNext/Frappe data is fake/test data for automation testing until GL explicitly says otherwise.

That does **not** lower the standard. It raises it:

- fake/test records are allowed and expected;
- fake success is not allowed;
- skipped partial failures must become visible record-level evidence;
- any automation that can/should happen must either happen or create a loud, queryable blocker.

Rule from GL/Codex:

> Implement the rule anywhere a failure can hide customer intent, lose payment context, send wrong paperwork, or make the business think something happened when it did not.

## Target Contract

Any customer-facing or operator-facing flow has only three acceptable outcomes:

1. **Success** — all required downstream work happened and has witnesses.
2. **Visible recoverable issue** — the primary record exists, but one or more downstream steps failed and a visible internal blocker/report row/comment exists.
3. **Visible failure** — the customer/operator is not shown fake success, and backend evidence names the failed connection.

No quiet skip. No “logged somewhere” as the only signal for business-critical loss. No customer-visible success that hides lost customer intent, lost payment context, or unsafe paperwork.

## Recommended First Implementation Slice

Build one reusable backend failure recorder, then wire it into the highest-value partial-failure paths.

### 1. Reusable backend failure recorder

Create a shared utility that can attach structured blocker evidence to business records.

Minimum fields:

- source surface / flow name;
- failing step;
- severity;
- primary DocType/name;
- linked DocType/name when available;
- customer-visible impact;
- internal next action;
- original exception/error summary;
- timestamp;
- checkup/report grouping key.

Expected durable surfaces:

- Frappe Error Log for developer/operator visibility;
- comment/timeline entry or custom blocker marker on the affected Lead/Sales Order/Payment Request/Sales Invoice where safe;
- business automation index/report row for scheduled discovery.

### 2. Inquiry intake photo handling

File:

- `apps/locally_twisted/locally_twisted/www/book.py`

Current concern:

- Lead creation fails loudly, but invalid/oversized/excess uploaded photos can be skipped.
- That protects storage, but can silently lose customer context.

Required behavior:

- return a visible upload summary;
- attach rejected/failed upload details to the Lead timeline/internal evidence;
- make the automation checkup flag Leads where submitted files were rejected or failed.

### 3. Lead cascade

File:

- `apps/locally_twisted/locally_twisted/lead_cascade.py`

Current concern:

- The current philosophy says backend hiccups should not block form success once the Lead exists.
- That is okay for the customer path only if internal failure becomes loud.

Required behavior:

- customer form may still succeed once the Lead exists;
- failed Contact creation, acknowledgment email, Task creation, or stage cascade must create visible internal blockers;
- scheduled checkups must report exact Lead/Contact/Task/email issue IDs.

### 4. Checkout customer-info transfer

File:

- `apps/locally_twisted/locally_twisted/www/checkout.py`

Current concern:

- Lead conversion and checkout notes can fail while order/payment continues with only Error Log evidence.

Required behavior:

- payment can continue;
- Sales Order receives a visible internal blocker/comment for failed Lead conversion or note transfer;
- checkup reports exact Sales Order / Lead IDs.

### 5. Stripe and paid-order reconciliation

Files:

- `apps/locally_twisted/locally_twisted/payments/stripe_session.py`
- `apps/locally_twisted/locally_twisted/payments/stripe_webhook.py`
- `apps/locally_twisted/locally_twisted/www/payment_success.py`

Current concern:

- Amount parity and webhook retry behavior are strong.
- Receipt delivery can quietly log/return when no receipt email is found.

Required behavior:

- paid order missing receipt email becomes reconciliation failure/blocker, not quiet skip;
- thank-you page distinguishes “payment received” from “invoice/receipt still being finalized” when backend reconciliation has errors.

### 6. Invoices and outbound documents

Files:

- `apps/locally_twisted/locally_twisted/outbound_documents/registry.py`
- `apps/locally_twisted/locally_twisted/seed/sync_invoice_branding.py`
- `apps/locally_twisted/locally_twisted/verify/invoice_branding_contract.py`

Required behavior before external send/readiness:

- correct recipient;
- invoice number;
- bill-to;
- balance;
- due date;
- payment terms;
- payment link/path;
- company branding;
- required corporate bookkeeping fields.

If any are missing, the document is not send-ready.

### 7. Unpaid invoice reminders / statements

Folder:

- `apps/locally_twisted/locally_twisted/paperwork/`

Current posture:

- draft-only is correct.

Future send-path guard:

- no customer delivery unless invoice status, recipient, cadence, balance, and copy have all been reviewed.

### 8. Business automation index as central dashboard

File:

- `apps/locally_twisted/locally_twisted/verify/business_automation_index.py`

Required upgrade:

Record-level health checks for:

- Leads missing Contacts;
- Leads missing acknowledgment;
- Leads with rejected/failed photo uploads;
- Sales Orders missing checkout notes;
- Sales Orders with failed Lead conversion;
- Payment Requests without Stripe sessions;
- paid orders missing Sales Invoices;
- paid orders missing receipt emails;
- failed Email Queue rows;
- invoices missing payment paths;
- documents not send-ready due to required field gaps.

## Verification Gates

The implementation slice is not complete until there are witnesses for:

- fake-data tests can create/rollback or use in-memory payloads safely;
- backend failure recorder writes durable blocker evidence;
- Lead cascade failures show up in record evidence and business automation report;
- checkout note/Lead-conversion failures show up in Sales Order evidence and business automation report;
- paid-order receipt failures show up as reconciliation blockers;
- automation index exits/report-fails on record-level loud-failure gaps;
- no live customer emails/reminders/accounting mutations occur during tests.

Candidate commands to extend/run:

```powershell
python scripts/verify/business_automation_index.py --report output/business-automation-index.json
python scripts/verify/synthetic_business_pipeline.py --report output/synthetic-business-pipeline.json
python scripts/verify/lead_backend_intake_parity.py
python scripts/verify/checkout_lead_conversion_contract.py
python scripts/verify/payment_cascade_contract.py
python scripts/verify/customer_documents_contract.py
python scripts/verify/outbound_documents_contract.py
python scripts/verify/unpaid_invoice_draft_packet_contract.py
python scripts/verify/customer_reminder_review_report_contract.py
```

## Do Not Do

- Do not treat current fake/test data as real customer/business truth.
- Do not use live Stripe keys, webhook secrets, bank credentials, payroll/tax credentials, or real customer messaging for this hardening lane.
- Do not send customer reminders or statements.
- Do not auto-submit Sales Invoices, Purchase Invoices, Journal Entries, Payment Entries, payroll records, or tax filings.
- Do not call the system ready because an Error Log exists; the affected business record/report must make the issue visible.

## Done When

- The reusable failure recorder exists and is used by the first critical flows.
- Record-level checkup rows identify exact affected records and missing downstream steps.
- Existing fake-data verifier suite passes.
- New failure-path verifier(s) prove that partial failures become visible blockers.
- Queue and business automation index report no launch-required loud-failure gaps.
