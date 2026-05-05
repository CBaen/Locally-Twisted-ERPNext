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

/* Civic Celebration redesign for secondary editorial pages. */
.lt-accessibility {
    background-color: #faf7f2;
    color: #0a0a0b;
}
.lt-accessibility__inner {
    background-color: #fffdf9;
    border: 1px solid rgba(14, 34, 64, 0.16);
    border-top: 8px solid #b31b34;
    border-radius: 0.375rem;
    box-shadow: 0 18px 50px rgba(14, 34, 64, 0.08);
    padding: 2rem;
}
.lt-accessibility__eyebrow {
    color: #b31b34;
    font-size: 0.75rem;
    font-weight: 800;
    letter-spacing: 0.14em;
    margin: 0 0 0.75rem;
    text-transform: uppercase;
}
.lt-accessibility h1 {
    font-family: 'Cormorant Garamond', Georgia, serif;
    color: #0e2240;
    letter-spacing: 0;
}
.lt-accessibility__lede,
.lt-accessibility p,
.lt-accessibility__contact {
    color: rgba(10, 10, 11, 0.72);
}
.lt-accessibility__link {
    color: #0a0a0b;
}
.lt-accessibility__link:hover,
.lt-accessibility__link:focus {
    color: #b31b34;
}
.lt-accessibility__link:focus-visible {
    outline-color: #b31b34;
}
@media (max-width: 480px) {
    .lt-accessibility__inner {
        padding: 1.25rem;
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
