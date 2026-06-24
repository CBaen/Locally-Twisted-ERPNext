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
- Add Customer Favorites with the four user-provided products.
- Show prices as `From $XX.XX` because the full product-page configuration
  still owns option/add-on clarity.
- Replace the weak/cartoony Fourth of July image with realistic balloon decor.
- Relevant homepage order should be Reviews, Customer Favorites, Live
  Entertainment, then One of a Kind Designs.

## Implementation Boundary

This decision packet is planning only. It did not change source templates,
assets, CSS, product records, ERPNext data, Frappe Cloud, cache, DNS, Stripe,
or live site behavior.

## Hard Stop

Classic Arch is currently quote-first on the live product page and does not
expose a visible starting price. The recommended path is product-page/source
parity first. Do not show a homepage `From $XX.XX` for Classic Arch unless
product-page/source parity exists or GL explicitly approves a homepage-only
exception with the amount and reason recorded.

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
lead split the work into child features, added hard stops, and prepared the
implementation plan on 2026-06-24.
