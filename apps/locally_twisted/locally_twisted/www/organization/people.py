from locally_twisted.customer_portal_pages import organization_context


sitemap = 0
no_cache = 1


def get_context(context):
    return organization_context(context, "people")
