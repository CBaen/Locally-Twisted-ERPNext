"""
Schools & Campuses audience page controller.

Route: /schools-campuses
Audience: Activity directors, athletic departments, PTAs, college student life,
graduation organizers.
Buyer posture: Spirit-driven, schedule-tight, school colors disciplined, family-friendly.
"""

no_cache = 1
sitemap = 1

# Named school/campus clients from the approved roster.
SCHOOL_CLIENTS = [
    "University of Utah",
    "Weber State University",
    "St. Joseph's High School",
    # Community org/event adjacents that serve school audiences
    "Tree House Museum",
    "Safe Kids Fair",
]

# Proof photos for school/campus context.
SCHOOL_PHOTOS = [
    {
        "src": "/assets/locally_twisted/images/portfolio/optimized/school-back-to-school-stage.webp",
        "alt": "Large balloon stage display installed for a back-to-school event",
        "label": "Back-to-School — Stage Installation",
    },
    {
        "src": "/assets/locally_twisted/images/portfolio/optimized/corporate-wsu-arch-bouquets.webp",
        "alt": "Balloon arch and bouquet arrangements at Weber State University",
        "label": "Weber State University — Event Arch",
    },
    {
        "src": "/assets/locally_twisted/images/portfolio/optimized/school-grad-garland.webp",
        "alt": "Balloon garland installation for a graduation ceremony",
        "label": "Graduation — Ceremony Garland",
    },
]

# Proof icons for school buyers.
SCHOOL_ICONS = [
    {
        "asset": "/assets/locally_twisted/icons/brand/school-spirit.svg",
        "label": "SCHOOL COLORS",
        "desc": "Exact color matches for school and team palettes — not close enough, exact.",
    },
    {
        "asset": "/assets/locally_twisted/icons/brand/event-stage.svg",
        "label": "STAGE READY",
        "desc": "Installations designed for auditoriums, gymnasiums, and campus venues.",
    },
    {
        "asset": "/assets/locally_twisted/icons/brand/professional.svg",
        "label": "FAMILY FRIENDLY",
        "desc": "Clean, professional work appropriate for all ages and school contexts.",
    },
    {
        "asset": "/assets/locally_twisted/icons/brand/delivery-install.svg",
        "label": "ON SCHEDULE",
        "desc": "School events run on the bell. Installs are completed before your first student arrives.",
    },
]

PAGE_CSS = """
/* ======================================================
 * Schools & Campuses audience page — .lt-page-school root
 * Container modes per section:
 *   hero          : fullbleed
 *   clients-band  : fullbleed
 *   photo-row     : band
 *   case-study    : band
 *   services      : band
 *   icons         : fullbleed
 *   cta           : fullbleed
 * ====================================================== */

/* --- Hero ------------------------------------------------------------ */
.lt-page-school .lt-school-hero {
    position: relative;
    min-height: 220px;
    height: 220px;
    max-height: 220px;
    background-color: var(--lt-navy);
    overflow: hidden;
    display: flex;
    align-items: center;
}
.lt-page-school .lt-school-hero__image {
    position: absolute;
    inset: 0;
    background-image: url('/assets/locally_twisted/images/portfolio/optimized/school-back-to-school-stage.webp');
    background-size: cover;
    background-position: center;
}
.lt-page-school .lt-school-hero__image::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, rgba(14,34,64,0.92) 0%, rgba(14,34,64,0.72) 50%, rgba(14,34,64,0.12) 100%);
}
.lt-page-school .lt-school-hero__content {
    position: relative;
    z-index: 1;
    width: 100%;
    max-width: 1280px;
    margin: 0 auto;
    padding: 1.5rem 1rem;
    color: var(--lt-warm-white);
}
.lt-page-school .lt-school-hero__eyebrow {
    font-family: var(--lt-font-body);
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--lt-brass);
    margin: 0 0 0.4rem;
}
.lt-page-school .lt-school-hero__title {
    font-family: var(--lt-font-heading);
    font-size: 1.9rem;
    font-weight: 700;
    line-height: 1.05;
    color: var(--lt-warm-white);
    margin: 0 0 0.6rem;
    max-width: 22ch;
}
.lt-page-school .lt-school-hero__lede {
    font-family: var(--lt-font-body);
    font-size: 0.9rem;
    line-height: 1.4;
    color: rgba(250,247,242,0.88);
    margin: 0 0 0.75rem;
    max-width: 52ch;
}
.lt-page-school .lt-school-hero__cta {
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
.lt-page-school .lt-school-hero__cta:hover,
.lt-page-school .lt-school-hero__cta:focus-visible {
    background-color: var(--lt-ink);
    outline: 2px solid var(--lt-brass);
    outline-offset: 2px;
}
@media (min-width: 768px) {
    .lt-page-school .lt-school-hero { min-height: 250px; height: 250px; max-height: 250px; }
    .lt-page-school .lt-school-hero__content { padding: 2rem; }
    .lt-page-school .lt-school-hero__title { font-size: 2.6rem; max-width: 28ch; }
    .lt-page-school .lt-school-hero__lede { font-size: 1rem; }
}
@media (min-width: 1200px) {
    .lt-page-school .lt-school-hero { min-height: 280px; height: 280px; max-height: 280px; }
    .lt-page-school .lt-school-hero__title { font-size: 2.9rem; }
}

/* --- Clients band ---------------------------------------------------- */
.lt-page-school .lt-school-clients {
    background-color: var(--lt-navy);
    padding: 2.5rem 1rem;
    text-align: center;
}
.lt-page-school .lt-school-clients__inner {
    max-width: 900px;
    margin: 0 auto;
}
.lt-page-school .lt-school-clients__heading {
    font-family: var(--lt-font-body);
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--lt-brass);
    margin: 0 0 1.25rem;
}
.lt-page-school .lt-school-clients__list {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 0.75rem 2rem;
    list-style: none;
    margin: 0;
    padding: 0;
}
.lt-page-school .lt-school-clients__list li {
    font-family: var(--lt-font-heading);
    font-size: 1.25rem;
    font-weight: 600;
    color: rgba(250,247,242,0.9);
}
/* Schools roster is small — larger type makes each name feel more prominent */

/* --- Photo row ------------------------------------------------------- */
.lt-page-school .lt-school-photos {
    background-color: var(--lt-warm-white);
    padding: 3.5rem 1rem;
}
.lt-page-school .lt-school-photos__inner {
    max-width: 1200px;
    margin: 0 auto;
}
.lt-page-school .lt-school-photos__heading {
    font-family: var(--lt-font-heading);
    font-size: 2rem;
    color: var(--lt-ink);
    text-align: center;
    margin: 0 0 0.5rem;
}
.lt-page-school .lt-school-photos__lede {
    font-family: var(--lt-font-body);
    font-size: 0.95rem;
    color: var(--lt-soft-gray);
    text-align: center;
    max-width: 54ch;
    margin: 0 auto 2.25rem;
}
.lt-page-school .lt-school-photos__grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1rem;
}
@media (min-width: 768px) {
    .lt-page-school .lt-school-photos__grid { grid-template-columns: repeat(3,1fr); }
}
.lt-page-school .lt-school-photos__item {
    position: relative;
    aspect-ratio: 4/3;
    overflow: hidden;
    border-radius: 2px;
}
.lt-page-school .lt-school-photos__item img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}
.lt-page-school .lt-school-photos__label {
    position: absolute;
    bottom: 0; left: 0; right: 0;
    background: linear-gradient(transparent, rgba(10,10,11,0.72));
    padding: 1.25rem 0.75rem 0.625rem;
    font-family: var(--lt-font-body);
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: rgba(250,247,242,0.9);
}

/* --- School Colors block (distinctive) ------------------------------ */
.lt-page-school .lt-school-colors {
    background-color: var(--lt-stone);
    padding: 3.5rem 1rem;
}
.lt-page-school .lt-school-colors__inner {
    max-width: 900px;
    margin: 0 auto;
}
.lt-page-school .lt-school-colors__eyebrow {
    font-family: var(--lt-font-body);
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--lt-crimson);
    margin: 0 0 0.5rem;
}
.lt-page-school .lt-school-colors__heading {
    font-family: var(--lt-font-heading);
    font-size: 1.75rem;
    color: var(--lt-ink);
    margin: 0 0 1.25rem;
    line-height: 1.15;
}
@media (min-width: 768px) {
    .lt-page-school .lt-school-colors__heading { font-size: 2.25rem; }
}
.lt-page-school .lt-school-colors__body p {
    font-family: var(--lt-font-body);
    font-size: 1rem;
    color: var(--lt-soft-gray);
    line-height: 1.7;
    margin: 0 0 1rem;
    max-width: 72ch;
}

/* --- Service notes --------------------------------------------------- */
.lt-page-school .lt-school-services {
    background-color: var(--lt-white);
    padding: 3.5rem 1rem;
}
.lt-page-school .lt-school-services__inner {
    max-width: 1100px;
    margin: 0 auto;
}
.lt-page-school .lt-school-services__heading {
    font-family: var(--lt-font-heading);
    font-size: 1.875rem;
    color: var(--lt-ink);
    margin: 0 0 0.5rem;
    text-align: center;
}
.lt-page-school .lt-school-services__lede {
    font-family: var(--lt-font-body);
    font-size: 0.95rem;
    color: var(--lt-soft-gray);
    text-align: center;
    max-width: 54ch;
    margin: 0 auto 2.25rem;
}
.lt-page-school .lt-school-services__grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.25rem;
}
@media (min-width: 768px) {
    .lt-page-school .lt-school-services__grid { grid-template-columns: repeat(2,1fr); gap: 1.5rem; }
}
@media (min-width: 1200px) {
    .lt-page-school .lt-school-services__grid { grid-template-columns: repeat(4,1fr); }
}
.lt-page-school .lt-school-services__card {
    border: 1px solid var(--lt-stone);
    border-radius: 2px;
    padding: 1.5rem;
    background-color: var(--lt-warm-white);
}
.lt-page-school .lt-school-services__card-name {
    font-family: var(--lt-font-body);
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--lt-navy);
    margin: 0 0 0.5rem;
}
.lt-page-school .lt-school-services__card-desc {
    font-family: var(--lt-font-body);
    font-size: 0.925rem;
    color: var(--lt-soft-gray);
    line-height: 1.6;
    margin: 0;
}

/* --- Icons band ------------------------------------------------------ */
.lt-page-school .lt-school-icons {
    background-color: var(--lt-slate);
    padding: 2.75rem 1rem;
}
.lt-page-school .lt-school-icons__inner {
    max-width: 1100px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: repeat(2,1fr);
    gap: 2rem 1.5rem;
}
@media (min-width: 768px) {
    .lt-page-school .lt-school-icons__inner { grid-template-columns: repeat(4,1fr); gap: 1.5rem; }
}
.lt-page-school .lt-school-icons__item { text-align: center; }
.lt-page-school .lt-school-icons__img {
    width: 48px; height: 48px;
    color: var(--lt-brass);
    margin: 0 auto 0.75rem;
    display: block;
}
.lt-page-school .lt-school-icons__label {
    font-family: var(--lt-font-body);
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--lt-brass);
    margin: 0 0 0.35rem;
    display: block;
}
.lt-page-school .lt-school-icons__desc {
    font-family: var(--lt-font-body);
    font-size: 0.825rem;
    color: rgba(250,247,242,0.75);
    line-height: 1.5;
    margin: 0;
}

/* --- CTA ------------------------------------------------------------ */
.lt-page-school .lt-school-cta {
    background-color: var(--lt-navy);
    padding: 4rem 1rem;
    text-align: center;
}
.lt-page-school .lt-school-cta__inner {
    max-width: 680px;
    margin: 0 auto;
}
.lt-page-school .lt-school-cta__heading {
    font-family: var(--lt-font-heading);
    font-size: 2.25rem;
    color: var(--lt-warm-white);
    margin: 0 0 0.75rem;
    line-height: 1.15;
}
@media (min-width: 768px) {
    .lt-page-school .lt-school-cta__heading { font-size: 2.75rem; }
}
.lt-page-school .lt-school-cta__body {
    font-family: var(--lt-font-body);
    font-size: 1rem;
    color: rgba(250,247,242,0.82);
    line-height: 1.6;
    max-width: 56ch;
    margin: 0 auto 1.75rem;
}
.lt-page-school .lt-school-cta__button {
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
.lt-page-school .lt-school-cta__button:hover,
.lt-page-school .lt-school-cta__button:focus-visible {
    background-color: var(--lt-ink);
    outline: 2px solid var(--lt-brass);
    outline-offset: 2px;
}
"""


def get_context(context):
    context.title = "Schools & Campuses — Locally Twisted Utah Balloon Decor"
    context.metatags = {
        "description": (
            "Balloon decor for Utah schools and campuses. Exact school color matches, "
            "on-time installs, and graduation-to-back-to-school service. University of Utah, "
            "Weber State, and more."
        ),
        "og:title": "School & Campus Balloon Decor — Locally Twisted",
        "og:description": (
            "Spirit events, graduation ceremonies, and campus installations "
            "for Utah's schools and universities."
        ),
        "og:type": "website",
    }
    context.school_clients = SCHOOL_CLIENTS
    context.school_photos = SCHOOL_PHOTOS
    context.school_icons = SCHOOL_ICONS
    context.colocated_css = PAGE_CSS
    return context
