from locally_twisted.customer_portal_pages import account_context


no_cache = 1
sitemap = 0


def get_context(context):
    return account_context(context, "dashboard")
