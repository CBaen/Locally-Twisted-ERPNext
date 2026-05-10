---
name: External document audience contract
level: recipe
last_verified: 2026-05-09
---

## What it does

Builds Locally Twisted external documents so each one is 100 percent professional for the person who actually receives it.

The document should answer the recipient's practical questions before they need to contact Locally Twisted. It should still reinforce the brand, but the audience's workflow wins over decoration.

## When to reach for it

Use this for invoices, receipts, quotes, proposals, event packets, contracts, W-9/vendor setup packets, purchase-order support, statements, payment reminders, corporate reorder prompts, and any PDF/print/email artifact sent outside the company.

## Audience rule

Start with the recipient, not the brand flourish.

- Accounts payable wants invoice number, dates, due date, PO/reference, vendor/contact, bill-to, expense category, itemized lines, taxes, totals, balance, payment/remittance instructions, W-9/vendor setup path, and enough terms to log the expense without asking questions.
- Accounts receivable wants payment status, payment record, receipt number if available, amount paid, amount remaining, related invoice/order, and clear contact if reconciliation fails.
- Event buyers want scope, location, install/teardown timing, weather/venue assumptions, design assets/photos, acceptance terms, and who owns next action.
- Procurement wants vendor identity, tax/W-9 support, insurance/contract path when available, PO/reference handling, repeat-event support, and contact routing.
- Executive/corporate sponsors want proof, confidence, and event outcomes; put the larger civic/patriotic brand story in proposals, portfolio, and corporate pages, not default accounting documents.

## Answer-first rule

For every outbound document, the first scannable block should answer what the recipient is trying to do. Use a visible label such as `Key fields to review`, `Payment summary`, `Approval summary`, or `Event details`.

Do not put an `Automation Contract`, integration metadata, generator notes, or internal review mechanics in that first customer-facing slot. Internal automation belongs in source templates, review queues, and verifier evidence. The audience-facing document should make the next useful answer obvious first.

## Fail-loud rule

Mantra: if it can fail, it must fail loudly. An outbound document must not look
send-ready when the recipient, amount, status, approval path, payment path,
policy lane, or source record is missing or contradictory.

- Invoices and receipts must not imply paid, unpaid, approved terms, or
  corporate billing status unless the source record proves it.
- Reminder, statement, proposal, and contract packets must stay draft/review
  gated until recipient, cadence, copy, payment link, and approval state are
  explicit.
- Every client/customer/company paperwork or documentation email must copy the
  business at `hi@locallytwisted.com`. Do not make Cameron a standing future
  copy recipient. Use `cameron@locallytwisted.com` only for explicit one-time
  QA/review sends. Prefer BCC for internal copies on outside-recipient email.
- Missing data should become a blocker in the review packet or verifier output,
  not a blank field in a customer-facing PDF.

## Layout rules

1. Make bookkeeping easy first.

   Put the critical bookkeeping facts high on page one. Invoice numbers and reference IDs must stay on one line.

2. Use brand restraint by document type.

   Default invoices and receipts should be mostly black, white, and neutral gray with the company text logo, clean type, horizontal rules, and excellent spacing. Rich civic/patriotic color, brass/gold accents, and dog-logo treatment belong in proposals, event packets, portfolio proof, reorder follow-ups, and corporate sales pages, not ordinary Sales Invoices.

3. Prefer horizontal lines over boxes.

   Containers are allowed only when they make a document easier to scan. Avoid large outlined cards, nested boxes, and oversized title panels in accounting documents. Use thin rules, aligned tables, and whitespace to group information.

4. Fit the page before calling it done.

   External documents must render cleanly as HTML/print/PDF. Avoid pushing a contact note, terms block, or total line onto a second page when the document should fit one page.

5. Avoid unnecessary contact.

   Every external document should include the likely next-step path: payment coordination, vendor setup/W-9 packet when it is the actual document purpose, repeat order, continued event support, contract review, or quote acceptance.

6. Keep legal and accounting claims scoped.

   Do not invent policy terms, insurance claims, tax claims, or contract promises. Use approved policy lanes and mark legal/accounting review needs when they exist.

## LT invoice standard

The default Sales Invoice is an accounts-payable document, not marketing collateral.

Required traits:

- Locally Twisted logo and contact.
- One-line invoice number.
- Invoice date, due date, status, and balance due.
- PO/reference and customer/bill-to.
- Expense category for bookkeeping.
- Itemized lines and clear totals.
- Invoice/receipt terms appropriate to paid, unpaid, or approved corporate terms.
- Gray vertical callout treatment for secondary AP summary, policy, and note blocks: light neutral gray background, thin gray left rule, compact spacing.
- Solid black bottom support bar with white text:
  `Customer Service, Continued Event Support, and Repeat Orders:`
  `Reply to this invoice and we will route the request to the right person.`
- Mostly black, white, and neutral gray.
- No gold bar, gold rule, brass/gold accent, navy/berry/promo color treatment, dog logo, or marketing-style decoration on ordinary Sales Invoices.
- Fewer containers; simple horizontal rules and gray callouts instead of heavy boxes.
- One-page PDF for ordinary invoices.

Gold, dog-logo, and more expressive brand treatments can be used later in proposals, event packets, reorder follow-ups, and other sales/support documents where the audience expects brand context. The default Sales Invoice stays AP-first.

## LT verification commands

For Sales Invoice output:

```powershell
python scripts/setup/sync_invoice_branding.py
python scripts/verify/invoice_branding_contract.py
```

For the standard outbound document source folder:

```powershell
python scripts/verify/outbound_documents_contract.py
python scripts/verify/unpaid_invoice_draft_packet.py --report output/unpaid-invoice-draft-packet.json
python scripts/verify/unpaid_invoice_draft_packet_contract.py
python scripts/verify/paperwork_review_digest.py --report output/paperwork-review-digest.json
python scripts/verify/customer_reminder_dry_run.py --report output/customer-reminder-dry-run.json
python scripts/verify/customer_reminder_dry_run_contract.py
python scripts/verify/customer_reminder_review_report.py --report output/customer-reminder-review-report.json
python scripts/verify/customer_reminder_review_report_contract.py
python scripts/verify/outbound_document_send_readiness_contract.py
```

Source lives at `apps/locally_twisted/locally_twisted/outbound_documents/`. Extend that registry before adding a new external invoice, receipt, quote, proposal, packet, statement, reminder, work order, contract summary, or follow-up document elsewhere.

The outbound registry verifier requires each source template to include `## Answer First`. The preview renderer should place `Key fields to review` in the high-visibility slot, not automation metadata. Draft renderers, digest surfaces, dry-run reminder queues, and reminder review reports that prepare reminder or statement packets must remain internal-review output until an explicit send approval path exists.

For customer-policy text touched by documents:

```powershell
python scripts/verify/customer_documents_contract.py
python scripts/verify/payment_cascade_contract.py
```

Render a visual proof before making a visual claim. Use `output/playwright/` for screenshots/PDF renders and check page count when PDF fit matters.

## Failure modes

- A document looks branded but does not help accounting enter, approve, or reconcile it.
- A print format uses web-style cards and large containers, creating odd spacing and page overflow.
- A colored proposal treatment leaks into invoices/receipts and makes accounting documents feel promotional.
- Gold, dog-logo, or full-color brand decoration leaks into the default Sales Invoice.
- Corporate Net 30 language appears on ordinary invoices or receipts without the record proving those terms apply.
- The browser preview looks acceptable but the PDF prints on two pages or adds unwanted browser headers/footers.
- A repeat-order or contract prompt reads like pressure instead of helpful routing.
- A statement or payment-reminder draft looks ready enough to send but lacks the reviewed recipient, cadence, balance, and copy approval path.
- A customer reminder queue item hides payment-path gaps or skips the internal approval blockers that make no-live setup safe.
- A reminder report row looks operational but omits no-live delivery flags or blockers.
