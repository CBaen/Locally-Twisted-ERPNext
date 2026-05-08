# Private Celebrations — Design Notes

## Concept signature: "Every Detail"

The private celebrations page is the one page in the suite that must be warm
without being loud. The buyer is a parent planning their kid's birthday, a
partner planning a wedding, someone planning a memorial for a person they loved.
The page must feel like someone who understands that these moments matter —
not a party supply store, not a sales funnel.

## Page structure rationale

### 1. Hero
- Background: `wedding-organic-half-arch.webp` — the most premium, tasteful
  private event image in the optimized portfolio. An organic half-arch is
  wedding/celebration register; it's not a cartoon birthday balloon.
- Overlay: slightly lighter than corporate/civic — the private celebrations page
  can breathe a little more. Still dark enough for readability.
- CTA copy: "Tell Us What You're Imagining" — taken directly from the voice
  guide's approved CTA. This is the most personal CTA in the suite.
- Eyebrow: "Private Celebrations · Wasatch Front" — no named clients, just
  geography and occasion type.

### 2. Memorial entry (Round 2 addition)
- Slate-blue fullbleed band immediately after the hero — the grief buyer finds herself
  in the first scroll, before she has to scan through birthday and wedding cards.
- Two-column on desktop: invitation copy left, KJSCOTT blockquote right.
- Heading: "If you're here for a celebration of life, you're in the right place."
  — direct address, no euphemism, no ceremony. Claims the buyer by name before
  anything else on the page does.
- Body copy: names the things families bring (a sports theme, a color, a place)
  rather than listing service capabilities. The buyer recognizes her own situation.
- KJSCOTT blockquote in structural position: brass left-rule, dark inset panel,
  italic Cormorant Garamond. This is the proof that earns the invitation — real
  words from a real family, at the top of the page, not buried in a testimonial grid.
- The types grid still includes the memorial card in position 5 for discovery
  completeness, but the grief buyer is no longer required to filter through four
  other occasion types to find herself.

### 3. Celebration types
- Warm White band. Five cards in a grid (3+2 on desktop — accepted orphan
  because the types are intrinsically odd-count and the card design accommodates it).
- Each card: icon + title + body description + proof line.
- Proof lines are category-level (no named clients): "300+ birthday installs,"
  "Ceremonies and receptions across Utah venues," etc.
- The "Memorials & Celebrations of Life" card is an intentional presence.
  The review from KJSCOTT (sports-themed funeral stand) is real and remarkable.
  Including memorial as an explicit type says: LT handles this with care.

### 3. Photo gallery
- Near-white band. Four images in portrait aspect ratio (3:4) — this is
  deliberate. Private celebration photography is more vertical than civic/corporate.
  It mirrors how people photograph their own events on phones.
- Leads with birthday then wedding then birthday again then wedding — alternating
  to show the breadth without making one type dominate.

### 4. Testimonials
- White band. Six review excerpts in a grid.
- No full names (abbreviated per the privacy practice in home.py).
- Includes the memorial review (KJSCOTT) — this is the most distinctive and
  trust-building review in the portfolio. A funeral stand that was "very tasteful
  and meaningful" is not what most balloon companies mention.
- Also includes Sara M. (7-year relationship), which proves longevity of
  private client relationships.

### 5. Buyer notes
- Stone band (lighter than slate — private pages should feel warmer than corporate).
- Four notes: same-day delivery, at-home or venue, custom to your vision, rush orders.
- Presented in white cards with brass left-rule.
- "Rush orders welcome" is an important signal — impulse celebration purchases
  are common, and LT has done rush jobs (multiple reviews confirm this).

### 6. CTA
- Navy fullbleed. Crimson button.
- Copy: "Tell us what you're imagining." — exactly the style guide's approved
  CTA phrasing.
- Phone number visible with "Planning on short notice?" — private celebration
  buyers are more likely to call when they need something fast.

## Photo choices
- Hero: `wedding-organic-half-arch.webp` — most elevated private event image
- Types: icons (no photos in the card grid — cleaner for this warmer page)
- Gallery:
  - `birthday-smurfs-arch.webp` — themed birthday (proves character/custom ability)
  - `wedding-floral-half-arch.webp` — wedding ceremony
  - `birthday-dolphin-backdrop.webp` — birthday photo moment
  - `wedding-foil-heart-arch.webp` — wedding reception backdrop

## Audience-specific moves
- "Every detail matters" as the hero sub-headline — this is the emotional
  register of private celebrations. Not civic authority. Not brand safety. Personal care.
- Memorials explicitly named as a celebration type — LT has done this, has a
  real five-star review for it, and most private celebrants don't know balloon
  decor can serve this moment. Naming it is a service differentiator.
- Warm white + stone + white palette throughout — the warmest palette in the
  suite, matching the warmest buyer register.
- Testimonials from real Google reviews, abbreviated, not fabricated — the
  testimonial for the sick girl and the unicorn balloon is the most human
  moment in the entire review corpus. It belongs on this page.

## Container discipline
- Hero: fullbleed
- Memorial entry: fullbleed (slate-blue) — the one dark band on this page; creates
  structural weight for the memorial buyer without making the whole page cold
- Types: band (warm white)
- Gallery: visual-field (near-white)
- Testimonials: band (white)
- Buyer notes: band (stone) — lighter than slate, warmer register
- CTA: fullbleed (navy)

The palette alternation is: warm-white hero → slate memorial entry → warm-white types
→ near-white gallery → white testimonials → stone buyer notes → navy CTA.
The slate memorial band is a deliberate interruption — it signals "this is different,
this is serious" before returning to the warmer register for the rest of the page.
No two adjacent same-color fullbleed sections. The hero image darkens to near-navy;
the slate band reads as a visual step, not an adjacency violation.

## Loop 1-1 change: Memorial card rewritten

Proxy-Loop-1-1 identified that the memorial card's proof line — "Verified by
customer reviews" — read like a Yelp disclaimer. This is the one card in the
suite where a real human is in grief, searching at midnight, needing to feel
that LT has done this before and knows what it means.

Two changes made:

1. **Card body copy rewritten** from generic "Sports themes, favorite colors,
   and personal tributes handled with care" to second-person address: "You tell
   us what they loved — a team, a color, a place, a thing that was theirs. We
   make it visible." This speaks to the person planning, not a category label.
   It acknowledges they have knowledge (what the person loved) and LT's job is
   to make that visible.

2. **Proof line replaced** with the KJSCOTT review excerpt verbatim:
   `"They captured my vision, delivered on time, very tasteful and meaningful."
   — KJSCOTT`. The real review is the proof. The disclaimer was not.

The KJSCOTT review still appears in the testimonials grid below, but the card
itself now carries human evidence rather than institutional reassurance.
