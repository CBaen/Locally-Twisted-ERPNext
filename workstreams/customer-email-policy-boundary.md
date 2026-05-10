# Customer Email Policy Boundary

Last updated: 2026-05-09 by Codex after adding mandatory internal copy routing for paperwork/documentation email paths.

## Outcome

Keep customer/operator email behavior aligned with receipts, policy lanes, and bookkeeping expectations without sending live email or mutating accounting records during verification.

## Current State

- `locally_twisted.verify.customer_email_policy_contract.run` statically checks source code for inquiry acknowledgment, paid receipt, operator notification, first-order welcome, and paid-order cascade coverage.
- `scripts/verify/customer_email_policy_contract.py` runs the in-app contract through Docker/Frappe and exits nonzero on missing policy markers, attachment/PDF kwargs, wrong reference DocTypes, or non-queued sendmail calls.
- `locally_twisted.communication_copy_policy` owns internal copy routing: all code-owned document/paperwork emails copy `hi@locallytwisted.com`; customer/client/contractor/accountant-facing emails also copy `cameron@locallytwisted.com`.
- `scripts/verify/customer_documents_contract.py` and `scripts/verify/payment_cascade_contract.py` now prove the required copy recipients exist in ERPNext `Email Queue Recipient` rows during rollback-safe fake-data runs.
- Business automation index now treats this contract as part of Lead acknowledgment and paid-order reconciliation.
- Synthetic business pipeline now includes `customer_email_policy_boundaries`.

## Boundaries

- No customer email is sent.
- No Email Queue row is created by this verifier.
- No Sales Invoice, Payment Request, Payment Entry, or Communication is mutated.
- No PDF or print attachment kwargs are allowed in the checked sendmail calls.
- This is source-policy verification, not final copy approval.
- Internal copies are queued as BCC where possible so outside recipients do not see the copy-routing addresses.

## Owner Files

- `apps/locally_twisted/locally_twisted/verify/customer_email_policy_contract.py`
- `scripts/verify/customer_email_policy_contract.py`
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
python scripts/verify/payment_cascade_contract.py
python scripts/verify/synthetic_business_pipeline.py --report output/synthetic-business-pipeline.json
python scripts/verify/business_automation_index.py --report output/business-automation-index.json
```

## Next Safe Slice

Review customer-facing email copy against the approved brand voice and policy pages. Keep delivery no-live until recipients, opt-out/response handling, and approval gates are explicit.
