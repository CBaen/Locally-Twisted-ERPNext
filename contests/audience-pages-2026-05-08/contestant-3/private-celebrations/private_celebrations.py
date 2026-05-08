"""Controller for /private-celebrations audience landing page.

Audience: Birthday parents, wedding planners, baby shower hosts, milestone families,
memorial/celebration-of-life organizers.

Buyer posture: Personal, milestone-emotional, taste-elevated, gift-feeling.

No named-client roster — private celebrations expect privacy.
Proof is category-level: count claims, testimonial phrasing, photo proof.
"""
import frappe

no_cache = 1
sitemap = 1


PRIVATE_PROOF_STATS = [
    {"number": "300+", "label": "Birthday installs delivered"},
    {"number": "Wasatch\nFront", "label": "Weddings across the"},
    {"number": "Every\ndetail", "label": "matters"},
]

# Testimonials - privacy-friendly (abbreviated last name, no venue/location)
PRIVATE_TESTIMONIALS = [
    {
        "text": "Jeff has been listed in my phone for 7-ish years as 'balloon guy' and has been my go-to for that long. I know I can trust him and his team to always exceed my expectations.",
        "attr": "Sara M., longtime client",
    },
    {
        "text": "I needed a sports themed funeral stand. They captured my vision, delivered on time, very reasonable, and had many complements. Very tasteful and meaningful.",
        "attr": "KJSCOTT, celebration of life",
    },
    {
        "text": "We were seriously blown away and my kids were delighted. My oldest son requested they come to his birthday party. They were fantastic!",
        "attr": "Mark T., wedding + birthday",
    },
    {
        "text": "They went above and beyond what they needed to do for my mom's Mother's Day gift. I made a mistake on the delivery date and they fixed it and made the delivery.",
        "attr": "LuAnn K., gift delivery",
    },
]

PRIVATE_OCCASIONS = [
    {
        "name": "Birthdays",
        "body": "From a first birthday backdrop to a milestone 50th — arches, columns, organic garlands, and photo ops in any palette.",
        "image": "/assets/locally_twisted/images/portfolio/optimized/birthday-balloon-bouquets.webp",
        "image_alt": "Colorful birthday balloon bouquets for a milestone celebration",
    },
    {
        "name": "Weddings",
        "body": "Ceremony arches, reception garlands, and organic decor in your exact palette. Venue coordination included.",
        "image": "/assets/locally_twisted/images/portfolio/optimized/wedding-organic-half-arch.webp",
        "image_alt": "Elegant organic balloon half arch for a wedding ceremony",
    },
    {
        "name": "Baby & Bridal Showers",
        "body": "Soft, elevated decor that matches the invitation aesthetic. Balloon garlands, photo ops, and table decor.",
        "image": "/assets/locally_twisted/images/portfolio/optimized/wedding-floral-half-arch.webp",
        "image_alt": "Floral balloon arch for an elegant baby or bridal shower celebration",
    },
    {
        "name": "Milestones",
        "body": "Quinceañera, retirement, anniversary, graduation — the pieces that make a milestone feel finished.",
        "image": "/assets/locally_twisted/images/portfolio/optimized/birthday-dolphin-backdrop.webp",
        "image_alt": "Custom themed balloon backdrop for a special milestone celebration",
    },
    {
        "name": "Celebration of Life",
        "body": "Tasteful, meaningful decor for memorials and celebrations of life. Every tribute deserves care.",
        "image": "/assets/locally_twisted/images/portfolio/optimized/wedding-foil-heart-arch.webp",
        "image_alt": "Elegant foil heart balloon arch for a memorial or celebration of life",
    },
    {
        "name": "Custom Themes",
        "body": "Characters, sculptural pieces, themed backdrops — if you can imagine it, bring us the brief.",
        "image": "/assets/locally_twisted/images/portfolio/optimized/birthday-smurfs-arch.webp",
        "image_alt": "Custom character-themed balloon arch for a birthday celebration",
    },
]

PAGE_CSS = """
/* =====================================================================
 * Private Celebrations audience page — lt-page-private namespace
 * Sections: hero, intro, occasions, testimonials, cta
 * ===================================================================== */

/* --- Private hero (fullbleed) --------------------------------------- */
.lt-page-private .lt-priv-hero {
    position: relative;
    min-height: 220px;
    height: 220px;
    max-height: 280px;
    background-color: var(--lt-ink);
    overflow: hidden;
    display: flex;
    align-items: center;
}
.lt-page-private .lt-priv-hero__image {
    position: absolute;
    inset: 0;
    background-image: url('/assets/locally_twisted/images/portfolio/optimized/wedding-organic-half-arch.webp');
    background-size: cover;
    background-position: center;
    background-color: var(--lt-ink);
}
.lt-page-private .lt-priv-hero__image::after {
    content: '';
    position: absolute;
    inset: 0;
    background:
        linear-gradient(90deg, rgba(10,10,11,0.88) 0%, rgba(10,10,11,0.55) 50%, rgba(10,10,11,0.08) 100%),
        linear-gradient(180deg, transparent 0%, rgba(10,10,11,0.25) 100%);
}
.lt-page-private .lt-priv-hero__content {
    position: relative;
    z-index: 1;
    width: 100%;
    max-width: 1280px;
    margin: 0 auto;
    padding: 1.5rem 1rem;
    color: var(--lt-warm-white);
}
.lt-page-private .lt-priv-hero__eyebrow {
    font-family: var(--lt-font-body);
    font-size: 0.74rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--lt-brass);
    margin: 0 0 0.4rem;
}
.lt-page-private .lt-priv-hero__h1 {
    font-family: var(--lt-font-heading);
    font-weight: 700;
    font-size: clamp(1.75rem, 5vw, 2.25rem);
    line-height: 1.05;
    color: var(--lt-warm-white);
    margin: 0 0 0.5rem;
    max-width: 20ch;
}
.lt-page-private .lt-priv-hero__lede {
    font-family: var(--lt-font-body);
    font-size: 0.94rem;
    line-height: 1.45;
    color: rgba(250,247,242,0.9);
    margin: 0 0 0.85rem;
    max-width: 50ch;
}
.lt-page-private .lt-priv-hero__cta {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.6rem 1.25rem;
    background-color: var(--lt-berry);
    color: var(--lt-warm-white);
    font-family: var(--lt-font-body);
    font-weight: 700;
    font-size: 0.85rem;
    text-decoration: none;
    min-height: 44px;
    border-radius: 2px;
}
.lt-page-private .lt-priv-hero__cta:hover,
.lt-page-private .lt-priv-hero__cta:focus-visible {
    background-color: var(--lt-crimson);
    outline: 2px solid var(--lt-brass);
    outline-offset: 2px;
}
@media (min-width: 768px) {
    .lt-page-private .lt-priv-hero {
        min-height: 250px;
        height: 250px;
        max-height: 300px;
    }
    .lt-page-private .lt-priv-hero__content { padding: 2rem; }
    .lt-page-private .lt-priv-hero__h1 { font-size: 2.5rem; max-width: 24ch; }
}
@media (min-width: 1200px) {
    .lt-page-private .lt-priv-hero {
        min-height: 280px;
        height: 280px;
        max-height: 320px;
    }
    .lt-page-private .lt-priv-hero__h1 { font-size: 2.75rem; }
}

/* --- Intro prose (band / warm white) ------------------------------- */
.lt-page-private .lt-priv-intro {
    background-color: var(--lt-warm-white);
    padding: 3.5rem 1.25rem;
}
.lt-page-private .lt-priv-intro__inner {
    max-width: 780px;
    margin: 0 auto;
}
.lt-page-private .lt-priv-intro__label {
    font-family: var(--lt-font-body);
    font-size: 0.74rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--lt-berry);
    margin: 0 0 0.75rem;
}
.lt-page-private .lt-priv-intro__h2 {
    font-family: var(--lt-font-heading);
    font-size: clamp(1.5rem, 3.5vw, 2.25rem);
    color: var(--lt-ink);
    line-height: 1.1;
    margin: 0 0 1rem;
}
.lt-page-private .lt-priv-intro__body {
    font-family: var(--lt-font-body);
    font-size: 1.0625rem;
    color: var(--lt-soft-gray);
    line-height: 1.65;
    margin: 0 0 1rem;
}
.lt-page-private .lt-priv-intro__stats {
    display: flex;
    gap: 2rem;
    flex-wrap: wrap;
    margin-top: 2rem;
    padding-top: 1.75rem;
    border-top: 1px solid var(--lt-stone);
}
.lt-page-private .lt-priv-intro__stat {
    flex: 0 0 auto;
}
.lt-page-private .lt-priv-intro__stat-number {
    font-family: var(--lt-font-heading);
    font-size: 2rem;
    color: var(--lt-berry);
    line-height: 1;
    margin: 0 0 0.25rem;
    white-space: pre-line;
}
.lt-page-private .lt-priv-intro__stat-label {
    font-family: var(--lt-font-body);
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--lt-soft-gray);
    white-space: pre-line;
}

/* --- Occasions grid (visual-field / stone) -------------------------- */
.lt-page-private .lt-priv-occasions {
    background-color: var(--lt-stone);
    padding: 3.5rem 1.25rem;
}
.lt-page-private .lt-priv-occasions__inner {
    max-width: 1300px;
    margin: 0 auto;
}
.lt-page-private .lt-priv-occasions__h2 {
    font-family: var(--lt-font-heading);
    font-size: clamp(1.5rem, 3.5vw, 2.25rem);
    color: var(--lt-ink);
    margin: 0 0 0.5rem;
}
.lt-page-private .lt-priv-occasions__lede {
    font-family: var(--lt-font-body);
    font-size: 1rem;
    color: var(--lt-soft-gray);
    margin: 0 0 2rem;
    max-width: 60ch;
}
.lt-page-private .lt-priv-occasions__grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.5rem;
}
@media (min-width: 600px) {
    .lt-page-private .lt-priv-occasions__grid { grid-template-columns: repeat(2, 1fr); }
}
@media (min-width: 992px) {
    .lt-page-private .lt-priv-occasions__grid { grid-template-columns: repeat(3, 1fr); }
}
.lt-page-private .lt-priv-occasions__card {
    background-color: var(--lt-white);
    border-radius: 2px;
    overflow: hidden;
    box-shadow: 0 4px 16px rgba(10,10,11,0.06);
}
.lt-page-private .lt-priv-occasions__img {
    width: 100%;
    aspect-ratio: 4/3;
    object-fit: cover;
    display: block;
}
.lt-page-private .lt-priv-occasions__body {
    padding: 1.25rem 1.5rem 1.5rem;
}
.lt-page-private .lt-priv-occasions__name {
    font-family: var(--lt-font-heading);
    font-size: 1.25rem;
    color: var(--lt-ink);
    margin: 0 0 0.5rem;
}
.lt-page-private .lt-priv-occasions__desc {
    font-family: var(--lt-font-body);
    font-size: 0.9375rem;
    color: var(--lt-soft-gray);
    line-height: 1.6;
    margin: 0;
}

/* --- Testimonials (band / white) ----------------------------------- */
.lt-page-private .lt-priv-testimonials {
    background-color: var(--lt-white);
    padding: 3.5rem 1.25rem;
    border-top: 1px solid var(--lt-stone);
}
.lt-page-private .lt-priv-testimonials__inner {
    max-width: 1100px;
    margin: 0 auto;
}
.lt-page-private .lt-priv-testimonials__h2 {
    font-family: var(--lt-font-heading);
    font-size: clamp(1.25rem, 2.5vw, 1.875rem);
    color: var(--lt-ink);
    margin: 0 0 2rem;
}
.lt-page-private .lt-priv-testimonials__grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.25rem;
}
@media (min-width: 600px) {
    .lt-page-private .lt-priv-testimonials__grid { grid-template-columns: repeat(2, 1fr); }
}
.lt-page-private .lt-priv-testimonials__card {
    padding: 1.5rem;
    background-color: var(--lt-near-white);
    border: 1px solid rgba(184,154,91,0.2);
    border-radius: 2px;
    position: relative;
}
.lt-page-private .lt-priv-testimonials__mark {
    font-family: var(--lt-font-heading);
    font-size: 2.5rem;
    color: var(--lt-brass);
    line-height: 1;
    margin: 0 0 0.5rem;
    opacity: 0.5;
}
.lt-page-private .lt-priv-testimonials__text {
    font-family: var(--lt-font-body);
    font-size: 0.9375rem;
    color: var(--lt-ink);
    line-height: 1.6;
    margin: 0 0 0.75rem;
}
.lt-page-private .lt-priv-testimonials__attr {
    font-family: var(--lt-font-body);
    font-size: 0.8125rem;
    color: var(--lt-soft-gray);
    margin: 0;
}

/* --- CTA (fullbleed / navy) ---------------------------------------- */
.lt-page-private .lt-priv-cta {
    background-color: var(--lt-navy);
    padding: 4rem 1.25rem;
    text-align: center;
}
.lt-page-private .lt-priv-cta__inner {
    max-width: 680px;
    margin: 0 auto;
}
.lt-page-private .lt-priv-cta__h2 {
    font-family: var(--lt-font-heading);
    font-size: clamp(1.75rem, 4vw, 2.75rem);
    color: var(--lt-warm-white);
    margin: 0 0 1rem;
    line-height: 1.1;
}
.lt-page-private .lt-priv-cta__body {
    font-family: var(--lt-font-body);
    font-size: 1.0625rem;
    color: rgba(250,247,242,0.8);
    max-width: 52ch;
    margin: 0 auto 1.75rem;
    line-height: 1.55;
}
.lt-page-private .lt-priv-cta__btn {
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
.lt-page-private .lt-priv-cta__btn:hover,
.lt-page-private .lt-priv-cta__btn:focus-visible {
    background-color: var(--lt-crimson);
    outline: 2px solid var(--lt-brass);
    outline-offset: 2px;
}
.lt-page-private .lt-priv-cta__sub {
    margin: 1.25rem 0 0;
    font-family: var(--lt-font-body);
    font-size: 0.875rem;
    color: rgba(250,247,242,0.5);
}
.lt-page-private .lt-priv-cta__sub a {
    color: var(--lt-brass);
    text-decoration: none;
}
.lt-page-private .lt-priv-cta__sub a:hover { text-decoration: underline; }
"""


def get_context(context):
    context.title = "Private Celebrations — Locally Twisted Balloon Decor"
    context.metatags = {
        "description": (
            "Custom balloon decor for birthdays, weddings, baby showers, anniversaries, "
            "graduations, and celebrations of life across the Wasatch Front. "
            "300+ birthday installs. Every detail matters."
        ),
        "og:title": "Private Celebrations — Locally Twisted Balloon Decor",
        "og:description": (
            "Tasteful, milestone-quality balloon decor for private celebrations. "
            "Birthdays, weddings, showers, memorials, and milestone moments. Wasatch Front delivery."
        ),
        "og:type": "website",
    }
    context.private_proof_stats = PRIVATE_PROOF_STATS
    context.private_testimonials = PRIVATE_TESTIMONIALS
    context.private_occasions = PRIVATE_OCCASIONS
    context.colocated_css = PAGE_CSS
    return context
