# Design Notes — Private Celebrations

## Audience

Birthday parents, wedding planners, baby shower hosts, milestone families (60th anniversaries, retirements), and memorial/celebration-of-life organizers. Buyer posture: personal, emotionally invested, taste-elevated, gift-feeling. Expects privacy — no named clients.

## Page intent

This is the most emotionally complex page of the four. The buyer isn't choosing between two vendors based on roster credibility (there is no named roster for private clients) — they're evaluating whether the company understands what this moment means and whether the decor will feel worthy of it.

The page has to:
1. Show range (birthdays to weddings to memorials — a 300+ install history)
2. Show taste (the wedding and organic decor photos are the strongest in the portfolio)
3. Communicate that customization is real, not a catalog upsell
4. Acknowledge memorial work explicitly — it's a differentiator most competitors don't mention and it earns trust from the most emotionally vulnerable buyers

The tone is warmer than the other three pages. Not softer — still quiet confidence — but the language is more personal. "Tell us what you're imagining" instead of "Request a quote."

## Section decisions

### 1. Hero
Background: `wedding-organic-half-arch.webp` — the highest-taste photo in the portfolio. Organic arch with floral accents at an elevated aesthetic. This signals immediately that private celebrations are treated with taste, not mass-production. Pure Ink gradient (no navy — Ink is warmer and more intimate than Deep Navy for this context). Eyebrow names all the celebration types. H1 includes "life's milestone moments" — broad enough to include memorials without naming them.

### 2. Category proof (Warm White)
Six cards with icon + label + detail. Icon-led cards (brass SVG icons from the brand suite, 40px) rather than a pure text grid — more personal, less corporate registry. The "300+ birthday installs" appears in the Birthdays card, not in the hero or proof band, so it lands with the context that explains it. The Birthdays card leads the grid because it has the most proof weight. Wedding second, then baby showers, then memorial, then anniversary, then graduation.

Memorial is the fourth card — not buried, not leading. It's in the middle third where a buyer scanning the grid will see it. The language is direct: "Tasteful, restrained, and meaningful balloon decor for honoring someone." No euphemism. No selling.

### 3. Photo proof (Sandstone background)
Six photos in a portrait-oriented grid (3:4 aspect ratio) rather than landscape — suits wedding/celebration photography better. Sandstone background (#D9C7B3) is the warmest surface in the palette, appropriate for personal celebrations. Photos:
- `wedding-organic-half-arch.webp` — hero-quality organic arch
- `wedding-floral-half-arch.webp` — floral wedding arch
- `birthday-smurfs-arch.webp` — themed children's birthday (shows range)
- `birthday-dolphin-backdrop.webp` — custom birthday backdrop (milestone scale)
- `wedding-foil-heart-arch.webp` — foil heart arch for celebrations
- `birthday-balloon-bouquets.webp` — bouquet arrangement (accessible price point proof)

6 photos = 6-column desktop, 3-column tablet, 2-column mobile = balanced grid, no orphans.

### 4. Story block (Warm White)
Three editorial paragraphs. First paragraph establishes the core argument: private events are personal, the decor should feel like a gift. Names specific examples (60th birthday, wedding arch vs. children's party). Second paragraph describes the design-first approach and calls out the 300+ birthday installs plus wedding work. Third paragraph closes with the practical logistics note (delivery/setup/teardown included).

### 5. Testimonials (Ink, dark, fullbleed)
Four real customer quotes from the home.py REVIEW_QUOTES, selected for private celebration relevance:
1. Out-of-town client — demonstrates LT serves anyone, not just Salt Lake locals
2. Personal celebration ("sick girl smile" / unicorn balloon) — shows the deeply personal work
3. Memorial/funeral — the most important quote on this page; shows the company handles grief with grace
4. Children's birthday — the most common purchase type, reassurance for parents

Using `<blockquote>` / `<cite>` for semantic correctness. Attribution is "Out-of-town client" / "Personal celebration" / "Memorial service" / "Children's birthday" — context without names. This is the right privacy balance.

### 6. Memorial note (Warm White)
A dedicated section for memorial work, not just a card in the category grid. This is a deliberate choice: the buyer who is planning a memorial for someone they loved needs to know they can bring this conversation to a real person. The section gives them permission to do that. Two paragraphs — the first describes what different looks like (colors, scale, approach), the second is an explicit invitation ("share the context when you reach out").

This section doesn't appear on any other page. It's specific to private celebrations and it's the most emotionally careful writing in the suite.

### 7. Icon bar (Navy)
Four icons: premium-private-event, design-driven, balloon-bouquet (with "300+ Birthday Installs" label), delivery-install. The design-driven icon is specific to this page — it speaks to the buyer who wants to know their vision will be heard, not just fulfilled from a menu.

### 8. CTA (Ink)
"Tell us what you're imagining." — the brand voice copy example from the style guide, used here where it fits perfectly. This is an invitation, not a form push. The body explains what to share and how ("the occasion, the date, and the feel you're going for").

## Color pattern
Warm White (categories) → Sandstone (photos) → Warm White (story) → Ink (testimonials) → Warm White (memorial) → Navy (icon bar) → Ink (CTA)
No two adjacent colored full-width sections. ✓

## Distinct private-celebrations-only elements
- Sandstone background for photo section (warmest palette surface — only this page uses it)
- Portrait-oriented photo grid (3:4) vs. landscape (4:3) on other pages
- Category proof with brass icon + text cards (vs. plain text grids on civic/corporate)
- Testimonial section with four customer voices (no other page has this)
- Dedicated memorial/celebration-of-life section (unique to this page)
- CTA copy uses "Tell us what you're imagining" (brand voice touchstone)
- No named client roster — honest privacy posture
