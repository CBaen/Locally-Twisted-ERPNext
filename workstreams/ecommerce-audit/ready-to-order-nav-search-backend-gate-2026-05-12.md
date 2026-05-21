D:2026-05-12 | Check:local ERPNext DB + rendered search/nav verifier evidence | Confidence:[LOCAL-PROOF]
# Ready-to-Order Nav/Search Backend Gate

## Superseded For Public Chrome On 2026-05-21

This handoff is historical product-checkout eligibility evidence. It no longer
owns the public `Ready-to-Order` header/menu/search/drawer chrome. GL corrected
that public chrome should be category discovery, not product quick links. The
current source handoff is
`../ready-to-order-category-menu-2026-05-21.md`.

Do not use this file to restore product quick links or ERPNext/backend copy in
the customer-facing menu. Product eligibility still matters below the category
page and in checkout/product-page contracts.

Use this handoff for GPT-5.5/OpenClaw peers touching LT Ready-to-Order header
links, mobile drawer links, search quick links, or Website Item checkout
classification.

## Current State

- Ready-to-Order nav/search product links are backend-derived from ERPNext
  Website Item records, not hardcoded product categories.
- `READY_TO_ORDER_OWNER_INCLUDE_CODES` is an owner merchandising allowlist only.
  It does not bypass backend checkout eligibility.
- A product must be published, backed by an enabled root Item, owner-included,
  `lt_product_page_type == "simple_product"`, `lt_commerce_lane == "checkout"`,
  and have a Standard Selling price before it can appear as a Ready-to-Order
  product quick link.
- The header search overlay keeps backend-approved quick-link nodes in the DOM
  and hides nonmatching entries with the `hidden` attribute while filtering.
  Tests must assert hidden/non-visible for filtered-but-approved products, not
  DOM absence.
- Owner-excluded Classic products remain absent from Ready-to-Order quick links.

## Current Owner-Included Products

Live local ERPNext read on 2026-05-12:

- `6-graduation-stands` -> published, `simple_product`, `checkout`,
  `shop-items/stands-easels/6-graduation-stands`
- `7-butterfly-column` -> published, `simple_product`, `checkout`,
  `shop-items/columns/7-butterfly-column`
- `easter-balloon-cups` -> published, `simple_product`, `checkout`,
  `shop-items/seasonal-specialty/easter-balloon-cups`
- `graduation-grab-n-go` -> published, `simple_product`, `checkout`,
  `shop-items/grab-go/graduation-grab-n-go`

If an import/seed later reverts one of these records to `quote_first` or
`needs_review`, the nav/search link must disappear until the backend fields are
restored intentionally.

## Review Fixes Closed

1. `scripts/verify/search_contract.spec.js` now treats
   `7-butterfly-column` as a backend-approved quick-link node that can be
   filtered hidden after typing `balloon cups`; the test no longer expects that
   node to be removed from the DOM.
2. `apps/locally_twisted/locally_twisted/navbar_context.py` now rejects
   owner-included products whose Website Item fields are not explicitly
   `simple_product|checkout`.
3. `scripts/verify/nav_ia.py` now fails if the old
   `_is_backend_checkout_enabled(...) or owner_include` bypass returns.
4. The mobile Ready-to-Order drawer uses `All Ready-to-Order`, not `Shop All`,
   so it matches the backend-approved route framing already guarded by
   `nav_ia.py`.

## Verification Receipt

Passed on 2026-05-12:

```powershell
python -m py_compile apps/locally_twisted/locally_twisted/navbar_context.py scripts/verify/nav_ia.py
python scripts\verify\nav_ia.py
npm run test:search-contract
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute frappe.client.get_list --kwargs "{'doctype':'Website Item','filters':{'item_code':['in',['6-graduation-stands','7-butterfly-column','easter-balloon-cups','graduation-grab-n-go']]},'fields':['item_code','published','lt_product_page_type','lt_commerce_lane','route'],'limit_page_length':20,'order_by':'item_code asc'}"
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.navbar_context._ready_to_order_exclusion_reason --args "[{'item_code':'7-butterfly-column','lt_product_page_type':'quote_first','lt_commerce_lane':'quote'}]"
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.navbar_context._ready_to_order_product_links
```

The synthetic `quote_first` owner-included product returned
`"not_checkout_enabled"`.

## Next Peer Rule

Do not add a product to Ready-to-Order nav/search by editing the template alone.
Change the Website Item fields and owner include/exclude constants
deliberately, then rerun `python scripts\verify\nav_ia.py` and
`npm run test:search-contract`.
