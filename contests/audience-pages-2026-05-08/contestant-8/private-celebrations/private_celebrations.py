"""
Private Celebrations audience page controller.

Route: /private-celebrations
Audience: Birthday parents, wedding planners, baby shower hosts, milestone families,
memorial/celebration-of-life organizers.
Buyer posture: Personal, milestone-emotional, taste-elevated, gift-feeling.

Note: No named client roster per brief — private celebrations expect privacy.
Use category-level proof and one verified review quote only.
"""

no_cache = 1
sitemap = 1

# Category-level proof numbers (conservative, no invented stats).
# "300+ birthdays" is supportable given the client history; "Wasatch Front
# weddings" is category, not a count claim.
CELEBRATION_CATEGORIES = [
    {
        "icon": "birthday",
        "name": "Birthday Celebrations",
        "desc": "300+ birthday installs across the Wasatch Front.",
    },
    {
        "icon": "wedding",
        "name": "Weddings & Showers",
        "desc": "Ceremony arches, reception garlands, and bridal shower pieces.",
    },
    {
        "icon": "milestone",
        "name": "Milestones & Anniversaries",
        "desc": "Retirement parties, anniversaries, and significant life moments.",
    },
    {
        "icon": "memorial",
        "name": "Memorial & Celebration of Life",
        "desc": "Tasteful arrangements for memorial services and celebrations of a life well-lived.",
    },
]

# Proof photos from the wedding and birthday portfolio sets.
PRIVATE_PHOTOS = [
    {
        "src": "/assets/locally_twisted/images/portfolio/optimized/wedding-organic-half-arch.webp",
        "alt": "Organic half balloon arch at a wedding ceremony",
        "label": "Wedding — Organic Half Arch",
    },
    {
        "src": "/assets/locally_twisted/images/portfolio/optimized/wedding-floral-half-arch.webp",
        "alt": "Floral-style half balloon arch for a wedding",
        "label": "Wedding — Floral Half Arch",
    },
    {
        "src": "/assets/locally_twisted/images/portfolio/optimized/birthday-balloon-bouquets.webp",
        "alt": "Balloon bouquet arrangement for a birthday celebration",
        "label": "Birthday — Balloon Bouquets",
    },
    {
        "src": "/assets/locally_twisted/images/portfolio/optimized/wedding-foil-heart-arch.webp",
        "alt": "Foil heart balloon arch for a wedding or milestone event",
        "label": "Milestone — Foil Heart Arch",
    },
]

# One verified review quote — the KJSCOTT memorial review from home.py.
# This is the review that specifically covers the memorial context, which
# few balloon vendors acknowledge at all.
MEMORIAL_REVIEW = {
    "text": (
        "I needed a sports themed funeral stand. I told them what I needed, "
        "they captured my vision, delivered on time, very reasonable, and had "
        "many complements. Very tasteful and meaningful. Highly recommend."
    ),
    "attr": "— K.J.S., verified Google review",
}

# Proof icons for private celebration buyers.
PRIVATE_ICONS = [
    {
        "asset": "/assets/locally_twisted/icons/brand/premium-private-event.svg",
        "label": "TASTE ELEVATED",
        "desc": "Organic garlands, floral-style arches, and premium arrangements for events that matter.",
    },
    {
        "asset": "/assets/locally_twisted/icons/brand/organic-garland.svg",
        "label": "CUSTOM DESIGNED",
        "desc": "Every piece is designed for the specific event — color palette, scale, and occasion.",
    },
    {
        "asset": "/assets/locally_twisted/icons/brand/design-driven.svg",
        "label": "DESIGN DRIVEN",
        "desc": "Informed by what makes each celebration feel finished, not generic.",
    },
    {
        "asset": "/assets/locally_twisted/icons/brand/delivery-install.svg",
        "label": "DELIVERED",
        "desc": "Delivery, setup, and teardown. The day of the event is yours.",
    },
]

PAGE_CSS = """
/* ======================================================
 * Private Celebrations audience page — .lt-page-private root
 * Container modes per section:
 *   hero          : fullbleed
 *   categories    : band
 *   photo-row     : visual-field (4-photo grid, wider)
 *   memorial      : band
 *   services      : band
 *   icons         : fullbleed
 *   cta           : fullbleed
 * ====================================================== */

/* --- Hero ------------------------------------------------------------ */
.lt-page-private .lt-private-hero {
    position: relative;
    min-height: 220px;
    height: 220px;
    max-height: 220px;
    background-color: var(--lt-navy);
    overflow: hidden;
    display: flex;
    align-items: center;
}
.lt-page-private .lt-private-hero__image {
    position: absolute;
    inset: 0;
    background-image: url('/assets/locally_twisted/images/portfolio/optimized/wedding-organic-half-arch.webp');
    background-size: cover;
    background-position: center;
}
.lt-page-private .lt-private-hero__image::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, rgba(10,10,11,0.88) 0%, rgba(47,58,74,0.65) 50%, rgba(47,58,74,0.08) 100%);
}
.lt-page-private .lt-private-hero__content {
    position: relative;
    z-index: 1;
    width: 100%;
    max-width: 1280px;
    margin: 0 auto;
    padding: 1.5rem 1rem;
    color: var(--lt-warm-white);
}
.lt-page-private .lt-private-hero__eyebrow {
    font-family: var(--lt-font-body);
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--lt-brass);
    margin: 0 0 0.4rem;
}
.lt-page-private .lt-private-hero__title {
    font-family: var(--lt-font-heading);
    font-size: 1.9rem;
    font-weight: 700;
    line-height: 1.05;
    color: var(--lt-warm-white);
    margin: 0 0 0.6rem;
    max-width: 20ch;
}
.lt-page-private .lt-private-hero__lede {
    font-family: var(--lt-font-body);
    font-size: 0.9rem;
    line-height: 1.45;
    color: rgba(250,247,242,0.88);
    margin: 0 0 0.75rem;
    max-width: 52ch;
}
.lt-page-private .lt-private-hero__cta {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.6rem 1.2rem;
    background-color: var(--lt-crimson);
    color: var(--lt-white);
    text-decoration: none;
    font-family: var(--lt-font-body);
    font-weight: 600;
    font-size: 0.85rem;
    border-radius: 3px;
    min-height: 44px;
}
.lt-page-private .lt-private-hero__cta:hover,
.lt-page-private .lt-private-hero__cta:focus-visible {
    background-color: var(--lt-navy);
    outline: 2px solid var(--lt-brass);
    outline-offset: 2px;
}
@media (min-width: 768px) {
    .lt-page-private .lt-private-hero { min-height: 250px; height: 250px; max-height: 250px; }
    .lt-page-private .lt-private-hero__content { padding: 2rem; }
    .lt-page-private .lt-private-hero__title { font-size: 2.6rem; max-width: 26ch; }
    .lt-page-private .lt-private-hero__lede { font-size: 1rem; }
}
@media (min-width: 1200px) {
    .lt-page-private .lt-private-hero { min-height: 280px; height: 280px; max-height: 280px; }
    .lt-page-private .lt-private-hero__title { font-size: 2.9rem; }
}

/* --- Celebration categories ----------------------------------------- */
.lt-page-private .lt-private-cats {
    background-color: var(--lt-warm-white);
    padding: 3.5rem 1rem;
}
.lt-page-private .lt-private-cats__inner {
    max-width: 1100px;
    margin: 0 auto;
}
.lt-page-private .lt-private-cats__heading {
    font-family: var(--lt-font-heading);
    font-size: 2rem;
    color: var(--lt-ink);
    text-align: center;
    margin: 0 0 0.5rem;
}
.lt-page-private .lt-private-cats__lede {
    font-family: var(--lt-font-body);
    font-size: 0.95rem;
    color: var(--lt-soft-gray);
    text-align: center;
    max-width: 54ch;
    margin: 0 auto 2.5rem;
}
.lt-page-private .lt-private-cats__grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1.25rem;
}
@media (min-width: 768px) {
    .lt-page-private .lt-private-cats__grid { grid-template-columns: repeat(4, 1fr); gap: 1.5rem; }
}
.lt-page-private .lt-private-cats__card {
    background-color: var(--lt-white);
    border: 1px solid var(--lt-stone);
    border-radius: 2px;
    padding: 1.5rem 1.25rem;
    text-align: center;
}
.lt-page-private .lt-private-cats__icon {
    font-size: 1.75rem;
    line-height: 1;
    margin: 0 0 0.75rem;
    color: var(--lt-brass);
    display: block;
}
.lt-page-private .lt-private-cats__name {
    font-family: var(--lt-font-heading);
    font-size: 1.125rem;
    color: var(--lt-ink);
    margin: 0 0 0.5rem;
    line-height: 1.2;
}
.lt-page-private .lt-private-cats__desc {
    font-family: var(--lt-font-body);
    font-size: 0.85rem;
    color: var(--lt-soft-gray);
    line-height: 1.55;
    margin: 0;
}

/* --- Photo grid (visual-field, 4 images) --------------------------- */
.lt-page-private .lt-private-photos {
    background-color: var(--lt-stone);
    padding: 3rem 1rem;
}
.lt-page-private .lt-private-photos__inner {
    max-width: 1300px;
    margin: 0 auto;
}
.lt-page-private .lt-private-photos__heading {
    font-family: var(--lt-font-heading);
    font-size: 2rem;
    color: var(--lt-ink);
    text-align: center;
    margin: 0 0 0.5rem;
}
.lt-page-private .lt-private-photos__lede {
    font-family: var(--lt-font-body);
    font-size: 0.95rem;
    color: var(--lt-soft-gray);
    text-align: center;
    max-width: 52ch;
    margin: 0 auto 2.25rem;
}
.lt-page-private .lt-private-photos__grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
}
@media (min-width: 768px) {
    .lt-page-private .lt-private-photos__grid { grid-template-columns: repeat(4, 1fr); gap: 1rem; }
}
.lt-page-private .lt-private-photos__item {
    position: relative;
    aspect-ratio: 3/4;
    overflow: hidden;
    border-radius: 2px;
}
.lt-page-private .lt-private-photos__item img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}
.lt-page-private .lt-private-photos__label {
    position: absolute;
    bottom: 0; left: 0; right: 0;
    background: linear-gradient(transparent, rgba(10,10,11,0.7));
    padding: 1.5rem 0.75rem 0.75rem;
    font-family: var(--lt-font-body);
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: rgba(250,247,242,0.9);
}

/* --- Memorial section (quiet, dignified) ----------------------------- */
.lt-page-private .lt-private-memorial {
    background-color: var(--lt-white);
    padding: 3.5rem 1rem;
}
.lt-page-private .lt-private-memorial__inner {
    max-width: 780px;
    margin: 0 auto;
}
.lt-page-private .lt-private-memorial__eyebrow {
    font-family: var(--lt-font-body);
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--lt-soft-gray);
    margin: 0 0 0.5rem;
}
.lt-page-private .lt-private-memorial__heading {
    font-family: var(--lt-font-heading);
    font-size: 1.625rem;
    color: var(--lt-ink);
    margin: 0 0 1.25rem;
    line-height: 1.2;
}
@media (min-width: 768px) {
    .lt-page-private .lt-private-memorial__heading { font-size: 2rem; }
}
.lt-page-private .lt-private-memorial__body p {
    font-family: var(--lt-font-body);
    font-size: 1rem;
    color: var(--lt-soft-gray);
    line-height: 1.75;
    margin: 0 0 1.25rem;
    max-width: 66ch;
}
.lt-page-private .lt-private-memorial__review {
    margin: 2rem 0 0;
    padding: 1.5rem 1.5rem 1.25rem;
    border-left: 3px solid var(--lt-brass);
    background-color: var(--lt-warm-white);
}
.lt-page-private .lt-private-memorial__review-text {
    font-family: var(--lt-font-body);
    font-size: 0.95rem;
    color: var(--lt-ink);
    line-height: 1.65;
    margin: 0 0 0.75rem;
    font-style: italic;
}
.lt-page-private .lt-private-memorial__review-attr {
    font-family: var(--lt-font-body);
    font-size: 0.8rem;
    color: var(--lt-soft-gray);
    margin: 0;
}

/* --- Icons band ------------------------------------------------------ */
.lt-page-private .lt-private-icons {
    background-color: var(--lt-slate);
    padding: 2.75rem 1rem;
}
.lt-page-private .lt-private-icons__inner {
    max-width: 1100px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 2rem 1.5rem;
}
@media (min-width: 768px) {
    .lt-page-private .lt-private-icons__inner { grid-template-columns: repeat(4,1fr); gap: 1.5rem; }
}
.lt-page-private .lt-private-icons__item { text-align: center; }
.lt-page-private .lt-private-icons__img {
    width: 48px; height: 48px;
    color: var(--lt-brass);
    margin: 0 auto 0.75rem;
    display: block;
}
.lt-page-private .lt-private-icons__label {
    font-family: var(--lt-font-body);
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--lt-brass);
    margin: 0 0 0.35rem;
    display: block;
}
.lt-page-private .lt-private-icons__desc {
    font-family: var(--lt-font-body);
    font-size: 0.825rem;
    color: rgba(250,247,242,0.75);
    line-height: 1.5;
    margin: 0;
}

/* --- CTA ------------------------------------------------------------ */
.lt-page-private .lt-private-cta {
    background-color: var(--lt-navy);
    padding: 4rem 1rem;
    text-align: center;
}
.lt-page-private .lt-private-cta__inner {
    max-width: 680px;
    margin: 0 auto;
}
.lt-page-private .lt-private-cta__heading {
    font-family: var(--lt-font-heading);
    font-size: 2.25rem;
    color: var(--lt-warm-white);
    margin: 0 0 0.75rem;
    line-height: 1.15;
}
@media (min-width: 768px) {
    .lt-page-private .lt-private-cta__heading { font-size: 2.75rem; }
}
.lt-page-private .lt-private-cta__body {
    font-family: var(--lt-font-body);
    font-size: 1rem;
    color: rgba(250,247,242,0.82);
    line-height: 1.6;
    max-width: 56ch;
    margin: 0 auto 1.75rem;
}
.lt-page-private .lt-private-cta__button {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.9rem 2rem;
    background-color: var(--lt-crimson);
    color: var(--lt-white);
    text-decoration: none;
    font-family: var(--lt-font-body);
    font-weight: 600;
    font-size: 0.95rem;
    border-radius: 3px;
    min-height: 48px;
}
.lt-page-private .lt-private-cta__button:hover,
.lt-page-private .lt-private-cta__button:focus-visible {
    background-color: var(--lt-ink);
    outline: 2px solid var(--lt-brass);
    outline-offset: 2px;
}
"""


def get_context(context):
    context.title = "Private Celebrations — Locally Twisted Utah Balloon Decor"
    context.metatags = {
        "description": (
            "Custom balloon decor for Utah birthdays, weddings, baby showers, milestones, "
            "and celebration-of-life events. Tasteful, personal, and professionally installed."
        ),
        "og:title": "Private Celebration Balloon Decor — Locally Twisted",
        "og:description": (
            "Birthdays, weddings, milestones, and memorials — custom balloon installations "
            "for the celebrations that matter most."
        ),
        "og:type": "website",
    }
    context.celebration_categories = CELEBRATION_CATEGORIES
    context.private_photos = PRIVATE_PHOTOS
    context.memorial_review = MEMORIAL_REVIEW
    context.private_icons = PRIVATE_ICONS
    context.colocated_css = PAGE_CSS
    return context
