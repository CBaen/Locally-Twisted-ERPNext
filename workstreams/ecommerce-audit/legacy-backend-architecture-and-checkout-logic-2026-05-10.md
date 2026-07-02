# catalog_data Backend Architecture and Checkout Logic Source Witness

D:2026-05-10 | Check:live catalog_data backend/public read-only inspection + local catalog_data module source 2026-05-10 | Confidence:high

## Scope and guardrail

This is a read-only source-witness artifact. catalog_data is being used as the behavioral reference for ERPNext/Frappe ecommerce receiving-layer design.

Allowed during this pass: backend navigation, browser inspection, JSON-RPC reads, public cart/checkout/payment page reads, local source reads.

Not performed: save, create, delete, submit product inquiry, submit checkout, create transaction, pay, publish, import, purge.

Sensitive checkout values observed in the browser were redacted from this artifact. Do not copy catalog_data code/schema blindly; preserve business meaning and guardrails.

## Evidence sources

### Live catalog_data backend / public site

- Backend product: `catalog_data/products/57` (`Classic Arch`).
- Public product: `shop/classic-arch-57`.
- Public cart, checkout, payment pages observed read-only.
- Live catalog_data module: `locally_twisted`, installed version `19.0.2.15.0`.
- Live Classic Arch product template id: `57`.
- Live payment page was observed only up to the payment method selection screen; `Pay now` was not clicked.

### Local source files checked

- `/home/guidingl/projects/external-catalog-data/addons/locally_twisted/__manifest__.py`
- `.../models/product_template.py`
- `.../models/crm_lead.py`
- `.../models/project_task.py`
- `.../views/website_sale_templates.xml`
- `.../views/product_views.xml`
- `.../data/automation_data.xml`
- `.../data/delivery_data.xml`
- `.../data/ir_config_parameter.xml`
- `.../data/ir_asset.xml`
- `.../static/src/js/payment_post_processing.js`
- `.../controllers/main.py`

## 1. catalog_data module architecture: this is not only ecommerce

The catalog_data addon is a business system module, not just shop styling. Its manifest depends on website/shop, delivery, Stripe payments, portal/auth, CRM, calendar, account, purchase, MRP, project/sale_project, HR/timesheets/expenses, surveys, mass mailing, loyalty, base automation, and privacy lookup.

ERPNext implication: the ecommerce build cannot be treated as isolated product cards. Shop decisions touch CRM, customer accounts, payments, tax/delivery, project/task execution, follow-up automation, and privacy exposure.

## 2. Product page architecture: true variants vs no-variant configuration

Live Classic Arch backend facts:

- `product.template` id `57`, name `Classic Arch`.
- Published: `true`.
- Website URL: `/shop/classic-arch-57`.
- Category id: `[26]` / What We Make / Balloon Arches.
- Product type: `consu`.
- Base list price: `$260`.
- Invoice policy: ordered quantities.
- Out-of-stock order allowed: `true`; available threshold observed as `5`.
- Variant count: `4`.
- Ecommerce media image count: `10`.
- Optional/accessory products: empty on this product in the live read.

Attribute architecture:

| Attribute | Display | Variant mode | Values | Pricing role |
|---|---:|---:|---:|---|
| Arch Size | pills | `always` | 4 | Creates real variants and price extras |
| latex colors | multi | `no_variant` | 53 | Preserved as cart/order-line configuration, no variant explosion |
| Design | image | `no_variant` | 2 | Preserved as configuration |
| LED Lights | image | `no_variant` | 2 | Preserved as configuration; `Add LED Lights` adds `$50` |

Real variants are only size variants:

| product.product | Display | PTAV | Price |
|---:|---|---:|---:|
| 91 | Classic Arch (20ft) | 201 | $260 |
| 92 | Classic Arch (25ft) | 202 | $325 |
| 93 | Classic Arch (30ft) | 203 | $390 |
| 94 | Classic Arch (35ft) | 204 | $455 |

Price extras observed:

- 25ft: +$65.
- 30ft: +$130.
- 35ft: +$195.
- Add LED Lights: +$50.
- latex colors: 53 values, no price extras observed.

Critical pattern: **catalog_data keeps the combinatorial dimension out of SKU variants**. Size creates the product identity; colors/design/lights are option payload attached to the cart/order line.

ERPNext receiving requirement:

- Use ERPNext Item Variant only for dimensions that truly change the SKU/price identity.
- Create an LT product configuration layer for no-variant attributes:
  - multi-select color options,
  - image/radio design options,
  - LED add-on options,
  - custom text/name fields,
  - per-option price extras,
  - selected-option persistence into cart, quotation, sales order, invoice/project handoff.

## 3. 50+ color stress behavior

Read-only public product inspection selected all 53 `latex colors` checkboxes without clicking add-to-cart.

Observed behavior:

- Page accepted all 53 checked color options.
- URL became an `attribute_values=` query containing the selected size id, all selected color value ids, design id, and LED id.
- Visible price stayed `$260.00` for the 20ft/no-lights case because colors have no price extras.
- Hidden `product_id` stayed `91`, proving color choices did not create/switch product variants.
- Add-to-cart remained enabled.
- No network call occurred during checkbox selection; selection updated local state/URL only.

ERPNext receiving requirement:

- Product page must not create a variant matrix for 50+ colors.
- Color selection must be a bounded configuration payload, with server-side validation of max/min rules per product.
- URL/share state may include selected options, but server state should be authoritative at cart add time.

## 4. Media and product description logic

catalog_data product media:

- Live Classic Arch has 10 product template images.
- Local backend view adds a dedicated product Images tab for `product_template_image_ids` (`product_views.xml:11`).
- Live installed views include attribute/carousel synchronization customizations:
  - `Classic Arch Attribute Image Sync`.
  - `Latex Colors Image Checkboxes (All Products)`.

Description logic:

- Local model syncs `description_sale` into `website_description` only when ecommerce description is empty (`product_template.py:12-21`, `product_template.py:28-30`, `product_template.py:46-50`).
- This is a one-direction seed; handcrafted website copy is not overwritten.

ERPNext receiving requirement:

- Product source needs separate fields for sales/quotation copy and website marketing copy.
- Import/build logic may seed website copy from sales copy only when empty.
- Media needs first-class product-gallery support plus optional attribute-driven image behavior.

## 5. Product inquiry / quote-first path

catalog_data injects a product inquiry form below product description on every product page (`website_sale_templates.xml:114-123`).

The form:

- Posts to `/website/form/`.
- Uses `data-model_name="crm.lead"` (`website_sale_templates.xml:137`).
- Includes CSRF (`website_sale_templates.xml:139`).
- Sets hidden lead name to `Product Inquiry: <product.name>` (`website_sale_templates.xml:141`).
- Captures:
  - contact name,
  - email,
  - occasion type (`x_occasion_type`, lines 166-168),
  - event date (`x_event_date`, lines 182-184),
  - vision/details in `description` (lines 190-192),
  - inspiration photos in `ufile` (lines 196-201),
  - submit button `Send My Request` (line 209).
- Redirects to `/shop#inquiry-sent` on success.

CRM lead model support:

- `crm.lead` has event/service fields including `x_event_type`, `x_event_date`, location, venue, crew size, setup duration (`crm_lead.py:9+`).
- Website/book multi-select services are stored as `x_services` char (`crm_lead.py:68`).
- Booking-confirmation duplicate-send guard is `x_booking_confirmed` (`crm_lead.py:82`).
- Lead creation auto-builds a name and auto-links/creates a partner when email or phone exists (`crm_lead.py:131-179`).

ERPNext receiving requirement:

- Every product page needs a quote/request lane separate from ecommerce checkout.
- Product inquiry should create a Lead/Opportunity with product context and optional uploaded inspiration media.
- Do not force configurable/custom event products into direct checkout when quote-first is the safer business state.

## 6. Cart/order-line preservation proof from existing live draft cart

A live draft website cart/order was observed read-only from the current browser session. This was not created by this pass.

Backend proof, sanitized:

- Sale order state: `draft`.
- Website: `Locally Twisted`.
- Amounts: untaxed `$65.00`, tax `$9.75`, total `$74.75`.
- Carrier: `Standard delivery`.
- Payment term: `Immediate Payment`.
- Transactions: `0`.
- Lines: 2.

Order line preservation:

- Product line: `Graduation bouquet`.
- Product line name preserved selected no-variant colors: `latex colors: Wintergreen, Royal Blue`.
- Product line name preserved custom text field but redacted here: `Add Name: Enter name: [custom text redacted]`.
- `product_no_variant_attribute_value_ids` contained two latex color PTAV ids.
- `product_custom_attribute_value_ids` contained one custom value record, redacted.
- Delivery line was a separate order line with `is_delivery=true` and `$0.00` in this observed cart state.

This is the key backend proof pattern: no-variant selections and custom text are not only UI decoration; they are persisted on the sale order line.

ERPNext receiving requirement:

- Cart line must store selected no-variant options as structured child rows, not only display text.
- Display text can be generated from structured rows.
- Custom values must be stored separately from enumerated option ids and redacted/handled carefully in logs.
- Delivery/service charge lines must remain distinguishable from product lines.

## 7. Checkout/payment architecture observed read-only

Checkout sequence observed:

1. Cart.
2. Address.
3. Payment.

Cart page showed:

- Cart item, selected options, delivery, subtotal, tax, total.
- `Checkout` link to `/shop/checkout?try_skip_step=true`.

Checkout/address page showed:

- Delivery method options:
  - Standard delivery / free observed default label from catalog_data native option,
  - Pickup (Free),
  - Standard Delivery $15,
  - Park City Delivery $50,
  - Out-of-Area Quote $35.
- Address cards and billing/delivery same-address behavior.
- Confirm link to `/shop/payment`.

Payment page showed:

- Payment method: Card.
- Provider: Stripe, state observed as test.
- Payment form mode: payment.
- Transaction route pattern: `/shop/payment/transaction/<order_id>`.
- Landing route: `/shop/payment/validate`.
- `Pay now` submit button present but not clicked.
- Payment form contained sensitive Stripe/billing details in browser data; these are intentionally not recorded here.

Important: this artifact does **not** claim payment works end-to-end because no transaction was submitted and no confirmation/backend transaction record was created in this pass.

ERPNext receiving requirement:

- Payment page must remain last-mile only after cart/order intent is preserved.
- Checkout verification must prove:
  - cart line option persistence,
  - delivery option persistence,
  - tax calculation,
  - payment intent creation only at the approved step,
  - no secret or customer PII leakage in logs/artifacts.

## 8. Delivery / shipping logic

Local delivery data defines service products and delivery carriers (`delivery_data.xml`).

Carriers:

- Pickup (Free): `delivery_data.xml:92`.
- Standard Delivery: `delivery_data.xml:101`, fixed `$15`, zip prefixes for Wasatch Front.
- Park City Delivery: `delivery_data.xml:119`, fixed `$50`, zip prefixes `84060`, `84068`, `84098`.
- Out-of-Area Quote: `delivery_data.xml:133`, fixed `$35` in current catalog_data source.

Source note says zone overlap is intentional and business review happens at invoice time.

ERPNext receiving requirement:

- Delivery options need explicit service-item mapping.
- Zone logic must be configurable and operator-reviewable; quote-first/out-of-area should not pretend to be final when human review is needed.

## 9. Sales order, invoice, deposit, and automation architecture

Live backend reported 16 active `base.automation` rules from `locally_twisted`.

Major automation groups:

- Lead lifecycle:
  - form auto-acknowledgment on lead create with email,
  - booking confirmation on Won with duplicate guard,
  - anniversary init/reminder/rollover.
- Sales order/invoice:
  - auto-create/post/send invoice on sale order confirmation.
- Project/task/event:
  - copy CRM lead fields to auto-created project task,
  - create calendar event when task is confirmed,
  - pre-event reminder,
  - post-event thank you,
  - review/photo request,
  - rebooking prompt.
- Payment follow-up:
  - gentle/follow-up/final reminders on unpaid/partial posted customer invoices.

Critical sales-order guard from source:

- Auto-invoice server action explicitly skips website shop orders: `if order.website_id: continue` (`automation_data.xml:731`).
- This means direct shop checkout and internal confirmed service orders are deliberately separate flows.
- Service-line sales orders can create a fixed deposit invoice using configured deposit product/amount.
- Product-only sales orders can create full invoices.
- Guards include zero amount/no partner, duplicate deposit invoice, native automatic invoice setting, and recent website-shop deposit checks.

Deposit configuration:

- `locally_twisted.deposit_product_id` default `32`.
- `locally_twisted.deposit_amount` default `$50.00`.
- `sale.default.down.payment.product` default `32`.

ERPNext receiving requirement:

- Do not let webshop payment automation collide with quote/service deposit automation.
- Direct ecommerce checkout, custom quote deposits, and final invoices need separate states and guards.
- Valid success states include:
  - direct paid order,
  - draft quote/inquiry captured,
  - deposit-required hold,
  - blocked/manual-review state.

## 10. Project/task fulfillment architecture

catalog_data uses sale/project/CRM links for fulfillment:

- `project.task` has event location, venue, crew size, setup duration, materials notes, onsite contacts, gate instructions, special instructions, CRM lead link, calendar event link, internal company photos, bin status, missing items, pickup tracking (`project_task.py`).
- Automation copies CRM lead fields to new tasks when sale_project creates tasks from confirmed sales order lines.
- Automation creates calendar events when tasks enter Confirmed stage.
- Portal readable/writable fields are explicitly controlled; company photos are internal-only.

ERPNext receiving requirement:

- Ecommerce/order handoff must create enough structured fulfillment context for operations, not just collect money.
- Customer-facing portal fields and internal crew/proof fields must be separated.

## 11. Public/security hardening observed in catalog_data source

Public-route hardening exists:

- `/website/info` redirects away to avoid internal exposure (`controllers/main.py:19`).
- Public profile pages redirect away (`controllers/main.py:25`).
- `/terms` placeholder redirects away until real TOS exists.
- `/slides` is auth=user only (`controllers/main.py:36`).

Cart summary hardening:

- Custom QWeb fix guards down-payment/section lines without a product template from crashing cart summary (`website_sale_templates.xml:262+`).

Payment UX asset:

- Payment post-processing JS is added to frontend assets (`ir_asset.xml:134`) and reduces polling interval after payment (`payment_post_processing.js`).

ERPNext receiving requirement:

- Shop module must include negative-space security: what public routes are blocked, not only what pages exist.
- Cart/summary rendering must tolerate service, deposit, delivery, section, and non-product lines without crashing.

## 12. ERPNext/Frappe receiving-layer blueprint from this evidence

Minimum viable but enviable receiving layer:

1. **Catalog Source / Product Contract**
   - Product Template/Item source data.
   - Variant dimensions vs no-variant option dimensions.
   - Media/gallery classification.
   - Sales copy vs website copy seeding.

2. **Product Configurator Runtime**
   - True variants only for SKU/price identity.
   - Multi-select option groups for colors and similar large sets.
   - Image/radio option groups for design/lights.
   - Custom text fields.
   - Per-option price extras.
   - Server-side validation and canonical pricing.

3. **Cart Intent Preservation**
   - Cart line child table for selected options.
   - Separate child table/record for custom text values.
   - Generated display string from structured data.
   - Delivery/service lines distinguishable from product lines.

4. **Quote-first Product Inquiry**
   - Product-context lead/opportunity creation.
   - Event fields and inspiration uploads.
   - Does not force custom jobs into fake checkout.

5. **Checkout + Payment Gate**
   - Cart/order proof before payment intent.
   - Delivery/tax proof before payment intent.
   - Stripe/payment integration only at payment step.
   - No claim of checkout success without transaction/order backend proof.

6. **Automation Guard Layer**
   - Webshop direct orders separated from service/deposit quotes.
   - Duplicate-send guards.
   - Follow-up schedules source-backed and operator-visible.
   - Manual-review/blocked states are valid.

7. **Fulfillment Handoff**
   - Lead/order -> project/task/event fields.
   - Crew/internal notes separate from customer-visible portal fields.
   - Calendar and reminder automation after confirmation, not before intent is clear.

## 13. Immediate build gates for ERPNext

Before importing or launching product rows, ERPNext must prove:

- A product can have 50+ selectable colors without generating variants.
- A cart line can preserve selected colors and custom text in structured backend records.
- A cart/order summary can render product, delivery, deposit/service lines without crashing.
- Product inquiry creates a lead/opportunity with product context and event fields.
- Checkout does not create payment intent until cart/order/delivery/tax state is valid.
- Quote/deposit automation does not double-invoice direct website shop orders.
- Public route/security exposure is checked.
- Evidence is produced as artifacts/verifier output, not chat claims.

## Open blockers

- ERPNext implementation still needs to be mapped against this blueprint.
- Prior ERPNext verifier failure `bench execute failed` was rechecked at 2026-05-10 14:06 MDT and no longer reproduces; latest readiness report is passing with 14 pass / 0 blocked / 1 deferred. Treat the original failure as a transient runtime issue unless it recurs with stdout/stderr preserved.
- Lane E convergence artifact is required in the packet; it should cite this live catalog_data witness rather than the earlier artifactless child completion.
- This pass observed catalog_data payment page but did not submit payment; no end-to-end payment claim is made.
- Existing current cart was observed read-only; this pass did not create a fresh cart/order.

## Bottom line

catalog_data's architecture is not “every customer choice becomes a variant.” The survival pattern is:

> true variant for SKU/price identity + no-variant structured options for customer meaning + backend-preserved cart/order-line intent + quote-first escape hatch + guarded automations.

ERPNext should receive that pattern directly instead of trying to make native Webshop carry all of Locally Twisted's business meaning alone.

---

## Addendum: deeper live catalog_data extraction, 2026-05-10 14:05 MDT

D:2026-05-10 | Check:live catalog_data JSON-RPC read-only extraction 2026-05-10T20:05Z | Confidence:high

This addendum captures the specific backend records GL asked for: product page, variant records, variant/no-variant attribute pages, delivery/payment choices, automations, custom CRM/task fields, and checkout/order-line preservation. No write routes were called.

### A. Classic Arch product template record

`product.template` id `57`:

- Name/display: `Classic Arch`.
- Published fields: `website_published=true`, `is_published=true`.
- Public URL: `/shop/classic-arch-57`.
- Product type: `consu`.
- Sale/purchase: `sale_ok=true`, `purchase_ok=true`.
- Invoice policy: `order`.
- Base list price: `$260`.
- Category: public category id `26`.
- Attribute lines: `[13, 115, 15, 16]`.
- Actual variants: `[91, 92, 93, 94]` only.
- Product template gallery images: `[4,5,6,7,8,9,12,13,14,15]` = 10 images.
- Accessory/optional/alternative products: none on this template.
- Out-of-stock ordering: allowed; threshold observed as `5`.
- Website description and sales description are both present; text intentionally not copied here.

### B. Real variants are only the Arch Size dimension

| Variant id | Display | Variant PTAV | List/base | Variant price extra | Public URL |
|---:|---|---:|---:|---:|---|
| 91 | Classic Arch (20ft) | 201 | $260 | $0 | `/shop/classic-arch-57?attribute_values=1` |
| 92 | Classic Arch (25ft) | 202 | $260 | $65 | `/shop/classic-arch-57?attribute_values=2` |
| 93 | Classic Arch (30ft) | 203 | $260 | $130 | `/shop/classic-arch-57?attribute_values=3` |
| 94 | Classic Arch (35ft) | 204 | $260 | $195 | `/shop/classic-arch-57?attribute_values=4` |

Meaning: the SKU/variant axis is size. Color, design, and LED choices do not create variants; they are option payload.

### C. Attribute lines and product-template attribute values

| Attribute line | Attribute | Sequence | Count | Display | Variant behavior from attribute | Backend proof |
|---:|---|---:|---:|---|---|---|
| 13 | Arch Size | 10 | 4 | pills | `create_variant=always` | PTAVs 201-204 each point to one variant id |
| 115 | latex colors | 11 | 53 | multi | `create_variant=no_variant` | PTAVs 1508-1560 have empty `ptav_product_variant_ids` |
| 15 | Design | 13 | 2 | image | `create_variant=no_variant` | PTAVs 234-235 have empty variant ids |
| 16 | LED Lights | 14 | 2 | image | `create_variant=no_variant` | PTAVs 236-237 have empty variant ids |

#### Arch Size PTAVs

| PTAV | PAV | Name | Extra | Related variant |
|---:|---:|---|---:|---:|
| 201 | 1 | 20ft | $0 | 91 |
| 202 | 2 | 25ft | $65 | 92 |
| 203 | 3 | 30ft | $130 | 93 |
| 204 | 4 | 35ft | $195 | 94 |

#### Design PTAVs

| PTAV | PAV | Name | Extra | Related variant |
|---:|---:|---|---:|---|
| 234 | 43 | Swirl (up to 4 colors) | $0 | none |
| 235 | 44 | Layered (up to 8 colors) | $0 | none |

#### LED PTAVs

| PTAV | PAV | Name | Extra | Related variant |
|---:|---:|---|---:|---|
| 236 | 45 | No Lights | $0 | none |
| 237 | 46 | Add LED Lights | $50 | none |

#### Full latex color PTAV list from Classic Arch

All are `display_type=multi`, `price_extra=0`, `is_custom=false`, and have no related variant ids.

| PTAV | PAV | Color |
|---:|---:|---|
| 1508 | 177 | Reflex Champage |
| 1509 | 178 | Reflex Truffle |
| 1510 | 179 | Dusk Cream |
| 1511 | 180 | Dusk Green Tea |
| 1512 | 181 | Dusk Blue |
| 1513 | 182 | Dusk Lilac |
| 1514 | 183 | Dusk Rose |
| 1515 | 187 | Teal |
| 1516 | 188 | Blue Slate |
| 1517 | 189 | Smoke Grey |
| 1518 | 171 | Reflex Silver |
| 1519 | 172 | Reflex Gold |
| 1520 | 173 | Reflex Blue |
| 1521 | 174 | Reflex green |
| 1522 | 175 | Reflex Violet |
| 1523 | 176 | Reflex Red |
| 1524 | 117 | White |
| 1525 | 118 | black |
| 1526 | 119 | Red |
| 1527 | 120 | Orange |
| 1528 | 121 | yellow |
| 1529 | 123 | raspberry |
| 1530 | 124 | fuchsia |
| 1531 | 126 | bubble Gum |
| 1532 | 127 | eucalyptus |
| 1533 | 128 | Forest |
| 1534 | 129 | Shamrock |
| 1535 | 130 | Wintergreen |
| 1536 | 131 | Lime |
| 1537 | 132 | LT Blue |
| 1538 | 133 | Periwinkle |
| 1539 | 134 | Royal Blue |
| 1540 | 136 | Robin's Egg |
| 1541 | 137 | Deep Teal |
| 1542 | 138 | Honey |
| 1543 | 139 | Violet |
| 1544 | 140 | Orchid |
| 1545 | 141 | Lilac |
| 1546 | 142 | Chocolate |
| 1547 | 143 | Brown |
| 1548 | 145 | Latte |
| 1549 | 146 | Pastel Pink |
| 1550 | 147 | Pastel Blue |
| 1551 | 148 | Pastel Green |
| 1552 | 149 | Pastel Purple |
| 1553 | 150 | Pastel Yellow |
| 1554 | 151 | Pastel Melon |
| 1555 | 152 | Grey |
| 1556 | 153 | Clear |
| 1557 | 154 | Blush |
| 1558 | 184 | Blue slate |
| 1559 | 185 | Smoke grey |
| 1560 | 186 | Empowermint |

ERPNext target: this entire list belongs in an option-group / product-configuration table, not in an Item Variant matrix.

### D. Delivery carriers and service item mapping

Live `delivery.carrier` records matching checkout:

| Carrier id | Name | Type | Product/service item | Fixed price | Published |
|---:|---|---|---|---:|---|
| 4 | Pickup (Free) | fixed | `[DELIVERY_PICKUP] Pickup` | $0 | true |
| 5 | Standard Delivery | fixed | `[DELIVERY_STANDARD] Standard Delivery` | $15 | true |
| 6 | Park City Delivery | fixed | `[DELIVERY_PARK_CITY] Park City Delivery` | $50 | true |
| 7 | Out-of-Area Quote | fixed | `[DELIVERY_OUT_OF_AREA] Out-of-Area Delivery Quote` | $35 | true |
| 1 | Standard delivery | fixed | `[Delivery_007] Standard delivery` | $0 | true |

The fifth `Standard delivery` is an catalog_data/default-ish published carrier observed in the live DB, while the local LT data file defines the capitalized Standard Delivery/Pickup/Park City/Out-of-Area carriers. ERPNext needs an explicit delivery-service mapping and a rule to avoid duplicate/confusing checkout choices.

### E. Payment provider state observed without submitting payment

Live provider list shows:

- Stripe: `code=stripe`, `state=test`, `is_published=true`, journal Bank, capture manually false.
- Cash on Delivery: `code=custom`, `state=enabled`, `is_published=true`, journal Bank, but payment availability report on the live payment page said COD was not allowed for the current order context.
- Other providers are installed provider records but disabled/unpublished.

Public payment page proof:

- Form mode: `payment`.
- Amount observed from current draft order: `$74.75`.
- Transaction route pattern: `/shop/payment/transaction/<order_id>`.
- Landing route: `/shop/payment/validate`.
- Stripe Elements loaded with test-mode provider.

No transaction was submitted. No payment success claim is made.

### F. Active automation architecture

Live active automation count observed: `18`.

Major active rules:

- Lead automations: form auto-acknowledgment, booking confirmation with `x_booking_confirmed=false` guard, anniversary init/reminder/rollover, booking-contact auto-create/link, new-booking notification.
- Sales-order automation: auto-create/post/send invoice on confirmed SO.
- Task automations: copy CRM lead fields to new task, create calendar event when task confirmed, pre-event reminder, post-event thank you, review/photo request, rebooking prompt.
- Invoice/payment follow-up: gentle/follow-up/final reminders for unpaid or partially paid customer invoices.
- Loyalty coupon welcome.

Source-critical guard confirmed in `automation_data.xml`: the custom SO invoice automation skips website shop orders with `if order.website_id: continue`. That is the line preventing direct ecommerce checkout from colliding with quote/service deposit invoice automation.

### G. Custom field footprint: CRM and task are the real receiving backend

Live custom-field read and local model source agree on the business shape:

CRM lead fields include service/event date/location/venue, crew size, setup duration, service choice, occasion type, event time, guest count, hours needed, indoor/outdoor, shade required, twister/painter counts, artist/setup times, colors, decor types, multi-service `x_services`, notes per service category, booking-confirmed guard, source channel, client type, and task linkage.

Project task fields include event location, venue, crew size, setup duration, materials/equipment notes, onsite contacts, gate/entry instructions, special instructions, related opportunity, calendar event link, internal company photos, bin status, missing items, pickup scheduling/completion.

ERPNext target: product pages and checkout must feed CRM/Opportunity/Project/Event context, not just Website Item and Sales Order rows.

### H. Current ERPNext verifier recheck

Parent re-ran:

```bash
python scripts/verify/product_page_architecture_readiness.py --report output/product-page-architecture-readiness-infrastructure-research-20260510.json
```

Result at 2026-05-10 14:06 MDT:

- Exit code: `0`.
- `ok=true`.
- `technical_architecture_ok=true`.
- `import_reopen_ok=true`.
- Summary: `pass=14`, `blocked=0`, `partial=0`, `deferred=1`, `info=0`.
- Deferred item: finance/bank/payment integration remains explicitly backburnered.

This clears the specific stale `bench execute failed` blocker for now. It does not clear the no-payment-submission catalog_data boundary and does not authorize product purge/import/public launch by itself.

---

## Addendum: catalog-wide backend pattern extraction, 2026-05-10 14:12 MDT

D:2026-05-10 | Check:live catalog_data JSON-RPC catalog summary 2026-05-10T20:12Z | Confidence:high

To verify Classic Arch is not a one-off, a live read-only catalog summary was extracted from `product.template`, `product.template.attribute.line`, and `product.attribute`.

Counts:

- Saleable product templates checked: `128`.
- Published templates: `58`.
- Templates with attributes: `59`.
- Templates with at least one `create_variant=no_variant` attribute: `48`.
- Templates with at least one `display_type=multi` attribute: `45`.
- Option-heavy products, meaning a multi/no-variant group or 10+ option values: `49`.

Representative option-heavy products:

| Product id | Product | Published | Real variants | Option pattern |
|---:|---|---:|---:|---|
| 14 | Baby Shower Combination Photo opt | yes | 1 | `latex colors`: 53, multi, no-variant |
| 19 | Classic Organic Balloon Garland | yes | 3 | `Garland Length`: 3 variants + `latex colors`: 53 no-variant |
| 22 | Number Balloon Columns | yes | 7 | `Number colors`: 7 variants + `Number selection`: 10 no-variant + `latex colors`: 53 no-variant |
| 39 | Halloween arch | yes | 4 | `Arch Size`: 4 variants + `latex colors`: 53 no-variant |
| 52 | Premium Organic Garland | yes | 3 | `Garland Length`: 3 variants + `latex colors`: 53 no-variant |
| 53 | Premium Organic Arch | yes | 8 | `Arch Size`: 4 variants + `Add ons`: 2 variants + `latex colors`: 53 no-variant |
| 54 | Pemium Organic Column | yes | 12 | `Column Height`: 6 variants + `Add ons`: 2 variants + `latex colors`: 53 no-variant |
| 57 | Classic Arch | yes | 4 | `Arch Size`: 4 variants + `latex colors`: 53 no-variant + `Design`: 2 no-variant + `LED Lights`: 2 no-variant |
| 58 | Classic Column | yes | 36 | `Column Height`: 6 variants + `topper`: 6 variants + `latex colors`: 53 no-variant |
| 65 | Classic Organic columns | yes | 6 | `Column Height`: 6 variants + `latex colors`: 53 no-variant |
| 71 | Baby Shower Garland | yes | 3 | `Garland Length`: 3 variants + `latex colors`: 53 no-variant |
| 74 | Balloon Drop | yes | 3 | `Drop Size`: 3 variants + `latex colors`: 53 no-variant |
| 99 | Classic Organic Arch | yes | 12 | `Arch Size`: 4 variants + `Add ons`: 3 variants + `latex colors`: 53 no-variant |
| 104 | Missionary Homecoming Display | yes | 1 | `latex colors`: 53, multi, no-variant |
| 115-119 | Character bouquets | yes | 3 each | `Bouquet Size`: 3 variants + `Add Foil Number`: 10 no-variant |

Conclusion: catalog_data's catalog architecture repeatedly uses the same pattern, not just Classic Arch. Variant axes stay small and commercially meaningful; large/customer-choice dimensions are no-variant option payloads.

ERPNext implication: the receiving layer must be generalized across the catalog, not hard-coded for Classic Arch.

## Addendum: cart/checkout/payment DOM route proof, 2026-05-10 14:13 MDT

D:2026-05-10 | Check:live catalog_data public cart/checkout/payment DOM read-only 2026-05-10T20:13Z | Confidence:high

The current browser session has an existing draft cart/order. It was inspected without mutating it. Customer/account/address specifics are redacted here.

Cart page `/shop/cart`:

- Cart summary shows one product line: `Graduation bouquet`.
- Line displays no-variant color choices: `Wintergreen`, `Royal Blue`.
- Line displays a custom text/name field; value redacted here.
- Product page link includes `attribute_values=268`.
- Checkout link is `/shop/checkout?try_skip_step=true`.
- Promo form posts to `/shop/pricelist`.
- Remove/save-for-later controls are present but were not clicked.

Checkout page `/shop/checkout?try_skip_step=true`:

- Delivery form id: `o_delivery_form`.
- Delivery selection uses five radio inputs named `o_delivery_radio`.
- Observed options:
  - `Standard delivery` / free,
  - `Pickup (Free)` / free,
  - `Standard Delivery` / `$15.00`,
  - `Park City Delivery` / `$50.00`,
  - `Out-of-Area Quote` / `$35.00`.
- Confirm link points to `/shop/payment`.
- Back link points to `/shop/cart`.
- Order summary shows product subtotal, delivery line, tax, and total.
- Address/account context exists on the page and was intentionally redacted.

Payment page `/shop/payment`:

- Payment form id: `o_payment_form`.
- Form dataset mode: `payment`.
- Amount in dataset: `74.75` for the current draft order.
- Currency id: `1`.
- Partner id exists but is not repeated here.
- Transaction route pattern: `/shop/payment/transaction/<order_id>`.
- Landing route: `/shop/payment/validate`.
- Access token exists in the DOM dataset and is intentionally not recorded.
- Selected payment option:
  - method code: `card`,
  - provider code: `stripe`,
  - provider state: `test`.
- Tokenization checkbox: `o_payment_tokenize_checkbox`, unchecked.
- Submit button text: `Pay now`; it was not clicked.

ERPNext implication: the checkout process should be modeled as explicit state transitions:

1. Product-page configuration payload.
2. Cart line structured preservation.
3. Checkout delivery selection.
4. Tax/total calculation.
5. Payment form/payment-intent creation at the final route only.
6. Confirmation/validation route only after payment action.

No `Pay now`, add-to-cart mutation, delivery-change mutation, remove/save-for-later, promo apply, inquiry submit, or form submit was performed in this pass.
