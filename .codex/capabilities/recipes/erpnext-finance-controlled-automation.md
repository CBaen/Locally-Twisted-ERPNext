---
name: ERPNext finance controlled automation
level: recipe
last_verified: 2026-05-06
---

## What it does

Builds ERPNext finance, payroll, collections, and accounting migration surfaces without creating accountant-risky automation.

## When to reach for it

Use this when a client repo starts handling QuickBooks migration, invoicing, payment reconciliation, bank import, payroll, contractors, 1099 readiness, or accountant-facing workspaces.

## How to use it

1. Inventory the live finance surface first.

   Check whether core DocTypes, settings, accounts, fiscal year, tax templates, payment gateway accounts, payment terms, bank accounts, suppliers, invoices, payments, and payroll DocTypes exist before claiming readiness.

2. Map existing money creators before adding automation.

   Checkout, payment success handlers, webhooks, native Payment Requests, and import scripts may already create Customers, Sales Orders, Sales Invoices, Payment Entries, emails, or accounting rows. Do not add CRM-stage money automation until those paths are mapped.

3. Start with visibility and review queues.

   Dashboards, Number Cards, draft queues, reminder candidates, reports, and reconciliation checklists are safe first steps. Auto-submit, write-off, reminder sending, payroll, tax filing, direct deposit, and bank sync need explicit approval of exact rules.

4. Keep QuickBooks migration scoped.

   Import active operating data, open AR/AP, opening balances, vendors, customers, and accountant-approved reports. Keep the full QuickBooks export as archive unless the accountant requests deeper transaction import.

5. Treat banking as a controlled cutover.

   CSV import is the first test path. Plaid or live bank sync waits for bank support, credential/security approval, and successful test matching.

6. Verify payroll before promising payroll.

   `Employee` alone is not payroll readiness. Real ERPNext payroll needs HRMS/payroll DocTypes such as `Payroll Entry`, `Salary Slip`, and `Salary Structure`, plus accountant/provider review for filing and direct deposit.

7. Track contractors as vendors first.

   Contractors belong as Suppliers/vendors with payment history and tax identity support unless they have a proven backend operator workflow. Do not claim automated 1099 filing without a verified filing path.

8. Keep the automation map current.

   Cross-system finance work should have one index that says what exists, what is connected, what exists but is not connected, what is missing and required, and what is missing but useful. For LT, `business_automation_index.py` is that index and should fail nonzero when launch-required links break.

## LT verification commands

```powershell
python scripts/verify/finance_inventory.py
python scripts/verify/finance_inventory_contract.py
python scripts/setup/sync_finance_workspace.py
python scripts/verify/finance_workspace_parity.py
```

When changing checkout, payment, or CRM finance boundaries, also run:

```powershell
python scripts/verify/checkout_lead_conversion_contract.py
python scripts/verify/payment_backend_config_contract.py
python scripts/verify/payment_webhook_contract.py
python scripts/verify/payment_cascade_contract.py
python scripts/verify/cart_checkout_contract.py
python scripts/verify/payment_launch_readiness.py
python scripts/verify/business_automation_index.py --report output/business-automation-index.json
python scripts/verify/unpaid_invoice_review.py --report output/unpaid-invoice-review.json
python scripts/verify/unpaid_invoice_draft_packet.py --report output/unpaid-invoice-draft-packet.json
python scripts/verify/unpaid_invoice_draft_packet_contract.py
python scripts/verify/paperwork_review_digest.py --report output/paperwork-review-digest.json
python scripts/verify/stripe_amount_parity_contract.py
```

Run live inventory after mutating verifiers finish and rollback, not in parallel with them, if the count will be documented as stable state.

## Failure modes

- A dashboard card can make finance look ready while payment terms, bank accounts, suppliers, or payroll DocTypes are still missing.
- A CRM stage can duplicate the checkout/payment path if it creates Customers, Sales Orders, Payment Requests, invoices, or emails independently.
- Automated reminders can become customer-facing collection activity before copy, cadence, and audience are approved.
- Plaid setup can turn a technical spike into a credential/security decision if it is not gated.
- QuickBooks history can become messy operational data if imported deeper than accountant-approved cutover scope.
- `Employee` records can be mistaken for payroll readiness when HRMS/payroll DocTypes are not installed.
- Stripe hosted-checkout line items can silently omit ERPNext taxes or charges if amount parity is not checked before redirect.
- Draft reminder or statement helpers can become collections automation if they do not prove `send_allowed: false`, `mutation_allowed: false`, and unchanged guarded record counts.
- Draft packet renderers can accidentally become delivery automation if they create Email Queue, Communication, Payment Request, Payment Entry, Journal Entry, or invoice mutations while preparing review output.
- Review digests can look harmless while hiding setup blockers or recursively triggering indexed checks; keep them read-only, mutation-guarded, and explicit about partially connected finance surfaces.
