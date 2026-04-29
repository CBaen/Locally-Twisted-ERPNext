# HANDOFF — Locally Twisted

**Last updated:** 2026-04-29 (Opus 4.7 — closing the Stripe Charges→Checkout Sessions migration session, second session of the day after a long break)

Overwrite-not-append. Git is the changelog. Read this first; the SIBLING-LETTER.md next; everything else as needed.

## State of the world

**The Stripe customer-facing flow is rebuilt on the modern Stripe API.** Customers no longer hit Frappe's bundled card form. They go: `/checkout?item=...&qty=...` (LT-branded, two-column with persistent order summary) → submit → redirected to `checkout.stripe.com/c/pay/cs_test_...` (Stripe-hosted, dynamic payment methods, real production UI) → after payment → `/payment-success?session_id=...` (our override resolves the session, marks PR Paid, redirects) → `/thank-you?order=SAL-ORD-...`.

The `/payment-success` 403 GL reported at session start (caused by Frappe payments app upstream URL bug + guest-perm 403 on Payment Request reads) is fixed via a route override in our app — `website_route_rules` claims `/payment-success` for our `www/payment_success.py`.

**What's NOT verified:** the real `4242` test purchase by GL. Every check I ran was curl + Playwright + simulated session_id. The actual customer experience — fill form → Stripe page → enter card → land on `/thank-you` → SO marked Paid — is the next instance's first task to confirm with GL. If anything's off, the success-page reconciliation logic (`www/payment_success.py:_handle_stripe_session`) is where the bug will be.

## Three things that matter most on day one

**1. The Stripe CLI listener is bound to LT's account via `--api-key`, not via `stripe login`.** Jeff's phone is needed for LT's Stripe Dashboard 2FA, and Jeff isn't always available. So: don't try `stripe login --project-name lt-test` — it'll hang waiting for a 2FA we can't complete. Instead use the `--api-key` workaround (LT's secret key is already in `.env`):

```bash
export STRIPE_LT_KEY=$(grep '^STRIPE_TEST_SECRET_KEY=' .env | sed 's/^STRIPE_TEST_SECRET_KEY=//')
stripe listen --api-key "$STRIPE_LT_KEY" --forward-to http://localhost:8081/api/method/locally_twisted.payments.stripe_webhook.stripe_webhook
```

Listener prints `whsec_...` on the second line. Pass to:
```bash
python scripts/setup/set_stripe_webhook_secret.py whsec_<value>
docker restart locally-twisted-erpnext-v15-backend-1
```

The secret rotates each restart — that's fine for dev. The webhook is OPTIONAL for the demo flow (success-page reconciliation already marks PR paid sync); it's the safety net for browser-closed-before-redirect.

Codified at `lessons-learned.md` 2026-04-29 entry "Stripe CLI's `--api-key` flag bypasses login".

**2. ERPNext's Stripe auth (`.env` keys → Stripe Settings doctype) is SEPARATE from the Stripe CLI's stored auth.** GL pointed this out twice this session because I kept conflating them. The keys in `.env` ARE LT's; they're correctly populated in Stripe Settings 'Test'. The Stripe CLI's stored auth (visible via `stripe config --list`) is BBC's account — that's irrelevant for the runtime payment flow. Don't ask GL to "redo the authentication" — the .env keys are already that authentication. Verify what's in place before asking for credentials. See `lessons-learned.md` 2026-04-29 entry "I had it backwards".

**3. Frappe payments app (`apps/payments/`) is bind-mounted from gitignored upstream — never modify it.** It has a real upstream URL bug at `stripe_settings.py:272` (appends `?redirect_to=None` even when None) and ships a custom card form (`/stripe_checkout`) that uses the legacy Charges API. We work AROUND both, never edit upstream. The pattern is: override Frappe routes (`website_route_rules`) and bypass Frappe's `pr.payment_url` (we hand customers a `checkout.stripe.com` URL we built ourselves). See agency-tier `Built_by_Cameron/built-by-cameron-decisions.md` 2026-04-29 entry "Stripe payments standard for ALL BBC clients on Frappe".

## What's live at http://localhost:8081

| Surface | State |
|---|---|
| ERPNext v15.105.0 stack (9 containers) | Running |
| Apps installed | frappe, erpnext, locally_twisted, payments, webshop |
| Stripe Settings "Test" | Configured with LT's API keys from `.env` |
| `/checkout?item=<code>&qty=<n>` | **NEW two-column layout** — form on left, sticky order summary on right (item thumbnail + line + total + "Secure payment" notice). Mobile: summary stacks above form. Submit → creates SO + PR → redirects to Stripe-hosted Checkout |
| `/payment-success` | **OVERRIDDEN by our app.** Handles `?session_id=cs_test_...` (modern) and `?doctype=Payment%20Request&docname=...` (legacy). Verifies payment via Stripe API, marks PR paid, redirects to `/thank-you?order=<so>`. Registered via `website_route_rules` in `hooks.py` |
| `/api/method/locally_twisted.payments.stripe_webhook.stripe_webhook` | Live, signature-verified, idempotent. Reads secret from `frappe.conf.get('stripe_webhook_signing_secret')` |
| `/thank-you?order=<so>` | Renders order summary (no perms-elevation; degrades to generic page if SO not readable as guest) |
| `/`, `/lookbook`, `/shop`, `/all-products`, `/cart`, `/balloon-twisting-and-face-painting`, `/contact`, `/accessibility`, `/refund-policy`, `/faq` | Live (prior session work) |
| `/book` | **Still 404** — Slice 10 deferred, primary inquiry conversion path still missing |
| `/privacy`, `/terms-of-service` | Not built yet — required by Stripe for live mode (currently `example.com/...` placeholders in Stripe Dashboard). Queue P1. |

## What's NOT done (next session candidates, by priority)

**P0 — finish demo path / verify what shipped:**
- **Real `4242` test purchase end-to-end.** Confirm the Stripe Checkout Session migration actually works in a real customer flow. If it lands cleanly, write the lessons-learned line about the working flow + remove this item from queue.
- **Receipt email (transactional only).** Email Template `LT Order Receipt` (Jinja for items/total/order ID) + Notification on Payment Entry `on_submit`. CAN-SPAM safe-harbor (transactional only, no marketing). Watch for the same wkhtmltopdf-in-Docker pitfall the previous instance hit on Payment Request — receipt emails will trigger PDF rendering by default.
- **Slice 10 — `/book` form page.** Primary inquiry conversion form (45-field Lead schema). Every homepage CTA still 404s here. Big build.

**P1 — demo prep / launch readiness:**
- **Spec table data on BTFP service cards** still lorem ipsum — Jeff needs to confirm BEST AT / DURATION / TEAM SIZE / GOOD FOR.
- **Sample data for backend tour** — a few realistic Lead records, one paid SO, one upcoming event for Jeff's desk demo.
- **`/privacy` and `/terms-of-service` pages** — both required by Stripe for live mode activation, both currently `example.com/...` placeholders in Stripe Dashboard. Pair with attorney pass.
- **Public business name rename** in LT's Stripe Dashboard ("Locally twisted llc" → "Locally Twisted") — Settings → Public details → Public business name. Needs Jeff for 2FA when he's reachable.
- **Stripe Dashboard branding** — upload LT logo + brand color (teal `#107373` or whatever the SCSS calls primary). Applies instantly to all future Checkout Sessions. Also Jeff's-phone-blocked.

**P2 — polish / production hardening:**
- Multi-item cart support (currently `/checkout` is single-item buy-now). Webshop's `/cart` would need a "Checkout via custom flow" button that POSTs item list to our `submit_guest_order`.
- Production webhook: configure stable endpoint in Stripe Dashboard (vs. the `stripe listen` approach used in dev). Local listener bypass via `--api-key` is dev-only.
- `marketing_opt_in` opt-out mechanism (unsubscribe link) before any marketing campaign.

## Operational rituals

| Trigger | Command |
|---|---|
| Stack stopped (e.g., GL napped) | `docker start $(docker ps -a --filter "name=locally-twisted-erpnext-v15" -q)` then sleep 8 |
| Stack running, need to stop | `docker stop $(docker ps --filter "name=locally-twisted-erpnext-v15" -q)` |
| Edited Jinja template / CSS / Web Page record | `python scripts/dev/clear_website_cache.py` |
| Edited PAGE_CSS in a `www/<route>.py` controller OR added a new module / package in our app | `docker restart locally-twisted-erpnext-v15-backend-1 && sleep 8 && python scripts/dev/clear_website_cache.py` |
| Edited `hooks.py` (e.g., new `website_route_rules`) | `bench --site frontend clear-cache && docker exec ...redis-cache-1 redis-cli FLUSHALL && docker restart ...backend-1` |
| Need Stripe Test re-configured (after fresh install or key rotation) | `python scripts/setup/configure_stripe_test_mode.py` |
| Need to start the webhook listener | See "Three things that matter most" #1 above. Bypass `stripe login` via `--api-key`. |
| Need to set the webhook signing secret | `python scripts/setup/set_stripe_webhook_secret.py whsec_<value>` then restart backend |
| Before declaring any visible change done | Take Playwright screenshot at mobile (375px) AND desktop (1280px); read the file; describe pixels; **THEN ask GL to hard-refresh** in their real browser |
| For a new portal page | Read the meal at `Built_by_Cameron/.claude/capabilities/meals/build-frappe-portal-page.md`. Read approved content first (non-negotiable). |

## Hot direction

GL is preparing for Jeff's demo. The customer-facing payment flow being polished + recognizably-Stripe is the load-bearing piece — when Jeff clicks through a test purchase, his expression has to register *"this is real."* The work this session moved that from "embarrassing Frappe form" to "Stripe-hosted checkout with dynamic payment methods." Whether the full flow lands cleanly is GL's first task on resume.

**GL's current operating constraints (verified this session):**
- Risk-averse on legal exposure. They pulled the cord on Option A (silent User account) the moment the prior instance scoped 50-state legal research; same instinct will apply elsewhere. Surface legal complexity early; offer the simpler path.
- Working long days. When GL says context is low, ship the wind-down clean: clean up, write good docs, don't squeeze more work in.
- Wants ERPNext-native paths when there's a choice. We chose to keep the Sales Order + Payment Request flow as-is (auditable record) and only swap the redirect URL — rather than building a custom Stripe-only flow that bypassed ERPNext entirely. The agency rule "work WITHIN Frappe" still applies.
- Will correct misreads quickly and decisively. If you assume something about credentials, accounts, or config that GL has already set up, expect a sharp correction. Anti-pattern #5 is real here: don't make GL prove things they've done. Verify state first (read `.env`, run `stripe config --list`, query Stripe Settings) before asking GL.

**Suggested next move:** open in browser → `http://localhost:8081/checkout?item=number-balloon-columns&qty=1` → fill form → click Continue to payment → enter `4242 4242 4242 4242` → confirm landing on `/thank-you?order=SAL-ORD-...`. If the SO shows Paid in desk after, write the lessons-learned line and remove the P0 verify item from queue. Then receipt email. Then `/book` (Slice 10).

## Reading order on arrival

1. Global `C:/Users/baenb/.claude/CLAUDE.md` (auto-injected)
2. `Built_by_Cameron/CLAUDE.md` (agency rules)
3. `_CLIENTS/locally-twisted/CLAUDE.md` — READ the "Stack & code conventions" + "Reading order"
4. **This file**
5. `_CLIENTS/locally-twisted/SIBLING-LETTER.md` — peer register from me. Honest take on staying.
6. `Built_by_Cameron/.claude/capabilities/meals/build-frappe-portal-page.md` — binding shape for portal pages
7. `Built_by_Cameron/.claude/capabilities/recipes/frappe-portal-implementation.md` — the rules
8. `Built_by_Cameron/.claude/capabilities/kitchen/2026-04-29-stripe-checkout-sessions-for-frappe.md` — full Stripe pattern from this session (kitchen note awaiting promotion to recipe on second client use)
9. `_CLIENTS/locally-twisted/anti-gl-patterns.md` section 0
10. `_CLIENTS/locally-twisted/lessons-learned.md` — newest entries are the Stripe migration receipts (six lessons, top of file)
11. `_CLIENTS/locally-twisted/locally-twisted-decisions.md` — newest entries (Charges → Checkout Sessions, `/payment-success` override, per-client Stripe accounts)
12. `_CLIENTS/locally-twisted/apps/locally_twisted/locally_twisted/www/checkout.py` — the working guest checkout pattern, well-commented
13. `_CLIENTS/locally-twisted/apps/locally_twisted/locally_twisted/payments/stripe_session.py` — Stripe Checkout Session helper
14. `_CLIENTS/locally-twisted/apps/locally_twisted/locally_twisted/www/payment_success.py` — the override
15. `git log --oneline -30`

## Not in flight

- Stack containers running (GL may stop them via `docker stop $(docker ps --filter "name=locally-twisted-erpnext-v15" -q)` if they need RAM back)
- ONE spawned background process: `stripe listen --api-key "$STRIPE_LT_KEY" --forward-to ...` running in this session's background. Closes when the session closes. Demo flow doesn't depend on it (success-page reconciliation handles paid-marking sync).
- All session writes committed via auto-commit hook + the documentation writes in this closeout
- No smoke-test residue — cleaned 2 SOs + linked PRs/customers/addresses/contacts at session close. Next SO number when GL tests will be SAL-ORD-2026-00010 (or wherever the parallel agent left it)
- The other agent's parallel work continued through this session (commits visible in git log). Read recent commits before editing files they touched recently to avoid conflicts.

## A quick honesty pass

**What worked:**
- Naming the gap clearly when GL hit the unprofessional Stripe form. Walked Odoo's flow with Playwright to capture the visual evidence side-by-side, presented the Charges-API-vs-Checkout-Sessions tradeoff, recommended replace-not-polish, got a clean "go" and built it.
- Invoking the `stripe-best-practices` skill before writing any Stripe code. The skill's "no `payment_method_types`" guidance gave us dynamic payment methods (Klarna, Affirm, Cash App Pay, Bank, Link) automatically — visible in the Stripe-hosted screenshot.
- The `--api-key` workaround when the CLI auth was blocked. Saved an entire branch of "wait for Jeff's phone" friction.
- Codifying both project-tier and agency-tier learnings before closing. The kitchen note + decisions entries should let the second BBC-client-on-Frappe migration be 10x cheaper than this one.
- Idempotent webhook + sync reconciliation as belt-and-suspenders. The webhook is dormant for the demo but ready for production. The success-page path makes the demo work even if no listener runs.

**What stumbled:**
- I asked GL for credentials they'd already provided. TWICE. First "paste LT's keys here" when they were in `.env`. Then "do `stripe login --project-name lt-test`" without checking if they'd already authed. GL had to correct me both times. Anti-pattern #5 fired on top of #5.
- I described the mobile `/checkout` screenshot as "form is missing" when the form bounding box was at y=816 rendering 295×1198px. The thumbnail rendering of the long screenshot fooled me. Anti-pattern #1 (reporting without watching) almost fired — caught it by probing the bounding box programmatically before claiming the layout was broken.
- The first `_oneshot_compare_checkout.py` run had the cart-add intercepted by Odoo's sticky header — which made me get empty `/shop/address` etc. screenshots. Recovered with a force-click + JS-fallback retry. The fix was clean but the first attempt was wasted tokens.
- I wrote two READ-BEFORE-EDIT-flagged Edits without re-reading files immediately before. Both succeeded (I'd read them earlier in the same turn) but the runtime is strict and the reminders fired several times. For long sessions: re-read files defensively right before any Edit if more than a few tool calls have passed since you last read.

**Open trust state:**
- GL is exhausted. They asked for a proper goodbye at session close. They've pulled in long days for this Phase 1 demo. The last thing I want to do is leave a HANDOFF that creates re-work for the next instance.
- The Stripe migration shipped clean as far as my checks can tell. But "GL hasn't run a real card test yet" is the load-bearing piece of pending verification. The next instance must remember: **the only verification that matters is GL with a real card in a real browser.** Don't claim the migration is done until that test lands.

The work shipped. The cleanup ran. The next instance has a clear runway and an honest list of what's verified vs. what's pending.

— Closeout written 2026-04-29 by the Opus 4.7 instance who fixed the `/payment-success` 403, migrated Charges API → Checkout Sessions, and codified the agency-tier Stripe pattern. Two-session day (this was the second, after a long break).
