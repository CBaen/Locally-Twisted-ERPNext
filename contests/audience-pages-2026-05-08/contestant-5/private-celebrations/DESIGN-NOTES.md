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

## Round 2 changes

**Structural change — opening act section added (section 2):**
The grief buyer in Round 1 had to scroll through the category grid (memorial as card #4), all six photos, the story block, and three other testimonials before reaching the KJSCOTT review and the memorial section. The field summary confirmed this was the test no one had fully cleared: "claim the grief buyer early, KJSCOTT in structural position before the category grid, memorial container commensurate with weight."

Round 2 fix: added a no-heading editorial section immediately after the hero. It contains:
- Two paragraphs that claim all buyer types including grief buyers explicitly ("the celebration-of-life for someone who meant everything to the people in that room")
- An explicit direct address: "If you're here planning a memorial or celebration of life, you're in the right place."
- KJSCOTT's review as a brass-rule pull-quote — before the category grid, not buried in a testimonials block

The category grid, photo proof, story block, and dedicated memorial section all remain. The memorial section is now the *second* time the grief buyer is addressed (not the first). The duplication is intentional — it signals the work is real and recurring, not a courtesy acknowledgment.

**Hero lede revised:**
"Personal, custom, and elevated. The decor that makes the room feel like the occasion deserves it." → "The celebrations that call for something beautiful. And the days that need it most." The new lede reaches both the joy buyer and the grief buyer without naming either.

**Eyebrow revised:**
Added "Remembrance" to "Birthdays · Weddings · Showers · Milestones · Remembrance" so the eyebrow itself signals inclusion before the first paragraph.

**Memorial section CTA link:**
Added a soft CTA link ("Start a conversation →") on the memorial section that routes to `/contact?intent=memorial` — distinct from the page-wide CTA button. Softer register, separate intent parameter.

**Photo section background:** moved from Sandstone to Warm White to preserve the no-adjacent-colored-sections rule (opening act is Warm White, category proof is Sandstone, photos now Warm White — alternating correctly). Story block moved to Ink (dark) for rhythm.

---

## Section decisions

### 1. Hero
Background: `wedding-organic-half-arch.webp` — the highest-taste photo in the portfolio. Organic arch with floral accents at an elevated aesthetic. This signals immediately that private celebrations are treated with taste, not mass-production. Pure Ink gradient (no navy — Ink is warmer and more intimate than Deep Navy for this context). Eyebrow now names all celebration types including "Remembrance." Lede reaches both joy and grief buyers.

### 2. Opening act (Warm White) — NEW Round 2
Short editorial section. No heading — reads as prose, not a labeled section. Claims all buyers before the category grid. KJSCOTT's review as pull-quote (brass left rule, light Sandstone tint background) is the first customer voice on the page, and it's the memorial review. Any grief buyer who lands here encounters this within the first scroll, without having to self-select through birthday and wedding content first.

### 3. Category proof (Sandstone)
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

### 4. Photo proof (Warm White)
Six photos. Background changed from Sandstone to Warm White in Round 2 to preserve alternation: opening act (Warm White) → categories (Sandstone) → photos (Warm White) → story (Ink). No two adjacent colored full-width sections.

Photos:
- `wedding-organic-half-arch.webp` — hero-quality organic arch
- `wedding-floral-half-arch.webp` — floral wedding arch
- `birthday-smurfs-arch.webp` — themed children's birthday (shows range)
- `birthday-dolphin-backdrop.webp` — custom birthday backdrop (milestone scale)
- `wedding-foil-heart-arch.webp` — foil heart arch for celebrations
- `birthday-balloon-bouquets.webp` — bouquet arrangement (accessible price point proof)

6 photos = 6-column desktop, 3-column tablet, 2-column mobile = balanced grid, no orphans.

### 5. Story block (Ink, dark)
Three editorial paragraphs on a dark Ink background — moved to dark in Round 2 for visual rhythm (alternating with Warm White photo section above). First paragraph: core argument, private events are personal, the decor should feel like a gift. Second paragraph: 300+ birthday installs, wedding work across Wasatch Front. Third paragraph: delivery/setup/teardown logistics.

### 6. Memorial section (Warm White, standalone, full-weight)
The second time the memorial buyer is addressed on this page — the first was in the opening act (section 2). Two paragraphs, eyebrow label, editorial heading. Soft dedicated CTA link ("Start a conversation →") routes to `/contact?intent=memorial` — distinct from the page-wide CTA button, softer register.

This section doesn't appear on any other page. The duplication (opening act + dedicated section) signals that memorial work is a real recurring part of the business, not a courtesy acknowledgment.

### 7. Icon bar (Navy)
Four icons: premium-private-event, design-driven, balloon-bouquet (with "300+ Birthday Installs" label), delivery-install. The design-driven icon is specific to this page — it speaks to the buyer who wants to know their vision will be heard, not just fulfilled from a menu.

### 8. CTA (Ink)
"Tell us what you're imagining." — the brand voice copy example from the style guide, used here where it fits perfectly. This is an invitation, not a form push. The body explains what to share and how ("the occasion, the date, and the feel you're going for").

## Color pattern (Round 2)
Warm White (opening act) → Sandstone (categories) → Warm White (photos) → Ink (story) → Warm White (memorial) → Navy (icon bar) → Ink (CTA)
No two adjacent colored full-width sections. ✓

## Distinct private-celebrations-only elements
- Opening act section claiming grief buyer before category grid (only this page)
- KJSCOTT pull-quote as first customer voice (brass left rule, before category grid)
- Sandstone background for category proof (warmest palette surface used as section background)
- Portrait-oriented photo grid (3:4) vs. landscape (4:3) on other pages
- Category proof with brass icon + text cards (vs. plain text grids on civic/corporate)
- Dedicated memorial/celebration-of-life section with its own soft CTA link (unique to this page)
- Memorial buyer claimed twice: opening act paragraph + dedicated section
- CTA copy uses "Tell us what you're imagining" (brand voice touchstone)
- No named client roster — honest privacy posture
