"""Corporate Events audience landing page — /corporate-events

Buyer: Marketing teams, brand activations, store openings, broadcaster events,
bank/credit-union community days, corporate parties.

Posture: Brand-safe, on-color, repeatable, professional, billable through AP.
"""
import frappe

no_cache = 1
sitemap = 1

CORP_CLIENTS = [
    {"name": "Ancestry", "category": "Tech & Data"},
    {"name": "Megaplex Theatres", "category": "Entertainment"},
    {"name": "Paramount", "category": "Entertainment"},
    {"name": "KSL", "category": "Broadcast Media"},
    {"name": "KUTV", "category": "Broadcast Media"},
    {"name": "FOX13", "category": "Broadcast Media"},
    {"name": "LVT", "category": "Tech & SaaS"},
    {"name": "Clear", "category": "Tech & SaaS"},
    {"name": "Henry Schein", "category": "Healthcare & Medical"},
    {"name": "Intermountain Health (IHC)", "category": "Healthcare & Medical"},
    {"name": "Mountain Star Medical", "category": "Healthcare & Medical"},
    {"name": "Museum of Illusion", "category": "Attractions & Hospitality"},
    {"name": "Lux", "category": "Attractions & Hospitality"},
    {"name": "SeaQuest", "category": "Attractions & Hospitality"},
    {"name": "Zions Bank", "category": "Financial Services"},
    {"name": "America First Credit Union", "category": "Financial Services"},
    {"name": "Fidelity", "category": "Financial Services"},
    {"name": "Morgan Stanley", "category": "Financial Services"},
    {"name": "Utah Jazz", "category": "Sports & Entertainment"},
    {"name": "Young Automotive", "category": "Automotive"},
    {"name": "Chick-Fil-A", "category": "Food & Hospitality"},
    {"name": "Texas Roadhouse", "category": "Food & Hospitality"},
    {"name": "Applebee's", "category": "Food & Hospitality"},
    {"name": "Chili's", "category": "Food & Hospitality"},
    {"name": "Honey Baked Ham", "category": "Food & Hospitality"},
    {"name": "PotBelly", "category": "Food & Hospitality"},
    {"name": "Alpine Events", "category": "Event Production"},
    {"name": "In the Events", "category": "Event Production"},
    {"name": "FanX", "category": "Conventions & Expos"},
    {"name": "The Boiler Room", "category": "Venue"},
]

CORP_PROOF_STATS = [
    {"icon": "corporate-entrance", "label": "BRAND-SAFE", "value": "On-Color", "sub": "Custom-matched to your brand palette or Pantone reference"},
    {"icon": "trusted-partner", "label": "TRUSTED PARTNER", "value": "AP Ready", "sub": "Clean invoicing, vendor setup documentation, and purchase order support"},
    {"icon": "professional", "label": "PROFESSIONAL", "value": "Insured Install", "sub": "On-site, on-time, fully managed from load-in to strike"},
    {"icon": "delivery-install", "label": "REPEATABLE", "value": "Return Clients", "sub": "FanX, Chick-Fil-A, IHC, and Utah Jazz return event after event"},
]

CORP_PHOTO_PROOF = [
    {
        "image": "/assets/locally_twisted/images/portfolio/optimized/corporate-logo-arch.webp",
        "alt": "Custom logo balloon arch at corporate event entrance",
        "caption": "Logo arch — branded entrance install",
        "client": "Corporate activation",
        "highlight": True,
    },
    {
        "image": "/assets/locally_twisted/images/portfolio/optimized/corporate-weberstock-photo-opt.webp",
        "alt": "Large event photo backdrop at Weberstock branded festival",
        "caption": "Photo moment — Weberstock festival, Weber State",
        "client": "Corporate festival",
        "highlight": False,
    },
    {
        "image": "/assets/locally_twisted/images/portfolio/optimized/corporate-wsu-arch-bouquets.webp",
        "alt": "WSU branded arch with balloon bouquets at university event",
        "caption": "WSU arch & bouquet arrangement — university event",
        "client": "Weber State University",
        "highlight": False,
    },
    {
        "image": "C:/Users/baenb/projects/locally-twisted-odoo/assets/image assets/photos for website/themed decor/Logo arch.png",
        "alt": "Custom corporate logo arch installation",
        "caption": "Branded logo arch — retail activation",
        "client": "Corporate brand activation",
        "highlight": False,
    },
    {
        "image": "C:/Users/baenb/projects/locally-twisted-odoo/assets/image assets/photos for website/latex free decor/ihc heart columns latex free.png",
        "alt": "IHC branded latex-free heart columns at healthcare event",
        "caption": "IHC — latex-free heart column pair, healthcare event",
        "client": "Intermountain Health",
        "highlight": False,
    },
]

CORP_SERVICE_CARDS = [
    {
        "icon": "corporate-entrance",
        "name": "Branded Entrances",
        "desc": "Logo arches, column pairs, and entry markers sized for lobbies, storefronts, and outdoor grand openings. On-color to your brand spec.",
    },
    {
        "icon": "event-stage",
        "name": "Stage & Broadcast Backdrops",
        "desc": "Clean, camera-ready backdrops for on-air events, broadcasts, press moments, and conference main stages. KSL, KUTV, and FOX13 have used Locally Twisted for broadcast-adjacent installs.",
    },
    {
        "icon": "balloon-arch",
        "name": "Activation & Photo Moments",
        "desc": "Branded photo ops, experiential arches, and interactive moments for retail activations, conventions, and expos. FanX has relied on Locally Twisted for convention-scale installs.",
    },
    {
        "icon": "trusted-partner",
        "name": "Latex-Free Options",
        "desc": "Foil-only and latex-free configurations for healthcare environments, corporate wellness events, and facilities with allergy policies. IHC and Mountain Star have used latex-free installs.",
    },
]

PAGE_CSS = """
/* ====================================================================
 * Corporate Events page — .lt-page-corp scoped
 * Container modes:
 *   hero=fullbleed, stats=fullbleed, photos=band, roster=fullbleed,
 *   services=band, trust-note=contained, cta=fullbleed
 * ==================================================================== */

/* --- hero ----------------------------------------------------------- */
.lt-page-corp .lt-corp-hero {
    position: relative;
    height: 220px;
    min-height: 220px;
    max-height: 220px;
    background-color: var(--lt-slate);
    overflow: hidden;
    display: flex;
    align-items: center;
}
.lt-page-corp .lt-corp-hero__bg {
    position: absolute;
    inset: 0;
    background-image: url('/assets/locally_twisted/images/portfolio/optimized/corporate-logo-arch.webp');
    background-size: cover;
    background-position: center;
}
.lt-page-corp .lt-corp-hero__bg::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, rgba(10,10,11,0.9) 0%, rgba(47,58,74,0.72) 48%, rgba(47,58,74,0.12) 100%);
}
.lt-page-corp .lt-corp-hero__content {
    position: relative;
    z-index: 1;
    width: 100%;
    max-width: 1280px;
    margin: 0 auto;
    padding: 1.5rem 1rem;
}
.lt-page-corp .lt-corp-hero__eyebrow {
    font-family: var(--lt-font-body);
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--lt-brass);
    margin: 0 0 0.35rem;
}
.lt-page-corp .lt-corp-hero__h1 {
    font-family: var(--lt-font-heading);
    font-size: clamp(1.75rem, 4.5vw, 2.2rem);
    font-weight: 700;
    color: var(--lt-white);
    margin: 0 0 0.45rem;
    max-width: 26ch;
    line-height: 1.05;
}
.lt-page-corp .lt-corp-hero__lede {
    font-family: var(--lt-font-body);
    font-size: 0.9rem;
    color: rgba(250,247,242,0.92);
    margin: 0 0 0.75rem;
    max-width: 52ch;
    line-height: 1.35;
}
.lt-page-corp .lt-corp-hero__cta {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.6rem 1.1rem;
    background-color: var(--lt-navy);
    color: var(--lt-white);
    text-decoration: none;
    font-family: var(--lt-font-body);
    font-weight: 700;
    font-size: 0.85rem;
    border-radius: 2px;
    min-height: 44px;
    border: 1px solid rgba(184,154,91,0.45);
}
.lt-page-corp .lt-corp-hero__cta:hover,
.lt-page-corp .lt-corp-hero__cta:focus-visible {
    background-color: var(--lt-crimson);
    border-color: transparent;
    outline: 2px solid var(--lt-brass);
    outline-offset: 2px;
}
@media (min-width: 768px) {
    .lt-page-corp .lt-corp-hero { height: 250px; min-height: 250px; max-height: 250px; }
    .lt-page-corp .lt-corp-hero__content { padding: 2rem; }
    .lt-page-corp .lt-corp-hero__h1 { font-size: 2.6rem; }
}
@media (min-width: 1200px) {
    .lt-page-corp .lt-corp-hero { height: 280px; min-height: 280px; max-height: 280px; }
}

/* --- stats authority band ------------------------------------------ */
.lt-page-corp .lt-corp-stats {
    background-color: var(--lt-ink);
    padding: 2.5rem 1.25rem;
}
.lt-page-corp .lt-corp-stats__inner {
    max-width: 1200px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem 1rem;
}
@media (min-width: 768px) {
    .lt-page-corp .lt-corp-stats__inner {
        grid-template-columns: repeat(4, 1fr);
        gap: 1.5rem;
    }
}
.lt-page-corp .lt-corp-stat {
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
}
.lt-page-corp .lt-corp-stat__icon {
    width: 44px;
    height: 44px;
    color: var(--lt-brass);
}
.lt-page-corp .lt-corp-stat__label {
    font-family: var(--lt-font-body);
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--lt-brass);
}
.lt-page-corp .lt-corp-stat__value {
    font-family: var(--lt-font-heading);
    font-size: 1.625rem;
    color: var(--lt-white);
    line-height: 1.1;
}
.lt-page-corp .lt-corp-stat__sub {
    font-family: var(--lt-font-body);
    font-size: 0.78rem;
    color: rgba(250,247,242,0.6);
    line-height: 1.3;
    max-width: 18ch;
}

/* --- photo proof ---------------------------------------------------- */
.lt-page-corp .lt-corp-photos {
    background-color: var(--lt-near-white);
    padding: 4rem 1.25rem;
}
.lt-page-corp .lt-corp-photos__inner {
    max-width: 1280px;
    margin: 0 auto;
}
.lt-page-corp .lt-corp-photos__heading {
    font-family: var(--lt-font-heading);
    font-size: 2rem;
    color: var(--lt-ink);
    margin: 0 0 0.5rem;
}
.lt-page-corp .lt-corp-photos__lede {
    font-family: var(--lt-font-body);
    font-size: 1rem;
    color: var(--lt-soft-gray);
    margin: 0 0 2.5rem;
    max-width: 58ch;
    line-height: 1.5;
}
/* Featured hero photo + 4-grid layout */
.lt-page-corp .lt-corp-photos__layout {
    display: grid;
    grid-template-columns: 1fr;
    gap: 0.75rem;
}
@media (min-width: 768px) {
    .lt-page-corp .lt-corp-photos__layout {
        grid-template-columns: 3fr 2fr;
        grid-template-rows: auto auto;
        gap: 1rem;
    }
    .lt-page-corp .lt-corp-photo--hero {
        grid-column: 1;
        grid-row: 1 / 3;
    }
    .lt-page-corp .lt-corp-photos__secondary {
        grid-column: 2;
        grid-row: 1 / 3;
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.75rem;
        align-content: start;
    }
}
.lt-page-corp .lt-corp-photo {
    position: relative;
    overflow: hidden;
    border-radius: 3px;
    background-color: var(--lt-stone);
}
.lt-page-corp .lt-corp-photo--hero {
    aspect-ratio: 4/3;
}
.lt-page-corp .lt-corp-photos__secondary .lt-corp-photo {
    aspect-ratio: 1/1;
}
.lt-page-corp .lt-corp-photo img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}
.lt-page-corp .lt-corp-photo__caption {
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

/* --- client roster -------------------------------------------------- */
.lt-page-corp .lt-corp-roster {
    background-color: var(--lt-navy);
    padding: 3.5rem 1.25rem;
}
.lt-page-corp .lt-corp-roster__inner {
    max-width: 1200px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 1fr;
    gap: 2rem;
}
@media (min-width: 1024px) {
    .lt-page-corp .lt-corp-roster__inner {
        grid-template-columns: 2fr 3fr;
        gap: 3rem;
        align-items: start;
    }
}
.lt-page-corp .lt-corp-roster__eyebrow {
    font-family: var(--lt-font-body);
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--lt-brass);
    margin: 0 0 0.75rem;
}
.lt-page-corp .lt-corp-roster__heading {
    font-family: var(--lt-font-heading);
    font-size: 1.875rem;
    color: var(--lt-white);
    margin: 0 0 0.5rem;
    line-height: 1.15;
}
.lt-page-corp .lt-corp-roster__sub {
    font-family: var(--lt-font-body);
    font-size: 0.9rem;
    color: rgba(250,247,242,0.65);
    margin: 0;
    max-width: 38ch;
    line-height: 1.5;
}
.lt-page-corp .lt-corp-roster__grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.4rem 1.25rem;
    list-style: none;
    padding: 0;
    margin: 0;
}
@media (min-width: 768px) {
    .lt-page-corp .lt-corp-roster__grid {
        grid-template-columns: repeat(3, 1fr);
    }
}
.lt-page-corp .lt-corp-roster__item {
    font-family: var(--lt-font-body);
    font-size: 0.87rem;
    color: rgba(250,247,242,0.85);
    padding: 0.3rem 0;
    border-bottom: 1px solid rgba(184,154,91,0.12);
    line-height: 1.25;
}
.lt-page-corp .lt-corp-roster__cat {
    display: block;
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--lt-brass);
    opacity: 0.78;
    margin-top: 0.1rem;
}

/* --- service cards -------------------------------------------------- */
.lt-page-corp .lt-corp-services {
    background-color: var(--lt-warm-white);
    padding: 4rem 1.25rem;
}
.lt-page-corp .lt-corp-services__inner {
    max-width: 1200px;
    margin: 0 auto;
}
.lt-page-corp .lt-corp-services__heading {
    font-family: var(--lt-font-heading);
    font-size: 1.875rem;
    color: var(--lt-ink);
    margin: 0 0 0.5rem;
}
.lt-page-corp .lt-corp-services__lede {
    font-family: var(--lt-font-body);
    font-size: 1rem;
    color: var(--lt-soft-gray);
    margin: 0 0 2.5rem;
    max-width: 54ch;
    line-height: 1.5;
}
.lt-page-corp .lt-corp-services__grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.25rem;
}
@media (min-width: 768px) {
    .lt-page-corp .lt-corp-services__grid {
        grid-template-columns: 1fr 1fr;
        gap: 1.5rem;
    }
}
.lt-page-corp .lt-corp-service-card {
    display: flex;
    gap: 1rem;
    padding: 1.5rem;
    background-color: var(--lt-white);
    border: 1px solid var(--lt-stone);
    border-radius: 3px;
    align-items: flex-start;
}
.lt-page-corp .lt-corp-service-card__icon {
    width: 40px;
    height: 40px;
    flex-shrink: 0;
    color: var(--lt-brass);
}
.lt-page-corp .lt-corp-service-card__name {
    font-family: var(--lt-font-heading);
    font-size: 1.25rem;
    color: var(--lt-ink);
    margin: 0 0 0.4rem;
}
.lt-page-corp .lt-corp-service-card__desc {
    font-family: var(--lt-font-body);
    font-size: 0.9rem;
    color: var(--lt-soft-gray);
    margin: 0;
    line-height: 1.5;
}

/* --- AP / admin trust note ----------------------------------------- */
.lt-page-corp .lt-corp-trust {
    background-color: var(--lt-slate-tint);
    padding: 2.5rem 1.25rem;
    border-top: 2px solid var(--lt-brass);
}
.lt-page-corp .lt-corp-trust__inner {
    max-width: 860px;
    margin: 0 auto;
}
.lt-page-corp .lt-corp-trust__heading {
    font-family: var(--lt-font-heading);
    font-size: 1.5rem;
    color: var(--lt-ink);
    margin: 0 0 0.75rem;
}
.lt-page-corp .lt-corp-trust__body {
    font-family: var(--lt-font-body);
    font-size: 0.95rem;
    color: var(--lt-soft-gray);
    margin: 0;
    line-height: 1.6;
    max-width: 66ch;
}
.lt-page-corp .lt-corp-trust__body--human {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid var(--lt-stone);
}

/* --- CTA ------------------------------------------------------------ */
.lt-page-corp .lt-corp-cta {
    background-color: var(--lt-slate);
    padding: 4rem 1.25rem;
    text-align: center;
}
.lt-page-corp .lt-corp-cta__inner {
    max-width: 680px;
    margin: 0 auto;
}
.lt-page-corp .lt-corp-cta__heading {
    font-family: var(--lt-font-heading);
    font-size: 2.25rem;
    color: var(--lt-white);
    margin: 0 0 0.75rem;
    line-height: 1.1;
}
.lt-page-corp .lt-corp-cta__body {
    font-family: var(--lt-font-body);
    font-size: 1rem;
    color: rgba(250,247,242,0.78);
    margin: 0 0 2rem;
    line-height: 1.55;
}
.lt-page-corp .lt-corp-cta__btn {
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
.lt-page-corp .lt-corp-cta__btn:hover,
.lt-page-corp .lt-corp-cta__btn:focus-visible {
    background-color: var(--lt-ink);
    outline: 2px solid var(--lt-brass);
    outline-offset: 2px;
}
"""


def get_context(context):
    context.title = "Corporate Events — Locally Twisted"
    context.metatags = {
        "description": (
            "Professional balloon decor for Utah corporate events, brand activations, "
            "store openings, and broadcaster events. KSL, Ancestry, Utah Jazz, Zions Bank, and more."
        ),
        "og:title": "Corporate Events — Locally Twisted",
        "og:description": (
            "Branded, on-color balloon installs for Utah corporate events. "
            "AP-ready invoicing, insured install, professional setup and strike."
        ),
        "og:type": "website",
    }
    context.corp_clients = CORP_CLIENTS
    context.corp_proof_stats = CORP_PROOF_STATS
    context.corp_photo_proof = CORP_PHOTO_PROOF
    context.corp_service_cards = CORP_SERVICE_CARDS
    context.colocated_css = PAGE_CSS
    return context
