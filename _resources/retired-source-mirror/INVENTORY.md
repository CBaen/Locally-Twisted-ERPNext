# legacy_source Live Mirror — Site Inventory
Source: `http://5.78.136.133/` (failed legacy_source test deployment)
Mirror: `_resources/retired-source-mirror/pages/` — 346 HTML files
Purpose: Reference for ERPNext rebuild visual/IA/content layer only. Backend stays (ERPNext webshop + Stripe + 45-field Lead schema).

---

## 1. Route Map (canonical → file)

### Static / Content Pages

```
/                          → pages/index.html          [71 KB]   — Homepage: hero carousel, Google reviews, service tiles, FAQ, CTA
/about                     → pages/about.html          [40 KB]   — About Jeff + Locally Twisted story
/accessibility             → pages/accessibility.html  [36 KB]   — Accessibility statement
/balloon-twisting-and-face-painting → pages/balloon-twisting-and-face-painting.html [68 KB] — Entertainment services landing
/book                      → pages/book.html           [68 KB]   — Event booking inquiry form (45-field Lead)
/contact                   → pages/contact.html        [50 KB]   — Short contact form + address + map
/gallery                   → pages/gallery.html        [32 KB]   — Photo gallery page
/privacy                   → pages/privacy.html        [33 KB]   — Privacy policy
/refund-policy             → pages/refund-policy.html  [32 KB]   — Refund policy
/services                  → pages/services.html       [32 KB]   — 404 page (route exists but content not published)
```

**Note:** `/contactus` (pages/contactus.html) is the same 50 KB contact page as `/contact` — legacy_source's built-in `/contactus` route. Canonical is `/contact`. One page, two routes; only one needed in ERPNext.

### Blog

```
/blog                                      → pages/blog.html                  [40 KB] — Blog index ("Behind the Balloons")
/blog/behind-the-balloons-1                → pages/blog_behind-the-balloons-1.html [40 KB] — Blog channel landing
/blog/behind-the-balloons-1/will-balloon-decor-survive-your-utah-summer-party-1 → pages/blog_behind-the-balloons-1_will-balloon-decor-survive-your-utah-summer-party-1.html [61 KB] — Single blog post
/blog/behind-the-balloons-1/i-dont-know-anything-about-balloon-decor-2 → pages/blog_behind-the-balloons-1_i-dont-know-anything-about-balloon-decor-2.html [64 KB] — Single blog post
```

Tag filter pages (`/blog/.../tag/...`) are parameter views of the same channel, not distinct content pages.

### Shop — All Products

```
/shop                      → pages/shop.html         [345 KB] — All products grid, sidebar category filter, sort dropdown, paginated (21/page)
/shop/page/2               → pages/shop_page_2.html  [347 KB] — Page 2
/shop/page/3               → pages/shop_page_3.html  [326 KB] — Page 3
/shop/cart                 → pages/shop_cart.html    [39 KB]  — Cart page
/shop/wishlist             → pages/shop_wishlist.html         — Wishlist (authenticated only)
```

Sort-variant files (`/shop?order=...`) are the same grid with a query param; not distinct pages.

### Shop — Category Landing Pages

```
/shop/category/special-occasions-1         → pages/shop_category_special-occasions-1.html         — Special Occasions (top-level)
/shop/category/special-occasions-birthday-parties-5       → pages/shop_category_special-occasions-birthday-parties-5.html
/shop/category/special-occasions-baby-reveal-showers-6    → pages/shop_category_special-occasions-baby-reveal-showers-6.html
/shop/category/special-occasions-graduations-8            → pages/shop_category_special-occasions-graduations-8.html
/shop/category/special-occasions-missionary-farewell-9    → pages/shop_category_special-occasions-missionary-farewell-9.html
/shop/category/special-occasions-get-well-40              → pages/shop_category_special-occasions-get-well-40.html
/shop/category/special-occasions-get-well-get-well-bouquets-42 → pages/shop_category_special-occasions-get-well-get-well-bouquets-42.html

/shop/category/holidays-seasons-2             → pages/shop_category_holidays-seasons-2.html             — Holidays & Seasons (top-level)
/shop/category/holidays-seasons-new-years-eve-10         → pages/shop_category_holidays-seasons-new-years-eve-10.html
/shop/category/holidays-seasons-valentines-day-12        → pages/shop_category_holidays-seasons-valentines-day-12.html   — empty (32 KB = 404-like)
/shop/category/holidays-seasons-st-patricks-day-13       → pages/shop_category_holidays-seasons-st-patricks-day-13.html
/shop/category/holidays-seasons-easter-14                → pages/shop_category_holidays-seasons-easter-14.html
/shop/category/holidays-seasons-mothers-day-16           → pages/shop_category_holidays-seasons-mothers-day-16.html
/shop/category/holidays-seasons-fathers-day-17           → pages/shop_category_holidays-seasons-fathers-day-17.html     — empty
/shop/category/holidays-seasons-pride-18                 → pages/shop_category_holidays-seasons-pride-18.html
/shop/category/holidays-seasons-4th-of-july-19           → pages/shop_category_holidays-seasons-4th-of-july-19.html     — empty
/shop/category/holidays-seasons-fall-20                  → pages/shop_category_holidays-seasons-fall-20.html            — empty
/shop/category/holidays-seasons-halloween-21             → pages/shop_category_holidays-seasons-halloween-21.html
/shop/category/holidays-seasons-christmas-24             → pages/shop_category_holidays-seasons-christmas-24.html       — empty

/shop/category/what-we-make-3              → pages/shop_category_what-we-make-3.html     — What We Make (top-level, paginated 3 pages)
/shop/category/what-we-make-26            → pages/shop_category_what-we-make-26.html     — alternate "What We Make" top-level
/shop/category/what-we-make-balloon-arches-26    → pages/shop_category_what-we-make-balloon-arches-26.html
/shop/category/what-we-make-columns-27           → pages/shop_category_what-we-make-columns-27.html
/shop/category/what-we-make-centerpieces-28      → pages/shop_category_what-we-make-centerpieces-28.html
/shop/category/what-we-make-helium-bouquets-29   → pages/shop_category_what-we-make-helium-bouquets-29.html
/shop/category/what-we-make-organic-garlands-30  → pages/shop_category_what-we-make-organic-garlands-30.html
/shop/category/what-we-make-backdrops-31         → pages/shop_category_what-we-make-backdrops-31.html
/shop/category/what-we-make-balloon-drops-32     → pages/shop_category_what-we-make-balloon-drops-32.html
/shop/category/what-we-make-grab-n-go-33         → pages/shop_category_what-we-make-grab-n-go-33.html
/shop/category/what-we-make-balloon-cups-34      → pages/shop_category_what-we-make-balloon-cups-34.html
/shop/category/what-we-make-table-decor-36       → pages/shop_category_what-we-make-table-decor-36.html
/shop/category/organic-garlands-31              → pages/shop_category_organic-garlands-31.html     — duplicate of what-we-make-backdrops-31?
/shop/category/backdrops-32                     → pages/shop_category_backdrops-32.html
/shop/category/balloon-arches-27               → pages/shop_category_balloon-arches-27.html
/shop/category/balloon-drops-33               → pages/shop_category_balloon-drops-33.html
/shop/category/birthday-parties-5             → pages/shop_category_birthday-parties-5.html
/shop/category/columns-28                     → pages/shop_category_columns-28.html
/shop/category/graduations-8                  → pages/shop_category_graduations-8.html
/shop/category/missionary-farewell-9          → pages/shop_category_missionary-farewell-9.html
/shop/category/personalized-displays-4       → pages/shop_category_personalized-displays-4.html
/shop/category/photo-frames-35               → pages/shop_category_photo-frames-35.html           — empty (32 KB)
/shop/category/table-decor-36                → pages/shop_category_table-decor-36.html
```

Category pages with `?order=...` query params are sorted views of the same grid — not distinct templates.

### Shop — Product Detail Pages (canonical slugs)

Products appear under multiple category prefixes (e.g. `/shop/basketball-arch-21`, `/shop/what-we-make-3/basketball-arch-21`, `/shop/special-occasions-1/basketball-arch-21`). All are the same product rendered with different breadcrumbs. Canonical slug = the non-prefixed route: `/shop/<slug>-<id>`.

Total distinct products: **53 mirrored** at top-level canonical URL. (86 IDs appear in the full crawl including all category-prefix variants.)

```
/shop/6-color-rainbow-arch-135
/shop/6-graduation-stands-149
/shop/7-8-tall-new-year-numbers-161
/shop/7-butterfly-column-125
/shop/7-epic-column-126
/shop/baby-shower-combination-photo-opt-14
/shop/baby-shower-garland-71
/shop/baby-table-decor-133
/shop/balloon-drop-74
/shop/bandage-get-well-bouquet-latex-free-146
/shop/basketball-arch-21
/shop/birthday-deliveries-128
/shop/butterfly-get-well-bouquet-latex-free-144
/shop/classic-arch-57
/shop/classic-column-58
/shop/classic-organic-arch-99
/shop/classic-organic-balloon-garland-19
/shop/classic-organic-columns-65
/shop/classic-organic-for-easel-152
/shop/custom-graduation-delivery-148
/shop/easter-arch-158
/shop/easter-balloon-arch-bunny-ear-30
/shop/easter-balloon-cups-130
/shop/elsa-bouquet-142
/shop/encanto-bouquet-118
/shop/event-booking-deposit-32             — 404 in the crawl; product was unpublished
/shop/flamingo-bouquet-120
/shop/football-bouquet-121
/shop/graduation-bouquet-150
/shop/graduation-grab-n-go-38
/shop/halloween-arch-39
/shop/holy-cow-bouquet-143
/shop/large-garland-177
/shop/large-head-missionary-45
/shop/large-organic-column-178
/shop/logo-3-layered-bouquet-134
/shop/magic-gender-reveal-136
/shop/marble-table-decor-140
/shop/mickey-mouse-bouquet-116
/shop/minion-bouquet-117
/shop/missionary-homecoming-display-104
/shop/mothers-day-bouquet-165
/shop/mothers-day-front-yard-7-column-137
/shop/number-balloon-columns-22
/shop/organic-grab-n-go-127
/shop/over-the-hill-bouquet-124
/shop/paw-patrol-bouquet-141
/shop/pemium-organic-column-54             — note: "pemium" is a typo in the original slug
/shop/premium-organic-arch-53
/shop/premium-organic-garland-52
/shop/pride-arch-179
/shop/pride-progress-rainbow-balloon-arch-55
/shop/shooting-star-get-well-bouquet-latex-free-147
/shop/sleepy-baby-column-132
/shop/soccer-bouquet-122
/shop/space-bouquet-123
/shop/star-column-131
/shop/stitch-bouquet-119
/shop/unicorn-bouquet-115
```

Some product IDs appear in the crawl only under category prefixes (never captured at top-level): `baby-table-decor-133`, `easter-arch-158`, `mothers-day-front-yard-7-column-137`, `6-graduation-stands-149`, etc.

### Auth / Skip

```
/web/login          → pages/web_login.html        — legacy_source auth — skip
/web/signup         → pages/web_signup.html       — legacy_source auth — skip
/web/reset_password → pages/web_reset_password.html — legacy_source auth — skip
```

---

## 2. Header Markup

From `pages/index.html` (lines 286–635). Two navs — desktop (`.d-none.d-lg-block`) and mobile (`.d-block.d-lg-none`).

```html
<!-- DESKTOP NAV -->
<header id="top" data-anchor="true" class="o_header_standard">
<nav class="navbar navbar-expand-lg navbar-light o_colored_level o_cc d-none d-lg-block shadow-sm lt-header">
  <div id="o_main_nav" class="o_main_nav">

    <!-- Utility bar: delivery truck tagline | logo | sign-in + cart + CTA -->
    <div class="container lt-utility-bar d-flex align-items-center justify-content-between py-2">
      <div class="lt-utility-left">
        <i class="fa fa-truck lt-delivery-truck"></i>
        <span class="lt-utility-text">Bringing celebration to the Wasatch Front since 1998</span>
      </div>
      <div class="lt-utility-center">
        <a href="/" class="navbar-brand logo">
          <img src="/web/image/website/1/logo/..." alt="Locally Twisted" width="1050" height="300">
        </a>
      </div>
      <ul class="navbar-nav lt-utility-right align-items-center gap-2">
        <li><a href="/web/login" class="o_nav_link_btn nav-link border px-3">Sign in</a></li>
        <li class="o_wsale_my_cart nav-item">
          <a href="/shop/cart" aria-label="eCommerce cart" class="nav-link">
            <i class="fa fa-shopping-cart fa-stack"></i>
            <sup class="my_cart_quantity badge bg-primary d-none">0</sup>
          </a>
        </li>
        <li>
          <a href="/contactus" class="btn btn-primary btn_cta">Contact Us</a>
        </li>
      </ul>
    </div>

    <!-- Primary nav: Balloon Twisting | Special Occasions (mega) | Holidays & Seasons (mega) | What We Make (mega) | [+overflow: Contact, Blog] | search -->
    <div class="container d-flex align-items-center pb-2">
      <ul id="top_menu" class="nav navbar-nav top_menu justify-content-center">
        <li class="nav-item"><a href="/balloon-twisting-and-face-painting">Balloon Twisting &amp; Face Painting</a></li>
        <li class="nav-item dropdown">
          <a data-bs-toggle="dropdown" class="dropdown-toggle nav-link o_mega_menu_toggle">Special Occasions</a>
          <div class="o_mega_menu dropdown-menu"><!-- mega menu content --></div>
        </li>
        <li class="nav-item dropdown">
          <a class="dropdown-toggle nav-link o_mega_menu_toggle">Holidays &amp; Seasons</a>
          <div class="o_mega_menu dropdown-menu"><!-- mega menu content --></div>
        </li>
        <li class="nav-item dropdown">
          <a class="dropdown-toggle nav-link o_mega_menu_toggle">What We Make</a>
          <div class="o_mega_menu dropdown-menu"><!-- mega menu content --></div>
        </li>
        <li class="o_extra_menu_items dropdown"><!-- Contact, Blog overflow --></li>
      </ul>
      <!-- search modal trigger -->
      <a data-bs-target="#o_search_modal" data-bs-toggle="modal" class="btn rounded-circle o_not_editable">
        <i class="oi oi-search"></i>
      </a>
    </div>
  </div>
</nav>

<!-- MOBILE NAV -->
<nav class="navbar navbar-light d-block d-lg-none shadow-sm o_header_mobile">
  <!-- logo | cart | wishlist | hamburger toggler -->
  <!-- offcanvas drawer: search input + same nav items + Sign in + Contact Us CTA -->
</nav>
</header>
```

**legacy_source class conventions used:**
- `o_header_standard`, `o_colored_level`, `o_cc` — legacy_source theme color-cascade
- `o_mega_menu`, `o_mega_menu_toggle` — legacy_source mega menu engine
- `o_wsale_my_cart` — legacy_source ecommerce cart widget
- `o_extra_menu_items` — legacy_source overflow nav items
- `o_not_editable`, `oe_unremovable`, `oe_unmovable` — legacy_source editor guards
- `s_text_block`, `oe_structure`, `oe_structure_solo` — legacy_source snippet containers
- `lt-header`, `lt-utility-bar`, `lt-utility-left`, `lt-utility-right`, `lt-mega-heading`, `lt-mega-link`, `lt-mega-cta` — custom LT classes

---

## 3. Footer Markup

From `pages/index.html` (lines 1111–1223).

```html
<footer id="bottom" class="o_footer o_colored_level o_cc">

  <!-- Newsletter strip -->
  <section class="s_lt_footer_newsletter">
    <div class="container text-center">
      <p class="s_lt_newsletter_heading">Stay in the loop</p>
      <p class="s_lt_newsletter_text">Seasonal specials, new designs, and celebration ideas.</p>
      <div class="js_subscribe" data-list-id="2">
        <div class="input-group s_lt_newsletter_form">
          <input type="email" class="js_subscribe_value form-control" placeholder="Your email address">
          <button class="btn btn-primary js_subscribe_btn">Join</button>
        </div>
      </div>
    </div>
  </section>

  <!-- Main footer: brand + social + 3-column links + contact info -->
  <section class="s_lt_footer_main">
    <div class="container">
      <div class="text-center s_lt_footer_social_row">
        <p class="s_lt_footer_brand">Locally Twisted</p>
        <p class="s_lt_footer_tagline">Utah's Balloon Specialists since 1998.</p>
        <nav class="s_lt_footer_social">
          <a href="https://facebook.com/locallytwisted" class="s_lt_social_icon s_lt_social_facebook"><i class="fa fa-facebook"></i></a>
          <a href="https://instagram.com/locally_twisted" class="s_lt_social_icon s_lt_social_instagram"><i class="fa fa-instagram"></i></a>
          <a href="https://pinterest.com/locallytwisted" class="s_lt_social_icon s_lt_social_pinterest"><i class="fa fa-pinterest"></i></a>
        </nav>
      </div>
      <nav class="row s_lt_footer_links_row">
        <div class="col-12 col-md-4 s_lt_footer_col">
          <p class="s_lt_footer_col_title">Shop</p>
          <!-- All Products, Special Occasions, Holidays & Seasons, What We Make -->
        </div>
        <div class="col-12 col-md-4 s_lt_footer_col">
          <p class="s_lt_footer_col_title">Company</p>
          <!-- About Us, Balloon Twisting, Book an Event, Blog, Contact -->
        </div>
        <div class="col-12 col-md-4 s_lt_footer_col">
          <p class="s_lt_footer_col_title">Get In Touch</p>
          <!-- West Jordan UT | (801) 285-0860 | Tue-Fri 12-6, Sat 10-4 -->
        </div>
      </nav>
    </div>
  </section>

  <!-- Legal bar -->
  <section class="s_lt_footer_bar">
    <div class="container text-center">
      <span class="s_lt_footer_legal">
        © 2026 Locally Twisted. All rights reserved.
        | <a href="/refund-policy">Refund Policy</a>
        | <a href="/accessibility">Accessibility</a>
      </span>
    </div>
  </section>

</footer>
```

**Social links:** Facebook (`/locallytwisted`), Instagram (`/locally_twisted`), Pinterest (`/locallytwisted`).
**Hours block** is in the "Get In Touch" column — text only, not schema-encoded in footer.
**No Google Maps iframe in footer** (it's on the /contact page sidebar).
**Newsletter JS** uses `js_subscribe` / `js_subscribe_value` — legacy_source mailing list widget. ERPNext equivalent is a custom handler.

legacy_source classes: `o_footer`, `js_subscribe`, `js_subscribe_btn`, `js_subscribe_value`.
Custom LT classes: `s_lt_footer_newsletter`, `s_lt_footer_main`, `s_lt_footer_bar`, `s_lt_footer_social`, `s_lt_footer_brand`, `s_lt_footer_col_title`, `s_lt_footer_legal`.

---

## 4. /book Form Schema

From `pages/book.html`. Form posts to `/website/form/` targeting `crm.lead`.
Success redirect: `/book#received` (triggers confirmation modal via JS `hashchange` listener).
File upload: 5 images × 25 MB each, accepts JPEG/PNG/GIF/WebP/HEIC.

All fields map to ERPNext Lead Custom Fields — names already match the 45-field schema built on the ERPNext side.

### Always-visible fields

| Field name | Type | Label | Required |
|---|---|---|---|
| `name` | hidden | (internal) sets Lead name = "Booking Request" | — |
| `contact_name` | text | Your Name | yes |
| `phone` | tel | Phone | yes |
| `email_from` | email | Email | yes |
| `partner_name` | text | Company | no |
| `x_occasion_type` | select | What are you celebrating? | no |
| `x_event_date` | date | Event Date | no |
| `x_event_time` | time | Preferred Event Time | no |
| `x_event_location` | text | City / Location | no |
| `x_guest_count` | number (min 1) | Estimated Guests | no |
| `x_services` | checkbox group (multi) | What services are you interested in? | no |
| `ufile` | file (multiple) | Inspiration photos | no |
| `description` | textarea | Anything else we should know? | no |

`x_occasion_type` options: Birthday Party, School Event, Corporate Event, Festival / Fair, Church Event, Family Reunion, Holiday Party, Other.

`x_services` checkbox values: "Balloon Decor", "Balloon Twisting", "Face Painting", "Delivery Only", "Event Package", "Something Else".

### Conditional fields (shown when service checkbox selected)

Conditional logic is handled by inline JS — `data-visibility-dependency`, `data-visibility-comparator`, `data-visibility-condition` attributes on wrapper divs. When the parent condition is met the wrapper's `d-none` is removed and nested `disabled` is cleared on all inputs.

**When "Balloon Decor" checked:**
| Field name | Type | Label |
|---|---|---|
| `x_decor_types` | text | What type of decor? |
| `x_setup_time_arrival` | time | What time can we arrive to set up? |
| `x_decor_notes` | textarea | Decor notes |

**When "Balloon Twisting" checked:**
| Field name | Type | Label |
|---|---|---|
| `x_num_twisters` | number | Number of twisters |
| `x_artist_start` | time | Start time |
| `x_artist_end` | time | End time |
| `x_twisting_notes` | textarea | Twisting notes |

**When "Face Painting" checked:**
| Field name | Type | Label |
|---|---|---|
| `x_num_painters` | number | Number of face painters |
| `x_painter_start` | time | Start time |
| `x_painter_end` | time | End time |
| `x_painting_notes` | textarea | Face painting notes |

**When "Delivery Only" checked:**
| Field name | Type | Label |
|---|---|---|
| `x_delivery_notes` | textarea | Delivery time frame |

**When "Event Package" checked:**
| Field name | Type | Label |
|---|---|---|
| `x_package_notes` | textarea | Tell us what you're envisioning |

**When "Something Else" checked:**
| Field name | Type | Label |
|---|---|---|
| `x_other_notes` | textarea | Describe what you're looking for |

**When ANY service is checked (any value in `x_services`):**
| Field name | Type | Label |
|---|---|---|
| `x_indoor_outdoor` | select | Indoor / Outdoor (options: Indoor, Outdoor, Both) |
| `x_shade_required` | checkbox | Shade is required for outdoor events |
| `x_colors` | text | Color preferences |

### JS behaviors (inline `<script>` blocks)

1. **File validation:** `change` handler on `input[name="ufile"]` — enforces max 5 files, max 25 MB each. Shows error in `#book_photos_hint`. Clears the input if violated.
2. **Conditional show/hide:** Reads all checked `input[name="x_services"]` values. Finds wrappers with `data-visibility-dependency="x_services"`. Two comparators: `contains` (specific service) and `set` (any service checked). Removes/adds `d-none` and toggles `disabled` on nested inputs/selects/textareas.
3. **Confirmation modal:** Watches `window.location.hash` and `fetch` intercepts. If hash becomes `#received` OR fetch response URL ends with `/website/form/` + response is success, shows the confirmation modal overlay. Also listens for `hashchange` to handle legacy_source's redirect-without-reload pattern.

Total form fields: 30+ (varies by service selection). 10 always-visible; up to 20 additional conditional.

---

## 5. /contact Form Schema

From `pages/contact.html`. Form posts to `/website/form/` targeting `crm.lead`.
Success redirect: `/contact#received`.
No file upload.

| Field name | Type | Label | Required |
|---|---|---|---|
| `name` | text | Your Name | yes |
| `email_from` | email | Email | yes |
| `phone` | tel | Phone | no |
| `event_type` | select | Event Type | no |
| `event_date` | date | Event Date | no |
| `body` | textarea (4 rows) | Tell Us About Your Event | no |

`event_type` options: Birthday Party, Wedding, Baby Shower, Corporate Event, Grand Opening, Other.

**Note:** Contact form uses `name="name"` (not `contact_name` like /book). Field naming inconsistency between the two forms — the ERPNext backend normalizes these.

Sidebar content (right col on desktop): phone number `(801) 285-0860`, "Book a Free Phone Consultation" CTA, Google Maps iframe of 8969 S 2700 W West Jordan UT.

Confirmation modal similar to /book — watches `#received` hash.

---

## 6. Product Page Pattern

### 6a. Premium Organic Arch (shop_premium-organic-arch-53.html — 139 KB, high-variant)

**Title block:**
```html
<h1 class="h3">Premium Organic Arch</h1>
<div class="oe_structure mb-3 text-muted">
  Primium organic arch using up to 24" balloons. 20' arch is great for a single door...
</div>
```
Description text is in an legacy_source editable `oe_structure` div — plain div content, not a tab.

**Gallery:** Single carousel (`#o-carousel-product`, class `o_carousel_product_left_indicators`). One image shown at page load (only 1 `data-image-amount`). No thumbnail strip — left-indicator dots only. Zoom enabled via `data-zoom` + `data-zoom-image` on `<img>`.

**Variant selectors — two attributes:**
1. **Arch Size** (`data-attribute-display-type="pills"`) — radio buttons styled as pill buttons. Values: 20ft (base $770), 25ft (+$180), 30ft (+$360), 35ft (+$540). Price delta shown inline as `(+$X.XX)`.
2. **latex colors** (`data-attribute-display-type="multi"`) — checkboxes with swatch images (48×48 px). ~53 colors. `class="no_variant"` means color selection doesn't create a new product.product record; it's captured as a note/attribute. Also a third attribute: **Add ons** (Foil stars / themed foils) — also `no_variant` checkboxes.

**Price display:** `<span class="oe_price">$770.00</span>` — single price (not range). Updates client-side when size is changed via legacy_source's `js_variant_change` JS. Base price = lowest variant.

**Add-to-cart form:**
```html
<input type="hidden" name="product_id" value="441">
<input type="hidden" name="product_template_id" value="53">
<a id="add_to_cart" class="btn btn-primary js_check_product a-submit">Add to cart</a>
<div class="css_quantity input-group">
  <a class="css_quantity_minus js_add_cart_json">−</a>
  <input type="text" name="add_qty" class="quantity" value="1">
  <a class="css_quantity_plus js_add_cart_json">+</a>
</div>
```
Also: Compare + Wishlist buttons (`o_add_compare_dyn`, `o_add_wishlist_dyn`).

**Below-the-fold product sections:**
1. **"Customize This for Your Event"** — mini Lead inquiry form (name, email, occasion, event date, free-text vision). Posts to `/website/form/` → `crm.lead`. Appears on every product page, pre-filled with product name.
2. **Specifications** — `<table>` listing attribute names and all their values (Arch Size: 20ft, 25ft, 30ft, 35ft; latex colors: [53 items]; Add ons: Foil stars, themed foils).

**No related products section.** No product detail tabs (single description div, not a tab component).

---

### 6b. Basketball Arch (shop_basketball-arch-21.html — 62 KB, low-variant)

Same structure as 6a but simpler:
- **1 attribute only:** Arch Size, pills, 2 values: 20ft ($340 base), 25ft (+$85).
- **No color/add-on selectors.**
- Gallery: 1 image.
- Description: blank (no `oe_structure` content).
- Product inquiry form present.
- Specifications table shows: Arch Size: 20ft, 25ft.

---

### 6c. Event Booking Deposit (shop_event-booking-deposit-32.html — 33 KB)

**This page is a 404.** The product was unpublished (or deleted) before the crawl. The mirrored file contains legacy_source's standard 404 page ("We couldn't find the page you're looking for!") with nav/footer. No product detail markup. The ERPNext rebuild has its own deposit handling — this reference is not needed.

---

### Common product page template

All product pages share:
- `id="wrap" class="js_sale o_wsale_product_page ecom-zoomable"` on the main wrapper
- `section#product_detail.oe_website_sale.lt-product-detail` containing breadcrumb + sticky image col + sticky details col
- `#product_detail_main` with `data-image_layout="carousel"` (single-image carousel, not multi)
- `#o_wsale_product_details_content.js_product.js_main_product` for the details side
- Price in `div[name="product_price"] span.oe_price span.oe_currency_value`
- Variant list in `ul.o_wsale_product_page_variants.js_add_cart_variants` with `data-attribute-exclusions` JSON
- Add-to-cart in `div#o_wsale_cta_wrapper`
- Specifications table in `section#product_full_spec div#product_specifications`
- Customization inquiry mini-form in `section.s_lt_product_inquiry`
- Custom class `lt-product-detail` on the section — means the site already has custom CSS for this section

---

## 7. /shop Landing Page Pattern

From `pages/shop.html` (345 KB, 21 products/page, 3 pages total).

**Left sidebar (desktop, `aside#products_grid_before`, sticky, hidden on mobile):**
- **Categories accordion** (`div.products_categories`) — nested `<ul class="nav">` tree of all categories with hierarchy indentation via `ul.nav-hierarchy.ps-3`.
- **Attribute filters** (`div.products_attributes_filters`) — collapsible accordion section. Contains checkboxes for each attribute value across all visible products (e.g. "Arch Size: 20ft", "Arch Size: 25ft"). No price-range slider visible in the crawl.

**Top bar (desktop + mobile):**
- Pricelist dropdown (hidden `d-none` — pricelist feature disabled)
- Sort dropdown (`div.o_sortby_dropdown`): Featured, Newest Arrivals, Name A-Z, Price Low-High, Price High-Low
- "Filters" button (mobile only) — opens offcanvas sidebar

**Product grid:**
```html
<section id="o_wsale_products_grid"
  class="o_wsale_products_grid_table grid o_wsale_products_opt_layout_catalog
         o_wsale_products_opt_design_thumbs o_wsale_products_opt_rounded_2
         o_wsale_products_opt_thumb_cover o_wsale_products_opt_has_cta
         o_wsale_products_opt_actions_onhover o_wsale_products_opt_has_wishlist
         o_wsale_products_opt_has_description o_wsale_products_opt_actions_subtle"
  style="--o-wsale-ppr: 3; --o-wsale-ppg: 21; --o-wsale-products-grid-gap: 16px;">

  <div class="oe_product g-col-6 g-col-md-4 g-col-lg-4">       <!-- 2-col mobile, 3-col desktop -->
    <div class="o_wsale_product_grid_wrapper o_wsale_product_grid_wrapper_1_1">  <!-- 1:1 ratio -->
      <form class="oe_product_cart">
        <div class="oe_product_image">                           <!-- image + ribbon + wishlist icon on hover -->
          <a href="/shop/baby-shower-combination-photo-opt-14" class="oe_product_image_link">
            <span class="oe_product_image_img_wrapper_primary">
              <img src="..." class="oe_product_image_img h-100 w-100">
            </span>
            <span class="o_ribbons"></span>
          </a>
        </div>
        <div class="o_wsale_product_information">
          <h2 class="o_wsale_products_item_title"><a href="...">Baby Shower Combination Photo opt</a></h2>
          <div class="oe_subdescription text-muted small"></div>  <!-- empty on most products -->
          <div class="o_wsale_product_sub">
            <div class="product_price">
              <span class="oe_currency_value">$650.00</span>     <!-- or "$340.00 – $425.00" for ranges -->
            </div>
            <div class="o_wsale_product_btn">
              <button class="o_wsale_product_btn_primary btn btn-primary a-submit">Add to Cart</button>
              <button class="o_add_wishlist btn">Add to wishlist</button>
            </div>
          </div>
        </div>
      </form>
    </div>
  </div>
  <!-- repeat for each product -->
</section>
```

**Pagination:**
```html
<ul class="pagination m-0">
  <li><a class="page-link">‹</a></li>      <!-- prev (disabled on page 1) -->
  <li><a href="/shop" class="page-link">1</a></li>
  <li><a href="/shop/page/2" class="page-link">2</a></li>
  <li><a href="/shop/page/3" class="page-link">3</a></li>
  <li><a href="/shop/page/2" class="page-link">›</a></li>   <!-- next -->
</ul>
```

Category pages use the same layout — sidebar, grid, pagination — with `/shop/category/<slug>/page/N` for multi-page categories.

---

## 8. Distinct Page Templates Needed in Frappe

| Template | Routes | Key features |
|---|---|---|
| `lt_home.html` | `/` | Hero carousel (3 slides, CSS bg images), reviews strip, service tiles, FAQ accordion, CTAs |
| `lt_standard_page.html` | `/about`, `/gallery`, `/services`, `/accessibility`, `/refund-policy`, `/privacy` | Header + footer + single rich-text content region |
| `lt_book.html` | `/book` | 30+ field Lead form, conditional JS show/hide, file upload (5×25 MB), confirmation modal on `#received` |
| `lt_contact.html` | `/contact` | 6-field Lead form, sidebar contact card + Google Maps iframe, confirmation modal on `#received` |
| `lt_balloon_twisting.html` | `/balloon-twisting-and-face-painting` | Services landing — content-heavy, likely needs hero image + service detail blocks |
| `lt_blog_channel.html` | `/blog`, `/blog/<channel>` | Blog channel listing — post cards with cover image, title, excerpt, date, tags |
| `lt_blog_post.html` | `/blog/<channel>/<post>` | Single blog post — long-form content, hero image, tag sidebar, share links |
| ERPNext Webshop `/all-products` | `/shop`, `/shop/page/N` | Already provided by ERPNext webshop — customize layout/CSS only |
| ERPNext Webshop `/shop/category/<slug>` | `/shop/category/...` | Already provided by ERPNext webshop — same as above |
| ERPNext Webshop product detail | `/shop/<slug>-<id>` | Product detail with variant selectors — already in ERPNext webshop. Custom addition: `s_lt_product_inquiry` mini-form beneath description |
| ERPNext Cart | `/shop/cart` | Already provided by ERPNext webshop |

Note: `/services` returns 404 in the crawl — the route exists on the legacy_source site but the page was unpublished. It maps to the standard page template if content is added.

---

## 9. Asset Inventory Summary

From `manifest.json`. 622 assets total.

| Extension | Count | Notes |
|---|---|---|
| `.svg` | 279 | legacy_source UI icons (FontAwesome, OWL components, legacy_source icon set). Do not copy. |
| (no extension / dynamic URLs) | 285 | legacy_source dynamic endpoints (`/web/image/product.template/...`, `/web/static/...`). Product images served via legacy_source's image controller — not static files. |
| `.webp` | 28 | **Product photos + variant swatch images** — see below |
| `.js` | 16 | legacy_source bundle JS (assets_frontend_minimal, assets_frontend_lazy, etc.). Do not copy. |
| `.png` | 3 | LT logo + legacy_source transparent placeholder + webshop placeholder thumbnail |
| `.jpg` | 3 | Hero slide backgrounds (slide_1.jpg, slide_2.jpg, slide_3.jpg) |
| `.css` | 2 | legacy_source bundle CSS. Do not copy. |
| `.woff2 / .woff` | 4 | FontAwesome webfont. Do not copy — ERPNext ships its own FontAwesome. |

### Assets to copy verbatim into ERPNext app

These are genuine LT brand assets — not legacy_source framework files:

| Source path | Description | Copy to |
|---|---|---|
| `assets/locally_twisted/static/src/img/locally-twisted-logo.png` | LT logo | `apps/locally_twisted/.../public/images/` |
| `assets/locally_twisted/static/src/img/hero/slide_1.jpg` | Hero background 1 | same |
| `assets/locally_twisted/static/src/img/hero/slide_2.jpg` | Hero background 2 | same |
| `assets/locally_twisted/static/src/img/hero/slide_3.jpg` | Hero background 3 | same |
| `assets/web/image/product.image/*/image_1024/*.webp` | Product photos (28 files) | Webshop items already have these via ERPNext product image field — verify before copying |
| OG images referenced in `<meta property="og:image">` (og-home.png, og-book.png, og-contact.png) | OpenGraph images — not in manifest (not crawled as assets) | Source from Hetzner directly or recreate |

The 28 `.webp` files in `assets/web/image/product.image/` are product photos at 1024px and 128px thumbnail sizes. They're already in ERPNext as product images (imported in the catalog port 2026-04-30). The swatch images for latex colors (`/web/image/product.attribute.value/<id>/image`) were not captured in the asset crawl (dynamic URLs with no extension).

---

## 10. Open Questions / Oddities

1. **`/shop/event-booking-deposit-32` is a 404.** The deposit product (ID 32) was unpublished before the crawl. The 33 KB file is legacy_source's generic 404 page. If a deposit flow is needed in ERPNext, it needs to be built fresh — there's no reference page here.

2. **Two "What We Make" top-level categories exist:** `/shop/category/what-we-make-3` (ID 3, paginated 3 pages) and `/shop/category/what-we-make-26` (ID 26, single page, 163 KB). The nav mega menu points at `/shop/category/what-we-make-3` as "Shop All Products." ID 26 is the `what-we-make` category shown as a nav item "What We Make" in the footer. These are two different category nodes in the legacy_source tree that both cover the same product set — the ERPNext category tree will need a decision on this.

3. **Several category pages are empty (32 KB body):** holidays-seasons-valentines-day-12, holidays-seasons-fathers-day-17, holidays-seasons-4th-of-july-19, holidays-seasons-fall-20, holidays-seasons-christmas-24, photo-frames-35, services. These categories exist in the nav but had no published products at crawl time. They'll appear in the category tree in ERPNext webshop — either populate them or suppress them from display.

4. **`/services` is a 404.** The page title is "Page Not Found | Locally Twisted." If a /services route is needed, it must be built fresh.

5. **`/contactus` duplicates `/contact`.** legacy_source routes `/contactus` to its built-in contact controller. The crawled files are identical except for minor byte differences (50192 vs 50201 bytes). ERPNext does not have a `/contactus` route by default — a redirect `/contactus → /contact` is needed or the nav "Contact Us" button should point to `/contact` only.

6. **The nav "Contact Us" CTA button points to `/contactus` (the legacy_source default route), not `/contact`.** All internal links in nav use `/contactus` for this button. The canonical contact page is `/contact`. ERPNext rebuild should standardize on `/contact`.

7. **Product page image carousels are single-image.** `data-image-amount="1"` on all crawled product pages. Multi-image carousels would require product images to be uploaded as extras in ERPNext — not present in this legacy_source build.

8. **Color swatch images (`/web/image/product.attribute.value/<id>/image`)** are served as legacy_source dynamic image URLs. These were not captured in the asset crawl. In ERPNext, `ItemAttributeValue` has a `colour` field for hex codes only — swatch images would require a custom field or a different approach (e.g., color-picker tiles).

9. **Wishlist is authenticated-only.** `/shop/wishlist` requires login. The nav shows `o_wsale_my_wish_hide_empty` with `d-none` class — hidden unless items exist. ERPNext webshop has wishlist support but it behaves differently. Treat as low priority.

10. **`pemium-organic-column-54` has a typo in the slug.** "pemium" (missing 'r'). The ERPNext catalog port presumably preserved this slug — verify.

11. **The mini product inquiry form** (`section.s_lt_product_inquiry`) appears on product pages below the description. This is a custom legacy_source snippet. In the ERPNext rebuild, this form needs to be added to the webshop product detail template. It posts a Lead with `name = "Product Inquiry: <product name>"` and 4 fields (name, email, occasion, event date, vision text).

12. **Blog tag filter pages** are pure parameter views — no distinct content. The ERPNext blog built-in supports tags; no special page templates needed beyond the channel and post templates.

13. **`shop_baby-shower-combination-photo-opt-14.html` has an unusual name** — "Photo opt" suggests it may be a configurable photography option product, not a standard balloon piece. Worth confirming with Jeff.
