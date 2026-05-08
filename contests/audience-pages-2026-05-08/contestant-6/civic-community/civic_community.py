"""Civic & Community audience landing page — /civic-community

Buyer: City events coordinators, Pride organizers, chambers, county events,
public-facing community organizations.

Posture: Public-facing, civic-scale, photographable, Utah-proud.
"""
import frappe

no_cache = 1
sitemap = 1

CIVIC_CLIENTS = [
    {"name": "SLC Pride", "category": "Pride & Equity"},
    {"name": "Pride Center", "category": "Pride & Equity"},
    {"name": "Equality Utah", "category": "Pride & Equity"},
    {"name": "LGBT Chamber", "category": "Pride & Equity"},
    {"name": "Ogden City", "category": "City Government"},
    {"name": "Sandy City", "category": "City Government"},
    {"name": "Herriman City", "category": "City Government"},
    {"name": "Kearns City", "category": "City Government"},
    {"name": "Hooper City", "category": "City Government"},
    {"name": "Syracuse City", "category": "City Government"},
    {"name": "West Point City", "category": "City Government"},
    {"name": "Clinton City", "category": "City Government"},
    {"name": "SLC County", "category": "County & Regional"},
    {"name": "Ogden Weber Chamber", "category": "Chambers & Business"},
    {"name": "Gallivan Center", "category": "Venues & Parks"},
    {"name": "UDOT", "category": "State Agencies"},
    {"name": "Ogden Airport", "category": "Public Infrastructure"},
    {"name": "Utah Art Alliance", "category": "Arts & Culture"},
    {"name": "Safe Kids Fair", "category": "Public Safety & Community"},
    {"name": "Tree House Museum", "category": "Museums & Education"},
    {"name": "Western Sports Park", "category": "Venues & Parks"},
    {"name": "Station Park", "category": "Venues & Parks"},
    {"name": "Downtown Daybreak", "category": "Planned Communities"},
    {"name": "Live Daybreak", "category": "Planned Communities"},
    {"name": "Shops at Southtown", "category": "Retail & Commercial"},
    {"name": "Newgate Mall", "category": "Retail & Commercial"},
]

CIVIC_PROOF_STATS = [
    {"icon": "civic-parade", "label": "CIVIC EVENTS", "value": "60+", "sub": "municipalities, parks, and public organizations served"},
    {"icon": "utah-rooted", "label": "UTAH ROOTED", "value": "Since 1998", "sub": "Wasatch Front events from Ogden to Daybreak"},
    {"icon": "event-stage", "label": "EVENT READY", "value": "Parade to Podium", "sub": "Arches, columns, stage decor, photo moments"},
    {"icon": "delivery-install", "label": "DELIVERED CLEANLY", "value": "On-Site Install", "sub": "We handle setup and strike; your crew stays focused"},
]

CIVIC_PHOTO_PROOF = [
    {
        "image": "/assets/locally_twisted/images/portfolio/optimized/seasonal-pride-columns.webp",
        "alt": "Pride balloon columns installed at SLC civic event",
        "caption": "SLC Pride — Column installation, Gallivan Center",
        "client": "SLC Pride",
    },
    {
        "image": "C:/Users/baenb/projects/locally-twisted-odoo/assets/image assets/photos for website/Pride/20_ progress flag arch.png",
        "alt": "Progress flag balloon arch at Utah Pride event",
        "caption": "Equality Utah — Progress Flag arch, parade",
        "client": "Equality Utah",
    },
    {
        "image": "C:/Users/baenb/projects/locally-twisted-odoo/assets/image assets/photos for website/Standard arch for parade.png",
        "alt": "Standard parade arch installation for civic event",
        "caption": "City parade arch — custom community colors",
        "client": "Sandy City",
    },
    {
        "image": "C:/Users/baenb/projects/locally-twisted-odoo/assets/image assets/photos for website/Pride/rainbow columns.png",
        "alt": "Rainbow balloon columns at outdoor public event",
        "caption": "Pride Center — rainbow column pair, public plaza",
        "client": "Pride Center",
    },
    {
        "image": "C:/Users/baenb/projects/locally-twisted-odoo/assets/image assets/photos for website/Parades/Love heart pride parade.png",
        "alt": "Love heart balloon sculpture at Utah Pride parade",
        "caption": "SLC Pride Parade — marching decor",
        "client": "SLC Pride",
    },
    {
        "image": "C:/Users/baenb/projects/locally-twisted-odoo/assets/image assets/photos for website/themed decor/35_ Weberstock arch .png",
        "alt": "Festival arch at Weberstock community event",
        "caption": "Ogden community festival — event entrance arch",
        "client": "Ogden Weber Chamber",
    },
]

SERVICE_FORMATS = [
    {
        "icon": "balloon-arch",
        "name": "Parade & Event Arches",
        "desc": "Entrance arches and marching float decor at civic scale — designed for outdoor durability and photographability.",
    },
    {
        "icon": "balloon-column",
        "name": "Column Pairs & Markers",
        "desc": "Entry points, stage flanks, and venue markers for public parks, plazas, and municipal buildings.",
    },
    {
        "icon": "civic-parade",
        "name": "Parade Float Decor",
        "desc": "Secured, weather-considered balloon work for float entries, marching contingents, and public processions.",
    },
    {
        "icon": "event-stage",
        "name": "Stage & Podium Backdrops",
        "desc": "Official ribbon cuttings, mayoral events, public dedications — a backdrop that reads across a crowd and photographs well.",
    },
]

PAGE_CSS = """
/* ====================================================================
 * Civic & Community page — .lt-page-civic scoped
 * Container modes: hero=fullbleed, proof-stats=band, photo-grid=band,
 *   client-roster=fullbleed, service-formats=band, cta=fullbleed
 * ==================================================================== */

/* --- hero ----------------------------------------------------------- */
.lt-page-civic .lt-civic-hero {
    position: relative;
    height: 220px;
    min-height: 220px;
    max-height: 220px;
    background-color: var(--lt-navy);
    overflow: hidden;
    display: flex;
    align-items: center;
}
.lt-page-civic .lt-civic-hero__bg {
    position: absolute;
    inset: 0;
    background-image: url('/assets/locally_twisted/images/portfolio/optimized/seasonal-pride-columns.webp');
    background-size: cover;
    background-position: center top;
}
.lt-page-civic .lt-civic-hero__bg::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, rgba(10,10,11,0.87) 0%, rgba(14,34,64,0.68) 45%, rgba(14,34,64,0.14) 100%);
}
.lt-page-civic .lt-civic-hero__content {
    position: relative;
    z-index: 1;
    width: 100%;
    max-width: 1280px;
    margin: 0 auto;
    padding: 1.5rem 1rem;
}
.lt-page-civic .lt-civic-hero__eyebrow {
    font-family: var(--lt-font-body);
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--lt-brass);
    margin: 0 0 0.35rem;
}
.lt-page-civic .lt-civic-hero__h1 {
    font-family: var(--lt-font-heading);
    font-size: clamp(1.75rem, 4.5vw, 2.2rem);
    font-weight: 700;
    color: var(--lt-white);
    margin: 0 0 0.45rem;
    max-width: 22ch;
    line-height: 1.05;
}
.lt-page-civic .lt-civic-hero__lede {
    font-family: var(--lt-font-body);
    font-size: 0.9rem;
    color: rgba(250,247,242,0.92);
    margin: 0 0 0.75rem;
    max-width: 52ch;
    line-height: 1.35;
}
.lt-page-civic .lt-civic-hero__cta {
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
.lt-page-civic .lt-civic-hero__cta:hover,
.lt-page-civic .lt-civic-hero__cta:focus-visible {
    background-color: var(--lt-navy);
    outline: 2px solid var(--lt-brass);
    outline-offset: 2px;
}
@media (min-width: 768px) {
    .lt-page-civic .lt-civic-hero { height: 250px; min-height: 250px; max-height: 250px; }
    .lt-page-civic .lt-civic-hero__content { padding: 2rem 2rem; }
    .lt-page-civic .lt-civic-hero__h1 { font-size: 2.6rem; }
}
@media (min-width: 1200px) {
    .lt-page-civic .lt-civic-hero { height: 280px; min-height: 280px; max-height: 280px; }
}

/* --- brass rule divider --------------------------------------------- */
.lt-page-civic .lt-civic-rule {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1.5rem 1rem;
    gap: 0.75rem;
    background-color: var(--lt-warm-white);
}
.lt-page-civic .lt-civic-rule span {
    display: block;
    width: 0.4rem;
    height: 0.4rem;
    border-radius: 50%;
    background-color: var(--lt-brass);
    opacity: 0.7;
}
.lt-page-civic .lt-civic-rule hr {
    flex: 1;
    border: none;
    border-top: 1px solid var(--lt-stone);
    max-width: 180px;
}

/* --- proof stats band ----------------------------------------------- */
.lt-page-civic .lt-civic-stats {
    background-color: var(--lt-ink);
    padding: 2.5rem 1.25rem;
}
.lt-page-civic .lt-civic-stats__inner {
    max-width: 1200px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem 1rem;
}
@media (min-width: 768px) {
    .lt-page-civic .lt-civic-stats__inner {
        grid-template-columns: repeat(4, 1fr);
        gap: 1.5rem;
    }
}
.lt-page-civic .lt-civic-stat {
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
}
.lt-page-civic .lt-civic-stat__icon {
    width: 44px;
    height: 44px;
    color: var(--lt-brass);
}
.lt-page-civic .lt-civic-stat__label {
    font-family: var(--lt-font-body);
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--lt-brass);
}
.lt-page-civic .lt-civic-stat__value {
    font-family: var(--lt-font-heading);
    font-size: 1.75rem;
    color: var(--lt-white);
    line-height: 1;
}
.lt-page-civic .lt-civic-stat__sub {
    font-family: var(--lt-font-body);
    font-size: 0.78rem;
    color: rgba(250,247,242,0.6);
    line-height: 1.3;
    max-width: 16ch;
}

/* --- photo proof grid ----------------------------------------------- */
.lt-page-civic .lt-civic-photos {
    background-color: var(--lt-warm-white);
    padding: 4rem 1.25rem;
}
.lt-page-civic .lt-civic-photos__inner {
    max-width: 1280px;
    margin: 0 auto;
}
.lt-page-civic .lt-civic-photos__heading {
    font-family: var(--lt-font-heading);
    font-size: 2rem;
    color: var(--lt-ink);
    margin: 0 0 0.5rem;
}
.lt-page-civic .lt-civic-photos__lede {
    font-family: var(--lt-font-body);
    font-size: 1rem;
    color: var(--lt-soft-gray);
    margin: 0 0 2.5rem;
    max-width: 58ch;
    line-height: 1.5;
}
.lt-page-civic .lt-civic-photos__grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
}
@media (min-width: 768px) {
    .lt-page-civic .lt-civic-photos__grid {
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
    }
}
.lt-page-civic .lt-civic-photo {
    position: relative;
    overflow: hidden;
    border-radius: 3px;
    aspect-ratio: 4/3;
    background-color: var(--lt-stone);
}
.lt-page-civic .lt-civic-photo img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}
.lt-page-civic .lt-civic-photo__caption {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 0.5rem 0.75rem;
    background: linear-gradient(to top, rgba(10,10,11,0.78) 0%, transparent 100%);
    font-family: var(--lt-font-body);
    font-size: 0.72rem;
    color: rgba(250,247,242,0.92);
    line-height: 1.3;
}

/* --- client roster fullbleed --------------------------------------- */
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
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--lt-brass);
    margin: 0 0 0.75rem;
}
.lt-page-civic .lt-civic-roster__heading {
    font-family: var(--lt-font-heading);
    font-size: 1.875rem;
    color: var(--lt-white);
    margin: 0 0 0.5rem;
    max-width: 34ch;
    line-height: 1.15;
}
.lt-page-civic .lt-civic-roster__sub {
    font-family: var(--lt-font-body);
    font-size: 0.9rem;
    color: rgba(250,247,242,0.65);
    margin: 0 0 2.5rem;
    max-width: 52ch;
    line-height: 1.45;
}
.lt-page-civic .lt-civic-roster__grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.5rem 1.5rem;
}
@media (min-width: 768px) {
    .lt-page-civic .lt-civic-roster__grid {
        grid-template-columns: repeat(3, 1fr);
    }
}
@media (min-width: 1024px) {
    .lt-page-civic .lt-civic-roster__grid {
        grid-template-columns: repeat(4, 1fr);
    }
}
.lt-page-civic .lt-civic-roster__item {
    font-family: var(--lt-font-body);
    font-size: 0.9rem;
    color: rgba(250,247,242,0.82);
    padding: 0.35rem 0;
    border-bottom: 1px solid rgba(184,154,91,0.15);
    line-height: 1.3;
}
.lt-page-civic .lt-civic-roster__cat {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--lt-brass);
    display: block;
    margin-top: 0.15rem;
    opacity: 0.8;
}

/* --- service formats band ------------------------------------------ */
.lt-page-civic .lt-civic-services {
    background-color: var(--lt-warm-white);
    padding: 4rem 1.25rem;
}
.lt-page-civic .lt-civic-services__inner {
    max-width: 1200px;
    margin: 0 auto;
}
.lt-page-civic .lt-civic-services__heading {
    font-family: var(--lt-font-heading);
    font-size: 1.875rem;
    color: var(--lt-ink);
    margin: 0 0 0.5rem;
}
.lt-page-civic .lt-civic-services__lede {
    font-family: var(--lt-font-body);
    font-size: 1rem;
    color: var(--lt-soft-gray);
    margin: 0 0 2.5rem;
    max-width: 54ch;
    line-height: 1.5;
}
.lt-page-civic .lt-civic-services__grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.25rem;
}
@media (min-width: 768px) {
    .lt-page-civic .lt-civic-services__grid {
        grid-template-columns: 1fr 1fr;
        gap: 1.5rem;
    }
}
.lt-page-civic .lt-civic-service-card {
    display: flex;
    gap: 1rem;
    align-items: flex-start;
    padding: 1.5rem;
    background-color: var(--lt-white);
    border: 1px solid var(--lt-stone);
    border-radius: 3px;
}
.lt-page-civic .lt-civic-service-card__icon {
    width: 40px;
    height: 40px;
    flex-shrink: 0;
    color: var(--lt-brass);
}
.lt-page-civic .lt-civic-service-card__name {
    font-family: var(--lt-font-heading);
    font-size: 1.25rem;
    color: var(--lt-ink);
    margin: 0 0 0.4rem;
}
.lt-page-civic .lt-civic-service-card__desc {
    font-family: var(--lt-font-body);
    font-size: 0.9rem;
    color: var(--lt-soft-gray);
    margin: 0;
    line-height: 1.5;
}

/* --- process note band (contained) --------------------------------- */
.lt-page-civic .lt-civic-process {
    background-color: var(--lt-sandstone);
    padding: 3rem 1.25rem;
}
.lt-page-civic .lt-civic-process__inner {
    max-width: 860px;
    margin: 0 auto;
}
.lt-page-civic .lt-civic-process__eyebrow {
    font-family: var(--lt-font-body);
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--lt-ink);
    opacity: 0.55;
    margin: 0 0 0.5rem;
}
.lt-page-civic .lt-civic-process__heading {
    font-family: var(--lt-font-heading);
    font-size: 1.625rem;
    color: var(--lt-ink);
    margin: 0 0 1rem;
    line-height: 1.2;
}
.lt-page-civic .lt-civic-process__body {
    font-family: var(--lt-font-body);
    font-size: 1rem;
    color: var(--lt-ink);
    opacity: 0.78;
    margin: 0 0 1rem;
    line-height: 1.6;
    max-width: 62ch;
}
.lt-page-civic .lt-civic-process__steps {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}
.lt-page-civic .lt-civic-process__step {
    display: flex;
    gap: 0.75rem;
    align-items: flex-start;
}
.lt-page-civic .lt-civic-process__step-num {
    font-family: var(--lt-font-heading);
    font-size: 1.5rem;
    color: var(--lt-brass);
    line-height: 1;
    width: 1.75rem;
    flex-shrink: 0;
}
.lt-page-civic .lt-civic-process__step-text {
    font-family: var(--lt-font-body);
    font-size: 0.9rem;
    color: var(--lt-ink);
    opacity: 0.78;
    line-height: 1.5;
}

/* --- CTA fullbleed -------------------------------------------------- */
.lt-page-civic .lt-civic-cta {
    background-color: var(--lt-slate);
    padding: 4rem 1.25rem;
    text-align: center;
}
.lt-page-civic .lt-civic-cta__inner {
    max-width: 680px;
    margin: 0 auto;
}
.lt-page-civic .lt-civic-cta__heading {
    font-family: var(--lt-font-heading);
    font-size: 2.25rem;
    color: var(--lt-white);
    margin: 0 0 0.75rem;
    line-height: 1.1;
}
.lt-page-civic .lt-civic-cta__body {
    font-family: var(--lt-font-body);
    font-size: 1rem;
    color: rgba(250,247,242,0.78);
    margin: 0 0 2rem;
    line-height: 1.55;
}
.lt-page-civic .lt-civic-cta__btn {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.9rem 2rem;
    background-color: var(--lt-crimson);
    color: var(--lt-white);
    text-decoration: none;
    font-family: var(--lt-font-body);
    font-weight: 700;
    font-size: 0.95rem;
    border-radius: 2px;
    min-height: 48px;
}
.lt-page-civic .lt-civic-cta__btn:hover,
.lt-page-civic .lt-civic-cta__btn:focus-visible {
    background-color: var(--lt-ink);
    outline: 2px solid var(--lt-brass);
    outline-offset: 2px;
}
"""


def get_context(context):
    context.title = "Civic & Community Events — Locally Twisted"
    context.metatags = {
        "description": (
            "Balloon decor for Utah cities, parades, Pride events, chambers, county fairs, "
            "and public gatherings. Serving Sandy, Ogden, SLC County, Equality Utah, and more."
        ),
        "og:title": "Civic & Community Events — Locally Twisted",
        "og:description": (
            "Utah balloon decor for city events, parades, Pride organizations, and public gatherings."
        ),
        "og:type": "website",
    }
    context.civic_clients = CIVIC_CLIENTS
    context.civic_proof_stats = CIVIC_PROOF_STATS
    context.civic_photo_proof = CIVIC_PHOTO_PROOF
    context.service_formats = SERVICE_FORMATS
    context.colocated_css = PAGE_CSS
    return context
