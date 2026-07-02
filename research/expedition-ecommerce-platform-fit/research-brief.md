# Research Brief: E-commerce platform fit for Locally Twisted

**Date:** 2026-05-10
**Project:** Locally Twisted (BBC client) — `ERPNext v15.105.0` + `Frappe v15.106.0` stack
**Topic slug:** `ecommerce-platform-fit`

---

## Problem Statement (in GL's words)

> "Frappe's native ecommerce framework... a total disaster. catalog_data had so much more depth and variants, and logic, and connection to the checkout process. ... I'm not sure I can take the website live today because I don't have a functioning ecommerce component. ... It's just the crazy amount of options that the balloon company has, and it's the good logic that changes photos when you change variant. I'm having to fail at everything and then build the feature, but is there something better than what I am having OpenClaw build?"

The strategic question: **Is Frappe Webshop the right e-commerce surface for Locally Twisted's product depth, OR should the project pivot — either to a different open-source platform integrated into the ERPNext stack, OR by cloning specific deep-variant/photo/cart logic from another open-source platform's source into a custom Frappe-rendered storefront?**

GL clarifications during pre-flight (2026-05-10):
- **Excluded** (not open-source / not a fit): Shopify, WooCommerce, BigCommerce.
- **Acceptable shapes:**
  - **Easy integration** with the exact `ERPNext v15.105.0 + Frappe v15.106.0` stack (webhook/API).
  - **Easy to clone** — read its templates/variant logic and port specific UI components into a custom Frappe-rendered storefront. (GL's earlier framing: *"a professional, well-scaffolded e-commerce platform that we could have translated to Jinja code and put into the website."*)

## Expected Outcome (described as experience)

**Customer:** browses the balloon decor shop, picks a product (e.g. Unicorn Bouquet), sees a 50+ color swatch grid, picks a primary color (and possibly secondary/accent for combo arrangements). The product photo updates to reflect the chosen color. They pick size; the price updates. They add to cart, configure another product the same way, check out via Stripe, and get a confirmation email.

**Operator (Jeff):** manages products, colors, prices, and orders from the ERPNext admin only. No second platform admin. No copy-paste between systems.

**Phase 1 demo:** Jeff opens the new site, picks a few products with colors/sizes, confirms the workflow feels like the business he runs. He sees something noticeably better than the failed catalog_data attempt — without being told the prior attempt failed.

## Current State (verified from queue + handoff 2026-05-10)

- ERPNext v15.105.0 + Frappe v15.106.0 stack running locally at `:8081`.
- Webshop + payments installed, bind-mounted into containers.
- **Catalog imported:** 53 Website Items, 10,672 Items, 10,227 active customer-facing variants, 10,654 Item Prices.
- **Two product page templates implemented:** "Ready-to-order page" and "Custom quote page" (quote-first lane).
- **Variant media swap partially built:** 1,712 variants have `Item.image` mapped from catalog_data source; 95 source extra images still unclassified; gallery destination records missing.
- **Per-variant pricing:** 13 bouquet templates repaired (Small $35 / Medium $70 / Large $85). 36 non-bouquet variant templates still showing one flat price (known wrong for some, e.g. 25ft arches, longer Pride arches).
- **Quote-first flow built:** Lead → draft Quotation → operator review → tokenized customer approval → draft Sales Order. No invoice / payment / customer email side effects.
- **Add-on dependency contract:** `foil_number` add-on works in checkout; `Add ons`, `Plush add ons`, `Orbz toppers`, `Add Bouquet` are quote-only-until-approved.
- **Public ecommerce reopened for local testing** (`lt_ecommerce_paused=0`) on 2026-05-10. Not live cutover approval.
- **Architecture readiness audit currently passes** (`technical_architecture_ok: True`, `import_reopen_ok: True`, 14 pass rows, 0 blockers, 1 finance deferral).
- **Codex (OpenAI agent via OpenClaw) is doing the bulk of the build,** iterating quickly on incremental hardening (header banner, payment guards, quote approval, navigation chrome, ecommerce testing gates).

## What Specifically Hurts (GL's pain in their words)

- 50+ color variants per product, displayed legibly.
- "Common color combinations" as sellable variants (multi-color bouquets, decor, etc.).
- Variant photo-swap (the photo updates when the customer picks color/size).
- Per-size/variant pricing that flows correctly into cart.
- Webshop's cart UX feels like "a total disaster."
- Iteration tempo: "Fail at everything, then build the feature."
- Site cannot go live today without functioning ecommerce.

## Constraints (non-negotiable)

- Backend stays `ERPNext v15.105.0 + Frappe v15.106.0`. Lead, Customer, Sales Order, Item, Item Price, Item Variant Attribute, accounting, payroll. Not changing.
- Stripe payments via `frappe/payments` (already installed).
- **Open-source only.** Shopify / WooCommerce / BigCommerce excluded.
- **Acceptable platform shapes:** clean integration with the exact stack OR easy to clone source-level into a Jinja-rendered storefront.
- Jeff (owner) operates from ERPNext admin only — no second admin.
- Plain-language UI throughout (no B2B-CRM jargon).
- Visual contract: `_resources/STYLE-GUIDE.md` (Civic Celebration + Slate Blue/Berry).
- Loud Failure rule applies to forms, payments, automations.
- Final URL: `locallytwisted.com` at cutover.
- Phase 1 demo stealth: Jeff has not been told the catalog_data attempt failed in testing.

## Destructive Boundaries

- Do NOT modify any file in `/home/guidingl/projects/external-catalog-data/` (read-only reference per standing rule 2026-04-25).
- Do NOT modify the live `locallytwisted.com` site.
- Do NOT propose abandoning ERPNext as backend.
- Do NOT propose a re-import of the catalog into a third-party platform without explicit cost accounting (10,672 Items + 10,617 variants + 10,654 Item Prices is real work).

## Failed Approaches (and what they tell us)

- **Slice 2 build (2026-04-26):** `head_html` + `!important` overrides failed. Fix was adopting Frappe's intended primitives (Jinja partial overrides, `web_include_css`, `website_theme_scss`).
- **Bulk catalog_data→ERPNext catalog import (2026-04-30):** rejected; product-family-by-family approach landed.
- **Webshop behavior bugs (2026-05-02):** unpriced variant template codes added to cart; `item_configure.html` ran per-attribute Frappe queries from Jinja causing perf issues; partial selections not narrowed. All fixed via Frappe-side hardening, not platform pivot.
- **Variant price flatness (2026-05-08):** original scraper copied page base price into each variant row. Fixed for bouquets via catalog_data dynamic resolver; 36 non-bouquet templates still need per-family audit.

**The pattern:** every "Webshop is the wrong tool" feeling has resolved to an implementation defect, not a platform-architecture limit. The expedition needs to answer: **does the cumulative defect rate ITSELF indicate the platform is wrong, or is it indicating the build approach is wrong?**

## Options to Compare

- **A. Continue Webshop.** Build remaining variant photo-swap UX, color-combo data model + UI, finish the 36 non-bouquet variant prices, finish gallery classification.
- **B. Pivot to integrated open-source platform.** Run Medusa / Saleor / Sylius / Spree / PrestaShop / Magento OS / Reaction / Solidus / Vue Storefront / OpenCart as a separate service; ERPNext stays backend; orders flow back via webhooks.
- **C. Clone-from-source.** Read another platform's variant + photo + color-combo + cart source (catalog_data's `website_sale` is the obvious benchmark, but Saleor/Sylius/etc. are also clonable), port specific UI components and logic to a custom Jinja-rendered storefront on top of ERPNext primitives. No Webshop.
- **D. Custom on ERPNext primitives only.** Build storefront from scratch on Frappe + ERPNext, no platform reference. (Most flexibility, most work.)
- **E. Keep catalog_data's storefront only.** Decommission rest of catalog_data, run catalog_data's website module as the storefront; orders/customers/inventory sync to ERPNext via API.

## Researcher Source-Mandates

### Researcher 1 — Web Scout (live web ONLY)

Survey open-source e-commerce platforms for variant + photo + cart depth: **Medusa, Saleor, Sylius, Spree, PrestaShop, Magento Open Source, Reaction Commerce, Vue Storefront, OpenCart, Solidus**, plus any Frappe-ecosystem alternative apps to Webshop.

For each platform, evaluate on TWO axes:
- **Integration axis:** documented webhook/API integration with ERPNext or Frappe; prior art of running alongside Frappe; maintenance cost of two systems; license terms; auth/customer model alignment with ERPNext.
- **Clone axis:** template clarity (can a designer read them?); license terms (can we lift code into our app?); can we port specific variant-UI / photo-swap / cart components to Jinja; rough porting effort.

For each platform, specifically check:
- 50+ color variants (does the swatch UI scale gracefully)?
- Per-variant photo-swap (native or extension)?
- Color-combination-as-sellable-variant (multi-attribute SKU)?
- Per-size/variant pricing in cart?
- Stripe support?

Find prior-art reports of Frappe Webshop limit-hits and what those shops did. "Headless storefront rendered through Jinja" — does anyone actually do this in production? At what cost?

Date anchor: 2026-05-10. Look for content past May 2025 cutoff.

### Researcher 2 — Docs & Standards (official Frappe / ERPNext / Webshop docs ONLY)

Use `context7` MCP if available; verify against current versioned docs.

- What does Frappe Webshop v15 documentation actually say about variants, per-variant photos, color combinations, attribute conditional display, cart customization, checkout customization?
- What's the OFFICIAL override surface? `hooks.py` extension points, document override methods, template overrides, whitelisted methods, JS hooks for cart/checkout. Map it.
- Is there an OFFICIAL way to do per-variant photo-swap? Per-variant pricing with attribute combinations? Color-combination-as-sellable-unit?
- Are there OTHER Frappe ecosystem apps that compete with Webshop? Search the Frappe org / Frappe app store / community apps.
- What is `frappe.io`'s commerce surface (Webshop or custom)?
- What does the official `webshop` repo's templates and controllers actually contain — what hooks does it expose?

### Researcher 3 — Ground Truth (local codebase + git history ONLY)

**catalog_data benchmark (read-only):**
Open `/home/guidingl/projects/external-catalog-data/` and quantify what catalog_data's `website_sale` module actually provides for: per-variant photos (multi-image mechanism), conditional attribute display (the JS that reveals/hides options), color-swatch rendering, color combinations (multi-attribute variants), cart customization, checkout flow. Read the controllers and the variant + product templates. This is GL's implicit benchmark.

**Local LT install:**
Open `/home/guidingl/projects/Built_by_Cameron/_CLIENTS/locally-twisted/`:
- `apps/locally_twisted/locally_twisted/` — LT app source (templates, JS, hooks.py, the two product page templates)
- The bind-mounted Webshop install (find via docker volumes / image)
- `workstreams/erpnext-ecommerce-receiving-architecture.md` — existing architecture intent
- `workstreams/catalog_data-erpnext-ecommerce-parity-research-brief.md` — prior research framing
- `workstreams/product-page-backend-reconciliation-research-brief-2026-05-10.md` — latest research brief
- `workstreams/ecommerce-audit/README.md` — evidence inventory
- `capabilities/recipes/erpnext-ecommerce-receiving-architecture.md`
- `capabilities/recipes/erpnext-checkout-commerce-rules.md`
- `capabilities/recipes/frappe-product-page-company-first.md`

**Document:**
- What's WORKING right now: two product page templates, cart, checkout, paid-order cascade, partial variant media swap, partial variant pricing, quote-first flow.
- What's BROKEN or MISSING vs. GL's pain: photo-swap UX depth, 50+ color UI, color combinations, 36 templates' price flatness, cart/checkout polish.
- What Codex has been building/failing on: read recent git log + workstream files. Identify the actual cause of "disaster" — Webshop's design ceiling, implementation defect, data shape mismatch, or some combination?
- Catalog state: confirm 53 / 10,672 / 10,617 / 10,654 numbers, or correct.

## Convergence Expectation

Single recommendation OR clear "depends on X" with deciding criterion named. Effort comparison weighted against what's already built. Devil's-advocate strongest objection. GL-proxy read on which path actually fits how GL operates. The single blocking question (if any) for GL.

## Output Format (Synthesis)

Markdown with sections:
1. Recommendation (one sentence)
2. Reasoning (concise)
3. Decision Criterion (if depends on X)
4. Effort Comparison (table: Option × already-built × remaining work × risk)
5. Risks per option
6. Devil's Advocate take
7. GL-Proxy take
8. Blocking Question for GL
9. Path Forward (concrete next move — what gets coded/decided first)

## Tone

GL is a designer/creator, not a coder. Outcomes-only language. Don't ask GL to choose between technical implementations — frame any choice in terms of business / risk / scope. Use plain-language analogies, not engineering jargon.
