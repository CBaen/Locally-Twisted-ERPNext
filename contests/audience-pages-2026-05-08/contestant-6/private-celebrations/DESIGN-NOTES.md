# Design Notes — Private Celebrations

## Audience and buyer posture
Birthday parents, wedding planners, baby shower hosts, milestone families, and memorial/celebration-of-life organizers. This audience is the most emotionally diverse — a parent planning a surprise party has completely different emotional stakes than someone planning a celebration of life. The page must hold both without privileging one.

The buyer here isn't looking for a client roster — private clients expect privacy. Proof comes from volume stats and portfolio photography, not named organizations.

## The page's central structural difference from other audience pages
The three other pages (civic, corporate, schools) all have a named-client roster as a major section. Private celebrations cannot and should not have one. Instead, this page uses **event-type moment blocks** — each celebration type gets its own text + 3-photo cluster. This gives the page more visual rhythm and emotional range than the other pages, while delivering the same proof density through photography.

## Structural choices

### Hero
- Background: `wedding-organic-half-arch.webp` — the most emotionally resonant hero image available. An organic half arch is elegant, personal, and visually distinct from the civic/corporate arches used in other hero images. Position right — the arch composition leaves readable dark space on the left.
- Overlay: ink left fade (not navy), giving it a darker, more intimate ground than the civic or corporate pages.
- H1: "The moment deserves the detail." — the most emotionally loaded headline in the suite. Avoids "we" — the sentence is about the moment and the detail, not the company.
- CTA: "Tell us what you're imagining" — lifted from the style guide's recommended CTA voice. Invites, doesn't push. Deliberately softer than "Request a quote" used on corporate/civic/school pages.

### Stats band (ink, section 2)
Same ink ground as the civic page stats, but with different icons and different stat content:
- "300+" private events — volume proof without named clients
- "Every Detail" (Design Driven) — emotional promise around craft
- "To Your Door" (Delivered) — removes logistical anxiety
- "Wasatch Front" (Trusted) — geographic anchor, personal scale

The hero-to-stats transition: hero is ink ground with gradient → stats is full ink. They read as one continuous dark register before lifting into the warm-white moment blocks. This is intentional — the page starts deep/intimate and opens up.

### Event moment blocks (warm-white, section 3)
Four blocks: Birthday, Weddings, Baby Showers, Milestones & Memorials.

Each block is a two-column layout (desktop): copy left / photos right, alternating on even blocks. The photo cluster inside each block uses a 2-column grid with the first photo spanning full-width — hero + two thumbnails per occasion.

Desktop alternation: odd blocks = copy left / photos right; even blocks = photos left / copy right. This creates natural eye movement across the page.

**Memorial block special handling:** "Milestones & Memorials" is grouped because they share a tone register (retrospective, weighted, not celebratory-shouty). The copy explicitly acknowledges "Balloon decor can carry weight when it needs to" — this is the only place on the LT site that directly names the memorial use case. The Google review in home.py (KJSCOTT memorial sports-themed stand) proves this is real demand.

### Quote notes (navy, section 4)
Rather than another named-client section, the private page uses a list of five practical buyer assurances:
- No minimum order size
- Color matching from real-world sources (Pinterest, florals, venue swatches)
- Delivery and setup included
- Photo-moment orientation (for their phone camera, not just professional photography)
- Memorial discretion assurance

The header "A few things worth knowing before you quote" is deliberately humble — it doesn't oversell. The navy ground makes this section feel like a trusted aside, not a hard sales push.

### CTA (sandstone, section 5)
Sandstone is the warmest palette surface — appropriate for a page that culminates in personal occasions. The CTA heading "Tell us about the celebration" is the most personal of the four pages' closing CTAs. The button is navy (not crimson) — a quieter action color appropriate for the emotional weight of some of these events.

## Container contract
1. Hero — fullbleed
2. Stats — fullbleed (ink)
3. Moments — band (warm-white)
4. Quote notes — fullbleed (navy)
5. CTA — band (sandstone)

Adjacent fullbleed color check:
- Hero (ink) → Stats (ink): these two read as one continuous dark block — the border-top brass rule inside the stats section is the visual separator. Hero-to-stats is NOT two colored sections back-to-back; they're intentionally the same ground.
- Stats (ink) → Moments (warm-white): ✅
- Moments (warm-white) → Notes (navy): ✅
- Notes (navy) → CTA (sandstone): ✅

## Round 2 Changes

**Hero lede rewritten** to claim the grief buyer in the first sentence, before the scroll begins. Original lede listed occasion types; revised lede names the full emotional range — including celebrations of life — and closes with "Whatever brought you here, you're in the right place." The grief buyer is claimed before they have to self-select through birthday and wedding content.

**KJSCOTT review moved into the Milestones & Memorials block** as a brass-ruled blockquote inside the moment's prose. Previously referenced in design notes only; now structurally present in the HTML. The review is placed in the exact section that answers what that buyer came to find — not in a generic testimonials band. The blockquote format (brass left rule, italic) signals editorial weight without sentimental decoration.

**Milestones & Memorials desc_extended** adds a second paragraph that speaks directly to the grief buyer without euphemism, contextualizes the KJSCOTT review in narrative form, and names Jeff specifically — making it personal, not institutional.

These three changes together complete what the field summary identified as the unclosed memorial test: early claim (hero lede), structural proof position (KJSCOTT in the memorial block), and commensurate container (four-prose-block architecture, unchanged).

## What makes this page feel specifically private/personal
1. Hero CTA: "Tell us what you're imagining" — not "request a quote"
2. No named clients anywhere on the page
3. Four distinct event types given full prose treatment (including memorials)
4. Photo clusters grouped by occasion, not by product type
5. "No minimum order size" addressed in the quote notes — this audience is often nervous about that
6. Memorial discretion explicitly named
7. "Celebrate" and "every detail" language — emotional register, not operational
8. Sandstone closing CTA — the warmest page ending in the suite
