"""Controller for /corporate-events audience landing page.

Audience: Marketing teams, brand activations, store openings, broadcaster events,
bank/credit-union community days, corporate parties.

Buyer posture: Brand-safe, on-color, repeatable, professional, billable through AP.
"""
import frappe

no_cache = 1
sitemap = 1


CORPORATE_CLIENTS = [
    # Restaurant & hospitality
    "Chick-Fil-A", "Texas Roadhouse", "Applebee's", "Chili's",
    "Honey Baked Ham", "PotBelly",
    # Media & entertainment
    "KSL", "KUTV", "FOX13", "Megaplex", "Paramount",
    # Financial
    "Zions Bank", "America First Credit Union", "Fidelity", "Morgan Stanley",
    # Tech & business
    "Ancestry", "LVT", "Clear", "Henry Schein",
    # Healthcare
    "IHC", "Mountain Star Medical",
    # Events & venues
    "SeaQuest", "Museum of Illusion", "Lux", "FanX",
    "Alpine Events", "In the Events", "The Boiler Room",
    # Automotive & other
    "Young Automotive", "Utah Jazz",
]

CORPORATE_INSTALLS = [
    {
        "title": "Branded Logo Arch — Store Opening",
        "category": "Brand Activation",
        "image": "/assets/locally_twisted/images/portfolio/optimized/corporate-logo-arch.webp",
        "alt": "Custom branded balloon arch in corporate colors installed at a store opening entrance",
    },
    {
        "title": "Weber State Festival Photo Op",
        "category": "Sponsored Event",
        "image": "/assets/locally_twisted/images/portfolio/optimized/corporate-weberstock-photo-opt.webp",
        "alt": "Large-scale balloon photo opportunity backdrop at a sponsored corporate festival event",
    },
    {
        "title": "WSU Arch & Bouquet Package",
        "category": "Corporate Sponsor Install",
        "image": "/assets/locally_twisted/images/portfolio/optimized/corporate-wsu-arch-bouquets.webp",
        "alt": "Balloon arch with coordinated helium bouquets for a corporate-sponsored university event",
    },
    {
        "title": "Branded IHC Event Mockup",
        "category": "Healthcare / Corporate",
        "image": "/assets/locally_twisted/images/odoo/Mock up IHC.png",
        "alt": "Balloon decor design mockup for Intermountain Health corporate event",
    },
]

CORPORATE_PROCESS = [
    {
        "step": "01",
        "title": "Color-matched from your brand guide",
        "body": "Send your hex codes or Pantone references. We match latex and foil selections to your official palette — not a close approximation."
    },
    {
        "step": "02",
        "title": "Quoted for AP and budget approval",
        "body": "Itemized quotes structured for internal approval processes. Invoice on net terms when accounts payable requires it."
    },
    {
        "step": "03",
        "title": "On-time, documented, struck clean",
        "body": "We confirm arrival window before your event and hold to it. Professional install, clean teardown, photography documentation available on request for marketing recaps. If anything changes, you hear from us first — not your venue coordinator."
    },
]

PAGE_CSS = """
/* =====================================================================
 * Corporate Events audience page — lt-page-corporate namespace
 * Sections: hero, installs, process, client-roster, cta
 * ===================================================================== */

/* --- Corporate hero (fullbleed) ------------------------------------- */
.lt-page-corporate .lt-corp-hero {
    position: relative;
    min-height: 220px;
    height: 220px;
    max-height: 280px;
    background-color: var(--lt-ink);
    overflow: hidden;
    display: flex;
    align-items: center;
}
.lt-page-corporate .lt-corp-hero__image {
    position: absolute;
    inset: 0;
    background-image: url('/assets/locally_twisted/images/portfolio/optimized/corporate-logo-arch.webp');
    background-size: cover;
    background-position: center;
    background-color: var(--lt-ink);
}
.lt-page-corporate .lt-corp-hero__image::after {
    content: '';
    position: absolute;
    inset: 0;
    background:
        linear-gradient(90deg, rgba(10,10,11,0.93) 0%, rgba(14,34,64,0.70) 50%, rgba(14,34,64,0.1) 100%),
        linear-gradient(180deg, transparent 0%, rgba(10,10,11,0.3) 100%);
}
.lt-page-corporate .lt-corp-hero__content {
    position: relative;
    z-index: 1;
    width: 100%;
    max-width: 1280px;
    margin: 0 auto;
    padding: 1.5rem 1rem;
    color: var(--lt-warm-white);
}
.lt-page-corporate .lt-corp-hero__eyebrow {
    font-family: var(--lt-font-body);
    font-size: 0.74rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--lt-brass);
    margin: 0 0 0.4rem;
}
.lt-page-corporate .lt-corp-hero__h1 {
    font-family: var(--lt-font-heading);
    font-weight: 700;
    font-size: clamp(1.75rem, 5vw, 2.25rem);
    line-height: 1.05;
    color: var(--lt-warm-white);
    margin: 0 0 0.5rem;
    max-width: 24ch;
}
.lt-page-corporate .lt-corp-hero__lede {
    font-family: var(--lt-font-body);
    font-size: 0.94rem;
    line-height: 1.45;
    color: rgba(250,247,242,0.9);
    margin: 0 0 0.85rem;
    max-width: 50ch;
}
.lt-page-corporate .lt-corp-hero__cta {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.6rem 1.25rem;
    background-color: var(--lt-navy);
    color: var(--lt-warm-white);
    font-family: var(--lt-font-body);
    font-weight: 700;
    font-size: 0.85rem;
    text-decoration: none;
    min-height: 44px;
    border-radius: 2px;
    border: 1px solid rgba(184,154,91,0.4);
}
.lt-page-corporate .lt-corp-hero__cta:hover,
.lt-page-corporate .lt-corp-hero__cta:focus-visible {
    background-color: var(--lt-berry);
    border-color: transparent;
    outline: 2px solid var(--lt-brass);
    outline-offset: 2px;
}
@media (min-width: 768px) {
    .lt-page-corporate .lt-corp-hero {
        min-height: 250px;
        height: 250px;
        max-height: 300px;
    }
    .lt-page-corporate .lt-corp-hero__content { padding: 2rem; }
    .lt-page-corporate .lt-corp-hero__h1 { font-size: 2.5rem; }
}
@media (min-width: 1200px) {
    .lt-page-corporate .lt-corp-hero {
        min-height: 280px;
        height: 280px;
        max-height: 320px;
    }
    .lt-page-corporate .lt-corp-hero__h1 { font-size: 2.75rem; }
}

/* --- Proof intro (band / warm white) ------------------------------- */
.lt-page-corporate .lt-corp-intro {
    background-color: var(--lt-warm-white);
    padding: 3.5rem 1.25rem;
}
.lt-page-corporate .lt-corp-intro__inner {
    max-width: 1100px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 1fr;
    gap: 2rem;
    align-items: start;
}
@media (min-width: 768px) {
    .lt-page-corporate .lt-corp-intro__inner {
        grid-template-columns: 3fr 2fr;
        gap: 4rem;
        align-items: center;
    }
}
.lt-page-corporate .lt-corp-intro__label {
    font-family: var(--lt-font-body);
    font-size: 0.74rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--lt-berry);
    margin: 0 0 0.75rem;
}
.lt-page-corporate .lt-corp-intro__h2 {
    font-family: var(--lt-font-heading);
    font-size: clamp(1.5rem, 3.5vw, 2.25rem);
    color: var(--lt-ink);
    line-height: 1.1;
    margin: 0 0 1rem;
}
.lt-page-corporate .lt-corp-intro__body {
    font-family: var(--lt-font-body);
    font-size: 1.0625rem;
    color: var(--lt-soft-gray);
    line-height: 1.65;
    margin: 0 0 1rem;
}
.lt-page-corporate .lt-corp-intro__callouts {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
}
.lt-page-corporate .lt-corp-intro__callout {
    padding: 1.25rem 1.5rem;
    background-color: var(--lt-white);
    border-left: 3px solid var(--lt-brass);
    border-radius: 0 2px 2px 0;
}
.lt-page-corporate .lt-corp-intro__callout-title {
    font-family: var(--lt-font-body);
    font-size: 0.8125rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--lt-ink);
    margin: 0 0 0.3rem;
}
.lt-page-corporate .lt-corp-intro__callout-body {
    font-family: var(--lt-font-body);
    font-size: 0.9375rem;
    color: var(--lt-soft-gray);
    margin: 0;
    line-height: 1.5;
}

/* --- Installed work gallery (visual-field / near white) ------------- */
.lt-page-corporate .lt-corp-gallery {
    background-color: var(--lt-near-white);
    padding: 3.5rem 1.25rem;
}
.lt-page-corporate .lt-corp-gallery__inner {
    max-width: 1400px;
    margin: 0 auto;
}
.lt-page-corporate .lt-corp-gallery__heading {
    font-family: var(--lt-font-heading);
    font-size: clamp(1.5rem, 3.5vw, 2.25rem);
    color: var(--lt-ink);
    margin: 0 0 0.5rem;
}
.lt-page-corporate .lt-corp-gallery__subhead {
    font-family: var(--lt-font-body);
    font-size: 1rem;
    color: var(--lt-soft-gray);
    margin: 0 0 2rem;
    max-width: 60ch;
}
.lt-page-corporate .lt-corp-gallery__grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
}
@media (min-width: 992px) {
    .lt-page-corporate .lt-corp-gallery__grid {
        grid-template-columns: repeat(4, 1fr);
    }
}
.lt-page-corporate .lt-corp-gallery__item {
    position: relative;
    overflow: hidden;
    border-radius: 2px;
    background-color: var(--lt-slate);
}
.lt-page-corporate .lt-corp-gallery__img {
    width: 100%;
    aspect-ratio: 4/3;
    object-fit: cover;
    display: block;
}
.lt-page-corporate .lt-corp-gallery__cap {
    position: absolute;
    bottom: 0; left: 0; right: 0;
    padding: 0.75rem;
    background: linear-gradient(to top, rgba(10,10,11,0.85) 0%, transparent 100%);
}
.lt-page-corporate .lt-corp-gallery__cap-cat {
    font-family: var(--lt-font-body);
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--lt-brass);
    margin: 0 0 0.2rem;
}
.lt-page-corporate .lt-corp-gallery__cap-title {
    font-family: var(--lt-font-heading);
    font-size: 0.9375rem;
    color: var(--lt-warm-white);
    margin: 0;
    line-height: 1.2;
}

/* --- Process steps (band / slate blue) ----------------------------- */
.lt-page-corporate .lt-corp-process {
    background-color: var(--lt-slate);
    padding: 3.5rem 1.25rem;
}
.lt-page-corporate .lt-corp-process__inner {
    max-width: 1100px;
    margin: 0 auto;
}
.lt-page-corporate .lt-corp-process__eyebrow {
    font-family: var(--lt-font-body);
    font-size: 0.74rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--lt-brass);
    margin: 0 0 0.5rem;
}
.lt-page-corporate .lt-corp-process__h2 {
    font-family: var(--lt-font-heading);
    font-size: clamp(1.5rem, 3vw, 2rem);
    color: var(--lt-warm-white);
    margin: 0 0 2.5rem;
}
.lt-page-corporate .lt-corp-process__steps {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.5rem;
}
@media (min-width: 768px) {
    .lt-page-corporate .lt-corp-process__steps {
        grid-template-columns: repeat(3, 1fr);
    }
}
.lt-page-corporate .lt-corp-process__step {
    border-top: 2px solid rgba(184,154,91,0.45);
    padding-top: 1.25rem;
}
.lt-page-corporate .lt-corp-process__step-num {
    font-family: var(--lt-font-body);
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    color: var(--lt-brass);
    margin: 0 0 0.5rem;
}
.lt-page-corporate .lt-corp-process__step-title {
    font-family: var(--lt-font-heading);
    font-size: 1.1875rem;
    color: var(--lt-warm-white);
    margin: 0 0 0.5rem;
    line-height: 1.2;
}
.lt-page-corporate .lt-corp-process__step-body {
    font-family: var(--lt-font-body);
    font-size: 0.9375rem;
    color: rgba(250,247,242,0.75);
    line-height: 1.6;
    margin: 0;
}

/* --- Client roster (band / white) ---------------------------------- */
.lt-page-corporate .lt-corp-roster {
    background-color: var(--lt-white);
    padding: 3.5rem 1.25rem;
    border-top: 1px solid var(--lt-stone);
}
.lt-page-corporate .lt-corp-roster__inner {
    max-width: 1100px;
    margin: 0 auto;
}
.lt-page-corporate .lt-corp-roster__eyebrow {
    font-family: var(--lt-font-body);
    font-size: 0.74rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--lt-soft-gray);
    margin: 0 0 0.5rem;
}
.lt-page-corporate .lt-corp-roster__h2 {
    font-family: var(--lt-font-heading);
    font-size: clamp(1.25rem, 2.5vw, 1.75rem);
    color: var(--lt-ink);
    margin: 0 0 1.75rem;
}
.lt-page-corporate .lt-corp-roster__grid {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem 0.75rem;
}
.lt-page-corporate .lt-corp-roster__chip {
    font-family: var(--lt-font-body);
    font-size: 0.875rem;
    color: var(--lt-slate);
    background-color: var(--lt-stone-tint);
    border: 1px solid var(--lt-stone);
    padding: 0.375rem 0.875rem;
    border-radius: 2px;
    white-space: nowrap;
}

/* --- CTA (fullbleed / navy) ---------------------------------------- */
.lt-page-corporate .lt-corp-cta {
    background-color: var(--lt-navy);
    padding: 4rem 1.25rem;
    text-align: center;
}
.lt-page-corporate .lt-corp-cta__inner {
    max-width: 700px;
    margin: 0 auto;
}
.lt-page-corporate .lt-corp-cta__h2 {
    font-family: var(--lt-font-heading);
    font-size: clamp(1.75rem, 4vw, 2.75rem);
    color: var(--lt-warm-white);
    margin: 0 0 1rem;
    line-height: 1.1;
}
.lt-page-corporate .lt-corp-cta__body {
    font-family: var(--lt-font-body);
    font-size: 1.0625rem;
    color: rgba(250,247,242,0.8);
    max-width: 52ch;
    margin: 0 auto 1.75rem;
    line-height: 1.55;
}
.lt-page-corporate .lt-corp-cta__btn {
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
.lt-page-corporate .lt-corp-cta__btn:hover,
.lt-page-corporate .lt-corp-cta__btn:focus-visible {
    background-color: var(--lt-crimson);
    outline: 2px solid var(--lt-brass);
    outline-offset: 2px;
}
.lt-page-corporate .lt-corp-cta__sub {
    margin: 1.25rem 0 0;
    font-family: var(--lt-font-body);
    font-size: 0.875rem;
    color: rgba(250,247,242,0.5);
}
.lt-page-corporate .lt-corp-cta__sub a {
    color: var(--lt-brass);
    text-decoration: none;
}
.lt-page-corporate .lt-corp-cta__sub a:hover { text-decoration: underline; }
"""


def get_context(context):
    context.title = "Corporate Events — Locally Twisted Balloon Decor"
    context.metatags = {
        "description": (
            "Professional balloon decor for Utah corporate events, store openings, "
            "brand activations, and company celebrations. Trusted by KSL, Zions Bank, "
            "Chick-Fil-A, Utah Jazz, IHC, and 30+ Utah organizations."
        ),
        "og:title": "Corporate Event Balloon Decor — Locally Twisted",
        "og:description": (
            "Brand-matched, AP-invoiceable balloon decor for Utah corporate events. "
            "Color-matched to your brand guide. Professional install, clean strike."
        ),
        "og:type": "website",
    }
    context.corporate_clients = CORPORATE_CLIENTS
    context.corporate_installs = CORPORATE_INSTALLS
    context.corporate_process = CORPORATE_PROCESS
    context.colocated_css = PAGE_CSS
    return context
