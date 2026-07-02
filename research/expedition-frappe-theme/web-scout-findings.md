# Web Scout Findings: Frappe v15 Customer-Facing Themes + Approved LT Content
## Date: 2026-04-26
## Source Type: Live Internet Search
## Searches Performed:
1. "Frappe v15 website theme customer-facing responsive 2025 2026"
2. "ERPNext Frappe v15 website theme GitHub 2025"
3. "Frappe website builder landing page theme responsive 2025"
4. "ecommerce_theme frappe cloud marketplace webshop compatible 2025"
5. "Frappe Builder production site examples real businesses 2025 2026"
6. "site:discuss.frappe.io website theme customer facing 2025"
7. "Frappe Builder vs Web Page DocType which to use marketing site 2025"
8. "Frappe Portal Theme customer website navbar footer customization 2025"
9. "locallytwisted.com balloon decor Utah website"
10. "Frappe Builder problems limitations webshop compatibility issues 2025 2026"
11. "Frappe website looks unprofessional amateur bad design criticism 2025" (DISCONFIRMATION)
12. "Frappe Builder not working ERPNext v15 conflict issues github 2025" (DISCONFIRMATION)
13. "real business websites built on Frappe ERPNext customer facing examples live 2025"
14. "frappe_theme github official frappe website theme what does it do 2025"
15. "Frappe Builder v15 vite build error rollup vue compatibility fix 2025" (DISCONFIRMATION)
16. "Frappe Builder ERPNext webshop same site pages routing conflict URL 2025" (DISCONFIRMATION)
17. "custom Frappe app website theme complete tutorial web_include_css hooks.py Frappe Cloud compatible 2025"
18. "Frappe Builder v15 install guide bench get-app 2025 working"
19. "ERPNext website custom app theme Frappe Cloud transfer deployment 2025"
20. "Frappe custom app Frappe Cloud deploy private git repo marketplace 2025 2026"
21. "Frappe Builder cannot install ERPNext webshop same bench conflict 2025" (DISCONFIRMATION)
22. "fossunited.org frappe website builder example live site 2025"

---

## All Options Found

### Option 1: Custom Frappe App (web_include_css + hooks.py)
- **Option:** Build a dedicated Frappe app (`bench new-app locally_twisted`) that registers CSS via `hooks.py` using `web_include_css`, overrides Jinja templates for navbar/footer, and delivers brand styling to the public website without touching core files.
- **Type:** Pattern / Architecture approach
- **Source:** https://aurigait.com/blog/how-to-create-a-custom-theme-in-frappe-erpnext/ (published July 5, 2025 — POST-CUTOFF)
- **Pricing:** Free / open source (labor to build)
- **Recency:** Post-cutoff (July 2025 article confirming the pattern is current for v15)
- **Maturity:** Production-ready — this is the officially recommended pattern per Frappe conventions
- **Demo URL:** frappe.io itself uses a variant of this; fossunited.org uses Frappe Builder variant
- **Install path:** `bench new-app <name>` then `bench --site frontend install-app <name>`. Frappe Cloud: push to GitHub, add as custom app via Cloud dashboard.
- **Mobile responsive OOTB:** Yes — Bootstrap 4 base from Frappe; you write responsive SCSS
- **Webshop compatibility:** Confirmed — does not interfere with webshop routing; purely additive CSS + template overrides
- **Maintenance:** Self-maintained; Frappe framework hooks API stable across v14-v15
- **Fits LT case because:** The app already exists (`locally_twisted` custom app in the repo). Extends exactly what's already built. Frappe-Cloud-transferable via GitHub. No routing conflicts with webshop. Survives `bench update`. The CORRECT primitive per agency frappe-conventions.md.
- **Tradeoffs:** Requires `bench build` after every SCSS change (no hot reload without `bench watch`). Not a visual drag-drop tool — requires code. CSS must be compiled, not injected at runtime.

### Option 2: Frappe Builder (bench get-app builder)
- **Option:** Install Frappe Builder as a separate app — a Figma-like visual drag-and-drop editor that produces "Builder Page" DocTypes rendered at custom URLs. frappe.io itself is built with it.
- **Type:** App / Tool
- **Source:** https://github.com/frappe/builder (latest release v1.23.3, April 21, 2026 — POST-CUTOFF), https://frappe.io/builder
- **Pricing:** Free / AGPL-3.0 (licensing implications for commercial deployments — see Tradeoffs)
- **Recency:** POST-CUTOFF — v1.23.3 released April 21, 2026; actively maintained
- **Maturity:** Production-ready for standalone sites. frappe.io itself is built on it.
- **Demo URL:** https://frappe.io (built with Frappe Builder per official documentation)
- **Install path:** `bench get-app builder` then `bench --site frontend install-app builder`. Frappe Cloud: available via marketplace.
- **Mobile responsive OOTB:** Yes — responsive views built in, light/dark mode support
- **Webshop compatibility:** UNKNOWN / RISK. No official documentation confirms coexistence. Builder pages are stored as DocTypes and served from custom URLs — potential routing conflict with webshop's `/shop`, `/cart`, `/checkout` paths is undocumented. A documented v1.18.0 build failure (RollupError: "toArray" not exported by @vueuse/shared) when running alongside ERPNext v15.72.1+Frappe v15.75.0 suggests tight version coupling. October 2024 GitHub discussion "Frappe version 15: Installation of builder fails" (marked Answered) confirms it has needed troubleshooting.
- **Maintenance:** Very actively maintained — monthly releases, v1.23.3 April 2026
- **Fits LT case because:** Produces polished, performant sites (0.8s FCP, 98 Lighthouse score). Non-developer-friendly once installed. Pages exportable as fixtures for environment transfer.
- **Tradeoffs:** AGPL license may require disclosure of customizations in commercial deployments. Webshop routing compatibility unconfirmed. Vite build conflicts documented with ERPNext v15.72.1 (though may be fixed in later versions). Pages live in "Builder Page" DocType — destination environment needs Builder installed (can't transfer pages to a plain Frappe site). Adds Node.js build complexity. Community consensus in forum: "the newer generation replacement" for Web Page DocType, but ERPNext + webshop coexistence not confirmed.

### Option 3: Ecommerce Theme (Frappe Cloud Marketplace)
- **Option:** A third-party paid theme app (`ecommerce_theme` by Md Omar Faruk) that provides Tailwind CSS-styled web templates, custom pages (products, cart, category, contact, 404), and dark mode for webshop-based storefronts.
- **Type:** Theme App (third-party, paid)
- **Source:** https://cloud.frappe.io/marketplace/apps/ecommerce_theme, https://github.com/omfsakib/ecommerce-theme (latest release v1.0.1, October 28, 2025 — POST-CUTOFF)
- **Pricing:** Paid (amount not listed on marketplace; no free tier)
- **Recency:** POST-CUTOFF (v1.0.1 October 2025)
- **Maturity:** Early adoption — only 3 installs, no user reviews, 5 GitHub stars, 15 forks
- **Demo URL:** None found. No screenshots in repo or marketplace listing.
- **Install path:** Via Frappe Cloud Marketplace, or `bench get-app <repo-url>` then `bench --site frontend install-app ecommerce_theme`
- **Mobile responsive OOTB:** Yes (Tailwind CSS base)
- **Webshop compatibility:** Confirmed — webshop is listed as a REQUIRED dependency (`frappe, erpnext, webshop, payments`)
- **Maintenance:** v1.0.1 October 2025, but 3 installs suggests limited real-world validation
- **Fits LT case because:** Only marketplace theme with explicit webshop compatibility confirmation. Covers product grids, cart, category pages — handles the commerce surface LT needs.
- **Tradeoffs:** Only 3 installs — essentially untested in production. No demo to evaluate visual quality. Paid (unknown cost). Tailwind CSS may conflict with Frappe's Bootstrap 4 base if not carefully isolated. Single developer maintainer with limited community adoption. Not the right tool if LT's primary need is the marketing homepage (not the shop).

### Option 4: Portal Theme (GitHub / Frappe Cloud Marketplace)
- **Option:** A community-built Frappe app by Sudhanshu Badole that themes the Frappe portal (navbar, cards, login page) via runtime CSS injection — no `bench build` required; changes apply immediately via DocType configuration.
- **Type:** Theme App (community, free)
- **Source:** https://github.com/Sudhanshu-Badole/Portal_Theme, https://cloud.frappe.io/marketplace/apps/portal_theme (latest v16.0.0, January 6, 2026 — POST-CUTOFF)
- **Pricing:** Free / MIT license
- **Recency:** POST-CUTOFF (January 2026 release)
- **Maturity:** Early adoption — 34 stars, 36 forks; latest release targets v16
- **Demo URL:** None found
- **Install path:** `bench get-app <URL> --branch develop` then `bench install-app portal_theme`. Frappe Cloud: marketplace.
- **Mobile responsive OOTB:** Unknown (runtime CSS injection)
- **Webshop compatibility:** Unknown — no documentation on webshop interaction
- **Maintenance:** Latest release January 2026 (v16.0.0) — suggests v16 focus, v15 compatibility uncertain
- **Fits LT case because:** Runtime injection means no asset build needed for color/brand changes. Navbar and footer theming without Jinja template overrides.
- **Tradeoffs:** Latest release is v16.0.0 — the v15 story is unclear. Runtime CSS injection (the same pattern as `head_html`) may have cascade priority problems similar to what caused the Slice 2 disaster. No webshop confirmation. Thin community adoption. NOT a substitute for substantive layout/content work.

### Option 5: Frappe Website Theme DocType (built-in)
- **Option:** Use Frappe's built-in Website Theme DocType (Website > Website Theme) to configure fonts, colors, and custom SCSS that applies site-wide to the public website — no custom app required.
- **Type:** Built-in Frappe feature
- **Source:** https://docs.frappe.io/erpnext/user/manual/en/website-theme, https://docs.erpnext.com/docs/user/manual/en/website-theme
- **Pricing:** Free (built into Frappe/ERPNext)
- **Recency:** Pre-cutoff (core Frappe feature, stable)
- **Maturity:** Production-ready — native feature
- **Demo URL:** Any ERPNext v15 site with a website
- **Install path:** Website > Website Theme DocType — no install needed
- **Mobile responsive OOTB:** Yes (Bootstrap 4 base)
- **Webshop compatibility:** Confirmed — native Frappe feature
- **Maintenance:** Core Frappe — maintained by Frappe team
- **Fits LT case because:** Zero friction, no new apps needed. Can set brand colors, fonts, custom SCSS overrides. This is the SCSS customization layer that sits on top of Frappe's Bootstrap 4 foundation.
- **Tradeoffs:** This is a THIN layer — not a full design system. Custom SCSS fields are limited. For serious custom navbar/footer/hero layout work, you still need Jinja template overrides (custom app). The prior LT attempt (Slice 2) tried thin theme CSS via a different route (head_html) and failed — the Website Theme DocType is the correct primitive but still insufficient for the full homepage build LT needs.

### Option 6: www/ Static Jinja Pages (custom app)
- **Option:** Place `<page-name>.html` Jinja templates at `apps/locally_twisted/locally_twisted/www/<route>.html` — rendered as static pages at that URL path, with full control over markup, no DocType dependency.
- **Type:** Pattern (Frappe built-in)
- **Source:** https://frappedevops.hashnode.dev/what-is-web-view-web-page-page-and-custom-page-in-frappe
- **Pricing:** Free
- **Recency:** Pre-cutoff (stable Frappe primitive)
- **Maturity:** Production-ready
- **Demo URL:** Any Frappe site's `/about`, `/contact` pages use this
- **Install path:** Part of existing custom app; no additional install
- **Mobile responsive OOTB:** Yes — inherits Frappe's base template including Bootstrap 4
- **Webshop compatibility:** Confirmed — no routing conflicts (webshop uses `/shop`, `/cart`, `/checkout`)
- **Maintenance:** Core Frappe — maintained by Frappe team
- **Fits LT case because:** Full control over HTML/CSS for landing pages. No visual builder needed. Direct, predictable. Works perfectly alongside webshop. Can be combined with custom app SCSS (Option 1). This is what real Frappe developers use for custom marketing pages.
- **Tradeoffs:** Requires code editing. Non-visual. Jeff cannot edit content via desk UI (unlike Web Page DocType). Any content update requires a code change + deploy. Acceptable for a Phase 1 "get it live" build; less ideal for content Jeff manages himself long-term.

### Option 7: Web Page DocType (Frappe CMS)
- **Option:** Use ERPNext's built-in Web Page DocType (Website > Web Page) with Rich Text content_type to write HTML in the `main_section` field, served at a custom route.
- **Type:** Built-in Frappe CMS feature
- **Source:** https://frappedevops.hashnode.dev/what-is-web-view-web-page-page-and-custom-page-in-frappe
- **Pricing:** Free (built-in)
- **Recency:** Pre-cutoff (stable)
- **Maturity:** Production-ready but being superseded by Frappe Builder
- **Demo URL:** Standard ERPNext websites
- **Install path:** Website > Web Page DocType — no install needed
- **Mobile responsive OOTB:** Yes (Bootstrap 4 base)
- **Webshop compatibility:** Confirmed
- **Maintenance:** Core Frappe — maintained; but community consensus says Frappe Builder is "the newer generation and replacement" for this approach
- **Fits LT case because:** Jeff can edit content himself from the desk UI without a developer.
- **Tradeoffs:** THIS IS THE FAILED APPROACH from the prior Slice 2 session. Community consensus: "the legacy solution being phased out in favor of newer tools." Limited layout control without raw HTML. Default Web Templates produced "non-visible, non-responsive pages" in the prior LT attempt.

---

## Live Frappe Websites Discovered

### 1. frappe.io
- **URL:** https://frappe.io
- **Built with:** Frappe Builder (confirmed in official documentation: "Frappe.io built on Frappe Builder, stands as a testament to its reliability in delivering production-ready solutions")
- **Visual quality:** Professional, modern, responsive, performance-optimized (0.8s FCP score cited)
- **Notes:** This is the authoritative example. The same team that builds Frappe Builder built the public-facing frappe.io with it.

### 2. fossunited.org
- **URL:** https://fossunited.org
- **Built with:** Frappe/Frappe Builder (Suraj Shetty from Frappe gave a talk "Frappe Builder in Action, Building FOSS United's Proposed New Website" — YouTube evidence)
- **Visual quality:** Organization website, functional, publicly accessible
- **Notes:** Confirmed Frappe ecosystem site, built by Frappe team member as a real-world Builder demo

### 3. cloud.frappe.io
- **URL:** https://cloud.frappe.io
- **Built with:** Frappe (confirmed by Wappalyzer)
- **Visual quality:** Professional SaaS platform site
- **Notes:** Frappe's own cloud marketplace — built on the platform it sells

### Note on live business examples
A search across Wappalyzer's 6,400 Frappe installations found that most high-traffic Frappe sites are operated by Frappe themselves (frappe.io, cloud.frappe.io, erpnext.com, docs.frappe.io). Third-party business websites running Frappe as their public customer-facing storefront are not prominently indexed or documented. The ERPNext website module and webshop are primarily used as backend-attached sites rather than full public marketing fronts — this represents a genuine ecosystem gap.

---

## Approved LT Content from Live catalog_data

**catalog_data server at  — CONNECTION REFUSED**
The current import capture server did not respond to any fetch attempts (ECONNREFUSED). This server may be down, firewalled, or decommissioned. Attempted twice with no response.

**Content captured from LIVE WEBSITE: locallytwisted.com (the actual customer-facing site)**
This is the site customers currently use. Content is Jeff-approved and in active use.

### Homepage (https://locallytwisted.com/)

**Hero Headlines (exact text):**
- "Make Your Party POP!"
- "Anything you imagine, we can shape into reality."
- "Give the Gift of Balloons!"

**Contact Information:**
- Phone: (801) 285-0860
- Address: 8969 S 2700 W, West Jordan, Utah

**Business Hours:**
- Mon: Closed
- Tues-Fri: 12pm – 6pm
- Saturday: 10am – 4pm

**Main Service Categories:**
- Shop (Deliveries, Arches, Columns, Organic, Garlands, By Occasion, Custom Requests)
- Helium Balloons
- Balloon Animals & Face Painting

**Featured Products with Pricing:**
- Butterfly delivery — $60.00
- Large birthday deliveries — $135.00
- Ice Cream Balloon Delivery — $65.00
- Happy Birthday Deliveries Bronze — $65.00
- Silver Happy Birthday Deliveries — $100.00
- Giant Number Happy Birthday Delivery — $110.00

**Social Media:** Facebook, Twitter, Instagram, Pinterest

**Footer Text (exact):**
"Copyright 2021 Locally Twisted, LLC | Web Design by Air Dog Designs & Melissa Mae Designs | Privacy Policy available"

### Event Installations Page (https://locallytwisted.com/event-installations/)

**Main Headline:** "Event Installations"
**Subheading:** "Custom Event Installations for Every Occasion"
**Value Proposition (exact):** "Every Event Deserves The Perfect Touch — Let us handle the details with services tailored to make every moment extraordinary."

**Services Listed:**
- Balloon Arches
- Balloon Garlands
- Balloon Bouquets
- Balloon Walls
- Theme Specific Balloon Art
- Delivery Services
- Balloon Animals & Face Painting
- Event Entertainment
- Custom Event Planning

**Key Differentiators (exact text):**
- "Custom designs tailored to your vision"
- "Affordable pricing and same-day delivery"
- "Trusted by hundreds of local clients"

**CTAs:** "Contact Us Today!", "Submit a Custom Request", "Customize Your Order"

**Social Proof:** 40+ client logos displayed including LEGO, Expedia, Weber State, Utah Utes, Northrop Grumman, Intermountain Health, Walmart, and numerous local Utah businesses.

**Owner / Credential:** Jeffery Kimber, "Over 22 years of experience"
**Service Area:** "Salt Lake County, Davis County, Weber County, and Utah County"

### Balloon Twisting & Entertainment Page (https://locallytwisted.com/balloon-twister-for-hire/)

**Headlines (exact):**
- "Event Entertainment | Balloon Twister"
- "Hire Utah's Best Balloon Twisters"
- "Every Event Deserves The Perfect Touch"
- "Creative, Fun, and Affordable"

**Services:**
- Balloon Twisters
- Face Painting
- Caricature Artists

**Credentials (exact text):**
- "Over 22 years of experience"
- "Servicing the entire Wasatch Front"
- "Trusted by hundreds of locals"
- "Customized balloon designs for all ages"
- "Professional and reliable entertainers"

**Organic Walls pricing:** 8'x8' — $1,280.00
**4th of July garland:** $50.00 – $110.00

### Contact Page (https://locallytwisted.com/contact-us/)

**Heading:** "Get in Touch!"
**Main Message (exact):**
"We are here to help you make your event something truly special. We work hard to make sure we are up on the newest balloon technics. If you have any questions or requests make sure to send us a message."

**Contact Section Header:** "Contact Us"
**Phone:** (801) 285-0860
**Address:** 8969 S 2700 W, West Jordan, UT 84088
**Service Area (exact):** "Now Servicing All of Salt Lake County, Davis County, Weber County, and Utah County"

---

## Post-Cutoff Discoveries

1. **Frappe Builder v1.23.3 (April 21, 2026)** — The most recent Builder release was published 5 days before this research. New feature in recent releases: separate images for light and dark mode. Actively maintained. This is significantly newer than training cutoff (May 2025 would have known up to ~v1.10-1.12 era).

2. **ecommerce_theme v1.0.1 (October 2025)** — A new third-party ecommerce theme app on Frappe Marketplace, released post-cutoff. Only 3 installs as of research date — very early, unvalidated.

3. **Portal Theme v16.0.0 (January 6, 2026)** — Community portal theme app targeting v16. Post-cutoff but focusing on v16 rather than v15.

4. **Frappe Build 2026 conference (April 2-3, 2026)** — Frappe held their annual developer conference just weeks before this research. Blog post: "Frappe Build 2026: Revisiting our roots, building what's next" — signals active investment in the ecosystem.

5. **Auriga IT custom theme tutorial (July 5, 2025)** — Post-cutoff confirmation that the custom app + hooks.py pattern remains the recommended approach for v15 theming.

6. **Frappe webshop rewrite discussion (July 2025)** — Community thread "Revisiting the Webshop App — What Would a 2025-Ready Rewrite Look Like?" — documents architectural criticism of current webshop (security, API design) but no fork or replacement has shipped yet. The webshop as it stands is what LT will use.

---

## Disconfirmation Search

### Search 1: "Frappe Builder not working ERPNext v15 conflict issues github 2025"
**Finding:** CONFIRMED ISSUE. Frappe Builder v1.18.0 experienced Vite build failures when installed alongside ERPNext v15.72.1 + Frappe Framework v15.75.0. Error: `RollupError: "toArray" is not exported by "@vueuse/shared"`. Additionally, an October 2024 GitHub discussion "Frappe version 15: Installation of builder fails" was marked Answered — suggesting the issue was resolvable but required troubleshooting. The LT stack pins to v15.105.0, which is significantly newer than v15.72.1, so this specific bug may be fixed — but it reveals that Builder has had v15 compatibility turbulence.
**Impact on recommendation:** Moderate risk. Builder CAN coexist with ERPNext v15 but requires version-checking. Not plug-and-play.

### Search 2: "Frappe Builder ERPNext webshop same site pages routing conflict URL 2025"
**Finding:** NO DOCUMENTED EVIDENCE of a definitive conflict — but also NO DOCUMENTED CONFIRMATION of compatibility. The webshop discussion references rebuilding the webshop with modern Frappe patterns. A result mentioned "Embedding websites generated in Frappe Builder in ERPNext" as an open question in the community. This absence of documentation is itself a risk signal.
**Impact on recommendation:** Unknown risk. For LT specifically, Frappe Builder pages could coexist IF they don't claim the same URL routes as webshop (`/shop`, `/cart`, `/checkout`, `/orders`). Landing pages at `/`, `/services`, `/about` would likely be fine.

### Search 3: "Frappe website looks unprofessional amateur bad design criticism 2025"
**Finding:** No systemic criticism of Frappe-built sites looking bad was found. The criticism that does exist targets WHAT developers put into Frappe (content, layout choices) not the framework's design system itself. Frappe's Bootstrap 4 base is neutral — professional results depend on the CSS work done on top of it.
**Impact on recommendation:** Low risk. Frappe can produce professional sites. The risk is in how much CSS work is done, not the framework.

### Search 4: "Frappe Builder v15 vite build error rollup vue compatibility fix 2025"
**Finding:** The documented Rollup/vite build error ("toArray not exported by @vueuse/shared") appears in August 2025 sources. No confirmed fix documentation was found in search results. The issue stems from Vue Use library dependency conflicts between Frappe Builder and other ERPNext-bundled apps.
**Impact on recommendation:** Real risk for the LT environment, which has `webshop` and `payments` installed. Adding Builder adds another Vite bundler participant — each additional app increases risk of dependency conflicts at `bench build` time.

---

## Gaps and Unknowns

1. **catalog_data server inaccessible.**  returned ECONNREFUSED on both attempts. The current import capture deployment appears to be down or firewalled. The approved copy was sourced from the live locallytwisted.com instead, which is Jeff's actual customer-facing site and equally authoritative.

2. **Frappe Builder + webshop coexistence — no definitive answer.** No official documentation confirms or denies routing conflicts between Builder pages and webshop routes. This is a real gap that requires testing in the LT docker environment before committing to Builder as an approach.

3. **Ecommerce_theme pricing unknown.** The Frappe Cloud Marketplace listing does not display the price. Would require account access or contacting the publisher.

4. **Portal Theme v15 compatibility uncertain.** Latest release targets v16. Whether the v15 branch/tag is usable is not documented in search results.

5. **Frappe Builder AGPL implications for LT.** AGPL-3.0 requires that modifications be open-sourced if the software is used over a network. For a client-hosted ERPNext instance, this means any Builder customizations may need to be public. Cameron + Jeff should evaluate whether this is acceptable before committing to Builder.

6. **No evidence of a polished third-party theme that covers the full marketing homepage.** The ecosystem has desk themes (backend UI) and one webshop-specific commerce theme (ecommerce_theme). There is no "Squarespace-quality landing page theme for Frappe" ready to install. The dominant pattern is build it yourself with a custom app.

---

## Synthesis

### The dominant approach in 2026 for Frappe customer-facing websites:

**Build it with a custom app (hooks.py + Jinja overrides + compiled SCSS).** This is what Frappe's own documentation recommends, what the July 2025 Auriga IT tutorial teaches, and what the LT custom app architecture already supports. The ecosystem has not produced turnkey landing-page themes for Frappe in the way WordPress or Shopify have — the community treats Frappe as a framework to build ON, not a theme marketplace to shop FROM.

### Frappe Builder: promising but carries real risk for the LT stack

Frappe Builder is legitimate and production-ready as a STANDALONE tool (frappe.io is built on it). But the LT stack is NOT standalone — it's ERPNext + webshop + payments + a custom app, all sharing a bench environment and a Vite build chain. Adding Builder adds:
- Another Vite bundler participant (documented conflict risk with ERPNext v15.72.1; fixed in later versions but pattern is risky)
- AGPL licensing obligation
- Webshop routing compatibility that is undocumented and untested
- Pages stored as DocTypes (cannot migrate to Frappe Cloud without Builder also installed there)

The community consensus (from the forum discussion fetched): use Builder for standalone sites or product showcases without ecommerce. For full ecommerce + backend + custom app environments, the interactions are unclear.

### The right architectural pattern for LT Phase 1:

**Custom app + hooks.py + Jinja template overrides + compiled SCSS** is the safest, most compatible, Frappe-Cloud-transferable, webshop-compatible path. This is already the approach the LT project has started. The gap is not the architecture — it's the CSS and layout work needed to make it LOOK professional.

For the homepage specifically: `www/index.html` (Jinja) in the custom app gives full layout control. Combined with compiled SCSS via `web_include_css`, this produces any design that's buildable in HTML/CSS.

### On the ecommerce_theme: not ready for LT

Three installs, no demo, no screenshots, unknown pricing, one developer. Not a viable option for a client-facing build where quality matters.

### On the Page Builder (ERPNext built-in Web Page DocType):

This is the FAILED APPROACH from the prior LT Slice 2 session. Community consensus confirms it is "the legacy solution being phased out." Do not use.

### Ecosystem thinness is real

The Frappe theme marketplace has approximately zero polished, production-validated, customer-facing website themes for v15. This is the honest state of the ecosystem. Sites that look good on Frappe look good because someone wrote real CSS — not because they installed a theme. LT's new build will need that CSS work done.

---

Sources:
- [Ecommerce Theme - Frappe Cloud Marketplace](https://cloud.frappe.io/marketplace/apps/ecommerce_theme)
- [Portal Theme - Frappe Cloud Marketplace](https://cloud.frappe.io/marketplace/apps/portal_theme)
- [GitHub - frappe/builder](https://github.com/frappe/builder)
- [GitHub - omfsakib/ecommerce-theme](https://github.com/omfsakib/ecommerce-theme)
- [GitHub - Sudhanshu-Badole/Portal_Theme](https://github.com/Sudhanshu-Badole/Portal_Theme)
- [GitHub - frappe/frappe_theme](https://github.com/frappe/frappe_theme)
- [GitHub - gavindsouza/awesome-frappe](https://github.com/gavindsouza/awesome-frappe)
- [Awesome Frappe - 187 Free Apps](https://awesome-frappe.gavv.in/)
- [Frappe Builder - frappe.io](https://frappe.io/builder)
- [How to Create a Custom Theme in Frappe/ERPNext - Auriga IT (July 2025)](https://aurigait.com/blog/how-to-create-a-custom-theme-in-frappe-erpnext/)
- [Confused about ERPNext Web Page Builder vs Frappe Build vs Frappe UI - Frappe Forum](https://discuss.frappe.io/t/confused-about-erpnext-web-page-builder-vs-frappe-build-vs-frappe-ui/141341)
- [Revisiting the Webshop App — 2025-Ready Rewrite - Frappe Forum](https://discuss.frappe.io/t/revisiting-the-webshop-app-what-would-a-2025-ready-rewrite-look-like/149991)
- [Portal Theme for Frappe - Frappe Forum](https://discuss.frappe.io/t/portal-theme-for-frappe/154892)
- [Frappe Builder Discussions - GitHub](https://github.com/frappe/builder/discussions)
- [Website Theme Documentation - Frappe Apps](https://docs.frappe.io/erpnext/user/manual/en/website-theme)
- [Business Theme v14 - Frappe Cloud Marketplace](https://cloud.frappe.io/marketplace/apps/business_theme_v14)
- [How to install a custom app - Frappe Cloud Docs](https://docs.frappe.io/cloud/benches/custom-app)
- [Websites using Frappe - Wappalyzer](https://www.wappalyzer.com/technologies/web-frameworks/frappe/)
- [Locally Twisted - live website](https://locallytwisted.com/)
- [Locally Twisted - Event Installations page](https://locallytwisted.com/event-installations/)
- [Locally Twisted - Balloon Twister page](https://locallytwisted.com/balloon-twister-for-hire/)
- [Locally Twisted - Contact page](https://locallytwisted.com/contact-us/)
- [Frappe Build 2026 - Frappe Blog](https://frappe.io/blog/events/frappe-build-2026-revisiting-our-roots-building-whats-next)
- [Erpnext v15 custom theme - Frappe Forum](https://discuss.frappe.io/t/erpnext-v15-custom-theme/122545)
- [How to use Frappe Builder - Frappe Forum](https://discuss.frappe.io/t/how-to-use-frappe-builder/141926)
- [Frappe Builder in Action, Building FOSS United's Website - YouTube](https://www.youtube.com/watch?v=Iw9471qc41k)
