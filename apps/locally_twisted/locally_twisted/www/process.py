"""Process page for quote-led event balloon work."""

no_cache = 1
sitemap = 1


def get_context(context):
    context.title = "How Locally Twisted Plans Event Balloon Work"
    context.metatags = {
        "title": context.title,
        "description": (
            "How Locally Twisted quotes, plans, designs, delivers, installs, invoices, "
            "and follows up on Utah event balloon projects."
        ),
        "og:title": context.title,
        "og:description": (
            "A clear process for Utah business, school, civic, community, venue, and private event balloon work."
        ),
        "og:type": "website",
    }
    return context
