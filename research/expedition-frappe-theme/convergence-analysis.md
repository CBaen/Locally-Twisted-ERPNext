# Convergence Analysis: Frappe v15 Customer-Facing Theme + Approved Content
## Date: 2026-04-26
## Researchers Compared: Web Scout, Docs & Standards, Ground Truth

---

## Complete Options Table

| # | Option | Web Scout | Docs & Standards | Ground Truth | Rating |
|---|--------|-----------|-----------------|--------------|--------|
| 1 | Custom Frappe app (hooks.py + web_include_css + Jinja overrides) | Found — Option 1 | Found — Option C + D | Found — already exists in codebase | CONVERGED |
| 2 | Frappe Builder (separate app, visual editor) | Found — Option 2 | Found — Option B | Not installed; not attempted; routing unknown | PARTIAL (two sources recommend; Ground Truth shows no attempt + unresolved routing concern) |
| 3 | Ecommerce Theme (marketplace, paid) | Found — Option 3 | Found — Option E | Not present in container | PARTIAL (two sources describe; Ground Truth confirms not installed and no evidence of use) |
| 4 | Portal Theme (marketplace, community) | Found — Option 4 | Found — Option F | Not present in container | PARTIAL (two sources describe; Ground Truth confirms absent) |
| 5 | Website Theme DocType (built-in, brand-level vars) | Found — Option 5 | Found — Option D | Found — "Standard" record exists, empty | CONVERGED |
| 6 | www/ static Jinja pages (code-managed routes) | Found — Option 6 | Found — Option C | Not yet implemented; plan documented | CONVERGED (all three confirm this is valid; Ground Truth confirms none exist yet) |
| 7 | Web Page DocType / Legacy Page Builder | Found — Option 7 (as FAILED approach) | Found — Option A (documented, legacy) | Found — failed in build(), rolled back | CONVERGED (as failed / legacy path not recommended) |
| 8 | Website Theme DocType known v15 bugs | Not surfaced | Found — issues #27107, #28641, web_include_css conflict | Found — empty Standard record, no active bug reproducing yet | PARTIAL (Docs found bugs in detail; Ground Truth confirms no active theme = not yet hit; Web Scout did not surface) |
| 9 | Hero Slider Web Template Bootstrap 4 vs 5 incompatibility | Not found | Not found | Found — explicit `data-ride` vs `data-bs-ride` discrepancy confirmed in webshop template | SINGLE-SOURCE (Ground Truth only — critical bug) |
| 10 | webshop + Frappe Builder routing conflict | Found — as unknown risk | Found — Builder issue #116 (shopping cart open) | Not examined | PARTIAL (two sources flag as unknown; no source confirms or denies clean coexistence) |
| 11 | Official Frappe-supplied website themes | Web Scout: none found | Docs: none exist | Ground Truth: "Standard" record is empty default | CONVERGED (all three confirm: no pre-built polished named themes exist) |
| 12 | Ecosystem thinness (no Squarespace-quality turnkey theme) | Found — explicit finding | Found — implicit (marketplace scan shows 3 installs on best option) | Found — no third-party themes installed or evaluated in codebase | CONVERGED |
| 13 | AGPL licensing risk of Frappe Builder | Found | Not surfaced | Not surfaced | SINGLE-SOURCE (Web Scout only) |
| 14 | Page Builder = effectively legacy / no new investment | Found — community sources | Found — zero new features since ~v15.50, community calls it legacy | Ground Truth — failed in practice, rolled back | CONVERGED |
| 15 | !important chains in lt-theme.css still present and broken | Not found | Not found | Found — 28 occurrences, lines 388-415 data URI SVG bug confirmed unresolved | SINGLE-SOURCE (Ground Truth only — immediate blocker) |
| 16 | Approved copy in legacy_source XML is complete, structured, and available | Not applicable (fetched from locallytwisted.com instead — legacy_source server down) | Not applicable | Found — 43 XML files, complete content | SINGLE-SOURCE (Ground Truth only for legacy_source XML; Web Scout has alternate source) |
| 17 | web_include_css conflict with active Website Theme | Not surfaced | Found — documented conflict, no official fix | Ground Truth — `website_theme_scss` is commented out; web_include_css active; no Website Theme active = no conflict currently | PARTIAL (Docs found the conflict; Ground Truth shows current state avoids it by not activating a theme; Web Scout missed it) |
| 18 | No Jinja template overrides exist yet in LT app | Not surfaced | Not applicable | Found — no `templates/` directory in app | SINGLE-SOURCE (Ground Truth; critical gap) |
| 19 | Frappe Builder v1.23.3 (April 2026 release, actively maintained) | Found — POST-CUTOFF | Not surfaced at version level | Not installed / not examined | NEW (Web Scout only; post-cutoff) |
| 20 | ecommerce_theme v1.0.1 (October 2025) | Found — POST-CUTOFF | Found — POST-CUTOFF | Not installed | NEW (both sources; post-cutoff) |
| 21 | portal_theme v16.0.0 (January 2026) | Found — POST-CUTOFF | Found — POST-CUTOFF | Not installed | NEW (both sources; post-cutoff) |

---

## CONVERGED Findings (High Confidence)

### C1: The custom Frappe app (hooks.py + web_include_css + Jinja template overrides) is the correct baseline architecture

All three sources confirm independently:
- **Web Scout** (July 2025 Auriga IT tutorial, official Frappe docs): custom app with `web_include_css` in `hooks.py` is the recommended, stable, Frappe-Cloud-transferable pattern. Not a compromise — the intended primitive.
- **Docs & Standards** (official hooks docs, Website Theme docs): `web_include_css` registers pre-built CSS into the portal layer; Jinja template overrides at `templates/includes/navbar/` and `templates/includes/footer/` are officially documented paths.
- **Ground Truth**: The `locally_twisted` app is already scaffolded, `web_include_css` is already active and pointing at a real CSS file, 616 lines of LT design tokens are in place. The architecture is not theoretical — it exists and is wired.

**Where all three agree specifically:** `web_include_css` is the right CSS delivery hook; Jinja partial overrides by filename-match are the right template override path; this approach is webshop-compatible and Frappe-Cloud-transferable.

**What none of them contradict:** No source suggests abandoning this approach. The disagreements are about ADDING to it (Builder) or REPLACING parts of it (Website Theme SCSS), not about the core pattern being wrong.

### C2: No polished, production-validated, turnkey Frappe v15 website theme exists for a small-business marketing site

All three sources confirm:
- **Web Scout**: Searched Frappe Cloud marketplace, GitHub, Wappalyzer's 6,400 Frappe installs, awesome-frappe, Reddit, discuss.frappe.io — found no "Squarespace-quality landing page theme for Frappe." Only 3 installs on the best candidate.
- **Docs & Standards**: Frappe Cloud marketplace scan confirms: only 3 customer-facing-website-relevant apps (Frappe Builder, ecommerce_theme with 3 installs, portal_theme with 48 installs targeting portal/login layer). No official Frappe-shipped named themes in Website Theme DocType list.
- **Ground Truth**: Container inspection shows only one Website Theme record ("Standard") and it is empty — no fonts, no colors, no custom SCSS. No third-party theme apps are installed.

**Implication for LT:** GL's intuition that themes must exist — like WordPress or Shopify themes — is not confirmed by any source. The answer to "find existing themes" is: they don't meaningfully exist for this use case. LT will need to build its visual design from the existing `lt-theme.css` foundation.

### C3: Page Builder (Legacy Web Page DocType) is effectively abandoned and failed in practice for LT

All three sources confirm independently:
- **Web Scout**: Community consensus — "the legacy solution being phased out in favor of newer tools." Prior LT attempt: not visible in browser, not mobile-responsive.
- **Docs & Standards**: Zero new features in Page Builder across all v15 releases reviewed (v15.100-v15.106). Zero new features since approximately v15.50. Jinja does not evaluate in Page Builder blocks (issue #16564, open). Frappe's own positioning pushes Frappe Builder as "the newer generation and replacement."
- **Ground Truth**: The `landing.py` `build()` function is in the codebase, marked RETIRED, with an explicit warning not to run it. The failed attempt is in git history (commit `1ed6d29`). The current live site is the placeholder from `rollback()`.

**Caveat agreed by Docs & Standards:** There is no OFFICIAL deprecation notice. The API still works. The rendering failures observed may have been caused by: wrong Published flag, nginx Origin header issue (pre-existing fix), or CSS cascade problems — not necessarily Page Builder's fundamental architecture. However: the prior attempt was made with awareness of some of these issues, and still failed.

**Convergence verdict:** Do not use Page Builder for LT's homepage. The evidence from all three sources points away from it, and the one source (Ground Truth) that actually observed it behave — confirmed it failed.

### C4: www/ Jinja pages (code-managed, inside the custom app) are a valid and officially-documented path

All three sources confirm:
- **Web Scout**: "This is what real Frappe developers use for custom marketing pages." Full control over HTML/CSS, no DocType dependency, webshop-compatible.
- **Docs & Standards**: Official Frappe v15 framework docs document this as the developer path for portal pages. Foundational, all versions.
- **Ground Truth**: No www/ pages exist yet in the `locally_twisted` app — confirmed gap. But the app structure supports it and the override path is confirmed ("Place `<page-name>.html` at `apps/locally_twisted/locally_twisted/www/<route>.html`").

**Tradeoff confirmed by Web Scout and Ground Truth:** Jeff cannot self-edit www/ pages from the Desk UI. Content updates require code changes + deploy. Acceptable for Phase 1; limitation for self-service content management long-term.

### C5: Website Theme DocType is the right tool for brand-level font and color variables — but is thin and has v15 bugs

All three sources confirm:
- **Web Scout**: The built-in Website Theme DocType handles fonts, colors, Bootstrap variable overrides. Correct primitive for brand consistency. Cannot replace a custom app for serious layout work.
- **Docs & Standards**: Detailed field map, compilation behavior, two known v15 bugs (inter.css 404 at v15.34, `--primary` overwrite at v15.48), and the `web_include_css` conflict when an active theme is present.
- **Ground Truth**: The "Standard" theme record is empty — no font, no color, no SCSS. The `website_theme_scss` hook is commented out in `hooks.py`. The `web_include_css` is active and serving the CSS. Currently, no active Website Theme = no conflict.

**Key practical finding (from Docs & Standards, corroborated by Ground Truth):** When a Website Theme is active, `web_include_css` hook CSS stops loading. These two mechanisms conflict. The LT codebase is currently using `web_include_css` only, with no active Website Theme — the safer arrangement given the existing `lt-theme.css` investment.

**Convergence verdict:** Do not activate a Website Theme unless the team is willing to migrate the entire `lt-theme.css` design token system into the Website Theme SCSS fields. The current approach (web_include_css only, no active theme) avoids the known conflict.

---

## PARTIAL Findings (Moderate Confidence)

### P1: Frappe Builder is the current-direction, technically-capable option — but webshop routing compatibility is unconfirmed

**Two of three sources recommend it (with caveats):**
- **Web Scout**: Actively maintained (v1.23.3, April 2026), 22.7k installs, frappe.io itself built on it. Risks: AGPL license, documented Vite build conflicts with ERPNext v15.72.1, webshop routing unconfirmed, Builder pages stored in DocType (need Builder installed at destination).
- **Docs & Standards**: Official publisher (Frappe Tech), free, v15 + v16 supported. Issue #116 (shopping cart integration with webshop is open feature request — Builder does not natively integrate). Mobile responsiveness is not automatic — requires deliberate design methodology.

**What the disagreeing source found:**
- **Ground Truth**: Builder is not installed and has not been attempted. The routing question was not examined at the code level. The codebase shows no evidence of Builder evaluation. Ground Truth does not confirm OR deny compatibility — it simply has no information.

**Why this matters for LT:** The LT stack has webshop at `/all-products`, `/cart`, `/checkout`, and product detail URLs. Builder pages would need to own `/`, `/about`, `/contact`, `/gallery`, `/balloon-twisting-and-face-painting`. Whether these routes can coexist without conflict is the unanswered question. The community absence of a documented conflict is weak evidence — absence is not confirmation.

**Confidence verdict:** Builder is viable for STANDALONE Frappe sites. For the ERPNext + webshop + custom app + payments LT stack, it is unverified. Testing in the live Docker environment is the only way to resolve this.

### P2: ecommerce_theme (marketplace, paid) is technically relevant but untested in production

**Two of three sources found it:**
- **Web Scout**: 3 installs, no demo, unknown pricing, single developer maintainer, Tailwind CSS (potential Bootstrap cascade conflict).
- **Docs & Standards**: v15.x+ required dependency confirmed, Tailwind CSS noted, full rebuild required. Low adoption (3 installs on Marketplace).

**What the disagreeing source found:**
- **Ground Truth**: Not present in the container. No evidence of evaluation. Not mentioned in git history.

**Confidence verdict:** Low. Three installs is insufficient real-world validation. No demo to evaluate visual quality. Unknown pricing. Not a viable path for a client-facing build where quality matters and Jeff needs to trust the result.

### P3: Portal Theme is technically interesting but targets portal/login layer, not marketing pages

**Two of three sources found it:**
- **Web Scout**: 34 GitHub stars, 36 forks, v16.0.0 latest (January 2026) — v15 compatibility uncertain. Runtime CSS injection (same mechanism as head_html) may have cascade priority problems.
- **Docs & Standards**: 48 active installs, 5.0 stars (2 reviews), runtime injection avoids bench build dependency. Targets portal/login layer, not full marketing site theming.

**What the disagreeing source found:**
- **Ground Truth**: Not present in container. Not evaluated.

**Confidence verdict:** Portal Theme addresses the wrong surface for LT's needs. LT needs a polished customer-facing marketing homepage, not better styling of the ERPNext login page and portal cards. Pass.

### P4: Frappe Builder + webshop routing conflict — the absence of documented conflict is not confirmation of safety

**Two sources flag this as unknown:**
- **Web Scout**: Explicitly listed as Unknown/Risk. No official documentation confirms coexistence. Builder's URL routing and webshop's URL routing may conflict.
- **Docs & Standards**: Builder issue #116 (shopping cart integration with webshop — open feature request) confirms the two products are architecturally separate and have NOT been integrated. No routing conflict documentation found either direction.

**What the third source did:**
- **Ground Truth**: Did not examine this question at all. Builder is not installed; no test possible.

**Confidence verdict:** UNKNOWN — the two sources agree the question is unresolved. This must be tested before committing Builder to the LT stack. The risk is real: Builder manages dynamic URL routing via DocType; webshop manages `/all-products`, `/cart`, etc. A misconfigured Builder page at `/shop` or `/all-products` would conflict.

---

## SINGLE-SOURCE Findings (Low Confidence — but do not dismiss)

### S1: Hero Slider Web Template uses Bootstrap 4 API, incompatible with ERPNext v15 Bootstrap 5 runtime

**Source:** Ground Truth only. Found during container inspection of `webshop/web_template/hero_slider/hero_slider.html`.

**Finding:** `data-ride="carousel"` (Bootstrap 4) is used in the webshop Hero Slider template. The ERPNext v15 stack uses Bootstrap 5, which uses `data-bs-ride` and removed jQuery's `.carousel()` method. If Page Builder is used with the Hero Slider template, carousel autoplay will silently not work. The legacy_source `s_lt_hero.xml` correctly uses Bootstrap 5 syntax — confirming this is a template bug, not a design intent.

**Why this matters even though single-source:** This is a code-level fact, not an interpretation. The bytes in the file are what they are. Web Scout and Docs did not look at this specific file, but if they had, they would have found the same thing. The finding is trustworthy despite being single-source because it is directly observable.

**Action:** Do not use the webshop Hero Slider Web Template in Page Builder. Build a Bootstrap 5-correct carousel in `main_section_html` or as a `www/` Jinja template using the syntax confirmed in `s_lt_hero.xml`.

### S2: 28 !important occurrences in lt-theme.css; lines 388-415 contain broken data URI SVG for navbar toggler

**Source:** Ground Truth only. Direct file inspection.

**Finding:** The navbar toggler icon uses `background-image: url("data:image/svg+xml;utf8,...")` — the `utf8` encoding prefix is non-standard; real browsers (Chrome, Firefox) silently render an empty/broken icon. This is documented in `lessons-learned.md` as silently failing. Despite being documented as needing removal, the code is still in place as of the audit date.

**Why this matters:** This is a prerequisite blocker for any browser-testing of the site. If the navbar toggler icon is broken, every mobile browser session will show a broken hamburger icon. Any "does the site look professional?" test is invalid until this is fixed.

**Action:** This is Step 0. Fix `lt-theme.css` lines 388-415 before any other work. Remove the data URI SVG approach; use an SVG file in `public/icons/` or use Font Awesome's `bars` icon via existing FA include.

### S3: No Jinja template overrides exist yet in the locally_twisted app

**Source:** Ground Truth only. Directory inspection.

**Finding:** The `locally_twisted` app has no `templates/` directory. Every reference in HANDOFF.md to "we'll override the footer Jinja partial" is a plan, not an implementation. The footer that actually renders is Frappe's default footer partial.

**Why this matters:** Multiple prior instances described the Jinja override path as "the path forward" but none implemented it. The custom footer with the 3-column layout (Shop / Company / Get In Touch from `footer.xml`) does not exist yet. The header with the two-tier utility strip does not exist yet.

**Action:** Do not treat planned Jinja overrides as done. They must be built from scratch. The legacy_source XML source (`footer.xml`, `header.xml`) provides the content blueprint; the Frappe template override mechanism provides the delivery path.

### S4: AGPL licensing risk for Frappe Builder in commercial deployments

**Source:** Web Scout only.

**Finding:** Frappe Builder is AGPL-3.0. Under AGPL, if software is modified and used over a network (as a SaaS or hosted website), those modifications must be made available. For a client-hosted ERPNext instance where the website is delivered to the public, this means Builder customizations may require open-sourcing.

**Why this matters:** If GL + Jeff adopt Builder and create custom Builder Pages, that content and configuration may technically need to be open. The practical enforcement likelihood is low for a small business, but it represents a legal question GL and Jeff should evaluate before committing to Builder.

**Note:** This is a single-source finding from Web Scout. Docs & Standards did not explicitly surface this despite examining Builder's marketplace listing. However, AGPL-3.0 is a verifiable fact about the Builder repository license — trustworthy despite single-source.

### S5: legacy_source image URLs in catalog.json are not local files — will 404 after legacy_source decommission

**Source:** Ground Truth only.

**Finding:** All 48 product images in `catalog.json` are legacy_source server URLs (`http://5.78.136.133/web/image/...`). The legacy_source stack is currently running, making these fetchable now. When the legacy_source server is decommissioned (planned), all 48 image URLs become 404.

**Action:** Export all product images from the legacy_source server before it is decommissioned. This is a time-sensitive dependency — the legacy_source server is described as a temporary reference.

### S6: Catalog has no product descriptions (48 of 51 products have description: null)

**Source:** Ground Truth only.

**Finding:** The ERPNext webshop product detail pages will have no body copy unless descriptions are written. This is a content gap that will affect the quality of product pages regardless of which theme/architecture is chosen.

---

## DIVERGENT Findings (Conflict)

### D1: Is the legacy_source server at 5.78.136.133 accessible?

**Web Scout:** CONNECTION REFUSED on both attempts. Server appears down or firewalled.

**Ground Truth:** legacy_source stack is currently running locally (`locally-twisted-legacy_source-web-1 Up 30 hours`). Product images are fetchable from `http://5.78.136.133/...` URLs.

**Resolution:** These are not the same thing. Web Scout was accessing the HETZNER remote server (the failed deployment at http://5.78.136.133/ — the public-facing legacy_source). Ground Truth was examining the LOCAL Docker legacy_source stack running on Wardenclyffe (`locally-twisted-legacy_source-web-1`). They are two different legacy_source instances:
- **Remote Hetzner legacy_source** (http://5.78.136.133/): Public, appears down per Web Scout.
- **Local Wardenclyffe legacy_source** (local Docker, port unknown): Running, Ground Truth confirmed Up 30 hours.

The catalog.json image URLs point at the **Hetzner server** (http://5.78.136.133/). If that server is down (per Web Scout), those image URLs are already broken. The local legacy_source is a separate Docker container, likely at a different localhost port, not accessible at 5.78.136.133.

**Practical implication:** The catalog.json images may already be broken. This needs verification.

### D2: How many social media icons should the LT footer have?

**Web Scout (from locallytwisted.com):** Facebook, Twitter, Instagram, Pinterest — 4 icons.

**Ground Truth (from legacy_source footer.xml):** Facebook, Instagram, Pinterest — 3 icons. Explicitly no Twitter. Notes: "The `setup_slice2_header_footer.py` script added Twitter — that was wrong per the legacy_source source."

**Resolution:** These are two different "Jeff-approved" sources:
- `locallytwisted.com` (current live customer-facing site): shows Twitter/X.
- legacy_source `footer.xml` (the new-build blueprint Jeff reviewed): explicitly excludes Twitter.

The legacy_source XML was built more recently and represents the new build's intent. If Jeff approved the legacy_source design, the 3-icon footer (no Twitter) is the correct choice. However, the live site includes Twitter — which may mean Jeff added it there deliberately, or the legacy_source design was built based on a different intent at that time.

**This conflict requires GL clarification.** Neither source can definitively override the other without knowing Jeff's current preference. For the ERPNext build, the Ground Truth (legacy_source XML) is the stated authoritative source per the CLAUDE.md "canonical sources" section — use 3 icons unless GL confirms otherwise.

---

## NEW Findings (Post-Cutoff Discovery)

### N1: Frappe Builder v1.23.3 released April 21, 2026

**Source:** Web Scout.

The most recent Builder release was published 5 days before this research. Actively maintained. New features include separate images for light and dark mode. Version count significantly higher than training-cutoff-era knowledge (~v1.10-1.12).

**Impact:** Builder is not stagnant. The documented Vite build failure at v1.18.0/ERPNext v15.72.1 may be resolved in v1.23.3. However, the LT stack at v15.105.0 is significantly newer than v15.72.1 — the compatibility question needs fresh verification.

### N2: ecommerce_theme v1.0.1 (October 2025) on Frappe Marketplace

**Sources:** Web Scout and Docs & Standards both found this.

A new third-party ecommerce theme with explicit webshop compatibility claim. Only 3 installs. Rating: not ready for LT.

### N3: portal_theme v16.0.0 (January 2026) — v16 focus, v15 uncertain

**Sources:** Web Scout and Docs & Standards both found this.

Targets v16, not v15. Not relevant for LT at v15.105.0.

### N4: Frappe webshop rewrite discussion (July 2025)

**Source:** Web Scout.

Community thread documenting architectural criticism of current webshop (security, API design). No fork or replacement has shipped. LT will use the current webshop as-is.

### N5: Frappe Build 2026 conference (April 2-3, 2026) — ecosystem alive

**Source:** Web Scout.

Frappe held their annual developer conference weeks before this research — signaling active investment in the ecosystem. Not a technical finding, but confirms the platform is not abandoned.

---

## Approved Content for Q3

This section reconciles the two sources of "Jeff-approved" content: locallytwisted.com (Web Scout) and the legacy_source XML source (Ground Truth). These are materially different documents with the same customer.

### Where they agree (HIGH CONFIDENCE — use these)

| Content Element | locallytwisted.com | legacy_source XML |
|---|---|---|
| Phone | (801) 285-0860 | (801) 285-0860 |
| Hours | Tue-Fri 12-6pm, Sat 10-4pm, Mon closed | "Tue-Fri 12-6, Sat 10-4" |
| Location | West Jordan, UT / 8969 S 2700 W | "West Jordan, UT" |
| Service area | Salt Lake, Davis, Weber, Utah Counties | Same counties (header delivery strip references "Wasatch Front") |
| Owner credentials | "Over 22 years of experience" | "since 1998" (28 years) |
| Services offered | Arches, Garlands, Twisting, Face Painting | Same, plus Drops, Backdrops, Columns |
| Social proof | 40+ client logos | 52-name client crawl (FanX, Utah Jazz, Ancestry, Intermountain Health...) |
| Facebook | Listed | https://facebook.com/locallytwisted |
| Instagram | Listed | https://instagram.com/locally_twisted |
| Pinterest | Listed | https://pinterest.com/locallytwisted |
| Email (contact) | hi@locallytwisted.com (implied) | hi@locallytwisted.com (explicit in BTFP sidebar) |

**The founding year has a discrepancy:** locallytwisted.com says "Over 22 years" (which at 2024 ≈ 2002 founding). legacy_source XML says "since 1998" (28 years). The CLAUDE.md project brief confirms "27-year-old Utah balloon decor business" which corroborates 1998. The "22 years" on locallytwisted.com is stale. Use "since 1998" in the new build.

### Where they diverge (REQUIRES DECISION)

| Content Element | locallytwisted.com | legacy_source XML | Recommendation |
|---|---|---|---|
| Hero headline | "Make Your Party POP!" | "Utah's Balloon Specialists" | legacy_source XML is the new-build intent; more authoritative. Use "Utah's Balloon Specialists." |
| Hero sub | "Anything you imagine, we can shape into reality." | "Making celebrations unforgettable since 1998" | legacy_source XML — quieter, less pushy. Consistent with Quiet Confidence voice. |
| Social accounts | Facebook, Twitter, Instagram, Pinterest (4) | Facebook, Instagram, Pinterest (3, no Twitter) | Use legacy_source XML (3 icons). Ground Truth confirms Twitter was an error in prior script. Verify with GL. |
| Footer copyright | "Copyright 2021 Locally Twisted, LLC" | "© 2026 Locally Twisted. All rights reserved." | legacy_source XML — current year, cleaner format. |
| Review count | Not shown | 4.9 stars, 114 reviews (static badge) | legacy_source XML — include the badge. More credible than no reviews. |
| CTA copy | "Contact Us Today!", "Customize Your Order" | "Make Your Celebration Unforgettable" / "Contact Us" | legacy_source XML — quieter, less salesy. Better Quiet Confidence fit. |

### The authoritative approved content source for the ERPNext build

Per the LT CLAUDE.md "Reference Disposition" section: legacy_source XML source is the canonical source for the new build. The `locallytwisted.com` site is the old site, "damaged beyond repair" and out of scope for editing. The Ground Truth XML captures what the new build was designed to look like.

**Exception:** Contact info (phone, address, hours) should be verified against both — they agree, so the risk is low. The social account discrepancy (3 vs 4) requires GL clarification.

---

## Missing Options

Things the research brief expected and that NO researcher found:

**1. GitHub repos matching `frappe-theme-*`, `erpnext-website-*`, `frappe-website-template-*`**

The brief specifically asked researchers to check these patterns. Web Scout searched awesome-frappe (187 apps) and the Frappe Cloud Marketplace. No theme repos with these naming conventions were found. This is a genuine gap in the ecosystem — the repos do not appear to exist at production quality.

**2. Real business websites built on Frappe ERPNext (not just Frappe's own properties)**

Web Scout found frappe.io, fossunited.org, cloud.frappe.io — all Frappe's own sites. Wappalyzer shows 6,400 Frappe installs but the indexed high-traffic sites are Frappe's own. No third-party business (a balloon shop, a restaurant, a law firm) running Frappe as its public customer-facing website was found and confirmed. This is a meaningful ecosystem signal: Frappe is primarily used as a backend ERP with a website module, not as a public-facing website platform.

**3. Any evidence of Page Builder producing polished, mobile-responsive output in the wild**

No researcher found a screenshot, demo URL, or blog post showing a real website built with Frappe's Page Builder that looked polished. The official docs show it works; real-world validation is absent.

**4. A complete install + test procedure for Builder + webshop coexistence**

The brief anticipated someone might find community documentation confirming or denying this. No such documentation exists. This is genuinely uncharted territory.

**5. Per-template field schemas for the 23 built-in Web Templates**

Docs & Standards noted this gap explicitly: official docs do not publish what "Edit Values" shows for each template. Ground Truth's container inspection filled some of this in (Hero, Section with Cards, Section with CTA inspected) but not all 23. This is a minor gap — important for build planning but not for the architectural decision.

---

## Synthesis for Devil's Advocate

**The strongest overall picture:** The convergence is remarkable in what it rules OUT. All three sources independently reached the same conclusion: there are no ready-made Frappe v15 themes for a small-business marketing site; the Page Builder (legacy) is not the path forward for LT; the custom Frappe app with `web_include_css` is the correct baseline; the legacy_source XML content is a complete, WCAG-correct, Quiet Confidence-voiced blueprint ready to translate into ERPNext. The content problem is solved — the legacy_source XML files contain everything needed.

**The weakest link:** Frappe Builder. It is the only option that could meaningfully change the build approach (visual drag-drop vs code), and it is also the only option where the three sources diverge on what to do with it. Web Scout says "promising but carry risk"; Docs & Standards says "officially recommended but webshop cart integration is an unresolved feature request"; Ground Truth has no data because it hasn't been tried. The webshop routing question is genuinely open — no one knows if Builder pages at `/`, `/about`, `/contact` coexist cleanly with webshop at `/all-products`, `/cart`, `/checkout` on the same Frappe site. The risk of testing Builder and finding a conflict is that LT has spent time on a dead end when the custom-app path was always available.

**Where the devil's advocate should focus their challenge:**

1. **The "ecosystem thinness" conclusion is too comfortable.** If there are no good Frappe themes and the only path is custom code, LT may be better served by a different platform (Squarespace, Webflow, Shopify) for the public marketing site, with ERPNext as the backend only. The convergence analysis found that Frappe sites that look professional do so because of custom code investment — not because the platform provides good defaults. Is that level of investment justified for a small balloon business?

2. **The "custom app is already built" argument conflates scaffolding with substance.** Ground Truth confirmed: no Jinja template overrides, no www/ pages, no hero images, 28 `!important` occurrences including a broken navbar toggler, a placeholder homepage. "The architecture exists" and "the site works" are different claims. The devil's advocate should push: what is the gap between the current state and "polished, mobile-responsive, browser-tested"? That gap has not been measured.

3. **The legacy_source XML is not plug-and-play.** The content is ready. The images are not (legacy_source attachment IDs, not local files, may already be 404 from Hetzner). The category URLs use legacy_source numeric IDs that will not match ERPNext Item Group routes. The client crawl works in any environment. The hero carousel needs Bootstrap 5 markup (not the webshop Hero Slider template which uses Bootstrap 4). The devil's advocate should force the team to enumerate exactly which legacy_source XML sections can be directly translated versus which require work.

4. **Testing must happen in a real browser, not assumed.** Every prior failure (Slice 2, landing.py) was discovered by GL opening a browser and seeing something broken. The convergence analysis recommends the custom app path partly because it is the "safest" — but "safe" must be verified in practice. The devil's advocate should require: before any architectural decision is finalized, Stage 0 must be completed (strip !important chains, fix navbar toggler, verify clean render in Chrome at 375px mobile width).
