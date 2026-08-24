---
name: Public form photo storage owner attachment gap
type: failure
failure_kind: regression_pattern
schema_version: 0.1
date_discovered: 2026-05-15
last_updated: 2026-05-16
status: live_guarded
scope: project
owner_context: Locally Twisted ERPNext public inquiry forms
related_capabilities:
  - ../recipes/customer-email-delivery-branding-contract.md
  - ../recipes/erpnext-intake-form-parity.md
  - ../recipes/shared-inquiry-form-experience.md
related_failures:
  - public-form-stale-email-queue-idempotency.md
  - public-form-repeat-email-lead-conflict.md
  - frappe-cloud-release-site-migration-drift.md
tags:
  - locally-twisted
  - public-form
  - file-upload
  - crm
  - email-queue
  - fail-loud
---

# Failure Recipe: Public Form Photo Storage Owner Attachment Gap

## Symptom

A customer submits an inspiration photo through the public form. The business
owner sees an inquiry and a file count, but the photo is not visible in the
CRM photo table and is not attached to the owner confirmation email.

## Trigger Conditions

- The public form stores uploads only as generic private `File` attachments on
  the Lead.
- The Lead's custom photo child table is not populated.
- The owner/business notification is queued without `attachments=...`.
- Verifiers check only upload counts, email body text, or queue existence.

## Known Instances

| Date | Project | Surface | Bad outcome | Evidence | Guard state | Status |
|---|---|---|---|---|---|---|
| 2026-05-15 | Locally Twisted | Production `/contact` inquiry | `CRM-LEAD-2026-00007` had private File `44b4de500d` (`/private/files/image.jpg`) but `custom_inspiration_photos_count=0`; owner Email Queue rows had `attachments: []` | Production ERPNext Lead/File/Email Queue inspection; recovered image SHA256 `9ce7164e2d5a72ea74b714b57363c8972436f6337a5751fd2363d558a54bf4f5` | source fix, verifier guard, and 2026-05-16 live smoke proof added | live_guarded |

## Root Pattern

In ERPNext/Frappe, a `File` attached to a document, a custom child-table Attach
Image field, and an outgoing Email Queue attachment ref are separate contracts.
A form can satisfy one while silently failing the others unless the verifier
checks each surface explicitly.

## Detection Signals

- `File` rows exist for the Lead, but `Lead.custom_inspiration_photos` is empty.
- `Email Queue.message` mentions uploaded files, but `Email Queue.attachments`
  is `[]`.
- Owner reports missing photos while the backend count says files attached.
- A verifier passes without reading `Email Queue.attachments` JSON.
- A production incident investigation drifts into Gmail/personal inboxes
  instead of ERPNext Lead/File/Email Queue records.

## Required Guard

The public inquiry photo verifier must prove:

1. private `File` rows attached to the current Lead;
2. matching `custom_inspiration_photos` rows on the same Lead;
3. customer Email Queue has no photo attachment refs;
4. owner Email Queue has attachment refs matching the uploaded Lead Files;
5. verifier-owned records are cleaned after the run.

## Recovery Recipe

1. Inspect the production Lead, attached `File` rows, photo child table, and
   related Email Queue rows.
2. Do not use Gmail inbox search as the source of truth for form-upload
   storage.
3. Patch form handling so successful `File` inserts append
   `custom_inspiration_photos` rows.
4. Patch owner notification to resolve the Lead's private uploaded Files and
   pass queued `fid` attachment refs.
5. Keep customer confirmations attachment-free.
6. Extend the verifier to inspect `Email Queue.attachments`, not only message
   body text.
7. Prove locally, push the Frappe app mirror, deploy through Frappe Cloud, run
   site update/migrate, then run the live repeat-email/five-photo verifier.
8. For a real business-email smoke, record the Lead, File count, CRM photo row
   count, owner Email Queue attachment refs, and customer attachment absence.

## What Not To Do

- Do not forward unrelated local files or personal-email attachments.
- Do not treat `talking.png` or any local asset as a customer-submitted form
  upload without tracing it to ERPNext File rows.
- Do not claim the owner received photos because the email body says a count.
- Do not attach photos to the customer confirmation unless GL explicitly
  reopens that policy.
- Do not claim live production fixed from local proof or GitHub push alone.
- Do not claim future releases are narrow from the final source commit alone;
  compare old live app hash to target app mirror commit.

## Cross-links

- `../../workstreams/inquiry-photo-storage-owner-attachments-2026-05-15.md`
- `../../workstreams/inquiry-form-live-release-2026-05-16.md`
- `../../workstreams/form-email-confirmation-regression-2026-05-12.md`
- `../../workstreams/customer-email-policy-boundary.md`
- `../../workstreams/inquiry-photo-storage-owner-attachments-2026-05-15.md`
- `../recipes/customer-email-delivery-branding-contract.md`
- `../recipes/erpnext-intake-form-parity.md`
- `../recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`
- `frappe-cloud-app-mirror-release-scope-drift.md`

## Evidence Quality

Production root cause was verified against ERPNext Lead, File, and Email Queue
records. Local source fix was verified by compile checks, static email policy
contract, upload-failure contract, and real local repeat-email/five-photo form
submissions. Live production was verified on 2026-05-16 by site update
`b48j584nua`, update job `b48oge6unq`, and real smoke Lead
`CRM-LEAD-2026-00013` with five private Files, five CRM photo rows, owner Email
Queue `683s86r04b` carrying five attachment refs, and customer Email Queue
`683suhfaa9` carrying zero photo attachments.
