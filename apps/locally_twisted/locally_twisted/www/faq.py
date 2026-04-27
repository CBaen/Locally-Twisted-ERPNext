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
    font-weight: 600;
    margin: 0 0 1.5rem;
    line-height: 1.2;
}
.lt-faq__lede {
    font-size: 1.125rem;
    line-height: 1.6;
    margin: 0 0 2rem;
}
.lt-faq__group {
    margin: 0 0 2.5rem;
}
.lt-faq__group-title {
    font-size: 1.25rem;
    font-weight: 600;
    margin: 0 0 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    line-height: 1.3;
}
.lt-faq__item {
    margin: 0 0 1.5rem;
}
.lt-faq__question {
    font-size: 1rem;
    font-weight: 600;
    margin: 0 0 0.5rem;
    line-height: 1.4;
}
.lt-faq__answer {
    font-size: 1rem;
    line-height: 1.6;
    margin: 0;
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
