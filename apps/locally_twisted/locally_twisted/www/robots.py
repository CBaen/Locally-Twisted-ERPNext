"""Robots discovery file for the public Locally Twisted site."""

from locally_twisted.seo import absolute_url


no_cache = 1
base_template_path = "www/robots.txt"


def get_context(context):
    return {"sitemap_url": absolute_url("/sitemap.xml")}
