# Lane 03 - Guard Automation Design

Date: 2026-05-21
Status: design only
Owned output: `research/owner-product-operations-break-lab/lanes/03-guard-automation-design.md`

This lane designs the owner product/catalog guard layer. No production files were edited for this lane.

## Source Evidence

- `apps/locally_twisted/locally_twisted/hooks.py` already uses `doc_events`, `has_permission`, `permission_query_conditions`, and an `_append_doc_event` helper so new guards can be added without overwriting existing hooks.
- The current Guest party guard protects required anonymous ecommerce records through `validate`, `before_save`, `on_change`, `on_trash`, and `before_rename` handlers, with a narrow repair flag: `frappe.flags.lt_allow_webshop_guest_party_repair`.
- The marketing access guard blocks records for `LT Marketing Review Access` users through permission hooks plus mutation hooks on sensitive doctypes. Its customer-facing rule is simple: marketing review can inspect the public site, not change ERPNext records.
- `ecommerce_break_lab.py` is intentionally local-only and can use direct SQL for break/restore probes. Direct SQL does not go through document hooks, so a catalog guard cannot claim to stop all break-lab mutations. It must pair runtime hooks with drift verifiers.
- Product setup already has a safer path: `LT Product Blueprint` validates product intent, keeps live approval unavailable, previews local apply plans without writes, and only allows local writes behind an explicit local flag plus confirmation token.
- Classification and price verifiers are narrow contracts:
  - `website_item_classification_contract.py` mutates only `Website Item.lt_product_page_type` and `Website Item.lt_commerce_lane` when explicitly run with `--apply`.
  - price and product verifiers check active variants, price modifiers, page readiness, public price display, cart price paths, and checkout parity.
- Official Frappe docs confirm `doc_events` handlers receive the document and method name, permission hooks can supplement permission checks, and Document API calls can bypass permissions with `ignore_permissions=True`. See [Frappe hooks](https://docs.frappe.io/framework/user/en/python-api/hooks) and [Frappe Document API](https://docs.frappe.io/framework/user/en/api/document).

## Guard Decision

Use document mutation guards for catalog safety, not broad permission removal.

The owner should keep practical access to run the business, read records, use the existing owner home, and create product setup drafts. The dangerous boundary is not viewing catalog records. The dangerous boundary is changing product records, public product pages, prices, variants, and Webshop settings directly from Desk or scripts outside a guarded product workflow.

The guard should therefore:

- Permit owner-safe workflows through `LT Product Blueprint`, local preview, and approved local-only apply flows.
- Block direct edits to live catalog, price, variant, Webshop, and public product page records unless a named guarded context is active.
- Fail loudly with clear owner copy plus developer evidence.
- Detect direct SQL or break-lab drift with verifiers, because document hooks cannot intercept raw SQL.

## Triadic Lens Notes

### Lens 1 - Owner Workflow

Jeff should not need to know ERPNext's Item, Item Price, Website Item, or variant matrix rules. The safe owner path is:

- create or update an `LT Product Blueprint`;
- save as draft or review status;
- preview the apply plan;
- ask for or run a guarded local apply only in local/test when the explicit local gate is enabled;
- keep public publish, live approval, direct price changes, and checkout exposure behind verification.

The guard should explain that the change is protected because it affects public product pages, prices, or checkout. It should point toward Product Setup, not toward technical tables.

### Lens 2 - Catalog Safety

Owner roles currently have powerful access, including product and system permissions. Frappe permission hooks alone are not enough, because internal code can save with `ignore_permissions=True`. Document events are the right runtime boundary for normal Document API writes, deletes, renames, and saves.

The highest-risk records are:

- active `Item` templates and variants;
- `Item Price` rows for selling price lists;
- public `Website Item` records;
- variant axis child rows;
- `Webshop Settings`;
- files and media attached to public products;
- import/seed/purge runners that can change the catalog in bulk.

### Lens 3 - Operations And Break Lab

The break lab needs controlled local damage so guards and verifiers can be proven. It must remain explicitly local-only. Guard design must not pretend document hooks cover direct SQL. Any break-lab action that bypasses hooks must have a restore command and a verifier that detects the broken state before restore and proves recovery after restore.

## Protected DocTypes And Events

Add a new guard module, for example `locally_twisted.owner_catalog_guard`, and append these handlers through the existing `_append_doc_event` pattern in `hooks.py`.

| DocType | Events | Allow | Block |
|---|---|---|---|
| `LT Product Blueprint` | keep current controller validation; no new blocking hook by default | owner creates/edits draft and review records; `operator_notes`; save statuses up to local/staging review | live publish/apply from blueprint controller, already blocked by validation; direct public mutation from blueprint without local flag and token |
| `Item` | `validate`, `before_insert`, `before_save`, `on_update`, `on_change`, `on_trash`, `before_rename` | guarded local blueprint apply; approved import rehearsal; non-public support items only when policy classifies them as not catalog | direct create/update/delete/rename of catalog templates, variants, item codes, item groups, sales flags, UOM, disabled state, variant links, public product naming |
| `Website Item` | `validate`, `before_insert`, `before_save`, `on_update`, `on_change`, `on_trash`, `before_rename` | guarded local blueprint apply creates unpublished draft; classification verifier applies only `lt_product_page_type` and `lt_commerce_lane`; optional future reorder-only change to `weightage` if no other fields change | publish/unpublish, route change, item link change, description/name/image/gallery/page template/classification changes from Desk, delete, rename |
| `Item Price` | `validate`, `before_insert`, `before_save`, `on_update`, `on_change`, `on_trash` | guarded local blueprint apply; approved price repair/import context after dry-run verifier | direct owner edits to `price_list_rate`, `currency`, `price_list`, `selling`, `item_code`, validity dates, delete, insert for active catalog items |
| `Item Attribute` | `validate`, `before_insert`, `before_save`, `on_update`, `on_change`, `on_trash`, `before_rename` | guarded import or blueprint context for new draft/local products | changing active attribute names, numeric flags, value sets, order, delete, rename |
| `Item Variant Attribute` | `validate`, `before_insert`, `before_save`, `on_change`, `on_trash` | guarded blueprint/import context for draft/local products | changing variant axes for active products; adding/removing variant rows directly |
| `Item Attribute Value` | `validate`, `before_insert`, `before_save`, `on_change`, `on_trash` | guarded blueprint/import context | adding/removing/reordering values used by active catalog variants |
| `Webshop Settings` | `validate`, `before_save`, `on_update`, `on_change` | restore expected local settings through guarded break-lab restore context | toggling checkout, prices, guest visibility, login requirement, price list, default customer group, company, payment-affecting settings |
| `File` | `validate`, `before_insert`, `before_save`, `on_trash` when attached to protected catalog doctypes | attach media to `LT Product Blueprint` or unpublished guarded draft product | replacing/deleting media attached to public `Item`, `Website Item`, or item groups outside media review gate |
| `Item Group` | `validate`, `before_insert`, `before_save`, `on_trash`, `before_rename` | approved taxonomy/import context | renaming, deleting, or moving public catalog groups directly |

## Guard Contexts

Do not make the owner role itself a bypass. Bypass must be a short-lived server-side flag set only by vetted code paths.

Recommended context flag:

`frappe.flags.lt_owner_catalog_guard_context`

Allowed values:

| Context | Who sets it | What it may change |
|---|---|---|
| `blueprint_local_apply` | `apply_blueprint_locally` after local conf flag, explicit confirmation token, and blueprint validation | draft/unpublished Item, Website Item, Item Attribute, variant, Item Price records needed for the blueprint |
| `classification_contract_apply` | `website_item_classification_contract.py --apply` after dry-run confirms only two fields | only `Website Item.lt_product_page_type` and `Website Item.lt_commerce_lane` |
| `catalog_import_rehearsal` | import runner after readiness gate, backup/snapshot proof, dry-run report, and explicit operator confirmation | exact import scope named by the readiness gate |
| `price_repair_contract` | price repair verifier/runner after dry-run says intended changes are zero or explicitly approved | exact Item Price rows in the dry-run report |
| `ecommerce_break_lab_restore` | local break-lab restore code only when local break-lab conf flag is enabled | restore expected Webshop settings and local test records |

Never allow a Desk form, browser request parameter, role, or client script to set these flags directly.

## Safe Owner Actions

These should remain allowed:

- read catalog, product, order, customer, and owner action records;
- create and save `LT Product Blueprint` records in draft/review statuses;
- edit blueprint planning fields such as product name, summary, buying path, base price, option rows, add-ons, media rules, and `operator_notes`, subject to existing blueprint validation;
- run blueprint preview methods that do not write business records;
- run local apply only when local configuration and confirmation token are both present;
- use owner call/text/upcoming booking actions;
- view public website and product pages;
- request product changes through a guarded product update workflow.

Optional later safe action:

- allow `Website Item.weightage` reorder-only edits if the guard proves the document is public, the only changed field is `weightage`, no child rows changed, and a product page verifier passes afterward.

## Blocked Mutations

The first implementation should block these even for owner users:

- creating, deleting, renaming, disabling, or changing public catalog `Item` records outside guarded contexts;
- editing variant templates, variants, item codes, variant axes, item groups, stock UOM, sales flags, or product identity fields directly;
- creating, deleting, or changing active selling `Item Price` records directly;
- publishing, unpublishing, deleting, renaming, rerouting, relinking, or changing public `Website Item` records directly;
- changing `Website Item` product classification fields outside the classification contract runner;
- changing images/media attached to public product records outside media review;
- changing `Webshop Settings` fields that affect guest visibility, prices, checkout, company, or default customer group;
- importing, purging, reseeding, or applying catalog repairs without the readiness gate, dry-run report, snapshot/backup proof, and explicit confirmation;
- running break-lab mutators outside local/test conf gates.

## Owner-Facing Copy

Use one consistent title:

`Protected Owner Catalog Guard`

Recommended messages:

- General: "This product change is protected because it can change prices, checkout, or public product pages. Please use Product Setup or ask for a guarded product update."
- Public product record: "This product is already connected to the public shop. Please make the change in Product Setup so the page, price, and checkout checks can run together."
- Price: "Price changes need a guarded product update. That keeps the website, cart, and checkout using the same price."
- Publish/unpublish: "Publishing products from Desk is paused. Keep it as a draft until the product gate passes."
- Webshop Settings: "Store settings are protected. This switch can hide prices, block guests, or change checkout."
- Media: "Public product photos need a guarded media update so the page can be checked after the change."
- Break lab: "Break-lab changes are local-only and require the break-lab flag. They cannot run on staging or live."
- Blueprint safe save: "Saved as a Product Setup draft. Nothing public changed yet."

Developer evidence should include:

- doctype and document name;
- event name;
- changed field names;
- session user;
- active guard context, if any;
- the verifier command that should be run next.

## Verifier Commands

Existing commands to keep in the closeout loop:

```bash
python scripts/verify/product_blueprint_contract.py
python scripts/verify/website_item_classification_contract.py --json
python scripts/verify/product_import_readiness_gate.py --report output/product-import-readiness-gate.json
python scripts/verify/webshop_guest_party_contract.py
python scripts/verify/marketing_review_access_boundary.py --json
python scripts/verify/human_access_silo_matrix.py --json
python scripts/verify/catalog_variant_contract.py
python scripts/verify/product_variant_price_contract.py
python scripts/verify/product_price_modifier_contract.py
python scripts/verify/product_page_price_readiness_contract.py
npm run test:product-prices
npm run test:product-price-display
npm run test:layout-fit
npm run test:interactive-layout
npm run test:public-verify
```

Bench-backed app verifier commands:

```bash
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.verify.product_blueprint_contract.run
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.verify.webshop_guest_party_contract.run
```

New verifier to add before enforcing hooks:

```bash
python scripts/verify/owner_catalog_guard_contract.py --json
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.verify.owner_catalog_guard_contract.run
```

The new verifier should prove:

- expected hook events are registered;
- owner can save a Product Blueprint draft;
- owner can run no-write local apply preview;
- direct owner Item Price edit is blocked and rolled back;
- direct owner Website Item publish/route/classification edit is blocked and rolled back;
- direct owner Item variant axis edit is blocked and rolled back;
- Webshop Settings price/guest/checkout toggles are blocked and rolled back;
- classification apply can change only `lt_product_page_type` and `lt_commerce_lane` under the named guard context;
- blueprint local apply remains blocked without local flag and confirmation token;
- break-lab direct SQL damage is detected by drift/verifier checks after the break and cleared after restore.

Import/destructive gates remain separate and must stay explicit:

```bash
python scripts/verify/catalog_state_snapshot_contract.py
python scripts/verify/catalog_purge_scope_dry_run.py
python scripts/setup/stage_seed_data.py
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend backup --with-files
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.seed.seed_catalog.execute --kwargs "{'dry_run': True}"
```

## Staged Implementation Plan

### Stage 0 - Design Output

Create this lane file only. No production edits.

### Stage 1 - Pure Policy Module

Add a pure policy helper with no hooks enabled yet:

- classify protected doctypes;
- identify public catalog records;
- compute changed fields from current document state;
- classify guard contexts;
- return allow/block decisions and copy.

Unit-test this helper without touching ERPNext records.

### Stage 2 - Advisory Verifier

Add `owner_catalog_guard_contract` as a verifier before wiring enforcement. It should run rollback probes against the local site and initially report what would be blocked.

This avoids surprise owner workflow breakage and gives the team a concrete before/after report.

### Stage 3 - Narrow Enforcement

Wire hooks with `_append_doc_event` for the highest-risk surfaces first:

- `Item Price`;
- `Website Item`;
- `Webshop Settings`;
- `Item`;
- `Item Variant Attribute`.

Keep the first enforcement limited to direct Desk/document mutations and known high-risk fields.

### Stage 4 - Guarded Bypass Contexts

Set short-lived server-side context flags only inside vetted runners:

- blueprint local apply;
- classification apply;
- catalog import rehearsal;
- price repair;
- ecommerce break-lab restore.

Each context must name the exact fields or records it can change. Unknown fields should block.

### Stage 5 - Owner Workflow Proof

Run the owner workflow proof:

- owner can create/edit Product Blueprint draft;
- owner cannot directly alter public price/page/catalog records;
- local apply stays local and unpublished;
- public product and price verifiers still pass.

### Stage 6 - Staging/Launch Gate

Before staging/live enforcement:

- keep ecommerce paused where required;
- keep break-lab flags off;
- prove no direct publish/price/checkout mutation can happen from owner Desk;
- run product, price, classification, public page, and checkout verifier set;
- require explicit approval before enabling any destructive import or live publish path.

## Open Questions For Later Lanes

- Should owner reorder-only edits to `Website Item.weightage` be allowed directly, or should even ordering go through Product Setup?
- Should product media updates use the Product Blueprint as the only safe path, or is a separate media review doctype worth adding?
- Should the guard distinguish Jeff's real owner user from test owner personas, or should it protect every human owner-equivalent role the same way?
- Should a daily drift monitor compare live catalog fields against the last approved snapshot, especially for direct SQL bypass detection?
