"""Schools & Campuses audience landing page — /schools-campuses

Buyer: Activity directors, athletic departments, PTAs, college student life,
graduation organizers.

Posture: Spirit-driven, schedule-tight, school-colors disciplined, family-friendly.
"""
import frappe

no_cache = 1
sitemap = 1

SCHOOL_CLIENTS = [
    {"name": "University of Utah", "type": "University", "context": "Athletics & student events"},
    {"name": "Weber State University", "type": "University", "context": "Back-to-school, graduation, athletics"},
    {"name": "St. Joseph's High School", "type": "High School", "context": "School events & spirit"},
]

SCHOOL_PROOF_STATS = [
    {"icon": "school-spirit", "label": "SCHOOL COLORS", "value": "On-Spec", "sub": "Custom color matching for any school palette, mascot, or spirit guide"},
    {"icon": "event-stage", "label": "STAGE READY", "value": "Grad to Spirit", "sub": "Graduation ceremonies, back-to-school stages, athletic events"},
    {"icon": "delivery-install", "label": "SCHEDULE TIGHT", "value": "Load-In & Out", "sub": "We work around bell schedules, gymnasium access, and AV setups"},
    {"icon": "professional", "label": "FAMILY-SAFE", "value": "All-Ages Events", "sub": "K–12, university, community family events — appropriate for every crowd"},
]

SCHOOL_PHOTO_PROOF = [
    {
        "image": "/assets/locally_twisted/images/portfolio/optimized/school-back-to-school-stage.webp",
        "alt": "Large balloon stage backdrop for a school back-to-school event",
        "caption": "Back-to-school stage — large backdrop install",
        "client": "Weber State University",
    },
    {
        "image": "/assets/locally_twisted/images/portfolio/optimized/school-grad-garland.webp",
        "alt": "Organic balloon garland for graduation ceremony",
        "caption": "Graduation garland — ceremony stage decor",
        "client": "University event",
    },
    {
        "image": "/assets/locally_twisted/images/portfolio/optimized/corporate-wsu-arch-bouquets.webp",
        "alt": "Weber State University branded arch with balloon bouquets",
        "caption": "WSU branded arch & welcome bouquets — campus event",
        "client": "Weber State University",
    },
    {
        "image": "C:/Users/baenb/projects/locally-twisted-odoo/assets/image assets/photos for website/Photo opts/Back to school stage display.png",
        "alt": "Back to school balloon stage display",
        "caption": "Back-to-school stage display — full install",
        "client": "Campus event",
    },
    {
        "image": "C:/Users/baenb/projects/locally-twisted-odoo/assets/image assets/photos for website/Photo opts/Back to school stage display 2.png",
        "alt": "Back to school balloon stage display variation",
        "caption": "Stage backdrop — school spirit colors",
        "client": "Campus event",
    },
    {
        "image": "C:/Users/baenb/projects/locally-twisted-odoo/assets/image assets/photos for website/football/UofU football.png",
        "alt": "University of Utah football event balloon decor",
        "caption": "UofU athletics — football event decor",
        "client": "University of Utah",
    },
]

SCHOOL_EVENT_TYPES = [
    {
        "icon": "event-stage",
        "name": "Graduation Ceremonies",
        "desc": "Stage garlands, column pairs, arch entries, and photo-op backdrops for commencement events. Color-matched to school palette.",
    },
    {
        "icon": "school-spirit",
        "name": "Back-to-School Events",
        "desc": "Large backdrop installs for first-day celebrations, orientation fairs, and welcome events. Weber State is a returning client for back-to-school season.",
    },
    {
        "icon": "balloon-arch",
        "name": "Athletic Events & Pep Assemblies",
        "desc": "Spirit arches, tunnel arches for team entry, and gym or field decor for pep rallies, homecoming, and athletic season openers.",
    },
    {
        "icon": "balloon-cluster",
        "name": "Campus & Classroom Events",
        "desc": "Smaller-scale installs for student life fairs, club events, welcome weeks, and outdoor campus gatherings. Sized to fit indoor spaces without ceiling permits.",
    },
]

PAGE_CSS = """
/* ====================================================================
 * Schools & Campuses page — .lt-page-school scoped
 * Container modes:
 *   hero=fullbleed, stats=fullbleed, photos=band, clients=contained,
 *   event-types=band, note=band(sandstone), cta=fullbleed
 * ==================================================================== */

/* --- hero ----------------------------------------------------------- */
.lt-page-school .lt-school-hero {
    position: relative;
    height: 220px;
    min-height: 220px;
    max-height: 220px;
    background-color: var(--lt-navy);
    overflow: hidden;
    display: flex;
    align-items: center;
}
.lt-page-school .lt-school-hero__bg {
    position: absolute;
    inset: 0;
    background-image: url('/assets/locally_twisted/images/portfolio/optimized/school-back-to-school-stage.webp');
    background-size: cover;
    background-position: center top;
}
.lt-page-school .lt-school-hero__bg::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, rgba(10,10,11,0.88) 0%, rgba(14,34,64,0.7) 46%, rgba(14,34,64,0.1) 100%);
}
.lt-page-school .lt-school-hero__content {
    position: relative;
    z-index: 1;
    width: 100%;
    max-width: 1280px;
    margin: 0 auto;
    padding: 1.5rem 1rem;
}
.lt-page-school .lt-school-hero__eyebrow {
    font-family: var(--lt-font-body);
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--lt-brass);
    margin: 0 0 0.35rem;
}
.lt-page-school .lt-school-hero__h1 {
    font-family: var(--lt-font-heading);
    font-size: clamp(1.75rem, 4.5vw, 2.2rem);
    font-weight: 700;
    color: var(--lt-white);
    margin: 0 0 0.45rem;
    max-width: 24ch;
    line-height: 1.05;
}
.lt-page-school .lt-school-hero__lede {
    font-family: var(--lt-font-body);
    font-size: 0.9rem;
    color: rgba(250,247,242,0.92);
    margin: 0 0 0.75rem;
    max-width: 50ch;
    line-height: 1.35;
}
.lt-page-school .lt-school-hero__cta {
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
.lt-page-school .lt-school-hero__cta:hover,
.lt-page-school .lt-school-hero__cta:focus-visible {
    background-color: var(--lt-navy);
    outline: 2px solid var(--lt-brass);
    outline-offset: 2px;
}
@media (min-width: 768px) {
    .lt-page-school .lt-school-hero { height: 250px; min-height: 250px; max-height: 250px; }
    .lt-page-school .lt-school-hero__content { padding: 2rem; }
    .lt-page-school .lt-school-hero__h1 { font-size: 2.6rem; }
}
@media (min-width: 1200px) {
    .lt-page-school .lt-school-hero { height: 280px; min-height: 280px; max-height: 280px; }
}

/* --- stats band ---------------------------------------------------- */
.lt-page-school .lt-school-stats {
    background-color: var(--lt-slate);
    padding: 2.5rem 1.25rem;
}
.lt-page-school .lt-school-stats__inner {
    max-width: 1200px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem 1rem;
}
@media (min-width: 768px) {
    .lt-page-school .lt-school-stats__inner {
        grid-template-columns: repeat(4, 1fr);
        gap: 1.5rem;
    }
}
.lt-page-school .lt-school-stat {
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
}
.lt-page-school .lt-school-stat__icon {
    width: 44px;
    height: 44px;
    color: var(--lt-brass);
}
.lt-page-school .lt-school-stat__label {
    font-family: var(--lt-font-body);
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--lt-brass);
}
.lt-page-school .lt-school-stat__value {
    font-family: var(--lt-font-heading);
    font-size: 1.625rem;
    color: var(--lt-white);
    line-height: 1.1;
}
.lt-page-school .lt-school-stat__sub {
    font-family: var(--lt-font-body);
    font-size: 0.78rem;
    color: rgba(250,247,242,0.62);
    line-height: 1.3;
    max-width: 18ch;
}

/* --- photo proof ---------------------------------------------------- */
.lt-page-school .lt-school-photos {
    background-color: var(--lt-warm-white);
    padding: 4rem 1.25rem;
}
.lt-page-school .lt-school-photos__inner {
    max-width: 1280px;
    margin: 0 auto;
}
.lt-page-school .lt-school-photos__heading {
    font-family: var(--lt-font-heading);
    font-size: 2rem;
    color: var(--lt-ink);
    margin: 0 0 0.5rem;
}
.lt-page-school .lt-school-photos__lede {
    font-family: var(--lt-font-body);
    font-size: 1rem;
    color: var(--lt-soft-gray);
    margin: 0 0 2.5rem;
    max-width: 58ch;
    line-height: 1.5;
}
.lt-page-school .lt-school-photos__grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
}
@media (min-width: 768px) {
    .lt-page-school .lt-school-photos__grid {
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
    }
}
.lt-page-school .lt-school-photo {
    position: relative;
    overflow: hidden;
    border-radius: 3px;
    aspect-ratio: 4/3;
    background-color: var(--lt-stone);
}
.lt-page-school .lt-school-photo img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}
.lt-page-school .lt-school-photo__caption {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 0.5rem 0.75rem;
    background: linear-gradient(to top, rgba(10,10,11,0.78) 0%, transparent 100%);
    font-family: var(--lt-font-body);
    font-size: 0.7rem;
    color: rgba(250,247,242,0.92);
    line-height: 1.3;
}

/* --- named clients — contained ------------------------------------- */
.lt-page-school .lt-school-clients {
    background-color: var(--lt-navy);
    padding: 3rem 1.25rem;
}
.lt-page-school .lt-school-clients__inner {
    max-width: 1200px;
    margin: 0 auto;
}
.lt-page-school .lt-school-clients__eyebrow {
    font-family: var(--lt-font-body);
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--lt-brass);
    margin: 0 0 0.75rem;
}
.lt-page-school .lt-school-clients__heading {
    font-family: var(--lt-font-heading);
    font-size: 1.75rem;
    color: var(--lt-white);
    margin: 0 0 0.5rem;
    line-height: 1.15;
}
.lt-page-school .lt-school-clients__sub {
    font-family: var(--lt-font-body);
    font-size: 0.9rem;
    color: rgba(250,247,242,0.65);
    margin: 0 0 2rem;
    max-width: 56ch;
    line-height: 1.5;
}
.lt-page-school .lt-school-clients__list {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1rem;
    list-style: none;
    padding: 0;
    margin: 0;
}
@media (min-width: 768px) {
    .lt-page-school .lt-school-clients__list {
        grid-template-columns: repeat(3, 1fr);
        gap: 1.25rem;
    }
}
.lt-page-school .lt-school-client-card {
    background-color: rgba(250,247,242,0.06);
    border: 1px solid rgba(184,154,91,0.2);
    border-radius: 3px;
    padding: 1.25rem 1.5rem;
}
.lt-page-school .lt-school-client-card__name {
    font-family: var(--lt-font-heading);
    font-size: 1.25rem;
    color: var(--lt-white);
    margin: 0 0 0.25rem;
}
.lt-page-school .lt-school-client-card__type {
    font-family: var(--lt-font-body);
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--lt-brass);
    margin: 0 0 0.4rem;
}
.lt-page-school .lt-school-client-card__context {
    font-family: var(--lt-font-body);
    font-size: 0.85rem;
    color: rgba(250,247,242,0.65);
    margin: 0;
    line-height: 1.4;
}

/* --- event types ---------------------------------------------------- */
.lt-page-school .lt-school-events {
    background-color: var(--lt-warm-white);
    padding: 4rem 1.25rem;
}
.lt-page-school .lt-school-events__inner {
    max-width: 1200px;
    margin: 0 auto;
}
.lt-page-school .lt-school-events__heading {
    font-family: var(--lt-font-heading);
    font-size: 1.875rem;
    color: var(--lt-ink);
    margin: 0 0 0.5rem;
}
.lt-page-school .lt-school-events__lede {
    font-family: var(--lt-font-body);
    font-size: 1rem;
    color: var(--lt-soft-gray);
    margin: 0 0 2.5rem;
    max-width: 54ch;
    line-height: 1.5;
}
.lt-page-school .lt-school-events__grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.25rem;
}
@media (min-width: 768px) {
    .lt-page-school .lt-school-events__grid {
        grid-template-columns: 1fr 1fr;
        gap: 1.5rem;
    }
}
.lt-page-school .lt-school-event-card {
    display: flex;
    gap: 1rem;
    padding: 1.5rem;
    background-color: var(--lt-white);
    border: 1px solid var(--lt-stone);
    border-radius: 3px;
    align-items: flex-start;
}
.lt-page-school .lt-school-event-card__icon {
    width: 40px;
    height: 40px;
    flex-shrink: 0;
    color: var(--lt-brass);
}
.lt-page-school .lt-school-event-card__name {
    font-family: var(--lt-font-heading);
    font-size: 1.25rem;
    color: var(--lt-ink);
    margin: 0 0 0.4rem;
}
.lt-page-school .lt-school-event-card__desc {
    font-family: var(--lt-font-body);
    font-size: 0.9rem;
    color: var(--lt-soft-gray);
    margin: 0;
    line-height: 1.5;
}

/* --- practical note ------------------------------------------------ */
.lt-page-school .lt-school-note {
    background-color: var(--lt-sandstone);
    padding: 2.75rem 1.25rem;
}
.lt-page-school .lt-school-note__inner {
    max-width: 820px;
    margin: 0 auto;
}
.lt-page-school .lt-school-note__heading {
    font-family: var(--lt-font-heading);
    font-size: 1.5rem;
    color: var(--lt-ink);
    margin: 0 0 0.75rem;
}
.lt-page-school .lt-school-note__body {
    font-family: var(--lt-font-body);
    font-size: 0.95rem;
    color: var(--lt-ink);
    opacity: 0.78;
    margin: 0;
    line-height: 1.6;
    max-width: 64ch;
}

/* --- CTA ------------------------------------------------------------ */
.lt-page-school .lt-school-cta {
    background-color: var(--lt-navy);
    padding: 4rem 1.25rem;
    text-align: center;
}
.lt-page-school .lt-school-cta__inner {
    max-width: 680px;
    margin: 0 auto;
}
.lt-page-school .lt-school-cta__heading {
    font-family: var(--lt-font-heading);
    font-size: 2.25rem;
    color: var(--lt-white);
    margin: 0 0 0.75rem;
    line-height: 1.1;
}
.lt-page-school .lt-school-cta__body {
    font-family: var(--lt-font-body);
    font-size: 1rem;
    color: rgba(250,247,242,0.78);
    margin: 0 0 2rem;
    line-height: 1.55;
}
.lt-page-school .lt-school-cta__btn {
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
.lt-page-school .lt-school-cta__btn:hover,
.lt-page-school .lt-school-cta__btn:focus-visible {
    background-color: var(--lt-ink);
    outline: 2px solid var(--lt-brass);
    outline-offset: 2px;
}
"""


def get_context(context):
    context.title = "Schools & Campuses — Locally Twisted"
    context.metatags = {
        "description": (
            "Balloon decor for Utah schools and universities — graduation ceremonies, "
            "back-to-school events, athletic events, and campus spirit. "
            "University of Utah, Weber State, St. Joseph's High School."
        ),
        "og:title": "Schools & Campuses — Locally Twisted",
        "og:description": (
            "Spirit-driven, school-color-matched balloon decor for Utah K–12 and university events."
        ),
        "og:type": "website",
    }
    context.school_clients = SCHOOL_CLIENTS
    context.school_proof_stats = SCHOOL_PROOF_STATS
    context.school_photo_proof = SCHOOL_PHOTO_PROOF
    context.school_event_types = SCHOOL_EVENT_TYPES
    context.colocated_css = PAGE_CSS
    return context
