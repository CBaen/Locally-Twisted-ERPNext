D:2026-05-20 | Check:local ERPNext/Frappe product-page review | Confidence:[LOCAL-PROOF]
# Product Page Local Review - 2026-05-20

Use this handoff for the current product-page design/logic review before any
staging packet. This is local-only source work. It is not a Frappe Cloud deploy,
not a live release, not Stripe approval, and not a broader catalog
classification mutation.

## Scope Completed

- Reduced the large mobile gap between the product photo and product details in
  `lt-product-page-visual-first.css`.
- Changed the fulfillment panel to follow `lt_product_runtime.commerce_lane`
  before Item Group fallback.
- Kept quote-first/needs-review products on quote/install fulfillment language.
- Aligned Classic Arch proof expectations to
  `complex_custom_product|quote_first`.
- Added a shop smoke guard so quote-first pages fail if they show checkout
  pickup copy or omit quote/install copy.
- Regenerated the proof-product report after the Classic Arch lane correction.

## Files Owned By This Slice

- `apps/locally_twisted/locally_twisted/public/css/lt-product-page-visual-first.css`
- `apps/locally_twisted/locally_twisted/commerce_rules.py`
- `apps/locally_twisted/locally_twisted/templates/generators/item/item_details.html`
- `apps/locally_twisted/locally_twisted/verify/product_page_runtime_contract.py`
- `scripts/verify/proof_product_contract.py`
- `scripts/verify/smoke_shop.py`
- `audits/catalog-import-audit-2026-05-08/18-proof-product-contract-report.md`

## Verification Receipt

Passed locally after cache clear/restart:

- `python scripts/dev/clear_website_cache.py --restart`
- `python scripts/verify/product_page_runtime_contract.py`
- `python scripts/verify/proof_product_contract.py`
- `python scripts/verify/commerce_rules_contract.py`
- `npm run test:product-price-display`
- `npm run test:variant-media`
- `python scripts/verify/smoke_shop.py`
- `npm run test:layout-fit -- --grep "variant-product|single-product|seasonal-category"` (39/39)
- `python -m py_compile apps/locally_twisted/locally_twisted/commerce_rules.py apps/locally_twisted/locally_twisted/verify\product_page_runtime_contract.py scripts/verify/proof_product_contract.py scripts/verify/smoke_shop.py`

Ignored local screenshot evidence was kept at
`output/playwright/product-redesign-review-20260520/` with final desktop/mobile
captures for Classic Arch, Easter Bunny Ear Arch, and Encanto Bouquet. These
are review artifacts, not committed source.

## Explicit Non-Scope

- No staging deploy.
- No live deploy.
- No Frappe Cloud site update.
- No Stripe/live checkout approval.
- No DNS/provider change.
- No destructive import.
- No Website Item classification apply.

## Open Blocker Before Staging

The local product-page slice is green, but broader product classification is
not ready to treat as a release gate without review:

- `quote_event_checkout_boundary_contract.py` still expects older quote-first
  state for products including `basketball-arch`.
- The current local DB has at least `basketball-arch` as checkout.
- `website_item_classification_contract.py` dry-run passes as a dry run but
  reports 17 planned classification changes from an older target count model.

Do not apply those classification changes and do not promote this to staging
until GL reviews the current product-page design/logic and the classification
contract is reconciled with the current business model.

## Cross-Links

- Queue: `locally-twisted-queue.md`
- Decision: `locally-twisted-decisions.md`
- Lesson: `lessons-learned.md`
- Failure recipe: `capabilities/failures/product-fulfillment-copy-lane-drift.md`
- Product-page recipe: `capabilities/recipes/frappe-product-page-company-first.md`
- Control/layout recipe: `capabilities/recipes/frappe-product-clear-control-contract.md`
