D:2026-05-10 | Review:Phase 4 quote/event checkout boundary architecture rereview | Confidence:high
# Phase 4 architecture rereview — quote/event checkout boundary

## Verdict

PASS

The architecture concern from the first review has been addressed. Runtime contract precedence now fails closed for explicit/partial `needs_review`, blank fields that would otherwise infer checkout, and partial explicit checkout. Paid checkout is allowed only by an explicit `simple_product|checkout` Website Item contract, while the Phase 3 checkout family remains protected by that explicit contract path.

## Evidence reviewed

- Prior review: `workstreams/ecommerce-audit/phase-4-architecture-review-2026-05-10.md`
- Runtime contract: `apps/locally_twisted/locally_twisted/product_page_runtime.py`
- Cart API resolver: `apps/locally_twisted/locally_twisted/api/cart.py`
- Boundary verifier: `apps/locally_twisted/locally_twisted/verify/quote_event_checkout_boundary_contract.py`
- Recorded Phase 4 verifier output: `workstreams/ecommerce-audit/phase-4-quote-event-checkout-boundary-contract-20260510.json`
- Recorded Phase 3 checkout output: `workstreams/ecommerce-audit/phase-3-checkout-product-family-contract-20260510.json`

## Findings

1. Explicit/partial `needs_review` now fails closed.
   - `resolved_product_page_contract_values()` returns `needs_review|needs_review` if either explicit Website Item field is `needs_review`.
   - The verifier now includes the previously missing precedence cases:
     - explicit page type `needs_review` + blank lane + inferred checkout resolves `needs_review|needs_review`.
     - blank page type + explicit lane `needs_review` + inferred checkout resolves `needs_review|needs_review`.
   - Recorded Phase 4 output shows both cases passing under `contract_precedence`.

2. Checkout drift now fails closed.
   - Blank explicit fields with inferred checkout resolve `needs_review|needs_review`; item-group hints can no longer create paid checkout by themselves.
   - Partial explicit checkout without explicit `simple_product` resolves `needs_review|needs_review`.
   - `api/cart.py` still blocks trusted runtime contracts whose `commerce_lane` is not `checkout` before returning a purchasable cart line.
   - Sales Order line and add-on line builders still re-check the trusted runtime contract and block non-checkout lanes, so stale/localStorage payloads cannot bypass the cart resolver.

3. Paid checkout requires explicit `simple_product|checkout`.
   - The only runtime branch that returns checkout is `explicit_page_type == "simple_product" and explicit_commerce_lane == "checkout"`.
   - Explicit `checkout` lane alone is not enough.
   - Inferred checkout alone is not enough.

4. Phase 3 checkout path remains protected.
   - Recorded Phase 3 output remains `ok: true`.
   - The approved checkout rows still carry `stored_contract: simple_product|checkout` and resolve checkout/add-on sale lines.
   - The Phase 3 verifier reports zero survivor Customer/Sales Order/Sales Invoice records and `rolled_back: true`.

5. Phase 4 boundary coverage remains intact.
   - Recorded Phase 4 output is `ok: true`.
   - It blocks 33 quote-first rows and 5 needs-review rows across cart API, direct checkout URL, and stale localStorage/sale-line resolution.
   - It reports `record_count_deltas: {}` and `rolled_back: true`.

## Notes

`api/cart.py` still computes and returns the older item-group `checkout_lane` metadata, but enforcement is based on `product_page_contract_for_website_item(...).commerce_lane`. I do not see that legacy metadata opening a checkout path in the reviewed runtime/sale-line boundary.

## Conclusion

The specific architecture gap from the prior review is fixed. The boundary now has the intended allow-list posture: paid checkout only for explicitly classified `simple_product|checkout` products; quote-first, needs-review, partial, blank, and inferred-checkout drift fail closed.
