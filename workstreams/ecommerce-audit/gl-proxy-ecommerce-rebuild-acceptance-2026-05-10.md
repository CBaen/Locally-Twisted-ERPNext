D:2026-05-10 | Check:local docs/artifacts 2026-05-10 | Confidence:[LOCAL-PROOF]
# GL Proxy Ecommerce Rebuild Acceptance — customer/operator meaning gate

## Scope and verdict

**Verdict: HOLD for go-live; CLEAR to continue artifact-first rebuild mapping.**

This is a business/customer/operator acceptance gate, not an implementation design. The current ERPNext ecommerce work has useful proof slices, but GL should treat the site as **not go-live-ready** until the remaining blockers below are either fixed or explicitly accepted as quote-first/non-purchase behavior.

Evidence basis:

- `workstreams/ecommerce-audit/README.md` says Lane B/C/D artifacts exist, but Lane A legacy_source source map and Lane E docs/action convergence are missing and must be `[NO EVIDENCE]`.
- `workstreams/ecommerce-audit/erpnext-receiving-parity-matrix-2026-05-10.md` says the native receiving architecture preserves proof-slice meaning, but destructive import/reimport remains blocked by source audit/media/pricing/version gates.
- `workstreams/ecommerce-audit/cart-checkout-intent-preservation-audit-2026-05-10.md` proves selected Unicorn Bouquet + foil-number and Classic Arch quote-first handoff paths, while noting all 53 published Website Items still store `needs_review` page/lane fields.
- `workstreams/ecommerce-audit/native-frappe-product-template-architecture-2026-05-10.md` recommends a native ERPNext/Frappe contract layer, not legacy_source code copying.
- `audits/catalog-import-audit-2026-05-08/15-product-page-contract-source-audit.md` classifies 53 source products as 15 ready-to-order and 38 quote-first, but says destructive purge/import is blocked.
- Add-on, media, and price packets show 4 review-only add-on axes, 95 unclassified extra images, and 273 price review units with 0 approved public prices in those packets.

## Acceptance criteria — customer experience

### Product page

A customer must be able to tell, before acting, whether a product is:

1. **Ready to order online** — priced, option-complete, and safe for cart/checkout.
2. **Custom quote first** — visible as a planning/quote request, not a fake purchasable product.
3. **Needs review / unavailable** — blocked with friendly copy and a safe contact path, not a broken page or empty selector.

Acceptance means:

- Product name, photo, price/quote state, and primary action match the real buying path.
- No product with unresolved pricing, media, add-ons, color logic, or dependencies can show a normal paid checkout CTA.
- Product page labels use plain language: `Ready-to-order page`, `Custom quote page`, `Buying Path`, `Page Template`; no raw snake-case values leak to Jeff or customers.
- Product pages must fail loudly if stored backend classification is missing. Runtime fallback may protect testing, but go-live requires saved product classifications that GL/operator can review.

### Variants and options

A customer must experience options as meaningful choices, not technical variants:

- Required choices must visibly narrow to valid combinations; impossible combinations must be unavailable or loudly blocked.
- Same SKU with different customer choices must stay as separate cart/order lines.
- Color-heavy, setup-sensitive, or multi-axis decor must route quote-first until source mapping and operator review prove it can be priced safely.
- Unapproved source add-ons (`Add Bouquet`, `Add ons`, `Orbz toppers`, `Plush add ons`) must remain quote-only; only approved add-ons may appear as paid checkout controls.
- `foil_number` is the current proven checkout add-on pattern: customer sees selected number, quantity, line total, and it survives downstream records.

### Photos and galleries

A customer must see photos that support the exact product promise:

- Primary product image must show on every live product page.
- Variant-changing photos must change only when the variant/source supports that image mapping.
- Extra photos must be classified before public gallery claims: parent gallery, variant image, category/reference, or hold.
- If a photo cannot be mapped, the product must not imply that gallery/variant behavior is done.
- Multi-photo view must be usable on desktop and mobile, with clear next/previous or thumbnail behavior where multiple approved images exist.

### Cart

A customer must see their exact selected intent in cart:

- Base product, selected options, approved add-ons, add-on quantities, and add-on totals are visible.
- Cart line identity must preserve configured lines separately, especially same SKU + different options/add-ons.
- Quote-first products cannot be forced into cart; the customer gets quote-required copy and a contact/quote path.
- Cart setup errors must not expose internal field names, item codes, or stack traces.

### Checkout

A customer must see honest checkout state:

- Checkout totals must be server-calculated from ERPNext prices and approved add-on rules, not trusted browser values.
- Checkout must preserve selected options/add-ons into Sales Order Item rows.
- Payment path must not proceed for quote-first or unresolved products.
- Guest checkout may create the expected Lead/Contact/Customer/Sales Order/Payment Request only when the paid path is actually valid.
- After payment, invoice/receipt/customer email must preserve the same product meaning, not collapse to bare SKU/quantity.

### Quote-first handoff

A quote-first customer must experience the path as a request/review flow, not a checkout failure:

- Product-page selected options, colors, design notes, add-ons, route, and source product name carry into `/contact` as structured payload.
- Submission creates a Lead and internal draft Quotation/review packet only; no customer invoice, payment request, or paid-order email is created.
- Operator-approved quote delivery must be explicit and gated. Customer acceptance can create a draft Sales Order only after the quote is submitted, priced, not expired, and marked `Ready For Customer Review`.
- Quote acceptance success must clearly say no card was charged and nothing was invoiced.

## Acceptance criteria — operator/backend records

An operator must be able to open records and understand the order/request without decoding implementation details.

### Product/admin view

- Every published Website Item has an explicit saved `Page Template` and `Buying Path` before go-live.
- Each product has a reviewable source row showing source slug, ERPNext target, required axes, customization axes, add-ons, dependency matrix status, media status, price source, and blocker state.
- Unknown fields/axes are marked `needs review` or `quote first`; they are never silently dropped.

### Lead and quote-first records

- Product quote Leads show source product, page type, buying path, selected options, color recipes, notes, add-ons, payload JSON, and child quote item row.
- Draft Quotation review packets show what needs operator pricing/review and block customer send when payload, recipient, valid-until, terms, event context, or pricing is incomplete.
- Zero-dollar review items must display as `Pricing review required`, not as customer-ready $0 pricing.

### Sales Order / Invoice / fulfillment

- Sales Order Items and Sales Invoice Items preserve configuration JSON, human summary, product template item, page type, and version.
- Add-ons that are sold as priced add-ons appear as explicit line items with parent linkage and selected value.
- Accepted quote Sales Orders store source quote and written-approval details and are draft-only until the next approved finance/fulfillment step.
- Operator-facing labels explain fulfillment meaning plainly: selected size/length/design, selected foil number, color notes, delivery/pickup notes, and review blockers.

### Email/payment/document records

- Customer quote send, paid-order receipt, invoice, and operator notifications must show the same product meaning customers selected.
- Business copy routing must use delivery-safe BCC behavior; no routed-alias loop.
- Payment/invoice/receipt side effects must be absent from quote-first paths until explicitly approved.

## Not-go-live blockers

1. **Lane A legacy_source source map is missing** — no named artifact exists for refreshed legacy_source source product behavior, source axes, photos, option-changing photos, cart/quote behavior, and backend sales surfaces.
2. **Lane E docs/action convergence is missing** — no named artifact reconciles legacy_source docs/source/admin surfaces with current agent action plan.
3. **All 53 published Website Items still stored `needs_review` page/lane fields in Lane C evidence** — runtime inference is not enough for go-live because Jeff/operator cannot verify product intent record-by-record.
4. **Destructive purge/import is explicitly blocked** by the source audit: 53 products have blockers/warnings; warning buckets include `axis_needs_review: 9`, `color_axis_customization: 25`, `missing_resolver_prices: 49`, and `unclassified_gallery_images: 49`.
5. **Price public approval is not complete** — price review packet has 273 review units and 0 approved public prices in that packet. Current checkout proof is useful, but not full-catalog price approval.
6. **Media/gallery mapping is not complete** — 95 source extra images across 49 products are unclassified; approved parent-gallery images and assigned variant images in the packet are 0.
7. **Add-ons beyond `foil_number` are not approved checkout features** — 4 review-only source add-on families affect 9 products and must stay quote-first unless GL/Jeff approve mapping, pricing, eligibility, media, and fulfillment behavior.
8. **Version/source mismatch remains unresolved** — destination image label and legacy_source local/prod module version mismatch must be resolved or explicitly accepted before import claims.
9. **Aggregate architecture readiness had a Lane B live-mismatch/deadlock note** — direct contracts passed, but a clean aggregate run in the intended ecommerce mode is required before launch claims.
10. **Finance/payment live cutover remains separate** — local checkout testing is not live Stripe, DNS, Frappe Cloud, bank/accounting, owner review, or production approval.

## Questions legacy_source source mapping must answer

Lane A must produce a named artifact that answers, product-by-product:

1. What is the canonical legacy_source source product/template/variant identity, and which ERPNext Website Item should receive it?
2. Which choices are required variant axes, optional add-ons, color/customization prompts, backend-only fields, or source artifacts to drop?
3. Which combinations are valid, invalid, or conditionally available?
4. Which option changes should change product photos, and which photos are parent gallery/proof/reference only?
5. Which products are safe ready-to-order checkout, and which must be quote-first?
6. What is the price source for each sale unit: legacy_source resolver, legacy_source base/list price, live ERPNext snapshot, or human-approved override?
7. Which add-ons become priced checkout lines, included choices, quote-only prompts, separate bundle Items, inventory-managed SKUs, or removed options?
8. What must appear on cart, quote, Sales Order, invoice, and fulfillment records for each product family?
9. What did legacy_source show in product/sales/backend admin surfaces that ERPNext must preserve for Jeff/operator meaning?
10. What source version controlled the answer: local legacy_source `19.0.2.15.0`, possible production `19.0.2.14.0`, live shop scrape, or GL/Jeff decision?

## Decisions GL/Jeff must make before rebuild/purge

1. **Product lane decision:** confirm which product families are ready-to-order checkout vs quote-first for launch.
2. **Price decision:** approve, replace, or hold every live-snapshot price review unit before public price promises.
3. **Add-on decision:** decide each review-only add-on family/value: paid add-on, included option, quote-only prompt, bundle/separate Item, inventory-managed item, or drop.
4. **Photo decision:** classify source extra images and decide whether parent product galleries, variant-changing photos, category/reference images, or holds are desired.
5. **Color/customization decision:** decide how color recipes should be collected, displayed to customers, and shown to operators for each affected family.
6. **Import strategy decision:** choose phased family-batch rebuild vs full purge/reimport rehearsal. Recommendation: family-batch proof first; no broad purge until every gate has a named artifact and rollback/rehearsal proof.
7. **Public posture decision:** decide whether launch shop is small ready-to-order + quote-first catalog, or quote-first-first with limited checkout. Recommendation: small proven checkout catalog plus quote-first for complex decor.

## Concise actionable next steps

1. **Rerun Lane A artifact-first** using legacy_source source/admin/product/sales surfaces; no writes, no code copying, no secrets.
2. **Rerun Lane E artifact-first** to reconcile legacy_source source/docs/admin observations with ERPNext-native action plan.
3. **Create a single product-family acceptance matrix** with 53 rows: lane, required axes, add-ons, price status, media status, operator record requirements, blocker, decision owner.
4. **Require saved ERPNext page/lane fields** for every published Website Item before go-live; no saved `needs_review` product may expose paid checkout.
5. **Run a clean top-level architecture readiness gate** in the intended ecommerce mode after Lane A/E and product matrix updates.
6. **Do one non-destructive family rehearsal** before any purge: bouquet proof batch should demonstrate product page, option/photo behavior, cart, checkout, Sales Order, invoice, receipt, and operator fulfillment meaning.
7. **Keep complex decor quote-first by default** until GL/Jeff approve pricing, dependencies, add-ons, and media for that family.

## GL proxy flags

### What GL would not be able to verify unaided

- Whether selected customer options survive into Sales Order/Invoice rows.
- Whether current prices came from legacy_source resolver, ERPNext snapshot, or manual fallback.
- Whether source photos are variant-changing, parent-gallery, category/reference, or unsafe to show.
- Whether an add-on is truly priced/fulfillable or just visually present.

### Bare claims or missing witnesses

- Any statement that full legacy_source source parity is known while Lane A is missing.
- Any statement that public product photos/galleries are complete while the media packet holds 95 unclassified images.
- Any statement that full catalog pricing is approved while the price packet marks 273 review units and 0 approved public prices.
- Any statement that product import/purge is safe while source audit says blocked for destructive purge/import.

### Customer/business trust risks

- A customer buys the wrong variant because dependencies or same-SKU configured lines collapse.
- A customer sees $0 or flat placeholder pricing as real.
- A customer expects a photo/variation that operations cannot identify later.
- Jeff receives an order/invoice that omits the customer's actual customization.
- A quote-first product accidentally creates a payment/invoice path.

### Required fixes before GL/Jeff approval

- Named Lane A and Lane E artifacts, or explicit `[NO EVIDENCE]` carried into final synthesis.
- 53-row product acceptance matrix signed off for lane, price, add-on, media, and operator meaning.
- Clean aggregate verifier in intended ecommerce mode.
- Browser proof on desktop/mobile for at least one ready-to-order family and one quote-first complex family.
- Backend proof that cart/checkout/quote/accepted-quote records preserve customer meaning end-to-end.
