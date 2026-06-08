# Locally Twisted Ecommerce Architecture Upgrade

Date: 2026-06-08
Status: documentation checkpoint only
Scope: local architecture planning for the ERPNext/Frappe ecommerce system

This document does not approve implementation, product mutation, database
migration, staging deploy, live deploy, Stripe work, DNS work, or production
catalog changes. It records what is currently true enough to plan from, what
the old Odoo system did well, what Locally Twisted already does better, and
where an architectural rebuild must pause if it would damage or mutate existing
products.

## Short Decision

We should not replace the current Product Setup layer with a new ecommerce
engine from scratch.

The safer path is to upgrade the existing LT Product Setup and product-page
receiving architecture into one explicit Product Option Engine. That engine
must fit inside ERPNext/Frappe, preserve existing Items and Website Items, and
make staff product setup the source of truth for product pages, option logic,
media behavior, checkout payloads, quote payloads, cart identity, order lines,
invoice lines, receipts, and operator review.

If the next architecture step requires destructive changes to existing product
records, mass variant regeneration, silent field remapping, or reimporting the
catalog before we can prove parity, pause.

## Current Verified Local Evidence

Verified from the local ERPNext/Frappe site on 2026-06-08:

- Git branch: `main`.
- Local LT source was clean before this document task.
- Current local counts checked through the running Frappe backend:
  - `Website Item`: 51.
  - `LT Product Blueprint`: 51.
  - `Item`: 10,685.
  - `Item Attribute`: 30.
  - `LT Product Blueprint Gallery Image`: 68.
  - `LT Product Blueprint Option`: 78.
  - `LT Product Blueprint Media Rule`: 1,750.
  - `LT Product Blueprint Price`: 3,708.
- Rendered local route checked:
  `http://localhost:8081/shop-items/columns/classic-organic-columns`
  - The page renders one color drawer.
  - The page renders 51 color cards/swatches.
  - The page contains `Reflex Champagne`, `latex colors`, `Column Height`,
    `Delivery only`, and `Choose your palette`.
  - The page emits product-page architecture JSON.
  - The page emits Product Setup schema JSON.
  - The page is quote-first/delivery-only locally, not a direct checkout product.

Do not reuse older catalog counts as current truth without rechecking the
running local database.

## What LT Already Does Better Than Odoo

The current LT frontend is better than the old Odoo storefront for balloon
color selection.

Odoo exposed the `latex colors` set as a long customer option list. LT currently
renders grouped color drawers with visible swatches, named colors, and a more
usable scan pattern. That matters because balloon color choice is not a normal
retail variant picker. Customers need to recognize, compare, and select color
families without turning the product page into a raw ERP table.

The current LT system also already has important architecture that should not be
discarded:

- `LT Product Blueprint` is the owner-facing Product Setup record.
- Product Setup has child tables for:
  - options and variant axes;
  - color recipes;
  - add-ons;
  - conditional prices;
  - product gallery photos;
  - option-specific media rules;
  - option-specific content rules.
- Product Setup tracks changes.
- Product Setup has publish/review statuses separate from public Website Item
  visibility.
- Product Setup has target Item and target Website Item links.
- Product pages emit backend-owned architecture JSON.
- Product pages emit Product Setup schema JSON.
- The runtime separates selected SKU options from configuration-only groups,
  add-ons, media rules, and content rules.
- The current product-page architecture contract maps:
  - sale-unit axes to `selected_options`;
  - color customization to `color_recipes`;
  - approved add-ons to `add_ons`;
  - review-only add-ons to `quote_context`;
  - product meaning into Quotation Item, Sales Order Item, and Sales Invoice
    Item parity fields.
- Product gallery media is now supposed to flow from Product Setup to Website
  Slideshow to the product gallery rail.

This is not nothing. The failure is not that LT has no ecommerce architecture.
The failure is that the architecture is still split across Product Setup,
runtime helpers, source contracts, Webshop overrides, checkout code, quote code,
and verifiers. The upgrade should unify those contracts and make them easier
for staff to use.

## What Odoo Offered That LT Still Needs Structurally

The old Odoo product backend was stronger as a staff product console. The live
Odoo backend review and RPC pass showed the product form offered these product
tabs and surfaces:

- `General Information`
- `Attributes & Variants`
- `Sales`
- `Purchase`
- `Inventory`
- `Images`
- product smart buttons such as website page, variant count, documents,
  purchase/sales stats, and inventory movement summary
- product activity/chatter/audit history

For the reviewed `Classic Organic columns` product, Odoo used:

- `Column Height` as a true variant-producing attribute.
- `latex colors` as a visible multi-select/no-variant customer option.
- 6 true variants for column height.
- 53 visible latex color values that did not create 53x variant explosion.
- price extras on height values.
- public product page option rendering tied back to backend attributes.

That separation is the important logic. The lesson is not "make more variants."
The lesson is "classify option roles correctly."

Odoo also has first-class related product structures even though the reviewed LT
Odoo dataset did not currently populate them:

- Optional products: suggested after add-to-cart.
- Accessory products: suggested in the cart/review step.
- Alternative products: displayed on the product page for upsell.

LT needs those concepts, but we should implement them inside Product Setup and
ERPNext/Frappe instead of copying Odoo tables.

## What Official Sources Support

Checked external sources on 2026-06-08:

- Odoo 18 product variant docs describe display types including pills, radio,
  select, color, and multi-checkbox. They also state that multi-checkbox
  requires variant creation mode set to "Never", and that value price extras
  can affect variant price:
  https://www.odoo.com/documentation/18.0/applications/sales/sales/products_prices/products/variants.html
- Odoo 18 ecommerce docs describe variants as product versions with possible
  price and availability differences, and describe product image/video
  presentation controls:
  https://www.odoo.com/documentation/18.0/applications/websites/ecommerce/products.html
- Odoo 18 cross-sell/upsell docs describe optional, accessory, and alternative
  products as separate customer journey placements:
  https://www.odoo.com/documentation/18.0/applications/websites/ecommerce/products/cross_upselling.html
- ERPNext item variant docs describe an Item template plus concrete Item
  Variants; templates are not transaction items, and variants are generated
  from selected attributes:
  https://docs.frappe.io/erpnext/item-variants
- ERPNext item attribute docs describe Item Attributes as the characteristics
  used to create Item Variants:
  https://docs.frappe.io/erpnext/item-attribute
- Frappe child table docs support keeping many product option/media/pricing
  rows directly attached to the Product Setup parent record:
  https://docs.frappe.io/framework/user/en/basics/doctypes/child-doctype
- Frappe REST docs support backend-owned API methods and generated DocType
  APIs, but whitelisted methods still need explicit server validation for
  checkout logic:
  https://docs.frappe.io/framework/user/en/api/rest

The external conclusion is direct: ERPNext gives us strong Items, Item
Variants, DocTypes, child tables, permissions, and order documents. It does not
by itself give LT the Odoo-style distinction between SKU-defining attributes,
configuration-only multi-select options, quote-only options, add-on products,
media rules, and customer/order payload preservation. LT's custom Product Setup
layer is the right place for that.

## Product Option Engine V1

The next architecture layer should be named and treated as a system contract:
`LT Product Option Engine`.

It should not be a new disconnected app. It should be the shared engine under
the existing Product Setup records, product-page renderer, cart resolver,
checkout resolver, quote resolver, Sales Order writer, Sales Invoice writer,
receipt writer, and operator review surfaces.

### Option Classes

Every customer-facing product choice needs one option class:

1. `sku_variant`
   - Creates or resolves a concrete ERPNext Item variant.
   - Exactly one value per required SKU axis.
   - Examples: `Column Height`, `Bouquet Size`, `Arch Size` when those are
     true sale-unit choices.

2. `configuration_multi`
   - Does not create ERPNext variants.
   - Can allow one or many values.
   - Preserved in the cart/order/quote payload.
   - Examples: balloon color recipes, palette choices, design notes, placement
     preferences.

3. `priced_modifier`
   - Changes price but may not deserve a full ERPNext variant.
   - Must have server-owned pricing and order-line preservation.
   - If server price cannot be proven, it blocks checkout and routes to quote.

4. `add_on_product`
   - Adds a separate ERPNext Item line or clearly structured child payload.
   - Must have eligibility, quantity rules, tax behavior, receipt summary, and
     fulfillment meaning.
   - Current proof slice: foil-number add-on only.

5. `optional_product`
   - Suggested after add-to-cart or in a product decision moment.
   - Should not alter the base product silently.
   - Adds its own cart line if selected.

6. `accessory_product`
   - Suggested during cart/review before checkout.
   - Adds its own cart line if selected.

7. `alternative_product`
   - Merchandising suggestion on the product page.
   - Links the customer to a different product page, not a hidden mutation of
     the current product.

8. `quote_context`
   - Captures useful staff/customer context but blocks paid checkout.
   - Preserved on Lead, Quotation, operator review, and customer quote flows.

9. `media_rule`
   - Changes the main product image based on selected options.
   - Must not append duplicate thumbnails to the rail.
   - Must not override Product Setup gallery authority.

10. `content_rule`
    - Changes title/story/details based on selected options.
    - Must preserve backend source and reset cleanly when options change.

### Required Engine Contracts

The engine needs these contracts before any launch upgrade is trusted:

- Product Setup authoring contract:
  Staff can define the choices safely without editing raw Items, Item Prices,
  Website Items, or Website Slideshow rows directly.

- Product page rendering contract:
  The page renders controls from Product Setup and backend runtime truth, not
  ad hoc frontend assumptions.

- Selection payload contract:
  Customer choices become one versioned payload, currently compatible with
  `lt-product-config-v1`, and the payload names where every choice belongs.

- Resolver contract:
  The server resolves selected options to:
  - concrete sellable Item where needed;
  - server price;
  - line identity;
  - selected media;
  - readable customer/operator summary;
  - checkout allowed, quote required, or blocked.

- Cart identity contract:
  Same base product with different selected choices must not collapse into the
  same cart line.

- Checkout contract:
  Checkout cannot use browser price or browser eligibility as truth.

- Quote contract:
  Quote-first products preserve selected options, color recipes, notes, media
  context, and review blockers from contact intake to draft Quotation to
  accepted Sales Order.

- Order/invoice/receipt contract:
  Sales Order Item, Sales Invoice Item, payment success, customer receipt, and
  operator notification must preserve the same human-readable and JSON product
  meaning.

- Media contract:
  Product Setup gallery images are the rail authority. Variant/option media
  may change the main image but cannot create duplicate rail entries.

- Staff review contract:
  Staff see what is ready, what is blocked, and why. Silent "looks ready"
  states are forbidden.

## What Must Not Happen

Do not solve this by:

- exploding every color, addon, note, and event preference into ERPNext Item
  variants;
- treating Website Item fields as the authority layer;
- letting frontend JS decide price, checkout eligibility, or final cart line
  meaning;
- mutating existing Items before the resolver contract is proven;
- running a destructive import or purge to make the new design easier;
- making product-specific code branches for each hard product;
- hiding gaps behind `Needs review` without staff-visible blockers;
- treating Odoo as a data source to copy instead of a logic witness;
- treating old docs, old counts, or old audit snapshots as current truth.

## Safe Upgrade Path

The safe path is staged and non-destructive:

1. Inventory current Product Setup coverage.
   - Count every Product Setup record, option row, media rule, gallery row,
     price row, and active Website Item.
   - Report gaps without changing product data.

2. Normalize the option taxonomy in documentation and verifiers first.
   - Map existing Product Setup roles into the option classes above.
   - Identify where current names are too vague, such as `Configuration only`
     versus `configuration_multi`, without changing records yet.

3. Add or update verifiers before behavior changes.
   - Product Setup coverage.
   - Option-class mapping.
   - No destructive Item mutation.
   - No Website Item authority drift.
   - Product page JSON parity.
   - Cart/order/invoice/receipt payload parity.
   - Gallery rail no-duplicate behavior.

4. Build adapter functions against existing records.
   - Read existing Product Setup rows.
   - Produce the normalized Product Option Engine schema.
   - Do not change records in the first pass.

5. Prove the adapter on representative product classes.
   - One simple direct-checkout product.
   - One quote-first column/garland/arch-style product with color recipes.
   - One product with variant image rules.
   - One product with gallery-only media.
   - One product with the existing foil-number add-on.

6. Only after proof, decide whether Product Setup DocTypes need schema changes.
   - If yes, use migrations that preserve current rows.
   - Use a dry-run migration report before any write.
   - Keep rollback instructions and source-owner review.

7. Only after local proof, reopen staging-release planning.
   - No live checkout, live Stripe, DNS, or production data mutation from this
     architecture task.

## Pause Conditions

Pause before implementation if any of these are true:

- The proposed rebuild requires deleting or regenerating existing Item variants.
- The proposed rebuild requires replacing Product Setup records rather than
  adapting them.
- The proposed rebuild cannot preserve existing Website Item routes.
- Existing product pages would lose gallery photos, primary images, variant
  image behavior, or color controls.
- Existing checkout/quote payloads cannot be read by the new resolver.
- Staff would need an agent to fix normal product setup after the rebuild.
- A product class has no safe option class.
- Add-on pricing or tax behavior is not server-authoritative.
- A customer could see success while order, invoice, receipt, email, or
  operator payload preservation failed.
- The architecture can only be proven by staging/live mutation.

If any pause condition appears, the next artifact should be a plain-English
blocker report, not code.

## Open Gaps To Investigate Next

These are not implementation approvals. They are the next documentation and
verification questions:

- Which current Product Setup option rows are true `sku_variant`, and which are
  `configuration_multi`?
- Which current ERPNext Item Attributes are causing unnecessary variant
  explosion?
- Which current Product Setup media rules are option-specific image swaps
  versus gallery authority?
- Which add-on families from the old source are still quote-only, and what
  data is missing before they could become paid checkout add-ons?
- Which product pages should remain quote-first permanently even if ecommerce
  launches?
- Which product pages can safely become direct checkout without staff review?
- What staff Desk view makes Product Setup easy enough that no AI agent is
  needed for normal product maintenance?
- What exact local verifiers must pass before a staging release gate can even
  reopen?

## Working Conclusion

LT is not missing an ecommerce idea. It is missing one unified, staff-safe,
ERPNext-compatible product option engine that joins the pieces already built.

The front end should keep its better balloon-color UX. The backend should keep
Product Setup as the authority. ERPNext Items and Item Variants should remain
the sellable accounting/inventory units, not the dumping ground for every
customer choice. The product option engine should decide what becomes a variant,
what becomes configuration, what becomes an add-on line, what becomes quote
context, and what blocks checkout.

That upgrade is worth doing only if it preserves current products and makes
future product setup safer for Jeff and staff. If it requires destructive
catalog mutation to make the architecture work, pause.
