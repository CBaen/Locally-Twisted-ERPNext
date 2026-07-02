# LT Website + Ecommerce — Page-by-Page Build Index

**Status:** v2 — GL-confirmed 2026-04-26. All open questions resolved. Build order locked.

**Scope:** Customer-facing website + ecommerce + payment process only. NOT operator workflow, NOT lead intake (those are Phase 2/3). The point of this index is to lock the build approach BEFORE writing code, so we don't repeat the override-the-framework mistake.

---

## What this index is for

You showed Jeff catalog_data and it broke. The recovery move is to show him a system that **doesn't break** — and the way it doesn't break is by standing on Frappe's tested foundation rather than on our own scaffolding.

This index sorts every page we need into four tiers based on **how much we're modifying Frappe's code** (not how much visual customization we want):

| Tier | What we do | Risk profile |
|---|---|---|
| **1. Settings-only** | Configure Website Settings, Webshop Settings, DocType records (Item, Item Group, Web Page, Blog Post, etc.). No template files written. | Near zero. We're using the framework as designed. |
| **2. Page Builder + theme CSS** | Use Frappe's Web Page record with Page Builder for layout. Apply LT colors/typography via `lt-theme.css` already loaded by `web_include_css`. No template overrides. | Low. Page Builder is a Frappe primitive; theme CSS via `web_include_css` is the documented surface. |
| **3. Native page + content** | Frappe ships the page; we just configure the content. Zero customization beyond what Settings already inject. | Lowest. |
| **4. Custom code required** | Genuinely irreducible. No native primitive does this thing. We add the minimum code, in the right Frappe primitive (custom Web Template, hook, www/ page, custom DocType), and it gets called out as a deliberate decision in the decisions log. | Higher. Explicit opt-in only. |

**The pitch to Jeff** for tiers 1–3: *"Every page on your new site is built on Frappe's tested foundation. We added LT's colors, fonts, voice, and your products — but we didn't override anything Frappe owns. That's why it'll keep working when Frappe ships updates, and why we don't have to debug surprises."*

The **goal of this index** is to push every page as low in the tier list as possible. Most things should land in tier 1 or 2. Tier 4 should be small, named, and deliberate.

---

## Page-by-page map

### Header + Footer (sitewide)

| Item | Tier | Native source | What we add | Notes |
|---|---|---|---|---|
| Header (logo, nav, sign-in, cart) | **1** | Frappe's standard navbar (`apps/frappe/frappe/templates/includes/navbar/navbar.html`) renders from `Website Settings.top_bar_items` + `brand_html` + `banner_image` | Set `brand_html` to the LT logo PNG; populate `top_bar_items` per the resolved nav decision (Option B); LT theme CSS styles colors/typography | We already have the data wired (from the prior Slice 2 attempt's setup script). Strip the `!important` chains from `lt-theme.css` and the header is done. |
| Footer (columns, brand block, copyright) | **1** | Frappe's standard footer (`templates/includes/footer/footer.html`) renders from `Website Settings.footer_items` + `footer_address` + `copyright` | Configure `footer_items` for Shop / Company / Get In Touch columns; set `footer_address`; set `copyright` (without leading `©`); LT theme CSS for colors | Same — data is mostly wired. **What it WON'T have natively:** the centered brand block + 3 social icons + hours block in the exact catalog_data layout. **My recommendation: live with Frappe's default footer layout.** Per your directive, this is exactly the "doesn't need to look special, needs to be natively functional" call. |

**Outcome:** Header and footer are tier 1. The previous Slice 2 attempt was overcomplicated. Reset to native + colors and stop.

---

### Marketing pages (landing + service + content)

| Page | Tier | Native source | What we add | Notes |
|---|---|---|---|---|
| Homepage `/` | **2** | Web Page record with `content_type="Page Builder"` (`Website Settings.home_page = "home"`) | Build sections in Page Builder: hero, services snapshot, featured products, social proof, closing CTA. Use existing `_resources/images/`. Copy from style guide voice. | Page Builder gives us blocks for hero, columns, featured items, CTA bands. Theme CSS handles brand styling. |
| Balloon Twisting + Face Painting service page `/balloon-twisting-and-face-painting` | **1** (was tier 4 in v2 — recategorized 2026-04-26 after Web Page tabs finding) | Web Page record with all four tabs used: Page Builder, Script (`javascript`), Style (`css`), Header | Page Builder blocks for H1, photo, body copy, FAQ accordion. **Pricing calculator's HTML inputs go in a Page Builder HTML block; the live math goes in the page's `javascript` field; calculator-specific styling goes in the `css` field.** No custom Web Template, no app code. Pure DocType configuration. | See "Web Page native primitives" section below for the full tab map. |
| Contact page `/contact` | **2** | Web Page record with Page Builder + Frappe's Web Form for the form itself | Page Builder blocks for the brief about summary + service area + contact info + map; Web Form handles the form fields, submission, lead creation, acknowledgment | **Web Form is Phase 2 work** when we wire it to `Lead`. For Phase 1, the page can render with a stub form that shows "thank you" on submit but doesn't yet create a Lead. |
| FAQ `/faq` | **2** | Web Page record with Page Builder OR custom Web Template if we want JSON-LD FAQ schema | FAQ content from `_resources/policies/`. If we want rich-result FAQ schema, that's a small tier-4 (custom Web Template with schema markup). Otherwise tier 2. | Recommendation: tier 2 first, add schema markup later if SEO needs it. |
| Refund Policy `/refund-policy` | **3** | Web Page record with `content_type="Rich Text"` | Plain HTML body from `_resources/policies/legal-interview-answers.md` | Pure content. No layout work. |
| Accessibility `/accessibility` | **3** | Web Page record with `content_type="Rich Text"` | Statement text per the resolved Option B | Pure content. |
| Blog index `/blog` | **3** | Frappe's built-in Blog feature (`Blog Category` + `Blog Post` DocTypes; auto-generated index page) | Create Blog Categories; write Blog Posts with the "Kindergarten Teacher" voice. Theme CSS styles the listing. | Frappe Blog is a real, native feature — listing, post pages, categories, RSS, all built-in. |
| Individual blog post `/blog/<post-slug>` | **3** | Frappe's blog post template | Just write the Blog Post records (3 to start). | Native rendering. |

---

### Ecommerce (the load-bearing part)

| Page | Tier | Native source | What we add | Notes |
|---|---|---|---|---|
| Products listing `/all-products` | **1** | Webshop's `www/all-products/index.html` (already serving HTTP 200) | Configure `Webshop Settings`; create `Item Group` records (categories) + `Item` + `Website Item` records for each product. Theme CSS for visual polish. | The page exists, renders, has filtering. We need to seed the catalog. |
| Category browse `/shop-by-category` | **1** | Webshop's `www/shop-by-category/index.html` | `Item Group` records become categories. Optional: hero slideshow per `Webshop Settings`. | Native. |
| Friendly URL `/shop` → `/all-products` | **1 (tiny)** | `website_route_rules` in `apps/locally_twisted/locally_twisted/hooks.py` | One line in hooks.py | Trivial config, not "code" really. |
| Individual product page `/<product-slug>` | **1** | `website_generators = ["Website Item"]` in webshop's hooks auto-generates a public page per `Website Item` record. Template is `apps/webshop/webshop/templates/pages/product.html` (or similar). | Configure each `Item Template` with `Item Attribute` records. Webshop's product page renders attribute pills + variant price-update JS natively. | **THIS IS THE BIG ONE — see "Product complexity" section below.** Native works for what we need IF we configure attributes correctly. |
| Cart `/cart` | **1** | Webshop's `templates/pages/cart.html` (already serving) | Theme CSS styling. `Webshop Settings` controls cart behavior (allow guest checkout, show stock, etc.) | Native. |
| Checkout `/checkout` | **1** | Webshop's checkout page | Theme CSS. `Webshop Settings` for checkout flow (require login? guest allowed?) | Native. |
| Order confirmation | **1** | Webshop's `templates/pages/order.html` | Theme CSS. | Native. |
| Customer account / order history | **1** | Frappe's portal (`Customer` portal pages) + Webshop's order/wishlist pages | Theme CSS. | Native. Phase 5 expands this. |

---

### Payment process

| Item | Tier | Native source | What we add | Notes |
|---|---|---|---|---|
| Payment Gateway config (Stripe) | **1** | `Payment Gateway Account` DocType (provided by `payments` app, already installed) | Create a Payment Gateway Account record for Stripe with API keys. | Stripe is a first-class supported gateway. Just configuration. |
| Cart → Quotation → Sales Order → Payment Request | **1** | Webshop wires this entire flow natively via `doc_events` on Quotation, Sales Order, Payment Request | Nothing. We just trust the flow. | **Tier 1 is the magic here.** This is the chunk where overriding would have hurt the most; the native flow is well-tested and integrated with ERPNext invoicing/accounting. |
| Stripe webhook delivery | **1** | `payments` app provides webhook endpoints | Configure the webhook URL in Stripe dashboard pointing at `/api/method/payments.payments.doctype.payment_request.payment_request.notify_payment_status` (or equivalent — verify in payments docs) | Native. |
| Utah city-based tax | **2 or 4** | ERPNext's `Sales Taxes and Charges Template` + `Tax Rule` DocTypes natively support tax rules by territory/city | Create Tax Rules per Utah city using `_resources/utah-tax-rates-2026q2.md`. **If Frappe's Tax Rule supports city-based matching natively → tier 1/2 (just data).** **If it requires custom logic → tier 4 (small custom function).** Need to verify. | Tier classification pending source-check. |
| Invoice generation | **1** | ERPNext's `Sales Invoice` DocType auto-generates from Sales Order; native PDF rendering. | Configure invoice print format with LT brand. | Native. |
| Late fee + Net 30 (corporate) | **1 or 4** | ERPNext has Payment Terms + Auto Repeat. May or may not natively support 10% simple late fee + manual override workflow. | Configure if native; small custom hook if not. | Phase 4 work, deferred until Phase 1 ships. Verify capability when we get there. |

---

## Web Page native primitives — the unlock that recategorizes the calculator

GL surfaced this 2026-04-26: the previous instance edited the homepage Web Page (`/app/web-page/locally-twisted`) using only the **content field** (Rich Text → `main_section`). They missed the other tabs on the same DocType form. Reading the schema (`apps/frappe/frappe/website/doctype/web_page/web_page.json`) revealed:

| Tab | Field | What it does |
|---|---|---|
| Content | `main_section` (Rich Text) / `main_section_html` / `main_section_md` / `page_blocks` (Page Builder) | Body content. Pick `content_type` carefully — wrong content_type silently empties the page. |
| **Script** | `javascript` (Code field) | **Per-page JavaScript at page load.** Pricing calculators, form interactivity, dynamic UI live here. |
| **Style** | `css` (Code field), `insert_style` (Check) | **Per-page CSS scoped to this page only.** Toggle `insert_style` to inject. |
| Header and Breadcrumbs | `header` (HTML editor), `breadcrumbs` (Code), `dynamic_template` | Custom hero HTML + breadcrumb logic |
| Settings | `show_sidebar`, `enable_comments`, `full_width` | Layout toggles |
| Meta Tags | `meta_title`, `meta_description`, `meta_image`, `dynamic_route` | Per-page SEO |
| **Context** | `context_script` (Code, Python) | **Server-side Python that runs BEFORE render.** Inject Jinja context vars without writing a controller. |

**Implication for the LT plan:** the pricing calculator on BTFP, originally classified tier 4 ("custom Web Template required"), collapses to tier 1. Same JavaScript code, but it lives in the Web Page record's `javascript` field instead of in a Jinja template file. No app code, no template overrides, no hook registrations.

**Phase 1 may have ZERO tier-4 pieces.** The only remaining tier-4 candidate is color swatches for the Latex Color attribute, and even that may be reachable via `context_script` + a custom field on `Item Attribute Value` (will verify during Step 3).

**Standing pattern for any new page:** open the DocType `.json` schema first. Map the page's needs to the existing fields. Only escalate to a custom Web Template if the field set genuinely doesn't fit. (This rule is now codified at the top of the agency `frappe-conventions.md`.)

---

## Product complexity — special section

You linked the Classic Organic Arch product. Here's what I found:

**The data shape:**
- 1 product template (Classic Organic Arch)
- 3 attributes:
  - **Arch Size** (4 values: 20ft, 25ft, 30ft, 35ft) — affects price
  - **Latex Colors** (53 values: Reflex Champagne, Dusk Cream, … Empowermint) — does NOT affect price (cosmetic)
  - **Add-ons** (3 values: None, Foil stars, themed foils) — affects price
- 12 unique price points (4 sizes × 3 add-ons; color is free)
- Theoretical max combinations: 636. Actual price-distinct SKUs: 12.

**This is exactly what ERPNext's Item Variants are designed for.** The native model:

1. Create one `Item Template` for "Classic Organic Arch" with `has_variants = 1`.
2. Create three `Item Attribute` records (Arch Size, Latex Color, Add-ons), each with their values listed.
3. On the Item Template, link to the three attributes. Mark "price impact" for Size and Add-ons; mark Color as cosmetic.
4. Generate `Item Variants` — ERPNext can generate the full combinatorial set, OR just the 12 price-distinct ones depending on how we configure attribute price impact.
5. Create a `Website Item` record for the template (the customer-facing handle).
6. Webshop's `product.html` natively renders attribute pills, runs JS price-update math on selection change, and adds the right variant to the cart.

**My conclusion:** the rendering is **tier 1** (native webshop handles attribute pills + variant pricing). The work is **data entry** — seeding the catalog. The COMPLEXITY is in catalog data, not in code.

**What I need to verify before locking this in tier 1:**
- Does ERPNext's Item Attribute "price impact" model exactly match LT's Size + Add-on additive math? (`base_price + size_step + addon_surcharge`)
- Does webshop's product page render 3 attribute selectors cleanly (4-pill, 53-pill, 3-pill)? 53 colors is a lot of pills; might want a dropdown or color swatch grid for that one specifically. **Color swatches might be tier 4** (small custom rendering for one attribute), but pills work natively as a tier-1 fallback.
- Are there other LT products with structurally different attribute math (multiplicative? conditional exclusions? per-variant inventory?) — those might force tier 4. Need to look at the catalog scope.

**Open question for you:** Are all LT products structurally similar to the Classic Organic Arch (size + color + add-on, additive pricing)? Or do some products have radically different attribute models (custom builds, per-event quotes, etc.) that wouldn't fit a webshop product at all?

---

## What to tell Jeff (per page)

When the time comes for the demo, the Jeff-facing value sentence per area is:

- **Site visuals:** "Every page is built on Frappe's tested foundation. The styling, fonts, and content are LT — but the rendering machinery is the framework's, so it doesn't break."
- **Products + cart:** "Your full product catalog is in the system as proper records. Sizes, colors, add-ons all configurable in your admin. Customers see real-time pricing as they pick options. Cart and checkout are framework-native — no custom payment code we have to maintain."
- **Payments:** "Stripe is wired through Frappe's standard payments app. Charges hit your dashboard. Invoices generate automatically. Utah tax calculates per-city on every order."
- **Reliability story:** "We didn't fork or override anything Frappe owns. When Frappe ships an update, we get it for free. When you transfer ownership to your own Frappe Cloud account, the developers there can support it because it's standard."

---

## GL-confirmed answers (2026-04-26)

1. **Footer layout — RESOLVED.** Use whatever native Frappe footer template natively supports as close to the catalog_data design as possible; accept Frappe's default for everything else. **Specifically:** native footer supports columns (`footer_items`), address (`footer_address`), copyright (`copyright`), powered-by (`footer_powered`). Native footer does NOT have: centered brand block, hours block, social icon row. Per GL: skip those. Configure the natives, don't override the template.
2. **Pricing calculator — RESOLVED.** Confirmed: only tier-4 piece in Phase 1. Embedded in BTFP service page.
3. **Product catalog scope — RESOLVED via inventory.** Roughly **~50 products across ~20 categories**, scraped from catalog_data `What We Make` (3 paginated pages). Categories include: Backdrops, Balloon Arches, Balloon Cups, Balloon Drops, Classic Columns, Premium Garlands/Arches/Columns, Number Columns, Photo Frames, Bouquets (Unicorn, Mickey Mouse, etc.), themed event categories (Baby Shower, Graduation, Halloween, Easter, Pride). Sample products: Classic Organic Arch, Classic Organic Garland, Premium Organic Arch, Number Balloon Columns, Easter Bunny Ear Arch, Pride Progress Rainbow Arch, Mickey Mouse Bouquet, Balloon Drop. **Implication:** manual entry is impractical; an catalog_data data export is now a load-bearing deliverable.
4. **Color swatches vs pills — DEFERRED to mock comparison.** Confirmed `Item Attribute Value` DocType has no native swatch field (only `attribute_value` Data + `abbr` Data). Swatches require: custom field via Customize Form (e.g., `swatch_hex` Color field) + custom Web Template that renders swatch grid. **Pills = tier 1, swatches = tier 4.** Render both as mock pages with a 5-color test product so GL can decide before catalog seed.
5. **Product photography — RESOLVED.** Real photos exist in catalog_data. Export script will pull product assets (images), product list, attributes, variants, and customer list (customers deferred but captured opportunistically for Phase 6 cutover).
6. **Blog content — DEFERRED.** Instances will write blog posts. **Blog is OUT of Phase 1 scope per GL: "Blogs don't matter right now."** Slice 5b removed from active work; deferred until Phase 1 ships.

## Build order (LOCKED — GL directive 2026-04-26)

Per GL: *"I need the landing page, balloon twisting and face painting, ecommerce workflow, contact ... that is the order."*

| # | Step | Tier | Notes |
|---|---|---|---|
| 0 | **Reset to native baseline** (prereq) | — | Strip `!important` chains from `lt-theme.css` (lines 477-526). Retire `scripts/setup/setup_slice2_header_footer.py` from active use. Verify home + webshop pages render cleanly with native Frappe + LT theme colors only. |
| 1 | **Landing page** `/` | 2 | Web Page record with `content_type="Page Builder"`, route="home", set as `Website Settings.home_page`. Page Builder blocks. Placeholders from `_resources/images/`. |
| 2 | **Balloon Twisting + Face Painting** `/balloon-twisting-and-face-painting` | 2 + 4 | Page Builder for layout. Pricing calculator embedded — the one tier-4 piece in Phase 1. |
| 3a | Run **catalog_data data export** | tooling | Script-based: products + attributes + variants + photos + customers. Output to `_resources/catalog_data-export/`. |
| 3b | **Decide pills vs swatches** | — | After mock render comparison. |
| 3c | Seed **catalog data** (categories, products, attributes, variants, photos) into ERPNext | 1 (data only) | Bulk import via script. |
| 3d–f | Verify **`/all-products`, product detail, cart, checkout** flow | 1 | Native webshop pages. Theme CSS for visual polish only. No template overrides. |
| 4 | **Contact page** `/contact` | 2 | Page Builder + Frappe Web Form (form-to-Lead wiring is Phase 2; for now stub the submit). |

**Out of Phase 1 (per GL 2026-04-26):**
- Blog
- Refund Policy + Accessibility + FAQ standalone pages — DEFERRED. (May be added back as quick tier-3 pages once the four above ship; explicitly NOT in current scope.)
- Lead intake wiring (Phase 2)
- Stripe production wiring (Phase 4)

## What changed from v1

- All 6 open questions resolved.
- Build order now reflects GL's exact priority sequence (landing → BTFP → ecommerce → contact, blog out).
- Catalog scope confirmed as ~50 products / ~20 categories — catalog_data export is now load-bearing infrastructure (not a "nice to have").
- Footer decision locked as native-config-only (accept Frappe's defaults for what isn't natively supported).
- Color swatches confirmed tier 4 because Frappe's `Item Attribute Value` schema has no native swatch field.

---

*v2 — 2026-04-26 — GL-confirmed. Build order locked. Tasks created in current session: #7 (this update), #8 (Step 0 reset), #9 (catalog_data export), #10 (mock pills/swatches render), #11 (landing), #12 (BTFP), #13 (ecommerce), #14 (contact).*
