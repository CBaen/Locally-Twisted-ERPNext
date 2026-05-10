"""Balloon Twisting & Face Painting service page.

Frappe maps this file to the route /balloon-twisting-and-face-painting.
The customer inquiry path is the canonical /contact form. This page
explains the service and reuses the shared inquiry form with only the
live-service choices exposed.
"""

from locally_twisted.seo import service_schema
from locally_twisted.www.book import (
    MAX_PHOTO_BYTES,
    MAX_PHOTOS,
    OCCASION_OPTIONS,
    PACKAGE_ITEM_OPTIONS,
    SERVICE_OPTIONS,
)

no_cache = 1
sitemap = 1

BTFP_SERVICE_VALUES = {"Balloon Twisting", "Face Painting"}
BTFP_EVENT_TYPES = [
    "Birthday Parties",
    "School Carnivals",
    "School Field Days",
    "PTA Nights",
    "Library Programs",
    "Summer Camps",
    "Company Picnics",
    "Corporate Family Days",
    "Customer Appreciation Events",
    "Grand Openings",
    "Community Fairs",
    "City Celebrations",
    "Festivals",
    "Church Events",
    "Fundraisers",
    "Family Reunions",
    "Holiday Parties",
    "Trunk-or-Treats",
    "Block Parties",
    "Sports Team Parties",
]


PAGE_CSS = """.lt-btfp__intro {
    background-color: var(--lt-warm-tint);
    min-height: var(--lt-hero-standard-height);
    height: var(--lt-hero-standard-height);
    max-height: var(--lt-hero-standard-height);
    padding: 0 1.5rem;
    text-align: left;
    display: flex;
    align-items: center;
    overflow: hidden;
}
.lt-btfp__intro-inner {
    max-width: 1100px;
    margin: 0 auto;
    text-align: left;
    width: 100%;
    padding-block: var(--lt-hero-padding-y);
}
.lt-btfp__intro-title {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: var(--lt-hero-title-max);
    color: var(--lt-near-black);
    margin: 0 0 0.4rem;
    line-height: 1;
    text-align: left;
    max-width: 34rem;
}
.lt-btfp__intro-lede {
    font-size: 0.92rem;
    color: var(--lt-soft-gray);
    margin: 0;
    font-weight: 300;
    text-align: left;
    max-width: 46rem;
    line-height: 1.28;
}
@media (min-width: 992px) {
    .lt-btfp__intro {
        padding-inline: 2rem;
    }
}
@media (max-width: 575.98px) {
    .lt-btfp__intro-lede {
        display: none;
    }
}

.lt-btfp__services {
    padding: 2.5rem 1rem;
}
.lt-btfp__services-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.5rem;
    max-width: 1100px;
    margin: 0 auto;
}
@media (min-width: 768px) {
    .lt-btfp__services-grid {
        grid-template-columns: 1fr 1fr;
    }
}
.lt-btfp__service-card {
    background-color: var(--lt-white);
    border: 1px solid rgba(26, 26, 26, 0.08);
    border-radius: 0.5rem;
    padding: 1.75rem;
}
.lt-btfp__service-card h2 {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 1.5rem;
    margin: 0 0 0.85rem;
    color: var(--lt-near-black);
}
.lt-btfp__service-card ul {
    list-style: disc;
    padding-left: 1.25rem;
    margin: 0;
    color: var(--lt-soft-gray);
    line-height: 1.55;
}
.lt-btfp__service-card li {
    margin-bottom: 0.4rem;
}
.lt-btfp__carousel {
    width: 100%;
    /* Portrait 3:4 — matches the dominant source-photo orientation
       (10 of 12 photos are portrait/square iPhone shots). Avoids the
       aggressive cover-crop that made portraits feel "too close-up".
       No max-width cap — let carousels fill their column for presence. */
    aspect-ratio: 3 / 4;
    border-radius: 0.375rem;
    margin-bottom: 1rem;
    background-color: var(--lt-warm-tint);
    position: relative;
    overflow: hidden;
}
.lt-btfp__carousel-img {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    opacity: 0;
    transition: opacity 420ms ease;
}
.lt-btfp__carousel-img:first-child,
.lt-btfp__carousel-img.is-active {
    opacity: 1;
}
.lt-btfp__carousel[data-enhanced="true"] .lt-btfp__carousel-img:first-child:not(.is-active) {
    opacity: 0;
}
.lt-btfp__carousel-control {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    z-index: 2;
    width: 2.35rem;
    height: 2.35rem;
    border-radius: 999px;
    border: 1px solid rgba(255, 255, 255, 0.78);
    background: rgba(10, 10, 11, 0.48);
    color: #fff;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    line-height: 1;
    cursor: pointer;
}
.lt-btfp__carousel-control:hover,
.lt-btfp__carousel-control:focus-visible {
    background: rgba(10, 10, 11, 0.72);
    outline: 3px solid rgba(184, 154, 91, 0.45);
    outline-offset: 2px;
}
.lt-btfp__carousel-control--prev { left: 0.65rem; }
.lt-btfp__carousel-control--next { right: 0.65rem; }
.lt-btfp__carousel-status {
    position: absolute;
    left: 50%;
    bottom: 0.7rem;
    transform: translateX(-50%);
    z-index: 2;
    padding: 0.22rem 0.62rem;
    border-radius: 999px;
    background: rgba(10, 10, 11, 0.58);
    color: #fff;
    font-size: 0.78rem;
    font-weight: 800;
    letter-spacing: 0.03em;
}
@media (prefers-reduced-motion: reduce) {
    .lt-btfp__carousel-img { transition: none; }
}

.lt-btfp__kicker {
    font-family: 'Lato', sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.15em;
    color: var(--lt-soft-gray);
    text-transform: uppercase;
    margin: 0 0 1rem;
    text-align: left;
}
.lt-btfp__service-kicker {
    margin-top: 1.25rem;
    margin-bottom: 0.5rem;
}
.lt-btfp__service-title {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 1.5rem;
    color: #0e2240;
    margin: 0 0 1rem;
    line-height: 1.2;
    letter-spacing: 0;
}
.lt-btfp__service-body {
    color: rgba(10, 10, 11, 0.72);
    line-height: 1.6;
    margin: 0 0 1.5rem;
    font-size: 0.95rem;
}
.lt-btfp__service-spec {
    margin: 0;
    padding-top: 0.5rem;
    border-top: 1px solid rgba(14, 34, 64, 0.14);
}
.lt-btfp__service-spec-row {
    display: grid;
    grid-template-columns: 100px 1fr;
    gap: 1rem;
    padding: 0.65rem 0;
    border-bottom: 1px solid rgba(14, 34, 64, 0.14);
}
.lt-btfp__service-spec-row:last-child {
    border-bottom: none;
}
.lt-btfp__service-spec-row dt {
    font-family: 'Lato', sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    color: #0a0a0b;
    text-transform: uppercase;
    margin: 0;
    align-self: center;
}
.lt-btfp__service-spec-row dd {
    font-size: 0.95rem;
    color: rgba(10, 10, 11, 0.72);
    margin: 0;
    line-height: 1.5;
    align-self: center;
}
.lt-btfp__intro {
    background: linear-gradient(135deg, #0e2240 0%, #0a0a0b 100%);
    border-bottom: 0;
}
.lt-btfp__intro-title,
.lt-btfp__intro-lede,
.lt-btfp__intro .lt-btfp__kicker {
    color: #faf7f2;
}
.lt-btfp__intro .lt-btfp__kicker,
.lt-btfp__service-kicker,
.lt-btfp__booking .lt-btfp__kicker {
    color: #b31b34;
    font-weight: 800;
    letter-spacing: 0.16em;
}
.lt-btfp__services {
    background-color: #faf7f2;
}
.lt-btfp__service-card {
    background-color: #fffdf9;
    border: 1px solid rgba(14, 34, 64, 0.16);
    box-shadow: 0 18px 50px rgba(14, 34, 64, 0.08);
}
.lt-btfp__service-card h2 {
    color: #0e2240;
}
.lt-btfp__intro-title {
    letter-spacing: 0;
}
.lt-btfp__intro .lt-btfp__intro-lede {
    color: #faf7f2;
}
.lt-btfp__carousel {
    background-color: #d9c7b3;
}
/* Event suggestion crawl + shared intake form. Keep this section page-local so
   the general /contact form stays broad. */
.lt-btfp__event-crawl {
    background-color: #0e2240;
    color: #faf7f2;
    padding: 0.8rem 0;
    overflow: hidden;
    border: 0;
}
.lt-btfp__event-crawl-viewport {
    overflow-x: hidden;
    width: 100vw;
    position: relative;
    left: 50%;
    right: 50%;
    margin-left: -50vw;
    margin-right: -50vw;
}
.lt-btfp__event-crawl-track {
    display: flex;
    width: max-content;
    transform: translateX(-50%);
    animation: lt-btfp-event-crawl-scroll 80s linear infinite;
    animation-play-state: running;
    will-change: transform;
}
.lt-btfp__event-crawl-track:hover,
.lt-btfp__event-crawl-track:focus {
    animation-play-state: running;
}
.lt-btfp__event-crawl-group {
    display: flex;
    align-items: center;
    gap: clamp(1.5rem, 4vw, 3rem);
    flex: 0 0 auto;
    padding-right: clamp(1.5rem, 4vw, 3rem);
}
.lt-btfp__event-crawl-item {
    color: #faf7f2;
    font-family: 'Lato', sans-serif;
    font-size: clamp(0.9rem, 1.5vw, 1.08rem);
    font-weight: 800;
    letter-spacing: 0.08em;
    line-height: 1.2;
    text-transform: uppercase;
    white-space: nowrap;
}
@keyframes lt-btfp-event-crawl-scroll {
    from { transform: translateX(-50%); }
    to { transform: translateX(0); }
}
@media (prefers-reduced-motion: reduce) {
    .lt-btfp__event-crawl-track {
        animation-name: lt-btfp-event-crawl-scroll !important;
        animation-duration: 160s !important;
    }
}

.lt-btfp__booking {
    background-color: #faf7f2;
    padding: 3rem 1rem 3.5rem;
}
.lt-btfp__booking-grid {
    display: grid;
    grid-template-columns: minmax(0, 1fr);
    gap: 2rem;
    max-width: 1140px;
    margin: 0 auto;
}
@media (min-width: 992px) {
    .lt-btfp__booking-grid {
        grid-template-columns: minmax(0, 1.6fr) minmax(280px, 0.85fr);
        gap: 2.5rem;
        align-items: start;
    }
}
.lt-btfp__form-wrap {
    min-width: 0;
}
.lt-btfp__form-wrap > h2 {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: clamp(2rem, 4vw, 2.55rem);
    color: #0a0a0b;
    margin: 0 0 0.35rem;
    line-height: 1.05;
}
.lt-btfp__form-subtitle {
    color: rgba(10, 10, 11, 0.72);
    font-size: 1rem;
    line-height: 1.5;
    margin: 0 0 1.25rem;
}
.lt-btfp__form-wrap .lt-book {
    padding: 0;
}
.lt-btfp__form-wrap .lt-book__form-wrap {
    max-width: none;
}
.lt-btfp__form-wrap .lt-book__services {
    margin: 1.25rem 0;
}
.lt-btfp__side {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    min-width: 0;
}
.lt-btfp__calculator {
    background-color: #0e2240;
    border: 1px solid rgba(184, 154, 91, 0.34);
    border-radius: 0.375rem;
    box-shadow: 0 18px 42px rgba(10, 10, 11, 0.12);
    color: #faf7f2;
    padding: clamp(1.25rem, 3vw, 1.75rem);
}
.lt-btfp__calculator-kicker {
    color: #b89a5b;
    font-family: 'Lato', sans-serif;
    font-size: 0.74rem;
    font-weight: 900;
    letter-spacing: 0.14em;
    line-height: 1.2;
    margin: 0 0 0.55rem;
    text-transform: uppercase;
}
.lt-btfp__calculator h3 {
    color: #faf7f2;
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 1.55rem;
    font-weight: 700;
    line-height: 1.1;
    margin: 0 0 1rem;
}
.lt-btfp__calc-roster {
    display: grid;
    gap: 0.75rem;
    margin: 0 0 1rem;
}
.lt-btfp__calc-row {
    background-color: rgba(250, 247, 242, 0.08);
    border: 1px solid rgba(250, 247, 242, 0.18);
    border-radius: 0.25rem;
    display: grid;
    gap: 0.75rem;
    padding: 0.85rem;
}
.lt-btfp__calc-row-head {
    align-items: center;
    display: flex;
    gap: 0.75rem;
    justify-content: space-between;
}
.lt-btfp__calc-row-head strong {
    color: #faf7f2;
    font-family: 'Lato', sans-serif;
    font-size: 0.86rem;
    font-weight: 900;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.lt-btfp__calc-row-fields {
    display: grid;
    gap: 0.65rem;
    grid-template-columns: minmax(0, 1.2fr) minmax(0, 0.8fr);
}
@media (max-width: 479.98px) {
    .lt-btfp__calc-row-fields {
        grid-template-columns: minmax(0, 1fr);
    }
}
.lt-btfp__calc-control-label {
    color: rgba(250, 247, 242, 0.84);
    display: grid;
    gap: 0.38rem;
    font-family: 'Lato', sans-serif;
    font-size: 0.78rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    margin: 0;
    text-transform: uppercase;
}
.lt-btfp__calc-input {
    background-color: #fffdfa;
    border: 1px solid rgba(184, 154, 91, 0.58);
    border-radius: 0.25rem;
    color: #0a0a0b;
    font-family: 'Lato', sans-serif;
    font-size: 1rem;
    min-height: 44px;
    padding: 0.65rem 0.75rem;
    width: 100%;
}
.lt-btfp__calc-input:focus {
    border-color: #b89a5b;
    outline: 3px solid rgba(184, 154, 91, 0.32);
    outline-offset: 1px;
}
.lt-btfp__calc-remove,
.lt-btfp__calc-add {
    align-items: center;
    border-radius: 0.25rem;
    cursor: pointer;
    display: inline-flex;
    font-family: 'Lato', sans-serif;
    font-size: 0.82rem;
    font-weight: 800;
    justify-content: center;
    line-height: 1;
    min-height: 40px;
    padding: 0.65rem 0.8rem;
}
.lt-btfp__calc-remove {
    background-color: transparent;
    border: 1px solid rgba(250, 247, 242, 0.28);
    color: #faf7f2;
}
.lt-btfp__calc-add {
    background-color: rgba(184, 154, 91, 0.2);
    border: 1px solid #b89a5b;
    color: #faf7f2;
    width: 100%;
}
.lt-btfp__calc-remove:hover,
.lt-btfp__calc-remove:focus-visible,
.lt-btfp__calc-add:hover,
.lt-btfp__calc-add:focus-visible {
    border-color: #faf7f2;
    outline: 3px solid rgba(184, 154, 91, 0.32);
    outline-offset: 2px;
}
.lt-btfp__calc-help,
.lt-btfp__calc-formula {
    color: rgba(250, 247, 242, 0.76);
    font-size: 0.86rem;
    line-height: 1.45;
    margin: 0.5rem 0 0;
}
.lt-btfp__calc-results {
    border-top: 1px solid rgba(184, 154, 91, 0.28);
    margin: 1rem 0 0;
    padding: 0.85rem 0 0;
}
.lt-btfp__calc-results > div {
    align-items: baseline;
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    padding: 0.42rem 0;
}
.lt-btfp__calc-results dt {
    color: rgba(250, 247, 242, 0.78);
    font-size: 0.88rem;
    margin: 0;
}
.lt-btfp__calc-results dd {
    color: #faf7f2;
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 1.2rem;
    font-weight: 700;
    margin: 0;
    text-align: right;
    white-space: nowrap;
}
.lt-btfp__calc-total-row {
    border-bottom: 1px solid rgba(184, 154, 91, 0.24);
    margin-bottom: 0.2rem;
    padding-bottom: 0.65rem !important;
}
.lt-btfp__calc-total-row dd {
    color: #b89a5b;
    font-size: 1.85rem;
}
.lt-btfp__expect-card {
    background-color: #fffdfa;
    border: 1px solid rgba(14, 34, 64, 0.16);
    border-radius: 0.375rem;
    box-shadow: 0 18px 42px rgba(10, 10, 11, 0.07);
    padding: clamp(1.25rem, 3vw, 1.75rem);
}
.lt-btfp__expect-card h3,
.lt-btfp__expect-card h4 {
    color: #0a0a0b;
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-weight: 700;
    line-height: 1.1;
}
.lt-btfp__expect-card h3 {
    font-size: 1.55rem;
    margin: 0 0 1rem;
}
.lt-btfp__expect-card h4 {
    font-size: 1.18rem;
    margin: 0 0 0.65rem;
}
.lt-btfp__expect-card p {
    color: rgba(10, 10, 11, 0.72);
    font-size: 0.95rem;
    line-height: 1.55;
    margin: 0;
}
.lt-btfp__expect-list,
.lt-btfp__expect-contact {
    list-style: none;
    margin: 0;
    padding: 0;
}
.lt-btfp__expect-list li,
.lt-btfp__expect-contact li {
    display: flex;
    align-items: flex-start;
    gap: 0.6rem;
    margin-bottom: 0.6rem;
    color: rgba(10, 10, 11, 0.72);
    font-size: 0.95rem;
    line-height: 1.45;
}
.lt-btfp__expect-list li:last-child,
.lt-btfp__expect-contact li:last-child {
    margin-bottom: 0;
}
.lt-btfp__expect-icon {
    color: #b31b34;
    flex: 0 0 1.25rem;
    font-weight: 800;
    text-align: center;
}
.lt-btfp__expect-divider {
    border: none;
    border-top: 1px solid rgba(14, 34, 64, 0.14);
    margin: 1.2rem 0;
}
.lt-btfp__expect-contact a {
    color: #0e2240;
    font-weight: 700;
    text-decoration: none;
}
.lt-btfp__expect-contact a:hover,
.lt-btfp__expect-contact a:focus-visible {
    text-decoration: underline;
    text-underline-offset: 0.2em;
}
"""


def get_context(context):
    context.title = "Balloon Twisting & Face Painting — Locally Twisted | Utah"
    context.metatags = {
        "description": (
            "Professional balloon twisting and face painting for birthday parties, "
            "school events, corporate family days, and festivals. "
            "Serving Weber, Davis, Salt Lake, and Utah counties."
        ),
        "og:title": "Balloon Twisting & Face Painting — Locally Twisted",
        "og:description": "Live entertainment that keeps every guest smiling.",
        "og:type": "website",
    }
    context.structured_data = [
        service_schema(
            "Balloon twisting and face painting",
            context.metatags["description"],
            "/balloon-twisting-and-face-painting",
            service_type="Live event entertainment",
        )
    ]
    context.colocated_css = PAGE_CSS
    context.occasion_options = OCCASION_OPTIONS
    context.selected_occasion = ""
    context.service_options = [
        option for option in SERVICE_OPTIONS
        if option[1] in BTFP_SERVICE_VALUES
    ]
    context.package_item_options = PACKAGE_ITEM_OPTIONS
    context.preselected_services = []
    context.requested_item_code = ""
    context.requested_item_name = ""
    context.max_photos = MAX_PHOTOS
    context.max_photo_mb = MAX_PHOTO_BYTES // (1024 * 1024)
    context.update({"btfp_event_types": BTFP_EVENT_TYPES})
    return context
