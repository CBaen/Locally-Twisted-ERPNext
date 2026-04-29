# Locally Twisted — Work Queue

Current work only. **When an item is completed, DELETE it from this file.** Git tracks completion history. Queues are not for history.

Format: `- [priority] description — context / blocking notes`

LT-specific work only. Cross-client / agency-wide work lives at `Built_by_Cameron/built-by-cameron-queue.md`.

---

## Active

### Phase 1 — Customer site (lookbook-forward, with small shop)

See `.planning/phases/01-customer-site-and-storefront/PLAN.md` for the full slice list. Highlights:

**DONE this session (2026-04-27):**
- Slice 3 — Homepage (lookbook-forward shape). Hero with cycling headline + stable tagline + photo. Reviews carousel (19 real Google reviews, 5-star anchored at bottom of each card, hover-pause). Custom Creations 5-category grid. Recent Celebrations 3-photo featured work. Client logo crawl (54 names, 270s scroll). Closing CTA. Twisting & Face Painting moved to bottom (de-emphasized per business strategy). Full-bleed band pattern across the page.
- Site shape decision: lookbook-forward + small shop sidebar, with future "Design Studio" interactive experience for arches/columns/garlands/backdrops/drops/bouquets categories (captures customer vision → routes to inquiry, NOT a checkout). See `.planning/decisions/site-shape.md`.

**Already DONE in prior sessions:**
- Slice 1 (brand foundation theme), Slice 2 (header + footer chrome), Slice 4 (BTFP page), Slice 5 (Contact page), Slice 6a (Accessibility statement). All form-bearing pages have AJAX → Lead + Communication wiring.

**Remaining (in priority order):**

- [P0] **Slice 10 — `/book` form page.** Primary inquiry conversion form (45-field Lead schema). The hero CTA + closing CTA + every service-page CTA points here; currently 404. Was DEFERRED 2026-04-29 when guest checkout took precedence; deferred AGAIN 2026-04-29 (later) when guest cart Path B + Stripe Link kill + cascade work landed. **NEXT major build.**
- [P0] **Spec table data on BTFP service cards.** Currently `Lorem ipsum` placeholders for BEST AT / DURATION / TEAM SIZE-or-ARTISTS / GOOD FOR. Jeff needs to confirm the actual numbers/lists. Replace lorem when confirmed.
- [P0] **`/privacy` page (Privacy Policy)** — required by Stripe for live mode activation. Currently `https://example.com/privacy-policy` placeholder in Stripe Dashboard. Build the page, point Stripe Dashboard's "Privacy policy URL" field at it, then update the in-site form link targets.
- [P0] **`/terms-of-service` page (Terms of Service)** — required by Stripe for live mode activation. Currently `https://example.com/terms-of-service` placeholder. Pair with `/privacy` for attorney pass.
- [P1] **Slice 8 — Service category pages.** `/services/<event-type>` × 5 (Corporate, Weddings, Birthdays, Schools, Seasonal). Each ends with inquiry CTA pre-filling `/book` with the category.
- [P1] **Slice 9 — Color Chart page.** `/color-chart` — static reference, all 70 balloon colors with names. Answers Jeff's "customers want to see colors" instinct without a configurator. Visual swatch grid + print-friendly stylesheet.
- [P1] **Sample data for backend tour.** Before Jeff demo: a few realistic Lead records, one or two completed orders, one upcoming event. Lets Jeff click around the desk and see the system in motion.
- [P2] **Slice 13 — Blog framework + 2-3 first posts.** "Kindergarten Teacher" voice. Deferrable; not on demo critical path. **When this ships, the homepage's `HERO_CYCLING_TITLES` list should be replaced with a `frappe.get_list("Blog Post", ...)` call so real blog post titles cycle in the hero.**

**DONE 2026-04-29 (guest-cart + cascade session) — DELETED FROM QUEUE:**
- ~~Real-card end-to-end test~~ — GL completed `4242` purchase for SAL-ORD-2026-00019.
- ~~Receipt email~~ — shipped via `_send_receipt_email` in `payment_success.py`. Plus operator notification + welcome email + Sales Invoice creation. Email Account configured.
- ~~Multi-item cart support~~ — full localStorage-backed cart shipped (Path B). `/cart` is LT-owned; `/checkout` accepts items_json; `submit_guest_order` builds multi-line SO.

**Already DONE 2026-04-27:**
- Slice 6b — Refund Policy (`/refund-policy`) + FAQ (`/faq`). Both with accordion structure. Source: legal-interview-answers Part 2C + deposits.md + 6 confirmed policy files.
- BTFP page substantial restructure to match mockup: hero kicker + title, service cards with photo carousels + spec tables (lorem), process section "Booking is straightforward" 4 steps, event types "Any Event. Any Size.", blush + soft-blue ribbons, last-minute booking banner.
- Color: `--lt-near-white` warmed `#FBFBFB` → `#fffcfc`. Header bg matches footer (both `--lt-soft-blue`). Copyright bar uses new base white.
- LookBook → Portfolio in nav (URL stays /lookbook).
- Font-weight error fix on FAQ + Refund Policy headings (DM Serif Display synthetic-bold).
- Ribbon margin shorthand fix.

**Already DONE 2026-04-28/29 (Stripe + true guest checkout):**
- Stripe Settings "Test" configured with API keys from `.env`. Auto-created Payment Gateway "Stripe-Test", Bank Account "Stripe-Test - LT" (USD), Payment Gateway Account "Stripe-Test - USD - LT" (default).
- Webshop Settings: enable_checkout=1, payment_gateway_account=Stripe-Test - USD - LT.
- `/checkout?item=<code>&qty=<n>` page (controller + template). Form takes name + email + phone + UT shipping + marketing opt-in checkbox. POSTs to `submit_guest_order` whitelist endpoint.
- `submit_guest_order` creates Customer + Contact + Address + Sales Order (order_type="Shopping Cart") + Payment Request (mute_email + manual set_payment_request_url). Returns payment_url.
- `/thank-you` (alias of `/thank_you` via website_route_rule) page renders post-payment landing with order summary.
- `marketing_opt_in` Custom Field on Customer (Check, default 0).
- All 8 smoke-test records cleaned at session end (SAL-ORD-2026-00001 through 00008, test customers, addresses, payment requests).

**Already DONE other-agent work overnight 2026-04-27→28:**
- /lookbook (Portfolio) page exists and renders.
- /shop page exists and renders.
- BTFP carousel orientation/aspect work.
- Header truck icon zoom adjustments.
- web_include_css cache-bust query string pattern.

**Slice numbering as of 2026-04-29:** Slices 1-7 all done (1 brand, 2 chrome, 3 homepage, 4 BTFP, 5 Contact, 6a Accessibility, 6b Refund + FAQ, 7 Lookbook). Slice 8 (service categories), Slice 9 (color chart), Slice 10 (`/book`), Slice 11 (small shop browse — partial via webshop default), Slice 12 (cart+checkout — DONE via /checkout custom flow). Slice 13 (blog) deferred.

### Future scope (post-Phase 1)

- **Design Studio — interactive picker for the customizable categories** (arches, columns, garlands, backdrops, drops, bouquets). 6th category (Bouquets) added 2026-04-27 per GL — bouquets are also customizable. Pattern: SVG-based picker (NOT Remotion — wrong tool, video-rendering not interactive UI). Inputs: backdrop selection (indoor/outdoor presets) → balloon shape placement → 70-color palette pick. Output: an inquiry form pre-filled with the customer's "vision," NOT a checkout. Resolves Jeff's "customers want to see colors and pick options" instinct without the wrong checkout flow. Scoped post-Slice 9 once the lookbook surface lands.

### First-ship omissions to revisit (deliberate deferrals)

- [P2] **BTFP image carousels** — face-painting + balloon-twisting carousels (9 images each in Odoo source). Need real photos OR AI-generated placeholders.
- [P2] **BTFP event-type animated crawl** — horizontal-scroll thin band of event types. Polish, not core.
- [P2] **BTFP and contact confirmation modals with auto-redirect** — replaced with inline success banners on first ship; add modal+redirect on a polish pass.
- [P2] **Contact Google Maps iframe** — adds external dep; address visible without it. Add when GL wants.
- [P1] **`/privacy` page (Privacy Policy)** — referenced from contact + BTFP form privacy notes (currently pointing at `/refund-policy` as fallback). **Also required by Stripe** for live mode activation — Stripe Dashboard expects a public Privacy Policy URL describing what data is collected, how it's used, who it's disclosed to, disclosure method, and security practices. Build the page, point Stripe Dashboard's "Privacy policy URL" field at it, then update the in-site form link targets. Currently set to `https://example.com/privacy-policy` placeholder in Stripe.
- [P1] **`/terms-of-service` page (Terms of Service)** — required by Stripe for live mode activation. Stripe Dashboard expects a public ToS URL. Currently set to `https://example.com/terms-of-service` placeholder. Pair with the privacy page when drafting (same template/lawyer pass).
- [P2] **`/shop/event-booking-deposit-32` deposit link** — referenced from BTFP "Pay $50 Deposit" button (Odoo's webshop product ID). Needs webshop product seeding first.
- [P2] **Symmetry fix for Custom Creations on mobile** — currently 2-2-1 layout (Balloon Drops orphan on row 3). GL flagged the orphan-on-row-3 violates symmetry preference. Options: (a) center the orphan via `grid-column: 1 / -1` on `:nth-child(5)` (cleanest minimal change), (b) 1-per-row stack on mobile. Easy CSS fix; defer until next homepage iteration.

### Open iterations on already-built Lead schema (carried into Phase 2)

- [P1] **Inspiration Photos thumbnail UX decision.** Frappe blocks `in_list_view` on Attach Image AND Image fieldtypes in child tables. GL hasn't picked among: (a) click-to-expand (current state), (b) Frappe Client Script for inline gallery rendering, (c) drop child table for built-in attachments sidebar. Resume after GL chooses.
- [P1] **GL's "this is one Lead!" realization.** GL was thinking each tab was a Lead category; reality is sections of one Lead form. GL hasn't said what they actually wanted to model differently. Don't redesign without their explicit direction. Resume conversation when GL is ready.
- [P0] **Connect the missing Inspiration Photos Table field.** The `LT Lead Photo` child DocType exists and the Section Break exists, but the Table field that connects them was never created — iter 4's step F failed silently. Right now there's an empty section heading on the Lead form. Tied to the thumbnail UX decision above.

### Phase 2 — Form-handling depth (reframed 2026-04-27)

`/book` itself moved into Phase 1 (Slice 10). Phase 2 now covers depth around all forms:

- [P0] Contact dedup logic (Lead → existing Contact match by email/phone, else create new)
- [P0] Customer acknowledgment email automation (Server Script on Lead `before_insert` or similar)
- [P0] Loud-failure compliance audit across every form on Phase 1 surfaces
- [P1] Monitor alerts (Better Stack or equivalent) — fire if `/book` or `/contact` form-creation rate drops to zero for >24 hours

### New asset drops at `assets/` (GL added 2026-04-27)

- [P1] **`assets/blue dog favicon.png`** — the balloon dog favicon GL was looking for. Wire into the site's favicon slot when ready (Frappe: drop into `public/icons/` and reference via Website Settings or `<link rel="icon">` in template).
- [P1] **`assets/blue dog logo.png`** — the balloon dog logo (companion to the existing text logo). Possible future use: header chrome, footer brand block, OG image for social shares.
- [P2] **`assets/product photos/`** — additional product photography. Inventory + match against `_resources/odoo-export/catalog.json` SKUs when seeding the small shop (Slice 11).
- [P2] **`assets/what we do photos/`** — additional event/decor photography. Candidate pool for the homepage hero swap, Featured Work cards, and the future Lookbook (Slice 7).

### Real customer reviews — ongoing

- [P3] When new 5-star reviews land, append to `home.py` `REVIEW_QUOTES` list. Carousel auto-scales to any count. Truncated reviews from the 2026-04-27 paste (Holly Offret, Angela Corona, Susie Jones, Connie Norton, Lisa Olsen, Al van der Beek, Dallas Yates, Kristi Johnson) are dropped — if you can get the full text, wire them in.
- [P3] Replace the `HERO_CYCLING_TITLES` placeholder list in `home.py` with `frappe.get_list("Blog Post", ...)` once Slice 14 (blog framework) ships.

### Cross-cutting / housekeeping

- [P2] **Persist the nginx Origin patch across container recreation.** Currently applied via `docker exec` in `scripts/fix/patch_nginx_socketio_origin.py` and only survives until the frontend container is recreated. Cleaner long-term: docker-compose override that mounts a custom `frappe.conf` with the pass-through line.

### Gate-kit follow-ups (added 2026-04-26 by gate-kit install — see `docs/GATE-KIT-INSTALL-NOTES.md`)

- [P1] **Add `requirements.txt` at repo root.** Currently `playwright` and `requests` are install-time prerequisites for the gate kit but not declared anywhere. Minimum: `playwright>=1.40` and `requests>=2.31`.
- [P2] **Document the human-review-commit deploy ritual in `scripts/README.md`.** The gate at `scripts/deploy.py:gate_human_review_commit()` refuses to deploy when HEAD's commit message starts with `auto:`. Routine remediation: `git commit --allow-empty -m "review: <pre-deploy summary>"` before running deploy.
- [P2] **Set `STAGING_URL` secret in GitHub repo settings + uncomment the CI form-shape step.** `.github/workflows/ci.yml` lines 35-36 are commented out pending a staging URL. Defer until staging exists.
- [P3] **At cutover (Phase 6): flip `scripts/deploy.py` `CONFIG["site_url"]` and `smoke_test_screenshot_paths`.** Currently `http://localhost:8081`; production URL TBD.
- [P3] **Wire `/book` smoke test the day Slice 10 ships.** `CONFIG["smoke_test_form_path"] = "/book"` is parked. The form smoke test will FAIL until the form exists; that's expected.


## Blocked

*nothing*

## Waiting on GL

- **Inspiration Photos thumbnail UX** — pick (a)/(b)/(c) from the Lead-schema iteration item above (carries into Phase 2)
- **"This is one Lead" realization** — what did you want to model that you thought was happening? (carries into Phase 2)
- **Real photo replacements** — the 5 home photos in `apps/locally_twisted/locally_twisted/public/images/home/` are GL-acceptable for v1 but future swaps possible (especially the Twisting photo — there are 9 others in Odoo `assets/image assets/balloon twisting pics/` that could rotate in).

*All Phase 1 decision gates resolved.*

## Deferred (intentional, not blocked)

- **About page** — deferred until Jeff is ready (GL 2026-04-27). Contact page covers the basics; no About in v1.
- **Custom Frappe app scaffolding for LT** — DONE (the `locally_twisted` app exists and is installed). Marked complete; no longer deferred.
- **Frappe Cloud signup + production deployment** — Phase 6 (cutover).
- **Reading Jeff's UI-edited content from any prior platform's database** — Not applicable; the prior platform never went live.
- **Two-app split (`agency_platform` + `<client>_connector`) and three-tier alternative** — agency-wide architectural decision; deferred until BBC has 2-3 clients to inform pattern (see `Built_by_Cameron/built-by-cameron-decisions.md` 2026-04-26).

### Design Studio contest — post-synthesis follow-ups (added 2026-04-29 late evening; updated by next-day instance after surface)

**Contest itself is COMPLETE.** Render gallery (56 PNGs) + `FINAL-SURFACE.md` shipped. GL holding 5 agents (Proxy + 4 contestants by ID) for synthesis follow-ups. Shutdown deferred until GL signals contest fully done.

- [P1] **Write LT-tier lessons-learned + decisions log entries** for the contest outcomes. Capture *after* GL completes synthesis with the picked pieces — entries should reflect what GL chose and why, not the orchestration itself.
- [P2] **Possible global capabilities update** about the persistent-agent-by-ID pattern (the contest skill's name-addressing assumption is wrong-shaped per session learning).
- [P2] **Send shutdown SendMessages to the 5 contest agents** once GL signals the contest is fully done. IDs: Proxy `aa3108d9ab3c5a978`, C1 `a76396efd739881c3`, C2 `a3a7df4f715615f21`, C3 `ad72af232430d89f3`, C4 `a30d848ce821198bb`.

