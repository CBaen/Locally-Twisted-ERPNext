D:2026-05-10 | Check:local source + verifier runs 2026-05-10 | Confidence:[LOCAL-PROOF]
# Customer note checkout preservation audit

## 1. Claim being verified

Ready-to-order checkout optional `order_notes` should survive safely from the customer checkout form into backend order/payment/fulfillment evidence, without implying that notes change price, scope, or approve custom work.

## 2. Verification method

Read-only/source inspection plus the smallest relevant safe local verifier runs available during this pass.

Sources inspected:

- `apps/locally_twisted/locally_twisted/www/checkout.html`
- `apps/locally_twisted/locally_twisted/www/checkout.py`
- `apps/locally_twisted/locally_twisted/www/payment_success.py`
- `apps/locally_twisted/locally_twisted/api/cart.py`
- `apps/locally_twisted/locally_twisted/product_page_runtime.py`
- `apps/locally_twisted/locally_twisted/verify/checkout_fulfillment_contract.py`
- `apps/locally_twisted/locally_twisted/verify/checkout_lead_conversion_contract.py`
- `apps/locally_twisted/locally_twisted/verify/payment_cascade_contract.py`
- existing ecommerce-audit artifacts named in the agent brief.

Verifier commands run:

```bash
python scripts/verify/payment_cascade_contract.py
python scripts/verify/checkout_fulfillment_contract.py
```

## 3. Witness / output path

Artifact: `workstreams/ecommerce-audit/customer-note-checkout-preservation-audit-2026-05-10.md`

Command output witnessed in this session:

```text
[PAYMENT CASCADE CONTRACT] PASS
  sales_order: SAL-ORD-2026-00021
  payment_request: ACC-PRQ-2026-00020
  payment_entry: ACC-PAY-2026-00002
  sales_invoice: ACC-SINV-2026-00003
  receipt_email_queue: 1ubl34lhrm
  operator_email_queue: 1udp44vtqi
  welcome_email_queue: 1ue79o7ove
  checkout_notes: 1tefqhs0dm
  rollback: verifier rolled back all generated records
```

```text
[CHECKOUT FULFILLMENT CONTRACT] FAIL
  - ... KeyError: 'sales_order'
```

Relevant source witnesses:

- `checkout.html` has checkout UI field `name="order_notes"` labeled “Anything we should know? (optional)” and JS reads it into the quote handoff payload as `notes`.
- `checkout.py` accepts `order_notes` in `submit_guest_order`, strips it, composes checkout notes, and calls `_record_order_notes(...)` after Sales Order submission.
- `_record_order_notes` creates a `Communication` linked to `reference_doctype="Sales Order"`, `reference_name=<SO>`, subject `Customer checkout notes - <SO>`, content escaped from the composed notes.
- `checkout.py` records a backend failure at step `checkout_notes_transfer` if attaching notes fails, but checkout continues.
- `payment_success.py` reads that same Sales Order `Communication` via `_get_customer_order_notes_html(so.name)` and includes it in the operator “New paid order” email block as `Customer notes`.
- `payment_cascade_contract.py` directly seeds `_record_order_notes(...)`, reconciles a paid Sales Order, and verifies the checkout notes `Communication` exists and contains the submitted notes.

## 4. Result: BLOCKED / PARTIAL

Current answer: optional `order_notes` is implemented as backend Sales Order timeline `Communication`, not as a structured Sales Order field, Sales Order Item field, Payment Request field, Sales Invoice field, or separate fulfillment DocType field.

What is proven:

- UI/source path exists for collecting optional notes.
- `submit_guest_order(...)` contains the intended note-transfer call into a Sales Order-linked backend `Communication`.
- Payment/fulfillment cascade can consume an existing Sales Order note `Communication`: the safe `payment_cascade_contract.py` passed and verified `checkout_notes` after rollback.

What is not fully proven end-to-end:

- A single safe verifier did not prove `order_notes` submitted through `submit_guest_order(...)` becomes the Sales Order `Communication` and then appears in paid-order fulfillment/operator evidence.
- The closest checkout verifier path currently passes `order_notes` into `submit_guest_order`, but does not assert the note `Communication` content.
- `checkout_fulfillment_contract.py`, the closest ready-to-order checkout-path verifier run in this session, failed before producing a Sales Order witness, so it cannot be used as current proof for note preservation.

## 5. Exact blocker or failure

The remaining gap is verifier coverage, not an obvious missing code path.

Specific blocker:

- No current passing gate ties this chain together in one rollback-safe run:
  `checkout.html/order_notes` -> `submit_guest_order(order_notes=...)` -> Sales Order-linked `Communication` -> Payment Request/Sales Order paid cascade -> operator/fulfillment evidence.

Specific failure observed:

- `python scripts/verify/checkout_fulfillment_contract.py` failed with `KeyError: 'sales_order'` while trying to inspect `result["sales_order"]`; the submit result did not include a Sales Order in the first delivery scenario. I did not patch it because this task is report-only.

## 6. Minimal next action

Add the smallest focused verifier gate, either by extending `checkout_fulfillment_contract.py` after its current failure is diagnosed or by adding a narrow new verifier such as `customer_note_checkout_preservation_contract.py`.

Recommended gate:

1. Monkeypatch Stripe session creation and intercept/rollback commits, matching existing verifier style.
2. Submit a ready-to-order item through `submit_guest_order(...)` with a unique `order_notes` value.
3. Assert the returned Sales Order exists inside the transaction.
4. Assert one linked `Communication` exists with subject `Customer checkout notes - <SO>` and contains the unique note.
5. Assert the Payment Request links to the same Sales Order, but do not submit live payment.
6. Reconcile through the safe paid-order cascade with email/payment side effects stubbed or rollback-contained.
7. Assert the operator/fulfillment notification evidence includes the same note.
8. Run a no-note case proving no fake customer note is invented.
9. Roll back and prove no generated Sales Order, Payment Request, invoice, email queue, customer/contact/address, or Communication survived.

Until that gate passes, say: customer notes are code-wired into Sales Order timeline and payment-success operator email lookup, but ready-to-order checkout note preservation is not fully end-to-end verified.