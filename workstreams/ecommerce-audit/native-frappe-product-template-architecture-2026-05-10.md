# Lane D — Native Frappe Product Template Architecture Designer

## Status block

- **Lane:** D — Native Product Template Architecture Designer.
- **Environment/auth context:** local repository/source inspection only on `main` at `264c6553acd5708ecdb498cb6fa6a5c594260abc`; no browser clicks; no ERPNext admin/operator session; no customer/live surface interaction. Destination stack is treated as local/test unless Lane C proves otherwise. Compose source says the image is `${CUSTOM_IMAGE:-frappe/erpnext}:${CUSTOM_TAG:-$ERPNEXT_VERSION}`; AGENTS.md documents current intended stack as ERPNext/Frappe v15.105.0, apps `frappe`, `erpnext`, `payments`, `webshop`, `locally_twisted`.
- **Sources inspected:** `AGENTS.md`; `capabilities/recipes/erpnext-ecommerce-receiving-architecture.md`; `workstreams/ecommerce-audit-dispatch-prompts-2026-05-10.md`; `Locally-Twisted-Backend/frappe_docker/compose.yaml`; `package.json`; `apps/locally_twisted/locally_twisted/product_page_runtime.py`; `product_page_labels.py`; `product_options.py`; `product_quote_request.py`; `product_quote_runtime.py`; `catalog_contract/models.py`; `catalog_contract/source_builder.py`; `catalog_contract/addon_rules.py`; `catalog_contract/dependency_rules.py`; `seed/sync_commerce_rules.py`; `seed/sync_contact_intake_backend.py`; `templates/generators/item/item_details.html`; `item_configure.html`; `item_quote_first.html`; `www/book.py`; source audit reports under `audits/catalog-import-audit-2026-05-08/`. A local `.env` was opened accidentally during version lookup; no secrets from it are used, cited, or reproduced here.
- **Commands/actions run:** `git rev-parse --abbrev-ref HEAD`; `git rev-parse HEAD`; `git status --short`; Bash `Get-ChildItem`/`rg` source searches; read-only file reads; created this artifact directory/file only.
- **Records created/cleaned:** none. No ERPNext/catalog_data records, carts, orders, quotes, invoices, emails, payments, products, or catalog_data rows were created or mutated.
- **Key findings:** smallest safe architecture is a native Webshop/ERPNext extension layer with two reusable product-page classes, versioned line payloads, quote-first handoff, dependency matrices, approved add-on contracts, media classification staging, and explicit import/reopen gates. Current source code already contains a significant first slice, but this lane did not run runtime verifiers, so runtime survival claims remain `[PENDING-LANE-C]` unless directly evidenced by code.
- **Blockers:** Lane A/C/E artifacts are not present in `workstreams/ecommerce-audit/` at time of writing; source meaning, browser/cart/order proof, and docs convergence need reconciliation before Lane F or implementation decisions. Source-derived counts from older audit artifacts are useful but labeled `[PENDING-LANE-A]` until Lane A refreshes them.
- **Confidence:** medium-high for architecture shape from current code; medium for import/readiness sequencing; low for runtime end-to-end survival until Lane C inspects backend records.

## Recommendation in one sentence

Use ERPNext native `Item`/`Website Item`/`Item Price`/`Sales Order`/`Quotation`/`Sales Invoice` as the accounting and catalog spine, but make Locally Twisted product-page meaning live in a small, code-owned `locally_twisted` contract layer: product-page class fields, versioned payload JSON on every downstream line, executable dependency/add-on/pricing services, quote-first bridges, and fail-loud verifiers.

## Recommended product-page classes

Keep the class list intentionally small:

| Class | Storage value | Buying path | Use for | Default failure behavior | Evidence |
|---|---|---|---|---|---|
| Ready-to-order page | `simple_product` | `checkout` | Products with few required axes, approved checkout prices, no unapproved customization, and only checkout-approved add-ons. | Block checkout if schema/add-on/price/line storage is incomplete. | `product_page_labels.py`; `product_page_runtime.py`; `item_details.html`; `item_configure.html`. |
| Custom quote page | `complex_custom_product` | `quote_first` | Multi-axis decor, color recipes, setup-sensitive products, unapproved add-ons, or anything whose business promise cannot safely become a paid cart line yet. | Route to product quote handoff and Lead/Quotation review; do not create payment path. | `product_quote_request.py`; `product_quote_runtime.py`; `item_quote_first.html`; `www/book.py`. |
| Needs review | `needs_review` | `needs_review` | Missing, stale, or ambiguous import/template assignments. | Customer-safe quote/request-review block, not paid checkout. | `product_page_runtime.py` conservative fallback. |
| Hybrid | `hybrid` | `hybrid` | Reserve only for a future explicitly proven family that can support both checkout and quote. | Treat as disabled until a verifier exists. | Storage option exists in `product_page_labels.py`, but no inspected runtime proof here. |

[PENDING-LANE-A] Existing 2026-05-08 source audit classified 53 source products as 15 Ready-to-order and 38 Custom quote. Treat those as staging counts, not final import truth, until Lane A refreshes catalog_data/source meaning.

## Required native/custom fields, child tables, and DocTypes

### Already evidenced in current source

- `Website Item`
  - `lt_product_page_type` (`Page Template`) — reusable logic class, not product family.
  - `lt_commerce_lane` (`Buying Path`) — checkout vs quote-first vs review.
  - Evidence: `seed/sync_commerce_rules.py`, `product_page_runtime.py`.
- Line payload fields on `Quotation Item`, `Sales Order Item`, and `Sales Invoice Item`
  - `custom_lt_product_template_item`
  - `custom_lt_product_page_type`
  - `custom_lt_configuration_version`
  - `custom_lt_configuration_summary`
  - `custom_lt_configuration_json`
  - Evidence: `seed/sync_commerce_rules.py`, `product_page_runtime.py`, `product_quote_runtime.py`.
- Quote-first bridge fields on `Quotation`
  - `custom_lt_source_lead`, `custom_lt_product_template_item`, `custom_lt_product_page_type`, `custom_lt_commerce_lane`, `custom_lt_configuration_version`, `custom_lt_product_quote_summary`, `custom_lt_product_quote_payload`, `custom_lt_product_quote_status`, approval-token fields.
  - Evidence: `product_quote_runtime.py`, `seed/sync_commerce_rules.py`.
- Quote-first fields on `Lead`
  - `custom_lt_product_template_item`, `custom_lt_product_page_type`, `custom_lt_product_quote_summary`, `custom_lt_product_quote_payload`, `custom_lt_product_quote_items`.
  - Evidence: `seed/sync_contact_intake_backend.py`, `www/book.py`.
- Child DocType `LT Product Quote Item`
  - `product_page`, `product_page_type`, `commerce_lane`, `summary`, `payload_json`, `status`.
  - Evidence: `seed/sync_contact_intake_backend.py`.
- Code-owned review/add-on Items
  - `LT-PRODUCT-QUOTE-REVIEW` for quote-first draft Quotation rows where template Items cannot be sold directly.
  - `ADDON-FOIL-NUMBER` for the first confirmed checkout add-on.
  - Evidence: `product_quote_runtime.py`, `product_page_runtime.py`, `seed/sync_commerce_rules.py`.

### Recommended additions before broad import/reopen

Do not add these blindly; implement only behind verifiers and after Lane A/C/E reconciliation.

1. **Product-page contract staging DocType or generated artifact**
   - Purpose: store/import-review rows keyed by source slug, ERPNext `Website Item`, page class, commerce lane, required axes, customization axes, add-on families, dependency matrices, price source, media status, and source evidence id.
   - Smallest safe version: keep as generated JSON/report until import decisions stabilize; promote to DocType only if operators need Desk review.
2. **Add-on approval records**
   - Purpose: separate approved checkout add-ons from quote-only source axes.
   - Fields: key, label, source attribute, eligible product pages/groups, pricing rule, target Item, quantity rule, customer label, fulfillment notes, approval status, approved by/on.
   - Current source has hard-coded `foil_number`; future add-ons should not be added as more ad hoc constants once a second family is approved.
3. **Media classification records/artifacts**
   - Purpose: classify source extra images as parent-gallery, variant image, category/reference, or hold.
   - Current ERPNext native destinations can be `Website Item.website_image`, `Item.image`, and Website Slideshow/Website Slideshow Item if approved; the code currently exposes variant images as a temporary gallery helper.
4. **Price review packet / approved price source artifact**
   - Purpose: preserve whether a price came from source resolver, source base price, current ERPNext snapshot, or human-approved override.
   - Must block public price promises if status is `business_review_required`.

## Versioned payload schema boundaries

Use one public/cart/quote configuration schema boundary now: `lt-product-config-v1` (`CONFIG_VERSION` in `product_page_runtime.py`). Every consumer must reject unknown/old/malformed payloads loudly.

### Checkout line payload shape

Owner: `product_page_runtime.sales_order_line_configuration_fields()`.

Required fields:

- `schema_version`
- `item_code` — resolved variant or sold Item.
- `website_item_code` — parent/template Website Item.
- `product_page_type`
- `commerce_lane`
- `selected_options` — required variant/options that produced the sold Item.
- `add_ons` — approved checkout add-ons only, without trusting client price.
- `customizations` — must be empty for paid checkout until explicitly priced/approved.
- `source` — `lt_product_page_runtime`.

Persistence boundary: same JSON/version/summary fields on Sales Order Item and Sales Invoice Item. [PENDING-LANE-C] Runtime proof must inspect created Sales Order and invoice rows before saying customer intent survived.

### Add-on line payload shape

Owner: `product_page_runtime.sales_order_add_on_lines()`.

Required fields:

- `schema_version`
- `item_code` — add-on Item such as `ADDON-FOIL-NUMBER`.
- `parent_item_code`
- `website_item_code`
- `product_page_type`
- `commerce_lane`
- `add_on_key`, `add_on_label`, `selected_value`, `quantity_per_parent`, `parent_qty`
- `source` — `lt_product_page_add_on`.

Do not accept client-supplied add-on price; the server reads `Item Price` from ERPNext.

### Quote-first payload shape

Owners: product page JS in `item_quote_first.html`, server normalization in `product_quote_request.py`, Lead creation in `www/book.py`, Quotation bridge in `product_quote_runtime.py`.

Required fields:

- `schema_version`
- `source`
- `website_item_code`, `web_item_name`, `item_group`, `route`
- `product_page_type`, `commerce_lane`
- `summary`
- `selected_options`
- `add_ons`
- `customizations`
- `color_recipes`
- `needs_operator_review`

Quote-first records must never imply paid success. Draft Quotation is an internal review packet; acceptance may create a draft Sales Order only after human approval and with no invoice/payment side effects. [PENDING-LANE-C]

## Pricing and dependency service boundaries

### Pricing boundary

- ERPNext `Item Price` remains the source for actual checkout rates.
- Server-side checkout code must calculate base line + add-on line totals; browser prices are display hints only.
- Add-on pricing is server-owned through `ADD_ON_ITEM_CONTRACTS` + ERPNext `Item Price` lookup.
- Candidate import prices need an explicit source label: source resolver, source base price, live ERPNext snapshot, or approved override.
- [PENDING-LANE-A] The 2026-05-08 price enrichment report says all 290 expected sale units had candidate coverage, but 273 live-snapshot units still needed business review. Refresh before import decisions.
- [PENDING-LANE-C] Runtime cart/checkout totals must be verified against backend Sales Order rows, not just page display.

### Dependency boundary

- Source `valid_variants` should become dependency matrices over required axes only.
- Color/customization axes and quote-only add-on axes must be removed from required SKU matrices so ERPNext does not explode or flatten business meaning.
- Runtime selection narrowing should use `available_options_for_selection()` and fail for unknown/impossible axes.
- [PENDING-LANE-A] Existing audit says 36 products had source-backed dependency matrices and 273 required-axis valid combinations preserved; refresh in Lane A.
- [PENDING-LANE-C] Product pages need browser proof that customers cannot select impossible combinations and then still add a stale cart line.

## Media destination strategy

Use a staged, evidence-first media path:

1. **Primary product image** → ERPNext `Website Item.website_image` / native product image display.
2. **Variant-specific image** → ERPNext `Item.image` on active variant Items, used only when source or live data indicates variant-specific media.
3. **Parent gallery image** → approved Website Slideshow/Website Slideshow Item or a small LT gallery destination if native slideshow cannot meet product-page UX.
4. **Reference/category/marketing image** → hold outside product purchase promises unless assigned to a page/category with a reason.
5. **Unknown extra image** → `hold_until_classified`.

[PENDING-LANE-A] The 2026-05-08 media report found 53 source primary images, 95 unclassified source extra images, live primary images on 53 Website Items, no Website Slideshow records, and variant images on 1,751 active variants. Treat this as staging evidence until refreshed.

Do not block every variant for lacking a variant image; only flag missing variant media where source says a variant has or should expose an image.

## Add-on approval workflow

Smallest safe workflow:

1. Source mapper identifies add-on-looking axes and affected products.
2. Add-on review packet defaults each family to `quote_only_until_approved`.
3. GL/Locally Twisted decides for each value: paid add-on, included choice, quote-only prompt, bundle/separate Item, inventory-managed item, or drop.
4. Architecture owner creates a code-owned add-on contract or DocType row with:
   - normalized key;
   - customer label/help;
   - eligible Website Items/groups;
   - target ERPNext Item;
   - server price source;
   - quantity rule;
   - fulfillment/operator notes;
   - verifier coverage.
5. Product UI renders only approved checkout add-ons on checkout-class pages.
6. Cart/checkout creates base line + priced add-on line(s), preserving selected value in both payload and customer-facing label.
7. Unsupported/review-only add-ons fail as quote-required, not as free or silently dropped options.

Current direct evidence:

- `foil_number` is the only inspected confirmed checkout add-on contract.
- `Add ons`, `Plush add ons`, `Orbz toppers`, and `Add Bouquet` are known review-only families in `product_page_runtime.py` / `addon_rules.py`.
- The add-on approval packet says 4 review axes affect 9 products and approves 0 for checkout. [PENDING-LANE-A]

## Quote-first vs checkout decision tree

Use this decision tree at import/runtime:

1. **Missing or unknown template/lane?** → `needs_review`; no checkout.
2. **Malformed/stale payload?** → fail loudly; ask customer to reselect options.
3. **Any unapproved customization axis, balloon color recipe, setup/timing dependency, or source review warning?** → `complex_custom_product` / `quote_first`.
4. **More than one required axis or source dependency not executable?** → `complex_custom_product` / `quote_first` unless a runtime dependency verifier proves safe checkout.
5. **Known checkout category with at most one required axis, complete Item Prices, approved media, approved add-ons only, and runtime verifier coverage?** → `simple_product` / `checkout`.
6. **Unapproved add-on selected on a checkout page?** → fail as quote-required.
7. **Quote-first accepted by customer?** → create/reuse reviewed draft Quotation/Sales Order only through guarded approval path; no email/payment/invoice unless the matching verifier and operator gate say so. [PENDING-LANE-C]

## Migration/import staging plan

1. **Freeze source evidence**
   - Lane A refreshes catalog_data/source product classes, axes, valid combinations, add-ons, pricing/media facts, quote behavior, and unknowns.
2. **Build/refresh contract staging artifact**
   - One row per source product: slug, ERPNext target, class, lane, required axes, customization axes, add-ons, dependency matrices, media plan, price plan, blockers.
3. **Dry-run import gates**
   - Verify every product has a class/lane.
   - Verify every required axis has a destination and dependency matrix where needed.
   - Verify every checkout-class sale unit has approved Item Price.
   - Verify every customer-facing add-on is approved and priced.
   - Verify every media asset is assigned or held.
4. **Import/update in small family batches**
   - Ready-to-order bouquet proof batch first.
   - One quote-first complex family second.
   - No destructive purge/reimport without rollback anchor `lt-ecommerce-audit-pre-dispatch-20260510-0841` and fresh generated reports.
5. **Runtime proof per batch**
   - Product page controls.
   - Cart line identity.
   - Checkout payload.
   - Sales Order Item rows.
   - Invoice copy if payment/invoice path is in scope.
   - Quote-first Lead/Quotation handoff.
   - Customer-facing labels.
6. **Public reopen decision**
   - Only after Lane C proves representative journeys and Lane E reconciles docs/source/live gaps.

## Rollback and fail-loud gates

Rollback anchor for this workstream remains `lt-ecommerce-audit-pre-dispatch-20260510-0841`; rollback package is `/home/guidingl/.openclaw/workspace/reports/rollback/lt-ecommerce-audit-pre-dispatch-20260510-0841`.

Required fail-loud gates before implementation/import claims:

- Product page class/lane verifier: no raw snake_case operator labels, no missing fields.
- Dependency verifier: unknown/impossible combinations raise errors.
- Add-on verifier: only approved add-ons enter checkout; review-only source families route quote-first.
- Price verifier: every checkout sale unit and add-on has server price; no `$0` unless intentionally review-only/internal.
- Cart verifier: same SKU + different configuration creates separate line identities.
- Checkout verifier: Sales Order Item rows preserve configuration JSON and add-on lines.
- Invoice verifier: Sales Invoice Item rows copy line configuration where invoice path is safe.
- Quote verifier: product quote payload reaches Lead child row and draft Quotation; no payment side effects.
- Quote acceptance verifier: approved quote creates draft Sales Order only, preserving payload and audit fields.
- Media verifier: primary/variant/gallery assignments match approved classification.
- Public mode verifier: ecommerce pause/reopen mode matches launch decision.

Known verifier entrypoints from source/capability docs include:

```bash
python scripts/verify/product_page_runtime_contract.py
python scripts/verify/product_add_on_dependency_contract.py
python scripts/verify/product_page_dependency_contract.py
python scripts/verify/product_page_price_enrichment_contract.py
python scripts/verify/product_page_price_review_packet.py
python scripts/verify/product_page_media_visibility_contract.py
python scripts/verify/product_page_media_classification_packet.py
python scripts/verify/cart_checkout_contract.py
python scripts/verify/product_quote_customization_contract.py
python scripts/verify/product_quote_operator_review_contract.py
python scripts/verify/product_quote_acceptance_contract.py
python scripts/verify/product_quote_customer_delivery_contract.py
python scripts/verify/product_quote_operator_send_control_contract.py
npm run test:checkout-experience
npm run test:quote-accept-experience
npm run test:product-quote-first
npm run test:ecommerce-full
```

This lane did not run those commands; they are required gates, not results.

## What remains business-review required

- [PENDING-LANE-A] Final source product classification and unknowns from current catalog_data witness.
- [PENDING-LANE-A] Which source add-on families/values become paid checkout, quote-only, bundled separate Items, or dropped.
- [PENDING-LANE-A] Which color/customization axes are customer-selectable vs operator notes only.
- [PENDING-LANE-A] Final business approval for live-snapshot price candidates and any source-base fallback prices.
- [PENDING-LANE-A] Source extra-image classification: gallery vs variant vs category/reference vs hold.
- [PENDING-LANE-C] Whether customer intent survives actual local/test product-page → cart → checkout → Sales Order → invoice/receipt journeys.
- [PENDING-LANE-C] Whether quote-first product pages preserve structured choices through contact Lead, draft Quotation, operator review, customer quote delivery, and accepted-quote draft Sales Order.
- [PENDING-LANE-E] Any official catalog_data/ERPNext docs mismatch that changes variant/add-on/cart/order semantics.
- Payment/bank/finance readiness if public paid checkout is reopened; current capability notes treat finance as deferred, but launch/payment decisions need explicit owner approval.

## Implementation boundary

No implementation edits are recommended from Lane D alone. The next safe step is Lane F synthesis after Lane A-E artifacts exist, then a smallest-slice implementation plan that changes only the first unresolved gap with a verifier attached.
