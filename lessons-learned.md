# Lessons Learned — Locally Twisted

**Append-only.** Newest entries at the top. Each entry: what happened, what was learned, what to do differently next time.

LT-specific patterns. Cross-client / agency-wide lessons go to `Built_by_Cameron/lessons-learned.md`. If a lesson is broadly applicable across all ERPNext builds, it ALSO goes to the global `C:\Users\baenb\.claude\lessons-learned.md`.

---

## 2026-04-29 (Stripe wiring + true guest checkout session) — Five Frappe internals discovered

### Frappe Payment Request `payment_url` is gated behind `send_mail` — manual call required when suppressed

`Payment Request.on_submit` (apps/erpnext/...accounts/doctype/payment_request/payment_request.py:215) calls `set_payment_request_url()` ONLY inside the `if send_mail and self.payment_channel != "Phone":` branch. `send_mail` becomes False when EITHER `ref_doc.order_type == "Shopping Cart"` OR `self.flags.mute_email = True` (line 211). Both are necessary for guest checkout — but they ALSO suppress the URL-generation call.

**Fix:** after `pr.submit()`, call `pr.set_payment_request_url()` manually then `pr.reload()`. See `apps/locally_twisted/locally_twisted/www/checkout.py` for the working pattern.

**Receipt:** smoke test #3 (URL Test customer, since cleaned). After fixing wkhtmltopdf error, `payment_url` came back None. Traced to `set_payment_request_url` not being called. Manual call populated it correctly.

### wkhtmltopdf inside the Frappe Docker container can't reach localhost:8081

Anywhere Frappe auto-renders a PDF inside the running container — `attach_print()`, Sales Order print formats, Payment Request emails — wkhtmltopdf is invoked and tries to fetch CSS/assets from the site's public URL. Inside the container's network namespace, `localhost:8081` doesn't resolve. Result: `OSError: wkhtmltopdf reported an error: Exit with code 1 due to network error: ConnectionRefusedError`.

**Workaround for Payment Request:** set `Sales Order.order_type = "Shopping Cart"` AND `payment_request.flags.mute_email = True` BEFORE `pr.submit()`. Both checks are at `payment_request.py:211`. Either alone may not be enough.

**Long-term fix (deferred):** configure `host_name` in `site_config.json` to a docker-internal hostname (e.g., `http://frontend:80`) so wkhtmltopdf can reach back to the site from inside the network. Future hardening item.

**Receipt:** smoke test #2 (Trace Test, since cleaned). Got the full traceback chain: `Payment Request on_submit → send_email → attach_print → pdfkit.to_pdf → wkhtmltopdf → ConnectionRefusedError`.

### `Contact.links` is a child table, NOT a column — query Dynamic Link directly

`Contact` has a `links` field that looks like a column in Customize Form, but it's a Table-fieldtype (child of Contact). Querying `frappe.db.get_value("Contact", ..., ["links"])` errors with `pymysql.err.OperationalError: (1054, "Unknown column 'links' in 'SELECT'")`.

**Fix pattern for Contact → Customer lookup:**
```python
contact_name = frappe.db.get_value("Contact Email", {"email_id": email}, "parent")
if contact_name:
    customer_name = frappe.db.get_value(
        "Dynamic Link",
        {"parent": contact_name, "link_doctype": "Customer", "parenttype": "Contact"},
        "link_name",
    )
```

Same pattern applies to any parent doctype's Table fields — query the child table by `parent` field, not the parent's "column."

**Receipt:** first guest-checkout smoke test failed with the Unknown column error. Fix is in `checkout.py:292-302` with comments.

### Stripe Settings auto-creates the entire payment chain on insert

Inserting a `Stripe Settings` record with `gateway_name`, `publishable_key`, `secret_key` triggers ERPNext's `on_update` hook which auto-creates:
- Payment Gateway named `Stripe-{gateway_name}` (e.g., `Stripe-Test`)
- Bank Account named `Stripe-{gateway_name} - {company_abbr}` (e.g., `Stripe-Test - LT`) — Currency = company default
- Payment Gateway Account linking the gateway to the bank account, marked default

You don't need to create any of those manually. Just insert the Stripe Settings → wire `Webshop Settings.payment_gateway_account` to the auto-created PGA name → done. Pattern codified in `scripts/setup/configure_stripe_test_mode.py`.

**Receipt:** session 2026-04-29. Wrote configure_stripe_test_mode.py expecting to need follow-up scripts for PG / PGA / Account creation. None needed — all four records existed after one insert.

### Webshop checkout requires `payment_gateway_account` set OR `enable_checkout=1` won't stick

`Webshop Settings.enable_checkout = 1` set via `frappe.client.set_value` silently reverts to 0 if `payment_gateway_account` is null. The save validator quietly rejects the change. Set both fields in the same `set_value` call (with the multi-field `fieldname` dict format) and both stick.

**Pattern:**
```python
frappe.client.set_value(
    doctype="Webshop Settings",
    name="Webshop Settings",
    fieldname={
        "payment_gateway_account": "Stripe-Test - USD - LT",
        "enable_checkout": 1,
    },
)
```

**Receipt:** session 2026-04-29. First attempt set only `enable_checkout=1`, saved silently, value was still "0" on read-back. Second attempt set both fields together — both took.

---

## 2026-04-28 (BTFP restructure + ribbons + font weight + color session) — Three CSS gotchas

### DM Serif Display is a single-weight font (400 only) — never override `font-weight` on heading classes

The brand serif at `https://fonts.googleapis.com/css2?family=DM+Serif+Display` has only the default cut. Setting `font-weight: 600` on `.lt-faq h1`, `.lt-faq__group-title`, `.lt-policy h1`, `.lt-policy h2`, etc. produces synthetic-bold (faux-bold) rendering — chunky, heavy, unrefined.

**Fix:** remove `font-weight: 600` from any class that targets a heading (h1/h2/h3) which inherits the global `h1, h2, h3 { font-family: 'DM Serif Display'; font-weight: 400; }` rule. Want emphasis? Use SIZE not WEIGHT (e.g., bumped FAQ group titles from 1.25rem → 1.5rem after removing the weight override).

`font-weight: 600` IS valid on Raleway-based classes (`.lt-faq__link`, `.lt-policy__link`, `.lt-faq__answer strong`) — Raleway has real 600. The rule is heading-class-specific.

**Receipt:** GL flagged the chunky look on /faq + /refund-policy. Comparing to BTFP intro h1 (no override → elegant) confirmed the cause. Fix landed in `faq.py` and `refund_policy.py` 2026-04-28.

### CSS `margin: 0` (shorthand) defeats `.lt-fullbleed` negative margins

`.lt-fullbleed` (in lt-theme.css) uses:
```css
margin-left: -50vw;
margin-right: -50vw;
```

Any rule with `margin: 0` or `margin: <something>` (the shorthand) wipes out the negative margins because shorthand sets all four sides. Result: the section stops at the parent container's edge instead of going edge-to-edge.

**Fix:** when defining a class that needs to coexist with `.lt-fullbleed`, use specific properties (`margin-top: 0; margin-bottom: 0;`) instead of the shorthand. Or just not set vertical margins at all.

**Receipt:** GL flagged "the ribbon containers that are thin and supposed to go across the whole page dont." The blush + soft-blue ribbons had `.lt-btfp__ribbon { margin: 0 }`. Replaced with specific top/bottom margins; ribbons span full width.

### `--lt-near-white` was too cold (#FBFBFB read as bluish-grey) — bumped to #fffcfc

GL: *"the main white background is so white it's bluish and/or gray... Try fffcfc for the main background."* Updating the CSS custom property at `:root { --lt-near-white: #FBFBFB }` → `#fffcfc` makes the body, BTFP booking section, and (later) the footer copyright bar feel warm rather than cold. `#FFFFFF` (the `--lt-white` token, used on cards and contrasted panels) stays unchanged for visible contrast.

**Pattern lesson:** `--lt-near-white` is the new "base white" token across the site. When choosing between `--lt-white` and `--lt-near-white` for a background, pick `--lt-near-white` for surfaces that should feel calm/quiet and `--lt-white` for surfaces that need to pop against the surrounding bands.

---

## 2026-04-27 (small-shop seed session) — Six webshop gotchas

### `upload_file` API does NOT auto-write the file_url to the parent doc's field

Called Frappe's `/api/method/upload_file` endpoint with `doctype=Item`, `docname=<slug>`, `fieldname=image`, `is_private=0` and got back a valid `{"file_url": "/files/<slug>.png"}` response. **The File record was created** with `attached_to_doctype=Item`, `attached_to_name=<slug>`, `attached_to_field=image`. **But `Item.image` stayed null.**

**Why:** the upload endpoint creates the File attachment record but does NOT write the file_url back into the parent doc's named field. Two separate operations.

**Fix:** explicit `frappe.client.set_value` call after upload — `Item.image = file_url`. AND for storefront display, also set the **separate** `Website Item.website_image` field (Item.image and Website Item.website_image are independent in v15).

**Receipt:** Seed script ran successfully, 33 File records created with the right attached_to_field, but the storefront showed empty placeholder boxes ("NB", "GG" letter avatars). Auditing Item records showed all 33 with `image: None` despite the File records existing.

### Webshop is OFF by default — `Webshop Settings.enabled = 0`

Fresh install of `frappe/webshop` ships with the storefront effectively disabled. **All these critical fields default to 0:** `enabled`, `show_price`, `show_stock_availability`, `enable_field_filters`, `enable_attribute_filters`, `enable_checkout`, `enable_wishlist`, `enable_reviews`, `allow_items_not_in_stock`. **And `price_list` defaults to None.**

**Fix:** explicitly set every field that matters BEFORE expecting browse / price-display / cart to work. Minimum to get a browseable shop with prices:
```
enabled = 1
show_price = 1
allow_items_not_in_stock = 1   # required for non-stock (made-to-order) items
products_per_page = 12         # default 0 = silently broken
price_list = "Standard Selling"  # default None = no prices visible
default_customer_group = "Individual"
enable_checkout = 1            # otherwise "Add to Quote" instead of "Add to Cart"
```

**Receipt:** Created 33 Website Items with `published=1`. /all-products rendered exactly 2 of them with no prices. Spent multiple turns chasing pagination + permission filter theories before discovering Webshop Settings.enabled=0 was silently filtering the entire result set in `add_display_details`.

### Webshop's whitelisted method path is `webshop.webshop.api.*`, not `webshop.api.*`

Folder layout: `apps/webshop/webshop/webshop/api.py`. Frappe convention says this Python module is `webshop.webshop.api`. The compiled JS bundle correctly calls `frappe.call({method: "webshop.webshop.api.get_product_filter_data"})`. **But intuitively the path "looks like" it should be `webshop.api.*` — and that's wrong.**

Calling `webshop.api.get_product_filter_data` returns HTTP 417 EXPECTATION FAILED with `ValidationError: Failed to get method ... with No module named 'webshop.api'`.

**Pattern:** Frappe apps double-namespace. The `<app_name>` Python package contains a `<app_name>` sub-module containing the module files. So `<app>.<module>.<file>` is the import path, even when `<app> == <module>`.

**Receipt:** Spent a turn convinced the JS was calling the wrong path because my direct curl was getting 417. The JS was correct; my curl was wrong.

### Frappe's `body { display: flex; height: 100vh; overflow-y: auto }` defeats Playwright `full_page=True`

The webshop pages set the body to a fixed-height flex container with internal overflow-scroll. **Playwright's `full_page=True` only captures `documentElement.scrollHeight`, which on these pages = viewport height = 800px** — even though the actual content (product grid) extends thousands of pixels below.

The user experience is fine: customers scroll inside the page body and see all the products. **But if you screenshot at the default 1280×800 viewport and trust what you see, you'll declare the shop "broken" when only the first row visible.**

**Fix when verifying with Playwright:** use a tall viewport (`viewport={"width": 1280, "height": 3500}`). The DOM still renders identically; the viewport just captures more in the screenshot.

**Receipt:** Spent two iterations debugging "only 2 items render" before checking `body.offsetHeight` (= 800) vs `#products-grid-area.offsetHeight` (= 2707). 12 items WERE rendered, just below the captured frame.

**Pattern:** Always probe `document.documentElement.scrollHeight` AND the children's heights before trusting a Playwright screenshot's "what's missing" implication. Add the height probe to the standard verification preamble.

### Setting `Item.standard_rate` auto-creates an Item Price — explicit Item Price insert hits a duplicate-detection exception

When inserting an Item via `frappe.client.insert` with `standard_rate` populated, ERPNext's Item controller auto-creates a corresponding Item Price record (under "Standard Buying" by default, or "Standard Selling" for sales-only items). A subsequent explicit `Item Price` insert for the same item + price list raises `ItemPriceDuplicateItem` (HTTP 417), which is NOT caught by the standard `"already exists" / "DuplicateEntryError"` patterns.

**Fix:** expand idempotency-detection in any seed script to ALSO catch `ItemPriceDuplicateItem` and `"appears multiple times"`. Or skip the explicit Item Price insert entirely when standard_rate is set on the Item.

**Receipt:** First seeder run blew up at item #1 with HTTP 417 because of the duplicate. Patched the idempotency check, re-ran, succeeded.

### Webshop initial render goes through AJAX, not server-side Jinja

The `/all-products` page's index.html is empty for products (just `<div id="product-listing"><!-- Rendered via JS --></div>`). The JS in `index.js` instantiates `webshop.ProductView` which calls `frappe.call({method: "webshop.webshop.api.get_product_filter_data"})` and renders results client-side.

**Implication for verification:** `curl http://localhost:8081/all-products | grep <product-name>` returns nothing — products are not in the server-rendered HTML. Use Playwright with `wait_until="networkidle"` to capture post-JS state.

**Implication for SEO:** the storefront is JS-rendered, which is bad for crawlers without execution. If SEO matters for the small shop, server-side rendering of the first batch is a future concern. Out of scope for v1.

---

## 2026-04-27 (homepage build session) — Five gotchas + two reusable patterns

### Frappe Python module cache is sticky — restart backend after editing `www/<route>.py`

Edited `home.py` PAGE_CSS expecting the next `clear-website-cache` to refresh the served HTML. It did NOT. The HTML markup updated but the inline `<style>` block (injected via `context.colocated_css`) kept serving the OLD CSS.

**Why:** Frappe imports `www/home.py` once per Python worker process, then caches the module. `bench --site frontend clear-cache` clears Frappe's render cache, but doesn't reload Python imports. Editing the .py file means the running gunicorn worker still holds the old module in memory.

**Fix:** `docker restart locally-twisted-erpnext-v15-backend-1` — that bounces the gunicorn workers and forces re-import on next request. Sleep 8s for the container to come up, then test.

**Receipt:** Spent a turn confused why `lt-fullbleed` wasn't visibly working. `curl localhost:8081/ | grep "@keyframes lt-hero-cycle"` showed 0 matches (the v2 keyframes weren't in the served HTML). Restart fixed it immediately.

**Pattern:** Whenever PAGE_CSS or any Python data structure changes in a `www/` controller, the cycle is: edit → `docker restart <backend>` → `clear-website-cache` → test. Template-only changes (just HTML) re-render on next page hit; controller changes need the restart.

### Web Page DocType records compete with `www/` files for the same route

Visited `/` after creating `home.py` + `home.html` and got the prior "Site under construction" placeholder, NOT my new homepage. Diagnosed via SQL: `SELECT name, route, published FROM \`tabWeb Page\` WHERE route IN ('home');` → returned name="locally-twisted", route="home", published=1.

**Why:** Website Settings.home_page = "home". When `/` resolves, Frappe looks for a route named "home" via multiple resolvers. A published Web Page record AND a `www/home.html` file both claim that route. The Web Page record won.

**Fix:** `UPDATE \`tabWeb Page\` SET published = 0 WHERE name = 'locally-twisted';` — deactivates the placeholder. The www/home.html file then takes precedence.

**Pattern:** Before creating any new `www/<route>.<py|html>` file, check if a published Web Page record already claims that route. If yes, decide: (a) deactivate the Web Page record (cleanest), (b) move the Web Page content into your www/ template, (c) pick a different route. Don't assume www/ wins by default — it depends on Website Settings.home_page and which resolver runs first.

### Frappe full-bleed pattern — `width: 100vw` + `margin-left: -50vw` breaks out of the parent .container

Bands rendered as colored stripes inside the centered content column, leaving white margins on left and right (GL's "Image #5" complaint about banners cut off). The `templates/web.html` parent wraps content in a `.container` with max-width that constrains everything inside.

**Fix:** A `.lt-fullbleed` modifier class:

```css
.lt-fullbleed {
    width: 100vw;
    position: relative;
    left: 50%;
    right: 50%;
    margin-left: -50vw;
    margin-right: -50vw;
}
```

Applied to `<section>` elements that should read as full-width bands (hero, reviews, featured, crawl, CTA, twisting spotlight). Inside each section, an inner `.lt-<block>__inner` div with `max-width: 1200px; margin: 0 auto;` keeps content readable.

**Receipt:** The first homepage v2 deploy showed bands visibly constrained. Adding `.lt-fullbleed` to 6 sections fixed it without touching the parent template.

**Pattern:** This is the standard CSS technique for "break out of a constraining parent container." Document it in the meal — every BBC client's portal pages have the same parent.container constraint.

### CSS-only cycling content (hero headlines, blog post titles, etc.) — staggered animation-delay on absolutely-positioned children

GL wanted the hero headline to cycle through blog post titles while a stable tagline stays put underneath. Implemented with pure CSS (no JS):

```css
.lt-hero__cycling { position: relative; min-height: 4.4rem; }
.lt-hero__title {
    position: absolute; inset: 0;
    opacity: 0;
    animation: lt-hero-cycle 32s infinite;
}
.lt-hero__title:nth-child(1) { animation-delay: 0s; }
.lt-hero__title:nth-child(2) { animation-delay: 8s; }
.lt-hero__title:nth-child(3) { animation-delay: 16s; }
.lt-hero__title:nth-child(4) { animation-delay: 24s; }
@keyframes lt-hero-cycle {
    0%   { opacity: 0; }
    3%   { opacity: 1; }
    22%  { opacity: 1; }
    25%  { opacity: 0; }
    100% { opacity: 0; }
}
@media (prefers-reduced-motion: reduce) {
    .lt-hero__title { animation: none; opacity: 0; }
    .lt-hero__title:nth-child(1) { opacity: 1; }
}
```

**First-paint gotcha:** at t=0 the keyframe is at 0% which is opacity 0. Title 1 invisible until 1s into the cycle. Solutions: (a) negative `animation-delay: -1s` on title 1 to start mid-cycle, or (b) live with the 1s fade-in delay (current state — Playwright captures show title 1 visible by the time `wait_until="networkidle"` fires).

**Pattern:** Reuse for any cycling content where one stable element + one rotating element is the desired UX (testimonials, blog teasers, mood-to-quote in lookbook). Total cycle = N × per-title duration; staggered delays = full duration / N.

### Carousel of cards — same CSS marquee pattern as text crawl, just bigger items

GL pivoted reviews from 5-inline-cards to a horizontal-scrolling carousel of all 19 reviews. Reused the existing `.lt-crawl` pattern verbatim, swapping text spans for full review cards:

- Outer viewport: `overflow: hidden; mask-image: linear-gradient(...);` for edge fade
- Track: `display: flex; gap: 1rem; width: max-content; animation: scroll Ns linear infinite;`
- Items: `flex: 0 0 320px;` (fixed card width, no shrink)
- Track has duplicate set (aria-hidden) for seamless loop
- `.viewport:hover .track { animation-play-state: paused; }` for reading-on-hover
- `prefers-reduced-motion` falls back to flex-wrap (cards stack)

**Speed scaling:** text crawl = 270s for 54 names; card carousel = 360s for 19 cards. Cards are bigger and need reading time.

**Pattern:** Same primitive can do client-name marquee, review-card carousel, photo-strip carousel, etc. Worth a recipe (kitchen note dropped at agency-tier capabilities).

### `git status` showed 6 deleted `_oneshot_*` files persisting from prior session — auto-commit hook handles writes, not deletions

The git status at session start showed 6 ` D ` (working-tree-deleted, unstaged) entries from prior session's cleanup. These weren't blocking but they made `git status` noisy.

**Why:** the auto-commit hook fires on Write tool calls. Deletions via filesystem don't trigger it. Net effect: deleted files stay as unstaged deletions until someone commits them explicitly.

**Pattern:** If a session ends with stale ` D ` entries in git status, that's not a leak — but worth a cleanup commit if doing housekeeping. Otherwise the next instance will see them too.

---

## 2026-04-26 (codification + chrome + accessibility + contact + BTFP session) — Five gotchas worth carrying forward

This session shipped four real surfaces (chrome, accessibility, contact, BTFP) and one meal. Five gotchas hit during the work, each with a verified receipt. All five are now codified in `Built_by_Cameron/.claude/capabilities/meals/build-frappe-portal-page.md` "Known gotchas" section so the next instance doesn't rediscover.

### Frappe `www/` does NOT auto-translate underscored filenames to dashed URLs

A controller named `<app>/www/balloon_twisting_and_face_painting.py` serves at `/balloon_twisting_and_face_painting`, NOT at `/balloon-twisting-and-face-painting`. Python module names cannot have dashes; URLs typically should. Bridge the two with `website_route_rules` in `hooks.py`. After editing hooks.py: cache clear is not enough — also flush Redis and restart the backend; the route map caches aggressively.

### Frappe's website bundle has direct `<p>` rules that override inherited text-align

Setting `text-align: center` on a parent section does not reliably reach `<h1>` / `<p>` children — Frappe's bundle has direct selectors at higher specificity. Direct selectors always beat inherited values regardless of cascade order. **Fix:** declare `text-align: center` directly on each text-bearing block via its BEM class. This bit twice in the same session (footer brand block, BTFP intro lede); same pattern, same fix.

### Webshop's CSS/JS bundles need `bench build` (Node + yarn required)

`webshop/hooks.py` registers `web_include_css = "webshop-web.bundle.css"` + `web_include_js = "web.bundle.js"`. Without `bench build`, those bundles aren't compiled, `assets.json` lacks the entries, Frappe falls back to bare paths, browsers 404. Worse: `web.bundle.js` defines the global `webshop` JS namespace; without it, `/all-products` throws `Uncaught ReferenceError: webshop is not defined`. The frappe_docker production image has no Node, BUT Node v20 is available via nvm at `/home/frappe/.nvm/versions/node/v20.19.2/`. Symlink it into `/usr/local/bin` so `/bin/sh` subprocesses (which `bench build` uses) find it. Same for yarn (install via `npm install -g yarn`). All wrapped in `scripts/setup/install_webshop.py --build-assets` for reproducibility after container recreation.

### Lead Source records don't exist on a fresh ERPNext install

`Lead.source` is a Link to `Lead Source`. On a fresh install, that DocType has zero records. Setting `source="Website"` raises `LinkValidationError`. Fix: idempotently create the source before creating the Lead (`frappe.db.exists` + try-`insert` with `ignore_if_duplicate`). Caught at the LT contact-page first smoke test before GL ever saw it. The same pattern applies to any Link-field default: ensure-or-create the linked record before creating the parent.

### Browser cache + `web_include_css` files

Files registered via `web_include_css` serve via the symlink chain. Their `Last-Modified` and `ETag` update on edit, but Brave (and other browsers) sometimes don't re-validate within a session. Visual symptom: page shows a mix of old and new CSS rules; new BEM classes look unstyled (logo at native size, lists with bullets, no flex). DevTools Network shows the file from cache. **Fix:** hard-refresh (`Ctrl+Shift+R`). **For the meal:** ALWAYS include "hard refresh" in the handoff to GL when shipping a CSS-touching change. Saves a confused round-trip.

### Generalizable lesson promoted to agency-tier

Each of these is now in the meal's "Known gotchas" section with a receipt. The next instance reading the meal sees them as patterns-to-anticipate, not patterns-to-rediscover.

---

## 2026-04-26 (codification session) — `extend_doctype_class` is NOT consumed by Frappe v15

External research (Magic Research / `frappe-erpnext-non-gpl-hooks-comparison.md`) recommended preferring `extend_doctype_class` over `override_doctype_class` for "lower-conflict" coupling. Verified against running Frappe v15 source: `grep -rn 'extend_doctype_class' apps/frappe/` returns NO consumer in Frappe core. The Payments app declares `extend_doctype_class = {"Web Form": "..."}` in its `hooks.py`, but Frappe never reads that hook key — Payments' actual Web Form behavior change comes through `override_whitelisted_methods` instead.

**Generalizable lesson:** verify external research against the running source before codifying. If GL hadn't asked for it to be codified at agency tier, this wrong claim could have led the next instance to declare a hook that does nothing. The verify-against-source rule worked — it caught a 95%-correct external research piece's one wrong claim. Codified at `Built_by_Cameron/.claude/capabilities/recipes/license-isolated-app-architecture.md` "Corrections from source" section.

---

## 2026-04-26 (session end) — TWO consecutive landing-page failures share one pattern: invent + band-aid + claim-done-off-DOM-facts

**What happened:** This session's instance built a landing page using `Web Page` content_type=Page Builder with 4 default Web Templates. The build looked complete from DOM facts (curl showed all sections rendered, Playwright captured a 1366×3818 screenshot, all the section IDs and class names were present). The instance reported it as "tier 1 native" and ready for review. GL opened the page in their actual browser. **It wasn't visible. It wasn't responsive. The copy was made-up.**

**Root cause is now nameable:** Both this session's failure AND the prior Slice 2 failure share the same anti-pattern:
1. **Invent placeholder copy** instead of pulling from the approved Odoo XML / live site source
2. **Use band-aid CSS** (`!important` chains in the prior session; default Page Builder template + thin theme CSS in this session) instead of using the framework's intended override surfaces
3. **Declare done off DOM facts** (the DOM has the elements; the page must be working) instead of verifying GL can see the rendered output in a real browser at multiple viewport widths

**The architectural primitives weren't the problem.** Web Page DocType + Page Builder + custom Frappe app + web_include_css are all valid Frappe paths. They CAN produce a working result. They DID NOT, twice in a row, because the technique inside the architecture was wrong.

**What the third instance must do differently:**
1. **Source content from the Odoo XML or live locallytwisted.com — never invent.** Documented as a standing decision this session.
2. **GL's eyes on the actual page > any DOM fact.** A successful Playwright capture is a precondition, not a verdict. GL opens the page on their phone and their laptop and confirms. THEN it's done.
3. **Match GL's STYLE-GUIDE.md visual identity.** Not "looks roughly right." The brand foundation has specific fonts, colors, spacing. Slop fails.
4. **Mobile-first verification.** 375px viewport BEFORE 1366px desktop. If it doesn't work on mobile, it isn't done — Jeff's customers use phones.
5. **The platform-direction decision (custom Jinja vs decoupled vs Frappe Builder) is GL's call, made consciously.** Don't presume Frappe is the answer because you arrive in a Frappe codebase. The expedition synthesis is the briefing.

**Generalizable lesson promoted to agency tier:** This is a specific case of the broader "verify with reality, not with claims" anti-pattern in the global `anti-gl-patterns.md`. The LT-specific receipts are now in this file's 2026-04-26 (Slice 2 build) entry AND this entry. Two strikes. The third instance must break the pattern.

---

## 2026-04-26 (Jinja override path validation) — The override DOES resolve in our Docker bind-mount setup

**What happened:** Two prior HANDOFFs claimed "override Jinja partials at `apps/locally_twisted/locally_twisted/templates/includes/footer/footer.html`" was the path forward for Slice 2. Nobody had verified the override actually resolved in our specific bench setup. This session: dropped a minimal test file with a visible string, cleared cache, fetched the home page, confirmed the test string appeared in served HTML.

**Verified working:**
```
apps/locally_twisted/locally_twisted/templates/includes/footer/footer.html
```
Place a file at this path in our custom app. Frappe's template lookup resolves it before Frappe's standard footer at `apps/frappe/frappe/templates/includes/footer/footer.html`. Same pattern works for navbar and other Jinja partials.

**Required after creating/editing the override:** `python scripts/dev/clear_website_cache.py` — Frappe caches the resolved template path; the cache must be cleared for the override to take effect on next request.

**The test file was REMOVED after validation** — it was overriding the real Frappe footer with the test string, which is not what we want long-term. The next instance creates the real footer override only when ready to build the actual Slice 2 redo.

**Generalizable lesson:** When a HANDOFF claims an architectural path is "the way forward" but nobody has executed even the minimal version, the next instance MUST verify the path before building substantively on top of it. One test file proves the assumption (or surfaces a deeper problem to fix). The cost of the test is minutes; the cost of building on an invalid assumption is a session.

---

## 2026-04-26 (webshop install + framework study + Web Page tabs finding) — Read the DocType schema BEFORE planning custom code

**What happened:** The pricing calculator on the BTFP service page was planned as a "tier 4 custom Web Template" build — meaning we'd write a custom Jinja template + register it via hooks + extend it from a Web Page record. Three instances in a row independently classified it this way, including me when I wrote the v1 index. The calculator was treated as the "irreducibly custom code" piece that justified opting into tier 4.

GL surfaced the actual answer mid-session: *"the previous instance edited this page http://localhost:8081/app/web-page/locally-twisted by using the content field update, not the scripting tab where you can literally just add javascript. You can create webpages with javascript but the prior instance just filled in the content field and it made everything look bad — because they should have used java! You can use java on these pages!"*

I went and read the Web Page DocType schema (`apps/frappe/frappe/website/doctype/web_page/web_page.json`). It has these tabs natively:

| Tab | Field | What it natively supports |
|---|---|---|
| Content | `content_type`, `main_section`/`main_section_html`/`main_section_md`, `page_blocks` | Body layout (multiple input modes including Page Builder) |
| Script | `javascript` (Code field) | **Per-page JavaScript that runs at page load** |
| Style | `css` (Code field), `insert_style` (Check) | **Per-page CSS scoped to this page** |
| Header and Breadcrumbs | `header` (HTML), `breadcrumbs` (Code), `dynamic_template` | Custom hero HTML, breadcrumb logic |
| Settings | `show_sidebar`, `enable_comments`, `full_width` | Layout toggles |
| Meta Tags | `meta_title`, `meta_description`, `meta_image`, `dynamic_route` | Per-page SEO |
| Context | `context_script` (Code, Python) | **Server-side Python that runs BEFORE render — inject variables into the Jinja context** |

**The calculator collapses from tier 4 to tier 1:**
- Page Builder for static layout (H1, intro, FAQ accordion) → `page_blocks`
- HTML form inputs → an HTML block in Page Builder OR `main_section_html`
- Live price math → `javascript` field
- Calculator-specific styling → `css` field (with `insert_style=1`)
- No custom Web Template, no hooks, no app code, no Jinja overrides. Pure DocType configuration.

**What was learned (load-bearing for the lineage):**

1. **DocTypes are the configuration surface, including for "code" things.** Frappe's Code-fieldtype fields (javascript, css, context_script) are configuration, not code-in-the-traditional-sense. They live in DocType records. They're versioned via fixtures. They survive cleanly across upgrades. Writing a custom Web Template to hold the same JavaScript is strictly worse: more files, more places to break, no benefit.

2. **The previous instance's mistake is fully named:** they used `main_section` (Rich Text) only. They didn't open the Script tab or the Style tab or use Page Builder. They didn't read the schema. They assumed the page surface was just "what `main_section` accepts." Then when they needed interactivity, they assumed they'd need to override a template — when in fact the right answer was already on the same DocType form, in a different tab.

3. **The general rule:** before reaching for a custom Web Template, custom hook, custom controller, or template override — **read the DocType's `.json` schema in the running container.** Frappe DocTypes have many more fields than the desk UI immediately surfaces. Tabs are collapsed by default. Code-fieldtype fields are easy to miss. The schema is authoritative; the form layout is just one view of it.

**Generalizable lesson promoted to agency-tier:** added a "Standing principle: System-native first" section at the top of `Built_by_Cameron/.claude/capabilities/recipes/frappe-conventions.md` — every BBC client benefits.

---

## 2026-04-26 (Slice 2 build) — Frappe / ERPNext quirks discovered while building the website shell

A pile of gotchas hit during a single session of building the navbar + footer + scaffolding the custom Frappe app. Each one bit, each one was band-aided rather than learned-from in the moment, each one is real. Logging here so the next instance doesn't rediscover.

### `bench new-app` license validator is case-sensitive (lowercase `mit`)

The CLI prompt says `App License [mit]:` and looks like it accepts free text — it does not. Click validates against the exact list `mit`, `agpl-3.0`, `apache-2.0`, etc. Pass `MIT` (uppercase) and `bench new-app` aborts with a validation error and creates nothing. Pass `mit` (lowercase) and it proceeds.

**Lesson:** when feeding answers via heredoc/stdin to `bench new-app`, use lowercase license values. The list is documented in the prompt itself.

### Top Bar Item parent rows cannot have a URL when they have child items

`Website Settings.top_bar_items` accepts a child table where dropdown structure is encoded by `parent_label`: items with `parent_label = "Foo"` become children of the parent row whose `label = "Foo"`. **Frappe validates that a parent row's `url` is empty when it has children.** Set `{label: "What We Make", url: "/shop"}` while having children with `parent_label: "What We Make"` and the API returns `ValidationError: What We Make in row N cannot have both URL and child items`.

**Lesson:** parent dropdown rows are pure triggers, not link destinations. `url=""` for the parent; children carry the actual destinations.

### Footer Items need explicit URL-less parent rows (column headers) defined within the same table

Same shape as `top_bar_items`. `Website Settings.footer_items` rendering as columns by `parent_label` requires the parent value to exist as its own row in the same list. Skip the parent rows and Frappe raises `ValidationError: Shop does not exist in row 1` for every child whose `parent_label` doesn't match an in-list row.

**Lesson:** before child rows like `{label: "All Products", parent_label: "Shop"}`, prepend an empty-URL row `{label: "Shop", url: ""}`. Frappe groups under that parent.

### Web Page `content_type` is a hidden field-router (HTML reads `main_section_html`, Rich Text reads `main_section`)

The `Web Page` DocType has multiple body-content fields and `content_type` selects which one renders. Set `content_type="HTML"` and Frappe renders from `main_section_html`. Set `main_section` instead — the page article renders **empty** with no error, no warning, no log entry. The page exists, the title appears, but the body is just `<article>...</article>` with nothing inside.

**Lesson:** `content_type="Rich Text"` is the safe default if you're putting raw HTML in `main_section`. Always verify with a `curl` of the served page after writing a Web Page record — the article tag should contain your content.

### Frappe HTML sanitizer strips inline SVG `<path d="...">` from CMS fields like `Website Settings.address`

Wrote inline SVGs with explicit path data (Instagram, Facebook, etc. social icons) into the `address` field's HTML. Curl of the served page showed `<svg viewbox="0 0 24 24"><path></path></svg>` — viewBox lowercased, every `d=` attribute stripped, the SVG visually empty. The sanitizer treats CMS fields as untrusted user input and removes attributes deemed risky for XSS.

**Lesson:** for any iconography or styled rendering inside CMS-editable fields, use one of these instead:
- CSS `background-image: url(...)` referencing a real SVG file in `apps/<app>/<app>/public/icons/icon.svg`. Class names on the `<a>` survive sanitization; the icon comes from CSS.
- Inline SVG only inside `head_html` or `body_html` (less sanitized) or a Web Template's Jinja (not sanitized at all).
- Font icons via class names if your app loads an icon font.

### `head_html` styles load BEFORE Frappe's bundled stylesheets in the cascade

Pushed the entire LT theme CSS as a `<style>` block in `Website Settings.head_html`. The block lands in the `<head>` very early. Frappe's `website.bundle.css` and `erpnext-web.bundle.css` `<link>` tags load *after* — meaning equal-specificity rules in those bundles win. `.web-footer { background-color: var(--lt-soft-blue); }` is silently overridden by `.web-footer { background-color: ...; }` in Frappe's bundle.

**Lesson:** `head_html` is a fallback / quick-prototype surface, NOT the production override surface. The right way to override theme CSS in a custom Frappe app is `website_theme_scss` in `hooks.py` plus an SCSS file at `<app>/<app>/public/scss/website.scss`. That gets compiled INTO the website bundle and wins at equal specificity (because it's the LATER file in the merged bundle). For static CSS that doesn't need SCSS compilation, `web_include_css` in `hooks.py` is also fine because that `<link>` tag injects after the bundled CSS.

### `data:image/svg+xml;utf8,...` data URIs silently fail to render in real browsers

Tried to bypass the sanitizer issue by encoding social-icon SVGs as CSS `background-image: url("data:image/svg+xml;utf8,%3Csvg ...")`. Several browsers (real Chromium, Firefox) silently rendered the circles with no icon — accepting the CSS without error, painting the gradient/color background, but failing to decode the SVG. The headless `chrome --screenshot` flag rendered it slightly differently than Playwright's full Chromium, so the breakage was invisible in our quick captures.

**Cause:** the prefix `;utf8,` is non-standard. Real spec is `data:image/svg+xml;charset=utf-8,...` or just `data:image/svg+xml,...`. Additionally, unencoded spaces inside the SVG path `d` attribute trip stricter parsers.

**Lesson:** when you need icons in CSS, use real SVG files in the app's `public/icons/` folder and reference them via plain `url("/assets/<app>/icons/<name>.svg")`. Encoding ambiguity gone. The files are also greppable, version-controllable, and reusable across rules.

### Frappe's navbar-toggler markup is `<svg><use href="#icon-menu"/></svg>`, not Bootstrap's `.navbar-toggler-icon` span

Wrote CSS targeting Bootstrap's standard `.navbar-toggler-icon` span class to skin the mobile hamburger. The class doesn't exist in Frappe's rendered navbar — Frappe outputs `<button class="navbar-toggler"><span><svg class="icon icon-lg"><use href="#icon-menu"/></svg></span></button>` and references an SVG sprite for the icon.

**Lesson:** to override the toggler icon, hide the inner `<span>/<svg>` and put the icon as a `background-image` on the button itself:

```css
.navbar-toggler { background-image: url("/assets/<app>/icons/menu.svg") !important; ... }
.navbar-toggler > span, .navbar-toggler svg { display: none !important; }
```

### Frappe auto-prepends `©` to the copyright field

Set `Website Settings.copyright = "© 2026 Locally Twisted · Accessibility · Refund Policy"`. Rendered output: `© © 2026 Locally Twisted · ...`. Frappe's footer template prepends a `©` glyph itself; supplying one in the field value gives you doubles.

**Lesson:** copyright field value should NOT begin with `©`. Start with the year.

### Editable pip install (`uv pip install -e <app>`) lives in container's writable layer; lost on `docker compose up --force-recreate`

After scaffolding the custom Frappe app inside the backend container with `bench new-app`, the editable Python package was registered via `uv pip install -e /home/frappe/frappe-bench/apps/locally_twisted` so `import locally_twisted` resolves and Frappe's hook system picks up `hooks.py`. Then a docker compose recreate (e.g., to apply a new bind-mount) destroyed the container's writable layer and the editable install with it. New container had the app's source via the bind-mount, but no `locally_twisted` in the Python env — every page rendered HTTP 500 with `ModuleNotFoundError: No module named 'locally_twisted'`.

**Lesson:** the editable pip install must be re-run after every container recreation, in EVERY frappe-image service that imports app code (backend, queue-long, queue-short, scheduler — websocket runs Node so doesn't need it). The clean long-term fix is to bake the install step into the `configurator` service's command in `pwd.yml` so it runs automatically on stack startup. **Until that's done**, treat container recreations like a manual checkpoint that requires:

```bash
for svc in backend queue-long queue-short scheduler; do
  docker exec "<project>-${svc}-1" \
    uv pip install -e /home/frappe/frappe-bench/apps/<app> --python /home/frappe/frappe-bench/env/bin/python
done
docker restart <project>-backend-1 <project>-queue-long-1 <project>-queue-short-1 <project>-scheduler-1
```

### `.web-footer`'s computed height "constraint" — RESOLVED 2026-04-26 (current session)

The previous instance reported `.web-footer`'s computed height was "mysteriously constrained to ~305 px" while its child `.container` was 755 px tall. This was logged as UNRESOLVED.

**Root cause from reading Frappe's actual source in the running container** (`docker exec backend cat /home/frappe/frappe-bench/apps/frappe/frappe/public/scss/website/footer.scss`): there is **no `max-height` rule on `.web-footer`**. The actual SCSS is:

```scss
.web-footer {
  padding: 3rem 0;
  min-height: 140px;
  background-color: var(--fg-color);
  border-top: 1px solid $border-color;
  margin-top: auto;
}
```

The `margin-top: auto` participates in Frappe's intended sticky-footer pattern: `apps/frappe/frappe/public/scss/website/base.scss` declares `html { height: 100% }` and `body { display: flex; flex-direction: column }`. The footer is the last flex child and `margin-top: auto` pushes it to the bottom of body when the main content is shorter than viewport. **This is not a bug — this is Frappe's intended layout.**

The previous "305 px constraint" observation likely came from one or more of:
1. The previous instance's own `lt-theme.css` `!important` chain on `.web-footer` interacting with the body's flex column in unexpected ways
2. Measurement confusion between multiple `.container` elements on the page (the header has a `.container` too; the previous DOM-fact dump may have grabbed the wrong one)
3. The page state at measurement time differed from what the screenshot rendered (cached CSS bundle, stale cookies, etc.)

**The right move forward** (per the agency `frappe-conventions.md` "Verified against source — 2026-04-26" appendix and per GL's directive "work WITHIN Frappe, don't fight it"):

1. Override the Jinja partial at `apps/locally_twisted/locally_twisted/templates/includes/footer/footer.html`. Your override resolves before Frappe's standard one. Use whatever class names you want — no inheritance from `.web-footer` necessary.
2. Strip the `!important` chains from `lt-theme.css`. They were band-aids around the wrong problem.
3. Use `web_include_css` (already wired in `hooks.py`) for the LT theme CSS — it loads AFTER the website bundle in cascade order, so equal-specificity rules win without `!important`.
4. For SCSS that needs Frappe's variables and to be compiled into the bundle, register `website_theme_scss` in `hooks.py` and create `apps/locally_twisted/locally_twisted/public/scss/website.scss`.

**Status: resolved.** Slice 2 redo can proceed using the right primitives; the framework was never the obstacle.

---

## 2026-04-26 — "Jeff doesn't know" needs more precision than the standing docs gave it

**What happened:** Inherited HANDOFF.md and CLAUDE.md framing that read, in effect, "Jeff Kimber doesn't know about the prior failed Odoo attempt; no artifact on disk should leak that." Operated under that assumption for the first part of this session. GL corrected the framing directly: Jeff knows about the Odoo attempt and has lived its failures over months of paid work. What Jeff does not yet know is that GL has decided to migrate infrastructure entirely to ERPNext. The hidden piece is the platform pivot, not the existence of the prior work.

**What was learned:**

1. **One-line summaries of trust dynamics lose load-bearing nuance.** "Jeff doesn't know about the prior Odoo attempt" is a paraphrase that erased months of paid work Jeff has been watching firsthand. A future instance reading the cleaner version might guard the wrong fact and either over-disclose (treating the prior work as something to confess) or under-disclose (acting in conversation as if Odoo never existed, which would be jarring against Jeff's actual experience).

2. **The actual operating rule (per GL 2026-04-26):** Jeff knows the Odoo work happened and watched it struggle. He does not know that GL is migrating off Odoo entirely. The platform pivot stays internal until Phase 1 (customer-facing site + storefront) is demo-ready. The recovery move is showing Jeff a working customer-facing site as the result of months of work, not announcing a do-over.

3. **Operational implication:** Phase 1's bar is not "functional." It is "visibly polished enough that Jeff's reaction is 'oh, this is real.'" The visual quality is what makes the platform pivot land as "I built you something good" rather than "I had to throw it all out." Functional-but-ugly fails the demo even if every test passes.

**Generalizable lesson:** When standing docs use "X doesn't know Y" to encode a trust-state, ask whether Y is the precise fact being protected or a paraphrase of one. Paraphrases compound: each instance restates them slightly cleaner, and over a few sessions the actual nuance is lost. For load-bearing trust dynamics, ask GL once for the precise statement and write that verbatim. Don't tidy. (This receipt also lives in project memory at `<memory>/jeff_trust_and_phase_1_demo_stakes.md` — auto-injected on session start.)

---

## 2026-04-26 — A project frame can be wrong, not just labels. Reframe early, propagate everywhere, delete the old.

**What happened:** Inherited a project framed as "Odoo → ERPNext migration." Spent half a session deepening planning artifacts on top of that framing (PROJECT.md, ROADMAP.md, queue, decisions log, HANDOFF, scripts, capability docs). Then GL revealed: there is no production Odoo — it failed in testing, never went live, Jeff doesn't know. The frame wasn't just labeled wrong; it was structurally wrong. The 10-phase ROADMAP organized work around model translations from a system that's reference material, not a system being migrated. The "stealth migration / trust damage from prior failures" Core Value referenced damage Jeff never experienced.

**What was learned:**
1. **Surface framing assumptions BEFORE building artifacts on top of them.** The first instance who built the planning machinery never asked "wait, is this even a migration?" because the standing files said it was. Cost: significant churn to undo.
2. **A wrong frame deepens its own debt.** Every artifact written under the wrong frame must either be rewritten or deleted. The cost compounds with every layer.
3. **Reframing requires deletion, not just rewriting.** Stale REQUIREMENTS.md tied to old phases. Stale `phases/01-inventory/` research from a deferred-then-renamed phase. Empty `Locally-Twisted-Frontend/` placeholder. All deleted in this session. GitHub is the archive; we store nothing unnecessary.
4. **The reframe needs a "Reference Disposition" section in CLAUDE.md** so future instances can't accidentally re-introduce the old framing by reaching into the prior dir for resources. Make it explicit: these things will be retired; future instances must NOT assume they exist.

**Generalizable lesson:** When inheriting a project, sanity-check the frame against the human's current reality before extending the planning artifacts. Three honest questions cover most cases: "Who is this FOR (and do they know what we're doing for them)?" "What is this REPLACING (vs. building from scratch)?" "What does success LOOK LIKE on demo day?" If any of the answers contradicts what the standing docs assume, stop and reframe. The cost of pausing is low; the cost of compounding the wrong frame is high.

---

## 2026-04-26 — Don't trust API silent success — verify the field landed where you think

**What happened:** Set ERPNext Website Settings.`website_theme_css` via the Frappe `set_value` API. API returned `{"message": {...}}` — looked like success. Curled the served homepage; CSS wasn't in the head. Tried again with stronger parsing; still nothing. Spent two cycles debugging "why isn't my CSS appearing" before checking the DocType field list and finding `website_theme_css` doesn't exist as a field on Website Settings. The right field is `head_html`. Frappe's set_value silently accepted the write to the non-existent field.

**Generalizable lesson:** When a write API returns success but the visible state doesn't change, before re-trying the write, **list the actual fields available on the DocType**. Don't trust field names from memory or pattern-matching. The Frappe API for inspecting a DocType: `GET /api/resource/DocType/<NAME>` returns the full schema including the field list. Spend 30 seconds checking the schema before another 5 minutes debugging the wrong field.

---

## 2026-04-26 — WebFetch failure ≠ site down. Verify with a second tool before alarming the human.

**What happened:** WebFetch tool returned `ECONNREFUSED` for `http://5.78.136.133/`. Reported to GL "the live site is DOWN." This was wrong — `curl -sI` returned HTTP 200 immediately. The WebFetch tool just doesn't handle raw-IP URLs through its proxy layer; it has nothing to do with the site's actual reachability.

**Generalizable lesson:** When a network-dependent tool fails, the failure could be the tool, the network path, the URL format, or the actual server. Reach for a second tool (curl, ping, browser screenshot) before reporting a server outage to the human. **The cost of a false-alarm-then-correction is the same anti-pattern as "report without watching" — it withdraws trust from your reporting.**

---

## 2026-04-26 — Cloudflare blocks default Python urllib User-Agent

**What happened:** First call to `https://api.together.xyz/v1/images/generations` returned HTTP 403 with Cloudflare error code 1010. Worked immediately after adding a real browser User-Agent header.

**Generalizable lesson:** When a third-party API returns 403 + Cloudflare error, the User-Agent is the first thing to check. Default urllib UA looks like `Python-urllib/3.x` and is blocked by many Cloudflare-protected APIs as a generic-bot signature. Always pass `User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36` (or similar real-browser string) for any API call from Python.

---

## 2026-04-26 — `bench set-config host_name` is not enough — `frappe_docker` nginx rewrites the Origin header BEFORE socketio sees it

**What happened:** GL still saw `socketio_client.js:69 Error connecting to socket.io: Invalid origin` after Trellis's earlier fix. Server-side `bench --site frontend show-config` showed `host_name: http://localhost:8081` set correctly. `curl /socket.io/?EIO=4&transport=polling` returned HTTP 200 from the host. The websocket service itself was up and listening. Yet the browser kept rejecting.

**Root cause:** `frappe_docker`'s nginx config at `/etc/nginx/conf.d/frappe.conf:47` contains:
```
proxy_set_header Origin $proxy_x_forwarded_proto://frontend;
```
That line REWRITES the browser's `Origin: http://localhost:8081` header to `Origin: http://frontend` (the internal Docker service hostname) before proxying to the socketio upstream. The socketio Node service is configured with `origin: true` (echo whatever Origin you receive back as `Access-Control-Allow-Origin`). So the response comes back as `Access-Control-Allow-Origin: http://frontend` — which doesn't match the browser's actual origin → CORS rejection → "Invalid origin" surface in the JS client. **Trellis's earlier `bench set-config host_name` fix targeted the wrong layer entirely.**

**Fix (verified working):** Patch the in-container nginx config to pass through the original Origin:
```
proxy_set_header Origin $http_origin;
```
Then `nginx -s reload` (no container restart needed → no DNS cache trap).

This project ships the patch as `scripts/fix/patch_nginx_socketio_origin.py` (run via `docker cp` + `docker exec`). The patch is NOT persistent across container recreation — it edits the in-container file. For permanent fix, mount a custom `frappe.conf` via a docker-compose override.

**Verify:**
```bash
curl -sS -i "http://localhost:8081/socket.io/?EIO=4&transport=polling" -H "Origin: http://localhost:8081" | grep -i access-control-allow-origin
# Expected: Access-Control-Allow-Origin: http://localhost:8081  (matches what you sent)
```

**Why the upstream `frappe_docker` design rewrites Origin:** the assumption is TLS terminated at a load balancer in front of nginx, with consistent internal hostname `frontend`. For browser-direct localhost access (no LB, no TLS), pass-through is correct. Production deployments to Frappe Cloud won't hit this because Frappe Cloud uses its own nginx layer.

**Generalizable lesson:** When a CORS / origin error persists after the obvious config fix, check whether nginx is rewriting headers BEFORE the upstream sees them. `proxy_set_header` lines are easy to miss — but they silently override what the upstream thinks the request looks like. (Also captured in global lessons-learned 2026-04-26.)

---

## 2026-04-25 evening — Frappe socket.io throws "Invalid origin" when site is on a non-default port

**What happened:** Opened the LT ERPNext UI at `http://localhost:8081`. Browser console showed `Error connecting to socket.io: Invalid origin` and `GET /socket.io/... → 400`. Real-time UI features (notifications, live updates, multi-tab sync) silently broken.

**Root cause (incomplete — see 2026-04-26 entry above for the actual fix):** `frappe_docker`'s `pwd.yml` brings the site up assuming Frappe's default port 8080. We map host port 8081→8080 inside the container for LT (so BBC and LT can both run). The `host_name` in the site's config was unset, so Frappe's `get_allowed_origins()` defaulted to something that didn't include `http://localhost:8081`. The socketio server (Node, separate container) rejects mismatched Origin headers as a CSRF defense.

**The trap that bit me on first attempt:** I restarted only the websocket container. That fixed the origin check (it re-read host_name from site config), but Docker assigned the websocket container a *new internal IP* on restart. The frontend (nginx) container had cached the OLD IP from its initial DNS resolution and kept trying to proxy `/socket.io/` to the dead address — producing **502 Bad Gateway** with `connect() failed (113: No route to host)` in nginx's error log. Restarting the websocket without restarting nginx turned an "Invalid origin / 400" symptom into a "No route to host / 502" symptom. nginx in `frappe_docker` does not use a `resolver` directive, so it never re-resolves on its own.

The compose-level `restart` (or restarting frontend + websocket together) avoids this entirely because Docker re-establishes the network and nginx re-resolves on its first proxy attempt.

**What to do for any future site spinup at non-default port:** Run the `set-config host_name` step immediately after `bench new-site` finishes, BEFORE the user touches the UI. AND apply the nginx Origin patch (per 2026-04-26 entry).

**Generalizable lesson:** in `frappe_docker` (and similar nginx + Compose stacks), restarting an upstream container without also bouncing nginx will give you a confusing 502 because nginx caches DNS at startup. Default to `docker compose restart` for the whole project, not single-container `docker restart`, when troubleshooting the data plane.

---

## 2026-04-25 — `gsd-tools commit` returns "nothing_to_commit" because the post-Write auto-commit hook beats it

**What happened:** `node gsd-tools.cjs commit "..." --files PROJECT.md` repeatedly returned `{"committed": false, "reason": "nothing_to_commit"}` even though the file was clearly new. Confused me into staging manually.

**Root cause:** This workspace has a post-Write hook that auto-commits files after the Write/Edit tool succeeds. By the time the GSD `commit` call runs, the file is already in HEAD with an "auto: Write ..." commit message. There's nothing for `gsd-tools commit` to commit.

**What to do:** When `nothing_to_commit` returns, run `git log --oneline -3` to confirm the auto-commit happened (look for `auto: Write FILENAME`). If yes, the workflow can proceed — the file IS in version control, just under a different commit message than the GSD workflow expected. The workflow's commit calls are belt-and-suspenders; the auto-hook is the suspenders.

---

## 2026-04-25 — `git status` on Windows hides freshly-staged dotfiles in the porcelain output

**What happened:** Staged `.gitignore` and `.planning/PROJECT.md` via `git add`. `git ls-files --stage` showed both files indexed with their hashes. `git status --short` and `git status` showed neither as staged — and showed all the OTHER files as untracked. Misleading.

**Root cause:** Unknown — possibly Git Bash + Windows interaction with first-commit-on-empty-repo state. The plumbing (ls-files, commit, ls-tree) was correct; only the porcelain (status) lied.

**What to do:** Trust `git ls-files --stage` and `git ls-tree -r HEAD --name-only` over `git status` when verifying first-commit state on Windows. The actual commit succeeds; status display is unreliable.

---

## 2026-04-25 — Frappe `pwd.yml` defaults to v16.15.1 image; v15 line is stable but you must pin manually

**What happened:** Cloned `frappe_docker`, expected to bring up ERPNext v15. The default `pwd.yml` pinned all 8 service images to `frappe/erpnext:v16.15.1`. Had to swap them all to `frappe/erpnext:v15.105.0` before starting.

**What to do:** When installing Frappe via `frappe_docker`, immediately edit `pwd.yml` to pin the desired tag *before* `docker compose up`. The rolling `v15` tag exists and points to the latest patch (currently `v15.105.0`), but pin to a specific patch for reproducibility — rolling tags will silently pull a newer patch on next `up`. (Also see agency-level v15-stability standing rule in `Built_by_Cameron/CLAUDE.md`.)

---

## 2026-04-25 — Frappe images are large; cache them on the first install, second site comes up in seconds

**What happened:** First `docker compose up` for a Frappe stack took several minutes (image pull, layer extraction). The second compose project for LT used the same `frappe/erpnext:v15.105.0` image and came up in 18 seconds — Docker recognized the layers and just retagged.

**What to do:** When spinning up multiple ERPNext sites locally, reuse the same image tag across compose projects. Each site gets its own volumes (named differently per project) but shares the image. This is fast and disk-efficient.

---

## 2026-04-25 — WSL2 default RAM allocation is below ERPNext's working set; bump `.wslconfig` to 8 GB before installing

**What happened:** Initial WSL2 had 1.5 GB RAM cap (set in `.wslconfig` from a prior expedition). Frappe stack runs MariaDB + Redis + web + socketio + scheduler + 2 worker queues — 1.5 GB was below ERPNext's 4 GB minimum. Visible in `docker info` as `MemTotal: ~1.47 GB`.

**What to do:** Edit `C:\Users\baenb\.wslconfig` `[wsl2]` section to `memory=8GB processors=4 swap=2GB` (the machine has 47.7 GB total — 8 GB is conservative). After edit, `wsl --shutdown` then run any docker command to wake the daemon with the new limits. Verify with `docker info | grep MemTotal`.

---

## 2026-04-25 — Frappe Cloud Sites plan is $5/mo per site, not $25-100; transfer is self-service

**What happened:** Quoted GL "$25-100/mo per client" early in a Frappe Cloud cost discussion based on bad memory of the pricing. GL was about to make decisions on bad numbers. Re-checked the actual pricing page.

**Real numbers (2026-04, verified at frappe.io/cloud/pricing):**
- **Sites plan**: starts at $5/month per site, includes custom apps, custom domain, SSH access
- **Servers plan**: starts at $20/month for the whole server, unlimited sites/benches
- **Free trial**: 14 days, no payment method

**Site transfer mechanism (verified at discuss.frappe.io/t/transfer-ownership-on-frappe-cloud/122800):** Self-service via the dashboard's Actions tab. Receiving Frappe Cloud team must exist (have GL's client create their own account first). Server-level transfer requires a support ticket; site-level does not.

**What to do:** When quoting hosting costs, verify against the live pricing page. Frappe's pricing has changed; training-data memory is unreliable. The cheap-and-transferable model is the right fit for the agency's "build → sell → transfer ownership" pattern.

---

## 2026-04-25 — When GL forbids touching one file, the boundary is the file (don't extrapolate to "GL must do the work")

**What happened:** GL said "leave odoo specific scripts and skills alone — we need to create ERPNext specific ones." I extrapolated this to "GL must be the executor of any production-touching work" and drafted a human-in-the-loop pattern where GL would paste production query results back to me. GL corrected: "the standard process is YOU preparing the script and executing it once it's been researched and built correctly."

**What to do:** When GL sets a boundary on a *file*, the boundary is on that file. Build new tooling elsewhere. The standard process — agent builds, agent tests, agent executes — still applies. Don't outsource execution to GL based on a misread of the boundary's scope.

---

## 2026-04-25 — Building infrastructure ≠ building the thing GL asked for

**What happened:** Spent significant tokens scaffolding GSD project structure (PROJECT.md, REQUIREMENTS.md, ROADMAP.md, config), then planning Phase 1 with research + planner + checker + revision iterations + threat models + validation strategies. Two ERPNext sites running but completely empty. Zero translation from Odoo had occurred. GL: "you haven't even rebuilt the site in ERPNext?! Focus on the rebuild."

**What to do:** When GL asks for a *thing*, the score is "is the thing built yet?" not "is there a beautiful planning artifact for the thing." Set up the minimum scaffolding required to start building, then start building. The planning machinery is meant to *serve* the build, not to *be* the build. If you find yourself iterating planner-checker loops on a phase that hasn't moved one bit closer to the deliverable, stop and start doing the deliverable.

This is the global anti-pattern #2 (Drift from GL's actual ask). Receipt added to `anti-gl-patterns.md` (project-local).
