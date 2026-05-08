"""Private Celebrations audience landing page — /private-celebrations

Buyer: Birthday parents, wedding planners, baby shower hosts, milestone families,
memorial/celebration-of-life organizers.

Posture: Personal, milestone-emotional, taste-elevated, gift-feeling.

No named clients — private celebrations expect privacy. Uses category-level proof
and anonymized photo evidence.
"""
import frappe

no_cache = 1
sitemap = 1

PRIVATE_PROOF_STATS = [
    {"icon": "premium-private-event", "label": "PRIVATE EVENTS", "value": "300+", "sub": "Birthday, wedding, shower, milestone, and memorial installs"},
    {"icon": "organic-garland", "label": "DESIGN DRIVEN", "value": "Every Detail", "sub": "Custom color palettes, floral accents, organic textures, and themed forms"},
    {"icon": "delivery-install", "label": "DELIVERED", "value": "To Your Door", "sub": "Setup and strike handled — your space is ready when guests arrive"},
    {"icon": "professional", "label": "TRUSTED", "value": "Wasatch Front", "sub": "Weddings across Utah, from Salt Lake to Ogden to St. George planning"},
]

PRIVATE_EVENT_MOMENTS = [
    {
        "type": "Birthday",
        "desc": "The big round numbers, the milestone years, the surprise parties. Custom arches, themed sculptures, organic backdrops, and photo moments sized for your home, venue, or event space.",
        "photos": [
            {
                "image": "/assets/locally_twisted/images/portfolio/optimized/birthday-smurfs-arch.webp",
                "alt": "Custom Smurfs-themed balloon arch for a birthday party",
            },
            {
                "image": "/assets/locally_twisted/images/portfolio/optimized/birthday-dolphin-backdrop.webp",
                "alt": "Dolphin-themed balloon backdrop for a birthday celebration",
            },
            {
                "image": "/assets/locally_twisted/images/portfolio/optimized/birthday-balloon-bouquets.webp",
                "alt": "Birthday balloon bouquets arrangement",
            },
        ],
    },
    {
        "type": "Weddings",
        "desc": "Half arches at the altar, organic garlands along the head table, foil-heart photo moments, floral-accent columns at the entrance. Color-matched to your florals and palette.",
        "photos": [
            {
                "image": "/assets/locally_twisted/images/portfolio/optimized/wedding-organic-half-arch.webp",
                "alt": "Organic balloon half arch for a wedding ceremony",
            },
            {
                "image": "/assets/locally_twisted/images/portfolio/optimized/wedding-floral-half-arch.webp",
                "alt": "Balloon half arch with floral accents for a wedding",
            },
            {
                "image": "/assets/locally_twisted/images/portfolio/optimized/wedding-foil-heart-arch.webp",
                "alt": "Foil heart balloon arch for a wedding photo moment",
            },
        ],
    },
    {
        "type": "Baby Showers",
        "desc": "Organic garlands, gender-reveal setups, and soft-palette photo moments for the anticipation that deserves something beautiful.",
        "photos": [
            {
                "image": "C:/Users/baenb/projects/locally-twisted-odoo/assets/image assets/photos for website/Organic decor/Organic mothers day decor.png",
                "alt": "Soft organic balloon garland arrangement for a mother-themed celebration",
            },
            {
                "image": "C:/Users/baenb/projects/locally-twisted-odoo/assets/image assets/photos for website/Organic decor/Organic half arch with white flowers.png",
                "alt": "Organic balloon half arch with white flower accents",
            },
            {
                "image": "C:/Users/baenb/projects/locally-twisted-odoo/assets/image assets/photos for website/Organic decor/organic column white flower add-ons.png",
                "alt": "Organic balloon column with white flower accents",
            },
        ],
    },
    {
        "type": "Milestones & Memorials",
        "desc": "Retirements, anniversary years, celebration-of-life gatherings. Balloon decor can carry weight when it needs to — tasteful, considered, and built around what matters to the people in that room.",
        "photos": [
            {
                "image": "C:/Users/baenb/projects/locally-twisted-odoo/assets/image assets/photos for website/Organic decor/Organic step and repeat.png",
                "alt": "Organic balloon step and repeat backdrop for a milestone event",
            },
            {
                "image": "C:/Users/baenb/projects/locally-twisted-odoo/assets/image assets/photos for website/Organic decor/30_ Celebrate arch.png",
                "alt": "Celebrate balloon arch for a milestone celebration",
            },
            {
                "image": "C:/Users/baenb/projects/locally-twisted-odoo/assets/image assets/photos for website/Photo opts/Celebrate backdrop.png",
                "alt": "Celebrate balloon photo backdrop",
            },
        ],
    },
]

PRIVATE_QUOTE_NOTES = [
    "No minimum order size — a single arch or a full-room install, both get quoted.",
    "Color matching from your Pinterest board, florist palette, or venue swatches.",
    "Delivery and setup included in all private event quotes.",
    "Photo-moment setups built for your phone camera, not just professional photography.",
    "Memorial and celebration-of-life installs handled with full discretion.",
]

PAGE_CSS = """
/* ====================================================================
 * Private Celebrations page — .lt-page-private scoped
 * Container modes:
 *   hero=fullbleed, stats=fullbleed, event-sections=band,
 *   quote-notes=contained, cta=fullbleed
 * ==================================================================== */

/* --- hero ----------------------------------------------------------- */
.lt-page-private .lt-private-hero {
    position: relative;
    height: 220px;
    min-height: 220px;
    max-height: 220px;
    background-color: var(--lt-ink);
    overflow: hidden;
    display: flex;
    align-items: center;
}
.lt-page-private .lt-private-hero__bg {
    position: absolute;
    inset: 0;
    background-image: url('/assets/locally_twisted/images/portfolio/optimized/wedding-organic-half-arch.webp');
    background-size: cover;
    background-position: center right;
}
.lt-page-private .lt-private-hero__bg::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, rgba(10,10,11,0.92) 0%, rgba(10,10,11,0.72) 42%, rgba(10,10,11,0.14) 100%);
}
.lt-page-private .lt-private-hero__content {
    position: relative;
    z-index: 1;
    width: 100%;
    max-width: 1280px;
    margin: 0 auto;
    padding: 1.5rem 1rem;
}
.lt-page-private .lt-private-hero__eyebrow {
    font-family: var(--lt-font-body);
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--lt-brass);
    margin: 0 0 0.35rem;
}
.lt-page-private .lt-private-hero__h1 {
    font-family: var(--lt-font-heading);
    font-size: clamp(1.75rem, 4.5vw, 2.2rem);
    font-weight: 700;
    color: var(--lt-white);
    margin: 0 0 0.45rem;
    max-width: 22ch;
    line-height: 1.05;
}
.lt-page-private .lt-private-hero__lede {
    font-family: var(--lt-font-body);
    font-size: 0.9rem;
    color: rgba(250,247,242,0.88);
    margin: 0 0 0.75rem;
    max-width: 48ch;
    line-height: 1.4;
}
.lt-page-private .lt-private-hero__cta {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.6rem 1.1rem;
    background-color: var(--lt-crimson);
    color: var(--lt-white);
    text-decoration: none;
    font-family: var(--lt-font-body);
    font-weight: 700;
    font-size: 0.85rem;
    border-radius: 2px;
    min-height: 44px;
}
.lt-page-private .lt-private-hero__cta:hover,
.lt-page-private .lt-private-hero__cta:focus-visible {
    background-color: var(--lt-navy);
    outline: 2px solid var(--lt-brass);
    outline-offset: 2px;
}
@media (min-width: 768px) {
    .lt-page-private .lt-private-hero { height: 250px; min-height: 250px; max-height: 250px; }
    .lt-page-private .lt-private-hero__content { padding: 2rem; }
    .lt-page-private .lt-private-hero__h1 { font-size: 2.6rem; }
}
@media (min-width: 1200px) {
    .lt-page-private .lt-private-hero { height: 280px; min-height: 280px; max-height: 280px; }
}

/* --- stats --------------------------------------------------------- */
.lt-page-private .lt-private-stats {
    background-color: var(--lt-ink);
    padding: 2.5rem 1.25rem;
    border-top: 1px solid rgba(184,154,91,0.2);
}
.lt-page-private .lt-private-stats__inner {
    max-width: 1200px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem 1rem;
}
@media (min-width: 768px) {
    .lt-page-private .lt-private-stats__inner {
        grid-template-columns: repeat(4, 1fr);
        gap: 1.5rem;
    }
}
.lt-page-private .lt-private-stat {
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
}
.lt-page-private .lt-private-stat__icon {
    width: 44px;
    height: 44px;
    color: var(--lt-brass);
}
.lt-page-private .lt-private-stat__label {
    font-family: var(--lt-font-body);
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--lt-brass);
}
.lt-page-private .lt-private-stat__value {
    font-family: var(--lt-font-heading);
    font-size: 1.625rem;
    color: var(--lt-white);
    line-height: 1.1;
}
.lt-page-private .lt-private-stat__sub {
    font-family: var(--lt-font-body);
    font-size: 0.78rem;
    color: rgba(250,247,242,0.58);
    line-height: 1.3;
    max-width: 18ch;
}

/* --- event moment blocks (alternating rhythm) -------------------- */
.lt-page-private .lt-private-moments {
    background-color: var(--lt-warm-white);
    padding: 4rem 1.25rem;
}
.lt-page-private .lt-private-moments__inner {
    max-width: 1200px;
    margin: 0 auto;
}
.lt-page-private .lt-private-moment {
    padding: 3rem 0;
    border-bottom: 1px solid var(--lt-stone);
}
.lt-page-private .lt-private-moment__rule {
    border: none;
    border-top: 1px solid var(--lt-stone);
    margin: 0;
    opacity: 0.5;
}
.lt-page-private .lt-private-moment:last-child {
    border-bottom: none;
    padding-bottom: 0;
}
.lt-page-private .lt-private-moment:first-child {
    padding-top: 0;
}
@media (min-width: 768px) {
    .lt-page-private .lt-private-moment__inner {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 3rem;
        align-items: center;
    }
    .lt-page-private .lt-private-moment:nth-child(even) .lt-private-moment__photos {
        order: -1;
    }
}
.lt-page-private .lt-private-moment__type {
    font-family: var(--lt-font-body);
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--lt-crimson);
    margin: 0 0 0.5rem;
}
.lt-page-private .lt-private-moment__heading {
    font-family: var(--lt-font-heading);
    font-size: 1.875rem;
    color: var(--lt-ink);
    margin: 0 0 1rem;
    line-height: 1.15;
}
.lt-page-private .lt-private-moment__desc {
    font-family: var(--lt-font-body);
    font-size: 1rem;
    color: var(--lt-soft-gray);
    margin: 0 0 1.5rem;
    line-height: 1.65;
    max-width: 52ch;
}
.lt-page-private .lt-private-moment__cta-link {
    font-family: var(--lt-font-body);
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--lt-navy);
    text-decoration: none;
    border-bottom: 1px solid var(--lt-brass);
    padding-bottom: 0.1rem;
}
.lt-page-private .lt-private-moment__cta-link:hover,
.lt-page-private .lt-private-moment__cta-link:focus-visible {
    color: var(--lt-crimson);
    border-bottom-color: var(--lt-crimson);
}
.lt-page-private .lt-private-moment__photos {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.6rem;
}
.lt-page-private .lt-private-moment__photos .lt-private-photo:first-child {
    grid-column: 1 / -1;
}
.lt-page-private .lt-private-photo {
    overflow: hidden;
    border-radius: 3px;
    background-color: var(--lt-stone);
}
.lt-page-private .lt-private-moment__photos .lt-private-photo:first-child {
    aspect-ratio: 16/9;
}
.lt-page-private .lt-private-moment__photos .lt-private-photo:not(:first-child) {
    aspect-ratio: 4/3;
}
.lt-page-private .lt-private-photo img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}

/* --- quote notes --------------------------------------------------- */
.lt-page-private .lt-private-notes {
    background-color: var(--lt-navy);
    padding: 3rem 1.25rem;
}
.lt-page-private .lt-private-notes__inner {
    max-width: 1200px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 1fr;
    gap: 2rem;
}
@media (min-width: 768px) {
    .lt-page-private .lt-private-notes__inner {
        grid-template-columns: 1fr 2fr;
        gap: 3rem;
        align-items: center;
    }
}
.lt-page-private .lt-private-notes__heading {
    font-family: var(--lt-font-heading);
    font-size: 1.75rem;
    color: var(--lt-white);
    margin: 0;
    line-height: 1.2;
}
.lt-page-private .lt-private-notes__list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}
.lt-page-private .lt-private-notes__item {
    display: flex;
    gap: 0.75rem;
    align-items: flex-start;
    font-family: var(--lt-font-body);
    font-size: 0.9rem;
    color: rgba(250,247,242,0.82);
    line-height: 1.5;
}
.lt-page-private .lt-private-notes__item::before {
    content: '';
    display: block;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background-color: var(--lt-brass);
    margin-top: 0.5rem;
    flex-shrink: 0;
}

/* --- CTA ------------------------------------------------------------ */
.lt-page-private .lt-private-cta {
    background-color: var(--lt-sandstone);
    padding: 4rem 1.25rem;
    text-align: center;
}
.lt-page-private .lt-private-cta__inner {
    max-width: 680px;
    margin: 0 auto;
}
.lt-page-private .lt-private-cta__heading {
    font-family: var(--lt-font-heading);
    font-size: 2.25rem;
    color: var(--lt-ink);
    margin: 0 0 0.75rem;
    line-height: 1.1;
}
.lt-page-private .lt-private-cta__body {
    font-family: var(--lt-font-body);
    font-size: 1rem;
    color: var(--lt-soft-gray);
    margin: 0 0 2rem;
    line-height: 1.55;
}
.lt-page-private .lt-private-cta__btn {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.9rem 2rem;
    background-color: var(--lt-navy);
    color: var(--lt-white);
    text-decoration: none;
    font-family: var(--lt-font-body);
    font-weight: 700;
    font-size: 0.95rem;
    border-radius: 2px;
    min-height: 48px;
}
.lt-page-private .lt-private-cta__btn:hover,
.lt-page-private .lt-private-cta__btn:focus-visible {
    background-color: var(--lt-crimson);
    outline: 2px solid var(--lt-brass);
    outline-offset: 2px;
}
"""


def get_context(context):
    context.title = "Private Celebrations — Locally Twisted"
    context.metatags = {
        "description": (
            "Custom balloon decor for birthdays, weddings, baby showers, anniversaries, "
            "and celebration-of-life events across the Wasatch Front. Delivered and installed."
        ),
        "og:title": "Private Celebrations — Locally Twisted",
        "og:description": (
            "Custom balloon decor for private celebrations — birthdays, weddings, showers, milestones, and memorials."
        ),
        "og:type": "website",
    }
    context.private_proof_stats = PRIVATE_PROOF_STATS
    context.private_event_moments = PRIVATE_EVENT_MOMENTS
    context.private_quote_notes = PRIVATE_QUOTE_NOTES
    context.colocated_css = PAGE_CSS
    return context
