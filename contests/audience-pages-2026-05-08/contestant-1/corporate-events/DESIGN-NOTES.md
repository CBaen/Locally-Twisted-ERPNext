# Corporate Events — Design Notes

## Concept signature: "Brand Authority"

The corporate page is designed for a marketing director at Ancestry, a brand
manager at America First Credit Union, or an events coordinator at KSL. These
buyers care about: brand color accuracy, professional execution, AP-friendly
invoicing, and repeatable quality. The page should feel like handing them a
capability statement — controlled, credentialed, and specific.

## Page structure rationale

### 1. Hero
- Background: `corporate-logo-arch.webp` — a branded arch at a corporate entrance.
  This is the archetypal corporate balloon image. Logo integration, on-color,
  professional setting.
- Ink/black heavy overlay — darker than the civic page, more corporate in register.
  The Brand Direction banner uses ink grounds; this hero borrows that quality.
- Two CTAs: primary "Request a Corporate Quote" (navy) and secondary "View Installed Work"
  (outline). Corporate buyers often want to vet the portfolio before committing.
- Copy: "Brand-safe balloon decor for Utah corporate events." — Brand-safe is the
  operative term. It's the corporate buyer's primary concern.

### 2. Client crawl (scrolling name bar)
- Ink background (very dark, creates a distinct authority band after the hero).
- All 30 corporate clients scroll slowly. This is the proof density moment —
  seeing Ancestry next to Zions Bank next to KSL next to Utah Jazz says
  "this company works at every tier of corporate event."
- The crawl is aria-hidden with a visible label above. Screen reader users
  hear "Clients include" and can tab through if they want; the animation
  pauses on hover/focus.

### 3. Case story
- Text-first layout on mobile (image below on small screens, image right on desktop).
  This reversal from civic creates visual variety across the suite.
- Uses WSU Weberstock case — broadcast partners (KSL, KUTV) mentioned, which
  is very compelling for corporate buyers doing events that will be on camera.
- Copy names specific client categories: technology, financial services, media.

### 4. Photo gallery
- Slate Blue band — corporate in register without being black.
- Three photos in equal columns: logo arch, Weberstock photo op, WSU arch bouquets.
- All three are clearly corporate-context images.

### 5. Buyer notes
- White band. Four items with brass left-rule accent.
- AP-friendly invoicing, brand color matching, on-site install and strike,
  multi-location coordination.
- These are the exact four questions corporate buyers ask before approving a vendor.
  No other balloon company in Utah has them listed explicitly.

### 6. Services
- Near-white band. Four cards with navy left-border accent.
- Services named for corporate contexts: "Branded Entrances & Logo Arches",
  "Grand Opening Arches", "Lobby & Stage Columns", "Brand-Color Cluster Decor."
- Deliberately different naming from the civic page's services.

### 7. CTA
- Ink ground (very dark) — the premium corporate closer. Brass top rule accent.
- Navy primary button (not crimson) — corporate buyer register, quieter CTA.
- Phone number visible below as secondary option — corporate buyers sometimes
  prefer to call their vendor before committing.

## Photo choices
- Hero: `corporate-logo-arch.webp` — strongest corporate proof image
- Story: `corporate-wsu-arch-bouquets.webp` — university corporate event, broadcast context
- Gallery: All three corporate portfolio images combined

## Audience-specific moves
- "Brand-safe" appears in hero headline — the exact phrase corporate buyers use
- AP-friendly invoicing is called out explicitly — a real procurement consideration
- "On camera" copy in the story — corporate events are filmed
- Phone number in CTA — corporate buyers call vendors; other audiences click forms
- Client crawl vs. client grid: corporate gets the crawl (showing breadth);
  civic gets the grid (showing the full named list). Different emphasis for
  different buyer postures.

## Container discipline
- Hero: fullbleed
- Client crawl: fullbleed (Ink band, clip mode semantically)
- Story: band
- Gallery: visual-field (Slate Blue band)
- Buyer notes: band (white)
- Services: band (near-white)
- CTA: fullbleed (Ink)

Color alternation: hero (dark image) → crawl (ink) → story (warm white) →
gallery (slate) → buyer notes (white) → services (near-white) → CTA (ink).
The two dark bands (crawl and CTA) are separated by four lighter sections.

## Loop 2-2: Known gap — brand color visual proof

The crawl proves volume (30 names in motion = scale). What it does not prove is
brand color precision. A marketing director at Zions Bank sees her employer's
name scroll past — that lands. Her unstated follow-up question: "can they match
our exact corporate blue?"

The gap: no section currently shows the color work. The buyer notes claim color
matching is available; they don't show it.

The next evolution of this page is a section — after the crawl or inside the
buyer notes — that shows three or four real brand color swatches paired with
named clients. Something like: KSL's navy, Zions' corporate blue, Chick-Fil-A's
red, America First's palette. Not described. Shown as actual color blocks.

**Why not built in Round 2:** the proxy identified this as a future direction,
not a Round 2 requirement. The page is competitive now on operational voice
("invoice-ready," "AP-friendly," "brand-safe" — copy that sounds like someone
who has been in a vendor meeting before). The swatch section would move from
credible to visually proven.

**Hold the word choices.** The operational register in buyer notes and services
copy is the page's signature. Do not simplify or genericize "AP-friendly,"
"invoice-ready," or "brand-safe" in future edits — these are the thing a color
swatch section alone cannot provide.
