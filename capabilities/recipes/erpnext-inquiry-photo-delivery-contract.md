---
name: ERPNext inquiry photo delivery contract
level: recipe
last_verified: 2026-05-16
currently_true: true
---

# ERPNext Inquiry Photo Delivery Contract

## What It Does

Keeps Locally Twisted public inquiry photo uploads aligned across four surfaces:

- private `File` records attached to the Lead;
- owner-visible CRM photo rows on `Lead.custom_inspiration_photos`;
- customer confirmation copy with an accurate count only;
- owner/business Email Queue attachment refs that Frappe can resolve at send
  time.

Use this with `shared-inquiry-form-experience`,
`erpnext-intake-form-parity`, and
`customer-email-delivery-branding-contract` whenever changing public inquiry
uploads, Lead photo storage, or owner notifications.

## Contract

- A successful photo upload creates a private `File` attached to the current
  Lead.
- The same successful upload appends one `custom_inspiration_photos` child row
  on the same Lead, with `photo` pointing at the uploaded file URL.
- The customer confirmation must not attach the customer-submitted images back
  to the customer. It may only mention the received count.
- The owner/business notification may attach the uploaded images, but only by
  resolving `File` docs attached to the same Lead and passing queued attachment
  refs such as `{"fid": file_doc.name}`.
- Owner attachment verification must inspect `Email Queue.attachments` JSON.
  Frappe does not need to embed private queued file bytes directly in
  `Email Queue.message` at queue time.
- Public success still requires current customer and owner Email Queue proof.
  Photo storage success is not a substitute for email proof.
- Live release proof requires GitHub source push, Frappe Cloud bench deploy,
  site update/migrate success, and live form verifier cleanup.

## Source Files

- `apps/locally_twisted/locally_twisted/www/book.py`
- `apps/locally_twisted/locally_twisted/lead_cascade.py`
- `apps/locally_twisted/locally_twisted/verify/book_form_repeat_email_photos_email_contract.py`
- `apps/locally_twisted/locally_twisted/verify/book_form_repeat_email_photos_cleanup.py`
- `apps/locally_twisted/locally_twisted/verify/customer_email_policy_contract.py`
- `scripts/verify/book_form_repeat_email_photos.py`
- `scripts/verify/customer_email_policy_contract.py`
- `workstreams/inquiry-photo-storage-owner-attachments-2026-05-15.md`

## Verification

Local source and behavior proof:

```powershell
python -m py_compile apps\locally_twisted\locally_twisted\www\book.py apps\locally_twisted\locally_twisted\lead_cascade.py apps\locally_twisted\locally_twisted\verify\book_form_repeat_email_photos_email_contract.py apps\locally_twisted\locally_twisted\verify\customer_email_policy_contract.py scripts\verify\customer_email_policy_contract.py
python scripts\verify\customer_email_policy_contract.py
python scripts\verify\inquiry_upload_failure_contract.py
python scripts\dev\clear_website_cache.py --restart
python scripts\verify\book_form_repeat_email_photos.py --base-url http://localhost:8081
```

Live release proof after Frappe Cloud deploy and site update:

```powershell
$env:LT_BACKEND_BASE_URL='https://locallytwisted.v.frappe.cloud'
$env:LT_BACKEND_CDP_URL='http://127.0.0.1:9222'
python scripts\verify\book_form_repeat_email_photos.py --base-url https://locallytwisted.com --admin-base-url https://locallytwisted.v.frappe.cloud --cdp-url http://127.0.0.1:9222
```

2026-05-16 live proof used an intentional real business-email smoke instead of
the cleanup verifier. Receipt:

- source `631f9a8`, app mirror `b4b3bf8`;
- Frappe Cloud site update `b48j584nua` and update job `b48oge6unq` succeeded;
- Lead `CRM-LEAD-2026-00013` stored five private Files and five CRM photo rows;
- owner Email Queue `683s86r04b` was `Sent` to `locallytwisted@gmail.com` with
  five attachment refs;
- customer Email Queue `683suhfaa9` was `Sent` with zero photo attachments.

## Failure Modes

- Private `File` rows exist, but the CRM photo table is empty.
- CRM photo rows exist, but the owner notification has no queued attachment
  refs.
- The email body says files were attached, but `Email Queue.attachments` is
  empty.
- The customer confirmation gets image attachments and leaks customer-uploaded
  images back outside the business workflow.
- A verifier checks only response counts or message body text and misses the
  backend storage/attachment contract.
- A GitHub app mirror push is treated as live proof before Frappe Cloud site
  update and live verifier proof.
- The final source commit is treated as the complete release scope instead of
  comparing the previous live app hash to the target app mirror commit.

## Related

- `../failures/public-form-photo-storage-owner-attachment-gap.md`
- `../failures/frappe-cloud-app-mirror-release-scope-drift.md`
- `customer-email-delivery-branding-contract.md`
- `erpnext-intake-form-parity.md`
- `shared-inquiry-form-experience.md`
- `frappe-cloud-cloudflare-stripe-launch-gate.md`
