# Locally Twisted — Work Queue

Current work only. **When an item is completed, DELETE it from this file.** Git tracks completion history. Queues are not for history.

Format: `- [priority] description — context / blocking notes`

LT-specific work only. Cross-client / agency-wide work lives at `Built_by_Cameron/built-by-cameron-queue.md`.

---

## Active

**Reconciliation note (2026-05-01):** `scripts/verify/layout_fit.spec.js` has been restored and verified through `npm run test:layout-fit` (60 passed). Treat `.planning/phases/01-customer-site-and-storefront/PLAN.md` as historical; `/contact` is the primary inquiry route and `/book` redirects to `/contact?intent=quick`.

### Phase 1 — Customer site (lookbook-forward, with small shop)

See `.planning/phases/01-customer-site-and-storefront/PLAN.md` for the full slice list. Highlights:

**DONE this session (2026-04-27):**
- Slice 3 — Homepage (lookbook-forward shape). Hero with cycling headline + stable tagline + photo. Reviews carousel (19 real Google reviews, 5-star anchored at bottom of each card, hover-pause). Custom Creations 5-category grid. Recent Celebrations 3-photo featured work. Client logo crawl (54 names, 270s scroll). Closing CTA. Twisting & Face Painting moved to bottom (de-emphasized per business strategy). Full-bleed band pattern across the page.
- Site shape decision: lookbook-forward + small shop sidebar, with future "Design Studio" interactive experience for arches/columns/garlands/backdrops/drops/bouquets categories (captures customer vision → routes to inquiry, NOT a checkout). See `.planning/decisions/site-shape.md`.

**Already DONE in prior sessions:**
- Slice 1 (brand foundation theme), Slice 2 (header + footer chrome), Slice 4 (BTFP page), Slice 5 (Contact page), Slice 6a (Accessibility statement). All form-bearing pages have AJAX → Lead + Communication wiring.

**Mirror Rebuild Phase 1 (Chrome) DONE 2026-04-30 evening:**
- Hetzner-shaped header + footer + 3 mega menus + mobile drawer + newsletter strip + `LT Newsletter Signup` DocType + endpoint + smoke test. 6 pre-task fixes (including unblocking /book). Triadic-construction-v2 + GL Proxy + fix round + audit pass. See `HANDOFF.md`, `MIRROR-REBUILD-COMPLETE.md`, `research/triadic-build-chrome-rebuild/` for receipts.

**Remaining (in priority order):**

- [P0] **Website launch workstream.** Active launch coordination lane at `workstreams/website-launch.md`. Goal: launch the site with inquiry, trust/policy, shop, visual/accessibility, and quality gates passing while avoiding collision with the separate form audit.
- [P0] **ERPNext Backend simplification workstream.** Multi-handoff lane at `workstreams/erpnext-backend-simplification.md`. First owner/manager/employee desk pass now has simplified temp roles/workspaces, `Add Product` for owner, clearer Customer/Contact labels, `Booking Calendar` on Sales Orders by delivery date, and an Owner Home command center with live cards, a chart, and Jeff's guided next-action flow. Lead photo table wiring, first stale Lead-script cleanup, idempotent workspace sync, the six-stage custom CRM pipeline, non-financial stage-to-Task cascades, and repeatable backend schema inventory are done. Next: verify checkout/Lead conversion parity before adding manual stage-to-finance automation, decide which remaining DB-only records need keep/hide/export treatment, simplify the Contact/Customer/order flow, and build backend-tour sample data only after the schema is cleaned up.
- [P0] **Finance/payroll/QuickBooks migration workstream.** Active lane at `workstreams/finance-payroll-quickbooks-migration.md`. First slice added read-only finance inventory, Accountant Home finance cards/shortcuts, and parity checks. Next: GL/accountant approval for QuickBooks export scope, bank import path, payment terms/reminder timing, HRMS payroll evaluation, and contractor/1099 reporting. Do not auto-submit finance records, send reminders, enable bank sync, or claim payroll readiness before those gates are approved and verified.
- [P0] **Mirror Rebuild Phase 2 — page rebuilds, in priority order:**
  1. `/refund-policy` Hetzner-faithful refresh. Mirror source: `pages/refund-policy.html`.
  2. `/accessibility` Hetzner-faithful refresh. Mirror source: `pages/accessibility.html`.
  3. `/blog` channel index + 2 ported posts. Use Frappe's NATIVE `Blog Post` DocType (NOT a custom one — plan-deepen 2026-04-30 caught the regression). Add `tags` field via `Customize Form` linking to a tiny `LT Blog Tag` DocType. Override `templates/pages/blog_post.html` for SEO meta tags Frappe's native template doesn't emit.
  4. Webshop `/shop` layout overhaul (against the new design guide).
  5. Webshop product detail layout overhaul.
  6. Webshop category detail page layout overhaul (`/shop-items/<group>`).
- [P1] **Catalog media reconciliation follow-up.** First launch-safe pass completed 2026-05-02: `scripts/setup/sync_variant_media.py` staged `_resources/odoo-live/images/`, `locally_twisted.seed.sync_variant_media` mapped 1,712 variant `Item.image` values where Odoo image labels clearly matched size/height/length/design/lights/topper/theme options, and product pages now swap images through `locally_twisted.api.variant_media`. Refresh the detailed review report with `python scripts/setup/sync_variant_media.py --dry-run --include-details --report output/catalog-media-review.json`; latest report checked 49 products, found 35 with candidate image labels, flagged 45 for review, left 1,712 mapped variants unchanged, and skipped 6,831 assignments that were not safe to infer. Remaining work: review the skipped/unmatched products and any broad gallery/category imagery with GL/Jeff before assigning photos by judgment. Do not treat unmapped products as missing if the source labels are not specific enough.
- [P1] **Localo marketing resource mining.** GL/Jeff confirmed 2026-05-02 that `https://locally-twisted.localo.site/` is tied to Jeff's marketing company and the material is Locally Twisted's to use per contract. Use `workstreams/localo-secondary-site-inventory.md` as the source lane. Localo is not the brand and should not be a customer destination; mine photos, review themes, proof structure, service language, social links, and SEO clues. If linking publicly, link only to `https://locally-twisted.localo.site/reviews` as multi-site review-trust proof. Keep a source log; prefer original/highest-quality files where available; rewrite blog/service copy before publishing; verify phone/address/hours/website links before launch. Known stale fact: Localo shows Tuesday closed, but Jeff confirmed LT is open Tuesdays.
- [P1] **Newsletter X-Forwarded-For strip at nginx layer (Option B).** Option A (email-keyed rate limit) shipped on `/api/method/locally_twisted.api.newsletter.signup` this session. Option B would protect `/contact`, `/checkout`, `/balloon-twisting-and-face-painting` too — they all use IP-based `@rate_limit` and share the same XFF-spoofing vulnerability. Ops/infra task: edit nginx config to strip/overwrite X-Forwarded-For before forwarding to gunicorn. See `Built_by_Cameron/built-by-cameron-decisions.md` 2026-04-30 entry "Frappe `@rate_limit` IP+key combine into ONE identity, not two."
- [P1] **`/privacy` + `/terms-of-service` Stripe Dashboard wiring.** Pages now exist locally; after GL/legal approval, update Stripe Dashboard's "Privacy policy URL" + "Terms of service URL" (currently `example.com/...` placeholders blocking live-mode activation).
- [P1] **Category browse imagery.** Verified 2026-05-02: all 11 customer-facing Item Group children under `Shop Items` have empty `image` fields. Do not revive the retired `/shop-by-category` card index for launch; use representative category media for `/shop-items/<group>` pages or a future image-rich mega-menu only after photos are selected.
- [P1] **Slice 8 — Service category pages.** `/services/<event-type>` × 5 (Corporate, Weddings, Birthdays, Schools, Seasonal). Each ends with inquiry CTA to `/contact`.
- [P1] **Slice 9 — Color Chart page.** `/color-chart` — static reference, all balloon colors with names. Answers Jeff's "customers want to see colors" instinct without a configurator. Visual swatch grid + print-friendly stylesheet.
- [P1] **Sample data for backend tour.** Before Jeff demo: a few realistic Lead records, one or two completed orders, one upcoming event. Lets Jeff click around the desk and see the system in motion.
- [P2] **Slice 13 — Blog framework + 2-3 first posts.** "Kindergarten Teacher" voice. Deferrable. When this ships, the homepage's `HERO_CYCLING_TITLES` list should be replaced with a `frappe.get_list("Blog Post", ...)` call so real blog post titles cycle in the hero.
- [P2] **Variant cache rebuild on Webshop Settings change.** If the next instance enables/disables variants or attribute filters, run `for template in templates: ItemVariantsCacheManager(template).rebuild_cache()` to flush stale Redis state.
- [P2] **Visual asset generation/source cleanup.** Non-urgent tangent pinned 2026-05-02. Revisit Facebook/Instagram/X icon assets as one small slice of the larger visual asset system after the higher-priority Localo/resource-mining work. Use the global capability recipe at `C:\Users\baenb\.codex\capabilities\recipes\safe-visual-asset-sourcing-and-generation.md` for icons, SVGs, generated lifestyle images, representative balloon decor renders, blog visuals, proof-photo handling, rights checks, post-production, and site verification.
- [P6] **Phase 6 cutover work item — fixture pruning.** BEFORE Jeff's first post-takeover deploy, REMOVE operator-state-sensitive Item Attribute fixtures from `hooks.py fixtures = [...]` (especially `latex colors` — 51 values Jeff is most likely to edit as supplier inventory shifts). Otherwise BBC fixture sync silently overwrites his renames on every `bench migrate`. Document in `NOUPDATE-DRIFT.md` (TBD). See `locally-twisted-decisions.md` 2026-04-30 entry.

**Slice numbering (current state):** 1-7 done (brand, chrome, homepage, BTFP, Contact, Accessibility, Refund+FAQ, Lookbook). Slice 8 (service categories), Slice 9 (color chart), Slice 13 (blog) — PENDING. Slice 10 (`/book`) is retired; `/contact` is the primary inquiry route and `/book` redirects to `/contact?intent=quick`. Slice 11 (browse) + Slice 12 (cart+checkout) DONE. **2026-04-30 catalog port shipped on top of Slice 11/12** — verified DB counts: 53 Website Items, 10,631 Items total, 10,578 variants, 10,613 Item Prices, on-brand product detail, mega menu, `/shop` hub, and category detail pages. `/shop-by-category` is now a compatibility redirect to `/shop`. See `locally-twisted-decisions.md` 2026-04-30 and 2026-05-02 entries. Historical "Already DONE" entries removed from queue per the "GitHub is our archive" rule — `git log` is the changelog.

### Future scope (post-Phase 1)

- [P1] **Design Studio V2 hidden route decision after engine spike.** Research-only PlayCanvas/Babylon package is complete at `research/design-studio-v2/event-builder-spike/`; feature handoff is `workstreams/event-builder-spike.md`. Both engines passed, so the current recommendation is PlayCanvas. Next: review screenshots/payload with GL, then decide whether to build a hidden Frappe route. Keep save/share, Lead submission, checkout, pricing, and ERPNext writes out of scope until separately approved.
- **Design Studio — interactive picker for the customizable categories** (arches, columns, garlands, backdrops, drops, bouquets). 6th category (Bouquets) added 2026-04-27 per GL — bouquets are also customizable. Pattern: SVG-based picker (NOT Remotion — wrong tool, video-rendering not interactive UI). Inputs: backdrop selection (indoor/outdoor presets) → balloon shape placement → 70-color palette pick. Output: an inquiry form pre-filled with the customer's "vision," NOT a checkout. Resolves Jeff's "customers want to see colors and pick options" instinct without the wrong checkout flow. Scoped post-Slice 9 once the lookbook surface lands.

### First-ship omissions to revisit (deliberate deferrals)

- [P2] **BTFP image carousels** — face-painting + balloon-twisting carousels (9 images each in Odoo source). Need real photos OR AI-generated placeholders.
- [P2] **BTFP event-type animated crawl** — horizontal-scroll thin band of event types. Polish, not core.
- [P2] **BTFP and contact confirmation modals with auto-redirect** — replaced with inline success banners on first ship; add modal+redirect on a polish pass.
- [P2] **Contact Google Maps iframe** — adds external dep; address visible without it. Add when GL wants.
- [P2] **Symmetry fix for Custom Creations on mobile** — currently 2-2-1 layout (Balloon Drops orphan on row 3). GL flagged the orphan-on-row-3 violates symmetry preference. Options: (a) center the orphan via `grid-column: 1 / -1` on `:nth-child(5)` (cleanest minimal change), (b) 1-per-row stack on mobile. Easy CSS fix; defer until next homepage iteration.

### Open iterations on already-built Lead schema (carried into Phase 2)

- [P1] **Inspiration Photos thumbnail UX decision.** Frappe blocks `in_list_view` on Attach Image AND Image fieldtypes in child tables. GL hasn't picked among: (a) click-to-expand (current state), (b) Frappe Client Script for inline gallery rendering, (c) drop child table for built-in attachments sidebar. Resume after GL chooses.
- [P1] **GL's "this is one Lead!" realization.** GL was thinking each tab was a Lead category; reality is sections of one Lead form. GL hasn't said what they actually wanted to model differently. Don't redesign without their explicit direction. Resume conversation when GL is ready.

### Phase 2 — Form-handling depth (reframed 2026-04-27)

`/contact` is the primary inquiry route. `/book` is retired and redirects to `/contact?intent=quick`. Phase 2 now covers depth around all forms:

- [P0] Verify Contact dedup logic now in `apps/locally_twisted/locally_twisted/lead_cascade.py` (Lead → existing Contact match by email/phone, else create new). Queue previously listed this as unbuilt; confirm with a smoke record before deleting.
- [P0] Verify customer acknowledgment email automation now in `apps/locally_twisted/locally_twisted/lead_cascade.py` (`after_insert`, queued `frappe.sendmail`). Queue previously listed this as unbuilt; confirm mail queue behavior before deleting.
- [P0] Loud-failure compliance audit across every form on Phase 1 surfaces
- [P1] Monitor alerts (Better Stack or equivalent) — fire if `/contact` form-creation rate drops to zero for >24 hours

### New asset drops at `assets/` (GL added 2026-04-27)

- [P1] **`assets/blue dog favicon.png`** — the balloon dog favicon GL was looking for. Wire into the site's favicon slot when ready (Frappe: drop into `public/icons/` and reference via Website Settings or `<link rel="icon">` in template).
- [P1] **`assets/blue dog logo.png`** — the balloon dog logo (companion to the existing text logo). Possible future use: header chrome, footer brand block, OG image for social shares.
- [P2] **`assets/product photos/`** — additional product photography. Inventory + match against `_resources/odoo-export/catalog.json` SKUs when seeding the small shop (Slice 11).
- [P2] **`assets/what we do photos/`** — additional event/decor photography. Candidate pool for the homepage hero swap, Featured Work cards, and the future Lookbook (Slice 7).

### Real customer reviews — ongoing

- [P3] When new 5-star reviews land, append to `home.py` `REVIEW_QUOTES` list. Carousel auto-scales to any count. Truncated reviews from the 2026-04-27 paste (Holly Offret, Angela Corona, Susie Jones, Connie Norton, Lisa Olsen, Al van der Beek, Dallas Yates, Kristi Johnson) are dropped — if you can get the full text, wire them in.
- [P3] Replace the `HERO_CYCLING_TITLES` placeholder list in `home.py` with `frappe.get_list("Blog Post", ...)` once Slice 14 (blog framework) ships.

### Cross-cutting / housekeeping

- ~~**Sweep `scripts/verify/_screenshots/` accumulated bloat.**~~ DONE 2026-04-30: added `scripts/verify/_screenshots/` to `.gitignore` (option B). 127MB of accumulated diagnostic captures no longer reach git. Existing on-disk dirs not auto-deleted but gitignored — GL or future instance can `rm -rf scripts/verify/_screenshots/*` to reclaim disk space when desired.

- [P2] **Right-side whitespace on product detail desktop.** Webshop's stock layout (`col-md-7` for product info) doesn't fill the centered 1200px max-width — the right side is bare on desktop. Two paths: (a) tighten product-detail max-width to ~960px (less whitespace, more "dense" feel), or (b) override webshop's product-page template to a more balanced 50/50 image/info split. Surfaced as design observation 2026-04-29 evening; awaiting GL decision. May be subsumed into the P0 holistic redesign work.

### Gate-kit follow-ups (added 2026-04-26 by gate-kit install — see `docs/GATE-KIT-INSTALL-NOTES.md`)

- [P1] **Add `requirements.txt` at repo root.** Currently `playwright` and `requests` are install-time prerequisites for the gate kit but not declared anywhere. Minimum: `playwright>=1.40` and `requests>=2.31`.
- [P2] **Document the human-review-commit deploy ritual in `scripts/README.md`.** The gate at `scripts/deploy.py:gate_human_review_commit()` refuses to deploy when HEAD's commit message starts with `auto:`. Routine remediation: `git commit --allow-empty -m "review: <pre-deploy summary>"` before running deploy.
- [P2] **Set `STAGING_URL` secret in GitHub repo settings + uncomment the CI form-shape step.** `.github/workflows/ci.yml` lines 35-36 are commented out pending a staging URL. Defer until staging exists.
- [P3] **At cutover (Phase 6): flip `scripts/deploy.py` `CONFIG["site_url"]` and `smoke_test_screenshot_paths`.** Currently `http://localhost:8081`; production URL TBD.
- [P3] **Wire `/contact` smoke test into deploy config.** `CONFIG["smoke_test_form_path"]` should target `/contact`; `/book` redirects to `/contact?intent=quick`.


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
