---
id: frappe-public-container-contract
name: Frappe Public Container Contract
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted ERPNext/Frappe public page shell, full-bleed sections, Webshop containment, and container ownership
currently_true: yes
verification_level: 2
last_verified: 2026-05-06
evidence_quality: direct
successful_uses: 1
failed_uses: 0
regressions: 0
depends_on: []
used_by:
  - responsive-container-audit
  - frappe-shop-showroom-symmetry
  - frappe-sitewide-visual-overhaul
  - cross-browser-motion-visual-verification
tags:
  - Locally Twisted
  - Frappe
  - ERPNext
  - Webshop
  - container integrity
  - public site
---

# Frappe Public Container Contract

Use this recipe before changing public layout, full-bleed sections, crawls, carousels, Webshop surfaces, route templates, or shared CSS that changes how a page sits inside Frappe.

## Current Contract

Frappe provides the website lifecycle and wrapper. LT owns the visual containment inside that wrapper.

In installed Frappe v15, normal website pages extend `templates/web.html` and render:

- `.page-content-wrapper`
- `main.container.my-4` unless the page sets `full_width`
- `.page-header-wrapper`
- `.page_content`
- `.page-footer`

Frappe's website SCSS gives `.container` responsive horizontal padding and adds `.page-content-wrapper .container` padding at widths below the `lg` breakpoint.

LT currently neutralizes the stock Frappe visual box in `lt-theme.css`:

- `.page-content-wrapper .container`
- `.page-content-wrapper main.container`

Those rules set the page wrapper to `max-width: 100%` and zero horizontal padding. That means the stock Frappe `main.container` is still present in the DOM, but it is not the visual box that should protect the design. LT sections must provide their own containment.

`lt-page-containment.css` is the active LT containment layer. It defines gutters, max widths, full-bleed breakouts, and inner wrappers for LT pages.

## Layout Modes

Every public section must choose one of these modes before CSS is written.

**Contained workflow or reading surface**

Use this for forms, policy pages, FAQ content, cart, checkout, product detail, product grids, and dense operator/customer workflows.

- Preserve Frappe/Webshop structure and class hooks.
- Use an inner wrapper such as `.lt-<block>__inner`, `.lt-checkout__container`, `.lt-cart__container`, `.product-container`, or `.cart-container`.
- Use `width: min(<max>, 100%)`, `margin-inline: auto`, stable gutters, `box-sizing: border-box`, and `min-width: 0`.
- Do not depend on the global Frappe `main.container` to provide readable width because LT has neutralized it.

**Deliberate full-bleed band**

Use this only for intentional visual bands: hero, proof ribbon, image band, review marquee, client crawl, category band, or CTA.

- Use `.lt-fullbleed` or the shared containment-layer pattern.
- Put readable content inside an inner wrapper with max width and gutters.
- Do not put fixed-width tracks, cards, text, or images directly against the viewport without an inner containment decision.
- Animated tracks must clip intentionally and must not expose native horizontal scrollbars unless GL explicitly accepts that behavior.
- A full-bleed section is not permission for the whole page to feel detached from Frappe's page rhythm.

## Frappe And ERPNext Contracts To Preserve

- Website pages should keep using Frappe/Jinja routes under `apps/locally_twisted/locally_twisted/www/` unless a specific Frappe hook says otherwise.
- Shared website CSS and JS belong in the app and must be wired through `web_include_css` / `web_include_js` in `hooks.py`.
- Header/footer changes should use Jinja partial overrides, not page-local hacks.
- Webshop product, listing, cart, checkout, and add-to-cart behavior depends on existing Webshop templates, selectors, and JS hooks. Do not remove or rename native classes just to make styling easier.
- Webshop product detail uses `.product-container`; bundled cart uses `.cart-container`; LT's custom guest cart uses `.lt-cart__container`. These surfaces need explicit max-width containment because LT removed the stock Frappe wrapper width.
- Webshop shop/category pages must preserve listing, filter, product-card, and product-list update hooks. Visual repairs should rebalance rows and containment around those hooks instead of replacing the product pipeline.
- Dashed customer URLs that map to underscored Python modules belong in `website_route_rules`.
- After `hooks.py`, Jinja, controller, or CSS edits, clear Frappe website cache and restart the affected containers when hook/controller import state changed.

## Research Checked

Checked on 2026-05-06 against the running local stack:

- Frappe source in container: `/home/frappe/frappe-bench/apps/frappe/frappe/templates/web.html`
- Frappe website SCSS in container: `/home/frappe/frappe-bench/apps/frappe/frappe/public/scss/website/index.scss`
- Webshop templates in container: `webshop/templates/generators/item_group.html`, `webshop/templates/generators/item/item.html`, and `webshop/templates/pages/cart.html`
- LT theme source: `apps/locally_twisted/locally_twisted/public/css/lt-theme.css`
- LT containment layer: `apps/locally_twisted/locally_twisted/public/css/lt-page-containment.css`
- LT hooks: `apps/locally_twisted/locally_twisted/hooks.py`
- Live browser probe at `http://localhost:8081/`, `/all-products`, and `/cart`: `main.container.my-4` was present, computed at full viewport width with `max-width: 100%`, zero horizontal padding, and no document-level horizontal overflow at 1366px.

## Decision Pattern

1. Read the style guide and identify the page family: static marketing page, Webshop listing, product detail, cart/checkout, form, policy, or motion/crawl.
2. Inspect the rendered DOM before editing shared CSS. Confirm whether the section is inside Frappe's normal `main.container`, a Webshop template, or an LT custom route.
3. Classify each changed section as contained workflow/reading surface or deliberate full-bleed band.
4. Preserve Frappe/Webshop hooks first; wrap or style around them.
5. Use the LT containment layer for gutters and inner width. Avoid one-off negative margins or viewport-width tricks unless they match the shared `.lt-fullbleed` pattern.
6. Run the responsive container audit and motion verification when the change involves animated crawls, carousels, clipping, or media-query fallbacks.
7. Capture desktop and mobile screenshots before claiming the page is ready for GL review.

## Red Flags

- A full desktop section fills the viewport but has no inner wrapper.
- A crawl, marquee, or review track exposes a native horizontal scrollbar.
- Chrome and Brave show different layout modes and the only proof is a fresh headless browser.
- A Webshop route looks fixed after removing native classes or replacing bundled structure.
- A page looks "boxed" because it accidentally fell back to Frappe's stock container while neighboring LT sections are full-bleed.
- A page looks "broken out" because a full-bleed exception became the default section pattern.
- Product/category controls become text-width chip rows with ragged edges when the page is meant to show off products.
- A desktop product grid ends with one isolated orphan card when the same item count can be split into balanced rows.

## LT Receipt

On 2026-05-06, GL flagged a mismatch between Frappe-native boxing, LT full-bleed sections, the business crawl, and the review carousel. Local research confirmed that LT had intentionally neutralized Frappe's stock `main.container` and moved visual containment into LT CSS, but that contract was scattered across old lessons and inline comments. This recipe makes the standard explicit: keep Frappe/Webshop lifecycle and hooks, but require every LT public section to choose either contained workflow/reading mode or deliberate full-bleed band mode with its own inner containment and browser verification.
