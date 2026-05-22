# Sidecar Lens C - Access And Operational Guardrails

Date: 2026-05-21  
Scope: read-only analysis of local Locally Twisted ERPNext/Frappe access, Guest
infrastructure, owner access, customer portal, fake/demo cleanup, and
import/cleanup scripts. No source code, staging, live, provider, DNS, Stripe, or
indexing state was changed.

## Plain-English Read

Guiding Light's concern is correct: a normal human action can look harmless in
ERPNext and still break the public website because ERPNext product records,
Website Items, Item Prices, Webshop Settings, customer portal settings, and
Guest infrastructure are all connected.

The literal risk is not only "someone deletes a product." The bigger risk is
partial drift:

- a page still renders, but cart cannot resolve it;
- a price exists, but not in the public selling price list;
- an Item is disabled, but the public Website Item stays published;
- a customer or Guest-looking record is deleted as "fake data," but Webshop
  needed it as anonymous infrastructure;
- a role or portal setting changes one word from `Supplier` to `Customer` and
  exposes the wrong lane;
- an import/cleanup script bypasses permissions and document hooks.

## Current Verified Local Access State

Verified against the local Docker site `frontend` on 2026-05-21.

Enabled users:

- `Administrator`: System User.
- `cameron@builtbycameron.com`: System User, `LT Owner Home`, support/admin
  role set including `System Manager`.
- `locallytwisted@gmail.com`: System User, `LT Owner Home`, owner/operator role
  set including `LT Owner Access`, `Item Manager`, `Sales Master Manager`,
  `System Manager`, and `Website Manager`.
- `Guest`: Website User, only `Guest` role.

Important interpretation: Jeff currently has enough raw ERPNext role power to
break catalog, Webshop, prices, and global settings. That is why the owner
catalog guard is necessary. The owner should keep practical business access,
but direct catalog mutation needs guardrails.

## Normal Human Activity Blast Radius

| Human action | Current surface | Customer-facing blast radius | Current guard | Recommended physical guard |
|---|---|---|---|---|
| Owner clicks Product Setup / Add Product | `LT Product Blueprint` via `LT Owner Home` | Safe draft path if preview/apply gates hold | Product Blueprint contracts and owner catalog guard context | Keep as the only owner product authoring path |
| Owner clicks Product Prices | `LT Owner Home` shortcut to `Item Price` | Direct price changes can desync page/cart/checkout | Server hook now blocks owner-like direct edit | Hide or replace this shortcut with a guarded Price Review/Product Setup action |
| Owner edits raw `Item`, `Website Item`, `Item Price`, attributes, groups, or `Webshop Settings` | ERPNext Desk lists/forms | Wrong price, orphan page, disabled public product, dead URL, duplicate variants, global checkout/price break | `owner_catalog_guard.py` through `doc_events`; verifier passes | Keep hook, add scheduled catalog drift monitor, and keep owner instruction: do not edit raw catalog tables |
| Owner changes customer, booking, lead, task records | Owner workspace shortcuts | Business workflow impact; less likely to break public product pages | Human access matrix; owner DTO contract for `/owner-actions` | Keep owner actions through DTOs for phone-first workflows; add fake-data cleanup after demos |
| Customer logs in and uses `/me` or `/account/*` | Customer Website User + Customer role | Wrong portal settings can expose native ERPNext routes or supplier lanes | Customer portal inventory passes; signup disabled | Keep invite-only signup, no default portal role, strict portal menu verifier |
| Marketing reviewer logs in | Website User + `LT Marketing Review Access` | Adding Desk/DocPerm would expose backend records | Marketing boundary passes; hooks deny sensitive records | Keep no Desk/no DocPerm, no indexing authority, route-only review |
| Guest browses/shop/cart/checkout | `Guest` user plus Guest Customer/Contact/Portal User chain | Deleting Guest infrastructure breaks public pricing/variant/cart calls | Guest guard passes 11/11 destructive probes blocked | Preserve Guest infrastructure as platform plumbing, not fake customer data |

## Script And Automation Blast Radius

| Script/action | Current behavior | Risk | Recommended guard |
|---|---|---|---|
| `seed_catalog.py` | Dry-run by default; destructive mode requires `destructive=True`, backup path, snapshot path, purge report | Can rewrite Items, Website Items, Item Prices, variants, Files | Keep destructive approval expired daily; require same-day snapshot/backup/dry-run/review |
| `product_import_readiness_gate.py` | Read-only and currently blocked by stale snapshot, stale backup, stale approval | Blocks stale destructive import packet | Keep as release gate before any purge/import |
| `owner_demo_data.py --cleanup` | Deletes marker-scoped synthetic Lead/Customer/Contact/Sales Order data | Marker bug could delete useful local records | Keep marker validation; run owner access and Guest guard after cleanup |
| `book_form_repeat_email_photos_cleanup.py` | Deletes only verifier-owned invalid email namespace unless explicitly widened | Could delete real inquiry evidence if scope widened wrongly | Keep exact namespace guard; cleanup failure should fail verifier |
| `sync_backend_workspaces.py` | Uses `ignore_permissions=True`; owns owner/manager/employee workspace and roles | Can restore risky shortcuts or broad owner roles | Add workspace-shortcut guard to forbid direct `Product Prices` owner shortcut unless intentionally allowed |
| `public_access_break_lab.py` | Local-only mutators for signup, supplier routes, marketing DocPerm breaks | Can intentionally break portal/customer access | Keep local-only, restore functions, and require before/after access matrix |
| Direct SQL / raw DB tools | Bypasses Frappe document hooks | Can bypass owner catalog guard and Guest guard completely | Require backup, dry-run, exact scope report, and post-change drift monitors |

## Current Guard Receipts

Read-only verifier commands run in this pass:

```powershell
python scripts/verify/human_access_silo_matrix.py
python scripts/verify/webshop_guest_party_contract.py
python scripts/verify/owner_catalog_guard_contract.py
python scripts/verify/allow_guest_surface_inventory.py
python scripts/verify/ignore_permissions_justification_lint.py
python scripts/verify/customer_portal_inventory.py --base-url http://localhost:8081 --strict-menu
python scripts/verify/marketing_review_access_boundary.py
python scripts/verify/product_import_readiness_gate.py
npm run test:public-network -- --workers=1
python scripts/verify/catalog_public_sellability_contract.py
```

Results:

- Human access matrix: pass.
- Webshop Guest party: pass, `11/11` destructive runtime probes blocked.
- Owner catalog guard: pass, originally `5/5` probes passed; expanded
  2026-05-22 verifier now passes `19/19` owner-like probes across raw catalog,
  option, category, gallery, Webshop Settings, and guarded Product Setup
  context paths.
- Guest/public endpoint inventory: pass, `12` guest endpoints, `3` public write
  endpoints.
- Permission bypass lint: pass, `157` bypasses scanned, `0` requiring
  attention.
- Customer portal inventory: pass, supplier routes remain Supplier-only;
  invite-only customer portal settings hold.
- Marketing review boundary: pass.
- Product import readiness: blocked as intended because the latest destructive
  snapshot, backup, and approval are stale for 2026-05-21.
- Public network integrity: pass, `31` Playwright route checks.
- Catalog public sellability candidate: pass, `51` published Website Items,
  `30` checkout Website Items, `21` quote-first Website Items, `28` variant
  templates, `3706` active variants, `0` warnings.

## Weak Spots To Fix Next

Resolved later on 2026-05-21:

- Owner Home no longer exposes `Product Prices` as a direct `Item Price`
  shortcut. `backend_workspace_parity.py` now fails if that shortcut returns.
- `allow_guest_surface_inventory.py` now recognizes the newsletter signup
  validation guard marker and passes with `3` known public write endpoints.
- Public write/action allow-guest methods were made explicit. Inquiry submit,
  newsletter signup, checkout preview, guest order submit, and quote acceptance
  are POST-only and live direct-GET probes returned `403`.
- The public catalog sellability drift verifier was promoted into source and
  `package.json`.
- Product Setup coverage was backfilled for all `51` current Website Items.
  The generated records are Draft by default, include exact checkout price rows
  for all `3708` checkout sellable Items/variants, and do not mutate the live
  `Item`, `Website Item`, or `Item Price` records during sync.
- 2026-05-22 triad closeout tightened local apply and sync safety: existing
  public Website Items keep their current published state, local apply cannot
  hide or reroute an existing public Website Item, sync dry runs truthfully
  report would-update rows, and filling missing price rows no longer wipes
  existing option rows.
- A real blast radius was caught and fixed: active backfilled Product Setup
  records changed checkout runtime behavior. Backfilled records now stay Draft
  until reviewed, and `product_setup_catalog_coverage.py` enforces that marker.

Remaining work:

1. Wire the scheduled/pre-release public catalog sellability drift monitor. The
   verifier now exists locally and passed read-only:
   `scripts/verify/catalog_public_sellability_contract.py`. It checks that
   every published Website Item must point to an enabled Item, correct price
   list, known `lt_commerce_lane`, unique active variants, and a route that does
   not collide with protected routes.

2. Keep `product_setup_catalog_coverage.py` in owner-product safety checks so
   Jeff's Product Setup remains available for every storefront product without
   letting Draft records silently take over public checkout.

3. Expand the workspace shortcut verifier if owner/manager/accountant workspaces
   expose any new raw catalog or website settings shortcuts outside the approved
   Product Setup path.

4. Add a cleanup safety gate that must run after any fake/demo cleanup:

```powershell
python scripts/verify/webshop_guest_party_contract.py
python scripts/verify/human_access_silo_matrix.py
python scripts/verify/customer_portal_inventory.py --base-url http://localhost:8081 --strict-menu
npm run test:public-network -- --workers=1
```

5. Keep import destructive mode behind a release gate:

```powershell
python scripts/setup/stage_seed_data.py
python scripts/verify/catalog_state_snapshot_contract.py
python scripts/verify/catalog_purge_scope_dry_run.py
python scripts/verify/product_import_readiness_gate.py --report output/product-import-readiness-gate.json
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend backup --with-files
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.seed.seed_catalog.execute --kwargs "{'dry_run': True}"
```

Only after same-day evidence and explicit approval should destructive local
import be considered. Staging/live require a separate approval path.

## Recommended Physical Guards

- Permissions: keep Manager/Employee/Accountant narrowed by the human access
  matrix; keep owner broad enough for business operation but guarded on raw
  catalog mutation.
- UI hiding: remove raw `Product Prices` from Owner Home and block future raw
  catalog/settings shortcuts unless explicitly approved.
- Server hooks: keep `owner_catalog_guard.py`, `webshop_guest_party_guard.py`,
  and marketing review mutation hooks wired through `hooks.py`.
- Scheduled drift monitors: run Guest infrastructure, owner catalog, human
  access, customer portal, public network, and catalog sellability checks after
  cleanup/import/product changes and before release.
- Backups: require same-day DB/files backup before any destructive cleanup,
  purge, import, or large role/portal rewrite.
- Dry-run gates: require dry-run reports for product import, price repair,
  category/media assignment, customer reminder/send work, and fake-data cleanup.
- Release gates: do not treat local open-mode as staging/live approval; keep
  DNS, Stripe, provider, indexing, and live customer exposure separate.
- Owner instructions: Jeff can use Owner Home, Call/Text, inquiries, bookings,
  customers, tasks, and Product Setup drafts. Jeff should not use raw Item,
  Website Item, Item Price, Item Attribute, Item Group, Webshop Settings, Portal
  Settings, or Website Settings forms directly.

## Exact Paths

- `apps/locally_twisted/locally_twisted/owner_catalog_guard.py`
- `apps/locally_twisted/locally_twisted/webshop_guest_party_guard.py`
- `apps/locally_twisted/locally_twisted/marketing_review_access.py`
- `apps/locally_twisted/locally_twisted/hooks.py`
- `apps/locally_twisted/locally_twisted/seed/sync_backend_workspaces.py`
- `apps/locally_twisted/locally_twisted/seed/seed_catalog.py`
- `apps/locally_twisted/locally_twisted/seed/owner_demo_data.py`
- `apps/locally_twisted/locally_twisted/verify/human_access_silo_matrix.py`
- `apps/locally_twisted/locally_twisted/verify/webshop_guest_party_contract.py`
- `apps/locally_twisted/locally_twisted/verify/owner_catalog_guard_contract.py`
- `apps/locally_twisted/locally_twisted/verify/public_access_break_lab.py`
- `apps/locally_twisted/locally_twisted/verify/book_form_repeat_email_photos_cleanup.py`
- `scripts/verify/human_access_silo_matrix.py`
- `scripts/verify/webshop_guest_party_contract.py`
- `scripts/verify/owner_catalog_guard_contract.py`
- `scripts/verify/allow_guest_surface_inventory.py`
- `scripts/verify/ignore_permissions_justification_lint.py`
- `scripts/verify/customer_portal_inventory.py`
- `scripts/verify/marketing_review_access_boundary.py`
- `scripts/verify/product_import_readiness_gate.py`
- `scripts/verify/catalog_public_sellability_contract.py`
- `capabilities/recipes/erpnext-webshop-guest-party-contract.md`
- `capabilities/failures/webshop-guest-party-cleanup-regression.md`
- `capabilities/recipes/customer-client-portal-contract.md`
- `capabilities/recipes/erpnext-external-review-access.md`
- `capabilities/recipes/erpnext-owner-business-access-api.md`
- `workstreams/user-access-audit-2026-05-15.md`
