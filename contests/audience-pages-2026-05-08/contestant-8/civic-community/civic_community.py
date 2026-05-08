"""
Civic & Community audience page controller.

Route: /civic-community
Audience: City events coordinators, Pride organizers, chambers, county
events, community organizations across the Wasatch Front.
"""

no_cache = 1
sitemap = 1

# Named civic clients from the approved roster.
CIVIC_CLIENTS = [
    "SLC Pride", "Pride Center", "Equality Utah", "LGBT Chamber",
    "Ogden City", "Sandy City", "Herriman City", "Kearns City",
    "Hooper City", "Syracuse City", "West Point City", "Clinton City",
    "SLC County", "Ogden Weber Chamber", "Gallivan Center", "UDOT",
    "Ogden Airport", "Utah Art Alliance", "Safe Kids Fair",
    "Tree House Museum", "Western Sports Park", "Station Park",
    "Downtown Daybreak", "Live Daybreak", "Shops at Southtown", "Newgate Mall",
]

# Proof photos from the approved portfolio library.
# Paths reference the production optimized library and, where noted, the
# Odoo source library (implementation phase will copy into production tree).
CIVIC_PHOTOS = [
    {
        "src": "/assets/locally_twisted/images/portfolio/optimized/seasonal-pride-columns.webp",
        "alt": "Rainbow balloon columns installed at a Utah Pride event",
        "label": "SLC Pride — Column Installation",
    },
    {
        "src": "/assets/locally_twisted/images/portfolio/optimized/corporate-weberstock-photo-opt.webp",
        "alt": "Large balloon photo backdrop for a branded community festival",
        "label": "Community Festival — Photo Moment",
    },
    {
        "src": "C:/Users/baenb/projects/locally-twisted-odoo/assets/image assets/photos for website/Pride/20_ progress flag arch.png",
        "alt": "Progress Pride flag balloon arch installed at a public community event",
        "label": "Pride — Progress Flag Arch",
    },
]

# Proof icons from the brand SVG suite.
CIVIC_ICONS = [
    {
        "asset": "/assets/locally_twisted/icons/brand/utah-rooted.svg",
        "label": "UTAH ROOTED",
        "desc": "Based in Utah. Working across the Wasatch Front since 1998.",
    },
    {
        "asset": "/assets/locally_twisted/icons/brand/civic-parade.svg",
        "label": "CIVIC SCALE",
        "desc": "Parades, arches, columns, and photo ops designed for public venues.",
    },
    {
        "asset": "/assets/locally_twisted/icons/brand/professional.svg",
        "label": "PROFESSIONAL",
        "desc": "On-time install, clean strike, and documentation for public events.",
    },
    {
        "asset": "/assets/locally_twisted/icons/brand/delivery-install.svg",
        "label": "DELIVERED CLEANLY",
        "desc": "Full-service delivery, setup, and teardown — no coordination burden.",
    },
]

PAGE_CSS = """
/* ======================================================
 * Civic & Community audience page — .lt-page-civic root
 * Container modes per section:
 *   hero         : fullbleed
 *   clients-band : fullbleed
 *   photo-row    : band
 *   case-study   : band
 *   services     : band
 *   icons        : fullbleed
 *   cta          : fullbleed
 * ====================================================== */

/* --- Hero ------------------------------------------------------------ */
.lt-page-civic .lt-civic-hero {
    position: relative;
    min-height: 220px;
    height: 220px;
    max-height: 220px;
    background-color: var(--lt-navy);
    overflow: hidden;
    display: flex;
    align-items: center;
}
.lt-page-civic .lt-civic-hero__image {
    position: absolute;
    inset: 0;
    background-image: url('/assets/locally_twisted/images/portfolio/optimized/seasonal-pride-columns.webp');
    background-size: cover;
    background-position: center top;
}
.lt-page-civic .lt-civic-hero__image::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, rgba(10,10,11,0.90) 0%, rgba(14,34,64,0.70) 45%, rgba(14,34,64,0.10) 100%);
}
.lt-page-civic .lt-civic-hero__content {
    position: relative;
    z-index: 1;
    width: 100%;
    max-width: 1280px;
    margin: 0 auto;
    padding: 1.5rem 1rem;
    color: var(--lt-warm-white);
}
.lt-page-civic .lt-civic-hero__eyebrow {
    font-family: var(--lt-font-body);
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--lt-brass);
    margin: 0 0 0.4rem;
}
.lt-page-civic .lt-civic-hero__title {
    font-family: var(--lt-font-heading);
    font-size: 1.9rem;
    font-weight: 700;
    line-height: 1.05;
    color: var(--lt-warm-white);
    margin: 0 0 0.6rem;
    max-width: 22ch;
}
.lt-page-civic .lt-civic-hero__lede {
    font-family: var(--lt-font-body);
    font-size: 0.9rem;
    line-height: 1.4;
    color: rgba(250,247,242,0.9);
    margin: 0 0 0.75rem;
    max-width: 54ch;
}
.lt-page-civic .lt-civic-hero__cta {
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
.lt-page-civic .lt-civic-hero__cta:hover,
.lt-page-civic .lt-civic-hero__cta:focus-visible {
    background-color: var(--lt-navy);
    outline: 2px solid var(--lt-brass);
    outline-offset: 2px;
}
@media (min-width: 768px) {
    .lt-page-civic .lt-civic-hero {
        min-height: 250px; height: 250px; max-height: 250px;
    }
    .lt-page-civic .lt-civic-hero__content { padding: 2rem 2rem; }
    .lt-page-civic .lt-civic-hero__title { font-size: 2.6rem; max-width: 28ch; }
    .lt-page-civic .lt-civic-hero__lede { font-size: 1rem; }
}
@media (min-width: 1200px) {
    .lt-page-civic .lt-civic-hero {
        min-height: 280px; height: 280px; max-height: 280px;
    }
    .lt-page-civic .lt-civic-hero__title { font-size: 3rem; }
}

/* --- Clients band ---------------------------------------------------- */
.lt-page-civic .lt-civic-clients {
    background-color: var(--lt-ink);
    padding: 2.5rem 1rem;
    text-align: center;
}
.lt-page-civic .lt-civic-clients__inner {
    max-width: 1100px;
    margin: 0 auto;
}
.lt-page-civic .lt-civic-clients__heading {
    font-family: var(--lt-font-body);
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--lt-brass);
    margin: 0 0 1.25rem;
}
.lt-page-civic .lt-civic-clients__list {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 0.5rem 1.25rem;
    list-style: none;
    margin: 0;
    padding: 0;
}
.lt-page-civic .lt-civic-clients__list li {
    font-family: var(--lt-font-body);
    font-size: 0.875rem;
    font-weight: 500;
    color: rgba(250,247,242,0.82);
    white-space: nowrap;
}
.lt-page-civic .lt-civic-clients__list li + li::before {
    content: '·';
    margin-right: 1.25rem;
    color: var(--lt-brass);
    opacity: 0.5;
}

/* --- Photo row ------------------------------------------------------- */
.lt-page-civic .lt-civic-photos {
    background-color: var(--lt-warm-white);
    padding: 3.5rem 1rem;
}
.lt-page-civic .lt-civic-photos__inner {
    max-width: 1200px;
    margin: 0 auto;
}
.lt-page-civic .lt-civic-photos__heading {
    font-family: var(--lt-font-heading);
    font-size: 2rem;
    color: var(--lt-ink);
    text-align: center;
    margin: 0 0 0.5rem;
}
.lt-page-civic .lt-civic-photos__lede {
    font-family: var(--lt-font-body);
    font-size: 0.95rem;
    color: var(--lt-soft-gray);
    text-align: center;
    max-width: 54ch;
    margin: 0 auto 2.25rem;
}
.lt-page-civic .lt-civic-photos__grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1rem;
}
@media (min-width: 768px) {
    .lt-page-civic .lt-civic-photos__grid { grid-template-columns: repeat(3,1fr); }
}
.lt-page-civic .lt-civic-photos__item {
    position: relative;
    aspect-ratio: 4/3;
    overflow: hidden;
    border-radius: 2px;
}
.lt-page-civic .lt-civic-photos__item img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}
.lt-page-civic .lt-civic-photos__label {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(transparent, rgba(10,10,11,0.72));
    padding: 1.25rem 0.75rem 0.625rem;
    font-family: var(--lt-font-body);
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: rgba(250,247,242,0.9);
}

/* --- Case study ------------------------------------------------------ */
.lt-page-civic .lt-civic-case {
    background-color: var(--lt-stone);
    padding: 3.5rem 1rem;
}
.lt-page-civic .lt-civic-case__inner {
    max-width: 900px;
    margin: 0 auto;
}
.lt-page-civic .lt-civic-case__eyebrow {
    font-family: var(--lt-font-body);
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--lt-crimson);
    margin: 0 0 0.5rem;
}
.lt-page-civic .lt-civic-case__heading {
    font-family: var(--lt-font-heading);
    font-size: 1.75rem;
    color: var(--lt-ink);
    margin: 0 0 1.25rem;
    line-height: 1.15;
}
@media (min-width: 768px) {
    .lt-page-civic .lt-civic-case__heading { font-size: 2.25rem; }
}
.lt-page-civic .lt-civic-case__body p {
    font-family: var(--lt-font-body);
    font-size: 1rem;
    color: var(--lt-soft-gray);
    line-height: 1.7;
    margin: 0 0 1rem;
    max-width: 72ch;
}

/* --- Service notes --------------------------------------------------- */
.lt-page-civic .lt-civic-services {
    background-color: var(--lt-white);
    padding: 3.5rem 1rem;
}
.lt-page-civic .lt-civic-services__inner {
    max-width: 1100px;
    margin: 0 auto;
}
.lt-page-civic .lt-civic-services__heading {
    font-family: var(--lt-font-heading);
    font-size: 1.875rem;
    color: var(--lt-ink);
    margin: 0 0 0.5rem;
    text-align: center;
}
.lt-page-civic .lt-civic-services__lede {
    font-family: var(--lt-font-body);
    font-size: 0.95rem;
    color: var(--lt-soft-gray);
    text-align: center;
    max-width: 54ch;
    margin: 0 auto 2.25rem;
}
.lt-page-civic .lt-civic-services__grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.25rem;
}
@media (min-width: 768px) {
    .lt-page-civic .lt-civic-services__grid { grid-template-columns: repeat(2,1fr); gap: 1.5rem; }
}
@media (min-width: 1200px) {
    .lt-page-civic .lt-civic-services__grid { grid-template-columns: repeat(4,1fr); }
}
.lt-page-civic .lt-civic-services__card {
    border: 1px solid var(--lt-stone);
    border-radius: 2px;
    padding: 1.5rem;
    background-color: var(--lt-warm-white);
}
.lt-page-civic .lt-civic-services__card-name {
    font-family: var(--lt-font-body);
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--lt-navy);
    margin: 0 0 0.5rem;
}
.lt-page-civic .lt-civic-services__card-desc {
    font-family: var(--lt-font-body);
    font-size: 0.925rem;
    color: var(--lt-soft-gray);
    line-height: 1.6;
    margin: 0;
}

/* --- Icons band ------------------------------------------------------ */
.lt-page-civic .lt-civic-icons {
    background-color: var(--lt-slate);
    padding: 2.75rem 1rem;
}
.lt-page-civic .lt-civic-icons__inner {
    max-width: 1100px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 2rem 1.5rem;
}
@media (min-width: 768px) {
    .lt-page-civic .lt-civic-icons__inner { grid-template-columns: repeat(4,1fr); gap: 1.5rem; }
}
.lt-page-civic .lt-civic-icons__item {
    text-align: center;
}
.lt-page-civic .lt-civic-icons__img {
    width: 48px;
    height: 48px;
    color: var(--lt-brass);
    margin: 0 auto 0.75rem;
    display: block;
}
.lt-page-civic .lt-civic-icons__label {
    font-family: var(--lt-font-body);
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--lt-brass);
    margin: 0 0 0.35rem;
    display: block;
}
.lt-page-civic .lt-civic-icons__desc {
    font-family: var(--lt-font-body);
    font-size: 0.825rem;
    color: rgba(250,247,242,0.75);
    line-height: 1.5;
    margin: 0;
}

/* --- CTA ------------------------------------------------------------ */
.lt-page-civic .lt-civic-cta {
    background-color: var(--lt-navy);
    padding: 4rem 1rem;
    text-align: center;
}
.lt-page-civic .lt-civic-cta__inner {
    max-width: 680px;
    margin: 0 auto;
}
.lt-page-civic .lt-civic-cta__heading {
    font-family: var(--lt-font-heading);
    font-size: 2.25rem;
    color: var(--lt-warm-white);
    margin: 0 0 0.75rem;
    line-height: 1.15;
}
@media (min-width: 768px) {
    .lt-page-civic .lt-civic-cta__heading { font-size: 2.75rem; }
}
.lt-page-civic .lt-civic-cta__body {
    font-family: var(--lt-font-body);
    font-size: 1rem;
    color: rgba(250,247,242,0.82);
    line-height: 1.6;
    max-width: 56ch;
    margin: 0 auto 1.75rem;
}
.lt-page-civic .lt-civic-cta__button {
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
.lt-page-civic .lt-civic-cta__button:hover,
.lt-page-civic .lt-civic-cta__button:focus-visible {
    background-color: var(--lt-ink);
    outline: 2px solid var(--lt-brass);
    outline-offset: 2px;
}
"""


def get_context(context):
    context.title = "Civic & Community Events — Locally Twisted Utah Balloon Decor"
    context.metatags = {
        "description": (
            "Civic-scale balloon decor for Utah cities, counties, Pride organizations, "
            "community events, and public gatherings. Serving 12+ Utah cities since 1998."
        ),
        "og:title": "Civic & Community Balloon Decor — Locally Twisted",
        "og:description": (
            "From SLC Pride to Ogden City to the Gallivan Center — balloon installations "
            "for Utah's civic and community events."
        ),
        "og:type": "website",
    }
    context.civic_clients = CIVIC_CLIENTS
    context.civic_photos = CIVIC_PHOTOS
    context.civic_icons = CIVIC_ICONS
    context.colocated_css = PAGE_CSS
    return context
