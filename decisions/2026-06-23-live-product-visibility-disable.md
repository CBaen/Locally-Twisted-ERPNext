# 2026-06-23 - Live Product Visibility Disable

## Decision

Keep these four products hidden on the live site and disable their underlying
ERPNext Items/variants:

- `large-garland`
- `mothers-day-bouquet`
- `large-organic-column`
- `pride-progress-rainbow-balloon-arch`

The public visibility state is:

- template/single Item disabled;
- child variants disabled where they exist;
- Website Item unpublished;
- Website Item page type and commerce lane held at
  `needs_review|needs_review`.

Do not re-enable, publish, reroute, or move any of these products back to
checkout/quote visibility without fresh GL approval.

## Reasoning

The products were already documented as the retired set, but the live Desk
Item form was blocked by the custom `Protected Owner Catalog Guard`. That guard
is LT project code protecting raw catalog tables from owner-like edits; it is
not an external cybersecurity issue and not a reason to abandon the approved
business change.

For this exact approved product list, the safest live repair was a scoped admin
maintenance write through Desk System Console: only `Item.disabled` on the
target templates/single Item and variants, plus idempotent Website Item
unpublish/needs-review fields. No prices, orders, customers, payment settings,
Stripe records, DNS, Frappe Cloud release settings, or site settings changed.

## Implementation Boundary

Implemented live on `https://locallytwisted.com`:

- `large-garland`: 88 Items disabled, including 87 variants.
- `mothers-day-bouquet`: 1 Item disabled, no variants.
- `large-organic-column`: 175 Items disabled, including 174 variants.
- `pride-progress-rainbow-balloon-arch`: 5 Items disabled, including
  4 variants.

Verified after the write:

- every target root Item had `disabled=1`;
- every target child variant count had `active_variants=0`;
- each Website Item had `published=0` and `needs_review|needs_review`;
- all four product routes returned `404`;
- `/shop` returned `200` and contained none of the four slugs.

## Guard

Use `capabilities/recipes/erpnext-live-product-visibility-retirement.md` for
future live catalog visibility retirements. If the Item form blocks with
`Protected Owner Catalog Guard`, do not keep retrying the same form and do not
disable the guard. Use the documented scoped admin maintenance path only after
the product list and business approval are exact.

## Receipts

- Feature handoff:
  `workstreams/ecommerce-audit/live-product-disable-2026-06-23.md`
- Recipe:
  `capabilities/recipes/erpnext-live-product-visibility-retirement.md`
- Failure recipe:
  `capabilities/failures/owner-catalog-guard-live-disable-drift.md`

## Alternatives Considered

- Save from the normal Item form. Rejected by the owner catalog guard.
- Save the Item document through System Console. Rejected by the same guard.
- Disable or weaken the owner catalog guard. Rejected because the guard is
  correct for owner-like raw catalog edits.
- Use Product Setup alone to hide the products. Rejected for this live release
  because current public route visibility still depends on Website Item and
  Item state.

## Decided By

Guiding Light requested the documented product removals from live visibility.
Codex implemented and verified the scoped live disable on 2026-06-23.
