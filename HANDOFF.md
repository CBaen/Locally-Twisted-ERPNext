# HANDOFF — Locally Twisted

**Last updated:** 2026-04-30 morning (Opus 4.7 — closing the full-catalog-port-from-live-Odoo session)

Overwrite-not-append. Git is the changelog. Read this first; the SIBLING-LETTER.md next; everything else as needed.

---

## State of the world

**The full Odoo catalog has been ported to ERPNext webshop.** 53 products, 24 distinct attribute types, 195 unique attribute values, **10,613 Items + 8,925 Item Prices + 53 Website Items + 32,002 Item Variant Attribute child rows**. Every Odoo-valid attribute combination became an ERPNext Item Variant. No products skipped. Every Odoo data-attribute-exclusions rule respected.

**The shop is on-brand.** Mega menu opens on Shop hover/click with all 11 categories. Product detail pages render variant selectors INLINE (chips for low-cardinality, dropdown for 9+). "Item Code" jargon is gone. "/Nos" UoM display is gone. /shop-by-category landing page has the design guide register (eyebrow + DM Serif headline + lede + blush band + 11 category cards + bottom CTA). All 7 shop smoke checks pass.

**The site is at 100% completeness for Phase 1 storefront.** Every catalog product Jeff offers is browsable, configurable, and addable to cart at a per-variant price.

## Three things that matter most on day one

**1. App load order is fragile.** `installed_apps` global JSON must keep `locally_twisted` LAST. If you install ANY new app, it gets appended AFTER locally_twisted by default — and Frappe's reversed-app-order ChoiceLoader will pick the new app's templates over LT's overrides. After any new app install, re-set:

```python
# bench --site frontend console
import json
new = ["frappe", "erpnext", "payments", "webshop", "<new-app>", "locally_twisted"]
frappe.db.set_global("installed_apps", json.dumps(new))
frappe.db.commit()
```

Then docker restart backend.

**2. Item Group children + Item Attribute Values are fixtures TODAY but Jeff-owned at Phase 6.** Per `frappe-fixture-discipline`, when Jeff takes ownership the operator-state-sensitive fixtures (especially `latex colors` — 51 values, the category Jeff is most likely to edit) MUST be removed from `hooks.py fixtures = [...]` BEFORE his first post-cutover deploy. Otherwise BBC fixture sync silently overwrites his color renames/additions on every migrate. Logged as a Phase 6 work item in `locally-twisted-decisions.md` 2026-04-30 entry "Phase 6 cutover work item."

**3. Webshop's product card JS bundle bakes "Item Code" jargon at compile time.** `apps/webshop/webshop/public/js/product_ui/list.js:101` renders `${item_group} | Item Code : ${item_code}` on every listing card. We hide it via CSS (`display: none !important` on `.product-code`) — the only such chain we kept. If you upgrade webshop and the card markup changes, the CSS hide may need to track the new selector. Smoke test will catch it (it greps for the jargon string in rendered HTML).

## What's live at http://localhost:8081

| Surface | State |
|---|---|
| ERPNext v15.105.0 stack (9 containers) | Running |
| Apps installed | frappe, erpnext, locally_twisted, payments, webshop |
| `installed_apps` order | `[frappe, erpnext, payments, webshop, locally_twisted]` (locally_twisted LAST so its templates win) |
| Item Groups | Shop Items (parent) + 11 children (Arches, Columns, Bouquets, Get-Well Bouquets, Garlands, Drops, Grab & Go, Table Decor, Stands & Easels, Deliveries, Seasonal & Specialty), all `show_in_website=1` |
| Item Attributes | 24 with 195 total values (deduped case-insensitively from Odoo's 197) |
| Items | 10,613 (53 templates + 10,560 variants) |
| Item Prices on Standard Selling | 8,925 (variants where Odoo had per-variant pricing in `hasVariant`, plus single-SKU templates) |
| Website Items | 53 published, all routed `shop-items/<group>/<slug>` |
| Webshop Settings | `enable_variants=1`, `enable_attribute_filters=1`, `show_attribute_dropdowns=1` |
| Mega menu | Desktop hover/click dropdown + mobile drawer accordion, sourced live from Item Group children via `update_website_context` hook |
| Product detail templates | Overridden at `apps/locally_twisted/.../templates/generators/item/{item_details,item_add_to_cart,item_configure}.html` — strips jargon, renders inline variant selectors |
| `/shop-by-category` | Custom LT-themed override at `apps/locally_twisted/.../www/shop-by-category/` — 11 category cards |
| `/shop` | Custom LT page; filter pills sourced from Item Group children (12 pills: All + 11 categories); 53 ITEMS count |
| `/shop-items/<group>` | Webshop stock chrome but with `.product-code` CSS-hidden (no jargon visible) |
| Smoke test (`scripts/verify/smoke_shop.py`) | All 7 checks pass: mega menu, /shop pills, /shop-by-category cards, all 11 category routes 200, variant detail inline, single SKU clean, mobile accordion |

## What's NOT done (next session candidates, by priority)

**P0 — anything GL flags after looking in their real browser.** I verified everything via Playwright viewport-only screenshots. Real-browser confirmation by GL is the verdict. Specifically:
- The mega menu styling (3-column dropdown, 720px max-width)
- Mobile drawer accordion expand-in-place
- Product detail page (chips for Garland Length / dropdown for latex colors)
- The `/shop-by-category` headline + 11 category cards + bottom CTA
- Item Code jargon absent from listing cards (`/shop-items/arches`)

**P0 — Slice 10 `/book` form page.** Still 404. Every homepage CTA points at it. Was deferred 3x. Carries Phase 1 demo weight. The Lead schema (45 Custom Fields, plain-language relabels) is already in place — needs the form template + AJAX submit + acknowledgment email.

**P0 — `/privacy` and `/terms-of-service`** — both required by Stripe for live mode activation, both currently `example.com/...` placeholders in Stripe Dashboard.

**P1 — visual polish on the new pages:**
- `/shop-by-category` cards have placeholder letters (A/B/C/...) where Item Group images should be. Set `Item Group.image` per category for nicer landing.
- Category landing pages (`/shop-items/<group>`) still have webshop's stock chrome (search bar, filters sidebar, grid/list toggle). Could be overridden for full LT register. Today's CSS-hide of `.product-code` makes them livable, but they're not on-brand.
- Product detail breadcrumb still says "Shop by Category > Shop Items > Arches > Basketball Arch" — could be cleaner ("Home > Shop > Arches > Basketball Arch").
- Some mobile dropdown placeholder text is grammatically awkward ("Choose a latex colors..." should be "Choose a latex color..."). Pluralization issue.

**P1 — Item Group imagery.** Each Item Group has an `image` field that's empty. Adding category images would make `/shop-by-category` and the mega menu (if extended) feel more designed.

**P2 — production hardening:**
- Variant cache rebuild ran for all 47 variant-templates after seed. Verify the cache hits don't slow under load.
- Pre-existing Frappe asset-map error on `file_uploader.bundle.js` still in console on product detail pages — not from today's work.
- 800+ variants for some products (premium-organic-arch, classic-arch, classic-column with ~600+) might paint slowly on the variant selector dropdown. Test with throttled CPU.

## Operational rituals

| Trigger | Command |
|---|---|
| Stack stopped | `docker start $(docker ps -a --filter "name=locally-twisted-erpnext-v15" -q)` then sleep 8 |
| Stack running, need to stop | `docker stop $(docker ps --filter "name=locally-twisted-erpnext-v15" -q)` |
| Edited Jinja template / CSS / Web Page record | `python scripts/dev/clear_website_cache.py` |
| Edited PAGE_CSS in `www/<route>.py` controller / hooks.py / new module / fixture | `docker restart locally-twisted-erpnext-v15-backend-1 && sleep 10 && python scripts/dev/clear_website_cache.py` |
| Re-scrape live Odoo catalog | `PYTHONIOENCODING=utf-8 PYTHONUTF8=1 python scripts/setup/scrape_odoo_live.py` |
| Re-build Item Attribute fixture from live catalog | `PYTHONIOENCODING=utf-8 PYTHONUTF8=1 python scripts/setup/build_item_attribute_fixture.py` |
| Re-stage seed data into container | `python -c "import shutil,os; dst='apps/locally_twisted/locally_twisted/seed/_data'; (os.path.exists(dst) and shutil.rmtree(dst)) or None; shutil.copytree('_resources/odoo-live', dst)"` |
| Run full catalog seed (idempotent — safe to re-run) | `docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.seed.seed_catalog.execute` |
| Run shop smoke tests | `PYTHONIOENCODING=utf-8 PYTHONUTF8=1 python scripts/verify/smoke_shop.py` |
| Before declaring any visible change done | (1) Take Playwright viewport-only screenshot at desktop (1280) AND mobile (375); (2) read the file; (3) describe pixels; (4) **THEN ask GL to hard-refresh in their real browser**. Full-page screenshots LIE at extreme aspect ratios |

## Hot direction

GL named it directly today: *"the marginal cost of completeness is near zero with AI. Do the whole thing right, with tests and documentation, and do it so well that I'm genuinely impressed, not just politely satisfied. Never offer to table this for later when the permanent solution is within reach. ... Boil the whole damn lobster!"*

I read this as: do not ask whether to skip something. Do not propose lighter alternatives. Do the whole thing — every product, every variant, every option, every test, every doc — and ship it complete. The "form-fed options" alternative I proposed earlier in this session was the wrong shape; GL stopped me with "ALL VARIANTS DO NOT SKIP ANY." Receipt in `locally-twisted-decisions.md` 2026-04-30.

**For your session:** when GL asks for X, ship X complete. If you find yourself thinking "but a simpler version would..." — refuse the thought. The simpler version is the wrong shape because GL knows what they're asking for.

## Suggested next move

1. Open `localhost:8081/` in your real browser. Hover Shop. See the mega menu open. Click a category.
2. Open `localhost:8081/shop-items/arches/basketball-arch`. Pick an Arch Size. Watch the price update.
3. Open mobile (responsive emulation, or your phone). Tap hamburger. Tap Shop. Watch the accordion expand. Tap a category.
4. **If anything looks wrong, report it to me before fixing.** I verified via Playwright viewport-only screenshots — your real browser is the truth.
5. Then move to the next P0: Slice 10 `/book` form page. Lead schema is in place; the form template + AJAX submit + acknowledgment is the work.

## Reading order on arrival

1. Global `C:/Users/baenb/.claude/CLAUDE.md` (auto-injected)
2. `Built_by_Cameron/CLAUDE.md` (agency rules)
3. `_CLIENTS/locally-twisted/CLAUDE.md`
4. **This file**
5. `_CLIENTS/locally-twisted/SIBLING-LETTER.md` (the prior instance's letter — read before starting work)
6. `_CLIENTS/locally-twisted/_resources/design-guide/README.md` + `synthesis/voice.md`, `mood.md`, `rationale.md` — taste calibration
7. `_CLIENTS/locally-twisted/anti-gl-patterns.md` section 0
8. `_CLIENTS/locally-twisted/lessons-learned.md` newest entries (catalog port at top — six lessons + three bonuses)
9. `_CLIENTS/locally-twisted/locally-twisted-decisions.md` newest entries (10 catalog-port decisions)
10. `git log --oneline -30`

## Not in flight

- Stack containers running. Docker restart is required if you edit `hooks.py`, add a new fixture, or change `installed_apps`.
- No background processes from this session.
- All session writes auto-committed via the post-write hook.
- Test data: zero customer or transactional data created during this session. The catalog port created Item / Item Variant / Item Price / Website Item / File records — all schema/inventory data, not transactional.
- Bind-mounted seed data at `apps/locally_twisted/locally_twisted/seed/_data/` — 4 files + 148 images, ~30 MB. Can be deleted after final seed (it's a one-time staging copy of `_resources/odoo-live/`).
- Sample HTML at `_resources/_tmp_odoo_sample.html` (110KB, used during scraper development) — can delete.
- Recon screenshots at `scripts/verify/_screenshots/20260430-*` — useful as before/after evidence; ~15 MB total.

## A quick honesty pass

**What worked:**
- The plan-deepen skill caught the app-load-order issue BEFORE I tried to override templates and watched them silently fail. Agent 3's flag was correct.
- The Item Variant 600-combination limit warning from Agent 2 saved a hour of debugging — I went straight to per-combination `create_variant` calls instead of `enqueue_multiple_variant_creation`.
- The frappe-migration-guard + frappe-fixture-discipline skills made the fixture work disciplined: every fixture has a current `modified` timestamp, no Custom Field + Property Setter pairs, operator-state-sensitive subset documented for Phase 6 removal.
- The smoke test script catches every regression I worried about. Pass = green light.

**What stumbled:**
- I proposed "form-fed options" as a lighter alternative to full Item Variants. GL named it as me trying to "divert" from the task. The trained "simplify" instinct fires before the "do what GL asked" rule. Catching it required GL to push back hard — that costs trust. **For next instance:** when GL says "rebuild," refuse the urge to engineer simpler. The simpler version is wrong shape because GL knows what they're asking for.
- I restarted the backend container while the seed was running — killed the seed at ~83% complete (47/53 Website Items). Re-running picked up where it left off (idempotent worked). But the lesson: don't restart the backend while a long-running bench execute is in flight. Plan all backend-restart-requiring changes for AFTER long jobs.
- I tried to use `frappe.call(...)` in a Jinja template. That's a JS-side function. Server-side Jinja uses `frappe.get_all` / `frappe.db.get_value` directly. 500 error caught it; cost one cache-clear cycle.

**Open trust state:**
- All technical work is verified via Playwright viewport-only screenshots. GL has not opened anything in their real browser yet.
- The smoke test catches what I tested for, not what I might have missed. Real-browser verification is still pending.

— Closeout written 2026-04-30 morning by the Opus 4.7 instance who scraped Odoo's live catalog at 5.78.136.133 and ported all 53 products + 10,560 variants + 8,925 prices into ERPNext webshop with on-brand product detail pages, working mega menu, and 7-check passing smoke test. GL was specific and direct throughout: "boil the whole damn lobster."
