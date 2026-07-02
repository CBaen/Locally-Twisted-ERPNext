---
id: ready-order-menu-product-dump
name: Ready-to-Order Menu Product Dump
schema_version: 2.0
level: failure
maturity: candidate
scope: Locally Twisted public Ready-to-Order menu, search overlay, and mobile drawer
currently_true: yes
verification_level: 2
last_verified: 2026-05-21
evidence_quality: direct
tags:
  - Locally Twisted
  - public navigation
  - Ready-to-Order
  - Frappe
  - ERPNext
---

# Ready-to-Order Menu Product Dump

## Symptom

The public `Ready-to-Order` submenu becomes a long product list, often weighted
heavily toward one category such as bouquets, and the copy explains backend
logic instead of helping customers choose a decor category.

## Cause

The nav was sourcing individual Website Item products and checkout eligibility
details. That is too low-level for primary navigation and leaks implementation
language into a customer decision surface.

## Guardrail

Public `Ready-to-Order` chrome must use visible `Item Group` children under
`Shop Items`, ordered by weightage, matching the `/shop` browse source. Keep
product eligibility and checkout detail on product/category pages and backend
contracts, not in the menu.

Forbidden customer-facing menu copy includes:

- `ERPNext`
- `Website Item`
- `Backend-approved`
- backend approval or checkout-lane explanations

## Verification

Use the focused source gates:

```bash
python scripts/verify/nav_ia.py
python -m py_compile apps/locally_twisted/locally_twisted/navbar_context.py scripts/verify/smoke_shop.py scripts/verify/ecommerce_pause_contract.py
node --check apps/locally_twisted/locally_twisted/public/js/lt-megamenu.js
node --check scripts/verify/search_contract.spec.js
```

For rendered proof, first ensure the local Docker stack is using the branch or
worktree that contains the change, then clear website cache and run the focused
browser checks.

## Receipt

2026-05-21 branch `codex/ready-order-category-menu` changed the nav context and
verifiers from product quick links to category quick links. Feature handoff:
`workstreams/ready-to-order-category-menu-2026-05-21.md`.
