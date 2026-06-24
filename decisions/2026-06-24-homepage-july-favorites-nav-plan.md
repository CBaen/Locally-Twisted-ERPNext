# 2026-06-24 Homepage July Favorites And Pickups Navigation Plan

## Decision

Treat the requested homepage and supermenu update as one coordinated parent
release with four separately planned child features:

1. Fourth of July hero image replacement.
2. Customer Favorites homepage merchandising row.
3. Homepage flow reorder.
4. `Balloons-to-Order` to `Pickups & Deliveries` navigation contract rename.

Implementation is not started by this packet.

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

This decision packet is planning only. It did not change source templates,
assets, CSS, product records, ERPNext data, Frappe Cloud, cache, DNS, Stripe,
or live site behavior.

## Product Revision

Classic Arch was removed from the Customer Favorites plan because it is
quote-first and does not expose a visible starting price. GL replaced it with
Minion Bouquet, which returns HTTP 200 on live
`https://locallytwisted.com/shop-items/bouquets/minion-bouquet` and exposes
`from $ 35.00`.

The current approved row is Birthday Deliveries, Large head Missionary, Minion
Bouquet, and Bandage "GET WELL" Bouquet (Latex free). Future swaps must still
use product-page/source price truth for `From $XX.XX` labels.

## Receipts

- Workstream plan:
  `workstreams/homepage-july-favorites-nav-plan-2026-06-24.md`.
- Capability gate passed with:
  `capabilities/INDEX.md`,
  `capabilities/recipes/homepage-launch-proof-contract.md`,
  `capabilities/recipes/frappe-public-nav-business-route-contract.md`,
  `capabilities/recipes/frappe-shop-showroom-symmetry.md`, and
  `capabilities/recipes/codex-browser-verification-surface.md`.

## Decided By

Guiding Light supplied and confirmed the business direction. Codex technical
lead split the work into child features, added the product-price guard, and
prepared the implementation plan on 2026-06-24.
