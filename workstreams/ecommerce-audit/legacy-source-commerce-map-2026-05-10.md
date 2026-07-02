D:2026-05-10 | Check:local legacy_source source + public/browser legacy_source surfaces 2026-05-10 | Confidence:[LOCAL-PROOF]

# legacy_source Source Commerce Map — Locally Twisted

Purpose: map the working legacy_source commerce meaning that ERPNext must model. This is a read-only source-witness artifact. It does **not** prescribe copying legacy_source code into ERPNext.

## Scope and safety

- Read-only sources only: local legacy_source repo, project dispatch/context files, and safe public/authenticated legacy_source observations.
- No legacy_source writes, saves, imports, purges, checkout submission, payment action, email send, or customer-data export were performed.
- Browser observations are treated as behavior witnesses, not implementation source.
- Product/route IDs are included where safe because they identify catalog/product records, not private customer data.

## Sources read / witnessed

### Locally Twisted ERPNext project entrypoints

- `AGENTS.md` — project safety/verification rules.
- `ROLE.md` — ERPNext Project Operator contract.
- `capabilities/INDEX.md`.
- `capabilities/recipes/erpnext-ecommerce-receiving-architecture.md`.
- `workstreams/ecommerce-audit-dispatch-prompts-2026-05-10.md`.
- `workstreams/ecommerce-audit/user-provided-legacy_source-surfaces-2026-05-10.md`.

### Local legacy_source source witness

- `/home/guidingl/projects/locally-twisted-legacy_source/addons/locally_twisted/__manifest__.py` — module version `19.0.2.15.0`; dependencies include `website_sale`, `delivery`, `payment_stripe`, `sale_loyalty`.
- `addons/locally_twisted/models/product_template.py` — seeds `website_description` from `description_sale` when website description is empty.
- `addons/locally_twisted/views/product_views.xml` — adds backend product `Images` tab using `product_template_image_ids` and `image_1920`.
- `addons/locally_twisted/views/website_sale_templates.xml` — product detail branding, product inquiry form, multi-checkbox color dots, cart summary safety override.
- `addons/locally_twisted/data/delivery_data.xml` — delivery carrier/service product definitions and checkout delivery zones/prices.
- `addons/locally_twisted/data/automation_data.xml` — invoice/deposit automation and website-order skip guard.
- `addons/locally_twisted/views/pages/page_refund_policy.xml` — public payment/refund policy language.
- `addons/locally_twisted/controllers/portal.py` and `views/portal_templates.xml` — customer portal order/invoice/event/quote concepts.
- `addons/locally_twisted/static/src/js/dashboard.js` and `static/src/xml/dashboard.xml` — operator dashboard/product/order/invoice/data concepts.
- `deploy.py` — product/category/attribute/value/price-extra export/import shape; legacy_source production is treated as authoritative for existing products.

### legacy_source public/browser surfaces observed

- `/shop` via browser snapshot: product grid, category tree, attribute filters, cart badge, logged-in admin/editor chrome.
- `/shop/classic-arch-57` via web fetch + browser DOM evaluation.
- `/shop/classic-organic-balloon-garland-19` via web fetch.
- `/shop/number-balloon-columns-22` via web fetch.
- `/shop/balloon-drop-74` via web fetch.
- `/shop/unicorn-bouquet-115` via web fetch.
- Browser JSON-RPC read-only sample confirmed product template IDs and fields for published sale products; no mutation calls were made.

## Current verified legacy_source project state relevant to ecommerce

- legacy_source witness repo branch checked as `main` during this lane.
- Local legacy_source module version checked as `19.0.2.15.0`.
- The custom module depends on legacy_source ecommerce/payment/delivery stack (`website_sale`, `payment_stripe`, `delivery`) and is therefore not just a static website theme.
- legacy_source has a live/public shop at `http://5.78.136.133/shop` that rendered products, categories, filters, product pages, variant selectors, inquiry forms, and cart state during this audit.
- The legacy_source shop had at least one cart item in the observed browser session. I did not inspect or change cart contents because that could reveal/session-mutate private state.

## Source commerce model: objects and meaning

### Product/page classes

legacy_source represents purchasable commerce as `product.template` records, exposed by routes such as `/shop/classic-arch-57` and `/shop/unicorn-bouquet-115`.

Observed product/page classes:

| Class / family | Evidence | Commerce meaning to preserve |
|---|---|---|
| Balloon arches | `/shop/classic-arch-57`; `/shop` category `What We Make > Balloon Arches` | Base product with size, color, design, optional LED-style add-on choices. |
| Organic garlands | `/shop/classic-organic-balloon-garland-19`; `/shop` category `What We Make > Organic Garlands` | Length-driven product; color palette choices; installation/delivery language in description. |
| Columns | `/shop/number-balloon-columns-22`; `/shop` category `What We Make > Columns` | Number/color/latex-color choices; often personalized by selected number and colors. |
| Balloon drops | `/shop/balloon-drop-74`; `/shop` category `What We Make > Balloon Drops` | Drop-size axis plus latex-color selection; event-moment product. |
| Helium bouquets | `/shop/unicorn-bouquet-115`; `/shop` category `What We Make > Helium Bouquets` | Bouquet size base/upgrade plus optional foil-number add-ons. |
| Seasonal / occasion products | `/shop` category tree: New Year's Eve, Valentine's Day, Easter, Halloween, Christmas, graduations, missionary farewell, get-well, baby reveal/showers, etc. | Same commerce primitives reused under seasonal/occasion merchandising. |
| Personalized displays | `/shop` category tree shows `Personalized Displays` | Personalization-oriented products; exact option rules need full product export. |
| Service/quote pages | `/book`, product inquiry form, portal quotes | Some requests are quote/CRM flows rather than immediate checkout. |

ERPNext implication: do not model this as a flat Item list only. It needs a product-template/page layer with attributes/options, option pricing, categories, images, inquiry/quote capture, and delivery/checkout policy.

### Category taxonomy

Browser `/shop` category tree showed these top-level and nested public categories:

- `Special Occasions`: Birthday Parties, Baby Reveal & Showers, Weddings, Graduations, Missionary Farewell, Get Well, Get Well Bouquets.
- `Holidays & Seasons`: New Year's Eve, Lunar New Year, Valentine's Day, St. Patrick's Day, Easter, Cinco de Mayo, Mother's Day, Father's Day, Pride, 4th of July, Fall, Halloween, Diwali, Hanukkah, Christmas, Kwanzaa.
- `What We Make`: Balloon Arches, Columns, Centerpieces, Helium Bouquets, Organic Garlands, Backdrops, Balloon Drops, Grab N Go, Balloon Cups, Photo Frames, Table Decor.
- `Personalized Displays`.

Local source `deploy.py` exports/imports `product.public.category` using `name`, `parent_name`, and `sequence`, so the category hierarchy is first-class source data, not just navigation text.

### Option / variant axes and observed values

legacy_source uses product attributes/attribute values on `product.template` records. Local `deploy.py` exports:

- `product.attribute`: `name`, `display_type`, `create_variant`, `sequence`.
- `product.attribute.value`: `name`, `attribute_name`, `sequence`, `html_color`, `is_custom`.
- Product templates: `attr_lines` with `attribute_name` and `value_names`.
- `product.template.attribute.value.price_extra` for per-template option price deltas.

Observed axes from `/shop` and product pages:

| Axis | Values observed | Affected products/families observed | Required? | Pricing evidence |
|---|---|---|---|---|
| Arch Size | 20ft, 25ft, 30ft, 35ft | Classic Arch (`/shop/classic-arch-57`) | Effectively required as a single-choice variant axis; legacy_source renders a default-selected radio group. | Classic Arch: 25ft `+ $65`, 30ft `+ $130`, 35ft `+ $195`; base 20ft at $260. |
| Garland Length | 6ft, 9ft, 12ft | Classic Organic Balloon Garland (`/shop/classic-organic-balloon-garland-19`) | Required/default single-choice variant axis. | Page showed base $150 on shop grid; exact 9ft/12ft price extras were not captured in fetched readability output. [NO EVIDENCE] for deltas in this pass. |
| Column Height | 5ft, 6ft, 7ft, 8ft, 9ft, 10ft | `/shop` filters | Likely required/default where present; product-specific rules unknown. | [NO EVIDENCE] for per-height extras in this pass. |
| Color Palette | Black, White, Red, Royal Blue, Green, Yellow, Orange, Purple, Pastel Pink/Blue/Lilac/Green/Yellow, Peach, Chrome Silver/Gold/Rose Gold/Blue/Copper, Blush, Canyon Rose, Caramel, Sangria, Chocolate, Slate Blue, Seafoam, Teal, Smoke Grey, Navy | `/shop` filters | Multi-choice family; product-specific max-count rules unknown. | No price extras observed for this axis. |
| latex colors | Long palette including Reflex Champagne/Truffle/Silver/Gold/Blue/Green/Violet/Red, Dusk Cream/Green Tea/Blue/Lilac/Rose, Teal, Blue Slate, Smoke Grey, White, black, Red, Orange, yellow, raspberry, fuchsia, bubble Gum, eucalyptus, Forest, Shamrock, Wintergreen, Lime, LT Blue, Periwinkle, Royal Blue, Robin's Egg, Deep Teal, Honey, Violet, Orchid, Lilac, Chocolate, Brown, Latte, Pastels, Grey, Clear, Blush, Empowermint | Classic Arch, Classic Organic Garland, Number Balloon Columns, Balloon Drop | Multi-checkbox in legacy_source; product copy says e.g. Classic Arch `up to 4 colors`, garlands `Select up to 4 colors`. | No price extras observed for latex color choices. |
| Design | Swirl (up to 4 colors), Layered (up to 8 colors) | Classic Arch | Required/default single-choice axis. | No price extra observed in fetch; [NO EVIDENCE] if layered changes price. |
| LED Lights | No Lights, Add LED Lights | Classic Arch | Single-choice add-on axis; default likely No Lights. | [NO EVIDENCE] for price extra in this pass. |
| Bouquet Size | Small — 1 super shape, 2 foils, 7 latex; Medium — 2 super shapes, 4 foils, 14 latex; Large — 3 super shapes, 5 foil 16 latex | Unicorn Bouquet (`/shop/unicorn-bouquet-115`) and bouquet family | Required/default single-choice size axis. | Unicorn Bouquet: base Small $35, Medium `+ $35`, Large `+ $50`. |
| Add Foil Number | Digits 1–9, 0; appears twice on Unicorn Bouquet | Unicorn Bouquet and likely number bouquet family | Optional add-on axis; duplicate axis likely supports two numbers. | Unicorn Bouquet: each selected number `+ $12`; duplicate axis means two independent foil-number positions. |
| Number selection | Digits 1–9, 0 | Number Balloon Columns | Required/default selection axis for personalized number column. | No price extra observed. |
| Number colors | Gold, Silver, Rose gold, pink, blue, white gold, Black | Number Balloon Columns | Required/default or option axis; exact validation unknown. | No price extra observed. |
| Drop Size | 250, 500, 1000 | Balloon Drop | Required/default single-choice size axis. | [NO EVIDENCE] for price deltas in this pass. |
| Add ons | None, Foil stars, themed foils | `/shop` filters | Optional add-on family. | [NO EVIDENCE] for deltas in this pass. |
| Plush add ons | None, Teddy Bear | `/shop` filters | Optional add-on family for baby/gift products. | [NO EVIDENCE] for deltas in this pass. |
| Graduation stands | Congrats, Yay, Missionary, Elder, Sister | `/shop` filters | Product-specific design/sign option family. | [NO EVIDENCE] for deltas in this pass. |
| skin color / Hair color / Baby color / Orbz toppers / Delivery Size / Delivery themes / Easter Designs / Add Bouquet | Observed in `/shop` filters | Product-specific personalization/add-on families | Unknown; need complete product export to bind axes to products. | [NO EVIDENCE] for deltas in this pass. |

### Valid combinations and option mechanics

Evidence:

- `deploy.py` exports each template's attribute lines as attribute-value lists and exports `product.template.attribute.value.price_extra` separately.
- Browser product pages render legacy_source variant controls and hidden `product_template_id` / `product_id` fields. One DOM sample for Classic Arch showed template ID `57` and selected product ID `91` with attribute line inputs such as `ptal-13` and `ptal-115`.
- legacy_source product pages include combination/variant signals in HTML; product variants are computed by legacy_source's native `website_sale` machinery.

Meaning to preserve:

- ERPNext should store each product's allowed axes and allowed values per product, not just global attribute names.
- Variant-generating axes (e.g. size) and non-variant/multi-select option axes (e.g. colors/add-ons) must stay distinguishable.
- Multi-select color axes need max-count validation where product copy states limits (`up to 4 colors`, `up to 8 colors`), but I found that as page copy, not as a validated legacy_source rule. Treat max-count enforcement as [UNKNOWN] until source/browser validation proves it.
- Duplicate option families can be intentional: Unicorn Bouquet shows `Add Foil Number` twice, likely two independent number positions. ERPNext must support repeated option groups or named positions rather than collapsing by label.

### Optional vs required choices

Observed legacy_source behavior suggests:

- Size/design axes rendered as single-choice radio/select groups are required by legacy_source because one value must be selected for a valid combination; legacy_source appears to default the first value.
- Multi-checkbox color axes are optional at the browser input level unless legacy_source custom JS or server validation enforces a minimum; no such validation was found in local custom code. Product copy asks customers to select colors, but enforcement is [NO EVIDENCE].
- Add-on axes with `None` values (`Add ons`, `Plush add ons`) are semantically optional; model them with an explicit no-add-on value where parity matters.
- Product inquiry form has required `contact_name` and `email_from`; event occasion/date/vision/photos are optional.

### Pricing sources / rules / gaps

legacy_source pricing sources:

1. Base product price: `product.template.list_price`.
2. Product-specific attribute value deltas: `product.template.attribute.value.price_extra`.
3. Delivery/checkout price: `delivery.carrier.fixed_price` backed by service products in `delivery_data.xml`.
4. Quote/deposit policy: public policy + automation server action for backend-created orders.

Verified examples:

- Classic Arch (`/shop/classic-arch-57`, template ID 57 observed): base $260; Arch Size 25ft +$65, 30ft +$130, 35ft +$195.
- Unicorn Bouquet (`/shop/unicorn-bouquet-115`): base Small $35; Medium +$35; Large +$50; each Add Foil Number digit +$12; duplicate Add Foil Number groups observed.
- Delivery carriers from source:
  - Pickup (Free): $0.
  - Standard Delivery: $15; zip prefixes 840, 841, 842, 843, 844, 846, 847.
  - Park City Delivery: $50; zips 84060, 84068, 84098.
  - Out-of-Area Quote: $35; source comment says customer may choose and Jeff reviews at invoice time.
- Shop grid examples observed: Classic Organic Garland $150, Basketball Arch $340, Number Balloon Columns $55, Easter Balloon Arch $375, Premium Organic Garland $216, Premium Organic Arch $720, Premium Organic Column $180.

Gaps:

- [NO EVIDENCE] Full price-extra table was not exported in this pass because browser JSON-RPC bulk extraction timed out/intermittently failed. `deploy.py` proves how to export it safely, but this artifact does not contain the complete live table.
- [UNKNOWN] Whether any discounts/coupons/loyalty rules are active; manifest depends on `sale_loyalty`, but no current checkout discount behavior was tested.
- [BLOCKED] Payment/checkout finalization was not tested due safety stop rule.

### Media/gallery/multi-photo/variant-image switching signals

Source evidence:

- `product_views.xml` adds a backend Images tab for `product_template_image_ids` with `image_1920`, allowing multiple additional images per product template.
- `deploy.py` exports/imports only primary `image_1920` for product templates in its current product sync shape; it does **not** export `product_template_image_ids` additional gallery images in the inspected lines.
- `seo_head.xml` product schema image points to `/web/image/product.template/<product.id>/image_1920`.
- Browser product pages use `/web/image/product.product/<id>/image_1024/...` image URLs for product imagery.

Meaning to preserve:

- ERPNext needs a primary product image plus a gallery/additional-images model.
- Variant-image switching is likely native legacy_source `website_sale` behavior via `product.product` images, but I did not confirm a user-visible image changes when changing a variant. Mark variant-image switching as [UNKNOWN] until a safe browser interaction test captures before/after image URLs.
- Additional template gallery migration is [RISK] because the inspected `deploy.py` sync path does not include `product_template_image_ids` records.

### Quote vs checkout behavior

Evidence:

- legacy_source shop pages include `Add to cart` for products like Unicorn Bouquet; public policy says `/shop` products are paid in full at checkout.
- Every product page has `Customize This for Your Event`, a CRM lead form that posts to `/website/form/` with hidden lead name `Product Inquiry: <product name>`.
- Product inquiry required fields: name and email. Optional fields: occasion, event date, vision, inspiration photos.
- `/book` and page/contact forms feed CRM/event request workflows rather than direct checkout.
- `automation_data.xml` explicitly skips custom invoice automation for website shop orders (`if order.website_id: continue`) because website checkout has its own flow.
- Public refund policy differentiates: small/shop orders paid in full at checkout; balloon twisting/face painting requires $50 deposit per artist; personal decor requires 100% upfront; corporate events are Net 30.

ERPNext implication:

- Preserve two entry paths: immediate cart/checkout for purchasable configured products, and inquiry/quote request for custom/event-specific work.
- Do not force every product into the same checkout-only path; some choices are quote/inquiry semantics even when displayed on product pages.

### Backend order/sales/invoice/operator data that matters

Source-backed legacy_source concepts to model or consciously replace:

- `sale.order` state `sent` is treated as a pending quote in portal code.
- Portal exposes orders, invoices, events/tasks, day-of details, upcoming events, and quote banners.
- Dashboard reads product count/list (`product.template` `sale_ok`, `list_price`, `website_published`, `type`, `active`, category), CRM leads, open/unpaid invoices, paid revenue, outstanding balance, calendar events, project tasks, payments, purchase orders, and messages.
- Security source separates employee/manager/admin/accountant visibility for invoices/payments/sale orders. Finance/operator views are role-sensitive.
- Invoice automation: backend-created product-only sale orders can become full posted invoices; backend-created service-line orders can create $50 deposit invoices; website shop orders are explicitly skipped.

ERPNext implication:

- Ecommerce rebuild must not only receive products/cart lines. It must leave enough trace for operator follow-up: quote/order/invoice/payment/event task linkage, customer portal visibility, and staff dashboard review.

## Explicit unknowns / blockers

- [NO EVIDENCE] Complete live product/attribute/price-extra export table was not captured into this artifact. Safe route exists (`deploy.py` export shape), but browser JSON-RPC bulk extraction timed out/intermittently failed before I could include the whole table.
- [UNKNOWN] Full valid-combination matrix for every product. legacy_source computes variants from product attribute lines; this artifact maps observed families and mechanics, not every combination.
- [UNKNOWN] Server-side validation for color count limits. Product copy says up to 4/8 colors, but local custom code inspected did not show enforcement.
- [UNKNOWN] Variant-specific image switching. Source and legacy_source behavior imply product/product-template image support, but no before/after browser interaction was captured.
- [BLOCKED] Checkout/payment/deposit execution was intentionally not tested.
- [NO EVIDENCE] Active Stripe/payment-provider configuration and active coupon/loyalty behavior were not inspected.
- [RISK] `deploy.py` product sync includes primary images but not inspected additional gallery image export; gallery parity needs a dedicated read-only extraction before rebuild.

## Actionable next steps

1. Run a read-only legacy_source product export using the existing `deploy.py` export shape or equivalent safe server-side script, limited to product/category/attribute/value/price-extra/image metadata only. Do not include partners/leads/customer records.
2. Convert export into an ERPNext-facing product option matrix:
   - product template/page ID and route
   - base price
   - category paths
   - option groups
   - allowed values
   - required/default/multi-select flags
   - price extras
   - image/gallery references
3. Add a dedicated gallery/variant-image witness pass: for 5–10 representative products, capture primary image, gallery count, and variant-change image URL behavior.
4. Add a safe cart-only browser parity pass without submitting checkout/payment: configure representative products, confirm displayed price math/cart line semantics, then abandon/reset cart only with explicit permission.
5. Model ERPNext with separate concepts for:
   - Product Template / Product Page
   - Option Group
   - Product Option Value
   - Product-specific Option Price Extra
   - Product Gallery Image
   - Inquiry/Quote Form Submission
   - Delivery Method/Zone
   - Checkout Order vs Quote/CRM lead
6. Treat legacy_source as source witness for commerce meaning, but verify ERPNext implementation against browser/test evidence before any purge/rebuild/import.

## Verification gate

- Verified local source by direct file reads and targeted `rg` searches.
- Verified public legacy_source product/category/option behavior by browser snapshot and `web_fetch` on representative product routes.
- Verified no code changes/commits/product mutations were made during this lane.
- Artifact created at `workstreams/ecommerce-audit/legacy_source-source-commerce-map-2026-05-10.md`.

## Risk / rollback notes

- This artifact is additive documentation only. Rollback is deleting this one markdown file.
- Do not use this artifact as a complete import manifest; it intentionally marks missing live export tables as [NO EVIDENCE].
- Biggest rebuild risk: collapsing legacy_source's product-specific attributes/price extras/multi-select add-ons into flat ERPNext Item records will lose working commerce behavior.
