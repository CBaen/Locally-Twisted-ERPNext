# Corporate Events — Design Notes

## Audience posture
Marketing teams, event managers, AP departments, store openings, broadcasters, financial institutions.
Buyer thinks in: brand palette compliance, invoicing process, repeatability, and whether the vendor
will make their job harder or easier. They are NOT thinking "fun party."

## Distinctive move
"Brand-safe. Repeatable. On your colors." — three words as a tagline in the hero. This is the
language a marketing director actually thinks in when evaluating vendors. Putting it in the hero
makes LT sound like it understands the buyer immediately.

The case study section names industries rather than dwelling on a single client — broadcasters,
national restaurant groups, financial institutions — so the buyer self-identifies their peer group
in the proof.

## Section decisions

### Hero
- Image: `corporate-logo-arch.webp` — a branded arch, visually on-brand for corporate context
- H1: "Balloon decor that respects your brand." — implies LT won't embarrass the client with
  generic or off-brand work. Quiet confidence, not a sales shout.
- Three-word tagline in brass below H1: "Brand-safe. Repeatable. On your colors."
- Ink overlay (darker than civic) because corporate audiences read the darkness as premium.

### Client proof band
- Slate Blue background (vs. Ink for civic) — differentiates the two pages while staying within
  the brand system. Also creates the visual narrative: civic = darkest authority, corporate = still
  serious but slightly warmer.
- 29 named clients across media, finance, restaurant, healthcare, and event categories.

### Photo row
All three optimized portfolio photos: logo arch, WeberStock festival backdrop, WSU arch with bouquets.
These show range: entrance arch → festival scale → event arrangements. All visibly professional.

### Case study
Named KSL/KUTV/FOX13 (broadcasters), Ancestry (tech/genealogy), and financial institutions
(Zions, America First, Fidelity, Morgan Stanley). These are the names a Utah corporate buyer
recognizes as credible comparators. The copy also handles the repeatability point ("annual
parties, recurring grand openings") because corporate buyers think about process, not one-offs.

### Service notes
Four cards with left navy border treatment — more "corporate document" feel than the civic page's
plain card. Grid: 1×4 mobile stacked, 2×2 tablet, 4×1 desktop.
- Branded entrance arches
- Corporate party decor
- Brand activation installs
- Invoiceable & repeatable (the operational differentiator the AP buyer needs to see)

### Icons band
Ink background (darkest) for authority — this is the corporate credibility tier.
Icons: Corporate Entrance (brand-safe claim), Trusted Partner (repeat relationships),
Professional (operations), Delivered Cleanly (logistics).

### CTA
"Corporate events move on tight schedules." — names the buyer's real constraint.
"Share the date, venue, brand palette" — tells them exactly what LT needs, which reduces
friction for a busy event manager.

## Color sequence
Hero (Ink overlay) → Clients (Slate Blue) → Photos (Warm White) → Case Study (Stone) →
Services (White) → Icons (Ink) → CTA (Navy)

Adjacent pair check: Slate Blue → Warm White ✓, Stone → White ✓, Ink → Navy — these two are
both dark. The White services section separates them. Order is correct.

## Container contract
- `.lt-corp-hero` — fullbleed
- `.lt-corp-clients` — fullbleed (inner wrapper)
- `.lt-corp-photos` — band (max-width 1200px)
- `.lt-corp-case` — band (max-width 900px)
- `.lt-corp-services` — band (max-width 1100px)
- `.lt-corp-icons` — fullbleed (inner wrapper grid)
- `.lt-corp-cta` — fullbleed (inner wrapper max-width 680px)
