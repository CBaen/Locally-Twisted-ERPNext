# Ecommerce Operator Hardening Protective Contracts

Date: 2026-06-30

Status: controlling planning contract for the ecommerce operator hardening lane. This is not a release approval and not a live mutation plan.

## Purpose

These contracts convert the triad critique into enforceable rules for future implementation. Any later code, migration, verifier, or release packet in this lane must load this file and either satisfy these contracts or explicitly record a blocker.

## Contract 1 - Owner Personas And Permissions

Every Product Setup workflow must define which actor can perform each action.

| Persona | Allowed Actions | Not Allowed Without Escalation |
|---|---|---|
| Owner | Draft product changes, request review, approve business meaning, approve product-family rollout after proof | Payment/provider changes, destructive catalog repair, legal/policy changes without separate approval |
| Trained employee | Draft routine copy, media, visibility, option, and price changes inside approved templates | Approve live release, create unsupported pricing logic, change brand lane, bypass blockers |
| Manager/approver | Approve staging-ready product changes when proof passes and scope is approved | Push directly to live without release packet and rollback proof |
| Developer/admin | Maintain projection code, verifiers, migrations, rollback tooling, and emergency repair | Treat raw ERPNext edits as owner workflow or skip owner-facing proof |

If a Product Setup action cannot identify the actor, it must fail closed.

Responsibilities are separated:

| Responsibility | Primary Actor | Contract |
|---|---|---|
| Business meaning approval | Owner | Approves what the product should say, cost, show, hide, or offer |
| Routine draft entry | Trained employee | May draft inside approved templates but cannot bypass blockers |
| Proof review | Manager/approver, developer/admin | Confirms required proof passed before approval advances |
| Technical apply/projection | Developer/admin or approved automation | Performs controlled projection only from approved Product Setup authority |
| Live release execution | Developer/admin through release gate | Executes target-site release only with pre-mutation packet and rollback proof |
| Rollback execution | Developer/admin through release gate | Restores prior-live state and re-proves public behavior |
| Product-family rollout approval | Owner with manager/approver review | Approves scope after one-product proof and catalog dry-run pass |

## Contract 2 - Product Setup State Transitions

Product status must describe real power, not intent.

| State | Meaning | Who Can Move It | Required Proof | Public Behavior | Failure Message | Rollback Behavior |
|---|---|---|---|---|---|---|
| Draft | Work exists but is not ready for review | Owner, trained employee, developer/admin | Required fields only | No public change | Plain missing-field blockers | No public state changed |
| Needs Review | Draft has enough data for business review | Owner, trained employee | Validation summary | No public change | Plain review blockers | No public state changed |
| Local Proof Ready | Local/no-write proof or local test proof passes | Developer/admin | Diff, preview, local verifier output | No public change | Exact failed verifier and next step | Revert local-only artifacts if any |
| Staging Ready | Staging packet is ready to apply or verify | Manager/approver, developer/admin | Staging release packet | No live public change | Exact staging blocker | Restore staging snapshot |
| Approved For Live | Business approves the change after proof | Owner, manager/approver | Staging proof and pre-mutation release packet | Still no live public change | "Approved, not live yet" with next step | Previous live state remains authority |
| Live | Target live site has been updated and publicly re-proved | Developer/admin through release gate | Live site evidence, cache evidence if applicable, public route/API proof, owner Desk proof, rollback proof | Public reflects approved change | Exact live blocker if proof fails | Roll back to captured prior-live snapshot and re-prove |
| Hidden | Product is intentionally unavailable publicly | Owner, manager/approver, developer/admin | Visibility proof | Route/shop/cart behavior follows hidden rules | Hidden reason | Restore prior visibility only through packet |
| Retired | Product is intentionally inactive and should remain hidden | Owner approval required | Retirement packet | No checkout-looking public behavior | Retired reason | Reapproval required before return |
| Quote Only | Product can collect inquiry/review context but not checkout | Owner, manager/approver | Quote-lane proof | No checkout-looking controls | Quote-only reason | Restore prior lane through packet |
| Paused | Product or ecommerce flow is temporarily blocked | Developer/admin, manager/approver | Pause reason and scope | Customer sees safe unavailable state | Pause reason and next safe step | Unpause through proof packet |

`Approved For Live` is not live. A product is live only after target-site proof is attached.

Checkout readiness is not a state. It is a proved result of Contract 8 for products in a checkout lane.

Allowed transitions:

| From | To | Trigger | Required Actor | Proof Required |
|---|---|---|---|---|
| Draft | Needs Review | Submit for business review | Owner or trained employee | Required fields and plain validation summary |
| Needs Review | Draft | Return for edits | Owner, trained employee, manager/approver | Review blocker |
| Needs Review | Local Proof Ready | Build no-write/local proof | Developer/admin or approved automation | Diff, preview, verifier output |
| Local Proof Ready | Needs Review | Proof fails or business change requested | Manager/approver or developer/admin | Failed proof and next step |
| Local Proof Ready | Staging Ready | Request staging packet | Manager/approver | Local proof packet and scope approval |
| Staging Ready | Needs Review | Staging proof fails | Manager/approver or developer/admin | Failed staging proof |
| Staging Ready | Approved For Live | Business approves after staging proof | Owner or manager/approver | Staging proof, pre-mutation packet, rollback plan |
| Approved For Live | Staging Ready | Live packet expires or scope changes | Manager/approver or developer/admin | Reason and refreshed packet required |
| Approved For Live | Live | Execute release gate | Developer/admin | Target-site proof, cache proof where applicable, public route/API proof, owner Desk proof, cart proof where relevant, rollback proof |
| Live | Hidden | Hide product | Owner with release packet execution | Visibility packet and prior-live snapshot |
| Hidden | Live | Restore visible product | Owner with release packet execution | Visibility packet, current proof, rollback target |
| Live | Quote Only | Remove checkout behavior | Owner or manager/approver with release packet execution | Quote-lane proof and no checkout-looking public controls |
| Quote Only | Live | Restore checkout behavior | Owner with release packet execution | Contract 8 cart/listing proof and release packet |
| Live | Paused | Emergency or operational pause | Manager/approver or developer/admin | Pause reason, customer-safe behavior, owner-visible status |
| Paused | Live | Resume after pause | Manager/approver with developer/admin execution | Cause resolved, public proof, rollback target |
| Live | Retired | Retire product | Owner approval with release packet execution | Retirement packet and historical-reference note |
| Retired | Draft | Reopen retired product for redesign | Owner approval | Reapproval reason and new Product Setup draft |
| Retired | Live | Not allowed directly | None | Must pass Retired -> Draft -> Needs Review -> Local Proof Ready -> Staging Ready -> Approved For Live -> Live |

Any unlisted transition is blocked until it is added to this contract with actor, proof, public behavior, failure message, and rollback behavior.

## Contract 3 - Product Authority Matrix

Before migration or repair, every product must have a non-mutating authority packet. At minimum, the packet must identify:

- brand lane;
- public route and Website Item;
- Item template and sellable Item/variant rows;
- active Product Setup record;
- title, short copy, story/details, category, route, visibility, fulfillment lane, and quote/checkout lane authority;
- primary image, gallery, selected-option media, SEO/social image, cart image, payment image, and receipt image authority;
- base price, exact variant prices, add-on prices, fulfillment fees, quote-only estimates, and unsupported price rules;
- add-ons and option axes, classified under Contract 7;
- historical references: Sales Orders, invoices, payment records, customer communications, verifiers, and public links.

No mutation may proceed if the authority packet cannot resolve brand lane, route, Product Setup, Website Item, Item, price authority, and rollback target.

## Contract 4 - Active Product Setup Uniqueness

Runtime code must not rely on "newest active Product Setup by modified time" as a durable authority rule.

Before Product Setup can become live authority, the implementation must enforce one active Product Setup per:

- target item;
- public slug/route;
- brand lane.

The unique authority key is the composite of target item, public slug/route, and brand lane. "Active" means any status that can influence proof, projection, staging, or live behavior: Needs Review, Local Proof Ready, Staging Ready, Approved For Live, Live, Hidden, Quote Only, or Paused. Duplicate active records must block approval and show an owner-visible message with the affected product, route, and next step.

## Contract 5 - Price Identity Ledger

Price proof must be ordered. Downstream parity is not enough if the source price is wrong.

Required chain:

1. Business/source intent.
2. Product Setup price rule or exact price row.
3. Generated or selected Item Price row, naming `item_code`, variant/option key, Price List, currency, UOM if relevant, validity dates/scope, and source resolver or approval evidence.
4. Product page public display.
5. Variant/option selector display.
6. Cart API line amount.
7. Checkout preview/summary amount.
8. Sales Order Item amount.
9. Payment payload amount and label, if payment proof is in scope.
10. Invoice/receipt amount and customer-facing label, if document proof is in scope.

Any mismatch blocks live status. If payment proof is out of scope, the packet must say which no-write or local test mode was used.

## Contract 6 - Media Role Ledger

Media proof must distinguish image roles.

Required roles:

- Product Setup primary image.
- `Website Item.website_image`.
- `Item.image`.
- File attachment and file visibility.
- Website Slideshow/gallery rows.
- Product HTML metadata and social image.
- Shop card image.
- Product page gallery image.
- Selected-option or variant image.
- Cart image.
- Payment line image, if payment proof is in scope.
- Receipt/customer document image, if document proof is in scope.
- Merchandising references such as homepage/favorites, if the product is used there.

Gallery proof alone is not enough to prove primary image, shop card, cart, payment, or receipt image behavior.

Simple checkout variant `Item.image` may be approved as selected-option media when the Product Setup media rule explicitly accepts it. Complex/custom raw variant images remain held unless Product Setup media rules approve the image role and public behavior.

## Contract 7 - Option And Add-On Classification

Every owner-entered option or add-on must be classified before it becomes customer-visible.

Allowed classifications:

- SKU-defining variant attribute.
- Configuration-only selection.
- Color recipe/customization.
- Measurement/upload.
- Review-only quote context.
- Paid checkout add-on.
- Unsupported.

A paid checkout add-on requires:

- enabled Item;
- Standard Selling Item Price;
- product page display rule;
- cart expansion to separate order line;
- checkout summary;
- Sales Order Item;
- invoice label;
- payment label if payment proof is in scope;
- receipt/customer-facing label if document proof is in scope.

Anything visible in UI without the required runtime and document behavior is a false-success blocker.

## Contract 8 - Listing And Cart Eligibility Invariant

Any product that appears checkout-ready in `/shop` must also be cart-ready.

Required invariant:

- published Website Item;
- linked Item enabled;
- correct commerce/checkout lane;
- sellable Item or selected variant;
- Standard Selling Item Price;
- required Product Setup authority;
- public route proof;
- cart API proof.

If a product is quote-only, hidden, retired, paused, or blocked, `/shop` must not present it as checkout-ready.

## Contract 9 - Non-Destructive Migration

Existing catalog cleanup must start as dry-run only.

Do not delete, rename, disable, collapse, repurpose, or overwrite any existing Item, variant Item, Item Price, Website Item, Product Setup, Website Slideshow, File, Sales Order reference, invoice reference, payment reference, or customer-message-linked record until a dry-run proves:

- current dependency map;
- replacement record plan;
- historical reference handling;
- rollback/restore method;
- affected public route behavior;
- affected cart/checkout behavior;
- owner approval where product scope changes.

The first catalog-wide output must be a report, not a write.

## Contract 10 - Pre-Mutation Release Packet

Before any write path beyond no-write proof, create a pre-mutation release packet with:

- exact environment;
- branch and commit/hash, if code is involved;
- target products and routes;
- actor requesting the change;
- row-level diff or planned diff;
- backup/snapshot method;
- rollback command or maintenance procedure;
- cache plan;
- verifier list;
- brand-lane proof;
- payment/document proof mode;
- stop condition;
- owner/business approval if required;
- no-downtime/customer-impact section, including release containment, fallback or pause posture, expected customer impact, and proof the change does not accidentally expose checkout/payment;
- app-mirror release-scope guard for Frappe Cloud work, including old live app hash, target app-mirror branch/commit, old-live-to-target diff, deploy pipeline status, dirty-overlap audit, site update result, and migrate result where applicable.

No staging or live write may proceed without this packet.

## Contract 11 - Document And Payment Proof Modes

Document/payment proof must name its mode:

| Mode | Meaning | Allowed In This Lane Without Separate Payment Approval |
|---|---|---|
| No-write payload proof | Build/inspect intended payload without creating customer/provider records | Yes |
| Local test proof | Use local/test records only, no live customer/provider effect | Yes |
| Staging proof | Use staging environment under release gate and pause rules | Only with staging approval |
| Live proof | Live payment/document/customer-message path | No, requires separate payment/release approval |

No real payment session, customer email, Payment Request, submitted invoice, receipt send, provider change, or customer-facing payment promise belongs in this lane unless the separate payment/release gate is explicitly reopened and passes.

Live payment proof additionally requires:

- correct provider/account identity proof;
- live Stripe acceptance only when payment parameters change and the payment gate approves;
- no one-time promo, gift, or redemption code use unless Guiding Light explicitly approves that spend/burn;
- provider dashboard or API evidence captured without changing account configuration unless separately approved.

## Contract 12 - Brand-Lane Resolution

Every product authority packet and release packet must resolve the operating brand lane before public, payment, document, file, portal, or automation behavior is touched.

Allowed brand lanes:

- `locally_twisted`
- `commercial_balloon_decor`
- `memorial_balloons`

No fourth lane is allowed in this project scope.

Required brand-lane fields:

- brand lane;
- route namespace or public route;
- customer-facing copy surface;
- invoice/document identity;
- payment/customer message identity;
- file/media ownership;
- portal and automation behavior;
- inheritance proof through route, file/media, document, payment metadata, customer message, portal, and automation surfaces;
- failure behavior when lane is unclear.

Ambiguous brand lane fails closed.

## Contract 13 - Live Proof And Rollback

Live means the target customer-facing environment has changed and been re-proved.

Minimum live proof:

- old live app hash and target app-mirror branch/commit for Frappe Cloud app releases;
- old-live-to-target diff and dirty-overlap audit for files in the release scope;
- deploy pipeline status and site update result;
- migrate result where schema/patch/data migration is involved;
- target-site update evidence;
- migration/site update evidence where applicable;
- cache evidence where applicable;
- fresh public route proof;
- fresh public API proof where applicable;
- owner Desk proof;
- cart/checkout proof where the product looks checkout-ready;
- rollback proof.

Minimum rollback contract:

- pre-change row snapshot;
- exact fields touched;
- reversible patch, maintenance command, or documented manual procedure;
- cache rollback plan;
- public proof after rollback;
- owner-visible status after rollback.

If rollback cannot be defined, live mutation is blocked.

## Contract 14 - Change-Type Proof Matrix

Different changes require different proof. Routine edits should be easy, but never fake success.

| Change Type | Required Proof |
|---|---|
| Copy only | Product Setup authority, Website Item projection, product page render, shop card if visible, no unintended price/media/cart diff |
| Price | Price identity ledger through cart/checkout and no-write/local document/payment mode where relevant |
| Primary image | Media role ledger for Product Setup, Item, Website Item, shop card, product page, metadata, cart/payment/receipt where relevant |
| Gallery | Slideshow/gallery rows, product page gallery, desktop/mobile render, no unintended primary image drift |
| Selected-option media | Option/variant selector, product page selected image, cart/payment image where relevant |
| Add-on | Add-on classification plus separate order-line proof for paid add-ons |
| Option/configuration | Contract 7 classification, cart payload preservation, order/document preservation where relevant, no SKU explosion unless SKU-defining |
| Quote/checkout lane | Brand-lane proof, listing/cart invariant, no checkout-looking controls for quote-only behavior, release packet |
| New product or product family | Authority packet, owner scope approval, no-destructive migration rule where replacing existing products, full proof for all affected change types |
| Retire/revive | Historical-reference note, owner approval, visibility proof, route/shop/cart behavior proof, release packet |
| Fulfillment, tax, or fee | Source approval, price/fee identity, checkout totals, order/document proof, payment mode proof where relevant |
| Catalog repair/migration | Dry-run report first, dependency map, replacement plan, historical references, rollback/restore proof, owner approval where product scope changes |
| Visibility | Route, shop listing, cart eligibility, hidden/retired/quote-only customer behavior |
| Route/category | Old route handling, new route proof, shop/category listing proof, no unintended brand-lane drift |
| Brand lane | Full brand-lane resolution packet and approval |

Any unlisted change type is blocked until classified with proof burden, owner approval if needed, rollback behavior, and release-packet requirements.

## Contract 15 - Owner Blocker Report

The owner/admin workflow must include a report or dashboard that shows:

- product;
- public route;
- current state;
- blocker category;
- exact blocked proof;
- last proof time;
- required decision or next step;
- whether developer/admin help is required.

Verifiers and failed projections must feed an owner-readable blocker, not only a developer log.

Canonical blocker categories:

- Needs your decision.
- Needs manager approval.
- Needs a missing photo.
- Not safe to sell yet.
- Developer help required.
- Waiting for proof.
- Brand lane unclear.
- Payment/release gate required.

Example owner-facing blocker messages:

- Price mismatch: "This product is not safe to sell yet. The price you approved does not match the checkout price. Please leave it blocked until the price proof passes."
- Missing cart proof: "This product can appear on the website, but we have not proved it can be added to cart safely. It will stay out of checkout until that proof passes."
- Ambiguous brand lane: "This product is missing its brand lane. Choose the correct brand before it can affect pages, invoices, payment labels, or customer messages."
- Duplicate Product Setup: "More than one active setup controls this product. Pick the correct setup or ask for developer help before approving changes."
- Unsupported add-on: "This add-on is not ready for checkout. It needs a sellable item, price, order line, and customer label before customers can choose it."
