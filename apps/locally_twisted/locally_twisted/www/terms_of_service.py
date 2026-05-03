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
.lt-policy__eyebrow {
    margin: 0 0 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 0.75rem;
    font-weight: 700;
}
.lt-policy h1 {
    font-size: 2rem;
    margin: 0 0 1.5rem;
    line-height: 1.2;
}
.lt-policy h2 {
    font-size: 1.5rem;
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

/* Civic Celebration redesign for secondary editorial pages. */
.lt-policy {
    background-color: #faf7f2;
    color: #0a0a0b;
}
.lt-policy__inner {
    background-color: #fffdf9;
    border: 1px solid rgba(14, 34, 64, 0.16);
    border-top: 8px solid #b31b34;
    border-radius: 0.375rem;
    box-shadow: 0 18px 50px rgba(14, 34, 64, 0.08);
    padding: 2rem;
}
.lt-policy__eyebrow {
    color: #b31b34;
    font-weight: 800;
    letter-spacing: 0.14em;
}
.lt-policy h1,
.lt-policy h2 {
    font-family: 'DM Serif Display', Georgia, serif;
    color: #0e2240;
    letter-spacing: 0;
}
.lt-policy__lede,
.lt-policy p,
.lt-policy__list li,
.lt-policy__contact {
    color: rgba(10, 10, 11, 0.72);
}
.lt-policy__list strong,
.lt-policy__link {
    color: #0a0a0b;
}
.lt-policy__list li::before {
    color: #b31b34;
}
.lt-policy__contact {
    border-top-color: rgba(14, 34, 64, 0.16);
}
.lt-policy__link:hover,
.lt-policy__link:focus {
    color: #b31b34;
}
.lt-policy__link:focus-visible {
    outline-color: #b31b34;
}
@media (max-width: 480px) {
    .lt-policy__inner {
        padding: 1.25rem;
    }
}
"""


def get_context(context):
    context.title = "Terms of Service | Locally Twisted"
    context.metatags = {
        "description": (
            "Booking, payment, cancellation, service area, and website terms "
            "for Locally Twisted customers."
        ),
        "og:title": "Terms of Service | Locally Twisted",
        "og:description": (
            "Plain-language terms for booking and ordering from Locally Twisted."
        ),
        "og:type": "website",
    }
    context.colocated_css = PAGE_CSS
    return context
