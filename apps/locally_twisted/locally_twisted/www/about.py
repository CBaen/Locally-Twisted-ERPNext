"""Source-owned About page for Locally Twisted."""

from locally_twisted.seo import business_graph


no_cache = 1
sitemap = 1


META_TITLE = "About Locally Twisted | Utah Balloon Decor Since 1998"
META_DESCRIPTION = (
    "About Locally Twisted, a Utah balloon decor company creating custom "
    "installations, balloon twisting, face painting, and Wasatch Front event support."
)


PAGE_CSS = """
.lt-about__hero {
    align-items: center;
    border-bottom: 4px solid #b31b34;
    display: flex;
    height: var(--lt-hero-standard-height);
    max-height: var(--lt-hero-standard-height);
    min-height: var(--lt-hero-standard-height);
    overflow: hidden;
    padding: 0 1rem;
}
.lt-about__hero-inner {
    margin: 0 auto;
    padding-block: var(--lt-hero-padding-y);
    width: min(1160px, calc(100% - 2rem));
}
.lt-about__eyebrow {
    color: var(--lt-brass, #d9c7b3);
    font-family: 'Lato', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 0.78rem;
    font-weight: 900;
    letter-spacing: 0.14em;
    line-height: 1.35;
    margin: 0 0 0.45rem;
    text-transform: uppercase;
}
.lt-about__hero h1 {
    color: #fff;
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: var(--lt-hero-title-max);
    font-weight: 700;
    letter-spacing: 0;
    line-height: 1.02;
    margin: 0 0 0.55rem;
    max-width: 26ch;
}
.lt-about__hero-lede {
    color: rgba(255, 255, 255, 0.92);
    font-size: clamp(0.9rem, 1.6vw, 1rem);
    line-height: 1.35;
    margin: 0;
    max-width: 780px;
}
.lt-about {
    background: #faf7f2;
    color: #0a0a0b;
    padding: clamp(2.75rem, 7vw, 5rem) 1rem;
}
.lt-about__inner {
    box-sizing: border-box;
    margin: 0 auto;
    max-width: 100%;
    width: min(1160px, 100%);
}
.lt-about__intro {
    display: grid;
    gap: clamp(1.4rem, 3vw, 2rem);
}
@media (min-width: 900px) {
    .lt-about__intro {
        grid-template-columns: minmax(0, 1.05fr) minmax(280px, 0.55fr);
    }
}
.lt-about__copy {
    background: #fffdf9;
    border: 1px solid rgba(14, 34, 64, 0.16);
    border-top: 8px solid #b31b34;
    border-radius: 0.375rem;
    box-shadow: 0 18px 50px rgba(14, 34, 64, 0.08);
    padding: clamp(1.35rem, 3.5vw, 2.2rem);
}
.lt-about__copy h2,
.lt-about__card h2,
.lt-about__cta h2 {
    color: #0e2240;
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-weight: 700;
    letter-spacing: 0;
    line-height: 1.08;
    margin: 0;
}
.lt-about__copy h2 {
    font-size: clamp(1.9rem, 4vw, 3rem);
    max-width: 14ch;
}
.lt-about__copy p,
.lt-about__card p,
.lt-about__cta p {
    color: rgba(10, 10, 11, 0.72);
    font-family: 'Lato', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 1rem;
    line-height: 1.64;
}
.lt-about__copy p {
    margin: 1rem 0 0;
}
.lt-about__proof {
    display: grid;
    gap: 0.75rem;
}
.lt-about__proof-item {
    background: #0e2240;
    border: 1px solid rgba(184, 154, 91, 0.35);
    border-radius: 0.375rem;
    color: #faf7f2;
    padding: 1.15rem;
}
.lt-about__proof-item strong {
    color: #d9c7b3;
    display: block;
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 1.5rem;
    line-height: 1.05;
}
.lt-about__proof-item span {
    display: block;
    font-size: 0.95rem;
    line-height: 1.45;
    margin-top: 0.4rem;
}
.lt-about__grid {
    display: grid;
    gap: clamp(1rem, 2.5vw, 1.4rem);
    grid-template-columns: minmax(0, 1fr);
    margin-top: clamp(1.4rem, 4vw, 2rem);
}
@media (min-width: 760px) {
    .lt-about__grid {
        grid-template-columns: repeat(3, minmax(0, 1fr));
    }
}
.lt-about__card {
    background: #fffdf9;
    border: 1px solid rgba(14, 34, 64, 0.14);
    border-radius: 0.375rem;
    box-shadow: 0 16px 36px rgba(10, 10, 11, 0.06);
    min-width: 0;
    padding: clamp(1.15rem, 3vw, 1.5rem);
}
.lt-about__card h2 {
    font-size: clamp(1.45rem, 3vw, 2rem);
}
.lt-about__card p {
    margin: 0.75rem 0 0;
}
.lt-about__cta {
    background: linear-gradient(135deg, rgba(14, 34, 64, 0.96), rgba(10, 10, 11, 0.96));
    border-top: 1px solid rgba(184, 154, 91, 0.48);
    padding: clamp(2.75rem, 7vw, 4.5rem) 1rem;
}
.lt-about__cta-inner {
    box-sizing: border-box;
    margin: 0 auto;
    max-width: 100%;
    text-align: center;
    width: min(860px, 100%);
}
.lt-about__cta h2 {
    color: #faf7f2;
    font-size: clamp(2rem, 5vw, 3.35rem);
}
.lt-about__cta p {
    color: rgba(250, 247, 242, 0.86);
    margin: 0.85rem auto 0;
    max-width: 640px;
}
.lt-about__button {
    align-items: center;
    background: #b31b34;
    border: 1px solid #b31b34;
    border-radius: 0.25rem;
    color: #fff;
    display: inline-flex;
    font-weight: 900;
    justify-content: center;
    margin-top: 1.3rem;
    min-height: 44px;
    padding: 0.75rem 1.25rem;
    text-decoration: none;
}
.lt-about__button:hover,
.lt-about__button:focus-visible {
    background: #faf7f2;
    border-color: #faf7f2;
    color: #0e2240;
    outline: 3px solid rgba(184, 154, 91, 0.42);
    outline-offset: 2px;
}
"""


def get_context(context):
    context.title = META_TITLE
    context.metatags = {
        "title": META_TITLE,
        "description": META_DESCRIPTION,
        "og:title": META_TITLE,
        "og:description": META_DESCRIPTION,
        "og:type": "website",
    }
    context.structured_data = [business_graph("/about")]
    context.colocated_css = PAGE_CSS
    return context
