# Lane C — Cart / Checkout / Silent-Failure Intent Preservation Audit

Date: 2026-05-10  
Rollback anchor: `lt-ecommerce-audit-pre-dispatch-20260510-0841` (`264c6553acd5708ecdb498cb6fa6a5c594260abc`)  
Repo: `/home/guidingl/projects/Built_by_Cameron/_CLIENTS/locally-twisted`

## Status block

- **Lane:** C — Cart / Checkout / Silent-Failure Auditor.
- **Environment/auth context before clicking:** local/test ERPNext/Frappe stack at `http://localhost:8081`, Docker compose project `locally-twisted-erpnext-v15`; public guest product/cart/checkout pages inspected with Playwright. Existing Chrome/OpenClaw browser was not used for state-changing actions; it was already on an external IP tab and local navigation was blocked/aborted by browser policy, so runtime browser evidence below comes from local Playwright against `localhost:8081` only.
- **Destination version evidence:** `docker ps` showed local containers, including `locally-twisted-erpnext-v15-frontend-1` on `0.0.0.0:8081->8080`. `docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend version` returned `erpnext 15.105.0`, `frappe 15.106.0`, `locally_twisted 0.0.1`, `payments 0.0.1`, `webshop 0.0.1`.
- **Sources inspected:** current repo code and templates under `apps/locally_twisted/locally_twisted/`, browser observation JSON under `output/lane-c-*.json`, and verifier outputs listed below.
- **Commands/actions run:** code/search/DB inspection; Playwright local page observations; verifiers: `cart_checkout_contract.py`, `product_page_runtime_contract.py`, `npm run test:checkout-experience`, `npm run test:product-quote-first`, `checkout_fulfillment_contract.py`, `checkout_lead_conversion_contract.py`, `product_add_on_dependency_contract.py`, `product_add_on_approval_packet.py`, `product_quote_customization_contract.py`.
- **Records created/cleaned:** verifier-created test records were rollback-safe. Runtime verifier reported `rolled_back: true` for `SAL-ORD-2026-00021`, `SAL-ORD-2026-00022`, `ACC-SINV-2026-00003`, `ACC-SINV-2026-00004`, `CRM-LEAD-2026-00066`, `SAL-QTN-2026-00001`; checkout lead verifier reported rollback of generated Lead/Contact/Customer/Sales Order/Payment Request. Follow-up `frappe.db.exists` checks for those named records returned empty.
- **Key findings:** the current proof slice preserves ready-to-order configured intent through product page → cart display → checkout resolver → Sales Order Item fields → Sales Invoice Item fields. Same-SKU configured rows stay separate. Confirmed `foil_number` add-on expands to its own priced line and preserves selected value. Quote-first product pages route to `/contact` with structured payload. Unsupported/unapproved add-ons and quote-first checkout attempts fail loudly.
- **Blockers:** full catalog launch remains blocked outside the proof slice: all 53 published Website Items currently store `lt_product_page_type=needs_review` and `lt_commerce_lane=needs_review`; runtime inference makes representative pages work, but stored catalog classification/import approval is not complete. Source add-on families beyond `foil_number` are review-only/quote-only until approved.
- **Confidence:** high for the named proof paths and verifiers; medium for full-catalog safety because this lane did not deep-checkout every product and did not run Lane F synthesis.

## Product/category inventory enumerated first

DB query: `frappe.client.get_list` on `Website Item` with `published=1`, fields `name,item_code,web_item_name,route,item_group,published,lt_product_page_type,lt_commerce_lane`, limit 200.

- Total published Website Items: **53**.
- Groups: Arches 10; Bouquets 16; Columns 10; Deliveries 1; Drops 1; Garlands 4; Get-Well Bouquets 3; Grab & Go 2; Seasonal & Specialty 1; Stands & Easels 2; Table Decor 3.
- Stored page/lane fields: `needs_review` for all 53 `lt_product_page_type`; `needs_review` for all 53 `lt_commerce_lane`.
- Representative runtime classes tested:
  - Ready-to-order simple/configured: `unicorn-bouquet` / variant `unicorn-bouquet-SMA`.
  - Ready-to-order simple single-SKU: `mothers-day-bouquet`.
  - Quote-first complex: `classic-arch`.
  - Quote-first/unsupported negative: `6-color-rainbow-arch-20F`, review-only add-on `plush_add_ons`, ineligible `foil_number` on `mothers-day-bouquet`.

## Pages/actions clicked

Local Playwright only; no live payment or email submission.

- `/shop-items/bouquets/unicorn-bouquet`: selected first `Bouquet Size`, enabled/selected `Foil number`, entered `12`, clicked `#lt-add-to-cart-variant`; this wrote local cart state only.
- `/shop-items/arches/classic-arch`: selected `Arch Size=20ft`, selected `latex colors=Reflex Gold`, filled color/design notes, clicked `.js-lt-product-quote-request`; browser navigated to `/contact` and populated hidden product quote payload. No Lead was submitted by this browser action.
- `/cart` and `/checkout`: seeded localStorage cart with the configured Unicorn line and observed visible labels/order summary; did not submit checkout or enter payment.

Evidence files generated:

- `output/lane-c-browser-observations.json`
- `output/lane-c-payload-examples.json`
- `output/lane-c-cart-checkout-visible-labels.json`

## Product page payload examples

### Ready-to-order configured payload: Unicorn Bouquet + foil number

After selecting `Bouquet Size=Small...` and `Foil number=12`, the local cart stored:

```json
{
  "item_code": "unicorn-bouquet-SMA",
  "qty": 1,
  "configuration": {
    "schema_version": "lt-product-config-v1",
    "item_code": "unicorn-bouquet-SMA",
    "website_item_code": "unicorn-bouquet",
    "selected_options": {
      "Bouquet Size": "Small — 1 featured foil balloon, 2 coordinating foil balloons, 7 latex balloons"
    },
    "add_ons": [
      {"key": "foil_number", "label": "Foil number", "value": "12", "quantity": 2}
    ],
    "customizations": []
  }
}
```

The `line_key` includes the item code plus canonical JSON configuration, so the selected value participates in cart identity.

### Quote-first payload: Classic Arch

Clicking quote request carried this hidden `/contact` payload:

```json
{
  "schema_version": "lt-product-config-v1",
  "source": "product-page-quote",
  "website_item_code": "classic-arch",
  "web_item_name": "Classic Arch",
  "product_page_type": "complex_custom_product",
  "commerce_lane": "quote_first",
  "selected_options": {"Arch Size": "20ft", "latex colors": "Reflex Gold"},
  "add_ons": [],
  "customizations": [
    {"key": "color_notes", "label": "Color notes", "value": "Reflex Gold and Navy"},
    {"key": "design_notes", "label": "Design notes", "value": "Frame the stage entrance."}
  ],
  "needs_operator_review": true
}
```

## Cart line identity and same-SKU configured-line behavior

Verifier: `python scripts/verify/cart_checkout_contract.py` passed all checks.

Relevant code evidence:

- `apps/locally_twisted/locally_twisted/product_page_runtime.py:191` defines `cart_line_key(item_code, client_configuration)`.
- `apps/locally_twisted/locally_twisted/api/cart.py:236-262` carries `cart_line_key`, `display_lines`, line totals, and add-on totals in the cart API.
- `apps/locally_twisted/locally_twisted/www/checkout.py:434-487` canonicalizes `items_json` and keeps rows keyed by cart line key.
- `apps/locally_twisted/locally_twisted/www/lt_cart.html:327` and `www/checkout.html:543` show loud customer-safe mismatch text instead of silently matching by item code.

Observed cart/checkout labels for `unicorn-bouquet-SMA` + foil `12`:

- `/cart`: `Unicorn Bouquet`, selected Bouquet Size, `Foil number: 12 - qty 2 - $12 each - $24 total`, line total `$59`.
- `/checkout`: order summary preserved `Qty 1`, Bouquet Size, `Foil number: 12 - qty 2 - $12.00 each - $24.00 total`, total `$59.00`.

`cart_checkout_contract.py` specifically proved two `unicorn-bouquet-SMA` rows with different foil values return 2 cart rows and distinct `cart_line_key`s.

## Add-on line expansion behavior

Verifier evidence:

- `cart_checkout_contract.py`: passed `check_configured_same_sku_cart_lines_stay_separate_and_visible`, `check_multi_digit_add_on_quantity_and_total_are_visible`, `check_add_on_eligibility_rejects_unapproved_product`, and `check_review_only_source_add_ons_route_to_quote_not_checkout`.
- `product_page_runtime_contract.py`: passed and reported add-on Sales Order `SAL-ORD-2026-00022`, add-on Sales Invoice `ACC-SINV-2026-00004`, `rolled_back: true`.
- `product_add_on_dependency_contract.py`: `confirmed_add_ons: 1`, `review_only_source_add_ons: 4`.
- `product_add_on_approval_packet.py`: affected review-only products 9; approved-for-checkout count 0 for review axes; defaults `quote_only_until_approved`.

Relevant code evidence:

- `product_page_runtime.py:37-62` defines `FOIL_NUMBER_ELIGIBLE_WEBSITE_ITEMS` and maps `foil_number` to `ADDON-FOIL-NUMBER`.
- `product_page_runtime.py:342-420` builds add-on Sales Order lines and links them back to the parent product payload.
- `product_page_runtime.py:514` starts `_validated_checkout_add_ons`, enforcing eligibility/review-only behavior.

Current supported paid add-on proof: `foil_number` only. Source add-on families `Add Bouquet`, `Add ons`, `Orbz toppers`, and `Plush add ons` are not checkout-approved.

## Checkout translation into Sales Order Item rows

Verifier evidence:

- `product_page_runtime_contract.py` passed. It creates/submits rollback-safe Sales Orders and verifies each Sales Order Item retains runtime fields.
- The same verifier checks `sales_order_line_configuration_fields` output before Sales Order insert.
- `checkout_fulfillment_contract.py` passed with rollback.
- `checkout_lead_conversion_contract.py` passed with rollback, proving checkout-created Lead/Contact/Customer/Sales Order/Payment Request behavior without leaving records.

Relevant code evidence:

- `product_page_runtime.py:280-325` builds line fields: configuration JSON, summary, schema version, product page type, and product template item.
- `www/checkout.py:494-536` resolves cart items into server-priced Sales Order lines and applies `sales_order_line_configuration_fields`.
- `www/checkout.py:964-1044` creates the Sales Order and Payment Request; payment is Stripe-hosted and was not submitted in this audit.

Important wording: I am not saying “checkout passed” generically. The backend record proof was Sales Order Item configuration field preservation, add-on line expansion, Payment Request creation in rollback-safe verifier, and no surviving generated records after rollback.

## Invoice copying behavior

Verifier evidence:

- `product_page_runtime_contract.py` passed and reported rollback-safe Sales Invoice names `ACC-SINV-2026-00003` and `ACC-SINV-2026-00004`.
- The verifier calls ERPNext `make_sales_invoice`, then `copy_sales_order_line_configuration_to_invoice`, inserts/submits invoice, and verifies every Sales Invoice Item received every line configuration field.

Relevant code evidence:

- `product_page_runtime.py:428` defines `copy_sales_order_line_configuration_to_invoice(invoice_doc, sales_order_name)`.
- `www/payment_success.py:25` states payment success creates Sales Invoice from Sales Order; `www/payment_success.py:324-330` imports and calls the copy helper before invoice submission.

No live Stripe session was paid and no live email was sent.

## Quote-first rejection / handoff paths

Browser and verifier evidence:

- `classic-arch` public product page rendered quote-first controls, no normal add-to-cart controls, and carried selected Arch Size/color/design notes to `/contact` as a structured payload.
- `npm run test:product-quote-first` passed 4 tests: desktop/mobile quote-first contact payload and desktop/mobile ready-to-order controls/add-ons.
- `product_quote_customization_contract.py` passed with `color_recipe_count: 1`, draft Quotation rollback.
- `product_page_runtime_contract.py` checks quote-first blocks checkout with a ValidationError containing “needs a quote”.
- `cart_checkout_contract.py` checks `6-color-rainbow-arch-20F` is rejected from cart as `quote_required`.

Relevant code evidence:

- `templates/generators/item/item_quote_first.html:181-189` builds `lt-product-config-v1` quote payload with selected options/add-ons/customizations.
- `www/checkout.py:518-524` rejects unavailable/quote-first cart items with customer-safe copy.
- `api/cart.py:59-61` maps missing reasons to quote/choose-option messages; `api/cart.py:111` returns `quote_required` for quote-first products.

## User-facing and operator-facing error states

Customer-facing/fail-loud states observed or verified:

- Quantity too high: `Tiny snag: one cart line has more than 99 items...` (`www/checkout.py:426-428`; verifier passed).
- Bad cart details: `Tiny snag: the cart details did not come through cleanly...` (`www/checkout.py:451-456`).
- Cart/checkout server mismatch: `Tiny snag: one configured cart line did not match the server...` (`www/lt_cart.html:327`, `www/checkout.html:543`; verifier passed).
- Quote-first item in checkout: `Tiny snag: this design needs a quote before checkout...` (`www/checkout.py:518`; verifier passed).
- Checkout setup fallback strips internal details from customer text: `Tiny snag: we could not start checkout just now...` (`www/checkout.html:248`; cart verifier guards against leaking internal item codes/custom field names).

Operator/backend evidence:

- Sales Order Item, Sales Invoice Item, Quotation Item, Lead product quote fields, and child quote rows are verified by `product_page_runtime_contract.py`.
- `product_quote_customization_contract.py` verifies quote color recipe preservation into draft Quotation JSON.
- `checkout_lead_conversion_contract.py` verifies checkout lead/customer/order/payment-request conversion behavior and rollback.

## Negative tests for unsupported options/add-ons

Passed negative tests:

1. Direct template `unicorn-bouquet` and `6-color-rainbow-arch` are not cartable until options are chosen (`reason=choose_options`).
2. `6-color-rainbow-arch-20F` is rejected as `quote_required`.
3. Applying `foil_number` to unapproved `mothers-day-bouquet` fails with `this add-on is not available for this product`.
4. Applying review-only source add-on `plush_add_ons` to `unicorn-bouquet-SMA` fails with `this add-on needs a quote before checkout`.
5. Old/malformed cart schema fails loudly (`older option format`) in `product_page_runtime_contract.py`.
6. Over-limit quantities fail loudly before checkout.

## Commands run

```bash
git status --short --branch
git rev-parse HEAD
git tag --points-at HEAD
docker ps --format "table {{.Names}}/t{{.Image}}/t{{.Status}}/t{{.Ports}}"
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend version
python scripts/verify/cart_checkout_contract.py
python scripts/verify/product_page_runtime_contract.py
npm run test:checkout-experience
npm run test:product-quote-first
python scripts/verify/checkout_fulfillment_contract.py
python scripts/verify/checkout_lead_conversion_contract.py
python scripts/verify/product_add_on_dependency_contract.py
python scripts/verify/product_add_on_approval_packet.py
python scripts/verify/product_quote_customization_contract.py
```

Additional read-only DB/API checks used `frappe.client.get_list`, `locally_twisted.api.cart.get_cart_items`, and `frappe.db.exists` through `bench execute`.

## Cleanup / rollback evidence

- `product_page_runtime_contract.py`: `rolled_back: true`; follow-up `frappe.db.exists` for `SAL-ORD-2026-00021`, `SAL-ORD-2026-00022`, `ACC-SINV-2026-00003`, `ACC-SINV-2026-00004`, `CRM-LEAD-2026-00066`, and `SAL-QTN-2026-00001` returned empty.
- `checkout_fulfillment_contract.py`: `rollback: verifier rolled back generated records`.
- `checkout_lead_conversion_contract.py`: `rollback: verifier rolled back all generated records`; follow-up `frappe.db.exists` for `ACC-PRQ-2026-00020` returned empty.
- Browser/Playwright actions only changed localStorage/session state in headless browser contexts; no submitted checkout, no payment, no email.

## Current launch-safety conclusion for Lane C

The runtime receiving path is **technically proven for the representative proof slice**: ready-to-order configured product + confirmed `foil_number` add-on + quote-first complex product + negative add-on/quote-first cases. Customer intent survives through the backend surfaces that matter for those cases.

This is **not** a full-catalog launch green. Stored Website Item classification remains `needs_review` across all 53 published items, only one add-on family is checkout-approved, and this lane intentionally avoided live payment/email and did not deep-checkout every product. Keep product import/public launch behind synthesis gates.
