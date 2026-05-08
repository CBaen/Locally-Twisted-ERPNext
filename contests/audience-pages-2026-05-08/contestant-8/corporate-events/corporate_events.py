"""
Corporate Events audience page controller.

Route: /corporate-events
Audience: Marketing teams, brand activations, store openings, broadcaster events,
bank/credit-union community days, corporate parties.
Buyer posture: Brand-safe, on-color, repeatable, professional, billable through AP.
"""

no_cache = 1
sitemap = 1

# Named corporate clients from the approved roster.
CORPORATE_CLIENTS = [
    "KSL", "KUTV", "FOX13", "Paramount", "Ancestry",
    "Zions Bank", "America First Credit Union", "Fidelity", "Morgan Stanley",
    "Utah Jazz", "Chick-Fil-A", "Texas Roadhouse", "Applebee's", "Chili's",
    "Honey Baked Ham", "PotBelly", "IHC", "Mountain Star Medical",
    "Young Automotive", "LVT", "Clear", "Henry Schein",
    "Museum of Illusion", "Lux", "SeaQuest",
    "Alpine Events", "In the Events", "FanX", "The Boiler Room",
]

# Proof photos from portfolio libraries.
CORPORATE_PHOTOS = [
    {
        "src": "/assets/locally_twisted/images/portfolio/optimized/corporate-logo-arch.webp",
        "alt": "Corporate branded balloon arch at an event entrance",
        "label": "Branded Entrance Arch",
    },
    {
        "src": "/assets/locally_twisted/images/portfolio/optimized/corporate-weberstock-photo-opt.webp",
        "alt": "Large branded balloon photo backdrop at a corporate festival event",
        "label": "Festival Brand Moment",
    },
    {
        "src": "/assets/locally_twisted/images/portfolio/optimized/corporate-wsu-arch-bouquets.webp",
        "alt": "Balloon arch and bouquet arrangement at a corporate or university event",
        "label": "Event Arch + Bouquets",
    },
]

# Proof icons for corporate buyers.
CORPORATE_ICONS = [
    {
        "asset": "/assets/locally_twisted/icons/brand/corporate-entrance.svg",
        "label": "BRAND SAFE",
        "desc": "On-color installs. Your brand guide, your color palette, your entrance.",
    },
    {
        "asset": "/assets/locally_twisted/icons/brand/trusted-partner.svg",
        "label": "TRUSTED PARTNER",
        "desc": "Repeat clients across Utah's largest employers and broadcasters.",
    },
    {
        "asset": "/assets/locally_twisted/icons/brand/professional.svg",
        "label": "PROFESSIONAL",
        "desc": "On-time. Documented. AP-invoiceable. Clean worksite on exit.",
    },
    {
        "asset": "/assets/locally_twisted/icons/brand/delivery-install.svg",
        "label": "FULL SERVICE",
        "desc": "Delivery, setup, and teardown. No leftover logistics for your team.",
    },
]

PAGE_CSS = """
/* ======================================================
 * Corporate Events audience page — .lt-page-corp root
 * Container modes per section:
 *   hero           : fullbleed
 *   clients-band   : fullbleed
 *   photo-row      : band
 *   case-study     : band
 *   services       : band
 *   icons          : fullbleed
 *   cta            : fullbleed
 * ====================================================== */

/* --- Hero ------------------------------------------------------------ */
.lt-page-corp .lt-corp-hero {
    position: relative;
    min-height: 220px;
    height: 220px;
    max-height: 220px;
    background-color: var(--lt-ink);
    overflow: hidden;
    display: flex;
    align-items: center;
}
.lt-page-corp .lt-corp-hero__image {
    position: absolute;
    inset: 0;
    background-image: url('/assets/locally_twisted/images/portfolio/optimized/corporate-logo-arch.webp');
    background-size: cover;
    background-position: center;
}
.lt-page-corp .lt-corp-hero__image::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, rgba(10,10,11,0.92) 0%, rgba(14,34,64,0.75) 50%, rgba(14,34,64,0.08) 100%);
}
.lt-page-corp .lt-corp-hero__content {
    position: relative;
    z-index: 1;
    width: 100%;
    max-width: 1280px;
    margin: 0 auto;
    padding: 1.5rem 1rem;
    color: var(--lt-warm-white);
}
.lt-page-corp .lt-corp-hero__eyebrow {
    font-family: var(--lt-font-body);
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--lt-brass);
    margin: 0 0 0.4rem;
}
.lt-page-corp .lt-corp-hero__title {
    font-family: var(--lt-font-heading);
    font-size: 1.9rem;
    font-weight: 700;
    line-height: 1.05;
    color: var(--lt-warm-white);
    margin: 0 0 0.6rem;
    max-width: 20ch;
}
.lt-page-corp .lt-corp-hero__tagline {
    font-family: var(--lt-font-body);
    font-size: 0.88rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--lt-brass);
    margin: 0 0 0.5rem;
}
.lt-page-corp .lt-corp-hero__lede {
    font-family: var(--lt-font-body);
    font-size: 0.9rem;
    line-height: 1.4;
    color: rgba(250,247,242,0.88);
    margin: 0 0 0.75rem;
    max-width: 52ch;
}
.lt-page-corp .lt-corp-hero__cta {
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
.lt-page-corp .lt-corp-hero__cta:hover,
.lt-page-corp .lt-corp-hero__cta:focus-visible {
    background-color: var(--lt-navy);
    outline: 2px solid var(--lt-brass);
    outline-offset: 2px;
}
@media (min-width: 768px) {
    .lt-page-corp .lt-corp-hero { min-height: 250px; height: 250px; max-height: 250px; }
    .lt-page-corp .lt-corp-hero__content { padding: 2rem; }
    .lt-page-corp .lt-corp-hero__title { font-size: 2.6rem; max-width: 26ch; }
    .lt-page-corp .lt-corp-hero__lede { font-size: 1rem; }
}
@media (min-width: 1200px) {
    .lt-page-corp .lt-corp-hero { min-height: 280px; height: 280px; max-height: 280px; }
    .lt-page-corp .lt-corp-hero__title { font-size: 2.9rem; }
}

/* --- Clients band ---------------------------------------------------- */
.lt-page-corp .lt-corp-clients {
    background-color: var(--lt-slate);
    padding: 2.5rem 1rem;
    text-align: center;
}
.lt-page-corp .lt-corp-clients__inner {
    max-width: 1100px;
    margin: 0 auto;
}
.lt-page-corp .lt-corp-clients__heading {
    font-family: var(--lt-font-body);
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--lt-brass);
    margin: 0 0 1.25rem;
}
.lt-page-corp .lt-corp-clients__list {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 0.5rem 1.25rem;
    list-style: none;
    margin: 0;
    padding: 0;
}
.lt-page-corp .lt-corp-clients__list li {
    font-family: var(--lt-font-body);
    font-size: 0.875rem;
    font-weight: 500;
    color: rgba(250,247,242,0.82);
    white-space: nowrap;
}
.lt-page-corp .lt-corp-clients__list li + li::before {
    content: '·';
    margin-right: 1.25rem;
    color: var(--lt-brass);
    opacity: 0.5;
}

/* --- Photo row ------------------------------------------------------- */
.lt-page-corp .lt-corp-photos {
    background-color: var(--lt-warm-white);
    padding: 3.5rem 1rem;
}
.lt-page-corp .lt-corp-photos__inner {
    max-width: 1200px;
    margin: 0 auto;
}
.lt-page-corp .lt-corp-photos__heading {
    font-family: var(--lt-font-heading);
    font-size: 2rem;
    color: var(--lt-ink);
    text-align: center;
    margin: 0 0 0.5rem;
}
.lt-page-corp .lt-corp-photos__lede {
    font-family: var(--lt-font-body);
    font-size: 0.95rem;
    color: var(--lt-soft-gray);
    text-align: center;
    max-width: 54ch;
    margin: 0 auto 2.25rem;
}
.lt-page-corp .lt-corp-photos__grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1rem;
}
@media (min-width: 768px) {
    .lt-page-corp .lt-corp-photos__grid { grid-template-columns: repeat(3,1fr); }
}
.lt-page-corp .lt-corp-photos__item {
    position: relative;
    aspect-ratio: 4/3;
    overflow: hidden;
    border-radius: 2px;
}
.lt-page-corp .lt-corp-photos__item img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}
.lt-page-corp .lt-corp-photos__label {
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
.lt-page-corp .lt-corp-case {
    background-color: var(--lt-stone);
    padding: 3.5rem 1rem;
}
.lt-page-corp .lt-corp-case__inner {
    max-width: 900px;
    margin: 0 auto;
}
.lt-page-corp .lt-corp-case__eyebrow {
    font-family: var(--lt-font-body);
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--lt-crimson);
    margin: 0 0 0.5rem;
}
.lt-page-corp .lt-corp-case__heading {
    font-family: var(--lt-font-heading);
    font-size: 1.75rem;
    color: var(--lt-ink);
    margin: 0 0 1.25rem;
    line-height: 1.15;
}
@media (min-width: 768px) {
    .lt-page-corp .lt-corp-case__heading { font-size: 2.25rem; }
}
.lt-page-corp .lt-corp-case__body p {
    font-family: var(--lt-font-body);
    font-size: 1rem;
    color: var(--lt-soft-gray);
    line-height: 1.7;
    margin: 0 0 1rem;
    max-width: 72ch;
}

/* --- Service notes --------------------------------------------------- */
.lt-page-corp .lt-corp-services {
    background-color: var(--lt-white);
    padding: 3.5rem 1rem;
}
.lt-page-corp .lt-corp-services__inner {
    max-width: 1100px;
    margin: 0 auto;
}
.lt-page-corp .lt-corp-services__heading {
    font-family: var(--lt-font-heading);
    font-size: 1.875rem;
    color: var(--lt-ink);
    margin: 0 0 0.5rem;
    text-align: center;
}
.lt-page-corp .lt-corp-services__lede {
    font-family: var(--lt-font-body);
    font-size: 0.95rem;
    color: var(--lt-soft-gray);
    text-align: center;
    max-width: 54ch;
    margin: 0 auto 2.25rem;
}
.lt-page-corp .lt-corp-services__grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.25rem;
}
@media (min-width: 768px) {
    .lt-page-corp .lt-corp-services__grid { grid-template-columns: repeat(2,1fr); gap: 1.5rem; }
}
@media (min-width: 1200px) {
    .lt-page-corp .lt-corp-services__grid { grid-template-columns: repeat(4,1fr); }
}
.lt-page-corp .lt-corp-services__card {
    border: 1px solid var(--lt-stone);
    border-radius: 2px;
    padding: 1.5rem;
    background-color: var(--lt-warm-white);
    border-left: 3px solid var(--lt-navy);
}
.lt-page-corp .lt-corp-services__card-name {
    font-family: var(--lt-font-body);
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--lt-navy);
    margin: 0 0 0.5rem;
}
.lt-page-corp .lt-corp-services__card-desc {
    font-family: var(--lt-font-body);
    font-size: 0.925rem;
    color: var(--lt-soft-gray);
    line-height: 1.6;
    margin: 0;
}

/* --- Icons band ------------------------------------------------------ */
.lt-page-corp .lt-corp-icons {
    background-color: var(--lt-ink);
    padding: 2.75rem 1rem;
}
.lt-page-corp .lt-corp-icons__inner {
    max-width: 1100px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 2rem 1.5rem;
}
@media (min-width: 768px) {
    .lt-page-corp .lt-corp-icons__inner { grid-template-columns: repeat(4,1fr); gap: 1.5rem; }
}
.lt-page-corp .lt-corp-icons__item { text-align: center; }
.lt-page-corp .lt-corp-icons__img {
    width: 48px; height: 48px;
    color: var(--lt-brass);
    margin: 0 auto 0.75rem;
    display: block;
}
.lt-page-corp .lt-corp-icons__label {
    font-family: var(--lt-font-body);
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--lt-brass);
    margin: 0 0 0.35rem;
    display: block;
}
.lt-page-corp .lt-corp-icons__desc {
    font-family: var(--lt-font-body);
    font-size: 0.825rem;
    color: rgba(250,247,242,0.75);
    line-height: 1.5;
    margin: 0;
}

/* --- CTA ------------------------------------------------------------ */
.lt-page-corp .lt-corp-cta {
    background-color: var(--lt-navy);
    padding: 4rem 1rem;
    text-align: center;
}
.lt-page-corp .lt-corp-cta__inner {
    max-width: 680px;
    margin: 0 auto;
}
.lt-page-corp .lt-corp-cta__heading {
    font-family: var(--lt-font-heading);
    font-size: 2.25rem;
    color: var(--lt-warm-white);
    margin: 0 0 0.75rem;
    line-height: 1.15;
}
@media (min-width: 768px) {
    .lt-page-corp .lt-corp-cta__heading { font-size: 2.75rem; }
}
.lt-page-corp .lt-corp-cta__body {
    font-family: var(--lt-font-body);
    font-size: 1rem;
    color: rgba(250,247,242,0.82);
    line-height: 1.6;
    max-width: 56ch;
    margin: 0 auto 1.75rem;
}
.lt-page-corp .lt-corp-cta__button {
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
.lt-page-corp .lt-corp-cta__button:hover,
.lt-page-corp .lt-corp-cta__button:focus-visible {
    background-color: var(--lt-ink);
    outline: 2px solid var(--lt-brass);
    outline-offset: 2px;
}
"""


def get_context(context):
    context.title = "Corporate Events — Locally Twisted Utah Balloon Decor"
    context.metatags = {
        "description": (
            "Brand-safe, on-color balloon decor for Utah corporate events, brand activations, "
            "store openings, and company gatherings. Trusted by KSL, Utah Jazz, Zions Bank, and more."
        ),
        "og:title": "Corporate Event Balloon Decor — Locally Twisted",
        "og:description": (
            "Professional balloon installations for Utah's corporate buyers. "
            "Brand-safe. Repeatable. AP-invoiceable."
        ),
        "og:type": "website",
    }
    context.corporate_clients = CORPORATE_CLIENTS
    context.corporate_photos = CORPORATE_PHOTOS
    context.corporate_icons = CORPORATE_ICONS
    context.colocated_css = PAGE_CSS
    return context
