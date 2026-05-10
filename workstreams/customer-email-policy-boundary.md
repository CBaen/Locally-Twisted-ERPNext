# Customer Email Policy Boundary

Last updated: 2026-05-10 by Codex after moving public form confirmations behind upload handling and adding submitted-detail/file-count confirmation copy.

## Outcome

Keep customer/operator email behavior aligned with receipts, policy lanes, and bookkeeping expectations without sending live email or mutating accounting records during verification.

## Current State

- `locally_twisted.verify.customer_email_policy_contract.run` statically checks source code for inquiry acknowledgment, paid receipt, operator notification, first-order welcome, and paid-order cascade coverage.
- `scripts/verify/customer_email_policy_contract.py` runs the in-app contract through Docker/Frappe and exits nonzero on missing policy markers, attachment/PDF kwargs, wrong reference DocTypes, or non-queued sendmail calls.
- Public customer-facing inboxes are role-based: `hi@locallytwisted.com` for general inquiry/web copy, `legal@locallytwisted.com` for legal/policy/accessibility copy and legal paperwork, and `billing@locallytwisted.com` for invoices, billing, refunds, payment reconciliation, accounts payable, and payroll.
- Public inquiry acknowledgments use `customer_email_theme.py`: LT logo, mirrored red balloon-dog footer mark, no ERPNext standard footer, and dynamic subject `U+1F388 Locally Twisted U+1F388 Got your Message {first_name} - 1 day Follow-Up!`.
- The public form endpoint defers the customer confirmation until after inspiration-photo handling, so the confirmation can accurately say how many reference files were received. Direct Website Lead inserts still use the same renderer without a file-count line.
- Customer form confirmations use the email title `Here is what we received` instead of repeating the subject line. The body echoes only non-empty fields the customer submitted, includes free-text notes, and only includes `We received X files for reference.` when files were attached.
- Customer form confirmations tell customers to reply if anything looks wrong. Current reply-to stays `hi@locallytwisted.com`; external customer replies should route through Cloudflare, but same-Gmail routed-alias QA sends are blocked/unsafe while ERPNext sends from `locallytwisted@gmail.com`.
- Inquiry confirmation policy copy is compact links, not the full long policy block, so the email is better suited for one-page printing.
- The playful public inquiry subject is limited to public forms. Do not reuse it on legal, billing, receipt, invoice, payroll, vendor, or other finance/legal emails.
- `configure_email_branding.py` disables Frappe's standard email footer through System Settings/defaults so customer mail does not say `Sent via ERPNext`.
- `locally_twisted.communication_copy_policy` owns standing internal copy routing: current internal copy delivery goes to `locallytwisted@gmail.com`.
- `hi@locallytwisted.com` and `cameron@locallytwisted.com` are Cloudflare-routed aliases back into the same Gmail SMTP account; do not use routed aliases as internal copy or QA-send targets while the sender is `locallytwisted@gmail.com`.
- `locally_twisted.email_delivery_guard` is wired to `Email Queue.before_insert` and blocks routed-alias loop sends even when a live probe bypasses `communication_copy_policy`.
- Cameron is not a standing future copy recipient. Use a non-LT mailbox for explicit one-time QA/review sends unless the SMTP sender changes.
- `scripts/verify/customer_documents_contract.py` and `scripts/verify/payment_cascade_contract.py` now prove the required copy recipients exist in ERPNext `Email Queue Recipient` rows during rollback-safe fake-data runs.
- `scripts/verify/book_form_repeat_email_photos.py --base-url http://localhost:8081` proves the real form path can queue one customer confirmation after uploads and include the correct file count.
- One-page print proof for the current customer-form confirmation was generated from a real queued five-photo test Email Queue row at ignored path `output/email-print-fit/customer-form-confirmation.pdf`; large-document intake reported 1 PDF page. This proves the customer-form confirmation sample, not every outbound email family.
- Business automation index now treats this contract as part of Lead acknowledgment and paid-order reconciliation.
- Synthetic business pipeline now includes `customer_email_policy_boundaries`.

## Boundaries

- No customer email is sent.
- No Email Queue row is created by this verifier.
- No Sales Invoice, Payment Request, Payment Entry, or Communication is mutated.
- No PDF or print attachment kwargs are allowed in the checked sendmail calls.
- This is source-policy verification, not final copy approval.
- Internal business copies are queued as BCC where possible so outside recipients do not see the copy-routing address.
- Verifier runs must set Frappe test email flags before queue assertions; rollback-safe database tests are not delivery-safe if a background mail worker can send routed aliases first.

## Owner Files

- `apps/locally_twisted/locally_twisted/verify/customer_email_policy_contract.py`
- `scripts/verify/customer_email_policy_contract.py`
- `apps/locally_twisted/locally_twisted/customer_email_theme.py`
- `apps/locally_twisted/locally_twisted/public/icons/lt-balloon-dog-red-email-mirrored.png`
- `apps/locally_twisted/locally_twisted/patches/configure_email_branding.py`
- `apps/locally_twisted/locally_twisted/verify/customer_documents_contract.py`
- `apps/locally_twisted/locally_twisted/lead_cascade.py`
- `apps/locally_twisted/locally_twisted/www/payment_success.py`
- `apps/locally_twisted/locally_twisted/communication_copy_policy.py`
- `apps/locally_twisted/locally_twisted/verify/payment_cascade_contract.py`
- `apps/locally_twisted/locally_twisted/verify/business_automation_index.py`
- `apps/locally_twisted/locally_twisted/verify/synthetic_business_pipeline.py`
- `scripts/verify/synthetic_business_pipeline.py`

## Verification

```powershell
python scripts/verify/customer_email_policy_contract.py
python scripts/verify/customer_documents_contract.py
python scripts/verify/book_form_repeat_email_photos.py --base-url http://localhost:8081
python scripts/verify/payment_cascade_contract.py
python scripts/verify/synthetic_business_pipeline.py --report output/synthetic-business-pipeline.json
python scripts/verify/business_automation_index.py --report output/business-automation-index.json
```

## Next Safe Slice

Next email work should be either provider/sender architecture review or a formal print-fit verifier that covers every outbound email family. Do not treat the customer-form one-page proof as global proof for receipts, operator notices, welcome emails, reminders, or finance/legal packets. If LT moves away from Gmail-as-sender or changes Cloudflare routing, revalidate whether `hi@locallytwisted.com` can become an internal delivery mailbox. Keep delivery no-live until recipients, opt-out/response handling, and approval gates are explicit.
