# Ground Truth Findings: E-commerce Platform Fit
## Date: 2026-05-10
## Source Type: Codebase, Git History, Infrastructure
## Project: Locally Twisted — ERPNext v15.105.0 + Frappe v15.106.0
## Files Examined: ~35 source files, git history, running Docker containers

---

## What Already Exists

### 1. The LT Custom App — Overrides and Extensions

**What:** The `locally_twisted` Frappe app is the sole customization layer. All product-page behavior is contained here.

**Location:** `apps/locally_twisted/locally_twisted/`

**Status:** Active. All verifier suites pass as of 2026-05-10 (`technical_architecture_ok: True`, `import_reopen_ok: True`, 14 pass rows, 0 blockers, 1 finance deferral).

**What hooks.py registers (the full surface area):**
- `web_include_css`: 9 CSS files (theme, mega-menu, product polish, shop showroom, product visual-first, page containment, photo heroes, form experience, event playground).
- `web_include_js`: 7 JS files including `lt-guest-cart.js`, `lt-megamenu.js`, `lt-product-card-click.js`.
- `website_route_rules`: 14 route rules including the critical `/cart` → `lt_cart` and `/all-products` → `shop` overrides.
- `override_whitelisted_methods`: Overrides `webshop.webshop.api.get_product_filter_data` with `locally_twisted.api.product_listing.get_product_filter_data` (to inject `lt_brand_description` into listing cards).
- `doc_events`: Lead `before_insert`/`after_insert`/`on_update` for the cascade; Email Queue `before_insert` for delivery guard.
- `jinja.methods`: `locally_twisted.product_options` and `locally_twisted.commerce_rules` (expose Jinja helpers like `get_variant_attribute_options`, `get_balloon_color_groups`, `checkout_lane_for_item_group`).
- `before_request`: `locally_twisted.ecommerce_pause.before_request` (gate that can pause all ecommerce routes).
- `scheduler_events`: hourly/daily heartbeat and business automation index checkups.
- `fixtures`: Item Group children (11), Item Attribute records (24), Custom Field records (34+).

**Location:** `apps/locally_twisted/locally_twisted/hooks.py`

### 2. The Two Product Page Templates

**What:** Two fully-built product-page control surfaces replacing Webshop's default "Select Variant" button.

**Ready-to-order page (`item_configure.html`):**
- Location: `apps/locally_twisted/locally_twisted/templates/generators/item/item_configure.html`
- Status: Active.
- What it does: Renders inline attribute selectors. Color axes (`latex colors`, `Color Palette`, `number colors`, `baby color`) render as grouped color-swatch drawers (accordion groups: Reflex, Dusk, Pastels, Blues + Teals, Greens, Pinks + Purples, Neutrals, Brights). Non-color axes with ≤8 values render as chip radio buttons. Higher-cardinality non-color axes render as select dropdowns.
- Variant resolution: JS calls `webshop.webshop.variant_selector.utils.get_next_attribute_and_values` to find `exact_match` and `valid_options_for_attributes`.
- Photo swap: On `exact_match`, JS calls `locally_twisted.api.variant_media.get_variant_media` to fetch `Item.image` for the resolved variant. If variant has no distinct image, falls back to `Website Item.website_image`.
- Add-on selector: Renders `foil_number` add-on when backend eligibility confirms it (via `get_checkout_add_on_options`). Requires number entry before enabling Add-to-Cart.
- Add-to-cart: Calls `webshop.webshop.shopping_cart.update_cart` with a versioned `lt-product-config-v1` configuration payload.
- **Critical limitation documented in source:** Line 70: `"Choose one balloon color for current pricing. Multi-color recipes will be handled in the rebuilt catalog contract."` Line 322-324: `"// Temporary bridge for the current ERPNext variant model: one color maps to the SKU used for price/cart lookup. The purge/rebuild will move multi-color recipes out of SKU axes."` — Color is treated as a single-select SKU dimension; the product copy says "up to 4 colors" but the current ERPNext model can only resolve one color per variant combination. Multi-color combinations are not currently sellable through the ready-to-order path.

**Custom quote page (`item_quote_first.html`):**
- Location: `apps/locally_twisted/locally_twisted/templates/generators/item/item_quote_first.html`
- Status: Active.
- What it does: Renders the same color drawers (checkbox multi-select, not radio) plus design notes and color notes text areas. No variant resolution or price display. Links to `/contact` with a pre-built `lt_product_quote_handoff_v1` payload in sessionStorage.
- Color handling here: colors are captured as `color_recipes` (multi-value arrays per axis), not collapsed into single-SKU mapping. This is the correct multi-color path for catalog_data-style color combos.

### 3. Variant Media Swap

**What:** Backend whitelisted API that returns the variant image or falls back to the template image.

**Location:** `apps/locally_twisted/locally_twisted/api/variant_media.py`

**Status:** Active and tested. `scripts/verify/variant_media_contract.py` passes.

**What it does:** Takes `item_code` (a variant Item), returns `Item.image` if present, otherwise `Website Item.website_image`. Returns `has_variant_image: True` only when the variant image differs from the fallback. Falls back cleanly.

**Limitation:** Only single-image per variant (no gallery per color). The `product_options.py::get_product_gallery_slides` function assembles a gallery from all variant `Item.image` records sorted by item code — this is a temporary multi-image surface until proper `Website Slideshow` records exist. Current live DB: 1,751 active variant `Item.image` rows (out of 10,227 active variants), so 83% of variants have no distinct image.

**Confirmed data state:** 95 source extra images across 49 products are unclassified. No `Website Slideshow` records exist for approved parent-gallery media. Source: `audits/catalog-import-audit-2026-05-08/23-product-page-media-classification-packet.md` and `20-product-page-media-visibility-report.md`.

### 4. Guest Cart (Custom, Replaces Webshop's)

**What:** Full localStorage-backed guest cart that replaces Webshop's login-required cart.

**Location:** `apps/locally_twisted/locally_twisted/api/cart.py` (backend), `apps/locally_twisted/locally_twisted/www/lt_cart.py` (page), `apps/locally_twisted/locally_twisted/public/js/lt-guest-cart.js` (frontend).

**Status:** Active. Route `/cart` → `lt_cart` via `website_route_rules`.

**What it does:**
- Client stores cart in localStorage as `[{item_code, qty, configuration, cart_line_key}]`.
- `/cart` page calls `locally_twisted.api.cart.get_cart_items` to validate and enrich each line server-side.
- Server re-prices everything from `Item Price` — client-supplied prices never trusted.
- `cart_line_key` includes hashed configuration so same SKU with different add-ons/options stays separate.
- Returns `missing` list for unpublished, unpriced, or quote-required items so client can drop them with a notice.
- Add-on display: cart API expands `foil_number` add-on into `display_lines` with label, quantity, unit price, and line total visible in cart.

### 5. Guest Checkout (Custom, Full Stripe Integration)

**What:** Full custom checkout bypassing Webshop's checkout entirely.

**Location:** `apps/locally_twisted/locally_twisted/www/checkout.py`

**Status:** Active. Verified working (GL completed real `4242` test purchase 2026-04-29).

**What it does:**
- Accepts `item_code`/`qty` (buy-now) OR `items_json` (multi-item cart payload).
- Server re-prices from `Item Price`. Client prices never trusted.
- Creates Customer + Contact (no User account) + Sales Order + Payment Request + Stripe Checkout Session.
- Returns Stripe hosted URL; caller redirects.
- Tax: Utah destination-based tax via `commerce_rules.resolve_tax_rate`.
- Fulfillment: pickup (West Jordan / Riverdale) or delivery (Standard $15 / Park City $50 / Out-of-Area quote / quote-required zones).
- Writes versioned configuration to `Sales Order Item` custom fields (`custom_lt_configuration_json`, `custom_lt_configuration_summary`, `custom_lt_configuration_version`).
- Quote-first items blocked at checkout via `product_page_contract_for_website_item`.

### 6. Color Grouping Infrastructure (Qualatex Map)

**What:** Python module that classifies ~55+ balloon color names into visual groups with approximate hex values.

**Location:** `apps/locally_twisted/locally_twisted/catalog_contract/color_rules.py`

**Status:** Active and called from `product_options.py`.

**What it provides:**
- `QUALATEX_GUIDE_APPROX_HEX`: 55 color-name → hex mappings (sampled visually from Qualatex guide image; labeled as approximate).
- `classify_color_name`: Buckets into Reflex, Dusk, Pastels, Blues + Teals, Greens, Pinks + Purples, Neutrals, Brights, Review Needed.
- `grouped_colors`: Used by `get_balloon_color_groups` Jinja helper for the drawer rendering.
- `is_balloon_color_axis`: True for `latex colors`, `Color Palette`, `number colors`, `baby color`.

### 7. Product Page Runtime Contract

**What:** Backend Python module that owns commerce lane determination (checkout vs. quote_first vs. needs_review) for each Website Item.

**Location:** `apps/locally_twisted/locally_twisted/product_page_runtime.py`

**Status:** Active. `product_page_runtime_contract.py` verifies.

**Key behavior:**
- Reads `Website Item.lt_product_page_type` and `Website Item.lt_commerce_lane` fields.
- Falls back: if stored value is `needs_review` and the item has color axes or multi-axis complexity, infers `quote_first`.
- `product_page_contract_for_website_item` is the single source of truth for whether an item can enter paid checkout.
- `ADD_ON_ITEM_CONTRACTS`: dict of confirmed add-ons. Currently only `foil_number` at $12.
- `cart_line_key`: hashes item_code + configuration JSON for localStorage deduplication.
- `sales_order_add_on_lines`: expands configuration into explicit SO Item rows for add-ons.

### 8. Quote-First Pipeline (Complete)

**What:** Full pipeline from product-page quote to draft Sales Order.

**Location:** Multiple files — `product_quote_runtime.py`, `product_quote_acceptance.py`, `product_quote_customer_delivery.py`, `product_quote_operator_send.py`, `www/quote_accept.py`.

**Status:** Active. All contract verifiers pass.

**What it does:** Quote-first product page → sessionStorage payload → `/contact` → Lead → draft Quotation (automatically) → operator review → BCC-gated customer email with tokenized approval link → `/quote-accept` → draft Sales Order. Zero invoice/payment side effects at any step.

### 9. Webshop's Native Variant Machinery (What LT Inherits)

**What:** Webshop's `variant_selector/utils.py` provides two key whitelisted methods.

**Location (in container):** `/home/frappe/frappe-bench/apps/webshop/webshop/webshop/variant_selector/utils.py`

**Status:** Active; LT calls it directly.

**`get_attributes_and_values`:** Builds the list of valid attribute values for a template. Reads from `ItemVariantsCacheManager`. Used by LT's `get_variant_attribute_options` to get the attribute list, which LT then filters through `required_variant_attribute_names`.

**`get_next_attribute_and_values`:** Given a template + selected attributes so far, returns `exact_match` (list of variant item codes), `valid_options_for_attributes` (what's still available given current picks), and `product_info` with price. LT's `item_configure.html` calls this on every change event to drive the inline selector.

**Webshop's stock `item_configure.html`:** Simply renders a "Select Variant" button that opens a Frappe Dialog — no inline options, no color drawers, no photo swap. LT overrides this entirely.

**Webshop's `Website Item` schema:** Has `slideshow` field (link to `Website Slideshow` DocType) and `website_image`. Gallery support exists natively via `Website Slideshow` → `Website Slideshow Item` child records. LT is not yet using `Website Slideshow` records; the gallery in `item_image.html` is a custom implementation pulling from `Item.image` across all variants.

### 10. Catalog Data State

**Verified counts (from `PROJECT-STATUS.md` and `workstreams/erpnext-ecommerce-receiving-architecture.md`):**
- 53 Website Items (published product templates)
- 10,672 Items total
- 49 variant templates; 6 non-variant root Items
- 10,227 active customer-facing variants
- 390 disabled legacy optional-add-on variants
- 10,617 all variant records
- 10,654 Item Prices
- 32,028 Item Variant Attribute child rows
- 26 Item Attributes

**Source audit classification (from `15-product-page-contract-source-audit.json`):**
- 15 products classified as `simple_product` / Ready-to-order page candidates
- 38 products classified as `complex_custom_product` / Custom quote page candidates
- `blocked_for_destructive_import: true`
- Blockers: `missing_resolver_prices: 49`, `unclassified_gallery_images: 49`, `axis_needs_review: 9`, `color_axis_customization: 25`

**Price state:**
- 13 bouquet templates repaired with per-size prices (Small $35 / Medium $70 / Large $85) via catalog_data `get_combination_info` scraper (`repair_variant_prices_from_catalog_source.py`).
- 36 non-bouquet templates still have live-snapshot prices (single price copied from catalog_data page base price at scrape time — not per-variant price deltas). 273 live-snapshot-priced sale units in the review packet, 0 approved for public pricing.

---

## What Was Tried Before

### Failed: Webshop's default "Select Variant" dialog button

- **What:** Stock Webshop renders a "Select Variant" button that opens a Frappe Dialog with attribute selectors hidden behind a click.
- **When:** Pre-2026-04-30 (before `item_configure.html` override). Commit `dd37d9c` wrote the first LT override; `f6342a3` hardened it.
- **Outcome:** Replaced. GL flagged as "missing options."
- **Why it stopped:** Dialog-behind-click hides what the customer can pick at a glance. Replaced with inline chip/select/color-drawer rendering.

### Failed: Per-attribute Frappe DB lookups in Jinja (item_configure.html)

- **What:** An earlier version of `item_configure.html` ran `frappe.get_all("Item Attribute Value", parent=<attr>)` per attribute inside Jinja.
- **When:** Identified and fixed around 2026-04-30/2026-05-02. Decision log entry at line 2504: "Superseded implementation detail 2026-05-02: inline selectors remain, but the template no longer performs per-attribute `frappe.get_all` calls from Jinja."
- **Outcome:** Replaced with `get_attributes_and_values` one-call-for-all-attributes approach.
- **Why it stopped:** Performance issue (N+1 queries) and incorrect filtering.

### Failed: Unpriced variant template codes added to cart

- **What:** Template items (with `has_variants=True`) were being added to the guest cart instead of a resolved variant.
- **When:** Fixed ~2026-05-02. Decision entry at line 2079: "Variant cart contract uses sellable Item codes with parent Website Item display."
- **Outcome:** Cart server-side resolver now checks `has_variants` and returns `"choose_options"` reason if the template code is submitted.

### Fixed: Single-price scraper problem (bouquets repaired, 36 others pending)

- **What:** Original `scrape_catalog_data_live.py` copied the page's base/display price into every variant, creating flat pricing (e.g., all Unicorn Bouquet sizes showing $35 instead of Small $35 / Medium $70 / Large $85).
- **When:** Commit `c7f9da3` on 2026-05-08.
- **Outcome:** Added `repair_variant_prices_from_catalog_source.py` which hits catalog_data's `website_sale/get_combination_info` route per combination to get correct price deltas. Fixed 13 bouquet templates. 36 non-bouquet templates still pending — these need the same resolver treatment but haven't been run yet.
- **Relevance now:** The repair approach works (calling live catalog_data's `combination_info` endpoint). The 36 remaining templates are a known gap, not a structural impossibility.

### Fixed: head_html + !important CSS overrides (Slice 2 failure)

- **What:** Early CSS injection via `Website Settings.head_html` with `!important` chains.
- **When:** 2026-04-26 (Slice 2 build session). Committed in `066547d`.
- **Outcome:** Completely replaced with `web_include_css` hook and Jinja template overrides.
- **Why it stopped:** `head_html` renders BEFORE Frappe's bundled CSS; equal-specificity bundle rules silently won.

---

## Established Patterns

### Template override pattern
- LT places same-named files at `apps/locally_twisted/locally_twisted/templates/generators/item/` — they win Frappe's reversed-app-order ChoiceLoader because `locally_twisted` is last in `installed_apps`.
- Overridden templates: `item.html`, `item_image.html`, `item_details.html`, `item_configure.html`, `item_add_to_cart.html`, plus new `item_quote_first.html`.

### Commerce lane determination pattern
- Every product page decision flows through `product_page_contract_for_website_item(item_code)` → returns `product_page_type` and `commerce_lane`.
- Stored on `Website Item.lt_product_page_type` and `Website Item.lt_commerce_lane`. Currently all 53 products stored as `needs_review`; runtime inference provides behavioral fallback.

### Fail-loud pattern (enforced by verifiers)
- Every cross-system handoff has a verifier: `product_page_runtime_contract.py`, `cart_checkout_contract.py`, `product_add_on_dependency_contract.py`, etc.
- Architecture readiness gate at `verify/product_page_architecture_readiness.py` runs all contract verifiers and blocks on any failure.

### Server-side pricing authority
- Client prices never trusted at any layer: cart API, checkout page, Sales Order creation.
- Price always comes from `Item Price` (Standard Selling price list) for the specific variant `item_code`.

### Versioned configuration payloads
- All product configurations travel as `lt-product-config-v1` JSON: `{schema_version, item_code, website_item_code, selected_options, add_ons, customizations}`.
- Written to `Sales Order Item.custom_lt_configuration_json` and `Sales Invoice Item.custom_lt_configuration_json`.

---

## Integration Points

### What Webshop provides that LT still uses
- `get_next_attribute_and_values`: variant resolution and progressive option narrowing. LT calls this on every option change.
- `get_attributes_and_values`: attribute/value list for a template. LT calls this via `get_variant_attribute_options`.
- `shopping_cart.update_cart`: add-to-cart function. LT's `item_configure.html` calls this with the versioned payload. LT's `lt-guest-cart.js` overrides the browser-side behavior (intercepts Webshop's login redirect, writes to localStorage instead, keeps cart badge live).
- `Website Item` DocType: the core product publishing record. LT adds custom fields on top.
- Webshop's product listing API (`get_product_filter_data`): LT overrides this via `override_whitelisted_methods` to inject `lt_brand_description`.

### What LT has fully replaced
- `/cart` page: completely replaced (`lt_cart.py`/`lt_cart.html`).
- `/checkout` page: completely replaced (`checkout.py`/`checkout.html`).
- `item_configure.html`: completely replaced.
- `item_details.html`: completely replaced.
- `item_image.html`: completely replaced.
- Cart/checkout data model: localStorage-backed, no Webshop `cart` table used.

### What Webshop's item page still provides (inherited)
- Product page routing (`/shop-items/<group>/<slug>` format).
- `get_context` for product pages (populates `doc`, `slides`, `shopping_cart`, `product_info`).
- Wishlist functionality (referenced in `item_details.html` but LT keeps it as inherited behavior).

---

## Constraints and Risks

### The color-combo data model constraint (CRITICAL)

The current ERPNext data model represents each color as a separate variant SKU axis. A "Red + Gold" balloon arch requires a variant item with `latex colors = Red AND latex colors = Gold` — but ERPNext's variant model is single-value per attribute axis per variant. This is the structural root of the "multi-color combo" problem.

The LT codebase acknowledges this explicitly:
- `item_configure.html` line 70: `"Choose one balloon color for current pricing. Multi-color recipes will be handled in the rebuilt catalog contract."`
- `item_configure.html` lines 322-324: `"// Temporary bridge for the current ERPNext variant model: one color maps to the SKU used for price/cart lookup. The purge/rebuild will move multi-color recipes out of SKU axes."`

This is not a Webshop limitation — it is an ERPNext Item/Variant data model limitation. Webshop renders what ERPNext's variant model can represent. Any platform using ERPNext as backend faces this same structural constraint for multi-color combos unless a separate data structure is used (e.g., capturing color combos as free-text/JSON in a custom field rather than as variant axes).

**Resolution path already identified:** Quote-first color captures use `color_recipes` (multi-value JSON arrays), bypassing the SKU-axis constraint. The architectural split is already implemented: products where color combos matter should be `quote_first`; products where a single-color selection is meaningful for pricing (e.g., bouquets where the base price doesn't change by color) can be `checkout`.

### The 10,227-variant-to-SKU-axis problem

catalog_data's `website_sale` manages variant pricing via `price_extra` on `product.template.attribute.value` — a delta per attribute value. ERPNext requires a separate `Item Price` record per full variant combination (item code). With 10,227 active variants across 53 templates, every price delta in catalog_data needs a distinct `Item Price` row in ERPNext.

The `repair_variant_prices_from_catalog_source.py` script resolves this by calling catalog_data's `get_combination_info` for each required combination. 13 templates done; 36 remaining. This is implementation work, not a platform architectural barrier.

### Webshop's variant gallery: no native per-variant image gallery

Webshop's `Website Item` has `website_image` (single) and `slideshow` (link to `Website Slideshow` DocType). There is no native per-variant gallery. LT's current `item_image.html` builds a gallery from all variant `Item.image` records — a working improvisation that will become proper `Website Slideshow` records at import time.

catalog_data's `website_sale` also has no native per-variant image gallery in its upstream source — variant images are stored on `product.product` records (one image per variant), which is functionally equivalent to ERPNext's `Item.image`. The catalog_data LT custom module adds a backend Images tab via `product_template_image_ids` (template-level gallery), but `deploy.py` does NOT export these extra images — they exist in catalog_data admin but are not in the scraped catalog.

---

## Gaps

### Gap 1: Color combinations as sellable checkout units

Currently impossible as ready-to-order checkout for products where customer wants multiple specific colors. Current ERPNext variant model cannot represent "Red + Gold + Navy" as a single purchasable unit resolved from three color attribute values simultaneously.

Architectural decision already made: color-heavy products route to `quote_first`. The quote captures multi-color recipes as JSON. This is the correct resolution within the ERPNext constraint.

### Gap 2: Per-variant pricing for 36 non-bouquet templates

36 templates still have scraper-copied base prices on all variants instead of correct per-size/per-attribute deltas. `repair_variant_prices_from_catalog_source.py` can fix these by calling catalog_data's `get_combination_info`. This is implementation backlog, not a data model impossibility.

### Gap 3: Gallery / multi-image per product

No `Website Slideshow` records exist. Gallery currently improvised from variant `Item.image` records. 95 source extra images unclassified. This needs classification and `Website Slideshow` record creation.

### Gap 4: All 53 Website Items still stored as `needs_review`

All 53 `Website Item.lt_product_page_type` and `lt_commerce_lane` fields are `needs_review` in the live DB. Runtime inference provides behavioral fallback. The architecture for explicit classification exists (field sync via `seed/sync_commerce_rules.py`), but the bulk update hasn't run.

### Gap 5: Cart UX polish

The cart (`lt_cart.py`) is functionally complete but GL describes the cart UX as a "disaster." The cart page renders via a shell with JS hydration — this may feel slow or rough on first load. The checkout page is custom and complete.

---

## Disconfirmation Search

### Claim being checked: "The 'disaster' is an implementation build approach problem, not a Webshop platform-ceiling problem."

**Supporting evidence:**
- Every specific "Webshop is wrong" moment in git history resolved to implementation defects that were fixed without changing platforms:
  - Unpriced variant in cart → fixed by server-side `has_variants` check.
  - Per-attribute Jinja DB queries → fixed by using `get_attributes_and_values`.
  - CSS not applying → fixed by correct `web_include_css` hook.
  - Variant price flatness → fixed for bouquets; repair script exists for the rest.
- Architecture readiness audit passes (`technical_architecture_ok: True`).
- The core Webshop machinery (`get_next_attribute_and_values`, `get_attributes_and_values`) is working correctly and LT uses it.

**Disconfirming evidence (where Webshop's ceiling IS the limit):**

1. **Multi-color combinations as sellable checkout SKUs.** This is a HARD ceiling. ERPNext Item Variant data model = one value per attribute per variant. You cannot sell "Red + Gold + Navy" through a checkout path in ERPNext without fundamentally changing the data model (e.g., making color free-text on a custom field rather than a variant axis). Webshop renders what ERPNext models; changing platforms doesn't help if ERPNext stays the backend. **This is an ERPNext constraint, not a Webshop constraint.**

2. **Cart UX "disaster" claim not verified by code inspection.** The cart is a custom LT implementation (`lt_cart.py`) that completely replaces Webshop's cart. If the cart UX is a "disaster," it's LT's own cart code that's the problem, not Webshop's cart. GL's complaint about Webshop's cart UX may have predated the custom cart replacement.

3. **50+ color swatch grid.** The color drawer infrastructure EXISTS and is functioning (`color_rules.py`, `item_configure.html` color drawer rendering, `get_balloon_color_groups` Jinja helper). The constraint is not displaying the swatches — that works. The constraint is: a single-color selection resolves to a single ERPNext variant SKU. If the customer needs to pick 4 colors, the current ready-to-order path only captures one of them. **This is the ERPNext constraint again, not a Webshop display problem.**

4. **Iteration tempo: "fail at everything, then build the feature."** Git log shows this is Codex's build pattern (iterative small hardening commits). The commits from the last two weeks show 40+ commits, mostly incremental hardening (email routing, nav cleanup, quote gates, verifier cleanup). The product-page feature iteration (color drawers, add-on selector, gallery) happened in larger feature slices earlier. The current iteration tempo is NOT Webshop failing — it's the LT codebase being hardened for launch with verifier enforcement.

**The architecture readiness audit passes 14 criteria and 0 blockers.** This directly contradicts the "disaster" framing at the architectural level. What it does NOT prove: that the customer-visible UX for color selection and multi-color combos is good. The architecture is sound; the product-page experience for color-heavy products is legitimately incomplete for the multi-color use case.

---

## catalog_data `website_sale` Benchmark — What It Actually Has

This is the implicit benchmark GL refers to when saying "catalog_data had so much more depth."

**Per-variant images:** Stored on `product.product` records (one image per variant). The `deploy.py` catalog exporter captures only `image_1920` on `product.template` (primary product image), NOT `product.product` variant images AND NOT `product_template_image_ids` extra gallery images. This means even catalog_data's own export pipeline didn't include the full variant-image set. Equivalent to ERPNext's `Item.image`.

**Combination info / dynamic pricing:** `website_sale/get_combination_info` is catalog_data's JSON-RPC endpoint that returns price, availability, and image URL for a specific attribute combination. LT already reverse-engineered and uses this at `catalog_data_COMBINATION_ROUTE` in `repair_variant_prices_from_catalog_source.py`. ERPNext's equivalent is `get_next_attribute_and_values` which returns `product_info.price.formatted_price_sales_uom` for the exact match.

**Color swatch rendering:** catalog_data's `website_sale.variants` template renders `html_color` from `product.attribute.value` as colored dots. LT's `website_sale_templates.xml` (the catalog_data custom module) overrides this to use `ptav.html_color` for color dots on multi-checkbox attributes. ERPNext has no native `html_color` on Item Attribute Value — LT's `color_rules.py` approximates this with the Qualatex hex map. Functionally equivalent, but catalog_data's `html_color` is operator-editable per attribute value; LT's hex values are hardcoded in Python.

**Conditional attribute display / multi-attribute variant navigation:** catalog_data uses native `product.template.attribute.line` with `create_variant` flag to distinguish variant-generating axes from non-variant multi-select axes. `display_type` on the attribute controls radio vs. multi-checkbox vs. color pill rendering. ERPNext has no equivalent `display_type` on Item Attribute — all attributes are treated as variant-generating axes. LT's `addon_rules.py` and `color_rules.py` provide a code-level equivalent by classifying axes as required variant / optional add-on / color customization.

**Cart:** catalog_data's built-in cart is server-side, requires login or creates a guest session. LT's cart is localStorage-backed guest cart (custom). Functionally LT's cart is more capable for guests.

**Checkout:** catalog_data's checkout uses its native payment provider stack. LT's checkout uses Stripe Checkout Sessions (modern, hosted). LT's checkout is more capable (guest checkout, Utah tax resolution, pickup/delivery logic).

**The honest comparison:** catalog_data's `website_sale` is more mature and battle-tested. The main concrete depth advantage is that `product.attribute.value.html_color` is operator-configurable in the catalog_data admin, while LT's hex values are hardcoded in Python and require a code deploy to add new colors. Everything else is either matched or exceeded by LT's custom implementation.

---

## Synthesis

**What the codebase actually says about the "disaster" framing:**

The "disaster" language predates much of what is now built. The specific pain points GL described in the research brief (50+ color swatches, photo swap, variant pricing, cart UX) have been substantially addressed:

- 50+ color swatch grid: EXISTS (color drawers with Qualatex hex map).
- Photo swap on variant selection: EXISTS (`get_variant_media` API + JS update in `item_configure.html`).
- Variant pricing: EXISTS for bouquets (13 templates); 36 others are known backlog with a working repair script.
- Cart UX: The cart is now LT's own custom implementation — Webshop's cart is not in use.

**What genuinely doesn't exist yet:**
- Multi-color combos as checkout units (this is an ERPNext data model constraint, not Webshop).
- Color selections as operator-configurable hex values in admin (currently hardcoded in Python).
- Gallery with proper `Website Slideshow` records (95 source images unclassified).
- Explicit product page classification (all 53 Website Items still `needs_review`).

**The path of least resistance:** Continue on Webshop. The heavy lifting (custom cart, custom checkout, variant media API, color drawer infrastructure, quote-first pipeline, add-on subsystem, commerce rules, verifier suite) is already done and passing. The remaining work (price repair for 36 templates, gallery classification, product page classification, multi-color route to quote-first) is implementation backlog, not a platform rebuild.

**What would change under any pivot option:**
- The ERPNext backend (Items, Item Prices, Item Variant Attributes, Sales Orders, Customers, Stripe via `frappe/payments`) stays regardless of option.
- The LT custom app's commerce rules, checkout, cart, quote pipeline — all custom code — would need to integrate with a new platform's data surface.
- The 10,654 Item Prices are not tied to Webshop; they are ERPNext-native records.
- The `get_next_attribute_and_values` Webshop method is the one genuine Webshop dependency in the product-page flow. This could be re-implemented in LT's own app if Webshop were removed.

**What surprised me:**
1. The cart and checkout pages are ALREADY fully custom LT code. GL's complaint about "Webshop's cart UX" appears to predate the custom cart replacement. The current `/cart` and `/checkout` have no meaningful Webshop dependency.
2. The multi-color combo problem is an ERPNext constraint, not a Webshop constraint. Switching to Medusa/Saleor as a storefront frontend still leaves the ERPNext item variant model as the source of truth for pricing and inventory — the constraint doesn't move.
3. The architecture readiness audit passing with 14/14 criteria and 0 blockers is a surprisingly strong signal given GL's "disaster" framing. The verifier suite is thorough and rollback-safe.
4. catalog_data's own `deploy.py` export script did NOT include variant images or template gallery images — the depth advantage GL remembers from catalog_data's admin UI is not reflected in catalog_data's own export tooling.
5. The "Temporary bridge" comment in `item_configure.html` (line 322) is a candid admission that the color-to-SKU mapping is a known architectural debt with a named resolution path (catalog rebuild). This is healthy — the debt is named and bounded.
