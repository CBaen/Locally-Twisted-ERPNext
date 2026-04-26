# Docs & Standards Findings: Frappe v15 Website Theming Official Patterns
## Date: 2026-04-26
## Source Type: Official Frappe / ERPNext Documentation + Marketplace + Official GitHub
## Researcher Role: Docs & Standards (official sources only)

## Sources Consulted

- https://docs.frappe.io/erpnext/user/manual/en/web-page-builder
- https://docs.frappe.io/erpnext/user/manual/en/website-theme
- https://docs.frappe.io/erpnext/web-page
- https://docs.frappe.io/erpnext/user/manual/en/homepage
- https://docs.frappe.io/framework/v15/user/en/portal-pages
- https://docs.frappe.io/framework/v15/user/en/guides/portal-development/generators
- https://docs.frappe.io/framework/user/en/python-api/hooks
- https://docs.frappe.io/framework/user/en/basics/asset-bundling
- https://docs.frappe.io/builder/introduction
- https://frappe.io/builder
- https://cloud.frappe.io/marketplace/apps/ecommerce_theme
- https://cloud.frappe.io/marketplace/apps/portal_theme
- https://cloud.frappe.io/marketplace/apps/business_theme_v14
- https://cloud.frappe.io/marketplace/apps/builder
- https://cloud.frappe.io/marketplace/search
- https://github.com/frappe/frappe/tree/version-15/frappe/website/web_template
- https://github.com/frappe/frappe/blob/version-15/frappe/website/doctype/web_page/web_page.json
- https://github.com/frappe/frappe/wiki/Migrating-to-version-15
- https://github.com/frappe/frappe/issues/22559 (v15 features list)
- https://github.com/frappe/frappe/issues/27107 (inter.css import bug v15.34)
- https://github.com/frappe/frappe/issues/28641 (primary color overwrite bug v15.48)
- https://github.com/frappe/frappe/issues/16564 (dynamic template / Jinja in Page Builder)
- https://github.com/frappe/builder (README)
- https://github.com/omfsakib/ecommerce-theme (README)
- https://awesome-frappe.gavv.in/
- https://discuss.frappe.io/t/confused-about-erpnext-web-page-builder-vs-frappe-build-vs-frappe-ui/141341
- https://discuss.frappe.io/t/website-theme-and-hooks-web-include-css-conflict/84622
- https://discuss.frappe.io/t/mobile-responsiveness/145935
- https://discuss.frappe.io/t/portal-theme-for-frappe/154892
- https://discuss.frappe.io/t/looking-for-expert-help-build-company-website-with-product-catalog-using-frappe-builder/144036
- https://frappeframework.com/version-15

---

## Officially Documented Approaches for Customer-Facing Sites

### Option A: Legacy Page Builder (Web Page DocType with content_type="Page Builder")

- **Source:** https://docs.frappe.io/erpnext/user/manual/en/web-page-builder
- **Authority Level:** Official ERPNext documentation
- **Frappe Version:** Introduced in v13. Still present and documented in v15.
- **Documented Since:** Version 13 (per doc: "Introduced in Version 13")
- **Fits LT case because:** Content-manager approach, no code required, usable via ERPNext Desk UI.
- **Limitations per docs:** Docs are thin. No mention of mobile responsiveness. No note about which templates are "polished" vs structural. The documentation notes the Published checkbox must be ticked — an obvious gotcha but one the brief confirms was a failure point. No Jinja in Page Builder blocks (separate GitHub issue confirms Jinja in Page Builder blocks does not evaluate — issue #16564, filed v13.25, still open, may affect v15).

---

### Option B: Frappe Builder (Separate Official App, published by Frappe Tech)

- **Source:** https://cloud.frappe.io/marketplace/apps/builder — published by Frappe Tech (official publisher), 22.7k installs, free, v15 and v16 supported
- **Authority Level:** Official Frappe product (Frappe Tech publisher), official marketplace listing
- **Frappe Version:** v15 and v16 and nightly
- **Documented Since:** Active separate app, actively maintained (repository updated April 2026 per search results)
- **Fits LT case because:** Figma-like visual editor, responsive design handling built in, high Lighthouse scores, officially recommended for customer-facing marketing/landing pages by community experts. Frappe.io itself (the company's own website) is built on Frappe Builder.
- **Limitations per docs/official sources:**
  - Mobile responsiveness is not automatic — requires deliberate design methodology (confirmed in official forum discussion, April 2025 thread). Desktop-designed pages need manual vertical-direction switching for mobile containers.
  - The official Builder README does not document webshop integration or compatibility. Shopping cart integration via webshop is an open feature request (issue #116, unresolved). Builder and webshop appear to be architecturally separate: Builder builds marketing/landing pages; webshop handles /all-products, /cart, /checkout routes. No official documentation of conflicts or confirmed clean coexistence.
  - Fresh-install access bug reported June 2024 (issue #172) involving `get_web_pages_with_dynamic_routes()` traceback — status unclear for v15.105.

---

### Option C: www/ Folder (Code-managed static/templated pages)

- **Source:** https://docs.frappe.io/framework/v15/user/en/portal-pages
- **Authority Level:** Official Frappe Framework v15 documentation
- **Frappe Version:** All versions; fundamental Frappe architecture
- **Documented Since:** Frappe v1 (foundational)
- **Fits LT case because:** Full control, version-controllable, can produce highly polished output.
- **Limitations per docs:** Requires developer to author HTML/Jinja. Not manageable by non-technical operators. Content updates require deployments. Only documented as the developer path, not the operator path.

---

### Option D: Website Theme DocType + web_include_css/website_theme_scss

- **Source:** https://docs.frappe.io/erpnext/user/manual/en/website-theme
- **Authority Level:** Official ERPNext documentation
- **Frappe Version:** v15 (theme system has existed since earlier versions, docs are version-unspecified)
- **Documented Since:** Pre-v15; present and documented in v15.
- **Fits LT case because:** Controls font, color palette, Bootstrap variable overrides across ALL website pages simultaneously — the right layer for brand consistency regardless of which page-building method is chosen.
- **Limitations per docs:** Known bug in v15.48.1 where `--primary` CSS variable is overwritten by Frappe's default (#171717) regardless of theme setting (issue #28641, open, no fix). Known import path failure in v15.34.1 where inter.css causes 404 (issue #27107, has workaround). When a Website Theme is active, `web_include_css` hook CSS stops loading (conflict documented in community forum, v13+ affected, mechanism not officially resolved for v15). CSS in the Website Theme renders BEFORE Frappe's bundled CSS in the cascade — confirmed in agency lessons-learned.

---

### Option E: Ecommerce Theme (Third-party Frappe Cloud Marketplace app)

- **Source:** https://cloud.frappe.io/marketplace/apps/ecommerce_theme
- **Authority Level:** Frappe Cloud Marketplace listing (third-party, not Frappe Tech official)
- **Frappe Version:** 15.x+ (explicit requirement)
- **Documented Since:** First release 2024, v1.0.1 October 2025
- **Fits LT case because:** Explicitly designed for webshop + frappe + erpnext + payments on v15. Provides custom navbar, footer, hero, product grid templates. Uses Tailwind CSS. Replaces webshop's default templates with a themed version.
- **Limitations per docs:** Paid app. 3 installs on Frappe Cloud — very low adoption. Publisher is an individual developer (omfsakib@gmail.com), not Frappe Tech. No demo URL. No screenshots in Marketplace listing. Uses Tailwind CSS (potentially conflicts with Frappe's Bootstrap 4 cascade). Requires `bench get-app` + `bench install-app` + `bench clear-cache` + `bench build` — full rebuild required.

---

### Option F: Portal Theme (Third-party Marketplace app)

- **Source:** https://cloud.frappe.io/marketplace/apps/portal_theme
- **Authority Level:** Frappe Cloud Marketplace listing (third-party)
- **Frappe Version:** v15 and v16
- **Documented Since:** Multiple releases (v1 and v2 documented in forum thread April 2025)
- **Fits LT case because:** Runtime CSS injection without asset rebuild. Manages portal styling (navbar colors, login page, buttons) through DocTypes. 48 active installs. 5.0 stars. Complementary to Website Theme (targets portal layer separately).
- **Limitations per docs:** Targets portal/login-page layer, not full customer-facing marketing page theming. Publisher is an individual developer, not Frappe Tech.

---

## Web Page DocType — Full Native Capability Map

Source: Official schema extract from `frappe/website/doctype/web_page/web_page.json` (version-15 branch) + official docs.

### Content Tab Fields
| Field | Type | Notes |
|-------|------|-------|
| title | Data | Required. Max SEO weight. Auto-generates route. |
| route | Data | Unique URL path. Editable. |
| published | Check | Must be ticked. Default: true per schema (but user must confirm). |
| show_title | Check | Controls title display in rendered page. |
| slideshow | Link → Website Slideshow | Conditional on content_type. |
| content_type | Select | Options: **Rich Text, Markdown, HTML, Page Builder, Slideshow**. Default: Page Builder. |
| main_section | Text Editor | Rich Text content. |
| main_section_md | Markdown Editor | Markdown content. |
| main_section_html | HTML Editor | Raw HTML content. |
| page_blocks | Table | Page Builder building blocks. Each row references a Web Template. |
| dynamic_route | Check | Enables URL parameters like `/project/<name>`. |
| dynamic_template | Check | Allows dynamic Jinja template rendering. NOTE: Confirmed broken for Page Builder content type (issue #16564, filed v13.25, open). |

### Script Tab
| Field | Type | Notes |
|-------|------|-------|
| javascript | Code | Custom JS. Must be in frappe.ready() callback per docs. |
| context_script | Code | Python script for setting template context. |

### Style Tab
| Field | Type | Notes |
|-------|------|-------|
| insert_style | Check | Enables custom CSS field. |
| css | Code | Custom CSS for this page only. |
| text_align | Select | Left, Center, Right. |
| full_width | Check | Default: true. |

### Settings Tab
| Field | Type | Notes |
|-------|------|-------|
| show_sidebar | Check | Toggle sidebar. |
| website_sidebar | Link → Website Sidebar | Custom sidebar links. |
| enable_comments | Check | Visitor comments (requires name + email). |
| idx | Int | Priority ordering (0 = highest). |
| header | HTML Editor | Custom header HTML (overrides page title display). |
| breadcrumbs | Code | JSON array for navigation breadcrumbs above header. |

### Meta Tags Section
| Field | Notes |
|-------|-------|
| meta_title | SEO page title. |
| meta_description | SEO description. |
| meta_image | Social sharing image (Attach Image). |

### Publishing Section
| Field | Notes |
|-------|-------|
| start_date | Datetime. Auto-publishes within range. |
| end_date | Datetime. Auto-unpublishes outside range. 404 when unpublished. |

### Page Builder Section Fields (per block row in page_blocks)
The official docs list these per-block configuration options (in addition to selecting a Web Template):
- Add Container (centers content in constrained box)
- Add Space on Top / Add Space on Bottom
- Add Gray Background
- Hide Block
- CSS Class (for per-block custom styling via the Style tab's CSS field)

---

## Website Theme DocType — Full Capability Map

Source: https://docs.frappe.io/erpnext/user/manual/en/website-theme

### Activation Path
Navigate to Website Theme list → New → configure → Save → set as active in Website Settings. Activation is a two-step process; saving the theme record does NOT activate it automatically.

### Tabs & Fields

**Theme Configuration Tab**
Bootstrapping wizard: select color schemes, fonts, and button styling through guided dropdowns. This tab generates the initial SCSS variable overrides.

**Stylesheet Tab**
| Field | Purpose |
|-------|---------|
| Custom Overrides | SCSS that is included BEFORE any app theme imports. Use to override `$variable` values. |
| Custom SCSS | SCSS that is included AFTER all app theme imports. Use for custom rules. |

**Included Theme Files Tab**
Lists all installed apps and their `[app]/public/scss/website.scss` files. Checkboxes control which app themes are included. For the LT stack: frappe, erpnext, webshop, locally_twisted app all appear here.

**Custom JS Tab**
JavaScript that runs when the theme is applied. Can manipulate DOM and styling dynamically.

### Bundled Themes
The official documentation does NOT list any bundled/pre-built themes that ship with Frappe or ERPNext v15. The Website Theme list starts empty. No official Frappe-shipped named themes for the website layer were found in documentation or the Frappe Cloud Marketplace.

### Compilation Behavior
The Website Theme SCSS is compiled server-side by Frappe when the theme is saved/activated. This does NOT require `bench build` (unlike app-level SCSS registered via `web_include_css` which points to pre-built CSS files). This is a key distinction: Website Theme uses Frappe's runtime SCSS compiler; `web_include_css` serves pre-built static files.

However: when a Website Theme is active, CSS registered via `web_include_css` in hooks.py stops loading (conflict documented, mechanism unresolved in official docs for v15). Recommended separation: use Website Theme for brand-level variables and Custom SCSS for site-wide overrides; use `web_include_css` only when no active Website Theme exists.

### Known Active Bugs (v15)
- v15.34.1: inter.css import 404 when custom theme extends Frappe theme (issue #27107). Workaround: use `@use` instead of `@import` for inter.css.
- v15.48.1: `--primary` CSS variable overwritten by Frappe's hardcoded #171717 regardless of theme setting (issue #28641). Open, no fix.

---

## Web Template DocType — Full Capability Map

Source: GitHub `frappe/frappe/tree/version-15/frappe/website/web_template` (authoritative — this is the actual shipped code)

### DocType Schema Fields
| Field | Type | Notes |
|-------|------|-------|
| type | Select | Options: Component, Section, Navbar, Footer. Default: Section. |
| standard | Check | Default: 0. If checked, module is required. |
| module | Link → Module Def | Required when standard=true. |
| template | Code (HTML) | Shown only when NOT standard (i.e., for custom templates). |
| fields | Table → Web Template Field | Defines the editable fields shown in the "Edit Values" dialog. |

Only System Manager role has CRUD permissions on Web Template.

### All Built-in Web Templates Shipping with Frappe v15

The following templates are confirmed present in the version-15 branch of frappe/frappe:

| Template Name | Type | Notes |
|--------------|------|-------|
| cover_image | Section | Full-width image cover |
| discussions | Section | Community/forum discussion embed |
| full_width_image | Section | Full-width image display |
| hero | Section | Basic hero section |
| hero_with_right_image | Section | Hero with image on right side |
| markdown | Section | Raw markdown content section |
| primary_navbar | Navbar | Primary navigation bar |
| section_with_cards | Section | Grid of cards |
| section_with_collapsible_content | Section | Accordion/FAQ style |
| section_with_cta | Section | Call-to-action section |
| section_with_embed | Section | Embed (iframe/video) section |
| section_with_features | Section | Feature list section |
| section_with_image | Section | Section with image |
| section_with_image_grid | Section | Grid of images |
| section_with_small_cta | Section | Smaller CTA variant |
| section_with_tabs | Section | Tabbed content |
| section_with_testimonials | Section | Testimonial/review section |
| section_with_videos | Section | Video grid section |
| slideshow | Section | Image slideshow |
| split_section_with_image | Section | Split layout with image |
| standard_footer | Footer | Standard site footer |
| standard_navbar | Navbar | Standard navigation bar |
| testimonial | Section | Single testimonial |

Total: 23 built-in templates. The prior LT attempt used 4 of these (hero_with_right_image, section_with_cards, section_with_cta, section_with_testimonials) — 19 additional templates were not explored.

### No Official Docs on Template Field Schemas
The official Page Builder documentation at docs.frappe.io does NOT publish the field schema for each individual Web Template (i.e., what "Edit Values" dialog shows for each template). This information is only accessible by: (a) inspecting the running Frappe instance, or (b) reading the individual `[template_name].json` files in the version-15 branch.

---

## Page Builder — How It Officially Works

Source: https://docs.frappe.io/erpnext/user/manual/en/web-page-builder + schema analysis

**Architecture:**
Web Page record (content_type="Page Builder") → page_blocks table → each row references a Web Template by name → "Edit Values" button opens dialog populated from the Web Template's `fields` definition → values stored as JSON in `web_template_values` field → Frappe renders the template Jinja HTML with those values at page load time.

**Official Statement from Docs:**
"The framework comes with a great set of Web Templates for you to create all sorts of pages."

**What "polished" means per official position:**
The official docs do not distinguish between "polished" and "barebones" templates. All 23 shipped templates are presented as equally usable. The quality gap the prior LT instance encountered (unstyled/non-responsive output) is NOT acknowledged in official documentation as a limitation — it is presented as a working feature.

**Is there an official theme Page Builder is meant to be paired with?**
No. The official documentation does not specify that Page Builder requires a specific Website Theme to produce polished output. The implication is that Page Builder uses whatever Website Theme is active (or Frappe's default theme if none).

**Known bug (Jinja in Page Builder):**
`dynamic_template` checkbox does not enable Jinja evaluation within Page Builder content blocks (issue #16564, v13.25, open). HTML content_type pages evaluate Jinja correctly; Page Builder blocks do not.

---

## web_include_css vs website_theme_scss

Source: https://docs.frappe.io/framework/user/en/python-api/hooks + https://discuss.frappe.io/t/website-theme-and-hooks-web-include-css-conflict/84622

| Hook | Purpose | Compilation | When to Use |
|------|---------|-------------|-------------|
| `web_include_css` | Injects pre-built CSS files into portal pages (`web.html`) | Requires `bench build` to compile SCSS → CSS first. Serves static files. | When delivering app-level portal CSS that must survive across all Website Theme configurations. But: conflicts with active Website Theme. |
| `website_theme_scss` | Registers an SCSS file that the Website Theme system includes in its compile chain | No `bench build` required — compiled by Frappe's runtime SCSS engine when theme is saved. | When delivering SCSS that should participate in Bootstrap variable theming. Must be activated via Website Theme record. |

**Official guidance on when to use which:** The official hooks documentation does NOT draw an explicit distinction between these two hooks or state which is preferred. The official Website Theme documentation recommends using Custom Overrides + Custom SCSS fields in the Website Theme DocType itself rather than relying on either hook for ad-hoc theming.

**The conflict (documented in community, no official fix):** When a Website Theme is active, `web_include_css` hook CSS stops loading. The mechanisms conflict. The resolution is to commit to one approach per project — either Website Theme (and configure everything in its SCSS fields) or `web_include_css` (and have no active Website Theme).

**Critical note for LT:** The CLAUDE.md agency recipe documents that `head_html` in Website Settings renders BEFORE Frappe's bundled CSS (cascade ordering). This is consistent with the above — CSS injection points have a specific cascade order and equal-specificity bundle rules silently win.

---

## Frappe Cloud Marketplace Themes

Source: https://cloud.frappe.io/marketplace/search + individual app pages

### Themes Relevant to Customer-Facing Website (not just Desk/admin)

| App | Publisher | Price | v15 Compatible | Installs | Stars | Focus |
|-----|-----------|-------|----------------|---------|-------|-------|
| **Frappe Builder** | Frappe Tech (official) | Free | Yes (v15+v16) | 22,700 | N/A | Full website builder — marketing pages |
| **Ecommerce Theme** | Individual (omfsakib) | Paid | Yes (v15.x+) | 3 | N/A | Webshop storefront theming via Tailwind CSS |
| **Portal Theme** | Individual (Sudhanshu Badole) | Paid | Yes (v15+v16) | 48 | 5.0 (2 reviews) | Portal/login page theming, runtime CSS |

### Desk/Admin Themes Only (not customer-facing website)
Business Theme v14 (free, v14 only — NOT v15 compatible), Tekton Theme (free), Material Theme (free), Desk Themes (v16), Owl Theme (v15 apps — desk). These style the ERPNext desk/admin interface, not the customer website.

### Official Frappe-Shipped Website Themes
None. Frappe does not ship any named pre-built website themes in the Marketplace. The Website Theme DocType exists, but the built-in theme is Frappe's default Bootstrap-based style. No official named alternatives (e.g., "Minimal", "Bold", "Ecommerce") exist in official channels.

### Install Path (Frappe Cloud)
For Frappe Cloud hosted sites (LT's Phase 6 destination): apps are installed via the Frappe Cloud dashboard → Apps section → add app from Marketplace. No bench commands needed. The site's apps list is managed through the UI.

---

## Recent Changes (Post May 2025)

Based on review of Frappe framework release pages (v15.100.0 through v15.106.0) and the v15 features issue (#22559):

**Website module changes added to v15 (from the features tracker):**
- Rebuild website search index in background (perf improvement)
- Add campaign/medium tracking to web page view
- Enqueue 'removing of index' on web page save (perf)
- Hook to add dynamic routes
- Lazy load SVG icons

**Website module changes in v15.100–v15.106:** None. Releases in this range focused on ERP (inventory, accounting, purchasing), API, form fields, and security. Zero website/Page Builder/Website Theme changes documented.

**Key finding:** The website/Page Builder/Web Template surface has been essentially frozen since approximately v15.50 or earlier. No feature additions were found between the training cutoff (May 2025) and v15.105.0. The Frappe team's website investment is in Frappe Builder (separate app), not the legacy Page Builder.

---

## Disconfirmation Search

### Official Limitations Found

1. **Page Builder rendering gap:** The official docs describe Page Builder as working. The real behavior (un-styled output, non-responsive blocks) is not documented as a limitation. This gap between documentation and behavior is confirmed by the prior LT build attempt and by the fact that Frappe is directing new website work toward Frappe Builder.

2. **Jinja not evaluated in Page Builder blocks:** Issue #16564 (filed 2022, open). Official documentation does not warn users that `dynamic_template` + Page Builder content type does not enable Jinja evaluation in template blocks.

3. **Website Theme known bugs in v15:**
   - Issue #27107 (v15.34.1): inter.css 404 path failure. Has workaround.
   - Issue #28641 (v15.48.1): `--primary` overwritten by Frappe default. Open, no fix as of search date.

4. **web_include_css conflict with Website Theme:** Documented in community. No official resolution.

5. **Page Builder described as legacy:** Community experts (including The Commit Company members on the official forum) state "Frappe Builder is the newer generation and replacement of the 'Web Page'" and that "The original Web Page Builder that ships with Frappe Framework is expected to be discontinued in favor of Frappe Builder." This is community-sourced, not from a Frappe official deprecation notice — but it aligns with zero new feature investment in Page Builder across all v15 releases reviewed.

### Official Deprecation Warnings Found
None formally issued for Web Page / Page Builder in v15. No official deprecation notice found in: release notes, migration guide, changelog issue, or docs.frappe.io documentation pages.

### Migration-Away Guides Found
None. The migration guide from v14→v15 mentions only one website change (native lazy-loading images). No guidance to move away from Page Builder.

### Open GitHub Issues Relevant to LT
- #16564: Dynamic template / Jinja in Page Builder blocks broken (v13+, open)
- #27107: inter.css 404 in Website Theme (v15.34, has workaround)
- #28641: Primary color overwritten in Website Theme (v15.48, open)
- builder #116: Shopping cart integration with webshop (open feature request — Builder does not natively integrate with webshop cart)
- builder #172: Builder not accessible on fresh install v15 (June 2024, status unclear)

---

## Gaps and Unknowns

1. **Frappe Builder + webshop coexistence:** The official documentation does not confirm or deny that Frappe Builder can be installed alongside webshop on the same site without routing conflicts. The two products appear architecturally separate (Builder owns arbitrary routes it creates; webshop owns /all-products, /cart, /checkout, /orders). No documented conflict found, but also no documented "these work together" confirmation. The shopping cart issue (#116) is the clearest signal: a Builder user wanted cart integration and it did not exist natively.

2. **Page Builder mobile responsiveness:** Official docs do not address this. The templates ship with Frappe's default Bootstrap 4 responsive grid, which in theory should be responsive — but the prior LT build confirmed they were not displaying correctly in a real browser. The root cause (was it the Published flag? the nginx Origin header? CSS cascade?) is not documented.

3. **Website Theme SCSS compilation in production (frappe_docker):** The official asset bundling docs confirm that `bench build` (Node) is required to compile app-level SCSS bundles. However, the Website Theme's SCSS is compiled by Frappe's Python-side SCSS compiler at save/activation time — NOT by Node. This distinction matters for frappe_docker (where Node is not in the production image). The Website Theme approach appears safe for production; `website_theme_scss` hook SCSS registered by app code requires `bench build` to produce the target CSS file that the hook references. This needs verification against actual frappe_docker behavior.

4. **Ecommerce Theme quality:** With 3 installs and no demo, it is impossible to verify "polished, mobile-responsive" from official sources alone. The README's claim of Tailwind CSS is a potential cascade conflict point with Frappe's Bootstrap 4 base.

5. **Web Template field schemas:** Official docs do not publish the field-level detail for each of the 23 built-in templates. Ground Truth researcher would need to inspect the running instance or the per-template JSON files in the repo.

---

## Synthesis

**What is the official Frappe answer for "how do I build a polished customer-facing site"?**

As of v15.105.0, there are TWO official answers depending on who in the Frappe ecosystem you ask:

**Answer 1 (ERPNext documentation, legacy path):** Use the Web Page DocType with content_type="Page Builder". Select Web Templates from the 23 built-ins. Publish with the Published checkbox. Apply a Website Theme for branding. This is the documented path in the ERPNext docs.

**Answer 2 (Frappe Tech product positioning, current direction):** Use Frappe Builder (the separate app, 22.7k installs, official publisher). It is described by community experts and positioned by Frappe as "the newer generation and replacement" of the legacy Page Builder. Frappe.io itself uses it. It handles mobile responsiveness by design. It produces lightweight, high-Lighthouse-score pages.

**The critical architectural conflict for LT:** Frappe Builder builds marketing/landing pages at arbitrary routes. Webshop owns /all-products, /cart, /checkout, /orders. There is no official documentation confirming these two can share a site cleanly. Shopping cart integration (Builder + webshop cart) is an open unresolved feature request.

**Go/No-Go on legacy Page Builder for LT:** The official docs say it works. The actual evidence says: (a) the LT prior attempt produced pages not visible in a browser; (b) Jinja doesn't work in Page Builder blocks; (c) zero new investment from Frappe since v13; (d) community calls it legacy/soon-deprecated. The root cause of the prior LT failure (Published checkbox? nginx Origin? CSS cascade?) is not Page Builder's fundamental architecture — it may be solvable. But choosing Page Builder over Frappe Builder requires solving the rendering mystery first.

**Go/No-Go on Frappe Builder for LT:** Technically strong, officially maintained, zero confirmed webshop routing conflicts in the documentation. The unknown is: can Builder marketing pages (/, /about, /contact, /gallery) coexist with webshop pages (/all-products, /cart, /checkout) on the same site? No official answer. Requires a test install or Ground Truth researcher to examine routing code.

**The Website Theme layer is orthogonal and recommended regardless of which builder is chosen:** It controls brand-level fonts, colors, and Bootstrap variable overrides across all website pages. It has known bugs in v15 that need workarounds, but it is the right tool for brand consistency and the official recommended approach for site-wide styling.
