D:2026-05-10 | Check:local docs/source 2026-05-10 | Confidence:[CONFIDENT]

# Cart / Checkout Verification Gates — Intent Preservation

Purpose: define the minimum evidence gates before claiming Locally Twisted ERPNext ecommerce preserves customer intent from product page through cart, checkout, and backend records.

Scope basis:

- Existing audit: `workstreams/ecommerce-audit/cart-checkout-intent-preservation-audit-2026-05-10.md`.
- Current source inspected: `apps/locally_twisted/locally_twisted/product_page_runtime.py`, `apps/locally_twisted/locally_twisted/api/cart.py`, `apps/locally_twisted/locally_twisted/www/checkout.py`.
- This artifact defines gates only. It is not a launch pass, payment pass, full-catalog pass, or code-change record.

Hard stop rules:

- No launch claim unless every required gate below has a dated witness path.
- No live payment submission or real email send is required for these gates; use local/test proof and stop before external effects.
- No product delete/purge/import should be used to satisfy these gates.

## Gate 1 — Customer intent payload requirements

A product page may be considered cart/checkout-capable only when the captured payload proves all customer choices survive as structured data.

Required proof:

1. Browser witness for each representative product family showing selected controls before submit/add-to-cart.
2. Captured cart payload with:
   - `schema_version: lt-product-config-v1`.
   - selected sellable `item_code` / variant item code.
   - source `website_item_code` where relevant.
   - `selected_options` with customer-facing option labels and chosen values.
   - `add_ons` with key, label, value, quantity, and pricing basis when applicable.
   - `customizations` with key, label, and value when free-text/detail fields exist.
   - explicit quote/review flag when the product cannot go through direct checkout.
3. Server-side normalization proof that malformed, missing, stale, or oversized configuration fails loudly instead of silently dropping options.
4. Cart and checkout display witness showing the same options/add-ons/customizations in customer-visible language.
5. Backend record witness showing the same payload or summary stored on downstream document items.

Pass language allowed only after all evidence exists:

- "For the named representative payload, selected options/add-ons/customizations are preserved from product page to cart, checkout resolver, and backend item fields."

## Gate 2 — Same-SKU configured line identity requirements

Same item/variant code does not prove same customer intent. Configured line identity must include canonical configuration, not just `item_code`.

Required proof:

1. Unit/runtime verifier showing `cart_line_key(item_code, configuration)` changes when the selected configuration changes.
2. Cart API witness showing two lines with the same `item_code` but different configurations remain two cart rows.
3. Checkout resolver witness showing `items_json` coalesces only exact cart-line-key matches and preserves order.
4. Browser/cart witness showing both configured lines are visible with distinct labels.
5. Backend Sales Order witness showing both configured rows create distinct Sales Order Items or a clearly linked parent/add-on structure with no choice loss.

Negative requirement:

- Same-SKU rows with different foil numbers, colors, sizes, dates, or notes must not merge silently.

Pass language:

- "Same-SKU configured lines stayed separate for the tested configuration differences."

## Gate 3 — Variant / option / add-on preservation requirements

A direct-checkout product family must prove every supported choice is either preserved as priced checkout data or rejected as quote/review-only.

Required proof per product family:

1. Variant axis proof:
   - template item is not cartable until required options are chosen;
   - selected variant item code matches selected customer option(s);
   - customer-facing selected-option labels survive to cart/checkout/backend.
2. Supported add-on proof:
   - add-on eligibility is enforced by website item/product family;
   - add-on value is preserved;
   - add-on quantity calculation is proved;
   - add-on price/rate and line total are visible in cart and checkout;
   - backend Sales Order/Sales Invoice line expansion is linked to the parent configured product.
3. Review-only add-on proof:
   - source add-on families not approved for checkout route to quote/review language;
   - they do not become free options;
   - they do not become hidden backend-only notes;
   - they do not produce setup-looking internal messages for customers.
4. Customization proof:
   - text/color/design notes survive in structured payloads for quote-first products;
   - operator review flag is present where required;
   - Lead/Quotation backend records preserve the detail.

Current known representative proof set from the existing audit:

- Ready-to-order configured: `unicorn-bouquet` / `unicorn-bouquet-SMA`.
- Ready-to-order single-SKU: `mothers-day-bouquet`.
- Supported paid add-on: `foil_number` on eligible bouquet products.
- Quote-first complex: `classic-arch`.
- Negative/review-only add-ons: `plush_add_ons`, other source add-on-looking families until approved.

This is not sufficient for full-catalog launch by itself because all 53 published Website Items were reported as stored `needs_review` for page/lane fields in the existing audit.

## Gate 4 — Photo / media / variant display browser gates

Media behavior must be verified in the browser because backend item records alone do not prove the customer saw the right product/detail before adding it.

Required browser gates:

1. Product page loads primary image/gallery for the item without broken media.
2. Multi-photo view is reachable by keyboard/mouse/touch and does not hide option controls.
3. Variant/option selection updates the displayed label and, where product media differs by variant/option, switches to the correct photo or explicitly leaves a safe generic photo with no misleading claim.
4. Add-on UI does not imply an add-on is included unless selected and priced.
5. Cart line thumbnail/name/summary does not contradict selected variant or add-on.
6. Checkout order summary preserves product name, selected options, add-ons, quantities, and totals at desktop and mobile widths.
7. Quote-first product pages do not show normal add-to-cart controls and carry image/product context into the inquiry handoff where available.

Minimum browser witness set:

- Desktop product page before and after option selection.
- Mobile product page before and after option selection.
- Desktop cart with configured and add-on line detail.
- Mobile cart with configured and add-on line detail.
- Desktop checkout summary with configured and add-on detail.
- Mobile checkout summary with configured and add-on detail.
- Quote-first product page and resulting `/contact` payload state.

## Gate 5 — Sales Order / Sales Invoice / Quotation / Lead backend inspection requirements

Customer-visible preservation is not enough. Backend documents must carry the same operational meaning so Jeff can fulfill the order or inquiry.

Required Sales Order proof:

1. Sales Order Item contains the sellable `item_code`, quantity, rate, and item group.
2. Sales Order Item contains LT configuration fields:
   - product template item;
   - product page type;
   - configuration schema version;
   - readable configuration summary;
   - full configuration JSON.
3. Add-on Sales Order lines exist when add-ons are priced separately and preserve/link parent context.
4. Same-SKU configured rows are represented distinctly.
5. Quote-first or unavailable items cannot create direct checkout Sales Order lines.

Required Sales Invoice proof:

1. Invoice generated from Sales Order preserves all LT configuration fields on Sales Invoice Items.
2. Add-on invoice lines remain present and priced.
3. Payment success path copies configuration before invoice submission in local/test proof.
4. No live Stripe payment is required; if Stripe-hosted flow is tested, stop before actual payment unless explicitly approved.

Required Quotation proof:

1. Quote-first payload creates or can create a draft Quotation with selected options/customizations preserved.
2. Color/design recipe/customization JSON is visible to operators.
3. Quotation creation is rollback-safe in verifier output or performed only in a local/test environment.

Required Lead proof:

1. Quote/contact handoff payload arrives in structured Lead fields and/or child quote rows.
2. Lead retains product route/item/page type/commerce lane and customer-entered details.
3. Lead proof must not expose secrets, raw sessions, or customer private data in public artifacts.

Required cleanup proof:

- Any verifier-created Sales Order, Sales Invoice, Lead, Contact, Customer, Quotation, or Payment Request must be rolled back or followed by an existence check proving no test record survived, unless the test environment explicitly requires retained fixtures.

## Gate 6 — Negative tests for unsupported options / add-ons / fallbacks

A launch-safe checkout must prove bad or unsupported intent fails loudly.

Required negative tests:

1. Template/root item cannot be directly carted when required variant options are missing.
2. Quote-first variants cannot be forced into checkout by item code.
3. Unknown add-on key is rejected safely.
4. Review-only source add-ons are rejected as quote/review-needed, not checkout-ready.
5. Supported add-on applied to an ineligible product is rejected.
6. Malformed configuration JSON is rejected.
7. Stale/old schema version is rejected with customer-safe copy.
8. Oversized configuration is rejected before backend document creation.
9. Over-limit quantity fails before checkout/order creation.
10. Missing price, missing item, or setup errors produce customer-safe text and operator-useful verifier failures.
11. Cart/server mismatch produces a visible customer-safe error, not silent line deletion.
12. Direct checkout attempts for unpublished/unavailable products fail loudly.
13. Add-on quantity math edge cases are proved, including multi-digit foil number quantity/total.

Required evidence:

- For each negative, record the command/test/browser action, expected failure, actual failure text/reason, and whether any backend record was created. Backend record creation should be no/rolled back.

## Gate 7 — Exact banned claims and replacement evidence language

Banned until full proof exists:

- "checkout passed"
- "cart works"
- "ERPNext ecommerce works"
- "payments work"
- "orders work"
- "all products are checkout-ready"
- "variants are preserved"
- "add-ons are supported"
- "photos switch correctly"
- "backend has the details"
- "ready for launch"
- "full catalog verified"
- "Stripe/payment success verified"
- "email/receipt verified"
- "customer intent is preserved" with no named product/payload/backend witness

Required replacement language:

- "The named proof slice preserved configured intent through [specific surfaces] with witness [path]."
- "For `[product]` / `[variant]`, `[option/add-on]` appeared in product payload, cart display, checkout display, and `[Sales Order/Sales Invoice/Lead/Quotation]` fields."
- "Same-SKU configured lines stayed separate for `[case]`; this does not prove every catalog product."
- "Quote-first rejection passed for `[product]`; direct checkout was blocked with customer-safe copy."
- "Payment was not submitted; proof stops at Payment Request creation / pre-payment checkout setup."
- "Email was not sent; receipt/email delivery remains unverified."
- "Media switching is browser-verified for `[product]` only; other products remain unverified."
- "Full-catalog launch remains blocked until stored classifications and representative family gates pass."

## Gate 8 — Minimum representative proof set before launch

Before launch, collect one dated artifact bundle with all of the following.

### Product family coverage

At minimum:

1. One ready-to-order configured bouquet variant with supported add-on.
2. One ready-to-order configured bouquet variant without add-on.
3. One ready-to-order single-SKU product.
4. One delivery/get-well or delivery-adjacent product if it can enter checkout.
5. One quote-first complex arch/garland/decor product.
6. One quote-first product with color/design notes.
7. One unsupported/review-only add-on family.
8. One unavailable/unpublished or quote-required item-code force attempt.

Expand coverage if catalog classification shows materially different lanes for columns, arches, garlands, drops, table decor, stands/easels, seasonal/specialty, grab-and-go, deliveries, or get-well bouquets.

### Surface coverage per representative direct-checkout product

- Product page option/media witness.
- Captured payload.
- Cart API or local cart storage witness.
- Cart browser summary.
- Checkout browser summary.
- Server checkout resolver witness.
- Sales Order Item backend fields.
- Sales Invoice Item copy proof where payment-success/invoice path is in scope.
- Negative mismatch/stale payload proof.

### Surface coverage per quote-first product

- Product page no-normal-checkout witness.
- Captured quote payload.
- `/contact` payload handoff witness.
- Lead and/or Quotation backend preservation proof.
- Direct checkout rejection proof.

### Catalog readiness coverage

- Published Website Item inventory dated on launch day or within the launch verification window.
- Stored `lt_product_page_type` and `lt_commerce_lane` are no longer blanket `needs_review`, or launch scope explicitly excludes unresolved products.
- Every published checkout-capable item has a known lane, price, media, and variant/add-on behavior.
- Every published quote-first item has a quote handoff path and direct checkout rejection.

### Backend cleanup coverage

- Verifier-created records either rolled back or listed as retained fixtures with explicit reason.
- Existence checks for named rollback records when the verifier claims cleanup.

## Current blockers

1. Existing audit reports all 53 published Website Items store `lt_product_page_type=needs_review` and `lt_commerce_lane=needs_review`; runtime inference made representative pages work, but stored catalog launch classification is not complete.
2. Existing proof is representative, not full catalog.
3. Supported paid add-on proof is limited to `foil_number`; source add-on families remain review-only/quote-only until approved and mapped.
4. Media/photo switching needs explicit browser gate evidence before any photo/variant display claim.
5. No live payment submission or real email send was performed; payment/email success claims remain banned without separate explicit approval and evidence.

## Actionable next steps

1. Build a launch proof matrix from the 53 published Website Items: product route, item group, stored page type, commerce lane, checkout/quote lane, variant axes, add-on families, media status, proof artifact path.
2. Choose representative products for every materially different product family/lane and run the Gate 8 proof set.
3. Add/collect browser screenshots or JSON snapshots for media, cart, checkout, and quote handoff at desktop and mobile sizes.
4. Run or re-run existing local verifiers and save dated outputs beside the proof matrix.
5. Resolve stored `needs_review` classifications or explicitly remove/exclude unresolved products from launch scope.
6. Keep using replacement evidence language until full-catalog gates pass.
