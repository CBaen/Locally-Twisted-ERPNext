# Locally Twisted - Coding Handoff

Last updated: 2026-05-01 by Codex after storefront navigation/routing cleanup.

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

Verified or updated during the 2026-05-01 storefront correction pass:

- Header/menu no longer exposes `What We Make`; desktop dropdown panels are contained, and mobile cart/hamburger controls are visible at 390px and 430px with accessible target sizing.
- Primary nav order is now `Shop Balloon Decor`, `Plan by Occasion`, `Balloon Twisting & Face Painting`, `FAQ`, `Blog`, search. The top utility bar keeps the only `Contact Us` CTA; lower nav and mobile drawer do not duplicate it.
- `Plan by Occasion` is product-discovery navigation, not inquiry navigation. Every current occasion link routes to a verified product/category page, including missionary/religious paths. Do not re-point the occasion dropdown to `/contact?occasion=...`.
- Footer no longer exposes `What We Make`, `About Us`, or `Book an Event`; `All Balloon Decor` routes to `/shop-by-category`.
- Product detail/configure templates no longer include the "Start a conversation" or "Tell us what you're imagining" sales-pitch blocks.
- `/shop-items/arches` now scopes to Arches. Root cause was missing Webshop `.item-group-content` class in the custom Item Group wrapper, not catalog data.
- `/shop-items` and `/all-products` route to `/shop-by-category`; the ERPNext root Item Group page is too thin for customers.
- Project-level Codex capabilities are installed at `.codex/capabilities/` and routed from `AGENTS.md`; ephemeral Codex validation found the index and read the `screenshot` ingredient.
- `/book` is retired as a customer-facing page and aliases to `/contact`. Current CTAs should use `/contact`; old `/book` traffic is compatibility only.
- `/privacy` and `/terms-of-service` exist as static Frappe routes and return HTTP 200 locally. They are plain-language drafts for Stripe readiness; legal review and Stripe Dashboard URL wiring are still separate follow-ups.
- Product listing cards can display `lt_brand_description` through the local Webshop API wrapper in `locally_twisted.api.product_listing`.
- Website cache was cleared after Jinja/CSS changes; `hooks.py` CSS cache-bust was bumped to the current session version.

Claims from older docs still need re-verification before being repeated:

- ERPNext v15.105.0 stack on port `8081`.
- `locally_twisted` custom app installed.
- Webshop + payments installed.
- 53 Website Items published.
- `/shop-by-category` custom landing page.
- Local guest cart and Stripe test-mode checkout flow.
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

- Wire the Stripe Dashboard privacy/terms URLs to `/privacy` and `/terms-of-service` after GL/legal approval.
- Keep product navigation product-backed: use `scripts/verify/nav_ia.py` before touching header/footer IA.
- Replace remaining placeholder BTFP spec table values once Jeff confirms the real data.
- Add Item Group imagery for `/shop-by-category` cards when representative photos are selected.

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

Navigation IA regression check:

```powershell
python scripts/verify/nav_ia.py
```

Before declaring visible work done, capture and inspect desktop and mobile screenshots. Use the repo's existing Playwright scripts where possible.
