from locally_twisted.customer_portal_pages import account_context


sitemap = 0
no_cache = 1


def get_context(context):
    return account_context(context, "events")
