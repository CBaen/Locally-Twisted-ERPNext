# Staging Checkout Internal Processing - Item 4 Scope - 2026-05-29

Status: scope proposed by Codex after Guiding Light approved item 3 complete.
This scope needs Guiding Light approval before execution.

This is not a staging deploy approval, provider-change approval, live checkout
approval, DNS approval, Search Console approval, live Stripe approval, or product
data change approval.

## Human Outcome

After a customer completes a staging test-mode purchase, the business needs a
usable internal trail. The operator should be able to see what was purchased,
how it was configured, whether it was paid, how it should be fulfilled, who to
contact, which emails were sent, and whether anything failed.

Item 4 should prove the inside of the business process, not more product
combinations.

## Why This Is Next

Item 1 proved the important customer and internal emails were sent and received,
with links working.

Item 2 fixed and proved the one-cent checkout mismatch.

Item 3 proved staging test-mode checkout product diversity: pickup,
delivery-only, mixed carts, variants, approved foil-number add-ons, and
quote-first bypass prevention.

The remaining original risk is internal consistency and processing after the
purchase lands in ERPNext.

## Current Source Boundary

- Item 4 source branch: `codex/item4-internal-processing-scope`
- Item 3 approved baseline: `962e2f7 Record item 3 approval`
- Frappe app mirror remains at `35ac2b1`
- No new staging push is approved by this scope
- No provider dashboard, live Stripe, DNS, Search Console, or product data work
  is approved by this scope

## Review Targets

Use existing paid staging orders first:

- `SAL-ORD-2026-00024`
- `SAL-ORD-2026-00030`
- `SAL-ORD-2026-00031`
- `SAL-ORD-2026-00034`

Only create a new staging test order if the existing orders cannot answer a
required question. If a new order is needed, record exactly why the existing
orders were not enough.

## Item 4 Matrix

1. Sales Order record chain

   Confirm each representative paid order has the expected Sales Order state,
   line items, selected options, delivery or pickup information, tax, total, and
   customer-facing summary.

2. Payment and reconciliation chain

   Confirm the internal chain from Payment Request through Stripe test payment
   reference and ERPNext paid state. Where Payment Entry or Sales Invoice is
   expected, confirm it exists and matches the order total.

3. Customer, Contact, and Lead linkage

   Confirm the purchase is tied to a usable Customer and Contact, with the right
   email/phone/address where supplied. Confirm Lead conversion or linkage does
   not create confusing duplicates.

4. Email Queue and Communication tracking

   Confirm customer receipt, first-order welcome when expected, and internal
   paid-order notification are visible in internal records with matching order
   IDs, line summaries, totals, and links. Confirm moved Gmail messages are
   searched by order ID and are not treated as missing just because they are not
   in the main inbox folder.

5. Checkout notes and fulfillment handoff

   Confirm customer notes, selected options, delivery-only handling, pickup or
   delivery status, and operator instructions are visible where the operator
   would naturally review the order.

6. Error and scheduler health

   Confirm the paid checkout path did not leave new relevant Error Log entries,
   stuck Email Queue rows, failed jobs, or scheduler health issues that would
   hide a downstream failure.

7. Duplicate and idempotency protection

   Confirm repeat webhook or return-path behavior does not duplicate charges,
   Sales Invoices, Payment Entries, customer emails, or internal notifications.

8. Operator readability

   Confirm the Desk-facing handoff is understandable for non-technical users:
   what happened, what needs action, and where the order details live.

## Proof Order

1. Confirm source branch and staging/app-mirror baseline.
2. Run local rollback-safe contracts that already cover the paid-order backend
   path.
3. Inspect existing staging records read-only before creating any new order.
4. Search Email Queue, Communication, and Gmail by order ID where email tracking
   needs external proof.
5. Create a new staging test-mode order only if existing paid orders cannot
   prove a required internal-processing question.
6. Send the item 4 evidence packet to the triad for technical review.
7. Ask Guiding Light for business approval only after the triad records whether
   item 4 passed, passed with notes, or failed.

## Candidate Local Verifier Set

Use current local verifiers as proof helpers before touching staging:

- `python scripts/verify/payment_cascade_contract.py`
- `python scripts/verify/payment_success_reconciliation_contract.py`
- `python scripts/verify/payment_webhook_contract.py`
- `python scripts/verify/payment_backend_config_contract.py`
- `python scripts/verify/payment_launch_readiness.py`
- `python scripts/verify/checkout_lead_conversion_contract.py`
- `python scripts/verify/customer_note_checkout_preservation_contract.py`
- `python scripts/verify/business_automation_index.py --report output/business-automation-index.json`
- `python scripts/verify/synthetic_business_pipeline.py --report output/synthetic-business-pipeline.json`

If any verifier fails, stop and fix the failing item before widening the audit.

## Pass Conditions

Item 4 can pass only when representative paid staging purchases show a consistent
internal chain:

- Sales Order exists and matches the customer-facing purchase
- Payment Request and paid/reconciliation state match the order total
- Payment Entry and Sales Invoice exist where the paid-order cascade expects
  them
- Stripe test reference, ERPNext total, thank-you page, receipt email, and
  internal notification agree
- Customer and Contact records are usable and not confusingly duplicated
- Email Queue and Communication records show the expected sent or tracked email
  trail
- Customer notes and fulfillment details are visible to the operator
- No relevant new Error Log, stuck queue, or scheduler failure is left hidden
- Repeat payment/webhook paths do not create duplicate money or email records

## Stop Conditions

Stop item 4 and return a failed finding if any of these appear:

- Missing Sales Order for a paid checkout
- Order, Stripe, receipt, invoice, or internal email totals disagree
- Missing or confusing customer/contact linkage
- Missing required internal paid-order notification
- Missing receipt or welcome tracking where policy expects it
- Customer notes or fulfillment details are dropped before the operator can see
  them
- Duplicate charge, invoice, Payment Entry, receipt email, or internal email
- Relevant Error Log, failed job, or stuck queue row after a paid checkout
- A pending reconciliation state is shown to the customer or operator as clean
  success
- The next proof step would require provider mutation, live checkout, staging
  deployment, DNS, Search Console, live Stripe, or product data changes

## Triad Review Requirement

After execution, the triad should review the evidence from three angles:

- Customer/business trust: would a non-technical operator know what happened and
  what to do next?
- Backend/accounting integrity: do Sales Order, payment, invoice, customer, and
  email records agree?
- Failure handling: does any downstream problem fail loudly instead of looking
  successful?

Guiding Light should not need to approve the full data matrix manually. Guiding
Light approves the business risk after the triad gives a clear pass/fail
recommendation with evidence.

## Approval Marker Needed

Approve this exact scope before execution:

> I approve item 4 scope for staging test-mode internal-processing proof only.
> This does not approve live checkout, staging deployment, provider changes,
> DNS, Search Console, live Stripe, or product data changes.
