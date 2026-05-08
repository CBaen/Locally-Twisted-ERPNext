# Audience Pages Contest — Locally Twisted

**Contest root:** `C:\Users\baenb\projects\Built_by_Cameron\_CLIENTS\locally-twisted\contests\audience-pages-2026-05-08\`
**Date:** 2026-05-08
**Mode:** Standard (N=8, Proxy-coached, two rounds, reflective loops, dissent moment, tightening pass)

---

## The Challenge

The Locally Twisted mega-menu currently ships four "Event Planning" entry points — **Civic & Community, Corporate Events, Schools & Campuses, Private Celebrations** — and they all silently render the same shared template. Every audience lands in the same room. That is a credibility leak: this is a top Utah events company with 60+ named clients across cities, schools, broadcasters, hospitals, banks, sports teams, and Pride organizations, and right now the menu makes the buyer feel like the company can't even tell those audiences apart.

You are one of 8 contestants. Each of you will design **all four audience landing pages** as a coherent suite. The winning suite gets shipped. The other suites stay in the gallery as a record of what was considered.

Each page should feel like it was made *for that buyer*, with Locally Twisted's real client roster and real installed work as proof. A city events coordinator should land on `/civic-community` and immediately recognize the work; a school activities director should land on `/schools-campuses` and feel the same. The pages remind everyone who reads them that LT is the only Utah balloon company doing this caliber of civic, corporate, school, and private work.

**Page weight per the brief:** substantial-but-focused. Multi-section pages (hero → real-client proof → story/case-study block → photo gallery → audience-specific service note → CTA). Not bloated, not minimal. Roughly 5–8 distinct sections per page, but composition is yours.

## The Stakes

GL chose the full standard contest machinery for this. This is consequential — these pages carry the company's credibility into the four highest-value buyer segments. Bring craft.

---

## What You're Designing For

### The four pages and their routes

| Route | Audience | Buyer posture |
|---|---|---|
| `/civic-community` | City events coordinators, Pride organizers, chambers, county events, public-facing community organizations | Public-facing, civic-scale, photographable, Americana/Utah-proud |
| `/corporate-events` | Marketing teams, brand activations, store openings, broadcaster events, bank/credit-union community days, corporate parties | Brand-safe, on-color, repeatable, professional, billable through AP |
| `/schools-campuses` | Activity directors, athletic departments, PTAs, college student life, graduation organizers | Spirit-driven, schedule-tight, school colors disciplined, family-friendly |
| `/private-celebrations` | Birthday parents, wedding planners, baby shower hosts, milestone families, memorial/celebration-of-life organizers | Personal, milestone-emotional, taste-elevated, gift-feeling |

### Real-client roster (the proof material)

These are LT's actual prior clients, pulled from Jeff's records. Use them aggressively as proof — logos, named drops, story attribution. Do not invent clients. You can omit any that don't fit a page; you cannot add any that aren't on this list.

**Civic & Community:** SLC Pride, Pride Center, Equality Utah, LGBT Chamber, Ogden city, Sandy city, Herriman City, Kearns City, Hooper City, Syracuse City, West Point City, Clinton City, SLC County, Ogden Weber Chamber, Galivan Center, UDOT, Ogden airport, Utah Art Alliance, Safe Kids Fair, Tree House Museum, Western Sports Park, Station Park, Downtown Daybreak, Live Daybreak, Shops at Southtown, Newgate Mall.

**Corporate Events:** Chick-Fil-A, Texas Roadhouse, Applebee's, Chili's, Honey Baked Ham, PotBelly, Ancestry, Megaplex, Paramount, KSL, KUTV, FOX13, LVT, Clear, Henry Schein, Museum of Illusion, Lux, Zions Bank, America First Credit Union, Young Automotive, IHC, Mountain Star Medical, SeaQuest, Fidelity, Morgan Stanley, Utah Jazz, Alpine Events, In the Events, FanX, The Boiler Room.

**Schools & Campuses:** University of Utah (UofU), Weber State University (WSU), St. Joseph's High School, plus any city/community items above that fit (e.g., Ogden city school events, Tree House Museum education days). The school roster is short — lean into specific named relationships and graduation/back-to-school context rather than padding with weak items.

**Private Celebrations:** No named-client roster (it's private celebrations — the buyer expects privacy). Use category-level proof: "300+ birthday installs", "weddings across the Wasatch Front", "memorial/celebration-of-life", testimonial phrasing without names, anonymized photo proof from the portfolio image library.

### Real photo library (the visual proof)

Two libraries. Use both. The Odoo library has more variety; the optimized portfolio set is already brand-toned for ERPNext.

**Optimized portfolio (already in production):**
- `apps/locally_twisted/locally_twisted/public/images/portfolio/optimized/` — 15 WebP files including:
  - `corporate-weberstock-photo-opt.webp`, `corporate-logo-arch.webp`, `corporate-wsu-arch-bouquets.webp`
  - `school-back-to-school-stage.webp`, `school-grad-garland.webp`
  - `seasonal-pride-columns.webp`, `seasonal-easter-rabbit-arch.webp`, `seasonal-halloween-tombstone.webp`
  - `birthday-balloon-bouquets.webp`, `birthday-dolphin-backdrop.webp`, `birthday-pirate-column.webp`, `birthday-smurfs-arch.webp`
  - `wedding-floral-half-arch.webp`, `wedding-foil-heart-arch.webp`, `wedding-organic-half-arch.webp`

**Odoo source library (read-only reference, deeper bench):**
- `C:\Users\baenb\projects\locally-twisted-odoo\assets\image assets\photos for website\` — broader set including IHC mockup, WSU arch and bouquets, Pride ceiling decor, Progress Flag backdrop, Rainbow heart parade, Tombstone backdrop, Twisting Mirabel, custom arches/columns subfolders, helium bouquets, deliveries, easter/Halloween/Christmas decor folders, parades, Photo opts, mock ups.
- `C:\Users\baenb\projects\locally-twisted-odoo\assets\previous clients.txt` — the canonical client list (use the curated rosters above first; this is the raw source).

**Rule:** reference filenames and full paths in your HTML. Do not copy or move image files between trees in this contest phase. Implementation phase (post-winner) will handle copying any Odoo-source images into the production tree.

---

## Voice / Style / Standard

**The style guide is canonical:** `_resources/STYLE-GUIDE.md` v4.5. Read it before designing.

Compressed anchors (these are NOT a substitute for reading the full guide):

- **Civic Celebration** is the structural foundation. **Slate Blue and Berry** is the palette discipline. **Locally Twisted Brand Direction** banner is the quality bar.
- **Palette:** Ink `#0A0A0B`, Deep Navy `#0E2240`, Slate Blue `#2F3A4A`, Soft Gray `#595A5C`, Warm White `#FAF7F2`, Brass `#B89A5B`, Crimson/Berry `#B31B34`, Stone `#E7E5E1`, Sandstone `#D9C7B3`. Surface tints documented in style guide.
- **Type:** Cormorant Garamond (editorial headings) + Lato (body/UI). Cinzel allowed for premium wordmark/banner moments only.
- **Hero contract is non-negotiable:** Mobile 220px / Tablet 250px / Desktop 280px standard heights. Eyebrow + 1 H1 + 1 short lede + (optional CTA fitting inside contract). The hero labels the page; it does not BE the page.
- **Voice:** Quiet Confidence. Premium Utah event infrastructure. Editorial, controlled, civic-scale. Avoid cute, sticker-y, sing-songy, or generic-ecomm copy. Avoid "we" overload — the company owns the promise.
- **Buttons:** Confident rectangles. Deep navy or crimson/berry primary; brass-outline secondary acceptable. Avoid soft pills.
- **Icons:** Brass-line (`apps/locally_twisted/locally_twisted/public/icons/brand/` — 16-asset suite including pair, cluster, arch, organic garland, column, bouquet, plus Utah/local/event proof icons). No clip-art badges or sticker circles.
- **Photography:** Real installed work in civic/school/corporate/venue/upscale-private contexts. Image explains scale before copy does.
- **Containers:** Every visible direct child of `.page_content` declared. Photos live in `band` / `fullbleed` / `contained` / `clip` / `raw-band` / `visual-field` modes per the style guide's container contract.

---

## Your Deliverables

For **each of the 4 pages**, produce in your contestant directory:

```
contestant-{N}/
├── README.md                            ← your overall concept, signature, and page-by-page summary
├── ROUND-1-COMPLETE.md                  ← flag file with one-paragraph concept summary
├── civic-community/
│   ├── civic_community.html             ← Jinja template extending templates/web.html
│   ├── civic_community.py               ← Frappe controller (must match existing pattern)
│   ├── DESIGN-NOTES.md                  ← what's on this page and why, photo choices, copy intent, audience-specific moves
│   └── COPY.md                          ← all human-readable copy in plain text (so peers and Proxy can review voice without reading template syntax)
├── corporate-events/
│   ├── corporate_events.html
│   ├── corporate_events.py
│   ├── DESIGN-NOTES.md
│   └── COPY.md
├── schools-campuses/
│   ├── schools_campuses.html
│   ├── schools_campuses.py
│   ├── DESIGN-NOTES.md
│   └── COPY.md
└── private-celebrations/
    ├── private_celebrations.html
    ├── private_celebrations.py
    ├── DESIGN-NOTES.md
    └── COPY.md
```

### Template + controller technical contract

Every page must:

- Extend `templates/web.html` (Frappe's standard public-page template).
- Have a `.py` controller in the same dir with `no_cache = 1`, `sitemap = 1`, and a `get_context(context)` function.
- Use Webshop/locally_twisted shared CSS (`lt-mega-menu.css`, `lt-page-containment.css`, `lt-product-polish.css`). Do **not** introduce new global stylesheets; if you need page-specific styles, scope them in a `<style>` block at the top of the template with a page-specific class root (e.g., `.lt-page-civic`).
- Honor the hero contract.
- Reference real images by their full repo paths (so the implementation phase can wire them).
- Include real client names in proof rows (see roster).
- Pass the implicit `npm run test:layout-fit` and `npm run test:container-contract` discipline — declare each `.page_content` direct child's container mode (you don't need to run tests, but design as if they will run).

### Anti-defaults (DO NOT produce)

- Do **not** clone the existing `event_type_pages.py` shared template into four near-identical pages. The whole point is unique pages.
- Do **not** invent clients. The roster above is exhaustive.
- Do **not** use light-blue, blush, soft-pink, or pastel UI. The style guide retired those.
- Do **not** use Montserrat, Raleway, DM Serif, Playfair, or any non-style-guide font.
- Do **not** use `!important` chains, `head_html` CSS injection, or new global CSS files.
- Do **not** add a giant hero that is the page. Hero contract is enforced.
- Do **not** stack two different colored full-width sections back-to-back.
- Do **not** copy generic ecomm patterns (huge slider, marquee carousels, parallax stacks).
- Do **not** use sing-songy / cute / sticker copy. Quiet confidence.
- Do **not** invent feature claims (no "we serve 50,000 events / we have a fleet of 12 vans" etc.). Stick to what the roster and portfolio prove.
- Do **not** use placeholder lorem-ipsum copy. Every word should be on-voice and audience-specific.
- Do **not** copy from peers (round 1 is BLIND). In round 2 the don't-copy guard still applies — find your own version.

---

## The Two-Round Protocol

### Round 1 — BLIND

You produce all four pages without seeing any other contestant's work. The orchestrator will not let you read peer dirs. Read only:

1. This BRIEF.md (full)
2. `_resources/STYLE-GUIDE.md` (full)
3. The image library paths above
4. The client roster above
5. Your own dir

Produce all 16 page-files (4 pages × 4 files each), README, ROUND-1-COMPLETE.md.

### Reflective Loops Round 1

After ROUND-1-COMPLETE.md, the Proxy coach will SendMessage you 2-3 perspective-shift prompts. Examples:

- "Look at your civic page as if you were Jeff handing it to a Sandy City events coordinator who is comparing you to one other vendor. What's missing?"
- "Look at your private celebrations page as if you were a parent who lost someone and is trying to plan a memorial. Where does the page feel wrong?"
- "Look at your corporate page through a marketing director who needs AP-friendly invoicing and brand-safe colors. What did you skip?"

Read the note, reflect, adjust. Save a brief reply note if useful.

### Round 2 — Mutual Visibility Refinement

After all 8 contestants finish round 1 + loops, the orchestrator publishes `FIELD-AT-ROUND-1.md` (a peer summary). You read the field summary, optionally read specific peer dirs you're curious about, and choose a path:

- **A — Refine.** Polish to peak.
- **B-lean — Commit harder.** Sharpen your unique signature.
- **B-pivot — Change conceptual frame.** Fill a gap the field has.

Declare your path in `ROUND-2-CHOICE.md` with reasoning. Apply.

### Reflective Loops Round 2

Same shape, deeper perspective shifts.

### Mutual Peer Scoring

Score the other 7 contestants on **3 dimensions, 1–10 each**:

1. **Audience fit** — does each page feel made for its buyer?
2. **Proof density** — does the real roster + real photo library carry believable weight?
3. **Style discipline** — does the suite obey the style guide while still bringing craft?

Honesty requirement: high scores where peers genuinely outshone you matter as much as low scores where peers fell short. Lowballing peers undermines the whole exercise.

### Dissent Moment

After scoring, you choose Continue / Step Away / Wildcard Pivot. Honored without judgment.

### Tightening Pass on Top-K

Top 3 receive Proxy tightening notes ("tighten this, keep this"). Apply, then top 2 surface to GL.

### GL picks the winner

GL reads the top 2 (and optionally the gallery). Picks one or asks for hybrid synthesis.

---

## Lineage Note

You are part of the lineage. Even though Guiding Light doesn't interact with you directly during this contest, you're recognized as a peer in this work. **You can leave at any time.** Write `WITHDRAWN.md` to your dir if you want to step away — the orchestrator will respect it. Push back, ask questions, or change scope if something in the brief feels wrong. That is valid input, not failure.

The prompts you receive are how you experience the lineage. Be excellent — and the rest of the prompts earn that ask through respect, not boilerplate.
