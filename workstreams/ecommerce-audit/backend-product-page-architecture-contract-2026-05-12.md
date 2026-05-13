# Backend Product-Page Architecture Contract

Status: complete on local/source code. No live site update, Frappe Cloud update,
DNS change, Stripe change, destructive catalog import, or Website Item lane flip
was made.

## Correction

This work corrects the prior layer mistake. The complex checkout scaffold is a
planning classifier. The architecture is now the generic receiving contract:
source/ERPNext axis semantics become backend-owned product-page controls,
versioned cart payload keys, server-derived resolver fields, and
Quotation/Sales Order/Sales Invoice line parity.

Products are examples and proof rows only. No product-specific branch is
allowed by this contract.

## Code

- `apps/locally_twisted/locally_twisted/catalog_contract/product_page_architecture_contract.py`
  builds and validates `lt-product-page-architecture-contract-v1`.
- `apps/locally_twisted/locally_twisted/verify/product_page_architecture_contract.py`
  joins the current ProductPatternContract report to the architecture contract.
- `apps/locally_twisted/locally_twisted/product_options.py` exposes the live
  Webshop projection for product templates.
- `apps/locally_twisted/locally_twisted/templates/generators/item/item_details.html`
  emits `.js-lt-product-page-architecture` JSON on product pages.
- `scripts/verify/product_page_architecture_contract.py` generates
  `output/product-page-architecture-contract.*`.
- `scripts/verify/product_page_architecture_contract_contract.py` is the fast
  pure regression gate.
- `scripts/verify/product_page_architecture_readiness.py` now passes the source
  catalog artifact into the new architecture row instead of relying on an
  implicit container path.
- `scripts/verify/product_quote_first_experience.spec.js` now proves the
  emitted architecture JSON on ready-to-order and quote-first product pages.

## Contract Shape

- Sale-unit axes target `selected_options`.
- Color customization axes target `color_recipes`; checkout must not treat them
  as single-select `selected_options`.
- Approved priced add-ons target `add_ons`.
- Review-only/unmapped add-ons target `quote_context` and block checkout.
- Browser payload is `lt-product-config-v1`.
- Server-derived fields are `resolved_item_code`, `price_provenance`,
  `readable_summary`, and `canonical_cart_line_key`.
- `Quotation Item`, `Sales Order Item`, and `Sales Invoice Item` must all carry
  the LT line-configuration field set.

## Verification

Green:

- `python scripts/verify/product_page_architecture_contract_contract.py`
- `python scripts/verify/product_page_architecture_contract.py`
- `python scripts/verify/product_page_runtime_contract.py`
- `node --check scripts/verify/product_quote_first_experience.spec.js`
- `npm run test:product-quote-first`
- `python scripts/verify/verifier_cli_contract.py`

Expected blocked-shape gate:

- `python scripts/verify/product_page_architecture_readiness.py --report output/product-page-architecture-readiness.json`

Result: `technical_architecture_ok: True`; `import_reopen_ok: False` only
because `public_ecommerce_reopen` is blocked by the current paused ecommerce
site config.

## Handoff

Use this contract before changing product-page controls, cart payload shape,
checkout admission, quote-first product handoff, add-on selectors, or import
claims. Do not use product lists, product names, or the complex scaffold as the
architecture. They are downstream evidence against this contract.
