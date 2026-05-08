"""Controller for /schools-campuses audience landing page.

Audience: Activity directors, athletic departments, PTAs, college student life,
graduation organizers.

Buyer posture: Spirit-driven, schedule-tight, school colors disciplined, family-friendly.
"""
import frappe

no_cache = 1
sitemap = 1


SCHOOL_CLIENTS = [
    "University of Utah",
    "Weber State University",
    "St. Joseph's High School",
]

# Context items that extend the school story (civic/community cross-overs)
SCHOOL_CONTEXT_EVENTS = [
    "Back-to-school stage installs across the Wasatch Front",
    "Graduation garlands and columns for commencement ceremonies",
    "Spirit-day arches for school community events",
    "Tree House Museum education event decor",
    "Family-friendly community days and school carnivals",
]

SCHOOL_INSTALLS = [
    {
        "title": "Back-to-School Stage",
        "category": "School Event Stage",
        "image": "/assets/locally_twisted/images/portfolio/optimized/school-back-to-school-stage.webp",
        "alt": "Large balloon stage display for a school back-to-school community event, Utah",
    },
    {
        "title": "Back-to-School Stage Display",
        "category": "School Community Stage",
        "image": "/assets/locally_twisted/images/odoo/Parades/Back to school stage display.png",
        "alt": "Outdoor balloon stage display for school event with colorful arch structures",
    },
    {
        "title": "Graduation Garland",
        "category": "Commencement",
        "image": "/assets/locally_twisted/images/portfolio/optimized/school-grad-garland.webp",
        "alt": "Organic balloon garland installed for a graduation commencement ceremony",
    },
    {
        "title": "WSU Corporate Arch & Bouquets",
        "category": "University Sponsor Install",
        "image": "/assets/locally_twisted/images/portfolio/optimized/corporate-wsu-arch-bouquets.webp",
        "alt": "Balloon arch with coordinated bouquets installed at a Weber State University event",
    },
]

SCHOOL_OCCASIONS = [
    {
        "name": "Back-to-School",
        "body": "Stage installs, entrance arches, and photo ops that set the tone before the first bell.",
    },
    {
        "name": "Graduation",
        "body": "Organic garlands, columns, and arches for commencement. Color-matched to regalia, school colors, or both.",
    },
    {
        "name": "Homecoming & Spirit",
        "body": "School-color balloon work for rallies, dances, and spirit weeks. Family-friendly and photographable.",
    },
    {
        "name": "Athletic Events",
        "body": "Entrance arches and sideline decor for game days, championships, and team send-offs.",
    },
    {
        "name": "Campus & Student Life",
        "body": "University event decor — orientation days, student org events, campus fairs, and move-in activations.",
    },
    {
        "name": "PTA & Community Events",
        "body": "School carnivals, fundraisers, and parent events. Balloon twisting available for family-day programs.",
    },
]

PAGE_CSS = """
/* =====================================================================
 * Schools & Campuses audience page — lt-page-schools namespace
 * Sections: hero, installs, occasions, clients, cta
 * ===================================================================== */

/* --- Schools hero (fullbleed) --------------------------------------- */
.lt-page-schools .lt-school-hero {
    position: relative;
    min-height: 220px;
    height: 220px;
    max-height: 280px;
    background-color: var(--lt-navy);
    overflow: hidden;
    display: flex;
    align-items: center;
}
.lt-page-schools .lt-school-hero__image {
    position: absolute;
    inset: 0;
    background-image: url('/assets/locally_twisted/images/portfolio/optimized/school-back-to-school-stage.webp');
    background-size: cover;
    background-position: center;
    background-color: var(--lt-navy);
}
.lt-page-schools .lt-school-hero__image::after {
    content: '';
    position: absolute;
    inset: 0;
    background:
        linear-gradient(90deg, rgba(10,10,11,0.91) 0%, rgba(14,34,64,0.65) 48%, rgba(14,34,64,0.06) 100%),
        linear-gradient(180deg, transparent 0%, rgba(10,10,11,0.28) 100%);
}
.lt-page-schools .lt-school-hero__content {
    position: relative;
    z-index: 1;
    width: 100%;
    max-width: 1280px;
    margin: 0 auto;
    padding: 1.5rem 1rem;
    color: var(--lt-warm-white);
}
.lt-page-schools .lt-school-hero__eyebrow {
    font-family: var(--lt-font-body);
    font-size: 0.74rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--lt-brass);
    margin: 0 0 0.4rem;
}
.lt-page-schools .lt-school-hero__h1 {
    font-family: var(--lt-font-heading);
    font-weight: 700;
    font-size: clamp(1.75rem, 5vw, 2.25rem);
    line-height: 1.05;
    color: var(--lt-warm-white);
    margin: 0 0 0.5rem;
    max-width: 22ch;
}
.lt-page-schools .lt-school-hero__lede {
    font-family: var(--lt-font-body);
    font-size: 0.94rem;
    line-height: 1.45;
    color: rgba(250,247,242,0.9);
    margin: 0 0 0.85rem;
    max-width: 50ch;
}
.lt-page-schools .lt-school-hero__cta {
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
.lt-page-schools .lt-school-hero__cta:hover,
.lt-page-schools .lt-school-hero__cta:focus-visible {
    background-color: var(--lt-navy);
    outline: 2px solid var(--lt-brass);
    outline-offset: 2px;
}
@media (min-width: 768px) {
    .lt-page-schools .lt-school-hero {
        min-height: 250px;
        height: 250px;
        max-height: 300px;
    }
    .lt-page-schools .lt-school-hero__content { padding: 2rem; }
    .lt-page-schools .lt-school-hero__h1 { font-size: 2.5rem; max-width: 28ch; }
}
@media (min-width: 1200px) {
    .lt-page-schools .lt-school-hero {
        min-height: 280px;
        height: 280px;
        max-height: 320px;
    }
    .lt-page-schools .lt-school-hero__h1 { font-size: 2.75rem; }
}

/* --- Intro prose (band / warm white) ------------------------------- */
.lt-page-schools .lt-school-intro {
    background-color: var(--lt-warm-white);
    padding: 3.5rem 1.25rem;
}
.lt-page-schools .lt-school-intro__inner {
    max-width: 760px;
    margin: 0 auto;
}
.lt-page-schools .lt-school-intro__label {
    font-family: var(--lt-font-body);
    font-size: 0.74rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--lt-berry);
    margin: 0 0 0.75rem;
}
.lt-page-schools .lt-school-intro__h2 {
    font-family: var(--lt-font-heading);
    font-size: clamp(1.5rem, 3.5vw, 2.25rem);
    color: var(--lt-ink);
    line-height: 1.1;
    margin: 0 0 1rem;
}
.lt-page-schools .lt-school-intro__body {
    font-family: var(--lt-font-body);
    font-size: 1.0625rem;
    color: var(--lt-soft-gray);
    line-height: 1.65;
    margin: 0 0 1rem;
}
.lt-page-schools .lt-school-intro__brass-rule {
    width: 48px;
    height: 2px;
    background-color: var(--lt-brass);
    margin: 1.5rem 0 0;
    border: none;
}

/* --- Gallery (visual-field / stone) -------------------------------- */
.lt-page-schools .lt-school-gallery {
    background-color: var(--lt-stone);
    padding: 3.5rem 1.25rem;
}
.lt-page-schools .lt-school-gallery__inner {
    max-width: 1400px;
    margin: 0 auto;
}
.lt-page-schools .lt-school-gallery__heading {
    font-family: var(--lt-font-heading);
    font-size: clamp(1.5rem, 3.5vw, 2.25rem);
    color: var(--lt-ink);
    margin: 0 0 0.5rem;
}
.lt-page-schools .lt-school-gallery__subhead {
    font-family: var(--lt-font-body);
    font-size: 1rem;
    color: var(--lt-soft-gray);
    margin: 0 0 2rem;
    max-width: 60ch;
}
.lt-page-schools .lt-school-gallery__grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
}
@media (min-width: 992px) {
    .lt-page-schools .lt-school-gallery__grid {
        grid-template-columns: repeat(4, 1fr);
    }
}
.lt-page-schools .lt-school-gallery__item {
    position: relative;
    overflow: hidden;
    border-radius: 2px;
    background-color: var(--lt-slate);
}
.lt-page-schools .lt-school-gallery__img {
    width: 100%;
    aspect-ratio: 4/3;
    object-fit: cover;
    display: block;
}
.lt-page-schools .lt-school-gallery__cap {
    position: absolute;
    bottom: 0; left: 0; right: 0;
    padding: 0.75rem;
    background: linear-gradient(to top, rgba(10,10,11,0.82) 0%, transparent 100%);
}
.lt-page-schools .lt-school-gallery__cap-cat {
    font-family: var(--lt-font-body);
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--lt-brass);
    margin: 0 0 0.2rem;
}
.lt-page-schools .lt-school-gallery__cap-title {
    font-family: var(--lt-font-heading);
    font-size: 1rem;
    color: var(--lt-warm-white);
    margin: 0;
    line-height: 1.2;
}

/* --- Occasions grid (band / white) --------------------------------- */
.lt-page-schools .lt-school-occasions {
    background-color: var(--lt-white);
    padding: 3.5rem 1.25rem;
}
.lt-page-schools .lt-school-occasions__inner {
    max-width: 1100px;
    margin: 0 auto;
}
.lt-page-schools .lt-school-occasions__h2 {
    font-family: var(--lt-font-heading);
    font-size: clamp(1.5rem, 3vw, 2.25rem);
    color: var(--lt-ink);
    margin: 0 0 0.5rem;
}
.lt-page-schools .lt-school-occasions__lede {
    font-family: var(--lt-font-body);
    font-size: 1rem;
    color: var(--lt-soft-gray);
    margin: 0 0 2.5rem;
    max-width: 60ch;
}
.lt-page-schools .lt-school-occasions__grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1rem;
}
@media (min-width: 600px) {
    .lt-page-schools .lt-school-occasions__grid { grid-template-columns: repeat(2, 1fr); }
}
@media (min-width: 992px) {
    .lt-page-schools .lt-school-occasions__grid { grid-template-columns: repeat(3, 1fr); }
}
.lt-page-schools .lt-school-occasions__card {
    padding: 1.5rem;
    border: 1px solid var(--lt-stone);
    border-radius: 2px;
    background-color: var(--lt-near-white);
}
.lt-page-schools .lt-school-occasions__card-name {
    font-family: var(--lt-font-heading);
    font-size: 1.1875rem;
    color: var(--lt-ink);
    margin: 0 0 0.5rem;
}
.lt-page-schools .lt-school-occasions__card-body {
    font-family: var(--lt-font-body);
    font-size: 0.9375rem;
    color: var(--lt-soft-gray);
    line-height: 1.6;
    margin: 0;
}

/* --- Client band (band / navy) ------------------------------------- */
.lt-page-schools .lt-school-clients {
    background-color: var(--lt-navy);
    padding: 3rem 1.25rem;
}
.lt-page-schools .lt-school-clients__inner {
    max-width: 1000px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.5rem;
    align-items: start;
}
@media (min-width: 768px) {
    .lt-page-schools .lt-school-clients__inner {
        grid-template-columns: auto 1fr;
        gap: 3rem;
        align-items: center;
    }
}
.lt-page-schools .lt-school-clients__label {
    font-family: var(--lt-font-body);
    font-size: 0.74rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--lt-brass);
    margin: 0 0 0.75rem;
}
.lt-page-schools .lt-school-clients__h2 {
    font-family: var(--lt-font-heading);
    font-size: clamp(1.25rem, 2.5vw, 1.875rem);
    color: var(--lt-warm-white);
    margin: 0;
    white-space: nowrap;
}
.lt-page-schools .lt-school-clients__list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}
.lt-page-schools .lt-school-clients__item {
    font-family: var(--lt-font-body);
    font-size: 1rem;
    color: rgba(250,247,242,0.85);
    padding-left: 1rem;
    position: relative;
    line-height: 1.4;
}
.lt-page-schools .lt-school-clients__item::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0.55em;
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background-color: var(--lt-brass);
}

/* --- CTA (fullbleed / ink) ----------------------------------------- */
.lt-page-schools .lt-school-cta {
    background-color: var(--lt-ink);
    padding: 4rem 1.25rem;
    text-align: center;
}
.lt-page-schools .lt-school-cta__inner {
    max-width: 680px;
    margin: 0 auto;
}
.lt-page-schools .lt-school-cta__h2 {
    font-family: var(--lt-font-heading);
    font-size: clamp(1.75rem, 4vw, 2.75rem);
    color: var(--lt-warm-white);
    margin: 0 0 1rem;
    line-height: 1.1;
}
.lt-page-schools .lt-school-cta__body {
    font-family: var(--lt-font-body);
    font-size: 1.0625rem;
    color: rgba(250,247,242,0.8);
    max-width: 50ch;
    margin: 0 auto 1.75rem;
    line-height: 1.55;
}
.lt-page-schools .lt-school-cta__btn {
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
.lt-page-schools .lt-school-cta__btn:hover,
.lt-page-schools .lt-school-cta__btn:focus-visible {
    background-color: var(--lt-crimson);
    outline: 2px solid var(--lt-brass);
    outline-offset: 2px;
}
.lt-page-schools .lt-school-cta__sub {
    margin: 1.25rem 0 0;
    font-family: var(--lt-font-body);
    font-size: 0.875rem;
    color: rgba(250,247,242,0.5);
}
.lt-page-schools .lt-school-cta__sub a {
    color: var(--lt-brass);
    text-decoration: none;
}
.lt-page-schools .lt-school-cta__sub a:hover { text-decoration: underline; }
"""


def get_context(context):
    context.title = "Schools & Campuses — Locally Twisted Balloon Decor"
    context.metatags = {
        "description": (
            "Professional balloon decor for Utah school events, graduation ceremonies, "
            "homecoming, spirit days, and campus activations. Trusted by the University "
            "of Utah, Weber State, and St. Joseph's High School."
        ),
        "og:title": "Schools & Campus Balloon Decor — Locally Twisted",
        "og:description": (
            "School-color installs for graduation, back-to-school, homecoming, and campus events "
            "across the Wasatch Front. University of Utah, Weber State, and more."
        ),
        "og:type": "website",
    }
    context.school_clients = SCHOOL_CLIENTS
    context.school_context_events = SCHOOL_CONTEXT_EVENTS
    context.school_installs = SCHOOL_INSTALLS
    context.school_occasions = SCHOOL_OCCASIONS
    context.colocated_css = PAGE_CSS
    return context
