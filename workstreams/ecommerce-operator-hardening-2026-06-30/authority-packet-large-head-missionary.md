# Authority Packet - Large head Missionary

Date: 2026-06-30

Status: non-mutating authority packet with public, local, and authenticated live read-only evidence for the incident product. It does not approve mutation, release, payment, provider, cache, or deployment work.

## Packet Header

| Field | Value |
|---|---|
| Product | Large head Missionary |
| Slug | `large-head-missionary` |
| Scope | Non-mutating product authority mapping for ecommerce operator hardening Phase 0/1 |
| Public route checked | `https://locallytwisted.com/shop-items/bouquets/large-head-missionary` |
| Shop listing checked | `https://locallytwisted.com/shop` |
| Authenticated DB/Desk checked | Local snapshot plus live read-only API snapshot. Live evidence: `/tmp/lt-live-large-head-missionary-api-audit-2026-06-30.json` |
| Mutation allowed by this packet | No |
| Payment/provider/live settings touched | No |

## Confirmed Public And Source Evidence

| Area | Confirmed Evidence | Evidence Source |
|---|---|---|
| Brand lane | `locally_twisted` is the product lane used by the current paid-social/product-sales planning packet and by this ecommerce workstream's route context. | Source/workstream evidence, not DB proof |
| Public product route | Product route returns HTTP 200 from Frappe Cloud with `x-page-name: shop-items/bouquets/large-head-missionary` and `x-from-cache: False`. | Public render read on 2026-06-30 |
| Website Item public id | Public HTML contains `id="page-WEB-ITM-0039"` with `data-doctype="Website Item"` and route `shop-items/bouquets/large-head-missionary`. | Public render |
| Title | Public page renders `Large head Missionary`. | Public render |
| Canonical/meta route | Public HTML canonical and Open Graph URL point to `https://locallytwisted.com/shop-items/bouquets/large-head-missionary`. | Public render |
| Template item code | Public page runtime uses `data-template-item-code="large-head-missionary"` and architecture JSON `item_code: "large-head-missionary"`. | Public render |
| Product Setup runtime source | Embedded runtime JSON says `source: "lt_product_setup"`. | Public render |
| Product Setup status visible in runtime | Embedded runtime JSON says `setup_status: "Local Preview Ready"`. | Public render; exact Desk record unknown |
| Commerce lane | Architecture JSON says `checkout_allowed: true`, `commerce_lane: "checkout"`, and Product Setup runtime says `buying_path: "Direct checkout"`. | Public render |
| Product page type | Runtime says `complex_custom_product`; Product Setup runtime says `page_template: "Configurable product page"`. | Public render |
| Item group/category | Runtime says `item_group: "Bouquets"`; current route also includes `/bouquets/`. | Public render |
| Shop listing | `/shop` renders a Large head Missionary card linking to `/shop-items/bouquets/large-head-missionary`, with image `/files/large-head-missionary.png`, copy `Large head Missionary`, price `from $ 175.00`, and `Choose options` CTA. | Public render |
| Product page price display | Product page renders `from $ 175.00`. | Public render |
| Product Setup base price | Embedded Product Setup runtime JSON says `commerce.base_price: 125.0`, `pricing_authority: "server"`, and `requested_outcome: "checkout"`. | Public render |
| Variant axes | Public architecture/runtime JSON requires three SKU-defining single-select axes: `Missionary` with `Elder`/`Sister`; `skin color` with `Blush`/`Brown`/`Latte`; `Hair color` with `Black`/`Brown`/`Dark Brown`/`Orange`/`yellow`. | Public render |
| Variant count | Embedded Product Setup runtime says `variant_combination_count: 30`, with 3 SKU-defining groups and 0 configuration-only groups. | Public render |
| Add-ons | Embedded runtime JSON has `add_on_groups: []`. | Public render |
| Primary image | Product metadata, shop card, and product page primary image use `/files/large-head-missionary.png`. | Public render |
| Gallery image | Embedded runtime JSON includes `/files/large-head-missionary--extra-01.png` as approved customer gallery media. | Public render |
| Selected-option media | Runtime includes selected variant media rules for concrete variant codes, but the rules are marked `approved_for_customer: false` and note that complex product variant images need Product Setup approval. | Public render |
| Image file format risk | Public server reports the image URLs as `image/png`; local source/seed files with `.png` names identify as WebP bytes. | Public headers and local file metadata |

## Live Read-Only DB/API Evidence

Evidence file:

- `/tmp/lt-live-large-head-missionary-api-audit-2026-06-30.json`

| Area | Live Evidence | Status |
|---|---|---|
| Product Setup save | `LT Product Blueprint` `large-head-missionary` modified `2026-06-30 01:43:01.382176` by `locallytwisted@gmail.com`. | Owner save confirmed |
| Product Setup base price | `125.0`. | Confirmed |
| Product Setup exact prices | 30 `price_rows`, all `125.0`, same save timestamp/user. | Confirmed |
| Website Item | `WEB-ITM-0039`, published, route `shop-items/bouquets/large-head-missionary`, modified `2026-06-29 01:19:25.229958` by `Administrator`. | Confirmed |
| Template Item | `large-head-missionary`, enabled variant template, modified `2026-05-17 16:09:50.270338` by `Administrator`. | Confirmed |
| Variant Items | 30 variants. | Confirmed |
| Item Prices | 30 `Standard Selling` rows, all `175.0`, modified on 2026-04-30 by `Administrator`. | Confirmed |
| Public price | Public page still renders `from $ 175.00`. | Confirmed |
| Product Setup copy | `product_story` and `product_details` differ from public Website Item copy. | Confirmed |
| Public copy | Product page renders `Website Item.lt_brand_description` and `Website Item.lt_product_details`. | Confirmed |

Live interpretation:

- the owner save was real and reached live Product Setup;
- Product Setup price rows now say `125.0`;
- sellable `Item Price` rows still say `175.0`;
- public listing/product/cart price authority currently reads sellable `Item Price`, not Product Setup price rows;
- public product copy currently reads Website Item fields, not top-level Product Setup story/details.

## Unknowns Requiring Further Read-Only Proof Or Product Decision

| Area | Unknown / Needed Proof |
|---|---|
| Brand lane row authority | Confirm current row-level brand lane on Website Item, Product Setup, files/media, document/payment metadata, and any automation surfaces. |
| Product authority design | Decide whether Product Setup becomes direct runtime authority or an explicit publish/apply authority that writes Website Item and Item Price rows. |
| Business price approval | Confirm whether the intended customer price is now `125.0` or should remain `175.0`; the system currently contains both. |
| Public copy approval | Confirm whether Product Setup top-level story/details or current Website Item copy should be the customer-approved copy. |
| Product Setup uniqueness by brand lane | Live Product Setup row exists; brand-lane uniqueness still needs proof if brand field is absent or not captured. |
| Variant attribute rows | The live API list returned 30 variants; variant attribute detail still needs a focused follow-up because the broad query returned no rows in the current proof packet. |
| Price authority | Resolved mechanically: Product Setup price is `125.0`; public/sellable Item Price is `175.0`. Remaining decision is which authority should win and how owner saves should publish. |
| Variant selector API | Recheck selected variant API behavior and exact resolved item codes after authenticated row proof. |
| Cart API | Prove server cart resolution for a selected variant without trusting client-side price or old local-cart evidence. |
| Checkout/Sales Order | Use no-write or approved local/test proof only to confirm checkout summary and Sales Order line amount/configuration preservation. |
| Payment/document labels | Out of scope for live proof; needs no-write payload proof or separately approved payment/document mode. |
| Media rows | Confirm Website Item image, Item image, File rows, file visibility, Website Slideshow/gallery rows, and whether local WebP-in-PNG filenames are accepted or need cleanup. |
| Historical records | Identify Sales Orders, invoices, payment records, customer communications, and marketing/merchandising references that depend on the existing product and route. |
| Rollback target | Capture a row-level pre-change snapshot before any future mutation. This packet has no rollback target yet. |

## Local Read-Only DB Snapshot Evidence

Snapshot:

- `/tmp/lt-large-head-missionary-db-snapshot.json`
- Generated from local LT Docker workshop on site `frontend`.
- `read_only: true`
- failures: none
- This is local-only evidence. It does not prove hosted/live row state.

| Area | Local Evidence | Live Closure Status |
|---|---|---|
| Website Item | `WEB-ITM-0039`, item code `large-head-missionary`, published `1`, route `shop-items/bouquets/large-head-missionary`, image `/files/large-head-missionary.png`, slideshow `LT Product Gallery - large-head-missionary`, modified `2026-05-24 16:42:45.556169` by `Administrator` | Superseded by later live proof: live Website Item exists, is published, and has the same route/image with newer `2026-06-29` modification |
| Template Item | `large-head-missionary`, enabled, has variants, sales item, non-stock item, image `/files/large-head-missionary.png`, modified `2026-05-17 16:09:50.270338` by `Administrator` | Closed for template identity/enabled state by live proof |
| Variants | 30 enabled variants under `large-head-missionary` | Closed for variant count by live proof; detailed attribute rows still need focused follow-up |
| Item Prices | 30 `Standard Selling` rows, all `USD`, UOM `Nos`, selling `1`, each `175.0` | Closed for live price split: live Item Prices stayed `175.0` |
| Product Setup | one record named `large-head-missionary`, `publish_status: Local Preview Ready`, `validation_status: Ready For Local Preview`, `ready_for_live: 0`, `base_price: 175.0`, target item `large-head-missionary`, target Website Item `WEB-ITM-0039`, modified `2026-05-22 13:54:26.463965` by `Administrator` | Superseded by live owner save: live Product Setup base price is `125.0`, modified `2026-06-30 01:43:01.382176` by `locallytwisted@gmail.com` |
| Product Setup options | three SKU-defining selected-option axes: `Missionary`, `skin color`, `Hair color` | Public/runtime proof supports this; detailed live child row proof can be added in the projection verifier |
| Product Setup prices | 30 exact checkout price rows, each `175.0`, mapped to variant item codes | Superseded by live owner save: live Product Setup exact price rows are all `125.0` |
| Product Setup add-ons | none captured | No add-ons exposed in public runtime; detailed live add-on row proof can be added in the projection verifier |
| Product Setup media rules | 15 exact-variant selected-photo rules, all `approved_for_customer: 0` | Public/runtime proof supports held selected-option media; live media row detail still needs media-focused proof |
| Product Setup gallery | one approved customer gallery image `/files/large-head-missionary--extra-01.png` | Public/runtime proof supports this; live slideshow/File detail still needs media-focused proof |

Local interpretation:

- local Product Setup base price, Product Setup exact prices, and Item Prices agree at `175.0`;
- live public embedded Product Setup still reports `commerce.base_price: 125.0`;
- this changes the unresolved blocker from local price split to local-vs-live authority drift.

Do not use this local snapshot as live root-cause closure.

## Product Record Matrix

| Surface | Current Packet State | Evidence | Closure Requirement |
|---|---|---|---|
| Brand lane | Partial: `locally_twisted` by source/workstream context | Current planning/workstream source | DB/Desk row proof across product, media, document/payment/customer-message surfaces |
| Public route | Confirmed customer-visible route | Public HTTP 200 and HTML | Keep as public proof before repair |
| Website Item | Confirmed: live row `WEB-ITM-0039`, published, same route/image | Live read-only API and public HTML | Add copy/projection decision before mutation |
| Template Item | Confirmed: live Item `large-head-missionary`, enabled variant template | Live read-only API and public runtime | Keep as rollback target input |
| Variants | Confirmed count: 30 variants | Live read-only API and public runtime | Add focused attribute-row proof before variant architecture repair |
| Product Setup | Confirmed: live Product Setup saved by owner with `125.0` price rows | Live read-only API and public runtime | Add active uniqueness/brand-lane proof before runtime authority reliance |
| Category | Partial: `Bouquets` | Public runtime and route | DB row proof |

## Price Authority Matrix

| Price Surface | Current Packet State | Evidence | Closure Requirement |
|---|---|---|---|
| Business/source intent | Unknown | Not checked in this packet | Owner/business approval or approved source packet |
| Product Setup base price | Live Product Setup row says `125.0`; local old snapshot said `175.0` before owner live edit | Live read-only API; local snapshot is now historical local-only evidence | Decide whether Product Setup base price should drive public price directly or through publish/apply |
| Exact Product Setup prices | Live Product Setup has 30 exact price rows at `125.0` | Live read-only API | Decide publish/apply behavior |
| Exact sellable Item Prices | Live has 30 `Standard Selling` Item Prices at `175.0`; public surfaces show `$175.00` | Live read-only API; public product page and shop listing | Decide whether Item Prices should be updated from Product Setup or remain independent |
| Price list/currency/UOM | Live Item Prices are `Standard Selling`, `USD`, UOM `Nos`, selling `1`, no validity dates | Live read-only API | Decide price authority contract |
| Cart amount | Unknown in this packet | No cart API proof run here | Non-mutating cart API proof for selected variant |
| Checkout/Sales Order amount | Unknown | Not run | No-write/local-test proof only |
| Payment/invoice/receipt amount | Unknown and out of scope for live proof | Not run | Separate no-write or approved payment/document proof mode |

## Media Authority Matrix

| Media Role | Current Packet State | Evidence | Closure Requirement |
|---|---|---|---|
| Product Setup primary image | `/files/large-head-missionary.png` | Live read-only API and public Product Setup JSON | Confirm media authority contract before repair |
| Website Item website image | `/files/large-head-missionary.png` | Live read-only API | Confirm media authority contract before repair |
| Item image | `/files/large-head-missionary.png` | Live read-only API | Confirm media authority contract before repair |
| File attachment/visibility | Publicly reachable image URLs | Public HEAD checks | Authenticated File row and attachment proof |
| Social image | `/files/large-head-missionary.png` | Public metadata | Keep public proof; confirm source row |
| Shop card image | `/files/large-head-missionary.png` | Public `/shop` render | Keep public proof; confirm listing source row |
| Product gallery | `/files/large-head-missionary--extra-01.png` approved for customer gallery | Public Product Setup JSON | Authenticated slideshow/gallery and media-rule proof |
| Selected-option media | Held/not customer-approved in runtime media rules | Public Product Setup JSON | Product Setup media approval decision and variant-media proof |
| Cart/payment/receipt images | Unknown | Not proved | Cart/document/payment proof mode |
| Media cleanup | Filename extension and MIME/header do not prove byte format consistency | Public headers and local file metadata | Decide whether to normalize file type before ads, social previews, or media role closure |

## Options And Add-Ons

| Option/Add-On | Classification | Current Packet State | Evidence | Closure Requirement |
|---|---|---|---|---|
| Missionary | SKU-defining variant attribute | Required single select, values `Elder`, `Sister` | Public runtime | DB variant attribute proof |
| skin color | SKU-defining variant attribute | Required single select, values `Blush`, `Brown`, `Latte` | Public runtime | DB variant attribute proof |
| Hair color | SKU-defining variant attribute | Required single select, values `Black`, `Brown`, `Dark Brown`, `Orange`, `yellow` | Public runtime | DB variant attribute proof |
| Paid add-ons | None exposed in runtime | `add_on_groups: []` | Public runtime | Authenticated Product Setup add-on row proof |
| Configuration-only groups | None exposed in runtime | `configuration_only_group_count: 0` | Public runtime | Authenticated Product Setup row proof |

## Listing And Cart Eligibility

| Invariant | Current Packet State | Evidence | Closure Requirement |
|---|---|---|---|
| Published Website Item | Publicly visible, but row status unknown | Product page and shop card render | Authenticated Website Item `published` proof |
| Linked Item enabled | Unknown | Public listing does not prove enabled Item | Authenticated linked Item proof |
| Correct commerce lane | Public runtime says checkout | Public architecture/Product Setup JSON | DB/source contract proof |
| Sellable selected variant | Partial: page requires variant selection and runtime expects 30 variants | Public runtime | Variant selector plus DB variant proof |
| Standard Selling Item Price | Confirmed: 30 live Item Price rows at `175.0`; public render starts at `$175.00` | Live read-only API and public render | Decide Product Setup projection/runtime authority before mutation |
| Required Product Setup authority | Partial: runtime source exists | Public runtime | Product Setup row and active uniqueness proof |
| Public route proof | Confirmed | HTTP 200 public render | Keep proof current before any release |
| Shop listing proof | Confirmed visible in `/shop` | Public shop render | Keep proof current before any release |
| Cart API proof | Unknown in this packet | Not run | Non-mutating cart API proof for a selected variant |
| Checkout proof mode | Unknown | Not run | No-write/local-test only unless a separate release/payment gate approves more |

## Historical References

| Reference | What It Proves | What It Does Not Prove |
|---|---|---|
| Current ecommerce hardening workstream README, flow map, broken-connections register, owner workflow map, and protective contracts | This product is the concrete example for Product Setup/base-price divergence and owner-workflow hardening. | Current DB row values or safe mutation readiness |
| 2026-05 catalog price readiness audit | Historical audit recorded `large-head-missionary` as online checkout with 30 expected/live-priced units and `$175.00` live price range. | Current live DB prices on 2026-06-30 |
| 2026-05 price enrichment audit | Historical audit recorded 30 review units backed by live snapshot pricing rather than source resolver pricing. | Current business approval for the price |
| 2026-05 media classification packet | Historical source-approved gallery media existed for the extra image. | Current File, Website Slideshow, Item, cart, payment, or receipt media roles |
| 2026-05 import manifest | Historical route/template/Website Item code mapping and media/price import planning. | Current route after category path, live row state, or rollback target |
| 2026-06-30 paid-social missionary sales planning packet | Same-day source packet says the product route is live, starts at `$175.00`, has required axes, and had prior local-cart browser proof for one selected SKU. | This packet's own cart API proof or any live payment/provider approval |

## Rollback Target

No rollback target is defined yet. Before any future mutation, capture an authenticated read-only row snapshot for:

- Website Item `WEB-ITM-0039` or whatever current DB name resolves to this route.
- Template Item `large-head-missionary`.
- All 30 variant Items and their Item Variant Attribute rows.
- All current `Standard Selling` Item Price rows for the template/variants.
- Product Setup record(s) for target item, slug, and brand lane.
- File rows and attachments for `/files/large-head-missionary.png` and `/files/large-head-missionary--extra-01.png`.
- Website Slideshow/gallery rows and selected media rules.
- Current public route, shop listing, selected variant, cart, and checkout proof mode.

## Blocker List

| Blocker | Category | Blocks | Required Next Proof |
|---|---|---|---|
| Live Product Setup price `125.0` conflicts with live sellable Item Prices and public price `175.0`. | Not safe to sell yet | Any claim that Product Setup edits reliably control live customer price | Product authority design and owner-publish/apply implementation |
| Product Setup active record and uniqueness by brand lane are not fully closed. | Developer help required | Product Setup authority closure | Read live Product Setup records by target item, slug, and brand lane after brand field availability is confirmed |
| Website Item copy differs from Product Setup top-level copy. | Waiting for decision | Owner copy-edit confidence | Decide customer-approved copy authority and projection path |
| Variant Item and Item Price rows prove price split. | Waiting for repair design | Live cart/listing eligibility closure | Build no-write preview and fail-loud parity verifier before mutation |
| Cart API and checkout proof were not run in this packet. | Waiting for proof | Checkout-ready claim | Non-mutating cart API proof and no-write/local-test checkout proof |
| Media roles beyond public page/shop/gallery are unknown. | Needs a missing photo | Cart/payment/receipt media closure | Read File/Item/Website Item/gallery rows and run media role proof |
| Rollback target is absent. | Developer help required | Any mutation beyond no-write proof | Capture row-level pre-change snapshot and public proof |
| Historical order/document/payment references are unmapped. | Waiting for proof | Destructive repair, rename, deletion, variant collapse, or route change | Read-only dependency map for historical records and customer communications |
| Local old snapshot and live current Product Setup now differ because the owner made a live edit after the local snapshot. | Informational | Treating local snapshot as current live truth | Use live API snapshot as current authority for this incident |
