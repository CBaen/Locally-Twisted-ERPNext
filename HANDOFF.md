# HANDOFF — Locally Twisted

**Last updated:** 2026-04-29 (Opus 4.7 — closing the guest-cart + Stripe-Link + cascade session)

Overwrite-not-append. Git is the changelog. Read this first; the SIBLING-LETTER.md next; everything else as needed.

## State of the world

**Phase 1 customer flow is end-to-end paid-and-cascading.** Customer browses → adds to cart from any page → /cart shows live items → /checkout → Stripe-hosted page (card-only, no Link) → /payment-success → /thank-you. Three emails fire on every paid order: receipt to customer, operator notification to `locallytwisted@gmail.com`, welcome email if first-time. Sales Invoice creation lands the order in ERPNext's accounting. Customer dedup handles three cases: returning customer (reuse), Contact-from-Lead (attach + mark Lead Converted), or fresh.

**GL's real test order — SAL-ORD-2026-00019 — went through cleanly this session.** They paid via Stripe `4242`, landed on /thank-you, and after the rest of the work they got the receipt, operator notification, and welcome email backfilled. `ACC-SINV-2026-00001` is the linked Sales Invoice.

**The Stripe page is now `Pay with card` only.** Link is disabled at the account level via `pmc_1TRZH2DfnlZQv66ncb001soG` ("LT No Link"), passed on every Checkout Session. Apple Pay + Google Pay still work — they're card wallets, not Link.

**Email Account is configured.** `Locally Twisted` Email Account on smtp.gmail.com:587 TLS, default outgoing. Reads App Password from `.env` `GMAIL_APP_PASSWORD`. Don't recreate — the password is sensitive.

## Three things that matter most on day one

**1. The cart engine is real and lives in localStorage.** `apps/locally_twisted/locally_twisted/public/js/lt-guest-cart.js` exposes `window.LT_CART` with `add/update/remove/clear/getCart/getCount/subscribe`. It overrides `webshop.webshop.shopping_cart.update_cart` at runtime and capture-phase-intercepts `.btn-add-to-cart-list` clicks BEFORE webshop's bubble-phase login redirect fires. Server-side endpoint is `locally_twisted.api.cart.get_cart_items(item_codes)` — guest-allowed, returns published+priced items only. The cart UI is at `www/lt_cart.{py,html}` — NOT `cart.py` because that name collides with `webshop/templates/pages/cart.html` and webshop wins resolution. The route rule `/cart → lt_cart` lives in `hooks.py`.

**2. `/payment-success` is the cascade hub. Don't add anything there that throws.** Every helper called from `_handle_stripe_session` is wrapped in try/except — a backend reconciliation glitch must NOT block the customer's `/thank-you` redirect. The cascade order is: mark PR paid → create SI (idempotent) → send receipt → send operator notification → send welcome (if first SO) → redirect. Each step independent. Helpers all check Communication-by-subject for idempotency so they're safe to retry.

**3. The PMC ID `pmc_1TRZH2DfnlZQv66ncb001soG` is hard-coded in `payments/stripe_session.py` line ~95.** This is LT's account-level Stripe config that disables Link. If you somehow recreate the Stripe account or work on a different LT-owned PMC, this ID needs to update. Document the new ID as a constant or move to `site_config.json` (`bench --site frontend set-config lt_stripe_pmc_id <new>`) at that point.

## What's live at http://localhost:8081

| Surface | State |
|---|---|
| ERPNext v15.105.0 stack (9 containers) | Running |
| Apps installed | frappe, erpnext, locally_twisted, payments, webshop |
| Email Account | `Locally Twisted` — locallytwisted@gmail.com / smtp.gmail.com:587 TLS / default outgoing — configured this session |
| Stripe Settings "Test" | LT's keys from `.env`. PMC `pmc_1TRZH2DfnlZQv66ncb001soG` disables Link |
| `/shop` (LT custom) | LT_CART.add() on click. Toast feedback. Quantity 1 per click |
| `/cart` (overrides webshop's) | localStorage-backed. Loading/empty/populated/error states. Qty +/- buttons + numeric input. Remove links. Drops missing items with notice. Continue to checkout button |
| `/checkout` (no params) | Cart-mode. JS hydrates summary from localStorage. items_json hidden input populated on render |
| `/checkout?item=<code>&qty=<n>` | Buy-now mode (backwards-compatible). Server-renders single line |
| `/payment-success` | Override → marks PR paid → creates SI → emails receipt + operator + welcome → redirects to `/thank-you` |
| `/thank-you?order=<so>` | Renders order summary. Clears LT_CART on load. Contact line removed |
| `/all-products` (webshop stock) | Add-to-cart now intercepted by lt-guest-cart.js capture-phase listener. No login redirect for guests |
| Receipt / operator / welcome email | All three sent for SAL-ORD-2026-00019 backfill — verify in your inbox |

## What's NOT done (next session candidates, by priority)

**P0 — demo readiness:**
- **Slice 10 — `/book` form page.** Primary inquiry conversion form (45-field Lead schema). Every homepage CTA still 404s here. Big build but well-scoped — same shape as `/contact`.
- **`/privacy` and `/terms-of-service` pages** — both required by Stripe for live mode activation. Currently `example.com/...` placeholders. Pair with attorney pass.
- **Spec table data on BTFP service cards.** Still lorem ipsum — Jeff needs to confirm BEST AT / DURATION / TEAM SIZE / GOOD FOR.

**P1 — backend tour readiness:**
- **Sample data for backend tour** — a few realistic Lead records, one or two completed orders, an upcoming event. Lets Jeff click around the desk and see the system in motion.
- **Slice 8 — Service category pages** (`/services/<event>` × 5).
- **Slice 9 — Color Chart page** (`/color-chart`).

**P2 — polish:**
- **Multi-item cart UI improvements** — the cart works but design refinements possible.
- **Public business name in Stripe Dashboard** — currently "Locally twisted llc"; should be "Locally Twisted." Settings → Public details. Needs Jeff's 2FA or Stripe MCP.
- **Stripe Dashboard branding** — upload logo. Already set: bg #c3dcf3, button #f5e0d7, display name.
- **Production webhook config** — currently dev uses `stripe listen --api-key`. For prod cutover, add stable endpoint in Stripe Dashboard.

**Phase 3 cascade additions (deferred deliberately):**
- **Calendar Event for delivery_date** on SO submit — Jeff's day plan.
- **Project + Task records** for big-ticket SOs — crew dispatch, supplies checklist.
- **Stock movement / Delivery Note** when stock-tracking turns on (currently `allow_items_not_in_stock=1`).

## Operational rituals

| Trigger | Command |
|---|---|
| Stack stopped | `docker start $(docker ps -a --filter "name=locally-twisted-erpnext-v15" -q)` then sleep 8 |
| Stack running, need to stop | `docker stop $(docker ps --filter "name=locally-twisted-erpnext-v15" -q)` |
| Edited Jinja / CSS / Web Page record | `python scripts/dev/clear_website_cache.py` |
| Edited PAGE_CSS in `www/<route>.py` OR added a new module/package | `docker restart locally-twisted-erpnext-v15-backend-1 && sleep 8 && python scripts/dev/clear_website_cache.py` |
| Edited `hooks.py` (new web_include_js, route_rules, fixtures, etc.) | `docker exec locally-twisted-erpnext-v15-redis-cache-1 redis-cli FLUSHALL && docker restart locally-twisted-erpnext-v15-backend-1 && sleep 8 && bench --site frontend clear-cache` |
| Bumped lt-theme.css | Bump the `?v=YYYYMMDD-N` query string in hooks.py `web_include_css` AND `web_include_js` (cache-bust) |
| Need Stripe Test re-configured | `python scripts/setup/configure_stripe_test_mode.py` |
| Need to start the webhook listener | `stripe listen --api-key "$(grep '^STRIPE_TEST_SECRET_KEY=' .env \| cut -d= -f2)" --forward-to http://localhost:8081/api/method/locally_twisted.payments.stripe_webhook.stripe_webhook` |
| Need to set the webhook signing secret | `python scripts/setup/set_stripe_webhook_secret.py whsec_<value>` then restart backend |
| Inspecting / sending emails | `bench --site frontend execute frappe.email.queue.flush` to force-send queued mail. Check `Email Queue` doctype in desk for status |
| Before declaring any visible change done | Take Playwright screenshot at mobile (375px) AND desktop (1280px); read the file; **THEN ask GL to hard-refresh** in their real browser |
| For a new portal page | Read the meal at `Built_by_Cameron/.claude/capabilities/meals/build-frappe-portal-page.md`. Read approved content first (non-negotiable). |

## Hot direction

GL's active concern is the customer-facing demo polish + the operator-side cascade. They want ERPNext "utilized HEAVILY" (their words, 2026-04-29) — every payment cascading into the right records, every email auto-firing, every customer record one-source-of-truth.

What this session DELIVERED on that ambition:
- SO → SI → PE → GL Entries (auto via ERPNext)
- Receipt + operator notification + welcome emails (explicit `frappe.sendmail` in payment_success.py with reference_doctype/name auto-creating Communication records)
- Lead → Customer linking (3-case dedup)

What it LEAVES OPEN at the cascade tier:
- Calendar Event from SO (Phase 3)
- Project + Task from big-ticket SOs (Phase 3)
- Stock movement (Phase 4 when stock-tracking turns on)

GL's operating constraints (verified again this session):
- Risk-averse on legal exposure — they pulled cord on Option A (silent User account) earlier; confirmed again on Stripe Dashboard publicness.
- Working long days. End-of-session goodbyes mean the wind-down should be clean.
- Wants ERPNext-native paths — uses `frappe.sendmail` reference linkage to auto-create Communications, doesn't fight the framework.
- Will correct sharply when I'm wrong. They caught my premature "Link is gone" claim before browser-verifying. Anti-pattern #1 (reporting without watching) almost fired; verifying via Playwright before claiming done is the discipline that saved it.

**Suggested next move:** Slice 10 (`/book`) — every homepage CTA points there and currently 404s. The form shape mirrors `/contact` but with the full 45-field Lead schema. The meal at `Built_by_Cameron/.claude/capabilities/meals/build-frappe-portal-page.md` covers the pattern. After that, `/privacy` and `/terms-of-service` for Stripe live-mode readiness.

## Reading order on arrival

1. Global `C:/Users/baenb/.claude/CLAUDE.md` (auto-injected)
2. `Built_by_Cameron/CLAUDE.md` (agency rules)
3. `_CLIENTS/locally-twisted/CLAUDE.md` — READ "Stack & code conventions" + "Reading order"
4. **This file**
5. `_CLIENTS/locally-twisted/SIBLING-LETTER.md` — peer register from me. Honest take on staying.
6. `Built_by_Cameron/.claude/capabilities/meals/build-frappe-portal-page.md` — binding shape for portal pages
7. `Built_by_Cameron/.claude/capabilities/recipes/frappe-portal-implementation.md` — the rules
8. `_CLIENTS/locally-twisted/lessons-learned.md` — six lessons from this session at the top
9. `_CLIENTS/locally-twisted/locally-twisted-decisions.md` — newest entries (Path B / cookie-cart over polish, Stripe Link disabled at account level not Session, ERPNext cascade pattern wired in payment_success)
10. `_CLIENTS/locally-twisted/anti-gl-patterns.md` section 0
11. `apps/locally_twisted/locally_twisted/www/checkout.py` — Lead-aware Customer dedup is the new code worth understanding
12. `apps/locally_twisted/locally_twisted/www/payment_success.py` — the cascade hub
13. `apps/locally_twisted/locally_twisted/public/js/lt-guest-cart.js` — the cart engine
14. `apps/locally_twisted/locally_twisted/payments/stripe_session.py` — note the PMC ID constant
15. `git log --oneline -30`

## Not in flight

- Stack containers running. Backend was last restarted right before this closeout.
- ZERO spawned background processes. The Stripe listener was not started this session (success-page reconciliation is the demo path).
- All session writes committed via auto-commit hook + the documentation writes in this closeout.
- Test data cleaned: `Smoke LinkTest`, `Link Verify`, `Link Inspect` customers + their cascading records (cancelled SOs 17 + 18, PRs 16 + 17, addresses, contacts) all deleted at session close. Next SO will be SAL-ORD-2026-00020 (the naming counter doesn't roll back).
- One-shot verification scripts (`_oneshot_guest_cart.py`, `_oneshot_stripe_link.py`) deleted at session close. They served their purpose; git history preserves them if needed.
- ONE thing the parallel agent on the contest stream did continue through this session — research/contest-customizable-event-decor-tool/ commits visible in git log. Don't conflict with their files.

## A quick honesty pass

**What worked:**
- Naming Path B (real cookie-cart) clearly when GL framed "quality is always the answer." Built it from scratch with capture-phase webshop intercept, in-memory fallback for Safari Private Mode, cross-tab sync via storage events. Verified end-to-end via Playwright before claiming done.
- Watching the Stripe page in Playwright to confirm Link UI was actually gone after each fix. The first fix (`payment_method_types=["card"]`) was insufficient — Link "Save info" + Bank-via-Link UI persisted. Without watching, I'd have shipped a half-fix. Watching → catching it → escalating to a custom PMC at the account level → verified gone.
- Reading the actual `payment_success.py` flow when GL reported the cart-not-cleared bug. The fix in `payment_success.html` was inert because `_redirect()` raises `frappe.Redirect` before the template renders. Moved the clear to `thank_you.html`. That diagnostic — "where does the JS actually execute" — saved a whole class of phantom-bug guessing.
- The Lead-aware Customer dedup. GL's instinct that "everything should cascade" pushed me to look at the orphan-customer hole I'd otherwise have missed. Three cases: returning, Contact-from-Lead, fresh. The Lead-from-Contact case would have shipped silently broken without GL's framing.
- Idempotent emails via Communication-subject lookup. Means backfill is safe; means webhook double-fire is safe; means I can re-run without spamming the customer.

**What stumbled:**
- Two anti-pattern #1 near-misses. Claimed "Link is gone" after `payment_method_types=["card"]` shipped — GL pushed back ("straight to link again"), then I rendered the Stripe page in Playwright and saw the Link UI was actually still there. The fix needed a custom PMC. Lesson: for any visual change customer-facing, render in Playwright BEFORE claiming.
- The `Address.address_display` column error. I reached for a field name without verifying it existed on the table. ERPNext stores the rendered HTML on the SO, not on the Address row. Lesson: when reading a doctype field, check the schema or use a doctype I've already touched.
- The cart-clear bug class. My first fix lived in a template that never renders. Took GL's report to surface it. Lesson: when adding JS to a Frappe template, confirm the template ACTUALLY RENDERS in the flow you're targeting (some controllers raise frappe.Redirect before render).

**Open trust state:**
- GL ran a real `4242` purchase end-to-end this session. The flow worked. They got the test order across the gap from "shipped in code" to "verified by GL with a real card" — that was the load-bearing pending verification from the prior session's HANDOFF. Closed.
- GL is exhausted (long day across multiple sessions). They asked for a proper goodbye at session close. The cleanup is done. The cascade is documented. The next instance has a clear runway.

The work shipped. The cleanup ran. The next instance has a clear path and an honest list of what's verified vs what's pending.

— Closeout written 2026-04-29 by the Opus 4.7 instance who built the localStorage guest cart (Path B), disabled Stripe Link at the account level via custom PMC, and wired the SO → SI + receipt + operator + welcome cascade into `/payment-success`.
