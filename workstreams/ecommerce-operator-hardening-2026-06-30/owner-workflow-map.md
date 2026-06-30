# Owner Workflow Map

Date: 2026-06-30

Status: source/runtime mapping, not live Desk acceptance proof.

## Plain Contract The Owner Needs

The owner should be able to run ordinary shop operations without calling a developer:

- Add a product.
- Change a product name, short description, story, details, and photos.
- Change a price.
- Add or remove options.
- Add approved paid add-ons.
- Hide, publish, or schedule visibility changes.
- Know whether the change is draft, needs review, ready for local proof, staged, or live.
- See loud failure messages when a change cannot safely become public.

The current system has some of that machinery, but it is not yet a complete owner-run live workflow.

## Intended Owner Surface

The intended owner-facing product surface is `LT Product Blueprint`, labeled in operator language as Product Setup.

Evidence:

- Product Setup fields live in `lt_product_blueprint.json`.
- Owner Home exposes product shortcuts through backend workspace seed logic.
- Desk form buttons in `lt_product_blueprint.js` provide `Preview Local Apply`, `Apply Locally`, and target-record open buttons.
- Server controller methods validate the blueprint before preview/apply.

Product Setup can capture:

- Product name and slug.
- Item group/category.
- Page template.
- Buying path: direct checkout, quote first, or needs review.
- Publish status and shop visibility intent.
- Target Item/Website Item.
- Base price.
- Exact checkout prices.
- Product summary, story, and details.
- Primary image and gallery images.
- Options.
- Color recipes.
- Add-ons.
- Conditional pricing.
- Media rules.
- Content rules.
- Validation evidence and notes.

## What The Owner Can Do Today

An owner with the right backend profile can create and edit Product Setup records and save drafts. They can enter the content, media, price, options, add-ons, and rule data that a real owner workflow needs.

They can run preview, which should show what would be created or updated without writing product records.

If local/test flags and server-held apply confirmation are present, guarded local apply can create or update local records:

- Item templates.
- Variant Items.
- Item Prices.
- Website Item.
- Product page fields.
- Gallery projection.
- Variant cache.

Important: this is local/test apply, not live publish.

## What The Owner Cannot Reliably Do Today

The owner cannot safely use normal ERPNext catalog tables as the product management UI.

Protected direct-edit surfaces include:

- `Item`
- `Website Item`
- `Item Price`
- `Item Attribute`
- `Item Group`
- `Website Slideshow`
- `Webshop Settings`

That protection is correct. Raw catalog edits can desync public product pages, cart, checkout, media, documents, and payment behavior.

The problem is that the protected path does not yet have a complete owner-safe replacement for every live operation. The system blocks dangerous direct edits, but does not yet give the owner a finished, reviewed, live-safe workflow for all expected product maintenance.

## Owner Action Outcomes

### Change Description

What the owner may expect:

- Update a description field.
- Save.
- Public product page changes immediately.

What the product page currently reads:

- `Website Item.web_item_name` for title.
- `Website Item.lt_brand_description` for product story.
- `Website Item.lt_product_details` for "What's Included".
- Only if both LT custom fields are empty does it fall back to `web_long_description` or `description`.

Risk:

- Editing the standard ERPNext description can have no visible effect if the LT custom fields are populated.
- Seed/backfill logic can overwrite LT custom copy fields.

### Change Price

What the owner may expect:

- Update a price on the product.
- Save.
- Shop card, product page, cart, checkout, Sales Order, payment, invoice, and receipt all update.

What runtime currently reads:

- `/shop` joins `Website Item` to `Item Price` for `Standard Selling`, then overlays lowest active variant price for variant templates.
- Product pages show the lowest active variant `Item Price` as "from" price.
- Variant selector returns price from Webshop/ERPNext variant price logic.
- Cart and checkout re-read server-side `Item Price`.
- Stripe labels and amounts are built from Sales Order lines.

Risk:

- Changing Product Setup `base_price` does not automatically mean existing live variant Item Prices changed.
- Changing a template Item's price does not necessarily change variant prices.
- Changing the wrong price list does not change public checkout price.

### Change Photo Or Gallery

What the owner may expect:

- Upload or choose photos.
- Save.
- Product page, shop card, cart, checkout, and payment page use the new photo.

What runtime currently reads:

- Shop cards use `Website Item.website_image`.
- Product gallery prefers LT projected `Website Slideshow` rows and Product Setup approved media.
- Variant media can be held back unless approved by Product Setup/media rules.
- Cart selects Product Setup media first, then variant/media fallbacks.
- Stripe line item images use customer-facing Sales Order line helpers.

Risk:

- One uploaded image may not attach to every required authority.
- Gallery rows, primary image, variant image, cart image, and Stripe image can diverge.

### Add Options

What the owner may expect:

- Add options like size, colors, or style.
- Save.
- Product selector, variant matching, cart, checkout, and order details all understand them.

What the current system needs:

- SKU-defining options must map to Item Attributes, Item Variant Attribute rows, sellable variant Items, and Item Prices.
- Configuration-only options must serialize through Product Setup runtime payloads.
- Color/customization options must pass runtime validation and Sales Order custom fields.

Risk:

- A visible option without a matching sellable variant or runtime configuration contract becomes a broken or misleading product page.

### Add Paid Add-Ons

What the owner may expect:

- Add a paid upgrade.
- Save.
- Customer can select it and it appears on cart, checkout, Sales Order, invoice, and receipt.

What the current system needs:

- Add-on must be approved for checkout.
- Fixed-price add-on must have an enabled ERPNext Item.
- Add-on Item must have a `Standard Selling` Item Price.
- Runtime must convert it to a separate Sales Order line.
- Invoice copy must preserve the configuration fields.

Risk:

- A visible add-on without the full chain is worse than unavailable; it can look selectable but fail later or lose business meaning.

### Publish Or Hide A Product

What the owner may expect:

- Publish, hide, or update shop visibility.

What local apply currently does:

- Generated Website Items are local/unpublished.
- Existing public Website Item publish/hide/reroute changes are preserved and not changed by local apply.
- Live approval is intentionally absent from the local Product Setup slice.

Risk:

- Product Setup can describe desired visibility, but it is not yet a complete owner-run live publishing state machine.

## Required Owner Workflow Direction

The target owner workflow should be:

1. Owner opens Product Setup.
2. Owner edits product data in plain business language.
3. Save runs validation and records blockers.
4. Preview shows exact created/updated records and public impact.
5. Owner fixes blockers or requests review.
6. Approved changes pass local verifier proof.
7. Approved changes pass staging proof.
8. Live publish applies the exact reviewed packet.
9. Public route, shop card, product page, cart, checkout, Sales Order, payment, invoice, and receipt proof are attached to the change.

Anything less keeps the owner dependent on a developer for ordinary business operations.
