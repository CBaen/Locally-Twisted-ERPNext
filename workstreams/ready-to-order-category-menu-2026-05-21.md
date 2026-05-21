# Ready-to-Order Category Menu - 2026-05-21

## Scope

GL reported that the desktop `Ready-to-Order` submenu on
`http://localhost:8081/` was product-heavy and internally worded. The menu was
mostly bouquet products and used backend/ERPNext language. The requested
customer-facing behavior is category navigation: start from the real ERPNext
category source, then let shoppers choose the specific product on the category
page.

This branch changes the public header, search overlay, and mobile drawer only.
It does not change checkout eligibility, product classification, catalog
imports, prices, Stripe, DNS, staging, or live release state.

## Branch And Worktree

- Branch: `codex/ready-order-category-menu`
- Worktree: `C:\Users\baenb\agent-worktrees\builtbycameron-lt\codex-20260521-rom`
- Base: local LT `main` at `3a4d494 allow reviewed external worktrees for LT agents`
- Coordination claim: `codex-20260521-ready-order-menu` in
  `C:\Users\baenb\agent-coordination\LIVE-BOARD.md` and
  `SESSION-REGISTRY.md`

## Source Of Truth

Ready-to-Order menu categories come from live ERPNext `Item Group` children of
`Shop Items` with `show_in_website=1`, ordered by weightage. This matches the
existing `/shop` category source in `website_context.py` and `www/shop.py`.

Live local DB proof on 2026-05-21 returned these 11 category rows:

- Arches -> `shop-items/arches`
- Columns -> `shop-items/columns`
- Bouquets -> `shop-items/bouquets`
- Get-Well Bouquets -> `shop-items/get-well-bouquets`
- Garlands -> `shop-items/garlands`
- Drops -> `shop-items/drops`
- Grab & Go -> `shop-items/grab-go`
- Table Decor -> `shop-items/table-decor`
- Stands & Easels -> `shop-items/stands-easels`
- Deliveries -> `shop-items/deliveries`
- Seasonal & Specialty -> `shop-items/seasonal-specialty`

Proof command shape:

```powershell
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute frappe.client.get_list --kwargs "{'doctype':'Item Group','filters':{'parent_item_group':'Shop Items','show_in_website':1},'fields':['name','item_group_name','route','weightage'],'order_by':'weightage asc, item_group_name asc'}"
```

## Implementation

Changed files:

- `apps/locally_twisted/locally_twisted/navbar_context.py`
  - Removed the Ready-to-Order product-link builder from the nav context.
  - Added `_ready_to_order_category_links()` from `Item Group`.
  - Exposes `lt_nav_ready_to_order_links` and
    `lt_nav_search_ready_to_order_links`.
- `apps/locally_twisted/locally_twisted/templates/includes/navbar/navbar.html`
  - Uses category links in the desktop menu, search overlay, and mobile drawer.
  - Replaces internal copy with customer-facing category copy.
  - Keeps ecommerce pause guards intact.
- `apps/locally_twisted/locally_twisted/public/js/lt-megamenu.js`
  - Filters ready-to-order category search entries by
    `data-lt-search-ready-order-entry`.
- `apps/locally_twisted/locally_twisted/hooks.py`
  - Bumps the `lt-megamenu.js` cache key.
- `scripts/verify/nav_ia.py`
  - Guards the Item Group category contract and rejects the retired product
    selection contract.
- `scripts/verify/smoke_shop.py`
  - Expects category links in Ready-to-Order and rejects product links/internal
    wording.
- `scripts/verify/search_contract.spec.js`
  - Searches for category quick links instead of product quick links.
- `scripts/verify/ecommerce_pause_contract.py`
  - Updates the open-commerce marker to the category search attribute.
- `AGENTS.md`
  - Updates LT's approved worktree root to the shorter
    `C:\Users\baenb\agent-worktrees\builtbycameron-lt`.

## Local Runtime State

Initial finding: the running Docker stack for `http://localhost:8081/` was
bind-mounted to the main LT checkout:

`C:\Users\baenb\projects\Built_by_Cameron\_CLIENTS\locally-twisted\apps\locally_twisted`

For local review, Codex recreated the local compose services with a temporary
override that bind-mounted this branch worktree instead:

`C:\Users\baenb\agent-worktrees\builtbycameron-lt\codex-20260521-rom\apps\locally_twisted`

That made the branch visible on `http://localhost:8081/` without editing the
main checkout. The temporary override file was removed after the containers
were recreated. To restore the local stack to the main checkout, run compose
from the normal `pwd.yml` without the override.

## Verification Receipt

Fresh branch-level checks run from the worktree:

```powershell
python -m py_compile apps\locally_twisted\locally_twisted\navbar_context.py scripts\verify\nav_ia.py scripts\verify\smoke_shop.py scripts\verify\ecommerce_pause_contract.py
node --check apps\locally_twisted\locally_twisted\public\js\lt-megamenu.js
node --check scripts\verify\search_contract.spec.js
python scripts\verify\nav_ia.py
```

All four checks exited 0. These checks proved the branch source contract before
the local Docker stack was repointed.

Rendered local proof after repointing the Docker bind mount to this worktree:

```powershell
python scripts/dev/clear_website_cache.py
python scripts/verify/smoke_shop.py
```

`smoke_shop.py` passed with `=== All shop smoke checks PASSED ===`.

Direct homepage HTML probe after cache clear:

- `Browse ready-to-order by category.` present.
- Category links for Arches, Bouquets, and Seasonal & Specialty present.
- Product links for Unicorn Bouquet and Easter Balloon Cups absent from the
  header HTML.
- `ERPNext`, `Website Item`, and `Backend-approved` absent from the header
  HTML.

## Next Safe Step

For GL local testing:

1. Open `http://localhost:8081/`.
2. Hover/click `Ready-to-Order`.
3. Confirm the submenu reads as category browse, not individual product browse.
4. Confirm the dropdown avoids ERPNext/backend language.

Do not push to live, update Frappe Cloud, change Stripe, mutate DNS, or promote
this branch until GL has tested locally and explicitly approves the release
gate.
