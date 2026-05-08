---
id: fail-loud-operating-law
name: Fail Loud Operating Law
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted forms, automations, customer documents, route/layout contracts, containers, verification, and agent communication
currently_true: unknown
verification_level: 1
last_verified: 2026-05-08
evidence_quality: direct
successful_uses: 1
failed_uses: 0
regressions: 0
depends_on:
  - customer-facing-failure-voice
used_by:
  - erpnext-business-automation-index
  - erpnext-intake-form-parity
  - external-document-audience-contract
  - frappe-public-container-contract
  - responsive-container-audit
  - erpnext-record-level-failure-recorder
tags:
  - Locally Twisted
  - ERPNext
  - Frappe
  - automation
  - forms
  - containers
  - verification
---

# Fail Loud Operating Law

Mantra: **If it can fail, it must fail loudly.**

Use this before changing any surface where a customer, operator, accounting
person, scheduler, verifier, or future agent could mistake partial success for
real success.

## Fake Data Clarification

GL clarified on 2026-05-07 that all current Locally Twisted data is fake/test
data for automation testing until GL explicitly says otherwise.

That is intentional and useful. It means fake-data verifiers can be aggressive,
rollback-safe, and repeated. It does **not** permit fake success.

The standard is: every field and automation that can/should happen must either
happen or fail loudly with record-level evidence.

High-risk failures are anything that can hide customer intent, lose payment
context, send wrong paperwork, or make the business think something happened
when it did not.

## What Failing Loudly Means

A failure is loud only when it blocks false success and leaves actionable
evidence.

Minimum standard:

- User/operator surface: no false success message, receipt, invoice, saved state,
  submitted-form state, or clean-layout claim when the downstream path failed.
- Developer surface: exception, nonzero verifier, failed test, explicit blocker
  field, or reproducible report row.
- Monitor surface: Frappe Error Log, scheduled report, audit JSON, mutation
  guard, or equivalent durable signal for operational failures.
- Source contract: the missing or broken connection is named in code, schema,
  payload, route contract, document registry, or verifier output.

## Customer-Facing Failure Voice

Global source: `C:\Users\baenb\.codex\capabilities\recipes\customer-facing-failure-voice.md`.

Public/customer-facing failures must be warm, plain, and gently playful without
turning into fake success. Use the "calm kindergarten teacher" test:

- name the snag without blame or technical detail;
- reassure only what is true;
- give one safe next step;
- include a real retry/contact path when the customer cannot fix it alone;
- keep stack traces, DocTypes, webhook/API labels, and exact internal failures
  out of public copy.

Backend/operator evidence must still be exact: record ID, route, failing step,
exception/report row, and next repair action.

## Required Behavior By Surface

Forms and intake:

- Public success requires backend proof: Lead/contact/message/acknowledgment
  path must exist or the UI must show a failure.
- Form labels, field names, submit handlers, Lead fields, Desk conditionals, and
  acknowledgment copy must stay mapped. Drift belongs in a failed verifier, not
  in a customer relationship.

Automations:

- Required cascades must raise, fail nonzero, or write Error Log/report evidence
  when files, hooks, setup records, whitelisted methods, or downstream links are
  missing.
- Review-only and no-live surfaces must carry blockers and mutation guards.
  They are not safe just because they currently return data.

Documents and customer communication:

- Drafts must be labeled draft-only until the send/approval path is explicit.
- Sent/paid/approved language must not appear unless the source record proves
  it.
- Missing payment paths, missing recipient data, stale policy copy, or malformed
  approval flags must block delivery.
- Customer-visible document or email error states must be polite and useful:
  explain the missing piece and route the customer to a reply, call, or human
  review path instead of exposing internal automation language.

Containers and public layout:

- Route-level containers are not taste preferences. Missing top-level sections,
  wrong full-bleed modes, uncontained inners, native crawl scrollbars, and
  document overflow must fail tests.
- Do not hide layout failure with `overflow-x: hidden` on the body unless the
  actual section contract is still correct and independently verified.

Agent communication:

- Do not say a route, form, automation, payment, document, or layout works
  without current verification evidence.
- If a check was not run, say that plainly.

Verifier scripts:

- `--help` is part of the contract. It must print usage quickly and must not
  launch browser checks, Docker/Frappe calls, fake-data writes, or customer-path
  probes.
- Guard this with `python scripts/verify/verifier_cli_contract.py`.

## First Record-Level Hardening Slice

The next high-value implementation slice is:

1. Create a reusable backend failure recorder.
2. Wire it into Lead cascade partial failures.
3. Wire it into checkout note and paid-order Lead conversion partial failures.
4. Wire it into paid-order receipt delivery failures.
5. Extend the business automation index with record-level health rows.

Source workstream: `workstreams/fail-loud-record-level-hardening.md`.

## LT Gates To Reach For

```powershell
python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --shape-only --skip-newsletter
python scripts/verify/lead_backend_intake_parity.py
python scripts/verify/customer_email_policy_contract.py
python scripts/verify/business_automation_index.py --report output/business-automation-index.json
python scripts/verify/synthetic_business_pipeline.py --report output/synthetic-business-pipeline.json
python scripts/setup/sync_maintenance_package.py
python scripts/verify/maintenance_heartbeat.py --heavy
python scripts/verify/maintenance_admin_boundary.py
npm run test:container-contract
npm run test:public-verify
```

Use the narrower verifier when one exists. Use `test:public-verify` for broad
customer-facing layout/navigation/checkout closeout.

## Anti-Patterns

- Success toast after a failed backend write.
- Customer-facing copy that says only "Something went wrong" or exposes
  exception/webhook/DocType/API language.
- Email helper catches and logs only to console.
- A verifier timeout is dismissed as incidental before checking whether the
  verifier CLI accidentally ran live work.
- Scheduler silently skips because a method path changed.
- Document generator omits a payment link but still renders a send-ready packet.
- Form field is renamed in HTML but not in the Lead mapping.
- Route adds a visible `.page_content` child without updating
  `CONTAINER_CONTRACT_ROUTES`.
- A crawl becomes a native horizontal scrollbar on one browser.
- Agent reports "fixed" from code inspection alone.
