# Inquiry Photo Storage and Owner Attachments - 2026-05-15

## Scope

This handoff owns the production incident where a public inquiry photo existed
as a generic private `File` on a Lead but was not visible in the CRM photo table
and was not attached to the owner confirmation email.

It covers the shared `/contact` and BTFP inquiry path implemented by
`submit_book_inquiry`. It does not own Gmail inbox searches, manual email
forwarding, product quote emails, paid receipts, invoice emails, or finance
paperwork.

## Incident Facts

The missing production photo was recovered from ERPNext/Frappe, not from Gmail.

| Field | Value |
|---|---|
| Production Lead | `CRM-LEAD-2026-00007` |
| Lead title | `Michelle Roper - Balloon Decor` |
| File doc | `44b4de500d` |
| Filename | `image.jpg` |
| Private URL | `/private/files/image.jpg` |
| Size | `1,126,740` bytes |
| SHA256 | `9ce7164e2d5a72ea74b714b57363c8972436f6337a5751fd2363d558a54bf4f5` |

Production showed the exact broken shape:

- The Lead had the private `File` attached.
- `Lead.custom_inspiration_photos_count` was `0`.
- The owner/customer Email Queue rows had `attachments: []`.
- The email body mentioned the photo count, but no photo refs were queued.

The local recovered copy was deleted from `output/recovered-inquiry-photos/`
after source documentation captured the evidence. Do not keep recovered
customer images in repo-local output as an archive.

## Root Cause

`book.py` inserted private `File` docs attached to the Lead, then kept only an
integer count. It did not append those file URLs to the custom CRM child table
`Lead.custom_inspiration_photos`.

`lead_cascade.py` queued the owner/business notification without
`attachments=...`, so Frappe had no queued attachment refs to resolve when the
email was sent.

The previous verifier accepted a weaker contract: file count, customer/owner
queue existence, and message body checks. It did not prove CRM photo-table
storage or owner Email Queue attachment refs.

## Source Fix

Published full repo commit:

- `4422793 Fix inquiry photo storage and owner attachments`

Published Frappe Cloud app mirror commit:

- `6a06062 Fix inquiry photo storage and owner attachments`

Changed behavior:

- Successful uploads are kept as inserted `File` docs during form handling.
- The Lead is reloaded and each successful file appends a
  `custom_inspiration_photos` row with `photo = file_doc.file_url` and
  `caption = file_doc.file_name`.
- Owner/business inquiry notifications read the Lead photo table, resolve
  matching private `File` records attached to that Lead, and pass
  `attachments=[{"fid": file_doc.name}]` to `frappe.sendmail`.
- Customer confirmations stay attachment-free. They may mention the received
  file count, but they must not attach customer-submitted images back to the
  customer.
- The email policy contract now allows the owner-only photo attachment refs
  while continuing to block customer attachments and print/PDF attachment
  kwargs on the customer path.

## Verification Receipt

Local verification passed before this documentation update:

```bash
python -m py_compile apps/locally_twisted/locally_twisted/www/book.py apps/locally_twisted/locally_twisted/lead_cascade.py apps/locally_twisted/locally_twisted/verify/book_form_repeat_email_photos_email_contract.py apps/locally_twisted/locally_twisted/verify/customer_email_policy_contract.py scripts/verify/customer_email_policy_contract.py
python scripts/verify/customer_email_policy_contract.py
python scripts/verify/inquiry_upload_failure_contract.py
python scripts/dev/clear_website_cache.py --restart
python scripts/verify/book_form_repeat_email_photos.py --base-url http://localhost:8081
```

The strict local form verifier passed with two repeat same-email submissions,
five photos per submission, customer queue attachment refs absent, owner queue
attachment refs present, CRM photo rows present, and verifier-owned records
cleaned.

Frappe Cloud preflight and Cloudflare route health were checked after the
source push:

```bash
python scripts/verify/frappe_cloud_preflight.py
python scripts/verify/cloudflare_launch_readiness.py --base-url https://locallytwisted.com
```

Both passed with zero hard blockers. That proves route/preflight health, not
that the live site is already running this hotfix.

## Live Status

Production is now verified on the owner-photo delivery path.

Live release and smoke receipt from 2026-05-16:

| Field | Value |
|---|---|
| Full repo source commit | `631f9a8 Run contact intake schema sync on install` |
| Frappe app mirror commit | `b4b3bf8 Run contact intake schema sync on install` |
| Frappe Cloud site update | `b48j584nua`, `Success` |
| Frappe Cloud update job | `b48oge6unq`, `Success` |
| Source bench | `bench-39776-000013-f94-virginia` |
| Destination bench | `bench-39776-000015-f94v` |
| Deploy type | `Migrate` |
| Live cache clear | `26es8svcaq`, `Success` |
| Live smoke Lead | `CRM-LEAD-2026-00013` |
| Live smoke contact name | `smoke test from cameron` |
| Owner Email Queue | `683s86r04b`, `Sent`, to `locallytwisted@gmail.com`, subject `New website inquiry from smoke test from cameron`, attachment refs `5` |
| Customer Email Queue | `683suhfaa9`, `Sent`, attachment refs `0` |

The live smoke stored five private Lead `File` rows and five
`custom_inspiration_photos` child rows:

- `img-9111.jpeg`
- `baby-shower-garland.png`
- `birthday-deliveries--extra-02.webp`
- `basketball-arch.png`
- `contact-hero.png`

This proves the specific business-owner problem GL reported: customer-uploaded
photos are stored in the CRM photo table and are queued as owner-only email
attachments. Customer confirmations remain attachment-free.

The 2026-05-16 smoke was an intentional real business-email smoke, not the
rollback cleanup verifier. The repeat same-email/five-photo cleanup verifier
remains the right guard after future source changes because it proves the same
contract without leaving live test records behind.

## Owner Files

- `apps/locally_twisted/locally_twisted/www/book.py`
- `apps/locally_twisted/locally_twisted/lead_cascade.py`
- `apps/locally_twisted/locally_twisted/verify/book_form_repeat_email_photos_email_contract.py`
- `apps/locally_twisted/locally_twisted/verify/customer_email_policy_contract.py`
- `scripts/verify/customer_email_policy_contract.py`
- `scripts/verify/book_form_repeat_email_photos.py`
- `apps/locally_twisted/locally_twisted/verify/book_form_repeat_email_photos_cleanup.py`

## Guardrails

- Do not use Gmail or personal inbox search to diagnose Locally Twisted public
  form photo delivery. Source of truth is ERPNext/Frappe: Lead, File,
  `custom_inspiration_photos`, and Email Queue.
- Do not treat a private `File` attached to a Lead as CRM photo-table storage.
- Do not treat a photo count in the email body as proof the owner received the
  photos.
- Do not attach customer-submitted inspiration photos to the customer
  confirmation email.
- Do not verify Frappe queued attachment refs by reading only MIME attachment
  parts in `Email Queue.message`. For queued private files, inspect
  `Email Queue.attachments` JSON for `fid` refs.
- Do not claim a future live production release fixed from GitHub push, Frappe
  Cloud app hash, or route health alone. Site update/migrate plus live form
  verifier or intentional live smoke evidence must pass again.

## Cross-links

- `workstreams/form-email-confirmation-regression-2026-05-12.md`
- `workstreams/customer-email-policy-boundary.md`
- `workstreams/frappe-cloud-cloudflare-stripe-launch-2026-05-11.md`
- `capabilities/recipes/erpnext-inquiry-photo-delivery-contract.md`
- `capabilities/recipes/customer-email-delivery-branding-contract.md`
- `capabilities/recipes/erpnext-intake-form-parity.md`
- `capabilities/recipes/shared-inquiry-form-experience.md`
- `capabilities/failures/public-form-photo-storage-owner-attachment-gap.md`
