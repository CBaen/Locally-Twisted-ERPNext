# Contestant 4 — Audience Pages Suite

## Concept: One System, Four Buyers

The four pages share a single underlying structure but each diverges in ways that reflect its buyer. The suite is recognizably the same brand; the pages are not the same page.

## Signature Moves

**1. Buyer-specific hero copy and images**
Each hero leads with the buyer's own event type. Civic: rainbow columns. Corporate: branded arch. Schools: back-to-school stage. Private: organic wedding arch. The buyer lands and sees their own world immediately.

**2. Color system disciplined across all four**
Every page uses the approved palette without pastels or custom colors. The one intentional variation: `/private-celebrations` uses Sandstone (#D9C7B3) for the testimonials band — it's in the approved palette as "warm section separation" and the emotional context earns it. The other three pages use Stone (#E7E5E1).

**3. Proof pillars re-authored per buyer**
Each page has 4 proof pillars from the approved icon suite, but the pillar body text is written specifically for that buyer's concern. A city events coordinator and a marketing director and an activity director all care about different things. The pillars say different things.

**4. Roster treatment scaled to actual roster depth**
- Civic: 26-item chip list (full roster)
- Corporate: 30-item chip list (full roster)
- Schools: Named-relationship chips with context labels (roster is intentionally short — per brief, don't pad)
- Private: No roster (privacy) — replaced with testimonials from real Google reviews

**5. Testimonials section on private celebrations only**
The private buyer makes decisions on peer trust, not a client logo list. The testimonials section on `/private-celebrations` uses real Google reviews from `home.py` — the memorial testimonial (sports-themed funeral stand) is placed deliberately because it's the most emotionally resonant proof in the entire review set.

**6. Service note per audience**
Each page's service note explains how the process works for that specific buyer:
- Civic: coordinated install windows, insurance docs, city time
- Corporate: AP-invoiceable, color matching, latex-free for healthcare
- Schools: school calendar, exact color matching, facility access
- Private: how to start, latex-free, same-day option with phone

**7. No `!important`, no global CSS, no injected styles**
All CSS is scoped in a `<style>` block with a page-specific root class. No cross-page contamination.

## Page-by-Page Summary

| Route | Hero Image | Sections | Client Roster | Proof Style |
|---|---|---|---|---|
| `/civic-community` | Pride columns | 8 | 26 chip list | Case studies (3, named clusters) |
| `/corporate-events` | Logo arch | 8 | 30 chip list | Case studies (3, named clusters) |
| `/schools-campuses` | Back-to-school stage | 7 | 5 named chips | Moment cards (3) |
| `/private-celebrations` | Wedding organic arch | 7 | None (privacy) | Category cards (4) + testimonials |

## Technical Notes

- All templates extend `templates/web.html`
- All controllers use `no_cache = 1`, `sitemap = 1`, and `get_context(context)`
- CSS: scoped `<style>` blocks, page-specific root classes (`.lt-page-civic`, `.lt-page-corp`, `.lt-page-school`, `.lt-page-priv`)
- No new global stylesheets
- Hero contract honored: mobile 220px / tablet 250px / desktop 280px
- Container modes declared for all `.page_content` direct children
- All Odoo-source images referenced by full Windows path — implementation phase handles file copy
- CTAs: `/contact?intent={civic|corporate|school|private}` — prefills inquiry context
- Accessibility: one H1 per page, heading hierarchy observed, `aria-hidden` on decorative images, gallery `aria-label`, min 44px touch targets

## Anti-Defaults Compliance

- ✅ No light-blue, blush, soft-pink, or pastel UI
- ✅ No Montserrat, Raleway, or non-guide fonts
- ✅ No `!important`
- ✅ No `head_html` injection
- ✅ No new global CSS files
- ✅ Hero contract enforced (220/250/280px)
- ✅ No two adjacent full-width colored sections
- ✅ No lorem ipsum
- ✅ No invented clients
- ✅ No generic ecomm patterns (no sliders, no marquee carousels)
- ✅ Quiet confidence voice throughout
