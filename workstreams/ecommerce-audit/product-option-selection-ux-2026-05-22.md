# Product Option Selection UX - 2026-05-22

Status: local source repaired; verify again in final commit state before
staging. This is not live approval.

## Scope

Guiding Light reported that selecting a size inside the product option button
also copied the long option text into the main product area. The visible issue
was especially clear on product types whose option values included a customer
label plus extra included-copy text.

This lane fixes product-option display behavior and the foil-number add-on UX.
It does not change staging/live, Stripe, DNS, Frappe Cloud, or public launch
state.

## What Changed

- Option button/select labels now separate the customer-facing display label
  from included-copy detail.
- Selected tags beside option headings use the short display label, not the
  full stored option value.
- Included-copy detail is rendered intentionally inside product details as
  `"<label> includes <detail>"`, instead of duplicating raw option text outside
  the selected button.
- Product Setup option-specific copy rules can intentionally swap the product
  title, About This Design, and What's Included, then reset when the selection
  no longer matches.
- Foil-number add-on copy now says it is for birthday bouquets, accepts up to
  3 digits, validates digits only, prices selected digits, and updates the
  displayed product price to include the add-on total.
- The add-on contract, audit report, frontend markup, runtime validation, and
  Playwright product-options verifier agree on the 3-digit maximum.

## Files

- `apps/locally_twisted/locally_twisted/templates/generators/item/item_configure.html`
- `apps/locally_twisted/locally_twisted/public/css/lt-product-page-visual-first.css`
- `apps/locally_twisted/locally_twisted/public/js/lt-product-setup-runtime.js`
- `apps/locally_twisted/locally_twisted/product_page_runtime.py`
- `apps/locally_twisted/locally_twisted/product_options.py`
- `apps/locally_twisted/locally_twisted/catalog_contract/addon_rules.py`
- `scripts/verify/product_options_experience.spec.js`
- `audits/catalog-import-audit-2026-05-08/18-proof-product-contract-report.md`

## Verification

Final pre-commit local proof:

```powershell
npm run test:product-options-experience
npm run test:product-price-display
python scripts\verify\cart_checkout_contract.py
```

Result: product-options passed `4/4`; visible price display and cart/checkout
also passed through `npm run test:owner-product-safety`.

Before staging, rerun if source changes again:

```powershell
npm run test:product-options-experience
npm run test:product-price-display
python scripts\verify\cart_checkout_contract.py
```

## Boundaries

- Stored option values may still contain source detail where needed for backend
  matching. The UI must split display label from included detail instead of
  changing source authority to make text look shorter.
- Birthday foil numbers are an add-on, not a SKU-defining variant axis.
- This fix does not approve all product pages for checkout. It only protects
  the option/add-on display and payload behavior.

Backlinks:

- `workstreams/ecommerce-audit/owner-product-setup-guard-closeout-2026-05-22.md`
- `workstreams/ecommerce-audit/generic-product-setup-runtime-2026-05-15.md`
- `ECOMMERCE-SHOP-HANDOFF.md`
