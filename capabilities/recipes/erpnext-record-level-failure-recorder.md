---
id: erpnext-record-level-failure-recorder
name: ERPNext Record-Level Failure Recorder
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted backend partial-failure evidence on Leads, Sales Orders, Payment Requests, Sales Invoices, Email Queue rows, documents, and automation reports
currently_true: true
verification_level: 2
last_verified: 2026-05-08
evidence_quality: direct
successful_uses: 2
failed_uses: 0
regressions: 0
depends_on:
  - fail-loud-operating-law
used_by:
  - erpnext-business-automation-index
tags:
  - Locally Twisted
  - ERPNext
  - fail-loud
  - automation
  - record-health
---

# ERPNext Record-Level Failure Recorder

Use this when a backend operation can partially fail after the primary business
record exists.

## Current LT Implementation

Implemented source:

- `apps/locally_twisted/locally_twisted/failure_recorder.py`
- `apps/locally_twisted/locally_twisted/verify/record_level_failure_contract.py`
- `apps/locally_twisted/locally_twisted/verify/inquiry_upload_failure_contract.py`
- `scripts/verify/record_level_failure_contract.py`
- `scripts/verify/inquiry_upload_failure_contract.py`

First wiring is active in:

- `lead_cascade.py`: Contact linking, acknowledgment email, and initial Task cascade failures.
- `www/book.py`: invalid, oversized, excess, or failed inspiration uploads.
- `www/checkout.py`: checkout notes transfer failures.
- `www/payment_success.py`: paid-order Lead conversion and receipt missing-recipient failures.
- `verify/business_automation_index.py`: record-level failure rows become checkup failures with exact record IDs.

## Purpose

Create one contract for partial failures instead of scattered judgment calls.
If customer intent, payment context, paperwork readiness, or operator belief can
be harmed, the affected business record or central checkup must show the
failure.

## Required Recorder Shape

A reusable recorder should capture:

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

## Durable Evidence Targets

Use more than one layer when the failure is business-critical:

- Frappe Error Log for developer/operator visibility;
- record comment/timeline entry or explicit blocker marker on Lead, Sales Order,
  Payment Request, Sales Invoice, or document source where safe;
- business automation index or scheduled checkup row with exact record IDs.

## First LT Wiring Targets

Source workstream: `workstreams/fail-loud-record-level-hardening.md`.

1. `lead_cascade.py` partial failures: Contact creation, acknowledgment email,
   Task creation, stage cascade.
2. `checkout.py` partial failures: checkout note transfer.
3. Inquiry upload failures: rejected/failed/oversized/excess inspiration photos.
4. Paid-order reconciliation: Lead conversion, missing receipt email, and thank-you page backend
   reconciliation state.
5. Outbound document readiness: recipient, invoice number, bill-to, balance,
   due date, terms, payment path, branding, bookkeeping fields.

## Done When

- Fake-data tests prove each wired failure becomes visible record/report
evidence.
- The business automation index can report exact affected records.
- Error Log-only evidence is not the only signal for customer-intent, payment,
or paperwork failures.
- No live customer email/reminder/accounting/payment mutation is required to run
verification.

## Anti-Patterns

- Catching and logging only to Error Log when the operator needs record context.
- Letting customer payment continue but hiding missing Sales Order notes or Lead
conversion from the Sales Order.
- Returning a paid thank-you state while receipt/invoice reconciliation is still
broken and unreported.
- Treating fake-data verifier success as live cutover readiness.
