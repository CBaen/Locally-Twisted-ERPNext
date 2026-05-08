# /private-celebrations — Design Notes

## Audience

Birthday parents, wedding planners, baby shower hosts, milestone families, and memorial/celebration-of-life organizers. Buyer posture: personal, milestone-emotional, taste-elevated, gift-feeling.

Key difference from the other three pages: there is NO named-client roster. This is by design — private celebrations expect privacy. The page proves capability through category-level proof ("300+ birthday installs"), anonymized review quotes, and real portfolio photography. No invented numbers, no inflated claims.

## The Core Design Decision: Warmer, Not Softer

Private celebrations deserve a warmer page than civic or corporate, but NOT a pastel/balloon-party-flyer page. The risk here is sliding into the anti-defaults (cute, sticker-y, sing-songy). The solution:

- Use Sandstone (#D9C7B3) for the testimonials band — it's in the approved palette as "warm section separation and secondary soft backgrounds" — instead of Stone (#E7E5E1). This creates warmth without pastels.
- Hero image: `wedding-organic-half-arch.webp` — elegant, personal, organic form — not a birthday balloon cluster
- CTA copy: "Tell us what you're imagining." — the most personal, warm CTA on any of the four pages, and explicitly on-voice per the style guide's copy examples.
- Testimonials placed prominently (not buried at the bottom) — private buyers make decisions based on peer trust

## Structure (7 sections)

1. Hero — fullbleed, wedding arch photo, most personal of the four hero copies
2. Celebration types — 4-card grid, each card = a celebration category (no named clients)
3. Gallery strip — visual-field, 6 photos from birthday + wedding portfolio
4. Proof pillars — slate blue, 4 pillars designed for a milestone buyer
5. Testimonials — sandstone ground, 4 Google review quotes (real, sourced from home.py)
6. Service note — warm-white, explains how to start + latex-free + same-day option
7. CTA — ink, personal framing

## Celebration Type Cards

The 4-card grid is the structural move that distinguishes this page from the other three. Instead of named-client case studies, we use event-category cards with:
- A real portfolio photo
- A category label (Birthdays, Weddings, Baby Showers, Memorials)
- A category-proof stat ("300+ birthday installs", "Wasatch Front weddings")
- A 2-sentence body explaining the format

Grid layout: 1-col mobile → 2×2 at 600px → 4-wide at 1100px. This is the only page with a 4-across grid at desktop, which suits the category-card format.

"Memorials" is explicitly included. The Google review about the sports-themed funeral stand is one of the most powerful testimonials in the entire review set — this page earns it.

## Testimonials

4 testimonials from the real Google review set in `home.py`. Selected specifically for private-event relevance:
- Wedding (mark Taylor's review)
- Birthday (Sarah Johnston-Powell's review)
- Memorial (KJSCOTT's review — the most emotionally resonant in the entire review set)
- Repeat family client (Tiffiny Lipscomb's review)

Using `<blockquote>` with `<footer>` — semantically correct for testimonials. Sandstone ground creates warmth without being decorative or distracting.

## Gallery

6 images — all birthday and wedding portfolio photos. Every one from the optimized portfolio (WebP, production-ready):
- birthday-smurfs-arch, birthday-dolphin-backdrop, birthday-pirate-column
- wedding-organic-half-arch, wedding-foil-heart-arch, wedding-floral-half-arch

This is the most visually rich gallery of the four pages — the private celebrations portfolio has 6 directly relevant optimized images vs. the other pages needing to pull from Odoo for depth.

## Proof Pillars

On slate blue — slightly less dark than deep navy, appropriate for the warmer personal context. 4 pillars:
- "Milestone-Ready" → emotional weight
- "Design Driven" → custom, not catalog
- "Delivered & Installed" → logistical relief
- "Personal Attention" → Jeff works with you directly

The "Personal Attention" pillar is unique to this page — it's the value proposition that matters most to a private buyer (vs. invoice-ready or civic-scale for other pages).

## Service Note

Explicitly mentions:
- How to start (tell us what you're imagining)
- Latex-free (relevant for wedding/allergy context)
- Same-day option with phone number — private events sometimes happen with short notice

## What This Page Does NOT Do

- Does not name any private clients (privacy — per brief)
- Does not invent numbers ("thousands of weddings", etc.)
- Does not use pastel backgrounds, soft pink UI, or blush tones
- Does not use "magical" or "dream wedding" language
- Does not use clip-art hearts, balloons emojis, or badge circles
- Does not make Memorial/Celebration-of-Life feel clinical or uncomfortable

## Color Pattern Compliance

Warm White → [no rule, direct adjacent sections share warm-white ground, separated by gallery strip] → dark gallery strip → Slate Blue → Sandstone → Warm White → Ink

The Sandstone testimonials section is the designed exception to the normal stone/navy alternation. It replaces a stone band to create warmth for the testimonials section specifically. The style guide permits Sandstone for "warm section separation" — this is an intentional choice, not a rule violation. It's also NOT adjacent to a dark section — gallery (dark) → pillars (slate blue) → testimonials (sandstone) creates a stepdown, not a clash.

## Accessibility

- One H1
- Heading hierarchy: H1 → H2 (types) → H3 (type cards) → H2 (pillars label as `p`, not heading) → H2 (testimonials) → H2 (service note) → H2 (CTA)
- `<blockquote>` with `<footer>` for testimonials — correct semantic structure
- All decorative icons: `aria-hidden="true"`
- All content images: descriptive alt text
- Gallery: `aria-label`
- CTAs: min 44px / 48px
- `prefers-reduced-motion`: gallery hover transition disabled
- Testimonials are screen-reader accessible (blockquote pattern)
