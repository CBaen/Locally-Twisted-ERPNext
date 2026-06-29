---
name: Public form raw payload log PII drift
type: failure
failure_kind: regression_pattern
schema_version: 0.1
date_discovered: 2026-06-29
last_updated: 2026-06-29
status: guarded
scope: project
owner_context: Locally Twisted ERPNext public inquiry forms
related_capabilities:
  - ../recipes/shared-inquiry-form-experience.md
  - ../recipes/customer-email-delivery-branding-contract.md
  - ../recipes/fail-loud-operating-law.md
  - ../recipes/frappe-public-storefront-security.md
related_failures:
  - public-form-stale-email-queue-idempotency.md
  - public-form-repeat-email-lead-conflict.md
  - public-form-photo-storage-owner-attachment-gap.md
tags:
  - locally-twisted
  - public-form
  - pii
  - error-log
  - fail-loud
  - meta-ads
---

# Failure Recipe: Public Form Raw Payload Log PII Drift

## Symptom

A public form failure path logs the submitted form payload into Frappe Error Log
when Lead creation fails. The values can include customer name, email, phone,
event location, event date, free-text notes, product quote details, or other
customer-provided material.

## Trigger Conditions

- A form handler tries to preserve developer evidence by serializing
  `frappe.form_dict`.
- "Fail loud" is interpreted as "log everything" instead of "log actionable
  context without unnecessary sensitive values."
- A paid ad or launch review focuses on public route availability and misses
  admin-side privacy/logging blast radius.

## Known Instances

| Date | Project | Surface | Action being taken | Bad outcome | Evidence | Guard state | Status |
|---|---|---|---|---|---|---|---|
| 2026-06-29 | Locally Twisted | `/contact` / `locally_twisted.www.book.submit_book_inquiry` | Meta ad readiness triad before first missionary product ad spend | Lead-creation failure log serialized most submitted form values into Error Log | Lens A triad report plus source check in `locally_twisted/www/book.py`; repaired in source commit `6165015` and app-mirror local candidate `526e711` | `scripts/verify/inquiry_logging_privacy_contract.py` added in source; app mirror code changed locally pending release approval | guarded in source, live release pending |

## Root Pattern

Public-form failure evidence must be strong enough for operators to diagnose
the problem, but Error Log is not a place to store raw customer submissions.
The correct boundary is shape/context evidence, not form values.

## Why It Seemed Reasonable At The Time

The form had a real history of silent failure, so logging the submitted payload
looked like a practical way to preserve diagnostic context. That was directionally
right, but too broad for ad traffic because customer submissions become more
frequent and more sensitive once paid acquisition starts.

## Detection Signals

- `frappe.form_dict` serialized into `frappe.log_error`.
- Error-log messages containing `payload:`, `form_url:`, or `remote_ip:` in a
  public inquiry Lead-creation failure path.
- Form failure handling that logs contact fields directly rather than boolean
  presence, selected safe categories, request path, and upload count.
- Any pre-spend review that approves traffic without checking admin-side logs.

## Required Guard

Use a source guard that fails if public inquiry Lead-creation failure logging
returns to raw payload serialization:

```bash
python scripts/verify/inquiry_logging_privacy_contract.py
```

The safe context should keep:

- request path without query string;
- present field names, not field values;
- required-field boolean presence;
- selected service/package values from allowlisted public options;
- safe item code and upload count;
- no name, email, phone, location, free text, attribution payload, honeypot
  value, spam token, or remote IP value.

## Recovery Recipe

1. Remove raw `frappe.form_dict` serialization from the public form failure
   path.
2. Replace it with a helper such as `_safe_lead_creation_failure_context`.
3. Add or run `scripts/verify/inquiry_logging_privacy_contract.py`.
4. Run syntax and focused form/measurement contracts.
5. If live traffic is planned, push the full source fix, sync the Frappe app
   mirror, run Frappe Cloud update/migrate/cache through the release gate, then
   prove live `/contact` with an approved write smoke and cleanup.

## What Not To Do

- Do not remove loud failure logging completely.
- Do not log customer free text, contact values, raw attribution payloads, spam
  tokens, honeypot values, uploaded filenames, or remote IP values as the
  primary diagnostic record.
- Do not call the live issue fixed after a source commit only; the app mirror
  and Frappe Cloud site update are separate proof states.
- Do not run live form write smokes without explicit approval because they
  create temporary Lead and Email Queue records.

## Cross-Links

- Related workstream: `../../workstreams/meta-ad-foundation-readiness-2026-06-29.md`
- Related source verifier: `../../scripts/verify/inquiry_logging_privacy_contract.py`
- Related recipe: `../recipes/shared-inquiry-form-experience.md`
- Related recipe: `../recipes/frappe-public-storefront-security.md`
- Related failure: `public-form-stale-email-queue-idempotency.md`

## Evidence Quality

Source repair is verified by static contract, syntax check, local backend form
contracts, and local repeat-email/five-photo smoke. Live Frappe still requires
app-mirror push, Frappe Cloud site update, and an approved live write smoke
before first paid ad spend.
