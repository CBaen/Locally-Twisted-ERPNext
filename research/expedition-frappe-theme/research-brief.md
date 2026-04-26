# Research Brief: Frappe v15 Customer-Facing Website — Theme + Approved Content Sourcing

## Date: 2026-04-26
## Project: Locally Twisted (BBC client, ERPNext v15 + Frappe v15 + webshop)

## Decision being informed

Choose how to build a polished, mobile-responsive customer-facing website on Frappe v15 + ERPNext v15 + the `webshop` app, for Locally Twisted (a 27-year-old Utah balloon decor + twisting + face painting business).

**System-native principle is non-negotiable** per GL directive 2026-04-26: *"Work WITHIN Frappe and ERPNext, don't fight them."* No Jinja template overrides of Frappe's own code, no `!important` CSS chains, no custom Web Templates if a community-vetted alternative exists.

The previous attempt — building a Web Page record with `content_type="Page Builder"` and Frappe's default Web Templates ("Hero with Right Image", "Section with Cards", "Section with CTA") + a thin LT theme CSS — produced a page that:
1. Was not visible to GL when opened in their actual browser (cards/sections not rendering despite being in DOM)
2. Was not mobile-responsive
3. Used made-up copy (the responsible instance invented "Make Your Celebration Unforgettable" etc. instead of pulling Jeff-approved content)

GL stopped the work and asked: there must be existing Frappe themes / GitHub repos / community templates / Frappe Marketplace themes / Substack or Reddit examples used by real businesses. Find them. Don't keep building from scratch with placeholders.

## What we need to learn

**Question 1 (PRIMARY):** What polished, responsive, customer-facing Frappe v15 website themes exist?
- Frappe Cloud Marketplace themes
- GitHub repos matching `frappe-theme-*`, `erpnext-website-*`, `frappe-website-template-*`, `frappe-saas-template`
- Themes used by real businesses (find live Frappe-built sites that look professional — what theme are they using?)
- Frappe community recommendations on discuss.frappe.io, Reddit r/frappe, Twitter/X #frappe, Substack
- Whether any pre-built theme is suitable for a small-business retail/service site
- Install path for each candidate (bench get-app + URL? Paid Marketplace? GitHub clone?)
- Maintenance/upgrade story for each (does it survive Frappe upgrades?)
- Mobile responsiveness OUT OF THE BOX

**Question 2 (PRIMARY):** What's the right pattern for customer-facing landing/marketing pages on Frappe v15 when polished design matters?
- Web Page DocType + Page Builder — what makes it actually render well? Is there a missing CSS bundle, a webshop-specific theme that needs activating, a Website Theme record that needs configuring?
- `Website Theme` DocType — what does it do, what fields does it expose, are there pre-built themes shipped or installable?
- `www/` static pages with hand-authored HTML — when do real Frappe-built marketing sites use this?
- Custom Web Templates in a custom app — when do real Frappe theme authors use these vs. Web Page Page Builder?
- The current LT site has the `locally_twisted` custom app installed with `web_include_css` registered for `/assets/locally_twisted/css/lt-theme.css`. Should we be using `website_theme_scss` instead? Or installing a theme that registers its own SCSS via the Website Theme DocType?

**Question 3 (SECONDARY but load-bearing):** Capture the Jeff-approved homepage content from the live Odoo at `http://5.78.136.133/` AND from the local Odoo project at `C:/Users/baenb/projects/locally-twisted-odoo/addons/locally_twisted/views/` (header.xml, footer.xml, homepage.xml). Output to a structured markdown so future build attempts use Jeff-vetted content, not invented copy.

## Constraints

- **System-native first.** No template overrides of Frappe's own code. No `!important` CSS chains. If a candidate theme requires those patterns, reject it.
- **Frappe v15.105.0** pinned. v16 not in scope.
- **Webshop installed and durable** — `apps/webshop/` + `apps/payments/` bind-mounted in pwd.yml. Any theme has to play nicely with `/all-products`, `/cart`, `/shop-by-category`, product detail pages.
- **Custom app `locally_twisted` exists** at `apps/locally_twisted/` — a theme could either replace its current minimal hooks.py + lt-theme.css OR layer on top.
- **Frappe Cloud cutover is Phase 6.** Whatever theme we pick must be transferable to a Frappe Cloud Sites plan ($5/mo per site).
- **Mobile responsive is non-negotiable.** Test against real screenshots, not assertions.

## Destructive boundaries

- Do NOT modify anything in `C:/Users/baenb/projects/locally-twisted-odoo/` (read-only reference per agency rule).
- Do NOT modify the Frappe / ERPNext source under `apps/frappe/` or `apps/erpnext/`.
- Do NOT add `!important` chains to LT theme CSS (that anti-pattern is named in `anti-gl-patterns.md` section 0).
- Do NOT generate new placeholder copy — the approved content already exists in Odoo and must be captured.

## Failed approaches

- **2026-04-26 Slice 2 build (prior session):** instance pushed CSS into `Website Settings.head_html` with `!important` overrides. Visible state broken. Documented in `_CLIENTS/locally-twisted/lessons-learned.md`.
- **2026-04-26 landing page (current session):** instance built Web Page record with `content_type="Page Builder"` + 4 Frappe default Web Templates + made-up copy. Not visible in real browser. Not mobile-responsive. Rolled back to placeholder. This brief is the recovery move.

## Convergence targets

1. **2-4 candidate Frappe themes** ranked by suitability (install instructions, demo URLs, maintenance status, license, pros/cons for LT specifically).
2. **A clear architectural pattern** for LT customer-facing pages — grounded in what real Frappe websites actually do, not hypothesis.
3. **The Odoo-approved homepage copy** captured into `_resources/approved-content/homepage.md`.
4. **A go/no-go on Page Builder** — if Page Builder is fine but a Website Theme step was missed, name it. If Page Builder is for internal pages and customer sites need a different pattern, name that pattern.

## Devil's Advocate concerns to surface

- The Frappe theme ecosystem may be small + unmaintained. If most Frappe websites look mediocre and there are no good themes, that's a critical finding (and may trigger the Phase 1 off-ramp away from ERPNext).
- A community theme might lock us into design choices that conflict with LT's STYLE-GUIDE.md (Quiet Confidence voice, Soft Blue palette, DM Serif Display + Raleway fonts).
- A community theme might not be webshop-compatible.
- "Just use a custom Web Template" might be the right answer but it then puts us back in custom-code territory — needs to be deliberate, not default.
