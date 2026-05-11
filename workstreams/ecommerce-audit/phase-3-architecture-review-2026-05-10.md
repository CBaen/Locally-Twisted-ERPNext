# Phase 3 Architecture Review — Checkout Product-Family Proof

**Verdict: CONCERN**

The verifier is architecturally meaningful: it exercises backend runtime checkout resolution and ERPNext document persistence rather than a UI-only smoke path. I cannot mark full PASS because the requested proof artifact `output/phase-3-checkout-product-family-contract-20260510.json` is absent from the repo state inspected, so the actual latest run/result was not inspectable.

## Evidence inspected

- `apps/locally_twisted/locally_twisted/verify/checkout_product_family_contract.py`
  - Rollback-only runner intercepts commits, runs backend contract, then verifies survivor counts are zero.
  - Checks Sales Order Item and Sales Invoice Item custom line schema.
  - Iterates the approved foil bouquet family, resolves live Website Item/Item data, calls checkout sale-line resolution, submits a Sales Order, creates/submits a Sales Invoice, and asserts LT configuration fields survive both documents.
  - Includes Mother's Day as simple checkout/non-add-on path and Easter as explicitly deferred seasonal status.
- `scripts/verify/checkout_product_family_contract.py`
  - Runs `bench --site frontend execute locally_twisted.verify.checkout_product_family_contract.run` inside the ERPNext backend container and can write a JSON report with `--report`.
- `apps/locally_twisted/locally_twisted/product_page_runtime.py`
  - Runtime owns reusable backend helpers for configuration normalization, Sales Order line field construction, add-on line construction, add-on eligibility/pricing validation, and Sales Order → Sales Invoice configuration copy.
- `output/phase-3-checkout-product-family-contract-20260510.json`
  - **Not found.** The repo has no `output` directory in the inspected state.

## Architectural concerns

1. **Missing run artifact blocks proof-level PASS.** Source inspection shows a strong verifier, but the requested JSON output is absent, so there is no inspectable pass/fail payload, line counts, rollback status, or survivor counts for the current run.
2. **The verifier proves one approved product family, not arbitrary future families.** The hard-coded bouquet list is appropriate as a scope lock for this phase, but the result should be described as “foil-number bouquet family + Mother's Day simple path,” not generalized to all product families.
3. **Invoice preservation is proven through the runtime copy helper, not necessarily the whole live invoicing automation path.** The verifier explicitly calls `copy_sales_order_line_configuration_to_invoice(invoice, sales_order_name)` after `make_sales_invoice`. That proves the reusable backend helper works and data can survive invoice submission; it does not by itself prove every production invoice creation entrypoint invokes that helper.

## Reusable-backend-runtime assessment

**Positive.** This is not UI-only and not merely a hard-coded happy-path fixture. The verifier uses backend runtime boundaries: `get_checkout_add_on_options`, checkout sale-line resolution, `resolve_cart_item_for_sale`, runtime line-field helpers, real ERPNext Sales Order submit, real Sales Invoice creation/submit, and rollback verification. The hard-coded approved bouquet list functions as a contract boundary and drift detector.

## Required fixes before PASS

1. Run the script with `--report output/phase-3-checkout-product-family-contract-20260510.json` and commit/store the resulting JSON artifact for inspection.
2. If Phase 3 acceptance claims production invoice automation, add or reference a separate verifier that exercises the actual production invoice creation hook/path without manually calling the copy helper.
3. Keep acceptance wording scoped to the verified family unless/until discovery-based tests cover more product families.
