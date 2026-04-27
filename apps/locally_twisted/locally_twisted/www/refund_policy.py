import frappe

no_cache = 1
sitemap = 1


PAGE_CSS = """
.lt-policy {
    padding: 4rem 1.5rem;
}
.lt-policy__inner {
    max-width: 44rem;
    margin: 0 auto;
}
.lt-policy h1 {
    font-size: 2rem;
    font-weight: 600;
    margin: 0 0 1.5rem;
    line-height: 1.2;
}
.lt-policy h2 {
    font-size: 1.25rem;
    font-weight: 600;
    margin: 2.5rem 0 0.75rem;
    line-height: 1.3;
}
.lt-policy__lede {
    font-size: 1.125rem;
    line-height: 1.6;
    margin: 0 0 1.25rem;
}
.lt-policy p {
    font-size: 1rem;
    line-height: 1.6;
    margin: 0 0 1rem;
}
.lt-policy__list {
    list-style: none;
    padding: 0;
    margin: 0 0 1rem;
}
.lt-policy__list li {
    font-size: 1rem;
    line-height: 1.6;
    margin: 0 0 0.75rem;
    padding-left: 1.25rem;
    position: relative;
}
.lt-policy__list li::before {
    content: "\\2022";
    position: absolute;
    left: 0;
    top: 0;
    font-weight: 600;
}
.lt-policy__list strong {
    font-weight: 600;
}
.lt-policy__contact {
    margin-top: 2.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid rgba(0, 0, 0, 0.08);
}
.lt-policy__link {
    font-weight: 600;
    text-decoration: underline;
    text-underline-offset: 0.2em;
}
.lt-policy__link:hover,
.lt-policy__link:focus {
    text-decoration-thickness: 2px;
}
.lt-policy__link:focus-visible {
    outline: 3px solid currentColor;
    outline-offset: 4px;
}
@media (max-width: 480px) {
    .lt-policy {
        padding: 2.5rem 1rem;
    }
    .lt-policy h1 {
        font-size: 1.625rem;
    }
    .lt-policy h2 {
        font-size: 1.125rem;
    }
}
"""


def get_context(context):
    context.title = "Refund and Cancellation Policy | Locally Twisted"
    context.metatags = {
        "description": (
            "How Locally Twisted handles deposits, cancellations, and refunds "
            "for balloon decor, balloon twisting, and face painting events."
        ),
        "og:title": "Refund and Cancellation Policy | Locally Twisted",
        "og:description": (
            "Plain-language guide to our deposit structure, cancellation "
            "windows, and reschedule options."
        ),
        "og:type": "website",
    }
    context.colocated_css = PAGE_CSS
    return context
