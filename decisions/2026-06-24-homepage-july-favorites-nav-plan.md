# 2026-06-24 Homepage July Favorites And Pickups Navigation Plan

## Decision

Treat the requested homepage and supermenu update as one coordinated parent
release with four separately planned child features:

1. Fourth of July hero image replacement.
2. Customer Favorites homepage merchandising row.
3. Homepage flow reorder.
4. `Balloons-to-Order` to `Pickups & Deliveries` navigation contract rename.

Implementation is now complete in local source, but this packet remains the
planning/decision record for why the work was split this way. Live release is
not complete.

## Reasoning

The request looks like a landing-page refresh, but it touches multiple customer
contracts:

- the first viewport seasonal image and copy;
- product-card merchandising and customer price expectations;
- homepage proof-band order;
- public header, search, mobile drawer, footer, and verifier language.

Keeping the child features separate lets a future agent implement and verify
each surface without treating the supermenu rename or product pricing as a
simple text edit.

## User Direction Captured

- Use `Pickups & Deliveries` as the customer-facing supermenu label.
- Add Customer Favorites with the four user-provided products, revised on
  2026-06-24 to replace Classic Arch with Minion Bouquet.
- Show prices as `From $XX.XX` because the full product-page configuration
  still owns option/add-on clarity.
- Replace the weak/cartoony Fourth of July image with realistic balloon decor.
- Relevant homepage order should be Reviews, Customer Favorites, Live
  Entertainment, then One of a Kind Designs.

## Implementation Boundary

The planning packet itself did not change source templates, assets, CSS,
product records, ERPNext data, Frappe Cloud, cache, DNS, Stripe, or live site
behavior. The follow-up source implementation on 2026-06-24 changed local app
source, public hero assets, verifiers, and AI-facing docs only. It still did
not mutate ERPNext catalog data, Frappe Cloud, live cache, DNS, Stripe,
provider state, customer communication, or live `https://locallytwisted.com/`
behavior.

## Product Revision

Classic Arch was removed from the Customer Favorites plan because it is
quote-first and does not expose a visible starting price. GL replaced it with
Minion Bouquet, which returns HTTP 200 on live
`https://locallytwisted.com/shop-items/bouquets/minion-bouquet` and exposes
`from $ 35.00`.

The current approved row is Birthday Deliveries, Large head Missionary, Minion
Bouquet, and Bandage "GET WELL" Bouquet (Latex free). Future swaps must still
use product-page/source price truth for `From $XX.XX` labels.

## Source Implementation Update

Local source now implements the approved packet:

- Fourth of July first-slide hero crops were replaced with realistic
  red/white/blue balloon decor from stripped local source image
  `_resources/generated-hero-sources/2026-06-24/july-4-home-hero-source-IMG_4341.jpeg`.
- `Customer Favorites` renders after Reviews and before Live Entertainment.
- Favorite cards use the four approved Website Item routes and
  `get_variant_starting_price` for `From $XX.XX` labels.
- Homepage section order is Reviews, Customer Favorites, Live Entertainment,
  One of a Kind Designs, trusted-client crawl, and closing CTA.
- Active customer-facing shop-category labels now use `Pickups & Deliveries`
  and `All Pickups & Deliveries` across desktop nav, mobile drawer, search
  quick links, footer, shop category rail/select, `/shop` copy, and verifiers.
- Category discovery remains Item Group based and did not become product
  merchandising.

Local proof passed py_compile, nav IA, ecommerce pause, search contract,
container contract, interactive layout, layout-fit, shop smoke through the repo
venv, public asset integrity, and desktop/mobile screenshot inspection.

## Receipts

- Workstream plan:
  `workstreams/homepage-july-favorites-nav-plan-2026-06-24.md`.
- Capability gate passed with:
  `capabilities/INDEX.md`,
  `capabilities/recipes/homepage-launch-proof-contract.md`,
  `capabilities/recipes/frappe-public-nav-business-route-contract.md`,
  `capabilities/recipes/frappe-shop-showroom-symmetry.md`, and
  `capabilities/recipes/codex-browser-verification-surface.md`.
- Local source verification receipts:
  `npm run test:container-contract` `72 passed`,
  `npm run test:interactive-layout` `159 passed, 1 skipped`,
  `npm run test:layout-fit` `312 passed`,
  `.venv/bin/python scripts/verify/smoke_shop.py`, and
  `npm run test:public-assets` `PASS (31 routes, 362 unique local asset URLs)`.

## Decided By

Guiding Light supplied and confirmed the business direction. Codex technical
lead split the work into child features, added the product-price guard, and
prepared the implementation plan on 2026-06-24.
