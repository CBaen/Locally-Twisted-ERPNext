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

- [P0] **Slice 6b — FAQ page.** Small static portal page; content composed from `_resources/policies/` (deposits, service-area, tax, theme rules, pricing). Composition is a synthesis step beyond verbatim transcription — surface question list to GL before shipping.
  - **DONE 2026-04-27:** Refund Policy at `/refund-policy` (and `/refund_policy` alias). Plain-language translation of `legal-interview-answers.md` Part 2C + `deposits.md`. 8 sections, no console errors, mobile + desktop verified.
- [P0] **Slice 7 — Lookbook (full portfolio).** `/lookbook` — visual heart of the site, organized by event type (Corporate, Weddings, Birthdays, Schools, Seasonal). The 5 Custom Creations circles + the 3 Recent Celebrations cards on the homepage already link here as stubs (currently 404).
- [P0] **Slice 8 — Service category pages.** `/services/<event-type>` × 5 (Corporate, Weddings, Birthdays, Schools, Seasonal). Each ends with inquiry CTA pre-filling `/book` with the category.
- [P0] **Slice 9 — Color Chart page.** `/color-chart` — static reference, all 70 balloon colors with names. Answers Jeff's "customers want to see colors" instinct without a configurator. Visual swatch grid + print-friendly stylesheet.
- [P0] **Slice 10 — `/book` form page.** Primary inquiry conversion form (45-field Lead schema). The hero CTA + closing CTA + every service-page CTA points here; currently 404.
- [P1] **Slice 11 — Small Shop browse + detail.** Webshop-driven; ~6–12 sub-$300 SKUs (themed bouquets, gift items, simple kits). Catalog data exists at `_resources/odoo-export/catalog.json` + 48 product images. **No configurator** — pre-configured items only.
- [P1] **Slice 12 — Cart + checkout shell.** Webshop default. Stripe stubbed until Phase 4.
- [P2] **Slice 13 — Blog framework + 2-3 first posts.** "Kindergarten Teacher" voice. Deferrable; not on demo critical path. **When this ships, the homepage's `HERO_CYCLING_TITLES` list should be replaced with a `frappe.get_list("Blog Post", ...)` call so real blog post titles cycle in the hero.**

### Future scope (post-Phase 1)

- **Design Studio — interactive picker for the customizable categories** (arches, columns, garlands, backdrops, drops, bouquets). 6th category (Bouquets) added 2026-04-27 per GL — bouquets are also customizable. Pattern: SVG-based picker (NOT Remotion — wrong tool, video-rendering not interactive UI). Inputs: backdrop selection (indoor/outdoor presets) → balloon shape placement → 70-color palette pick. Output: an inquiry form pre-filled with the customer's "vision," NOT a checkout. Resolves Jeff's "customers want to see colors and pick options" instinct without the wrong checkout flow. Scoped post-Slice 9 once the lookbook surface lands.

### First-ship omissions to revisit (deliberate deferrals)

- [P2] **BTFP image carousels** — face-painting + balloon-twisting carousels (9 images each in Odoo source). Need real photos OR AI-generated placeholders.
- [P2] **BTFP event-type animated crawl** — horizontal-scroll thin band of event types. Polish, not core.
- [P2] **BTFP and contact confirmation modals with auto-redirect** — replaced with inline success banners on first ship; add modal+redirect on a polish pass.
- [P2] **Contact Google Maps iframe** — adds external dep; address visible without it. Add when GL wants.
- [P2] **`/privacy` page** — referenced from contact + BTFP form privacy notes (currently pointing at `/refund-policy` as fallback). Build the page, then update the link targets.
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
