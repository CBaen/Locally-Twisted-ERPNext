# Finance, Payroll, and QuickBooks Migration Workstream

Last updated: 2026-05-03 by Codex after finance inventory and Accountant Home workspace sync.

## Outcome

Turn the LT ERPNext backend into the business finance operating system without creating accounting risk.

Launch posture is controlled automation:

- ERPNext may create visibility, draft queues, reminder candidates, reports, and review surfaces.
- Customer reminders do not send until templates, timing, and customer groups are approved.
- Financial documents, write-offs, payroll runs, tax filings, direct deposit, W-2, and 1099 filings remain human/accountant-reviewed until proven.
- QuickBooks remains the historical archive unless the accountant asks for deeper legacy transaction import.

## Current Verified Local State

Verified on 2026-05-03 with `python scripts/verify/finance_inventory.py` against the local ERPNext stack.

- Installed apps: `frappe`, `erpnext`, `payments`, `webshop`, `locally_twisted`.
- Core finance DocTypes are present: Customer, Supplier, Sales Order, Sales Invoice, Payment Request, Payment Entry, Journal Entry, Account, Bank Account, Bank Transaction, Bank Reconciliation Tool, Plaid Settings, Process Statement Of Accounts, Payment Terms Template, Payment Term, Purchase Invoice, Company, Fiscal Year, Sales Taxes and Charges Template, Payment Gateway Account, Mode of Payment, Stripe Settings.
- Payroll is not ready: `Employee` DocType exists, but HRMS is not installed and `Payroll Entry`, `Salary Slip`, and `Salary Structure` are missing.
- Current counts at verification time: 4 Customers, 0 Suppliers, 8 Sales Orders, 1 Sales Invoice, 8 Payment Requests, 0 Payment Entries, 0 Journal Entries, 84 Accounts, 0 Bank Accounts, 0 Bank Transactions, 0 Payment Terms Templates, 0 Purchase Invoices, 0 Employees.
- Collections snapshot at verification time: 1 unpaid Sales Invoice, 1 overdue Sales Invoice, 8 expected Payment Requests, 0 paid Payment Requests.
- Company: `Locally Twisted`, USD, United States, fiscal year 2026 active, default bank account not set.
- Sales tax templates exist and `US ST 6% - LT` is marked default.
- Payment gateway account exists for local Stripe test mode: `Stripe-Test - USD - LT`.

Do not repeat those counts without rerunning the verifier; they are live data, not static documentation.

## Money Lifecycle

Target operating loop:

1. Inquiry lands as a Lead through `/contact`.
2. Jeff reviews the inquiry, follows up, and decides whether it becomes quote/order work.
3. Existing checkout path creates/reuses Customer/Contact, creates Sales Order and Payment Request, and sends the customer to Stripe.
4. Payment success/webhook marks Payment Request paid, creates Sales Invoice, and sends paid-order emails.
5. Accountant/Jeff reviews unpaid invoices, overdue invoices, expected payments, and recent paid orders from Accountant Home.
6. Bank transactions are imported by CSV first, or Plaid only after bank support and security approval.
7. Bank reconciliation matches deposits, Stripe payouts, expenses, and adjustments before monthly close.
8. Suppliers/contractors are tracked as vendors with payments that can support accountant-ready 1099 review.
9. Payroll feasibility waits on HRMS install/evaluation; accountant/provider remains responsible for tax filing and direct deposit until validated.
10. QuickBooks cutover is approved only after open balances and accountant reports match.

## QuickBooks Migration Path

Required QuickBooks exports before cutover:

- Chart of accounts.
- Customer list.
- Vendor/contractor list.
- Open invoices.
- Open bills.
- Account balances.
- Bank/account balances.
- Payroll summaries.
- 1099 contractor payment summaries.
- Sales tax liability.
- Accountant-approved Profit and Loss, Balance Sheet, Accounts Receivable, and Accounts Payable reports.

Import posture:

- Import active operating data into ERPNext: customers/vendors, open invoices/bills, opening balances, payment terms, and accountant-approved balances.
- Keep full QuickBooks export as an archive outside operational ERPNext records unless accountant requires deeper transaction history.
- Do a dry run first. The dry run must reconcile imported balances, open AR/AP, and tax liability to the accountant-approved QuickBooks reports before cutover.

## Invoicing And Collections

Source of truth:

- ERPNext Sales Invoice and Payment Request records are the operational amount-due surfaces.
- Payment Terms need to be configured before reminder timing can be trusted.
- Process Statement Of Accounts can support reminders only after templates, cadence, and customer groups are approved.

First launch behavior:

- Reminders can be staged as review candidates.
- Sending reminders automatically needs approval of the exact copy, schedule, audience, and opt-out/edge-case handling.
- Submitting documents, cancelling documents, and write-offs remain human-reviewed.

Accountant Home now has Number Cards for:

- Unpaid Invoices.
- Overdue Invoices.
- Expected Payments.
- Recent Paid Orders.

Sync and verify:

```powershell
python scripts/setup/sync_finance_workspace.py
python scripts/verify/finance_workspace_parity.py
```

## Banking And Reconciliation

Launch path:

- CSV statement import is the first test path because it is reviewable and does not require bank credentials.
- Plaid is preferred only if Jeff's bank is supported and GL/client approve the credential/security posture.
- Party matching and reconciliation automation should be enabled only after test transactions match correctly.

Monthly checklist:

- Import bank or payout statement.
- Match Stripe deposits, fees, refunds, and adjustments.
- Match supplier/vendor payments.
- Review unmatched transactions.
- Reconcile bank account.
- Export or save accountant review reports.

Current blocker:

- No Bank Account records exist and the Company default bank account is not set.

## Payroll, Contractors, And 1099 Readiness

Payroll:

- ERPNext native HRMS remains the preferred direction for employee/payroll records.
- Local ERPNext currently has `Employee`, but not payroll DocTypes. Run the finance inventory before claiming payroll readiness.
- Direct deposit, tax filing, W-2 filing, and compliance submissions stay accountant/provider-reviewed until a reliable setup is confirmed.

Contractors:

- Contractors/vendors should be Suppliers, not backend users by default.
- Supplier records need tax identity fields and payment history sufficient for accountant-ready 1099 reporting.
- Do not claim automated 1099 filing. First goal is clean contractor records and exportable payment summaries.

## Verification Commands

Read-only finance inventory:

```powershell
python scripts/verify/finance_inventory.py
python scripts/verify/finance_inventory.py --json
```

Unit/contract checks:

```powershell
python scripts/verify/finance_inventory_contract.py
python -B -m py_compile scripts/verify/finance_inventory.py scripts/verify/finance_inventory_contract.py scripts/verify/finance_workspace_parity.py scripts/setup/sync_finance_workspace.py apps/locally_twisted/locally_twisted/seed/sync_finance_workspace.py
```

Backend/payment guards to run when changing money flow:

```powershell
python scripts/verify/backend_schema_inventory.py
python scripts/verify/crm_pipeline_parity.py
python scripts/verify/crm_stage_cascade.py
python scripts/verify/backend_workspace_parity.py
python scripts/verify/payment_backend_config_contract.py
python scripts/verify/payment_webhook_contract.py
python scripts/verify/payment_cascade_contract.py
python scripts/verify/cart_checkout_contract.py
python scripts/verify/payment_launch_readiness.py
```

## Do Not Do

- Do not import QuickBooks transaction history into live ERPNext without accountant approval.
- Do not auto-submit Sales Invoices, Purchase Invoices, Journal Entries, Payment Entries, or payroll records from CRM stages.
- Do not send customer reminders until templates and timing are approved.
- Do not enable Plaid with real bank credentials as a casual setup step.
- Do not present HRMS/payroll as ready until payroll DocTypes exist and payroll flows are verified.
- Do not assume 1099 filing is automated.
