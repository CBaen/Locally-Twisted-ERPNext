# Decision Brief — Header Navigation Structure

**Status:** Awaiting GL decision before Phase 1 Slice 2 (header + footer build).

## The question

The prior platform attempt's header had three top-level menus that overlapped:
- **What We Make** (product types: arches, garlands, walls, drops, columns…)
- **Special Occasions** (use cases: birthday, wedding, baby shower, corporate, etc.)
- **Holidays & Seasons** (holiday-specific designs)

GL flagged uncertainty: "I'm unsure about 'Special Occasions' and 'Holidays & Seasons' and 'What We Make' being super menus. Is this logical?"

## The problem

These three menus point at the same products viewed through different lenses. A "birthday balloon arch" lives under:
- **What We Make** > Arches
- **Special Occasions** > Birthday
- (And maybe **Holidays & Seasons** if it's a milestone year)

This creates three problems:

1. **Customer confusion.** "Where do I look first?" is a friction step that competitors don't have. Customers bounce between menus instead of finding the product.
2. **SEO duplication.** Search engines see the same product reachable through multiple paths and have to choose one as canonical. The non-canonical paths get downweighted, splitting the page authority three ways instead of concentrating it.
3. **Maintenance drag.** Every new product has to be tagged into all three menus correctly. Easy to miss; hard to audit.

## Three options

### Option A — Keep all three super-menus (the prior approach)

Pros:
- Familiar to anyone who saw the prior platform
- Multiple entry paths can feel "rich"

Cons:
- All three problems above
- Mega-menus on mobile are hard to make accessible (deep nested touch targets)
- Adds substantial information architecture work to Phase 1

### Option B — Single product menu + occasion landing pages (recommended)

Structure:
- **Top nav:** Home · What We Make · Balloon Twisting & Face Painting · Shop · Contact
- **What We Make:** mega-menu by product type (Arches, Garlands, Walls, Drops, Columns, Centerpieces…)
- **Occasions and Seasons:** become filtered landing pages reachable from a "Browse by occasion" link in the header AND from the homepage. URL: `/occasions/birthdays`, `/occasions/weddings`, `/seasons/halloween`, etc.
- These landing pages show the same products as What-We-Make but with use-case framing and occasion-relevant photography.

Pros:
- Single product source-of-truth (canonical SEO path)
- Cleaner mobile nav (one mega-menu instead of three)
- Occasions and seasons still get found (via landing pages + internal linking + sitemap)
- Maintenance is simple: tag a product once with type, optionally with occasion/season tags
- Anthropologie / Etsy / Crayola use this pattern — exactly the "Creator" brand archetype the style guide names

Cons:
- Customers used to the prior approach lose the multiple-entry-path pattern (low cost since the prior site never went live to customers)
- Internal linking has to be deliberate so the occasion pages don't become orphans

### Option C — Single product menu, no occasion/season landing pages at all

Pros:
- Simplest possible structure

Cons:
- Loses the occasion-based discovery (someone searching "balloon decor for a baby shower" doesn't land on a tailored page)
- Wastes content opportunity that's already implicit in the product line
- Hurts SEO/AEO long-tail capture

## Claude's recommendation

**Option B.** Rationale:
- Resolves the three problems from Option A without losing the discovery surface
- Matches the brand archetype the style guide already names
- Sets up SEO correctly from day one (canonical product URLs + occasion landing pages with internal links to the canonical products)
- Lower mobile-accessibility burden than three competing mega-menus
- The occasion landing pages can ship in Phase 1 (no extra phase needed) — they're just product list pages with a different filter applied

## What this affects in Phase 1

- **Slice 2 (Header + footer):** structure depends on this decision. Need GL's call before this slice can build.
- **Slice 7 (Products listing) + Slice 8 (Product detail):** the canonical product URL pattern depends on this decision. Option B = `/shop/<product-type>/<product-slug>`.
- **Slice 3 (Landing page):** the homepage's "Browse by occasion" entry point depends on whether occasions exist as a discovery surface.

## What I need from GL

Pick A, B, or C. (My recommendation: B.)
