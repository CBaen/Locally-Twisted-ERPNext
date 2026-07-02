# Product Gallery Staging Follow-Up - 2026-05-24

Status: source and hosted staging product-gallery route proof pass.

## Scope

This follow-up covers two user-reported product-page issues on staging:

- remove the visible "Other product photos" copy;
- keep the base product photo available after another gallery or configured
  product photo is selected.

This is a follow-up to the architecture restoration documented in
`product-gallery-restoration-2026-05-22.md`.

## Source Points

- Label removal/full repo commit: `4d5c287 Fix product gallery thumbnail copy`
- Product-flow/gallery hardening commit: `70b8869 Fix staging checkout product flow`
- Safety/current full repo commit: `203127a Hide unsafe checkout provider errors`
- App mirror current point: `9ce07f2`

## Files

- `apps/locally_twisted/locally_twisted/templates/generators/item/item_image.html`
- `apps/locally_twisted/locally_twisted/product_page_runtime.py`
- `apps/locally_twisted/locally_twisted/public/css/lt-product-page-visual-first.css`
- `scripts/verify/product_gallery_experience.spec.js`

## Kept Behavior

- The gallery rail is self-explanatory and does not render the removed label.
- The base product image remains a selectable thumbnail.
- Variant/configured product media may change the main image, but it must not
  trap the user away from the base image.
- Webshop fallback image data stays fallback only; LT projected gallery/runtime
  data is the primary product-page source.

## Hosted Staging Proof

Fresh staging command during this documentation pass:

```bash
$env:LT_BASE_URL='https://locallytwisted-staging.frappe.cloud'
npm run test:product-gallery-experience
```

Observed result: `4/4` passed, including the configured bouquet proof that the
base product photo stays available after selecting a size.

## Boundaries

- This does not approve ERPNext category images.
- This does not approve new product media.
- This does not open checkout or payments.
- Product gallery proof does not prove Stripe/payment configuration.

## Backlinks

- `workstreams/ecommerce-audit/product-gallery-restoration-2026-05-22.md`
- `workstreams/frappe-cloud-staging-owner-review-2026-05-24.md`
- `capabilities/failures/product-gallery-projection-regression.md`
- `ECOMMERCE-SHOP-HANDOFF.md`
- `CODING-HANDOFF.md`
