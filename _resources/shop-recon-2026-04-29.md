# Shop Recon — 2026-04-29

**Mission:** map every gap between Odoo's product truth and what the live ERPNext shop renders. No code changes. Single-pass for GL to scan.

**Source data:**
- Odoo export: `_resources/odoo-export/catalog.json` (51 products, 48 images)
- ERPNext live: docker exec into backend, `frappe.client.get_list` queries, `bench --site frontend` (counts as of 2026-04-29 11:04 local)
- Live page render: `scripts/verify/_screenshots/20260429-110427-shop-recon/` — viewport-only Playwright captures at desktop (1280) + mobile (375)
- Design guide: `_resources/design-guide/synthesis/shop/page.tsx` + `screenshots/shop-{desktop,mobile}.png`

---

## TL;DR

The shop has **two parallel surfaces** that don't know about each other:

1. **`/shop`** — custom LT-themed page (`apps/locally_twisted/locally_twisted/www/shop.py`). Hero + filter pills + grid. Reads design guide register correctly. **But the data underneath is wrong** — 18 products missing, no variant options, naive categorization, inconsistent name capitalization.
2. **Webshop's stock pages** — `/shop-by-category`, `/shop-items`, `/all-products`, `/shop/<slug>`. Zero LT design treatment. `Item Code: <slug>` jargon visible to customers. `/shop-by-category` is **completely empty** (no Item Group children to render). Mobile `/shop-items` has Add-to-Cart button overlapping product titles.

Plus three structural data gaps that prevent any redesign from working until they're fixed:
- **18 of 51 Odoo products missing** in ERPNext (all the high-ticket structural items)
- **Zero variant options** for any product (`enable_variants=0` at webshop level, 0 Item Variant records, only generic stub Item Attributes "Colour" and "Size")
- **Item Group hierarchy is flat** — every product is in one bucket called `Shop Items` with `is_group=0`. No category structure exists for a mega menu to draw from.

The mega menu GL asked for can't render until the data is restructured. The webshop's stock pages can't be tamed without either disabling them or replacing them with LT-themed equivalents. The "/shop" custom page can't reach its design guide quality bar until the variant + categorization data is in place.

---

## 1. Catalog truth (Odoo) ↔ ERPNext state

### 1a. Product count diff

| Source | Count |
|---|---|
| Odoo `catalog.json` | **51** |
| Odoo with image downloaded | 48 |
| Odoo with attributes mapped | 47 |
| Odoo with description text | 40 |
| ERPNext `Item` records | **33** |
| ERPNext `Website Item` published | 33 |
| ERPNext `Item Variant` records | **0** |
| ERPNext `Item Attribute` records | 2 (generic "Colour", "Size" — neither used) |
| Match rate | **65%** (33/51) |

### 1b. The 18 missing products (all need to be seeded)

These are in `catalog.json` but have no corresponding `Item` / `Website Item` in ERPNext. Slug → name → Odoo price:

| Slug | Name | Odoo price |
|---|---|---|
| baby-shower-combination-photo-opt | Baby Shower Combination Photo opt | $650 |
| basketball-arch | Basketball Arch | $340 |
| classic-arch | Classic Arch | $260 |
| classic-organic-arch | Classic Organic Arch | $500 |
| easter-arch | Easter Arch | $250 |
| easter-balloon-arch-bunny-ear | Easter Balloon Arch (Bunny Ear) | $375 |
| halloween-arch | Halloween Arch | $300 |
| premium-organic-arch | Premium Organic Arch | $720 |
| pride-arch | Pride Arch | $325 |
| pride-progress-rainbow-balloon-arch | Pride Progress Rainbow Balloon Arch | $260 |
| 6-color-rainbow-arch | 6-Color Rainbow Arch | $340 |
| balloon-drop | Balloon Drop | $375 |
| premium-organic-garland | Premium Organic Garland | $216 |
| large-garland | Large Garland | $216 |
| sleepy-baby-column | Sleepy Baby Column | $220 |
| classic-organic-balloon-garland | Classic Organic Balloon Garland | _no price/image in Odoo_ |
| classic-column | Classic Column | _no price/image in Odoo_ |
| star-column | Star Column | _no price/image in Odoo_ |

**Pattern:** every arch is missing. Most premium structural pieces missing. Bouquets ($35 each) and small-ticket items mostly there. The shop currently is biased toward small SKUs; the high-ticket / high-impact items aren't there at all.

3 products have no usable Odoo data (no price, no image) — flagging for GL: omit from rebuild, or stub-create + flag for Jeff to fill in?

### 1c. Variant / option gap (the biggest data hole)

Odoo has **rich attribute data** for 47 of 51 products. In ERPNext: zero of it.

| Odoo attribute family | Products that use it | What's in ERPNext |
|---|---|---|
| latex colors (~50 colors per product) | 20+ products | Nothing |
| Garland Length (6ft / 9ft / 12ft) | 4 garlands | Nothing |
| Arch Size | 9 arches | Nothing |
| Bouquet Size + Add Foil Number | 13 bouquets | Nothing |
| Column Height | 6 columns | Nothing |
| Add ons | 3 premium items | Nothing |
| Drop Size | 1 (Balloon Drop) | Nothing |
| Color Palette | 3 products | Nothing |
| Orbz toppers | 2 products | Nothing |
| Number colors / Number selection | 1 (Number Balloon Columns) | Nothing |
| Design / LED Lights | 1 (Classic Arch) | Nothing |
| Easter Designs | 1 (Easter Balloon Cups) | Nothing |
| Plush add ons | 3 get-well bouquets | Nothing |
| Topper / Baby color / Graduation stands | 4 misc | Nothing |

**`Webshop Settings`:** `enable_variants=0`, `enable_attribute_filters=0`. Even if Item Variants existed, the storefront wouldn't render selectors.

**Implication:** every product page renders today with NO color picker, NO size selector, NO add-on options. A customer adding "Baby Shower Garland" to cart cannot specify 6/9/12 feet, cannot pick balloon colors. They just get a "Baby Shower Garland." That's why GL said "missing options."

### 1d. Pricing — actually correct in ERPNext

Spot-checked all 33 items: `Item.standard_rate` matches Odoo `base_price` to the dollar. `Item Price` records on `Standard Selling` price list also match. **Pricing data isn't broken at the storage layer.**

GL's "prices are wrong" likely refers to either: (a) variant-priced items where the base price is misleading without options shown (e.g. "Premium Organic Garland" base $216 but real price climbs with length + add-ons), or (b) the awkward `$ 150.00 ($ 150.00 / Nos)` UoM display on product detail pages, which looks like a duplicate price. Both are render-time issues, not data issues.

### 1e. Description coverage

| Source | Products with real prose |
|---|---|
| Odoo `description` field | 40 of 51 (78%) |
| ERPNext `Item.description` with prose ≥ 50 chars | ~7 of 33 (21%) — a few warm LT-voice descriptions |
| ERPNext `Website Item.short_description` | 33 of 33 (100%) — but most just echo the item name |
| ERPNext `Website Item.web_long_description` | 33 of 33 — same |

The 7 that DO have real prose (Number Balloon Columns, Baby Shower Garland, Mother's Day Bouquet, Graduation Grab n Go, Large Organic Column, Premium Organic Column [duplicate of Large], 6' Graduation stands) sound right. They read in LT's Quiet Confidence voice and can stand. **The other ~26 are just item-name-echo strings ("Stitch Bouquet" → description = "Stitch Bouquet")** — those will need real prose written.

Odoo's descriptions don't appear to have come over for most products. Worth checking if Odoo had real prose for the products that landed without — if yes, port them; if no, write fresh.

### 1f. Image gap

Odoo has 48 product images downloaded to `_resources/odoo-export/images/`. ERPNext has 33 Items, all referencing `/files/<slug>.png`. Spot-check: the file paths look right, image filenames match item codes.

**Photo accuracy ("photos don't always match"):** can't verify from data alone — needs visual review of each `/files/<slug>.png` against the product name. Suspect: the Odoo scrape grabbed the cover image of each product, which may not always be the most representative one for an LT customer. Or some images are mislabeled at the source. **Open question for visual review.**

Image alt text on `/shop` cards is empty (`alt=""` for every image) — accessibility regression.

### 1g. Item Group structure

Current ERPNext Item Group tree:

```
All Item Groups (group)
├── Consumable
├── Products
├── Raw Material
├── Services
├── Shop Items   ← all 33 products live here. is_group=0. show_in_website=1.
└── Sub Assemblies
```

**There is no category hierarchy.** "Shop Items" is a leaf, not a folder. So `/shop-by-category` (which renders Item Group children) has nothing to show. The mega menu has nothing to draw from.

**Natural taxonomy implied by Odoo slug patterns** (proposal — GL's call):

| Category | Products (count) |
|---|---|
| Arches | basketball-arch, classic-arch, classic-organic-arch, easter-arch, easter-balloon-arch-bunny-ear, halloween-arch, 6-color-rainbow-arch, premium-organic-arch, pride-arch, pride-progress-rainbow-balloon-arch (10) |
| Columns | 7-butterfly-column, 7-epic-column, classic-column, classic-organic-columns, large-organic-column, mothers-day-front-yard-7-column, number-balloon-columns, pemium-organic-column [typo at source], sleepy-baby-column, star-column (10) |
| Bouquets | elsa-, encanto-, flamingo-, football-, holy-cow-, mickey-mouse-, minion-, over-the-hill-, paw-patrol-, soccer-, space-, stitch-, unicorn-, mothers-day-, logo-3-layered- (15) |
| Get-Well Bouquets (latex-free) | bandage-, butterfly-, shooting-star- (3) |
| Garlands | baby-shower-garland, classic-organic-balloon-garland, large-garland, premium-organic-garland (4) |
| Grab-n-Go | graduation-grab-n-go, organic-grab-n-go (2) |
| Drops | balloon-drop (1) |
| Table Decor | baby-table-decor, marble-table-decor, baby-shower-combination-photo-opt (3) |
| Stands & Easels | 6-graduation-stands, classic-organic-for-easel (2) |
| Seasonal Misc | easter-balloon-cups (1) |

Total: 51. This 10-category split is what the mega menu would source from.

---

## 2. Page-by-page UI/UX audit

Screenshots in `scripts/verify/_screenshots/20260429-110427-shop-recon/`. All viewport-only at 1280×800 (desktop) / 375×812 (mobile).

### 2a. `/shop` — custom LT page (the one that's GOOD chrome but partial data)

| Aspect | State | Gap |
|---|---|---|
| Hero (eyebrow + headline + lede) | ✅ Renders correctly per design guide | None |
| Filter pills | ✅ 4 pills present: All / Bouquets / Cups & Centerpieces / Ready-Made | **Pills don't reflect Odoo's natural taxonomy** — 18 products are bucketed "ready-made" by a `_categorize()` keyword matcher in `shop.py` line 65–74 (substring "bouquet" / "cup" / else). Columns, garlands, table decor, stands all collapse into "ready-made." |
| Item count | ✅ "33 ITEMS" | Should be 51 once missing products seeded |
| Product card grid | ✅ 3-column desktop, 1-col mobile, image + name + price + Add-to-cart | **No description preview on cards** (synthesis design has 1-line desc), **no Option dropdown** on cards (synthesis shows e.g. "5 balloons (standard)"), **no OOS badge in use** (CSS exists at `.lt-shop__oos-badge` line 248 but no data driving it) |
| Card image alt text | ❌ All `alt=""` | Accessibility regression |
| Card name capitalization | ❌ Inconsistent | "classic organic for easel" (lowercase), "Pemium Organic Column" (typo from Odoo source preserved) |
| Bottom CTA | ❌ Missing | Synthesis design has eyebrow "FOR SOMETHING LARGER" + headline "Custom balloon decor starts with a conversation, not a cart." + 2 buttons (lookbook + "Tell us what you're imagining"). LT page has nothing at the bottom — customer just runs out of products and hits the footer. |
| Mobile layout | ✅ Hero / pills / item count cleanly stacked | None at hero level; product card layout below the fold inherits the issues above |

**Verdict:** the chrome is on-brand. The data is incomplete. The card UX is webshop-like (image, name, price, button) instead of synthesis-like (image, kicker, name, desc, option dropdown, price, button + OOS badge where applicable).

### 2b. `/shop-by-category` — the empty broken page

| Aspect | State |
|---|---|
| H2 heading | "Shop by Category" |
| Below heading | **Nothing.** Vast empty grey space until footer. |
| Phantom links in DOM | Two anchors "Special Occasions" and "Holidays & Seasons" both point at `/shop-by-category` (loop back to self). These are webshop-stock category stub renders for Item Groups that don't exist. |
| Mobile | Same — empty space below heading until footer |

**Root cause:** webshop's `/shop-by-category` Jinja template iterates over Item Group records with `show_in_website=1` AND `parent_item_group=<some root>`. Our root `Shop Items` is a leaf (`is_group=0`), has no children. The template renders the heading + an empty list.

**Verdict:** unusable. Customer hitting this page gets a content-free experience. **Either it gets populated with real categories, or it gets removed from any IA path.** Right now it's reachable from breadcrumbs on `/shop-items` and `/shop/<item>`.

### 2c. `/shop-items` (and `/all-products` — same template) — webshop stock list

| Aspect | State | Gap |
|---|---|---|
| Title | "Shop Items" | Stock — no LT register |
| Heading | "Shop Items" plain h2 | No DM Serif treatment, no eyebrow, no lede |
| Filter sidebar | "Filters" / "Clear All" with no actual filters under it | Empty stub |
| Search bar | Stock webshop search input | Functional but not on-brand |
| View toggles | Grid / list icons in top right | Stock UI |
| Product cards | Each card: image left, name + "Shop Items \| Item Code : <slug>" + description + price right. No add-to-cart on the listing. | **`Item Code : <slug>` jargon visible to customers** — exactly what GL flagged. Reads "Shop Items \| Item Code : number-balloon-columns" — not customer-friendly. |
| Mobile layout | **Add-to-Cart button overlaps product title** at 375px viewport | Real bug |
| Breadcrumb | Home > Shop by Category > Shop Items | "Shop by Category" link goes to the empty broken page |

**Verdict:** broken on mobile, jargon-laden everywhere. Either gets the LT design treatment via a Jinja override of webshop's `templates/pages/product_search.html` (and `website_item_row.html` for cards), or gets superseded entirely by the custom `/shop` page.

### 2d. `/shop/<slug>` — webshop stock product detail

Tested: `/shop/baby-shower-garland`, `/shop/7-butterfly-column`. Both same shape.

| Aspect | State | Gap |
|---|---|---|
| Breadcrumb | Home > Shop by Category > Shop Items > <product> | All four links route to broken/empty pages |
| Product image | ✅ Renders single image | Single only — no gallery, no lightbox-on-click, no thumbnails |
| Title | ✅ Item name | Some titles inherit Odoo's casing inconsistencies |
| Jargon line | "Shop Items \| Item Code: baby-shower-garland" | **GL flagged this exact jargon.** Customer-facing, internal-shaped. |
| Price display | "$ 150.00 ($ 150.00 / Nos)" | The `(/$ X / Nos)` UoM display is weird. "Nos" is webshop's default UoM ("Nos" = "Numbers"). Shows duplicate price + uninterpretable suffix. |
| Variant selectors | **None visible.** 0 select elements, 0 radio groups, 0 variant forms in DOM. | The Odoo source product has Garland Length (6/9/12 ft) + ~50 latex colors. NEITHER renders. Add-to-cart adds the "Baby Shower Garland" with no options. |
| Add-to-Cart button | ✅ Present, dark teal, visible | Brand teal — fine |
| Buy-Now button | ❌ Not present | Synthesis design didn't show one either; consistent |
| Description | ✅ Real prose for baby-shower-garland (echo for many others) | Coverage gap, not render gap |
| "Vestigial mid-page bar" GL flagged | Did not surface in viewport-only screenshots; visible on full-page scroll. **Need to verify scroll-deep on mobile + desktop** | Pending visual confirmation in browser |
| Image-expand modal close-on-outside-click | Not testable from screenshots | Pending interactive test |
| Right-side whitespace on desktop | The webshop product layout uses `col-md-7` for the info panel; the right side of the centered 1200px container is bare. | Either tighten max-width to ~960px OR override the template for a 50/50 split. Logged in HANDOFF P2. |

**Verdict:** functional but reads as backend, not as storefront. Every product detail is missing the customizing UX that drives Odoo product pages today (color picker, size picker, add-on checkboxes).

### 2e. `/shop` redirect

`/shop` resolves to the custom LT page (route registered via `apps/locally_twisted/locally_twisted/www/shop.py`). Working as intended. No collision with webshop's stock `/shop` (which doesn't exist as a top-level route — webshop's product detail uses `/shop/<slug>`, not `/shop` alone).

### 2f. `/all-products` — same as `/shop-items`

Webshop's stock listing route. Identical render to `/shop-items`. Same jargon, same mobile bug, same empty filter sidebar. Two entry points to the same broken page.

---

## 3. Navigation gap — current vs needed mega menu

### Current navbar (`apps/locally_twisted/locally_twisted/templates/includes/navbar/navbar.html`)

Desktop tier-2 nav (line 60–70):
```
Twisting & Face Painting | Customizable Event Decor | Shop | Portfolio | Contact
```

Mobile drawer (line 174–187):
```
Twisting & Face Painting
Customizable Event Decor
Shop
Portfolio
Contact
[divider]
Sign In / Account
Cart
```

**Shop is a single anchor pointing at `/shop`. No dropdown affordance, no category preview.**

### Needed mega menu (per GL direction)

A dropdown that opens on hover/click of "Shop" and shows the Odoo-derived categories. Each link routes to a category landing page. From there, customers drill to product detail.

Routing decision is GL's call (see Open Questions §5b). Three plausible shapes:

**Shape A — fix `/shop-by-category` to actually work**
- Restructure Item Groups so Shop Items has children: Arches, Bouquets, Columns, Garlands, Get-Well-Bouquets, Drops, Grab-n-Go, Table-Decor, Stands, Seasonal-Misc
- Webshop's stock `/shop-by-category` then renders those automatically
- Mega menu links to `/shop-by-category/<slug>` (or whatever webshop's URL pattern actually is — needs verification)
- Pro: uses webshop's machinery, less custom work
- Con: webshop's category template is stock-shaped (jargon-prone) — would need a Jinja override to bring it on-brand

**Shape B — extend the custom `/shop` page to filter by category via URL param**
- Mega menu links to `/shop?category=arches`, `/shop?category=bouquets`, etc.
- Same `/shop` page reads the param, pre-selects the matching pill, auto-scrolls to grid
- Pro: single canonical browse page, all on-brand chrome
- Con: doesn't use webshop's machinery at all; we'd be hand-rolling category state. Filter pill set would have to grow to ~10 pills (gets unwieldy)

**Shape C — category landing pages owned by us, product detail still webshop**
- Per category: `/shop/arches`, `/shop/bouquets`, etc. as Frappe www/ pages or Web Page records
- Each page = LT-themed listing of products in that category (custom Jinja, our register)
- Product detail still webshop's `/shop/<slug>` (we override the template later)
- Mega menu links to those category landing routes
- Pro: full design control on category pages, can add per-category copy/imagery
- Con: 10 new pages to author + maintain

The synthesis design's shop screenshot doesn't actually show a category-focused page — it shows ONE page with pill filters. So the synthesis is closer to Shape B.

### Mobile mega menu

Mobile drawer needs to handle category disclosure too. Two options:
- **Accordion**: tap "Shop" → expands to show category sub-list inline within the drawer
- **Drill-down**: tap "Shop" → drawer transitions to a sub-screen showing categories + back button

Accordion is faster to build, drill-down is more app-like. Synthesis design didn't render mobile mega menu so no reference.

---

## 4. Design guide alignment

`_resources/design-guide/synthesis/shop/page.tsx` + `screenshots/shop-desktop.png` are the reference.

| Synthesis says | Live `/shop` does | Live `/shop-items`, `/shop-by-category`, `/shop/<slug>` do |
|---|---|---|
| Eyebrow "TAKE HOME" | ✅ Present | ❌ Stock plain h2 |
| DM Serif headline "A few things you can take home today." | ✅ Present | ❌ Stock plain h2 |
| Lede with inline "a conversation" link | ✅ Present (verified — link removed earlier per GL but text retained) | ❌ Not present |
| Blush thin band between hero and grid | ✅ Present | ❌ Not present |
| Filter pills (outlined, blush-tint when active) | ✅ Present | ❌ Empty filter sidebar (stock) |
| Item count "9 ITEMS" eyebrow style | ✅ Present ("33 ITEMS") | ❌ Not present |
| 3-column grid, white cards on near-white | ✅ Present | ❌ List view, no card register |
| Card: image (3:4) / kicker / name (DM Serif) / desc / option select / price + Add to Cart (teal) | Partial — image, name, price, Add to Cart present. **No kicker, no description, no option select.** | ❌ Stock card chrome |
| OOS badge top-left of card image | CSS class exists (`.lt-shop__oos-badge` line 248) but no products marked OOS in data | ❌ Not implemented |
| Bottom: "FOR SOMETHING LARGER" eyebrow + "Custom balloon decor starts with a conversation, not a cart." + 2 CTAs | ❌ Missing entirely | ❌ Missing |
| Customer-facing voice (Quiet Confidence) | ✅ on hero/pills | ❌ Stock (jargon) |

**Product detail register** (synthesis didn't render a product detail page — but the design guide's mood + voice docs suggest):
- Two-column: full-bleed image left, info panel right
- Eyebrow + DM Serif title + price + "(Custom-made for your event — quote follows)" or similar honest framing
- Variant pickers grouped by attribute family (color, size, add-ons) with the synthesis chip register
- "Add to cart" teal CTA OR "Tell us what you're imagining" inquiry CTA depending on price tier
- Description in Raleway prose
- Bottom: related items strip + "Custom event? Start a conversation." cross-link

**Live `/shop/<slug>` has none of this.** Webshop's stock template wins.

---

## 5. Open questions that need GL's call before any rebuild plan can land

These are decisions where the data + recon don't dictate one answer.

**5a. Shop scope — full Odoo or curated subset?**
The site-shape decision (`.planning/decisions/site-shape.md`) and the synthesis design both pointed at "a few things you can take home today" (~9 SKUs, sub-$300, ready-made). GL's message today says rebuild the FULL Odoo catalog. Two ways to read this:
- **Reading 1:** GL has updated the site-shape — full 51-product catalog goes in shop, mega menu reflects all 10 Odoo categories, browse-and-buy works for everything including premium arches.
- **Reading 2:** "rebuild Odoo accurately" means seed all 51 products in ERPNext (so the data exists), but the customer-facing shop still surfaces a curated subset, with the rest reachable via lookbook / inquiry.
- **My read** of GL's message ("Odoo has almost everything. It just needs to be accurately rebuilt here. ... in the menu, 'shop' should be a mega menu... categories... and those links should lead to /shop-by-category and all the way down to the product level"): Reading 1. GL wants the full catalog browsable. The shop becomes the customer's window onto everything LT makes, not just take-home items.
- **Confirm or correct.** This decision drives every other decision.

**5b. Routing shape for the mega menu**
Pick Shape A / B / C from §3 above. My read: Shape A (restructure Item Groups + override webshop's `/shop-by-category` template) is the lowest-risk path that uses Frappe's machinery. But the synthesis design points at Shape B aesthetically. **GL's call.**

**5c. Variants / options — the Odoo-Frappe model fit**
Odoo's product variant model maps to ERPNext's Item Variant + Item Attribute model 1:1, but it's heavy: a 50-color × 3-size garland creates 150 Item Variant records. Two paths:
- **Full variant model:** create Item Attributes for every Odoo attribute family, generate Item Variants per combination. Webshop's variant selector then renders. Scales to thousands of records but is "right" by ERPNext's contract.
- **Form-fed options:** treat the product as a single Item, but on the product detail page render LT-owned color/size/add-on selectors, persist selections to the cart line as form data (or order notes). Avoids the variant explosion. Closer to LT's actual workflow (everything is made-to-order; no stock-tracked colors).
- **My read:** form-fed is right for LT — the products aren't held in stock by color, they're built per order. But this means we override webshop's product detail template and don't use Item Variants at all. Webshop's cart will then receive line items without variant attributes; we'd need a controller-side mechanism to capture options into the SO.
- **GL's call.** This decision drives the entire product-detail rebuild approach.

**5d. The 18 missing products**
- Re-seed all 18 from `catalog.json` data? Yes per GL's direction.
- 3 of them have no usable Odoo data (classic-organic-balloon-garland, classic-column, star-column — no price, no image). Skip these, or stub them with placeholders + flag for Jeff to fill?

**5e. Photos — visual review needed**
Can't assess "photos don't always match" from data alone. Two options:
- I open each `_resources/odoo-export/images/<slug>.png` and the running site's render side-by-side and flag mismatches (ask GL to verify any I'm uncertain about). ~30 images to scan.
- GL spot-checks by product name and tells me the offenders.

**5f. Descriptions for the ~26 echo-only products**
Either: (a) port from Odoo if available there (need to scrape the live Odoo site again or check if the JSON-LD scraper missed them); (b) write fresh in LT voice; (c) leave the echo-only as a rebuild-time TODO and write later. **My read:** (a) first — re-run the Odoo description fetch to see what's actually there before writing new copy. If Odoo doesn't have them either, write fresh.

**5g. Item Code jargon — where does it disappear?**
- `/shop-items` cards: "Shop Items | Item Code : <slug>" — comes from webshop's `website_item_row.html` template
- `/shop/<slug>` detail: "Shop Items | Item Code: <slug>" — comes from webshop's `templates/generators/website_item.html` (or similar)
- Both are Jinja overrideable by placing same-name files at `apps/locally_twisted/locally_twisted/templates/...`. Easy fix once we decide whether to keep these pages.

---

## 6. Sequenced plan (sketch — GL approves shape first)

This is just so GL can see the shape; not a commitment. Sequence assumes Reading 1 (full Odoo catalog in shop) + Shape A (Item Group restructure + webshop overrides) + form-fed options for variants. If GL picks differently, sequence rewrites.

1. **Data restructure** (no UI changes yet)
   - Restructure Item Groups: Shop Items becomes a parent (`is_group=1`), 10 children created (Arches, Columns, Bouquets, Get-Well Bouquets, Garlands, Grab-n-Go, Drops, Table Decor, Stands & Easels, Seasonal Misc), each `show_in_website=1`
   - Re-tag all 33 existing items into correct child groups
   - Seed the 15 missing products from `catalog.json` (excluding the 3 that have no data)
   - For each product, port Odoo description if available; flag missing for prose-write
2. **Variant data plumbing**
   - Decide form-fed vs Item Variants per §5c
   - If form-fed: add a `selections` JSON column on Sales Order Item (or use existing `description` field) + render LT-owned attribute selectors in product detail Jinja override
   - If Item Variants: create Item Attributes from Odoo families, generate variants, set `enable_variants=1`
3. **Mega menu**
   - Update `apps/locally_twisted/locally_twisted/templates/includes/navbar/navbar.html` desktop tier-2 to render Shop as a hover/click mega menu sourcing from Item Group children
   - Mobile drawer: accordion or drill-down for Shop
4. **Override webshop templates for on-brand register**
   - `templates/pages/product_search.html` (the listing template `/shop-items` uses)
   - `templates/generators/website_item.html` (product detail)
   - Strip "Item Code : <slug>" jargon
   - Strip "/Nos" UoM suffix
   - Apply LT typography, colors, spacing per design guide
5. **Either fix `/shop-by-category` or remove it from IA**
   - If keeping: override webshop's `/shop-by-category` template for on-brand register
   - If removing: redirect `/shop-by-category` → `/shop`, scrub breadcrumb references
6. **Update `/shop` page**
   - Replace `_categorize()` keyword matcher in `shop.py` with `item.item_group` lookup once items are properly tagged
   - Filter pills sourced from Item Group children (10 pills, possibly grouped or condensed)
   - Add card kicker (category label), description preview, OOS badge driven by `disabled` or stock fields
   - Add bottom CTA section ("FOR SOMETHING LARGER" + 2 buttons) per design guide
7. **Verify in GL's browser before declaring any of the above done**

Each step is its own commit. Each step can be paused for GL review.

---

## 7. What I did NOT do

- Did not change any code, fixture, or DocType field
- Did not touch the `_categorize()` keyword matcher
- Did not seed any products
- Did not update the navbar
- Did not write to agency-tier docs
- Did not fix the mobile Add-to-Cart overlap bug (it's a webshop template issue; fix lands in step 4 above)

---

## 8. Files referenced

| File | Purpose |
|---|---|
| `_resources/odoo-export/catalog.json` | Source of truth for 51 products |
| `_resources/odoo-export/images/*.png` | 48 product images |
| `apps/locally_twisted/locally_twisted/www/shop.py` | Custom `/shop` controller — has the keyword categorizer |
| `apps/locally_twisted/locally_twisted/templates/includes/navbar/navbar.html` | Where mega menu lands |
| `_resources/design-guide/synthesis/shop/page.tsx` | Design reference for shop UX |
| `_resources/design-guide/screenshots/shop-{desktop,mobile}.png` | Visual reference |
| `scripts/verify/_screenshots/20260429-110427-shop-recon/` | Live render screenshots, all viewport-only |
| `scripts/verify/_oneshot_shop_recon.py` | The Playwright script that captured them |
| `scripts/setup/export_odoo_catalog.py` | The Odoo scraper (idempotent — could re-run for missing descriptions) |
