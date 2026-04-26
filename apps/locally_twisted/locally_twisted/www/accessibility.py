import frappe

no_cache = 1
sitemap = 1


PAGE_CSS = """
.lt-accessibility {
    padding: 4rem 1.5rem;
}
.lt-accessibility__inner {
    max-width: 42rem;
    margin: 0 auto;
}
.lt-accessibility h1 {
    font-size: 2rem;
    font-weight: 600;
    margin: 0 0 1.5rem;
    line-height: 1.2;
}
.lt-accessibility__lede {
    font-size: 1.125rem;
    line-height: 1.6;
    margin: 0 0 1.25rem;
}
.lt-accessibility p {
    font-size: 1rem;
    line-height: 1.6;
    margin: 0 0 1.25rem;
}
.lt-accessibility__contact {
    margin-top: 2rem;
}
.lt-accessibility__link {
    font-weight: 600;
    text-decoration: underline;
    text-underline-offset: 0.2em;
}
.lt-accessibility__link:hover,
.lt-accessibility__link:focus {
    text-decoration-thickness: 2px;
}
.lt-accessibility__link:focus-visible {
    outline: 3px solid currentColor;
    outline-offset: 4px;
}
@media (max-width: 480px) {
    .lt-accessibility {
        padding: 2.5rem 1rem;
    }
    .lt-accessibility h1 {
        font-size: 1.625rem;
    }
}
"""


def get_context(context):
    context.title = "Accessibility | Locally Twisted"
    context.metatags = {
        "description": (
            "Accessibility commitment from Locally Twisted. "
            "Reach our team if you encounter a barrier on this site."
        ),
        "og:title": "Accessibility at Locally Twisted",
        "og:description": (
            "We work to keep our website usable for everyone. "
            "If you run into a barrier, please let us know."
        ),
        "og:type": "website",
    }
    context.colocated_css = PAGE_CSS
    return context
