"""Disable Frappe's bundled /search page for the public LT site."""

no_cache = 1
sitemap = 0


def get_context(context):
    context.http_status_code = 404
    context.no_cache = 1
    context.title = "Not Found"
    return context
