"""Controller for /civic-community audience landing page.

Audience: City events coordinators, Pride organizers, chambers, county events,
public-facing community organizations.

Buyer posture: Public-facing, civic-scale, photographable, Utah-proud.
"""
import frappe

no_cache = 1
sitemap = 1


# Grouped roster — category-first so the civic coordinator's eye can scan
# by type rather than reading a wall of names. Matches what C1/C2 learned
# in round 1: category-grouped rosters carry more proof weight than flat tags.
CIVIC_CLIENT_GROUPS = [
    {
        "label": "Cities & Counties",
        "clients": [
            "Ogden City", "Sandy City", "Herriman City", "Kearns",
            "Hooper City", "Syracuse City", "West Point City", "Clinton City",
            "SLC County",
        ],
    },
    {
        "label": "Pride & Equity Organizations",
        "clients": [
            "SLC Pride", "Pride Center", "Equality Utah", "LGBT Chamber",
        ],
    },
    {
        "label": "Chambers & Economic Organizations",
        "clients": [
            "Ogden Weber Chamber", "Gallivan Center", "UDOT", "Ogden Airport",
        ],
    },
    {
        "label": "Community Venues & Events",
        "clients": [
            "Utah Art Alliance", "Safe Kids Fair", "Tree House Museum",
            "Western Sports Park", "Station Park",
            "Downtown Daybreak", "Live Daybreak",
            "Shops at Southtown", "Newgate Mall",
        ],
    },
]

CIVIC_PROOF_STATS = [
    {"number": "26+", "label": "Utah Cities & Organizations"},
    {"number": "1998", "label": "Serving Utah Since"},
    {"number": "100%", "label": "Outdoor-Capable Install"},
]

CIVIC_INSTALLS = [
    {
        "title": "SLC Pride Parade Float",
        "category": "Parade & Civic",
        "image": "/assets/locally_twisted/images/odoo/Pride/Iheart media pride float.png",
        "alt": "Balloon-decorated pride parade float with large rainbow arches in Salt Lake City",
    },
    {
        "title": "Progress Flag Arch",
        "category": "Civic Entrance",
        "image": "/assets/locally_twisted/images/odoo/Pride/20_ progress flag arch.png",
        "alt": "Large progress pride flag balloon arch installed at a Utah civic event entrance",
    },
    {
        "title": "Rainbow Columns Display",
        "category": "Community Installation",
        "image": "/assets/locally_twisted/images/odoo/Pride/rainbow columns.png",
        "alt": "Rainbow balloon columns installed for a Utah community celebration event",
    },
    {
        "title": "Back-to-School Community Stage",
        "category": "Public Event Stage",
        "image": "/assets/locally_twisted/images/portfolio/optimized/school-back-to-school-stage.webp",
        "alt": "Large balloon stage display for a public Utah community school event",
    },
]

CIVIC_SERVICES = [
    {
        "icon": "arch",
        "title": "Parade Arches & Float Decor",
        "body": "Built to travel. Parade-weight structures that hold in Utah's variable weather — sun, wind, or canyon draft."
    },
    {
        "icon": "column",
        "title": "Civic Entrance Columns",
        "body": "Mark your entry, stage, or ribbon-cutting with clean balloon columns in any palette. Municipal and civic-scale."
    },
    {
        "icon": "garland",
        "title": "Stage & Venue Garlands",
        "body": "Organic or structured garlands for outdoor stages, park pavilions, fairground entrances, and public gathering spaces."
    },
    {
        "icon": "backdrop",
        "title": "Photo Opportunities",
        "body": "Community-facing photo ops that attendees post on their own. Civic events deserve visible proof of the moment."
    },
]


PAGE_CSS = """
/* =====================================================================
 * Civic & Community audience page — lt-page-civic namespace
 * Sections: hero, proof-stats, installs, client-roster, services, cta
 * Container modes noted per section for container-contract compliance.
 * ===================================================================== */

/* --- Civic hero (fullbleed mode) ------------------------------------ */
.lt-page-civic .lt-civic-hero {
    position: relative;
    min-height: 220px;
    height: 220px;
    max-height: 280px;
    background-color: var(--lt-navy);
    overflow: hidden;
    display: flex;
    align-items: center;
}
.lt-page-civic .lt-civic-hero__image {
    position: absolute;
    inset: 0;
    background-image: url('/assets/locally_twisted/images/odoo/Parades/Back to school stage display.png');
    background-size: cover;
    background-position: center top;
    background-color: var(--lt-navy);
}
.lt-page-civic .lt-civic-hero__image::after {
    content: '';
    position: absolute;
    inset: 0;
    background:
        linear-gradient(90deg, rgba(10,10,11,0.91) 0%, rgba(14,34,64,0.68) 48%, rgba(14,34,64,0.08) 100%),
        linear-gradient(180deg, rgba(14,34,64,0.04) 0%, rgba(10,10,11,0.32) 100%);
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
    font-size: 0.74rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--lt-brass);
    margin: 0 0 0.4rem;
}
.lt-page-civic .lt-civic-hero__h1 {
    font-family: var(--lt-font-heading);
    font-weight: 700;
    font-size: clamp(1.75rem, 5vw, 2.25rem);
    line-height: 1.05;
    color: var(--lt-warm-white);
    margin: 0 0 0.5rem;
    max-width: 22ch;
}
.lt-page-civic .lt-civic-hero__lede {
    font-family: var(--lt-font-body);
    font-size: 0.94rem;
    line-height: 1.45;
    color: rgba(250,247,242,0.9);
    margin: 0 0 0.85rem;
    max-width: 52ch;
}
.lt-page-civic .lt-civic-hero__cta {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.6rem 1.25rem;
    background-color: var(--lt-crimson);
    color: var(--lt-warm-white);
    font-family: var(--lt-font-body);
    font-weight: 700;
    font-size: 0.85rem;
    text-decoration: none;
    min-height: 44px;
    border-radius: 2px;
}
.lt-page-civic .lt-civic-hero__cta:hover,
.lt-page-civic .lt-civic-hero__cta:focus-visible {
    background-color: var(--lt-navy);
    outline: 2px solid var(--lt-brass);
    outline-offset: 2px;
}
@media (min-width: 768px) {
    .lt-page-civic .lt-civic-hero {
        min-height: 250px;
        height: 250px;
        max-height: 300px;
    }
    .lt-page-civic .lt-civic-hero__content { padding: 2rem; }
    .lt-page-civic .lt-civic-hero__h1 { font-size: 2.5rem; max-width: 28ch; }
}
@media (min-width: 1200px) {
    .lt-page-civic .lt-civic-hero {
        min-height: 280px;
        height: 280px;
        max-height: 320px;
    }
    .lt-page-civic .lt-civic-hero__h1 { font-size: 2.75rem; }
}

/* --- Proof stats band (band mode) ----------------------------------- */
.lt-page-civic .lt-civic-stats {
    background-color: var(--lt-slate);
    padding: 2rem 1rem;
}
.lt-page-civic .lt-civic-stats__inner {
    max-width: 900px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    text-align: center;
}
.lt-page-civic .lt-civic-stats__number {
    font-family: var(--lt-font-heading);
    font-size: 2.25rem;
    color: var(--lt-brass);
    line-height: 1;
    margin: 0 0 0.25rem;
}
.lt-page-civic .lt-civic-stats__label {
    font-family: var(--lt-font-body);
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--lt-warm-white);
    opacity: 0.85;
    line-height: 1.3;
}
@media (min-width: 768px) {
    .lt-page-civic .lt-civic-stats__number { font-size: 3rem; }
    .lt-page-civic .lt-civic-stats__label { font-size: 0.8rem; }
}

/* --- Intro prose (band mode) --------------------------------------- */
.lt-page-civic .lt-civic-intro {
    background-color: var(--lt-warm-white);
    padding: 3.5rem 1.25rem;
}
.lt-page-civic .lt-civic-intro__inner {
    max-width: 780px;
    margin: 0 auto;
}
.lt-page-civic .lt-civic-intro__label {
    font-family: var(--lt-font-body);
    font-size: 0.74rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--lt-berry);
    margin: 0 0 0.75rem;
}
.lt-page-civic .lt-civic-intro__h2 {
    font-family: var(--lt-font-heading);
    font-size: clamp(1.75rem, 4vw, 2.5rem);
    color: var(--lt-ink);
    line-height: 1.1;
    margin: 0 0 1rem;
}
.lt-page-civic .lt-civic-intro__body {
    font-family: var(--lt-font-body);
    font-size: 1.0625rem;
    color: var(--lt-soft-gray);
    line-height: 1.65;
    margin: 0 0 1rem;
}
.lt-page-civic .lt-civic-intro__brass-rule {
    width: 48px;
    height: 2px;
    background-color: var(--lt-brass);
    margin: 1.5rem 0 0;
    border: none;
}

/* --- Installed work proof gallery (visual-field mode) -------------- */
.lt-page-civic .lt-civic-gallery {
    background-color: var(--lt-stone);
    padding: 3.5rem 1.25rem;
}
.lt-page-civic .lt-civic-gallery__inner {
    max-width: 1400px;
    margin: 0 auto;
}
.lt-page-civic .lt-civic-gallery__heading {
    font-family: var(--lt-font-heading);
    font-size: clamp(1.5rem, 3.5vw, 2.25rem);
    color: var(--lt-ink);
    margin: 0 0 0.5rem;
}
.lt-page-civic .lt-civic-gallery__subhead {
    font-family: var(--lt-font-body);
    font-size: 1rem;
    color: var(--lt-soft-gray);
    margin: 0 0 2rem;
    max-width: 60ch;
}
.lt-page-civic .lt-civic-gallery__grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
}
@media (min-width: 992px) {
    .lt-page-civic .lt-civic-gallery__grid {
        grid-template-columns: repeat(4, 1fr);
    }
}
.lt-page-civic .lt-civic-gallery__item {
    position: relative;
    overflow: hidden;
    border-radius: 2px;
    background-color: var(--lt-slate);
}
.lt-page-civic .lt-civic-gallery__img {
    width: 100%;
    aspect-ratio: 3/4;
    object-fit: cover;
    display: block;
}
.lt-page-civic .lt-civic-gallery__caption {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 0.75rem 0.875rem;
    background: linear-gradient(to top, rgba(10,10,11,0.82) 0%, transparent 100%);
    color: var(--lt-warm-white);
}
.lt-page-civic .lt-civic-gallery__caption-cat {
    font-family: var(--lt-font-body);
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--lt-brass);
    margin: 0 0 0.2rem;
}
.lt-page-civic .lt-civic-gallery__caption-title {
    font-family: var(--lt-font-heading);
    font-size: 1rem;
    color: var(--lt-warm-white);
    margin: 0;
    line-height: 1.2;
}

/* --- Client roster band (band mode) -------------------------------- */
.lt-page-civic .lt-civic-roster {
    background-color: var(--lt-navy);
    padding: 3.5rem 1.25rem;
}
.lt-page-civic .lt-civic-roster__inner {
    max-width: 1200px;
    margin: 0 auto;
}
.lt-page-civic .lt-civic-roster__eyebrow {
    font-family: var(--lt-font-body);
    font-size: 0.74rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--lt-brass);
    margin: 0 0 0.5rem;
}
.lt-page-civic .lt-civic-roster__h2 {
    font-family: var(--lt-font-heading);
    font-size: clamp(1.5rem, 3vw, 2rem);
    color: var(--lt-warm-white);
    margin: 0 0 1.75rem;
}
.lt-page-civic .lt-civic-roster__grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.5rem 1.5rem;
}
@media (min-width: 600px) {
    .lt-page-civic .lt-civic-roster__grid { grid-template-columns: repeat(3, 1fr); }
}
@media (min-width: 992px) {
    .lt-page-civic .lt-civic-roster__grid { grid-template-columns: repeat(4, 1fr); }
}
.lt-page-civic .lt-civic-roster__item {
    font-family: var(--lt-font-body);
    font-size: 0.9375rem;
    color: rgba(250,247,242,0.82);
    padding: 0.375rem 0;
    border-bottom: 1px solid rgba(184,154,91,0.18);
    line-height: 1.3;
}

/* --- Client roster grouped layout ---------------------------------- */
.lt-page-civic .lt-civic-roster__groups {
    display: grid;
    grid-template-columns: 1fr;
    gap: 2rem;
}
@media (min-width: 600px) {
    .lt-page-civic .lt-civic-roster__groups { grid-template-columns: repeat(2, 1fr); }
}
@media (min-width: 992px) {
    .lt-page-civic .lt-civic-roster__groups { grid-template-columns: repeat(4, 1fr); }
}
.lt-page-civic .lt-civic-roster__group-label {
    font-family: var(--lt-font-body);
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--lt-brass);
    margin: 0 0 0.75rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(184,154,91,0.35);
}
.lt-page-civic .lt-civic-roster__list {
    list-style: none;
    margin: 0;
    padding: 0;
}
.lt-page-civic .lt-civic-roster__item {
    font-family: var(--lt-font-body);
    font-size: 0.9375rem;
    color: rgba(250,247,242,0.82);
    padding: 0.3rem 0;
    border-bottom: 1px solid rgba(184,154,91,0.1);
    line-height: 1.3;
}
.lt-page-civic .lt-civic-roster__item:last-child { border-bottom: none; }

/* --- Services (band mode) ------------------------------------------ */
.lt-page-civic .lt-civic-services {
    background-color: var(--lt-warm-white);
    padding: 3.5rem 1.25rem;
}
.lt-page-civic .lt-civic-services__inner {
    max-width: 1200px;
    margin: 0 auto;
}
.lt-page-civic .lt-civic-services__h2 {
    font-family: var(--lt-font-heading);
    font-size: clamp(1.5rem, 3vw, 2.25rem);
    color: var(--lt-ink);
    margin: 0 0 0.5rem;
}
.lt-page-civic .lt-civic-services__lede {
    font-family: var(--lt-font-body);
    font-size: 1rem;
    color: var(--lt-soft-gray);
    margin: 0 0 2.5rem;
    max-width: 60ch;
}
.lt-page-civic .lt-civic-services__grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.5rem;
}
@media (min-width: 600px) {
    .lt-page-civic .lt-civic-services__grid { grid-template-columns: repeat(2, 1fr); }
}
@media (min-width: 992px) {
    .lt-page-civic .lt-civic-services__grid { grid-template-columns: repeat(4, 1fr); }
}
.lt-page-civic .lt-civic-services__card {
    background-color: var(--lt-white);
    border: 1px solid var(--lt-stone);
    border-radius: 2px;
    padding: 1.75rem 1.5rem;
}
.lt-page-civic .lt-civic-services__icon {
    width: 48px;
    height: 48px;
    color: var(--lt-brass);
    margin-bottom: 1rem;
}
.lt-page-civic .lt-civic-services__card-title {
    font-family: var(--lt-font-heading);
    font-size: 1.25rem;
    color: var(--lt-ink);
    margin: 0 0 0.5rem;
    line-height: 1.2;
}
.lt-page-civic .lt-civic-services__card-body {
    font-family: var(--lt-font-body);
    font-size: 0.9375rem;
    color: var(--lt-soft-gray);
    line-height: 1.6;
    margin: 0;
}

/* --- Closing CTA (fullbleed mode) ---------------------------------- */
.lt-page-civic .lt-civic-cta {
    background-color: var(--lt-ink);
    padding: 4rem 1.25rem;
    text-align: center;
}
.lt-page-civic .lt-civic-cta__inner {
    max-width: 700px;
    margin: 0 auto;
}
.lt-page-civic .lt-civic-cta__h2 {
    font-family: var(--lt-font-heading);
    font-size: clamp(1.75rem, 4vw, 2.75rem);
    color: var(--lt-warm-white);
    margin: 0 0 1rem;
    line-height: 1.1;
}
.lt-page-civic .lt-civic-cta__body {
    font-family: var(--lt-font-body);
    font-size: 1.0625rem;
    color: rgba(250,247,242,0.82);
    max-width: 52ch;
    margin: 0 auto 1.75rem;
    line-height: 1.55;
}
.lt-page-civic .lt-civic-cta__btn {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 1rem 2.25rem;
    background-color: var(--lt-berry);
    color: var(--lt-warm-white);
    font-family: var(--lt-font-body);
    font-weight: 700;
    font-size: 1rem;
    text-decoration: none;
    border-radius: 2px;
    min-height: 48px;
}
.lt-page-civic .lt-civic-cta__btn:hover,
.lt-page-civic .lt-civic-cta__btn:focus-visible {
    background-color: var(--lt-crimson);
    outline: 2px solid var(--lt-brass);
    outline-offset: 2px;
}
.lt-page-civic .lt-civic-cta__sub {
    margin: 1.25rem 0 0;
    font-family: var(--lt-font-body);
    font-size: 0.875rem;
    color: rgba(250,247,242,0.55);
}
.lt-page-civic .lt-civic-cta__sub a {
    color: var(--lt-brass);
    text-decoration: none;
}
.lt-page-civic .lt-civic-cta__sub a:hover { text-decoration: underline; }
"""


def get_context(context):
    context.title = "Civic & Community Events — Locally Twisted Balloon Decor"
    context.metatags = {
        "description": (
            "Professional balloon decor for Utah city events, Pride celebrations, "
            "chambers, county fairs, and public community gatherings. "
            "Trusted by SLC Pride, Ogden City, Sandy City, UDOT, and 20+ Utah organizations."
        ),
        "og:title": "Civic & Community Balloon Decor — Locally Twisted",
        "og:description": (
            "Utah's civic balloon specialists. Parade floats, entrances, stage garlands, "
            "and photo ops for city events, Pride, chambers, and public organizations."
        ),
        "og:type": "website",
    }
    context.civic_client_groups = CIVIC_CLIENT_GROUPS
    context.civic_proof_stats = CIVIC_PROOF_STATS
    context.civic_installs = CIVIC_INSTALLS
    context.civic_services = CIVIC_SERVICES
    context.colocated_css = PAGE_CSS
    return context
