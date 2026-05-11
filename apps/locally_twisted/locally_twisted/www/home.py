"""Homepage controller for the public `/` route.

Current launch shape: civic/Utah hero, Google review proof crawl,
wide installed-work proof photos, full-stage client proof crawl,
custom decor discovery, a contact CTA, and secondary twisting/face-painting
support.
"""
import frappe

from locally_twisted.seo import business_graph

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


# The 8 customizable categories - items Jeff actually customizes for events.
# These point at the Portfolio and current Event Balloons route while the
# interactive Event Playground work remains outside the ASAP launch lane.
# Updated 2026-04-28 per GL:
# Columns is the canonical name; Garlands replaces "Organic Garlands"
# (organic remains an option, not a separate product); Centerpieces and
# Custom Sculptures added (Sculptures = the "anything you imagine" bucket
# - characters, themed shapes, one-off builds; distinct from balloon
# twisting entertainment which lives at /balloon-twisting-and-face-painting).
CUSTOM_CATEGORIES = [
    {"slug": "balloon-arches", "name": "Balloon Arches", "icon": "arch"},
    {"slug": "columns", "name": "Columns", "icon": "column"},
    {"slug": "garlands", "name": "Garlands", "icon": "garland"},
    {"slug": "picture-perfect-backdrops", "name": "Picture Perfect Backdrops", "icon": "backdrop"},
    {"slug": "balloon-drops", "name": "Balloon Drops", "icon": "drop"},
    {"slug": "balloon-bouquets", "name": "Balloon Bouquets", "icon": "bouquet"},
    {"slug": "centerpieces", "name": "Centerpieces", "icon": "centerpiece"},
    {"slug": "custom-sculptures", "name": "Custom Sculptures", "icon": "sculpture"},
]


# Featured work - 3 curated custom-install proof cards. Review and replace
# when the next approved one-of-a-kind photo packet is selected.
FEATURED_WORK = [
    {
        "category": "Balloon Arches",
        "title": "Corporate Brand Entrance",
        "image": "/assets/locally_twisted/images/portfolio/corporate-logo-arch.png",
        "alt": "Corporate brand balloon arch installed at an event entrance",
    },
    {
        "category": "Schools",
        "title": "Back-to-School Stage",
        "image": "/assets/locally_twisted/images/portfolio/school-back-to-school-stage.png",
        "alt": "Large balloon stage display for a school event",
    },
    {
        "category": "Corporate Decor",
        "title": "Festival Photo Moment",
        "image": "/assets/locally_twisted/images/portfolio/corporate-weberstock-photo-opt.png",
        "alt": "Large event balloon photo backdrop for a branded festival",
    },
]


HOME_HERO_SLIDES = [
    {
        "kicker": "Graduation season",
        "title": "Graduation balloon decor for Utah schools and families.",
        "proofline": "Now featuring grad garlands, stages, and photo moments.",
        "body": "Celebrate the class of 2026 with polished balloon installs for ceremonies, senior nights, grad parties, and campus events.",
        "image": "/assets/locally_twisted/images/portfolio/optimized/school-grad-garland.webp",
        "primary_label": "Plan graduation decor",
        "primary_url": "/contact?intent=quote&source=home-hero-graduation",
        "secondary_label": "See event balloons",
        "secondary_url": "/event-balloons",
    },
    {
        "kicker": "Civic & community",
        "title": "Balloon moments for public events and community gatherings.",
        "proofline": "Parades, city events, Pride, fairs, and public celebrations.",
        "body": "Create a welcoming entrance, stage, booth, or photo moment that helps the whole event feel organized and alive.",
        "image": "/assets/locally_twisted/images/portfolio/optimized/seasonal-pride-columns.webp",
        "primary_label": "Explore civic events",
        "primary_url": "/civic-community",
        "secondary_label": "Start a quote",
        "secondary_url": "/contact?intent=quote&source=home-hero-civic",
    },
    {
        "kicker": "Corporate events",
        "title": "Brand-ready balloon decor for business events.",
        "proofline": "Entrances, launches, client events, open houses, and staff celebrations.",
        "body": "Match colors, logos, and room flow so the event looks intentional without making your team babysit the decor.",
        "image": "/assets/locally_twisted/images/portfolio/optimized/corporate-logo-arch.webp",
        "primary_label": "Explore corporate events",
        "primary_url": "/corporate-events",
        "secondary_label": "Start a quote",
        "secondary_url": "/contact?intent=quote&source=home-hero-corporate",
    },
    {
        "kicker": "Schools & campuses",
        "title": "School balloon decor for big days on campus.",
        "proofline": "Graduations, back-to-school, senior nights, dances, and fundraisers.",
        "body": "Give students, staff, and families a photo-ready moment that feels festive, clear, and easy to navigate.",
        "image": "/assets/locally_twisted/images/portfolio/optimized/school-back-to-school-stage.webp",
        "primary_label": "Explore school events",
        "primary_url": "/schools-campuses",
        "secondary_label": "Start a quote",
        "secondary_url": "/contact?intent=quote&source=home-hero-schools",
    },
    {
        "kicker": "Private celebrations",
        "title": "Personal celebration decor that still feels polished.",
        "proofline": "Birthdays, weddings, showers, anniversaries, and family milestones.",
        "body": "Bring color, shape, and a finished focal point to the party without turning setup into another full-time job.",
        "image": "/assets/locally_twisted/images/portfolio/optimized/wedding-floral-half-arch.webp",
        "primary_label": "Explore private celebrations",
        "primary_url": "/private-celebrations",
        "secondary_label": "Start a quote",
        "secondary_url": "/contact?intent=quote&source=home-hero-private",
    },
]


# Reviews carousel - horizontal-scrolling proof from customer praise. Keep
# rating/count claims out of the visible badge unless they are reverified.
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
        "text": "Lovely balloon display, excellent balloon twisting into all kinds of interesting animals and shapes, plus a really talented face painter for our event. Very fun!",
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
        "text": "I LOVE Locally Twisted! Jeff has been listed in my phone for 7-ish years as \"balloon guy\" and has been my go-to for that long. I know I can trust him and his team to always exceed my expectations. They make every event I plan easier and extra special!!",
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
        "text": "Our balloon artist was Marianne; she was kind, organized, creative, and worked for two hours straight in the blazing heat. We hired her for a church picnic; all the children were delighted with their balloons, and so were several adults. Thank you Locally Twisted for making our party extra special.",
    },
    {
        "name": "Alisha", "rating": 5, "date": "2025-04",
        "source": "Google", "event": "personal",
        "text": "You made this sick girl smile with this big unicorn balloon. Very professional and wanted to give me exactly what I wanted. We spent a few days texting back and forth and you came through with exactly what I wanted. Thank you!",
    },
]


PAGE_CSS = """
/* ======================================================================
 * Launch homepage - proof-first event decor shape
 * BEM blocks: lt-hero, lt-authority, lt-featured, lt-reviews-block,
 *             lt-divider, lt-categories, lt-crawl, lt-cta,
 *             lt-twisting-spotlight
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
/* The shared page shell wraps content in a max-width .container.
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
    background-color: var(--lt-brass);
    opacity: 0.75;
}

/* --- Hero ------------------------------------------------------------ */
.lt-hero {
    position: relative;
    min-height: 220px;
    height: 220px;
    max-height: 220px;
    background-color: var(--lt-navy);
    padding: 0;
    overflow: hidden;
}
.lt-hero__slide {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    opacity: 0;
    pointer-events: none;
    animation: lt-home-hero-carousel 40s infinite;
}
.lt-hero__slide:nth-child(1) { animation-delay: 0s; }
.lt-hero__slide:nth-child(2) { animation-delay: 8s; }
.lt-hero__slide:nth-child(3) { animation-delay: 16s; }
.lt-hero__slide:nth-child(4) { animation-delay: 24s; }
.lt-hero__slide:nth-child(5) { animation-delay: 32s; }
.lt-hero__slide--active,
.lt-hero__slide:focus-within {
    pointer-events: auto;
}
.lt-hero[data-lt-hero-enhanced="true"] .lt-hero__slide {
    animation: none;
    opacity: 0;
    pointer-events: none;
    transition: opacity 500ms ease;
}
.lt-hero[data-lt-hero-enhanced="true"] .lt-hero__slide--active {
    opacity: 1;
    pointer-events: auto;
}
.lt-hero__image {
    position: absolute;
    inset: 0;
    background-size: cover;
    background-position: center;
    background-color: var(--lt-navy);
}
.lt-hero__image::after {
    content: '';
    position: absolute;
    inset: 0;
    background:
        linear-gradient(90deg, rgba(10, 10, 11, 0.88) 0%, rgba(14, 34, 64, 0.72) 42%, rgba(14, 34, 64, 0.12) 100%),
        linear-gradient(180deg, rgba(14, 34, 64, 0.05) 0%, rgba(10, 10, 11, 0.34) 100%);
}
.lt-hero__content {
    position: relative;
    z-index: 1;
    width: 100%;
    max-width: 1280px;
    margin: 0 auto;
    padding: 1.5rem 1rem;
    text-align: left;
    color: var(--lt-white);
}
@keyframes lt-home-hero-carousel {
    0% { opacity: 0; }
    2.5% { opacity: 1; pointer-events: auto; }
    17.5% { opacity: 1; pointer-events: auto; }
    20% { opacity: 0; }
    100% { opacity: 0; }
}
@media (prefers-reduced-motion: reduce) {
    .lt-hero__slide { animation: none; opacity: 0; }
    .lt-hero__slide:first-child { opacity: 1; pointer-events: auto; }
}
.lt-hero__eyebrow {
    font-family: var(--lt-font-body);
    font-size: 0.76rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    line-height: 1.12;
    text-transform: uppercase;
    margin: 0 0 0.3rem;
    color: var(--lt-brass);
    opacity: 0.95;
    text-align: left;
}
.lt-hero__title {
    font-family: var(--lt-font-heading);
    font-weight: 700;
    font-size: 1.92rem;
    line-height: 1.02;
    color: var(--lt-white);
    text-align: left;
    margin: 0 0 0.5rem;
    max-width: 18ch;
    animation: none;
}
.lt-hero__proofline {
    display: none;
    margin: 0;
    color: var(--lt-brass);
    font-family: var(--lt-font-body);
    font-size: 0.95rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    line-height: 1.35;
    text-transform: uppercase;
}
.lt-hero__tagline {
    font-family: var(--lt-font-body);
    font-size: 0.92rem;
    line-height: 1.3;
    margin: 0 0 0.65rem;
    max-width: 60ch;
    font-weight: 500;
    color: rgba(255, 255, 255, 0.96);
    text-align: left;
    letter-spacing: 0;
}
.lt-hero__cta {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.58rem 0.8rem;
    background-color: var(--lt-crimson);
    color: var(--lt-white);
    text-decoration: none;
    font-family: var(--lt-font-body);
    font-weight: 600;
    font-size: 0.84rem;
    border-radius: 0.375rem;
    min-height: 44px;
    line-height: 1.1;
}
.lt-hero__cta + .lt-hero__cta {
    margin-left: 0.5rem;
}
.lt-hero__cta--secondary {
    background-color: transparent;
    border: 1px solid rgba(250, 247, 242, 0.74);
}
.lt-hero__cta:hover,
.lt-hero__cta:focus-visible {
    background-color: var(--lt-navy);
    color: var(--lt-white);
    outline: 2px solid var(--lt-white);
    outline-offset: 2px;
}
@media (min-width: 768px) {
    .lt-hero {
        min-height: 250px;
        height: 250px;
        max-height: 250px;
    }
    .lt-hero__content { padding: 1.65rem 1.5rem; }
    .lt-hero__title {
        font-size: 2.42rem;
        line-height: 1;
        max-width: 32ch;
    }
    .lt-hero__tagline {
        font-size: 1rem;
        line-height: 1.25;
        margin-bottom: 0.55rem;
    }
    .lt-hero__cta {
        font-size: 0.94rem;
        padding-inline: 1.1rem;
    }
}
@media (min-width: 1200px) {
    .lt-hero {
        min-height: 280px;
        height: 280px;
        max-height: 280px;
    }
    .lt-hero__content { padding: 2rem; }
    .lt-hero__title {
        font-size: 2.55rem;
    }
}
@media (max-width: 575.98px) {
    .lt-hero {
        min-height: 220px;
        height: 220px;
        max-height: 220px;
        align-items: center;
    }
    .lt-hero__content {
        padding: 1.5rem 1rem;
    }
    .lt-hero__title {
        font-size: clamp(1.58rem, 7.3vw, 1.75rem);
        line-height: 1;
        max-width: none;
    }
    .lt-hero__proofline {
        margin-bottom: 0.65rem;
        font-size: 0.88rem;
    }
    .lt-hero__tagline {
        display: none;
    }
    .lt-hero__cta {
        width: calc(50% - 0.35rem);
        justify-content: center;
        padding-inline: 0.35rem;
    }
    .lt-hero__cta + .lt-hero__cta {
        margin-left: 0.45rem;
        margin-top: 0;
    }
}

/* --- Reviews block -------------------------------------------------- */
/* The review carousel uses a full-stage viewport so the fade-mask does
 * not clip readable card text on wide monitors. The badge stays centered;
 * the carousel viewport spans the full band so more cards are visible at
 * once and the mask fades into empty space, not readable text. */
.lt-reviews-block {
    background-color: var(--lt-near-white);
    padding: 2.2rem 1rem 2.4rem;
}
.lt-reviews-block__inner {
    /* Narrow column for the badge above the carousel. */
    max-width: 1200px;
    margin: 0 auto;
    text-align: center;
}
.lt-reviews-block__badge {
    display: inline-flex;
    flex-direction: column;
    align-items: center;
    gap: 0.4rem;
    margin: 0 0 1.1rem;
    text-decoration: none;
    color: var(--lt-navy);
}
.lt-reviews-block__stars {
    color: var(--lt-brass);
    font-size: 1.625rem;
    letter-spacing: 0.1em;
    line-height: 1;
}
.lt-reviews-block__score {
    font-family: var(--lt-font-heading);
    font-size: 2rem;
    color: var(--lt-near-black);
}
.lt-reviews-block__count {
    font-family: var(--lt-font-body);
    font-size: 0.95rem;
    color: var(--lt-soft-gray);
}
/* Reviews carousel - horizontal-scrolling marquee of customer praise.
 * Pattern mirrors .lt-crawl but with full review cards instead of
 * client names. The crawl moves left-to-right slowly so cards read
 * as a moving proof line, not a stacked testimonial grid. Pauses on hover/focus. */
.lt-reviews-block__quotes {
    /* Break out of the narrow badge column so the crawl spans the full stage. */
    overflow: hidden;
    padding: 0;
    width: 100vw;
    position: relative;
    left: 50%;
    right: 50%;
    margin-left: -50vw;
    margin-right: -50vw;
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
    width: max-content;
    animation: lt-reviews-scroll var(--lt-reviews-crawl-duration, 540s) linear infinite;
}
.lt-reviews-block__group {
    display: flex;
    align-items: stretch;
    flex: 0 0 auto;
    gap: 0.75rem;
    padding-right: 0.75rem;
}
.lt-reviews-block__quotes:hover .lt-reviews-block__track,
.lt-reviews-block__track:focus-within {
    animation-play-state: paused;
}
@keyframes lt-reviews-scroll {
    from { transform: translateX(-50%); }
    to   { transform: translateX(0); }
}
@media (max-width: 575.98px) {
    .lt-reviews-block__group {
        gap: 0.55rem;
        padding-right: 0.55rem;
    }
    .lt-reviews-block__quote {
        padding: 0.85rem;
    }
}
.lt-reviews-block__quote {
    flex: 0 0 300px;
    background-color: var(--lt-white);
    border-radius: 0.5rem;
    padding: 1.05rem 1.1rem 1rem;
    text-align: left;
    border: 1px solid rgba(184, 154, 91, 0.22);
    box-shadow: 0 10px 28px rgba(10, 10, 11, 0.06);
    display: flex;
    flex-direction: column;
}
.lt-reviews-block__quote-mark {
    font-family: var(--lt-font-heading);
    font-size: 1.85rem;
    color: var(--lt-brass);
    line-height: 1;
    margin: 0 0 0.35rem;
    opacity: 0.6;
}
.lt-reviews-block__quote-text {
    display: -webkit-box;
    font-family: var(--lt-font-body);
    font-size: 0.95rem;
    color: var(--lt-near-black);
    line-height: 1.45;
    margin: 0 0 0.55rem;
    min-height: 0;
    overflow: hidden;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 5;
}
.lt-reviews-block__quote-attr {
    font-family: var(--lt-font-body);
    font-size: 0.8125rem;
    color: var(--lt-soft-gray);
    margin: 0 0 0.45rem;
}
.lt-reviews-block__quote-stars {
    color: var(--lt-brass);
    font-size: 1rem;
    letter-spacing: 0.12em;
    line-height: 1;
    margin-top: auto;        /* push to bottom of flex-column card */
    padding-top: 0.35rem;
    text-align: center;
}
@media (max-width: 575.98px) {
    .lt-reviews-block {
        padding: 1.25rem 0.75rem 1.35rem;
    }
    .lt-reviews-block__badge {
        gap: 0.25rem;
        margin-bottom: 0.85rem;
    }
    .lt-reviews-block__stars {
        font-size: 1.2rem;
    }
    .lt-reviews-block__score {
        font-size: 1.45rem;
        line-height: 1.05;
    }
    .lt-reviews-block__count {
        font-size: 0.82rem;
        line-height: 1.25;
    }
    .lt-reviews-block__quotes {
        mask-image: linear-gradient(
            to right, transparent 0, #000 8%, #000 92%, transparent 100%
        );
        -webkit-mask-image: linear-gradient(
            to right, transparent 0, #000 8%, #000 92%, transparent 100%
        );
        padding: 0;
    }
    .lt-reviews-block__quote {
        flex-basis: min(248px, calc(100vw - 2.5rem));
        padding: 0.78rem 0.85rem 0.75rem;
    }
    .lt-reviews-block__quote-mark {
        font-size: 1.55rem;
        margin-bottom: 0.35rem;
    }
    .lt-reviews-block__quote-text {
        font-size: 0.86rem;
        line-height: 1.45;
        margin-bottom: 0.45rem;
        -webkit-line-clamp: 4;
    }
    .lt-reviews-block__quote-attr {
        font-size: 0.76rem;
        line-height: 1.25;
        margin-bottom: 0.4rem;
    }
    .lt-reviews-block__quote-stars {
        font-size: 0.82rem;
        padding-top: 0.45rem;
    }
}

/* --- Custom Event Decor categories ---------------------------------- */
.lt-categories {
    background-color: var(--lt-white);
    padding: 4rem 1.5rem;
}
.lt-categories__heading {
    font-family: var(--lt-font-heading);
    font-size: 2.25rem;
    text-align: center;
    color: var(--lt-near-black);
    margin: 0 0 0.5rem;
}
.lt-categories__heading-link {
    color: inherit;
    text-decoration: none;
    border-bottom: 2px solid transparent;
    padding-bottom: 0.15rem;
    transition: border-color 0.2s ease, color 0.2s ease;
}
.lt-categories__heading-link:hover,
.lt-categories__heading-link:focus-visible {
    color: var(--lt-berry);
    border-bottom-color: var(--lt-brass);
    text-decoration: none;
}
.lt-categories__lede {
    text-align: center;
    color: var(--lt-soft-gray);
    max-width: 540px;
    margin: 0 auto 2.75rem;
    font-size: 1rem;
}
/* 8-category grid (per GL 2026-04-28 — Centerpieces + Custom Sculptures
 * added; Garlands replaces "Organic Garlands"; Pillars retired):
 *   <768px : 2 columns × 4 rows  (clean 2-2-2-2 mobile)
 *   768-1399px : 4 columns × 2 rows (4-4 tablet, even rows, no orphans)
 *   ≥1400px : 4 columns × 2 rows (kept at 4-wide for legibility — 8 in a
 *                                  single ribbon would compress circles
 *                                  and labels at typical desktop widths) */
.lt-categories__grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 2rem 1.5rem;
    max-width: 1500px;
    margin: 0 auto;
}
@media (min-width: 768px) {
    .lt-categories__grid {
        grid-template-columns: repeat(4, 1fr);
        gap: 2.5rem 2rem;
    }
}
@media (min-width: 1200px) {
    .lt-categories__grid {
        grid-template-columns: repeat(4, 1fr);
        gap: 3rem 2.5rem;
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
    background-color: var(--lt-near-white);
    border: 1px solid rgba(184, 154, 91, 0.35);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: transform 0.2s ease, background-color 0.2s ease;
}
.lt-categories__link:hover .lt-categories__circle,
.lt-categories__link:focus-visible .lt-categories__circle {
    background-color: var(--lt-stone);
    transform: translateY(-3px);
}
.lt-categories__icon-svg {
    width: 56px;
    height: 56px;
    color: var(--lt-brass);
}
.lt-categories__name {
    font-family: var(--lt-font-body);
    font-size: 1rem;
    font-weight: 600;
    line-height: 1.3;
    max-width: 9rem;
}

/* --- Featured Work (One of a Kind Designs) - full-width proof band --- */
.lt-featured {
    background-color: var(--lt-near-white);
    padding: 3.25rem 1.25rem 3.75rem;
}
.lt-featured__inner {
    max-width: 1700px;
    margin: 0 auto;
}
.lt-featured__heading {
    font-family: var(--lt-font-heading);
    font-size: 2.25rem;
    text-align: center;
    color: var(--lt-near-black);
    margin: 0 0 0.5rem;
}
@media (min-width: 1200px) {
    .lt-featured__heading { font-size: 2.75rem; }
}
.lt-featured__lede {
    text-align: center;
    color: var(--lt-soft-gray);
    max-width: 680px;
    margin: 0 auto 2.25rem;
    font-size: 1rem;
}
.lt-featured__grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.5rem;
}
@media (min-width: 768px) {
    .lt-featured__grid { grid-template-columns: repeat(3, 1fr); gap: 1rem; }
}
@media (min-width: 1200px) {
    .lt-featured__grid { gap: 1.25rem; }
}
.lt-featured__card {
    background-color: var(--lt-white);
    border-radius: 0.5rem;
    overflow: hidden;
    text-decoration: none;
    color: inherit;
    border: 1px solid rgba(184, 154, 91, 0.22);
    box-shadow: 0 10px 30px rgba(10, 10, 11, 0.07);
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
    aspect-ratio: 4 / 3;
    background-color: var(--lt-warm-tint);
    background-size: cover;
    background-position: center;
}
.lt-featured__body {
    padding: 1.25rem 1.5rem 1.5rem;
}
.lt-featured__category {
    font-family: var(--lt-font-body);
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--lt-berry);
    margin: 0 0 0.5rem;
}
.lt-featured__title {
    font-family: var(--lt-font-heading);
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
    font-family: var(--lt-font-body);
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
    background-color: var(--lt-stone);
    padding: 2.75rem 0 3.25rem;
    overflow: hidden;
}
.lt-crawl__heading {
    font-family: var(--lt-font-heading);
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
    width: 100vw;
    position: relative;
    left: 50%;
    right: 50%;
    margin-left: -50vw;
    margin-right: -50vw;
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
    animation: lt-crawl-scroll var(--lt-crawl-duration, var(--lt-reviews-crawl-duration, 540s)) linear infinite;
}
.lt-crawl__item {
    flex: 0 0 auto;
    padding: 0 2rem;
    font-family: var(--lt-font-body);
    font-size: 1rem;
    font-weight: 500;
    color: var(--lt-near-black);
    white-space: nowrap;
    opacity: 0.7;
}
@keyframes lt-crawl-scroll {
    from { transform: translateX(-50%); }
    to   { transform: translateX(0); }
}
@media (prefers-reduced-motion: reduce) {
    .lt-reviews-block__quotes,
    .lt-crawl__viewport {
        overflow-x: hidden;
    }
    .lt-reviews-block__track {
        animation-name: lt-reviews-scroll !important;
        animation-duration: var(--lt-reviews-crawl-duration, 540s) !important;
        animation-timing-function: linear !important;
        animation-iteration-count: infinite !important;
    }
    .lt-crawl__track {
        animation-name: lt-crawl-scroll !important;
        animation-duration: var(--lt-crawl-duration, var(--lt-reviews-crawl-duration, 540s)) !important;
        animation-timing-function: linear !important;
        animation-iteration-count: infinite !important;
    }
}
/* --- Closing CTA ---------------------------------------------------- */
.lt-cta {
    background-color: var(--lt-navy);
    padding: 4rem 1rem 4.5rem;
    text-align: center;
}
.lt-cta__inner {
    max-width: 1200px;
    margin: 0 auto;
}
.lt-cta__heading {
    font-family: var(--lt-font-heading);
    font-size: 2.5rem;
    color: var(--lt-near-white);
    margin: 0 0 1rem;
    line-height: 1.15;
    text-align: center;
}
.lt-cta__body {
    font-family: var(--lt-font-body);
    font-size: 1.125rem;
    color: rgba(250, 247, 242, 0.82);
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
    background-color: var(--lt-berry);
    color: var(--lt-white);
    text-decoration: none;
    border-radius: 0.375rem;
    font-family: var(--lt-font-body);
    font-weight: 600;
    font-size: 1rem;
    min-height: 48px;
}
.lt-cta__button:hover,
.lt-cta__button:focus-visible {
    background-color: var(--lt-ink);
    color: var(--lt-white);
    outline: 2px solid var(--lt-brass);
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
    background-color: var(--lt-stone-tint);
    background-image: url('/assets/locally_twisted/images/home/twisting.jpg');
    background-size: cover;
    background-position: center;
    border-radius: 0.5rem;
}
.lt-twisting-spotlight__eyebrow {
    font-family: var(--lt-font-body);
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--lt-soft-gray);
    margin: 0 0 0.5rem;
}
.lt-twisting-spotlight__heading {
    font-family: var(--lt-font-heading);
    font-size: 1.875rem;
    color: var(--lt-near-black);
    margin: 0 0 1rem;
    line-height: 1.2;
}
.lt-twisting-spotlight__body p {
    font-family: var(--lt-font-body);
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
    font-family: var(--lt-font-body);
    font-weight: 600;
    margin-top: 0.5rem;
}
.lt-twisting-spotlight__cta:hover,
.lt-twisting-spotlight__cta:focus-visible {
    background-color: var(--lt-navy);
    color: var(--lt-white);
}
"""


def _abbreviate_name(name):
    """Privacy-friendly review attribution for homepage testimonials.

    "Mary DeMann"            -> "Mary D."
    "Sarah Johnston-Powell"  -> "Sarah J."
    "Mary Anne DeMann"       -> "Mary D."     (middle name dropped)
    "Lindsay"                -> "Lindsay"     (single name unchanged)
    "KJSCOTT"                -> "KJSCOTT"     (single name unchanged)
    """
    parts = (name or "").strip().split()
    if len(parts) <= 1:
        return parts[0] if parts else ""
    first = parts[0]
    last = parts[-1]
    initial = last[0].upper() if last else ""
    return f"{first} {initial}."


def get_context(context):
    context.title = "Locally Twisted - Utah Balloon Event Decor & Installations"
    context.metatags = {
        "description": (
            "Professional balloon decor and event installations for corporate, "
            "school, civic, community, and private events across the Wasatch Front."
        ),
        "og:title": "Locally Twisted - Utah Balloon Event Decor",
        "og:description": "Custom balloon decor and event installations across the Wasatch Front since 1998.",
        "og:type": "website",
    }
    context.client_crawl = CLIENT_CRAWL
    context.custom_categories = CUSTOM_CATEGORIES
    context.show_custom_event_decor = False
    context.featured_work = FEATURED_WORK
    context.home_hero_slides = HOME_HERO_SLIDES
    context.structured_data = [business_graph("/")]
    # Compute display_name at request time so the source list keeps full
    # names (audit trail) but the rendered cards show "First L." only.
    context.review_quotes = [
        dict(q, display_name=_abbreviate_name(q.get("name", ""))) if q else None
        for q in REVIEW_QUOTES
    ]
    context.colocated_css = PAGE_CSS
    return context
