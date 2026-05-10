# Web Scout Findings: Open-Source E-Commerce Platform Fit for Locally Twisted
## Date: 2026-05-10
## Source Type: Live Internet Search
## Searches Performed:
1. Frappe Webshop limitations problems 2025 2026 ERPNext ecommerce alternative
2. Open source ecommerce platform 50 color variants per-variant photos product configurator 2025 2026
3. Medusa Saleor Sylius ERPNext integration headless ecommerce 2025 2026
4. Frappe Webshop product variants color swatches per-variant images github issues 2024 2025
5. Medusa v2 product variants color swatches per-variant images open source 2025
6. Saleor product variants photos per variant 50+ colors storefront headless 2025
7. Frappe Webshop variant image does not change swap when selecting variant 2024
8. Spree Solidus Ruby on Rails open source ecommerce variants photos 2025 headless
9. Bagisto Laravel ecommerce variant swatches images open source 2025 headless API
10. Shopware Community Edition open source variant swatches color images product 2025
11. ERPNext Saleor integration webhook 2024 2025 ecommerce
12. Frappe Webshop color swatch variant selector javascript product page 2024 2025
13. Medusa v2 ERPNext problems limitations 2025 integration fails (DISCONFIRMATION)
14. Frappe Webshop alternatives 2025 2026 community discussion (DISCONFIRMATION)
15. Medusa v2 Stripe payments integration 2025 open source ecommerce
16. Medusa ERPNext two system admin burden maintenance 2025
17. Frappe Builder ERPNext ecommerce product page webshop replacement 2025 2026
18. Saleor "Jinja port" problems limitations (DISCONFIRMATION)
19. Medusa v2 Node.js TypeScript self-hosted maintenance complexity small team 2025

---

## SECTION A: What Frappe Webshop Actually Cannot Do (Confirmed)

This is the most important baseline finding. The research brief describes Webshop as "a total disaster" — the internet confirms specific, unfixed architectural reasons why.

### Finding A1: Per-Variant Image Swap Is Not Implemented in Webshop
- **Evidence:** Multiple Frappe forum threads (2022-2024) report that the product image does not change when a variant is selected. Thread from Oct 2023: "item-image remain the same on any variants button clicked." This is a recurring unanswered complaint with no native fix documented anywhere.
- **Source:** https://discuss.frappe.io/t/how-to-change-item-image-along-with-their-slideshow-when-variants-button-is-clicked-in-template-page/111934 (2023-10)
- **Source:** https://github.com/frappe/erpnext/issues/8774 — "Item Variant has Image, do not Copy image from Template Item" (old, not resolved)
- **Pricing:** N/A (missing feature in free Webshop)
- **Recency:** Pre-cutoff issue, confirmed still unresolved as of 2024 forum activity
- **Verdict:** Confirmed unfixed gap. No workaround documented in Frappe's own docs.

### Finding A2: Variant Selector Is Pure JavaScript With No HTML Templates (No Color Swatches)
- **Evidence:** The Frappe Webshop variant selector uses an `ItemConfigure` class that dynamically generates dropdown select fields from attribute data — no visual swatch rendering, no color picker UI. The June 2025 Frappe Forum thread about translation confirmed: "The Variant Selector at the Webshop is pure Javascript lacking any html" — which is why translation tags don't work in it.
- **Source:** https://discuss.frappe.io/t/translation-of-webshop-variant-selector/143966 (2025)
- **Pricing:** N/A (missing feature)
- **Recency:** Confirmed 2025
- **Verdict:** No color swatch UI. No visual variant picker. Text dropdowns only.

### Finding A3: Webshop Architecture Is Flagged as Outdated — Community Rewrite Discussion Happening
- **Evidence:** A July 2025 Frappe Forum thread titled "Revisiting the Webshop App — What Would a 2025-Ready Rewrite Look Like?" catalogs the architectural problems: heavy `ignore_permissions = True` patterns, legacy RPC-over-whitelist instead of REST, Jinja templates returning HTML instead of JSON (blocking headless), and security exposure on guest whitelists. This is a community request aimed at Webshop maintainers, not an official Frappe roadmap announcement. The tone is: "the foundations are there but it needs work." Not abandoned; not actively being rewritten.
- **Source:** https://discuss.frappe.io/t/revisiting-the-webshop-app-what-would-a-2025-ready-rewrite-look-like/149991 (2025-07)
- **Pricing:** N/A
- **Recency:** Post-cutoff (July 2025)
- **Verdict:** Webshop is not being actively rewritten. It is in maintenance-only limbo with recognized architectural debt.

### Finding A4: Frappe ecommerce_integrations Does Not Include Saleor or Medusa
- **Evidence:** The official `frappe/ecommerce_integrations` repo (actively maintained, last release April 2026) supports Shopify, Unicommerce, Zenoti, and Amazon. No Saleor, Medusa, or Bagisto connector exists in the official Frappe organization. License is GPL v3.
- **Source:** https://github.com/frappe/ecommerce_integrations (2026-04-29 last release)
- **Pricing:** Free / GPL v3
- **Recency:** Post-cutoff (active 2026)
- **Verdict:** No official Frappe pathway to Saleor or Medusa integration. Any integration is custom.

---

## SECTION B: Platform-by-Platform Findings

### Option B1: Medusa v2 (Node/TypeScript, Headless)
- **Type:** Headless commerce backend + optional Next.js storefront
- **Source:** https://github.com/medusajs/medusa (MIT license confirmed)
- **Source:** https://github.com/medusajs/medusa/releases/tag/v2.11.2 (released 2025-10-31)
- **Pricing:** Free/open source (MIT). Self-hosted: you pay for PostgreSQL + Redis + S3 + Node server. Managed Medusa Cloud exists but pricing unknown from searches.
- **Recency:** Post-cutoff — v2.11.2 released October 2025, actively maintained with v2.12.x releases in early 2026.
- **Maturity:** Production-ready (v2 GA), but specific v2.12.4 introduced build regressions (disconfirmation finding).
- **License:** MIT — clean for integration AND clone-and-port purposes.

**Variant / photo / cart depth:**
- **Per-variant image swap:** YES, natively added in v2.11.2 (October 2025). Images are added at product level; variant images are selected from the product image pool and assigned via many-to-many relationship. Admin has two workflows: link one image to many variants, or many images to one variant. This is native, not a plugin.
- **Community plugin for richer variant images:** `medusa-variant-images` plugin exists on npm for even more variant-specific management. Source: https://github.com/Betanoir/medusa-variant-images
- **Color swatches:** NOT native in the Medusa backend. The Next.js starter storefront renders options as buttons; color swatch UI would need custom frontend CSS/JS. The documentation shows the basic buttons pattern, not swatches.
- **Multi-attribute SKU (color+size):** YES — fully supported. The `variant.options.every()` pattern handles any combination.
- **Per-variant pricing:** YES — each variant has independent pricing per currency and price list.
- **Stripe:** YES — first-party Stripe module provider, installed by default, well documented.

**Integration axis (Medusa + ERPNext as backend):**
- One prior-art integration exists: `aerele/medusa_integration` (27 stars, 5 forks, MIT license, no published releases — experimental). Source: https://github.com/aerele/medusa_integration
- A second integration: `bitspur/medusa-erpnext-sync` on GitLab (created July 2024, 34 commits, license unclear). Source: https://gitlab.com/bitspur/community/medusa-erpnext-sync
- A third partial implementation: `clayrisser/medusa-erpnext-sync` mentioned in Frappe forum thread (July 2024, developer called it incomplete).
- Medusa's official ERP recipe covers the integration pattern (modules + workflows + scheduled jobs) but names only Odoo as the reference example, not ERPNext specifically.
- Source: https://discuss.frappe.io/t/request-for-full-frappe-erpnext-integration-with-medusajs/116557
- **Jeff's admin burden:** Running Medusa means two systems to maintain (ERPNext + Medusa). Jeff as a non-technical operator would need all order/customer data flowing back to ERPNext automatically. None of the existing integrations are production-hardened or officially supported. This is a real risk.

**Clone axis (port Medusa's variant/cart logic to Jinja):**
- Medusa's storefront is Next.js/TypeScript/React (App Router). Not Jinja.
- The variant selection logic is TypeScript: state management, `variant.options.every()` matching. Translatable to Jinja + vanilla JS conceptually.
- The per-variant image swap uses Medusa's JS SDK + async fetch. In a Jinja context, you'd replicate the lookup via a whitelisted Frappe API endpoint returning variant image URLs as JSON, then swap with JS.
- License is MIT — clean to read and port logic from.
- **Porting difficulty:** The logic is readable and not deeply React-specific. A developer comfortable with Frappe's whitelisted Python APIs and vanilla JS could translate the variant matching and image swap patterns into a Frappe `www/product.py` controller + Jinja template + small JS module.
- **Fits our case because:** MIT license, natively solves all three hard problems (variant images, multi-attribute, per-variant pricing), actively maintained, TypeScript codebase is readable even if the target is Jinja.
- **Tradeoffs (integration route):** Two systems to run. No production-proven ERPNext connector. Jeff cannot admin Medusa — it's developer-admin only. Node.js stack is different from Frappe's Python stack.
- **Tradeoffs (clone route):** You're writing the Frappe product page controller and template from scratch, borrowing Medusa's data model logic as a reference. This is building custom Frappe pages, not running Medusa at all.

---

### Option B2: Saleor (Python/Django, Headless GraphQL)
- **Type:** Headless GraphQL commerce API (Django/Python backend) + Next.js storefront
- **Source:** https://github.com/saleor/saleor (BSD license)
- **Source:** https://docs.saleor.io/developer/products/overview
- **Pricing:** Free/open source (BSD). Self-hosted: Django + PostgreSQL stack. Cloud managed option exists.
- **Recency:** Actively maintained (2025 releases confirmed).
- **Maturity:** Production-ready, used by enterprise clients.
- **License:** BSD-3-Clause — clean for both integration and clone-and-port. No copyleft restrictions.

**Variant / photo / cart depth:**
- **Per-variant image:** YES, confirmed via `variantMediaAssign` mutation. Images uploaded at product level; specific images assigned to specific variants via the dashboard or API. Source: https://github.com/saleor/saleor/discussions/12312
- **Color swatches:** NOT native. Saleor's storefront renders variant options as interactive elements; color swatch presentation is a frontend concern not handled by the backend.
- **Multi-attribute SKU:** YES — the storefront handles combinations like Color + Size + Material. Source: https://github.com/saleor/saleor/discussions/8525
- **Per-variant pricing:** YES — prices are assigned at variant level in the dashboard.
- **Stripe:** YES — Saleor has first-party payment plugins.

**Integration axis (Saleor + ERPNext):**
- No prior-art ERPNext-Saleor integration found anywhere in searches. Zero GitHub repos, zero Frappe forum threads, zero blog posts.
- Saleor speaks GraphQL; ERPNext speaks REST and Frappe RPC. An integration would require a custom middleware.
- **Jeff's admin burden:** Saleor is Python/Django so it's more stack-compatible with ERPNext's Python ecosystem conceptually, but it's still a separate system. The Django admin is not ERPNext admin — Jeff cannot admin it.

**Clone axis (port Saleor's storefront logic to Jinja):**
- Saleor storefront is Next.js/React/TypeScript (App Router, graphql-codegen). Source: https://github.com/saleor/storefront
- License on the storefront: FSL-1.1-ALv2 (Functional Source License, converts to Apache 2.0 after 2 years). The FSL-1.1 has a restriction: you cannot use it to compete with Saleor's commercial offering. For porting code patterns (not redistributing the product), this is likely acceptable, but it is NOT MIT-clean. Caution warranted.
- The Saleor CORE (backend) is BSD-3 — clean. The STOREFRONT is FSL — less clean.
- Saleor's variant logic is GraphQL-heavy (`variantMediaAssign`, typed queries). Translating to Jinja + Python requires understanding the GraphQL schema and rewriting the data-fetch patterns as Frappe whitelisted API calls. More translation work than Medusa.
- **Fits our case because:** Python backend (conceptually closer to Frappe), native per-variant image support, BSD core license.
- **Tradeoffs (clone route):** Storefront license is FSL (not MIT), adding ambiguity. GraphQL-centric storefront logic is harder to translate to Jinja than Medusa's REST-and-SDK approach.

---

### Option B3: Spree Commerce (Ruby on Rails, Headless REST)
- **Type:** Open-source headless ecommerce with REST API + Next.js storefront
- **Source:** https://github.com/spree/spree (BSD-3-Clause)
- **Source:** https://github.com/spree/storefront (MIT license)
- **Pricing:** Free/open source. Rails deployment is operationally heavier than Node or Python.
- **Recency:** Actively maintained (Next.js 16/React 19 storefront referenced in 2025).
- **Maturity:** Production-ready. Long track record.
- **License:** Backend BSD-3-Clause; storefront MIT — clean for clone-and-port.

**Variant / photo / cart depth:**
- **Per-variant image:** YES — "images can be attached to the product (via the master variant) or to individual variants." When a variant is selected, show variant images, falling back to product-level images. Source: https://spreecommerce.org/docs/developer/core-concepts/products
- **Multi-attribute SKU:** YES — T-shirt + Size + Color = 6 variants each with own SKU.
- **Per-variant pricing:** YES — multiple prices per variant per currency, plus price lists.
- **Stripe:** YES — confirmed in storefront stack.
- **Color swatches:** Not explicitly documented, but the storefront has "variant selection" mentioned; actual swatch rendering is frontend concern.

**Integration axis (Spree + ERPNext):**
- No prior-art ERPNext-Spree integration found in any searches. Zero results.
- Spree's REST API could theoretically be connected to ERPNext via webhooks, but no community has done this.
- Adding a Rails stack alongside an ERPNext stack is maximum operational complexity for a small operator.

**Clone axis (port Spree's storefront logic to Jinja):**
- Spree's official storefront is Next.js/React/TypeScript (App Router). MIT licensed.
- The variant logic + image fallback pattern from Spree's product docs is readable and clearly described. The REST API responses are JSON; translating the image-fallback logic to Python/Jinja is straightforward.
- **Fits our case because:** MIT storefront license (cleanest), well-documented variant + image model, REST API (not GraphQL).
- **Tradeoffs:** Ruby on Rails backend adds a third language ecosystem if used as integration target. Rails deployment complexity is high for a team running Python/Frappe. But for CLONE purposes (reading the logic, not running Spree), the language is irrelevant.

---

### Option B4: Shopware 6 Community Edition (PHP/Symfony)
- **Type:** Full-stack monolith ecommerce with headless option
- **Source:** https://www.shopware.com/en/community/community-edition/ 
- **Source:** https://github.com/shopware/shopware (MIT license as of Shopware 6)
- **Pricing:** Free (MIT). BUT: as of March 2025, a Fair Usage Policy applies — merchants over €1M GMV must move to paid plan. For LT's scale, this is irrelevant (they are far below €1M GMV).
- **Recency:** Shopware 6.7.3.0 released October 2025. Post-cutoff active development.
- **Maturity:** Production-ready, major European platform.
- **License:** MIT (Shopware 6 core). Template components available under BSD.

**Variant / photo / cart depth:**
- **Per-variant images:** Native support documented. Shopware's product detail page shows images for the selected variant. Extensions exist in the plugin store for color swatch previews in listing pages.
- **Color swatches in listing:** Plugin extensions exist (commercial plugins in Shopware store for color variant preview). Core has property-based variants but swatch UI is plugin territory.
- **Multi-attribute SKU:** YES — properties create variant matrices.
- **Per-variant pricing:** YES — standard.
- **Stripe:** Yes via plugins.

**Integration axis (Shopware + ERPNext):**
- No ERPNext-Shopware integration found in searches. Zero prior art.
- PHP ecosystem is completely foreign to Frappe/Python stack.

**Clone axis (port Shopware templates to Jinja):**
- Shopware uses Twig (PHP templating, similar concept to Jinja). Twig and Jinja share heritage — both are Jinja-inspired. The template syntax is very close.
- This is the closest conceptual analog to porting templates to Jinja. A Shopware Twig product template can be read and translated to Jinja with less cognitive overhead than React/JSX.
- Shopware's variant image swap is natively implemented in Twig + JS. The pattern is readable.
- **Fits our case because:** Twig-to-Jinja port is the lowest conceptual translation cost of any platform. MIT license on core. Production-proven variant and swatch handling.
- **Tradeoffs:** PHP ecosystem. No ERPNext integration prior art. Shopware's templating is not publicly well-documented for porting purposes — this is inference from Twig/Jinja similarity, not a documented pathway.

---

### Option B5: Bagisto (Laravel/PHP + GraphQL)
- **Type:** Full-stack Laravel ecommerce with GraphQL headless option
- **Source:** https://github.com/bagisto/bagisto (MIT license)
- **Source:** https://github.com/bagisto/headless-ecommerce (GraphQL headless API)
- **Pricing:** Free/MIT. Self-hosted Laravel + MySQL stack.
- **Recency:** Actively maintained. Headless API changelog shows 2024-2025 releases.
- **Maturity:** Production-ready. Growing community.
- **License:** MIT — clean.

**Variant / photo / cart depth:**
- **Swatches:** Confirmed swatch support with a recent bugfix for "swatchValue and category filterableAttribute null issue" in the headless API. Source: https://github.com/bagisto/headless-ecommerce/blob/main/CHANGELOG.md
- **Per-variant images:** Not explicitly confirmed in searches, but swatch support implies variant-level visual differentiation.
- **Multi-attribute SKU:** Standard Laravel ecommerce — yes.
- **Stripe:** Supported.

**Integration axis (Bagisto + ERPNext):**
- No ERPNext-Bagisto integration found. Zero results.
- PHP + Python = two different language ecosystems.

**Clone axis:**
- Bagisto uses Blade templates (Laravel's templating). Less Jinja-like than Twig (Shopware). PHP-specific syntax would require more translation work.
- MIT license is clean.

---

### Option B6: Sylius (PHP/Symfony, Headless)
- **Type:** Headless ecommerce framework on Symfony
- **Source:** https://github.com/Sylius/Sylius
- **Pricing:** Free/MIT. Symfony stack.
- **Recency:** Actively maintained.
- **Maturity:** Enterprise/mid-market production-ready.
- **License:** MIT.

**Variant / photo / cart depth:**
- Multi-attribute variants via option types: standard.
- A plugin exists specifically for attributes ON variants (not just product-level attributes): `umanit/sylius-product-variant-attribute-plugin`. Source: https://github.com/umanit/sylius-product-variant-attribute-plugin
- Per-variant images: Sylius supports product images linked to specific variants in its product model.
- Swatch UI: Not native — frontend concern.

**Integration axis:**
- No ERPNext-Sylius integration found. Zero results.

**Clone axis:**
- Sylius uses Twig templates (same as Shopware) — Jinja port is conceptually feasible.
- MIT license — clean.

---

### Option B7: Frappe Ecosystem Alternatives — Frappe Builder + Custom www/ Pages
- **Type:** Building a custom Frappe product page using `apps/locally_twisted/www/product.py` + Jinja template, bypassing Webshop entirely for the storefront surface while keeping Webshop's backend model (Website Item, cart RPCs).
- **Source:** Frappe Build 2025 talk (Tridotstech): https://frappe.io/build/talk/3d9b4b38a0 — positions Frappe Builder as the path to a custom ecommerce portal on ERPNext.
- **Pricing:** Free — already in the stack.
- **Recency:** Talk from 2025; Frappe Builder had Page View Analytics added June 2025.
- **Maturity:** Frappe Builder is production-ready for CMS pages. Extending it to full ecommerce product detail pages with variant swap + cart is uncharted territory in public documentation.
- **License:** N/A (it's already your stack).

**Variant / photo / cart depth:**
- ERPNext's Item model natively supports multi-attribute variants (color + size = n variants, each with own SKU and price).
- The BACKEND supports per-variant images (each Item can have its own image).
- The STOREFRONT (Webshop's product page template) does NOT dynamically swap images when variant is selected (Finding A1 above).
- A custom www/ product page controller can query the correct variant's image via `frappe.get_doc("Item", variant_code).image` via a whitelisted API call.
- A custom Jinja product page can render variant data server-side and use a small JS module to handle swatch clicks + image swap via AJAX to a whitelisted endpoint.
- Webshop's cart RPC (`shopping_cart.add_to_cart`) can still be called from a custom product page — the cart backend is functional even if the product page is custom.

**Fits our case because:** No second system. Jeff admins only ERPNext. Already have 10,578 variants and 10,654 Item Prices in ERPNext. No integration maintenance.

**Tradeoffs:** GL must write the variant image swap, swatch UI, and multi-attribute selection logic from scratch in Frappe's Jinja + vanilla JS pattern. There is no community reference implementation for this in the Frappe ecosystem — the pattern must be built from first principles or borrowed from another platform's logic (Medusa, Spree, or Shopware) and translated.

---

### Option B8: Ecommerce Theme (Frappe Cloud Marketplace)
- **Type:** Third-party Frappe app (community developer, not Frappe official) — a theme layer on top of Webshop
- **Source:** https://cloud.frappe.io/marketplace/apps/ecommerce_theme
- **Pricing:** Paid (amount not disclosed). AGPL-3.0 license (code may be on GitHub).
- **Recency:** Listed in Frappe marketplace (2025).
- **Maturity:** Unknown — single developer, no version info visible.
- **License:** AGPL-3.0 — copyleft. If you modify and deploy, you may need to open-source your modifications. Caution for commercial use.

**Variant / photo / cart depth:**
- Mentions "variant price comparison (lowest variant detection)" — suggests it handles variant pricing display.
- Does NOT mention per-variant image swap or color swatch UI.

**Fits our case:** Marginally — might improve Webshop's look but does not address the core variant image problem.
**Tradeoffs:** AGPL license (copyleft risk), unknown maturity, paid.

---

## SECTION C: Integration Axis Summary

| Platform | ERPNext Prior Art | Quality of Prior Art | Admin Model | Maintenance Cost |
|---|---|---|---|---|
| Medusa v2 | 3 community repos (aerele, bitspur, clayrisser) | Experimental / incomplete / no releases | Two systems (developer admin for Medusa) | High — PostgreSQL + Redis + Node + ERPNext |
| Saleor | 0 | None | Two systems | High — Django + PostgreSQL + ERPNext |
| Spree | 0 | None | Two systems | Very High — Rails + PostgreSQL + ERPNext |
| Shopware CE | 0 | None | Two systems | High — PHP/Symfony + ERPNext |
| Bagisto | 0 | None | Two systems | Medium — Laravel + ERPNext |
| Sylius | 0 | None | Two systems | High — Symfony + ERPNext |
| Custom Frappe pages | N/A (already integrated) | Native | One system (ERPNext only) | None (no new system) |

**Integration axis winner by prior-art:** Medusa has the most evidence of anyone trying to connect it to ERPNext — but all three attempts are incomplete, experimental, and unsupported. The honest read is: NO open-source ecommerce platform has a proven, maintained ERPNext integration. This is not a solved problem.

---

## SECTION D: Clone Axis Summary

| Platform | Template Technology | Jinja Port Difficulty | License (Storefront) | Variant Image Clarity | Color Swatch Clarity |
|---|---|---|---|---|---|
| Medusa (Next.js starter) | TypeScript/React/Next.js | Medium — REST + SDK patterns, logic is readable | MIT | Clear (v2.11.2 docs explicit) | Not native (buttons) |
| Saleor storefront | TypeScript/React/Next.js | Hard — GraphQL-heavy | FSL-1.1 (caution) | Clear (variantMediaAssign) | Not native |
| Spree storefront | TypeScript/React/Next.js | Medium — REST + documented fallback logic | MIT | Clear (documented) | Not explicit |
| Shopware CE | Twig (PHP) | Lowest — Twig is Jinja-family | MIT | Native (documented) | Plugin-level |
| Bagisto headless | Blade (PHP) / GraphQL | Hard — PHP-specific templates | MIT | Implied via swatches | Confirmed (changelog) |
| Sylius | Twig (PHP) | Low-Medium — Twig-to-Jinja | MIT | Supported in model | Plugin-level |
| Custom Frappe pages | N/A (you write Jinja) | None (already Jinja) | N/A | You implement it | You implement it |

**Clone axis winner by template readability:** Shopware CE (Twig) and Sylius (Twig) have the lowest Jinja translation cost because Twig and Jinja share heritage. Medusa and Spree are next — MIT licensed, REST-based, readable patterns even if React.

---

## SECTION E: Post-Cutoff Discoveries

These findings are NEW since my May 2025 training cutoff:

1. **Medusa v2.11.2 (October 31, 2025) natively shipped per-variant image support.** This is a major shift — Medusa is the first platform on this list to natively ship this feature in a stable release during the 2025 post-cutoff window. Source: https://github.com/medusajs/medusa/releases/tag/v2.11.2

2. **Shopware's Fair Usage Policy (March 2025)** — Community Edition now has a €1M GMV threshold for free use. Does not affect LT at current scale. Source: https://qualimero.com/en/blog/shopware-community-guide-edition-ecosystem-2025

3. **Frappe Webshop rewrite discussion (July 2025)** — Community thread proposing a 2025-ready rewrite. Not an official roadmap item. Confirms Webshop is in architectural limbo, not being actively improved. Source: https://discuss.frappe.io/t/revisiting-the-webshop-app-what-would-a-2025-ready-rewrite-look-like/149991

4. **Saleor storefront now uses FSL-1.1-ALv2 license** — Not the BSD-3-Clause of the core. This is a restrictive license for the storefront code specifically. Note for clone considerations.

5. **Frappe's `ecommerce_integrations` repo had a release as recently as April 2026** (v1.20.3) — but it supports only Shopify, Amazon, Unicommerce, Zenoti. No new platforms added. Source: https://github.com/frappe/ecommerce_integrations

---

## SECTION F: Disconfirmation Searches

### Disconfirmation 1: Medusa v2 Problems (Integration Route)
**Searches run:** "Medusa v2 ERPNext problems limitations 2025 integration fails" and "Medusa v2 problems criticism 2025 2026 not production ready issues"

**What was found:**
- Medusa v2.12.4 introduced a production build regression (April 2026). Reverting to 2.12.3 resolved it. Source: https://github.com/medusajs/medusa/issues/14474
- Medusa v2.6.0 had a production startup failure. Source: https://github.com/medusajs/medusa/issues/11763
- v2.10.3 had a critical HTTP server handler bug (fatal crash on any HTTP request). Source: Medium article on v2.10.3
- Community discussion "Why is the development team ignoring global issues?" (GitHub Discussion #9444) — developer frustration with team responsiveness.
- Self-hosting Medusa requires PostgreSQL + Redis + S3 + two separate process instances (server + worker). The real infrastructure cost is higher than simple Node deployments.
- A developer cost estimate found: Year 1 total cost of ownership for self-hosted Medusa on a typical $500K business ranges from $66,000-$144,000 including development. This is enterprise-scale tooling being assessed at small business scale.
- **The aerele/medusa_integration connector has 27 stars, 5 forks, NO published releases.** It cannot be called production-ready.
- **Conclusion:** Medusa's integration route to ERPNext has no production-ready connector. Medusa itself has had a pattern of production regressions across minor versions. For a non-technical operator (Jeff) who cannot admin a second system, this route carries significant operational risk that would fall entirely on GL/BBC.

### Disconfirmation 2: Saleor Jinja Port Limitations
**Search run:** "Saleor Jinja port server side rendered problems limitations NOT React GraphQL overhead"

**What was found:**
- No documented examples of anyone porting Saleor's storefront logic to Jinja or any server-side rendered template system. The result set returned nothing about Saleor-to-Jinja specifically.
- Saleor's architecture is GraphQL-first. Every product query, variant selection, and media assignment goes through typed GraphQL operations. Translating this to Frappe's whitelisted Python API + Jinja requires re-implementing not just the UI logic but the data-fetch layer from scratch.
- The Saleor storefront's FSL-1.1 license adds legal ambiguity for porting code into a commercial Frappe app that will be sold/transferred.
- **Conclusion:** The Saleor clone path has higher translation friction than Medusa or Spree. The storefront license adds risk. No evidence anyone has done this successfully.

### Disconfirmation 3: Frappe Webshop Alternatives (Do They Exist Within Frappe?)
**Search run:** "Frappe Webshop alternatives 2025 2026 community discussion"

**What was found:**
- The community discussion about Webshop alternatives within Frappe does NOT produce a viable alternative from inside the Frappe ecosystem. The Frappe marketplace has one third-party Ecommerce Theme app (paid, AGPL, unknown maturity). Frappe Builder is being positioned by some community members for ecommerce portals but this is community initiative, not an official Frappe product with documented cart/checkout support.
- No open-source Frappe app with variant-image support was found.
- **Conclusion:** There is no Frappe-native alternative to Webshop that solves the variant image problem. The options are: fix it yourself inside Frappe (custom www/ pages), or go outside Frappe.

---

## SECTION G: Gaps and Unknowns

1. **What does the aerele/medusa_integration actually sync in practice?** The repo has 27 stars but no published releases. Is anyone running it in production? No blog posts, no case studies found.

2. **Does Shopware's Twig variant image swap logic match what a Frappe Jinja implementation would need?** The conceptual similarity is high (Twig ≈ Jinja), but I did not fetch specific Shopware product template code to verify the pattern. This would require fetching specific Shopware GitHub template files.

3. **Is the Medusa Next.js starter storefront's variant+image-swap code directly readable and translatable?** I confirmed it exists (v2.11.2) but didn't fetch the specific implementation code. The `medusa-variant-images` npm plugin would show the implementation pattern.

4. **What is the actual per-variant image data model in ERPNext's Item doctype?** The Item doctype supports an image field, but does it support a gallery of per-attribute-value images (e.g., "show these 3 photos when Red is selected")? This is a Ground Truth researcher question, not answerable from web searches.

5. **Are there any Frappe community members who have built custom product pages with variant image swap?** The forum threads asking about it are from 2022-2024. I found no success-story posts or tutorial blog posts describing a working implementation.

6. **What is Medusa Cloud's pricing?** The search returned infrastructure-based pricing ("no transaction fees") but not a specific monthly cost. This matters if GL considers managed hosting.

---

## SECTION H: Synthesis

**What the internet says about this question:**

The dominant approach in 2025-2026 open-source ecommerce is headless React/Next.js frontends against a commerce API backend (Medusa, Saleor, Spree). No platform in this space has a Jinja-rendered storefront — Jinja is Frappe's domain, not a recognized ecommerce pattern outside of it.

**The core problem Frappe Webshop has is confirmed:**
Per-variant image swap is not implemented. Color swatch UI is not implemented. These are unfixed gaps with threads going back to 2022. The variant selector is pure JavaScript with no template hooks. Webshop is in architectural maintenance limbo with a community rewrite discussion but no official roadmap for it.

**For the INTEGRATION AXIS (running a second system alongside ERPNext):**
Medusa has the most prior art for ERPNext integration, but "most prior art" means three experimental repos with no production releases and a community discussion. The honest verdict: no open-source platform has a production-proven ERPNext connector. Any integration route requires building and maintaining a custom connector. That connector is a permanent operational liability for a small shop with one non-technical operator.

**For the CLONE AXIS (reading another platform's variant logic and porting it to Jinja):**
- Medusa (MIT, REST + SDK, post-cutoff v2.11.2 has explicit per-variant image model) is the cleanest source to read.
- Spree (MIT storefront, REST, documented per-variant image fallback) is equally clean.
- Shopware CE (MIT, Twig templates — Jinja's cousin) has the lowest translation cost for template logic specifically.
- Saleor (FSL storefront, GraphQL-heavy) has the highest friction and license caution.

The clone path does NOT require running any of these platforms. It means: read their product page + variant picker + image swap implementation as a reference design, then write it in Frappe's Jinja + Python + vanilla JS. The implementation lives in `apps/locally_twisted/www/product.py` + `product.html` + a small JS module. Webshop's cart backend RPCs remain callable.

**What's emerging:** The "custom Frappe product page" approach — bypassing Webshop's product page while keeping its cart machinery — appears to be the gap the community is discovering but nobody has fully documented or shipped. The Frappe Builder talk gestures at it. The Tridotstech workshop covers it conceptually. But there is no production reference implementation publicly available.

**What surprised me:**
1. Medusa shipped native per-variant image support AFTER my training cutoff (October 2025, v2.11.2). This makes Medusa's implementation the most immediately useful reference for the clone approach.
2. Shopware's Twig-to-Jinja angle went unmentioned in the research brief but is potentially the closest architectural analog for reading template code.
3. No Frappe community member appears to have successfully shipped and written about a custom product page with variant image swap. The threads asking about it are all unanswered or end in "I need help."
4. The WooCommerce-ERPNext integration is mature and well-documented (GPL v3, multiple connectors), but WooCommerce is PHP/WordPress, which conflicts with the open-source-only constraint if Shopify is excluded. WooCommerce itself IS open-source (GPL), but the brief's spirit appears to exclude this path since it would require running WordPress alongside ERPNext.

---

Sources:
- [Frappe Webshop Forum — Real-World Ecommerce Gaps](https://discuss.frappe.io/t/enhance-webshop-for-real-world-ecommerce/147982)
- [Frappe Webshop 2025 Rewrite Discussion](https://discuss.frappe.io/t/revisiting-the-webshop-app-what-would-a-2025-ready-rewrite-look-like/149991)
- [Frappe Webshop GitHub Issues](https://github.com/frappe/webshop/issues)
- [Frappe ecommerce_integrations GitHub](https://github.com/frappe/ecommerce_integrations)
- [Medusa ERPNext Integration (aerele)](https://github.com/aerele/medusa_integration)
- [Medusa ERPNext Sync (bitspur/GitLab)](https://gitlab.com/bitspur/community/medusa-erpnext-sync)
- [Medusa v2.11.2 Release — Variant Images](https://github.com/medusajs/medusa/releases/tag/v2.11.2)
- [Medusa Variant Images Plugin](https://github.com/Betanoir/medusa-variant-images)
- [Medusa ERP Integration Recipe](https://docs.medusajs.com/resources/recipes/erp)
- [Medusa Frappe Forum Integration Request Thread](https://discuss.frappe.io/t/request-for-full-frappe-erpnext-integration-with-medusajs/116557)
- [Medusa Variant Selection Docs](https://docs.medusajs.com/resources/storefront-development/products/variants)
- [Medusa v2 Production Build Issues (v2.12.4)](https://github.com/medusajs/medusa/issues/14474)
- [Medusa Production Startup Issue (v2.6.0)](https://github.com/medusajs/medusa/issues/11763)
- [Medusa GitHub](https://github.com/medusajs/medusa)
- [Saleor GitHub](https://github.com/saleor/saleor)
- [Saleor Open Source License Docs](https://docs.saleor.io/overview/why-saleor/open-source)
- [Saleor Per-Variant Images Discussion](https://github.com/saleor/saleor/discussions/12312)
- [Saleor Storefront GitHub (FSL-1.1 license)](https://github.com/saleor/storefront)
- [Saleor Product Configuration](https://docs.saleor.io/developer/products/configuration)
- [Spree Commerce Product Docs](https://spreecommerce.org/docs/developer/core-concepts/products)
- [Spree Storefront GitHub (MIT)](https://github.com/spree/storefront)
- [Spree Commerce GitHub](https://github.com/spree/spree)
- [Shopware Community Edition](https://www.shopware.com/en/community/community-edition/)
- [Shopware 2025 Community Guide](https://qualimero.com/en/blog/shopware-community-guide-edition-ecosystem-2025)
- [Bagisto GitHub (MIT)](https://github.com/bagisto/bagisto)
- [Bagisto Headless Ecommerce](https://github.com/bagisto/headless-ecommerce)
- [Sylius GitHub](https://github.com/Sylius/Sylius)
- [Sylius Variant Attribute Plugin](https://github.com/umanit/sylius-product-variant-attribute-plugin)
- [Frappe Webshop Variant Selector Translation Thread](https://discuss.frappe.io/t/translation-of-webshop-variant-selector/143966)
- [Frappe Webshop Variant Image Thread](https://discuss.frappe.io/t/how-to-change-item-image-along-with-their-slideshow-when-variants-button-is-clicked-in-template-page/111934)
- [ERPNext Variant Image Bug](https://github.com/frappe/erpnext/issues/8774)
- [Frappe Build 2025 Ecommerce Talk](https://frappe.io/build/talk/3d9b4b38a0)
- [Frappe Ecommerce Theme (marketplace)](https://cloud.frappe.io/marketplace/apps/ecommerce_theme)
- [Open Source Ecommerce 2026 Comparison](https://www.wpbundle.com/guides/open-source-ecommerce)
- [18 Best Open Source Ecommerce Platforms 2026](https://wp-content.co/open-source-ecommerce-platforms/)
