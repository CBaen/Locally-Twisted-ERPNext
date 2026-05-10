"""Authority hub for quote-led Utah event balloon work."""

from locally_twisted.seo import service_schema

no_cache = 1
sitemap = 1


def get_context(context):
    context.title = "Event Balloons for Utah Businesses, Schools, and Civic Events"
    context.metatags = {
        "title": context.title,
        "description": (
            "Quote-led balloon decor, delivery, and install support for Utah corporate, "
            "school, civic, community, venue, and institutional events."
        ),
        "og:title": context.title,
        "og:description": (
            "Locally Twisted designs and installs professional event balloon work across Utah."
        ),
        "og:type": "website",
    }
    context.structured_data = [
        service_schema(
            "Utah event balloon decor",
            context.metatags["description"],
            "/event-balloons",
            service_type="Balloon decor and event installation",
        )
    ]
    return context
