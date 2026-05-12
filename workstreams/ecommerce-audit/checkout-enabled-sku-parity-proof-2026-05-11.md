# Checkout enabled-SKU parity proof - 2026-05-11

D:2026-05-11 | Check:`python scripts/verify/checkout_product_family_contract.py --report workstreams/ecommerce-audit/2026-05-10-2330-phase-1-4-shop-audit/checkout-product-family-all-skus-final.json` | Confidence:high

## What changed

The checkout product-family verifier no longer proves one sample SKU per family. It now proves every currently enabled sellable SKU that is classified as `simple_product|checkout`:

- 13 bouquet Website Item families x 3 enabled size variants = 39 sale SKUs.
- 39 foil-number add-on rows, one per bouquet SKU.
- 7 Easter Balloon Cups variants.
- 1 Mother's Day Bouquet single SKU.

The rollback-safe verifier creates one Sales Order and one Sales Invoice with 86 rows total, verifies LT payload/schema fields on every base/add-on row, and rolls back all generated records.

## Files changed

- `apps/locally_twisted/locally_twisted/verify/checkout_product_family_contract.py`
  - Replaced sample Small-bouquet proof with all enabled `Bouquet Size` variant proof.
  - Added all enabled Easter `Easter Designs` variant proof.
  - Kept Mother's Day as the single-SKU simple-path proof.
  - Counts expected base sale SKU rows and add-on rows explicitly before asserting Sales Order/Sales Invoice preservation.
- `scripts/verify/checkout_product_family_contract.py`
  - Prints `enabled_sale_sku_count`, `add_on_line_count`, and the architecture-not-launch Easter status.
- `workstreams/ecommerce-audit/2026-05-10-2330-phase-1-4-shop-audit/phase-1-4-shop-audit-closeout-2026-05-10.md`
  - Corrects the peer handoff from “15 products” to “15 checkout Website Item families/pages and 47 enabled sale SKUs.”

## Verification

```text
python -m py_compile apps/locally_twisted/locally_twisted/verify/checkout_product_family_contract.py scripts/verify/checkout_product_family_contract.py
python scripts/verify/checkout_product_family_contract.py --report workstreams/ecommerce-audit/2026-05-10-2330-phase-1-4-shop-audit/checkout-product-family-all-skus-final.json

[CHECKOUT PRODUCT-FAMILY CONTRACT] PASS
  bouquet_family_count: 13
  enabled_sale_sku_count: 47
  add_on_line_count: 39
  sales_order_line_count: 86
  sales_invoice: ACC-SINV-2026-00003
  easter_balloon_cups: architecture_verified_not_launch_approval
  survivor_counts: {'customer': 0, 'sales_order': 0, 'sales_invoice': 0}
  rollback: verifier rolled back all generated records
```

## Boundaries for next agents

- Do not call this live checkout readiness. Public ecommerce is still paused with `lt_ecommerce_paused=1`.
- Do not call current ERPNext product records final catalog truth; they are test fixtures until a future controlled purge/reupload/import proof passes.
- Do not collapse Website Item family/page count and sellable SKU count again. Use both counts in peer-facing docs.
- Run rollback/Frappe DB verifiers serially unless a verifier explicitly proves parallel isolation.
