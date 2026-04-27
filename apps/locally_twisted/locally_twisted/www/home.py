"""Homepage controller — `/` route. v2.

v2 changes (per GL feedback 2026-04-27):
- Hero: cycling headline (placeholder for future blog post titles) +
  stable tagline below + single CTA. Photo stays static.
- Reviews block replaces the prior trust strip ("Since 1998 / Custom
  Designs / Made with Love"). Shows stars + count + placeholder slot
  for 3 real Google review quotes.
- Three-dot divider element between key sections, brand-Teal.
- Recent Celebrations photos significantly bigger (taller aspect, wider
  container).
- Twisting & Face Painting spotlight moved to bottom of page (per
  business strategy: big-event work leads, twisting/face painting is
  a smaller revenue line).
- About snippet removed (defer until Jeff is ready, per GL 2026-04-27).
- Client crawl slowed 50% (90s -> 180s).
- Sections that should read as bands now use the .lt-fullbleed pattern
  to break out of Frappe's constraining parent .container.
- Inner content max-widths bumped to ~1200px so the page feels grand
  on desktop.

Voice and copy carry from the approved Odoo XML (homepage.xml +
snippet templates) where they exist; cycling headline lines are pulled
from the gallery/ design competition voice docs (designer-1, -3, -5
all converge on the same Quiet Confidence rules from BRIEF.md).
"""
import frappe

no_cache = 1
sitemap = 1


# Cycling hero headlines. These rotate via CSS animation in the hero —
# stable tagline below stays put. When the blog framework ships
# (Slice 14), these get replaced by the latest blog post titles
# pulled from `frappe.get_list("Blog Post", ...)`.
HERO_CYCLING_TITLES = [
    "Twenty-eight years, made by hand.",
    "Every arch begins with a color conversation.",
    "We make things people remember.",
    "Custom balloon decor, Wasatch Front.",
]


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


# The 6 customizable categories — these are the items GL/Jeff actually
# customize (arches, columns, garlands, backdrops, drops, bouquets). Each
# will eventually point at a Lookbook category page (Slice 7) and into
# the future Design Studio interactive experience (post-Slice 9).
# Bouquets added 2026-04-27 per GL — also customizable in Jeff's business.
CUSTOM_CATEGORIES = [
    {"slug": "balloon-arches", "name": "Balloon Arches", "icon": "arch"},
    {"slug": "columns-and-pillars", "name": "Columns & Pillars", "icon": "column"},
    {"slug": "organic-garlands", "name": "Organic Garlands", "icon": "garland"},
    {"slug": "picture-perfect-backdrops", "name": "Picture Perfect Backdrops", "icon": "backdrop"},
    {"slug": "balloon-drops", "name": "Balloon Drops", "icon": "drop"},
    {"slug": "balloon-bouquets", "name": "Balloon Bouquets", "icon": "bouquet"},
]


# Featured work — 3 case-study cards (odd ≤ 3 → single row per GL's
# symmetry rule). Photos and event names are placeholder until GL
# surfaces real ones from Jeff's archive.
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


# Reviews carousel — horizontal-scrolling marquee of customer praise.
# Per GL 2026-04-27: 28 years in business deserves a carousel of real
# reviews, not just 5 inline cards. Words matter more than client logos
# for an event-decor business. When GL pastes the JSON from the
# browser-Claude prompt, REVIEW_QUOTES becomes a list of dicts:
#   {"name": "Sarah K.", "rating": 5, "date": "2025-11", "source": "Google",
#    "event": "wedding", "text": "Full review verbatim..."}
# Until then, None entries render as clearly-marked placeholder cards.
REVIEW_QUOTES = [
    {
        "name": "Bobbie Weyland", "rating": 5, "date": "2026-04",
        "source": "Google", "event": "delivery",
        "text": "Great company to work with and same day delivery.",
    },
    {
        "name": "Craig Campbell", "rating": 5, "date": "2026-03",
        "source": "Google", "event": "event decor",
        "text": "Awesome place for your party or event decor!! Jeff and his team do an outstanding job and customize the decor to fit your needs. HIGHLY recommend Locally Twisted!!",
    },
    {
        "name": "Maria Manby", "rating": 5, "date": "2026-03",
        "source": "Google", "event": None,
        "text": "Very helpful and customer service oriented!",
    },
    {
        "name": "KJSCOTT", "rating": 5, "date": "2026-03",
        "source": "Google", "event": "memorial",
        "text": "I needed a sports themed funeral stand. I reached out to Totally Twisted. I told them what I needed, they captured my vision, delivered on time, very reasonable, and had many complements. Very tasteful and meaningful. Highly recommend!",
    },
    {
        "name": "Vishal Lakhani", "rating": 5, "date": "2026-02",
        "source": "Google", "event": "out-of-town client",
        "text": "Jeff and the team are amazing. I am not local to the area so I really need their assistance and they were simply brilliant. They provided an amazing product and went above and beyond. Top service. Using Locally Twisted is a no-brainer. I wish I could give them 6 stars!",
    },
    {
        "name": "Victoria Fischer", "rating": 5, "date": "2025-12",
        "source": "Google", "event": "kids party",
        "text": "So easy to book. Even on short notice. Wendy was amazing! She brought our 4 year old a Lego Minifigure balloon and handled a room full of tiny humans with wild requests. Would definitely recommend her!",
    },
    {
        "name": "Leslie Barcus", "rating": 5, "date": "2025-12",
        "source": "Google", "event": "balloon twisting + face painting",
        "text": "Lovely balloon display, excellent balloon twisting into all kinds of interesting animals and shapes — and a really talented face painter for our event. Very fun!",
    },
    {
        "name": "Hannah Hinde", "rating": 5, "date": "2025-09",
        "source": "Google", "event": "school",
        "text": "Amazing group and amazing artists! They are our school's new go-to group for all the balloon animals!",
    },
    {
        "name": "Kyley Jex", "rating": 5, "date": "2025-08",
        "source": "Google", "event": "neighborhood event",
        "text": "Locally Twisted was a hit at our neighborhood summer bash! The kids LOVED the variety of the balloon art. The biggest line at the party for sure.",
    },
    {
        "name": "Sara Mejeur", "rating": 5, "date": "2025-07",
        "source": "Google", "event": "longtime client",
        "text": "I LOVE Locally Twisted! Jeff has been listed in my phone for 7-ish years as “balloon guy” and has been my go-to for that long. I know I can trust him and his team to always exceed my expectations. They make every event I plan easier and extra special!!",
    },
    {
        "name": "Matt Tipton", "rating": 5, "date": "2025-07",
        "source": "Google", "event": "face painting",
        "text": "Our face painters were EXCELLENT!! They were on time. Their setup was incredibly professional. They probably painted 50 faces, and made the day of every single person. Great job!!",
    },
    {
        "name": "Lindsay", "rating": 5, "date": "2025-06",
        "source": "Google", "event": "ribbon cutting",
        "text": "They provided a balloon arch for our ribbon cutting. They were wonderful to work with, very responsive, and the arch looked great!",
    },
    {
        "name": "Mary DeMann", "rating": 5, "date": "2025-06",
        "source": "Google", "event": "corporate",
        "text": "Locally Twisted is truly the best! Jeff is always kind, professional, and reliable. We've hired Locally Twisted for multiple company events, and every time, our guests have been amazed by the incredible balloon art. They consistently impress and add a fun, memorable touch to our gatherings.",
    },
    {
        "name": "LuAnn Keith", "rating": 5, "date": "2025-05",
        "source": "Google", "event": "Mother's Day",
        "text": "They went above and beyond what they needed to do for my mom's Mother's Day gift. I made a mistake on the delivery date and they fixed the date and made the delivery. I will definitely order again! Thank you Locally Twisted for fixing my mistake!",
    },
    {
        "name": "Sarah Johnston-Powell", "rating": 5, "date": "2025-05",
        "source": "Google", "event": "birthday",
        "text": "Jeff was super nice and helpful, helped me figure out the perfect thing for our son's birthday. Prompt, accommodating, great communication and friendly!",
    },
    {
        "name": "Tiffiny Lipscomb", "rating": 5, "date": "2025-04",
        "source": "Google", "event": "family events",
        "text": "Locally Twisted has done a phenomenal job on many occasions (I don't use that word lightly!). They are kind, friendly, and have done some rush jobs for me. In fact, they are now my go-to easy decorating plan for any of my family events. I don't have to do anything, my house is festive, and I get to enjoy it too! Five big stars!",
    },
    {
        "name": "Mark Taylor", "rating": 5, "date": "2025-04",
        "source": "Google", "event": "wedding + birthday",
        "text": "I have told so many people about how much we loved the balloon creations at a friend's wedding. We were seriously blown away and my kids were delighted. My oldest son requested they come to his birthday party. They were fantastic!",
    },
    {
        "name": "Em Cebrowski", "rating": 5, "date": "2025-04",
        "source": "Google", "event": "church picnic",
        "text": "Our balloon artist was Marianne — she was kind, organized, creative, and worked for two hours straight in the blazing heat. We hired her for a church picnic; all the children were delighted with their balloons, and so were several adults. Thank you Locally Twisted for making our party extra special.",
    },
    {
        "name": "Alisha", "rating": 5, "date": "2025-04",
        "source": "Google", "event": "personal",
        "text": "You made this sick girl smile with this big unicorn balloon. Very professional and wanted to give me exactly what I wanted. We spent a few days texting back and forth and you came through with exactly what I wanted. Thank you!",
    },
]


PAGE_CSS = """
/* ======================================================================
 * HOMEPAGE v2 — lookbook-forward shape (lookbook-led, twisting at bottom)
 * BEM blocks: lt-hero, lt-reviews-block, lt-divider, lt-categories,
 *             lt-featured, lt-crawl, lt-cta, lt-twisting-spotlight
 * Uses CSS variables from lt-theme.css (--lt-teal, --lt-near-black, etc.)
 * ====================================================================== */

/* --- Visually hidden (screen-reader only) --------------------------- */
.lt-hero ~ * .visually-hidden,
.visually-hidden {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
}

/* --- Full-bleed helper ---------------------------------------------- */
/* Frappe's templates/web.html wraps content in a max-width .container.
 * Sections that should read as full-width horizontal bands need to
 * break out via this technique. Used on hero, reviews, featured, crawl,
 * twisting spotlight, and the closing CTA. */
.lt-fullbleed {
    width: 100vw;
    position: relative;
    left: 50%;
    right: 50%;
    margin-left: -50vw;
    margin-right: -50vw;
}

/* --- 3-dot divider --------------------------------------------------- */
.lt-divider {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.75rem;
    padding: 1.75rem 0;
    background-color: var(--lt-white);
}
.lt-divider span {
    display: block;
    width: 0.45rem;
    height: 0.45rem;
    border-radius: 50%;
    background-color: var(--lt-teal);
    opacity: 0.55;
}

/* --- Hero ------------------------------------------------------------ */
.lt-hero {
    position: relative;
    min-height: 580px;
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
        rgba(0, 0, 0, 0) 30%,
        rgba(0, 0, 0, 0.65) 100%
    );
}
.lt-hero__content {
    position: relative;
    z-index: 1;
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 3rem 1.5rem 2.75rem;
    text-align: center;
    color: var(--lt-white);
}
.lt-hero__eyebrow {
    font-family: 'Raleway', sans-serif;
    font-size: 0.875rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin: 0 0 0.75rem;
    opacity: 0.92;
    text-align: center;
}
.lt-hero__cycling {
    position: relative;
    min-height: 4.4rem;
    margin: 0 0 0.75rem;
}
.lt-hero__title {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 2.25rem;
    line-height: 1.1;
    color: var(--lt-white);
    text-align: center;
    margin: 0;
    opacity: 0;
    animation: lt-hero-cycle 32s infinite;
}
/* Stagger 4 titles — each visible ~6.5s out of 32s */
.lt-hero__title:nth-child(1) { animation-delay: 0s; }
.lt-hero__title:nth-child(2) { animation-delay: 8s; }
.lt-hero__title:nth-child(3) { animation-delay: 16s; }
.lt-hero__title:nth-child(4) { animation-delay: 24s; }
@keyframes lt-hero-cycle {
    0%   { opacity: 0; }
    3%   { opacity: 1; }
    22%  { opacity: 1; }
    25%  { opacity: 0; }
    100% { opacity: 0; }
}
@media (prefers-reduced-motion: reduce) {
    .lt-hero__title {
        animation: none;
        opacity: 0;
    }
    .lt-hero__title:nth-child(1) { opacity: 1; }
}
.lt-hero__tagline {
    font-family: 'Raleway', sans-serif;
    font-size: 1.0625rem;
    margin: 0 auto 1.75rem;
    max-width: 38ch;
    font-weight: 300;
    color: rgba(255, 255, 255, 0.96);
    text-align: center;
    letter-spacing: 0.01em;
}
.lt-hero__cta {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.95rem 2rem;
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
    .lt-hero { min-height: 680px; }
    .lt-hero__content { padding: 4.5rem 2rem 4rem; }
    .lt-hero__cycling { min-height: 5.5rem; }
    .lt-hero__title { font-size: 3.75rem; }
    .lt-hero__tagline { font-size: 1.25rem; }
}

/* --- Reviews block (replaces the prior trust strip) ----------------- */
.lt-reviews-block {
    background-color: var(--lt-blue-tint);
    padding: 3rem 1rem 3.5rem;
}
.lt-reviews-block__inner {
    max-width: 1200px;
    margin: 0 auto;
    text-align: center;
}
.lt-reviews-block__badge {
    display: inline-flex;
    flex-direction: column;
    align-items: center;
    gap: 0.4rem;
    margin: 0 0 2rem;
    text-decoration: none;
    color: var(--lt-near-black);
}
.lt-reviews-block__stars {
    color: #f5b400;
    font-size: 1.625rem;
    letter-spacing: 0.1em;
    line-height: 1;
}
.lt-reviews-block__score {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 2rem;
    color: var(--lt-near-black);
}
.lt-reviews-block__count {
    font-family: 'Raleway', sans-serif;
    font-size: 0.95rem;
    color: var(--lt-soft-gray);
}
/* Reviews carousel — horizontal-scrolling marquee of customer praise.
 * Pattern mirrors .lt-crawl but with full review cards instead of
 * client names. Speed is much slower (360s vs 180s) because the
 * cards need reading time. Pauses on hover/focus.
 * Per GL 2026-04-27: "carousel review of praise that matter more
 * than the carousel of businesses at the bottom." */
.lt-reviews-block__quotes {
    overflow: hidden;
    width: 100%;
    margin: 0;
    mask-image: linear-gradient(
        to right, transparent 0, #000 4%, #000 96%, transparent 100%
    );
    -webkit-mask-image: linear-gradient(
        to right, transparent 0, #000 4%, #000 96%, transparent 100%
    );
}
.lt-reviews-block__track {
    display: flex;
    align-items: stretch;
    gap: 1rem;
    width: max-content;
    animation: lt-reviews-scroll 360s linear infinite;
}
.lt-reviews-block__quotes:hover .lt-reviews-block__track,
.lt-reviews-block__track:focus-within {
    animation-play-state: paused;
}
@keyframes lt-reviews-scroll {
    from { transform: translateX(0); }
    to   { transform: translateX(-50%); }
}
@media (prefers-reduced-motion: reduce) {
    .lt-reviews-block__quotes { mask-image: none; -webkit-mask-image: none; }
    .lt-reviews-block__track {
        animation: none;
        flex-wrap: wrap;
        justify-content: center;
        width: 100%;
    }
}
.lt-reviews-block__quote {
    flex: 0 0 320px;
    background-color: var(--lt-white);
    border-radius: 0.5rem;
    padding: 1.5rem 1.5rem 1.25rem;
    text-align: left;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    display: flex;
    flex-direction: column;
}
.lt-reviews-block__quote-mark {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 2.5rem;
    color: var(--lt-teal);
    line-height: 1;
    margin: 0 0 0.5rem;
    opacity: 0.6;
}
.lt-reviews-block__quote-text {
    font-family: 'Raleway', sans-serif;
    font-size: 0.95rem;
    color: var(--lt-near-black);
    line-height: 1.55;
    margin: 0 0 0.75rem;
    min-height: 3.5rem;
}
.lt-reviews-block__quote-attr {
    font-family: 'Raleway', sans-serif;
    font-size: 0.8125rem;
    color: var(--lt-soft-gray);
    margin: 0 0 0.75rem;
}
.lt-reviews-block__quote-stars {
    color: #f5b400;
    font-size: 1rem;
    letter-spacing: 0.12em;
    line-height: 1;
    margin-top: auto;  /* push to bottom of flex-column card */
    padding-top: 0.5rem;
}
.lt-reviews-block__quote--placeholder {
    background-color: rgba(255, 255, 255, 0.5);
    border: 1px dashed var(--lt-soft-gray);
}
.lt-reviews-block__quote--placeholder .lt-reviews-block__quote-text {
    color: var(--lt-soft-gray);
    font-style: italic;
}

/* --- Custom Creations categories ------------------------------------ */
.lt-categories {
    background-color: var(--lt-white);
    padding: 4rem 1rem;
}
.lt-categories__heading {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 2.25rem;
    text-align: center;
    color: var(--lt-near-black);
    margin: 0 0 0.5rem;
}
.lt-categories__lede {
    text-align: center;
    color: var(--lt-soft-gray);
    max-width: 540px;
    margin: 0 auto 2.75rem;
    font-size: 1rem;
}
.lt-categories__grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 2rem 1.5rem;
    max-width: 1200px;
    margin: 0 auto;
}
@media (min-width: 768px) {
    .lt-categories__grid {
        grid-template-columns: repeat(5, 1fr);
        gap: 2rem;
    }
}
.lt-categories__item {
    text-align: center;
}
.lt-categories__link {
    display: inline-flex;
    flex-direction: column;
    align-items: center;
    gap: 0.85rem;
    text-decoration: none;
    color: var(--lt-near-black);
}
.lt-categories__circle {
    width: 130px;
    height: 130px;
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
    width: 56px;
    height: 56px;
    color: var(--lt-near-black);
}
.lt-categories__name {
    font-family: 'Raleway', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    line-height: 1.3;
    max-width: 9rem;
}

/* --- Featured Work (Recent Celebrations) ---------------------------- */
.lt-featured {
    background-color: var(--lt-near-white);
    padding: 4rem 1rem 4.5rem;
}
.lt-featured__inner {
    max-width: 1300px;
    margin: 0 auto;
}
.lt-featured__heading {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 2.25rem;
    text-align: center;
    color: var(--lt-near-black);
    margin: 0 0 0.5rem;
}
.lt-featured__lede {
    text-align: center;
    color: var(--lt-soft-gray);
    max-width: 580px;
    margin: 0 auto 3rem;
    font-size: 1rem;
}
.lt-featured__grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.5rem;
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
    transform: translateY(-4px);
    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.12);
}
.lt-featured__image {
    width: 100%;
    aspect-ratio: 4 / 5;
    background-color: var(--lt-blush-tint);
    background-size: cover;
    background-position: center;
}
.lt-featured__body {
    padding: 1.25rem 1.5rem 1.5rem;
}
.lt-featured__category {
    font-family: 'Raleway', sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--lt-soft-gray);
    margin: 0 0 0.5rem;
}
.lt-featured__title {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 1.375rem;
    color: var(--lt-near-black);
    margin: 0;
    line-height: 1.25;
}
.lt-featured__viewall {
    text-align: center;
    margin: 2.5rem 0 0;
}
.lt-featured__viewall a {
    display: inline-block;
    padding: 0.75rem 1.75rem;
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

/* --- Client Logo Crawl ---------------------------------------------- */
.lt-crawl {
    background-color: var(--lt-blush-tint);
    padding: 2.75rem 0 3.25rem;
    overflow: hidden;
}
.lt-crawl__heading {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 1.625rem;
    text-align: center;
    color: var(--lt-near-black);
    margin: 0 0 1.75rem;
    padding: 0 1rem;
}
@media (min-width: 768px) {
    .lt-crawl__heading { font-size: 2rem; }
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
    /* v2: 90s -> 180s per GL feedback (was moving way too fast)
     * v3: 180s -> 270s — still too fast at 180s. */
    animation: lt-crawl-scroll 270s linear infinite;
}
.lt-crawl__item {
    flex: 0 0 auto;
    padding: 0 2rem;
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

/* --- Closing CTA ---------------------------------------------------- */
.lt-cta {
    background-color: var(--lt-soft-blue, var(--lt-blue-tint));
    padding: 4rem 1rem 4.5rem;
    text-align: center;
}
.lt-cta__inner {
    max-width: 1200px;
    margin: 0 auto;
}
.lt-cta__heading {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 2.5rem;
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
    padding: 0.95rem 2rem;
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
    .lt-cta__heading { font-size: 3rem; }
}

/* --- Twisting & Face Painting spotlight (now at bottom) ------------ */
.lt-twisting-spotlight {
    background-color: var(--lt-white);
    padding: 4rem 1rem;
}
.lt-twisting-spotlight__inner {
    max-width: 1200px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 1fr;
    gap: 2rem;
    align-items: center;
}
@media (min-width: 768px) {
    .lt-twisting-spotlight__inner {
        grid-template-columns: 1fr 1fr;
        gap: 3.5rem;
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
    letter-spacing: 0.12em;
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
    context.hero_cycling_titles = HERO_CYCLING_TITLES
    context.client_crawl = CLIENT_CRAWL
    context.custom_categories = CUSTOM_CATEGORIES
    context.featured_work = FEATURED_WORK
    context.review_quotes = REVIEW_QUOTES
    context.colocated_css = PAGE_CSS
    return context
