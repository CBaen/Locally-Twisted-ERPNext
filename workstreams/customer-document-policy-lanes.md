# Customer Document Policy Lanes

Last updated: 2026-05-06 by Codex.

## Outcome

Keep all customer-facing policy language for receipts, inquiry emails, checkout notices, and future invoice-style documents aligned with the same public Terms and Refund lanes.

Canonical public anchors:

- `/terms-of-service#event-balloon-decor`
- `/terms-of-service#ready-to-order-pickup-delivery`
- `/terms-of-service#face-painting-balloon-twisting`
- `/terms-of-service#corporate-invoicing`
- matching anchors on `/refund-policy`

## Current State

- `locally_twisted.policy_documents` owns code-level policy lane summaries and links.
- Inquiry auto-ack emails choose lanes from Lead services.
- Paid-order receipt emails always include the ready-to-order pickup/delivery block plus Privacy.
- Checkout links directly to ready-to-order Terms, Refund Policy, and Privacy.
- No ERPNext Terms and Conditions or Email Template records are added for this feature. Keep LT whitelabel/code-owned unless a verified customer-facing invoice path truly requires ERPNext setup records.

## Verification

Run after changing customer document, receipt, invoice, or policy-page copy:

```powershell
python scripts/verify/customer_documents_contract.py
python scripts/verify/payment_cascade_contract.py
```

For public page copy/layout changes, also run:

```powershell
python scripts/dev/clear_website_cache.py
npm run test:layout-fit
```

## Remaining

- Legal/accounting approval is still separate from business-proxy approval.
- Larger event/corporate work may still need an attorney-drafted event contract beyond invoice payment-as-acceptance language.
- If a future invoice/contract feature needs document-embedded legal language, prefer code-owned custom print/email templates first and only add ERPNext setup records when the real customer path requires them.
- Future service/deposit payment automation must continue to keep service, service deposits, and delivery non-taxable unless accounting/legal review changes the rule.
