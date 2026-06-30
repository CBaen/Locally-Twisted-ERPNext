# Live Read-Only API Audit - Large head Missionary

Date: 2026-06-30

Status: live authenticated read-only proof complete for the incident product. This is not repair approval, not release approval, not cache approval, not provider/payment approval, and not customer-message approval.

## User Timeline

Guiding Light reported:

- Live Desk route used: `https://locallytwisted.com/app/lt-product-blueprint/large-head-missionary`.
- Product Setup record: `large-head-missionary`.
- Price fields changed from `175` to `125`.
- Base Checkout Price was additionally toggled `125 -> 120 -> 125`.
- Each save showed a saved confirmation.
- Most recent save: 2026-06-30 at about 1:43 AM America/Denver.
- Account context: `locallytwisted.com`.
- The public page did not reflect the expected price change.
- The Product Setup "About This Design" style copy differs from the public product page copy.

## Proof Mode

Live proof used:

- Frappe Cloud API credentials from approved local `.env`, without printing values.
- Frappe Cloud `press.api.site.login` to obtain a temporary live site session.
- Live ERPNext `GET /api/resource/...` requests through `https://locallytwisted.com`.
- Public product-page `GET`.

Blocked in this audit:

- no ERPNext writes;
- no cache clear;
- no deploy or site update;
- no migration/import/patch;
- no provider/payment/DNS/Frappe Cloud mutation;
- no cart, checkout, payment session, invoice, receipt, or customer message;
- no secrets or session ids printed or stored.

Evidence file:

- `/tmp/lt-live-large-head-missionary-api-audit-2026-06-30.json`

Reusable helper:

```bash
python scripts/dev/lt_live_readonly_product_api_audit.py \
  --output /tmp/lt-live-helper-proof.json
```

## Confirmed Live Backend Facts

| Area | Live Read-Only Evidence |
|---|---|
| Product Setup row | `LT Product Blueprint` `large-head-missionary` exists and is linked to target item `large-head-missionary` and Website Item `WEB-ITM-0039`. |
| Owner save proof | Product Setup modified `2026-06-30 01:43:01.382176` by `locallytwisted@gmail.com`. |
| Product Setup base price | `base_price: 125.0`. |
| Product Setup status | `publish_status: Local Preview Ready`, `validation_status: Ready For Local Preview`, `ready_for_live: 0`, `shop_visibility: Visible in shop`. |
| Product Setup exact prices | 30 `price_rows`, all `125.0`, modified by `locallytwisted@gmail.com` at the same 1:43 timestamp. |
| Website Item | `WEB-ITM-0039`, published, route `shop-items/bouquets/large-head-missionary`, modified `2026-06-29 01:19:25.229958` by `Administrator`. |
| Template Item | `large-head-missionary`, enabled variant template, modified `2026-05-17 16:09:50.270338` by `Administrator`. |
| Variant Items | 30 variants found. |
| Item Prices | 30 `Standard Selling` Item Price rows found, all `175.0`, modified on 2026-04-30 by `Administrator`. |
| Public page | Public HTML still contains `$ 175.00` and does not contain `$125` / `125.00` as the customer-visible product price. |

## Price Authority Finding

The owner save worked. Product Setup is not the current sellable price authority.

Live split:

- Product Setup base price: `125.0`.
- Product Setup exact checkout price rows: `125.0`.
- Public Product Setup JSON: `commerce.base_price: 125.0`.
- Sellable `Item Price` rows: `175.0`.
- Public customer-visible starting price: `from $ 175.00`.

Source resolver proof:

- `/shop` joins `Website Item` to `Item Price` and then applies variant starting price logic in `www/shop.py`.
- Product page visible starting price calls `get_variant_starting_price_display`, which reads enabled variant `Item` rows joined to `Item Price` in `product_options.py`.
- Cart resolution reads `Item Price` in `api/cart.py` and explicitly ignores client-supplied prices.

Conclusion: Product Setup price edits save successfully but do not currently update the `Item Price` rows that drive public listing, product selection, cart, and checkout pricing.

## Copy Authority Finding

The public product page is not using Product Setup top-level copy as the server-rendered public copy.

Live split:

- Product Setup `product_story`: starts with "A bouquet for the day someone leaves on a mission..."
- Product Setup `product_details`: starts with "Hand-tied missionary send-off bouquet..."
- Website Item `lt_brand_description`: starts with "A larger-than-life missionary balloon gift..."
- Website Item `lt_product_details`: starts with "Personalized large-head missionary balloon gift..."
- Public page visible story renders from `Website Item.lt_brand_description`.
- Public page visible details render from `Website Item.lt_product_details`.
- Product Setup `content_rule_rows`: `0`, so no approved selected-copy rules are currently projected into the public Product Setup runtime for this product.

Source resolver proof:

- `item_details.html` renders visible product story from `doc.lt_brand_description`.
- `item_details.html` renders "What's Included" from `doc.lt_product_details`.
- Product Setup can expose selected copy through `content_rules`, but this live product has no content rule rows.

Conclusion: Product Setup copy edits save successfully, but top-level Product Setup copy does not currently project to the server-rendered public product copy.

## Root Cause Classification

Confirmed:

- This is not a failed Desk save.
- This is not simply public cache, because live read-only API and public GET agree on the split authority.
- This is not local-vs-live drift for the owner save; live Product Setup reflects the owner edit.

Root cause:

**Product Setup is an owner-editable authoring surface, but it is not wired as the write-through authority for every customer-facing commerce field.**

For this product:

- Product Setup price changed.
- Sellable `Item Price` rows did not change.
- Public/customer commerce uses `Item Price`.
- Product Setup top-level copy differs.
- Public/customer copy uses Website Item fields.

## Required Fix Direction

Do not patch this one product by hand as the final answer. The durable fix needs an owner-publish/apply contract:

- Save can remain a draft/preview action, but it must say that plainly if it does not publish.
- A separate explicit owner action can apply Product Setup to Website Item, Item Price, Website Item copy, gallery/media, and variant rows.
- Or Product Setup must become the direct runtime authority for those public surfaces.
- Either path must fail loudly when Product Setup and customer-facing authority disagree.

Until that exists, owner-facing Product Setup saves can show success while public commerce remains unchanged.

## Still Blocked

Before any repair:

- Capture rollback target for affected live rows.
- Decide whether Product Setup should be direct runtime authority or publish/apply authority.
- Decide which copy field is customer-approved truth.
- Build a no-write preview that shows exactly which public rows would change.
- Add a live read-only verifier that fails when Product Setup price/copy and public sellable authority disagree after an owner save.

Stop before repair, cache clear, deploy, provider/payment work, or customer-facing action.
