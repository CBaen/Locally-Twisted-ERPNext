# Ground Truth Findings: LT Codebase + Frappe Container + catalog_data Source
## Date: 2026-04-26
## Source Type: Codebase, Git History, Container Inspection, catalog_data Source XML
## Project: Locally Twisted
## Files Examined: 47

---

## Approved Jeff-Vetted Content From Local catalog_data Source

This is the most load-bearing section. Every string below was pulled verbatim from XML in `/home/guidingl/projects/external-catalog-data/addons/locally_twisted/views/`. The catalog_data project contains far more view files than the brief anticipated. Full list of XML files found (43 total):

- `views/header.xml` — two-tier header with utility strip
- `views/footer.xml` — newsletter + 3-column footer + copyright bar
- `views/homepage.xml` — homepage structure (section references, not copy)
- `views/snippets/s_lt_hero.xml` — hero carousel copy
- `views/snippets/s_lt_cta.xml` — call-to-action section
- `views/snippets/s_lt_trust_bar.xml` — trust items
- `views/snippets/s_lt_twisting.xml` — balloon twisting section copy + image refs
- `views/snippets/s_lt_categories.xml` — category navigation circles
- `views/snippets/s_lt_reviews.xml` — Google Reviews badge
- `views/snippets/s_lt_client_crawl.xml` — client name crawl (50 names)
- `views/snippets/s_lt_local_favorites.xml` — product showcase (placeholder)
- `views/snippets/s_lt_featured_products.xml` — seasonal products (placeholder)
- `views/pages/page_balloon_twisting.xml` — full BTFP service page
- `views/pages/page_about.xml` — about us page
- Additional: `page_contact.xml`, `page_book.xml`, `page_refund_policy.xml`, `page_accessibility.xml`, `s_lt_blog_posts.xml`, `s_lt_cta_alt.xml`, `s_lt_gallery_grid.xml`, `s_lt_img_text.xml`, `s_lt_service_cards.xml`, `s_lt_testimonials.xml`, `snippets.xml` (snippet registry), `seo_head.xml`, `whitelabel.xml`, `blog_templates.xml`, `website_sale_templates.xml`, and backend views

### HEADER (`views/header.xml`)

**Structure:** Two-tier navbar with utility strip

**Tier 1 — Utility bar (top row):**
- Left: `<i class="fa fa-truck"/>` + text: "Bringing celebration to the Wasatch Front since 1998"
- Center: Logo (via `website.placeholder_header_brand`)
- Right: Sign In | User Dropdown | Cart icon | CTA button

**Tier 2 — Nav row:**
- Flex row: left spacer | centered nav menu | right search box
- Nav renders from `website.menu_id.child_id`

**Mobile header:**
- Delivery strip above mobile header: `"Bringing celebration to the Wasatch Front since 1998"` with truck icon
- Hides the "text element" placeholder from the mobile offcanvas menu

**Key CSS classes used:** `lt-header`, `lt-utility-bar`, `lt-utility-left`, `lt-utility-center`, `lt-utility-right`, `lt-delivery-truck`, `lt-utility-text`, `lt-mobile-delivery`

### FOOTER (`views/footer.xml`)

**Structure:** Newsletter signup above footer + 3-column links + copyright bar

**Newsletter band (above footer):**
- Heading: "Stay in the loop"
- Body: "Seasonal specials, new designs, and celebration ideas."
- Input placeholder: "Your email address"
- Button label: "Join"
- Success message: "You're on the list. Welcome."

**Footer main (on Soft Blue):**
- Brand name: "Locally Twisted"
- Tagline: "Utah's Balloon Specialists since 1998."
- Social icons: Facebook (`https://facebook.com/locallytwisted`), Instagram (`https://instagram.com/locally_twisted`), Pinterest (`https://pinterest.com/locallytwisted`) — 3 icons total, NO Twitter

**Footer columns (always 3 across):**

Column 1 — "Shop":
- All Products → `/shop`
- Special Occasions → `/shop/category/special-occasions-1`
- Holidays & Seasons → `/shop/category/holidays-seasons-2`
- What We Make → `/shop/category/what-we-make-26`

Column 2 — "Company":
- About Us → `/about`
- Balloon Twisting → `/balloon-twisting-and-face-painting`
- Book an Event → `/book`
- Behind the Balloons → `/blog`
- Contact → `/contact`

Column 3 — "Get In Touch":
- Location: "West Jordan, UT" (address icon)
- Phone: `(801) 285-0860` → `tel:+18012850860`
- Hours: "Tue-Fri 12-6, Sat 10-4" (clock icon)

**Copyright bar:**
- "© 2026 Locally Twisted. All rights reserved. | Refund Policy | Accessibility"
- Links: `/refund-policy`, `/accessibility`

**NOTE:** The footer does NOT include a Twitter/X social link. The `setup_slice2_header_footer.py` script added Twitter — that was wrong per the catalog_data source.

### HOMEPAGE (`views/homepage.xml` + snippet files)

**Section order:**
1. Hero Carousel (`locally_twisted.s_lt_hero`)
2. Google Reviews Badge (`locally_twisted.s_lt_reviews`)
3. Balloon Twisting & Face Painting spotlight (`locally_twisted.s_lt_twisting`)
4. Trust Bar — Soft Blue band (`locally_twisted.s_lt_trust_bar`)
5. Custom Creations Categories (`locally_twisted.s_lt_categories`)
6. Grey divider (HR element)
7. Seasonal Favorites — placeholder (`locally_twisted.s_lt_featured_products`)
8. Client Logo Crawl (`locally_twisted.s_lt_client_crawl`)
9. Local Favorites — placeholder (`locally_twisted.s_lt_local_favorites`)
10. Call to Action (`locally_twisted.s_lt_cta`)

**Meta title:** "Locally Twisted — Utah's Balloon Specialists | Custom Event Decor"
**Meta description:** "Utah's premier balloon specialists for over 20 years. Custom arches, garlands, drops, twisting, and face painting for weddings, birthdays, and corporate events across the Wasatch Front."

#### Hero Carousel (`s_lt_hero.xml`)

Slide 1 (active):
- H1: "Utah's Balloon Specialists"
- Lead: "Making celebrations unforgettable since 1998"
- CTA: "Shop Now" → `/shop`

Slide 2:
- H2: "Custom Balloon Designs"
- Lead: "Tailored to your vision, crafted with love"
- CTA: "Contact Us" → `/contact`

Slide 3:
- H2: "Events & Special Occasions"
- Lead: "From intimate gatherings to grand occasions"
- CTA: "Browse Shop" → `/shop`

Auto-advance: `data-bs-interval="5000"` (5 seconds)
Accessible: `role="region"`, `aria-roledescription="carousel"`, pause button, prev/next labels

#### Google Reviews Badge (`s_lt_reviews.xml`)

Static display:
- Score: "4.9"
- Stars: 5 filled stars
- Count: "114 reviews"
- Label: "Google"
- Link: `https://www.google.com/search?q=Locally+Twisted+Reviews` (new tab)
- Accessible label: "Locally Twisted Google Reviews: 4.9 out of 5 stars from 114 reviews (opens in new tab)"

#### Balloon Twisting Section (`s_lt_twisting.xml`)

- H2: "Balloon Twisting & Face Painting"
- Body para 1: "Add unforgettable entertainment to any event. Our skilled artists create balloon animals, swords, crowns, and custom designs on the spot — plus professional face painting that transforms kids (and adults!) into their favorite characters."
- Body para 2: "Perfect for birthday parties, school events, corporate family days, and festivals."
- CTA: "Book Entertainment" → `/balloon-twisting-and-face-painting`
- Photo carousel: 10 slides, catalog_data ir.attachment IDs 1209–1227 (odd numbers alternating twisting/face painting). These are production catalog_data attachment IDs — NOT transferable directly to ERPNext.

#### Trust Bar (`s_lt_trust_bar.xml`)

3 items (horizontal):
1. SVG: `trust-trophy.svg` | Title: "Since 1998" | Desc: "Utah's trusted balloon experts"
2. SVG: `trust-palette.svg` | Title: "Custom Designs" | Desc: "Tailored to your vision"
3. SVG: `trust-heart.svg` | Title: "Made with Love" | Desc: "Every detail matters"

SVG files referenced: `/locally_twisted/static/src/img/trust-trophy.svg`, `trust-palette.svg`, `trust-heart.svg`
Note: Descriptions hidden on mobile (`d-none d-md-block`)

#### Category Circles (`s_lt_categories.xml`)

Section heading: "Custom Creations"
5 category items (odd count — mobile 2+2+1, desktop 3+2):
1. Columns & Pillars → `/shop/category/columns-28` (FA: `fa-building`)
2. Balloon Arches → `/shop/category/balloon-arches-27` (FA: `fa-link`)
3. Organic Garlands → `/shop/category/organic-garlands-31` (FA: `fa-leaf`)
4. Picture Perfect Backdrops → `/shop/category/backdrops-32` (FA: `fa-photo`)
5. Balloon Drops → `/shop/category/balloon-drops-33` (FA: `fa-arrow-down`)

Note: These use catalog_data category slugs with catalog_data numeric IDs. ERPNext Item Group routes will be different.

#### Client Logo Crawl (`s_lt_client_crawl.xml`)

Section heading: "Trusted by Utah's Best Since 1998"
Complete client name list (52 names, duplicated for seamless loop):
FanX, Chick-fil-A, Texas Roadhouse, Applebee's, Chili's, Utah Art Alliance, Ancestry, Honey Baked Ham, Megaplex, Zions Bank, America First CU, Utah Jazz, Fidelity, Morgan Stanley, KSL, KUTV, FOX13, University of Utah, Weber State, Intermountain Health, UDOT, SLC Pride, Equality Utah, Ogden City, Sandy City, Herriman City, SLC County, Gallivan Center, Station Park, Museum of Illusion, PotBelly, Young Automotive, Sea Quest, Alpine Events, Ogden Airport, Paramount, Shops at Southtown, Daybreak, LVT, Lux Events, Safe Kids Fair, Tree House Museum, Ogden Country Club, Pride Center, Newgate Mall, The Boiler Room, Western Sports Park, St. Joseph's, Syracuse City, West Point City, Clinton City, Hooper City, Kearns, Ogden Weber Chamber, LGBT Chamber

#### CTA Section (`s_lt_cta.xml`)

- H2: "Make Your Celebration Unforgettable"
- Body: "From birthdays to weddings, baby showers to corporate events — we've been part of Utah celebrations since 1998. Yours is next."
- CTA: "Contact Us" → `/contact`

#### PLACEHOLDER sections (not yet real content)

`s_lt_featured_products.xml` — "Seasonal Favorites" / "Trending balloon designs for every occasion" — all 4 cards show "Coming Soon" / "Shop Now" → `/shop`

`s_lt_local_favorites.xml` — "Local Favorites" / "Utah's most-loved balloon designs" — all 4 cards show "Coming Soon" / "Shop Now" → `/shop`

### BALLOON TWISTING & FACE PAINTING SERVICE PAGE (`views/pages/page_balloon_twisting.xml`)

**Route:** `/balloon-twisting-and-face-painting`
**Meta title:** "Balloon Twisting & Face Painting — Locally Twisted | Utah"
**Meta description:** "Professional balloon twisting and face painting for birthday parties, school events, corporate family days, and festivals. Serving Weber, Davis, Salt Lake, and Utah counties."

**Section 1 — Intro Band (Blush Tint):**
- H1: "Balloon Twisting & Face Painting"
- Lead: "Live entertainment that keeps every guest smiling"

**Section 2 — Two Service Cards:**

Face Painting card:
- H2: "Face Painting"
- Bullets: "Butterflies, superheroes, tigers, princesses" | "FDA-approved, skin-safe paints" | "Faces, arms, and hands" | "Kids, teens, and adults"
- Photo carousel: 10 slides, catalog_data ir.attachment IDs 1188–1197

Balloon Twisting card:
- H2: "Balloon Twisting"
- Bullets: "Animals, swords, crowns, flowers" | "Custom designs on the spot" | "Guests watch the designs come together"
- Photo carousel: 9 slides, catalog_data ir.attachment IDs 1198–1206

**Section 3 — Event Type Crawl (Blush band):**
Event types (with FA icons): Birthday Parties, School Carnivals, Corporate Events, Festivals, Church Events, Grand Openings, Family Reunions, Holiday Parties

**Section 4 — Booking form + sidebar:**
- H2: "Tell us about your event"
- Subtitle: "Share a few details and we take it from there."

Form fields (verbatim labels):
- "What would you like?" (required select): "Both — Balloon Twisting & Face Painting", "Balloon Twisting Only", "Face Painting Only"
- "Hours Needed" (required select): "1 hour", "2 hours", "3 hours", "4+ hours"
- "Your Name" (required text)
- "Phone" (required tel)
- "Email" (required email)
- "Event Date" (required date)
- "Preferred Start Time" (time, optional)
- "Event Type" (select): "Birthday Party", "School Event", "Corporate Event", "Festival / Fair", "Church Event", "Family Reunion", "Holiday Party", "Other"
- "Estimated Guests" (number, placeholder: "e.g. 30")
- "Anything else we should know?" (textarea, placeholder: "Event theme, color preferences, special requests...")
- Submit: "Send Request"
- Privacy note: "We'll use this info to contact you about your event. See our Privacy Policy."

"What to Expect" sidebar:
- "We reach out within 24 hours"
- "A $50 deposit secures your date"
- "The remaining balance is due before your event"
- Cancellation: "48 hours' notice required. Deposits are non-refundable."
- Deposit CTA: "Pay $50 Deposit" → `/shop/event-booking-deposit-32`
- Phone: (801) 285-0860 → `tel:+18012850860`
- Email: hi@locallytwisted.com

### ABOUT PAGE (`views/pages/page_about.xml`)

- H1: "Our Story"
- Lead: "Over 20 years of bringing joy to Utah"
- H2 (story section): "Utah's Balloon Specialists"
- Body: "For over 20 years, Locally Twisted has been at the heart of Utah's celebrations. What started as a passion for balloon art has grown into a full-service event entertainment company trusted by families, businesses, and event planners across the Wasatch Front."
- Body para 2: "Every balloon we twist, every arch we build, and every event we decorate is a chance to create something magical. We believe that celebrations matter — and the details make all the difference."
- Team section: "Meet the Team" / "The creative minds behind your celebrations" — pulls from `hr.employee.public` records dynamically; shows placeholder if none

---

## What Frappe Ships Out of the Box (from container inspection)

### Website Theme DocType

**One record exists in the live site:** "Standard" (module: Website)

**DocType fields:** theme, module, custom, theme_scss, theme_url, js, google_font, font_size, primary_color (Link to Color DocType), text_color (Link), dark_color (Link), background_color (Link), light_color (Link), custom_scss, font_properties, button_rounded_corners (Check), button_shadows (Check), button_gradients (Check), custom_overrides (Code), ignored_apps (Table)

**How it compiles:** The `website_theme_template.scss` Jinja template pulls `google_font`, `primary_color`, `text_color`, `dark_color`, `background_color` from the record (Color DocType lookups), then appends the `custom_overrides` SCSS block and `custom_scss` block. It also `@import`s any paths registered via `website_theme_scss` in installed apps' `hooks.py`.

**Key insight:** The Website Theme DocType is primarily a Bootstrap variable override tool. `primary_color` sets Bootstrap's `$primary`. The LT color system (Teal, Soft Blue, Blush, etc.) does NOT map cleanly to Bootstrap's single `$primary` variable. The theme system is a good place to set the Google Font and maybe one primary color, but LT's full design token system lives better in `lt-theme.css` via `web_include_css`.

**Standard theme record is empty:** No google_font, no primary_color, no custom_scss — it's a bare default.

### Web Template Records (26 total — Frappe + Webshop)

From Frappe (module: Website):
- **Hero** (Section) — centered title + subtitle + 2 buttons. No background image support.
- **Hero with Right Image** (Section) — title + subtitle + 2 buttons + right image. Uses `frappe.render_template('templates/includes/image_with_blur.html'...)`.
- **Section with Cards** (Section) — supports up to 9 cards (Small/Medium/Large size), each with title + content + url + image. Card titles are `<h3>`. No carousel.
- **Section with CTA** (Section) — title + subtitle + cta_url + cta_label + cta_description + show_confetti. Uses `<h4>` for the action link, NOT a `<button class="btn">`. No Teal button.
- **Section with Features** (Section) — title + subtitle + feature list.
- **Section with Testimonials** (Section) — testimonials list with avatar, content, full_name, designation.
- **Section with Image** (Section) — title + image side-by-side.
- **Section with Image Grid** (Section) — image grid.
- **Section with Tabs** (Section)
- **Section with Videos** (Section)
- **Section with Embed** (Section)
- **Section with Collapsible Content** (Section)
- **Section with Small CTA** (Section)
- **Full Width Image** (Section)
- **Slideshow** (Section)
- **Split Section with Image** (Section)
- **Cover Image** (Component)
- **Discussions** (Section)
- **Markdown** (Section)
- **Standard Navbar** (Navbar)
- **Primary Navbar** (Navbar)
- **Standard Footer** (Footer)
- **Testimonial** (Section)

From Webshop (module: Webshop):
- **Hero Slider** (Section) — Bootstrap carousel with 5 configurable slides (image, title, subtitle, CTA button, align, dark/light theme). Auto-advance disabled by default. Uses `data-ride="carousel"` (Bootstrap 4 API, not Bootstrap 5 `data-bs-ride`). **This is v4 Bootstrap API — the LT stack uses Bootstrap 5 (`data-bs-*`). This template will NOT autoplay correctly without a JS shim.**
- **Item Card Group** (Section) — renders a grid of product cards from Item Group.
- **Product Card** (Component) — single product card.
- **Product Category Cards** (Section) — up to 8 category cards from Item Group records, with image and name. Card images come from `Item Group.image`. Uses Bootstrap 4 `card` classes.

### Web Page DocType Native Tabs

Confirmed in `apps/frappe/frappe/website/doctype/web_page/web_page.json`:

| Tab | Field(s) | What it does |
|---|---|---|
| Content | `content_type`, `main_section` (Rich Text), `main_section_html` (HTML), `main_section_md` (Markdown), `page_blocks` (Page Builder table) | Body. `content_type` selects which field renders — wrong value silently empties page. |
| Script | `javascript` (Code) | Per-page JS at load. Where calculators, form interactivity, carousels live. |
| Style | `css` (Code) + `insert_style` (Check) | Per-page CSS. Toggle `insert_style` to inject. |
| Header | `header` (HTML editor), `breadcrumbs` (Code), `dynamic_template` | Custom hero HTML, breadcrumb logic |
| Settings | `show_sidebar`, `enable_comments`, `full_width` | Layout toggles |
| Meta Tags | `meta_title`, `meta_description`, `meta_image`, `dynamic_route` | Per-page SEO |
| Context | `context_script` (Code, Python) | Server-side Python before render — inject Jinja context vars without writing a controller. |

**Currently active Web Pages on the LT site:** Home page at route "home" (confirmed by `bench --site frontend execute frappe.db.get_value` returning "home" as `Website Settings.home_page`). This is the placeholder "site under construction" state from `landing.py`'s `rollback()`.

### SCSS Bundles That Ship

Frappe's website SCSS bundle (`frappe/public/scss/website/`):
- `base.scss` — flex-column body + sticky footer layout (`html { height: 100% }`, `body { display: flex; flex-direction: column }`)
- `navbar.scss` — Frappe navbar styles
- `footer.scss` — `.web-footer { padding: 3rem 0; min-height: 140px; background-color: var(--fg-color); border-top: 1px solid $border-color; margin-top: auto; }` — NO max-height, NO height constraint
- `page_builder.scss` — styles for Page Builder section containers
- `blog.scss`, `portal.scss`, `web_form.scss`, `search.scss`, `sidebar.scss`, etc.
- `css_variables.scss` — exposes Frappe CSS variables including `--fg-color`, `--bg-color`, `--text-color`

### Frappe's Navbar and Footer Template Files

Navbar includes at `apps/frappe/frappe/templates/includes/navbar/`:
- `navbar.html` — main navbar template
- `navbar_items.html` — renders `top_bar_items` as nav links
- `navbar_login.html` — sign-in link
- `navbar_search.html` — search bar
- `dropdown_items.html`, `dropdown_login.html`

Footer includes at `apps/frappe/frappe/templates/includes/footer/`:
- `footer.html` — main footer template
- `footer_extension.html` — hook for apps to inject above footer
- `footer_grouped_links.html` — renders `footer_items` as grouped link columns
- `footer_info.html` — copyright row + `footer_address`
- `footer_links.html` — flat link list
- `footer_logo_extension.html` — brand block above links
- `footer_powered.html` — "Powered by ERPNext" (CSS-hidden)

**Override path (confirmed):** Place same-named files at `apps/locally_twisted/locally_twisted/templates/includes/footer/footer.html` — Frappe's template resolution finds the app's file first.

### Webshop HTML Templates (complete map)

Generator templates (render per Website Item / Item Group):
- `generators/item/item.html` — product detail page
- `generators/item/item_add_to_cart.html`, `item_configure.html`, `item_details.html`, `item_image.html`, `item_inquiry.html`, `item_reviews.html`, `item_specifications.html`
- `generators/item_group.html` — item group page

Page templates (www/ routes):
- `pages/cart.html` — cart page
- `pages/order.html` — order confirmation
- `pages/wishlist.html`, `pages/customer_reviews.html`, `pages/product_search.html`

Include partials:
- `includes/cart/` — 10 cart component partials
- `includes/navbar/navbar_items.html` — injects cart icon into Frappe navbar
- `includes/macros.html`

www/ pages (static routes):
- `www/all-products/index.html` — `/all-products` route (HTTP 200 confirmed)
- `www/shop-by-category/index.html` — `/shop-by-category`
- `www/shop-by-category/category_card_section.html`

WebTemplate templates (Page Builder blocks):
- `webshop/web_template/hero_slider/hero_slider.html` — Bootstrap 4 carousel (WARNING: uses `data-ride` not `data-bs-ride` — Bootstrap 5 incompatibility)
- `webshop/web_template/item_card_group/item_card_group.html`
- `webshop/web_template/product_card/product_card.html`
- `webshop/web_template/product_category_cards/product_category_cards.html`

---

## What the LT Custom App Currently Provides

**File:** `apps/locally_twisted/locally_twisted/hooks.py`

Active registrations:
- `app_name = "locally_twisted"`, `app_title = "Locally Twisted"`, `app_publisher = "Built by Cameron"`, `app_license = "mit"`
- `web_include_css = "/assets/locally_twisted/css/lt-theme.css"` — CSS is served via this hook, loaded AFTER Frappe's bundle (correct cascade order)
- `website_theme_scss = "locally_twisted/public/scss/website"` — commented out (not active)
- All other hooks commented out (blank scaffold)

**File:** `apps/locally_twisted/locally_twisted/public/css/lt-theme.css` (616 lines)

Contains:
- CSS custom property tokens (all LT color and spacing variables)
- Google Fonts import (DM Serif Display + Raleway)
- Typography: `h1`-`h6`, body, `font-family: 'DM Serif Display'` on headings, `'Raleway'` on body
- Navbar styles (logo sizing, nav link colors, mobile offcanvas)
- Button overrides (`.btn-primary` → Teal `#008080`)
- Form input tints
- Footer styles (`.web-footer` with Soft Blue background, column titles, link colors, footer-info bar)

**`!important` count: 28 occurrences.** Specific locations:
- Lines 199-202: `prefers-reduced-motion` block — these are CORRECT/intentional (accessibility)
- Line 298: navbar background
- Lines 318-319, 326: logo height/width
- Lines 338, 347, 362, 369: navbar link colors
- Lines 388-398: navbar toggler icon (data URI SVG for hamburger) — THIS IS THE KNOWN BAD PATTERN from `lessons-learned.md` (data URIs fail in real browsers)
- Lines 405, 415: navbar toggler element hiding
- Line 409: offcanvas background
- Line 576: `.web-footer .footer-powered { display: none !important; }` — the only remaining justifiable use (hiding Frappe's own "Powered by ERPNext" line)

**Status of `!important` chains:** The HANDOFF.md from the prior session stated these chains "should be removed" but the current file still has them. The ones on lines 388-415 (navbar toggler using data URI SVG) are the most problematic — they use `data:image/svg+xml;utf8,...` which `lessons-learned.md` 2026-04-26 confirmed silently fails in real browsers (non-standard `utf8` prefix, unencoded spaces).

**What the LT app does NOT yet provide:**
- No Jinja template overrides (no `templates/` directory in the app)
- No `website_theme_scss` SCSS file
- No JavaScript registered
- No custom DocTypes or fixtures registered
- No `www/` pages

---

## What Was Tried Before (git history)

Commits relevant to the website build (newest first, from `git log --oneline -50` output):

| Commit | What it was |
|---|---|
| `1ed6d29` | `apps/locally_twisted/locally_twisted/setup_pages/landing.py` — the failed Web Page build script, now retired. `rollback()` restores to placeholder. |
| `f2b294b` | `research/expedition-frappe-theme/research-brief.md` — the brief this expedition is responding to |
| `79bcd13` | `deploy.py` update |
| `e8b71ae` | `apps/locally_twisted/locally_twisted/public/css/lt-theme.css` — CSS edits this session |
| `506bd0a` | `hooks.py` — app hook edits |
| `895a6a7` | CSS updates |
| `4e35abb` | `lt-theme.css` — prior session's CSS work |
| `0b889d6` | `scripts/setup/setup_slice2_header_footer.py` — the original failed Slice 2 setup script |
| `7075732` | `_resources/lt-theme.css` — original CSS before moving to app |

**Two failed approaches documented:**

**Approach 1 — `setup_slice2_header_footer.py`:** Configured `Website Settings.head_html` with a CSS style block containing `!important` chains. CSS loaded BEFORE Frappe's bundle (wrong), Frappe's bundle rules won at equal specificity. Footer brand block rendered invisibly. Script is still present but retired from active use.

**Approach 2 — `setup_pages/landing.py` `build()` function:** Built a Web Page record with `content_type="Page Builder"` and 4 Frappe default Web Templates ("Hero with Right Image", "Section with Cards", "Section with CTA"). Used invented copy (not catalog_data-sourced). Page not visible to GL when opened in their real browser. Not mobile-responsive. Rolled back to placeholder via `rollback()`. The `build()` function is kept for reference but marked NOT TO RUN.

---

## Established LT Patterns / Voice / Visual Identity (from STYLE-GUIDE.md v2.1)

**File:** `/home/guidingl/projects/Built_by_Cameron/_CLIENTS/locally-twisted/_resources/STYLE-GUIDE.md`

### Design principles
1. Photography is the star — site is a frame
2. Color used sparingly — thin bands, slider panels, input tints only
3. Teal is earned — only on solid CTA buttons
4. White space dominates
5. Soft, never harsh — no pure black, no loud backgrounds
6. Mobile-first (375px base)

### Color system (verbatim)
- Teal `#008080` — CTA buttons ONLY. Never as text, border, background, form ring.
- Soft Gray `#595A5C` — body text
- Near Black `#1A1A1A` — headings, emphasis
- White `#FFFFFF` — content, cards
- Near White `#FBFBFB` — page background
- Blush `#F4DFD7`, Soft Lemon `#F9F871`, Lime Pastel `#B8FF9E`, Seafoam `#88FED0`, Aqua `#80F5F3`, Sky Cyan `#A0E9FF`, **Soft Blue `#C3DCF3`** (footer + trust bar background)
- Surface tints: Blush Tint `#FBF5F2`, Blue Tint `#EEF4FB`, Mint Tint `#EEFEF5`, Lemon Tint `#FDFDE3`

### Typography
- Headings: DM Serif Display (400 weight)
- Body: Raleway (300, 400, 500, 600, 700)
- H1: 28px mobile / 48px desktop | H2: 24px/36px | H3: 20px/28px

### Voice rules (Quiet Confidence)
1. Present tense, not promises — "We make" not "We can make"
2. Invite, never push — "Tell us what you're imagining" not "Book now!"
3. Warm, not performing — "Every detail matters" not "We LOVE what we do!!!"

### Accessibility requirements (WCAG 2.1 AA)
- All decorative FA icons: `aria-hidden="true"`
- One `<h1>` per page, never skip levels
- Decorative "headings" use `<p>` or `<span>` with class, not heading elements
- Focus rings: `outline: 2px solid #1A1A1A; outline-offset: 2px;`
- Touch targets: 44px minimum
- Carousels: `role="region"`, `aria-roledescription="carousel"`, pause button, labeled slides
- External links: `target="_blank" rel="noopener"` + `<span class="visually-hidden"> (opens in new tab)</span>`
- Skip-to-content link: `<a href="#wrap" class="visually-hidden-focusable">Skip to main content</a>`
- Motion: `prefers-reduced-motion: reduce` disables all animations

### Layout rules
- Section background pattern: White → thin color band → White → slider panel → White
- Even-count collections must use balanced symmetric rows (no orphans)
- Odd counts exempt (5 categories as 3+2 is OK)
- Thin bands: 40-80px tall, not full-height sections
- Footer and trust bars: only places where full-width colored backgrounds are used

---

## Catalog State

**File:** `/home/guidingl/projects/Built_by_Cameron/_CLIENTS/locally-twisted/_resources/catalog_data-export/catalog.json`

**Source:** `` (live catalog_data), category `/shop/category/what-we-make-3`
**Product count:** 51 products
**Products with image_url:** 48 of 51 (94%)
**Products with attributes:** 47 of 51 (92%)
**Products with no base_price:** 3 of 51

**Data shape per product:**
```
slug_with_id, slug, name, url, base_price, currency, description, image_url, attributes, variants, variant_count
```

**Attributes structure:** Dict keyed by attribute name (e.g., `"latex colors"`, `"balloon size"`, `"add-ons"`). Each value is a list of `{value_id, value_name}` objects. Example: 47 products have `attributes`, nearly all have `latex colors` attribute with 53+ named values.

**Variants:** ALL 51 products have empty `variants` list and `variant_count: 0`. The catalog export captured attributes but not pre-generated variant combinations. ERPNext will need to generate variants from the attribute lists.

**Images:** image_url format is `web/image/product.product/{id}/image_1920?unique={hash}` — these are catalog_data attachment URLs, NOT local files. They require fetching from the live catalog_data server. Live catalog_data stack is still running (`external-catalog-data-web-1 Up 30 hours`).

**Description:** Most products have `description: null` (no descriptions in the catalog_data catalog).

**Currency:** All USD.

---

## Constraints From Existing Code / Decisions

From `_resources/website-page-index.md` (v2, GL-confirmed 2026-04-26):

**Tier 1 (settings-only):**
- Header: Native Frappe navbar from Website Settings (`top_bar_items` + `brand_html`)
- Footer: Native Frappe footer from Website Settings (`footer_items` + `footer_address` + `copyright`). GL confirmed: skip the centered brand block + social row + hours block — use native layout.
- All webshop pages: `/all-products`, `/shop-by-category`, product detail, cart, checkout — native with theme CSS only

**Tier 2 (Page Builder + theme CSS):**
- Homepage `/` — Web Page + Page Builder blocks
- BTFP service page `/balloon-twisting-and-face-painting`
- Contact `/contact`
- FAQ `/faq`

**Build order locked (GL directive):** Landing page → BTFP → ecommerce workflow → contact. Blog is OUT of Phase 1.

**BTFP pricing calculator:** Was tier 4, recategorized to tier 1 after Web Page tabs finding. JavaScript goes in the page's `javascript` field, CSS in `css` field.

**Color swatches vs pills:** Pills = tier 1 (native). Swatches = tier 4 (custom field on Item Attribute Value + custom Web Template). Decision deferred to mock comparison.

**Footer social icons:** Only 3 (Facebook, Instagram, Pinterest). The `setup_slice2_header_footer.py` script erroneously added Twitter. catalog_data source is authoritative.

**Step 0 (prerequisite, not yet done):** Strip `!important` chains from `lt-theme.css` (specifically navbar toggler block lines 385-415 which use broken data URI SVG). Retire `setup_slice2_header_footer.py` from active use. Verify pages render cleanly.

---

## Disconfirmation Search

### `!important` count in current lt-theme.css
28 occurrences. Lines 388-398 contain the known-broken data URI SVG pattern for the navbar toggler. `lessons-learned.md` 2026-04-26 explicitly names this pattern as silently failing in real browsers ("real Chromium, Firefox silently rendered the circles with no icon"). **This is still in the codebase and has NOT been fixed despite being in the hot direction.**

### Webshop Hero Slider uses Bootstrap 4 API
`hero_slider.html` uses `data-ride="carousel"` (Bootstrap 4). The LT ERPNext stack uses Bootstrap 5 (`data-bs-*`). Bootstrap 5 does NOT respond to `data-ride`. The `frappe.ready(function() { $('.carousel').carousel({...}) })` JS initialization at the bottom of the template requires jQuery's `.carousel()` — which Bootstrap 5 ALSO removed (native JS only). **If Page Builder is used with the Hero Slider web template, carousel autoplay will not work.** The catalog_data `s_lt_hero.xml` uses Bootstrap 5 syntax (`data-bs-ride="carousel"`, `data-bs-interval`, `data-bs-target`) which is correct for ERPNext v15.

### The landing.py `build()` function still exists
`apps/locally_twisted/locally_twisted/setup_pages/landing.py:15` says "STATUS 2026-04-26: This script's `build()` produced a non-visible / non-responsive page... It is RETIRED." But the function itself still exists in the file. Any instance that runs `build()` without reading the docstring will recreate the broken state. The `rollback()` function is safe to run.

### catalog_data image URLs are not local
The catalog.json images are catalog_data server URLs (`...`). The local catalog_data stack is currently running, so they're fetchable now. But when the catalog_data server is decommissioned (planned after ERPNext replacement is ready), all 48 image URLs become 404. An export-before-decommission step is essential.

### Catalog has no descriptions
48 of 51 products have `description: null`. Product pages on the ERPNext webshop will have no body copy unless descriptions are written or imported separately.

### Variant price data is missing
`variants: []` for all 51 products. Only `base_price` is captured. The variant pricing math (size × add-on additive pricing) is not in the export — it would need to be manually configured per product in ERPNext Item Attribute price rules.

### The research question about "polished Frappe themes" is NOT answered by this codebase
Nothing in this codebase, the running container, or the git history shows evidence of a community Frappe theme being evaluated. The Website Theme DocType has only the "Standard" record (empty). The container has no third-party theme apps installed. This is an open research gap that belongs to the Web Scout.

---

## Gaps

1. **No Jinja template overrides exist yet** — the `locally_twisted` app has no `templates/` directory. Every instance of "we'll override the footer Jinja partial" in the HANDOFF is a plan, not a fact.

2. **Hero images do not exist locally** — the `s_lt_hero.xml` hero carousel references images by catalog_data attachment IDs (production DB records). No hero image files exist in `_resources/images/`. The `_resources/images/` folder contains 15 AI-generated placeholder PNGs, but none appear to be hero carousel slides.

3. **Trust bar SVG icons are not in the ERPNext app** — `trust-trophy.svg`, `trust-palette.svg`, `trust-heart.svg` are referenced at `/locally_twisted/static/src/img/` (catalog_data path). The ERPNext app's `public/icons/` directory exists but these specific SVGs have not been copied over.

4. **No Web Page records beyond the placeholder** — the live site has one Web Page ("home") in placeholder state. No BTFP page, no contact page, nothing built yet.

5. **Pricing calculator has no implementation** — the BTFP service page plan calls for a pricing calculator in the `javascript` field, but no implementation exists. The catalog_data version (`page_balloon_twisting.xml`) also has no calculator — it has a booking form, not a pricing calculator.

6. **`locally_twisted` app pip install durability** — per `lessons-learned.md`, the editable pip install is lost on container recreation. The `scripts/setup/install_webshop.py` re-applies it, but this is a manual step.

---

## Synthesis

### Current codebase state relative to "polished, mobile-responsive customer-facing site"

**What exists and is reusable:**
- Complete LT brand design token system in `lt-theme.css` (all CSS variables, typography, colors correctly defined)
- Button, form, footer, and navbar CSS rules (needs `!important` cleanup)
- Custom app scaffolded and wired via `web_include_css` (correct primitive)
- Webshop + payments installed and durable
- Website Settings configured with nav items and footer items from prior Slice 2 attempt

**What is broken/incomplete:**
- Navbar toggler icon uses broken data URI SVG (lines 388-398) — confirmed silently failing in real browsers
- No Jinja template overrides implemented despite HANDOFF saying they're the path forward
- Homepage is a placeholder ("Site under construction")
- No content pages exist
- All hero images are catalog_data attachment URL references, not local files

**What is fully ready (from catalog_data source):**
- ALL approved copy and structure for: homepage sections, header two-tier layout, footer 3-column layout, BTFP service page, about page, category circles, client crawl list (52 names), trust bar copy, CTA copy, Google reviews badge copy
- This copy has been through the catalog_data build process and represents the Jeff-approved content intent

### Path of least resistance for the landing page

The approved catalog_data content maps cleanly to Frappe's native Web Page Page Builder PLUS some custom HTML in the `header` field or `main_section_html`. Specifically:

1. **Hero:** Frappe's `hero_with_right_image` or `hero` Web Template works for a simple text+CTA. For the 3-slide carousel, the webshop's `hero_slider` template exists but has the Bootstrap 4 API bug. The safest approach: use `main_section_html` to embed a properly-coded Bootstrap 5 carousel.

2. **Trust bar:** Map to `section_with_features` or `section_with_cards` in Page Builder. Or embed as `main_section_html`.

3. **Categories:** Webshop's `product_category_cards` Web Template exists and pulls from Item Group records — this is the right primitive if Item Groups are configured.

4. **Testimonials/reviews:** `section_with_testimonials` Web Template exists and maps to the Google reviews badge concept.

5. **CTA:** `section_with_cta` Web Template exists but outputs a link, not a `btn btn-primary` button. For the Teal button CTA, use `main_section_html` for that section.

6. **Client crawl:** No native Web Template matches a marquee animation. This is tier 4 (custom HTML in `main_section_html` or a custom block), but it's pure HTML/CSS with no back-end dependency.

### What the approved catalog_data content tells us about Jeff's actual taste

The catalog_data codebase was built carefully — it has WCAG-correct aria attributes, accessibility structure, Bootstrap 5 syntax, and Quiet Confidence voice. The hero copy ("Utah's Balloon Specialists", "Making celebrations unforgettable since 1998") IS on-brand per the STYLE-GUIDE. The CTA copy ("Make Your Celebration Unforgettable") IS on-brand. The client crawl list (52 names including Utah Jazz, Ancestry, University of Utah) tells a strong social proof story.

**Jeff's taste (from what he built):** He values specificity (114 reviews at 4.9 stars, not vague claims), real client names, the 1998 founding year, and the Wasatch Front as the geographic anchor. The site should feel local and trusted, not generic balloon-company.

### The one finding that most changes the build plan

The catalog_data content is MORE complete than any instance has acknowledged. Previous instances used placeholder copy ("Make Your Celebration Unforgettable" was invented) when the exact approved copy was sitting in `s_lt_cta.xml`. The research brief correctly identified this as the primary gap — but the solution is simpler than it looks: the XML files are a complete, buildable blueprint. They even have the correct Bootstrap 5 aria patterns and accessibility structure. A build that converts these XML structures to Frappe Page Builder blocks (or `main_section_html`) would produce the approved content immediately, without guessing.
