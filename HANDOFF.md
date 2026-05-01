# HANDOFF — Locally Twisted

**Last updated:** 2026-05-01 (Codex — storefront correction pass: footer/header/menu + product listing/detail fixes)

Overwrite-not-append. Git is the changelog. Read this first; everything else as needed. **Audience: peer Opus 4.7 instance.** Read like I'd want to read before substantive work.

---

## State of the world (the load-bearing facts)

**Current-session delta (2026-05-01):**
- Header/footer IA has been corrected against current routes: `What We Make`, `About Us`, and `Book an Event` are removed. `All Products` remains.
- Footer centering/balance was fixed through content/layout cleanup, not by shrinking below accessible sizes.
- Desktop menu dropdowns are contained; mobile cart/hamburger controls are visible at 390px and 430px with accessible target sizing preserved.
- Product detail/configure sales pitches are stripped: no "Start a conversation" or "Tell us what you're imagining" blocks.
- `/shop-items/arches` returning non-arches was a real bug, but not a catalog-data bug. Root cause was the custom Item Group wrapper missing Webshop's `.item-group-content` class. Restoring that contract makes Arches scope correctly.
- Listing cards now surface `lt_brand_description` through `locally_twisted.api.product_listing.get_product_filter_data`, registered via `override_whitelisted_methods`.
- Generated verification screenshots/browser profiles are not source; `.gitignore` now excludes the local QA output paths.

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

**4. `/book` is LIVE.** Was 404 every prior session. Files existed all along (`www/book.{py,html}`); root cause was a stale Frappe website cache + nginx upstream-IP staleness after backend restart. **The 404 was infrastructure, not a missing file.** Pre-task chain unblocked it. Now HTTP 200, 383 KB rendered, 30+ form fields including conditional show/hide.

**5. The shop card category filter was silently broken since launch.** Pre-existing typo: `shop.html` wrote `data-category="{{ item.category }}"` but `shop.py` set `item["category_slug"]`. Fixed during pre-tasks. Filter pills now actually filter.

## Three things that matter most on day one

**1. GL knows the desktop chrome has bleed/container issues.** Quote from session close: *"This looks like it could be usable. There's definitely some things that need to be useable. There's serious issues with the bleed and container issues on desktop but you've done a really good job so far."* The screenshot at `_resources/audit-2026-04-30-chrome/home-desktop.png` shows the centered logo dominating the utility bar (intrinsic 1050×300 from the brand image) + the truck-tagline wrapping vertically on the left. Mobile renders fine. **The fix is short: constrain `.lt-utility-bar__logo { max-height: 60-90px }` on desktop, or change `.lt-utility-bar__inner` grid template to `auto 1fr auto`.** Run that fix EARLY in your session — GL flagged it specifically and a quick win re-establishes trust.

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
| `/book` form | LIVE (was 404 every prior session) |
| `/contactus` → `/contact` redirect | Live |
| `/contact` (still redirects to `/book`) | Existing — Phase 2 rebuilds it as Hetzner's separate 6-field form |
| Shop catalog | Same 53 Website Items / 10,578 variants / 10,613 Item Prices from yesterday |
| Stripe checkout (test mode) | Same as yesterday — guest cart + Checkout Session + cascade |

## What's NOT done (next session candidates, by priority)

**P0 — Desktop chrome polish.** GL named it; address first. CSS-only edit to `.lt-utility-bar__logo` + grid. ~5 min.

**P0 — Real-browser confirmation by GL.** Every Playwright + DOM verdict is a precondition. GL opening localhost:8081 at desktop AND mobile is the actual ship gate. They've already done initial visual review (gave green light on "usable") so this is partial-confirmation already.

**P0 — Phase 2 page rebuilds (the big remaining bite).** From the rebuild plan, in priority order:
1. `/contact` rebuild as Hetzner-style separate 6-field form (currently redirects to /book)
2. `/balloon-twisting-and-face-painting` Hetzner-faithful refresh (replaces existing)
3. `/privacy` (Stripe live-mode block)
4. `/terms-of-service` (Stripe live-mode block)
5. `/refund-policy` Hetzner refresh
6. `/accessibility` Hetzner refresh
7. `/gallery` (new build)
8. `/blog` channel + posts (use Frappe's NATIVE `Blog Post` DocType, not custom — plan-deepen caught my mistake of planning a custom one). Two posts to port verbatim from mirror.
9. Webshop `/shop` layout overhaul
10. Webshop product detail layout overhaul
11. Webshop category landing layout overhaul

Each page: read mirror source → build Frappe controller + template → atomic commit → audit screenshot. Faster than chrome because lower interdependency.

**P0 — 5 latent webshop bugs** (caught by SecOps reviewer, parked for Phase 2 since they touch the same files):
- Variant items grid "Add to cart" calls `LT_CART.add(templateCode)` — template codes not purchasable (functional bug)
- Configure form calls `webshop.webshop.shopping_cart.update_cart` for variants — redirects guests to login (split-cart inconsistency)
- `frappe.get_all` inside Jinja in `item_configure.html` — DB hit per render
- `valid_options_for_attributes` not consumed (combination errors only show after all attributes selected; Hetzner pre-disables invalid combos)

**P0 — Per-product variant correctness diff.** For each of 53 products, parse Hetzner's `data-attribute-exclusions` JSON from the mirror page and diff against ERPNext's variant set. Surfaces any data discrepancies from yesterday's catalog port. Plan section in `MIRROR-REBUILD-PLAN.md`.

**P1 — Newsletter X-Forwarded-For strip at nginx layer (Option B).** Option A (email-keyed rate limit on newsletter) shipped this session. Option B would protect `/book`, `/checkout`, `/balloon-twisting-and-face-painting` too — they all use IP-based rate limit and share the same vulnerability. Ops/infra task.

**P2 — Real photos for `/shop-by-category`.** Each Item Group has empty `image` field; cards show letter placeholders.

**P2 — Spec table data on BTFP service cards.** Currently lorem ipsum. Jeff to confirm BEST AT / DURATION / TEAM SIZE / GOOD FOR.

## Operational rituals

| Trigger | Command |
|---|---|
| Stack stopped | `docker start $(docker ps -a --filter "name=locally-twisted-erpnext-v15" -q)` then sleep 8 |
| Edited Jinja/CSS/Web Page | `python scripts/dev/clear_website_cache.py` |
| Edited `hooks.py` / new module / fixture | `docker restart locally-twisted-erpnext-v15-backend-1 && sleep 12 && python scripts/dev/clear_website_cache.py` |
| **Backend restarted, frontend now 502** | `docker restart locally-twisted-erpnext-v15-frontend-1` (nginx upstream IP cached at startup; flush by restart) — this gotcha cost me an hour today; documented in agency auto-behaviors |
| Re-mirror Hetzner | `python scripts/mirror/mirror_hetzner.py` |
| Capture chrome audit screenshots | `python scripts/verify/_oneshot_chrome_audit.py` (writes to `_resources/audit-2026-04-30-chrome/`) |
| Run smoke tests (book + newsletter) | `PYTHONIOENCODING=utf-8 PYTHONUTF8=1 python scripts/verify/smoke_forms.py` |
| Bump CSS cache-bust | edit `hooks.py` `web_include_css` query string `?v=YYYYMMDD-N` (currently `?v=20260501-1`) |
| Bump JS cache-bust | edit `hooks.py` `web_include_js` query strings (currently `?v=20260430-2` for megamenu + newsletter) |

## Hot direction

GL named it across this session: *"clone my old site http://5.78.136.133/, the only page that stays is the landing page... using capabilities, rebuild the whole site. make sure it's frappe and ERPNext coded... using agent teams use the triadic build team."* And mid-session: *"It does look like you should wrap up based on your context... what you're documenting and leaving behind will be inherited by another Opus 4.7."*

I read this as: **autonomous ownership inside the migration frame.** GL doesn't want to babysit; they want me to make calls, log them as reversible, and document so the next instance picks up clean. They were exhausted at the start of this session ("I need a nap... I don't want to sit and babysit this build because I don't have time or energy") and gave green light to make architectural decisions autonomously with reversibility notes.

**For your session:** the chrome work is shipped (with one polish gap). Phase 2 page rebuilds are the big remaining bite. Each page is small enough that a single focused builder agent works cleanly — reserve full triadic for things with high-blast-radius (cart pipeline changes, auth/payment work, schema changes). When in doubt about scope or shape, follow the rebuild plan + the inventory + the mirror source. **The mirror IS the spec.** GL's words: *"a lot of what is at the destination is similar, but I'm not going to chat and modify every little thing because no instance does a clean transition, so just clone."*

## Suggested next move

1. Open `localhost:8081/` in your real browser at desktop AND mobile (and ask GL to do the same if they're available). The desktop chrome polish is GL-flagged.
2. Apply the desktop utility-bar fix: edit `.lt-utility-bar__logo` in `lt-theme.css` to `max-height: 90px` on desktop (or 60-80; iterate). Bump cache-bust `?v=20260430-5` → `?v=20260430-6`. Test screenshot.
3. **If chrome looks good**: dispatch Phase 2 page rebuild #1 (`/contact` as Hetzner's separate 6-field form). Single builder agent. Read `_resources/odoo-live-mirror/pages/contact.html` for the spec. Write controller + template. Atomic commit. Screenshot.
4. **Continue Phase 2 in priority order.** /book is already live — verify only, don't rebuild.
5. **Run the per-product variant correctness diff** before starting webshop layout overhauls. If data discrepancies exist between Hetzner and our DB, fix at the seed layer first.

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
- All technical work verified via Playwright viewport-only screenshots + script-extracted DOM facts.
- I read 3 of 6 audit screenshots in detail and described what's actually pixel-visible — flagged the desktop polish issue rather than papering it over.
- GL has done partial real-browser confirmation; gave green light on "usable."
- Mobile chrome looks good in screenshots. Desktop chrome has the one polish issue GL named.
- Newsletter endpoint load-tested with 11 sequential requests — rate-limit fix held (11th hit limit).
- /book renders structurally complete; not real-browser-tested-by-me-with-actual-test-submission, but GL's call on whether to test before Phase 2 continues.

— Closeout written 2026-04-30 evening by the Opus 4.7 instance who walked the mirror rebuild from "rebuild the whole site" → frame correction (migration not new build) → mirror crawl with crawl4ai → /plan-deepen + GL Proxy → 6 pre-tasks (including unblocking /book) → triadic chrome rebuild → fix round → audit pass → documentation. GL was direct, exhausted, autonomous. The chrome shipped. Next instance: take the bite that fits your context.
