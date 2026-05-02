# HANDOFF — Locally Twisted

> **Deprecated for active coordination as of 2026-05-02.** This file is now a legacy whole-project handoff/context record, not the active coordination surface. For current work, use `locally-twisted-queue.md` for active lanes, `workstreams/<feature>.md` for feature-specific handoffs, `locally-twisted-decisions.md` for durable decisions, and `CODING-HANDOFF.md` for compact technical startup. Do not try to force this file into full parity with every active workstream.

**Last updated:** 2026-05-02 (Codex - shop hub routing cleanup)

Overwrite-not-append. Git is the changelog. Read this first; everything else as needed. **Audience: peer Opus 4.7 instance.** Read like I'd want to read before substantive work.

---

## State of the world (the load-bearing facts)

**Current-session delta (2026-05-02):**
- `/shop` is now the all-decor hub. Header, mobile drawer, footer, `/shop-items`, and `/all-products` send broad browse traffic to `/shop`.
- `/shop-by-category` is retired as a customer-facing category-card page and redirects to `/shop` for compatibility. Do not rebuild the old placeholder-card index for launch.
- Primary nav order is now `Balloon Decor`, `Plan by Occasion`, `Balloon Twisting & Face Painting`, `FAQ`, `Blog`, search. `Balloon Decor` stays far-left.
- `scripts/verify/smoke_shop.py` now verifies the `/shop-by-category` redirect and desktop/mobile `All Balloon Decor` links to `/shop`.

**Current-session delta (2026-05-01):**
- `/contact` is the canonical inquiry form and now carries the revised service taxonomy: Balloon Decor, Balloon Twisting, Face Painting, Delivery, Pickup, Events Inquiry, Something Else.
- `/book` is retired as a customer-facing page and redirects to `/contact?intent=quick`. Do not restore `/book` as a separate public form unless GL explicitly changes direction.
- Guided service links prefill the contact form: `/contact?service=btfp`, `/contact?service=twisting`, and `/contact?service=face-painting`.
- `/balloon-twisting-and-face-painting` was refreshed into a contact-led service page using Hetzner content and current LT styling. It no longer embeds a separate form or public deposit checkout CTA.
- `Events Inquiry` replaced `Event Package`; it is the high-value package planning path with structured package-piece checkboxes from the homepage custom categories, color prompt, and a single notes field that aggregates into existing Lead text fields.
- Delivery and Pickup are stackable services, not "Only" choices. Do not reintroduce `Delivery Only` or `Pickup Only` labels unless the UI enforces mutual exclusion.
- "Shade is required for outdoor events" only appears for live artists: Balloon Twisting and Face Painting. It does not apply to outside balloon decor, delivery, pickup, Events Inquiry, or Something Else.
- Pickup has its own panel and points customers to the location information below the form. The Riverdale badge now reads `Northern Utah Location (Residential Address)`.
- Backend Lead/CRM parity is synced for the revised intake taxonomy. `LT Service Type` now has `Delivery`, `Pickup`, and `Events Inquiry`; stale `Delivery Only` / `Event Package` records are gone; Lead Custom Field labels/depends_on logic match the public form; website submissions populate the Desk Table MultiSelect `custom_event_type`.
- Header/footer IA has been corrected against current routes: `What We Make`, `About Us`, and `Book an Event` are removed. `All Products` remains.
- Primary nav order was `Shop Balloon Decor`; superseded 2026-05-02 by `Balloon Decor`.
- Top utility bar keeps the only `Contact Us` CTA. No lower-nav Contact duplicate and no mobile-drawer Contact duplicate.
- `Plan by Occasion` routes to product/category pages, not `/contact?occasion=...` shortcuts. Verified current links: Birthday Deliveries, Baby Shower Garland, Graduation Grab n Go, Get-Well Bouquets, Large head Missionary, Garlands, Easter Arch, Logo 3 layered bouquet, Basketball Arch, Seasonal & Specialty.
- No Gallery link in current nav.
- `/book` is retired as a customer-facing page and redirects to `/contact?intent=quick`; CTAs now use `/contact`.
- `/shop-items` and `/all-products` previously aliased to `/shop-by-category`; superseded 2026-05-02. They now route to `/shop`.
- `/privacy` and `/terms-of-service` now exist and return HTTP 200 locally. Treat as plain-language drafts for Stripe readiness; Dashboard wiring/legal approval still separate.
- `scripts/verify/layout_fit.spec.js` is restored and verified. Latest command: `npm run test:layout-fit` -> 60 passed after the gate caught and Codex fixed `.lt-contact__icon` text overflow on `/contact`.
- Playwright is installed as Node/CLI tooling in npm's npx cache, not as Python `playwright` for `C:\Python314\python.exe`. Working direct CLI path: `C:\Users\baenb\AppData\Local\npm-cache\_npx\420ff84f11983ee5\node_modules\.bin\playwright.cmd` (v1.59.1).
- `scripts/verify/nav_ia.py` now guards nav order, no duplicate Contact, no retired `/book` nav links, and product-backed occasion links.
- Footer centering/balance was fixed through content/layout cleanup, not by shrinking below accessible sizes.
- Desktop menu dropdowns are contained; mobile cart/hamburger controls are visible at 390px and 430px with accessible target sizing preserved.
- Product detail/configure sales pitches are stripped: no "Start a conversation" or "Tell us what you're imagining" blocks.
- `/shop-items/arches` returning non-arches was a real bug, but not a catalog-data bug. Root cause was the custom Item Group wrapper missing Webshop's `.item-group-content` class. Restoring that contract makes Arches scope correctly.
- Listing cards now surface `lt_brand_description` through `locally_twisted.api.product_listing.get_product_filter_data`, registered via `override_whitelisted_methods`.
- Generated verification screenshots/browser profiles are not source; `.gitignore` now excludes the local QA output paths.

**Completed after the 2026-05-01 handoff, before the next handoff pivot:**
- Balloon render direction moved from idea to showable pilot artifacts. Completed commits: `67ff66a` render bible spec, `8db6acc` pilot prompt pack, `e18d545` first pilot drafts, `b708511` revised classic-arch direction.
- Showable pilot sheet lives at `_resources/generated-renders/pilot/pilot-contact-sheet.png`; review notes live at `_resources/generated-renders/pilot/README.md`.
- The render pilot plan at `docs/superpowers/plans/2026-05-01-balloon-render-pilot.md` now marks Tasks 1-2 complete. Task 3, ERPNext media import/mapping, remains intentionally unchecked and unbuilt.
- GL review feedback is captured: the column is closest; organic garland is possible but not assumed approved; the first arch drafts were rejected/misaligned; classic arch scale changes span/opening, not default density. Dense rainbow/multi-row arch work is custom/high-density, not the default `classic-arch` product.
- No generated pilot images have been attached to ERPNext products or Website Items.

**1. The frame is now "migration."** Earlier today I parroted the prior reframe ("new build, not a migration") and GL stopped me cold: *"it is a migration, not a new build."* Project frame is **migration of business intent + catalog data into a fresh ERPNext install**. The 2026-04-26 reframe is superseded. Internal docs use migration framing freely; Jeff-disclosure stealth survives as a separate constraint (he doesn't yet know the prior Odoo attempt failed in testing). All docs updated. See `locally-twisted-decisions.md` 2026-04-30 frame entry.

**2. The mirror landed.** Full clone of `http://5.78.136.133/` lives at `_resources/odoo-live-mirror/` — 346 pages + 510 assets + INVENTORY.md (38 KB structural analysis). Tool: `crawl4ai` (Python, Playwright-backed; chosen over httrack/wget because Odoo's site is JS-rendered). Mirror script at `scripts/mirror/mirror_hetzner.py` is reusable; re-run if you need a fresh capture. Tool-discovery research at `research/website-mirror-tool-discovery.md`.

**3. Chrome rebuild Phase 1 SHIPPED via /triadic-construction-v2.** 3 builders + 3 reviewers (Architect/SecOps/Execution Engine) + GL Proxy + fix round. The triadic discipline caught 4 critical defects + 4 important + several advisories that solo build would have shipped:
   - Mobile drawer always visible (CSS class mismatch — every mobile page would have looked broken)
   - 2 of 3 mobile mega menu accordions completely dead (data-attr + querySelector singular bug)
   - Megamenu panel had no CSS rules (would render as inline blocks pushing content down)
   - Mega-trigger CSS open-state targeting wrong class
   - Newsletter `showError` `textContent` strips the `<a href="tel:">` phone fallback
   - `@rate_limit` X-Forwarded-For bypass
   - `hash(email)` instability across container restarts
   - Esc-key on `/book` navigates away from form (pre-existing UX bug surfaced)
   - Newsletter smoke test missing (loud-failure rule violation)

   All caught and fixed in Round 2. Full receipts at `research/triadic-build-chrome-rebuild/`.

**4. `/book` is NOT the customer path anymore.** It redirects to `/contact?intent=quick` for old traffic only. GL corrected the product direction on 2026-05-01: the old booking/intake surface is now the standard solo contact form, and customer CTAs/nav should use `/contact`.

**5. The shop card category filter was silently broken since launch.** Pre-existing typo: `shop.html` wrote `data-category="{{ item.category }}"` but `shop.py` set `item["category_slug"]`. Fixed during pre-tasks. Filter pills now actually filter.

## Three things that matter most on day one

**1. Layout fit now has a restored automated gate, but GL's real browser remains the ship gate.** Use `npm run test:layout-fit` before visual claims, then inspect desktop/mobile screenshots and have GL open the actual pages because screenshots and DOM checks are still preconditions, not verdicts.

**2. Triadic-construction-v2 is heavy but it earned its keep.** I dispatched it for the chrome rebuild and it caught real defects. The skill's discipline (3 builders, 3 reviewers with distinct personas, mandatory GL Proxy, Selective Re-Validation) ate significant context but the fix-round was mechanical because the defects were named clearly with file:line. **For Phase 2 page rebuilds, you can probably go lighter** — page-by-page work has less interdependency than chrome. Single focused builder per page + audit pass at the end is probably the right shape. Reserve triadic for things touching every page.

**3. The agency gate enforces safety skills per-session, including for sub-agents.** When I dispatched 3 builder agents for the chrome work, each one had to invoke `frappe-form-integrity` / `frappe-asset-pipeline` skills in their OWN session before edits would be allowed. I documented this in each builder's brief ("Required skill invocation BEFORE any edit"). **If you spawn agents that touch Frappe app files, give them explicit skill-invocation instructions in the brief.** Builder JS in this session noted a gate detection edge case for the `frappe-migration-guard` skill that doesn't fire correctly for sub-agent contexts (was worked around with Bash). Flag for ops if it bites.

## What's live at http://localhost:8081

| Surface | State |
|---|---|
| ERPNext v15.105.0 stack (9 containers) | Running |
| Apps: frappe, erpnext, payments, webshop, locally_twisted (LAST) | Installed |
| Hetzner-shaped header (utility bar + current customer menu + search trigger) | Shipped; `What We Make` removed from current IA |
| Hetzner-shaped footer (newsletter + 3-col + social + legal) | Shipped; obsolete/nonexistent links removed |
| Mobile drawer with accordion-expand mega menus | Shipped + fixed (was always-visible at Round 1) |
| Newsletter form + endpoint + DocType + smoke test | Shipped, rate-limited 10/hr per email |
| `/book` | Retired customer surface; redirects to `/contact?intent=quick` |
| `/contactus` → `/contact` redirect | Live |
| `/contact` | Primary customer inquiry form with stackable service taxonomy, guided prefill, Events Inquiry package path, Pickup, and service-specific conditional fields |
| `/balloon-twisting-and-face-painting` | Contact-led service page refreshed from Hetzner source; CTAs use guided `/contact?service=...` links |
| `/shop-items` + `/all-products` | Route to `/shop` |
| `Plan by Occasion` | Product/category links only; no contact shortcuts |
| `/privacy` + `/terms-of-service` | Static policy routes live; Stripe Dashboard wiring still pending |
| Shop catalog | Same 53 Website Items / 10,578 variants / 10,613 Item Prices from yesterday |
| Stripe checkout (test mode) | Same as yesterday — guest cart + Checkout Session + cascade |

## What's NOT done (next session candidates, by priority)

**P0 — Real-browser confirmation by GL.** Every Playwright + DOM verdict is a precondition. GL opening localhost:8081 at desktop AND mobile is the actual ship gate. They've already done initial visual review (gave green light on "usable") so this is partial-confirmation already.

**P0 — Phase 2 page rebuilds (the big remaining bite).** From the rebuild plan, in priority order:
1. `/refund-policy` Hetzner refresh
2. `/accessibility` Hetzner refresh
3. `/blog` channel + posts (use Frappe's NATIVE `Blog Post` DocType, not custom — plan-deepen caught my mistake of planning a custom one). Two posts to port verbatim from mirror.
4. Webshop `/shop` layout overhaul
5. Webshop product detail layout overhaul
6. Webshop category detail page layout overhaul (`/shop-items/<group>`)

No Gallery for now per GL 2026-05-01.

Each page: read mirror source → build Frappe controller + template → atomic commit → audit screenshot. Faster than chrome because lower interdependency.

**P0 — Webshop behavior bugs resolved 2026-05-02.**
- `/shop` no longer adds unpriced variant template codes; variant-template cards go to "Choose options" and single-SKU cards can still add directly.
- Configured variants add the actual sellable variant code to the guest cart instead of using Webshop's logged-in cart path.
- `item_configure.html` no longer runs per-attribute `frappe.get_all` lookups from Jinja; it uses the project Jinja helper `get_variant_attribute_options`.
- Partial option selections now consume `valid_options_for_attributes` and disable invalid later choices.
- Verification receipts: `python scripts/verify/smoke_shop.py`, `python scripts/verify/cart_checkout_contract.py`, `python scripts/verify/variant_media_contract.py`, and `python scripts/verify/catalog_variant_contract.py`.

**P0 — Per-product variant correctness diff resolved 2026-05-02.** `scripts/verify/catalog_variant_contract.py` compares normalized `_resources/odoo-live/catalog.json` `valid_variants` to live ERPNext `Item Variant Attribute` rows. Latest result: 53 products checked, 10,578 expected variants, 10,578 live variants, 4 single-SKU products, PASS.

**P1 — Newsletter X-Forwarded-For strip at nginx layer (Option B).** Option A (email-keyed rate limit on newsletter) shipped this session. Option B would protect `/contact`, `/checkout`, `/balloon-twisting-and-face-painting` too — they all use IP-based rate limit and share the same vulnerability. Ops/infra task.

**P2 — Category browse imagery.** Each Item Group has empty `image` field. Use representative images for category detail pages or a future image-rich mega menu; do not revive the retired `/shop-by-category` card index for launch.

## Operational rituals

| Trigger | Command |
|---|---|
| Stack stopped | `docker start $(docker ps -a --filter "name=locally-twisted-erpnext-v15" -q)` then sleep 8 |
| Edited Jinja/CSS/Web Page | `python scripts/dev/clear_website_cache.py` |
| Edited `hooks.py` / new module / fixture | `docker restart locally-twisted-erpnext-v15-backend-1 && sleep 12 && python scripts/dev/clear_website_cache.py` |
| Edited nav IA | `python scripts/verify/nav_ia.py` plus route checks for new links |
| Edited contact form service logic | `python scripts/verify/contact_service_logic.py --base-url http://localhost:8081` and `python scripts/verify/contact_prefill.py --base-url http://localhost:8081` |
| Edited backend Lead/CRM intake mapping | `python scripts/setup/sync_contact_intake_backend.py` then `python scripts/verify/lead_backend_intake_parity.py` |
| Smoke test `/contact` form | `python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --form-path /contact --skip-newsletter` (set `LT_ADMIN_PASSWORD` when backend record verification is required) |
| Check customer-site layout fit | `npm run test:layout-fit` |
| **Backend restarted, frontend now 502** | `docker restart locally-twisted-erpnext-v15-frontend-1` (nginx upstream IP cached at startup; flush by restart) — this gotcha cost me an hour today; documented in agency auto-behaviors |
| Re-mirror Hetzner | `python scripts/mirror/mirror_hetzner.py` |
| Capture chrome audit screenshots | `python scripts/verify/_oneshot_chrome_audit.py` (writes to `_resources/audit-2026-04-30-chrome/`) |
| Run smoke tests (contact + newsletter) | `PYTHONIOENCODING=utf-8 PYTHONUTF8=1 python scripts/verify/smoke_forms.py` |
| Bump CSS cache-bust | edit `hooks.py` `web_include_css` query string `?v=YYYYMMDD-N` (currently `?v=20260501-5`) |
| Bump JS cache-bust | edit `hooks.py` `web_include_js` query strings (currently `?v=20260430-2` for megamenu + newsletter) |

## Hot direction

GL named it across this session: *"clone my old site http://5.78.136.133/, the only page that stays is the landing page... using capabilities, rebuild the whole site. make sure it's frappe and ERPNext coded... using agent teams use the triadic build team."* And mid-session: *"It does look like you should wrap up based on your context... what you're documenting and leaving behind will be inherited by another Opus 4.7."*

I read this as: **autonomous ownership inside the migration frame.** GL doesn't want to babysit; they want me to make calls, log them as reversible, and document so the next instance picks up clean. They were exhausted at the start of this session ("I need a nap... I don't want to sit and babysit this build because I don't have time or energy") and gave green light to make architectural decisions autonomously with reversibility notes.

**For your session:** the chrome work is shipped (with one polish gap). Phase 2 page rebuilds are the big remaining bite. Each page is small enough that a single focused builder agent works cleanly — reserve full triadic for things with high-blast-radius (cart pipeline changes, auth/payment work, schema changes). When in doubt about scope or shape, follow the rebuild plan + the inventory + the mirror source. **The mirror IS the spec.** GL's words: *"a lot of what is at the destination is similar, but I'm not going to chat and modify every little thing because no instance does a clean transition, so just clone."*

## Suggested next move

1. Have GL open `localhost:8081/` plus `/shop-items/seasonal-specialty`, `/shop-items/seasonal-specialty/easter-balloon-cups`, `/privacy`, and `/terms-of-service` in a real browser.
2. Wire Stripe Dashboard policy URLs after GL/legal approval of `/privacy` and `/terms-of-service`.
3. Continue Phase 2 in the current order above. `/contact` is the inquiry surface; `/book` redirects to `/contact?intent=quick`.
4. Run the per-product variant correctness diff before starting webshop layout overhauls. If data discrepancies exist between Hetzner and our DB, fix at the seed layer first.

## Reading order on arrival

1. Global `C:/Users/baenb/.claude/CLAUDE.md` (auto-injected)
2. `Built_by_Cameron/CLAUDE.md` (agency rules)
3. `_CLIENTS/locally-twisted/CLAUDE.md`
4. **This file**
5. `MIRROR-REBUILD-PLAN.md` — full rebuild plan with Research Notes from /plan-deepen + GL Proxy review
6. `MIRROR-REBUILD-COMPLETE.md` — last session's wrap report
7. `_resources/design-guide/README.md` + `synthesis/voice.md` for taste calibration if doing visual work
8. `lessons-learned.md` newest entries (chrome rebuild + catalog port stacked at top)
9. `locally-twisted-decisions.md` newest entries
10. `git log --oneline -50`

## Not in flight

- Stack containers running. Backend: 8000 internal, frontend nginx forwards from 8081 host.
- No background processes from this session (all builders/reviewers exited cleanly).
- All session writes auto-committed via the post-write hook.
- No customer or transactional test data created. Newsletter test records get cleaned up by the smoke test runner.
- Mirror dir at `_resources/odoo-live-mirror/` is REFERENCE for Phase 2 page rebuilds — keep until those are done. ~30 MB. Gitignored.
- Audit screenshots at `_resources/audit-2026-04-30-chrome/` — keep as before/after evidence for chrome work; ~6 PNGs.

## A quick honesty pass for the next instance

**What worked:**
- /plan-deepen caught the custom-Blog-DocType plan error before I dispatched builders. Saved an entire wasted Phase 2 cycle.
- /triadic-construction-v2 reviewers' Active Agreement findings (mobile drawer + accordion + cart badge) were all real and would have shipped broken without independent review. The discipline earned its keep.
- The pre-task chain ("verify max_file_size, fix smoke selector, wrap log_error, /contactus redirect, shop typo, cache flush") unblocked /book in 30 minutes after weeks of "404 every session." The bug was always cache + nginx, never code.
- The autonomous architectural decision pattern (decide low-blast option + log reversibility note) let me move fast without GL gates. GL's later "great job" confirms it was the right shape.
- Sub-agents dispatched in parallel saved real wall time. Builder Jinja + Builder CSS + Builder JS each took 4-12 min running concurrently vs ~30 min sequential.

**What stumbled:**
- I parroted the "new build" frame from CLAUDE.md without questioning it on the very first message of the session. GL corrected me immediately. Then I had to undo the documentation cascade. **For you:** when GL has named a frame, that's authoritative — even if a "Reframe is locked" rule disagrees. Live correction beats documented rule.
- The Builder Jinja → Builder CSS → Builder JS coordination on class names was the single biggest time-sink. Round 1 shipped with naming divergence (template vs CSS vs JS selectors). The Build Brief specified BEM namespaces but not specific class names per element. **For your future triadic dispatches: include a class-name alignment table in the Build Brief, not just namespaces.**
- The nginx-upstream-IP-cache-after-backend-restart cost me ~30 min of confusion and three iterations. New trap; documented in agency auto-behaviors as B5.
- The `@rate_limit` "two-tier" framing in my synthesis was mechanically wrong — Frappe's decorator combines `ip:key` into ONE identity, not two counters. GL Proxy caught it before fix dispatch. **For you:** read the actual Frappe source before describing decorator behavior. Don't synthesize from training memory.
- I wrote the `lt-megamenu.js` file path in the brief but didn't enumerate the inner content classes for mega panels. Builder Jinja used `lt-megamenu__inner`/`__col`/`__heading` etc. while CSS had `lt-header__mega-inner`/`__link`. Required a final orchestrator-level rename pass after fix round. **For you:** specify INNER content class names too, not just block-level.

**Open trust state:**
- All visible work still needs route checks plus inspected desktop/mobile screenshots before visual claims.
- The current layout-fit gate is `scripts/verify/layout_fit.spec.js`; latest run via `npm run test:layout-fit` passed 60 checks.
- I read the current homepage desktop/mobile screenshots after the fit pass; the older desktop chrome bleed complaint is not currently reproducing at 1366px.
- GL has done partial real-browser confirmation; gave green light on "usable."
- Mobile chrome and the reported shop/product overflow pages look contained in the latest verification screenshots.
- Newsletter endpoint load-tested with 11 sequential requests — rate-limit fix held (11th hit limit).
- /book is no longer a structural page to test; verify its redirect behavior only. `/contact` is the form surface.

— Closeout written 2026-04-30 evening by the Opus 4.7 instance who walked the mirror rebuild from "rebuild the whole site" → frame correction (migration not new build) → mirror crawl with crawl4ai → /plan-deepen + GL Proxy → 6 pre-tasks (including unblocking /book) → triadic chrome rebuild → fix round → audit pass → documentation. GL was direct, exhausted, autonomous. The chrome shipped. Next instance: take the bite that fits your context.
