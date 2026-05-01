# Locally Twisted — Decisions Log

**Append-only.** Newest entries at the top. Each entry: date, decision, reasoning, alternatives considered, and who decided.

Reasoning matters more than the decision itself. A future instance reading this should be able to tell whether the decision still applies given new context, or whether the conditions that justified it have changed.

LT-specific decisions only. Cross-client / agency-wide decisions live at `Built_by_Cameron/built-by-cameron-decisions.md`.

---

## 2026-05-01 — Customer chrome IA cleanup: no `What We Make`, no About, no Book an Event links

**Decision:** The current header/footer navigation does not include `What We Make`, `About Us`, or `Book an Event`. The footer Shop column keeps `All Products`; Company links stay limited to real, currently supported surfaces.

**Reasoning:** GL explicitly corrected the footer and menu: `What We Make` is no longer a menu item, there is no About Us page, and there is no Book an Event page. Leaving links to nonexistent pages creates broken navigation and makes the footer look like copied site furniture rather than the current ERPNext storefront.

**Alternatives considered:** Keep the Hetzner mirror's historical menu labels as placeholders for future Phase 2 pages. Rejected because current navigation must only expose real or intentionally active routes.

**Decided by:** GL directive during the 2026-04-30/2026-05-01 storefront correction session.

---

## 2026-05-01 — Product listing cards use `lt_brand_description` surfaced through a local Webshop API override

**Decision:** Product listing cards should show the product's brand description, not only the product title and not generic sales-pitch copy. The implementation wraps Webshop's `webshop.webshop.api.get_product_filter_data` via Frappe `override_whitelisted_methods`, delegates to the stock API, then appends `lt_brand_description` for returned Website Items. Listing JavaScript prefers `lt_brand_description`, with fallback to existing Webshop description fields.

**Reasoning:** GL asked for the brand description on the listing card, not just the detail page. The least invasive path is a local app override that preserves Webshop's filtering/sorting behavior while adding one LT-specific field to the response. Editing Webshop core or replacing the listing endpoint would increase maintenance risk.

**Alternatives considered:** Patch Webshop source directly; rejected because Webshop is an upstream app and this project has a standing "work within Frappe/ERPNext" rule. Rebuild the whole listing pipeline; rejected because the needed behavior is a small data enrichment.

**Decided by:** Codex implementation under GL directive.

---

## 2026-05-01 — `/shop-items/<group>` filtering depends on Webshop's `.item-group-content` wrapper contract

**Decision:** Custom Item Group wrapper markup must keep Webshop's `item-group-content` class when rendering `/shop-items/<group>` pages.

**Reasoning:** The Arches category bug was not a product-data issue. Webshop's `all-products/index.js` reads the active Item Group from `.item-group-content`; the LT override had moved the group value to a custom `.lt-shop` wrapper without the class Webshop's JavaScript expects. The result: `/shop-items/arches` fell back to unscoped product results and returned non-arches. Restoring the expected class fixes category filtering without touching catalog data.

**Alternatives considered:** Add a second custom category-detection path in JavaScript. Rejected because preserving the framework contract is simpler and less fragile.

**Decided by:** Codex implementation after debugging the actual Webshop listing behavior.

---

## 2026-05-01 — Accessibility sizing is a hard constraint, not a layout variable

**Decision:** Layout fixes must preserve legal-accessibility-sized text, controls, and hit targets. Do not "fix" footer/header/listing density by shrinking text or interactive controls below accessible sizes. For touch/click targets, use at least 44px practical target height where controls are interactive.

**Reasoning:** GL explicitly corrected the bad instinct to make the footer smaller by shrinking everything. The correct fix is layout, spacing, alignment, and content removal, not illegible text or undersized controls.

**Alternatives considered:** Reduce font sizes and control heights to visually balance header/footer. Rejected as inaccessible and against GL's directive.

**Decided by:** GL directive, promoted into local/global memory for future sessions.

---

## 2026-04-30 (late evening) — Container reversion: bind-mount + post-recreate-reinstall pattern replaced by self-contained custom Docker image

**Decision:** Replace the bind-mount-and-pip-install-after-every-recreate pattern with a custom Docker image (`locally-twisted-erpnext:v15`, built from `docker/Dockerfile`) that bakes everything into the image: frappe + erpnext (from base `frappe/erpnext:v15.105.0`), payments + webshop (cloned from upstream), locally_twisted (COPYed from local source), Node 18 + yarn, compiled bench assets, and the nginx Origin pass-through patch. The compose file (`Locally-Twisted-Backend/frappe_docker/pwd.yml`) now references the new image and has all bind-mounts for the three apps removed. `scripts/setup/install_webshop.py` and `scripts/fix/patch_nginx_socketio_origin.py` are marked deprecated; both kept on disk for historical reference, neither runs against the current stack.

**Reasoning:** GL directive: *"There's constantly breaking of containers because ERPNext naturally contains everything. We need to revert to that. An instance said that they made a 'structural change' so that container issue wouldn't happen and all it did was break everything. We need to fix that first and revert back to frappe's native containers."* The structural change was the bind-mount pattern: apps lived on the host, were mounted into the container, and an editable pip install + Node + yarn install + nginx patch had to be replayed in the container's writable layer after every `docker compose up --force-recreate` (because the writable layer is destroyed on recreate). The previous instance who shipped webshop documented this in the install script's own docstring: *"Long-term fix: bake Node + yarn into a custom Docker image."* That long-term fix is now done. Verified: a `--force-recreate` round-trip produces a fully-working stack with all 5 apps registered, all key URLs returning HTTP 200, and the nginx Origin pass-through line correctly rendered into `/etc/nginx/conf.d/frappe.conf` — with NO post-recreate scripts.

**Trade-off accepted:** Editing `apps/locally_twisted/` source files no longer takes effect at runtime; image rebuild + recreate is required for changes to be served. The image rebuild is fast (heavy layers cache; only the diff is rebuilt), and the trade is worth it for eliminating the recurring breakage that prompted the reversion.

**Alternatives considered:** (a) Keep bind-mount but auto-run `install_webshop.py` from the configurator service's command — would still leave Node + yarn in the writable layer (broken on recreate) and still leave editable pip installs vulnerable; not actually native. (b) Push locally_twisted to a private GitHub repo and use upstream `images/custom/Containerfile` with apps.json — required GL to set up GitHub plumbing, rejected per the global "don't make GL the engineer" rule.

**Reversibility:** The previous pwd.yml is at `Locally-Twisted-Backend/frappe_docker/pwd.yml.bak-pre-image-bake`. To roll back: copy that over `pwd.yml`, recreate the stack, run `install_webshop.py` to reinstate editable installs, run `patch_nginx_socketio_origin.py` to reinstate the runtime nginx patch. Data volumes (sites, db-data, redis-queue-data, logs) are unchanged by the swap.

**Decided by:** Claude Opus 4.7 under GL autonomous-engineering authorization (2026-04-30: *"this session it is acceptable to break the cache rule"* + the new global hard rule *"Don't Make GL the Engineer."*).

---

## 2026-04-30 (evening) — Mega menu IA: flat 11-Item-Group structure preserved + template-level grouping into 3 panels

**Decision:** The Hetzner mirror has 3 mega menu panels (Special Occasions / Holidays & Seasons / What We Make) with 2-level hierarchy. Our ERPNext catalog has 11 flat children under "Shop Items" (Arches, Columns, Bouquets, etc. — verified by the catalog port: 53 Website Items, 10,578 variants, 10,613 Item Prices). Rather than restructuring the Item Group tree to add Special Occasions + Holidays & Seasons parents (and reassigning all 53 Website Items), we keep the flat 11 and group them into the 3 Hetzner panels at the **template layer** via three new context keys exposed by `navbar_context.py`: `mega_special_occasions`, `mega_holidays_seasons`, `mega_what_we_make`. Each is a list of `{label, route}` dicts. Some leafs (Birthdays, Showers, Graduations, Missionary, Get-Well) point at content-only routes that may not have published pages yet — those will resolve via Phase 2 page builds OR remain as 404 placeholders until populated.

**Reasoning:** Lower blast radius. Restructuring the catalog tree would risk the just-verified data integrity (53/10,578/10,613). Template-level grouping is reversible — if GL prefers the 2-level Item Group tree structure later, we restructure `fixtures/item_group.json` and re-tag the 53 Website Items, and the navbar template adjusts. The "flat + template-group" choice preserves all existing investment in catalog data while delivering Hetzner's 3-panel UX.

**Alternatives considered:** Restructure the Item Group tree with Special Occasions + Holidays & Seasons as new parents under "Shop Items," reassign the 11 children appropriately. Rejected because it touches the data layer that was just verified at high cost.

**Decided by:** Claude Opus 4.7 (orchestrator), under GL's autonomous-decision authorization for the chrome rebuild session. **Reversible** — see `MIRROR-REBUILD-PLAN.md` Decision A.

---

## 2026-04-30 (evening) — Category URL shape: ERPNext-native `/shop-items/<slug>` retained, NOT Hetzner's `/shop/category/<slug>-<id>`

**Decision:** ERPNext webshop's `WebshopItemGroup.make_route()` auto-generates `/shop-items/<slug>` from the Item Group's `route` field (no Odoo-style numeric IDs). The Hetzner mirror uses `/shop/category/<slug>-<id>` URLs. Rather than mimic Hetzner's URLs exactly, we use ERPNext-native `/shop-items/<slug>` everywhere. Mega menu links + footer Shop column links + breadcrumbs all use the ERPNext shape.

To handle inbound references to Hetzner-shaped URLs (none exist externally today, but mirror markup contains them and Phase 2 page rebuilds may reference them):  add `website_route_rules` redirects from `/shop/category/<slug>` → `/shop-items/<slug>` for the 11 known categories when a real referrer surfaces.

**Reasoning:** Doesn't fight ERPNext's `make_route()` convention. No need to manually set `route` on each Item Group (which would be operator-state-sensitive — Jeff might rename a category later and the URL would break). Lower blast than redirect rules per category. Pre-launch — no external bookmarks to preserve. Hetzner-shape URL preservation can be added later via redirects if real inbound traffic appears.

**Alternatives considered:**
- Manually set `route="shop/category/arches"` etc. on each of the 11 Item Groups via fixture override. Rejected — operator-state-sensitive (per `frappe-fixture-discipline`).
- Add 11 `website_route_rules` redirect entries today. Rejected — no inbound traffic yet; would be premature complexity.

**Decided by:** Claude Opus 4.7 (orchestrator), under GL's autonomous-decision authorization. **Reversible** — see `MIRROR-REBUILD-PLAN.md` Decision B.

---

## 2026-04-30 (evening) — Blog: use Frappe's NATIVE `Blog Post` DocType, NOT a custom `LT Blog Post`

**Decision:** Frappe core ships a fully-functional blog system: `Blog Post` + `Blog Category` + `Blogger` + `Blog Settings` DocTypes, plus `blog_post.html` and `blog_post_list.html` templates. Use the native DocType. Add a `tags` field via `Customize Form` (Table MultiSelect linking to a tiny `LT Blog Tag` DocType — 1 field) for the tag-filtering feature Hetzner has but Frappe's blog lacks. Add a thin template override at `apps/locally_twisted/locally_twisted/templates/pages/blog_post.html` for the SEO meta tags Frappe's native template doesn't emit (canonical link, article:published_time/modified_time/tag OG metas, Twitter `summary_large_image`, BreadcrumbList JSON-LD).

**Reasoning:** Frappe's native `Blog Post` provides for free: schema.org BlogPosting itemscope, OG meta tags with auto-fallback, `read_time` auto-calc, RSS/Atom feeds per category, "Load More" pagination, browse_by_category dropdown, full-text search, breadcrumbs, social sharing toggles, likes, comments, blog_intro 200-char excerpt, `Blogger` author block. Building a custom `LT Blog Post` would duplicate all of that and lose the framework integration. The original `MIRROR-REBUILD-PLAN.md` called for a custom DocType; `/plan-deepen` caught this regression vs the website-page-index.md (which had already classified blog as Tier 3 native).

**Alternatives considered:** Custom `LT Blog Post` DocType. Rejected — reinvents the wheel.

**Decided by:** Claude Opus 4.7 (orchestrator) following /plan-deepen finding. Plan section "Phase 2 — orders #9/#10" rewritten accordingly.

---

## 2026-04-30 — Project frame: this IS a migration, not a new build

**Decision:** Frame Locally Twisted's ERPNext project as **a migration of business intent + catalog data into a fresh ERPNext install** — superseding the 2026-04-26 "first professional business platform / new build, not a migration" reframe.

**Reasoning:** GL directive 2026-04-30: *"it is a migration, not a new build."* The 2026-04-26 reframe was motivated by (a) Jeff-disclosure concerns — the failed Odoo attempt is BBC-internal context Jeff hasn't been briefed on yet — and (b) avoiding a too-mechanical "translate Odoo → ERPNext" mental model. Both concerns remain valid, but neither justifies denying the technical reality:

- Catalog data was ported from the prior Odoo deployment to ERPNext on 2026-04-30 (53 Website Items, 10,631 Items, 10,578 variants, 10,613 Item Prices — verified against the running DB).
- Form intent (the 45-field Lead schema, the `/book` + `/contact` form shapes) was carried forward from the Hetzner Odoo `arch_db` snapshots in `_resources/odoo-live-snapshot/`.
- Business policies, brand identity, voice rules, and the legal interview answers all originated in the Odoo phase and were brought across into `_resources/`.
- At cutover (Phase 6), the new ERPNext storefront replaces `locallytwisted.com` at the same domain.

The right framing: **migration of business intent + catalog data into a fresh ERPNext install.** "Fresh install" captures that we did NOT auto-translate Odoo modules / DB dumps / configuration — the destination was greenfield ERPNext, hand-built informed by Odoo discovery. "Migration" captures the truth about catalog records, form schema, policies, and the eventual domain cutover.

**What stays from the 2026-04-26 reframe:**

- **Jeff-disclosure stealth.** Jeff knows there's an audit; he doesn't know the prior Odoo attempt failed in testing. Internal docs use migration framing; Jeff-facing communications still don't leak that context until Phase 1 is demo-ready.
- **Hand-build, not auto-translate.** No automated Odoo-to-ERPNext module/data conversion tooling. Catalog data was the only record-level port; everything else was hand-built from discovery.
- **`_resources/` is canonical and platform-agnostic** in language. Anything from the Odoo dir that applies has been copied + scrubbed.
- **Reference Disposition stands.** `locally-twisted-odoo/` clone, `5.78.136.133` Hetzner deployment, `CBaen/locally-twisted-odoo` GitHub repo, and current `locallytwisted.com` all retire at/post-cutover.

**Alternatives considered:** keep the "new build" frame. Rejected — denying the migration reality cost token-spend across multiple sessions and contributed to Codex's `CHATGPT.md` / `CODING-HANDOFF.md` push to "verify before relying on" the Claude-era docs.

**Files updated** to carry the new framing: `CLAUDE.md`, `HANDOFF.md`, `PROJECT-STATUS.md`, `CODING-HANDOFF.md`, `AGENTS.md`, `.planning/PROJECT.md`, `.planning/ROADMAP.md`, `locally-twisted-index.md`. Historical entries (prior decisions log entries, lessons-learned entries, `research/` artifacts) preserved as-is — they record what was true at writing time. This entry supersedes the 2026-04-26 reframe entry below.

**Decided by:** GL.

---

## 2026-04-30 — Catalog rebuild from live Odoo (no exceptions)

**Decision:** Live Odoo (`http://5.78.136.133/shop`) is the catalog source of truth. The cached `_resources/odoo-export/catalog.json` (2026-04-26) is historical reference. Fresh scrape lives at `_resources/odoo-live/catalog.json`. Re-scrape via `scripts/setup/scrape_odoo_live.py` before any catalog work.

**Reasoning:** GL directive 2026-04-30: *"the only source of truth is the live site... pull every product from the live site... with every single variation that a product has."* The cached catalog had 51 products; the live re-scrape on 2026-04-30 found 53 (Odoo had added `birthday-deliveries`, `large-head-missionary` since the cache). 5 products had `image_url=null` cached but DO have images on the live site (the original scraper missed lazy-loaded `data-src` patterns). Also Odoo's per-product `data-attribute-exclusions` JSON was not captured in the original scraper — the new live scrape captures and respects it.

**Alternatives considered:** keep the cached catalog and patch missing fields. Rejected — caches drift, GL was explicit.

**Decided by:** GL.

---

## 2026-04-30 — Full Item Variant model, no skipping

**Decision:** Every Odoo-valid attribute combination becomes an `Item Variant` record. Honoring Odoo's `data-attribute-exclusions` to filter forbidden combinations from the cartesian product. Verified DB counts on 2026-04-30: 53 Website Items, 10,631 Items total, 49 variant templates, 4 single-SKU templates, 10,578 variants, 10,613 Item Prices, and 32,002 Item Variant Attribute child rows.

**Reasoning:** GL directive 2026-04-30: *"ALL VARIANTS DO NOT SKIP ANY."* Earlier in the same session I had proposed a "form-fed options" alternative (treat each product as single Item, render LT-owned color/size selectors at order time) — GL named it as me trying to "divert" from the task. Rebuild Odoo accurately means full ERPNext variant model.

**Alternatives considered:** form-fed options (simpler, no variant explosion). Rejected.

**Decided by:** GL.

---

## 2026-04-30 — 11-category Item Group hierarchy

**Decision:** `Shop Items` becomes a parent (`is_group=1`) with 11 children: Arches (10), Columns (10), Bouquets (16), Get-Well Bouquets (3), Garlands (4), Drops (1), Grab & Go (2), Table Decor (3), Stands & Easels (2), Deliveries (1), Seasonal & Specialty (1). Each `show_in_website=1`. Routes auto-generated as `shop-items/<scrubbed-name>`.

**Reasoning:** GL directive: mega menu populated from Odoo's natural taxonomy. The taxonomy is implied by Odoo product slug patterns (`*-arch`, `*-column`, `*-bouquet`, etc.) — formalized as 11 explicit BBC-decision Item Groups. Captured as a fixture so it's reproducible on transfer.

**Slug→group mapping:** lives at `_resources/odoo-live/slug_to_group.json` for review.

**Decided by:** Claude (taxonomy proposal), confirmed by GL via "Shape A" answer.

---

## 2026-04-30 — Routes change to `/shop-items/<group>/<item>`

**Decision:** All Website Items re-route from `shop/<item_code>` (the prior pattern) to `shop-items/<group_slug>/<item_slug>` for IA cleanliness. Pre-launch site has no public bookmarks; old `/shop/<item>` returns 404 from this date forward.

**Implementation gotcha:** webshop's `WebsiteItem.make_route()` appends `random_string(5)` to every auto-generated route. Override by setting `wi.route = clean_route` BEFORE save. Captured in `lessons-learned.md` 2026-04-30 Lesson 3.

**Decided by:** Claude (implementation choice within GL's "Shape A" routing decision).

---

## 2026-04-30 — `installed_apps` order changed: `locally_twisted` last

**Decision:** Reordered Frappe's `installed_apps` global JSON list to put `locally_twisted` LAST: `["frappe", "erpnext", "payments", "webshop", "locally_twisted"]`. Required for our template overrides at `apps/locally_twisted/.../templates/generators/item/...` to win the reversed-app-order ChoiceLoader resolution against webshop's stock templates.

**Reasoning:** `template_page.py:53` does `for app in reversed(frappe.get_installed_apps())` and picks the first match. Default order placed locally_twisted in middle; reversed put webshop first. Empirically verified: a marker class in our override file did NOT render until apps order was changed.

**Side-effect:** any future new app installed AFTER this change will appear AFTER locally_twisted in the list — meaning the new app would WIN over our overrides for any template path it defines. If a new app is installed, re-set the global to keep `locally_twisted` last.

**Decided by:** Claude (necessary technical fix to enable template overrides).

---

## 2026-04-30 — "Item Code" jargon and "/Nos" UoM stripped from customer-facing surfaces

**Decision:** Strip both via:

| Surface | Mechanism |
|---|---|
| Product detail title block | Jinja override at `templates/generators/item/item_details.html` (deletes the `<p class="product-code">` block) |
| Product detail price block | Jinja override at `item_add_to_cart.html` (deletes the `(...$X / Nos)` line) |
| Listing cards (JS-rendered) | CSS hide `.product-code` in lt-theme.css — webshop's compiled JS bundle can't be Jinja-overridden |

The CSS-hide is `display: none !important` — the only such chain we kept. It's contained: it removes the jargon at customer-render time without forking webshop's compiled JS bundle.

**Reasoning:** GL flagged "Shop Items | Item Code : baby-shower-garland" and "$ 150.00 / Nos" as customer-facing leakage of internal naming. Both are stock webshop chrome. Three different override mechanisms because three different render paths.

**Decided by:** GL (the flag), Claude (the implementation choice).

---

## 2026-04-30 — Variant selectors render INLINE, not behind a dialog

**Decision:** Override webshop's `item_configure.html` to render attribute selectors inline (chips for ≤8 values, dropdown for 9+) via Jinja iteration over `doc.attributes` × `frappe.get_all("Item Attribute Value", parent=<attr>)`. JS validates selection via `webshop.webshop.variant_selector.utils.get_next_attribute_and_values` and updates Add-to-Cart with the matched variant + price.

**Reasoning:** Webshop's stock pattern is a "Select Variant" button that opens a Frappe Dialog modal — customer perception is "options are hidden." GL flagged this as "missing options." Inline selectors solve the perception problem without rebuilding the underlying variant matching logic.

**Decided by:** Claude (implementation choice).

---

## 2026-04-30 — Webshop Settings managed via setup script, not fixture

**Decision:** `enable_variants=1`, `enable_attribute_filters=1`, `show_attribute_dropdowns=1` set via `scripts/setup/enable_webshop_variants.py` (one-shot, idempotent). NOT fixtured.

**Reasoning:** Webshop Settings is a Singles doctype with many fields Jeff might tweak (Stripe gateway account, checkout behavior flags, recommendations, etc.). Fixturing the whole record would risk overwriting his other config on the next `bench migrate`. Targeted setup script is precise and won't fight Jeff's edits.

**Decided by:** Claude (per fixture-discipline skill — operator-state-sensitive fields stay out of fixtures).

---

## 2026-04-30 — Phase 6 cutover work item: prune `Item Attribute Value` from fixtures

**Decision (forward-looking):** Before Jeff's first deploy after Phase 6 takeover, REMOVE `Item Attribute` from `hooks.py fixtures = [...]` for the operator-state-sensitive subset (especially `latex colors` — 51 values Jeff is most likely to add/rename as his supplier inventory shifts). Document in `NOUPDATE-DRIFT.md`.

**Reasoning:** Per `frappe-fixture-discipline` skill: BBC fixture sync uses `force=True`, which silently overwrites DB records on every migrate. If Jeff renames "Empowermint" via UI and BBC's deploy chain later runs, his rename gets reverted with no warning. Today's risk is zero (no Jeff edits yet); future risk is real.

**Decided by:** Claude (per fixture-discipline skill).

---

## 2026-04-29 (mobile-responsiveness session) — LT design competition synthesis imported as `_resources/design-guide/`

**Decision:** The 2026-04-26 LT design competition output (synthesis dir + 8 approved screenshots) is imported into this project's `_resources/design-guide/` and signposted from `CLAUDE.md` reading order step 6. Original location at `C:\Users\baenb\projects\zoho-locally-twisted\gallery\` will be deleted by GL. Treated as reference inspiration / taste calibration, not as a contract to implement verbatim.

**Reasoning:** Multiple build instances (including this one) failed to find the design contest output because it lived in a separate project directory (`zoho-locally-twisted/gallery/`) outside our LT working tree. Phase 1 PLAN.md line 47 referenced "GL's Opus Competition Redesign concept" with no path. The standard reading order on arrival (CLAUDE.md → HANDOFF.md → PROJECT.md → PLAN.md → decisions log → git log) led every instance THROUGH every artifact, and not one of them pointed at the gallery. Instances either skipped the design reference or worked without it — measurable trust cost on the resulting customer-facing pages.

GL's directive 2026-04-29: *"they should live in our directory as a design guide, not as gospel."* — affirms the inspiration framing and the agency client-isolation rule (each client folder is self-contained for transfer).

**What was imported:**
- `_resources/design-guide/synthesis/` — 4 page TSXs (landing, lookbook, shop, balloon-twisting), layout.tsx, globals.css, 5 markdown docs (rationale, mood, voice, menu, SYNTHESIS-BRIEF, SYNTHESIS-COMPLETE)
- `_resources/design-guide/screenshots/` — 8 approved PNGs (4 pages × 2 viewports) + RENDER-REPORT.md
- `_resources/design-guide/README.md` — framing note (guide, not gospel) + per-file purpose

**What was NOT imported:**
- `take_screenshots.py` (utility specific to the source project's Next.js dev server)
- `WINNER.md`, `BRIEF.md`, `SCORING-RESULTS.md`, designer-1 through designer-7 outputs — the contest provenance was preserved in this entry; the only artifact the build phase needs is the synthesis itself

**Updates to standing artifacts:**
- `CLAUDE.md` "Reference Disposition" — added `_resources/design-guide/` as a canonical resource, reading order step 6 now requires skimming the README + voice/mood/rationale before any frontend work
- `.planning/phases/01-customer-site-and-storefront/PLAN.md` line 47 — replaced vague "Opus Competition Redesign concept" reference with concrete file paths inside `_resources/design-guide/`

**Trust-cost receipt that drove this:** mobile-responsiveness session 2026-04-29. GL had to point me at the contest output explicitly because no signpost existed in the project. Every prior instance had the same gap. The fix is structural — once the README is in the standard reading order, future instances will encounter it during the normal arrival path.

**Decided by:** GL directive 2026-04-29.

---

## 2026-04-29 (guest-cart + Stripe-Link + cascade session) — Path B (true cookie cart) over the cheap Buy-Now-only alternative

**Decision:** Build a real localStorage-backed multi-item guest cart (Path B) rather than removing webshop's Add-to-Cart UI and routing all flows through the single-item buy-now `/checkout?item=...` path (Path A).

**Reasoning:** GL: *"Path B is the only answer. Quality is ALWAYS the answer."* The cheaper Path A would have shipped today but locked the customer experience to one item per checkout. For LT's small-shop tier (sub-$200 themed bouquets, kits) that's acceptable for a single purchase but blocks the natural "I'll add a few things while I'm here" multi-item shopping behavior. Path B took the rest of the session to build but matches what customers expect from any e-commerce site.

**Architecture committed:**
- Cart stored in browser localStorage (versioned schema, in-memory fallback for Safari Private Mode)
- Server-side state created ONCE at checkout submit (Customer + Contact + Address + SO + PR + Stripe Session)
- Webshop's `update_cart` JS function overridden at runtime; `.btn-add-to-cart-list` clicks intercepted in capture phase BEFORE webshop's bubble-phase login redirect
- `/cart` page LT-owned (overrides webshop's via `website_route_rules`, file named `lt_cart.{py,html}` to avoid name collision)
- `/checkout` operates in two modes: buy-now (server-renders single line from `?item=&qty=`) or cart (JS hydrates summary from localStorage)
- `submit_guest_order` accepts EITHER buy-now params OR `items_json` array

**Alternatives rejected:**
- Path A: hide webshop's stock product pages from nav, convert LT `/shop` Add-to-Cart buttons to Buy Now, drop multi-item entirely. (Rejected: loses the natural multi-item UX customers expect.)
- Path C: change `redirect_on_action` to /contact instead of /login. (Rejected: still bounces the customer off the cart, doesn't actually solve the requirement.)
- Modifying webshop directly: `apps/webshop/` is bind-mounted from a gitignored upstream clone; modifications would be wiped on next install/restart.

**Decided by:** GL 2026-04-29. *"Quality is ALWAYS the answer."*

---

## 2026-04-29 (guest-cart session) — Stripe Link disabled at the ACCOUNT level via custom PMC, not per-Session

**Decision:** Disable Link via a custom Stripe Payment Method Configuration on LT's account (`pmc_1TRZH2DfnlZQv66ncb001soG` "LT No Link", `link.display_preference="off"`), passed on every Checkout Session. Do NOT rely on `payment_method_types=["card"]` on the Session.

**Reasoning:** GL hit the Stripe-hosted Checkout page and saw Link "Save info" + "Pay with Bank via Link" + "By paying, you agree to Link's Terms and Privacy" UI rendering on top of the card form. *"I hate Link, it's not going to gatekeep our checkout. 'Pay without link' is not going to be forced upon anyone."*

I shipped `payment_method_types=["card"]` first; GL caught it ("straight to link again"). Rendered the page in Playwright, confirmed Link UI persisted regardless of the Session-level restriction. Per Stripe documentation and a knowledge gem in the `stripe:stripe-best-practices` skill: *"Link is controlled through the Dashboard. Create a custom payment method configuration with Link off."*

**Pattern:**
1. Create a top-level PMC on the account: `stripe.PaymentMethodConfiguration.create(name=..., card={"display_preference": {"preference": "on"}}, link={"display_preference": {"preference": "off"}})`
2. Pass `payment_method_configuration: <pmc_id>` on every Checkout Session
3. Verify by rendering the page in Playwright and grepping for "Link" — the SDK Session response is misleading (it'll say `payment_method_types: ["card"]` even when Link UI is showing)

**Side effects accepted:**
- No Klarna / Affirm / Cash App Pay / Bank-via-ACH (could be added by enabling those individually on the PMC if GL ever wants them)
- Apple Pay + Google Pay still work — they're card wallets, surface automatically on supported devices, independent of Link

**Constraint discovered:** PMC parent-child API has ownership rules. Pre-existing platform-managed PMCs on the account cannot be modified or used as parents for child configs ("Child configurations can only be created by the parent configuration's owner"). Workaround: create a NEW top-level PMC without specifying parent — succeeds because the account owns it.

**Decided by:** GL 2026-04-29. The PMC pattern was implementation-level; the "kill Link entirely, sign-in is optional" product rule came from GL.

---

## 2026-04-29 (cascade session) — ERPNext "everything cascades" pattern wired in `/payment-success`

**Decision:** Beyond marking PR paid, `/payment-success` now also: creates Sales Invoice from SO (idempotent), sends transactional receipt email to customer, sends operator notification to `locallytwisted@gmail.com` (overridable via `site_config.lt_operator_email`), sends welcome email if first-time customer. All four wrapped in try/except so a backend reconciliation glitch never blocks the customer's `/thank-you` redirect.

**Reasoning:** GL's framing: *"This is one of the things we need to utilize HEAVILY with this software. That's why I picked it."* Per the discussion-tier ambition, every paid order should propagate into ERPNext's accounting + comms + analytics surfaces automatically — not as discrete subsequent tasks. The cascade is the foundation for "one source of truth" customer records.

**What cascades automatically post-decision:**
- Customer dedup at /checkout (3-case: returning / Contact-from-Lead / fresh) — closes the orphan-customer hole
- SO submit → ERPNext's standard chain (Customer record updated, address attached)
- PR.set_as_paid → Payment Entry (auto via ERPNext) → posts to AR + Bank account in GL
- SI submit → posts to Sales income + Tax payable in GL
- Each email send → Communication record on SO/Customer (auto via `frappe.sendmail` reference_doctype/name)

**What's deliberately deferred:**
- Calendar Event from SO delivery_date — Phase 3 (operator workflow)
- Project + Task from big-ticket SOs — Phase 3
- Stock movement / Delivery Note — Phase 4 (when stock-tracking turns on; currently `allow_items_not_in_stock=1`)

**Idempotency principle:** Every email helper checks for existing Communication with the exact subject before sending. Means: backfill is safe, webhook double-fire is safe, retry is safe. Same principle for SI: check existing Sales Invoice Item rows for this SO before creating.

**Trap avoided:** wkhtmltopdf-in-Docker. Set `mute_email = True` on Sales Invoice and never pass `attach_print` on `frappe.sendmail`. The HTML body of the email IS the receipt; production should configure `host_name` in `site_config.json` to a docker-internal hostname so PDF rendering works, but for the demo flow the HTML email is sufficient.

**Operator email recipient:** Hardcoded constant `OPERATOR_EMAIL = "locallytwisted@gmail.com"` in `payment_success.py`, with override path via `frappe.conf.get("lt_operator_email")`. When LT routes to a different inbox, set via `bench --site frontend set-config lt_operator_email <addr>` rather than editing the constant.

**Decided by:** GL 2026-04-29. The cascade architecture, the file structure, and the idempotency pattern are all implementation choices; the "utilize HEAVILY" ambition came from GL.

---

## 2026-04-29 (Stripe migration session) — Migrate Charges API → Checkout Sessions NOW, not in Phase 4

**Decision:** The migration from Frappe's bundled Stripe Charges API integration to Stripe Checkout Sessions (Stripe-hosted page) happens BEFORE the demo to Jeff, not in Phase 4 hardening. The previous instance had logged this as Phase 4 debt (entry below 2026-04-29 "Frappe payments app uses legacy Charges API"); GL pulled it forward when they saw the customer experience.

**Reasoning:** GL hit `/stripe_checkout` (Frappe's bundled card form, legacy Charges API) during a real test purchase and stopped. *"This looks unprofessional. I don't trust it."* Compared against the Odoo `/shop/cart` → `/shop/address` → `/shop/payment` flow which had branded LT chrome + persistent order summary throughout. The Frappe form had the LT header but a barebones unbranded panel below — no order summary, no item visual, no security indicators, no "Powered by Stripe" badge.

The professionalism gap is bigger than the dev-effort cost. Jeff will react the same way GL did. Migration cannot wait.

**What it commits us to:**
- `submit_guest_order` returns a `https://checkout.stripe.com/c/pay/cs_test_...` URL instead of Frappe's `pr.payment_url`
- Customer sees Stripe's hosted page with their full production UI: dynamic payment methods (Card / Klarna / Affirm / Cash App Pay / Bank / Link), real-time card validation, "Powered by Stripe" footer, security badges
- URL bar reads `checkout.stripe.com` — recognized trust signal
- Sales Order + Payment Request creation stays as-is (auditable record); only the customer-facing URL changes
- Webhook handler shipped at `apps/locally_twisted/locally_twisted/payments/stripe_webhook.py` (signature-verified, idempotent) for production reconciliation
- Server-side reconciliation on `/payment-success` route makes webhook OPTIONAL for the demo flow — the moment a customer lands after Stripe success, we retrieve the session via Stripe API, verify `payment_status == 'paid'`, and call `pr.set_as_paid()` synchronously. Idempotent: if the webhook also fires, it no-ops because the PR is already Paid.

**Alternatives considered:**
- Polish the existing Frappe `/stripe_checkout` template via CSS overrides (rejected — customer still doesn't see `checkout.stripe.com`, still legacy Charges API, still no Apple Pay / Link / 3DS, looks "homemade" no matter how well styled)
- Stripe Payment Element (embedded) instead of hosted Checkout (rejected for now — keeping customer on our domain is nice but the trust signal of `checkout.stripe.com` in the URL bar is the bigger win for LT's customer base of one-off occasional buyers)

**Decided by:** GL 2026-04-29, after seeing the side-by-side comparison (Odoo's flow vs. our Frappe form vs. Stripe's hosted page).

---

## 2026-04-29 (Stripe migration session) — `/payment-success` overridden via website_route_rules

**Decision:** `/payment-success` is overridden in our app (not Frappe's bundled template). Custom controller at `apps/locally_twisted/locally_twisted/www/payment_success.py` handles two paths: Stripe Checkout Session redirect (`?session_id=cs_test_...`) and a legacy fallback for the Frappe payments redirect URL.

**Reasoning:** Frappe's `payments` app has TWO upstream bugs that converge on this route:
1. `apps/payments/.../stripe_settings.py:272` unconditionally appends `?redirect_to=None` (literal "None") to the redirect URL even when the URL already has `?` — produces a malformed double-`?` URL
2. The bundled `/payment-success` controller calls `frappe.get_doc("Payment Request", ...)` under the GUEST session — 403s because Payment Request is restricted

We can't patch upstream cleanly: `apps/payments/` is bind-mounted from a gitignored upstream clone. The agency rule "work WITHIN Frappe, don't fight it" still applies — the right move is to use Frappe's documented mechanism (`website_route_rules` in `hooks.py`) to claim the route in our app.

**The override does:**
- Strips any `?redirect_to=None` tail off the `docname` form_dict value (defends against the upstream URL malformation if it ever fires)
- Verifies the linked `Integration Request` is `Completed` OR the Stripe session reports `payment_status == 'paid'` — proves the charge actually succeeded; defends against guessing PR/SO names
- Looks up the SO with elevated read perms (we never read PR as guest)
- Marks the PR Paid synchronously (creates Payment Entry)
- Redirects to `/thank-you?order=<so_name>` (already exists, works for guests)

**Trade-off:** when (if) Frappe fixes the upstream bugs, our override is still useful — it gives guests a clean post-checkout landing without exposing Payment Request, and handles `session_id`-based redirects that the Frappe controller doesn't.

**Decided by:** This instance, 2026-04-29, after debugging GL's `/payment-success?...?redirect_to=None` 403 report.

---

## 2026-04-29 (Stripe migration session) — Each LT integration uses LT's own Stripe account, not BBC's

**Decision:** LT's customer-facing payments flow through LT's own Stripe account. BBC's Stripe account is only ever used to bill GL's clients for agency work — never to process customer charges to LT (or any other BBC client).

**Reasoning:** This is the agency-wide standard codified during the same session at `Built_by_Cameron/built-by-cameron-decisions.md`. For LT specifically, the previous instance configured Stripe Settings 'Test' from `.env` keys provided by GL. Those keys ARE LT's. The Stripe CLI's stored auth (via `stripe login`) is a SEPARATE auth context — it can be (and currently is) authed to BBC for development convenience without affecting ERPNext's runtime.

**Practical implications:**
- ERPNext's Stripe Settings 'Test' uses LT's `pk_test_...` and `sk_test_...` from `.env` — verified by the Stripe Checkout page rendering the line item under LT's account name
- The Stripe Dashboard's public business name shown on the Checkout page comes from LT's account profile (currently "Locally twisted llc" — rename to "Locally Twisted" when Jeff's available for 2FA)
- For Stripe CLI tasks (e.g., webhook listening), use `stripe listen --api-key $SK_TEST_FROM_ENV` to point at LT's account WITHOUT needing CLI auth — bypasses the 2FA blocker
- At Frappe Cloud cutover (Phase 6), LT's live mode keys go in `.env` and Stripe Settings 'Live'; webhook endpoint is configured in Stripe Dashboard against LT's account; signing secret goes in production `site_config.json`

**Decided by:** GL 2026-04-29, in response to my mistakenly assuming BBC's CLI auth was the right credentials. *"the Built by Cameron account is for my personal business not locally twisted. they have their own account. we need to keep them separate."*

---

## 2026-04-29 (Stripe + guest checkout session) — Option B (true guest checkout) over Option A (silent User account)

**Decision:** No User account is created during checkout — ever. Guest checkout creates only Customer + Contact + Address + Sales Order + Payment Request. The customer is identified by email; they cannot log in to a portal because no User record exists for their email.

**Reasoning:** GL initially greenlit Option A (silently create User with `send_welcome_email=0` so the customer experiences "guest checkout" without a registration form, but a User record exists). I drafted a research brief at `research/expedition-guest-checkout-legal/research-brief.md` to scope the legal compliance — 50 state privacy laws, CAN-SPAM, UCPA, the silent-account-creation gray area. GL read the framing and pulled the cord: *"Oh, this is too complex legally. We cannot deal with that. There needs to be a genuine guest checkout. I'm not dealing with this research being wrong."*

Option B is well-trodden e-commerce territory: collect customer data for order fulfillment + send transactional receipt + don't market without explicit opt-in. No account-creation gray area. No silent-User state to defend in court. The legal surface stays small and uniform across all 50 US states.

**Trade-off accepted:** customer cannot self-serve their order history through a portal. Communications and receipts go through email only. For LT's customer base (one-off occasional sub-$200 buyers), this is fine — most never come back to a portal anyway.

**Decided by:** GL.

---

## 2026-04-29 (Stripe session) — Frappe payments app uses legacy Charges API; accepted for test demo, swap before live launch

**Decision:** For the demo to Jeff and through Phase 1, use Frappe's built-in Stripe integration as-is. Do not refactor to Stripe Checkout Sessions or Payment Intents during the customer-site phase.

**Reasoning:** Frappe's Stripe controller at `apps/payments/payments/payment_gateways/doctype/stripe_settings/stripe_settings.py:create_charge_on_stripe` calls `stripe.Charge.create()` — the LEGACY Charges API. Per the `stripe-best-practices` skill (invoked this session): *"Never recommend the Charges API. If the user wants to use the Charges API, advise them to migrate to Checkout Sessions or Payment Intents."* The reasons modern Stripe pushes off Charges:
- No 3DS / Strong Customer Authentication support (will fail in EU; may fail with US issuers requiring 3DS)
- No dynamic payment methods (no Apple Pay, Google Pay, Link auto-injection)
- No fraud signals as rich as PaymentIntents

For test mode + a US-only customer base in Utah at sub-$300 transaction sizes, Charges API still works and serves the demo. **For production hardening (Phase 4 — Stripe + invoicing slice), this gets fixed first.** Either:
- Build a custom controller in our app that uses CheckoutSessions, register it via `override_payment_gateway_controller` (or wrap the existing Stripe Settings via subclass)
- Wait for Frappe community to update the payments app and rebase

**Alternatives considered:**
- Build CheckoutSessions integration NOW, bypassing the payments app entirely — too much work for the demo timeline; would require reimplementing the Sales Order → Payment Request → Payment Entry plumbing
- Use Stripe Payment Links per product, sidestepping ERPNext checkout — loses the "ERPNext is doing the work" framing for the demo

**Decided by:** This instance, ratified by demo timeline. Logged as known debt for Phase 4.

---

## 2026-04-29 (Stripe session) — Order type "Shopping Cart" + flags.mute_email pattern for guest-checkout Payment Requests

**Decision:** Sales Orders created via `submit_guest_order` MUST have `order_type = "Shopping Cart"`. Payment Request submission MUST set `pr.flags.mute_email = True` AND a manual `pr.set_payment_request_url()` call after `pr.submit()` to populate `payment_url`.

**Reasoning:** Frappe's Payment Request `on_submit` hook (apps/erpnext/...payment_request.py:215) calls `send_email() → attach_print() → wkhtmltopdf` regardless of test/live mode. Inside the LT Docker stack, wkhtmltopdf cannot reach `localhost:8081` from the container's network namespace → `ConnectionRefusedError`. Both `order_type="Shopping Cart"` (line 211) AND `flags.mute_email` short-circuit `send_mail` to False, skipping the email/PDF render.

But: `set_payment_request_url()` is INSIDE the same `if send_mail:` branch. Suppressing the email also suppresses URL generation. So we must call it manually after submit, then `pr.reload()` to refresh `payment_url`.

This pattern is documented inline in `apps/locally_twisted/locally_twisted/www/checkout.py` for the next instance.

**Long-term fix (deferred):** configure `host_name` in `site_config.json` to a docker-internal hostname so wkhtmltopdf can reach back to the site without the workaround. Until that's done, every PDF-generating operation in the container will need the same pattern.

**Decided by:** This instance, after debugging three failed smoke tests and reading the Frappe payments source.

---

## 2026-04-28 (BTFP restructure session) — Background warmer (`--lt-near-white: #fffcfc`) + header matches footer blue

**Decision:** `--lt-near-white` token changed from `#FBFBFB` (cold grey) to `#fffcfc` (warm pink-tinted off-white). `.lt-header` background changed from `var(--lt-white)` to `var(--lt-soft-blue)` (the same color as `.lt-footer`). `.lt-footer__bar` (copyright bar) changed to use `var(--lt-near-white)` instead of `rgba(26, 26, 26, 0.04)` — establishing `--lt-near-white` as the new "base white" token.

**Reasoning:** GL: *"the main white background is so white it's bluish and/or gray... Try fffcfc for the main background."* The chrome (header) being matched to the footer creates a "wrap" feeling — the page is bookended by the same brand color. The copyright bar uses the new warm white to break visually from the soft-blue footer band above it.

**Tokens after this decision (for the next instance to know):**
- `--lt-white: #FFFFFF` — pure white, used for cards and panels that need to pop
- `--lt-near-white: #fffcfc` — warm base white, used for body / off-white sections / copyright bar
- `--lt-soft-blue: #C3DCF3` — the brand soft blue, used for header + footer band
- `--lt-blush-tint: #FBF5F2` — used for hero bands

**Decided by:** GL.

---

## 2026-04-28 (BTFP restructure session) — Aqua + green ribbons rejected; blush + soft-blue kept

**Decision:** When adding decorative thin ribbons (full-bleed colored bands as visual separators), use ONLY blush (`.lt-band--blush`) and soft-blue (`.lt-band--soft-blue`). Aqua (`.lt-band--aqua`) and lime/green (`.lt-band--lime`) are not used in the LT visual identity.

**Reasoning:** GL specified: *"The Aqua ribbon and green ribbon have to go."* The brand palette includes those colors but they don't serve the calm/celebratory tone of the LT site. The blush + soft-blue alternation matches the brand identity and the customer base (event clients, parents, corporate event coordinators).

**Decided by:** GL.

---

## 2026-04-27 (LookBook → Portfolio rename) — Menu name changed; URL /lookbook stays

**Decision:** The navigation link previously labeled "LookBook" now reads "Portfolio" in both desktop and mobile menus. Same homepage CTAs that read "lookbook" now read "portfolio." The URL path `/lookbook` is unchanged — clicking "Portfolio" goes to `/lookbook`.

**Reasoning:** GL: *"I prefer 'Portfolio' over 'LookBook' or 'Gallery.' Jeff charges art prices so he might as well act like an artist haha. No he really is."* "Lookbook" is physical-book terminology; "portfolio" matches an artist's positioning and Jeff's actual price tier ($400+ custom installations, $130/$115 hourly per artist).

**URL trade-off:** keeping `/lookbook` avoids 301 redirect chains and any SEO disruption (though the page wasn't getting indexed yet). When Slice 7 is iterated again, GL can reconsider renaming the route to `/portfolio` with a redirect.

**Decided by:** GL.

---

## 2026-04-27 (homepage build session — late) — Bouquets added as 6th customizable category for the future Design Studio

**Decision:** Bouquets join Balloon Arches, Columns & Pillars, Organic Garlands, Picture Perfect Backdrops, and Balloon Drops as the customizable categories that will eventually get the interactive "Design Studio" experience.

**Reasoning:** GL realized 2026-04-27 that bouquets are also customizable in Jeff's actual business (size of bouquet, number of balloons, mylar add-ons, themed toppers, etc.). The original 5-category list came from the approved Odoo `s_lt_categories` snippet which didn't include bouquets explicitly. Adding it to the future Design Studio scope; the homepage Custom Creations grid stays at 5 for now until the Lookbook surface (Slice 7) is the right place to surface the 6th.

**Decided by:** GL.

---

## 2026-04-27 (homepage build session) — Reviews carousel chosen over expanded client logo crawl as primary social proof

**Decision:** The reviews block on the homepage uses a horizontal-scrolling carousel of full review cards (currently 19 real Google 5-star reviews × 2 for seamless loop = 38 cards in the DOM). The client logo crawl stays at the bottom of the page but is now visually subordinated to the reviews.

**Reasoning:** GL's instinct: "He's been in business 28 years; the man can have a carousel of praise that matters more than the carousel of businesses at the bottom." For a high-touch event-decor business, customer *words* persuade prospective clients more than corporate *logos*. Logos prove "we worked with X"; quotes prove "X said this thing about working with us." The latter is harder to fake and harder to ignore.

**Implementation:** Same CSS marquee pattern as the client crawl (overflow:hidden + flex track + animation:translateX + duplicate set with aria-hidden + edge-fade mask + pause-on-hover) but with full review cards (320px wide, fixed). 360s for full loop so cards have reading time. Reduced-motion users see all cards stacked statically.

**Alternatives considered:** Single-card fade carousel (simpler, less visible content); page-based fade (5 cards visible, fade to next 5); arrow-controlled manual carousel (more complex). Horizontal marquee won because it matches the existing client crawl pattern and lets the user pause-on-hover to read whichever card catches their eye.

**Decided by:** GL.

---

## 2026-04-27 (homepage build session) — Twisting & Face Painting moved to bottom of homepage

**Decision:** The Balloon Twisting & Face Painting spotlight section moved from mid-page (after Recent Celebrations) to the bottom of the homepage (after the Closing CTA).

**Reasoning:** Per GL's strategic frame: balloon twisting and face painting are Jeff's love but are not the high-margin work and don't grow the business. Big-event corporate/wedding/birthday work is where the revenue is and where the business can be set up for sale. The homepage should lead with the lookbook-forward shape (hero → reviews → categories → recent work) and only mention the live-services side at the bottom for visitors specifically looking for it. Quote: *"That is not where this is right now. I do not think people who buy a balloon event company want to deal with a face-painting company run by white Mormon women who are all very self-important."*

The `/balloon-twisting-and-face-painting` page itself is still a first-class surface (already built); just no longer mid-homepage.

**Decided by:** GL. Strategic frame for the rebuild.

---

## 2026-04-27 (homepage build session) — `/book` moved from Phase 2 → Phase 1 (Slice 10)

**Decision:** The `/book` form (the deep 45-field inquiry intake) is now part of Phase 1 (Customer site), specifically Slice 10. It was originally Phase 2 (Lead Intake).

**Reasoning:** The lookbook-forward shape requires `/book` to be live on day one. Every "Tell us about your event" CTA on the site (hero, closing, future service-category pages, future Color Chart, future Lookbook) points at `/book` as the inquiry conversion path. Without `/book`, the inquiries go nowhere. Phase 1 cannot be demoed to Jeff without the conversion path working.

**Phase 2 reframed:** Phase 2 is now "form-handling depth" — Contact dedup logic, customer acknowledgment email automation, loud-failure compliance audit across all forms, monitor alerts. The forms exist in Phase 1; the depth around them lives in Phase 2.

**Decided by:** This instance, ratified by the lookbook-forward direction GL had already locked. ROADMAP.md and PLAN.md updated to reflect.

---

## 2026-04-27 (homepage build session) — About page deferred until Jeff is ready

**Decision:** No About page or About snippet ships in v1 of the homepage. Contact page covers the basics. The previously-coded "About" section on the homepage was removed.

**Reasoning:** Jeff hasn't approved the About copy. GL's frame: *"We will make an about page when Jeff is ready. We don't need to pressure him. There's a contact page. No about section, no about page for now. It doesn't need to ship with v1."* The synthesis design instances had filler "Built by hand. Built by people who love this." copy; that's voice-OK but not GL-confirmed about the actual team. Better to omit than to invent.

**Decided by:** GL.

---

## 2026-04-27 (homepage build session, earlier) — Site shape: lookbook-forward + small shop sidebar

**Decision:** LT's website shape is portfolio/lookbook-forward, with a small e-commerce sidebar for sub-$300 pre-configured items. Configurator UI for custom arches/columns/etc. is rejected as a checkout flow but accepted as a future "Design Studio" inquiry-capture experience.

**Reasoning:** Surveyed 9 live competitor sites in the events-decor / luxury-floral / balloon-decor category (`_resources/competitor-survey-2026-04-26.md`). Five patterns emerged across all 9: (1) every high-dollar custom item routes through consultation/quote, never a configurator; (2) portfolio is a nav item, not a homepage feature; (3) shops, when they exist, are sidebars, never headlines; (4) "Inquire" beats "Buy" above ~$30; (5) social proof tier (testimonials → Google reviews → press) matches business tier.

LT's revenue concentration is in big-ticket events ($400-15,000 custom arches, walls, drops, garlands) sold through pitch decks → invoices → phone calls. Customers don't configure $400+ on a website. The "Design Studio" concept resolves Jeff's "customers want to see colors and pick options" instinct without the wrong checkout flow: pick mood + colors + scale → output is an inquiry, not a cart.

Full rationale: `.planning/decisions/site-shape.md`. Cover story for Jeff: *"We couldn't use Odoo, so we had to rebuild on a different program. While I was rebuilding, I looked at how every other custom-balloon and event-decor company in our tier is structured today — Partistry, Balloon Emporium, the wedding florists. None of them sell custom installs through a checkout flow."*

**Decided by:** GL, with concurrence from this instance after competitor survey.

---

## 2026-04-26 (later, after Slice 2 + accessibility + contact build) — Platform direction RESOLVED: stay Frappe-native

**Decision:** LT's customer-facing website stays inside Frappe / Frappe webshop. The platform-direction question that the previous instance left open at session end is now answered by demonstration.

**Reasoning:** The codified Frappe-native technique passed three independent visual gates this session:

1. **`/accessibility` static portal page** — built end-to-end as `apps/locally_twisted/locally_twisted/www/accessibility.{html,py}`, GL confirmed: *"the content in the middle of the page looked good!"*
2. **Slice 2 chrome (header + footer)** — Jinja partial overrides at `templates/includes/{navbar,footer}/`, replaced Frappe's defaults with the approved Odoo two-tier desktop / single-row mobile structure. GL iterated on logo size, footer centering, footer padding, and 3-column-on-mobile spec; technique held under those iterations. GL confirmed: *"so far so good! It's getting better."*
3. **`/contact` form-bearing portal page** — full pipeline working: AJAX form → whitelisted controller → Lead + linked Communication created, zero console errors, smoke test confirmed `CRM-LEAD-2026-00001` persisted with the message body. GL confirmed: *"Holy shit! You did it!"*

The two prior failed attempts on this stack failed by *technique*, not *architecture*. The codification work earlier this session (`frappe-portal-implementation.md`, `frappe-conventions.md` updates, `license-isolated-app-architecture.md`, plus the `Built_by_Cameron/.claude/capabilities/meals/build-frappe-portal-page.md` meal) made the right technique discoverable and enforceable. The architecture was always sound.

**What this commits us to:**
- All Phase 1 customer-facing surfaces continue on Frappe + webshop. The remaining slices (refund-policy, FAQ, BTFP service page, products browse, product detail, cart, checkout) build on the meal pattern.
- Phase 2 (`/book` lead intake form) follows the same form-bearing portal page shape as `/contact`, with the larger Lead schema.
- Phase 4 (Stripe via webshop's payments-app integration) stays in scope; webshop's bundles are now compiled (Node + yarn installed in the backend container) so storefront pages render correctly.
- The agency-tier "two-app split" question (`agency_platform` + `<client>_connector`) stays open as a future architectural decision per the agency decisions log; not blocking for LT's current Phase 1 work.

**What's NOT committed:**
- The platform decision is *Frappe-native for the customer-facing website*. It does NOT preclude a future pivot if a specific page or workflow proves Frappe-impossible. The off-ramp condition GL set ("if Frappe can't deliver this visual + UX bar, GL pivots away from ERPNext") still applies — it just hasn't fired yet.
- Newsletter signup, Google Maps embed, modal-with-auto-redirect, and a few other polish items were deliberately skipped on the contact page and are documented as future work; they don't change the platform decision.

**Decided by:** GL by demonstration. The contact-page success was the implicit affirmation; this entry makes it written.

---

## 2026-04-26 (post-session research) — License posture clarified: ERPNext is GPL-3.0, Frappe is MIT, AGPL concern was Builder-specific (not installed)

**Decision:** The expedition's Flag 8 raised an AGPL concern. Research + direct verification against `apps/<app>/license.txt` in the running LT stack establishes the actual license set:

| App | License | Notes |
|---|---|---|
| frappe (Framework) | MIT | Custom code on Frappe sits closest to MIT territory |
| erpnext | GPL-3.0 | Derivative-work exposure if our app derives from ERPNext internals |
| webshop | GPL-3.0 | Same |
| payments | MIT | No copyleft pressure |
| locally_twisted (custom) | MIT | License placeholder in license.txt — owner field needs filling |

**The AGPL claim was specifically about Frappe Builder** (a separate optional app) — NOT about ERPNext or Frappe Framework core. Builder is not installed on LT. The AGPL concern only re-applies if a future BBC client adopts Builder; it does not apply to LT's current stack.

**Reasoning:** the expedition's Flag 8 left this ambiguous, and a downstream reading could have absorbed "ERPNext / Frappe might be AGPL." Direct verification corrects that. Our Build → Sell → Transfer model deals with GPL-3.0 derivative-work analysis (a more conventional, well-documented legal posture), not the AGPL network-use clause.

**Operational consequence for LT specifically:**
- Continue building `locally_twisted` as a Frappe-first custom app
- Interact with ERPNext / Webshop via documented hooks, public APIs, DocType reads, NOT by editing core or subclassing internals
- When Phase 4 (payments) wires up Stripe, that goes through the `payments` app's `Payment Gateway Account` DocType (MIT-licensed surface)
- When the catalog seeds, query through Webshop's `Website Item` API (GPL-3.0 read), don't copy Webshop internals into our app

**Open architectural question for the agency tier (not LT's call alone):** whether to split custom code into `agency_platform` (reusable) + `locally_twisted_connector` (thin adapter) for stronger license isolation. Tracked at `Built_by_Cameron/built-by-cameron-decisions.md` 2026-04-26 entry "License matrix verified..." Finding 3.

**Decided by:** Perplexity research surfaced the license question; verification done by reading license files directly in the running LT container 2026-04-26. Codified at agency-tier conventions doc.

---

## 2026-04-26 (session end) — Platform-direction question is OPEN; landing build approach was wrong on three counts

**Decision:** No platform direction decided this session. The question is now explicitly on GL's desk for the next conversation.

**The question, verbatim from the synthesis:** *Do you want to keep building the customer-facing website inside Frappe + webshop, OR explore a simpler front door (WordPress / Webflow / Next.js) with ERPNext quietly running the back office?*

**Reasoning:** A full expedition (3 source-separated researchers + convergence + devil's advocate + GL Proxy) found:

1. The Frappe theme ecosystem is THIN. No turnkey polished customer-facing themes exist. Every Frappe-built site that looks polished was built by Frappe employees for Frappe properties (frappe.io, fossunited.org, cloud.frappe.io). No documented case of a small business successfully running a polished customer-facing site on Frappe was found.
2. Two LT homepage builds have failed in two consecutive sessions. Both failed by the same pattern: invented placeholder copy + band-aid CSS overrides + declaring "done" off DOM facts before GL opened the page in a real browser. The architecture wasn't the problem; the technique was.
3. The Phase 1 off-ramp condition GL set ("if ERPNext can't deliver this visual + UX bar, GL pivots away from ERPNext") is exactly what the Devil's Advocate questioned. It has not been answered consciously.

The GL Proxy flagged the convergence's tendency to route past the platform question and steelman the Frappe path. This decision entry surfaces it as the open question it is.

**What's known:**
- Frappe + custom Jinja + custom CSS will work eventually but requires substantial custom CSS work and Jeff cannot maintain it post-handoff.
- WordPress + WooCommerce has the most off-the-shelf plugins for service booking + ecommerce but is the most-hacked CMS in the world (security maintenance burden).
- Webflow is designer-first and Jeff can edit pages himself, but its ecommerce is light for complex variant catalogs.
- Next.js + headless commerce (Vercel Commerce, Saleor, Medusa.js) gives best design freedom and best SEO but is Cameron-maintained forever and adds a sync layer to ERPNext.

**Alternatives considered:** Keep building on Frappe without surfacing the question (rejected — would repeat the two-session failure pattern). Pre-decide for GL based on convergence (rejected — the choice depends on trade-offs only GL can weigh). Run more research first (rejected — the expedition was thorough; what's missing is GL's input, not more data).

**Decided by:** No decision yet. GL is collecting more information. They asked specifically about webshop architecture, SEO/GEO/AEO of decoupled, service-scheduling needs, GitHub catalog import patterns, and whether Next.js works for ecommerce. All answered in the session transcript before this entry was written. They want to compare Vercel Commerce demo + Frappe Builder + Webflow templates side by side before deciding.

**Status:** PENDING. Blocks all build tasks (#11, #12, #13, #14 in the session-end queue). Next instance must read `research/expedition-frappe-theme/synthesis.md` and confirm direction with GL before any visible build work resumes.

---

## 2026-04-26 (session end) — Approved Jeff content is NEVER invented — pull from Odoo XML or live locallytwisted.com

**Decision:** All customer-facing copy on the LT site comes from one of two authoritative sources, never from instance imagination:
1. **`C:/Users/baenb/projects/locally-twisted-odoo/addons/locally_twisted/views/`** (XML view files in the local Odoo project) — the most recent Jeff-approved Odoo update, captured verbatim in `research/expedition-frappe-theme/ground-truth-findings.md`. Per CLAUDE.md, this is authoritative for the new build.
2. **`https://locallytwisted.com/`** (the live WordPress site Jeff still uses) — actively in front of customers today, captured verbatim in `research/expedition-frappe-theme/web-scout-findings.md`. The two sources diverge on hero copy, social icon count (3 vs 4), and credential framing ("since 1998" vs "Over 22 years"). GL has NOT yet picked which is "the" version.

**Reasoning:** Two consecutive instances invented placeholder copy ("Make Your Celebration Unforgettable", "Three services. One promise: you get the moment, we handle the magic", "Ready to plan something unforgettable?") when the actual approved copy was sitting on disk. GL caught both. The trust cost was real both times. The pattern needs to die.

**What this means in practice:**
- Before writing any text that will appear on a customer-facing page, READ the Odoo XML or scrape the live site and use the actual content.
- For copy that needs to be slightly adapted to fit a new layout, do the adaptation but preserve voice + key phrases verbatim.
- If neither source has copy for a new surface, ASK GL — do not invent.

**Open sub-decision for GL:** Which of the two sources is "the" approved version when they disagree? Specifically:
- Hero copy: "Utah's Balloon Specialists" / "Making celebrations unforgettable since 1998" (Odoo) vs "Make Your Party POP!" / "Anything you imagine, we can shape into reality" (live site)
- Social icons: 3 (Facebook, Instagram, Pinterest — Odoo) vs 4 (+ Twitter — live site)
- Credentials: "since 1998" / 28 years (Odoo) vs "Over 22 years" (live site)
- Tagline: "Utah's Balloon Specialists since 1998." (Odoo) vs different framings on live site

**Decided by:** Lessons-learned pattern from this session + GL's explicit "did you make it up?" callout. The decision becomes a standing rule once GL confirms which source is authoritative.

---

## 2026-04-26 (Web Page tabs finding) — Per-page interactivity belongs in the DocType, not a custom Web Template

**Decision:** All per-page interactivity (JavaScript, CSS, server-side data fetching) for one-off pages goes into the corresponding `Web Page` record's native tabs (`javascript`, `css`, `context_script`, `header`), NOT into a custom Web Template or a custom controller. Custom Web Templates are reserved for layouts that genuinely need cross-page reuse.

**Reasoning:** GL surfaced this 2026-04-26 after noticing that the previous instance's homepage Web Page record (`/app/web-page/locally-twisted`) used only `main_section` (Rich Text) and ignored the Script + Style + Page Builder tabs. Reading the actual `Web Page` DocType schema confirmed the framework natively provides:
- `javascript` (Code field) — per-page JavaScript at page load
- `css` (Code field) + `insert_style` (Check) — per-page CSS
- `page_blocks` (Table) — Page Builder for layout
- `header` (HTML editor) — custom hero HTML
- `context_script` (Code, Python) — server-side data fetching that injects into the Jinja context BEFORE render
- Plus full meta-tag, breadcrumb, and sidebar control

**Concrete impact on this project:**
- The pricing calculator on the BTFP service page was classified as the only tier-4 piece in Phase 1 (per the v2 website-page-index.md). It now collapses to tier 1: Page Builder for static layout + `javascript` field for math + `css` field for styling. No custom Web Template, no hooks, no app code.
- Phase 1 may have **zero tier-4 pieces**. Color swatches are the only remaining candidate, and even that may be reachable via `context_script` + a custom field on `Item Attribute Value`.
- Future page builds (landing, BTFP, contact) all use the right tabs from the start. The previous instance's content-field-only pattern is a documented anti-pattern.

**Alternatives considered:**
- Custom Web Template per interactive page (rejected — strictly worse than using the DocType's native fields; more files, more breakage surfaces, no benefit).
- Per-page `<script>` tags injected into `main_section_html` (rejected — works but harder to maintain than the dedicated `javascript` field; loses the structural separation Frappe provides).
- Custom controller per page (rejected — `context_script` does this natively without registering a controller).

**Generalizable to agency tier:** This decision motivated promoting "System-native first" to a standing principle at the top of `Built_by_Cameron/.claude/capabilities/recipes/frappe-conventions.md`, with a concrete rule: "before writing custom code, read the relevant DocType's full schema." Every BBC client benefits.

**Decided by:** GL directive 2026-04-26 ("you can use java on these pages!") + framework verification by reading the Web Page DocType schema.

---

## 2026-04-26 (webshop install + framework study) — Webshop installed durably; "work within Frappe" is the standing principle

**Decision:** Three reinforcing decisions taken in one session.

1. **`frappe/webshop` and `frappe/payments` are installed on the LT site as durable infrastructure** — bind-mounted in `pwd.yml` into all 8 frappe-image services, gitignored at the project level (the install script is the source-of-truth for HOW we installed them, not the upstream code itself). Reproducible via `python scripts/setup/install_webshop.py`. Phase 1 Slices 7-9 (products + cart + checkout) and Phase 4 (payments) are unblocked.

2. **"Work within Frappe, don't fight it" is the standing principle for all UI/template work.** GL directive 2026-04-26: *"I don't want to fight Frappe or ERPNext and their code. I want to work within it."* Operationalized as: use Jinja partial overrides (templates/includes/...) as the primary surface for header/footer/page customization; use `web_include_css` (loads after the bundle) or `website_theme_scss` (compiles into the bundle) for theme CSS; refuse `!important` chains as the receipt of fighting the framework; use Webshop's existing hooks for cart/checkout customization rather than replacing the cart pipeline.

3. **The `.web-footer` height "constraint" was never a framework constraint.** Reading `apps/frappe/frappe/public/scss/website/footer.scss` in the running container confirmed there is no `max-height` rule. The previous instance's observation came from `lt-theme.css`'s own `!important` chain interacting with the body's flex-column sticky-footer pattern. The `.web-footer` block in `lt-theme.css` (lines 477-503) and the related `.web-footer ul/li/footer-group` blocks (505-526) should be removed before the Slice 2 redo. Documented in `lessons-learned.md` 2026-04-26 entry (RESOLVED) + agency `frappe-conventions.md` "Verified against source" appendix.

**Reasoning:** Webshop install was already a known requirement (per the prior Slice 2 build session's queue + the agency capability). The install proved: (a) `bench get-app` requires `--skip-assets` to avoid the Node-not-in-image error; (b) `payments` is a hard `webshop` dependency missed in the original conventions doc; (c) `apps/` is NOT shared across frappe-image services in pwd.yml — each service needs its own bind-mount + editable pip install. All three discoveries are now in the agency conventions doc.

The "work within Frappe" principle locks in what the previous Slice 2 attempt failed to do. It is non-negotiable going forward — the band-aid pattern doubles trust damage by inheriting brittle code into the next session.

The `.web-footer` resolution unblocks the Slice 2 redo: the next instance can override the Jinja partial with their own structure (any class names, no inheritance from `.web-footer`'s SCSS) without needing to chase a phantom framework bug.

**Alternatives considered:**
- Skip webshop, run an external storefront (rejected — destroys the value of an integrated ERPNext build).
- Bake webshop into a custom Docker image instead of bind-mounting (deferred to Phase 6 Frappe Cloud cutover work — bind-mount is consistent with the existing `locally_twisted` pattern).
- Keep the `.web-footer` `!important` chains "just in case" (rejected — they actively interfere with the redo).

**Decided by:** GL directive 2026-04-26 ("we want the workshop", "I don't want to fight Frappe or ERPNext and their code. I want to work within it") + framework verification by current session.

---

## 2026-04-26 (Slice 2 build) — Custom Frappe app scaffolding is on; only Frappe Cloud cutover stays deferred

**Decision:** Custom Frappe app scaffolding (`locally_twisted` as an installable app inside the local bench) is part of the active build, not deferred. What stays deferred until Phase 6 is the Frappe Cloud signup, production deployment, and transfer-to-Jeff machinery.

**Reasoning:** GL clarified directly during the Slice 2 build session: "Frappe can and should be added. It's the cloud migration that isn't a priority until there's something to show." The earlier 2026-04-25 evening entry below conflated two things — local app scaffolding and cloud cutover — and deferred both. Only the latter should have been deferred.

The shape of the work changes with this correction:
- Theme CSS migrates from `Website Settings.head_html` (current Slice 2 implementation) to a real bundled asset at `apps/locally_twisted/locally_twisted/public/css/lt-theme.css`, registered via `hooks.py`, served through Frappe's asset pipeline.
- Custom DocTypes (`Dashboard Reviewed Item`, `LT Service Type`, `LT Lead Photo`) export as fixtures owned by the app.
- The 45+ Custom Fields on Lead export as Custom Field fixtures.
- Future Server Scripts (Phase 2 lead intake, Phase 3 cascades) live in the app, not as one-off DocType records.
- The whole customization surface becomes one installable unit (`bench install-app locally_twisted`).

**What this means in practice for Slices 3-9:** Better to scaffold the app *before* Slice 3 (landing page) so Slices 3-9 build natively into the app structure rather than as records that later need migration. Doing it now is hours of work; deferring it costs more later when the customization surface is larger.

**Supersedes:** the relevant clauses of the 2026-04-25 evening entry below ("No custom Frappe app scaffolding, no bench planning"). What that entry got right: keep all build work against the local `:8081` install, defer Frappe Cloud / transfer machinery until Phase 6. What it got wrong: lumping app scaffolding in with the cloud-side deferrals.

**Decided by:** GL directive during Slice 2 build, 2026-04-26.

---

## 2026-04-26 (later) — Phase 1 decision gates resolved

**Decision:** All four Phase 1 decision gates surfaced earlier today are resolved.

1. **Header navigation:** Option B — single "What We Make" mega-menu by product type; "Special Occasions" and "Holidays & Seasons" become filtered landing pages reachable from a "Browse by occasion" header link. See `.planning/decisions/header-navigation.md` for the full analysis.

2. **Accessibility statement:** Option B — brief intent-only statement with a working `accessibility@locallytwisted.com` contact + actually meeting WCAG 2.1 AA on the live site. Statement text drafted. See `.planning/decisions/accessibility-statement.md`.

3. **Blog presence in Phase 1:** YES — ship the blog framework with live posts (not deferred, not empty framework). Adds Slice 5b to the Phase 1 plan.

4. **Real photography sourcing:** placeholders. GL's exact words: "Generate fake quality images please... leave most images blank except everything on the main pages and 1 product image on product pages." 15 placeholder images generated via Together AI's FLUX.1-schnell, committed to `_resources/images/`. Real photography is "possibly a project for another instance" — these placeholders carry the demo until then.

5. **Customer-inquiry email destination:** `locallytwisted@gmail.com` (GL's account; GL handles inquiries currently).

6. **Pricing calculator placement:** embedded in the Balloon Twisting + Face Painting service page (Slice 4), NOT a standalone `/pricing` URL. GL's call: "the pricing calculator would be perfect for the face painting and balloon twisting page!" Better placement — customers already on that page are asking the cost question. Standalone Slice 10 removed; calculator scope folded into Slice 4.

**Reasoning:** GL chose all four answers explicitly in the green-light turn. Recommendations from `.planning/decisions/header-navigation.md` (Option B) and `.planning/decisions/accessibility-statement.md` (Option B) were accepted. Blog framework + live posts gives Phase 1 more substance for Jeff's eventual demo. Placeholder images close the visual-demo gap without committing to real photography sourcing yet.

**Decided by:** GL directive 2026-04-26.

---

## 2026-04-26 (later) — All clients default to ERPNext native payroll; Gusto removed from project scope

**Decision:** All Built by Cameron client builds default to ERPNext's native HRMS / Payroll module. Gusto is removed from the LT ERPNext-side project scope: no Gusto credential fields, no `gusto_service` Python helper, no Gusto CSV export job. The Gusto integration in the failed Odoo attempt was **never wired or used** (per GL clarification 2026-04-26) — the Odoo files are dead code on a never-launched test deployment.

**Reasoning:** GL directive 2026-04-26: "All clients will default to the ERP's native payroll. Please delete anything labeled 'Gusto.'" ERPNext HRMS supports salary structures, payroll periods, leave, attendance, and direct deposit natively. One less third-party integration to learn, configure, document, and hand off. Since Gusto never went live, there is no production behavior to preserve — clean slate.

**Alternatives considered:** Keep Gusto on ERPNext side as a CSV-export Server Script (rejected — perpetuates a third-party-payroll pattern the agency standard now overrides).

**What this means in practice:**
- `res_config_settings.py` translation drops any `gusto_*` fields; only `twilio_*` credentials carry over.
- A future phase (after the core build is stable) installs Frappe HRMS and configures it for LT.
- No accountant conversation needed — Gusto was never the system of record for LT's payroll.

**Supersedes:** the earlier 2026-04-26 entry that treated `gusto_service` as Phase 3 scope. The earlier entry has been rewritten to cover only `twilio_service`.

**Decided by:** GL directive 2026-04-26.

---

## 2026-04-26 — `twilio_service.py` is NOT a new DocType — it's an abstract service class

**Decision:** When the Phase 2 translation reaches `twilio_service.py`, do NOT create a new DocType for it. It was `models.AbstractModel` in Odoo (no records, only methods bound to a model namespace for `env["..."].method()` invocation). The Frappe-equivalent is Python helper functions inside a custom Frappe app, OR Server Scripts bound to a hook — not a DocType.

**Reasoning:** HANDOFF.md and the queue originally claimed "3 custom domain models need new DocTypes" — counting `dashboard_review` (done), `twilio_service`, and (formerly) `gusto_service`. Reading the actual sources confirmed that only `dashboard_review` stores records. `twilio_service` is a stub-and-ready service abstraction: it reads `ir.config_parameter` for credentials and calls the Twilio SDK. In Frappe it becomes a Python utility module referencing `frappe.db.get_single_value('LT Settings', '...')`.

**Alternatives considered:** Create an empty DocType that holds nothing and exists just to namespace the methods (rejected — pointless, breaks the Frappe pattern). Skip Twilio entirely (rejected — SMS notifications are real product scope).

**Decided by:** Trellis-successor (this session), 2026-04-26, after reading the actual model files. Documents the correction so the next instance doesn't re-introduce the wrong assumption.

---

## 2026-04-26 — GSD execution mode for translation work: lighter than `/gsd-execute-phase`

**Decision:** Translation phases (Phase 2 onward) execute via direct script-write-and-run rather than `/gsd-execute-phase`'s planner-checker-revision loop. Strategic GSD frame stays intact (PROJECT.md, ROADMAP.md, REQUIREMENTS.md, STATE.md, decisions log). Heavier GSD process is reserved for genuinely architectural choices.

**Reasoning:** Trellis's session burned tokens running `/gsd-execute-phase` on Phase 1 (inventory). The planner-checker-revision loop produced six PLAN files for what was conceptually mechanical work and never moved a deliverable. For translation work where the source is a file on disk and the destination is configurable through an API, the translation script *is* the plan: executable, testable, reviewable. The script doubles as commit-able evidence of the work.

The pattern that worked: read the Odoo source → write a Python script targeting Frappe's REST API → run it → verify in the UI → commit (auto-commit hook). When something needed revision (multi-select + conditional visibility, GL feedback), the revision was another script — keeps both the original translation and the revision as separate, replayable artifacts.

**Alternatives considered:** Stay on `/gsd-execute-phase` (rejected — caused the drift Trellis named). Drop GSD entirely for translation phases (rejected — the strategic artifacts answer "what does done look like" and stay valuable). Use `/gsd-quick` for each translation (acceptable but adds ceremony for what is single-file work).

**When to escalate to heavier GSD process:** When a decision is genuinely architectural and reversible-only-with-cost. Examples: choosing Server Script vs Notification framework for porting the 17 base.automations (Phase 3); the Phase 5 storefront UI direction; the Phase 9 Frappe Cloud deploy strategy.

**Decided by:** Trellis-successor proposed; GL accepted with "you are my partner and collaborator with all things technical. I need you to lead!" 2026-04-26.

---

## 2026-04-25 evening — Build locally first; defer bench/transferables until real

**Decision:** All translation work (Odoo → ERPNext) happens against the local LT install at `:8081`. No custom Frappe app scaffolding, no bench planning, no Frappe Cloud setup, no transfer-to-Jeff machinery until there is something real to transfer.

**Reasoning:** GL explicitly called this out after the session drifted: "we will deal with the bench and transferables when THERE ARE." Building deployment scaffolding for nothing wastes tokens and creates the illusion of progress. Local-first means: configure DocTypes/fields/automations/theme directly in the running ERPNext at `:8081`, prove each piece works, then formalize the packaging much later when the rebuild is far enough along to make packaging meaningful.

**Alternatives considered:** Set up custom Frappe app first (rejected — premature optimization for transfer when nothing exists yet). Plan elaborate phase machinery first (rejected — see other decision below).

**Decided by:** GL explicitly.

---

## 2026-04-25 evening — Skip Phase 1 entirely; use existing expedition inventory

**Decision:** Phase 1 (Inventory, INV-01 + INV-02) plans exist on disk but will NOT be executed. The off-Odoo expedition's `locally-twisted-odoo/research/extended-expedition-off-odoo-replacement/inventory-findings.md` is treated as the working inventory baseline. INV-02 (production arch_db read) is deferred to a late phase — content migration concern, not rebuild concern.

**Reasoning:** Phase 1 was elaborately planned (6 plans across 5 waves, parallel execution, threat models, validation strategies, two checker iterations) but it never produced code or DocTypes. GL named the drift: "you haven't even rebuilt the site in ERPNext?!" The expedition inventory covers ~65% of what INV-01 was meant to produce. The remaining 35% can be filled by reading source files inline during translation phases — no separate inventory document needed. INV-02 is about Jeff's UI-edited content, which only matters at content-migration time near cutover.

**Alternatives considered:** Compress Phase 1 to a single quick plan (rejected — even one plan is more inventory ceremony when we already have one). Stay the course on Phase 1 as planned (rejected — was the source of the drift GL just called out).

**Decided by:** GL chose "Skip Phase 1 entirely" from a pivot question.

---

## 2026-04-25 evening — Don't modify anything in locally-twisted-odoo

**Decision:** All scripts, tools, and code written in service of the migration go in `_CLIENTS/locally-twisted/`. The Odoo project at `C:\Users\baenb\projects\locally-twisted-odoo\` is read-only reference. Even "operational" tooling like `deploy.py` is off-limits.

**Reasoning:** GL: "leave odoo specific scripts and skills alone. we need to create ERPNext specific ones." The Odoo project is in production, has its own deploy gates and trust history with Jeff, and any modification — even additive — risks the same trust damage that motivated this migration. ERPNext-side tools are separate concerns and stay separate.

**Alternatives considered:** Modify `deploy.py` to add an `--inventory` subcommand (rejected by GL for the rule above). Use Odoo's MCP server (currently disconnected, status uncertain).

**Decided by:** GL explicitly.

---

## 2026-04-25 — LT Standard with Numbers chart of accounts; Calendar fiscal year; Services domain

**Decision:** ERPNext Company "Locally Twisted" uses Standard with Numbers chart of accounts, Calendar fiscal year (Jan 1 – Dec 31, 2026), Services as the industry domain.

**Reasoning:** Standard with Numbers matches Odoo's default convention (carryover for Jeff's familiarity). Calendar year is US small-business default; no indication LT has a different fiscal year. Services is the closest fit for event services (balloon decor, twisting, face painting); Retail is less natural (LT is mostly service work, not goods sale).

**Decided by:** GL confirmed via AskUserQuestion 2026-04-26.
