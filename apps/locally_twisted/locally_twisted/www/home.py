"""Homepage controller — `/` route.

Renders the lookbook-forward homepage. Section order, copy, and the
client-crawl list are sourced from the prior project's approved Odoo
XML at addons/locally_twisted/views/homepage.xml + the snippet templates
in views/snippets/. Reframed for the lookbook-forward shape decided
2026-04-26 (see .planning/decisions/site-shape.md):
- Hero CTA points at /book (inquiry-led), not /shop
- "Featured Work" replaces "Seasonal Favorites" placeholder (lookbook-led)
- About snippet replaces the "Local Favorites" e-commerce placeholder
- Custom Creations categories link into the future /lookbook?category=X
  (placeholder hrefs for now; will activate when Slice 7 ships)

CSS is colocated as PAGE_CSS and injected via context.colocated_css —
the same pattern as /contact and /balloon-twisting-and-face-painting.
This keeps each page's CSS scoped to the page that uses it; the
shared brand foundation lives in lt-theme.css.
"""
import frappe

no_cache = 1
sitemap = 1


# Real client list from the approved homepage XML's s_lt_client_crawl
# snippet (54 names). Duplicated in the template for the seamless
# marquee loop; the second copy gets aria-hidden so screen readers
# don't double-read.
CLIENT_CRAWL = [
    "FanX", "Chick-fil-A", "Texas Roadhouse", "Applebee's", "Chili's",
    "Utah Art Alliance", "Ancestry", "Honey Baked Ham", "Megaplex",
    "Zions Bank", "America First CU", "Utah Jazz", "Fidelity",
    "Morgan Stanley", "KSL", "KUTV", "FOX13", "University of Utah",
    "Weber State", "Intermountain Health", "UDOT", "SLC Pride",
    "Equality Utah", "Ogden City", "Sandy City", "Herriman City",
    "SLC County", "Gallivan Center", "Station Park", "Museum of Illusion",
    "PotBelly", "Young Automotive", "Sea Quest", "Alpine Events",
    "Ogden Airport", "Paramount", "Shops at Southtown", "Daybreak",
    "LVT", "Lux Events", "Safe Kids Fair", "Tree House Museum",
    "Ogden Country Club", "Pride Center", "Newgate Mall",
    "The Boiler Room", "Western Sports Park", "St. Joseph's",
    "Syracuse City", "West Point City", "Clinton City", "Hooper City",
    "Kearns", "Ogden Weber Chamber", "LGBT Chamber",
]


# The 5 customizable categories — these are the items GL/Jeff actually
# customize (arches, columns, garlands, backdrops, drops). Each will
# eventually point at a Lookbook category page (Slice 7) and into the
# future Design Studio interactive experience (post-Slice 9).
CUSTOM_CATEGORIES = [
    {"slug": "balloon-arches", "name": "Balloon Arches", "icon": "arch"},
    {"slug": "columns-and-pillars", "name": "Columns & Pillars", "icon": "column"},
    {"slug": "organic-garlands", "name": "Organic Garlands", "icon": "garland"},
    {"slug": "picture-perfect-backdrops", "name": "Picture Perfect Backdrops", "icon": "backdrop"},
    {"slug": "balloon-drops", "name": "Balloon Drops", "icon": "drop"},
]


# Featured work — 3 case-study cards. Photos and event names are
# placeholder until GL surfaces real ones from Jeff's archive. Source
# of real photos when ready: locally-twisted-odoo/assets/image assets/
# photos for website/.
FEATURED_WORK = [
    {
        "category": "Balloon Arches",
        "title": "Knight & Dragon Birthday Arch",
        "image": "/assets/locally_twisted/images/home/featured-arches.png",
        "alt": "Custom themed balloon arch for a children's birthday party",
    },
    {
        "category": "Organic Garlands",
        "title": "Wedding Ceremony Garland",
        "image": "/assets/locally_twisted/images/home/featured-garlands.png",
        "alt": "Soft organic balloon garland framing a wedding ceremony space",
    },
    {
        "category": "Corporate Decor",
        "title": "Brand Logo Arch",
        "image": "/assets/locally_twisted/images/home/featured-corporate.png",
        "alt": "Custom corporate event arch incorporating brand colors and logo",
    },
]


PAGE_CSS = """
/* ======================================================================
 * HOMEPAGE — lookbook-forward shape
 * BEM blocks: lt-hero, lt-reviews, lt-trust, lt-categories, lt-featured,
 *             lt-twisting-spotlight, lt-crawl, lt-about, lt-cta
 * Uses CSS variables from lt-theme.css (--lt-teal, --lt-near-black, etc.)
 * ====================================================================== */

/* --- Hero ----------------------------------------------------------- */
.lt-hero {
    position: relative;
    min-height: 560px;
    background-color: var(--lt-blush-tint);
    overflow: hidden;
    display: flex;
    align-items: flex-end;
}
.lt-hero__image {
    position: absolute;
    inset: 0;
    background-image: url('/assets/locally_twisted/images/home/hero.jpg');
    background-size: cover;
    background-position: center;
    background-color: var(--lt-blush-tint);
}
.lt-hero__image::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(
        to bottom,
        rgba(0, 0, 0, 0) 40%,
        rgba(0, 0, 0, 0.55) 100%
    );
}
.lt-hero__content {
    position: relative;
    z-index: 1;
    width: 100%;
    padding: 3rem 1.25rem 2.5rem;
    text-align: center;
    color: var(--lt-white);
}
.lt-hero__eyebrow {
    font-family: 'Raleway', sans-serif;
    font-size: 0.875rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin: 0 0 0.5rem;
    opacity: 0.95;
    text-align: center;
}
.lt-hero__title {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 2.5rem;
    line-height: 1.1;
    margin: 0 0 0.6rem;
    color: var(--lt-white);
    text-align: center;
}
.lt-hero__lede {
    font-family: 'Raleway', sans-serif;
    font-size: 1.125rem;
    margin: 0 auto 1.5rem;
    max-width: 38ch;
    font-weight: 300;
    color: rgba(255, 255, 255, 0.95);
    text-align: center;
}
.lt-hero__cta {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.875rem 1.75rem;
    background-color: var(--lt-teal);
    color: var(--lt-white);
    text-decoration: none;
    font-family: 'Raleway', sans-serif;
    font-weight: 600;
    font-size: 1rem;
    border-radius: 0.375rem;
    min-height: 48px;
}
.lt-hero__cta:hover,
.lt-hero__cta:focus-visible {
    background-color: #006666;
    color: var(--lt-white);
    outline: 2px solid var(--lt-white);
    outline-offset: 2px;
}
@media (min-width: 768px) {
    .lt-hero { min-height: 640px; }
    .lt-hero__title { font-size: 3.5rem; }
    .lt-hero__lede { font-size: 1.25rem; }
    .lt-hero__content { padding: 4rem 2rem 3.5rem; }
}

/* --- Reviews badge --------------------------------------------------- */
.lt-reviews {
    background-color: var(--lt-white);
    padding: 1.75rem 1rem;
    text-align: center;
}
.lt-reviews__link {
    display: inline-flex;
    align-items: center;
    gap: 0.65rem;
    color: var(--lt-near-black);
    text-decoration: none;
    font-family: 'Raleway', sans-serif;
    font-size: 1rem;
    font-weight: 500;
}
.lt-reviews__link:hover,
.lt-reviews__link:focus-visible {
    text-decoration: underline;
}
.lt-reviews__score {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 1.5rem;
    color: var(--lt-near-black);
}
.lt-reviews__stars {
    color: #f5b400;
    letter-spacing: 0.12em;
}
.lt-reviews__count {
    color: var(--lt-soft-gray);
}

/* --- Trust strip ---------------------------------------------------- */
.lt-trust {
    background-color: var(--lt-blue-tint);
    padding: 2.5rem 1rem;
}
.lt-trust__row {
    max-width: 980px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    text-align: center;
}
.lt-trust__item {
    padding: 0.5rem;
}
.lt-trust__title {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 1.125rem;
    color: var(--lt-near-black);
    margin: 0 0 0.25rem;
    text-align: center;
}
.lt-trust__desc {
    display: none;
    font-family: 'Raleway', sans-serif;
    font-size: 0.875rem;
    color: var(--lt-soft-gray);
    margin: 0;
    text-align: center;
}
@media (min-width: 768px) {
    .lt-trust__title { font-size: 1.375rem; }
    .lt-trust__desc { display: block; }
}

/* --- Custom Creations categories ------------------------------------ */
.lt-categories {
    background-color: var(--lt-white);
    padding: 3.5rem 1rem;
}
.lt-categories__heading {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 2rem;
    text-align: center;
    color: var(--lt-near-black);
    margin: 0 0 0.5rem;
}
.lt-categories__lede {
    text-align: center;
    color: var(--lt-soft-gray);
    max-width: 540px;
    margin: 0 auto 2.5rem;
    font-size: 1rem;
}
.lt-categories__grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
    max-width: 980px;
    margin: 0 auto;
}
@media (min-width: 768px) {
    .lt-categories__grid { grid-template-columns: repeat(5, 1fr); }
}
.lt-categories__item {
    text-align: center;
}
.lt-categories__link {
    display: inline-flex;
    flex-direction: column;
    align-items: center;
    gap: 0.75rem;
    text-decoration: none;
    color: var(--lt-near-black);
}
.lt-categories__circle {
    width: 110px;
    height: 110px;
    border-radius: 50%;
    background-color: var(--lt-blush-tint);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: transform 0.2s ease, background-color 0.2s ease;
}
.lt-categories__link:hover .lt-categories__circle,
.lt-categories__link:focus-visible .lt-categories__circle {
    background-color: var(--lt-blue-tint);
    transform: translateY(-3px);
}
.lt-categories__icon-svg {
    width: 48px;
    height: 48px;
    color: var(--lt-near-black);
}
.lt-categories__name {
    font-family: 'Raleway', sans-serif;
    font-size: 0.9375rem;
    font-weight: 600;
    line-height: 1.3;
    max-width: 8rem;
}

/* --- Featured Work --------------------------------------------------- */
.lt-featured {
    background-color: var(--lt-near-white);
    padding: 3.5rem 1rem;
}
.lt-featured__heading {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 2rem;
    text-align: center;
    color: var(--lt-near-black);
    margin: 0 0 0.5rem;
}
.lt-featured__lede {
    text-align: center;
    color: var(--lt-soft-gray);
    max-width: 540px;
    margin: 0 auto 2.5rem;
    font-size: 1rem;
}
.lt-featured__grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.5rem;
    max-width: 1100px;
    margin: 0 auto;
}
@media (min-width: 768px) {
    .lt-featured__grid { grid-template-columns: repeat(3, 1fr); gap: 2rem; }
}
.lt-featured__card {
    background-color: var(--lt-white);
    border-radius: 0.5rem;
    overflow: hidden;
    text-decoration: none;
    color: inherit;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    display: block;
}
.lt-featured__card:hover,
.lt-featured__card:focus-visible {
    transform: translateY(-3px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}
.lt-featured__image {
    width: 100%;
    aspect-ratio: 4 / 3;
    background-color: var(--lt-blush-tint);
    background-size: cover;
    background-position: center;
}
.lt-featured__body {
    padding: 1rem 1.25rem 1.25rem;
}
.lt-featured__category {
    font-family: 'Raleway', sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--lt-soft-gray);
    margin: 0 0 0.4rem;
}
.lt-featured__title {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 1.25rem;
    color: var(--lt-near-black);
    margin: 0;
    line-height: 1.25;
}
.lt-featured__viewall {
    text-align: center;
    margin: 2rem 0 0;
}
.lt-featured__viewall a {
    display: inline-block;
    padding: 0.625rem 1.5rem;
    color: var(--lt-near-black);
    text-decoration: none;
    border: 1px solid var(--lt-near-black);
    border-radius: 0.375rem;
    font-family: 'Raleway', sans-serif;
    font-weight: 600;
    font-size: 0.9375rem;
}
.lt-featured__viewall a:hover,
.lt-featured__viewall a:focus-visible {
    background-color: var(--lt-near-black);
    color: var(--lt-white);
}

/* --- Twisting & Face Painting spotlight ----------------------------- */
.lt-twisting-spotlight {
    background-color: var(--lt-white);
    padding: 3.5rem 1rem;
}
.lt-twisting-spotlight__inner {
    max-width: 1100px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 1fr;
    gap: 2rem;
    align-items: center;
}
@media (min-width: 768px) {
    .lt-twisting-spotlight__inner {
        grid-template-columns: 1fr 1fr;
        gap: 3rem;
    }
}
.lt-twisting-spotlight__image {
    width: 100%;
    aspect-ratio: 4 / 3;
    background-color: var(--lt-blue-tint);
    background-image: url('/assets/locally_twisted/images/home/twisting.jpg');
    background-size: cover;
    background-position: center;
    border-radius: 0.5rem;
}
.lt-twisting-spotlight__eyebrow {
    font-family: 'Raleway', sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--lt-soft-gray);
    margin: 0 0 0.5rem;
}
.lt-twisting-spotlight__heading {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 1.875rem;
    color: var(--lt-near-black);
    margin: 0 0 1rem;
    line-height: 1.2;
}
.lt-twisting-spotlight__body p {
    font-family: 'Raleway', sans-serif;
    font-size: 1rem;
    color: var(--lt-near-black);
    margin: 0 0 1rem;
    line-height: 1.6;
}
.lt-twisting-spotlight__cta {
    display: inline-flex;
    align-items: center;
    padding: 0.75rem 1.5rem;
    background-color: var(--lt-teal);
    color: var(--lt-white);
    text-decoration: none;
    border-radius: 0.375rem;
    font-family: 'Raleway', sans-serif;
    font-weight: 600;
    margin-top: 0.5rem;
}
.lt-twisting-spotlight__cta:hover,
.lt-twisting-spotlight__cta:focus-visible {
    background-color: #006666;
    color: var(--lt-white);
}

/* --- Client Logo Crawl ---------------------------------------------- */
.lt-crawl {
    background-color: var(--lt-blush-tint);
    padding: 2.5rem 0 3rem;
    overflow: hidden;
}
.lt-crawl__heading {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 1.5rem;
    text-align: center;
    color: var(--lt-near-black);
    margin: 0 0 1.5rem;
    padding: 0 1rem;
}
@media (min-width: 768px) {
    .lt-crawl__heading { font-size: 1.875rem; }
}
.lt-crawl__viewport {
    overflow: hidden;
    width: 100%;
    mask-image: linear-gradient(
        to right,
        transparent 0,
        #000 5%,
        #000 95%,
        transparent 100%
    );
    -webkit-mask-image: linear-gradient(
        to right,
        transparent 0,
        #000 5%,
        #000 95%,
        transparent 100%
    );
}
.lt-crawl__track {
    display: flex;
    align-items: center;
    width: max-content;
    animation: lt-crawl-scroll 90s linear infinite;
}
.lt-crawl__item {
    flex: 0 0 auto;
    padding: 0 1.75rem;
    font-family: 'Raleway', sans-serif;
    font-size: 1rem;
    font-weight: 500;
    color: var(--lt-near-black);
    white-space: nowrap;
    opacity: 0.7;
}
@keyframes lt-crawl-scroll {
    from { transform: translateX(0); }
    to   { transform: translateX(-50%); }
}
@media (prefers-reduced-motion: reduce) {
    .lt-crawl__track {
        animation: none;
        flex-wrap: wrap;
        justify-content: center;
        width: 100%;
    }
    .lt-crawl__item { padding: 0.4rem 1rem; }
}

/* --- About snippet --------------------------------------------------- */
.lt-about {
    background-color: var(--lt-white);
    padding: 3rem 1rem;
}
.lt-about__inner {
    max-width: 720px;
    margin: 0 auto;
    text-align: center;
}
.lt-about__eyebrow {
    font-family: 'Raleway', sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--lt-soft-gray);
    margin: 0 0 0.5rem;
    text-align: center;
}
.lt-about__heading {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 1.875rem;
    color: var(--lt-near-black);
    margin: 0 0 1rem;
    line-height: 1.2;
    text-align: center;
}
.lt-about__body {
    font-family: 'Raleway', sans-serif;
    font-size: 1.0625rem;
    color: var(--lt-near-black);
    margin: 0;
    line-height: 1.65;
    text-align: center;
}

/* --- Closing CTA ----------------------------------------------------- */
.lt-cta {
    background-color: var(--lt-soft-blue, var(--lt-blue-tint));
    padding: 3.5rem 1rem;
    text-align: center;
}
.lt-cta__heading {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 2.25rem;
    color: var(--lt-near-black);
    margin: 0 0 1rem;
    line-height: 1.15;
    text-align: center;
}
.lt-cta__body {
    font-family: 'Raleway', sans-serif;
    font-size: 1.125rem;
    color: var(--lt-near-black);
    max-width: 620px;
    margin: 0 auto 1.75rem;
    line-height: 1.55;
    text-align: center;
}
.lt-cta__button {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.875rem 2rem;
    background-color: var(--lt-teal);
    color: var(--lt-white);
    text-decoration: none;
    border-radius: 0.375rem;
    font-family: 'Raleway', sans-serif;
    font-weight: 600;
    font-size: 1rem;
    min-height: 48px;
}
.lt-cta__button:hover,
.lt-cta__button:focus-visible {
    background-color: #006666;
    color: var(--lt-white);
    outline: 2px solid var(--lt-near-black);
    outline-offset: 2px;
}
@media (min-width: 768px) {
    .lt-cta__heading { font-size: 2.75rem; }
}
"""


def get_context(context):
    context.title = "Locally Twisted — Utah's Balloon Specialists | Custom Event Decor"
    context.metatags = {
        "description": (
            "Utah's premier balloon specialists for over 25 years. Custom arches, "
            "garlands, drops, twisting, and face painting for weddings, birthdays, "
            "and corporate events across the Wasatch Front."
        ),
        "og:title": "Locally Twisted — Utah's Balloon Specialists",
        "og:description": "Custom balloon decor for celebrations across the Wasatch Front since 1998.",
        "og:type": "website",
    }
    context.client_crawl = CLIENT_CRAWL
    context.custom_categories = CUSTOM_CATEGORIES
    context.featured_work = FEATURED_WORK
    context.colocated_css = PAGE_CSS
    return context
