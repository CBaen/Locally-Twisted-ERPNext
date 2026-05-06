# Locally Twisted - Coding Handoff

Last updated: 2026-05-06 by Codex after the portfolio proof-gallery reel, Event Playground build, checkout commerce-rule reconciliation, header color repair, responsive/public verification, and prior responsive container audit gate.

## State Of Reality

The ERPNext build is active at `http://localhost:8081`. The project is **a migration of Locally Twisted's business intent + catalog data into a fresh ERPNext install** (frame revised 2026-04-30 — see `locally-twisted-decisions.md`). "Fresh install" — destination is greenfield ERPNext; no auto-translated Odoo modules or DB dumps. "Migration" — catalog records (10,631 Items / 10,578 variants / 10,613 Item Prices, ported 2026-04-30), form intent, policies, voice/brand all carried across from the prior Odoo attempt and the legacy `locallytwisted.com` site, and the new storefront replaces `locallytwisted.com` at cutover.

The catalog port from the old Odoo test deployment appears real, but several docs had stale counts. The Odoo shop at `http://5.78.136.133/shop` was used as the catalog source/reference for that port because GL explicitly named it as the old live account/source for catalog data. That does not make Odoo the product truth for unrelated business scope.

Verified DB counts on 2026-04-30:

| Record | Count |
|---|---:|
| Website Items | 53 |
| Items total | 10,631 |
| Variant templates | 49 |
| Single-SKU templates | 4 |
| Variants | 10,578 |
| Item Prices | 10,613 |
| Item Variant Attribute rows | 32,002 |
| Item Attributes | 26 |

Docs that still mention `10,613 Items`, `8,925 Item Prices`, or `10,560 variants` are stale.

## Actually Working, Pending Re-Verification

Verified or updated during the 2026-05-01 storefront correction and contact cleanup passes:

- `/contact` is the canonical customer inquiry form. `/book` returns a 301 to `/contact?intent=quick`; do not rebuild `/book` as a separate public page.
- `/balloon-twisting-and-face-painting` is now a contact-led editorial service page using real BTFP information. It has no embedded form and no public deposit-checkout CTA.
- `/contact` supports guided prefill for `?service=btfp`, `?service=twisting`, and `?service=face-painting`.
- The contact form service taxonomy is current: `Balloon Decor`, `Balloon Twisting`, `Face Painting`, `Delivery`, `Pickup`, `Events Inquiry`, `Something Else`. Do not reintroduce `Delivery Only`, `Pickup Only`, or `Event Package`.
- `Events Inquiry` is the high-value package planning path. It shows "Let's build a memory", package-piece checkboxes from the homepage custom categories, color prompt, and one planning text area. The server aggregates those values into `custom_package_notes`; no new ERPNext fields were added in this slice.
- `Event Environment` and "Shade is required for outdoor events" only appear for live artist services: Balloon Twisting and Face Painting.
- `Pickup` is stackable with other services and points customers to the locations section. Riverdale is labeled `Northern Utah Location (Residential Address)`.
- Backend Lead/CRM parity is synced: `LT Service Type` now has `Delivery`, `Pickup`, and `Events Inquiry`; stale `Delivery Only` / `Event Package` records are gone; Lead Custom Field labels/depends_on logic match the public form; website submissions populate the Desk Table MultiSelect `custom_event_type`.
- LT CRM pipeline parity is synced: the approved stages `New Inquiry`, `Quote Sent/Awaiting Approval`, `Approved`, `In Production`, `Event/Post Event`, and `Archive` live on `Lead.custom_pipeline_stage` and drive `LT Inquiry Board`. Native ERPNext `Lead.status` remains intact. `Archive` is off-board only, not a finance/win-rate trigger.
- LT CRM stage movement now creates/closes operational Tasks only. `stage_cascade.py` creates the next Task for non-Archive stages and closes open cascade Tasks on `Archive`; it does not create quotes, orders, invoices, payments, customers, or win/loss reporting state.
- Backend schema inventory is now repeatable with `python scripts/verify/backend_schema_inventory.py`. Latest live pass found 12 Leads, 25 Contacts, 4 Customers, 8 Sales Orders, 8 Payment Requests, 1 Sales Invoice, 0 Tasks, 94 Custom Fields, 102 Property Setters, and 5 custom/LT DocTypes. The inventory classifies 28 Custom Fields as code-owned and 66 as unclassified DB/app-owned records that still need keep/hide/export decisions.
- Existing `/checkout` is already the finance path: it creates/reuses Customer/Contact, creates Sales Order, creates Payment Request, and sends the customer to Stripe. `/payment-success` and the Stripe webhook reconcile paid orders by marking Payment Request paid, creating Sales Invoice, and sending paid-order emails. Do not add manual stage-to-finance automation until this existing path is coordinated with the custom LT pipeline.
- Checkout/Lead conversion parity is now coordinated with the custom LT pipeline. If checkout uses an email already tied to a Contact linked to a Lead, it converts native `Lead.status`, fills `Lead.customer`, moves `Lead.custom_pipeline_stage` to `Approved`, closes the old New Inquiry Task, and opens the Approved follow-up Task. Verified by `python scripts/verify/checkout_lead_conversion_contract.py`, which rolls back its generated records.
- Checkout commerce rules are now coordinated with fulfillment, tax, and inquiry lanes. Ready-to-order goods can check out; custom/quote-required products and out-of-area delivery stay in the quote/Lead path. Standard local delivery is `$15`, Park City delivery is `$50`, and past fulfillment dates are rejected server-side.
- Checkout tax now separates jurisdiction from taxable base. ZIP/city selects the Utah rate, but only goods are taxable. Services, face painting, balloon twisting, deposits for those services, and delivery charges are non-taxable. The local stack has a 0 percent `LT Non-Taxable Sales` Item Tax Template; delivery fee lines and `Services` item-group lines use that non-taxable override in Sales Orders.
- Contact/Lead intake now records service payment guidance fields: payment timing, deposit due, balance timing, and payment notes. Artist services use `$50 per artist` deposit guidance; mixed artist + decor/event inquiries preserve that deposit note and include the full-before-prep guidance for quoted work. This is guidance only, not an automatic service/deposit finance record.
- Header/menu now uses the deliberate premium two-level mega-menu: full-height Locally Twisted logo image, desktop `Event Balloons` and `Ready-to-Order` mega panels, `Portfolio`, `Process`, `FAQ`, search/cart, top proof row, mobile drawer accordions, and `Free Event Quote` pointed at `/contact`.
- Header color repair completed 2026-05-06 after GL flagged the all-black chrome as off-style. The mega-menu contract stayed intact, but `lt-mega-menu.css` now uses a style-guide split: slim deep-navy desktop proof row, warm-white desktop main nav, warm-white mobile header/drawer surfaces, berry CTA, brass borders, and ink text. `hooks.py` cache-bust is `lt-mega-menu.css?v=20260506-mega-5`, and `interactive_layout.spec.js` guards against regressing the header shell back to the black ink band.
- `/event-balloons`, `/portfolio`, and `/process` are real public routes and return 200 locally. `/event-balloons` and `/process` are lightweight authority pages added so the current primary nav has no dead links. `/portfolio` now uses a proof-first floating photo reel: natural-ratio installed-work images, quiet event/category filters, screen-reader-only card text, and a lightbox modal. The raw generated/reference folder used to translate the reel was deleted; the Frappe implementation and verifier are the kept source.
- The mega-menu source contract is active: `navbar_context.py`, `templates/includes/navbar/navbar.html`, `public/css/lt-mega-menu.css`, and `public/js/lt-megamenu.js` must stay in parity with `hooks.py`, `nav_ia.py`, and `smoke_shop.py`.
- Footer no longer exposes `What We Make`, `About Us`, or `Book an Event`; `All Ready-to-Order` routes to `/shop`.
- Product detail/configure templates no longer include the "Start a conversation" or "Tell us what you're imagining" sales-pitch blocks.
- `/shop-items/arches` now scopes to Arches. Root cause was missing Webshop `.item-group-content` class in the custom Item Group wrapper, not catalog data.
- `/shop` is the customer-facing all-decor hub. `/shop-items`, `/all-products`, and `/shop-by-category` route or redirect to `/shop`; individual category pages remain at `/shop-items/<group>`.
- Project-level Codex capabilities are installed at `.codex/capabilities/` and routed from `AGENTS.md`; ephemeral Codex validation found the index and read the `screenshot` ingredient.
- `/book` is retired as a customer-facing page and redirects to `/contact?intent=quick`. Current CTAs should use `/contact`; old `/book` traffic is compatibility only.
- `/privacy` and `/terms-of-service` exist as static Frappe routes and return HTTP 200 locally. Current copy reflects GL business-proxy answers from 2026-05-06 for delivery, returns, tax wording, cookies/tracking, children/privacy, opt-out event photo use, invoice acceptance, and temporary balloon/service limitations. A sitewide cookie/tracking accept/decline notice stores `lt_cookie_consent`; future optional analytics/ads/tracking must honor that stored choice. Legal/accounting review and Stripe Dashboard URL wiring are still separate follow-ups.
- Customer-facing policy documents now use anchored lanes on `/terms-of-service` and `/refund-policy`: event balloon decor, ready-to-order pickup/delivery, face painting/balloon twisting, and corporate invoicing. `locally_twisted.policy_documents` owns reusable policy blocks for code-owned receipt/inquiry emails. Do not add ERPNext Terms/Email Template records unless a verified customer-facing invoice path truly requires them; LT should stay as whitelabel/code-owned as possible. Run `python scripts/verify/customer_documents_contract.py` after changing customer document copy.
- Legal/accounting review packet lives at `_resources/policies/legal-accounting-review-packet-2026-05-06.md`.
- `/event-playground` is now a hidden internal-preview route for the first PlayCanvas decor planner. The PlayCanvas/Vite game source lives under `research/design-studio-v2/event-builder-spike/`; the Frappe route shell is `www/event_playground.html`/`.py`; and the route wraps the local Vite preview at `127.0.0.1:4306` in an iframe. Submit Inquiry hands the design to `/contact?intent=quote&source=event-playground` through `postMessage` + `sessionStorage` and pre-fills the existing contact form. There is no public nav entry, committed production bundle, DocType, backend save API, automatic Lead/Quote/Sales Order creation, pricing, checkout, CAD, room scanning, or full organic/twisting physics in this slice.
- Product listing cards can display `lt_brand_description` through the local Webshop API wrapper in `locally_twisted.api.product_listing`.
- Variant media first pass completed 2026-05-02. ERPNext now has 1,712 variant `Item.image` values mapped from `_resources/odoo-live/images/` where Odoo image labels clearly matched product options. Product detail pages call `locally_twisted.api.variant_media.get_variant_media` after exact option selection and swap the main image when a variant image exists. Cart/checkout use the variant image when present and fall back to the parent Website Item image otherwise. The review command `python scripts/setup/sync_variant_media.py --dry-run --include-details --report output/catalog-media-review.json` currently reports 49 products checked, 35 with candidate image labels, 45 needing review, 1,712 unchanged mapped variants, and 6,831 skipped variant image assignments.
- Category browse media is still empty in ERPNext: all 11 customer-facing child Item Groups under `Shop Items` have `image = null` as of the 2026-05-02 DB check. Do not revive `/shop-by-category`; choose representative category media for `/shop-items/<group>` or future menu treatment.
- Product detail breadcrumbs now use `All Balloon Decor > category > product`; the retired `Shop by Category` label/link is blocked by `scripts/verify/smoke_shop.py`.
- Civic Celebration is now the V1 visual direction across the public site. See `_resources/STYLE-GUIDE.md`, `workstreams/brand-audience-style-reset.md`, and `workstreams/civic-sitewide-redesign.md`. The pass covers shared header/footer/theme CSS, homepage, contact/book form, BTFP, portfolio, FAQ, policies, accessibility, thank-you/payment success, shop, category pages, product detail, cart, and checkout. The generated Wasatch/city hero asset is `apps/locally_twisted/locally_twisted/public/images/home/hero-wasatch-city-20260503.png`.
- Homepage review cards crawl left-to-right slowly as a horizontal proof line. The normal animation is `lt-reviews-scroll` at `540s`; reduced-motion mode disables animation but keeps the cards in a horizontal scroll row instead of stacking.
- `_resources/STYLE-GUIDE.md` version 4.2 is the only current visual authority. The old `_resources/design-guide/`, stale shop/spec comparison docs, and generic icon-comparison resources were deleted on 2026-05-05 because they conflicted with Civic Celebration + Slate Blue/Berry + Brand Direction and kept reintroducing light-blue/blush, old-font, and weak-icon choices.
- Rendered site repair pass completed 2026-05-05: mega-menu assets are served through hooks, desktop click pins mega menus open, mobile drawer opens accordions, product/shop pages use `lt-product-polish.css`, broad route containment uses `lt-page-containment.css`, and the homepage/portfolio/newsletter mobile clipping issues were fixed.
- Responsive container integrity is now a standing launch gate, not a one-off fix. `scripts/verify/layout_helpers.js` centralizes public routes, breakpoint-edge viewports, and overflow/text-fit checks. `npm run test:layout-fit` now covers 260 passive route/viewport checks across 20 routes and 13 viewport families; `npm run test:interactive-layout` covers stateful checks for header breakpoint behavior, desktop mega panels, mobile drawer accordions, shop/product controls, contact conditionals, portfolio modal, and reduced-motion homepage states. `npm run test:portfolio-reel` is the route-specific proof-gallery gate.
- `npm run test:public-verify` runs nav IA, the passive layout spec, the interactive layout spec, checkout experience, and shop smoke with quieter Playwright output. Latest targeted visual verification 2026-05-06 after the review-marquee repair: layout-fit 260/260 passed and interactive-layout 42/42 passed. Earlier same-day public-verify after the header color repair passed nav IA, layout-fit 260/260, interactive-layout 40/40, checkout-experience 1/1, and shop smoke.
- The active theme/app source has been cleaned away from old font and UI-pastel references. Do not reintroduce `DM Serif`, `Raleway`, `Montserrat`, `Playfair`, `lt-blush`, `lt-soft-blue`, old `soft-blue`/`light-blue`, UI `blush`, or unresolved `--lt-primary` in customer-facing source.
- A 16-asset custom brass-line icon suite now lives at `apps/locally_twisted/locally_twisted/public/icons/brand/`. Balloon-specific surfaces should use balloon-form icons first: pair, cluster, arch, organic garland, column, and bouquet.
- The contact page no longer depends on an external map iframe for the main service-area proof; it uses a controlled service-area panel.
- Per-product variant correctness passed on 2026-05-02. `scripts/verify/catalog_variant_contract.py` compared normalized Odoo `valid_variants` to live ERPNext `Item Variant Attribute` rows: 53 products checked, 10,578 expected variants, 10,578 live variants, 4 single-SKU products.
- Product option UX P0 pass completed 2026-05-02 and was reconciled with the current commerce lane on 2026-05-05. `item_configure.html` no longer runs per-attribute `frappe.get_all` lookups from Jinja; it uses `get_variant_attribute_options`, a project Jinja helper backed by Webshop's `get_attributes_and_values`. Quote-required custom installs such as Arches and Garlands intentionally show a `/contact?item=...` quote CTA instead of cart selectors. Retail variants such as `unicorn-bouquet` still render inline single-select chips/selects, consume `valid_options_for_attributes`, and write selected variant codes to `LT_CART`.
- Generated Webshop asset-map drift was corrected in the running ERPNext stack on 2026-05-02. The container already has Yarn Classic at `/home/frappe/.nvm/versions/node/v20.19.2/bin/yarn`, but non-interactive `docker exec` does not include that directory in `PATH`. Use `export PATH=/home/frappe/.nvm/versions/node/v20.19.2/bin:$PATH` before `bench build --app webshop`; no package install was needed. Important Docker nuance: the frontend/nginx container must be the final Webshop build target because `sites/assets/webshop` links to each container's own app-public files while `assets.json` is shared. Building only in the backend writes asset-map names nginx cannot serve. After rebuilding from the frontend container and clearing `assets_json` plus website cache, follow-up console checks returned 200s with 0 console errors/warnings.
- `scripts/verify/layout_fit.spec.js` is the committed passive Playwright Test gate. Latest verified command: `npm run test:layout-fit` -> 260 passed across 20 routes and 13 viewport families, including `/checkout` and `/thank-you`. `scripts/verify/interactive_layout.spec.js` is the stateful layout gate; latest verified command: `npm run test:interactive-layout` -> 42 passed. `scripts/verify/portfolio_reel.spec.js` is the route-specific proof-gallery gate; latest verified command: `npm run test:portfolio-reel` -> 3 passed.
- Catalog variant counts match the normalized Odoo source: the raw scrape has duplicate-case latex color values, but `_resources/odoo-live/value_normalize_map.json` collapses them and the normalized expected variant counts match ERPNext.
- Website cache was cleared after Jinja/CSS changes; `hooks.py` CSS cache-bust was bumped to the current session version.

Claims from older docs still need re-verification before being repeated:

- ERPNext v15.105.0 stack on port `8081`.
- `locally_twisted` custom app installed.
- Webshop + payments installed.
- 53 Website Items published.
- `/shop-by-category` compatibility redirect to `/shop`.
- Local guest cart and Stripe test-mode checkout flow.
- Payment backend launch-readiness now has a feature lane at `workstreams/payment-backend-launch-readiness.md`; use `scripts/verify/payment_launch_readiness.py` for non-secret structural checks. Local mode passes; live mode is expected to fail until production Stripe/site config exists.
- Existing pages including `/`, `/lookbook`, `/shop`, `/contact`, `/faq`, `/refund-policy`, `/accessibility`, `/cart`, `/checkout`, `/payment-success`, `/thank-you`.

Treat these as verified only after re-running smoke tests or checking the routes. Do not repeat a visual claim without screenshots.

## Known Incorrect Or Risky Docs

- `CLAUDE.md`, `HANDOFF.md`, `PROJECT-STATUS.md`, `lessons-learned.md`, `locally-twisted-decisions.md`, and `locally-twisted-queue.md` contain stale catalog counts in places.
- `.planning/phases/01-customer-site-and-storefront/PLAN.md` is stale about slice completion. Use the queue/status plus git/files/routes instead.
- `CLAUDE.md` and related files contain tool-specific mythology and emotionally loaded handoff instructions. Useful technical receipts should be preserved in neutral docs; do not propagate the tone.
- Existing docs say `24` Item Attributes from the Odoo-derived catalog, but the DB currently has `26` Item Attribute records. Investigate before changing fixture logic.

## Next Safest Slice

P0 is no longer `/book`; GL retired that surface. The primary customer inquiry path is the standard `/contact` form, and `/book` is only a route alias for legacy traffic.

Next safest slices:

- Design and wire the remaining stage cascades deliberately: decide which LT CRM stage should create/update Quote, Sales Order, Project/job, Calendar invite, customer email/text follow-up, Customer record, and finance records. The Task-only layer is done; do not infer finance triggers from `Archive`.
- Before manual stage-to-finance automation, decide exact stage thresholds for Quote, Sales Order, Project/job, Calendar invite, customer follow-up, Customer record, invoice, and Payment Request changes. Checkout/Lead conversion parity is done; do not duplicate its Customer/Sales Order/Payment Request creation from stage movement.
- Finish the checkout/policy approval loop: GL business-proxy answers are reflected in current Terms/FAQ/Refund/Privacy/tax copy, receipt/inquiry emails, and a basic cookie/tracking notice. Legal/accounting review and future analytics/ads tracking integration remain before final live-readiness claims.
- Send `_resources/policies/legal-accounting-review-packet-2026-05-06.md` to Jeff/legal/accounting before treating the public policy set as final.
- Wire the Stripe Dashboard privacy/terms URLs to `/privacy` and `/terms-of-service` after GL/legal approval.
- Finish payment live-mode configuration and run `python scripts/verify/payment_launch_readiness.py --mode live` before any real cutover claim.
- Review skipped/unmatched catalog media with GL/Jeff: the automated pass only mapped photos whose Odoo labels clearly matched product options. Refresh `output/catalog-media-review.json` with the detailed dry-run command before assigning anything. Do not assign generic gallery images by guess.
- Keep product navigation product-backed: use `scripts/verify/nav_ia.py` before touching header/footer IA.
- Continue brand review from `workstreams/brand-style-guide-consolidation.md`. The emergency menu/container/product repair is verified; remaining visual work is GL/Jeff review of photos, proof hierarchy, exact review/trust counts, and category/product imagery.
- Keep the responsive container gate green for any new public UI. Add route-specific interactive checks when a change introduces a new drawer, modal, accordion, filter, product control, or breakpoint state.
- Review the new `/portfolio` proof reel with GL/Jeff for photo order, photo quality, and whether any images should be removed before launch. Do not restore the raw generated/reference folder; use `workstreams/portfolio-proof-gallery.md`, restart/clear cache after controller edits, and run `npm run test:portfolio-reel`.
- Reconcile product/category media without reviving the retired `/shop-by-category` card index; use `/shop` and `/shop-items/<group>` as the customer-facing browse surfaces.
- Complete the blog channel and two ported posts.
- Continue Event Playground after reviewing the hidden local-preview route with GL/Jeff: decide whether it becomes public, sales-shared only, or remains internal; decide whether saved designs need a DocType, Frappe File screenshots, private share links, and Desk review; then add richer venue/prop packs and any V2 organic/twisting physics that can be modeled honestly. Do not add backend saves, automatic Lead/Quote/Sales Order creation, pricing, or checkout behavior until those workflows are deliberately approved.

## Verification Commands

Run DB counts with `bench execute` from the backend container:

```powershell
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute frappe.client.get_count --kwargs "{'doctype':'Item'}"
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute frappe.client.get_count --kwargs "{'doctype':'Website Item'}"
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute frappe.client.get_count --kwargs "{'doctype':'Item Price'}"
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute frappe.client.get_count --kwargs "{'doctype':'Item Variant Attribute'}"
```

Filtered counts:

```powershell
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute frappe.client.get_count --kwargs "{'doctype':'Item','filters':{'has_variants':1}}"
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute frappe.client.get_count --kwargs "{'doctype':'Item','filters':{'variant_of':['is','set']}}"
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute frappe.client.get_count --kwargs "{'doctype':'Item','filters':{'has_variants':0,'variant_of':['is','not set']}}"
```

After Jinja/CSS/Web Page changes:

```powershell
python scripts/dev/clear_website_cache.py
```

If Webshop assets need a real rebuild, expose the existing Yarn path and build from the frontend container last:

```powershell
docker exec locally-twisted-erpnext-v15-frontend-1 bash -lc 'export PATH=/home/frappe/.nvm/versions/node/v20.19.2/bin:$PATH; cd /home/frappe/frappe-bench && bench build --app webshop'
docker exec locally-twisted-erpnext-v15-redis-cache-1 redis-cli DEL assets_json
python scripts/dev/clear_website_cache.py
```

Navigation IA regression check:

```powershell
python scripts/verify/nav_ia.py
```

Variant media contract:

```powershell
python scripts/verify/variant_media_contract.py
```

Catalog variant contract:

```powershell
python scripts/verify/catalog_variant_contract.py
```

Variant media sync from the captured Odoo image files:

```powershell
python scripts/setup/sync_variant_media.py --dry-run
python scripts/setup/sync_variant_media.py --dry-run --include-details --report output/catalog-media-review.json
python scripts/setup/sync_variant_media.py
```

Public layout and interaction regression checks:

```powershell
npm run test:layout-fit
npm run test:interactive-layout
npm run test:portfolio-reel
npm run test:event-playground
npm run test:checkout-experience
python scripts/verify/smoke_shop.py
npm run test:public-verify
```

Event Playground source, browser, and Frappe handoff checks:

```powershell
cd research/design-studio-v2/event-builder-spike
npm run test:classic
npm run build
npm run verify:event-playground
cd ..\..\..
npm run test:event-playground
```

Contact form logic regression checks:

```powershell
python scripts/verify/contact_service_logic.py --base-url http://localhost:8081
python scripts/verify/contact_prefill.py --base-url http://localhost:8081
python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --form-path /contact --skip-newsletter
```

Backend Lead/CRM intake parity:

```powershell
python scripts/setup/sync_contact_intake_backend.py
python scripts/setup/sync_crm_pipeline.py
python scripts/setup/sync_stage_cascade.py
python scripts/verify/lead_backend_intake_parity.py
python scripts/verify/crm_pipeline_parity.py
python scripts/verify/crm_stage_cascade.py
python scripts/verify/checkout_lead_conversion_contract.py
python scripts/verify/backend_schema_inventory.py
```

Before declaring visible work done, run the passive and interactive layout gates, then capture and inspect desktop and mobile screenshots. Use the repo's existing Playwright scripts where possible; automated fit gates are necessary but do not replace screenshot review.
