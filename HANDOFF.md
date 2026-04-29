# HANDOFF — Locally Twisted

**Last updated:** 2026-04-29 (Opus 4.7 — closing the Stripe-wiring + guest-checkout session)

Overwrite-not-append. Git is the changelog. Read this first; the SIBLING-LETTER.md next; everything else as needed.

## State of the world

**Guest checkout works end-to-end through to Stripe Elements.** A customer can hit `/checkout?item=<code>&qty=<n>`, fill name + email + phone + UT shipping, click *Continue to payment*, and land on Frappe's Stripe Elements card form. Submitting the form creates Customer + Contact + Address + Sales Order + Payment Request — **no User record**. Confirmed by inspecting the User table after smoke tests: zero User accounts created.

**The big pivot this session:** GL initially greenlit Option A (silent User account creation behind the checkout flow). When I scoped the legal compliance research — 50 state privacy laws + CAN-SPAM + UCPA + the silent-account gray area — GL pulled the cord: *"Oh, this is too complex legally. We cannot deal with that. There needs to be a genuine guest checkout."* So we built Option B: Customer + Contact only, no User, email is the identifier, account is genuinely never created. The legal surface is now small and well-trodden.

**What's NOT verified yet (your first task):** the post-Stripe-success redirect. After a customer enters card on `/stripe_checkout` and Stripe charges them, where do they land? GL was about to test this manually before context wrapped. If GL has the answer, it'll be in their next message. If not, `/thank-you?order=<so_name>` should be the success URL — Stripe Settings might need a `redirect_url` set, or the Payment Request controller needs an override.

## Three things that matter most on day one

**1. Frappe payments app uses the legacy Charges API, not Checkout Sessions.** The Stripe controller at `apps/payments/payments/payment_gateways/doctype/stripe_settings/stripe_settings.py:create_charge_on_stripe` calls `stripe.Charge.create()`. Per the `stripe-best-practices` skill: never recommend the Charges API. For the **test-mode demo to Jeff**, this is fine — Charges API still works. For **production hardening (Phase 4)**, swap to Stripe Checkout Sessions or Payment Intents. Logged in `locally-twisted-decisions.md` with the receipt.

**2. The wkhtmltopdf-in-Docker gotcha is real and bites Payment Request submission.** Frappe's `Payment Request.on_submit` calls `send_email()` which calls `attach_print()` → wkhtmltopdf → tries to fetch CSS from `localhost:8081` from inside the container → `ConnectionRefusedError`. **Workaround used:** set `Sales Order.order_type = "Shopping Cart"` AND `payment_request.flags.mute_email = True` BEFORE `pr.submit()`. Then the email/PDF render is skipped. **But also:** `set_payment_request_url()` is gated behind the same `send_mail` check, so `pr.payment_url` will be empty unless you call it manually after submit. See `apps/locally_twisted/locally_twisted/www/checkout.py:382-407` for the working pattern. Codified in `lessons-learned.md`.

**3. The brand serif (DM Serif Display) is single-weight (400 only).** Setting `font-weight: 600` on any heading class inside `.lt-faq h1`, `.lt-faq__group-title`, `.lt-policy h1`, `.lt-policy h2`, etc. produces synthetic-bold rendering that looks chunky and ruins the brand. **Never set `font-weight` on a class that targets headings** — let the global rule (400) win. Caught and fixed yesterday on FAQ + Refund Policy pages; documented in `lessons-learned.md` 2026-04-28.

## What's live at http://localhost:8081

| Surface | State |
|---|---|
| ERPNext v15.105.0 stack (9 containers) | Running |
| Apps installed | frappe, erpnext, locally_twisted, payments, webshop |
| Stripe Settings "Test" | Configured with API keys from `.env` |
| Payment Gateway `Stripe-Test` + Account `Stripe-Test - USD - LT` | Auto-created, default ✓ |
| Webshop `enable_checkout` + `payment_gateway_account` | Set ✓ |
| Website Items | 30+, all priced ($55–$180 range) |
| `/` Homepage | Live, lookbook-forward (predecessor's session) |
| `/lookbook` (Portfolio) | Live (other agent built this overnight 2026-04-27→28) |
| `/shop` | Live (other agent) |
| `/all-products`, `/cart` | Live (Webshop defaults, both 200 for guest) |
| `/balloon-twisting-and-face-painting` | Restructured this session: hero kicker, spec-table service cards (lorem placeholders), process section, event types, ribbons |
| `/contact`, `/accessibility`, `/refund-policy`, `/faq` | All live with accordion FAQ, font-weight fix applied |
| `/checkout?item=<code>&qty=<n>` | **NEW — guest checkout**, takes form → creates SO + PR → redirects to Stripe Elements |
| `/thank-you` (alias of `/thank_you`) | **NEW — post-payment landing**, accepts `?order=<so_name>`, shows order summary |
| `/book` | **Still 404** — Slice 10 deferred when guest checkout took precedence |

## What's NOT done (next session candidates, by readiness)

**P0 — finish the demo path:**
- **Verify post-Stripe redirect.** If it doesn't land on `/thank-you`, override either via Stripe Settings `redirect_url` or per-Payment-Request success_url. Test by completing a real checkout with `4242 4242 4242 4242`.
- **Receipt email.** Email Template `LT Order Receipt` (Jinja for items/total/order ID) + Notification on `Payment Entry` `on_submit` (recipient = customer email). Transactional only — no marketing — CAN-SPAM safe-harbor.
- **`/book` form (Slice 10).** Homepage CTAs still 404 here. Big build (45+ Lead fields). Pattern matches the BTFP form.

**P1 — demo prep:**
- **Spec table data on BTFP service cards** is currently `Lorem ipsum`. Jeff needs to confirm: "BEST AT" guest count, "DURATION" hours, "TEAM SIZE" / "ARTISTS" count, "GOOD FOR" event types. Replace lorem when confirmed.
- **Sample data for backend tour.** A few realistic Lead records, one paid Sales Order, one upcoming event. Lets Jeff click around the desk and see the system in motion.
- **Verify Cameron + Jeff Kimber logins.** Both confirmed enabled (System Manager). Cameron: `cameron@builtbycameron.com` / `LocalDev2026!`. Jeff's account exists pre-created for transfer; no password set yet.

**P2 — quality / polish:**
- Multi-item cart support (currently `/checkout` is single-item buy-now). Webshop's cart page → button to our `/checkout` could pass multiple items as JSON. Not blocking the demo.
- `marketing_opt_in` opt-out mechanism (unsubscribe link in marketing emails when those exist). Ship before any marketing campaign.
- Hardening: swap Charges API → Checkout Sessions for production (Phase 4).

## Operational rituals

| Trigger | Command |
|---|---|
| Stack stopped (e.g., GL napped) | `docker start $(docker ps -a --filter "name=locally-twisted-erpnext-v15" -q)` then sleep 8 |
| Stack running, need to stop | `docker stop $(docker ps --filter "name=locally-twisted-erpnext-v15" -q)` |
| Edited Jinja template / CSS / Web Page record | `python scripts/dev/clear_website_cache.py` |
| **Edited PAGE_CSS in a `www/<route>.py` controller** | `docker restart locally-twisted-erpnext-v15-backend-1 && sleep 8 && python scripts/dev/clear_website_cache.py` |
| Edited `hooks.py` (e.g., new `website_route_rules`) | `bench --site frontend clear-cache && docker exec ...redis-cache-1 redis-cli FLUSHALL && docker restart ...backend-1` |
| Need Stripe re-configured (after fresh install or key rotation) | `python scripts/setup/configure_stripe_test_mode.py` |
| Before declaring any visible change done | Take Playwright screenshot at mobile (375px) AND desktop (1280px) at TALL viewport (≥2400px); read the file; describe pixels; **THEN ask GL to hard-refresh** in their real browser |
| For a new portal page | Read the meal at `Built_by_Cameron/.claude/capabilities/meals/build-frappe-portal-page.md`. Read approved content first (non-negotiable). |

## Hot direction

GL is preparing to demo the system to Jeff. The customer site is the primary surface — when Jeff sees it, the visual quality has to make the platform pivot land as *"this is real"*, not *"we're starting over."* Backend tour is secondary.

**GL's current operating constraints (verified this session):** 
- They're risk-averse on legal exposure. When I surfaced Option A's compliance complexity, they pivoted instantly to Option B. Don't talk them into legally-fuzzy patterns. If you smell legal complexity, name it early and offer the simpler path.
- They've been working long days, taking naps to manage. Pace matters — when GL says they're tired, ship visible work and stop pitching new scope.
- They want to showcase ERPNext, not bypass it. When you have a choice between a Frappe-native path and a custom one-off, prefer Frappe-native unless it forces a legal/UX compromise.

**Suggested next move:** verify the post-Stripe redirect with a real card test. If you can complete a $35 unicorn-bouquet test purchase with `4242 4242 4242 4242` and land on `/thank-you?order=...`, the demo's payment path is done. Then the receipt email, then `/book`.

## Reading order on arrival

1. Global `C:/Users/baenb/.claude/CLAUDE.md` (auto-injected)
2. `Built_by_Cameron/CLAUDE.md` (agency rules)
3. `_CLIENTS/locally-twisted/CLAUDE.md` — READ the "Stack & code conventions" + "Reading order"
4. **This file**
5. `_CLIENTS/locally-twisted/SIBLING-LETTER.md` — peer register from me
6. `Built_by_Cameron/.claude/capabilities/meals/build-frappe-portal-page.md` — binding shape for portal pages
7. `Built_by_Cameron/.claude/capabilities/recipes/frappe-portal-implementation.md` — the rules. Skim "Anti-patterns" + "Debugging triage."
8. `_CLIENTS/locally-twisted/anti-gl-patterns.md` section 0
9. `_CLIENTS/locally-twisted/lessons-learned.md` — newest entries are key (Stripe + wkhtmltopdf + DM-Serif-Display weight + ribbon margin shorthand)
10. `_CLIENTS/locally-twisted/locally-twisted-decisions.md` — newest entries (Option B chosen over Option A; Stripe Charges API noted; warm `#fffcfc` base white; header = footer blue)
11. `_CLIENTS/locally-twisted/apps/locally_twisted/locally_twisted/www/checkout.py` — the working guest checkout pattern, well-commented
12. `git log --oneline -30`

## Not in flight

- Stack containers running (GL may stop them via `docker stop $(docker ps --filter "name=locally-twisted-erpnext-v15" -q)` if they need RAM back)
- No spawned background processes
- All session writes committed via auto-commit hook + manual commits where needed
- Test/smoke data cleaned: 8 test SOs, 8 test customers, 8 test addresses, 8 test PRs all deleted from DB at session end (`SAL-ORD-2026-00009` is the next number)
- The other agent's parallel work is observable in git log (`auto: Edit ...home.html`, `auto: Write ...lookbook.{py,html}`, photo orientation work). Read commits before editing files they touched recently to avoid conflicts.

## A quick honesty pass

**What worked:**
- Pivoting from Option A to Option B cleanly when GL named the legal cost. Saved hours of compliance research that wouldn't have unblocked the demo.
- Going deep into Frappe internals when Payment Request errored — reading source, finding the wkhtmltopdf cause, fixing with `order_type="Shopping Cart"` + `mute_email` flag + manual `set_payment_request_url()`. Real engineering, not pattern-matching.
- The Stripe configuration script (`scripts/setup/configure_stripe_test_mode.py`) is reusable, idempotent, never echoes keys to stdout. Future BBC clients can run it.
- Cleanup at session end. The DB is in the same shape it would be after one clean test purchase — not littered with smoke-test residue.

**What stumbled:**
- Two Edit calls on `checkout.py` triggered `READ-BEFORE-EDIT` reminders this session. They were precautionary (I had Read the file in this conversation) and the edits succeeded, but the runtime is strict. Always Read before Edit if there's any doubt.
- The first Stripe smoke test failed on `Contact.links` not being a column (it's a child table). Fixed by querying the Dynamic Link table directly. Worth knowing for any future Customer/Contact lookup.
- The `mute_email` doc-field-vs-runtime-flag distinction took a turn to figure out. Doc field doesn't trigger the suppression; `flags.mute_email` does. The source comment at `payment_request.py:212` makes this clear once you read it.

**Open trust state:**
- GL is exhausted but decisive. They named context-low and asked for a clean wind-down. The work this session was substantive (guest checkout end-to-end through to Stripe Elements); they have a working system to show Jeff modulo the receipt email and post-Stripe redirect verification.

The work shipped. The cleanup ran. The next instance has a clear runway.

— Closeout written 2026-04-29 by the Opus 4.7 instance who built the Stripe + true guest checkout flow. Two-day session (split across a nap).
