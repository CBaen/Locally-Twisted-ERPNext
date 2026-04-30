# Webshop State vs Spec — 2026-04-30

Screenshots live at:
- `_resources/webshop-state-vs-spec-2026-04-30/screenshots/now/` — current ERPNext site
- `_resources/webshop-state-vs-spec-2026-04-30/screenshots/spec/` — Odoo mirror (the spec)

---

## 1. What it looks like NOW

### /shop — the main landing page (desktop)

The page has two distinct visual sections stacked vertically.

**Top section (hero):** A soft off-white band with an eyebrow label in small caps ("TAKE HOME TODAY" or similar), a large serif headline ("A few things you can take home today."), and a short paragraph of body copy. A small "View cart" button sits in the top-right of the band. The overall feeling is spacious and editorial — similar to the design guide's tone.

**Filter row:** Below the hero is a row of rounded pill-shaped filter buttons labeled All items, Arches, Columns, Bouquets, Get-Well Bouquets, Garlands, Drops, Grab & Go, Table Decor, Stands & Easels, Deliveries, Seasonal & Specialty. "All items" appears active.

**Product grid:** A 3-column grid fills the rest of the page at desktop width. Each card has a tall photo (roughly 3:4 portrait ratio), the product name in a serif font underneath, a short description in small gray text, a price ("from $340"), and a teal "Add to cart" button. 53 cards are visible, all on one page — no pagination visible. Images are real product photos (balloon arches, bouquets, etc.).

**Mobile (375px):** The filter pills wrap to multiple lines above the grid. The grid drops to a single column. Each card is full-width. The same card structure (photo → name → desc → price → button) is preserved. The page is very long because all 53 cards stack vertically.

### /all-products (desktop + mobile)

The webshop's built-in "All Products" page (Frappe's default) renders **completely empty** — just a header, breadcrumb, and then a blank white area with the label "All Products / Filters / Clear All" and nothing else. The product listing area says "Rendered via JS" in the source but never populates, because the Webshop JS bundle (`web.bundle.WLOGYSZO.js`) is returning a 404. The page exists and loads, but shows no items to a shopper.

### /shop-by-category (desktop + mobile)

A clean page with an eyebrow label "BROWSE", a large serif headline "Everything we make.", and a short lede about custom work. Below is a 3-column grid of category tiles (desktop) / single-column stack (mobile). Each tile is a large square in the brand's warm blush/cream color with just the first letter of the category name as a placeholder (no photos), the category name below it in a serif font, and "None items" in small gray text — the item count is broken. Categories present: Arches, Columns, Bouquets, Get Well Bouquets, Garlands, Drops, Grab & Go, Table Decor, Stands & Easels, Deliveries, Seasonal & Specialty. Below the grid is a "For something larger" call-to-action band.

### /shop-items/arches — category landing (desktop + mobile)

The page is almost empty. It shows the header, a breadcrumb (Home > Shop by Category > Shop Items > Arches), "Arches" as the page label, then "Filters / Clear All" with nothing beneath — no products at all. Same issue as /all-products: the product listing for this route relies on the broken webshop JS bundle. The footer immediately follows the empty content area.

### /shop-items/arches/6-color-rainbow-arch — product detail (desktop + mobile)

The page works. At desktop: a breadcrumb trail at top (Shop by Category > Shop Items > Arches > 6 color rainbow arch), a large full-width product photo below it, then the product name in a serif font, size option pills (20ft / 25ft / 30ft / 35ft), a note "Price shows when you choose your options", and a grayed-out teal "Request a conversation" button. A short description paragraph follows. The page is clean and uncluttered.

At mobile: the photo stacks above the name and size pills. The layout holds well — nothing overlaps or breaks. The "Request a conversation" button is full-width at the bottom.

### /cart (desktop + mobile)

The cart page works. It shows the header, a "Your cart" heading, a small cart icon, the message "Your cart is empty. Browse the shop or get in touch about a custom installation." with two text links below ("Browse the shop" and "Tell us about your event"). Clean, minimal, branded correctly.

---

## 2. What the spec (Hetzner/Odoo) looks like

### /shop — Odoo product listing (desktop)

The Odoo shop has a **two-column layout**: a left sidebar that is roughly ¼ of the page width, and a product grid that takes the remaining ¾.

**Left sidebar:** A collapsible "Categories" accordion showing the full nested category tree — Special Occasions (with Birthday Parties, Baby Reveal & Showers, Graduations, Missionary Farewell, Get Well as sub-items), Holidays & Seasons (with New Year's Eve, St. Patrick's Day, Easter, Mother's Day, Pride, Halloween as sub-items), What We Make (with Balloon Arches, Columns, Centerpieces, Helium Bouquets, Organic Garlands, Backdrops, Balloon Drops, Grab N Go, Balloon Cups, Table Decor as sub-items), Personalized Displays. Below the categories are attribute filter accordions: Arch Size (checkboxes for 20ft / 25ft / 30ft / 35ft), Column Height, Garland Length, Color Palette (scrollable list of 29 colors with a search box), Design (image swatches for Swirl / Layered), LED Lights (image swatches), Bouquet Size, and "latex colors" (53 items, searchable). A price range slider sits at the bottom of the sidebar.

**Product grid:** 3 columns at desktop (configured as 3 items per row, 21 per page). Each card has a square or portrait photo, the product name, and a price. Cards show a "wishlist" heart on hover. No item count label. Pagination with "21 products" shown.

**Sort bar:** Above the grid is a bar showing the total count ("21 products") and a "Sort by" dropdown with options: Featured, Newest Arrivals, Name (A-Z), Price Low-High, Price High-Low.

**Mobile (375px):** The sidebar is hidden by default — accessed via a "Filters" button. The grid drops to 2 columns (not 1). Sort dropdown is still visible. Cards are noticeably more compact (2 across).

### /shop-items/arches — Odoo category page (spec)

Same sidebar + grid structure as the main shop. The page header shows a breadcrumb (Products > What We Make > Balloon Arches) and the category title "Balloon Arches". The full left sidebar with all filter accordions is present. The grid shows 10 arch products with photos and prices. A "10 products" count label above the grid. Filter attributes are category-specific (Arch Size, Color Palette, Design, LED Lights).

### Product detail — Baby Shower Garland (spec, desktop)

Large photo on the left (50% width), product info panel on the right: product name as heading, breadcrumb above it (All products > Special Occasions > Baby Reveal & Showers > Baby Shower Garland), price ($150.00 starting), then variant selection — Garland Length as pill buttons (6ft / 9ft / 12ft with price extras shown), then a long list of "latex colors" checkboxes (53 options, displayed as a multi-select list with names only — no color swatches), a quantity field, and "Add to Cart" button. Below the cart button is a "Product Customization Request" form with fields for event date, notes, and photo upload. A "Specifications" section lists all variants. The page is very information-dense.

**Mobile:** Photo stacks above the info panel. The color list is extremely long — it dominates the page. No pagination on the color list.

### Cart — spec (desktop)

The Odoo cart page renders essentially empty (no items in the session) with a cart icon and "Your cart is empty!" message and a "Shop" button. The page structure shows Order / Address / Payment / Order Summary section labels even when empty, which are placeholders for the checkout flow.

---

## 3. The Gap

### Main shop listing (/shop vs Odoo /shop)

| What a shopper sees | Hetzner spec | ERPNext now | Visible difference |
|---|---|---|---|
| Navigation to categories | Left sidebar with full nested tree, always visible | Horizontal filter pill row (12 flat categories) | Spec has persistent category drill-down; current has flat one-level pills. No sub-category access from the listing. |
| Product grid columns | 3 columns desktop, 2 columns mobile | 3 columns desktop, 1 column mobile | Mobile drops to single column in current vs 2 columns in spec — shows fewer items per screen |
| Filtering | Sidebar with 7+ attribute types (size, color, design, LED, price range) all simultaneously visible | 12 category chips, no attribute filtering | No size, color, or price filtering at all in the current build |
| Sort control | Dropdown: Featured / Newest / Name / Price-Low / Price-High | None visible | Shoppers can't sort in the current build |
| Item count | "21 products" shown above grid | No count label | Shopper can't tell how many items are in a category |
| Pagination | 21 per page with page controls | All 53 on one infinite scroll | All items load at once — no pagination |
| Wishlist | Heart icon on card hover | None | Absent |
| Category images | Photos on category tiles (in sidebar) | Letter placeholders only ("A", "C", "B"…) | Category tiles have no photos and show "None items" count |

### /shop-by-category

| What a shopper sees | Hetzner spec | ERPNext now | Visible difference |
|---|---|---|---|
| Category images | Real product photos in tiles | Single capital letter placeholder (no images) | Every tile is an empty blush square with just an initial |
| Item count per category | Numeric counts (e.g. "10 products") | "None items" on every tile | Counts are broken — all show None |
| Layout | Not a standalone page in Odoo — categories live in sidebar | Full page 3-column grid (desktop) / 1-column (mobile) | Current has a dedicated page Odoo doesn't; but without images or counts the page is underpowered |

### Category landing (/shop-items/arches vs Odoo Balloon Arches)

| What a shopper sees | Hetzner spec | ERPNext now | Visible difference |
|---|---|---|---|
| Products | 10 arch products with photos + prices | Empty — no products displayed at all | This page is broken: the webshop JS bundle 404s, so no items render |
| Sidebar filters | Full attribute sidebar (Arch Size, Color, Design, LED) | Nothing | No filtering available |
| Category header | "Balloon Arches" heading + breadcrumb + description | "Arches" label + breadcrumb + Filters/Clear All labels | Same idea, but current shows an empty listing below |

### Product detail

| What a shopper sees | Hetzner spec | ERPNext now | Visible difference |
|---|---|---|---|
| Photo placement | Left 50%, product info right 50% | Full-width photo above product info (stacked) | Current is top-photo layout; spec is side-by-side |
| Variant selection | Pill buttons for size, long checkbox list for colors (53 options) | Size pill buttons only | No color selection in current build |
| Price visibility | Shows starting price, shows price extras per variant | "Price shows when you choose your options" — no number until variant selected | Current doesn't show any price until interaction |
| Add to Cart button | Blue filled button, always active | "Request a conversation" button (grayed out) | Current routes to conversation, not direct cart — intentional but differs |
| Customization form | "Product Customization Request" with date + notes + photo upload below cart button | Not present | Spec has an inline customization form; current build does not |
| Breadcrumb | Full path shown desktop, back-link on mobile | Full path shown both | Match |

### Cart

| What a shopper sees | Hetzner spec | ERPNext now | Visible difference |
|---|---|---|---|
| Empty state message | "Your cart is empty!" + Shop button | "Your cart is empty. Browse the shop or get in touch about a custom installation." + 2 links | Current is more on-brand; spec is generic |
| Checkout skeleton | Order / Address / Payment section labels visible even when empty | Clean — nothing shown until items added | Current is cleaner on empty state |
| Overall | Both handle the empty state | Both handle the empty state | Broadly equivalent at empty state |

---

## 4. Priority Recommendations

1. **Fix the category-level product listing first.** The `/shop-items/arches` route (and all other `/shop-items/{category}` pages) show zero products because the Webshop JS bundle is returning a 404. Shoppers who click any category tile land on an empty page — this is the most damaging gap to the shopping experience.

2. **Add real photos to the `/shop-by-category` category tiles.** Every tile currently shows a letter placeholder and "None items" — both the image and the count are broken. Category images from the spec mirror exist; the item counts can be pulled from the same Item Group query that drives the `/shop` page filter chips.

3. **Add a sort control and item count label to the main `/shop` listing.** The spec shows a simple "21 products / Sort by" bar above the grid. Without it, shoppers have no way to find cheapest or newest items, and no sense of how big the catalog is.

4. **Add attribute filtering (at minimum: size and price range) to the main listing.** The spec's sidebar has Arch Size, Column Height, Garland Length, and Price Range as the most-used filters. A simplified version — even just a price range slider and a few size chips — would close the biggest functional gap without requiring the full sidebar.

5. **Switch mobile grid from 1 column to 2 columns on `/shop`.** The spec shows 2 columns at mobile width. At 1 column, a shopper scrolling through all 53 items on a phone sees half as much at a time. This is a 1-line CSS change and is the fastest visible improvement with the least risk.
