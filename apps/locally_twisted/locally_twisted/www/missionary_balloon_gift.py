"""Missionary Balloon Gift ad landing page."""

from locally_twisted.www.product_ad_pages import get_product_ad_context


no_cache = 1
sitemap = 1


def get_context(context):
    return get_product_ad_context(context, "missionary_balloon_gift")
