# Lane 2 - Owner Product Operations Breakage Probes

Date: 2026-05-21

Scope: adversarial local-only probes for owner-like product/catalog mutations that can break the public storefront. This lane did not edit production source files, did not touch staging/live, and did not change provider, DNS, Stripe, Frappe Cloud, or public indexing state.

Owned output: `research/owner-product-operations-break-lab/lanes/02-breakage-probes.md`

## Current Local State

Verified against the local Docker ERPNext site during this lane:

| Surface | Value |
|---|---:|
| Local URL | `http://localhost:8081` |
| Backend container used | `locally-twisted-erpnext-v15-backend-1` |
| Frappe site | `frontend` |
| Item count before/after probes | `10685` / `10685` |
| Website Item count before/after probes | `51` / `51` |
| Item Price count before/after probes | `10666` / `10666` |
| Item Variant Attribute count before/after probes | `32049` / `32049` |
| Disposable probe prefix count after cleanup | `0` Items, `0` Website Items, `0` Item Prices |
| Webshop Settings before/after | unchanged: enabled, show price, checkout, variants on; guest prices visible; `price_list=Standard Selling` |

Probe records used only the disposable prefix `LT-BREAKLAB-02-*`. Each committed probe was cleaned up immediately or during final cleanup. Final route checks for the disposable routes returned `404`.

## Source Facts Used

- `/shop` source: `apps/locally_twisted/locally_twisted/www/shop.py` lists `Website Item` rows where `wi.published = 1`, left-joins `Item Price` on `Standard Selling`, and only excludes variant rows. It does not filter disabled `Item` rows.
- Cart source: `apps/locally_twisted/locally_twisted/api/cart.py` resolves a cart line from active `Item`, published parent `Website Item`, explicit checkout contract, and `Standard Selling` `Item Price`. Missing pieces return `missing` reasons such as `unavailable` or `unpriced`.
- Product page source: `apps/locally_twisted/locally_twisted/overrides/website_item.py` uses Webshop Settings, guest-safe price lookup, and Website Item context. It can render a route even when downstream cart resolution will fail.
- Variant source: `webshop.webshop.variant_selector.item_variants_cache.ItemVariantsCacheManager` builds selector choices from active variants. Attribute edits need cache rebuild and duplicate-combination checks.

## Triadic Read

### Lens 1: Owner Intent

Most dangerous owner actions are normal shop operations: drafting, publishing, hiding, repricing, renaming URLs, reorganizing categories, removing options, or fixing variant labels. These should be allowed only when the storefront can either stay correct or fail loudly.

### Lens 2: Storefront Breaker

The storefront breaks when public visibility and sellability drift apart. The worst pattern is "page still renders, cart later rejects." Customers see a product page or listing, then hit missing price, unavailable item, wrong option, or dead old URL.

### Lens 3: Guard Designer

Owner actions should not be globally blocked. They need state-specific guards:

- Draft actions are allowed when unpublished.
- Public product actions need a publishability gate.
- Variant actions need exact-one-match and cache rebuild proof.
- Global Webshop Settings changes need a separate break-glass gate because they affect every product.

## Probes Run And Restored

| Probe | Mutation type | Restore/final state |
|---|---|---|
| Item without Website Item | Created `LT-BREAKLAB-02-NOWI` Item only | Deleted disposable Item |
| Website Item without Standard Selling price | Deleted probe Item Price while Website Item stayed published | Recreated Standard Selling price before next probe |
| Price on wrong price list | Replaced Standard Selling price with Standard Buying buying price | Deleted wrong price and recreated Standard Selling price |
| Disabled Item with published Website Item | Set `Item.disabled=1` on disposable product | Restored `disabled=0` |
| Unpublished Website Item | Set `Website Item.published=0` | Restored `published=1` |
| Edited route | Changed route from old slug to renamed slug | Restored original route |
| Changed Item Group | Moved disposable Item and Website Item from `Bouquets` to `Services` | Restored `Bouquets` |
| Deleted Website Item | Deleted Website Item while Item and price remained | Final cleanup removed remaining disposable Item and price |
| Orphan Website Item | Created Website Item for a missing Item code; follow-up confirmed Administrator can insert it without `ignore_permissions` | Final cleanup removed orphan Website Item |
| Disabled one variant | Disabled `LT-BREAKLAB-02-VAR-MED` under a published template | Final cleanup removed disposable template and variants |
| Duplicate variant attributes | Edited two variants to share the same `Bouquet Size` value | Final cleanup removed disposable template and variants |

## Breakage Matrix

| Action | Expected owner desire | Observed/likely break | Severity | Should block/allow/guard | Test needed |
|---|---|---|---|---|---|
| Create Item without Website Item | Add product draft or internal item before public setup | Observed: Item exists, `/shop?q=...` does not show it, cart API returns `missing: unavailable`. This is safe as draft but confusing if owner thinks it is live. | Medium | Allow as draft. Guard any "publish/sell" state until Website Item exists. | Draft vs public verifier: sellable Item must have exactly one Website Item before any checkout/public label. |
| Create Website Item without existing Item | Publish product page before linked Item exists | Observed: Administrator document insert without `ignore_permissions` allowed orphan Website Item. The orphan route returned `200` and product name, final cleanup route returned `404`. Cart would not resolve because Item is missing. | Critical | Block. A public Website Item must not save or publish unless linked Item exists and is active. | Orphan Website Item guard: fail if published Website Item item_code does not exist in Item. Include route crawl. |
| Publish Website Item without Standard Selling Item Price | Make page visible before pricing is complete | Observed: product route stayed `200`, `/shop` still listed the product, no `$12` price string, cart API returned `missing: unpriced`. | High | Guard. Allow unpublished draft, block public checkout lane. | Publishability gate: published checkout Website Item requires Standard Selling selling Item Price for sellable item or every active variant. |
| Move price to wrong price list | Use buying/internal price list or change product price list by mistake | Observed: with only `Standard Buying` price, route and `/shop` still rendered product but cart API returned `missing: unpriced`. | High | Guard. Price records can exist, but public checkout requires Standard Selling parity. | Price-list contract: every public checkout item/variant must resolve in Webshop Settings price list and LT cart `Standard Selling` contract. |
| Disable Item while Website Item remains published | Temporarily retire backend item | Observed: product route stayed `200`, `/shop` still listed product with price, cart API returned `missing: unavailable`. | Critical | Block or auto-unpublish. Disabled Item must not remain public. | Public-disabled guard: no published Website Item may point to `Item.disabled=1`; `/shop` query must filter or verifier must fail. |
| Unpublish Website Item | Hide product from store while preserving backend record | Observed: route returned `404`, `/shop` no longer showed product, cart API returned `missing: unavailable`. | Low/Medium | Allow, but require old-cart/customer message path. | Hidden product cart test: direct cart line for unpublished item returns customer-safe unavailable notice and removes localStorage line. |
| Delete Website Item while Item and price remain | Remove public product record but keep accounting/catalog item | Observed: route `404`, `/shop` absent, Item still existed, Item Price still existed, cart API returned `missing: unavailable`. | Medium/High | Guard. Allow only with archive/redirect decision and cart fallout check. | Website Item deletion preflight: identify old route, existing carts/orders/links, and restore recipe. |
| Edit Website Item route/slug | Clean up URL after publish | Observed: old route immediately `404`; new route `200`; cart API returned new route. Existing links become dead unless redirected. | High | Guard. Allow only with redirect/alias or explicit broken-link acceptance. | Route-change test: old route redirects to new route or explicit no-redirect decision is recorded; sitemap/canonical update proof. |
| Change Item/Website Item group | Reorganize public categories | Observed: route still `200`, `/shop` search still listed product, cart still worked, but item group changed to `Services` while route remained under `/shop-items/bouquets/...`. Likely category/nav/breadcrumb mismatch. | Medium | Guard. Allow only if group is public-shop-approved and route/category contract stays coherent. | Item Group move verifier: group must be under `Shop Items` or explicitly allowed; route prefix/category nav/breadcrumb must match. |
| Disable one variant under a published template | Remove one size/design while keeping product live | Observed: selector options collapsed to only active Small value; Medium selection exact match empty; cart for disabled Medium returned `missing: unavailable`; product route stayed `200`. | Medium | Allow with guard. This is acceptable if stale carts fail loudly and selector cache rebuilds. | Variant disable test: active selector values exclude disabled variant; old cart line returns unavailable; ItemVariantsCacheManager cache is rebuilt. |
| Edit variant attributes to duplicate another variant | Correct an option value by hand | Observed: normal save succeeded; selector for Small returned two exact matches; product_info used the first variant price `$11` while the duplicate variant cart line still resolved at `$18` with the same option label. This creates ambiguous customer choice and price drift. | Critical | Block. Variant combinations must be unique per template. | Variant uniqueness guard: for each template, active variants must have unique required attribute tuple; selector exact_match length must be `0` or `1`, never `>1`. |
| Modify template variant attribute list | Owner changes which option axes appear | Not run. On real templates this can erase or reshape customer selectors across many variants and requires source-catalog comparison. | High | Guard. Block on real products until source manifest and variant cache proof exist. | Template-axis verifier: template attributes equal expected required axis set; active variants include only valid axes; cache rebuild proof. |
| Change Webshop Settings `price_list` | Owner changes storefront price list globally | Not run because this is global shared local state and other agents are active. Likely break: product page and cart price sources diverge from LT `Standard Selling` cart contract. | Critical | Block unless break-glass gated. | Settings mutation gate: after any price_list change, run product page, listing, variant selector, cart, checkout price parity against sampled products. |
| Toggle Webshop Settings `show_price` or `hide_price_for_guest` | Hide prices until checkout or for guests | Not run due global shared local state. Likely break: public product pages/listings look unpriced while cart/checkout behavior may still have server prices. | High | Guard. Allow only for deliberate quote-first campaign, not checkout products. | Guest price visibility test: product, listing, variant selector, cart, checkout copy all agree on whether price is visible. |
| Toggle Webshop Settings `enable_checkout` | Temporarily pause checkout | Not run due global shared local state. Likely break: product pages may say Add to Quote or suppress checkout while LT localStorage cart still exists. | High | Guard. Prefer existing `lt_ecommerce_paused` gate over raw setting changes. | Checkout mode verifier: `/shop`, product, `/cart`, `/checkout`, cart API, and expected mode agree. |
| Toggle Webshop Settings `enable_variants` or `hide_variants` | Simplify product pages or hide variant clutter | Not run due global shared local state. Likely break: published variant templates become non-configurable or variant Website Items appear directly. | Critical | Block for LT unless a dedicated migration plan exists. | Variant settings gate: every variant template page renders options; `/shop` and category pages do not leak raw variant product cards. |
| Route collision with existing page/product | Owner reuses a nicer URL already taken | Not run. Too risky to test on shared local routes such as `/contact`, `/cart`, or real product paths. | Critical | Block. Route uniqueness and protected-route list required. | Route collision guard: reject protected routes and duplicates; crawl old/new route before save. |
| Delete Item Group or hide category | Clean up categories | Not run. It can affect all child product pages, breadcrumbs, filters, and `/shop` category nav. | High | Guard. Allow only if no public Website Items depend on it or replacement route is known. | Category dependency verifier: list Website Items and child groups affected before delete/hide; require migration plan. |

## Required Guard Shape

### Publishability Guard

Block public checkout state unless all are true:

- `Website Item.published = 1`
- linked `Item` exists
- linked `Item.disabled = 0`
- route is unique and not protected
- `lt_product_page_type` and `lt_commerce_lane` are explicit and known
- checkout lane has Standard Selling Item Price
- variant template has at least one active priced variant
- every active variant has a unique required attribute tuple
- Item group belongs to the approved shop taxonomy or is explicitly allowed

### Owner Operation Guard

For owner-like Desk changes, guard by action instead of banning the whole DocType:

| Operation | Guard |
|---|---|
| Save draft Item | Allow |
| Publish Website Item | Run publishability guard |
| Disable Item | Auto-unpublish or block if Website Item is published |
| Delete Website Item | Require route/cart/link impact report |
| Edit route | Require redirect/alias or explicit dead-link decision |
| Change item_group | Require shop-taxonomy and route/category proof |
| Edit variant attributes | Require unique combination proof and cache rebuild |
| Disable variant | Rebuild cache and prove stale cart failure copy |
| Change Webshop Settings | Break-glass gate plus full storefront/cart/checkout smoke |

## Final State

Final local state after probes:

- No `LT-BREAKLAB-02-*` Items remain.
- No `LT-BREAKLAB-02-*` Website Items remain.
- No `LT-BREAKLAB-02-*` Item Prices remain.
- Disposable old, renamed, and variant routes return `404`.
- Webshop Settings match the pre-probe state.
- No staging/live/provider/payment/DNS state was touched.
