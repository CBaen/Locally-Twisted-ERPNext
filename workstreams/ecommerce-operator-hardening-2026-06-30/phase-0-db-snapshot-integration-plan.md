# Phase 0 DB Snapshot Integration Plan

Date: 2026-06-30

Status: Worker B integration plan only. This file does not contain row values, does not update the authority packet, and does not approve mutation.

Input expected from Worker A:

- `/tmp/lt-large-head-missionary-db-snapshot.json`

Capability gate: PASS

Loaded resources:

- `capabilities/INDEX.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/protective-contracts.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/authority-matrix-template.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/authority-packet-large-head-missionary.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/phase-0-incident-audit-large-head-missionary-2026-06-30.md`
- `scripts/dev/lt_readonly_product_db_snapshot.py`

## Integration Rule

Treat the snapshot as local authenticated read-only DB proof only if the JSON says:

- `read_only` is `true`;
- `contract.erpnext_writes` is `blocked`;
- `contract.cache_clear` is `blocked`;
- `contract.deploy` is `blocked`;
- `contract.payment_provider` is `blocked`;
- `failures` is empty or every failure is copied into the blocker list.

Do not infer live row values from this file. If the snapshot came from the local container, every mapped authority-packet evidence cell must say `Local authenticated read-only DB snapshot`, not `Live proof`.

## Packet Field Mapping

Use these exact JSON paths when the authority-packet owner integrates the snapshot. Do not copy a value unless the JSON path exists in the snapshot.

| Authority Packet Area | Snapshot JSON Path | Fields To Map |
|---|---|---|
| Packet header / environment | top-level keys | `generated_at`, `container`, `site`, `item_code`, `route`, `read_only`, `failures` |
| Product Record Authority - Website Item row | `rows.website_items[]` | `name`, `item_code`, `web_item_name`, `published`, `route`, `item_group`, `website_image`, `slideshow`, `modified`, `modified_by`, `owner` |
| Brand and route authority | `rows.website_items[]`, `rows.product_blueprints[]` | route, item group/category, target Website Item linkage, target item linkage. Keep brand lane unresolved unless a captured row field explicitly proves it. |
| Product Record Authority - Template Item | `rows.template_items[]` | `name`, `item_code`, `item_name`, `item_group`, `variant_of`, `has_variants`, `disabled`, `is_sales_item`, `is_stock_item`, `image`, `modified`, `modified_by`, `owner` |
| Product Record Authority - Variant Items | `rows.variant_items[]` | `name`, `item_code`, `item_name`, `item_group`, `variant_of`, `disabled`, `is_sales_item`, `image`, `modified`, `modified_by` |
| Option axes and values | `rows.item_variant_attributes[]` | `parent`, `idx`, `attribute`, `attribute_value`, `modified`, `modified_by`; group by `parent` to prove which variant rows carry each option value |
| Product Setup authority | `rows.product_blueprints[]` | `name`, `product_name`, `product_slug`, `item_group`, `page_template`, `buying_path`, `publish_status`, `shop_visibility`, `base_price`, `primary_image`, `validation_status`, `ready_for_live`, `target_item_code`, `target_website_item`, `modified`, `modified_by`, `owner` |
| Product Setup active uniqueness | `rows.product_blueprints[]` | Count rows matching the target item, slug/route, and brand lane. If brand lane is absent from the snapshot, uniqueness remains partial. |
| Product Setup price rows | `rows.product_blueprint_prices[]` | All captured child-row fields; map to Product Setup price authority only, not sellable Item Price authority. |
| Product Setup option rows | `rows.product_blueprint_options[]` | All captured child-row fields; map to option classification evidence and unresolved classification blockers. |
| Product Setup add-on rows | `rows.product_blueprint_add_ons[]` | All captured child-row fields; map to paid add-on or no-add-on proof only if the child table is present and complete. |
| Product Setup media rules | `rows.product_blueprint_media_rules[]` | All captured child-row fields; map to selected-option media approval, gallery approval, and held-media decisions. |
| Product Setup gallery rows | `rows.product_blueprint_gallery_images[]` | All captured child-row fields; map to Product Setup gallery authority. |
| Product Setup content rules | `rows.product_blueprint_content_rules[]` | All captured child-row fields; map to title/copy/details/SEO only when the field names are explicit. |
| Sellable price authority | `rows.item_prices[]` | `name`, `item_code`, `price_list`, `price_list_rate`, `currency`, `uom`, `selling`, `valid_from`, `valid_upto`, `modified`, `modified_by` |
| Website slideshow/gallery | `rows.website_slideshows[]`, `rows.website_slideshow_items[]` | All captured fields; map to Website Slideshow and product-page gallery authority. |
| File URL authority | `rows.files_by_url[]` | `name`, `file_name`, `file_url`, `is_private`, `attached_to_doctype`, `attached_to_name`, `modified`, `modified_by` |
| File attachment authority | `rows.files_by_attachment[]` | Same file fields, mapped by attachment target to Website Item, Item, or Product Setup media roles. |
| Rollback target | all `rows.*` groups | Copy the current row identities, timestamps, and fields into rollback-target evidence. Do not convert this into a mutation plan. |
| Blocker list | `failures`, missing row groups, mismatched counts | Every script failure or missing required group becomes an owner-readable blocker with the next proof step. |

## Blockers This Snapshot Can Help Close

Close these only when the snapshot contains the required row group and no contradicting failure:

- Website Item row fields: close local row identity, linked Item, published status, route, image, slideshow, and modification evidence from `rows.website_items[]`.
- Template Item row: close local template status, image, category, variant-template status, and sales/stock flags from `rows.template_items[]`.
- Variant rows: close local existence, enabled/disabled status, image, and option linkage for the expected variant set from `rows.variant_items[]` plus `rows.item_variant_attributes[]`.
- Sellable price rows: close local Item Price existence, price list, currency, UOM, validity, and modified evidence from `rows.item_prices[]`.
- Product Setup row: close local Product Setup identity, target links, state-like fields, base price, primary image, and modified evidence from `rows.product_blueprints[]`.
- Product Setup child rows: close local option, add-on, media-rule, gallery, content-rule, and Product Setup price child-row evidence from the matching child arrays.
- Media file authority: close local File row and attachment evidence from `rows.files_by_url[]` and `rows.files_by_attachment[]`.
- Rollback snapshot: close local pre-change row inventory for captured row groups.

## Blockers That Remain Unless Separate Proof Exists

Do not close these from the local snapshot alone:

- Live row authority for Website Item, Product Setup, Item, Item Price, File, gallery, and child rows.
- Brand lane across all route, media, document, payment, customer-message, portal, and automation surfaces unless the snapshot explicitly captures brand fields.
- Business/source approval for price, option meaning, product scope, and customer-facing claims.
- Public route proof, shop listing proof, selected variant behavior, cart API behavior, checkout summary, Sales Order preservation, or document/payment labels.
- Historical dependency mapping for Sales Orders, invoices, payment records, customer communications, merchandising references, and old public links.
- Root cause of the owner save until `modified`, `modified_by`, and the edited doctype/field are compared with owner action timing.
- Any claim that Product Setup price controls the customer sellable price while Product Setup and sellable Item Price authority are still split.
- Any live mutation readiness; the snapshot is evidence, not approval.

## Local Proof Labels

Use these labels in the authority packet:

- `Local authenticated read-only DB snapshot`: current row facts from `/tmp/lt-large-head-missionary-db-snapshot.json`, produced through read-only local `frappe.get_all` calls.
- `Local public/source comparison`: comparison between local row facts and already captured public/source evidence.
- `Local blocker`: a blocker proven or narrowed by the local snapshot, still requiring live confirmation before live closure.

Never label the local snapshot as:

- `Live proof`;
- `Hosted DB proof`;
- `Release proof`;
- `Payment proof`;
- `Owner approval`.

## Live Proof Labels

Reserve these labels for later authenticated live read-only evidence:

- `Live authenticated read-only DB/Desk proof`: current hosted row facts read without mutation from the target live site.
- `Live public route proof`: fresh public route, shop listing, public API, image, or cart-safe read evidence from the target customer-facing site.
- `Live rollback target`: current live pre-change row snapshot plus rollback procedure and post-rollback proof plan.

Live status remains blocked until live row proof and public proof agree.

## Required Live Read-Only Follow-Up

Authenticated live read-only Desk/DB access is still required to close:

- the exact live Website Item row for the route and linked Item;
- the exact live Product Setup row or rows for target item, slug/route, and brand lane;
- active Product Setup uniqueness by target item, public slug/route, and brand lane;
- live template Item state and all live sellable variant Item rows;
- live Item Variant Attribute rows for the expected option axes;
- live Standard Selling Item Price rows for the template and variants;
- live Product Setup child rows for prices, options, add-ons, media rules, gallery images, and content rules;
- live File rows, privacy flags, attachments, and slideshow/gallery rows;
- `modified`, `modified_by`, and timestamp evidence for the owner-saved backend row;
- historical dependencies that would make rename, disable, delete, collapse, or route changes unsafe;
- a live rollback target before any future mutation.

## Integration Sequence

1. Confirm the JSON exists and is parseable.
2. Check the top-level read-only contract and copy any `failures` into the blocker list.
3. Fill authority-packet cells only from the JSON paths listed above.
4. Keep all values copied from the snapshot labeled as local read-only proof.
5. Compare local Product Setup base price evidence to local sellable Item Price evidence, then record whether the split authority remains, narrows, or is explained locally.
6. Compare local row counts to the packet's public expectations without inventing missing rows. If a count differs, add a blocker instead of choosing the product scope.
7. Add rollback-target inventory from captured local rows, but mark it local-only.
8. Leave live closure blockers in place until authenticated live read-only Desk/DB proof is attached.
9. Do not run cache clear, deploy, record mutation, payment/provider action, or checkout/payment proof as part of this integration.

## Key Plan

The snapshot should turn the current public/source-only packet into a local row-backed packet for Product Setup, Website Item, Item, variants, prices, media, and rollback inventory. It should not be used to claim live authority. The main decision to surface is whether local Product Setup authority and local sellable Item Price authority agree; if they do not, the blocker remains `Not safe to sell yet` until business approval and live read-only proof resolve which source controls customer price.
