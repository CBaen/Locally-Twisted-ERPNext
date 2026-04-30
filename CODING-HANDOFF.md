# Locally Twisted - Coding Handoff

Last updated: 2026-04-30 by Codex after DB verification.

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

Claims from existing docs say these work:

- ERPNext v15.105.0 stack on port `8081`.
- `locally_twisted` custom app installed.
- Webshop + payments installed.
- 53 Website Items published.
- Shop mega menu and product detail inline variant selectors.
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

P0 remains `/book`:

- Primary inquiry conversion page.
- Existing CTAs point there.
- Queue says it is still missing/404.
- Existing Lead schema is supposed to be in place.
- Canonical form shape is the Hetzner `/book` snapshot in `_resources/odoo-live-snapshot/hetzner-book.html`, cross-checked against the running ERPNext Lead Custom Fields.

Then build `/privacy` and `/terms-of-service` for Stripe live-mode readiness.

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

Before declaring visible work done, capture and inspect desktop and mobile screenshots. Use the repo's existing Playwright scripts where possible.
