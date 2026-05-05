import frappe

no_cache = 1
sitemap = 1


PAGE_CSS = """
.lt-faq {
    padding: 4rem 1.5rem;
}
.lt-faq__inner {
    max-width: 44rem;
    margin: 0 auto;
}
.lt-faq h1 {
    font-size: 2rem;
    margin: 0 0 1.5rem;
    line-height: 1.2;
}
.lt-faq__lede {
    font-size: 1.125rem;
    line-height: 1.6;
    margin: 0 0 2rem;
}
.lt-faq__group {
    margin: 0 0 2rem;
}
.lt-faq__group-title {
    font-size: 1.5rem;
    margin: 0 0 0.75rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    line-height: 1.3;
}
.lt-faq__item {
    border-bottom: 1px solid rgba(0, 0, 0, 0.08);
    margin: 0;
    padding: 0;
}
.lt-faq__item summary {
    list-style: none;
    cursor: pointer;
    padding: 1rem 2.5rem 1rem 0;
    position: relative;
    font-size: 1rem;
    font-weight: 600;
    line-height: 1.4;
    color: inherit;
}
.lt-faq__item summary::-webkit-details-marker {
    display: none;
}
.lt-faq__item summary::after {
    content: "+";
    position: absolute;
    right: 0.25rem;
    top: 50%;
    transform: translateY(-50%);
    font-size: 1.5rem;
    font-weight: 400;
    line-height: 1;
    color: inherit;
    transition: transform 0.2s ease;
}
.lt-faq__item[open] summary::after {
    content: "\\2212";
}
.lt-faq__item summary:hover {
    color: var(--lt-teal, #008080);
}
.lt-faq__item summary:focus-visible {
    outline: 3px solid var(--lt-teal, #008080);
    outline-offset: 2px;
    border-radius: 2px;
}
.lt-faq__answer {
    padding: 0 0 1.25rem;
    font-size: 1rem;
    line-height: 1.6;
}
.lt-faq__answer p {
    font-size: 1rem;
    line-height: 1.6;
    margin: 0 0 0.75rem;
}
.lt-faq__answer p:last-child {
    margin-bottom: 0;
}
.lt-faq__answer ul {
    list-style: none;
    padding: 0;
    margin: 0.5rem 0;
}
.lt-faq__answer li {
    margin: 0 0 0.5rem;
    padding-left: 1.25rem;
    position: relative;
}
.lt-faq__answer li::before {
    content: "\\2022";
    position: absolute;
    left: 0;
    top: 0;
    font-weight: 600;
}
.lt-faq__answer strong {
    font-weight: 600;
}
.lt-faq__contact {
    margin-top: 2.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid rgba(0, 0, 0, 0.08);
}
.lt-faq__link {
    font-weight: 600;
    text-decoration: underline;
    text-underline-offset: 0.2em;
}
.lt-faq__link:hover,
.lt-faq__link:focus {
    text-decoration-thickness: 2px;
}
.lt-faq__link:focus-visible {
    outline: 3px solid currentColor;
    outline-offset: 4px;
}
@media (prefers-reduced-motion: reduce) {
    .lt-faq__item summary::after {
        transition: none;
    }
}
@media (max-width: 480px) {
    .lt-faq {
        padding: 2.5rem 1rem;
    }
    .lt-faq h1 {
        font-size: 1.625rem;
    }
    .lt-faq__group-title {
        font-size: 1.125rem;
    }
}

/* Civic Celebration redesign for secondary editorial pages. */
.lt-faq {
    background-color: #faf7f2;
    color: #0a0a0b;
}
.lt-faq__inner {
    background-color: #fffdf9;
    border: 1px solid rgba(14, 34, 64, 0.16);
    border-top: 8px solid #b31b34;
    border-radius: 0.375rem;
    box-shadow: 0 18px 50px rgba(14, 34, 64, 0.08);
    padding: 2rem;
}
.lt-faq h1 {
    font-family: 'Cormorant Garamond', Georgia, serif;
    color: #0e2240;
    letter-spacing: 0;
}
.lt-faq__lede,
.lt-faq__answer,
.lt-faq__answer p,
.lt-faq__contact {
    color: rgba(10, 10, 11, 0.72);
}
.lt-faq__group-title {
    color: #0e2240;
    border-bottom-color: rgba(14, 34, 64, 0.18);
}
.lt-faq__item {
    border-bottom-color: rgba(14, 34, 64, 0.14);
}
.lt-faq__item summary,
.lt-faq__answer strong,
.lt-faq__link {
    color: #0a0a0b;
}
.lt-faq__item summary::after,
.lt-faq__item summary:hover,
.lt-faq__link:hover,
.lt-faq__link:focus {
    color: #b31b34;
}
.lt-faq__item summary:focus-visible,
.lt-faq__link:focus-visible {
    outline-color: #b31b34;
}
.lt-faq__answer li::before {
    color: #b31b34;
}
@media (max-width: 480px) {
    .lt-faq__inner {
        padding: 1.25rem;
    }
}
"""


def get_context(context):
    context.title = "Frequently Asked Questions | Locally Twisted"
    context.metatags = {
        "description": (
            "Common questions about booking Locally Twisted for balloon decor, "
            "balloon twisting, and face painting events: pricing, deposits, "
            "cancellations, service area, themes."
        ),
        "og:title": "FAQ | Locally Twisted",
        "og:description": (
            "Pricing, deposits, cancellation, service area, themes, "
            "and how we work."
        ),
        "og:type": "website",
    }
    context.colocated_css = PAGE_CSS
    return context
