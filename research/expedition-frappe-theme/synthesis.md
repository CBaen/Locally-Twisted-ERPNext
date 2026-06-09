# Expedition Synthesis: Frappe v15 Customer-Facing Theme + Approved Content
## Date: 2026-04-26
## Verdict from GL Proxy: FLAGS (9 items) — most importantly, a direction question that needs to come back to you

## TL;DR for GL — One Page

The team went looking for ready-made tools that would let us build the LT website on Frappe with the polish you want. We came back with two true findings and one direction question.

**True finding 1 — There are no ready-made polished themes for Frappe.** The Frappe ecosystem is like a frame shop that sells raw frames but no finished paintings. If the LT site is going to look professional on Frappe, someone has to paint it by hand. There is no "install this theme and you have a beautiful balloon-business site" option. We checked the marketplace, GitHub, the community, the official documentation. The only Frappe-built sites that actually look polished are sites Frappe themselves built (frappe.io, fossunited.org). No documented case of a balloon company, a restaurant, or any similar small business successfully running a polished customer-facing website on Frappe was found.

**True finding 2 — The approved Jeff content was sitting on the disk the entire time.** Every previous instance invented placeholder copy when the actual approved copy lived in the legacy_source project files. The hero headline is "Utah's Balloon Specialists." The tagline is "Making celebrations unforgettable since 1998." The CTA-section heading is "Make Your Celebration Unforgettable." All verbatim. We do not need to invent or guess any of it for the new site.

**Direction question — Is Frappe the right home for the customer-facing website?** You said at the start: *"if ERPNext can't deliver this visual + UX bar, GL pivots away from ERPNext."* The team found two technically-possible paths to keep building inside Frappe (custom Jinja templates + custom CSS, or installing Frappe Builder as an experiment). Both are real. Both are buildable. But neither is easy, fast, or risk-free. The simpler alternative is to use Frappe ERPNext as the back office (orders, invoices, payroll, taxes — the things it is genuinely good at) and put a different platform on the customer-facing front door — WordPress or Webflow, which is what most small businesses with this much catalog actually use. That switch is easy now because nothing customer-facing is built yet on Frappe. It gets harder with every session.

I want you to make this choice on purpose. The team is ready to build whichever way you point.

## Recommended next action

One direction question, before any more building:

**Do you want to keep building the customer-facing website inside Frappe + webshop, or explore a simpler front door (WordPress / Webflow / plain Next.js storefront) with ERPNext quietly running the back office?**

There is no wrong answer. There is a best answer for what you actually want, which I cannot guess.

If your answer is "keep building inside Frappe" — the team has a clear plan ready. It will require real CSS work and Jinja template work, both of which we can do.

If your answer is "explore a different front door" — we change scope: ERPNext becomes the back office only, the customer-facing site moves to a platform that has thousands of polished themes, and Frappe webshop is replaced by a Stripe-direct or Shopify-Lite cart. This is the bigger change, but it is what most small businesses actually use, and it is the standard pattern when the back-office system is enterprise software.

---

## All Options Discovered

| # | Option | Convergence | Confidence | Source Evidence |
|---|--------|-------------|------------|-----------------|
| 1 | Custom Frappe app (hooks.py + web_include_css + Jinja overrides + SCSS) | CONVERGED | High | All three sources independently confirm. Already exists in LT codebase. |
| 2 | www/ static Jinja pages in custom app | CONVERGED | High | All three sources confirm as a valid Frappe primitive. None built yet for LT. |
| 3 | Web Page DocType + Page Builder (legacy) | CONVERGED | High — and high confidence it's WRONG | All three confirm: legacy, being phased out, failed in LT (twice), Jinja broken in Page Builder blocks. |
| 4 | Website Theme DocType (built-in) | CONVERGED | High for what it does — but it's THIN | Native to Frappe. Sets brand colors, font, simple SCSS. NOT a layout solution. Conflicts with web_include_css if both active. |
| 5 | Frappe Builder (separate official app) | PARTIAL | Moderate | Web + Docs confirm it's the "newer generation" tool; webshop coexistence unconfirmed/unresolved (open GitHub feature request #116). frappe.io is built on it. |
| 6 | ecommerce_theme (third-party paid marketplace app) | PARTIAL | Low | Only 3 installs. No demo. Unknown price. Single developer. Not viable. |
| 7 | Portal Theme (community app) | PARTIAL | Low | Targets v16; v15 compatibility unclear. Runtime CSS injection (similar pattern to what failed in Slice 2). |
| 8 | **External platform front door** (WordPress / Webflow / Next.js + ERPNext backend only) | NOT EVALUATED | — | Ruled out before research started by the brief's "system-native" constraint. Devil's Advocate flagged this as the most important overlooked option. |
| 9 | Web Page DocType with content_type="HTML" (NOT Page Builder) | NOT EVALUATED | — | Devil's Advocate identified: prior failure was specifically Page Builder content_type; the HTML content_type is different and was never tried. Quick test possible. |
| 10 | ERPNext Homepage DocType | SINGLE-SOURCE | Low | Mentioned in source URLs but never examined by any researcher. |

## Recommended approach (per convergence — but see direction question)

If GL chooses to keep building inside Frappe:

**Custom Frappe app + hooks.py + Jinja template overrides + compiled SCSS + www/ static pages where appropriate.** This is what real Frappe developers use. This is what the existing LT custom app architecture already supports. This is what every previous instance was supposed to be doing but didn't follow through on. The previous failures were technique failures within this architecture (made-up copy, broken `!important` chains, didn't actually override Jinja partials), NOT architecture failures. The path forward is real.

Specific build sequence if Frappe wins the direction question:
1. **Step 0 (mandatory before any new visible work):** Remove the broken navbar toggler block from `lt-theme.css` lines 388-415 (uses non-standard `data:image/svg+xml;utf8,` data URI that silently fails in real browsers). Replace with a real SVG file at `apps/locally_twisted/locally_twisted/public/icons/menu.svg`. Verify at 375px mobile width with Playwright.
2. **Step 0.5 (mandatory):** Verify the Jinja override path actually works in our Docker setup — drop a minimal `apps/locally_twisted/locally_twisted/templates/includes/footer/footer.html` with one visible test string, clear cache, confirm it resolves. The HANDOFF has been claiming "override Jinja partials" as the plan for two sessions; nobody has verified it actually works in our specific stack yet.
3. Then build navbar override + footer override using approved legacy_source content.
4. Then `www/` static page for the homepage with the approved Jeff copy.
5. Then BTFP page (the calculator collapses to tier 1 via Web Page's Script tab — confirmed earlier this session).
6. Then Contact page + ecommerce work.

## Devil's Advocate challenges (addressed transparently)

The Devil's Advocate raised the platform question as the strongest challenge. The convergence analyst recognized the discomfort and routed past it. **The GL Proxy flagged this as a routing-past-a-real-decision pattern.** This synthesis surfaces it as a direct question to GL above. That is the correction.

Other DA challenges:
- **"Test Frappe Builder empirically in 20 minutes"** — fair point. If GL's direction is "stay on Frappe but explore Builder," we run that test before committing to the custom-Jinja path.
- **"Web Page with content_type='HTML' was never tried"** — fair point. Different code path than Page Builder. Worth a 5-minute test if GL wants to keep using Web Page records (so Jeff can edit content via the desk UI later).
- **"Jeff cannot edit www/ pages without a developer"** — real trade-off. The build-sell-transfer model means Jeff inherits the system. If he can't update homepage copy without us, that's an ongoing engagement requirement we've never confirmed he wants. Ask GL.

## Approved content captured (Q3 ready)

Two sources of approved Jeff content now exist:

**Source A — Local legacy_source XML (`C:/Users/baenb/projects/locally-twisted-legacy_source/addons/locally_twisted/views/`):** This was the most recent legacy_source-side update before the legacy_source project was paused. Per CLAUDE.md, this is the authoritative content for the new build. Key strings (verbatim):
- Utility strip: "Bringing celebration to the Wasatch Front since 1998"
- Hero (3 slides): "Utah's Balloon Specialists" / "Custom Balloon Designs" / "Events & Special Occasions"
- CTA section: "Make Your Celebration Unforgettable" / "From birthdays to weddings, baby showers to corporate events — we've been part of Utah celebrations since 1998. Yours is next."
- Footer tagline: "Utah's Balloon Specialists since 1998."
- Newsletter: "Stay in the loop" / "Seasonal specials, new designs, and celebration ideas."
- 3 social icons: Facebook, Instagram, Pinterest (NO Twitter)
- Hours: "Tue-Fri 12-6, Sat 10-4"
- 4.9 stars / 114 reviews (Google)
- 52 named clients (FanX, Utah Jazz, Chick-fil-A, Ancestry, etc.)

**Source B — Live locallytwisted.com (current customer-facing WordPress site):** This is what customers see today. Key strings:
- Hero: "Make Your Party POP!" / "Anything you imagine, we can shape into reality."
- Differentiators: "Over 22 years of experience" (Source A says "since 1998" = 28 years)
- 4 social icons: Facebook, Twitter, Instagram, Pinterest (Source A excludes Twitter)
- 40+ corporate logos (LEGO, Expedia, Weber State, Northrop Grumman, Intermountain Health, Walmart, etc.)

**These two sources differ in voice, hero copy, social icon count, and credential framing.** GL needs to pick which is "the" approved content (or specify a third). The proxy flags this as a decision GL has not yet been asked.

## Post-Cutoff Discoveries

- Frappe Builder v1.23.3 (April 21, 2026 — five days before this research). Most actively maintained Frappe-side tool relevant to this question. 22,700 installs. Free, AGPL-3.0.
- ecommerce_theme v1.0.1 (October 2025). New on marketplace, only 3 installs.
- Portal Theme v16.0.0 (January 6, 2026). Targets v16, not v15.
- Frappe Build 2026 conference (April 2-3, 2026). Confirms active investment in the ecosystem.
- Auriga IT custom-app theme tutorial (July 2025). Post-cutoff confirmation that the custom-app pattern remains the recommended path.
- Webshop 2025 rewrite community discussion (July 2025). Existing webshop is criticized but no replacement has shipped.

## Open Questions (forced to GL — see direction question above)

1. **Platform direction:** Frappe customer-facing OR external front door + Frappe back office? (Load-bearing for everything else.)
2. **Approved content:** legacy_source XML version OR locallytwisted.com version OR a third Jeff confirmation? (Affects every page.)
3. **Social icons:** 3 (legacy_source XML, no Twitter) OR 4 (live site, with Twitter)? (Affects footer build.)
4. **Founding year:** "since 1998" (legacy_source XML; 28 years) OR "Over 22 years" (live site)? Reconcile to one number.
5. **Jeff's content self-management:** Will Jeff need to update homepage copy without a developer post-handoff? (Affects choice between Web Page DocType vs. www/ static pages.)

## What's Filtered Out

- Custom Web Templates from scratch — the convergence rejected this as worse than alternative options for one-off pages.
- Themes that target v16 only — Portal Theme, etc. We're pinned to v15.105.0.
- Theme apps with 3 installs and no demo — risk too high without validation.

## Critical pre-build tasks (regardless of platform direction)

These need doing whether the platform stays Frappe or pivots:

1. **Verify catalog image URLs against the Hetzner legacy_source server.** All 48 product image URLs in `_resources/legacy_source-export/catalog.json` point at `http://5.78.136.133/...`. Web Scout confirmed the Hetzner server is ECONNREFUSED. If the images are 404, they need to be re-exported from the local Docker legacy_source stack BEFORE that stack is decommissioned. Time-sensitive.
2. **Strip `!important` band-aids from `lt-theme.css` (full pass).** Step 0 from earlier this session removed the `.web-footer` chains, but Ground Truth audit confirmed 28 `!important` occurrences remain — including the broken navbar toggler block at lines 388-415.
3. **Verify the Jinja override path works in our Docker setup.** Two sessions of HANDOFF have claimed "override Jinja partials" as the plan; nobody has empirically confirmed the override resolves in our specific bind-mounted bench environment. One test file proves it works (or surfaces another problem to fix).

## Process notes

- **No code was written in this expedition.** The research is informational and decision-supporting only.
- **Two prior failed builds preceded this expedition.** This is not "third time's the charm with the same approach." The convergence-recommended path explicitly addresses both prior failure modes (the made-up copy issue and the !important-chain issue) — but only if GL's direction question is answered first.
- **The proxy's nine flags are listed in the gl-proxy-review.md** for the next instance picking this up. The most critical for build-readiness are Flags 1, 4, 5, and 6.
